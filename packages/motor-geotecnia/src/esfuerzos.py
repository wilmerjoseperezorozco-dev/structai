"""Incrementos de esfuerzo vertical (Boussinesq y 2:1) y esfuerzo efectivo geostático.

Unidades: kPa y m. Referencias: Newmark (1935) para la esquina de un área rectangular uniformemente cargada;
aproximación 2:1 de uso común en NSR-10 Título H (H.4.9, estimación de asentamientos).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

GAMMA_AGUA_KN_M3 = 9.81
_REF = "NSR-10 Título H (H.4.9) / teoría de elasticidad de Boussinesq"


def _positivo(nombre: str, valor: float) -> None:
    if not (valor > 0) or not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser positivo y finito ({_REF}); se recibió {valor!r}.")


def esfuerzo_boussinesq_esquina_rect(q_kpa: float, B_m: float, L_m: float, z_m: float) -> float:
    """Δσz bajo la esquina de un rectángulo B×L con carga uniforme q (Newmark, forma cerrada)."""
    for n, v in (("B", B_m), ("L", L_m), ("z", z_m)):
        _positivo(n, v)
    if q_kpa < 0:
        raise ValueError(f"La presión de contacto q no puede ser negativa ({_REF}).")
    m, n = B_m / z_m, L_m / z_m
    r = math.sqrt(m * m + n * n + 1.0)
    num = 2.0 * m * n * r
    primero = num / (m * m + n * n + m * m * n * n + 1.0) * (m * m + n * n + 2.0) / (m * m + n * n + 1.0)
    segundo = math.atan2(num, m * m + n * n + 1.0 - m * m * n * n)
    return q_kpa * (primero + segundo) / (4.0 * math.pi)


def esfuerzo_boussinesq_centro_rect(q_kpa: float, B_m: float, L_m: float, z_m: float) -> float:
    """Δσz bajo el centro de un rectángulo B×L: superposición de cuatro esquinas de (B/2)×(L/2)."""
    return 4.0 * esfuerzo_boussinesq_esquina_rect(q_kpa, B_m / 2.0, L_m / 2.0, z_m)


def esfuerzo_2a1(q_kpa: float, B_m: float, L_m: Optional[float], z_m: float) -> float:
    """Método 2:1: la carga se reparte con pendiente 2V:1H. L_m=None → zapata corrida (por metro)."""
    _positivo("B", B_m)
    if not (math.isfinite(q_kpa) and q_kpa >= 0):
        raise ValueError(f"La presión de contacto q debe ser finita y no negativa ({_REF}); se recibió {q_kpa!r}.")
    if not (math.isfinite(z_m) and z_m >= 0):
        raise ValueError(f"La profundidad z debe ser finita y no negativa ({_REF}); se recibió {z_m!r}.")
    if L_m is None:
        return q_kpa * B_m / (B_m + z_m)
    _positivo("L", L_m)
    return q_kpa * B_m * L_m / ((B_m + z_m) * (L_m + z_m))


def esfuerzo_efectivo_vertical(estratos: Sequence[tuple[float, float, float]], z_m: float, nivel_freatico_m: Optional[float]) -> float:
    """σ'v a la profundidad z. `estratos`: (espesor m, γ sobre el nivel freático, γsat) de arriba hacia abajo.

    Sin nivel freático (None) se usa γ en todo el perfil. Bajo el nivel freático, γ' = γsat − γw.
    """
    if not (math.isfinite(z_m) and z_m >= 0):
        raise ValueError(f"La profundidad z debe ser finita y no negativa ({_REF}); se recibió {z_m!r}.")
    if nivel_freatico_m is not None and not (math.isfinite(nivel_freatico_m) and nivel_freatico_m >= 0):
        raise ValueError(f"La profundidad del nivel freático debe ser finita y no negativa ({_REF}); se recibió {nivel_freatico_m!r}.")
    if z_m > sum(e[0] for e in estratos) + 1e-12:
        raise ValueError(f"La profundidad z={z_m} m excede el perfil de estratos definido ({_REF}).")
    sigma, tope = 0.0, 0.0
    for espesor, gamma, gamma_sat in estratos:
        _positivo("espesor del estrato", espesor)
        _positivo("peso unitario", gamma)
        if nivel_freatico_m is not None and not (math.isfinite(gamma_sat) and gamma_sat > GAMMA_AGUA_KN_M3 and gamma_sat >= gamma):
            raise ValueError(f"El peso unitario saturado debe ser finito, mayor que el del agua ({GAMMA_AGUA_KN_M3} kN/m³) y no menor que el seco ({_REF}); se recibió {gamma_sat!r}.")
        fondo = min(tope + espesor, z_m)
        if fondo > tope:
            if nivel_freatico_m is None:
                sigma += gamma * (fondo - tope)
            else:
                seco = max(0.0, min(fondo, nivel_freatico_m) - tope)
                humedo = (fondo - tope) - seco
                sigma += gamma * seco + (gamma_sat - GAMMA_AGUA_KN_M3) * humedo
        tope += espesor
        if tope >= z_m:
            break
    return sigma
