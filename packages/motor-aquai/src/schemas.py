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


class ZonaIncendio(str, Enum):
    """
    Tipo de zona servida, para determinar el número de hidrantes en uso
    simultáneo exigido por el Art. 70 de la Res. 0330/2017.
    """
    UNIFAMILIAR = "unifamiliar"
    DENSA_MULTIFAMILIAR_COMERCIAL_INDUSTRIAL = "densa_multifamiliar_comercial_industrial"


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
    altura_msnm: float = Field(
        ..., ge=0, le=6000,
        description="Altura sobre el nivel del mar de la zona atendida (m). Determina el tope de dotación neta — Res. 0330/2017 Art. 43, Tabla 1."
    )
    zona_incendio: ZonaIncendio = Field(
        default=ZonaIncendio.UNIFAMILIAR,
        description="Tipo de zona servida. Determina el número de hidrantes en uso simultáneo exigido — Res. 0330/2017 Art. 70."
    )
    dotacion_manual: Optional[float] = Field(
        None,
        description="L/hab/día. Si se provee, omite la tabla normativa y usa este valor directamente (debe sustentarse en datos históricos reales de consumo — Art. 43)."
    )
    perdidas_pct: float = Field(
        default=25.0, ge=0, le=25,
        description="% de pérdidas técnicas máximas para diseño — tope legal 25% (Res. 0330/2017 Art. 44, Parágrafo)"
    )

class CaudalesResponse(BaseModel):
    dotacion_lhd: float            = Field(description="Dotación neta L/hab/día (Res. 0330/2017 Art. 43, Tabla 1)")
    dotacion_bruta_lhd: float      = Field(description="Dotación bruta incluyendo pérdidas")
    Qp_ls: float                   = Field(description="Caudal promedio diario (L/s)")
    Qmd_ls: float                  = Field(description="Caudal máximo diario (L/s)")
    Qmh_ls: float                  = Field(description="Caudal máximo horario (L/s)")
    Qci_ls: float                  = Field(description="Caudal mínimo contra incendio (L/s) — Res. 0330/2017 Art. 70")
    fmd: float                     = Field(description="Factor día máximo K1 usado — Res. 0330/2017 Art. 47")
    fmh: float                     = Field(description="Factor hora máxima K2 usado — Res. 0330/2017 Art. 47")
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
    tipo_tramo: Optional[str]   = Field(
        default=None,
        description="Opcional. Tipo de tramo de la Tabla 16 (Res. 0330/2017, Art. 135) para verificar el período de retorno mínimo."
    )


class VerificacionRes0330Request(BaseModel):
    """Verificación independiente de requisitos de la Res. 0330/2017. Solo se evalúa lo que se informe."""
    desnivel_caida_m: Optional[float] = Field(None, ge=0, description="Diferencia de cotas batea en una estructura de conexión (Art. 155).")
    diametro_entrada_mm: Optional[float] = Field(None, gt=0, description="Diámetro interno real de la tubería de entrada (Tabla 20).")
    reduccion_pico_suds_pct: Optional[float] = Field(None, ge=0, le=100, description="Reducción del caudal pico lograda con SUDS (Art. 153).")
    suds_viable: Optional[bool] = Field(None, description="Resultado documentado de la evaluación de viabilidad de SUDS.")


class VerificacionRes0330Response(BaseModel):
    verificaciones_normativas: list["VerificacionNormativa"]
    vigencia: dict
    no_verificado: list[str]


class VerificacionNormativa(BaseModel):
    """Resultado de una regla de la Resolución 0330/2017. 'requiere_criterio' = la norma habilita una excepción que decide el diseñador."""
    regla: str
    fuente: str
    estado: str = Field(description="cumple | no_cumple | requiere_criterio")
    detalle: str


class HidrologiaResponse(BaseModel):
    tiempo_concentracion_min: float = Field(description="Tiempo de concentración Tc (min)")
    intensidad_mm_h: float          = Field(description="Intensidad de diseño I (mm/h) para TR dado")
    caudal_diseno_m3s: float        = Field(description="Caudal de diseño Q (m³/s) — Método Racional")
    caudal_diseno_ls: float
    metodo_tc_usado: str
    parametros_idf: dict            = Field(description="Coeficientes a, b, n de la curva IDF regional usada")
    formula_racional: str
    notas_region: str
    verificaciones_normativas: list[VerificacionNormativa] = Field(default_factory=list, description="Verificación frente a la Res. 0330/2017 (Art. 135)")
    sensibilidad_tc: dict = Field(default_factory=dict, description="Caudal con Tc mínimo de 3 y de 10 min (Art. 135); el caudal principal no cambia")


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
