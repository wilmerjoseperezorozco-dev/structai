"""
Experimento 2026-11-08: ¿cuánto concreto "sobra" en una zapata prismática diseñada con NSR-10?

Compara, sobre una malla de cargas y suelos, el mínimo prismático (`zapata.disenar`) contra el mínimo troncopiramidal
(`zapata_troncopiramidal.optimizar`), con las mismas verificaciones y la misma función objetivo (volumen + masa de acero/7850).
No usa precios ni factores de CO2 (sin fuente verificada todavía).

Uso:  python scripts/experimentos/desperdicio_zapata.py [--salida docs/experimentos/desperdicio_zapata_2026-11.json]
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import time
from itertools import product
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))

from src import zapata as z  # noqa: E402
from src import zapata_troncopiramidal as t  # noqa: E402
from src.viga import Materiales  # noqa: E402

P_SERV = (300.0, 600.0, 1000.0, 1500.0, 2500.0)       # kN
Q_ADM = (120.0, 200.0, 300.0)                          # kPa
FC = (21.0, 28.0)                                      # MPa
RELACION_PU_PS = 1.35                                  # supuesto: mezcla típica de 1,2D+1,6L con D≈0,6·P_serv
DESPLANTE_M = 1.5


def columna_para(p_serv: float) -> float:
    return 300.0 if p_serv <= 600 else 400.0 if p_serv <= 1500 else 500.0


def correr() -> list[dict]:
    filas = []
    for p, q, fc in product(P_SERV, Q_ADM, FC):
        c = columna_para(p)
        cargas = z.CargasZapata(P_serv=p, P_u=p * RELACION_PU_PS)
        suelo = z.Suelo(q_adm_kpa=q, profundidad_desplante_m=DESPLANTE_M)
        m = Materiales(fc, 420.0, 420.0)
        t0 = time.time()
        base = z.disenar(c, c, cargas, suelo, m)
        opt = t.optimizar(c, cargas, suelo, m)
        if not base or opt is None:
            filas.append({"P_serv": p, "q_adm": q, "fc": fc, "c": c, "nota": "sin solución en la rejilla"})
            continue
        b = base[0]
        a_enc_prisma = 4 * (b.Lx / 1000) * (b.h / 1000)
        filas.append({
            "P_serv": p, "q_adm": q, "fc": fc, "c": c,
            "prisma": {"L": b.Lx, "h": b.h, "vol": b.volumen_concreto_m3, "acero": b.masa_acero_kg, "encofrado": a_enc_prisma},
            "tronco": {"L": opt.L_mm, "h_c": opt.h_c_mm, "h_e": opt.h_e_mm, "vol": opt.volumen_m3, "acero": opt.masa_acero_kg,
                       "encofrado": opt.area_encofrado_m2, "angulo": opt.angulo_talud_grados},
            "ahorro_concreto_pct": 100 * (1 - opt.volumen_m3 / b.volumen_concreto_m3),
            "ahorro_acero_pct": 100 * (1 - opt.masa_acero_kg / b.masa_acero_kg),
            "delta_encofrado_pct": 100 * (opt.area_encofrado_m2 / a_enc_prisma - 1),
            "segundos": round(time.time() - t0, 1),
        })
    return filas


def resumir(filas: list[dict]) -> dict:
    ok = [f for f in filas if "prisma" in f]
    def est(k):
        v = [f[k] for f in ok]
        return {"min": min(v), "mediana": st.median(v), "media": st.mean(v), "max": max(v)}
    return {"casos": len(filas), "casos_con_solucion": len(ok), "ahorro_concreto_pct": est("ahorro_concreto_pct"),
            "ahorro_acero_pct": est("ahorro_acero_pct"), "delta_encofrado_pct": est("delta_encofrado_pct"),
            "angulos_grados": [round(f["tronco"]["angulo"], 1) for f in ok]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=str(RAIZ / "docs" / "experimentos" / "desperdicio_zapata_2026-11.json"))
    args = ap.parse_args()
    filas = correr()
    res = resumir(filas)
    Path(args.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(args.salida).write_text(json.dumps({"resumen": res, "casos": filas}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))
