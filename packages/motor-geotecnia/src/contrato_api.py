"""Salida con contrato uniforme de motor-geotecnia (#136): asentamiento por consolidación y capacidad portante."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .consolidacion import asentamiento_primario, tiempo_para_grado  # noqa: E402
from .esfuerzos import esfuerzo_2a1, esfuerzo_boussinesq_centro_rect  # noqa: E402
from .portante import capacidad_portante_general  # noqa: E402

LIMITES_ASENT_TOTAL_MM = {"aislada": 300.0, "medianera": 150.0}   # NSR-10 H.4.9.2 (a 20 años), verificados en motor-concreto
_UTILIZACION_BORDE = 0.95
_PHI_BORDE_DEG = 40.0


class EstratoArcilla(BaseModel):
    espesor_m: float = Field(..., gt=0)
    z_medio_m: float = Field(..., gt=0, description="Profundidad del punto medio bajo la base de la zapata")
    sigma0_kpa: float = Field(..., gt=0, description="Esfuerzo efectivo vertical inicial en el punto medio")
    sigma_p_kpa: float = Field(..., gt=0, description="Presión de preconsolidación (= σ'0 si es normalmente consolidada)")
    cc: float = Field(..., gt=0)
    cr: float = Field(..., ge=0)
    e0: float = Field(..., gt=0)
    cv_m2_dia: float = Field(..., gt=0)
    hdr_m: float = Field(..., gt=0, description="Trayectoria de drenaje (mitad del espesor con doble drenaje)")


class SolicitudAsentamiento(BaseModel):
    q_kpa: float = Field(..., gt=0, description="Presión neta aplicada por la zapata")
    B_m: float = Field(..., gt=0)
    L_m: Optional[float] = Field(..., description="null = corrida (solo método 2a1)")
    estratos: list[EstratoArcilla] = Field(..., min_length=1, max_length=20)
    metodo: Literal["boussinesq", "2a1"]
    tipo_cimentacion: Literal["aislada", "medianera"]


def asentamiento_contrato(s: SolicitudAsentamiento) -> ResultadoMotor:
    if s.L_m is None and s.metodo == "boussinesq":
        raise ValueError("Zapata corrida: use el método 2a1; Boussinesq está implementado para áreas rectangulares (NSR-10 Título H, H.4.9).")
    capas, total_m = [], 0.0
    for e in s.estratos:
        delta = (esfuerzo_boussinesq_centro_rect(s.q_kpa, s.B_m, s.L_m, e.z_medio_m) if s.metodo == "boussinesq"
                 else esfuerzo_2a1(s.q_kpa, s.B_m, s.L_m, e.z_medio_m))
        asent = asentamiento_primario(cc=e.cc, cr=e.cr, e0=e.e0, espesor_m=e.espesor_m, sigma0_kpa=e.sigma0_kpa,
                                      delta_kpa=delta, sigma_p_kpa=e.sigma_p_kpa)
        total_m += asent
        capas.append({"delta_sigma_kpa": delta, "asentamiento_mm": asent * 1000.0,
                      "t90_dias": tiempo_para_grado(0.90, cv_m2_dia=e.cv_m2_dia, hdr_m=e.hdr_m)})
    total_mm = total_m * 1000.0
    limite = LIMITES_ASENT_TOTAL_MM[s.tipo_cimentacion]
    utilizacion = total_mm / limite
    return ResultadoMotor(
        valor={"asentamiento_total_mm": total_mm, "limite_total_mm": limite, "utilizacion": utilizacion,
               "cumple_asentamiento_total": total_mm <= limite, "estratos": capas},
        unidad_si="Asentamientos en mm; esfuerzos en kPa; tiempos en días",
        ecuacion="S = Σ [H/(1+e0)]·[Cr·log10(σ'p/σ'0) + Cc·log10(σ'f/σ'p)] (ramal de recompresión hasta σ'p); "
                 "Δσ por Boussinesq (Newmark) o 2:1; t90 de Terzaghi con U(Tv) = 1 − Σ 2/M²·exp(−M²·Tv)",
        referencia_normativa="NSR-10 Título H (H.4.9, límites de asentamiento) · Terzaghi (1943) · Boussinesq/Newmark",
        supuestos=["Solo consolidación primaria unidimensional: no incluye asentamiento inmediato ni consolidación secundaria.",
                   "Δσ en el eje de la zapata, en el punto medio de cada estrato; los estratos se tratan como independientes.",
                   f"Límite total de {limite:.0f} mm para cimentación {s.tipo_cimentacion} (NSR-10 H.4.9.2); el asentamiento diferencial y el giro (H.4.9) NO se verifican.",
                   "σ'0 y σ'p provienen del estudio geotécnico; el motor no calcula el perfil geostático ni la historia de esfuerzos."],
        en_borde_dominio=bool(utilizacion >= _UTILIZACION_BORDE),
    )


class SolicitudPortante(BaseModel):
    c_kpa: float = Field(..., ge=0)
    phi_deg: float = Field(..., ge=0, le=45)
    gamma_kn_m3: float = Field(..., gt=0)
    B_m: float = Field(..., gt=0)
    L_m: Optional[float] = Field(..., description="null = corrida")
    Df_m: float = Field(..., ge=0)
    nivel_freatico_m: Optional[float] = Field(..., ge=0, description="null = sin nivel freático (queda declarado)")
    gamma_sat_kn_m3: Optional[float] = Field(default=None, gt=0, description="Obligatorio si hay nivel freático")
    factor_seguridad: float = Field(..., ge=1.0, description="NSR-10 Tabla H.4.7-1")
    q_aplicada_kpa: float = Field(..., gt=0)


def portante_contrato(s: SolicitudPortante) -> ResultadoMotor:
    r = capacidad_portante_general(c_kpa=s.c_kpa, phi_deg=s.phi_deg, gamma_kn_m3=s.gamma_kn_m3, B_m=s.B_m, L_m=s.L_m,
                                   Df_m=s.Df_m, nivel_freatico_m=s.nivel_freatico_m, gamma_sat_kn_m3=s.gamma_sat_kn_m3)
    q_adm = r["q_ult_kpa"] / s.factor_seguridad
    utilizacion = s.q_aplicada_kpa / q_adm
    supuestos = ["Carga vertical y centrada: sin factores de inclinación ni de excentricidad.",
                 "El Título H de la NSR-10 no da una fórmula de capacidad portante; este resultado NO sustituye el estudio geotécnico (H.4.2.3).",
                 "La presión última puede disminuir al ensanchar la zapata a igual Df porque el factor de profundidad depende de Df/B "
                 "(comportamiento de las formulaciones de Hansen/Vesić); la carga última total sí crece con B.",
                 f"Factor de seguridad {s.factor_seguridad:g} suministrado por el usuario (NSR-10 Tabla H.4.7-1)."]
    if s.nivel_freatico_m is None:
        supuestos.append("Sin nivel freático: no se reduce el peso unitario ni la sobrecarga.")
    return ResultadoMotor(
        valor={**r, "q_adm_kpa": q_adm, "q_aplicada_kpa": s.q_aplicada_kpa, "utilizacion": utilizacion, "cumple": s.q_aplicada_kpa <= q_adm},
        unidad_si="Presiones en kPa",
        ecuacion="q_ult = c·Nc·sc·dc + q·Nq·sq·dq + ½·γ'·B·Nγ·sγ; Nq = e^(π tanφ)·tan²(45°+φ/2), Nc = (Nq−1)cotφ, Nγ = 2(Nq+1)tanφ; q_adm = q_ult/FS",
        referencia_normativa="Vesić (1973) · NSR-10 Título H (H.4, Tabla H.4.7-1)",
        supuestos=supuestos,
        en_borde_dominio=bool(utilizacion >= _UTILIZACION_BORDE or s.phi_deg >= _PHI_BORDE_DEG),
    )
