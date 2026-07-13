"""
motor-gerencia — Schemas Pydantic de entrada.
Ciencia de datos gerencial: Earned Value Management (EVM) + ML predictivo
sobre series de avance de obra. Puerto de core/evm.py y core/ml_engine.py
de CivilDS_Symbiont (verificado byte a byte por CRC contra el ZIP fuente).
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SnapshotInput(BaseModel):
    period: str = Field(..., description="Etiqueta del período, ej. 'Ene', 'Feb'")
    pv: float = Field(..., description="Planned Value — valor planificado acumulado")
    ev: float = Field(..., description="Earned Value — valor ganado acumulado")
    ac: float = Field(..., description="Actual Cost — costo real acumulado")
    quality_pct: float = Field(..., description="% de calidad del período (0-100)")
    resources_planned: float = Field(..., description="Recursos planificados del período")
    resources_actual: float = Field(..., description="Recursos realmente empleados")
    incidents: int = 0
    eac_method: str = Field(default="cpi", description="cpi | bac | composite")


class ProjectInput(BaseModel):
    id: str
    name: str
    project_type: str = ""
    icon: str = "🏗️"
    location: str = ""
    contractor: str = ""
    bac: float = Field(..., description="Budget at Completion")
    scope_quantity: float = 0.0
    unit: str = ""
    duration_months: int = 12
    snapshots: list[SnapshotInput] = Field(default_factory=list)


class SnapshotKPIRequest(BaseModel):
    """Cálculo de KPIs para un único snapshot, sin necesidad de historial completo."""
    bac: float
    snapshot: SnapshotInput


class PortfolioRequest(BaseModel):
    projects: list[ProjectInput] = Field(..., min_length=1)


class ProjectSeriesRequest(BaseModel):
    """Serie histórica de una sola obra — usada por los endpoints de ML."""
    project: ProjectInput
    n_ahead: int = Field(default=3, description="Períodos a proyectar (forecast)")
    kpi: str = Field(default="cpi", description="cpi | spi | qpi | ppi — para anomalías")
    anomaly_threshold: float = Field(default=2.0, description="Umbral de z-score")
