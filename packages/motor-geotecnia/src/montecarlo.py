"""Monte Carlo del asentamiento primario con Cc y e0 lognormales (opcionalmente correlacionados).

Distribución lognormal parametrizada por mediana y coeficiente de variación; correlación por cópula gaussiana.
Cr se acota a Cr ≤ Cc en cada muestra. Resultados reproducibles por semilla explícita. Referencia: NSR-10 Título H (H.4.9).
"""
from __future__ import annotations

import math

import numpy as np

_REF = "NSR-10 Título H (H.4.9) / Terzaghi"
N_MIN, N_MAX, CV_MAX = 100, 1_000_000, 2.0


def _requerir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(f"{mensaje} ({_REF}).")


def _lognormal(mediana: float, cv: float, z: np.ndarray) -> np.ndarray:
    sigma = math.sqrt(math.log(1.0 + cv * cv))
    return mediana * np.exp(sigma * z)


def simular_asentamiento_primario(*, estrato: dict, cc_mediana: float, cc_cv: float, e0_mediana: float, e0_cv: float,
                                  rho_cc_e0: float, n: int, semilla: int, limite_m: float) -> dict:
    """estrato: espesor_m, sigma0_kpa, delta_kpa, sigma_p_kpa, cr (fijos). Devuelve estadísticos y P(S > límite)."""
    h, s0, d, sp, cr = (estrato[k] for k in ("espesor_m", "sigma0_kpa", "delta_kpa", "sigma_p_kpa", "cr"))
    for nombre, v in (("espesor", h), ("σ'0", s0), ("Δσ", d), ("σ'p", sp), ("Cr", cr), ("Cc mediana", cc_mediana),
                      ("e0 mediana", e0_mediana), ("límite", limite_m)):
        _requerir(math.isfinite(v), f"{nombre} debe ser finito")
    _requerir(h > 0 and s0 > 0 and cc_mediana > 0 and e0_mediana > 0 and limite_m > 0,
              "Espesor, σ'0, Cc, e0 y el límite deben ser positivos")
    _requerir(d >= 0 and cr >= 0 and sp >= s0, "Se requiere Δσ ≥ 0, Cr ≥ 0 y σ'p ≥ σ'0")
    for nombre, cv in (("Cc", cc_cv), ("e0", e0_cv)):
        _requerir(math.isfinite(cv) and 0.0 <= cv <= CV_MAX,
                  f"El coeficiente de variación de {nombre} debe estar en [0, {CV_MAX}]")
    _requerir(math.isfinite(rho_cc_e0) and -1.0 <= rho_cc_e0 <= 1.0, "La correlación Cc–e0 debe estar en [−1, 1]")
    _requerir(isinstance(n, int) and N_MIN <= n <= N_MAX, f"El número de simulaciones debe estar entre {N_MIN} y {N_MAX}")
    _requerir(isinstance(semilla, int) and semilla >= 0, "La semilla debe ser un entero no negativo (reproducibilidad)")
    rng = np.random.default_rng(semilla)
    z1, z2 = rng.standard_normal(n), rng.standard_normal(n)
    z_e0 = rho_cc_e0 * z1 + math.sqrt(1.0 - rho_cc_e0 ** 2) * z2
    cc = _lognormal(cc_mediana, cc_cv, z1)
    e0 = _lognormal(e0_mediana, e0_cv, z_e0)
    cr_m = np.minimum(cr, cc)
    final = s0 + d
    if d == 0:
        s = np.zeros(n)
    elif final <= sp:
        s = h / (1.0 + e0) * cr_m * math.log10(final / s0)
    else:
        s = h / (1.0 + e0) * (cr_m * math.log10(sp / s0) + cc * math.log10(final / sp))
    p5, p50, p95 = np.percentile(s, [5, 50, 95])
    return {"n": n, "semilla": semilla, "media_m": float(s.mean()), "desv_m": float(s.std(ddof=1)), "p5_m": float(p5),
            "p50_m": float(p50), "p95_m": float(p95), "prob_exceder_limite": float(np.mean(s > limite_m)), "limite_m": limite_m}
