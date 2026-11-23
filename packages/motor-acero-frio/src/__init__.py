"""
Motor Acero Formado en Frio -- NSR-10 F.4. Issue #81.

Perfiles C (con o sin pestaña): propiedades brutas y sectoriales, sección efectiva (F.4.2), flexión por
resistencia de la sección (F.4.3.3.1.1), cortante (F.4.3.3.2.1), interacción (F.4.3.3.3), tensión (F.4.3.2)
y compresión (F.4.3.4.1). La capa con contrato uniforme está en contrato_api.py.
"""
from __future__ import annotations

from .ancho_efectivo import (
    E_ACERO_MPA,
    K_NO_RIGIDIZADO,
    K_RIGIDIZADO,
    LAMBDA_LIMITE,
    MU_ACERO,
    ancho_efectivo,
    ancho_efectivo_no_rigidizado,
    ancho_efectivo_rigidizado,
    esfuerzo_pandeo_critico,
    factor_esbeltez,
    factor_reduccion,
)
from .flexion import interaccion_flexion_cortante, resistencia_flexion_c
from .miembros import resistencia_compresion_c, resistencia_cortante, resistencia_tension
from .seccion import GeometriaC, Propiedades, propiedades_brutas

__all__ = [
    "E_ACERO_MPA", "K_NO_RIGIDIZADO", "K_RIGIDIZADO", "LAMBDA_LIMITE", "MU_ACERO",
    "ancho_efectivo", "ancho_efectivo_no_rigidizado", "ancho_efectivo_rigidizado",
    "esfuerzo_pandeo_critico", "factor_esbeltez", "factor_reduccion",
    "GeometriaC", "Propiedades", "propiedades_brutas",
    "resistencia_flexion_c", "interaccion_flexion_cortante",
    "resistencia_compresion_c", "resistencia_cortante", "resistencia_tension",
]
