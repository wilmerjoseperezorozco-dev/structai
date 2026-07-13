"""
Civil DS Symbiont — ML Predictive Engine
Modelos de predicción: EAC, fecha de término, riesgo, anomalías.
No requiere scikit-learn — usa regresión lineal y estadística pura.
"""
from __future__ import annotations
from typing import List, Dict, Tuple, Optional
import math
import statistics


# ── Regresión lineal simple ────────────────────────────────────────────────────

def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float, float]:
    """
    Retorna (slope, intercept, r_squared).
    """
    n = len(x)
    if n < 2:
        return 0.0, y[0] if y else 0.0, 0.0
    sx  = sum(x)
    sy  = sum(y)
    sxx = sum(xi**2 for xi in x)
    sxy = sum(xi*yi for xi, yi in zip(x, y))
    denom = n*sxx - sx**2
    if denom == 0:
        return 0.0, sy/n, 0.0
    slope     = (n*sxy - sx*sy) / denom
    intercept = (sy - slope*sx) / n
    # R²
    y_mean = sy / n
    ss_tot = sum((yi - y_mean)**2 for yi in y)
    ss_res = sum((yi - (slope*xi + intercept))**2 for yi, xi in zip(y, x))
    r2 = 1 - ss_res/ss_tot if ss_tot else 1.0
    return slope, intercept, max(0.0, min(1.0, r2))


def predict_values(slope: float, intercept: float,
                   future_x: List[float]) -> List[float]:
    return [slope*x + intercept for x in future_x]


# ── Detección de anomalías (z-score) ──────────────────────────────────────────

def detect_anomalies(series: List[float], threshold: float = 2.0) -> List[int]:
    """Retorna índices donde el valor es anómalo (|z| > threshold)."""
    if len(series) < 3:
        return []
    mean = statistics.mean(series)
    std  = statistics.stdev(series)
    if std == 0:
        return []
    return [i for i, v in enumerate(series) if abs((v - mean) / std) > threshold]


# ── Predicción de fecha de término ────────────────────────────────────────────

def predict_completion_date(
    snapshots,
    total_months: int,
) -> Dict:
    """
    Usa el SPI actual para estimar la duración total revisada y la fecha de término.
    """
    if not snapshots:
        return {}
    latest = snapshots[-1]
    n_done = len(snapshots)
    spi = latest.spi if latest.spi > 0 else 1.0

    # Duración revisada
    revised_duration = total_months / spi
    months_remaining = revised_duration - n_done
    delay_months = max(0.0, months_remaining - (total_months - n_done))

    return {
        "planned_duration": total_months,
        "revised_duration": round(revised_duration, 1),
        "months_elapsed": n_done,
        "months_remaining_revised": round(months_remaining, 1),
        "delay_months": round(delay_months, 1),
        "on_time_probability": round(min(100, max(0, spi * 100)), 1),
    }


# ── Modelo de riesgo compuesto ─────────────────────────────────────────────────

def risk_score(snapshots) -> Dict:
    """
    Score de riesgo 0-100 basado en tendencias de CPI, SPI, QPI y PPI.
    0 = sin riesgo, 100 = riesgo máximo.
    """
    if len(snapshots) < 3:
        return {"score": 50, "level": "🟡 Insuficientes datos", "factors": []}

    cpi_series = [s.cpi for s in snapshots]
    spi_series = [s.spi for s in snapshots]
    qpi_series = [s.qpi for s in snapshots]
    ppi_series = [s.ppi for s in snapshots]

    def penalty(series: List[float], threshold: float) -> float:
        """Penalización 0-25 basada en valores bajo umbral y tendencia."""
        current = series[-1]
        below_thresh = max(0, threshold - current) / threshold * 25
        # tendencia negativa
        slope, _, _ = linear_regression(list(range(len(series))), series)
        trend_pen = max(0, -slope * 50)
        return min(25, below_thresh + trend_pen)

    p_cpi = penalty(cpi_series, 1.0)
    p_spi = penalty(spi_series, 1.0)
    p_qpi = penalty(qpi_series, 0.95)
    p_ppi = penalty(ppi_series, 0.90)

    score = round(p_cpi + p_spi + p_qpi + p_ppi, 1)

    if score < 20:
        level = "🟢 Bajo riesgo"
    elif score < 45:
        level = "🟡 Riesgo moderado"
    else:
        level = "🔴 Alto riesgo"

    factors = []
    if p_cpi > 10:
        factors.append(f"Eficiencia de costo crítica (CPI={cpi_series[-1]:.2f})")
    if p_spi > 10:
        factors.append(f"Retraso de cronograma (SPI={spi_series[-1]:.2f})")
    if p_qpi > 8:
        factors.append(f"Calidad deficiente (QPI={qpi_series[-1]:.2f})")
    if p_ppi > 8:
        factors.append(f"Baja productividad (PPI={ppi_series[-1]:.2f})")

    return {"score": score, "level": level, "factors": factors}


# ── Forecast de KPIs (próximos 3 períodos) ────────────────────────────────────

def forecast_kpis(snapshots, n_ahead: int = 3) -> Dict[str, List[float]]:
    """
    Proyecta CPI, SPI, QPI, PPI para los próximos n_ahead períodos.
    """
    if len(snapshots) < 3:
        return {}

    forecasts = {}
    x = list(range(len(snapshots)))
    x_future = [len(snapshots) + i for i in range(n_ahead)]

    for kpi in ["cpi", "spi", "qpi", "ppi"]:
        series = [getattr(s, kpi) for s in snapshots]
        slope, intercept, r2 = linear_regression(x, series)
        preds = predict_values(slope, intercept, x_future)
        # Clamp to reasonable bounds
        preds = [round(max(0.5, min(1.5, p)), 3) for p in preds]
        forecasts[kpi] = preds
        forecasts[f"{kpi}_r2"] = round(r2, 3)

    return forecasts


# ── Análisis de correlación entre KPIs ────────────────────────────────────────

def pearson_correlation(x: List[float], y: List[float]) -> float:
    """Coeficiente de correlación de Pearson."""
    n = len(x)
    if n < 2:
        return 0.0
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((xi - mx)*(yi - my) for xi, yi in zip(x, y))
    dx  = math.sqrt(sum((xi - mx)**2 for xi in x))
    dy  = math.sqrt(sum((yi - my)**2 for yi in y))
    if dx == 0 or dy == 0:
        return 0.0
    return round(num / (dx * dy), 3)


def kpi_correlation_matrix(snapshots) -> Dict[str, Dict[str, float]]:
    """Matriz de correlación entre CPI, SPI, QPI, PPI."""
    kpis = ["cpi", "spi", "qpi", "ppi"]
    series = {k: [getattr(s, k) for s in snapshots] for k in kpis}
    matrix = {}
    for k1 in kpis:
        matrix[k1] = {}
        for k2 in kpis:
            matrix[k1][k2] = pearson_correlation(series[k1], series[k2])
    return matrix
