import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.viga import (AREA_MM2, Cargas, Materiales, Seccion, beta1, combinacion_ultima, momento_nominal,
                      peso_propio_kn_m, verificar)

M = Materiales(fc=21.0, fy=420.0, fyt=420.0)


def sec(**kw):
    base = dict(b=300, h=500, barras_n=3, barras_dia="6", estribo_dia="3", estribo_s=150)
    base.update(kw)
    return Seccion(**base)


def test_beta1_fc21_es_085():
    assert beta1(21.0) == 0.85


def test_beta1_fc42_es_075():
    assert beta1(42.0) == pytest.approx(0.75)


def test_d_efectivo_calculo_a_mano():
    # 500 - 40 - 9.5 - 19.1/2 = 440.95
    assert sec().d == pytest.approx(440.95)


def test_momento_nominal_a_mano():
    s = sec()
    As = 3 * math.pi / 4 * 19.1**2
    a = As * 420 / (0.85 * 21 * 300)
    esperado = 0.9 * As * 420 * (s.d - a / 2) / 1e6
    phiMn, a_calc, _ = momento_nominal(s, M)
    assert phiMn == pytest.approx(esperado)
    assert a_calc == pytest.approx(a)


def test_combinacion_incluye_peso_propio():
    wu, Mu, _ = combinacion_ultima(Cargas(10.0, 5.0, 6.0), 300, 500)
    D = 10.0 + peso_propio_kn_m(300, 500)
    assert peso_propio_kn_m(300, 500) == pytest.approx(3.6)
    assert wu == pytest.approx(1.2 * D + 1.6 * 5.0)
    assert Mu == pytest.approx(wu * 36 / 8)


def test_viga_holgada_cumple():
    r = verificar(sec(barras_n=4), M, Cargas(10.0, 5.0, 6.0))
    assert r.cumple, [f.nombre for f in r.fallas()]


def test_falla_por_flexion_con_poco_acero():
    r = verificar(sec(barras_n=2, barras_dia="4"), M, Cargas(20.0, 10.0, 6.0))
    assert "Flexión φMn ≥ Mu" in [f.nombre for f in r.fallas()]


def test_falla_por_cortante_con_estribos_muy_separados():
    r = verificar(sec(barras_n=4, estribo_s=400), M, Cargas(25.0, 10.0, 6.0))
    nombres = [f.nombre for f in r.fallas()]
    assert any("Cortante" in n or "Separación de estribos" in n for n in nombres)


def test_vc_calculo_a_mano():
    s = sec()
    Vc = 0.17 * math.sqrt(21) * 300 * s.d / 1000
    assert Vc == pytest.approx(103.06, abs=0.2)


def test_separacion_libre_barras_insuficiente():
    r = verificar(sec(b=200, barras_n=4, barras_dia="8"), M, Cargas(5.0, 2.0, 4.0))
    assert "Separación libre entre barras" in [f.nombre for f in r.fallas()]


def test_area_barra_6():
    assert AREA_MM2["6"] == pytest.approx(286.5, abs=0.2)
