"""Evaluación simplificada de licuación por SPT (Seed e Idriss, 1971; NCEER, Youd et al., 2001).

CSR = 0.65·(amax/g)·(σv/σ'v)·rd;  FS = (CRR7.5/CSR)·MSF.  Válido para arenas y limos arenosos con (N1)60cs < 30,
profundidades hasta 30 m y magnitudes 5–9,5. No sustituye el estudio geotécnico (NSR-10 Título H, H.4 y H.9 licuación).
"""
from __future__ import annotations

import math
from typing import Sequence

_REF = "Youd et al. (2001) / NSR-10 Título H"
Z_MAX_M = 30.0
MW_MIN, MW_MAX = 5.0, 9.5
N_NO_LICUABLE = 30.0
PROF_LPI_M = 20.0


def _requerir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(f"{mensaje} ({_REF}).")


def _finito(nombre: str, v: float) -> None:
    _requerir(isinstance(v, (int, float)) and math.isfinite(v), f"{nombre} debe ser un número finito; se recibió {v!r}")


def rd_nceer(z_m: float) -> float:
    """Coeficiente de reducción de esfuerzo cortante con la profundidad (Liao y Whitman, forma de NCEER)."""
    _finito("La profundidad z", z_m)
    _requerir(0.0 <= z_m <= Z_MAX_M, f"La profundidad debe estar en [0, {Z_MAX_M}] m para este método; se recibió {z_m}")
    if z_m <= 9.15:
        return 1.0 - 0.00765 * z_m
    if z_m <= 23.0:
        return 1.174 - 0.0267 * z_m
    return 0.744 - 0.008 * z_m


def csr_seed_idriss(*, amax_g: float, sigma_v_kpa: float, sigma_v_efectivo_kpa: float, z_m: float) -> float:
    for nombre, v in (("amax", amax_g), ("σv", sigma_v_kpa), ("σ'v", sigma_v_efectivo_kpa)):
        _finito(nombre, v)
    _requerir(0.0 < amax_g <= 2.0, f"amax/g debe estar en (0, 2]; se recibió {amax_g}")
    _requerir(sigma_v_efectivo_kpa > 0, "El esfuerzo vertical efectivo debe ser positivo")
    _requerir(sigma_v_kpa >= sigma_v_efectivo_kpa, "El esfuerzo vertical total no puede ser menor que el efectivo")
    return 0.65 * amax_g * (sigma_v_kpa / sigma_v_efectivo_kpa) * rd_nceer(z_m)


def msf_idriss(mw: float) -> float:
    """Factor de escala de magnitud MSF = 10^2.24 / Mw^2.56 (Idriss, en NCEER)."""
    _finito("La magnitud", mw)
    _requerir(MW_MIN <= mw <= MW_MAX, f"La magnitud Mw debe estar en [{MW_MIN}, {MW_MAX}]; se recibió {mw}")
    return 10.0 ** 2.24 / mw ** 2.56


def corregir_finos(*, n1_60: float, finos_pct: float) -> tuple[float, bool]:
    """(N1)60 → (N1)60cs equivalente en arena limpia (Idriss y Seed, en NCEER); devuelve (valor, en_borde por finos > 35 %)."""
    _finito("(N1)60", n1_60)
    _finito("El contenido de finos", finos_pct)
    _requerir(n1_60 >= 0, "(N1)60 no puede ser negativo")
    _requerir(0.0 <= finos_pct <= 100.0, "El contenido de finos debe estar en [0, 100] %")
    if finos_pct <= 5.0:
        return n1_60, False
    if finos_pct < 35.0:
        alfa = math.exp(1.76 - 190.0 / finos_pct ** 2)
        beta = 0.99 + finos_pct ** 1.5 / 1000.0
        return alfa + beta * n1_60, False
    return 5.0 + 1.2 * n1_60, True


def crr_spt(n1_60cs: float) -> float:
    """CRR para Mw = 7.5 y σ'v = 100 kPa (Rauch, aproximación de la curva de Seed); solo para (N1)60cs < 30."""
    _finito("(N1)60cs", n1_60cs)
    _requerir(n1_60cs >= 0, "(N1)60cs no puede ser negativo")
    _requerir(n1_60cs < N_NO_LICUABLE, f"(N1)60cs ≥ {N_NO_LICUABLE:g}: suelo no licuable según el método; la curva CRR no aplica")
    n = n1_60cs
    return 1.0 / (34.0 - n) + n / 135.0 + 50.0 / (10.0 * n + 45.0) ** 2 - 1.0 / 200.0


def factor_seguridad_estrato(*, n1_60cs: float, amax_g: float, sigma_v_kpa: float, sigma_v_efectivo_kpa: float,
                             z_m: float, mw: float) -> float:
    """FS contra licuación; math.inf si (N1)60cs ≥ 30 (no licuable por el método)."""
    csr = csr_seed_idriss(amax_g=amax_g, sigma_v_kpa=sigma_v_kpa, sigma_v_efectivo_kpa=sigma_v_efectivo_kpa, z_m=z_m)
    msf = msf_idriss(mw)
    _finito("(N1)60cs", n1_60cs)
    if n1_60cs >= N_NO_LICUABLE:
        return math.inf
    return crr_spt(n1_60cs) * msf / csr


def indice_potencial_licuacion(estratos: Sequence[tuple[float, float, float]]) -> float:
    """LPI de Iwasaki: ∫0..20 m F(z)·w(z) dz con F = 1 − FS (FS < 1), w = 10 − 0.5·z. Estratos (z_top, z_base, FS)."""
    _requerir(len(estratos) >= 1, "Se requiere al menos un estrato")
    ordenados = sorted(estratos, key=lambda e: e[0])
    previo_base = 0.0
    for z0, z1, fs in ordenados:
        _finito("z_top", z0)
        _finito("z_base", z1)
        if fs != math.inf:
            _finito("FS", fs)
        _requerir(z0 >= 0 and z1 > z0, f"Cada estrato necesita 0 ≤ z_top < z_base; se recibió ({z0}, {z1})")
        _requerir(fs >= 0, "El factor de seguridad no puede ser negativo")
        _requerir(z0 >= previo_base - 1e-9, "Los estratos se solapan")
        previo_base = z1
    lpi = 0.0
    for z0, z1, fs in ordenados:
        if fs >= 1.0 or z0 >= PROF_LPI_M:
            continue
        a, b = z0, min(z1, PROF_LPI_M)
        lpi += (1.0 - fs) * (10.0 * (b - a) - 0.25 * (b * b - a * a))
    return lpi
