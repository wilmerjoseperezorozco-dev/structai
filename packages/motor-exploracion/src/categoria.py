"""Categoría de la unidad de construcción (NSR-10 H.3.1.1, Tabla H.3.1-1).

Se asigna la más desfavorable entre la categoría por número total de niveles (incluye sótanos, terrazas y pisos
técnicos) y la categoría por carga máxima de servicio (carga muerta + carga viva).
"""
from __future__ import annotations

import math

REF = "NSR-10 H.3.1.1, Tabla H.3.1-1"
ORDEN = ("baja", "media", "alta", "especial")
# límite superior (inclusive) de cada categoría; por encima del último: especial
NIVELES_MAX = (("baja", 3), ("media", 10), ("alta", 20))
CARGA_MAX_KN = (("baja", 800.0), ("media", 4000.0), ("alta", 8000.0))
_BORDE_REL = 0.05   # carga a ±5 % de un límite: la categoría cambia con una incertidumbre pequeña de cargas


def por_niveles(niveles: int) -> str:
    if not (isinstance(niveles, int) and niveles >= 1):
        raise ValueError(f"El número de niveles debe ser un entero ≥ 1 ({REF}).")
    return next((c for c, m in NIVELES_MAX if niveles <= m), "especial")


def por_carga(carga_kn: float) -> str:
    if not (math.isfinite(carga_kn) and carga_kn > 0):
        raise ValueError(f"La carga máxima de servicio debe ser positiva y finita ({REF}).")
    return next((c for c, m in CARGA_MAX_KN if carga_kn <= m), "especial")


def categoria(niveles: int, carga_kn: float) -> dict:
    cn, cq = por_niveles(niveles), por_carga(carga_kn)
    cat = max(cn, cq, key=ORDEN.index)
    borde = any(abs(carga_kn - m) <= _BORDE_REL * m for _, m in CARGA_MAX_KN) or \
        any(niveles in (m, m + 1) for _, m in NIVELES_MAX)
    return {"categoria": cat, "por_niveles": cn, "por_carga": cq, "en_borde": borde}
