"""Capacidad portante general de cimentaciones superficiales (Vesić, 1973) con factores de forma y profundidad.

q_ult = c·Nc·sc·dc + q·Nq·sq·dq + ½·γ'·B·Nγ·sγ·dγ. El Título H de la NSR-10 no entrega una fórmula de capacidad
portante: este motor la calcula con la teoría clásica y el resultado NO sustituye el estudio geotécnico (H.4.2.3).
No incluye factores de inclinación de carga ni de excentricidad: la carga se supone vertical y centrada.
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
