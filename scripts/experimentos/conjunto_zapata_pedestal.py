"""Corre el optimizador conjunto zapata+pedestal en 15 casos (P_serv x q_adm), 3 exposiciones C.4 y 2 objetivos. Guarda JSON y un DXF de ejemplo."""
from __future__ import annotations
import json, statistics as st, sys
from itertools import product
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
from src import zapata as z  # noqa: E402
from src.diseno_zapata_pedestal import EXPOSICIONES, optimizar_conjunto  # noqa: E402

CARGAS = (300.0, 600.0, 1000.0, 1500.0, 2500.0); QADM = (120.0, 200.0, 300.0)
filas = []
for p, q in product(CARGAS, QADM):
    c = 300.0 if p <= 600 else 400.0 if p <= 1500 else 500.0
    cg, su = z.CargasZapata(P_serv=p, P_u=1.35 * p), z.Suelo(q_adm_kpa=q, profundidad_desplante_m=1.5)
    for ex, obj in product(EXPOSICIONES, ("costo", "co2")):
        d = optimizar_conjunto(c, cg, su, exposicion=ex, objetivo=obj)
        filas.append({"P": p, "q": q, "c": c, "exposicion": ex, "objetivo": obj, "ok": d is not None} | (
            {} if d is None else {"fc": d.fc, "x": d.x_ceniza, "L": d.zapata.L_mm, "h_c": d.zapata.h_c_mm, "h_e": d.zapata.h_e_mm, "h_p": d.h_pedestal_mm,
                                  "pedestal": d.pedestal.barras, "cop": round(d.costo_cop), "co2": round(d.co2_kg, 1)}))
res = {}
for ex in EXPOSICIONES:
    a = {(f["P"], f["q"]): f for f in filas if f["exposicion"] == ex and f["objetivo"] == "costo"}
    b = {(f["P"], f["q"]): f for f in filas if f["exposicion"] == ex and f["objetivo"] == "co2"}
    ok = [k for k in a if a[k]["ok"] and b[k]["ok"]]
    res[ex] = {"casos_con_solucion": len(ok), "casos": len(a),
               "co2_opt_vs_cost_opt_co2_pct": round(st.median(100 * (1 - b[k]["co2"] / a[k]["co2"]) for k in ok), 1) if ok else None,
               "co2_opt_vs_cost_opt_costo_pct_extra": round(st.median(100 * (b[k]["cop"] / a[k]["cop"] - 1) for k in ok), 1) if ok else None,
               "sin_solucion": [list(k) for k in a if not (a[k]["ok"] and b[k]["ok"])]}
(RAIZ / "docs/experimentos/conjunto_zapata_pedestal_2026-11.json").write_text(json.dumps({"resumen": res, "casos": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False, indent=1))
