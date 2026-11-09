"""Consolidación unidimensional multicapa por volúmenes finitos con integración exacta en el tiempo.

mv_i·∂u/∂t = ∂/∂z(cv_i·mv_i·∂u/∂z), u = exceso de presión de poros. Discretizado en celdas, el sistema C·u' = −K·u se
resuelve por descomposición espectral (K simétrica tridiagonal): sin error de paso de tiempo, solo error espacial.
Carga instantánea: u(0) = Δσ de cada capa. Referencia: Terzaghi (1943); NSR-10 Título H (H.4.9).
"""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from scipy.linalg import eigh_tridiagonal

_REF = "Terzaghi / NSR-10 Título H (H.4.9)"
_MAX_CAPAS = 20
_MAX_NODOS = 400


def _requerir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(f"{mensaje} ({_REF}).")


def consolidacion_multicapa(capas: Sequence[dict], *, tiempos_dias: Sequence[float], drenaje_superior: bool,
                            drenaje_inferior: bool, nodos_por_capa: int) -> dict:
    """capas de arriba hacia abajo: espesor_m, cv_m2_dia, mv_kpa_inv, delta_sigma_kpa. Devuelve grado y asentamiento(t)."""
    _requerir(drenaje_superior or drenaje_inferior, "Se requiere al menos un borde con drenaje")
    _requerir(1 <= len(capas) <= _MAX_CAPAS, f"Se admiten entre 1 y {_MAX_CAPAS} capas")
    _requerir(isinstance(nodos_por_capa, int) and 4 <= nodos_por_capa <= _MAX_NODOS,
              f"nodos_por_capa debe estar entre 4 y {_MAX_NODOS}")
    t = np.asarray(list(tiempos_dias), dtype=float)
    _requerir(t.size >= 1 and bool(np.all(np.isfinite(t))) and bool(np.all(t >= 0)) and bool(np.all(np.diff(t) > 0)),
              "Los tiempos deben ser finitos, no negativos y estrictamente crecientes")
    dz, kp, mv, u0 = [], [], [], []
    for c in capas:
        h, cv, m, d = c["espesor_m"], c["cv_m2_dia"], c["mv_kpa_inv"], c["delta_sigma_kpa"]
        for nombre, v in (("espesor", h), ("cv", cv), ("mv", m)):
            _requerir(math.isfinite(v) and v > 0, f"{nombre} de la capa debe ser finito y positivo; se recibió {v!r}")
        _requerir(math.isfinite(d) and d >= 0, f"Δσ de la capa debe ser finito y no negativo; se recibió {d!r}")
        dz += [h / nodos_por_capa] * nodos_por_capa
        kp += [cv * m] * nodos_por_capa          # k/γw
        mv += [m] * nodos_por_capa
        u0 += [d] * nodos_por_capa
    dz, kp, mv, u0 = map(np.asarray, (dz, kp, mv, u0))
    n = dz.size
    cap = mv * dz
    g = 1.0 / (dz[:-1] / (2 * kp[:-1]) + dz[1:] / (2 * kp[1:]))      # conductancia entre celdas contiguas
    diag = np.zeros(n)
    diag[:-1] += g
    diag[1:] += g
    if drenaje_superior:
        diag[0] += kp[0] / (dz[0] / 2.0)
    if drenaje_inferior:
        diag[-1] += kp[-1] / (dz[-1] / 2.0)
    s = 1.0 / np.sqrt(cap)
    lam, vec = eigh_tridiagonal(diag * s * s, -g * s[:-1] * s[1:])
    coef = vec.T @ (u0 / s)                                          # C^{1/2}·u0 proyectado
    final = float(np.sum(cap * u0))
    asent = []
    for ti in t:
        u = s * (vec @ (np.exp(-lam * ti) * coef))
        asent.append(float(np.sum(cap * (u0 - u))))
    asent_arr = np.clip(np.asarray(asent), 0.0, final)
    grado = (asent_arr / final).tolist() if final > 0 else [0.0] * t.size
    return {"tiempos_dias": t.tolist(), "asentamiento_m": asent_arr.tolist(), "grado": grado, "asentamiento_final_m": final}
