"""Filtro 1: ¿el índice RAG local cambia lo que ve el LLM en las baterías de regresión?

Para cada pregunta de las baterías NSR-10 (ask) y de motores (ask_delegado) se arma el prompt de generación dos veces:
con el índice local en memoria y con las RPC de Supabase (la ruta anterior de producción). Si el prompt es idéntico
byte a byte, la respuesta del LLM no puede depender del índice y esa pregunta no necesita generación en la fase 2.

- La descomposición en sub-preguntas (_descomponer_pregunta) es la única llamada al LLM previa a la recuperación y no
  depende del índice: se hace UNA vez por pregunta con Groq usando GROQ_API_KEY_EVAL (nunca la clave de producción) y se
  guarda en caché; los dos modos reciben exactamente la misma descomposición.
- La llamada de generación se intercepta: se guarda el hash del prompt y no se genera respuesta.
- Supabase: solo lecturas (RPC de búsqueda y datos de referencia). La caché de respuestas está apagada.
- La salida no guarda texto del corpus: solo hashes, similitud y metadatos de la pregunta (que ya está en el repo).

Uso: python scripts/evaluacion/indice_local/filtro_contexto.py [--limite N]
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
API = RAIZ / "apps" / "api"
SALIDA = Path(__file__).parent / "resultados"
CACHE_DESC = SALIDA / "cache_descomposicion.json"
PRIVADO = Path(os.environ.get("STRUCTAI_PRIVADO", r"C:\Users\wilme\dev\structai\_privado"))
ENV_PROD_LECTURA = Path(os.environ.get("STRUCTAI_ENV_LECTURA", r"C:\Users\wilme\dev\structai\apps\api\.env"))


def _leer_env(ruta: Path, claves: set[str]) -> dict[str, str]:
    out = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*([A-Z_]+)\s*=\s*(.*)\s*$", linea)
        if m and m.group(1) in claves:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def _preparar_entorno() -> str:
    """Solo SUPABASE_URL/SUPABASE_SERVICE_KEY de la API (lectura). Groq/OpenAI de producción quedan con valores ficticios."""
    os.environ.update(_leer_env(ENV_PROD_LECTURA, {"SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_JWT_SECRET"}))
    os.environ.update({"GROQ_API_KEY": "no-usar-produccion", "OPENAI_API_KEY": "no-usar-produccion",
                       "RAG_CACHE_DISABLED": "true"})
    clave = _leer_env(PRIVADO / ".env.groq_eval", {"GROQ_API_KEY_EVAL"}).get("GROQ_API_KEY_EVAL")
    if not clave:
        sys.exit("Falta GROQ_API_KEY_EVAL en _privado/.env.groq_eval")
    return clave


def _groq_eval(clave: str, modelo: str, messages: list, max_tokens: int) -> tuple[str, dict]:
    cuerpo = json.dumps({"model": modelo, "messages": messages, "temperature": 0.1, "max_tokens": max_tokens,
                         "reasoning_effort": "low"}).encode()
    for intento in range(8):
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=cuerpo, method="POST",
                                     headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json",
                                              "User-Agent": "structai-eval-offline"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"] or "", d.get("usage") or {}
        except urllib.error.HTTPError as e:
            if e.code == 429:
                espera = float(e.headers.get("retry-after") or 20)
                if "tokens per day" in e.read().decode(errors="ignore").lower():
                    raise RuntimeError("cuota diaria de tokens agotada") from None
                time.sleep(min(espera + 1, 120)); continue
            raise
    raise RuntimeError("Groq siguió devolviendo 429")


def _casos() -> list[dict]:
    sys.path.insert(0, str(API / "tests"))
    import test_rag_motores_regresion as tm  # noqa: E402
    import test_rag_nsr10_regresion as tn  # noqa: E402
    casos = []
    for mod, bateria in ((tn, "nsr10"), (tm, "motores")):
        for nombre, val in vars(mod).items():
            if nombre.startswith("CASOS") and isinstance(val, list):
                for p in val:
                    v = getattr(p, "values", None)
                    if not v:
                        continue
                    pregunta = v[0] if bateria == "nsr10" else v[1]
                    casos.append({"id": f"{bateria}:{getattr(p, 'id', None) or len(casos)}", "bateria": bateria,
                                  "grupo": nombre, "pregunta": pregunta})
    vistos, unicos = set(), []
    for c in casos:
        if c["id"] not in vistos:
            vistos.add(c["id"]); unicos.append(c)
    return unicos


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()
    clave = _preparar_entorno()
    sys.path.insert(0, str(API)); sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
    import rag_multi_norma as rmn  # noqa: E402

    SALIDA.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE_DESC.read_text(encoding="utf-8")) if CACHE_DESC.exists() else {}
    tokens = {"descomposicion": 0}
    capturados: list[str] = []

    def llm(messages, max_tokens_groq=700):
        if max_tokens_groq == 250:                            # _descomponer_pregunta: real, con caché
            k = messages[0]["content"]
            if k not in cache:
                texto, uso = _groq_eval(clave, rmn.GROQ_MODEL, messages, 250)
                cache[k] = texto; tokens["descomposicion"] += uso.get("total_tokens", 0)
                CACHE_DESC.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
                time.sleep(2)
            return cache[k]
        capturados.append(json.dumps(messages, ensure_ascii=False, sort_keys=True))
        return "Respuesta interceptada por el filtro (sin generación)."
    rmn._llamar_llm_con_respaldo = llm

    def correr(caso: dict, local: bool) -> list[str]:
        rmn.RAG_INDICE_LOCAL = local
        n0 = len(capturados)
        if caso["bateria"] == "nsr10":
            rmn.ask(caso["pregunta"])
        else:
            rmn.ask_delegado(caso["pregunta"], top_k=4)
        return capturados[n0:]

    casos = _casos()[: a.limite or None]
    filas = []
    for i, c in enumerate(casos, 1):
        try:
            pl, pr = correr(c, True), correr(c, False)
            h = lambda xs: [hashlib.sha256(x.encode()).hexdigest()[:16] for x in xs]
            sim = (difflib.SequenceMatcher(None, pl[-1], pr[-1], autojunk=False).ratio() if pl and pr else None)
            fila = {**c, "llamadas_local": len(pl), "llamadas_rpc": len(pr), "hash_local": h(pl), "hash_rpc": h(pr),
                    "identico": pl == pr, "similitud_prompt": round(sim, 4) if sim is not None else None,
                    "chars_prompt": len(pl[-1]) if pl else 0, "error": None}
        except Exception as e:  # noqa: BLE001
            fila = {**c, "identico": None, "error": f"{type(e).__name__}: {str(e)[:160]}"}
        filas.append(fila)
        print(f"[{i}/{len(casos)}] {'=' if fila['identico'] else ('≠' if fila['identico'] is False else '!')} "
              f"{c['id'][:60]}", flush=True)

    ok = [f for f in filas if f["identico"] is not None]
    resumen = {"preguntas": len(filas), "comparadas": len(ok), "identicas": sum(f["identico"] for f in ok),
               "distintas": sum(not f["identico"] for f in ok), "errores": len(filas) - len(ok),
               "tokens_groq_descomposicion": tokens["descomposicion"], "modelo": rmn.GROQ_MODEL,
               "fecha": time.strftime("%Y-%m-%d %H:%M")}
    (SALIDA / "filtro_contexto.json").write_text(json.dumps({"resumen": resumen, "filas": filas}, ensure_ascii=False,
                                                            indent=1), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
