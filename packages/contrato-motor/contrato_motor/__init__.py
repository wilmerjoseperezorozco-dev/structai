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
    def _nativo_y_finito(cls, v: Any) -> Any:
        return _normalizar(v)

    @field_validator("supuestos")
    @classmethod
    def _con_supuestos(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("debe declarar al menos un supuesto")
        return v


def _normalizar(v: Any) -> Any:
    """Convierte tipos numpy a nativos (serialización JSON) y exige finitud en toda la estructura."""
    if hasattr(v, "item") and not isinstance(v, (dict, list, tuple)):
        v = v.item()
    if isinstance(v, dict):
        return {k: _normalizar(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_normalizar(x) for x in v]
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
