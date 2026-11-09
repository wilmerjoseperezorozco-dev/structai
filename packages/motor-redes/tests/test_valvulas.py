"""Válvula de pérdida local h = K·Q·|Q|/(2g·A²). Referencia independiente: raíz escalar (brentq) del sistema en serie."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from scipy.optimize import brentq

from src.gradiente import resolver_red

G = 9.80665


def _red(k=20.0, dv=0.2):
    nodos = [dict(id="R", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=50.0), dict(id="V", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None),
             dict(id="S", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=20.0)]
    tramos = [dict(id="a", desde="R", hasta="V", longitud_m=500.0, diametro_m=0.2, c_hw=130.0),
              dict(id="b", desde="V", hasta="S", longitud_m=300.0, diametro_m=0.2, c_hw=130.0)]
    return nodos, tramos


def _con_valvula(k, dv=0.2):
    nodos = [dict(id="R", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=50.0), dict(id="V1", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None),
             dict(id="V2", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None), dict(id="S", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=20.0)]
    tramos = [dict(id="a", desde="R", hasta="V1", longitud_m=500.0, diametro_m=0.2, c_hw=130.0),
              dict(id="b", desde="V2", hasta="S", longitud_m=300.0, diametro_m=0.2, c_hw=130.0)]
    valvulas = [dict(id="v", desde="V1", hasta="V2", diametro_m=dv, k=k)]
    return nodos, tramos, valvulas


def test_valvula_en_serie_coincide_con_la_raiz_escalar():
    k, dv = 20.0, 0.2
    nodos, tramos, valvulas = _con_valvula(k, dv)
    red = resolver_red(nodos, tramos, valvulas=valvulas)
    r = lambda L: 10.67 * L / (130.0 ** 1.852 * 0.2 ** 4.871)
    area = math.pi * dv ** 2 / 4
    f = lambda q: r(500.0) * q ** 1.852 + k * q ** 2 / (2 * G * area ** 2) + r(300.0) * q ** 1.852 - 30.0
    q = brentq(f, 0.0, 1.0)
    assert red["tramos"]["a"]["caudal_m3s"] == pytest.approx(q, rel=1e-8)
    assert red["valvulas"]["v"]["perdida_m"] == pytest.approx(k * q ** 2 / (2 * G * area ** 2), rel=1e-8)


def test_mayor_k_reduce_el_caudal():
    qs = []
    for k in (1.0, 20.0, 400.0):
        nodos, tramos, valvulas = _con_valvula(k)
        qs.append(resolver_red(nodos, tramos, valvulas=valvulas)["tramos"]["a"]["caudal_m3s"])
    assert qs[0] > qs[1] > qs[2]


def test_diametro_menor_de_la_valvula_con_igual_k_pierde_mas_carga():
    p = []
    for dv in (0.3, 0.2, 0.1):
        nodos, tramos, valvulas = _con_valvula(10.0, dv)
        p.append(resolver_red(nodos, tramos, valvulas=valvulas)["valvulas"]["v"]["perdida_m"])
    assert p[0] < p[1] < p[2]


@pytest.mark.parametrize("cambio", [dict(k=0.0), dict(k=-1.0), dict(k=float("nan")), dict(diametro_m=0.0), dict(desde="Z"), dict(hasta="V1")])
def test_valvulas_invalidas_se_rechazan(cambio):
    nodos, tramos, valvulas = _con_valvula(10.0)
    valvulas[0].update(cambio)
    with pytest.raises(ValueError):
        resolver_red(nodos, tramos, valvulas=valvulas)


def test_id_de_valvula_repetido_con_un_tramo_se_rechaza():
    nodos, tramos, valvulas = _con_valvula(10.0)
    valvulas[0]["id"] = "a"
    with pytest.raises(ValueError, match="duplicad"):
        resolver_red(nodos, tramos, valvulas=valvulas)
