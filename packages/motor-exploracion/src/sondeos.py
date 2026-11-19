"""Número y profundidad mínimos de sondeos (NSR-10 H.3.2.3, Tabla H.3.2-1, y H.3.2.5).

Profundidad (H.3.2.5): al menos el 50 % de los sondeos alcanza la profundidad de la tabla, medida desde el nivel
inferior de excavación, afectada por (a) la profundidad a la que el incremento de esfuerzo vertical de la
edificación es el 10 % del esfuerzo en la interfaz suelo-cimentación (aquí: Boussinesq bajo el centro de la planta
con carga uniforme, motor-geotecnia) y (b) 1,5 veces el ancho de la losa corrida. Se toma la mayor.
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

REF = "NSR-10 H.3.2.3 (Tabla H.3.2-1) y H.3.2.5"
TABLA = {"baja": (3, 6.0), "media": (4, 15.0), "alta": (4, 25.0), "especial": (5, 30.0)}   # (n mínimo, prof. m)
FRACCION_ESFUERZO = 0.10
FACTOR_LOSA = 1.5
FRACCION_SONDEOS_PROFUNDOS = 0.5

_esf = None


def _esfuerzos():
    """Carga motor-geotecnia/src/esfuerzos.py por ruta (ambos paquetes se llaman `src`)."""
    global _esf
    if _esf is None:
        ruta = Path(__file__).resolve().parents[2] / "motor-geotecnia" / "src" / "esfuerzos.py"
        spec = importlib.util.spec_from_file_location("motor_geotecnia_esfuerzos", ruta)
        _esf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_esf)
    return _esf


def razon_boussinesq_centro(B_m: float, L_m: float, z_m: float) -> float:
    return _esfuerzos().esfuerzo_boussinesq_centro_rect(1.0, B_m, L_m, z_m)


def profundidad_10pct(B_m: float, L_m: float) -> float:
    """z (m bajo la cimentación) con Δσ/q = 0,10 bajo el centro de la planta B×L (bisección; Δσ/q decrece con z)."""
    for n, v in (("ancho de planta", B_m), ("largo de planta", L_m)):
        if not (math.isfinite(v) and v > 0):
            raise ValueError(f"El {n} debe ser positivo y finito ({REF}).")
    lo, hi = 1e-3, 50.0 * max(B_m, L_m)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if razon_boussinesq_centro(B_m, L_m, mid) > FRACCION_ESFUERZO:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def exploracion_minima(cat: str, planta_ancho_m: float | None, planta_largo_m: float | None,
                       losa: bool, profundidad_excavacion_m: float) -> dict:
    if cat not in TABLA:
        raise ValueError(f"Categoría '{cat}' no reconocida ({REF}); válidas: {', '.join(TABLA)}.")
    n, z_tabla = TABLA[cat]
    criterios = {"tabla_H.3.2-1": z_tabla}
    if planta_ancho_m is not None and planta_largo_m is not None:
        B, L = sorted((planta_ancho_m, planta_largo_m))
        criterios["incremento_10pct"] = profundidad_10pct(B, L)
        if losa:
            criterios["1.5_ancho_losa"] = FACTOR_LOSA * B
    elif losa:
        raise ValueError(f"Con losa de cimentación hay que dar el ancho y el largo de la planta ({REF}).")
    gobierna = max(criterios, key=criterios.get)
    z = criterios[gobierna]
    return {"n_sondeos_min": n, "n_sondeos_a_profundidad_min": math.ceil(FRACCION_SONDEOS_PROFUNDOS * n),
            "profundidad_bajo_excavacion_m": z, "profundidad_desde_terreno_m": z + profundidad_excavacion_m,
            "criterios_m": criterios, "gobierna": gobierna}
