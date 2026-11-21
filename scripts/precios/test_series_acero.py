"""Pruebas del lector de series del acero (#262) con hojas sintéticas; no necesita los archivos del DANE.
Ejecutar desde scripts/precios: python -m pytest test_series_acero.py -q"""
from __future__ import annotations

import json

import pytest

import series_acero as sa


def _hoja_iccp():
    f = [["ICCP - Índices serie empalme"], ["Índices 2021"], ["Meses"] + [m.capitalize() for m in sa.MESES],
         ["   Aceros y elementos metálicos"] + [100 + k for k in range(12)], [],
         ["Índices 2000"], ["Meses"] + [m.capitalize() for m in sa.MESES],
         ["   Aceros y elementos metálicos"] + [50.0] * 11 + [None],
         ["   Acero estructural y cables de acero"] + [60.0] * 12]
    return f


def test_bloques_iccp_lee_el_año_de_cada_bloque_sin_suponer_orden():
    s = sa.bloques_iccp(_hoja_iccp(), sa.GRUPO_ICCP)
    assert s["2021-01"] == 100 and s["2021-12"] == 111
    assert s["2000-01"] == 50 and "2000-12" not in s       # celda vacía no se inventa
    assert len(s) == 23


def _hoja_icociv():
    meses = [m.capitalize() for m in sa.MESES]
    return [["A16.4 otra sección"], ["Materiales", 51.3, 101.0],
            ["A16.5 ICOCIV - Serie histórica índice por grupos de costos e insumos"],
            ["Grupos de costos", "Código", "Insumos", "Ponderación (%)", 2021] + [None] * 11 + [2022],
            [None] * 4 + meses + ["Enero"],
            [None] * 4 + ["Índice"] * 13,
            ["Materiales", "105", "Alambre", 0.14] + [101.0] * 13,
            ["Materiales", "106", "Acero corrugado", 2.297] + [105.0 + k for k in range(13)],
            ["A16.6 siguiente"], ["Materiales", "106", "Acero corrugado", 9.9] + [1.0] * 13]


def test_insumo_icociv_hereda_el_año_y_no_cruza_de_sección():
    s = sa.insumo_icociv(_hoja_icociv(), "Acero corrugado")
    assert s["2021-01"] == 105.0 and s["2021-12"] == 116.0 and s["2022-01"] == 117.0
    assert len(s) == 13


def test_insumo_icociv_falla_si_no_existe():
    with pytest.raises(KeyError):
        sa.insumo_icociv(_hoja_icociv(), "Titanio")


def test_trm_pondera_por_días_de_vigencia(tmp_path):
    p = tmp_path / "trm.csv"
    p.write_text('"valor","unidad","vigenciadesde","vigenciahasta"\n'
                 '"100","COP","2024-01-01T00:00:00.000","2024-01-30T00:00:00.000"\n'
                 '"400","COP","2024-01-31T00:00:00.000","2024-02-02T00:00:00.000"\n', encoding="utf-8")
    s = sa.trm_mensual(p)
    assert s["2024-01"] == round((30 * 100 + 400) / 31, 4)   # el 31 vale 400; los otros 30 días, 100
    assert "2024-02" not in s             # febrero solo tiene 2 días cubiertos: mes incompleto, se descarta


def test_bls_ignora_el_promedio_anual_m13(tmp_path):
    p = tmp_path / "bls_wpu1012_2020.json"
    p.write_text(json.dumps({"Results": {"series": [{"seriesID": "WPU1012", "data": [
        {"year": "2021", "period": "M02", "value": "410.5"}, {"year": "2021", "period": "M13", "value": "999"},
        {"year": "2021", "period": "M01", "value": "400"}]}]}}), encoding="utf-8")
    s = sa.bls([p])
    assert list(s) == ["2021-01", "2021-02"] and s["2021-02"] == 410.5


def test_traslape_elasticidad_de_un_grupo_que_amortigua():
    pasos = [0.03, -0.01, 0.05, 0.02, -0.03, 0.04, 0.0, 0.06, -0.02, 0.01, 0.03, -0.04]
    insumo, v = {}, 100.0
    for m, g in enumerate(pasos, 1):
        v *= 1 + g
        insumo[f"2021-{m:02d}"] = v
    grupo, w = {}, 100.0
    for m, g in enumerate(pasos, 1):
        w *= 1 + 0.5 * g                    # el grupo transmite la mitad de cada variación
        grupo[f"2021-{m:02d}"] = w
    t = sa.traslape(grupo, insumo)
    assert t["meses"] == 12 and t["corr_variacion"] > 0.99
    assert 0.4 < t["elasticidad"] < 0.6
    assert t["var_total_grupo"] < t["var_total_insumo"]


def test_traslape_exige_meses_comunes():
    with pytest.raises(ValueError):
        sa.traslape({"2000-01": 1.0}, {"2021-01": 1.0})
