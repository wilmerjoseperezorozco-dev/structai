"""Edificio 3D con diafragmas rígidos y fuerza horizontal equivalente, con contrato uniforme (#274, F1)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .portico3d import Diafragma, Elemento3D, Nodo3D, Portico3D  # noqa: E402
from .sismo3d import Piso, analizar_fhe  # noqa: E402

_COND_BORDE = 1e10
_POS = dict(gt=0, allow_inf_nan=False)


class Elemento3DIn(BaseModel):
    model_config = ConfigDict(strict=True)
    i: int = Field(..., ge=0)
    j: int = Field(..., ge=0)
    E: float = Field(..., le=1e9, description="kN/m²", **_POS)
    G: float = Field(..., le=1e9, description="kN/m²", **_POS)
    A: float = Field(..., le=1e3, description="m²", **_POS)
    Iy: float = Field(..., le=1e4, description="m⁴", **_POS)
    Iz: float = Field(..., le=1e4, description="m⁴", **_POS)
    J: float = Field(..., le=1e4, description="m⁴", **_POS)
    eje_ref: Optional[tuple[float, float, float]] = None


class PisoIn(BaseModel):
    model_config = ConfigDict(strict=True)
    nombre: str = Field(..., min_length=1, max_length=40)
    nodos: list[int] = Field(..., min_length=1)
    x_cm: float = Field(..., allow_inf_nan=False)
    y_cm: float = Field(..., allow_inf_nan=False)
    altura_entrepiso_m: float = Field(..., le=50, **_POS)
    dim_x_m: float = Field(..., le=1000, **_POS)
    dim_y_m: float = Field(..., le=1000, **_POS)
    carga_vertical_kn: float = Field(..., ge=0, le=1e8, allow_inf_nan=False)
    fs_x_kn: float = Field(..., ge=0, le=1e8, allow_inf_nan=False, description="Fuerza sísmica del piso Fs (sin dividir por R)")
    fs_y_kn: float = Field(..., ge=0, le=1e8, allow_inf_nan=False)


class SolicitudEdificio3D(BaseModel):
    model_config = ConfigDict(strict=True)
    nodos: list[tuple[float, float, float]] = Field(..., min_length=2, max_length=20000)
    elementos: list[Elemento3DIn] = Field(..., min_length=1, max_length=40000)
    apoyos: dict[int, tuple[bool, bool, bool, bool, bool, bool]]
    pisos: list[PisoIn] = Field(..., min_length=1, max_length=200, description="De abajo hacia arriba")
    sistema_deriva: Literal["general", "mamposteria_cortante"] = Field(
        ..., description="Tabla A.6.4-1: 'general' = concreto, acero, madera o mampostería que falla por flexión")
    secciones_fisuradas: bool = Field(..., description="A.6.4.1.1: si las inercias ya están fisuradas, deriva × 0,7")


def edificio_3d_fhe_contrato(s: SolicitudEdificio3D) -> ResultadoMotor:
    modelo = Portico3D([Nodo3D(*n) for n in s.nodos],
                       [Elemento3D(e.i, e.j, e.E, e.G, e.A, e.Iy, e.Iz, e.J, e.eje_ref) for e in s.elementos],
                       {k: v for k, v in s.apoyos.items()},
                       [Diafragma(p.nombre, tuple(p.nodos), p.x_cm, p.y_cm) for p in s.pisos])
    pisos = [Piso(p.nombre, p.altura_entrepiso_m, p.dim_x_m, p.dim_y_m, p.carga_vertical_kn) for p in s.pisos]
    r = analizar_fhe(modelo, pisos, [p.fs_x_kn for p in s.pisos], [p.fs_y_kn for p in s.pisos],
                     s.sistema_deriva, s.secciones_fisuradas)
    cond = modelo.numero_condicion()
    adv = []
    if r["irregularidad_torsional"] != "ninguna":
        adv.append(f"Irregularidad torsional {r['irregularidad_torsional']} (Tabla A.3-6): se amplificó la torsión "
                   "accidental con Ax (A.3.6-2) y la deriva se evaluó en los ejes de columna (A.6.3-1). "
                   "Revise si A.3.4.2 exige análisis dinámico (F2, próximamente).")
    if r["Qi_max"] > 0.10:
        adv.append("Qi > 0,10 en algún piso: los efectos P-Δ son obligatorios (A.6.2.3) y aún no se incluyen en los "
                   "desplazamientos (F3, próximamente).")
    if r["sin_limite_un_piso"]:
        adv.append("Edificación de un piso: sin límite de deriva si muros, particiones y cielorrasos la acomodan (A.6.4.1.5).")
    return ResultadoMotor(
        valor=r, unidad_si="desplazamientos y derivas en m; derivas relativas adimensionales (fracción de hpi)",
        ecuacion="K·u = F en 3D con diafragma rígido (ux, uy, rz del centro de masa); Mz = ±0,05·L⊥·Fs; "
                 "δtot = |δcm| + |r·θ|; deriva ≤ límite·hpi (×0,7 si fisuradas)",
        referencia_normativa="NSR-10 A.3.6.7, Tabla A.3-6 (1aP/1bP), A.3.6-2, A.6.2, A.6.3, A.6.4 (Tabla A.6.4-1)",
        supuestos=["Fuerzas por piso Fs de A.4.3 (sin dividir por R), calculadas por el llamador (motor-geopot).",
                   "Diafragmas rígidos en su plano, con el nodo maestro en el centro de masa del piso.",
                   "Elementos prismáticos de Euler-Bernoulli, material lineal, sin P-Δ en los desplazamientos.",
                   "Se evalúan 4 casos: Ex y Ey, cada uno con la masa corrida a ambos lados (±5 %)."],
        en_borde_dominio=bool(cond > _COND_BORDE or r["Qi_max"] > 0.10),
        advertencias=adv + ["Efectos ortogonales (A.3.6.3) y análisis dinámico (A.5): próximamente."])
