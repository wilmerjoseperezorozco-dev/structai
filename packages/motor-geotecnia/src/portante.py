"""Capacidad portante general de cimentaciones superficiales (Vesić, 1973) con factores de forma y profundidad.

q_ult = c·Nc·sc·dc·ic + q·Nq·sq·dq·iq + ½·γ'·B'·Nγ·sγ·iγ. El Título H de la NSR-10 no entrega una fórmula de
capacidad portante: este motor la calcula con la teoría clásica y el resultado NO sustituye el estudio geotécnico (H.4.2.3).

`capacidad_portante_general` supone carga vertical y centrada. `capacidad_portante_excentrica_inclinada` considera la
excentricidad, que H.4.10 obliga a tener en cuenta en la capacidad ante falla, con el área efectiva de Meyerhof
(B' = B − 2·eB, L' = L − 2·eL). Una carga horizontal en la dirección de B se trata con los factores de inclinación de
Vesić (1975): m = (2 + B'/L')/(1 + B'/L'), iq = [1 − H/(V + A'·c·cot φ)]^m, iγ = [1 − H/(V + A'·c·cot φ)]^(m+1),
ic = iq − (1 − iq)/(Nc·tan φ) (φ > 0) o ic = 1 − m·H/(A'·c·Nc) (φ = 0).
"""
from __future__ import annotations

import math
from typing import Optional

from .esfuerzos import GAMMA_AGUA_KN_M3

PHI_MAX_DEG = 45.0
_REF = "Vesić (1973) / NSR-10 Título H (H.4)"


def _requerir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(f"{mensaje} ({_REF}).")


def factores_capacidad(phi_deg: float) -> tuple[float, float, float]:
    """(Nc, Nq, Nγ) de Vesić. Nc → π+2 cuando φ → 0."""
    _requerir(0.0 <= phi_deg <= PHI_MAX_DEG, f"El ángulo de fricción debe estar en [0°, {PHI_MAX_DEG}°]; se recibió {phi_deg}")
    phi = math.radians(phi_deg)
    nq = math.exp(math.pi * math.tan(phi)) * math.tan(math.pi / 4 + phi / 2) ** 2
    nc = math.pi + 2.0 if phi_deg == 0.0 else (nq - 1.0) / math.tan(phi)
    ng = 2.0 * (nq + 1.0) * math.tan(phi)
    return nc, nq, ng


def _pesos_con_agua(gamma: float, gamma_sat: Optional[float], nf: Optional[float], Df: float, B: float) -> tuple[float, float]:
    """(sobrecarga q a nivel de desplante, γ' efectivo bajo la base) considerando el nivel freático."""
    if nf is None:
        return gamma * Df, gamma
    _requerir(gamma_sat is not None, "Con nivel freático se requiere el peso unitario saturado")
    _requerir(math.isfinite(gamma_sat) and gamma_sat > GAMMA_AGUA_KN_M3 and gamma_sat >= gamma,
              f"El peso unitario saturado debe ser finito, mayor que el del agua ({GAMMA_AGUA_KN_M3} kN/m³) y no menor que el seco; se recibió {gamma_sat!r}")
    _requerir(math.isfinite(nf) and nf >= 0, "La profundidad del nivel freático debe ser finita y no negativa")
    sumergido = gamma_sat - GAMMA_AGUA_KN_M3
    q = gamma * Df if nf >= Df else gamma * nf + sumergido * (Df - nf)
    if nf <= Df:
        g_ef = sumergido
    elif nf < Df + B:
        g_ef = sumergido + (nf - Df) / B * (gamma - sumergido)
    else:
        g_ef = gamma
    return q, g_ef


