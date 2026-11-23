"""Salida con contrato uniforme de motor-geotecnia (#136).

Asentamiento primario; asentamiento total a 20 años (inmediato + consolidación + secundario, H.4.8.4 y H.4.9.2);
asentamiento diferencial y giro (Tabla H.4.9-1 y H.4.9.4); consolidación multicapa; Monte Carlo; y capacidad portante
centrada o con excentricidad e inclinación (H.4.10), verificada contra la Tabla H.4.7-1.
Cotejado con la NSR-10 impresa (págs. H-17 a H-19).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

import numpy as np
from pydantic import BaseModel, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .consolidacion import asentamiento_primario, factor_tiempo, grado_consolidacion, tiempo_para_grado  # noqa: E402
from .esfuerzos import esfuerzo_2a1, esfuerzo_boussinesq_centro_rect  # noqa: E402
from .inmediato import asentamiento_inmediato_flexible, asentamiento_secundario  # noqa: E402
from .montecarlo import simular_asentamiento_primario  # noqa: E402
from .multicapa import consolidacion_multicapa  # noqa: E402
from .portante import capacidad_portante_excentrica_inclinada, capacidad_portante_general  # noqa: E402

LIMITES_ASENT_TOTAL_MM = {"aislada": 300.0, "medianera": 150.0}   # NSR-10 H.4.9.2 (a 20 años), cotejado con la impresa (H-18)
HORIZONTE_DIAS = 20 * 365.25                                       # H.4.9.2: asentamientos totales calculados a 20 años
# Tabla H.4.9-1 (H-19): Δmax = ℓ / divisor, ℓ = distancia entre apoyos o columnas
DIVISOR_DIFERENCIAL = {
    "muros_acabados_susceptibles": 1000.0,      # (a) muros y acabados susceptibles de dañarse con asentamientos menores
    "muros_de_carga": 500.0,                    # (b) muros de carga en concreto o en mampostería
    "porticos_concreto": 300.0,                 # (c) pórticos en concreto, sin acabados susceptibles
    "estructura_metalica": 160.0,               # (d) estructura metálica, sin acabados susceptibles
}
DIVISOR_GIRO = 250.0                            # H.4.9.4: el giro no puede sobrepasar localmente ℓ/250
# Tabla H.4.7-1 (H-17): factores de seguridad indirectos mínimos para capacidad portante
FS_MINIMO = {"muerta_viva_normal": 3.0, "muerta_viva_maxima": 2.5, "muerta_viva_normal_sismo": 1.5}
GRADO_FIN_PRIMARIA = 0.95                       # tp para el secundario: tiempo al 95 % de consolidación (supuesto)
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


def _validar_estratos(estratos: list[EstratoArcilla]) -> None:
    for e in estratos:
        if e.hdr_m > e.espesor_m:
            raise ValueError(f"Hdr ({e.hdr_m} m) no puede exceder el espesor del estrato ({e.espesor_m} m) (Terzaghi / NSR-10 Título H).")
        if e.z_medio_m < e.espesor_m / 2.0 - 1e-9:
            raise ValueError(f"z_medio ({e.z_medio_m} m) es menor que la mitad del espesor ({e.espesor_m / 2.0} m): el estrato quedaría por encima de la base de la zapata (NSR-10 Título H).")
    orden = sorted(estratos, key=lambda x: x.z_medio_m)
    for a, c in zip(orden, orden[1:]):
        if (a.z_medio_m + a.espesor_m / 2.0) > (c.z_medio_m - c.espesor_m / 2.0) + 1e-9:
            raise ValueError("Los estratos se solapan: revise z_medio y espesor de cada uno (NSR-10 Título H).")


def asentamiento_contrato(s: SolicitudAsentamiento) -> ResultadoMotor:
    if s.L_m is None and s.metodo == "boussinesq":
        raise ValueError("Zapata corrida: use el método 2a1; Boussinesq está implementado para áreas rectangulares (NSR-10 Título H, H.4.9).")
    _validar_estratos(s.estratos)
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
        supuestos=["La presión q es neta (sobrecarga ya descontada); si se ingresa la presión bruta el asentamiento se sobrestima.",
                   "Solo consolidación primaria unidimensional: no incluye asentamiento inmediato ni consolidación secundaria.",
                   "Δσ en el eje de la zapata, en el punto medio de cada estrato; los estratos se tratan como independientes.",
                   f"Límite total de {limite:.0f} mm para cimentación {s.tipo_cimentacion} (NSR-10 H.4.9.2); el asentamiento diferencial y el giro (H.4.9) NO se verifican.",
                   "H.4.9.2 aplica 'siempre y cuando no se afecte la funcionalidad de conducciones/accesos': esa condición NO se verifica. "
                   "El límite es sobre el asentamiento total a 20 años; el motor solo calcula la consolidación primaria última.",
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
    factor_seguridad: float = Field(..., ge=1.0, allow_inf_nan=False, description="NSR-10 Tabla H.4.7-1")
    q_aplicada_kpa: float = Field(..., gt=0)
    condicion_carga: Optional[Literal["muerta_viva_normal", "muerta_viva_maxima", "muerta_viva_normal_sismo"]] = Field(
        default=None, description="Si se da, FS debe ser ≥ el mínimo de la Tabla H.4.7-1 para esa condición")


def _verificar_fs(fs: float, condicion: Optional[str]) -> tuple[list[str], list[str]]:
    """(supuestos, advertencias) del factor de seguridad frente a la Tabla H.4.7-1; FS bajo el mínimo es error."""
    if condicion is None:
        adv = [] if fs >= 3.0 else [f"Factor de seguridad {fs:g} < 3,0: verifique el mínimo de la Tabla H.4.7-1 de la NSR-10 para su caso de carga."]
        return ["Sin condición de carga declarada: el FS no se contrasta con la Tabla H.4.7-1."], adv
    minimo = FS_MINIMO[condicion]
    if fs < minimo:
        raise ValueError(f"FS = {fs:g} es menor que el mínimo de {minimo:g} de la Tabla H.4.7-1 de la NSR-10 para la condición {condicion}.")
    return [f"FS = {fs:g} ≥ {minimo:g}, mínimo de la Tabla H.4.7-1 para {condicion}."], []


def portante_contrato(s: SolicitudPortante) -> ResultadoMotor:
    r = capacidad_portante_general(c_kpa=s.c_kpa, phi_deg=s.phi_deg, gamma_kn_m3=s.gamma_kn_m3, B_m=s.B_m, L_m=s.L_m,
                                   Df_m=s.Df_m, nivel_freatico_m=s.nivel_freatico_m, gamma_sat_kn_m3=s.gamma_sat_kn_m3)
    q_adm = r["q_ult_kpa"] / s.factor_seguridad
    if not (r["q_ult_kpa"] > 0 and q_adm > 0):
        raise ValueError("La capacidad portante admisible es nula: no hay capacidad que verificar (Vesić / NSR-10 Título H).")
    utilizacion = s.q_aplicada_kpa / q_adm
    sup_fs, advertencias = _verificar_fs(s.factor_seguridad, s.condicion_carga)
    supuestos = ["Carga vertical y centrada: sin factores de inclinación ni de excentricidad (para eso, /geotecnia/portante-excentrica).",
                 "El Título H de la NSR-10 no da una fórmula de capacidad portante; este resultado NO sustituye el estudio geotécnico (H.4.2.3).",
                 "La presión última puede disminuir al ensanchar la zapata a igual Df porque el factor de profundidad depende de Df/B "
                 "(comportamiento de las formulaciones de Hansen/Vesić); la carga última total sí crece con B.",
                 f"Factor de seguridad {s.factor_seguridad:g} suministrado por el usuario (NSR-10 Tabla H.4.7-1)."] + sup_fs
    supuestos += ["q_aplicada es la presión de contacto bruta; la verificación de la tabla H.2.4-1 (F_SB) no se realiza aquí.",
                  "Los factores de profundidad de Hansen/Vesić cambian de forma en Df = B (k=Df/B → atan(Df/B)): q_ult puede caer al cruzar Df = B."]
    if s.nivel_freatico_m is None:
        supuestos.append("Sin nivel freático: no se reduce el peso unitario ni la sobrecarga.")
    return ResultadoMotor(
        valor={**r, "q_adm_kpa": q_adm, "q_aplicada_kpa": s.q_aplicada_kpa, "utilizacion": utilizacion, "cumple": s.q_aplicada_kpa <= q_adm},
        unidad_si="Presiones en kPa",
        ecuacion="q_ult = c·Nc·sc·dc + q·Nq·sq·dq + ½·γ'·B·Nγ·sγ; Nq = e^(π tanφ)·tan²(45°+φ/2), Nc = (Nq−1)cotφ, Nγ = 2(Nq+1)tanφ; q_adm = q_ult/FS",
        referencia_normativa="Vesić (1973) · NSR-10 Título H (H.4, Tabla H.4.7-1)",
        supuestos=supuestos,
        advertencias=advertencias,
        en_borde_dominio=bool(utilizacion >= _UTILIZACION_BORDE or s.phi_deg >= _PHI_BORDE_DEG),
    )


# ── Asentamiento total a 20 años (H.4.8.4, H.4.9.2) ─────────────────────────────────────────────────────────────────
class EstratoTotal(EstratoArcilla):
    c_alfa: Optional[float] = Field(..., ge=0, description="Cα; null = sin compresión secundaria (queda declarado)")


class SolicitudAsentamientoTotal(BaseModel):
    q_kpa: float = Field(..., gt=0, description="Presión neta aplicada por la zapata")
    B_m: float = Field(..., gt=0)
    L_m: float = Field(..., gt=0, description="L ≥ B (rectangular; el inmediato elástico no admite zapata corrida)")
    es_kpa: float = Field(..., gt=0, description="Módulo elástico del suelo bajo la zapata (inmediato, H.4.8.1)")
    nu: float = Field(..., ge=0, lt=0.5)
    estratos: list[EstratoTotal] = Field(..., min_length=1, max_length=20)
    metodo: Literal["boussinesq", "2a1"]
    tipo_cimentacion: Literal["aislada", "medianera"]


def asentamiento_total_contrato(s: SolicitudAsentamientoTotal) -> ResultadoMotor:
    """S(20 años) = Si + Σ U(20 años)·Sc,i + Σ Ss,i, contra el límite de H.4.9.2."""
    if s.L_m < s.B_m:
        raise ValueError("Se requiere L ≥ B (B es la dimensión menor) (NSR-10 Título H, H.4.8.1).")
    _validar_estratos(s.estratos)
    si_m = asentamiento_inmediato_flexible(q_kpa=s.q_kpa, B_m=s.B_m, L_m=s.L_m, es_kpa=s.es_kpa, nu=s.nu,
                                           ubicacion="centro")
    capas, prim_ult, prim_20, sec_20 = [], 0.0, 0.0, 0.0
    sin_secundario = []
    for i, e in enumerate(s.estratos):
        delta = (esfuerzo_boussinesq_centro_rect(s.q_kpa, s.B_m, s.L_m, e.z_medio_m) if s.metodo == "boussinesq"
                 else esfuerzo_2a1(s.q_kpa, s.B_m, s.L_m, e.z_medio_m))
        ult = asentamiento_primario(cc=e.cc, cr=e.cr, e0=e.e0, espesor_m=e.espesor_m, sigma0_kpa=e.sigma0_kpa,
                                    delta_kpa=delta, sigma_p_kpa=e.sigma_p_kpa)
        u20 = grado_consolidacion(factor_tiempo(e.cv_m2_dia, HORIZONTE_DIAS, e.hdr_m))
        tp = tiempo_para_grado(GRADO_FIN_PRIMARIA, cv_m2_dia=e.cv_m2_dia, hdr_m=e.hdr_m)
        if e.c_alfa is None:
            sec = 0.0
            sin_secundario.append(i)
        elif tp >= HORIZONTE_DIAS:
            sec = 0.0
        else:
            sec = asentamiento_secundario(c_alfa=e.c_alfa, e0=e.e0, espesor_m=e.espesor_m,
                                          t_fin_dias=HORIZONTE_DIAS, t_primaria_dias=tp)
        prim_ult += ult
        prim_20 += u20 * ult
        sec_20 += sec
        capas.append({"delta_sigma_kpa": delta, "primario_ultimo_mm": ult * 1e3, "grado_20_anios": u20,
                      "primario_20_anios_mm": u20 * ult * 1e3, "tp95_dias": tp, "secundario_20_anios_mm": sec * 1e3})
    total_20_mm = (si_m + prim_20 + sec_20) * 1e3
    total_ult_mm = (si_m + prim_ult + sec_20) * 1e3
    limite = LIMITES_ASENT_TOTAL_MM[s.tipo_cimentacion]
    utilizacion = total_20_mm / limite
    advertencias = []
    if total_ult_mm > limite >= total_20_mm:
        advertencias.append(f"Cumple a 20 años ({total_20_mm:.1f} mm), pero el asentamiento último ({total_ult_mm:.1f} mm) "
                            f"supera el límite de {limite:.0f} mm: la consolidación sigue después del horizonte de H.4.9.2.")
    supuestos = [
        "Total = inmediato + consolidación primaria + secundaria (H.4.8.4); el asentamiento por sismo (H.4.8) no se calcula.",
        "Inmediato: semiespacio elástico, zapata flexible, en el centro (H.4.8.1). Una zapata rígida asienta algo menos.",
        "La consolidación a 20 años es U(20 años)·Sc última, con carga instantánea y estratos independientes (Terzaghi).",
        f"El secundario empieza en tp = t(U = {GRADO_FIN_PRIMARIA:.0%}) y llega hasta los 20 años; si tp ≥ 20 años, es cero.",
        "La presión q es neta; Δσ en el eje de la zapata y en el punto medio de cada estrato.",
        f"Límite de {limite:.0f} mm para cimentación {s.tipo_cimentacion} (H.4.9.2), 'siempre y cuando no se afecte' la "
        "funcionalidad de servicios y vecinos: esa condición NO se verifica.",
    ]
    if sin_secundario:
        supuestos.append(f"Sin Cα en los estratos {sin_secundario}: su compresión secundaria se toma como nula; H.4.8.3 pide "
                         "comprobarla en laboratorio si hay contenido orgánico.")
    return ResultadoMotor(
        valor={"asentamiento_total_20_anios_mm": total_20_mm, "asentamiento_total_ultimo_mm": total_ult_mm,
               "inmediato_mm": si_m * 1e3, "primario_20_anios_mm": prim_20 * 1e3, "primario_ultimo_mm": prim_ult * 1e3,
               "secundario_20_anios_mm": sec_20 * 1e3, "limite_total_mm": limite, "utilizacion": utilizacion,
               "cumple_asentamiento_total": total_20_mm <= limite, "estratos": capas},
        unidad_si="Asentamientos en mm; esfuerzos en kPa; tiempos en días",
        ecuacion="S20 = q·B·(1−ν²)/Es·Iw + Σ U(Tv20)·Sc + Σ Cα·H/(1+e0)·log10(t20/tp); "
                 "Sc = H/(1+e0)·[Cr·log10(σ'p/σ'0) + Cc·log10(σ'f/σ'p)]",
        referencia_normativa="NSR-10 H.4.8.1–H.4.8.4 y H.4.9.2 · Terzaghi (1943) · Harr / Timoshenko & Goodier",
        supuestos=supuestos,
        advertencias=advertencias,
        en_borde_dominio=bool(utilizacion >= _UTILIZACION_BORDE),
    )


# ── Asentamiento diferencial y giro (Tabla H.4.9-1, H.4.9.4) ────────────────────────────────────────────────────────
class Apoyo(BaseModel):
    x_m: float = Field(..., allow_inf_nan=False, description="Posición del apoyo o columna a lo largo del eje")
    asentamiento_mm: float = Field(..., ge=0, allow_inf_nan=False)


class SolicitudDiferencial(BaseModel):
    apoyos: list[Apoyo] = Field(..., min_length=2, max_length=200)
    tipo_construccion: Literal["muros_acabados_susceptibles", "muros_de_carga", "porticos_concreto", "estructura_metalica"]


def diferencial_contrato(s: SolicitudDiferencial) -> ResultadoMotor:
    """Δ entre apoyos contiguos contra ℓ/divisor (Tabla H.4.9-1) y giro de cuerpo rígido contra 1/250 (H.4.9.4)."""
    ap = sorted(s.apoyos, key=lambda a: a.x_m)
    for a, b in zip(ap, ap[1:]):
        if b.x_m - a.x_m <= 0:
            raise ValueError("Dos apoyos comparten la misma posición x: la distancia ℓ entre apoyos debe ser positiva (NSR-10 Tabla H.4.9-1).")
    divisor = DIVISOR_DIFERENCIAL[s.tipo_construccion]
    tramos, peor = [], 0.0
    for a, b in zip(ap, ap[1:]):
        luz_mm = (b.x_m - a.x_m) * 1e3
        delta = abs(b.asentamiento_mm - a.asentamiento_mm)
        limite = luz_mm / divisor
        util = delta / limite
        peor = max(peor, util)
        tramos.append({"x_inicio_m": a.x_m, "x_fin_m": b.x_m, "luz_m": luz_mm / 1e3, "diferencial_mm": delta,
                       "limite_mm": limite, "distorsion": delta / luz_mm, "utilizacion": util, "cumple": delta <= limite})
    x = np.array([a.x_m for a in ap]) * 1e3
    y = np.array([a.asentamiento_mm for a in ap])
    giro = float(abs(np.polyfit(x, y, 1)[0])) if len(ap) >= 2 else 0.0      # pendiente del ajuste lineal (mm/mm)
    util_giro = giro * DIVISOR_GIRO
    return ResultadoMotor(
        valor={"tramos": tramos, "utilizacion_diferencial_max": peor, "cumple_diferencial": peor <= 1.0,
               "giro": giro, "limite_giro": 1.0 / DIVISOR_GIRO, "utilizacion_giro": util_giro,
               "cumple_giro": util_giro <= 1.0, "cumple": peor <= 1.0 and util_giro <= 1.0,
               "asentamiento_maximo_mm": float(y.max())},
        unidad_si="Asentamientos en mm; distancias en m; distorsión y giro adimensionales",
        ecuacion=f"Δmax = ℓ/{divisor:g} entre apoyos contiguos (Tabla H.4.9-1); giro = |pendiente del ajuste lineal "
                 f"S(x)| ≤ 1/{DIVISOR_GIRO:g} (H.4.9.4)",
        referencia_normativa="NSR-10 H.4.9.1, H.4.9.3 (Tabla H.4.9-1) y H.4.9.4",
        supuestos=[
            "Apoyos sobre un mismo eje (análisis en una dirección); un edificio se revisa eje por eje.",
            "ℓ es la distancia entre apoyos contiguos del eje; los asentamientos vienen de un cálculo previo.",
            "El giro se estima como la rotación de cuerpo rígido: pendiente de la recta de mínimos cuadrados de S(x).",
            "H.4.9.4 pide además que el giro no produzca efectos estéticos o funcionales: eso no se verifica.",
        ],
        en_borde_dominio=bool(peor >= _UTILIZACION_BORDE or util_giro >= _UTILIZACION_BORDE),
    )


# ── Consolidación multicapa ─────────────────────────────────────────────────────────────────────────────────────────
class CapaMulticapa(BaseModel):
    espesor_m: float = Field(..., gt=0, allow_inf_nan=False)
    cv_m2_dia: float = Field(..., gt=0, allow_inf_nan=False)
    mv_kpa_inv: float = Field(..., gt=0, allow_inf_nan=False, description="Coeficiente de compresibilidad volumétrica")
    delta_sigma_kpa: float = Field(..., ge=0, allow_inf_nan=False)


class SolicitudMulticapa(BaseModel):
    capas: list[CapaMulticapa] = Field(..., min_length=1, max_length=20)
    tiempos_dias: list[float] = Field(..., min_length=1, max_length=200)
    drenaje_superior: bool
    drenaje_inferior: bool
    nodos_por_capa: int = Field(40, ge=4, le=400)


def multicapa_contrato(s: SolicitudMulticapa) -> ResultadoMotor:
    r = consolidacion_multicapa([c.model_dump() for c in s.capas], tiempos_dias=s.tiempos_dias,
                                drenaje_superior=s.drenaje_superior, drenaje_inferior=s.drenaje_inferior,
                                nodos_por_capa=s.nodos_por_capa)
    return ResultadoMotor(
        valor={**r, "asentamiento_mm": [v * 1e3 for v in r["asentamiento_m"]],
               "asentamiento_final_mm": r["asentamiento_final_m"] * 1e3},
        unidad_si="Asentamientos en m y mm; tiempos en días",
        ecuacion="mv·∂u/∂t = ∂/∂z(cv·mv·∂u/∂z); volúmenes finitos con solución espectral exacta en el tiempo",
        referencia_normativa="NSR-10 H.4.8.2 · Terzaghi (1943)",
        supuestos=["Carga instantánea; u(0) = Δσ de cada capa; mv y cv constantes por capa (consolidación lineal).",
                   "El asentamiento final es Σ mv·Δσ·H: para arcillas con Cc use /geotecnia/asentamiento.",
                   f"Bordes: superior {'drenado' if s.drenaje_superior else 'impermeable'}, "
                   f"inferior {'drenado' if s.drenaje_inferior else 'impermeable'}.",
                   f"Error solo espacial: {s.nodos_por_capa} celdas por capa."],
        en_borde_dominio=False,
    )


# ── Monte Carlo del asentamiento primario ───────────────────────────────────────────────────────────────────────────
class SolicitudMonteCarlo(BaseModel):
    espesor_m: float = Field(..., gt=0, allow_inf_nan=False)
    sigma0_kpa: float = Field(..., gt=0, allow_inf_nan=False)
    delta_kpa: float = Field(..., ge=0, allow_inf_nan=False)
    sigma_p_kpa: float = Field(..., gt=0, allow_inf_nan=False)
    cr: float = Field(..., ge=0, allow_inf_nan=False)
    cc_mediana: float = Field(..., gt=0, allow_inf_nan=False)
    cc_cv: float = Field(..., ge=0, le=2.0)
    e0_mediana: float = Field(..., gt=0, allow_inf_nan=False)
    e0_cv: float = Field(..., ge=0, le=2.0)
    rho_cc_e0: float = Field(..., ge=-1.0, le=1.0)
    n: int = Field(10_000, ge=100, le=200_000)
    semilla: int = Field(..., ge=0)
    tipo_cimentacion: Literal["aislada", "medianera"]


def montecarlo_contrato(s: SolicitudMonteCarlo) -> ResultadoMotor:
    limite_mm = LIMITES_ASENT_TOTAL_MM[s.tipo_cimentacion]
    r = simular_asentamiento_primario(
        estrato=dict(espesor_m=s.espesor_m, sigma0_kpa=s.sigma0_kpa, delta_kpa=s.delta_kpa,
                     sigma_p_kpa=s.sigma_p_kpa, cr=s.cr),
        cc_mediana=s.cc_mediana, cc_cv=s.cc_cv, e0_mediana=s.e0_mediana, e0_cv=s.e0_cv, rho_cc_e0=s.rho_cc_e0,
        n=s.n, semilla=s.semilla, limite_m=limite_mm / 1e3)
    mm = {k.replace("_m", "_mm"): v * 1e3 for k, v in r.items() if k.endswith("_m")}
    p95 = mm["p95_mm"]
    return ResultadoMotor(
        valor={**mm, "n": r["n"], "semilla": r["semilla"], "prob_exceder_limite": r["prob_exceder_limite"],
               "limite_total_mm": limite_mm, "cumple_p95": p95 <= limite_mm},
        unidad_si="Asentamientos en mm; probabilidad adimensional",
        ecuacion="Cc, e0 ~ lognormal(mediana, CV) con cópula gaussiana ρ; S = H/(1+e0)·[Cr·log10(σ'p/σ'0) + Cc·log10(σ'f/σ'p)]",
        referencia_normativa="NSR-10 H.4.8.2 y H.4.9.2 · Terzaghi (1943)",
        supuestos=["Solo el primario último de un estrato; Cr, σ'0, σ'p y Δσ son fijos.",
                   "La incertidumbre viene de Cc y e0; Cr se acota a Cr ≤ Cc en cada muestra.",
                   f"Semilla {s.semilla}: el resultado es reproducible.",
                   "cumple_p95 es un criterio informativo: la NSR-10 no fija un percentil."],
        en_borde_dominio=bool(p95 >= _UTILIZACION_BORDE * limite_mm),
    )


# ── Capacidad portante con excentricidad e inclinación (H.4.10) ─────────────────────────────────────────────────────
class SolicitudPortanteExcentrica(BaseModel):
    c_kpa: float = Field(..., ge=0, allow_inf_nan=False)
    phi_deg: float = Field(..., ge=0, le=45)
    gamma_kn_m3: float = Field(..., gt=0, allow_inf_nan=False)
    B_m: float = Field(..., gt=0, allow_inf_nan=False)
    L_m: Optional[float] = Field(..., description="null = corrida (cargas por metro)")
    Df_m: float = Field(..., ge=0, allow_inf_nan=False)
    nivel_freatico_m: Optional[float] = Field(..., ge=0)
    gamma_sat_kn_m3: Optional[float] = Field(default=None, gt=0)
    V_kn: float = Field(..., gt=0, allow_inf_nan=False, description="Carga vertical (kN; kN/m en corrida)")
    H_kn: float = Field(..., ge=0, allow_inf_nan=False, description="Carga horizontal en la dirección de B")
    eB_m: float = Field(..., ge=0, allow_inf_nan=False)
    eL_m: float = Field(..., ge=0, allow_inf_nan=False)
    factor_seguridad: float = Field(..., ge=1.0, allow_inf_nan=False)
    condicion_carga: Literal["muerta_viva_normal", "muerta_viva_maxima", "muerta_viva_normal_sismo"]


def portante_excentrica_contrato(s: SolicitudPortanteExcentrica) -> ResultadoMotor:
    sup_fs, advertencias = _verificar_fs(s.factor_seguridad, s.condicion_carga)
    r = capacidad_portante_excentrica_inclinada(
        c_kpa=s.c_kpa, phi_deg=s.phi_deg, gamma_kn_m3=s.gamma_kn_m3, B_m=s.B_m, L_m=s.L_m, Df_m=s.Df_m,
        nivel_freatico_m=s.nivel_freatico_m, V_kn=s.V_kn, H_kn=s.H_kn, eB_m=s.eB_m, eL_m=s.eL_m,
        gamma_sat_kn_m3=s.gamma_sat_kn_m3)
    Q_adm = r["Q_ult_kn"] / s.factor_seguridad
    utilizacion = s.V_kn / Q_adm
    if not r["sin_traccion"]:
        advertencias.append("La resultante cae fuera del núcleo central (e > B/6 o e > L/6): parte de la base se levanta; "
                            "revise la estabilidad al volcamiento y el diseño estructural (H.4.10).")
    supuestos = [
        "Área efectiva de Meyerhof: B' = B − 2eB, L' = L − 2eL; la presión se supone uniforme sobre A'.",
        "Factores de inclinación de Vesić (1975) con H paralela a B; los de profundidad usan B real (Df/B).",
        "No se verifica el deslizamiento ni el volcamiento de la zapata; solo la capacidad portante.",
        "El Título H no da fórmula de capacidad portante; el resultado NO sustituye el estudio geotécnico (H.4.2.3).",
    ] + sup_fs
    if s.nivel_freatico_m is None:
        supuestos.append("Sin nivel freático: no se reduce el peso unitario ni la sobrecarga.")
    return ResultadoMotor(
        valor={**r, "Q_adm_kn": Q_adm, "V_kn": s.V_kn, "utilizacion": utilizacion, "cumple": s.V_kn <= Q_adm,
               "fs_minimo_tabla": FS_MINIMO[s.condicion_carga]},
        unidad_si="Presiones en kPa; cargas en kN (kN/m en corrida); dimensiones en m",
        ecuacion="q_ult = c·Nc·sc·dc·ic + q·Nq·sq·dq·iq + ½·γ'·B'·Nγ·sγ·iγ; Q_ult = q_ult·B'·L'; Q_adm = Q_ult/FS",
        referencia_normativa="Vesić (1973, 1975) · Meyerhof (1953) · NSR-10 H.4.7 (Tabla H.4.7-1) y H.4.10",
        supuestos=supuestos,
        advertencias=advertencias,
        en_borde_dominio=bool(utilizacion >= _UTILIZACION_BORDE or s.phi_deg >= _PHI_BORDE_DEG or not r["sin_traccion"]),
    )
