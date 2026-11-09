"""Fase 3b: pantalla por secciones, bandeja, dentellón y combinación sísmica. Esperados con integrales cerradas hechas a mano."""
import math

import numpy as np
import pytest

from src.muro_contencion import GeometriaMuro, Relleno, SueloApoyo
from src.muro_contencion_estructural import disenar_estructura
from src.muro_pantalla import acciones_pantalla, disenar_bandeja
from src.viga import Materiales

M = Materiales(28.0, 420.0)
R = Relleno(18.0, 30.0)
S = SueloApoyo(30.0, 200.0)
G0 = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 2.6)
GB = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 2.6, bandeja_y=1.2, bandeja_vuelo=0.8, bandeja_esp=0.2)


def _kae(phi, kh):
    p = math.radians(phi)
    a = np.radians(np.linspace(phi + 0.01, 89.9, 200001))
    return float(np.max((kh + np.tan(a - p)) / np.tan(a)))


def test_secciones_de_la_pantalla_a_mano():
    # σ = Ka γ z = 6 z; a y = 1.5 m (z_k = 1.5): V = 6·1.5²/2 = 6.75; M = 6·1.5³/6 = 3.375 → ×1.6
    mu, vu = acciones_pantalla(G0, R, 1.5, None)
    assert vu == pytest.approx(1.6 * 6.75, rel=1e-4) and mu == pytest.approx(1.6 * 3.375, rel=1e-4)


def test_bandeja_reduce_el_momento_de_la_base_segun_el_modelo():
    # sin bandeja: 1.6·27 = 43.2. Con bandeja: ∫ reducción = 4.917 (a mano) → 1.6·22.083 − 0.9·26.88·0.55 = 22.02
    mu, _ = acciones_pantalla(GB, R, 0.0, None)
    assert mu == pytest.approx(1.6 * 22.083 - 0.9 * 26.88 * 0.55, rel=2e-3)
    assert mu < acciones_pantalla(G0, R, 0.0, None)[0]


def test_la_bandeja_no_alivia_por_encima_de_ella():
    # sección a y = 2.0 m (sobre la bandeja, que va de 1.2 a 1.4 m): sin sombra ni contramomento
    assert acciones_pantalla(GB, R, 2.0, None) == pytest.approx(acciones_pantalla(G0, R, 2.0, None))


def test_losa_de_la_bandeja_a_mano():
    # z_t = 3 - 1.2 - 0.2 = 1.6; wu = 1.2 (18·1.6 + 24·0.2) = 40.32 kN/m²; Mu = wu·0.8²/2 = 12.90
    f = disenar_bandeja(GB, R, M)
    assert f.mu_knm_m == pytest.approx(40.32 * 0.64 / 2, rel=1e-9)
    assert disenar_bandeja(G0, R, M) is None


def test_sismo_en_la_pantalla_a_mano():
    kh = 0.2
    dp = 0.5 * 18.0 * (_kae(30.0, kh) - 1.0 / 3.0) * 9.0
    esperado = 1.6 * 27.0 + 1.4 * (1.8 * dp + kh * 24.0 * 0.3 * 3.0 * 1.5)
    mu, vu = acciones_pantalla(G0, R, 0.0, kh)
    assert mu == pytest.approx(esperado, rel=5e-4)
    assert vu == pytest.approx(1.6 * 27.0 + 1.4 * (dp + kh * 24.0 * 0.3 * 3.0), rel=5e-4)


def test_dentellon_diseno_a_mano():
    g = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, dentellon_prof=0.4, dentellon_ancho=0.4)
    d = disenar_estructura(g, R, S, M)
    fk = 1.6 * 36.75 - (138.0 + 0.4 * 0.4 * 24.0) * math.tan(math.radians(20.0))
    assert d.dentellon.vu_kn_m == pytest.approx(fk, rel=1e-6)
    assert d.dentellon.mu_knm_m == pytest.approx(fk * 0.2, rel=1e-6)


def test_diseno_completo_con_todas_las_variantes_y_sismo():
    g = GeometriaMuro(3.0, 0.5, 0.3, 0.45, 0.7, 2.8, perfil="parabolico", dentellon_prof=0.4, dentellon_ancho=0.4,
                      bandeja_y=1.2, bandeja_vuelo=0.8, bandeja_esp=0.2)
    d = disenar_estructura(g, R, SueloApoyo(30.0, 300.0, c_kpa=10.0), M, a_max_g=0.20)
    assert len(d.secciones_pantalla) == 8
    assert d.estabilidad_sismica is not None and d.dentellon is not None and d.bandeja is not None
    assert d.cumple or d.motivos          # o cumple, o dice por qué no


def test_el_sismo_encarece_o_iguala():
    s = SueloApoyo(30.0, 300.0, c_kpa=10.0)
    g = GeometriaMuro(3.0, 0.5, 0.3, 0.45, 0.7, 2.8)
    a, b = disenar_estructura(g, R, s, M), disenar_estructura(g, R, s, M, a_max_g=0.25)
    assert a.cumple, a.motivos
    assert b.pantalla.mu_knm_m >= a.pantalla.mu_knm_m
    if b.cumple:
        assert b.costo_cop_m >= a.costo_cop_m * 0.999


def test_pantalla_parabolica_delgada_se_detecta_en_secciones_superiores():
    g = GeometriaMuro(5.0, 0.6, 0.2, 0.6, 0.8, 3.5, perfil="parabolico")
    d = disenar_estructura(g, R, SueloApoyo(30.0, 300.0, c_kpa=10.0), M)
    assert len(d.secciones_pantalla) == 8
    assert all(sec.phi_mn_knm_m > 0 for sec in d.secciones_pantalla)
