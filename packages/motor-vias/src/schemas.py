"""
Motor-Vías — Schemas Pydantic de entrada.
Las salidas se dejan como dict: los .validar()/.disenar()/.diagnosticar()/
.verificar_*() de las dataclasses portadas retornan dataclasses o dicts que
se serializan con dataclasses.asdict() en __init__.py — no vale la pena
forzar un Response model rígido sobre estructuras de forma variable.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

from .diseno_geometrico import TipoVia as TipoViaGeometrico, Topografia as TopografiaGeometrico, TipoSuperficie
from .pavimentos import TipoPavimento, TipoVia as TipoViaPavimento
from .mantenimiento import TipoVia as TipoViaMantenimiento, TipoMantenimiento, TipoDeterioro, GravedadDeterioro
from .topografia import EstandarNivelacion
from .ntc_materiales_1 import (
    AplicacionAdoquin, TipoAdoquin as TipoAdoquinNTC2017,
    TipoGeotextil,
    TipoCemento,
    TipoAditivo,
    TipoCementoBlanco,
    FuenteAgua,
    ClaseAditivoMineral,
)
from .ntc_materiales_2 import (
    TipoAditivoAire,
    PresentacionPigmento, TipoPigmento,
    GradoEscoria,
    TipoPrefabricado,
    TipoAgregadoLiviano, TipoUnidadMamposteria,
    TipoMaterial,
)


# ── Diseño geométrico ───────────────────────────────────────────────────────

class DisenoGeometricoRequest(BaseModel):
    tipo_via: TipoViaGeometrico
    velocidad_diseno: float = Field(..., description="km/h, múltiplo de 10 entre 30 y 120")
    topografia: TopografiaGeometrico
    volumen_transito: int = Field(..., description="TPD")
    radio_curva: Optional[float] = Field(None, description="metros")
    pendiente_longitudinal: Optional[float] = Field(None, description="%")
    peralte: Optional[float] = Field(None, description="%")
    ancho_carril: Optional[float] = Field(None, description="metros")
    bombeo: Optional[float] = Field(None, description="%")
    tipo_superficie: Optional[TipoSuperficie] = None


# ── Pavimentos ───────────────────────────────────────────────────────────────

class PavimentosRequest(BaseModel):
    tipo_pavimento: TipoPavimento
    tipo_via: TipoViaPavimento
    tpd: int = Field(..., description="Tránsito Promedio Diario")
    esals_millones: float = Field(..., description="Ejes equivalentes de 8.2 t (millones)")
    cbr_subrasante: float = Field(..., description="CBR de la subrasante (%)")
    modulo_subrasante: Optional[float] = Field(None, description="MPa")
    ip_subrasante: Optional[float] = None
    temperatura_media: Optional[float] = Field(None, description="°C")
    espesor_subbase: Optional[float] = Field(None, description="cm")
    espesor_base: Optional[float] = Field(None, description="cm")
    modulo_subbase: Optional[float] = Field(None, description="MPa")
    modulo_base: Optional[float] = Field(None, description="MPa")


# ── Mantenimiento ────────────────────────────────────────────────────────────

class MantenimientoRequest(BaseModel):
    tipo_via: TipoViaMantenimiento
    tipo_mantenimiento: TipoMantenimiento
    deterioro_tipo: TipoDeterioro
    deterioro_gravedad: GravedadDeterioro
    area_afectada: Optional[float] = Field(None, description="m²")
    profundidad: Optional[float] = Field(None, description="cm")
    longitud: Optional[float] = Field(None, description="m, para grietas")
    ancho: Optional[float] = Field(None, description="mm, para grietas")
    indice_condicion: Optional[float] = Field(None, description="PCI (%)")
    volumen_transito: Optional[int] = Field(None, description="TPD")


# ── Topografía ───────────────────────────────────────────────────────────────

class CierreNivelacionRequest(BaseModel):
    error_medido_mm: float
    distancia_km: float
    estandar: EstandarNivelacion = EstandarNivelacion.INVIAS


# ── NTC 2017 — Adoquines de concreto para pavimentos ─────────────────────────

class NTC2017Request(BaseModel):
    nombre: str
    aplicacion: AplicacionAdoquin
    tipo: TipoAdoquinNTC2017
    largo_mm: float
    ancho_mm: float
    espesor_mm: float
    resistencia_flexion_mpa: float
    absorcion_porcentaje: float
    fabricante: Optional[str] = None


# ── NTC 4342 — Geotextiles ────────────────────────────────────────────────────

class NTC4342Request(BaseModel):
    nombre: str
    tipo: TipoGeotextil
    retencion_asfaltica_l_m2: float
    composicion: str
    porcentaje_poliolefinas: float
    fabricante: Optional[str] = None


# ── NTC 121 — Cemento hidráulico ──────────────────────────────────────────────

class NTC121Request(BaseModel):
    nombre: str
    tipo: TipoCemento
    resistencia_compresion_mpa: dict[int, float] = Field(..., description="{edad_dias: resistencia_mpa}")
    tiempo_fraguado_inicial_min: float
    tiempo_fraguado_final_min: float
    expansion_autoclave_porcentaje: float
    finura_blaine_m2_kg: float
    densidad_g_cm3: float
    fabricante: Optional[str] = None


# ── NTC 1299 — Aditivos químicos para concreto ────────────────────────────────

class NTC1299Request(BaseModel):
    nombre: str
    tipo: TipoAditivo
    descripcion: str
    aplicaciones: list[str] = Field(default_factory=list)
    fabricante: Optional[str] = None
    dosificacion_recomendada: Optional[str] = None


# ── NTC 1362 — Cemento hidráulico blanco ──────────────────────────────────────

class NTC1362Request(BaseModel):
    nombre: str
    tipo: TipoCementoBlanco
    resistencia_mpa: dict[int, float] = Field(..., description="{edad_dias: resistencia_mpa}")
    tiempo_fraguado_inicial_min: float
    tiempo_fraguado_final_min: float
    expansion_autoclave_porcentaje: float
    finura_blaine_m2_kg: float
    blancura_porcentaje: float
    contenido_alcalis_porcentaje: Optional[float] = None
    fabricante: Optional[str] = None


# ── NTC 3459 — Agua para elaboración de concreto ──────────────────────────────

class AnalisisAguaInput(BaseModel):
    sulfatos_mg_l: float
    cloruros_mg_l: float
    solidos_totales_mg_l: float
    solidos_disueltos_mg_l: float
    ph: float
    turbiedad: Optional[float] = None
    iones_comunes_mg_l: Optional[float] = None
    observaciones: Optional[str] = None


class NTC3459Request(BaseModel):
    nombre: str
    fuente: FuenteAgua
    analisis: AnalisisAguaInput
    fecha_muestreo: Optional[str] = None
    laboratorio: Optional[str] = None
    concreto_preesforzado: bool = False


# ── NTC 3493 — Cenizas volantes y puzolanas naturales ─────────────────────────

class AnalisisAditivoMineralInput(BaseModel):
    sio2_porcentaje: float
    al2o3_porcentaje: float
    fe2o3_porcentaje: float
    perdida_ignicion_porcentaje: float
    retencion_malla_325_porcentaje: float
    finura_blaine_m2_kg: Optional[float] = None
    densidad_g_cm3: Optional[float] = None
    observaciones: Optional[str] = None


class NTC3493Request(BaseModel):
    nombre: str
    clase: ClaseAditivoMineral
    analisis: AnalisisAditivoMineralInput
    fabricante: Optional[str] = None
    origen: Optional[str] = None
    tolerancia_loi: bool = False


# ── NTC 3502 — Aditivos incorporadores de aire ────────────────────────────────

class NTC3502Request(BaseModel):
    nombre: str
    tipo: TipoAditivoAire
    contenido_aire_porcentaje: float
    dosificacion_recomendada: str
    libre_cloruros: bool = True
    ph: Optional[float] = None
    densidad_g_cm3: Optional[float] = None
    fabricante: Optional[str] = None


# ── NTC 3760 — Pigmentos para concreto coloreado ──────────────────────────────

class NTC3760Request(BaseModel):
    nombre: str
    tipo: TipoPigmento
    presentacion: PresentacionPigmento
    dosificacion_maxima_porcentaje: float
    color: str
    resistencia_alcalina: bool = True
    resistencia_intemperie: bool = True
    fabricante: Optional[str] = None


# ── NTC 4018 — Escoria de alto horno ──────────────────────────────────────────

class AnalisisEscoriaInput(BaseModel):
    indice_actividad_7dias: float
    indice_actividad_28dias: float
    finura_blaine_m2_kg: float
    densidad_g_cm3: float
    contenido_azufre_porcentaje: Optional[float] = None
    perdida_ignicion_porcentaje: Optional[float] = None
    observaciones: Optional[str] = None


class NTC4018Request(BaseModel):
    nombre: str
    grado: GradoEscoria
    analisis: AnalisisEscoriaInput
    fabricante: Optional[str] = None
    origen: Optional[str] = None


# ── NTC 4024 — Prefabricados de concreto ──────────────────────────────────────

class DimensionesPrefabricadoInput(BaseModel):
    longitud_mm: float
    altura_mm: float
    espesor_mm: float
    espesor_pared_mm: Optional[float] = None
    espesor_tabique_mm: Optional[float] = None


class ResultadosEnsayoInput(BaseModel):
    resistencia_compresion_mpa: Optional[float] = None
    absorcion_porcentaje: Optional[float] = None
    densidad_g_cm3: Optional[float] = None
    contenido_humedad_porcentaje: Optional[float] = None
    observaciones: Optional[str] = None


class NTC4024Request(BaseModel):
    nombre: str
    tipo: TipoPrefabricado
    dimensiones: DimensionesPrefabricadoInput
    resultados: ResultadosEnsayoInput
    tamano_lote: int
    numero_especimenes: int
    fabricante: Optional[str] = None
    fecha_muestreo: Optional[str] = None


# ── NTC 4924 — Agregados livianos y unidades de mampostería ──────────────────

class AgregadoLivianoInput(BaseModel):
    nombre: str
    tipo: TipoAgregadoLiviano
    densidad_aparente_kg_m3: float
    absorcion_porcentaje: float
    resistencia_compresion_mpa: Optional[float] = None
    tamano_maximo_mm: Optional[float] = None
    modulo_finura: Optional[float] = None
    fabricante: Optional[str] = None


class NTC4924AgregadoRequest(AgregadoLivianoInput):
    pass


class NTC4924MamposteriaRequest(BaseModel):
    nombre: str
    tipo: TipoUnidadMamposteria
    agregado: AgregadoLivianoInput
    dimensiones_mm: dict[str, float] = Field(..., description="largo, ancho, alto")
    resistencia_compresion_mpa: float
    densidad_aparente_kg_m3: float
    absorcion_porcentaje: float
    fabricante: Optional[str] = None


# ── NTC 5147 — Resistencia a la abrasión ──────────────────────────────────────

class ResultadoAbrasionInput(BaseModel):
    longitud_huella_1_mm: float
    longitud_huella_2_mm: float
    longitud_huella_3_mm: float
    longitud_huella_4_mm: float
    longitud_huella_5_mm: float
    observaciones: Optional[str] = None


class NTC5147Request(BaseModel):
    nombre: str
    tipo: TipoMaterial
    resultados: ResultadoAbrasionInput
    fecha_ensayo: Optional[str] = None
    laboratorio: Optional[str] = None
    fabricante: Optional[str] = None


# ── NTC 6008 — Terminología y clasificación ───────────────────────────────────

class NTC6008Request(BaseModel):
    termino_busqueda: str