def capacidad_portante_general(*, c_kpa: float, phi_deg: float, gamma_kn_m3: float, B_m: float, L_m: Optional[float],
                               Df_m: float, nivel_freatico_m: Optional[float],
                               gamma_sat_kn_m3: Optional[float] = None) -> dict:
    """q_ult (kPa) de una zapata de ancho B (L_m=None → corrida). Todos los parámetros físicos son obligatorios."""
    _requerir(math.isfinite(c_kpa) and c_kpa >= 0, "La cohesión debe ser finita y no negativa")
    _requerir(math.isfinite(gamma_kn_m3) and gamma_kn_m3 > 0, "El peso unitario debe ser finito y positivo")
    _requerir(math.isfinite(B_m) and B_m > 0, "El ancho B debe ser finito y positivo")
    _requerir(math.isfinite(Df_m) and Df_m >= 0, "La profundidad de desplante debe ser finita y no negativa")
    _requerir(L_m is None or (math.isfinite(L_m) and L_m >= B_m), "Para zapata rectangular se requiere L finita y L ≥ B (B es la dimensión menor)")
    nc, nq, ng = factores_capacidad(phi_deg)
    phi = math.radians(phi_deg)
    t, s = math.tan(phi), math.sin(phi)
    razon = 0.0 if L_m is None else B_m / L_m
    sc = 1.0 + razon * nq / nc
    sq = 1.0 + razon * t
    sg = 1.0 - 0.4 * razon
    k = Df_m / B_m if Df_m <= B_m else math.atan(Df_m / B_m)
    dq = 1.0 + 2.0 * t * (1.0 - s) ** 2 * k
    dc = 1.0 + 0.4 * k if phi_deg == 0.0 else dq - (1.0 - dq) / (nc * t)
    q, g_ef = _pesos_con_agua(gamma_kn_m3, gamma_sat_kn_m3, nivel_freatico_m, Df_m, B_m)
    q_ult = c_kpa * nc * sc * dc + q * nq * sq * dq + 0.5 * g_ef * B_m * ng * sg
    _requerir(q_ult > 0, "La capacidad portante resultante es nula o negativa (suelo sin cohesión ni sobrecarga a nivel de desplante): no hay capacidad que verificar")
    return {"q_ult_kpa": q_ult, "Nc": nc, "Nq": nq, "Ng": ng, "sc": sc, "sq": sq, "sg": sg, "dc": dc, "dq": dq,
            "sobrecarga_kpa": q, "gamma_efectivo_kn_m3": g_ef}


def _factores_inclinacion(*, phi_deg: float, c_kpa: float, V_kn: float, H_kn: float, area_ef_m2: float, nc: float,
                          razon_ef: float) -> tuple[float, float, float, float]:
    """(ic, iq, iγ, m) de Vesić (1975). razon_ef = (dimensión efectiva paralela a H)/(la otra); corrida: 0 → m = 2."""
    m = (2.0 + razon_ef) / (1.0 + razon_ef)
    if H_kn == 0.0:
        return 1.0, 1.0, 1.0, m
    if phi_deg == 0.0:
        _requerir(c_kpa > 0, "Con φ = 0 y carga horizontal se requiere cohesión para resistirla")
        ic = 1.0 - m * H_kn / (area_ef_m2 * c_kpa * nc)
        _requerir(ic > 0, "La carga horizontal agota la resistencia al deslizamiento de la base (ic ≤ 0)")
        return ic, 1.0, 1.0, m
    phi = math.radians(phi_deg)
    base = 1.0 - H_kn / (V_kn + area_ef_m2 * c_kpa / math.tan(phi))
    _requerir(base > 0, "La carga horizontal supera la resistencia disponible (1 − H/(V + A'·c·cot φ) ≤ 0)")
    iq = base ** m
    ig = base ** (m + 1.0)
    ic = iq - (1.0 - iq) / (nc * math.tan(phi))
    return ic, iq, ig, m


