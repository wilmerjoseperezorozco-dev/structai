"""Pruebas del harness de pronóstico del acero (#262), sin Chronos. Desde scripts/precios: python -m pytest test_pronostico_acero.py -q"""
from __future__ import annotations

import numpy as np
import pytest

import pronostico_acero as pa


def test_ventana_es_copia_y_no_incluye_el_futuro():
    y = np.arange(10.0)
    v = pa.ventana(y, 4)
    assert list(v) == [0, 1, 2, 3, 4]
    v[0] = 99
    assert y[0] == 0


def test_estacional_toma_el_mismo_mes_del_año_anterior():
    y = np.arange(24.0)                      # último dato: índice 23
    assert pa.estacional(y, 3) == y[23 - 12 + 3]
    assert pa.estacional(y, 12) == y[23]
    assert pa.caminata(y, 6) == 23
    assert pa.deriva(y, 6) == pytest.approx(23 + 6)


def test_mes_anterior_y_rezago_de_exogenas():
    assert pa.mes_anterior("2021-01", 1) == "2020-12"
    assert pa.mes_anterior("2021-03", 14) == "2020-01"
    s = {"2020-10": 1.0, "2020-11": np.e, "2020-12": np.e ** 3}
    d = pa.dlog_rezagada(s, ["2021-01"], 1)          # Δlog en 2020-12 = 3 − 1
    assert d[0] == pytest.approx(2.0)
    with pytest.raises(KeyError):
        pa.dlog_rezagada(s, ["2021-01"], 3)          # falta el dato: no se rellena


def test_winkler_penaliza_fuera_del_intervalo():
    assert pa.winkler(5, 4, 6) == 2
    assert pa.winkler(7, 4, 6) == pytest.approx(2 + 2 / 0.2 * 1)


def test_dm_errores_iguales_no_rechaza_y_mejor_si():
    rng = np.random.default_rng(262)
    e = rng.normal(size=40)
    _, p = pa.diebold_mariano(e, e, 6)
    assert p == 0.5
    _, p = pa.diebold_mariano(e * 0.3, e, 6)
    assert p < 0.01
    _, p = pa.diebold_mariano(e, e * 0.3, 6)
    assert p > 0.99


def test_holm_paso_a_paso():
    r = pa.holm({"a": 0.01, "b": 0.02, "c": 0.04})   # umbrales 0,0167 / 0,025 / 0,05
    assert r == {"a": True, "b": True, "c": True}
    r = pa.holm({"a": 0.01, "b": 0.03, "c": 0.04})
    assert r == {"a": True, "b": False, "c": False}  # al fallar b se detiene


def test_intervalo_empirico_contiene_al_punto():
    y = np.cumsum(np.random.default_rng(1).normal(0, 0.01, 40))
    p, lo, hi = pa.simple(pa.caminata)(y, 3)
    assert lo <= p <= hi


def test_evaluar_de_punta_a_punta_sin_chronos():
    rng = np.random.default_rng(7)
    def serie(ini, n, desde):
        a, m = map(int, desde.split("-"))
        v, out = 100.0, {}
        for k in range(n):
            t = a * 12 + m - 1 + k
            v *= 1 + rng.normal(0.005, 0.02)
            out[f"{t // 12}-{t % 12 + 1:02d}"] = v
        return out
    s = {"icociv_acero_corrugado": serie(100, 50, "2021-01"),
         "iccp_aceros_elementos_metalicos": serie(100, 120, "2010-01"),
         "trm_promedio_mensual": serie(100, 80, "2019-01"), "bls_wpu1012": serie(100, 80, "2019-01")}
    res = pa.evaluar(s, usar_chronos=False)
    n6 = sum(1 for f in res["filas"] if f["h"] == 6 and f["modelo"] == "M0")
    assert n6 == 50 - 6 - (pa.ENTRENAMIENTO_INICIAL - 1)
    resumen, texto = pa.resumir(res)
    assert "H4** no evaluada" in texto and "M5" in texto
