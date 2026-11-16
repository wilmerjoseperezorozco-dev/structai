"""Fase 2: ¿el índice RAG local cambia la CALIDAD de las respuestas frente a la ruta anterior (RPC + HNSW)?

Diseño preregistrado en docs/evaluacion/PREREGISTRO_INDICE_LOCAL.md (fijado antes de ver resultados):
- Población: las preguntas de las baterías NSR-10 y motores cuyo prompt de generación DIFIERE entre modos según el
  filtro 1 (filtro_contexto.json). Si el prompt es idéntico, la respuesta no puede depender del índice.
- Orden: aleatorio con semilla fija (20261116), para que cualquier corte diario sea una muestra sin sesgo.
- Por pregunta: una generación por modo (local y RPC), en orden también aleatorio por pregunta, con el mismo modelo,
  la misma temperatura y la misma descomposición en caché que producción.
- Calificación: la misma de las baterías (_contiene_alguna con las variantes del caso; en motores, además el dominio).
- Groq: solo GROQ_API_KEY_EVAL. Se detiene limpio al agotar la cuota diaria y retoma el día siguiente.

Las respuestas crudas (pueden citar texto del corpus) quedan en resultados/fase2_respuestas.jsonl, que NO se versiona.
Uso: python scripts/evaluacion/indice_local/fase2_generacion.py [--max-preguntas N]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import deque
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
import filtro_contexto as fc  # noqa: E402

RES = AQUI / "resultados"
FILTRO = RES / "filtro_contexto.json"
RESPUESTAS = RES / "fase2_respuestas.jsonl"
SEMILLA = 20261116
TPM_SEGURO = 7000                                  # límite de la clave: 8.000 tokens/min


class Cuota(Exception):
    pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-preguntas", type=int, default=0)
    a = ap.parse_args()
    clave = fc._preparar_entorno()
    sys.path.insert(0, str(fc.API)); sys.path.insert(0, str(fc.RAIZ / "packages" / "construdata"))
    sys.path.insert(0, str(fc.API / "tests"))
    import rag_multi_norma as rmn  # noqa: E402
    import test_rag_motores_regresion as tm  # noqa: E402
    import test_rag_nsr10_regresion as tn  # noqa: E402

    variantes = {}
    for mod, bateria in ((tn, "nsr10"), (tm, "motores")):
        for nombre, val in vars(mod).items():
            if nombre.startswith("CASOS") and isinstance(val, list):
                for p in val:
                    v = getattr(p, "values", None)
                    if v:
                        # nsr10: (pregunta, variantes) · motores: (motor, pregunta, variantes)
                        variantes[f"{bateria}:{p.id}"] = (v[2], v[0]) if bateria == "motores" else (v[1], None)

    filas = json.loads(FILTRO.read_text(encoding="utf-8"))["filas"]
    poblacion = [f for f in filas if f.get("identico") is False]
    random.Random(SEMILLA).shuffle(poblacion)
    hechas = set()
    if RESPUESTAS.exists():
        for linea in RESPUESTAS.read_text(encoding="utf-8").splitlines():
            r = json.loads(linea); hechas.add((r["id"], r["modo"]))

    cache = json.loads(fc.CACHE_DESC.read_text(encoding="utf-8")) if fc.CACHE_DESC.exists() else {}
    ventana: deque = deque()                       # (t, tokens) del último minuto
    uso_total = {"tokens": 0}

    def esperar(tokens_previstos: int) -> None:
        while True:
            ahora = time.time()
            while ventana and ahora - ventana[0][0] > 60:
                ventana.popleft()
            # Un prompt que solo ya supera TPM_SEGURO nunca cabría: con la ventana vacía se envía igual (antes se
            # quedaba esperando para siempre) y Groq decide; si lo rechaza, el error queda en el log.
            if not ventana or sum(t for _, t in ventana) + tokens_previstos <= TPM_SEGURO:
                return
            time.sleep(2)

    def llm(messages, max_tokens_groq=700):
        if max_tokens_groq == 250:
            k = messages[0]["content"]
            if k in cache:
                return cache[k]
        previsto = sum(len(m["content"]) for m in messages) // 3 + max_tokens_groq
        if previsto > TPM_SEGURO:
            print(f"  aviso: prompt estimado en {previsto} tokens (> {TPM_SEGURO})", flush=True)
        esperar(previsto)
        try:
            texto, uso = fc._groq_eval(clave, rmn.GROQ_MODEL, messages, max_tokens_groq)
        except RuntimeError as e:
            if "cuota diaria" in str(e):
                raise Cuota() from None
            raise
        t = uso.get("total_tokens", previsto)
        ventana.append((time.time(), t)); uso_total["tokens"] += t
        if max_tokens_groq == 250:
            cache[messages[0]["content"]] = texto
        return texto
    rmn._llamar_llm_con_respaldo = llm

    hechas_hoy = 0
    with RESPUESTAS.open("a", encoding="utf-8") as out:
        for f in poblacion:
            if a.max_preguntas and hechas_hoy >= a.max_preguntas:
                break
            modos = ["local", "rpc"]
            random.Random(f"{SEMILLA}:{f['id']}").shuffle(modos)
            pendientes = [m for m in modos if (f["id"], m) not in hechas]
            if not pendientes:
                continue
            try:
                for modo in pendientes:
                    rmn.RAG_INDICE_LOCAL = modo == "local"
                    t0, tok0 = time.time(), uso_total["tokens"]
                    if f["bateria"] == "nsr10":
                        r = rmn.ask(f["pregunta"]); dominio_ok = None
                    else:
                        r = rmn.ask_delegado(f["pregunta"], top_k=4)
                        dominio_ok = r.get("dominio") == variantes[f["id"]][1]
                    esperadas = variantes[f["id"]][0]
                    contiene = (tn if f["bateria"] == "nsr10" else tm)._contiene_alguna(r["respuesta"], esperadas)
                    out.write(json.dumps({"id": f["id"], "bateria": f["bateria"], "modo": modo,
                                          "aprueba": bool(contiene and dominio_ok is not False),
                                          "contiene_hecho": bool(contiene), "dominio_ok": dominio_ok,
                                          "tokens": uso_total["tokens"] - tok0, "segundos": round(time.time() - t0, 1),
                                          "modelo": rmn.GROQ_MODEL, "fecha": time.strftime("%Y-%m-%d %H:%M"),
                                          "respuesta": r["respuesta"]}, ensure_ascii=False) + "\n")
                    out.flush()
                    print(f"{f['id'][:55]:55} {modo:5} {'✓' if contiene else '✗'} {uso_total['tokens']:>7} tok", flush=True)
            except Cuota:
                print("Cuota diaria de Groq agotada: se retoma mañana.", flush=True)
                break
            hechas_hoy += 1
    fc.CACHE_DESC.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"tokens usados en esta corrida: {uso_total['tokens']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
