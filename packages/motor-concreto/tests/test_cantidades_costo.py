"""Cantidades, costo y CO₂ de vigas y columnas: esperados calculados a mano y coherencia con la mezcla del resto de motores."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.cantidades_costo import Cantidades, cantidades_columna, cantidades_viga, costo_co2, longitud_estribo_m
from src.columna import DisenoColumna
from src.diseno_viga import DisenoViga
from src.economia_concreto import Economia, co2_m3, costo_m3

VIGA = DisenoViga(b=300, h=600, dia="6", n_sup=3, n_inf=3, estribo_dia="3", s_conf=100, s_centro=200, n_estribos=40, nivel="DMO", verificaciones=())
COL = DisenoColumna(h=400, b=400, n_cara=3, dia="7", estribo="3", nivel="DMO", s_conf=100, s_fuera=150, lo_mm=600, n_estribos=30, verificaciones=())
A6 = math.pi / 4 * 19.1**2
A3 = math.pi / 4 * 9.5**2
A7 = math.pi / 4 * 22.2**2


def test_estribo_perimetro_del_nucleo_mas_dos_ganchos():
    assert longitud_estribo_m(300, 600, 40, "3") == pytest.approx((2 * 220 + 2 * 520 + 2 * 75) / 1000)      # 6·9,5 = 57 < 75 mm


def test_cantidades_de_viga_a_mano():
    q = cantidades_viga(VIGA, 5.6)
    longitud_barra = 5.6 + 2 * 40 * 19.1 / 1000
    acero = 6 * A6 * 1e-6 * longitud_barra * 7850 + 40 * A3 * 1e-6 * 1.63 * 7850
    assert q.volumen_m3 == pytest.approx(0.3 * 0.6 * 5.6)
    assert q.acero_kg == pytest.approx(acero)
    assert q.encofrado_m2 == pytest.approx((0.3 + 2 * 0.6) * 5.6)


def test_cantidades_de_columna_a_mano():
    q = cantidades_columna(COL, 3.0)
    assert COL.n_barras == 8
    acero = 8 * A7 * 1e-6 * 3.0 * 7850 + 30 * A3 * 1e-6 * ((2 * 320 + 2 * 320 + 150) / 1000) * 7850
    assert q.volumen_m3 == pytest.approx(0.4 * 0.4 * 3.0)
    assert q.acero_kg == pytest.approx(acero)
    assert q.encofrado_m2 == pytest.approx(4 * 0.4 * 3.0)


def test_costo_y_co2_usan_la_misma_mezcla_y_precios_que_zapata_y_muro():
    q = Cantidades(2.0, 150.0, 12.0)
    eco = Economia()
    cop, co2 = costo_co2(q, 28.0, eco)
    assert cop == pytest.approx(2.0 * costo_m3(28.0, 0.0, eco.p_ceniza, eco.mult_concreto) + 150.0 * eco.p_acero + 12.0 * eco.p_encofrado)
    assert co2 == pytest.approx(2.0 * co2_m3(28.0, 0.0, eco.fe_cemento) + 150.0 * eco.fe_acero)


def test_mas_acero_cuesta_mas_y_emite_mas_y_los_precios_escalan_el_costo():
    base = Cantidades(1.0, 100.0, 5.0)
    c0, e0 = costo_co2(base, 21.0)
    c1, e1 = costo_co2(Cantidades(1.0, 130.0, 5.0), 21.0)
    assert c1 > c0 and e1 > e0
    dif = costo_co2(base, 21.0, Economia(p_acero=Economia().p_acero * 2))[0] - c0
    assert dif == pytest.approx(100.0 * Economia().p_acero)


def test_suma_de_cantidades():
    assert Cantidades(1, 2, 3) + Cantidades(4, 5, 6) == Cantidades(5, 7, 9)
