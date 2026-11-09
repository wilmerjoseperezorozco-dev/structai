"""Fase 3a del muro: variantes geométricas (perfil parabólico, dentellón, bandeja) y sismo seudoestático. Esperados a mano o por un método independiente."""
import math

import numpy as np
import pytest

from src.muro_contencion import (GeometriaMuro, Relleno, SueloApoyo, _piezas, coeficiente_activo_mononobe_okabe, coeficiente_activo_rankine,
                                 mu_efectivo, verificar_estabilidad, verificar_estabilidad_sismica)

G = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6)
R = Relleno(18.0, 30.0)
S = SueloApoyo(30.0, 200.0)


def _kae_cuna(phi_deg, kh):
    """Método independiente: cuña de Coulomb con inercia, muro vertical liso, relleno plano: Pa/(½γH²) = max_α [kh + tan(α-φ)]/tanα."""
    phi = math.radians(phi_deg)
    a = np.radians(np.linspace(phi_deg + 0.01, 89.9, 200001))
    return float(np.max((kh + np.tan(a - phi)) / np.tan(a)))


@pytest.mark.parametrize("phi,beta", [(30, 0), (34, 10), (28, 20)])
def test_mononobe_okabe_sin_sismo_es_rankine(phi, beta):
    assert coeficiente_activo_mononobe_okabe(phi, beta, 0.0) == pytest.approx(coeficiente_activo_rankine(phi, beta), rel=1e-9)


@pytest.mark.parametrize("kh", [0.05, 0.1, 0.2, 0.3])
def test_mononobe_okabe_coincide_con_cuna_de_coulomb(kh):
    assert coeficiente_activo_mononobe_okabe(30.0, 0.0, kh) == pytest.approx(_kae_cuna(30.0, kh), rel=2e-4)


def test_mononobe_okabe_sin_solucion_cuando_theta_supera_phi():
    assert math.isinf(coeficiente_activo_mononobe_okabe(25.0, 0.0, 0.6))


def test_pantalla_parabolica_tiene_el_area_de_la_integral():
    g = GeometriaMuro(3.0, 0.5, 0.2, 0.5, 0.6, 1.6, perfil="parabolico")
    gl = GeometriaMuro(3.0, 0.5, 0.2, 0.5, 0.6, 1.6)
    f = {n: v for n, v, _, _ in _piezas(g, R, 24.0)}
    fl = {n: v for n, v, _, _ in _piezas(gl, R, 24.0)}
    assert f["pantalla"] / 24.0 == pytest.approx(0.2 * 3 + 0.3 * 3 / 3, rel=2e-3)      # ∫ t dy con n = 2
    assert fl["pantalla"] / 24.0 == pytest.approx(0.2 * 3 + 0.3 * 3 / 2, rel=1e-9)


def test_sismo_caso_de_mano():
    kh = 0.8 * 0.25
    kae = _kae_cuna(30.0, kh)
    pae = 0.5 * kae * 18.0 * 3.5**2
    d_pae = pae - 36.75
    mo = 36.75 * 3.5 / 3 + d_pae * 0.6 * 3.5 + kh * (21.6 * 2.0 + 30.0 * 0.25 + 86.4 * 2.0)
    ph = 36.75 + d_pae + kh * 138.0
    r = verificar_estabilidad_sismica(G, R, S, 0.25)
    assert r.empuje_kn_m == pytest.approx(pae, rel=3e-4)
    assert r.fs_deslizamiento == pytest.approx(138.0 * math.tan(math.radians(20.0)) / ph, rel=5e-4)
    assert r.fs_volcamiento == pytest.approx(200.58 / mo, rel=5e-4)


def test_el_sismo_empeora_los_factores_pero_sus_limites_son_menores():
    est = verificar_estabilidad(G, R, S)
    sis = verificar_estabilidad_sismica(G, R, S, 0.25)
    assert sis.fs_deslizamiento < est.fs_deslizamiento and sis.fs_volcamiento < est.fs_volcamiento
    assert any("1.05" in m for m in sis.motivos) or sis.fs_deslizamiento >= 1.05


def test_dentellon_efectivo_sube_la_friccion_y_el_deslizamiento():
    gk = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, dentellon_prof=0.4)
    assert mu_efectivo(gk, S) == pytest.approx(math.tan(math.radians(30.0)))
    assert mu_efectivo(G, S) == pytest.approx(math.tan(math.radians(20.0)))
    assert verificar_estabilidad(gk, R, S).fs_deslizamiento > verificar_estabilidad(G, R, S).fs_deslizamiento * 1.4


def test_dentellon_corto_no_cambia_el_coeficiente_pero_suma_peso():
    gk = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, dentellon_prof=0.2)
    assert mu_efectivo(gk, S) == pytest.approx(S.mu)
    assert verificar_estabilidad(gk, R, S).sum_v_kn_m == pytest.approx(138.0 + 0.2 * 0.4 * 24.0)


def test_bandeja_no_cambia_el_empuje_global_solo_el_peso():
    gb = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, bandeja_y=1.2, bandeja_vuelo=0.8, bandeja_esp=0.2)
    a, b = verificar_estabilidad(G, R, S), verificar_estabilidad(gb, R, S)
    assert b.empuje_kn_m == pytest.approx(a.empuje_kn_m)
    assert b.sum_v_kn_m == pytest.approx(a.sum_v_kn_m + 0.8 * 0.2 * (24.0 - 18.0))


def test_volumen_de_variantes():
    gb = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, dentellon_prof=0.4, bandeja_y=1.2, bandeja_vuelo=0.8, bandeja_esp=0.2)
    assert verificar_estabilidad(gb, R, S).volumen_concreto_m3_m == pytest.approx(0.9 + 1.25 + 0.4 * 0.4 + 0.8 * 0.2)


@pytest.mark.parametrize("kw", [dict(bandeja_y=2.9, bandeja_vuelo=1.0, bandeja_esp=0.3), dict(perfil="cubico"), dict(dentellon_prof=0.3, dentellon_ancho=5.0)])
def test_variantes_invalidas_lanzan_error(kw):
    with pytest.raises(ValueError):
        verificar_estabilidad(GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, **kw), R, S)
