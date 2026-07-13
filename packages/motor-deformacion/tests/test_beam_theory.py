"""Tests de teoría de vigas — validados contra fórmulas de libro de texto
(Timoshenko & Gere, Hibbeler) y verificación cruzada con el solver BVP general."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import beam_theory as bt
from src.models import CondicionApoyo

E = 200e9   # Pa, acero
I = 8.5e-6  # m4
EI = E * I
L = 4.0
P = 10_000.0
w = 5_000.0

TOL = 1e-9


def test_cantilever_puntual_en_la_punta():
    r = bt.cantilever_puntual(P, L, L, EI)
    assert abs(r.deflexion_max - P * L ** 3 / (3 * EI)) / r.deflexion_max < TOL
    assert abs(r.momento_max - P * L) / r.momento_max < TOL
    assert abs(r.cortante_max - P) / r.cortante_max < TOL


def test_cantilever_udl():
    r = bt.cantilever_udl(w, L, EI)
    assert abs(r.deflexion_max - w * L ** 4 / (8 * EI)) / r.deflexion_max < TOL
    assert abs(r.momento_max - w * L ** 2 / 2) / r.momento_max < TOL
    assert abs(r.cortante_max - w * L) / r.cortante_max < TOL


def test_simple_puntual_centrado():
    r = bt.simple_puntual(P, L / 2, L, EI)
    assert abs(r.deflexion_max - P * L ** 3 / (48 * EI)) / r.deflexion_max < TOL
    assert abs(r.momento_max - P * L / 4) / r.momento_max < TOL


def test_simple_udl():
    r = bt.simple_udl(w, L, EI)
    assert abs(r.deflexion_max - 5 * w * L ** 4 / (384 * EI)) / r.deflexion_max < TOL
    assert abs(r.momento_max - w * L ** 2 / 8) / r.momento_max < TOL
    assert abs(r.cortante_max - w * L / 2) / r.cortante_max < TOL


def test_fixfix_puntual_centrado():
    r = bt.empotrada_empotrada_puntual(P, L, EI)
    assert abs(r.deflexion_max - P * L ** 3 / (192 * EI)) / r.deflexion_max < TOL
    assert abs(r.momento_max - P * L / 8) / r.momento_max < TOL


def test_fixfix_udl():
    r = bt.empotrada_empotrada_udl(w, L, EI)
    assert abs(r.deflexion_max - w * L ** 4 / (384 * EI)) / r.deflexion_max < TOL
    assert abs(r.momento_max - w * L ** 2 / 12) / r.momento_max < TOL  # momento en el empotramiento


def test_solver_general_coincide_con_formulas_cerradas_cantilever_udl():
    r_cerrado = bt.cantilever_udl(w, L, EI)
    r_general = bt.resolver_general(lambda x: w, L, EI, CondicionApoyo.CANTILEVER)
    assert abs(r_general.deflexion_max - r_cerrado.deflexion_max) / r_cerrado.deflexion_max < 1e-4
    assert abs(r_general.momento_max - r_cerrado.momento_max) / r_cerrado.momento_max < 1e-4


def test_solver_general_coincide_con_formulas_cerradas_simple_udl():
    r_cerrado = bt.simple_udl(w, L, EI)
    r_general = bt.resolver_general(lambda x: w, L, EI, CondicionApoyo.SIMPLE)
    assert abs(r_general.deflexion_max - r_cerrado.deflexion_max) / r_cerrado.deflexion_max < 1e-4


def test_solver_general_coincide_con_formulas_cerradas_fixfix_udl():
    r_cerrado = bt.empotrada_empotrada_udl(w, L, EI)
    r_general = bt.resolver_general(lambda x: w, L, EI, CondicionApoyo.EMPOTRADA_EMPOTRADA)
    assert abs(r_general.deflexion_max - r_cerrado.deflexion_max) / r_cerrado.deflexion_max < 1e-4


def test_propped_cantilever_udl_contra_valor_de_referencia():
    """Viga empotrada-apoyada, UDL: v_max ≈ wL⁴/(184.6·EI) (Roark's Formulas for Stress and Strain)."""
    r = bt.resolver_general(lambda x: w, L, EI, CondicionApoyo.EMPOTRADA_APOYADA)
    v_ref = w * L ** 4 / (184.6 * EI)
    assert abs(r.deflexion_max - v_ref) / v_ref < 5e-3
    m_ref = w * L ** 2 / 8  # momento en el empotramiento
    assert abs(r.momento_max - m_ref) / m_ref < 1e-3


def test_superposicion_es_aditiva():
    r1 = bt.cantilever_puntual(P, L, L, EI)
    r2 = bt.cantilever_udl(w, L, EI)
    rs = bt.superponer([r1, r2], L)
    assert abs(rs.deflexion_max - (r1.deflexion_max + r2.deflexion_max)) < 1e-9
    assert abs(rs.v(L / 2) - (r1.v(L / 2) + r2.v(L / 2))) < 1e-12
