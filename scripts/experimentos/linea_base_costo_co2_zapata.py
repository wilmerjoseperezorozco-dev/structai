"""Línea base costo (APU Barranquilla) + CO2 (A1-A3) de la zapata prismática vs troncopiramidal.
Lee docs/experimentos/desperdicio_zapata_2026-11.json (geometrías ya optimizadas por volumen+acero) y las evalúa con precios y factores.
NO re-optimiza por costo/CO2: es la línea base contra la que se medirá el diseño inverso.
Precios: RPC buscar_precios_apu, región Barranquilla, consultados 2026-11-08 (ver PRECIOS). Factores: data/factores_emision/factores_emision_2026-11.json.
"""
from __future__ import annotations
import json, statistics as st, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]

# COP. Concreto: actividades APU Barranquilla. f'c 28 NO tiene precio de zapata: se usa "Concreto para vigas f'c=28" como sustituto (supuesto).
PRECIOS = {
    "concreto_cop_m3": {21.0: 688_796, 28.0: 822_510},
    "acero_cop_kg": 4_151,                     # actividad "ACERO DE REFUERZO fy = 420 Mpa"
    "encofrado_cop_m2": {"bajo": 20_000, "alto": 27_000},  # insumo "ENCONFRADO EN MADERA" (solo material; sin mano de obra: subestima)
}
# SUPUESTO sin fuente verificada: dosificación kg por m3 de concreto.
MEZCLA = {21.0: {"cemento": 350, "grueso": 1000, "fino": 800, "agua": 190}, 28.0: {"cemento": 420, "grueso": 980, "fino": 780, "agua": 190}}
FE = {"grueso": 0.0020, "fino": 0.0080, "agua": 0.0013}      # Pardo 2022 Tabla 2 (secundaria)
FE_CEMENTO = {"bajo_0.892": 0.892, "alto_1.010": 1.010}       # Pardo 2022 / EPD 857 Argos Cartagena
FE_ACERO = 1.322                                              # Pardo 2022 (secundaria); Paz del Río 0.850 NO verificado


def co2_m3(fc: float, fe_cem: float) -> float:
    m = MEZCLA[fc]
    return m["cemento"] * fe_cem + sum(m[k] * FE[k] for k in FE)


def evaluar(g: dict, fc: float, fe_cem: float, enc: float) -> dict:
    cop = g["vol"] * PRECIOS["concreto_cop_m3"][fc] + g["acero"] * PRECIOS["acero_cop_kg"] + g["encofrado"] * enc
    co2 = g["vol"] * co2_m3(fc, fe_cem) + g["acero"] * FE_ACERO
    return {"cop": cop, "co2_kg": co2}


filas = [f for f in json.loads((RAIZ / "docs/experimentos/desperdicio_zapata_2026-11.json").read_text(encoding="utf-8"))["casos"] if "prisma" in f]
res = []
for f in filas:
    esc = {}
    for nc, fe in FE_CEMENTO.items():
        a, b = evaluar(f["prisma"], f["fc"], fe, PRECIOS["encofrado_cop_m2"]["bajo"]), evaluar(f["tronco"], f["fc"], fe, PRECIOS["encofrado_cop_m2"]["bajo"])
        esc[nc] = {"prisma": a, "tronco": b, "ahorro_co2_pct": 100 * (1 - b["co2_kg"] / a["co2_kg"])}
    ab = {k: evaluar(f["prisma"], f["fc"], 1.01, v) for k, v in PRECIOS["encofrado_cop_m2"].items()}
    tb = {k: evaluar(f["tronco"], f["fc"], 1.01, v) for k, v in PRECIOS["encofrado_cop_m2"].items()}
    res.append({"P_serv": f["P_serv"], "q_adm": f["q_adm"], "fc": f["fc"], "co2": esc,
                "ahorro_cop_pct": {k: 100 * (1 - tb[k]["cop"] / ab[k]["cop"]) for k in ab}, "cop_prisma_bajo": ab["bajo"]["cop"],
                "cop_tronco_bajo": tb["bajo"]["cop"], "co2_kg_prisma_alto": esc["alto_1.010"]["prisma"]["co2_kg"]})

def est(v): return {"min": round(min(v), 1), "mediana": round(st.median(v), 1), "max": round(max(v), 1)}
resumen = {"casos": len(res),
           "ahorro_co2_pct_cemento_0.892": est([r["co2"]["bajo_0.892"]["ahorro_co2_pct"] for r in res]),
           "ahorro_co2_pct_cemento_1.010": est([r["co2"]["alto_1.010"]["ahorro_co2_pct"] for r in res]),
           "ahorro_cop_pct_encofrado_20000": est([r["ahorro_cop_pct"]["bajo"] for r in res]),
           "ahorro_cop_pct_encofrado_27000": est([r["ahorro_cop_pct"]["alto"] for r in res]),
           "por_carga_ahorro_cop_pct_mediana": {str(p): round(st.median([r["ahorro_cop_pct"]["bajo"] for r in res if r["P_serv"] == p]), 1) for p in sorted({r["P_serv"] for r in res})},
           "por_carga_ahorro_co2_pct_mediana": {str(p): round(st.median([r["co2"]["alto_1.010"]["ahorro_co2_pct"] for r in res if r["P_serv"] == p]), 1) for p in sorted({r["P_serv"] for r in res})},
           "co2_kg_por_m3": {str(fc): {k: round(co2_m3(fc, v), 1) for k, v in FE_CEMENTO.items()} for fc in MEZCLA}}
salida = RAIZ / "docs/experimentos/linea_base_costo_co2_zapata_2026-11.json"
salida.write_text(json.dumps({"precios": {k: {str(a): b for a, b in v.items()} if isinstance(v, dict) else v for k, v in PRECIOS.items()}, "resumen": resumen, "casos": res}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(resumen, ensure_ascii=False, indent=1))
