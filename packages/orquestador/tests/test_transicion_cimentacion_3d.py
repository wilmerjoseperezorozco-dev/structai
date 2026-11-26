"""Transición de cimentación (#333): zapata rectangular y losa rígida, con comprobaciones a mano."""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import transicion_cimentacion_3d as tr  # noqa: E402
from tests.test_cimentacion_edificio_3d import proyecto  # noqa: E402


def test_resultantes_suman_el_par_axial_y_los_momentos_de_base():
    nodos = [{"k": 0, "x": 0.0, "y": 0.0}, {"k": 1, "x": 10.0, "y": 0.0}]
    r = {"D": {0: np.array([100.0, 0.0, 0.0]), 1: np.array([300.0, 0.0, 0.0])},
         "E": {0: np.array([0.0, 7.0, -20.0]), 1: np.array([0.0, 3.0, -30.0])}}
    P, My, Mx = tr.resultantes(nodos, r, {"D": 1, "E": 1}, 5.0, 0.0)
    assert P == 400.0
    assert My == pytest.approx(100 * -5 + 300 * 5 + 50)       # ΣP·x′ − ΣMy
    assert Mx == pytest.approx(10.0)                           # ΣP·y′ + ΣMx, con y′ = 0


def test_presiones_de_losa_rigida_a_mano():
    # 10 × 10 m, P = 1000 kN, M_y = 1000 kN·m: q = 10 ± 1000·5/(10·10³/12) = 10 ± 6 kPa
    assert tr.presiones_losa([(1000.0, 1000.0, 0.0)], 10.0, 10.0) == pytest.approx((16.0, 4.0))


def test_punzonamiento_interior_a_mano():
    # c = d = 500 mm: bo = 4000 mm, área 1 m²; vc = 0,33·√28 (gobierna sobre 0,083·(40·500/4000 + 2) = 0,58)
    vu, fvc = tr.punzonamiento(3000.0, 100.0, 500.0, 500.0, 0, 1000.0, 28.0)
    assert vu == pytest.approx(3000 - 100 * 1.0)
    assert fvc == pytest.approx(0.75 * 0.33 * math.sqrt(28) * 4000 * 500 / 1000)
    # esquina sin voladizo: dos lados de c + d/2 = 750 mm y αs = 20
    _vu, fvc_e = tr.punzonamiento(3000.0, 0.0, 500.0, 500.0, 2, 0.0, 28.0)
    assert fvc_e == pytest.approx(0.75 * min(0.33, 0.083 * (20 * 500 / 1500 + 2)) * math.sqrt(28) * 1500 * 500 / 1000)


def test_losa_bajo_edificio_bajo_cumple_y_respeta_q_adm():
    p = proyecto()
    losa = tr.disenar_losa(p, 100.0)
    assert losa.cumple and losa.q_max_serv_kpa <= 100.0 and losa.q_min_serv_kpa >= 0
    assert losa.Bx_m == pytest.approx(10.0 + 0.35 + 2 * losa.voladizo_m)
    assert losa.costo_cop > 0 and losa.acero_kg > 0


def test_losa_sin_capacidad_portante_no_cumple():
    losa = tr.disenar_losa(proyecto(), 20.0)                   # q_adm menor que el relleno y la losa
    assert not losa.cumple and "pilotes" in losa.motivo


def test_rectangular_se_alarga_en_la_direccion_con_espacio():
    from src import diseno_edificio_3d as de
    suelo = tr._zp.Suelo(q_adm_kpa=200.0, profundidad_desplante_m=1.5)
    mat = de._vg.Materiales(fc=28.0, fy=420.0, fyt=420.0)
    cg = [tr._zp.CargasZapata(P_serv=2000.0, P_u=2800.0)]
    r = tr.rectangular(cg, 400.0, 6000.0, 2500.0, suelo, mat)
    assert r is not None
    Lx, Ly, h, *_ = r
    assert Ly <= 2500 and Lx > Ly and Lx * Ly / 1e6 * 200 >= 2000
