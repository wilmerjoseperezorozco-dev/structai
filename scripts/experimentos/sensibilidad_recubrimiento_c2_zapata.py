"""Sensibilidad al recubrimiento de la zapata en ambiente costero C2 (f'c 35 MPa, único valor permitido por Tabla C.4.3.1).
NSR-10 C.7.7.6 NO da un número de recubrimiento para refuerzo no preesforzado en ambientes corrosivos ("debe aumentarse adecuadamente"); el 1.5x de
C.7.7.6.1 es solo para preesforzado. El mínimo normativo contra el suelo es 75 mm (C.7.7.1(a)). Los valores 100 y 125 mm son HIPÓTESIS de sensibilidad.
"""
from __future__ import annotations
import json, math, statistics as st, sys
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto")); sys.path.insert(0, str(Path(__file__).parent))
from src import zapata as z  # noqa: E402
from src import zapata_troncopiramidal as t  # noqa: E402
from src.viga import Materiales  # noqa: E402
import reoptimizar_zapata_costo_co2 as R  # noqa: E402

RECUBRIMIENTOS = (75.0, 100.0, 125.0)


def cands(args):
    p, q, rec = args
    c = 300.0 if p <= 600 else 400.0 if p <= 1500 else 500.0
    cargas = z.CargasZapata(P_serv=p, P_u=1.35 * p); suelo = z.Suelo(q_adm_kpa=q, profundidad_desplante_m=1.5); m = Materiales(35.0, 420.0, 420.0)
    out = [("prisma", b.volumen_concreto_m3, b.masa_acero_kg, 4 * (b.Lx / 1000) * (b.h / 1000)) for b in z.disenar(c, c, cargas, suelo, m, top=40, recubrimiento_mm=rec)]
    o = t.optimizar(c, cargas, suelo, m, recubrimiento_mm=rec)   # óptimo por volumen+acero; suficiente para esta sensibilidad
    if o:
        out.append(("tronco", o.volumen_m3, o.masa_acero_kg, o.area_encofrado_m2))
    return {"P": p, "q": q, "fc": 35.0, "rec": rec, "cand": out}


if __name__ == "__main__":
    with Pool() as pool:
        bl = pool.map(cands, list(product(R.CARGAS, R.QADM, RECUBRIMIENTOS)))
    res = {}
    for rec in RECUBRIMIENTOS:
        for en, esc in (("sin_ensayo", {"fc_min": 35.0, "amc_max": 0.40, "x_max": 0.0}), ("con_ensayo", {"fc_min": 35.0, "amc_max": 0.40, "x_max": 0.25})):
            filas = [R.analizar([b for b in bl if b["rec"] == rec], p, q, 150.0, 1.01, esc) for p, q in product(R.CARGAS, R.QADM)]
            res[f"rec{int(rec)}_{en}"] = {"base_cop_mediana": round(st.median(f["base_cop"] for f in filas)), "base_co2_mediana": round(st.median(f["base_co2"] for f in filas), 1),
                                          "ambos_min_co2_pct": round(st.median(f["ambos_min_co2_pct"] for f in filas), 1), "ambos_costo_pct": round(st.median(f["ambos_costo_pct"] for f in filas), 1)}
    (RAIZ / "docs/experimentos/sensibilidad_recubrimiento_c2_zapata_2026-11.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))
