"""Re-optimización de zapata por costo y CO2 con dosificación variable (HIPÓTESIS, no método aprobado).

Variables: geometría (prismática o troncopiramidal), f'c ∈ {21,28,35} MPa y fracción de ceniza volante x ∈ {0,.1,.2,.3} del ligante.
Modelo de mezcla (supuestos SIN verificar contra el corpus ni ensayos): Abrams f_cm = 90/9^(a/c_ef); f_cm = f'c + 8.5 MPa; agua 190 kg/m3;
ligante efectivo = cemento + 0.4·ceniza (k de EN 206); resistencia a 28 d. Costo: ancla APU Barranquilla del concreto a x=0 + delta de cemento (223.5 COP/kg)
+ ceniza (precio SUPUESTO por escenario; no hay precio en el APU). CO2: factores de data/factores_emision (cemento 0.892 / 1.010).
Línea base = zapata PRISMÁTICA de mínimo costo con x=0 (mejor f'c). Uso: python scripts/experimentos/reoptimizar_zapata_costo_co2.py
"""
from __future__ import annotations
import json, math, statistics as st, sys
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "packages" / "motor-concreto"))
from src import zapata as z  # noqa: E402
from src import zapata_troncopiramidal as t  # noqa: E402
from src.viga import Materiales  # noqa: E402

CARGAS = (300.0, 600.0, 1000.0, 1500.0, 2500.0); QADM = (120.0, 200.0, 300.0); FCS = (21.0, 28.0, 35.0); FA_X = (0.0, 0.1, 0.2, 0.25, 0.3)
PRECIO_ANCLA = {21.0: 688_796.0, 28.0: 822_510.0, 35.0: 822_510.0 + (822_510.0 - 688_796.0)}  # 35 extrapolado linealmente (SUPUESTO)
PRECIO_CEMENTO = 223.5; PRECIO_ACERO = 4_151.0; PRECIO_ENC = 23_500.0   # COP/kg, COP/kg, COP/m2 (encofrado solo material, punto medio 20-27 mil)
PRECIO_CENIZA = {"ceniza_150": 150.0, "ceniza_300": 300.0}                # COP/kg SUPUESTOS (sin dato)
FE = {"grueso": 0.0020, "fino": 0.0080, "agua": 0.0013, "ceniza": 0.015, "aditivo": 0.511, "acero": 1.322}
FE_CEM = {"0.892": 0.892, "1.010": 1.010}
AGUA, ADITIVO_FRAC = 190.0, 0.008


def mezcla(fc: float, x: float) -> dict:
    wc = math.log(90.0 / (fc + 8.5)) / math.log(9.0)
    b = AGUA / (wc * (1 - 0.6 * x))
    cem, ash = (1 - x) * b, x * b
    vol_agg = 1000.0 - cem / 3.15 - ash / 2.2 - AGUA - 20.0
    agg = vol_agg * 2.65
    return {"cem": cem, "ash": ash, "gru": 0.55 * agg, "fin": 0.45 * agg, "ref_cem": AGUA / wc, "wc": wc}


def costo_m3(fc, x, p_ash):
    m = mezcla(fc, x)
    return PRECIO_ANCLA[fc] + (m["cem"] - m["ref_cem"]) * PRECIO_CEMENTO + m["ash"] * p_ash


def co2_m3(fc, x, fe_cem):
    m = mezcla(fc, x)
    return m["cem"] * fe_cem + m["ash"] * FE["ceniza"] + m["gru"] * FE["grueso"] + m["fin"] * FE["fino"] + AGUA * FE["agua"] + (m["cem"] + m["ash"]) * ADITIVO_FRAC * FE["aditivo"]


def candidatos(args):
    p, q, fc = args
    c = 300.0 if p <= 600 else 400.0 if p <= 1500 else 500.0
    cargas = z.CargasZapata(P_serv=p, P_u=1.35 * p); suelo = z.Suelo(q_adm_kpa=q, profundidad_desplante_m=1.5); m = Materiales(fc, 420.0, 420.0)
    out = []
    for b in z.disenar(c, c, cargas, suelo, m, top=40):
        out.append(("prisma", b.volumen_concreto_m3, b.masa_acero_kg, 4 * (b.Lx / 1000) * (b.h / 1000)))
    A_min = p / q; L0 = max(math.ceil(math.sqrt(A_min) * 1000 / 50) * 50, c + 200.0); primera = None
    for L in np.arange(L0, 6000.0 + 1, 50.0):
        if primera is not None and L > primera + 600.0:
            break
        for hc in np.arange(300.0, 1001.0, 50.0):
            for he in np.arange(300.0, hc + 1, 50.0):
                r = t.verificar(float(L), float(hc), float(he), c, cargas, suelo, m)
                if r.cumple:
                    primera = L if primera is None else primera
                    out.append(("tronco", r.volumen_m3, r.masa_acero_kg, r.area_encofrado_m2))
    return {"P": p, "q": q, "fc": fc, "cand": out}


