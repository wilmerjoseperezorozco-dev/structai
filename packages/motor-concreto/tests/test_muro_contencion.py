"""Fase 1 del muro de contención: estabilidad externa. Los valores esperados se calcularon a mano (ver comentarios), no con el propio código."""
import math

import pytest

from src.muro_contencion import (GeometriaMuro, Relleno, SueloApoyo, _cargas_verticales, _poligono, coeficiente_activo_rankine,
                                 verificar_estabilidad)

# Caso de mano: H_pant=3, h_zap=0.5, t=0.3 (prismática), puntera 0.6, talón 1.6 -> B=2.5; γ_s=18, φ=30°, γ_c=24, μ=tan(20°)
G = GeometriaMuro(h_pantalla=3.0, h_zapata=0.5, t_corona=0.3, t_base=0.3, b_puntera=0.6, b_talon=1.6)
R = Relleno(gamma=18.0, phi_deg=30.0)
S = SueloApoyo(phi_deg=30.0, q_adm_kpa=200.0)


def test_ka_rankine_plano_es_un_tercio_para_30_grados():
    assert coeficiente_activo_rankine(30.0, 0.0) == pytest.approx(1.0 / 3.0, abs=1e-12)


def test_ka_con_talud_igual_a_phi_vale_cos_phi():
    # con β = φ la raíz se anula y K_A = cos φ (resultado cerrado de Rankine)
    assert coeficiente_activo_rankine(30.0, 30.0) == pytest.approx(math.cos(math.radians(30.0)), abs=1e-12)


def test_ka_crece_con_la_inclinacion_del_relleno():
    valores = [coeficiente_activo_rankine(32.0, b) for b in (0, 5, 10, 20, 32)]
    assert all(a < b for a, b in zip(valores, valores[1:]))


def test_poligono_trapecio_de_la_pantalla_conica():
    # trapecio (0.2 corona, 0.4 base, altura 3): área = (0.2+0.4)/2·3 = 0.9 m²
    area, _, yc = _poligono([(0, 0), (0.4, 0), (0.2, 3.0), (0, 3.0)])
    assert area == pytest.approx(0.9)
    assert 1.0 < yc < 1.5   # el centroide queda por debajo de la mitad porque la base es más ancha


def test_pesos_de_la_pieza_a_mano():
    pesos = {n: (f, x) for n, f, x in _cargas_verticales(G, R, 24.0)}
    assert pesos["pantalla"][0] == pytest.approx(21.6) and pesos["pantalla"][1] == pytest.approx(0.75)
    assert pesos["zapata"][0] == pytest.approx(30.0) and pesos["zapata"][1] == pytest.approx(1.25)
    assert pesos["relleno_talon"][0] == pytest.approx(86.4) and pesos["relleno_talon"][1] == pytest.approx(1.7)


def test_caso_de_mano_completo():
    # Pa = 1/2·(1/3)·18·3.5² = 36.75 kN/m a 3.5/3 m; Mo = 42.875; ΣV = 138; Mr = 200.58; FS_v = 4.678
    # x_R = (200.58-42.875)/138 = 1.1428; e = 1.25-1.1428 = 0.1072; q_max = 55.2·(1+6·0.1072/2.5) = 69.40; FS_d = 138·tan20°/36.75 = 1.367
    r = verificar_estabilidad(G, R, S)
    assert r.empuje_kn_m == pytest.approx(36.75)
    assert r.sum_v_kn_m == pytest.approx(138.0)
    assert r.fs_volcamiento == pytest.approx(200.58 / 42.875, rel=1e-4)
    assert r.excentricidad_m == pytest.approx(0.1072, abs=2e-4)
    assert r.q_max_kpa == pytest.approx(69.40, abs=0.05)
    assert r.fs_deslizamiento == pytest.approx(138.0 * math.tan(math.radians(20.0)) / 36.75, rel=1e-6)
    assert r.volumen_concreto_m3_m == pytest.approx((0.9 + 1.25))


def test_el_caso_de_mano_falla_solo_por_deslizamiento():
    r = verificar_estabilidad(G, R, S)
    assert not r.cumple
    assert len(r.motivos) == 1 and "deslizamiento" in r.motivos[0]


def test_equilibrio_de_presiones_integra_la_vertical():
    r = verificar_estabilidad(G, R, S)
    B = G.ancho_base
    assert (r.q_max_kpa + r.q_min_kpa) / 2.0 * B == pytest.approx(r.sum_v_kn_m, rel=1e-9)


def test_talon_mas_largo_mejora_volcamiento_y_deslizamiento():
    base = verificar_estabilidad(G, R, S)
    largo = verificar_estabilidad(GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 2.4), R, S)
    assert largo.fs_volcamiento > base.fs_volcamiento and largo.fs_deslizamiento > base.fs_deslizamiento


def test_un_muro_holgado_cumple():
    r = verificar_estabilidad(GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 2.6), R, SueloApoyo(phi_deg=30.0, q_adm_kpa=200.0, c_kpa=10.0))
    assert r.cumple, r.motivos


def test_la_sobrecarga_empeora_el_volcamiento_y_el_empuje():
    sin = verificar_estabilidad(G, R, S)
    con = verificar_estabilidad(G, Relleno(18.0, 30.0, sobrecarga_kpa=20.0), S)
    assert con.empuje_kn_m > sin.empuje_kn_m and con.fs_volcamiento < sin.fs_volcamiento


def test_relleno_inclinado_aporta_componente_vertical_y_mas_empuje():
    plano = verificar_estabilidad(G, R, S)
    inclinado = verificar_estabilidad(G, Relleno(18.0, 30.0, beta_deg=15.0), S)
    assert inclinado.ka > plano.ka and inclinado.empuje_kn_m > plano.empuje_kn_m
    assert inclinado.fs_volcamiento < plano.fs_volcamiento


def test_desplante_menor_a_un_metro_se_reporta():
    g = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 2.6, desplante=0.6)
    assert any("desplante" in m for m in verificar_estabilidad(g, R, S).motivos)


@pytest.mark.parametrize("kwargs", [dict(t_corona=0.5, t_base=0.3), dict(h_pantalla=0.0)])
def test_geometria_invalida_lanza_error(kwargs):
    base = dict(h_pantalla=3.0, h_zapata=0.5, t_corona=0.3, t_base=0.3, b_puntera=0.6, b_talon=1.6)
    with pytest.raises(ValueError):
        verificar_estabilidad(GeometriaMuro(**{**base, **kwargs}), R, S)


def test_beta_mayor_que_phi_es_invalido():
    with pytest.raises(ValueError):
        coeficiente_activo_rankine(30.0, 35.0)
