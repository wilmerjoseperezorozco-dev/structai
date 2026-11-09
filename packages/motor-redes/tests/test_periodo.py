"""Periodo extendido con tanques de nivel variable (Euler explícito al inicio de cada paso, como EPANET).
Referencias independientes: vaciado a demanda constante (lineal exacto), llenado desde embalse contra solve_ivp, balance de volumen."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from scipy.integrate import solve_ivp

from src.periodo import simular_periodo

N = 1.852


def _r(L, D, C):
    return 10.67 * L / (C ** N * D ** 4.871)


def _tanque(area=100.0, nivel=5.0, nmin=0.5, nmax=10.0, fondo=40.0, id="T"):
    return dict(id=id, cota_fondo_m=fondo, area_m2=area, nivel_inicial_m=nivel, nivel_min_m=nmin, nivel_max_m=nmax)


def _red_vaciado(demanda=0.01):
    nodos = [dict(id="T", cota_m=40.0, demanda_m3s=0.0, carga_fija_m=None), dict(id="N", cota_m=30.0, demanda_m3s=demanda, carga_fija_m=None)]
    tramos = [dict(id="p", desde="T", hasta="N", longitud_m=500.0, diametro_m=0.2, c_hw=130.0)]
    return nodos, tramos


def test_vaciado_a_demanda_constante_es_lineal_y_exacto():
    nodos, tramos = _red_vaciado(0.01)
    s = simular_periodo(nodos, tramos, tanques=[_tanque()], paso_s=600.0, n_pasos=6)
    for k, paso in enumerate(s["pasos"]):
        assert paso["tanques"]["T"]["nivel_m"] == pytest.approx(5.0 - 0.01 * 600.0 * k / 100.0, rel=1e-9)
    assert s["completo"] is True and len(s["pasos"]) == 7        # estados en t = 0, dt, ..., 6·dt


def test_patron_de_demanda_multiplica_la_demanda_y_se_repite():
    nodos, tramos = _red_vaciado(0.01)
    s = simular_periodo(nodos, tramos, tanques=[_tanque()], paso_s=600.0, n_pasos=4, patron_demanda=[1.0, 3.0])
    n = [p["tanques"]["T"]["nivel_m"] for p in s["pasos"]]
    assert n[1] == pytest.approx(5.0 - 0.01 * 1.0 * 600.0 / 100.0, rel=1e-9)
    assert n[2] == pytest.approx(n[1] - 0.01 * 3.0 * 600.0 / 100.0, rel=1e-9)
    assert n[3] == pytest.approx(n[2] - 0.01 * 1.0 * 600.0 / 100.0, rel=1e-9)     # el patrón se repite


def test_llenado_desde_embalse_converge_a_la_edo_de_referencia():
    nodos = [dict(id="R", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=60.0), dict(id="T", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None)]
    tramos = [dict(id="p", desde="R", hasta="T", longitud_m=800.0, diametro_m=0.2, c_hw=130.0)]
    area, h0, fondo, dt, n = 50.0, 2.0, 30.0, 5.0, 240
    s = simular_periodo(nodos, tramos, tanques=[_tanque(area, h0, 0.1, 40.0, fondo)], paso_s=dt, n_pasos=n)
    r = _r(800.0, 0.2, 130.0)
    ref = solve_ivp(lambda t, h: [(max(60.0 - fondo - h[0], 0.0) / r) ** (1 / N) / area], [0, dt * n], [h0], rtol=1e-10, atol=1e-12)
    assert s["pasos"][-1]["tanques"]["T"]["nivel_m"] == pytest.approx(ref.y[0, -1], rel=2e-3)


def test_balance_de_volumen_entre_demanda_y_tanque():
    nodos, tramos = _red_vaciado(0.02)
    s = simular_periodo(nodos, tramos, tanques=[_tanque(area=80.0, nivel=8.0)], paso_s=300.0, n_pasos=10, patron_demanda=[0.5, 1.5, 1.0])
    perdido = (8.0 - s["pasos"][-1]["tanques"]["T"]["nivel_m"]) * 80.0
    entregado = sum(0.02 * f * 300.0 for f in [0.5, 1.5, 1.0, 0.5, 1.5, 1.0, 0.5, 1.5, 1.0, 0.5])
    assert perdido == pytest.approx(entregado, rel=1e-9)


def test_el_tanque_que_se_vacia_detiene_la_simulacion_con_un_evento():
    nodos, tramos = _red_vaciado(0.05)
    s = simular_periodo(nodos, tramos, tanques=[_tanque(area=10.0, nivel=1.0, nmin=0.5)], paso_s=60.0, n_pasos=20)
    assert s["completo"] is False and any("vacía" in e or "mínimo" in e for e in s["eventos"])
    assert s["pasos"][-1]["tanques"]["T"]["nivel_m"] >= 0.5 - 1e-9 or len(s["pasos"]) < 21


def test_el_tanque_que_se_llena_detiene_la_simulacion():
    nodos = [dict(id="R", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=80.0), dict(id="T", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None)]
    tramos = [dict(id="p", desde="R", hasta="T", longitud_m=100.0, diametro_m=0.3, c_hw=130.0)]
    s = simular_periodo(nodos, tramos, tanques=[_tanque(area=5.0, nivel=9.0, nmax=10.0, fondo=30.0)], paso_s=60.0, n_pasos=30)
    assert s["completo"] is False and any("máximo" in e or "llena" in e for e in s["eventos"])


@pytest.mark.parametrize("cambio", [dict(area_m2=0.0), dict(area_m2=float("nan")), dict(nivel_inicial_m=-1.0), dict(nivel_min_m=6.0),
                                    dict(nivel_max_m=4.0), dict(id="X")])
def test_tanques_invalidos_se_rechazan(cambio):
    nodos, tramos = _red_vaciado()
    with pytest.raises(ValueError):
        simular_periodo(nodos, tramos, tanques=[{**_tanque(), **cambio}], paso_s=60.0, n_pasos=2)


@pytest.mark.parametrize("kw", [dict(paso_s=0.0), dict(paso_s=-1.0), dict(n_pasos=0), dict(n_pasos=100000), dict(patron_demanda=[]),
                                dict(patron_demanda=[-1.0]), dict(patron_demanda=[float("nan")])])
def test_parametros_de_tiempo_invalidos_se_rechazan(kw):
    nodos, tramos = _red_vaciado()
    base = dict(paso_s=60.0, n_pasos=2)
    base.update(kw)
    with pytest.raises(ValueError):
        simular_periodo(nodos, tramos, tanques=[_tanque()], **base)


def test_tanque_sobre_un_nudo_con_demanda_o_carga_fija_se_rechaza():
    nodos, tramos = _red_vaciado()
    nodos[0]["demanda_m3s"] = 0.01
    with pytest.raises(ValueError, match="tanque"):
        simular_periodo(nodos, tramos, tanques=[_tanque()], paso_s=60.0, n_pasos=2)
