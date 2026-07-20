"""Tests para Motor Gerencia — Earned Value Management (PMBOK) + ML predictivo.

Mismo patrón que los otros 3 motores: cada aserción recalcula el valor
esperado con la fórmula documentada en el módulo, no con un número supuesto.
"""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from src.models import Snapshot, Project
from src.evm import (
    KPI_META, classify_kpi, composite_score, trend_direction, forecast_eac, cross_project_summary,
)
from src.ml_engine import (
    linear_regression, predict_values, detect_anomalies, predict_completion_date,
    risk_score, forecast_kpis, pearson_correlation, kpi_correlation_matrix,
)
from src.schemas import SnapshotInput, ProjectInput, SnapshotKPIRequest, PortfolioRequest, ProjectSeriesRequest
from src import calcular_snapshot, analizar_portafolio, calcular_riesgo, calcular_forecast_kpis, \
    calcular_fecha_termino, detectar_anomalias, calcular_correlacion


def _snapshot(period="P1", pv=100.0, ev=90.0, ac=95.0, quality_pct=92.0,
              resources_planned=10.0, resources_actual=11.0, incidents=1, bac=1000.0, eac_method="cpi"):
    return Snapshot(period=period, pv=pv, ev=ev, ac=ac, quality_pct=quality_pct,
                     resources_planned=resources_planned, resources_actual=resources_actual,
                     incidents=incidents, bac=bac, eac_method=eac_method)


# ─── models.py — Snapshot ─────────────────────────────────────────────────────

def test_snapshot_cpi_spi_formulas():
    s = _snapshot(pv=100.0, ev=90.0, ac=95.0)
    assert s.cpi == pytest.approx(90.0 / 95.0)
    assert s.spi == pytest.approx(90.0 / 100.0)


def test_snapshot_cpi_ac_cero_no_divide_por_cero():
    s = _snapshot(ac=0.0)
    assert s.cpi == 0.0


def test_snapshot_ppi_formula():
    s = _snapshot(ev=90.0, ac=95.0, resources_planned=10.0, resources_actual=12.0)
    base = 90.0 / 95.0
    factor = 10.0 / 12.0
    assert s.ppi == pytest.approx(base * factor)


def test_snapshot_sv_cv_tcpi():
    s = _snapshot(pv=100.0, ev=90.0, ac=95.0, bac=1000.0)
    assert s.sv == pytest.approx(90.0 - 100.0)
    assert s.cv == pytest.approx(90.0 - 95.0)
    assert s.tcpi == pytest.approx((1000.0 - 90.0) / (1000.0 - 95.0))


def test_snapshot_eac_metodos():
    s_cpi = _snapshot(bac=1000.0, ev=90.0, ac=95.0, eac_method="cpi")
    s_bac = _snapshot(bac=1000.0, ev=90.0, ac=95.0, eac_method="bac")
    assert s_cpi.eac == pytest.approx(1000.0 / s_cpi.cpi)
    assert s_bac.eac == pytest.approx(95.0 + (1000.0 - 90.0))


def test_snapshot_percent_complete():
    s = _snapshot(ev=250.0, bac=1000.0)
    assert s.percent_complete == pytest.approx(25.0)


def test_snapshot_to_dict_incluye_kpis_redondeados():
    s = _snapshot()
    d = s.to_dict()
    assert d["cpi"] == round(s.cpi, 4)
    assert "eac" in d and "percent_complete" in d


# ─── models.py — Project ──────────────────────────────────────────────────────

def test_project_sin_snapshots_estado_sin_datos():
    p = Project(id="P1", name="Proyecto Vacío", bac=1000.0)
    assert p.latest is None
    assert p.overall_status == "Sin datos"


def test_project_estado_critico_cpi_bajo():
    p = Project(id="P1", name="Proyecto Crítico", bac=1000.0)
    p.snapshots.append(_snapshot(pv=100.0, ev=80.0, ac=100.0, bac=1000.0))   # cpi=0.8 < 0.9
    assert p.overall_status == "🔴 Crítico"


def test_project_estado_en_control():
    p = Project(id="P1", name="Proyecto Sano", bac=1000.0)
    p.snapshots.append(_snapshot(pv=100.0, ev=105.0, ac=100.0, bac=1000.0))   # cpi=1.05, spi=1.05
    assert p.overall_status == "🟢 En control"


# ─── evm.py — classify_kpi / composite_score / trend_direction ───────────────

def test_classify_kpi_zonas_reales_de_kpi_meta():
    assert classify_kpi("cpi", 1.0) == "🟢"    # KPI_META["cpi"]["good"] = (1.0, 99)
    assert classify_kpi("cpi", 0.95) == "🟡"   # alert = (0.9, 0.999)
    assert classify_kpi("cpi", 0.5) == "🔴"
    assert classify_kpi("kpi_inexistente", 1.0) == "⚪"


def test_classify_kpi_tcpi_higher_is_worse():
    # tcpi: good=(0,1.05), alert=(1.051,1.10), critical=(1.101,99)
    assert classify_kpi("tcpi", 1.0) == "🟢"
    assert classify_kpi("tcpi", 1.08) == "🟡"
    assert classify_kpi("tcpi", 1.20) == "🔴"


