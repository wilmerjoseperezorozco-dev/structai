"""Cálculo hidráulico (#336 F5). Valores de referencia calculados con la fórmula de Hazen-Williams escrita aparte
(h_f = 10,67·L·Q^1,852/(C^1,852·d^4,8704), γ = 9,81 kPa/m). Los datos son ILUSTRATIVOS, no normativos:
K = 80 L/(min·√bar), P_min = 50 kPa, C = 120, d = 26,6 y 35,1 mm, codo 0,6 m, te lateral 1,5 m."""
import math
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import geometria as g  # noqa: E402
from src import hidraulica as h  # noqa: E402
from src import rociadores as r  # noqa: E402
from src import trazado as t  # noqa: E402

D = h.Demanda(80.0, 50.0, 0.0, 0.0, fuente="ilustrativo (prueba)")
T25 = h.Tuberia("1in", 0.0266, 120.0)
T32 = h.Tuberia("1-1/4in", 0.0351, 120.0)
LE = {("codo90", "1in"): 0.6, ("te_lateral", "1in"): 1.5}
Q1 = 80 * math.sqrt(0.5)                                  # 56,57 L/min a 50 kPa


def test_un_rociador_en_tramo_horizontal():
    res = h.calcular([((0, 0, 0), (10, 0, 0))], (0, 0, 0), [(10, 0, 0)], D, T25, LE)
    assert res.p_alimentacion_kpa == pytest.approx(67.2695, abs=1e-3)
    assert res.q_total_lpm == pytest.approx(Q1, abs=1e-3)
    assert res.tramos[0].v_m_s == pytest.approx(1.6966, abs=1e-3)
    assert h.verificar(res, D) == []


def test_subida_y_codo():
    tr = [((0, 0, 0), (0, 0, 3)), ((0, 0, 3), (10, 0, 3))]
    res = h.calcular(tr, (0, 0, 0), [(10, 0, 3)], D, T25, LE)
    assert res.tramos[1].accesorios == ["codo90"]
    assert res.p_alimentacion_kpa == pytest.approx(102.9165, abs=1e-3)    # incluye 3 m × 9,81 kPa/m
    assert h.verificar(res, D) == []


def test_te_simetrica_reparte_por_igual():
    tr = [((0, 0, 0), (5, 0, 0)), ((5, 0, 0), (5, 3, 0)), ((5, 0, 0), (5, -3, 0))]
    tubs = {frozenset(tr[0]): T32, frozenset(tr[1]): T25, frozenset(tr[2]): T25}
    res = h.calcular(tr, (0, 0, 0), [(5, 3, 0), (5, -3, 0)], D, tubs, LE)
    assert [x.accesorios for x in res.tramos] == [[], ["te_lateral"], ["te_lateral"]]
    assert res.p_alimentacion_kpa == pytest.approx(65.8480, abs=1e-3)
    assert res.rociadores[0][2] == pytest.approx(res.rociadores[1][2], abs=1e-6)
    assert h.verificar(res, D) == []


def test_ramales_desiguales_gobierna_el_lejano():
    tr = [((0, 0, 0), (5, 0, 0)), ((5, 0, 0), (5, 2, 0)), ((5, 0, 0), (5, -6, 0))]
    res = h.calcular(tr, (0, 0, 0), [(5, 2, 0), (5, -6, 0)], D, T25, LE)
    assert res.gobernante == (5, -6, 0)
    cerca, lejos = res.rociadores
    assert lejos[1] == pytest.approx(50.0, abs=1e-3) and cerca[1] > 50.0 and cerca[2] > lejos[2]
    assert h.verificar(res, D) == []                                        # balance y energía cierran


def test_el_caudal_minimo_puede_gobernar():
    d = h.Demanda(40.0, 50.0, 40.0, 0.0, fuente="ilustrativo")             # (40/40)² bar = 100 kPa > 50 kPa
    assert d.p_requerida_kpa == pytest.approx(100.0)
    res = h.calcular([((0, 0, 0), (10, 0, 0))], (0, 0, 0), [(10, 0, 0)], d, T25, LE)
    assert res.rociadores[0][2] == pytest.approx(40.0, abs=1e-3)


def test_mangueras_se_suman_en_la_alimentacion():
    d = h.Demanda(80.0, 50.0, 0.0, 380.0, fuente="ilustrativo")
    res = h.calcular([((0, 0, 0), (10, 0, 0))], (0, 0, 0), [(10, 0, 0)], d, T25, LE)
    assert res.q_total_lpm == pytest.approx(Q1 + 380.0, abs=1e-3)


def test_falta_longitud_equivalente_o_fuente():
    tr = [((0, 0, 0), (0, 0, 3)), ((0, 0, 3), (10, 0, 3))]
    with pytest.raises(ValueError, match="longitud equivalente"):
        h.calcular(tr, (0, 0, 0), [(10, 0, 3)], D, T25, {})
    with pytest.raises(ValueError):
        h.Demanda(80.0, 50.0, 0.0, 0.0, fuente="")


def test_velocidad_maxima_declarada():
    res = h.calcular([((0, 0, 0), (10, 0, 0))], (0, 0, 0), [(10, 0, 0)], D, T25, LE)
    assert h.verificar(res, D, v_max_m_s=1.5) != [] and h.verificar(res, D, v_max_m_s=2.0) == []


def test_red_de_f4_completa():
    p = SimpleNamespace(luces_x_m=(5.0, 5.0), luces_y_m=(5.0,), alturas_piso_m=(3.0,), columnas_mm=(400,),
                        vigas_mm=((300, 500),))
    e = g.desde_porticos(p, 0.12)
    pts = r.distribuir(r.panos_entre_vigas(p, 0, 0.12), r.Criterios(4.0, 2.0, 2.0, 0.1, 12.0, 0.10, "ilustrativo")).puntos
    red = t.trazar(e, (2.5, 2.5, 2.78), pts, t.ParametrosTrazado(0.05, 0.02))
    le = {("codo90", "1in"): 0.6, ("te_lateral", "1in"): 1.5}
    alim = red.terminales[0]
    res = h.calcular(red.tramos(), alim, red.terminales[1:], D, T25, le)
    assert len(res.rociadores) == 8 and h.verificar(res, D) == []
    assert min(P for _, P, _ in res.rociadores) == pytest.approx(50.0, abs=1e-3)
    assert res.q_rociadores_lpm == pytest.approx(sum(x.q_lpm for x in res.tramos if x.a == alim), abs=1e-6)
