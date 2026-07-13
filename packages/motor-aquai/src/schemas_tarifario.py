"""
AquaAI — Schemas Pydantic: Módulo Tarifario / SUI
Referencia normativa:
  - Resolución CRA 688 de 2014 (prestadores > 5.000 suscriptores)
  - Resolución CRA 825 de 2017 (prestadores ≤ 5.000 suscriptores)
  - Resolución CRA 943 de 2021 (actualización parámetros período 2021-2026)
  - Resolución CRA 750 de 2016 (zonas rurales / esquemas diferenciales)
  - Ley 142 de 1994 (régimen de subsidios y contribuciones)
"""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ─── Enumeraciones ────────────────────────────────────────────────────────────

class TipoPrestador(str, Enum):
    GRANDE     = "grande"       # > 5.000 suscriptores — aplica CRA 688/2014 + 943/2021
    PEQUENO    = "pequeno"      # ≤ 5.000 suscriptores — aplica CRA 825/2017
    RURAL      = "rural"        # Esquema diferencial — aplica CRA 750/2016


class Estrato(str, Enum):
    E1          = "1"
    E2          = "2"
    E3          = "3"
    E4          = "4"
    E5          = "5"
    E6          = "6"
    COMERCIAL   = "comercial"
    INDUSTRIAL  = "industrial"
    OFICIAL     = "oficial"


class ServicioTarifario(str, Enum):
    ACUEDUCTO     = "acueducto"
    ALCANTARILLADO = "alcantarillado"
    AMBOS         = "ambos"


# ─── Request: cálculo de tarifa ───────────────────────────────────────────────

class TarifaRequest(BaseModel):
    tipo_prestador: TipoPrestador
    clima: str = Field(
        ...,
        description="frio | templado | calido — define consumo básico CRA"
    )
    servicio: ServicioTarifario = ServicioTarifario.ACUEDUCTO

    # Costos medios (en $/m³ o $/suscriptor/mes según componente)
    # El prestador los calcula con su contabilidad regulatoria
    costo_medio_inversion_cmi: float = Field(
        ..., ge=0,
        description="CMI en $/m³. Para pequeños prestadores puede estimarse con la tabla CRA 825."
    )
    costo_medio_operacion_cmo: float = Field(
        ..., ge=0,
        description="CMO en $/m³. Incluye energía, químicos, personal operativo."
    )
    costo_medio_administracion_cma: float = Field(
        ..., ge=0,
        description="CMA en $/suscriptor/mes. Costos administrativos fijos."
    )
    consumo_medio_facturado_m3: float = Field(
        default=15.0, gt=0,
        description="Consumo promedio facturado por suscriptor (m³/mes). Usado para distribuir CMA en el cargo por consumo."
    )
    factor_perdidas: float = Field(
        default=0.25, ge=0, le=0.60,
        description="Fracción de agua no contabilizada (IANC). RAS recomienda ≤25% para sistema nuevo."
    )
    anio_calculo: int = Field(default=2025, ge=2021, le=2030)


# ─── Response: tarifa calculada ───────────────────────────────────────────────

class ComponenteTarifa(BaseModel):
    cargo_fijo_mes: float           = Field(description="Cargo fijo mensual por suscriptor ($/mes)")
    cargo_consumo_basico_m3: float  = Field(description="Cargo por consumo básico ($/m³)")
    cargo_consumo_compl_m3: float   = Field(description="Cargo por consumo complementario ($/m³)")
    cargo_consumo_suntuario_m3: float = Field(description="Cargo consumo suntuario ($/m³)")
    consumo_basico_limite_m3: float = Field(description="Límite de consumo básico (m³/suscriptor/mes) por clima")
    consumo_complementario_limite_m3: float


class TarifaEstrato(BaseModel):
    estrato: str
    cargo_fijo_aplicado: float
    cargo_consumo_basico_aplicado: float
    factor_subsidio_contribucion: float
    tipo: str                   # "subsidio" | "equilibrio" | "contribucion"
    norma_ref: str


class TarifaResponse(BaseModel):
    tarifa_base: ComponenteTarifa
    tarifas_por_estrato: list[TarifaEstrato]
    cmlp_m3: float              = Field(description="Costo Medio de Largo Plazo total ($/m³)")
    metodologia_aplicada: str
    norma_ref: str
    advertencias: list[str]
    ejemplo_factura: dict       = Field(description="Factura ejemplo para un suscriptor estrato 3 con consumo medio")


# ─── Request: reporte SUI ─────────────────────────────────────────────────────

class ReporteSUIRequest(BaseModel):
    municipio: str
    departamento: str
    nit_prestador: str          = Field(..., description="NIT del prestador registrado en SUI")
    periodo: str                = Field(..., description="Período de reporte: 'YYYY-MM' (ej. '2025-03')")
    servicio: ServicioTarifario

    # Datos operativos del período
    suscriptores_totales: int   = Field(..., gt=0)
    suscriptores_por_estrato: dict = Field(
        description="{'1': 120, '2': 80, '3': 50, ...}"
    )
    volumen_producido_m3: float = Field(..., gt=0, description="m³ producidos en el período")
    volumen_facturado_m3: float = Field(..., gt=0, description="m³ facturados a suscriptores")
    recaudo_total_cop: float    = Field(..., ge=0, description="Recaudo total en pesos colombianos")

    # Calidad del agua
    irca_promedio: Optional[float] = Field(
        None, ge=0, le=100,
        description="IRCA promedio del período (0=sin riesgo, 100=inviable). Res 2115/2007."
    )
    muestras_tomadas: Optional[int] = None
    muestras_no_conformes: Optional[int] = None

    # Tarifas vigentes del período
    tarifa_cargo_fijo_estrato3: float
    tarifa_cargo_consumo_basico_estrato3: float


# ─── Response: reporte SUI ───────────────────────────────────────────────────

class IndicadorSUI(BaseModel):
    nombre: str
    valor: float
    unidad: str
    rango_aceptable: str
    cumple: Optional[bool]


class ReporteSUIResponse(BaseModel):
    periodo: str
    prestador_nit: str
    municipio: str
    ianc_pct: float             = Field(description="Índice de agua no contabilizada (%)")
    irca_categoria: str         = Field(description="Sin riesgo / Bajo / Medio / Alto / Inviable")
    indicadores: list[IndicadorSUI]
    campos_sui: dict            = Field(description="Estructura lista para copiar/pegar en el portal SUI")
    alertas_regulatorias: list[str]
    normas_aplicadas: list[str]
