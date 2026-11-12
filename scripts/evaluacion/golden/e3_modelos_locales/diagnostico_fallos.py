"""
Diagnóstico de los fallos de E3 que NO son de configuración (#172). Sin LLM, solo lectura.

Para cada caso donde el hecho esperado no llegó al contexto (recuperacion_<modelo>.jsonl,
hecho_en_contexto = False) responde: ¿el hecho existe en nsr10_chunks?
  - Si existe: fallo de RECUPERACIÓN (el chunk está, el buscador no lo trae) → se arregla en
    el buscador (consulta, reranker, top_k), no en el modelo.
  - Si no existe: HUECO DE CORPUS → se arregla ingiriendo (plan de huecos).
Se busca cada variante del test con ILIKE en el prefijo del título del caso.

Uso: python diagnostico_fallos.py [--modelo qwen2.5:7b]
"""
from __future__ import annotations

import argparse
import json

import correr_bateria as cb

r = cb.r


def buscar(variantes: list[str], prefijo: str) -> list[dict]:
    hallados = []
    for v in variantes:
        filas = (r.sb.table("nsr10_chunks").select("id,seccion").ilike("id", f"{prefijo}%")
                 .ilike("texto", f"%{v}%").limit(3).execute().data)
        for f in filas:
            hallados.append({"variante": v, **f})
        if hallados:
            break
    return hallados


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="qwen2.5:7b")
    a = ap.parse_args()
    rec = [json.loads(l) for l in (cb.RESULTADOS / f"recuperacion_{a.modelo.replace(':', '_')}.jsonl")
           .read_text(encoding="utf-8").splitlines()]
    casos = {c["id"]: c for c in cb.cargar_casos("nsr10")}
    print("| Caso | ¿Hecho en el corpus? | Dónde | Diagnóstico |\n|---|---|---|---|")
    for f in rec:
        if f["hecho_en_contexto"]:
            continue
        c = casos[f["id"]]
        prefijo = "NSR10-" + f["titulo"] + "-" if len(f["titulo"]) == 1 else f["titulo"]
        h = buscar(c["variantes"], prefijo)
        donde = "; ".join(f"{x['id']} §{x['seccion']} ({x['variante']!r})" for x in h[:2]) or "—"
        diag = "recuperación (está y no se trae)" if h else "hueco de corpus o variante no literal"
        print(f"| {f['id']} | {'sí' if h else 'no'} | {donde} | {diag} |")


if __name__ == "__main__":
    main()
