"""
Civil DS Symbiont — modelos de dominio (Project/Snapshot).

El ZIP fuente (CivilDS_Symbiont) generaba estos datos con data/projects.py,
que no se pudo recuperar íntegro del origen. Las fórmulas de cada KPI
derivado sí están completas en evm.py (KPI_META) y se reimplementan aquí
como propiedades calculadas sobre los valores crudos (pv, ev, ac, ...)
que aporta el cliente — mismo resultado, sin datos de ejemplo simulados.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .evm import forecast_eac


@dataclass
class Snapshot:
    period: str
    pv: float
    ev: float
    ac: float
    quality_pct: float
    resources_planned: float
    resources_actual: float
    incidents: int
    bac: float
    eac_method: str = "cpi"

    @property
    def cpi(self) -> float:
        return self.ev / self.ac if self.ac else 0.0

    @property
    def spi(self) -> float:
        return self.ev / self.pv if self.pv else 0.0

    @property
    def qpi(self) -> float:
        return self.quality_pct / 100

    @property
    def ppi(self) -> float:
        base = self.ev / self.ac if self.ac else 0.0
        factor = self.resources_planned / self.resources_actual if self.resources_actual else 1.0
        return base * factor

    @property
    def sv(self) -> float:
        return self.ev - self.pv

    @property
    def cv(self) -> float:
        return self.ev - self.ac

    @property
    def tcpi(self) -> float:
        denom = self.bac - self.ac
        return (self.bac - self.ev) / denom if denom else 0.0

    @property
    def eac(self) -> float:
        return forecast_eac(self.bac, self.ev, self.ac, self.cpi, method=self.eac_method)

    @property
    def percent_complete(self) -> float:
        return round(self.ev / self.bac * 100, 2) if self.bac else 0.0

    def to_dict(self) -> dict:
        return {
            "period": self.period,
            "pv": self.pv, "ev": self.ev, "ac": self.ac,
            "cpi": round(self.cpi, 4), "spi": round(self.spi, 4),
            "qpi": round(self.qpi, 4), "ppi": round(self.ppi, 4),
            "sv": round(self.sv, 2), "cv": round(self.cv, 2), "tcpi": round(self.tcpi, 4),
            "eac": round(self.eac, 2), "percent_complete": self.percent_complete,
            "quality_pct": self.quality_pct, "incidents": self.incidents,
        }


@dataclass
class Project:
    id: str
    name: str
    project_type: str = ""
    icon: str = "🏗️"
    location: str = ""
    contractor: str = ""
    bac: float = 0.0
    scope_quantity: float = 0.0
    unit: str = ""
    duration_months: int = 12
    snapshots: List[Snapshot] = field(default_factory=list)

    @property
    def latest(self) -> Optional[Snapshot]:
        return self.snapshots[-1] if self.snapshots else None

    @property
    def overall_status(self) -> str:
        s = self.latest
        if not s:
            return "Sin datos"
        if s.cpi < 0.9 or s.spi < 0.9:
            return "🔴 Crítico"
        if s.cpi < 1.0 or s.spi < 1.0:
            return "🟡 Alerta"
        return "🟢 En control"
