"""Diseño integral de pórtico (vigas + columnas, costo APU) con contrato uniforme (`contrato_motor.ResultadoMotor`).

La rejilla pedida está acotada para que una solicitud no pueda pedir un cómputo ilimitado.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .diseno_integral import diseno_integral  # noqa: E402
from .diseno_portico import DERIVA_MAX, ProyectoPortico  # noqa: E402

_MAX_COLUMNAS, _MAX_B, _MAX_H, _MAX_VANOS, _MAX_PISOS = 8, 8, 12, 6, 8
_FRACCION_DERIVA_BORDE = 0.95
_SCWB_BORDE = 1.05           # razón ΣMnc/(1,2·ΣMnb) − 1 menor a 5 %


class SolicitudDisenoIntegral(BaseModel):
    luces_m: list[float] = Field(..., min_length=1, max_length=_MAX_VANOS)
    alturas_piso_m: list[float] = Field(..., min_length=1, max_length=_MAX_PISOS)
    carga_muerta_kn_m: float = Field(..., ge=0)
    carga_viva_kn_m: float = Field(..., ge=0)
    calidad_concreto: str
    fy_mpa: float = Field(..., gt=0)
    recubrimiento_mm: float = Field(..., gt=0)
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    codigo_dane: Optional[str] = None
    capacidad: Optional[str] = Field(default=None, description="DMI | DMO | DES; sin municipio es obligatoria")
    perfil_suelo: str = Field(..., description="A..E (NSR-10 A.2.4)")
    grupo_uso: str = Field(..., description="I, II, III, IV (Tabla A.2.5-1)")
    columnas_mm: list[float] = Field(..., min_length=1, max_length=_MAX_COLUMNAS)
    b_mm: list[float] = Field(..., min_length=1, max_length=_MAX_B)
    h_mm: list[float] = Field(..., min_length=1, max_length=_MAX_H)


def disenar_integral_contrato(s: SolicitudDisenoIntegral) -> ResultadoMotor:
    p = ProyectoPortico(
        luces_m=tuple(s.luces_m), alturas_piso_m=tuple(s.alturas_piso_m), carga_muerta_kn_m=s.carga_muerta_kn_m,
        carga_viva_kn_m=s.carga_viva_kn_m, calidad_concreto=s.calidad_concreto, fy_mpa=s.fy_mpa,
        recubrimiento_mm=s.recubrimiento_mm, municipio=s.municipio, departamento=s.departamento, codigo_dane=s.codigo_dane,
        capacidad=s.capacidad, perfil_suelo=s.perfil_suelo, grupo_uso=s.grupo_uso)
    informe = diseno_integral(p, top=1, columnas_mm=tuple(s.columnas_mm), grilla=(tuple(s.b_mm), tuple(s.h_mm)), verificar_escalar=True)
    o = informe.optimo
    if o is None:
        raise ValueError(
            "Ninguna combinación de la rejilla cumple deriva (NSR-10 A.6.4), estabilidad (C.10.10.5.2), flexo-compresión y "
            f"columna fuerte–viga débil (C.21.6.2) ({informe.evaluadas} evaluadas): ampliar la rejilla o reducir las cargas."
        )
    en_borde = (
        o.c in (min(s.columnas_mm), max(s.columnas_mm)) and len(s.columnas_mm) > 1
        or o.b in (min(s.b_mm), max(s.b_mm)) and len(s.b_mm) > 1
        or o.h in (min(s.h_mm), max(s.h_mm)) and len(s.h_mm) > 1
        or (o.deriva == o.deriva and o.deriva >= _FRACCION_DERIVA_BORDE * DERIVA_MAX)
        or (o.razon_scwb == o.razon_scwb and o.razon_scwb < _SCWB_BORDE)
    )
    nan_a_none = lambda x: None if x != x else float(x)  # noqa: E731
    return ResultadoMotor(
        valor={"c_mm": o.c, "b_mm": o.b, "h_mm": o.h, "costo_vigas_cop": float(o.costo_vigas), "costo_columnas_cop": float(o.costo_columnas),
               "costo_directo_cop": float(o.costo_directo), "deriva": nan_a_none(o.deriva), "q_max": nan_a_none(o.q_max),
               "razon_scwb": nan_a_none(o.razon_scwb), "capacidad": informe.capacidad, "evaluadas": informe.evaluadas,
               "factibles": informe.factibles},
        unidad_si="Secciones en mm; costos en COP (APU); deriva y estabilidad adimensionales",
        ecuacion="Mínimo de costo total (vigas + columnas) sobre la rejilla declarada, sujeto a deriva Δ/hp ≤ 1,0 %, estabilidad Q ≤ límite, "
                 "flexo-compresión con todas las combinaciones, ΣMnc ≥ 1,2·ΣMnb y cortante por capacidad; análisis por rigidez directa",
        referencia_normativa="NSR-10 Título A (A.2, A.3, A.4, A.6.4) y Título C (C.10.10.5.2, C.21.6)",
        supuestos=list(informe.supuestos), en_borde_dominio=bool(en_borde),
    )
