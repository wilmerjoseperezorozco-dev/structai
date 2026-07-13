"""
Civil DS Symbiont — EVM Engine
Cálculos de Earned Value Management + análisis avanzado de trazabilidad.
"""
from __future__ import annotations
from typing import List, Dict, Tuple
import statistics


KPI_META = {
    "cpi": {
        "name": "Cost Performance Index",
        "formula": "EV / AC",
        "unit": "ratio",
        "good": (1.0, 99),
        "alert": (0.9, 0.999),
        "critical": (0, 0.899),
        "higher_better": True,
    },
    "spi": {
        "name": "Schedule Performance Index",
        "formula": "EV / PV",
        "unit": "ratio",
        "good": (1.0, 99),
        "alert": (0.9, 0.999),
        "critical": (0, 0.899),
        "higher_better": True,
    },
    "qpi": {
        "name": "Quality Performance Index",
        "formula": "Calidad% / 100",
        "unit": "ratio",
        "good": (1.0, 99),
        "alert": (0.9, 0.999),
        "critical": (0, 0.899),
        "higher_better": True,
    },
    "ppi": {
        "name": "Productivity Performance Index",
        "formula": "(EV/AC) × (RP/RR)",
        "unit": "ratio",
        "good": (1.0, 99),
        "alert": (0.85, 0.999),
        "critical": (0, 0.849),
        "higher_better": True,
    },
    "sv": {
        "name": "Schedule Variance",
        "formula": "EV − PV",
        "unit": "USD",
        "good": (0, 999_999_999),
        "alert": (-50_000, -1),
        "critical": (-999_999_999, -50_001),
        "higher_better": True,
    },
    "cv": {
        "name": "Cost Variance",
        "formula": "EV − AC",
        "unit": "USD",
        "good": (0, 999_999_999),
        "alert": (-50_000, -1),
        "critical": (-999_999_999, -50_001),
        "higher_better": True,
    },
    "tcpi": {
        "name": "To-Complete Performance Index",
        "formula": "(BAC−EV) / (BAC−AC)",
        "unit": "ratio",
        "good": (0, 1.05),
        "alert": (1.051, 1.10),
        "critical": (1.101, 99),
        "higher_better": False,
    },
}


def classify_kpi(kpi: str, value: float) -> str:
    """Retorna '🟢', '🟡' o '🔴' según el valor del KPI."""
    meta = KPI_META.get(kpi)
    if not meta:
        return "⚪"
    g_lo, g_hi = meta["good"]
    a_lo, a_hi = meta["alert"]
    if g_lo <= value <= g_hi:
        return "🟢"
    elif a_lo <= value <= a_hi:
        return "🟡"
    return "🔴"


def composite_score(cpi: float, spi: float, qpi: float, ppi: float) -> float:
    """Score compuesto 0-100 para semáforo global."""
    weights = {"cpi": 0.30, "spi": 0.25, "qpi": 0.25, "ppi": 0.20}
    values  = {"cpi": cpi, "spi": spi, "qpi": qpi, "ppi": ppi}
    score = sum(weights[k] * min(v, 1.2) / 1.2 * 100 for k, v in values.items())
    return round(score, 1)


def trend_direction(series: List[float]) -> str:
    """↗ Mejorando / ↘ Deteriorando / → Estable"""
    if len(series) < 3:
        return "→"
    recent = series[-3:]
    delta = recent[-1] - recent[0]
    if abs(delta) < 0.01:
        return "→ Estable"
    return "↗ Mejorando" if delta > 0 else "↘ Deteriorando"


def forecast_eac(bac: float, ev: float, ac: float, cpi: float,
                 method: str = "cpi") -> float:
    """
    Estima el costo final del proyecto (EAC).
    method: 'cpi' | 'bac' | 'composite'
    """
    if method == "cpi":
        return bac / cpi if cpi else bac
    elif method == "bac":
        return ac + (bac - ev)
    elif method == "composite":
        spi_approx = 1.0
        return ac + (bac - ev) / (cpi * spi_approx)
    return bac


def cross_project_summary(projects) -> Dict:
    """
    Análisis de trazabilidad cruzada: compara todos los proyectos
    en el último período y retorna rankings y alertas.
    """
    rows = []
    for p in projects:
        s = p.latest
        if not s:
            continue
        rows.append({
            "id": p.id,
            "name": p.name,
            "type": p.project_type,
            "icon": p.icon,
            "cpi": s.cpi,
            "spi": s.spi,
            "qpi": s.qpi,
            "ppi": s.ppi,
            "sv":  s.sv,
            "cv":  s.cv,
            "tcpi": s.tcpi,
            "eac":  s.eac,
            "percent_complete": s.percent_complete,
            "score": composite_score(s.cpi, s.spi, s.qpi, s.ppi),
            "status": p.overall_status,
        })

    if not rows:
        return {}

    # Rankings
    for kpi in ["cpi", "spi", "qpi", "ppi", "score"]:
        ranked = sorted(rows, key=lambda r: r[kpi], reverse=True)
        for rank, row in enumerate(ranked, 1):
            row[f"rank_{kpi}"] = rank

    # Aggregates
    def avg(key): return round(statistics.mean(r[key] for r in rows), 3)
    def best(key): return max(rows, key=lambda r: r[key])["id"]
    def worst(key): return min(rows, key=lambda r: r[key])["id"]

    portfolio = {
        "n_projects": len(rows),
        "avg_cpi": avg("cpi"),
        "avg_spi": avg("spi"),
        "avg_qpi": avg("qpi"),
        "avg_ppi": avg("ppi"),
        "avg_score": avg("score"),
        "best_cpi": best("cpi"),
        "worst_cpi": worst("cpi"),
        "best_spi": best("spi"),
        "worst_spi": worst("spi"),
        "total_bac": sum(p.latest.bac for p in projects if p.latest),
        "total_eac": sum(r["eac"] for r in rows),
        "total_cv":  sum(r["cv"]  for r in rows),
        "total_sv":  sum(r["sv"]  for r in rows),
    }

    # Alertas automáticas
    alerts = []
    for r in rows:
        if r["cpi"] < 0.9:
            alerts.append({
                "level": "🔴 CRÍTICO",
                "project": r["name"],
                "message": f"CPI = {r['cpi']:.2f} — Sobrecoste severo. EAC estimado: ${r['eac']:,.0f}",
            })
        if r["spi"] < 0.9:
            alerts.append({
                "level": "🔴 CRÍTICO",
                "project": r["name"],
                "message": f"SPI = {r['spi']:.2f} — Retraso severo en cronograma.",
            })
        if r["tcpi"] > 1.1:
            alerts.append({
                "level": "🟡 ALERTA",
                "project": r["name"],
                "message": f"TCPI = {r['tcpi']:.2f} — Meta de eficiencia difícilmente alcanzable.",
            })
        if r["qpi"] < 0.9:
            alerts.append({
                "level": "🟡 ALERTA",
                "project": r["name"],
                "message": f"QPI = {r['qpi']:.2f} — Calidad por debajo de estándar.",
            })

    return {"rows": rows, "portfolio": portfolio, "alerts": alerts}
