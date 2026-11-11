"""
Issue #179 (E4): dataset RAFT para ajustar un modelo local con QLoRA.

Receta RAFT (Zhang et al., 2024, arXiv:2403.10131): entrenar con la pregunta,
el documento correcto ("oráculo") mezclado con documentos distractores, y una
respuesta que se apoya en el documento correcto. En una fracción de los
ejemplos se quita el oráculo, para que el modelo aprenda a abstenerse en vez
de inventar. Objetivo: que el modelo USE el contexto de StructAI, cite y se
abstenga, no que memorice la norma (Ovadia et al., 2024; Gekhman et al., 2024).

Fuente: scripts/evaluacion/qlora_export/{train,heldout}.jsonl. Son respuestas de
Groq (gpt-oss-120b) sobre el contexto real de producción, filtradas por RAGAS
(faithfulness y context_recall). La partición train/heldout original se
respeta: el held-out nunca se mezcla con el entrenamiento.

Transformaciones:
  1. Filtro de Gekhman: se descarta todo ejemplo cuya respuesta tenga cifras
     con unidad que no aparecen en el contexto ni en la pregunta
     (_detectar_posible_alucinacion_numerica de producción). Así no se
     entrena ningún "hecho" que el modelo tendría que saber de memoria.
  2. Oráculo: los chunks del contexto que contienen las anclas de la
     respuesta (numerales como G.12.11.3 y cifras). Si no se puede
     identificar, el ejemplo se usa tal cual y no genera variante.
  3. Variante con oráculo (todas): el contexto original más, en la mitad de
     los casos, un distractor de otra pregunta en una posición aleatoria.
  4. Variante sin oráculo (FRACCION_SIN_ORACULO de los que tienen oráculo
     identificable): se quita el oráculo, se agregan 2 distractores, y la
     respuesta es la abstención con la forma que pide el prompt de producción
     ("No encontré eso en las normas que tengo cargadas — revisa directo
     [norma X]").

Salida en scripts/finetuning/datos/ (formato messages system/user/assistant,
compatible con Unsloth/TRL):
  raft_train.jsonl, raft_heldout.jsonl (solo originales), raft_heldout_abstencion.jsonl
  MANIFIESTO.json con conteos, filtros y huecos de cobertura.
No se usa ningún dato de usuarios (consultas_history).

Uso: python scripts/finetuning/construir_dataset_raft.py
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(RAIZ / "apps" / "api" / ".env")
import rag_multi_norma as r  # noqa: E402

ORIGEN = RAIZ / "scripts" / "evaluacion" / "qlora_export"
SALIDA = Path(__file__).parent / "datos"
SEMILLA = 179
FRACCION_SIN_ORACULO = 0.25     # sobre los que tienen oráculo; ~20 % del total final
SEP = "\n\n---\n\n"
RE_NUMERAL = re.compile(r"\b[A-K]\.\d+(?:\.\d+)*(?:-\d+)?\b|\bArt(?:ículo|iculo|\.)\s*\d+", re.I)
RE_CIFRA = re.compile(r"\d+(?:[.,]\d+)?")


def partir(user: str):
    """(chunks, pregunta) si el mensaje tiene la forma de ask(); None si no."""
    if "CONTEXTO NORMATIVO:" not in user or "PREGUNTA:" not in user:
        return None
    cuerpo, pregunta = user.rsplit("PREGUNTA:", 1)
    cuerpo = cuerpo.split("CONTEXTO NORMATIVO:", 1)[1].strip()
    return [c.strip() for c in cuerpo.split(SEP) if c.strip()], pregunta.strip()


def armar(chunks, pregunta):
    return "CONTEXTO NORMATIVO:\n" + SEP.join(chunks) + "\n\nPREGUNTA: " + pregunta


def anclas(texto: str) -> set[str]:
    numerales = {m.group(0).lower() for m in RE_NUMERAL.finditer(texto)}
    cifras = {c for c in RE_CIFRA.findall(texto) if len(c.replace(",", "").replace(".", "")) >= 2}
    return numerales | cifras


def oraculos(chunks, respuesta, pregunta) -> list[int]:
    objetivo = anclas(respuesta) - anclas(pregunta)
    if not objetivo:
        return []
    # TODOS los chunks que contienen alguna ancla de la respuesta: en preguntas
    # comparativas el dato está repartido en varios (primera versión: quitar solo
    # el mejor dejaba, en la mediana, la mitad de las anclas en el contexto).
    return [i for i, c in enumerate(chunks) if objetivo & anclas(c)]


def norma_de(chunk: str) -> str | None:
    """Referencia citable del chunk: 'NSR-10 Título G G.12.11.3' si el encabezado la
    trae, o el primer numeral/tabla del texto. None si no hay nada citable."""
    cab = chunk.split("\n", 1)[0]
    m = re.match(r"^((?:NSR-10|NTC|Resoluci[oó]n|Decreto|Ley|CCP-14|Res\.)[^–—]{0,60}?)\s[–—-]\s", cab)
    if m:
        return m.group(1).strip()
    t = re.search(r"\b(?:Tabla\s+)?[A-K]\.\d+(?:\.\d+)*(?:-\d+)?\b", chunk)
    return t.group(0) if t else None


def abstencion(norma: str | None) -> str:
    if norma:
        return f"No encontré eso en las normas que tengo cargadas — revisa directo {norma}, ahí debería estar."
    return "No encontré eso en las normas que tengo cargadas, así que no te doy un valor que no pueda respaldar con la norma."


def cargar(nombre):
    return [json.loads(l) for l in (ORIGEN / nombre).read_text(encoding="utf-8").splitlines()]


def procesar(filas, rng, aumentar: bool, banco_distractores: list[str], stats: Counter, abst_out: list):
    out = []
    for x in filas:
        msgs = {m["role"]: m["content"] for m in x["messages"]}
        sistema, user, resp = msgs["system"], msgs["user"], msgs["assistant"]
        if r._detectar_posible_alucinacion_numerica(user, resp):
            stats["descartado_cifra_no_soportada"] += 1
            continue
        partes = partir(user)
        base = {"_origen": x.get("_metadata", {}), "_variante": "original"}
        if partes is None:
            stats["sin_formato_contexto (se usa tal cual)"] += 1
            out.append({"messages": x["messages"], **base})
            continue
        chunks, pregunta = partes
        ors = oraculos(chunks, resp, pregunta)
        if aumentar and rng.random() < 0.5 and banco_distractores:
            nuevos = chunks[:]
            nuevos.insert(rng.randrange(len(nuevos) + 1), rng.choice(banco_distractores))
            out.append({"messages": [{"role": "system", "content": sistema},
                                     {"role": "user", "content": armar(nuevos, pregunta)},
                                     {"role": "assistant", "content": resp}],
                        **base, "_variante": "con_oraculo+distractor"})
            stats["con_oraculo+distractor"] += 1
        else:
            out.append({"messages": x["messages"], **base})
            stats["original"] += 1
        if not ors:
            stats["oraculo_no_identificable"] += 1
            continue
        if rng.random() < FRACCION_SIN_ORACULO:
            objetivo = anclas(resp) - anclas(pregunta)
            restantes = [c for i, c in enumerate(chunks) if i not in ors]
            limpios = [c for c in banco_distractores if not (objetivo & anclas(c))]
            distr = rng.sample(limpios, k=min(2, len(limpios)))
            sin = restantes + distr
            # Solo se acepta si el dato quedó realmente fuera: cero anclas de la
            # respuesta en el contexto resultante. Si no, abstenerse sería un
            # ejemplo incorrecto (enseñaría a negarse teniendo el dato).
            if not restantes and not distr or any(objetivo & anclas(c) for c in sin):
                stats["sin_oraculo_descartado_dato_residual"] += 1
                continue
            rng.shuffle(sin)
            ej = {"messages": [{"role": "system", "content": sistema},
                               {"role": "user", "content": armar(sin, pregunta)},
                               {"role": "assistant", "content": abstencion(norma_de(chunks[ors[0]]))}],
                  **base, "_variante": "sin_oraculo"}
            (out if aumentar else abst_out).append(ej)
            stats["sin_oraculo"] += 1
    return out


def main():
    rng = random.Random(SEMILLA)
    train, heldout = cargar("train.jsonl"), cargar("heldout.jsonl")
    # distractores: chunks de las preguntas de entrenamiento (nunca del held-out)
    banco = []
    for x in train:
        p = partir(next(m["content"] for m in x["messages"] if m["role"] == "user"))
        if p:
            banco.extend(p[0])
    st_tr, st_ho, abst = Counter(), Counter(), []
    raft_train = procesar(train, rng, True, banco, st_tr, [])
    raft_heldout = procesar(heldout, random.Random(SEMILLA + 1), False, banco, st_ho, abst)
    rng.shuffle(raft_train)

    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, filas in (("raft_train.jsonl", raft_train), ("raft_heldout.jsonl", raft_heldout),
                          ("raft_heldout_abstencion.jsonl", abst)):
        (SALIDA / nombre).write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")

    def dominio(f):
        u = next(m["content"] for m in f["messages"] if m["role"] == "user").lower()
        return "precios" if re.search(r"precio|cuesta|vale|\bcop\b|\$", u[-500:]) else "nsr10/ntc/general"

    largos = sorted(len(next(m["content"] for m in f["messages"] if m["role"] == "user")) for f in raft_train)
    manifiesto = {
        "fuente": "scripts/evaluacion/qlora_export (train/heldout originales, partición respetada)",
        "sha1_fuente": {n: hashlib.sha1((ORIGEN / n).read_bytes()).hexdigest()[:12] for n in ("train.jsonl", "heldout.jsonl")},
        "semilla": SEMILLA, "fraccion_sin_oraculo": FRACCION_SIN_ORACULO,
        "train": {"n": len(raft_train), "variantes": dict(Counter(f["_variante"] for f in raft_train)), "transformaciones": dict(st_tr),
                  "por_dominio": dict(Counter(dominio(f) for f in raft_train))},
        "heldout": {"n": len(raft_heldout), "transformaciones": dict(st_ho)},
        "heldout_abstencion": {"n": len(abst)},
        "largo_user_caracteres": {"p50": largos[len(largos) // 2], "p95": largos[int(0.95 * (len(largos) - 1))], "max": largos[-1]},
        "huecos": [
            "Sin ejemplos de los motores (aquai, geopot, vias, gerencia, vivienda): faltan respuestas de un modelo maestro "
            "para esas preguntas (OpenAI sin crédito, Groq reservado para producción). Ver #170/#179.",
            "Contextos largos: max_seq_length en el entrenamiento debe cubrir el p95 o recortar distractores.",
        ],
    }
    (SALIDA / "MANIFIESTO.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(manifiesto, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
