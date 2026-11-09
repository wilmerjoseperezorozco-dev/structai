"""Auditoría por páginas de la NSR-10: numerales-encabezado de los PDF fuente vs. numerales presentes en `nsr10_chunks`.

Uso: python scripts/ingesta/nsr10/auditoria_paginas.py --db-json <archivo con filas {"n":..,"c":..}> --out docs/AUDITORIA_NSR10_PAGINAS_2026-11.md
El PDF no se versiona (raw/ está en .gitignore); el reporte solo contiene numerales y conteos, no texto normativo.
Un «faltante» es un candidato: la regla del proyecto exige verificar a mano cada uno antes de ingestar
(falsos positivos conocidos: remisiones cruzadas, numerales que el documento fuente imprime mal).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages" / "rag-audit-kit"))
from src.cobertura import _cubierto  # noqa: E402

ENCABEZADO = re.compile(r"^\s*([A-K]\.\d{1,3}(?:\.\d{1,3}){0,6})\s*[—–\-]\s*\S")
RAW = ROOT / "scripts" / "ingesta" / "nsr10" / "raw"


def numerales_pdf() -> dict[str, str]:
    import pypdf
    out: dict[str, str] = {}
    for pdf in sorted(RAW.glob("NSR-10-*.pdf")):
        try:
            lector = pypdf.PdfReader(str(pdf))
            texto = "\n".join((p.extract_text() or "") for p in lector.pages)
        except Exception as exc:                              # PDF corrupto: se reporta, no se oculta
            print(f"!! {pdf.name}: {exc}", file=sys.stderr)
            continue
        for linea in texto.splitlines():
            m = ENCABEZADO.match(linea)
            if m and m.group(1) not in out:
                out[m.group(1)] = pdf.name
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default="")
    ap.add_argument("--mencionados", default="", help="archivo con numerales que aparecen en seccion o texto de algún chunk (más estricto contra falsos huecos)")
    a = ap.parse_args()
    crudo = Path(a.db_json).read_text(encoding="utf8")
    db = {n: (int(c), int(ch)) for n, c, ch in re.findall(r'"n":"([^"]+)","c":(\d+),"chars":(\d+)', crudo.replace('\\"', '"'))}
    cache = Path(a.cache) if a.cache else None
    if cache and cache.exists():
        fuente = json.loads(cache.read_text(encoding="utf8"))
    else:
        fuente = numerales_pdf()
        if cache:
            cache.write_text(json.dumps(fuente), encoding="utf8")
    estrictos = list(db)
    cubiertos = list(db)
    if a.mencionados:
        m = Path(a.mencionados).read_text(encoding="utf8")
        cubiertos = list(set(cubiertos) | set(re.findall(r'"n":"([A-K]\.[0-9.]+)"', m.replace('\\"', '"'))))
    por_cap: dict[str, list[str]] = defaultdict(list)
    por_cap_est: dict[str, list[str]] = defaultdict(list)
    for n in fuente:
        cap_n = ".".join(n.split(".")[:2])
        if not _cubierto(n, cubiertos):
            por_cap[cap_n].append(n)
        if not _cubierto(n, estrictos):
            por_cap_est[cap_n].append(n)
    tot_cap: dict[str, int] = defaultdict(int)
    for n in fuente:
        tot_cap[".".join(n.split(".")[:2])] += 1
    lineas = ["# Auditoría por páginas de la NSR-10 (numerales-encabezado, 2026-11-08)", "",
              f"PDF fuente: {len(set(fuente.values()))} archivos; {len(fuente)} numerales-encabezado únicos. Base: {len(db)} numerales distintos en `nsr10_chunks`.", "",
              "Candidatos a hueco por capítulo (verificar a mano antes de ingestar; el patrón de encabezado puede perder numerales y capturar referencias).", "",
              "«Sin sección» = ningún chunk tiene ese numeral como `seccion` (cota superior del hueco; los rangos «X a Y» y los chunks agrupados inflan este número). «Nunca mencionado» = el numeral no aparece ni en `seccion` ni en el texto de ningún chunk (cota inferior: una remisión cruzada lo da por cubierto).", "",
              "| Capítulo | Numerales en el PDF | Sin sección | Nunca mencionado | Ejemplos nunca mencionados |", "|---|---|---|---|---|"]
    clave = lambda c: (c[0], int(c.split(".")[1]))
    for cap in sorted(tot_cap, key=clave):
        f = por_cap.get(cap, [])
        lineas.append(f"| {cap} | {tot_cap[cap]} | {len(por_cap_est.get(cap, []))} | {len(f)} | {', '.join(f[:6])}{' …' if len(f) > 6 else ''} |")
    Path(a.out).write_text("\n".join(lineas) + "\n", encoding="utf8")
    Path(a.out).with_suffix(".json").write_text(json.dumps({"nunca_mencionado": {c: sorted(v) for c, v in por_cap.items()}, "sin_seccion": {c: sorted(v) for c, v in por_cap_est.items()}}, indent=0), encoding="utf8")
    print(len(fuente), sum(len(v) for v in por_cap.values()))


if __name__ == "__main__":
    main()
