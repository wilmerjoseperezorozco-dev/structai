"""
Motor Vulnerabilidad Vivienda — Schemas Pydantic de entrada.
Las salidas se dejan como dict (evaluar_vulnerabilidad() ya devuelve un
dataclass fácilmente serializable con forma fija -- se convierte a dict en
la capa pública __init__.py, mismo patrón que motor-geopot).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EvaluacionVulnerabilidadRequest(BaseModel):
    """Las 15 respuestas del checklist AIS, cada una 1=baja, 2=media o
    3=alta. Usar GET /vulnerabilidad-vivienda/checklist para obtener la
    lista completa de criterios con sus 3 descripciones antes de calificar."""

    respuestas: dict[str, int] = Field(
        ...,
        description="Mapa criterio_id -> nivel (1=baja, 2=media, 3=alta). "
        "Debe incluir exactamente los 15 criterios listados en /checklist.",
    )
    municipio: Optional[str] = Field(
        None,
        description="Municipio donde está ubicada la vivienda, para "
        "enriquecer el resultado con la amenaza sísmica real (Aa/Av) del "
        "Servicio Geológico Colombiano. Opcional.",
    )

    @field_validator("respuestas")
    @classmethod
    def _no_vacio(cls, v: dict[str, int]) -> dict[str, int]:
        if not v:
            raise ValueError("'respuestas' no puede estar vacío")
        return v
