"""Pórtico plano por rigidez directa con contrato uniforme (`contrato_motor.ResultadoMotor`)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .portico import Caso, Elemento, Nodo, Portico  # noqa: E402

_COND_BORDE = 1e10           # el solver rechaza > 1e14; entre ambos el resultado pierde ≥ 10 cifras
_PUNTOS_DIAGRAMA = 41


class ElementoIn(BaseModel):
    i: int = Field(..., ge=0)
    j: int = Field(..., ge=0)
    E: float = Field(..., gt=0, description="kN/m²")
    A: float = Field(..., gt=0, description="m²")
    I: float = Field(..., gt=0, description="m⁴")


class CasoIn(BaseModel):
    nombre: str
    nodales: dict[int, tuple[float, float, float]] = Field(default_factory=dict, description="nodo → (fx kN, fy kN, mz kN·m)")
    uniformes: dict[int, float] = Field(default_factory=dict, description="elemento horizontal → w kN/m hacia abajo")


class SolicitudPortico(BaseModel):
    nodos: list[tuple[float, float]] = Field(..., min_length=2, description="(x m, y m)")
    elementos: list[ElementoIn] = Field(..., min_length=1)
    apoyos: dict[int, tuple[bool, bool, bool]] = Field(..., description="nodo → (ux, uy, rz) restringidos")
    casos: list[CasoIn] = Field(..., min_length=1)


def resolver_portico_contrato(s: SolicitudPortico) -> ResultadoMotor:
    n = len(s.nodos)
    for e in s.elementos:
        if e.i >= n or e.j >= n:
            raise ValueError("Un elemento referencia un nodo inexistente")
    modelo = Portico([Nodo(x, y) for x, y in s.nodos], [Elemento(e.i, e.j, e.E, e.A, e.I) for e in s.elementos], s.apoyos)
    lib = modelo._libres
    cond = float(np.linalg.cond(modelo._K[np.ix_(lib, lib)])) if lib.size else 1.0
    casos: dict[str, dict] = {}
    for c in s.casos:
        r = modelo.resolver(Caso(c.nombre, c.nodales, c.uniformes))
        m_max = 0.0
        for idx, el in enumerate(modelo.elementos):
            xs = np.linspace(0.0, modelo.longitud(el), _PUNTOS_DIAGRAMA)
            m_max = max(m_max, float(np.max(np.abs(modelo.diagrama(r, idx, xs)["M"]))))
        carga_y = sum(f[1] for f in c.nodales.values()) - sum(
            w * modelo.longitud(modelo.elementos[k]) for k, w in c.uniformes.items())
        reac_y = sum(v[1] for v in r.reacciones.values())
        casos[c.nombre] = {
            "reacciones": {str(k): list(v) for k, v in r.reacciones.items()},
            "flecha_max_m": float(np.max(np.abs(r.u[:, 1]))),
            "desplazamiento_horizontal_max_m": float(np.max(np.abs(r.u[:, 0]))),
            "momento_max_knm": m_max,
            "residuo_equilibrio_vertical_kn": float(reac_y + carga_y),
        }
    return ResultadoMotor(
        valor={"casos": casos, "numero_condicion": cond},
        unidad_si="reacciones en kN y kN·m; desplazamientos en m; momentos en kN·m",
        ecuacion="Rigidez directa K·u = F con elementos viga-columna de Euler-Bernoulli (3 gdl/nodo); reacciones R = K·u − F",
        referencia_normativa="Método matricial de rigidez directa (análisis estructural lineal); combinaciones de carga según NSR-10 B.2 las define el llamador",
        supuestos=["Elementos prismáticos, material lineal, sin segundo orden ni deformación por cortante.",
                   "Cargas uniformes solo sobre elementos horizontales.",
                   "Los efectos de agrietamiento se representan reduciendo I desde fuera."],
        en_borde_dominio=bool(cond > _COND_BORDE),
    )
