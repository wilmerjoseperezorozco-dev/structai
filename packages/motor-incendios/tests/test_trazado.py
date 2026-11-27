"""Trazado de Steiner rectilíneo 3D (#336 F4), casos a mano. Vanos de 5 × 5 m, piso de 3,0 m, viga 300 × 500, losa de
0,12 m. Rociadores de F3 con criterios ilustrativos. Tubo envolvente de 0,05 m y holgura ilustrativa de 0,02 m."""
import math
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import geometria as g  # noqa: E402
from src import rociadores as r  # noqa: E402
from src import trazado as t  # noqa: E402

C = r.Criterios(4.0, 2.0, 2.0, 0.1, 12.0, 0.10, fuente="ilustrativo (prueba)")
P = t.ParametrosTrazado(0.05, 0.02)


def _caso(luces_x=(5.0,), pisos=1):
    p = SimpleNamespace(luces_x_m=luces_x, luces_y_m=(5.0,), alturas_piso_m=(3.0,) * pisos, columnas_mm=(400,) * pisos,
                        vigas_mm=((300, 500),) * pisos)
    e = g.desde_porticos(p, 0.12)
    return e, r.distribuir(r.panos_entre_vigas(p, 0, 0.12), C).puntos


def test_un_vano_alcanza_el_optimo_a_mano():
    # 4 rociadores en las esquinas de un cuadrado de 2,35 m y alimentación en el centro. El árbol de Steiner
    # rectilíneo óptimo es un eje de 2,35 m más dos ramales de 2,35 m: 7,05 m.
    e, pts = _caso()
    red = t.trazar(e, (2.5, 2.5, 2.78), pts, P)
    assert red.longitud_m == pytest.approx(7.05) and red.longitud_vertical_m == pytest.approx(0.0)
    assert red.no_conectados == [] and t.verificar_red(e, red, P) == []


def test_dos_vanos_pasan_bajo_la_viga():
    # Plano: eje de 7,35 m + 4 ramales de 2,35 m = 16,75 m. Para cruzar la viga (fondo en 2,50) hay que bajar a
    # 2,50 − 0,025 − 0,02 = 2,455 desde 2,78: 0,325 m a cada lado. Total: 16,75 + 0,65 = 17,40 m.
    e, pts = _caso((5.0, 5.0))
    red = t.trazar(e, (2.5, 2.5, 2.78), pts, P)
    assert red.longitud_vertical_m == pytest.approx(0.65, abs=1e-5)
    assert red.longitud_m == pytest.approx(17.40, abs=1e-5)
    assert t.verificar_red(e, red, P) == []


def test_un_ducto_obliga_a_rodear():
    e, pts = _caso()
    base = t.trazar(e, (1.325, 2.5, 2.78), pts, P).longitud_m
    e.agregar([g.Caja(1.8, 0.15, 2.6, 3.2, 4.85, 2.88, "ducto", "D1")])   # franja central bajo la losa
    red = t.trazar(e, (1.325, 2.5, 2.78), pts, P)
    assert red.no_conectados == [] and t.verificar_red(e, red, P) == []
    assert red.longitud_m > base + 0.3                               # baja bajo el ducto (2,6 − 0,045) y vuelve
    assert red.longitud_vertical_m > 0


def test_rociador_dentro_de_columna_no_se_conecta():
    e, pts = _caso()
    red = t.trazar(e, (2.5, 2.5, 2.78), pts + [(0.0, 0.0, 2.0)], P)
    assert red.no_conectados == [(0.0, 0.0, 2.0)] and t.verificar_red(e, red, P) == []


def test_la_losa_solo_se_atraviesa_en_un_pase_declarado():
    e, _ = _caso(pisos=2)
    alim, roc = (2.5, 2.5, 0.5), (2.5, 2.5, 5.78)
    assert t.trazar(e, alim, [roc], P).no_conectados == [roc]
    par = t.ParametrosTrazado(0.05, 0.02, pases_losa=((2.5, 2.5),))
    red = t.trazar(e, alim, [roc], par)
    assert red.no_conectados == [] and red.longitud_m == pytest.approx(5.28)
    assert t.verificar_red(e, red, par) == []
    assert t.verificar_red(e, red, P) != []                          # sin el pase, el verificador lo rechaza


def test_tramos_conservan_la_longitud():
    e, pts = _caso((5.0, 5.0))
    red = t.trazar(e, (2.5, 2.5, 2.78), pts, P)
    tr = red.tramos()
    assert len(tr) < len(red.aristas)
    assert sum(math.dist(a, b) for a, b in tr) == pytest.approx(red.longitud_m)


def test_parametros_incoherentes():
    with pytest.raises(ValueError):
        t.ParametrosTrazado(0.0, 0.02)
    with pytest.raises(ValueError):
        t.ParametrosTrazado(0.05, -0.01)
