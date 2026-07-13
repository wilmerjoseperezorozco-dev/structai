"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — INCERTIDUMBRE Y CONFIABILIDAD ESTRUCTURAL
Mismo criterio de Motor APU: simulación Monte Carlo (N=5000) en vez de un
número determinístico "exacto" que oculta el margen de error real.

Además se calcula el índice de confiabilidad β (First-Order Second-Moment,
FOSM — Cornell, 1969), estándar en diseño estructural probabilístico
(base de los factores de carga y resistencia LRFD/NSR-10):

    g = Resistencia − Solicitación          (estado límite)
    β = μ_g / σ_g                            (índice de confiabilidad)
    Pf ≈ Φ(−β)                               (probabilidad de falla, aprox. normal)

β ≥ 3.0 se considera un nivel de confiabilidad aceptable en códigos modernos
(AISC/NSR-10 implican β≈3.0–3.5 para elementos dúctiles).

Muestreo dimensional CORRELACIONADO: la desviación de una dimensión controlante
(p.ej. altura de una viga) afecta simultáneamente I (∝ dimensión³) y el módulo
de sección S (∝ dimensión²) de forma consistente — no se muestrean de forma
independiente, porque físicamente están acopladas a la misma geometría real.
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import math
from dataclasses import dataclass

import numpy as np

N_SIMULATIONS = 5_000
SEMILLA = 42
PISO_RELATIVO = 0.05    # floor de muestreo: 5% de la media, evita valores no físicos (<=0)


@dataclass
class EstadisticaMuestra:
    mean: float
    std: float
    p05: float
    p95: float


def _rng(seed: int = SEMILLA) -> np.random.Generator:
    return np.random.default_rng(seed)


def muestrear_normal(media: float, cov: float, N: int, rng: np.random.Generator, piso_relativo: float = PISO_RELATIVO) -> np.ndarray:
    """Muestras ~ N(media, (media·cov)²), truncadas para evitar valores no físicos."""
    muestras = rng.normal(media, media * cov, N)
    return np.maximum(muestras, media * piso_relativo)


def estadisticas(muestra: np.ndarray) -> EstadisticaMuestra:
    return EstadisticaMuestra(
        mean=float(np.mean(muestra)), std=float(np.std(muestra)),
        p05=float(np.percentile(muestra, 5)), p95=float(np.percentile(muestra, 95)),
    )


def indice_confiabilidad(margen: np.ndarray) -> float:
    """β = μ_g/σ_g (FOSM) sobre el margen de seguridad g = Resistencia − Solicitación."""
    std = float(np.std(margen))
    if std <= 1e-12:
        return float("inf") if float(np.mean(margen)) > 0 else float("-inf")
    return float(np.mean(margen)) / std


def probabilidad_falla(beta: float) -> float:
    """Pf ≈ Φ(−β), aproximación normal estándar de la probabilidad de falla."""
    if math.isinf(beta):
        return 0.0 if beta > 0 else 1.0
    return 0.5 * (1.0 - math.erf(beta / math.sqrt(2.0)))


@dataclass
class ResultadoIncertidumbreFlexion:
    deflexion: EstadisticaMuestra
    esfuerzo: EstadisticaMuestra
    indice_confiabilidad_esfuerzo: float
    probabilidad_falla_esfuerzo: float
    indice_confiabilidad_deflexion: float
    probabilidad_falla_deflexion: float


@dataclass
class ContribucionCarga:
    """Efecto determinístico de UNA carga individual, evaluado en el punto
    crítico x* de la respuesta superpuesta (no en su propio máximo local)."""
    v_det: float          # v_i(x*) — contribución a la deflexión en x*
    M_det: float          # M_i(x*) — contribución al momento en x*
    carga_mean: float
    cov_carga: float


