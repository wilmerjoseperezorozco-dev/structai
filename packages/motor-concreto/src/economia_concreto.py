"""Modelo económico-ambiental del concreto (HIPÓTESIS de investigación; supuestos sin verificar marcados).

Mezcla: Abrams f_cm = 90/9^(a/c_ef), f_cm = f'c + 8.5 MPa, agua 190 kg/m3, ligante efectivo = cemento + 0.4·ceniza (k de EN 206), resistencia a 28 d.
Costo: ancla APU Barranquilla (consulta 2026-11-08) a ceniza = 0 + delta de cemento + ceniza (precio SUPUESTO, el APU no la tiene); el precio de 35 MPa
está extrapolado linealmente. CO2 (A1-A3): data/factores_emision/factores_emision_2026-11.json (cemento EPD 857 Argos 1.010; Pardo 2022 el resto).
"""
from __future__ import annotations

import math

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
