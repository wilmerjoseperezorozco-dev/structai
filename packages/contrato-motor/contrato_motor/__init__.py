"""Contrato uniforme de salida de los motores de cálculo de StructAI.

Todo resultado público de un motor se entrega como `ResultadoMotor`: valor, unidad SI, ecuación, referencia
normativa, supuestos, bandera de borde de dominio y aviso de responsabilidad profesional (no puede omitirse).
`exigir` reemplaza `tabla.get(clave, defecto)`: si la clave no existe lanza ValueError citando la norma.
"""
from __future__ import annotations

import math
from typing import Any, Mapping

from pydantic import BaseModel, Field, field_validator

AVISO_RESPONSABILIDAD = (
    "Resultado de apoyo al diseño: no sustituye el criterio, la verificación ni la firma de un ingeniero "
    "matriculado responsable del proyecto (Ley 400 de 1997; NSR-10, Título A)."
)


class ResultadoMotor(BaseModel):
    valor: Any
    unidad_si: str
    ecuacion: str
    referencia_normativa: str
    supuestos: list[str]
    en_borde_dominio: bool
    aviso_responsabilidad_profesional: str = AVISO_RESPONSABILIDAD
    advertencias: list[str] = Field(default_factory=list)

    @field_validator("unidad_si", "ecuacion", "referencia_normativa", "aviso_responsabilidad_profesional")
    @classmethod
    def _no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("el campo no puede estar vacío")
        return v

    @field_validator("valor")
    @classmethod
    def _finito(cls, v: Any) -> Any:
        if isinstance(v, float) and not math.isfinite(v):
            raise ValueError("el valor debe ser finito")
        return v


def exigir(clave: Any, tabla: Mapping[Any, Any], norma: str, que: str) -> Any:
    """Devuelve tabla[clave] o lanza ValueError citando la norma (sin valores por defecto)."""
    if clave not in tabla:
        raise ValueError(
            f"{que} '{clave}' no reconocido ({norma}): no se asume ningún valor por defecto. "
            f"Valores válidos: {', '.join(map(str, tabla))}."
        )
    return tabla[clave]