def test_composite_score_formula():
    cpi, spi, qpi, ppi = 1.0, 0.95, 1.0, 0.90
    weights = {"cpi": 0.30, "spi": 0.25, "qpi": 0.25, "ppi": 0.20}
    values = {"cpi": cpi, "spi": spi, "qpi": qpi, "ppi": ppi}
    esperado = round(sum(weights[k] * min(v, 1.2) / 1.2 * 100 for k, v in values.items()), 1)
    assert composite_score(cpi, spi, qpi, ppi) == esperado


def test_trend_direction_requiere_minimo_3_puntos():
    assert trend_direction([1.0, 1.0]) == "→"


def test_trend_direction_mejorando_y_deteriorando():
    assert "Mejorando" in trend_direction([0.8, 0.9, 1.0])
    assert "Deteriorando" in trend_direction([1.0, 0.9, 0.8])
    assert "Estable" in trend_direction([1.0, 1.0, 1.0])


def test_forecast_eac_tres_metodos():
    bac, ev, ac, cpi = 1000.0, 400.0, 420.0, 400.0 / 420.0
    assert forecast_eac(bac, ev, ac, cpi, method="cpi") == pytest.approx(bac / cpi)
    assert forecast_eac(bac, ev, ac, cpi, method="bac") == pytest.approx(ac + (bac - ev))
    assert forecast_eac(bac, ev, ac, cpi, method="metodo_desconocido") == bac


# ─── evm.py — cross_project_summary ──────────────────────────────────────────

def _proyecto(id_, name, cpi_target_ev, cpi_target_ac, bac=1000.0):
    p = Project(id=id_, name=name, bac=bac)
    p.snapshots.append(_snapshot(pv=100.0, ev=cpi_target_ev, ac=cpi_target_ac, bac=bac))
    return p


def test_cross_project_summary_rankings_y_alertas():
    bueno = _proyecto("P1", "Obra Sana", cpi_target_ev=110.0, cpi_target_ac=100.0)     # cpi=1.10
    critico = _proyecto("P2", "Obra Crítica", cpi_target_ev=70.0, cpi_target_ac=100.0)  # cpi=0.70

    resultado = cross_project_summary([bueno, critico])
    filas = {r["id"]: r for r in resultado["rows"]}

    assert filas["P1"]["rank_cpi"] == 1
    assert filas["P2"]["rank_cpi"] == 2
    assert resultado["portfolio"]["n_projects"] == 2
    assert any(a["project"] == "Obra Crítica" and "CPI" in a["message"] for a in resultado["alerts"])


def test_cross_project_summary_ignora_proyectos_sin_snapshots():
    con_datos = _proyecto("P1", "Con datos", cpi_target_ev=100.0, cpi_target_ac=100.0)
    sin_datos = Project(id="P2", name="Sin datos", bac=1000.0)
    resultado = cross_project_summary([con_datos, sin_datos])
    assert len(resultado["rows"]) == 1
    assert resultado["rows"][0]["id"] == "P1"


def test_cross_project_summary_vacio_retorna_dict_vacio():
    assert cross_project_summary([]) == {}


# ─── ml_engine.py — regresión, anomalías, riesgo, forecast, correlación ──────

def test_linear_regression_linea_perfecta():
    x = [0.0, 1.0, 2.0, 3.0]
    y = [1.0, 3.0, 5.0, 7.0]   # y = 2x + 1, exacto
    slope, intercept, r2 = linear_regression(x, y)
    assert slope == pytest.approx(2.0)
    assert intercept == pytest.approx(1.0)
    assert r2 == pytest.approx(1.0)


def test_linear_regression_menos_de_2_puntos():
    slope, intercept, r2 = linear_regression([1.0], [5.0])
    assert slope == 0.0
    assert intercept == 5.0
    assert r2 == 0.0


def test_predict_values_aplica_recta():
    assert predict_values(slope=2.0, intercept=1.0, future_x=[4.0, 5.0]) == [9.0, 11.0]


def test_detect_anomalies_serie_corta_no_detecta():
    assert detect_anomalies([1.0, 2.0]) == []


def test_detect_anomalies_detecta_outlier_real():
    serie = [1.0, 1.05, 0.95, 1.02, 1.0, 5.0]   # 5.0 es un outlier claro
    idx = detect_anomalies(serie, threshold=2.0)
    assert 5 in idx


def test_predict_completion_date_formula():
    s1 = _snapshot(period="P1", pv=100.0, ev=80.0, bac=1000.0)   # spi = 0.8
    resultado = predict_completion_date([s1], total_months=10)
    revised = 10 / 0.8
    assert resultado["revised_duration"] == pytest.approx(round(revised, 1))
    assert resultado["on_time_probability"] == pytest.approx(80.0)


def test_predict_completion_date_sin_snapshots():
    assert predict_completion_date([], total_months=10) == {}


