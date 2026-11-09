"""Validación del solver FEM contra soluciones cerradas e integración independiente."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest
from scipy.integrate import quad

from src import beam_theory as bt
from src import discretizado as d

E, I, L, W, P = 200e9, 8.5e-6, 4.0, 5000.0, 10000.0
EI = E * I


def test_simple_udl_coincide_con_formula_cerrada_y_con_beam_theory():
    r = d.flexion(L, EI, q=-W, n_elem=8)
    assert r.w.min() == pytest.approx(-5 * W * L**4 / (384 * EI), rel=1e-9)
    assert r.M.max() == pytest.approx(W * L**2 / 8, rel=1e-9)
    assert abs(r.w.min()) == pytest.approx(bt.simple_udl(W, L, EI).deflexion_max, rel=1e-9)
    assert r.V[0] == pytest.approx(W * L / 2, rel=1e-9) and r.V[-1] == pytest.approx(-W * L / 2, rel=1e-9)


def test_voladizo_udl_momento_negativo_en_el_empotramiento():
    r = d.flexion(L, EI, q=-W, izquierdo="fijo", derecho="libre", n_elem=8)
    assert r.w.min() == pytest.approx(-W * L**4 / (8 * EI), rel=1e-9)
    assert r.M[0] == pytest.approx(-W * L**2 / 2, rel=1e-9)
    assert r.reacciones["Fy"][0] == pytest.approx(W * L, rel=1e-9)


def test_puntual_en_posicion_arbitraria_nodo_insertado():
    a = 1.3                                              # no coincide con la malla uniforme
    r = d.flexion(L, EI, cargas_puntuales=[(a, -P)], n_elem=10)
    i = int(np.argmin(np.abs(r.x - a)))
    assert r.x[i] == pytest.approx(a)
    b = L - a
    esperado = -P * a * b * (L**2 - a**2 - b**2) / (6 * EI * L)
    assert r.w[i] == pytest.approx(esperado, rel=1e-9)


def test_empotrada_empotrada_puntual_al_centro():
    r = d.flexion(L, EI, cargas_puntuales=[(L / 2, -P)], izquierdo="fijo", derecho="fijo", n_elem=10)
    assert r.w.min() == pytest.approx(-P * L**3 / (192 * EI), rel=1e-9)
    assert r.M[0] == pytest.approx(-P * L / 8, rel=1e-9)


def test_dos_vanos_reaccion_central_5_4_wl():
    l = 3.0
    r = d.flexion(2 * l, EI, q=-W, apoyos_intermedios=[l], n_elem=10)
    k = int(np.argmin(np.abs(np.array(r.reacciones["x"]) - l)))
    assert r.reacciones["Fy"][k] == pytest.approx(1.25 * W * l, rel=1e-9)
    assert sum(r.reacciones["Fy"]) == pytest.approx(W * 2 * l, rel=1e-9)


def test_EI_variable_contra_integral_independiente():
    ei = lambda x: EI * (1 + x / L)                      # sección que crece hacia la punta
    r = d.flexion(L, ei, cargas_puntuales=[(L, -P)], izquierdo="fijo", derecho="libre", n_elem=200)
    ref, _ = quad(lambda x: P * (L - x) ** 2 / ei(x), 0, L)       # δ = ∫ M m / EI
    assert -r.w[-1] == pytest.approx(ref, rel=1e-6)


def test_fundacion_winkler_con_carga_senoidal_exacta():
    k = 5e5
    q0 = 8000.0
    r = d.flexion(L, EI, q=lambda x: -q0 * np.sin(np.pi * x / L), k_fundacion=k, n_elem=200)
    ref = -q0 * np.sin(np.pi * r.x / L) / (EI * (np.pi / L) ** 4 + k)
    assert np.max(np.abs(r.w - ref)) / np.max(np.abs(ref)) < 1e-6


def test_convergencia_orden_cuatro_con_carga_senoidal():
    errs = []
    for n in (4, 8, 16):
        r = d.flexion(L, EI, q=lambda x: -W * np.sin(np.pi * x / L), n_elem=n)
        ref = -W * np.sin(np.pi * r.x / L) / (EI * (np.pi / L) ** 4)
        errs.append(np.max(np.abs(r.w - ref)))
    assert errs[0] / errs[1] > 12 and errs[1] / errs[2] > 12          # ~16 para h^4


@pytest.mark.parametrize("izq,der,k", [("articulado", "articulado", 1.0), ("fijo", "libre", 2.0), ("fijo", "fijo", 0.5)])
def test_pandeo_euler_factores_clasicos(izq, der, k):
    p = d.pandeo(L, EI, izquierdo=izq, derecho=der, n_elem=40)
    assert p.P_cr == pytest.approx(np.pi**2 * EI / (k * L) ** 2, rel=1e-4)
    assert p.K_efectivo == pytest.approx(k, rel=1e-4)


def test_pandeo_empotrada_articulada_k_0699():
    p = d.pandeo(L, EI, izquierdo="fijo", derecho="articulado", n_elem=60)
    assert p.K_efectivo == pytest.approx(0.6992, abs=2e-4)           # raíz de tan(x)=x: 4.4934


def test_pandeo_apoyo_intermedio_duplica_modo():
    p = d.pandeo(L, EI, apoyos_intermedios=[L / 2], n_elem=40)
    assert p.P_cr == pytest.approx(4 * np.pi**2 * EI / L**2, rel=1e-4)


def test_pandeo_es_adimensional_no_depende_de_E_I_ni_de_L():
    a = d.pandeo(1.0, 1.0, n_elem=30).lambda_cr
    b = d.pandeo(37.0, 3.3e12, n_elem=30).lambda_cr
    assert a == pytest.approx(b, rel=1e-9) and a == pytest.approx(np.pi**2, rel=1e-5)


def test_errores_de_entrada():
    with pytest.raises(ValueError):
        d.flexion(L, EI, izquierdo="libre", derecho="libre")          # mecanismo
    with pytest.raises(ValueError):
        d.flexion(L, EI, izquierdo="rodillo")
    with pytest.raises(ValueError):
        d.flexion(L, EI, cargas_puntuales=[(L + 1, -P)])
    with pytest.raises(ValueError):
        d.flexion(0.0, EI)
