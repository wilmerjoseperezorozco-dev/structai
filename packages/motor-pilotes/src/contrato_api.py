"""Salida con contrato uniforme de motor-pilotes (#118): capacidad axial a compresión de un grupo de pilotes contra la
reacción vertical de una columna (eslabón motor-analisis → pilotes → optimizador-portico)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .axial import Estrato, Pilote  # noqa: E402
from .grupo import SEPARACION_MIN_REL, capacidad_grupo  # noqa: E402

_UTILIZACION_BORDE = 0.95
_PHI_BORDE_DEG = 40.0
_L_SOBRE_D_MIN = 10.0
_ZONA_PUNTA_DIAMETROS = 3.0


class EstratoEntrada(BaseModel):
    espesor_m: float = Field(..., gt=0)
    gamma_kn_m3: float = Field(..., gt=0, le=30)
    gamma_sat_kn_m3: Optional[float] = Field(default=None, gt=0, le=30)
    comportamiento: Literal["drenado", "no_drenado"]
    su_kpa: Optional[float] = Field(default=None, gt=0, le=1000)
    c_kpa: Optional[float] = Field(default=None, ge=0, le=500)
    phi_deg: Optional[float] = Field(default=None, gt=0, lt=50)
    k_lateral: Optional[float] = Field(default=None, gt=0, le=5)
    qp_ult_kpa: Optional[float] = Field(default=None, gt=0, le=50000)


class SolicitudPilotes(BaseModel):
    estratos: list[EstratoEntrada] = Field(..., min_length=1, max_length=30)
    nivel_freatico_m: Optional[float] = Field(..., ge=0, description="null = sin nivel freático (queda declarado)")
    seccion: Literal["circular", "cuadrada"]
    ancho_m: float = Field(..., gt=0, le=3.0)
    longitud_m: float = Field(..., gt=0, le=80.0)
    tipo: Literal["hincado", "excavado"]
    filas: int = Field(..., ge=1, le=10)
    columnas: int = Field(..., ge=1, le=10)
    separacion_m: Optional[float] = Field(..., gt=0, description="Entre ejes; null solo para un pilote")
    combinacion: Literal["cm_cv_normal", "cm_cv_maxima", "cm_cv_sismo"]
    eficiencia_grupo: Literal["converse_labarre", "ninguna"] = Field(
        ..., description="Reducción por eficiencia (H.4.4.1 b-3, «posible»): la decide el ingeniero")
    reaccion_vertical_kn: float = Field(..., gt=0, description="Compresión de servicio (sin mayorar) que baja de la columna")

    @model_validator(mode="after")
    def _separacion(self):
        if self.filas * self.columnas > 1 and self.separacion_m is None:
            raise ValueError("Grupo de más de un pilote: falta separacion_m (NSR-10 H.4.4.1).")
        return self


def pilotes_contrato(s: SolicitudPilotes) -> ResultadoMotor:
    estratos = [Estrato(**e.model_dump()) for e in s.estratos]
    pilote = Pilote(seccion=s.seccion, ancho_m=s.ancho_m, longitud_m=s.longitud_m, tipo=s.tipo)
    g = capacidad_grupo(estratos, pilote, filas=s.filas, columnas=s.columnas, separacion_m=s.separacion_m or 0.0,
                        nivel_freatico_m=s.nivel_freatico_m, combinacion=s.combinacion,
                        eficiencia=s.eficiencia_grupo)
    ind = g["individual"]
    razon = s.reaccion_vertical_kn / g["q_adm_grupo_kn"]

    advertencias, borde = [], razon >= _UTILIZACION_BORDE
    if ind["distancia_punta_a_base_estrato_m"] < _ZONA_PUNTA_DIAMETROS * s.ancho_m:
        borde = True
        advertencias.append(f"La punta queda a menos de {_ZONA_PUNTA_DIAMETROS:g}·D de la base de su estrato: un estrato "
                            "más blando debajo reduce la resistencia por punta y el motor no lo considera.")
    if any(e.comportamiento == "drenado" and e.phi_deg >= _PHI_BORDE_DEG for e in s.estratos):
        borde = True
        advertencias.append(f"φ' ≥ {_PHI_BORDE_DEG:g}° en algún estrato: fuera del rango usual de los métodos.")
    if s.longitud_m / s.ancho_m < _L_SOBRE_D_MIN:
        borde = True
        advertencias.append(f"L/D < {_L_SOBRE_D_MIN:g}: el elemento se acerca a una cimentación superficial y Nc = 9 deja de aplicar.")
    if g["separacion_relativa"] is not None and g["separacion_relativa"] < SEPARACION_MIN_REL:
        borde = True
        advertencias.append(f"Separación s/D = {g['separacion_relativa']:.2f} < {SEPARACION_MIN_REL:g} (práctica usual).")
    if g["bloque"] is not None and "no_evaluado" in g["bloque"]:
        advertencias.append("La falla en bloque (H.4.4.1 b-2) no se evaluó porque hay estratos drenados: próximamente.")

    supuestos = [
        "Solo compresión axial: no se considera la tracción (H.4.4.1), la carga lateral, la excentricidad ni la fricción negativa.",
        "Fricción y punta con factores de seguridad separados (H.4.4.1): F_SL = F_SB de la Tabla H.2.4-1 y F_SICP de la Tabla H.4.7-1, valores mínimos de diseño.",
        "En arcilla con Su se usa FSBUM (H.2.4.2), que no se permite en análisis seudo-estático: con sismo hay que analizar en esfuerzos efectivos.",
        "τL = 2/3·τF en suelo drenado (H.4.7-2) y τL = α·Su en arcilla (H.4.7-3); K del fuste lo da el estudio geotécnico.",
        "Punta en arcilla qp = 9·Su (Skempton, 1951); en suelo drenado qp viene del estudio geotécnico (CCP-14 §10.7/10.8 próximamente).",
        "La cabeza del pilote está en la superficie del perfil (z = 0); no se descuenta el peso propio del pilote ni del encepado.",
        "No se demuestra que los F_SB directos equivalentes cumplan la Tabla H.2.4-1 (H.4.7.1); eso queda al ingeniero.",
        f"Eficiencia de grupo: {s.eficiencia_grupo} (Converse-Labarre si se pide). El bloque en arcilla es el de Terzaghi y Peck con Nc de Skempton; la NSR-10 no fija fórmulas.",
        "No se verifican asentamientos (H.4.4.2) ni la resistencia estructural del pilote.",
        f"Tipo '{s.tipo}': hoy solo informa; la diferencia entre hincado y excavado entra a través de K y qp del estudio.",
        "Se reporta el perfil de entrada tal como se recibe; las correlaciones SPT → Su/φ' están próximamente.",
    ]
    if s.nivel_freatico_m is None:
        supuestos.append("Sin nivel freático: σ'v = σv en todo el perfil.")
    return ResultadoMotor(
        valor={"capacidad_pilote_kn": ind["q_adm_kn"], "capacidad_grupo_kn": g["q_adm_grupo_kn"],
               "razon_demanda_capacidad": razon, "cumple": razon <= 1.0, "gobierna": g["gobierna"],
               "eficiencia_grupo": g["eficiencia"], "individual": ind, "modos_adm_kn": g["modos_adm_kn"],
               "modos_ult_kn": g["modos_ult_kn"], "bloque": g["bloque"]},
        unidad_si="Fuerzas en kN; esfuerzos en kPa; longitudes en m",
        ecuacion="Qadm = Σ τL·p·Δz / F_SL + qp·Ap / F_SICP; τL = 2/3(c' + K·σ'v·tanφ') o α·Su, "
                 "α = 0.2 + 0.8·exp[0.35 − 2Su/PA] ≤ 1; grupo = mín(Σ individuales, bloque, E·Σ individuales)",
        referencia_normativa="NSR-10 Título H (H.4.4.1, H.4.7.1, H.4.7.2, Tablas H.4.7-1 y H.2.4-1) · Skempton (1951) · "
                             "Terzaghi y Peck · Converse-Labarre",
        supuestos=supuestos,
        advertencias=advertencias,
        en_borde_dominio=bool(borde),
    )
