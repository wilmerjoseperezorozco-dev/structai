"""
══════════════════════════════════════════════════════════════
MOTOR APU — MODELOS DE DATOS
Análisis de Precios Unitarios Jerarquico — Colombia
══════════════════════════════════════════════════════════════
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class UnidadMedida(str, Enum):
    M3   = "m³"
    M2   = "m²"
    ML   = "ml"
    KG   = "kg"
    UN   = "un"
    GL   = "gl"
    TON  = "ton"
    HR   = "hr"
    DIA  = "día"
    MES  = "mes"
    BTO  = "bulto"
    LT   = "lt"
    VJE  = "viaje"


class CategoriaObrero(str, Enum):
    OFICIAL       = "Oficial"
    AYUDANTE      = "Ayudante"
    MAESTRO       = "Maestro de obra"
    RESIDENTE     = "Residente de obra"
    OPERARIO      = "Operario maquinaria"
    SOLDADOR      = "Soldador"
    ELECTRICISTA  = "Electricista"
    TECNICO       = "Técnico especializado"


@dataclass
class MaterialItem:
    """Componente de material en APU"""
    codigo:       str
    descripcion:  str
    unidad:       UnidadMedida
    cantidad:     float          # cantidad por unidad de la actividad
    precio_unit:  float          # COP/unidad — Construdata 2026 Barranquilla
    desperdicio:  float = 0.05   # factor desperdicio (5% defecto)
    # Incertidumbre
    variacion_precio: float = 0.08  # ±8% variación mercado (σ/μ)
    variacion_cant:   float = 0.03  # ±3% variación en medición

    @property
    def subtotal(self) -> float:
        return self.cantidad * (1 + self.desperdicio) * self.precio_unit

    @property
    def cantidad_total(self) -> float:
        return self.cantidad * (1 + self.desperdicio)


@dataclass
class ManoObraItem:
    """Componente de mano de obra en APU"""
    categoria:          CategoriaObrero
    cantidad_cuadrilla: float           # número de trabajadores
    rendimiento:        float           # unidades producidas por día-cuadrilla
    jornal_dia:         float           # COP/día (SMMLV + factor)
    # Factor prestaciones sociales Colombia: ~1.6084 sobre salario básico
    # Incluye: prima, cesantías, intereses, vacaciones, dotación, ARL, EPS, pensión
    factor_prestaciones: float = 1.6084
    # Incertidumbre en rendimiento
    variacion_rend:      float = 0.12   # ±12% variación de rendimiento

    @property
    def costo_cuadrilla_dia(self) -> float:
        return self.cantidad_cuadrilla * self.jornal_dia * self.factor_prestaciones

    @property
    def subtotal(self) -> float:
        """Costo MO por unidad de la actividad"""
        if self.rendimiento <= 0:
            return 0.0
        return self.costo_cuadrilla_dia / self.rendimiento


@dataclass
class EquipoItem:
    """Componente de equipo/maquinaria en APU"""
    codigo:         str
    descripcion:    str
    unidad:         UnidadMedida      # hr o día
    cantidad:       float             # unidades de equipo
    rendimiento:    float             # unidades actividad por unidad tiempo
    valor_hora:     float             # COP/hora (depreciación + mantenimiento + combustible)
    horas_dia:      float = 8.0
    # Incertidumbre
    variacion_rend: float = 0.10      # ±10% variación rendimiento equipo

    @property
    def subtotal(self) -> float:
        if self.rendimiento <= 0:
            return 0.0
        costo_por_dia = self.cantidad * self.valor_hora * self.horas_dia
        return costo_por_dia / (self.rendimiento * self.horas_dia)


@dataclass
class AIU:
    """Administración, Imprevistos y Utilidad"""
    administracion: float = 0.10   # 10% sobre costos directos
    imprevistos:    float = 0.05   # 5%
    utilidad:       float = 0.08   # 8%

    @property
    def total_pct(self) -> float:
        return self.administracion + self.imprevistos + self.utilidad

    @property
    def factor(self) -> float:
        return 1 + self.total_pct


@dataclass
class APUResult:
    """Resultado completo del APU"""
    actividad_id:   str
    descripcion:    str
    unidad:         UnidadMedida
    # Costos directos
    costo_materiales: float
    costo_mano_obra:  float
    costo_equipo:     float
    costo_directo:    float
    # AIU
    aiu:             AIU
    costo_aiu:       float
    precio_unitario: float
    # Incertidumbre (Monte Carlo)
    pu_mean:         float = 0.0
    pu_std:          float = 0.0
    pu_p05:          float = 0.0    # percentil 5%
    pu_p95:          float = 0.0    # percentil 95%
    # Metadata
    capitulo:        str = ""
    norma_ref:       str = ""       # referencia NSR-10 / NTC
    fecha:           str = ""
    ciudad:          str = "Barranquilla"
    fuente_precios:  str = "Construdata 2026"
