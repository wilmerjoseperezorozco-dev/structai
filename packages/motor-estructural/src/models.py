"""
Modelos Pydantic — motor-estructural
Esquemas de request/response para el router FastAPI de StructAI.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class PropiedadesConcreto(BaseModel):
    fc:  float = Field(28.0,  description="Resistencia cilíndrica f'c [MPa]")
    fy:  float = Field(420.0, description="Fluencia del acero longitudinal [MPa]")
    b:   float = Field(300.0, description="Ancho de sección en el nudo [mm]")
    h:   float = Field(300.0, description="Altura de sección en el nudo [mm]")
    d:   float = Field(265.0, description="Peralte efectivo [mm]")
    Av:  float = Field(56.5,  description="Área de estribos (2 ramas Ø6) [mm²]")
    s:   float = Field(75.0,  description="Separación de estribos en zona confinada [mm]")


class CargasGravedad(BaseModel):
    peso_propio_losa:       float = Field(4.80, description="kN/m²")
    carga_muerta_adicional: float = Field(1.50, description="kN/m²")
    carga_viva_piso:        float = Field(2.00, description="kN/m²")
    tributaria_viga:        float = Field(4.00, description="m²")
    numero_pisos:           int   = Field(3,    description="Pisos que convergen al nudo")


class AnalisisNudoRequest(BaseModel):
    guid_viga:    str = Field(..., description="GlobalId IFC de la viga en el nudo")
    guid_columna: str = Field(..., description="GlobalId IFC de la columna en el nudo")
    concreto:     PropiedadesConcreto = Field(default_factory=PropiedadesConcreto)
    cargas:       CargasGravedad      = Field(default_factory=CargasGravedad)


class ChequeoNSR10(BaseModel):
    Vc_kN:             float
    Vs_kN:             float
    Vn_max_kN:         float
    phi_Vn_kN:         float
    Vu_diseno_kN:      float
    margen_pct:        float
    cumple:            bool
    combinacion_governa: str


class EspectroDiseno(BaseModel):
    SDS: float
    SD1: float
    T0:  float
    Ts:  float


class AnalisisNudoResponse(BaseModel):
    posicion_nudo_mm:    list[float]
    matriz_T12_shape:    list[int]
    matriz_T12_columna_shape: list[int]
    periodo_T_seg:       float
    Sa_g:                float
    espectro:            EspectroDiseno
    Vs_basal_kN:         float
    Vu_sismo_kN:         float
    Vu_gravedad_kN:      float
    chequeo_nsr10:       ChequeoNSR10
    veredicto:           str            # "PASA" | "FALLA"
    norma_referencia:    str


class ResultadoEstriboItem(BaseModel):
    par:            str    # "E0–E1"
    separacion_mm:  float
    cumple_nsr10:   bool
    s_max_mm:       float


class InspeccionEstribosResponse(BaseModel):
    estribos_detectados: int
    s_max_diseno_mm:     float
    resultados:          list[ResultadoEstriboItem]
    fallos:              int
    veredicto:           str   # "CUMPLE" | "INCUMPLE"
    accion_requerida:    Optional[str]
    norma_referencia:    str
