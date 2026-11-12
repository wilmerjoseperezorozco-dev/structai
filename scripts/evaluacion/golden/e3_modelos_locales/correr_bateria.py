"""
Issue #172: ¿pueden los modelos locales (Ollama en WSL) pasar las baterías de
StructAI? Corre las baterías de regresión con un modelo local como generador.

Qué cambia y qué no:
  - Se reemplaza SOLO _llamar_llm_con_respaldo() de rag_multi_norma, el único
    punto por donde pasan todas las llamadas al LLM (verificado: es el único
    lugar con chat.completions.create). Los mensajes que recibe el modelo
    (prompt del sistema, contexto recuperado, pregunta) son idénticos a los
    de producción.
  - Enrutamiento, recuperación (Supabase, solo lectura) y prompts: los de
    producción. No se llama a Groq ni a OpenAI.
  - Se usa la API nativa de Ollama (/api/chat) y no la compatible con OpenAI,
    porque solo la nativa acepta num_ctx: con el valor por defecto de Ollama
    (2048) el contexto del RAG (3.000-5.000 tokens) se truncaría en silencio.

Baterías (verificación determinista del hecho esperado, sin juez LLM; se
reutilizan los casos y _contiene_alguna de los propios tests):
  motores  apps/api/tests/test_rag_motores_regresion.py  (13, ask_delegado top_k=4,
           exige además el dominio correcto)
  nsr10    apps/api/tests/test_rag_nsr10_regresion.py    (125, ask())
  piloto   motores + 25 de nsr10 (uno por bloque de título, en orden)

Cada caso se guarda al terminar en resultados/<modelo>.jsonl: si se corta,
se retoma donde quedó.

Uso:
  python correr_bateria.py --modelo qwen2.5:7b --bateria piloto
  python correr_bateria.py --resumen
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[4]
API = RAIZ / "apps" / "api"
sys.path.insert(0, str(API))
sys.path.insert(0, str(API / "tests"))
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
load_dotenv(API / ".env")
# El caché de respuestas vive en el Supabase de PRODUCCIÓN (rag_cache_respuestas):
# sin esto, ask() escribiría ahí y, peor, leería respuestas viejas de Groq en vez
# de llamar al modelo local (se mediría a Groq). Se fija antes de importar el
# módulo porque lo lee al importarse. Mismo criterio que el CI (ci.yml).
os.environ["RAG_CACHE_DISABLED"] = "true"

import rag_multi_norma as r  # noqa: E402

AQUI = Path(__file__).parent
RESULTADOS = AQUI / "resultados"
OLLAMA = "http://127.0.0.1:11434"
# Ventana de contexto. 8192 por defecto; los contextos de más de ~18.000 caracteres no caben
# con num_predict 700 y Ollama los recorta a la mitad (4.098 tokens) sin avisar (hallazgo E3).
NUM_CTX = int(os.environ.get("STRUCTAI_NUM_CTX", "8192"))
_ultima: dict = {}


def generador_local(modelo: str):
    def llamar(messages: list, max_tokens_groq: int = 700) -> str:
        t = time.time()
        d = httpx.post(f"{OLLAMA}/api/chat", timeout=3600, json={
            "model": modelo, "messages": messages, "stream": False,
            "options": {"temperature": 0.1, "num_predict": max_tokens_groq, "num_ctx": NUM_CTX},
        }).json()
        if "message" not in d:
            raise RuntimeError(f"Ollama no respondió: {d}")
        _ultima.update(
            segundos=time.time() - t,
            tokens_prompt=d.get("prompt_eval_count", 0),
            tokens_salida=d.get("eval_count", 0),
            tok_s=d.get("eval_count", 0) / max(d.get("eval_duration", 1) / 1e9, 1e-9),
            prompt_truncado=d.get("prompt_eval_count", 0) >= NUM_CTX - 8,
            contexto="\n".join(m["content"] for m in messages if m["role"] != "system"),
        )
        return d["message"]["content"]
    return llamar


def _casos(funcion) -> list:
    """La lista exacta que parametriza el test (mismo orden, mismos ids)."""
    return list(next(m for m in funcion.pytestmark if m.name == "parametrize").args[1])


def cargar_casos(bateria: str) -> list[dict]:
    import test_rag_motores_regresion as tm
    import test_rag_nsr10_regresion as tn
    casos = []
    if bateria in ("motores", "piloto", "todo"):
        for p in _casos(tm.test_delegador_enruta_y_responde_hecho_verificado):
            motor, pregunta, variantes = p.values
            casos.append({"id": p.id, "bateria": "motores", "pregunta": pregunta, "variantes": variantes,
                          "motor": motor, "contiene": tm._contiene_alguna})
    if bateria in ("nsr10", "piloto", "todo"):
        todos = _casos(tn.test_respuesta_contiene_hecho_verificado)
        if bateria == "piloto":
            vistos, elegidos = set(), []
            for p in todos:            # uno por bloque (prefijo del id), en orden
                bloque = p.id.split("-")[0]
                if bloque not in vistos:
                    vistos.add(bloque)
                    elegidos.append(p)
            for p in todos:            # completar hasta 25 con los siguientes no usados
                if len(elegidos) >= 25:
                    break
                if p not in elegidos:
                    elegidos.append(p)
            todos = elegidos[:25]
        for p in todos:
            pregunta, variantes = p.values
            casos.append({"id": p.id, "bateria": "nsr10", "pregunta": pregunta, "variantes": variantes,
                          "contiene": tn._contiene_alguna})
    return casos


def _archivo(modelo):
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    sufijo = "" if NUM_CTX == 8192 else f"_ctx{NUM_CTX}"
    return RESULTADOS / f"{modelo.replace(':', '_').replace('/', '_')}{sufijo}.jsonl"


def correr(modelo: str, bateria: str, ids: set | None = None):
    r._llamar_llm_con_respaldo = generador_local(modelo)
    salida = _archivo(modelo)
    hechos = {json.loads(l)["clave"] for l in salida.read_text(encoding="utf-8").splitlines()} if salida.exists() else set()
    casos = [c for c in cargar_casos(bateria) if not ids or c["id"] in ids]
    print(f"{modelo} | {bateria}: {len(casos)} casos | ya hechos {sum(1 for c in casos if _clave(c) in hechos)}", flush=True)
    for i, c in enumerate(casos, 1):
        if _clave(c) in hechos:
            continue
        _ultima.clear()
        t = time.time()
        fila = {"clave": _clave(c), "id": c["id"], "bateria": c["bateria"], "modelo": modelo}
        try:
            if c["bateria"] == "motores":
                res = r.ask_delegado(c["pregunta"], top_k=4)
                fila["dominio"] = res.get("dominio")
                fila["enruta_ok"] = res.get("dominio") == c["motor"]
            else:
                res = r.ask(c["pregunta"])
            resp = res.get("respuesta", "")
            fila["hecho_ok"] = bool(c["contiene"](resp, c["variantes"]))
            fila["paso"] = fila["hecho_ok"] and fila.get("enruta_ok", True)
            alu = res.get("advertencia_posible_alucinacion")
            if alu is None and _ultima.get("contexto"):
                alu = r._detectar_posible_alucinacion_numerica(_ultima["contexto"], resp)
            fila["alucinacion_numerica"] = alu or []
            fila["llamo_llm"] = bool(_ultima)
            fila["respuesta"] = resp
        except Exception as e:  # noqa: BLE001
            fila.update(paso=False, hecho_ok=False, error=f"{type(e).__name__}: {str(e)[:300]}")
        fila["segundos_total"] = round(time.time() - t, 1)
        fila.update({k: v for k, v in _ultima.items() if k != "contexto"})
        with salida.open("a", encoding="utf-8") as f:
            f.write(json.dumps(fila, ensure_ascii=False, default=str) + "\n")
        print(f"  [{i}/{len(casos)}] {c['id'][:45]:45s} {'OK ' if fila['paso'] else 'NO '} "
              f"{fila['segundos_total']:6.1f}s prompt={_ultima.get('tokens_prompt', '-')}"
              f"{' TRUNCADO' if _ultima.get('prompt_truncado') else ''}{' ' + fila['error'] if 'error' in fila else ''}", flush=True)


def _clave(c):
    return hashlib.sha1(f"{c['bateria']}|{c['id']}|{c['pregunta']}".encode()).hexdigest()[:16]


def resumen():
    filas_md = ["| Modelo | Batería | n | Pasa | Hecho | Enruta | Alucinación num. | Latencia p50 / p95 | tok/s | Truncados | Errores |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in sorted(RESULTADOS.glob("*.jsonl")):
        filas = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines()]
        for bat in ("motores", "nsr10"):
            fs = [x for x in filas if x["bateria"] == bat]
            if not fs:
                continue
            lat = sorted(x["segundos_total"] for x in fs)
            p95 = lat[min(len(lat) - 1, int(round(0.95 * (len(lat) - 1))))]
            enr = [x for x in fs if "enruta_ok" in x]
            enruta = f"{sum(x['enruta_ok'] for x in enr)}/{len(enr)}" if enr else "—"
            filas_md.append(
                f"| {fs[0]['modelo']} | {bat} | {len(fs)} | {sum(x['paso'] for x in fs)}/{len(fs)} "
                f"| {sum(x['hecho_ok'] for x in fs)}/{len(fs)} "
                f"| {enruta} "
                f"| {sum(bool(x.get('alucinacion_numerica')) for x in fs)} "
                f"| {statistics.median(lat):.0f}s / {p95:.0f}s "
                f"| {statistics.median([x['tok_s'] for x in fs if x.get('tok_s')] or [0]):.1f} "
                f"| {sum(bool(x.get('prompt_truncado')) for x in fs)} | {sum('error' in x for x in fs)} |")
    texto = "\n".join(filas_md)
    print(texto)
    (AQUI / "RESUMEN.md").write_text("# Modelos locales en las baterías de StructAI (#172)\n\n" + texto + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo")
    ap.add_argument("--bateria", choices=["motores", "nsr10", "piloto", "todo"], default="piloto")
    ap.add_argument("--resumen", action="store_true")
    ap.add_argument("--ids", help="ids de casos separados por coma (solo esos)")
    a = ap.parse_args()
    if a.resumen:
        resumen()
    else:
        correr(a.modelo, a.bateria, set(a.ids.split(",")) if a.ids else None)
        resumen()


if __name__ == "__main__":
    main()
