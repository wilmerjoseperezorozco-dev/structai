"""
Índice numeral -> chunks de la NSR-10, a partir de los ENCABEZADOS dentro del
texto (issue #186). Solo lectura en Supabase; el índice se guarda como JSON
versionado y se regenera con este script.

Por qué existe: un chunk de nsr10_chunks suele contener varios numerales (el
de su `seccion` y sus subnumerales), pero solo se indexa por el primero. El
grafo normas_referencias_cruzadas resolvía las citas contra `seccion`, así que
marcaba "sin_destino" numerales cuyo texto sí estaba en el corpus: de 82,
72 tenían su encabezado dentro de otro chunk (verificado 2026-11-11).

Encabezado = el numeral al inicio de línea o tras un salto, seguido de un guion
largo o corto con texto, o de una mayúscula (forma de los textos verbatim:
"A.2.6.1.1 — Para períodos..."). Una mención dentro de una frase ("de acuerdo
con la sección F.4.2.2.2") NO cuenta como encabezado.

Uso: python scripts/evaluacion/golden/e5_grafo/indice_numerales.py
Salida: indice_numerales_nsr10.json  {numeral: [chunk_id, ...]}
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

RAIZ = Path(__file__).resolve().parents[4]
load_dotenv(RAIZ / "apps" / "api" / ".env")
AQUI = Path(__file__).parent

# numeral (A.2.6.1.1, A-3.2.5, F.4.2.3.1) como encabezado: inicio de texto o tras
# salto/espacio doble/punto, y seguido de " — Texto" / " - Texto" / " Texto en mayúscula".
RE_ENCABEZADO = re.compile(
    r"(?:^|\n|\s{2,}|(?<=[.:;)]\s))"
    r"((?:[A-K]\.|[A-K]-)\d+(?:\.\d+)*)"
    r"(?![\d.])\s*(?:[—–-]\s*[^\s\d]|[A-ZÁÉÍÓÚÑ(])"
)
RE_SECCION = re.compile(r"^\s*((?:[A-K]\.|[A-K]-)\d+(?:\.\d+)*)")


def main():
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    filas, off = [], 0
    while True:
        d = sb.table("nsr10_chunks").select("id,seccion,texto").like("id", "NSR10-%").range(off, off + 999).execute().data
        filas += d
        off += 1000
        if len(d) < 1000:
            break
    indice: dict[str, set[str]] = defaultdict(set)
    for f in filas:
        s = RE_SECCION.match(f.get("seccion") or "")
        if s:
            indice[s.group(1).upper()].add(f["id"])
        for m in RE_ENCABEZADO.finditer(f.get("texto") or ""):
            indice[m.group(1).upper()].add(f["id"])
    salida = {n: sorted(ids) for n, ids in sorted(indice.items())}
    (AQUI / "indice_numerales_nsr10.json").write_text(json.dumps(salida, ensure_ascii=False, indent=0), encoding="utf-8")
    por_seccion = sum(1 for f in filas if RE_SECCION.match(f.get("seccion") or ""))
    print(f"chunks NSR-10 leídos: {len(filas)} | con numeral en seccion: {por_seccion} | numerales indexados: {len(salida)}")


if __name__ == "__main__":
    main()