def evaluar(cand, fc, x, p_ash, fe_cem):
    _, vol, acero, enc = cand
    cop = vol * costo_m3(fc, x, p_ash) + acero * PRECIO_ACERO + enc * PRECIO_ENC
    co2 = vol * co2_m3(fc, x, fe_cem) + acero * FE["acero"]
    return cop, co2


# Escenarios de durabilidad NSR-10 C.4 (Tablas C.4.2.1 y C.4.3.1, verificadas en las imágenes de C-35/C-36). a/mc = agua / TOTAL de materiales cementantes (C.4.1.1).
# NSR-10 no fija un tope de ceniza fuera de la clase F3 (25 %, Tabla C.4.4.2, congelamiento: no aplica en Colombia). x_max 0.25 es un tope de diseño
# conservador POR ANALOGÍA. En S1 (agua marina) solo se permiten cementos tipo II/IP(MS)/MS: con ceniza añadida en obra se exige ensayo C.4.5.1 -> x_max 0 si no se ensaya.
ESCENARIOS = {
    "interior_C1_S0": {"fc_min": 17.0, "amc_max": 0.50, "x_max": 0.25},
    "costa_C2_S1_sin_ensayo": {"fc_min": 35.0, "amc_max": 0.40, "x_max": 0.0},
    "costa_C2_S1_con_ensayo": {"fc_min": 35.0, "amc_max": 0.40, "x_max": 0.25},
    "sin_durabilidad_C4_ni_tope": {"fc_min": 0.0, "amc_max": 9.9, "x_max": 0.30},  # reproduce la corrida previa
}


def analizar(bloques, p, q, p_ash, fe_cem, esc):
    pts = []   # (cop, co2, tipo, fc, x)
    for b in (b for b in bloques if b["P"] == p and b["q"] == q and b["fc"] >= esc["fc_min"]):
        for cand in b["cand"]:
            for x in FA_X:
                m = mezcla(b["fc"], x)
                if x > esc["x_max"] + 1e-9 or AGUA / (m["cem"] + m["ash"]) > esc["amc_max"] + 1e-9:
                    continue
                cop, co2 = evaluar(cand, b["fc"], x, p_ash, fe_cem)
                pts.append((cop, co2, cand[0], b["fc"], x))
    base = min((pt for pt in pts if pt[2] == "prisma" and pt[4] == 0.0), key=lambda a: a[0])
    solo_geo = min((pt for pt in pts if pt[4] == 0.0), key=lambda a: a[0])
    solo_mezcla = min((pt for pt in pts if pt[2] == "prisma"), key=lambda a: a[1])
    ambos_co2 = min(pts, key=lambda a: a[1])
    igual_costo = min((pt for pt in pts if pt[0] <= base[0]), key=lambda a: a[1])
    f = lambda a, r: round(100 * (1 - a / r), 1)
    return {"P": p, "q": q, "base_cop": round(base[0]), "base_co2": round(base[1], 1), "base_fc": base[3],
            "geometria_sola_min_cop_pct": f(solo_geo[0], base[0]),
            "mezcla_sola_min_co2_pct": f(solo_mezcla[1], base[1]), "mezcla_sola_costo_pct": f(solo_mezcla[0], base[0]),
            "ambos_min_co2_pct": f(ambos_co2[1], base[1]), "ambos_costo_pct": f(ambos_co2[0], base[0]), "ambos_sel": ambos_co2[2:],
            "a_igual_costo_co2_pct": f(igual_costo[1], base[1]), "a_igual_costo_sel": igual_costo[2:]}


if __name__ == "__main__":
    with Pool() as pool:
        bloques = pool.map(candidatos, list(product(CARGAS, QADM, FCS)))
    res = {}
    for esc_n, esc in ESCENARIOS.items():
        pa, fe = 150.0, ("1.010", 1.010)
        filas = [analizar(bloques, p, q, pa, fe[1], esc) for p, q in product(CARGAS, QADM)]
        clave = f"{esc_n}"
        res[clave] = {"casos": filas, "mediana": {k: round(st.median(f[k] for f in filas), 1) for k in
                      ("geometria_sola_min_cop_pct", "mezcla_sola_min_co2_pct", "mezcla_sola_costo_pct", "ambos_min_co2_pct", "ambos_costo_pct", "a_igual_costo_co2_pct")}}
    (RAIZ / "docs/experimentos/reoptimizacion_zapata_durabilidad_2026-11.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v["mediana"] for k, v in res.items()}, indent=1))
    ej = res["costa_C2_S1_con_ensayo"]["casos"]
    print(json.dumps([e for e in ej if e["q"] == 200.0], ensure_ascii=False, indent=0))
    print({fc: {x: (round(mezcla(fc, x)["cem"]), round(co2_m3(fc, x, 1.01))) for x in FA_X} for fc in FCS})
