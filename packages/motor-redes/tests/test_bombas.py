"""Bomba con curva H-Q parabólica H = h0 − a·Q² como elemento de la red. Referencia independiente: raíz escalar con brentq
de la intersección curva de la bomba / curva del sistema."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from scipy.optimize import brentq

from src.gradiente import resolver_red

N = 1.852


def _r(L, D, C):
    return 10.67 * L / (C ** N * D ** 4.871)


def _red(h0=60.0, a=2000.0, demanda=None, z_alto=30.0, **kw):
    """Embalse bajo (carga 10) → bomba → tubería → nudo alto con demanda; si demanda es None el nudo no extrae (cierra)."""
    nodos = [dict(id="R", cota_m=10.0, demanda_m3s=0.0, carga_fija_m=10.0),
             dict(id="B", cota_m=10.0, demanda_m3s=0.0, carga_fija_m=None),
             dict(id="N", cota_m=z_alto, demanda_m3s=0.0 if demanda is None else demanda, carga_fija_m=None)]
    tramos = [dict(id="t", desde="B", hasta="N", longitud_m=800.0, diametro_m=0.25, c_hw=120.0)]
    bombas = [dict(id="bomba", desde="R", hasta="B", h0_m=h0, a_s2m5=a, **kw)]
    return nodos, tramos, bombas


def test_punto_de_operacion_coincide_con_la_interseccion_curva_sistema():
    h0, a, zq = 60.0, 2000.0, 30.0
    nodos, tramos, bombas = _red(h0, a, demanda=0.05)
    nodos[2]["demanda_m3s"] = 0.0
    nodos[2]["carga_fija_m"] = zq + 0.0   # tanque elevado de carga constante: bomba impulsa contra carga estática fija
    red = resolver_red(nodos, tramos, bombas=bombas)
    r = _r(800.0, 0.25, 120.0)
    q = brentq(lambda x: (10.0 + h0 - a * x ** 2) - zq - r * x ** N, 0.0, 1.0)
    assert red["bombas"]["bomba"]["caudal_m3s"] == pytest.approx(q, rel=1e-8)
    assert red["bombas"]["bomba"]["carga_m"] == pytest.approx(h0 - a * q ** 2, rel=1e-8)
    assert red["tramos"]["t"]["caudal_m3s"] == pytest.approx(q, rel=1e-8)


def test_bomba_con_demanda_conserva_la_continuidad():
    nodos, tramos, bombas = _red(demanda=0.03)
    red = resolver_red(nodos, tramos, bombas=bombas)
    assert red["bombas"]["bomba"]["caudal_m3s"] == pytest.approx(0.03, rel=1e-8)
    # la carga en N = carga de la bomba − pérdida: debe cumplir la curva
    q = 0.03
    assert red["nodos"]["B"]["carga_m"] == pytest.approx(10.0 + 60.0 - 2000.0 * q ** 2, rel=1e-9)


def test_mayor_a_en_la_curva_baja_el_caudal():
    qs = []
    for a in (500.0, 2000.0, 8000.0):
        nodos, tramos, bombas = _red(a=a)
        nodos[2].update(carga_fija_m=30.0)
        qs.append(resolver_red(nodos, tramos, bombas=bombas)["bombas"]["bomba"]["caudal_m3s"])
    assert qs[0] > qs[1] > qs[2]


def test_bomba_que_no_vence_la_carga_estatica_se_rechaza_o_marca_caudal_nulo():
    nodos, tramos, bombas = _red(h0=15.0)          # carga de cierre 25 m < carga estática 30 − 10 = 20? usa h0 < estática
    nodos[2].update(carga_fija_m=90.0)
    with pytest.raises(ValueError, match="no vence"):
        resolver_red(nodos, tramos, bombas=bombas)


@pytest.mark.parametrize("cambio", [dict(h0_m=0.0), dict(h0_m=-1.0), dict(a_s2m5=0.0), dict(a_s2m5=float("nan"))])
def test_bombas_invalidas_se_rechazan(cambio):
    nodos, tramos, bombas = _red(demanda=0.02)
    bombas[0].update(cambio)
    with pytest.raises(ValueError):
        resolver_red(nodos, tramos, bombas=bombas)


def test_flujo_inverso_por_la_bomba_se_detecta():
    # Un tanque a mucha mayor carga empuja agua hacia atrás por la bomba: no hay válvula de retención modelada
    nodos, tramos, bombas = _red()
    nodos[2].update(carga_fija_m=500.0)
    with pytest.raises(ValueError, match="no vence|inverso"):
        resolver_red(nodos, tramos, bombas=bombas)
