"""
GeoPot — Schemas Pydantic de entrada.
Las salidas se dejan como dict (los métodos .resumen()/.informe_completo()
de las dataclasses portadas ya devuelven estructuras JSON-serializables
con forma variable según el caso — no vale la pena forzar un Response
model rígido sobre ellas).
"""
from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ZonaSismicaRequest(BaseModel):
    departamento: str = Field(..., description="Nombre del departamento o su capital, ej. 'Atlántico' o 'Barranquilla'")


class CilindroInput(BaseModel):
    id_cilindro: str
    edad_dias: int = Field(..., description="3, 7, 14 o 28 días")
    diametro_mm: float
    carga_kN: float
    fecha_colada: date
    fecha_ensayo: date
    observaciones: str = ""


class SlumpInput(BaseModel):
    id_muestra: str
    slump_mm: float
    temperatura_C: float
    hora_toma: str
    observaciones: str = ""


class ConcretoRequest(BaseModel):
    fc_diseno_MPa: float
    zona_sismica: str = Field(default="ALTA", description="BAJA | INTERMEDIA | ALTA")
    proyecto: str = ""
    elemento: str = ""
    cilindros: list[CilindroInput] = Field(default_factory=list)
    slumps: list[SlumpInput] = Field(default_factory=list)


class USCSRequest(BaseModel):
    pasa_200_pct: float
    pasa_4_pct: float
    d10: Optional[float] = None
    d30: Optional[float] = None
    d60: Optional[float] = None
    ll: Optional[float] = None
    ip: Optional[float] = None


class AASHTORequest(BaseModel):
    ll: float
    ip: float
    pasa_200_pct: float


class ProctorRequest(BaseModel):
    id_muestra: str
    tipo: str = Field(default="MODIFICADO", description="ESTANDAR | MODIFICADO")
    puntos: list[tuple[float, float]] = Field(..., description="[(humedad_%, densidad_seca_g_cm3), ...], mínimo 3 puntos")
    densidad_campo_gcm3: Optional[float] = Field(None, description="Si se provee, verifica compactación de campo")
    porcentaje_minimo: float = 95.0


class CBRRequest(BaseModel):
    id_muestra: str
    carga_254_kN: float
    carga_508_kN: float
    densidad_seca: float
    humedad_pct: float
    condicion: str = "SATURADO"
    esal_millones: Optional[float] = Field(None, description="Si se provee, estima espesor de pavimento AASHTO 93")


class GranulometriaRequest(BaseModel):
    id_muestra: str
    tamices: list[tuple[float, float]] = Field(..., description="[(abertura_mm, %_que_pasa), ...]")


class AgregadoGruesoRequest(BaseModel):
    id_muestra: str
    origen: str = Field(default="Triturado", description="Triturado | Rodado | Mixto")
    masa_sss_g: float
    masa_seca_g: float
    masa_sumergida_g: float
    perdida_LA_pct: Optional[float] = None
    particulas_planas_pct: Optional[float] = None
    particulas_alargadas_pct: Optional[float] = None
    uso: str = Field(default="CONCRETO", description="CONCRETO | ASFALTO | BASE_GRANULAR")


class AgregadoFinoRequest(BaseModel):
    id_muestra: str
    masa_sss_g: float
    masa_seca_g: float
    masa_frasco_agua: float
    masa_frasco_agua_muestra: float
    modulo_finura: float
    impurezas_organicas: str = Field(default="CLARO", description="CLARO | MÁS CLARO | OSCURO")


class MezclaACIRequest(BaseModel):
    fc_MPa: float
    tamaño_max_agregado_mm: float = 19.0
    asentamiento_mm: float = 75.0
    zona_sismica: str = "ALTA"
    densidad_fino: float = 2.65
    densidad_grueso: float = 2.70
