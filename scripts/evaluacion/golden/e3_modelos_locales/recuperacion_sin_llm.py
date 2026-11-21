"""
¿Los fallos de E3 son de recuperación o de generación? (#172). Sin LLM.

Corre ask() de producción sobre los 125 casos NSR-10 con un generador falso que
solo registra los mensajes que recibiría el modelo y devuelve "". Si el hecho
esperado (las variantes del test, con el mismo _contiene_alguna) ya está en el
contexto recuperado, un fallo del modelo es de GENERACIÓN; si no está, es de
RECUPERACIÓN (ningún generador lo habría podido decir con fundamento).

Cruza con resultados/<modelo>.jsonl para clasificar cada fallo.

Uso: python recuperacion_sin_llm.py [--modelo qwen2.5:7b]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict

import correr_bateria as cb  # fija RAG_CACHE_DISABLED antes de importar rag_multi_norma

r = cb.r
_mensajes: list[str] = []


def _falso(messages: list, max_tokens_groq: int = 700) -> str:
    _mensajes.append("\n".join(m["content"] for m in messages if m["role"] != "system"))
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen2.5:7b")
    a = ap.parse_args()
    r._llamar_llm_con_respaldo = _falso
    previos = {}
    archivo = cb._archivo(a.modelo)
    for l in archivo.read_text(encoding="utf-8").splitlines():
        f = json.loads(l)
        previos[f["id"]] = f
    filas = []
    for i, c in enumerate(cb.cargar_casos("nsr10"), 1):
        _mensajes.clear()
        try:
            res = r.ask(c["pregunta"])
            respuesta = res.get("respuesta", "") if isinstance(res, dict) else str(res)
        except Exception as e:  # noqa: BLE001
            respuesta = f"ERROR {type(e).__name__}: {e}"
        contexto = "\n".join(_mensajes)
        en_ctx = bool(c["contiene"](contexto, c["variantes"])) if contexto else False
        # caso determinista: ask() respondió sin llamar al LLM
        determinista = not _mensajes and bool(respuesta)
        p = previos.get(c["id"], {})
        filas.append({"id": c["id"], "titulo": c["id"].split("-")[0], "hecho_en_contexto": en_ctx,
                      "sin_llm": determinista, "llm_paso": p.get("paso"), "chars_contexto": len(contexto)})
        print(f"[{i:3}/125] {c['id'][:48]:48} ctx={'SI' if en_ctx else 'no'} modelo={'OK' if p.get('paso') else 'NO'}",
              flush=True)
    (cb.AQUI / "resultados" / f"recuperacion_{a.modelo.replace(':', '_')}.jsonl").write_text(
        "\n".join(json.dumps(f, ensure_ascii=False) for f in filas) + "\n", encoding="utf-8")

    por = defaultdict(Counter)
    for f in filas:
        t = f["titulo"]
        por[t]["n"] += 1
        por[t]["ctx"] += f["hecho_en_contexto"]
        if not f["llm_paso"]:
            por[t]["fallos"] += 1
            por[t]["fallo_recuperacion" if not f["hecho_en_contexto"] else "fallo_generacion"] += 1
        elif not f["hecho_en_contexto"]:
            por[t]["paso_sin_ctx"] += 1
    print("\n| Título | n | Hecho en contexto | Fallos del modelo | de recuperación | de generación | Pasa sin estar en contexto |")
    print("|---|---|---|---|---|---|---|")
    tot = Counter()
    for t in sorted(por):
        d = por[t]
        tot.update(d)
        print(f"| {t} | {d['n']} | {d['ctx']}/{d['n']} | {d['fallos']} | {d['fallo_recuperacion']} | {d['fallo_generacion']} | {d['paso_sin_ctx']} |")
    print(f"| **Total** | {tot['n']} | {tot['ctx']}/{tot['n']} | {tot['fallos']} | {tot['fallo_recuperacion']} | {tot['fallo_generacion']} | {tot['paso_sin_ctx']} |")


if __name__ == "__main__":
    sys.exit(main())
