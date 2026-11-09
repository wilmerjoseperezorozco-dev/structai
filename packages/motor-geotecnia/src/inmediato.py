"""Asentamiento inmediato (elástico) y secundario (Cα) de cimentaciones superficiales.

Inmediato: semiespacio elástico, área rectangular flexible uniformemente cargada (Timoshenko & Goodier; Harr).
Secundario: Ss = Cα·H/(1+e0)·log10(t/tp). Referencia normativa de límites: NSR-10 Título H (H.4.9).
"""
from __future__ import annotations

import math
from typing import Literal

_REF = "NSR-10 Título H (H.4.9) / elasticidad lineal"


def _requerir(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise ValueError(f"{mensaje} ({_REF}).")


def _finito_pos(nombre: str, v: float) -> None:
    _requerir(math.isfinite(v) and v > 0, f"{nombre} debe ser finito y positivo; se recibió {v!r}")


def _factor_esquina(m: float) -> float:
    """(1/π)[ln((1+√(m²+1))/m) + m·ln(m+√(m²+1))]: asentamiento en la esquina de un rectángulo flexible, m = L/B."""
    r = math.sqrt(m * m + 1.0)
    return (math.log((1.0 + r) / m) + m * math.log(m + r)) / math.pi


def asentamiento_inmediato_flexible(*, q_kpa: float, B_m: float, L_m: float, es_kpa: float, nu: float,
                                    ubicacion: Literal["centro", "esquina"]) -> float:
    """Asentamiento elástico (m) bajo el centro o la esquina de una zapata flexible B×L (B ≤ L)."""
    _requerir(math.isfinite(q_kpa) and q_kpa >= 0, f"La presión q debe ser finita y no negativa; se recibió {q_kpa!r}")
    _finito_pos("B", B_m)
    _finito_pos("Es", es_kpa)
    _requerir(math.isfinite(L_m) and L_m >= B_m, "Se requiere L finita y L ≥ B (B es la dimensión menor)")
    _requerir(math.isfinite(nu) and 0.0 <= nu < 0.5, f"El módulo de Poisson debe estar en [0, 0,5); se recibió {nu!r}")
    _requerir(ubicacion in ("centro", "esquina"), f"La ubicación debe ser 'centro' o 'esquina'; se recibió {ubicacion!r}")
    esquina = q_kpa * B_m * (1.0 - nu ** 2) / es_kpa * _factor_esquina(L_m / B_m)
    return 2.0 * esquina if ubicacion == "centro" else esquina


def asentamiento_secundario(*, c_alfa: float, e0: float, espesor_m: float, t_fin_dias: float, t_primaria_dias: float) -> float:
    """Compresión secundaria (m) entre el fin de la primaria (tp) y el horizonte t_fin."""
    for nombre, v in (("Cα", c_alfa), ("e0", e0), ("espesor", espesor_m), ("t_fin", t_fin_dias), ("tp", t_primaria_dias)):
        _requerir(math.isfinite(v), f"{nombre} debe ser finito")
    _requerir(c_alfa >= 0, "El coeficiente de compresión secundaria Cα no puede ser negativo")
    _finito_pos("e0", e0)
    _finito_pos("espesor", espesor_m)
    _finito_pos("tp (fin de la primaria)", t_primaria_dias)
    _requerir(t_fin_dias >= t_primaria_dias, "El horizonte de análisis no puede ser anterior al fin de la consolidación primaria")
    return c_alfa * espesor_m / (1.0 + e0) * math.log10(t_fin_dias / t_primaria_dias)
