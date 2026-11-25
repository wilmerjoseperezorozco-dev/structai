"""Verificación a mano de la implementación de Boulanger e Idriss (2014) usada en validacion/medir_cetin2018.py (#328)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validacion"))

import pytest

import medir_cetin2018 as v


def test_valores_de_referencia_a_mano():
    assert math.exp(v.bi_f(0.0) - 2.8) == pytest.approx(0.0608, abs=1e-4)          # CRR con N = 0
    assert math.exp(v.bi_f(20.0) - 2.8) == pytest.approx(0.206, abs=2e-3)          # CRR con N = 20
    assert v.bi_rd(0.0, 7.5) == pytest.approx(1.0, abs=0.01)                       # rd en superficie
    assert v.bi_dn(0.0) == pytest.approx(0.0, abs=1e-6)                            # arena limpia
    assert v.bi_dn(35.0) == pytest.approx(math.exp(1.63 + 9.7 / 35.01 - (15.7 / 35.01) ** 2))


def test_msf_y_ksigma_neutros_en_la_referencia():
    c = {"n160": 15.0, "fc": 0.0, "amax": 0.2, "sv": 1.5 * v.PA_KPA, "sve": v.PA_KPA, "z": 5.0, "mw": 7.5}
    r = v.bi(c)
    csr = 0.65 * 0.2 * 1.5 * v.bi_rd(5.0, 7.5)
    assert r["csr75_bi"] == pytest.approx(csr, rel=2e-3)                          # MSF ≈ 1 y Kσ = 1
    assert r["fs_m1"] == pytest.approx(math.exp(v.bi_f(15.0) - 2.8) / r["csr75_bi"])
    assert 0 < r["pl_m1p"] < 1


def test_monotonia():
    base = {"n160": 10.0, "fc": 10.0, "amax": 0.25, "sv": 120.0, "sve": 80.0, "z": 6.0, "mw": 7.0}
    assert v.bi(base | {"n160": 20.0})["fs_m1"] > v.bi(base)["fs_m1"]
    assert v.bi(base | {"amax": 0.4})["pl_m1p"] > v.bi(base)["pl_m1p"]
    assert v.bi(base | {"fc": 30.0})["fs_m1"] > v.bi(base)["fs_m1"]


def test_evento_une_variantes_de_escritura():
    assert v._evento("1981 WestMorland ML=5.6") == v._evento("1981Westmorland ML=5.6")
