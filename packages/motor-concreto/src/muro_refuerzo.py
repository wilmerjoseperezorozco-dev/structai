"""Selección de refuerzo de flexión por franja de 1 m y capacidades de sección, compartido por los elementos del muro de contención.

Numerales leídos en el corpus (2026-11-08): C.10.5.1 (As mín), C.10.3.4 (tensión controlada), C.7.7.1 (recubrimientos), C.9.3.2 (φ), C.11.2.1.1 (Vc).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .viga import AREA_MM2, DIAMETRO_MM, EPS_T_MIN, PHI_CORTANTE, PHI_FLEXION, Materiales, beta1
from .zapata import _as_flexion

COBERTURA_SUELO_MM = 75.0            # C.7.7.1(a)
SEP_MAX_ABS_MM = 450.0


@dataclass(frozen=True)
class Franja:
    """Refuerzo de una franja de 1 m."""
    nombre: str
    mu_knm_m: float
    vu_kn_m: float
    h_mm: float
    d_mm: float
    dia: str
    sep_mm: float
    as_req_mm2_m: float
    as_prov_mm2_m: float
    as_min_mm2_m: float
    eps_t: float
    phi_vc_kn_m: float
    cumple: bool
    motivos: tuple[str, ...]


def recubrimiento(dia: str) -> float:
    """C.7.7.1(b): concreto expuesto a suelo o intemperie, barras ≤ #5 → 40 mm; #6 o mayores → 50 mm."""
    return 40.0 if dia in ("3", "4", "5") else 50.0


def suelo(dia: str) -> float:
    return COBERTURA_SUELO_MM


def as_min_flexion(d_mm: float, fc: float, fy: float, b_mm: float = 1000.0) -> float:
    return max(0.25 * math.sqrt(fc) / fy, 1.4 / fy) * b_mm * d_mm            # C.10.5.1 (C.10-3)


def phi_mn_knm(as_mm2: float, d_mm: float, m: Materiales) -> tuple[float, float]:
    """(φMn en kN·m/m, εt) de una franja de 1 m con As [mm²/m]."""
    a = as_mm2 * m.fy / (0.85 * m.fc * 1000.0)
    c = a / beta1(m.fc)
    eps = 0.003 * (d_mm - c) / c if c > 0 else math.inf
    return PHI_FLEXION * as_mm2 * m.fy * (d_mm - a / 2.0) / 1e6, eps


def phi_vc_kn(d_mm: float, m: Materiales) -> float:
    return PHI_CORTANTE * 0.17 * math.sqrt(m.fc) * 1000.0 * d_mm / 1000.0       # C.11.2.1.1, λ = 1


def elegir_barras(mu_knm: float, h_mm: float, cobertura, fc: float, fy: float, as_min_extra: float = 0.0):
    """Menor As provisto (por m) que cumple flexión, εt ≥ 0,005, As mín y separación; (dia, s, As_prov, d, As_req, As_min, eps_t) o None."""
    s_max = min(3 * h_mm, SEP_MAX_ABS_MM)
    mejor = None
    for dia in ("4", "5", "6", "7", "8"):
        db, a1 = DIAMETRO_MM[dia], AREA_MM2[dia]
        d = h_mm - cobertura(dia) - db / 2.0
        if d <= 0:
            continue
        as_req = _as_flexion(mu_knm, 1000.0, d, fc, fy)
        if math.isinf(as_req):
            continue
        as_min = max(as_min_flexion(d, fc, fy), as_min_extra)
        s = min(math.floor(1000.0 * a1 / max(as_req, as_min) / 10.0) * 10.0, s_max)
        if s < db + max(db, 25.0):
            continue
        as_prov = 1000.0 * a1 / s
        eps = phi_mn_knm(as_prov, d, Materiales(fc, fy))[1]
        if eps < EPS_T_MIN:
            continue
        if mejor is None or as_prov < mejor[2]:
            mejor = (dia, s, as_prov, d, as_req, as_min, eps)
    return mejor


def franja(nombre: str, mu: float, vu: float, h_mm: float, cobertura, m: Materiales, as_min_extra: float = 0.0) -> Franja:
    sel = elegir_barras(mu, h_mm, cobertura, m.fc, m.fy, as_min_extra)
    if sel is None:
        return Franja(nombre, mu, vu, h_mm, 0.0, "-", 0.0, math.inf, math.inf, 0.0, 0.0, 0.0, False,
                      (f"{nombre}: no hay arreglo de barras que cumpla (espesor insuficiente)",))
    dia, s, as_prov, d, as_req, as_min, eps = sel
    pvc = phi_vc_kn(d, m)
    motivos = (() if vu <= pvc else (f"{nombre}: cortante Vu {vu:.1f} kN/m > φVc {pvc:.1f} kN/m (C.11.2.1.1)",))
    return Franja(nombre, mu, vu, h_mm, d, dia, s, as_req, as_prov, as_min, eps, pvc, not motivos, motivos)
