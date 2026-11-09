"""Funciones públicas de motor-concreto con contrato uniforme (`contrato_motor.ResultadoMotor`).

Las solicitudes no traen valores por defecto físicos: suelo, agua, sobrecarga y sismo se declaran siempre.
Lo que no se verifica (asentamiento sin ks, agua ausente, cota de profundidad asumida) queda escrito en `supuestos`.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .excavacion_estabilidad import SueloExc, factor_seguridad_requerido, factor_seguridad_talud, perfil_talud  # noqa: E402
from .viga import Materiales  # noqa: E402
from .zapata import CargasZapata, SUPUESTOS as SUPUESTOS_ZAPATA, Suelo, disenar  # noqa: E402

_FRACCION_BORDE_FS = 0.05      # |FS/FSrequerido − 1| < 5 % se considera borde
_UTILIZACION_BORDE = 0.95      # demanda/capacidad ≥ 95 % en alguna verificación
_LADO_MAX_M = 6.0              # tope de la búsqueda de lados en zapata.disenar
_H_MAX_MM = 1000.0


class SolicitudZapata(BaseModel):
    c1_mm: float = Field(..., gt=0)
    c2_mm: float = Field(..., gt=0)
    P_serv: float = Field(..., gt=0, description="kN, compresión positiva")
    P_u: float = Field(..., gt=0, description="kN")
    Mx_serv: float = 0.0
    My_serv: float = 0.0
    Mx_u: float = 0.0
    My_u: float = 0.0
    q_adm_kpa: float = Field(..., gt=0, description="Capacidad admisible bruta del estudio geotécnico (NSR-10 H.4.2.3)")
    profundidad_desplante_m: float = Field(..., gt=0)
    peso_unitario_relleno_kn_m3: float = Field(..., gt=0)
    asentamiento_max_mm: float = Field(..., gt=0)
    ks_kn_m3: Optional[float] = Field(..., description="Módulo de balasto; null = NO se verifica asentamiento (queda declarado)")
    fc_mpa: float = Field(..., gt=0)
    fy_mpa: float = Field(..., gt=0)


class SolicitudTalud(BaseModel):
    altura_m: float = Field(..., gt=0)
    angulo_deg: float = Field(..., gt=0, le=90)
    gamma_kn_m3: float = Field(..., gt=0)
    c_kpa: float = Field(..., ge=0)
    phi_deg: float = Field(..., ge=0, lt=60)
    prof_freatico_m: Optional[float] = Field(..., ge=0, description="null = sin agua (queda declarado)")
    sobrecarga_kpa: float = Field(..., ge=0)
    kh: float = Field(..., ge=0)
    estado: Literal["diseno", "construccion"]
    prof_estrato_firme_m: Optional[float] = Field(default=None, gt=0)


def disenar_zapata_contrato(s: SolicitudZapata) -> ResultadoMotor:
    suelo = Suelo(q_adm_kpa=s.q_adm_kpa, profundidad_desplante_m=s.profundidad_desplante_m,
                  peso_unitario_relleno_kn_m3=s.peso_unitario_relleno_kn_m3,
                  ks_kn_m3=0.0 if s.ks_kn_m3 is None else s.ks_kn_m3, asentamiento_max_mm=s.asentamiento_max_mm)
    cargas = CargasZapata(P_serv=s.P_serv, P_u=s.P_u, Mx_serv=s.Mx_serv, My_serv=s.My_serv, Mx_u=s.Mx_u, My_u=s.My_u)
    sols = disenar(s.c1_mm, s.c2_mm, cargas, suelo, Materiales(fc=s.fc_mpa, fy=s.fy_mpa, fyt=s.fy_mpa), top=1)
    if not sols:
        raise ValueError(
            "Ninguna zapata de lados ≤ 6 m y espesor ≤ 1000 mm cumple las verificaciones de NSR-10 (Título C, "
            "capítulos 11 y 15, y Título H, H.4): aumentar q_adm, mejorar el suelo o usar cimentación profunda."
        )
    z = sols[0]
    utilizacion = max((v.demanda / v.capacidad for v in z.verificaciones if v.capacidad > 0), default=0.0)
    borde = utilizacion >= _UTILIZACION_BORDE or z.h >= _H_MAX_MM or max(z.Lx, z.Ly) >= _LADO_MAX_M
    supuestos = list(SUPUESTOS_ZAPATA)
    if s.ks_kn_m3 is None:
        supuestos.append("Asentamiento NO verificado: no se entregó ks (NSR-10 H.4.9 queda pendiente del estudio geotécnico).")
    return ResultadoMotor(
        valor={"Lx_m": z.Lx, "Ly_m": z.Ly, "h_mm": z.h, "d_mm": z.d, "barras_x": z.barras_x, "barras_y": z.barras_y,
               "q_max_serv_kpa": z.q_max_serv, "q_min_serv_kpa": z.q_min_serv, "volumen_concreto_m3": z.volumen_concreto_m3,
               "masa_acero_kg": z.masa_acero_kg, "cumple": z.cumple, "utilizacion_maxima": utilizacion,
               "verificaciones": [{"norma": v.norma, "nombre": v.nombre, "demanda": v.demanda, "capacidad": v.capacidad,
                                   "unidad": v.unidad, "cumple": v.cumple} for v in z.verificaciones]},
        unidad_si="Lx, Ly en m; h, d en mm; presiones en kPa; volumen en m³; masa en kg",
        ecuacion="Presión de contacto q = P/A ± M/S ≤ q_adm; flexión As por bloque rectangular de Whitney; cortante en una y dos direcciones; "
                 "barrido de lados y espesores con menor volumen equivalente (concreto + acero/7850)",
        referencia_normativa="NSR-10 Título C (C.11, C.15) y Título H (H.4)",
        supuestos=supuestos, en_borde_dominio=bool(borde), advertencias=list(z.advertencias),
    )


def evaluar_talud_contrato(s: SolicitudTalud) -> ResultadoMotor:
    suelo = SueloExc(gamma=s.gamma_kn_m3, c_kpa=s.c_kpa, phi_deg=s.phi_deg)
    res = factor_seguridad_talud(perfil_talud(s.altura_m, s.angulo_deg), suelo, prof_freatico=s.prof_freatico_m,
                                 sobrecarga_kpa=s.sobrecarga_kpa, kh=s.kh, prof_estrato_firme=s.prof_estrato_firme_m)
    fs_req = factor_seguridad_requerido(s.estado, s.kh > 0)
    borde_busqueda = bool(res.en_borde_dominio)
    borde = borde_busqueda or abs(res.fs / fs_req - 1.0) < _FRACCION_BORDE_FS
    supuestos = ["Grieta de tracción seca; agua sin red de flujo; presión de poros acotada a la superficie del terreno."]
    supuestos.append("Sin agua: no se declaró nivel freático." if s.prof_freatico_m is None else f"Nivel freático a {s.prof_freatico_m} m bajo la corona.")
    if s.prof_estrato_firme_m is None:
        supuestos.append("Profundidad de la superficie de falla limitada a 1,2·H por defecto de búsqueda (no hay estrato firme declarado): el FS en φ=0 con sismo depende de esa cota.")
    return ResultadoMotor(
        valor={"fs": res.fs, "fs_requerido": fs_req, "cumple": bool(res.fs >= fs_req), "radio_m": res.radio,
               "requiere_abatimiento": bool(res.requiere_abatimiento), "en_borde_busqueda": borde_busqueda},
        unidad_si="FS adimensional; radio en m",
        ecuacion="Bishop simplificado por equilibrio límite: FS = Σ[(c'b + (W−ub)tanφ')/mα]/ΣW sinα, con mα = cosα + sinα·tanφ'/FS (iterativo); círculo crítico por búsqueda",
        referencia_normativa="NSR-10 Título H, H.2.4 (Tabla H.2.4-1, factores de seguridad); Bishop (1955)",
        supuestos=supuestos, en_borde_dominio=bool(borde),
    )
