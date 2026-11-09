"""Composición de camiones por estación de conteo del INVIAS (TPDS camiones por clase, 2006-2011).

Entrada: el libro 'cuadros de tráfico promedio diario' descargado de INVIAS (una hoja 'Camiones <territorial>' por territorial).
Salida: data/transporte/composicion_camiones_invias.csv (una fila por estación y año) y un resumen por territorial en pantalla.
Clases del INVIAS en el libro: C-2P, C-2G, C-3-4, C-5 y >C-5. Cada estación aparece con una fila de conteos y otra de proporciones.
Límites: son estaciones de conteo (no necesariamente peajes), la serie termina en 2011 y la suma entre estaciones cuenta varias veces el mismo
camión; sirve para la MEZCLA de camiones que circula, no para el parque registrado.
Uso: python scripts/transporte/composicion_camiones_invias.py <ruta.xlsx>
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "data" / "transporte" / "composicion_camiones_invias.csv"
CLASES = ("C-2P", "C-2G", "C-3-4", "C-5", ">C-5")


def _bloques(fila_anios: tuple) -> dict[int, int]:
    """año -> columna inicial del bloque de 6 columnas (total + 5 clases)."""
    out = {}
    for j, v in enumerate(fila_anios):
        m = re.search(r"A.O\s+(\d{4})", str(v or ""))
        if m:
            out[int(m.group(1))] = j
    return out


def leer(ruta: Path) -> list[dict]:
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    filas = []
    for ws in wb.worksheets:
        if not ws.title.lower().startswith("camiones"):
            continue
        r = list(ws.iter_rows(values_only=True))
        bl = _bloques(r[1]) if len(r) > 1 else {}
        if not bl:
            continue
        terr = ws.title.split(" ", 1)[1] if " " in ws.title else ws.title
        for fila in r[3:]:
            if not isinstance(fila[0], (int, float)) or not isinstance(fila[1], str):
                continue
            for anio, j in bl.items():
                vals = fila[j:j + 6]
                if len(vals) == 6 and all(isinstance(v, (int, float)) for v in vals):
                    filas.append({"territorial": terr, "estacion": int(fila[0]), "sector": fila[1].strip(), "anio": anio,
                                  "total": vals[0], **dict(zip(CLASES, vals[1:]))})
    return filas


def resumen(filas: list[dict], anio: int) -> dict[str, dict[str, float]]:
    acum: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for f in filas:
        if f["anio"] == anio:
            for c in CLASES:
                acum[f["territorial"]][c] += f[c]
            acum[f["territorial"]]["n"] += 1
    return acum


if __name__ == "__main__":
    filas = leer(Path(sys.argv[1]))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["territorial", "estacion", "sector", "anio", "total", *CLASES])
        w.writeheader()
        w.writerows(filas)
    print(len(filas), "filas;", len({f['estacion'] for f in filas}), "estaciones;", sorted({f['anio'] for f in filas}))
    res = resumen(filas, 2011)
    print("Mezcla de camiones 2011 (% de los camiones contados; n = estaciones)")
    print(f"{'territorial':24s}{'n':>4s}" + "".join(f"{c:>8s}" for c in CLASES))
    tot = defaultdict(float)
    for t, d in sorted(res.items()):
        s = sum(d[c] for c in CLASES)
        for c in CLASES:
            tot[c] += d[c]
        print(f"{t:24s}{int(d['n']):4d}" + "".join(f"{100 * d[c] / s:8.1f}" for c in CLASES))
    s = sum(tot.values())
    print(f"{'TOTAL':24s}{sum(int(d['n']) for d in res.values()):4d}" + "".join(f"{100 * tot[c] / s:8.1f}" for c in CLASES))