def capacidad_portante_excentrica_inclinada(*, c_kpa: float, phi_deg: float, gamma_kn_m3: float, B_m: float,
                                            L_m: Optional[float], Df_m: float, nivel_freatico_m: Optional[float],
                                            V_kn: float, H_kn: float, eB_m: float, eL_m: float,
                                            gamma_sat_kn_m3: Optional[float] = None) -> dict:
    """Carga última (kN; kN/m en corrida) con área efectiva de Meyerhof y factores de inclinación de Vesić.

    V_kn: carga vertical; H_kn ≥ 0: carga horizontal en la dirección de B; eB, eL ≥ 0: excentricidades. Los factores
    de profundidad usan B real (Df/B) y los de forma, B'/L'.
    """
    for nombre, v in (("V", V_kn), ("H", H_kn), ("eB", eB_m), ("eL", eL_m)):
        _requerir(math.isfinite(v), f"{nombre} debe ser finito")
    _requerir(V_kn > 0, "La carga vertical V debe ser positiva")
    _requerir(H_kn >= 0, "La carga horizontal H no puede ser negativa (se toma su magnitud en la dirección de B)")
    _requerir(eB_m >= 0 and eL_m >= 0, "Las excentricidades se dan en valor absoluto (≥ 0)")
    _requerir(math.isfinite(B_m) and B_m > 0, "El ancho B debe ser finito y positivo")
    _requerir(2.0 * eB_m < B_m, "eB ≥ B/2: la resultante cae fuera de la base")
    _requerir(L_m is None or (math.isfinite(L_m) and L_m >= B_m),
              "Para zapata rectangular se requiere L finita y L ≥ B (B es la dimensión menor)")
    _requerir(L_m is not None or eL_m == 0.0, "La zapata corrida no admite excentricidad en la dirección de L")
    _requerir(L_m is None or 2.0 * eL_m < L_m, "eL ≥ L/2: la resultante cae fuera de la base")
    b_ef = B_m - 2.0 * eB_m
    l_ef = None if L_m is None else L_m - 2.0 * eL_m
    # m de Vesić con H paralela a B: (dimensión efectiva paralela a H)/(la otra), aunque luego B' y L' se intercambien
    razon_m = 0.0 if l_ef is None else b_ef / l_ef
    if l_ef is not None and l_ef < b_ef:          # la dimensión menor efectiva manda en los factores de forma
        b_ef, l_ef = l_ef, b_ef
    area_ef = b_ef * (1.0 if l_ef is None else l_ef)
    razon_ef = 0.0 if l_ef is None else b_ef / l_ef

    base = capacidad_portante_general(c_kpa=c_kpa, phi_deg=phi_deg, gamma_kn_m3=gamma_kn_m3, B_m=B_m, L_m=L_m,
                                      Df_m=Df_m, nivel_freatico_m=nivel_freatico_m, gamma_sat_kn_m3=gamma_sat_kn_m3)
    nc, nq, ng = base["Nc"], base["Nq"], base["Ng"]
    t = math.tan(math.radians(phi_deg))
    sc = 1.0 + razon_ef * nq / nc
    sq = 1.0 + razon_ef * t
    sg = 1.0 - 0.4 * razon_ef
    ic, iq, ig, m = _factores_inclinacion(phi_deg=phi_deg, c_kpa=c_kpa, V_kn=V_kn, H_kn=H_kn, area_ef_m2=area_ef,
                                          nc=nc, razon_ef=razon_m)
    q, g_ef = base["sobrecarga_kpa"], base["gamma_efectivo_kn_m3"]
    q_ult = (c_kpa * nc * sc * base["dc"] * ic + q * nq * sq * base["dq"] * iq
             + 0.5 * g_ef * b_ef * ng * sg * ig)
    _requerir(q_ult > 0, "La capacidad portante resultante es nula o negativa: no hay capacidad que verificar")
    return {"q_ult_kpa": q_ult, "Q_ult_kn": q_ult * area_ef, "B_ef_m": b_ef, "L_ef_m": l_ef, "area_ef_m2": area_ef,
            "presion_ef_kpa": V_kn / area_ef, "Nc": nc, "Nq": nq, "Ng": ng, "sc": sc, "sq": sq, "sg": sg,
            "dc": base["dc"], "dq": base["dq"], "ic": ic, "iq": iq, "ig": ig, "m": m,
            "sobrecarga_kpa": q, "gamma_efectivo_kn_m3": g_ef,
            "sin_traccion": eB_m <= B_m / 6.0 and (L_m is None or eL_m <= L_m / 6.0)}
