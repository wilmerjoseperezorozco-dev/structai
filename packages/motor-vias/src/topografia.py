"""
Topografía vial — nivelación diferencial y control de cierre altimétrico
(Guía de estandarización INVIAS 2023 / IDU / IGAC, NTC 6271).

Implementa la tolerancia estándar de error de cierre en nivelación
geométrica: E_max = C * sqrt(K), con K la longitud del circuito/tramo
nivelado (km) y C el coeficiente (mm) de la entidad de referencia
colombiana (INVIAS, IDU o IGAC).

NOTA DE ALCANCE (líneas 6285-12610 del documento fuente):
Ese tramo cubre topografía general, teodolito y GNSS/MAGNA-SIRGAS, pero es
mayoritariamente un generador de procedimientos/listas de verificación en
prosa: clases "Motor*" que arman strings de actividades, equipos y
recomendaciones a partir de reglas simples (comparaciones y lookups en
diccionarios), sin cálculo numérico real. No hay ajuste de poligonales
(Bowditch/regla de la brújula), transformación de coordenadas, ni
conversión UTM/MAGNA-SIRGAS codificadas — esos temas solo se mencionan en
texto descriptivo. La única fórmula de ingeniería explícita, con
coeficientes numéricos reutilizables, es la tolerancia de cierre de
nivelación (C·√K) para INVIAS/IDU/IGAC, implementada en este módulo.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import sqrt


class EstandarNivelacion(Enum):
    """Entidades colombianas de referencia para tolerancia de cierre altimétrico."""

    INVIAS = "invias"
    IDU = "idu"
    IGAC = "igac"


@dataclass(frozen=True)
class CoeficienteCierre:
    """Coeficiente C (mm) de la fórmula de tolerancia C*sqrt(K) y datos asociados."""

    coeficiente_mm: float
    precision_altimetrica_cm_km: float
    equipo_recomendado: str


COEFICIENTES_CIERRE = {
    EstandarNivelacion.INVIAS: CoeficienteCierre(
        coeficiente_mm=10.0,
        precision_altimetrica_cm_km=2.0,
        equipo_recomendado="Nivel automático de precisión",
    ),
    EstandarNivelacion.IDU: CoeficienteCierre(
        coeficiente_mm=5.0,
        precision_altimetrica_cm_km=1.0,
        equipo_recomendado="Nivel digital o automático",
    ),
    EstandarNivelacion.IGAC: CoeficienteCierre(
        coeficiente_mm=2.0,
        precision_altimetrica_cm_km=0.5,
        equipo_recomendado="Nivel geodésico de alta precisión",
    ),
}


def error_cierre_permisible_mm(
    distancia_km: float,
    estandar: EstandarNivelacion = EstandarNivelacion.INVIAS,
) -> float:
    """
    Tolerancia de error de cierre para nivelación geométrica/diferencial:

        E_max = C * sqrt(K)

    K es la longitud del circuito/tramo nivelado en km (ida + vuelta, o
    perímetro del circuito cerrado); C es el coeficiente (mm) de la entidad
    de referencia (INVIAS=10, IDU=5, IGAC=2).
    """
    if distancia_km < 0:
        raise ValueError("distancia_km debe ser mayor o igual que 0")
    coef = COEFICIENTES_CIERRE[estandar]
    return coef.coeficiente_mm * sqrt(distancia_km)


@dataclass
class ResultadoCierreNivelacion:
    """Resultado de comparar el cierre medido en campo contra la tolerancia."""

    error_medido_mm: float
    error_permisible_mm: float
    distancia_km: float
    estandar: EstandarNivelacion
    cumple: bool
    holgura_mm: float


def verificar_cierre_nivelacion(
    error_medido_mm: float,
    distancia_km: float,
    estandar: EstandarNivelacion = EstandarNivelacion.INVIAS,
) -> ResultadoCierreNivelacion:
    """
    Compara el error de cierre medido en campo (suma algebraica de las
    diferencias de nivelación ida/vuelta, o cierre del circuito) contra la
    tolerancia permisible C*sqrt(K) del estándar seleccionado.
    """
    error_medido_abs = abs(error_medido_mm)
    permisible = error_cierre_permisible_mm(distancia_km, estandar)
    return ResultadoCierreNivelacion(
        error_medido_mm=error_medido_abs,
        error_permisible_mm=permisible,
        distancia_km=distancia_km,
        estandar=estandar,
        cumple=error_medido_abs <= permisible,
        holgura_mm=permisible - error_medido_abs,
    )
