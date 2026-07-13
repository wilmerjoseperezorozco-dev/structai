"""
AquaAI — Schemas Pydantic
Motor de cálculo RAS 2000 · Colombia

Cada endpoint recibe un Request y devuelve un Response tipado.
El LLM extrae los parámetros del texto del usuario y llama al endpoint correcto.
NUNCA se le pide al LLM que calcule — solo que interprete y rutee.
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator


# ─── Enumeraciones RAS 2000 ───────────────────────────────────────────────────

class NivelComplejidad(str, Enum):
    BAJO       = "bajo"
    MEDIO      = "medio"
    MEDIO_ALTO = "medio_alto"
    ALTO       = "alto"


class ClimaRegion(str, Enum):
    """
    Regiones climáticas de Colombia relevantes para dotación y diseño.
    Temperatura media del municipio como proxy de clima.
    """
    FRIO       = "frio"        # T < 12°C   — Altiplano, páramos (> 2500 msnm)
    TEMPLADO   = "templado"    # 12–24°C    — Zona cafetera, valles andinos
    CALIDO     = "calido"      # T > 24°C   — Costa Caribe, Llanos, Amazonia, valles bajos


class MetodoPoblacion(str, Enum):
    ARITMETICO   = "aritmetico"
    GEOMETRICO   = "geometrico"
    EXPONENCIAL  = "exponencial"


class VariableHidro(str, Enum):
    PRECIPITACION = "precipitacion"
    CAUDAL        = "caudal"
    NIVEL         = "nivel"
    TEMPERATURA   = "temperatura"


# ─── Proyección de población ──────────────────────────────────────────────────

class PoblacionRequest(BaseModel):
    poblacion_censal: int = Field(..., gt=0, description="Población del último censo disponible")
    anio_censo: int       = Field(..., ge=1900, le=2100)
    anio_diseno: int      = Field(..., ge=1900, le=2100)
    tasa_crecimiento: Optional[float] = Field(
        None, description="Tasa anual decimal (ej. 0.025 = 2.5%). Si no se provee, se estima por nivel de complejidad."
    )
    nivel_complejidad: NivelComplejidad
    metodo: MetodoPoblacion = MetodoPoblacion.GEOMETRICO

    @model_validator(mode="after")
    def validar_anios(self) -> "PoblacionRequest":
        if self.anio_diseno <= self.anio_censo:
            raise ValueError("anio_diseno debe ser mayor que anio_censo")
        return self


class PoblacionResponse(BaseModel):
    poblacion_diseno: int
    periodo_diseno: int
    tasa_usada: float
    metodo: str
    formula: str
    notas: str


# ─── Dotación y caudales ──────────────────────────────────────────────────────

class CaudalesRequest(BaseModel):
    poblacion_diseno: int          = Field(..., gt=0)
    nivel_complejidad: NivelComplejidad
    clima: ClimaRegion
    dotacion_manual: Optional[float] = Field(
        None,
        description="L/hab/día. Si se provee, omite la tabla RAS y usa este valor directamente."
    )
    perdidas_pct: float = Field(
        default=25.0, ge=0, le=60,
        description="% de pérdidas en la red (RAS recomienda ≤25% para sistema nuevo)"
    )

class CaudalesResponse(BaseModel):
    dotacion_lhd: float            = Field(description="Dotación neta L/hab/día (tabla RAS B.2.1)")
    dotacion_bruta_lhd: float      = Field(description="Dotación bruta incluyendo pérdidas")
    Qp_ls: float                   = Field(description="Caudal promedio diario (L/s)")
    Qmd_ls: float                  = Field(description="Caudal máximo diario (L/s)")
    Qmh_ls: float                  = Field(description="Caudal máximo horario (L/s)")
    Qci_ls: float                  = Field(description="Caudal contra incendio (L/s) — RAS B.7")
    fmd: float                     = Field(description="Factor día máximo usado")
    fmh: float                     = Field(description="Factor hora máxima usado")
    norma_ref: str                 = Field(description="Referencia normativa aplicada")


# ─── Hidráulica de tuberías ───────────────────────────────────────────────────

class HazenWilliamsRequest(BaseModel):
    caudal_ls: float        = Field(..., gt=0, description="Caudal de diseño (L/s)")
    longitud_m: float       = Field(..., gt=0, description="Longitud del tramo (m)")
    diametro_mm: Optional[float] = Field(
        None, gt=0,
        description="Diámetro nominal en mm. Si se omite, el motor calcula el mínimo que cumple velocidad y presión."
    )
    cota_inicio_m: float    = Field(default=0.0, description="Cota piezométrica aguas arriba (m)")
    presion_minima_mca: float = Field(default=10.0, description="Presión mínima requerida (m.c.a.) — RAS B.6.4")
    presion_maxima_mca: float = Field(default=60.0, description="Presión máxima permitida (m.c.a.) — RAS B.6.4")
    material: str = Field(
        default="PVC",
        description="Material tubería: PVC, HDPE, ACERO, AC, CONCRETO — define coeficiente C de Hazen-Williams"
    )


class HazenWilliamsResponse(BaseModel):
    diametro_calculado_mm: float
    diametro_nominal_mm: float
    velocidad_ms: float
    perdida_unitaria_mm: float     = Field(description="Pérdida de carga por metro (mm/m)")
    perdida_total_mca: float
    presion_salida_mca: float
    coeficiente_C: int
    cumple_velocidad: bool
    cumple_presion: bool
    advertencias: list[str]
    norma_ref: str


# ─── Hidrología — caudal de diseño ───────────────────────────────────────────

class MetodoConcentracion(str, Enum):
    KIRPICH = "kirpich"
    TEMEZ   = "temez"
    BRANSBY = "bransby_williams"


class HidrologiaRequest(BaseModel):
    area_cuenca_ha: float       = Field(..., gt=0, description="Área de la cuenca en hectáreas")
    longitud_cauce_m: float     = Field(..., gt=0, description="Longitud del cauce principal (m)")
    pendiente_media: float      = Field(..., gt=0, le=1.0, description="Pendiente media del cauce (m/m)")
    periodo_retorno: int        = Field(default=25, description="Período de retorno en años (TR)")
    coeficiente_escorrentia: float = Field(
        ..., ge=0.05, le=1.0,
        description="Coeficiente C de escorrentía. Ver tabla RAS D.3 según uso del suelo."
    )
    region_idf: str             = Field(
        ...,
        description="Región IDF Colombia: 'caribe', 'andina_norte', 'andina_sur', 'pacifico', 'orinoquia', 'amazonia'"
    )
    metodo_tc: MetodoConcentracion = Field(
        default=MetodoConcentracion.KIRPICH,
        description="Método para calcular tiempo de concentración"
    )


class HidrologiaResponse(BaseModel):
    tiempo_concentracion_min: float = Field(description="Tiempo de concentración Tc (min)")
    intensidad_mm_h: float          = Field(description="Intensidad de diseño I (mm/h) para TR dado")
    caudal_diseno_m3s: float        = Field(description="Caudal de diseño Q (m³/s) — Método Racional")
    caudal_diseno_ls: float
    metodo_tc_usado: str
    parametros_idf: dict            = Field(description="Coeficientes a, b, n de la curva IDF regional usada")
    formula_racional: str
    notas_region: str


# ─── Bucle ↻ — registro de consulta ─────────────────────────────────────────

class RegistroConsultaRequest(BaseModel):
    municipio_id: Optional[str]   = None
    tipo_consulta: str             = Field(..., description="hidraulico | hidrologico | normativa | sui")
    pregunta: str
    respuesta: str
    normas_citadas: list[str]      = Field(default_factory=list, description="Lista de UUIDs de normas.id")
    parametros_calculo: dict       = Field(
        default_factory=dict,
        description="Inputs y outputs del cálculo: {caudal_diseno_ls: 42.3, metodo: 'racional', ...}"
    )


class RegistroConsultaResponse(BaseModel):
    consulta_id: str
    guardado: bool
    mensaje: str
