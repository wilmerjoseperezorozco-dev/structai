"""
Motor Acero Formado en Frio -- NSR-10 F.4. Issue #81.

Perfiles C (con o sin pestaña): propiedades brutas y sectoriales, sección efectiva (F.4.2), flexión (sección,
pandeo lateral-torsional y distorsional), cortante, interacción flexión-cortante, tensión, compresión (global, local
y distorsional), carga axial y momento combinados (F.4.3.5) y arrugamiento del alma (F.4.3.3.4). La capa con
contrato uniforme está en contrato_api.py; el espacio de diseño para #311, en espacio_diseno.py.
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
from .combinada import coeficiente_cm, flexo_compresion_uniaxial, flexo_tension_uniaxial
from .distorsional import distorsional_compresion_c, distorsional_flexion_c, propiedades_aleta
from .flexion import coeficiente_cb, interaccion_flexion_cortante, resistencia_flexion_c, resistencia_ltb_c
from .miembros import resistencia_compresion_c, resistencia_cortante, resistencia_tension
from .seccion import GeometriaC, Propiedades, propiedades_brutas

__all__ = [
    "E_ACERO_MPA", "K_NO_RIGIDIZADO", "K_RIGIDIZADO", "LAMBDA_LIMITE", "MU_ACERO",
    "ancho_efectivo", "ancho_efectivo_no_rigidizado", "ancho_efectivo_rigidizado",
    "esfuerzo_pandeo_critico", "factor_esbeltez", "factor_reduccion",
    "GeometriaC", "Propiedades", "propiedades_brutas",
    "resistencia_flexion_c", "interaccion_flexion_cortante", "resistencia_ltb_c", "coeficiente_cb",
    "distorsional_flexion_c", "distorsional_compresion_c", "propiedades_aleta",
    "coeficiente_cm", "flexo_compresion_uniaxial", "flexo_tension_uniaxial",
    "resistencia_compresion_c", "resistencia_cortante", "resistencia_tension",
]
