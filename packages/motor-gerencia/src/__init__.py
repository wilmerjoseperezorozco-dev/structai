from .schemas import (
    SnapshotInput, ProjectInput, SnapshotKPIRequest, PortfolioRequest, ProjectSeriesRequest,
)
from .models import Snapshot, Project
from .evm import (
    KPI_META, classify_kpi, composite_score, trend_direction,
    forecast_eac, cross_project_summary,
)
from .ml_engine import (
    linear_regression, predict_values, detect_anomalies,
    predict_completion_date, risk_score, forecast_kpis,
    pearson_correlation, kpi_correlation_matrix,
)


def _snapshot_from_input(s: SnapshotInput, bac: float) -> Snapshot:
    return Snapshot(
        period=s.period, pv=s.pv, ev=s.ev, ac=s.ac,
        quality_pct=s.quality_pct, resources_planned=s.resources_planned,
        resources_actual=s.resources_actual, incidents=s.incidents,
        bac=bac, eac_method=s.eac_method,
    )


def _project_from_input(p: ProjectInput) -> Project:
    proj = Project(
        id=p.id, name=p.name, project_type=p.project_type, icon=p.icon,
        location=p.location, contractor=p.contractor, bac=p.bac,
        scope_quantity=p.scope_quantity, unit=p.unit, duration_months=p.duration_months,
    )
    proj.snapshots = [_snapshot_from_input(s, p.bac) for s in p.snapshots]
    return proj


def calcular_snapshot(req: SnapshotKPIRequest) -> dict:
    snap = _snapshot_from_input(req.snapshot, req.bac)
    data = snap.to_dict()
    data["clasificacion"] = {
        kpi: classify_kpi(kpi, getattr(snap, kpi))
        for kpi in ["cpi", "spi", "qpi", "ppi", "tcpi"]
    }
    data["score_compuesto"] = composite_score(snap.cpi, snap.spi, snap.qpi, snap.ppi)
    return data


def analizar_portafolio(req: PortfolioRequest) -> dict:
    projects = [_project_from_input(p) for p in req.projects]
    resultado = cross_project_summary(projects)
    if not resultado:
        return {"rows": [], "portfolio": {}, "alerts": []}
    return resultado


def calcular_riesgo(req: ProjectSeriesRequest) -> dict:
    proj = _project_from_input(req.project)
    return risk_score(proj.snapshots)


def calcular_forecast_kpis(req: ProjectSeriesRequest) -> dict:
    proj = _project_from_input(req.project)
    return forecast_kpis(proj.snapshots, n_ahead=req.n_ahead)


def calcular_fecha_termino(req: ProjectSeriesRequest) -> dict:
    proj = _project_from_input(req.project)
    resultado = predict_completion_date(proj.snapshots, proj.duration_months)
    if not resultado:
        return {"error": "Se requiere al menos un snapshot"}
    return resultado


def detectar_anomalias(req: ProjectSeriesRequest) -> dict:
    proj = _project_from_input(req.project)
    if req.kpi not in ("cpi", "spi", "qpi", "ppi"):
        return {"error": f"KPI inválido: {req.kpi}"}
    series = [getattr(s, req.kpi) for s in proj.snapshots]
    idx = detect_anomalies(series, threshold=req.anomaly_threshold)
    return {
        "kpi": req.kpi,
        "indices_anomalos": idx,
        "periodos_anomalos": [proj.snapshots[i].period for i in idx],
        "valores": [round(v, 4) for v in series],
    }


def calcular_correlacion(req: ProjectSeriesRequest) -> dict:
    proj = _project_from_input(req.project)
    if len(proj.snapshots) < 3:
        return {"error": "Se requieren al menos 3 snapshots para correlación"}
    return kpi_correlation_matrix(proj.snapshots)


__all__ = [
    "SnapshotInput", "ProjectInput", "SnapshotKPIRequest", "PortfolioRequest", "ProjectSeriesRequest",
    "Snapshot", "Project", "KPI_META",
    "calcular_snapshot", "analizar_portafolio", "calcular_riesgo",
    "calcular_forecast_kpis", "calcular_fecha_termino", "detectar_anomalias", "calcular_correlacion",
]