def propagar_flexion(
    cargas: list[ContribucionCarga], S_det: float,
    E_mean: float, cov_E: float,
    fy_mean: float, cov_fy: float,
    deflexion_admisible: float,
    cov_dimension: float = 0.02,
    N: int = N_SIMULATIONS,
) -> ResultadoIncertidumbreFlexion:
    """
    Propaga incertidumbre de E, dimensión de sección, cada carga individual
    (con su propio coeficiente de variación) y fluencia, hacia la deflexión
    y el esfuerzo de flexión combinados en x*, usando las relaciones EXACTAS
    de la teoría de vigas prismáticas de EI constante:
      · M(x) es independiente de E, I (equilibrio/compatibilidad puros)
      · v(x) ∝ carga / (E·I), y es lineal ⇒ superponible carga a carga
    Todas las cargas comparten la MISMA realización de E e I por simulación
    (son propiedades del elemento, no de la carga); cada carga se muestrea
    de forma independiente porque sus orígenes de incertidumbre son distintos
    (carga viva vs. permanente vs. equipo, etc.).
    """
    rng = _rng()
    factor_dim = muestrear_normal(1.0, cov_dimension, N, rng)  # perturbación dimensional correlacionada
    E_s = muestrear_normal(E_mean, cov_E, N, rng)
    fy_s = muestrear_normal(fy_mean, cov_fy, N, rng)

    I_rel = factor_dim ** 3   # I ∝ dimensión³ (p.ej. b·h³/12)
    S_rel = factor_dim ** 2   # S=I/c ∝ dimensión² (p.ej. b·h²/6)

    v_s = np.zeros(N)
    M_s = np.zeros(N)
    for c in cargas:
        carga_s = muestrear_normal(c.carga_mean, c.cov_carga, N, rng, piso_relativo=0.0)
        razon = carga_s / c.carga_mean if c.carga_mean != 0 else np.ones(N)
        v_s += c.v_det * razon
        M_s += c.M_det * razon

    v_s = v_s * (E_mean / E_s) / I_rel
    S_s = S_det * S_rel
    esfuerzo_s = np.abs(M_s) / S_s

    margen_esfuerzo = fy_s - esfuerzo_s
    margen_deflexion = deflexion_admisible - np.abs(v_s)

    return ResultadoIncertidumbreFlexion(
        deflexion=estadisticas(np.abs(v_s)),
        esfuerzo=estadisticas(esfuerzo_s),
        indice_confiabilidad_esfuerzo=indice_confiabilidad(margen_esfuerzo),
        probabilidad_falla_esfuerzo=probabilidad_falla(indice_confiabilidad(margen_esfuerzo)),
        indice_confiabilidad_deflexion=indice_confiabilidad(margen_deflexion),
        probabilidad_falla_deflexion=probabilidad_falla(indice_confiabilidad(margen_deflexion)),
    )


@dataclass
class ResultadoIncertidumbrePandeo:
    carga_critica: EstadisticaMuestra
    indice_confiabilidad: float
    probabilidad_falla: float


def propagar_pandeo(
    Pcr_det: float, esbeltez: float, regimen: str,
    E_mean: float, cov_E: float, fy_mean: float, cov_fy: float,
    A_mean: float, cov_dimension: float,
    carga_aplicada_mean: float, cov_carga: float,
    N: int = N_SIMULATIONS,
) -> ResultadoIncertidumbrePandeo:
    """
    Propaga incertidumbre a la carga crítica de pandeo.
    Régimen Euler:   Pcr ∝ E · I ∝ E · dimensión³  (independiente de fy)
    Régimen Johnson: Pcr = σcr·A y σcr depende de fy y E — se recalcula
                     el esfuerzo crítico por muestra para no perder la
                     no linealidad de la parábola de Johnson.
    """
    rng = _rng()
    factor_dim = muestrear_normal(1.0, cov_dimension, N, rng)
    E_s = muestrear_normal(E_mean, cov_E, N, rng)
    fy_s = muestrear_normal(fy_mean, cov_fy, N, rng)
    carga_s = muestrear_normal(carga_aplicada_mean, cov_carga, N, rng)
    A_s = A_mean * factor_dim

    if regimen == "euler":
        I_rel = factor_dim ** 3
        Pcr_s = Pcr_det * (E_s / E_mean) * I_rel
    else:  # johnson — no linealidad respecto a fy y esbeltez, se recalcula
        lam_s = esbeltez / factor_dim  # r ∝ dimensión ⇒ λ=KL/r se reduce si la dimensión crece
        sigma_cr_s = fy_s * (1 - (fy_s * lam_s ** 2) / (4 * math.pi ** 2 * E_s))
        sigma_cr_s = np.maximum(sigma_cr_s, 0.0)
        Pcr_s = sigma_cr_s * A_s

    margen = Pcr_s - carga_s
    beta = indice_confiabilidad(margen)

    return ResultadoIncertidumbrePandeo(
        carga_critica=estadisticas(Pcr_s),
        indice_confiabilidad=beta,
        probabilidad_falla=probabilidad_falla(beta),
    )
