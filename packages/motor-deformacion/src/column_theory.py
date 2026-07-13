"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — TEORÍA DE COLUMNAS (PANDEO)
Ecuación diferencial de pandeo elástico (Euler, 1757):

    EI · d²v/dx²  +  P · v  =  0

Solución con condiciones de frontera según el apoyo (K = factor de
longitud efectiva) da la carga crítica de Euler:

    Pcr = π² E I / (K L)²

Para columnas cortas/intermedias el pandeo elástico de Euler sobreestima
la capacidad porque el material ya fluye antes de pandear — se usa la
parábola de Johnson (Shigley, "Mechanical Engineering Design"), tangente
a la hipérbola de Euler en la esbeltez de transición λc:

    λc = π √(2E / fy)
    σcr = fy [1 − (fy λ²) / (4π² E)]      para λ ≤ λc   (Johnson, inelástico)
    σcr = π² E / λ²                        para λ > λc   (Euler, elástico)

Efecto de segundo orden (P-Δ) para viga-columna vía factor de amplificación:

    M_amplificado = M₀ / (1 − P/Pcr)
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class ResultadoPandeo:
    esbeltez: float
    esbeltez_transicion: float
    regimen: str               # "euler" (pandeo elástico) | "johnson" (inelástico)
    carga_critica: float        # N (Pcr)
    esfuerzo_critico: float     # Pa (σcr)
    factor_seguridad: float     # Pcr / P_aplicada
    factor_amplificacion: float  # 1/(1-P/Pcr), para momentos de 2do orden


def carga_critica_euler(E: float, I: float, K: float, L: float) -> float:
    """Pcr = π²EI/(KL)² — carga crítica de pandeo elástico."""
    return math.pi ** 2 * E * I / (K * L) ** 2


def esbeltez_transicion(E: float, fy: float) -> float:
    """λc = π√(2E/fy) — frontera entre pandeo elástico (Euler) e inelástico (Johnson)."""
    return math.pi * math.sqrt(2 * E / fy)


def esfuerzo_critico_johnson(E: float, fy: float, esbeltez: float) -> float:
    return fy * (1 - (fy * esbeltez ** 2) / (4 * math.pi ** 2 * E))


def analizar_columna(
    P_aplicada: float, E: float, I: float, A: float, fy: float, K: float, L: float,
) -> ResultadoPandeo:
    """
    Evalúa la columna bajo carga axial P_aplicada, seleccionando automáticamente
    el régimen (Euler o Johnson) según la esbeltez.
    """
    r = math.sqrt(I / A)
    esbeltez = K * L / r
    lambda_c = esbeltez_transicion(E, fy)

    if esbeltez <= lambda_c:
        regimen = "johnson"
        sigma_cr = esfuerzo_critico_johnson(E, fy, esbeltez)
    else:
        regimen = "euler"
        sigma_cr = math.pi ** 2 * E / esbeltez ** 2

    Pcr = sigma_cr * A
    fs = Pcr / P_aplicada if P_aplicada > 0 else float("inf")

    if P_aplicada >= Pcr:
        factor_amp = float("inf")
    else:
        factor_amp = 1.0 / (1.0 - P_aplicada / Pcr)

    return ResultadoPandeo(
        esbeltez=esbeltez, esbeltez_transicion=lambda_c, regimen=regimen,
        carga_critica=Pcr, esfuerzo_critico=sigma_cr,
        factor_seguridad=fs, factor_amplificacion=factor_amp,
    )


def esfuerzo_combinado_viga_columna(
    P: float, A: float, M0: float, S: float, Pcr: float,
) -> tuple[float, float]:
    """
    Esfuerzo combinado axial + flexión amplificada por efecto P-Δ (2do orden).
    Retorna (esfuerzo_total, factor_amplificacion).
    σ = P/A + (M₀ · factor_amplificación) / S
    """
    if P >= Pcr:
        return float("inf"), float("inf")
    factor_amp = 1.0 / (1.0 - P / Pcr)
    sigma = P / A + (M0 * factor_amp) / S
    return sigma, factor_amp
