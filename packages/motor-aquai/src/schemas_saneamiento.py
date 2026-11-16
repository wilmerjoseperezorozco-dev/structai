"""
AquaAI — Schemas Pydantic: Módulo Saneamiento PTAP/PTAR
Referencia normativa:
  - Resolución 0330/2017 Título C — Potabilización (reemplaza RAS 2000 Tít. C)
  - Resolución 0330/2017 arts. 164-200 — Tratamiento de aguas residuales (reemplazó al RAS 2000 Título E)
  - Resolución 0631/2015 MADS  — Valores máximos permisibles vertimientos a cuerpos de agua
  - Decreto 1076/2015          — DUR sector ambiente (vertimientos)
  - Resolución 2115/2007       — Parámetros calidad agua potable (IRCA)
"""
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ─── Enumeraciones ────────────────────────────────────────────────────────────

class CoagulanteType(str, Enum):
    ALUMBRE          = "alumbre"           # Sulfato de aluminio Al₂(SO₄)₃·18H₂O
    PAC              = "pac"               # Poli-cloruro de aluminio (más eficiente a baja T°)
    SULFATO_FERRICO  = "sulfato_ferrico"   # Fe₂(SO₄)₃ — aguas con color alto
    CLORURO_FERRICO  = "cloruro_ferrico"   # FeCl₃

class TecnologiaPTAR(str, Enum):
    UASB             = "uasb"             # Reactor anaerobio flujo ascendente — nivel bajo/medio
    LODOS_ACTIVADOS  = "lodos_activados"  # Convencional — nivel medio-alto/alto
    FILTRO_PERCOLADOR= "filtro_percolador"# Nivel medio, sin electricidad abundante
    LAGUNA_FACULTATIVA = "laguna_facultativa" # Nivel bajo, disponibilidad de tierra

class TipoCuerpoReceptor(str, Enum):
    RIO              = "rio"
    QUEBRADA         = "quebrada"
    LAGO             = "lago"
    SUELO            = "suelo"            # La Res. 0631/2015 no aplica al suelo (art. 1, parágrafo): responde 422


# ─── PTAP ────────────────────────────────────────────────────────────────────

class PTAPRequest(BaseModel):
    caudal_diseno_ls: float     = Field(..., gt=0, description="Qmd de diseño (L/s) — salida del módulo hidráulico")
    turbidez_cruda_ntu: float   = Field(..., ge=0, description="Turbidez agua cruda (NTU) — dato IDEAM o aforo")
    color_crudo_uc: float       = Field(..., ge=0, description="Color aparente agua cruda (UC)")
    ph_crudo: float             = Field(..., ge=4.0, le=11.0, description="pH agua cruda")
    temperatura_c: float        = Field(..., ge=0, le=35.0, description="Temperatura media del agua (°C)")
    coagulante: CoagulanteType  = CoagulanteType.ALUMBRE
    nivel_complejidad: str      = Field(default="medio", description="bajo | medio | medio_alto | alto")


class UnidadPTAP(BaseModel):
    nombre: str
    dimensiones: dict
    parametros_diseno: dict
    norma_ref: str
    advertencias: list[str] = []


class PTAPResponse(BaseModel):
    caudal_diseno_ls: float
    dosis_coagulante_mg_l: float
    consumo_coagulante_kg_dia: float
    unidades: list[UnidadPTAP]           # floculador, sedimentador, filtros, desinfección
    cloro_residual_min_mg_l: float
    cloro_residual_max_mg_l: float
    ct_requerido_mg_min_l: float
    dosis_cloro_mg_l: float
    cumple_res2115: Optional[bool] = Field(description="null: el diseño no permite afirmarlo; se verifica con "
                                           "muestreo del agua tratada (Res. 2115/2007)")
    normas_aplicadas: list[str]
    advertencias: list[str]


# ─── PTAR ────────────────────────────────────────────────────────────────────

class PTARRequest(BaseModel):
    poblacion_diseno: int           = Field(..., gt=0)
    caudal_acueducto_ls: float      = Field(..., gt=0, description="Qmd del acueducto (L/s)")
    factor_retorno: float           = Field(..., ge=0.60, le=0.95,
                                            description="Fracción del caudal acueducto que llega al alcantarillado")
    dbo5_cruda_mg_l: Optional[float] = Field(None, gt=0, le=5000, description="DBO₅ agua residual cruda (mg/L). Si no se provee, se estima per cápita.")
    sst_crudo_mg_l: Optional[float]  = Field(None, gt=0, le=5000, description="SST agua residual cruda (mg/L). Estimado si no se provee.")
    tecnologia: TecnologiaPTAR      = TecnologiaPTAR.UASB
    nivel_complejidad: str          = Field(default="medio", pattern="^(bajo|medio|medio_alto|alto)$")
    tipo_cuerpo_receptor: TipoCuerpoReceptor
    temperatura_agua_c: Optional[float] = Field(None, ge=0, le=40,
        description="Temperatura del agua residual (°C). Obligatoria para UASB (Res. 0330 tabla 31) y laguna.")
    profundidad_laguna_m: Optional[float] = Field(None, gt=0, le=10,
        description="Obligatoria para laguna facultativa (Res. 0330 art. 197: 1,5 a 2,5 m).")
    factor_pico: Optional[float] = Field(None, ge=1.0, le=5.0,
        description="Factor pico Qmax/Qmed (Res. 0330 art. 164). Si se da, se verifica la velocidad UASB a caudal máximo.")
    eficiencia_requerida_dbo_pct: Optional[float] = Field(
        None, ge=0, le=100,
        description="Eficiencia mínima de remoción DBO requerida por la autoridad ambiental (%). "
                    "Si no se provee, se calcula desde la Res 0631/2015."
    )


class BalanceLodos(BaseModel):
    produccion_lodos_kg_dia: float  = Field(description="kg SST/día producidos en el sistema")
    volumen_lodos_m3_dia: float     = Field(description="m³/día de lodos al 1% de sólidos")
    destino_recomendado: str


class PTARResponse(BaseModel):
    caudal_ar_ls: float             = Field(description="Caudal aguas residuales de diseño (L/s)")
    caudal_ar_m3_dia: float
    dbo5_cruda_mg_l: float
    sst_crudo_mg_l: float
    carga_dbo_kg_dia: float
    carga_sst_kg_dia: float
    tecnologia: str
    dimensionamiento: dict          = Field(description="Dimensiones y parámetros del sistema seleccionado")
    eficiencia_dbo_pct: float       = Field(description="Eficiencia de remoción DBO esperada (%)")
    eficiencia_requerida_dbo_pct: float = Field(description="Máximo entre la exigida por la Res. 0631 y la de la autoridad (%)")
    dbo_efluente_mg_l: float        = Field(description="DBO₅ esperada en el efluente tratado")
    sst_efluente_mg_l: float
    limite_res0631_dbo: float       = Field(description="Límite DBO5 de la Res. 0631/2015 art. 8 según la carga (mg/L)")
    limite_res0631_sst: float       = Field(description="Límite SST de la Res. 0631/2015 art. 8 según la carga (mg/L)")
    cumple_res0631: bool
    balance_lodos: BalanceLodos
    normas_aplicadas: list[str]
    advertencias: list[str]