def test_risk_score_insuficientes_datos():
    r = risk_score([_snapshot(), _snapshot()])   # solo 2, se requieren >= 3
    assert r["score"] == 50
    assert "Insuficientes" in r["level"]


def test_risk_score_tendencia_negativa_sube_riesgo():
    # CPI/SPI/QPI/PPI cayendo consistentemente en 4 períodos
    snaps = [
        _snapshot(period=f"P{i}", pv=100.0, ev=100.0 - i * 10, ac=100.0, quality_pct=95 - i * 5,
                  resources_planned=10.0, resources_actual=10.0 + i, bac=1000.0)
        for i in range(4)
    ]
    r = risk_score(snaps)
    assert r["score"] > 20   # con caída consistente, no debería quedar en "bajo riesgo"


def test_forecast_kpis_menos_de_3_snapshots_vacio():
    assert forecast_kpis([_snapshot(), _snapshot()]) == {}


def test_forecast_kpis_clamp_a_rango_0_5_1_5():
    snaps = [_snapshot(period=f"P{i}", pv=100.0, ev=100.0, ac=100.0, bac=1000.0) for i in range(4)]
    forecasts = forecast_kpis(snaps, n_ahead=2)
    for kpi in ["cpi", "spi", "qpi", "ppi"]:
        for v in forecasts[kpi]:
            assert 0.5 <= v <= 1.5


def test_pearson_correlation_perfecta_positiva_y_negativa():
    x = [1.0, 2.0, 3.0, 4.0]
    assert pearson_correlation(x, [2.0, 4.0, 6.0, 8.0]) == pytest.approx(1.0)
    assert pearson_correlation(x, [8.0, 6.0, 4.0, 2.0]) == pytest.approx(-1.0)


def test_pearson_correlation_varianza_cero_retorna_cero():
    assert pearson_correlation([1.0, 2.0, 3.0], [5.0, 5.0, 5.0]) == 0.0


def test_kpi_correlation_matrix_diagonal_autocorrelacion():
    snaps = [
        _snapshot(period=f"P{i}", pv=100.0, ev=90.0 + i * 3, ac=95.0, quality_pct=90 + i,
                  resources_planned=10.0, resources_actual=10.0, bac=1000.0)
        for i in range(4)
    ]
    matrix = kpi_correlation_matrix(snaps)
    # cpi varía con i (ev cambia, ac fijo) -> autocorrelación real = 1.0
    assert matrix["cpi"]["cpi"] == pytest.approx(1.0)


# ─── src/__init__.py — capa pública que consume apps/api/routers/gerencia.py ─

def test_wrapper_calcular_snapshot():
    req = SnapshotKPIRequest(bac=1000.0, snapshot=SnapshotInput(
        period="Ene", pv=100.0, ev=90.0, ac=95.0, quality_pct=92.0,
        resources_planned=10.0, resources_actual=11.0,
    ))
    r = calcular_snapshot(req)
    assert r["cpi"] == pytest.approx(round(90.0 / 95.0, 4))
    assert "clasificacion" in r and "score_compuesto" in r


def _project_input(id_, ev):
    return ProjectInput(id=id_, name=f"Obra {id_}", bac=1000.0, snapshots=[
        SnapshotInput(period="P1", pv=100.0, ev=ev, ac=100.0, quality_pct=90.0,
                      resources_planned=10.0, resources_actual=10.0),
    ])


def test_wrapper_analizar_portafolio():
    req = PortfolioRequest(projects=[_project_input("A", 110.0), _project_input("B", 70.0)])
    r = analizar_portafolio(req)
    assert r["portfolio"]["n_projects"] == 2


def _project_input_serie(n=4):
    snaps = [
        SnapshotInput(period=f"P{i}", pv=100.0, ev=95.0 + i, ac=100.0, quality_pct=90.0,
                      resources_planned=10.0, resources_actual=10.0)
        for i in range(n)
    ]
    return ProjectInput(id="X", name="Obra X", bac=1000.0, duration_months=12, snapshots=snaps)


def test_wrapper_calcular_riesgo_forecast_fecha_anomalias_correlacion():
    req = ProjectSeriesRequest(project=_project_input_serie(), n_ahead=2, kpi="cpi", anomaly_threshold=2.0)

    riesgo = calcular_riesgo(req)
    assert "score" in riesgo

    forecast = calcular_forecast_kpis(req)
    assert "cpi" in forecast

    fecha = calcular_fecha_termino(req)
    assert "revised_duration" in fecha

    anomalias = detectar_anomalias(req)
    assert anomalias["kpi"] == "cpi"

    correlacion = calcular_correlacion(req)
    assert "cpi" in correlacion


def test_wrapper_detectar_anomalias_kpi_invalido():
    req = ProjectSeriesRequest(project=_project_input_serie(), kpi="kpi_que_no_existe")
    r = detectar_anomalias(req)
    assert "error" in r


def test_wrapper_calcular_correlacion_menos_de_3_snapshots():
    req = ProjectSeriesRequest(project=_project_input_serie(n=2))
    r = calcular_correlacion(req)
    assert "error" in r
