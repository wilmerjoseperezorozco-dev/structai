"""
Motor Vulnerabilidad Vivienda — capa pública consumida por
apps/api/routers/vulnerabilidad_vivienda.py.

Mismo patrón que motor-geopot/src/__init__.py: cada wrapper recibe el
Request Pydantic real y delega en la lógica de dominio pura de
checklist.py, devolviendo dict.
"""

from __future__ import annotations

from dataclasses import asdict

from .checklist import (
    ASPECTO_LABEL,
    ASPECTOS_ORDEN,
    CRITERIOS,
    CRITERIOS_POR_ID,
    PESO_ASPECTO,
    Criterio,
    NivelCriterio,
    ResultadoAspecto,
    ResultadoVulnerabilidad,
    evaluar_vulnerabilidad,
    listar_criterios,
)
from .schemas import EvaluacionVulnerabilidadRequest

__all__ = [
    "ASPECTO_LABEL",
    "ASPECTOS_ORDEN",
    "CRITERIOS",
    "CRITERIOS_POR_ID",
    "PESO_ASPECTO",
    "Criterio",
    "NivelCriterio",
    "ResultadoAspecto",
    "ResultadoVulnerabilidad",
    "EvaluacionVulnerabilidadRequest",
    "consultar_checklist",
    "evaluar",
]


def consultar_checklist() -> list[dict]:
    return listar_criterios()


def evaluar(req: EvaluacionVulnerabilidadRequest) -> dict:
    try:
        resultado = evaluar_vulnerabilidad(req.respuestas)
    except ValueError as e:
        return {"error": str(e)}

    return {
        "calificacion_global": resultado.calificacion_global,
        "clasificacion": resultado.clasificacion,
        "aspectos": [asdict(a) for a in resultado.aspectos],
        "criterios_evaluados": resultado.criterios_evaluados,
        "municipio": req.municipio,
        "metodologia": (
            "Manual de Construcción, Evaluación y Rehabilitación Sismo "
            "Resistente de Viviendas de Mampostería (AIS/FOREC, 2004), "
            "Capítulo II — checklist ponderado de 15 criterios, alcance "
            "Título E de la NSR-10 (vivienda de 1-2 pisos en mampostería)."
        ),
    }
