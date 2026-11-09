"""Asentamiento por consolidación primaria y tiempo de consolidación unidimensional (Terzaghi).

Cc·H/(1+e0)·log10(σ'f/σ'0), con ramal de recompresión (Cr) hasta la presión de preconsolidación σ'p.
Referencias: Terzaghi (1943); NSR-10 Título H (H.4.9) para los límites de asentamiento admisible.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq

_REF = "Terzaghi / NSR-10 Título H (H.4.9)"
_TV_CORTO = 0.01          # por debajo, U = 2·sqrt(Tv/π) es exacto salvo términos del orden de exp(-π²/(4·Tv))
_TERMINOS = 200
_TV_MAX = 50.0


def _requerir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(f"{mensaje} ({_REF}).")


def asentamiento_primario(*, cc: float, cr: float, e0: float, espesor_m: float, sigma0_kpa: float,
                          delta_kpa: float, sigma_p_kpa: float) -> float:
    """Asentamiento primario (m) de un estrato de arcilla. Todos los parámetros son obligatorios."""
    for nombre, v in (("cc", cc), ("cr", cr), ("e0", e0), ("espesor", espesor_m), ("σ'0", sigma0_kpa),
                      ("Δσ", delta_kpa), ("σ'p", sigma_p_kpa)):
        _requerir(math.isfinite(v), f"{nombre} debe ser finito")
    _requerir(cc > 0, "El índice de compresión Cc debe ser positivo")
    _requerir(0 <= cr <= cc, "El índice de recompresión Cr debe cumplir 0 ≤ Cr ≤ Cc")
    _requerir(e0 > 0, "La relación de vacíos inicial e0 debe ser positiva")
    _requerir(espesor_m > 0, "El espesor del estrato debe ser positivo")
    _requerir(sigma0_kpa > 0, "El esfuerzo efectivo inicial σ'0 debe ser positivo")
    _requerir(delta_kpa >= 0, "El incremento de esfuerzo Δσ no puede ser negativo (descarga fuera del alcance)")
    _requerir(sigma_p_kpa >= sigma0_kpa, "La presión de preconsolidación σ'p no puede ser menor que σ'0 (suelo no consolidado: use σ'p = σ'0 y verifique el exceso de presión de poros)")
    if delta_kpa == 0:
        return 0.0
    final = sigma0_kpa + delta_kpa
    base = espesor_m / (1.0 + e0)
    if final <= sigma_p_kpa:
        return base * cr * math.log10(final / sigma0_kpa)
    return base * (cr * math.log10(sigma_p_kpa / sigma0_kpa) + cc * math.log10(final / sigma_p_kpa))


def grado_consolidacion(tv: float) -> float:
    """Grado medio de consolidación U(Tv) de Terzaghi para drenaje doble o simple (Tv usa la trayectoria Hdr)."""
    _requerir(math.isfinite(tv) and tv >= 0, "El factor de tiempo Tv debe ser ≥ 0")
    if tv == 0:
        return 0.0
    if tv < _TV_CORTO:
        return 2.0 * math.sqrt(tv / math.pi)
    m = math.pi * (2.0 * np.arange(_TERMINOS) + 1.0) / 2.0
    return float(1.0 - np.sum(2.0 / m ** 2 * np.exp(-(m ** 2) * tv)))


def factor_tiempo(cv_m2_dia: float, t_dias: float, hdr_m: float) -> float:
    _requerir(cv_m2_dia > 0, "El coeficiente de consolidación cv debe ser positivo")
    _requerir(hdr_m > 0, "La trayectoria de drenaje Hdr debe ser positiva")
    _requerir(t_dias >= 0, "El tiempo no puede ser negativo")
    return cv_m2_dia * t_dias / hdr_m ** 2


def tiempo_para_grado(grado: float, *, cv_m2_dia: float, hdr_m: float) -> float:
    """Días necesarios para alcanzar un grado de consolidación (0 < U < 1), por raíz de U(Tv) − U con brentq."""
    _requerir(0.0 < grado < 1.0, "El grado de consolidación debe estar en (0, 1)")
    _requerir(cv_m2_dia > 0, "El coeficiente de consolidación cv debe ser positivo")
    _requerir(hdr_m > 0, "La trayectoria de drenaje Hdr debe ser positiva")
    tv = brentq(lambda x: grado_consolidacion(x) - grado, 1e-12, _TV_MAX, xtol=1e-14, rtol=1e-13)
    return tv * hdr_m ** 2 / cv_m2_dia
