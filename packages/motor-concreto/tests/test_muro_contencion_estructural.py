"""Fase 2 del muro de contención: diseño estructural. Los esperados se obtienen con fórmulas cerradas escritas en la propia prueba (no con el código)."""
import math

import pytest

from src.muro_contencion import GeometriaMuro, Relleno, SueloApoyo
from src.muro_contencion_estructural import (FACTOR_H, _franja, _momentos_zapata, _pantalla, _presion, _recubrimiento, disenar_estructura)
from src.viga import PHI_FLEXION, Materiales

M = Materiales(fc=28.0, fy=420.0)
G = GeometriaMuro(h_pantalla=3.0, h_zapata=0.5, t_corona=0.3, t_base=0.3, b_puntera=0.6, b_talon=1.6)
R = Relleno(gamma=18.0, phi_deg=30.0)
S = SueloApoyo(phi_deg=30.0, q_adm_kpa=200.0, mu_base=0.7)


def test_pantalla_momento_y_cortante_a_mano():
    # Ka = 1/3; Ph = 0.5·(1/3)·18·3² = 27 kN/m; Vu = 1.6·27 = 43.2; Mu = 1.6·27·(3/3) = 43.2 kN·m/m
    p = _pantalla(G, R, M)
    assert p.vu_kn_m == pytest.approx(43.2, rel=1e-9)
    assert p.mu_knm_m == pytest.approx(43.2, rel=1e-9)


def test_pantalla_con_sobrecarga_suma_rectangulo():
    # q = 10 kPa: Ph_q = Ka·q·h = (1/3)·10·3 = 10 kN/m a h/2 → Mu = 1.6(27·1 + 10·1.5) = 67.2
    p = _pantalla(G, Relleno(18.0, 30.0, sobrecarga_kpa=10.0), M)
    assert p.mu_knm_m == pytest.approx(67.2, rel=1e-9)
    assert p.vu_kn_m == pytest.approx(1.6 * 37.0, rel=1e-9)


def test_el_refuerzo_de_la_pantalla_resiste_el_momento():
    p = _pantalla(G, R, M)
    a = p.as_prov_mm2_m * M.fy / (0.85 * M.fc * 1000.0)
    phi_mn = PHI_FLEXION * p.as_prov_mm2_m * M.fy * (p.d_mm - a / 2.0) / 1e6
    assert phi_mn >= p.mu_knm_m and p.eps_t >= 0.005 and p.as_prov_mm2_m >= p.as_min_mm2_m
    # no está sobredimensionado: el área provista queda a un paso de 10 mm de separación de lo necesario (aquí gobierna el As mínimo C.10.5.1)
    necesario = max(p.as_req_mm2_m, p.as_min_mm2_m)
    assert p.as_prov_mm2_m <= necesario * (p.sep_mm + 10.0) / p.sep_mm * 1.0001 or p.sep_mm >= min(3 * p.h_mm, 450.0)


def test_recubrimiento_c_7_7_1():
    assert _recubrimiento("5") == 40.0 and _recubrimiento("6") == 50.0


def test_presiones_mayoradas_caso_de_mano():
    # Σ D = 138 kN/m y Mr = 200.58, Mo = 42.875 (Fase 1). Combinación A: V = 165.6; x_R = (1.2·200.58 − 1.6·42.875)/165.6
    q, qa, qb, v = _presion(G, R, 24.0, 1.2, 1.6)
    x_r = (1.2 * 200.58 - 1.6 * 42.875) / 165.6
    e = 1.25 - x_r
    assert v == pytest.approx(165.6, rel=1e-9)
    assert qa == pytest.approx(165.6 / 2.5 * (1 + 6 * e / 2.5), rel=2e-4)
    assert (qa + qb) / 2.0 * 2.5 == pytest.approx(v, rel=1e-9)


def test_momento_de_la_puntera_a_mano():
    # q(x) lineal de q_punta a q_talón; puntera 0.6 m; propio 1.2·24·0.5 = 14.4. M = ∫0^0.6 (q(x) − 14.4)(0.6 − x) dx
    _, qa, qb, _ = _presion(G, R, 24.0, 1.2, 1.6)
    k = (qb - qa) / 2.5
    esperado_a = (qa - 14.4) * 0.6**2 / 2 + k * 0.6**3 / 6
    z = _momentos_zapata(G, R, 24.0, 0.4)
    assert z["mu_p"] >= esperado_a - 1e-6
    assert esperado_a == pytest.approx(14.40, abs=0.1)        # cálculo manual independiente del enunciado de la prueba


def test_momento_del_talon_es_el_mayor_de_las_dos_combinaciones():
    # talón de 1.6 m, uniforme w − q lineal; se evalúa A y B en forma cerrada y se exige la envolvente
    def talon(f_d, f_q):
        q, qa, qb, _ = _presion(G, R, 24.0, f_d, f_q)
        k = (qb - qa) / 2.5
        w = f_d * (24.0 * 0.5 + 18.0 * 3.0)
        q_h = qa + k * 0.9                                     # presión en la cara posterior (x = 0.9)
        n0 = w - q_h
        return n0 * 1.6**2 / 2 + (-k) * 1.6**3 / 3
    esperado = max(talon(1.2, 1.6), talon(0.9, 0.0))
    z = _momentos_zapata(G, R, 24.0, 0.4)
    assert z["mu_t"] == pytest.approx(esperado, rel=5e-3)


def test_un_muro_holgado_cumple_y_reporta_costo_y_co2():
    g = GeometriaMuro(3.0, 0.5, 0.3, 0.4, 0.6, 2.6)
    d = disenar_estructura(g, R, SueloApoyo(30.0, 200.0, c_kpa=10.0), M)
    assert d.cumple, d.motivos
    assert d.acero_kg_m > 0 and d.costo_cop_m > 0 and d.co2_kg_m > 0
    assert d.pantalla.cumple and d.puntera.cumple and d.talon.cumple


def test_el_costo_crece_con_la_altura():
    s = SueloApoyo(30.0, 300.0, c_kpa=20.0)
    a = disenar_estructura(GeometriaMuro(2.5, 0.5, 0.3, 0.35, 0.6, 2.2), R, s, M)
    b = disenar_estructura(GeometriaMuro(3.5, 0.6, 0.3, 0.5, 0.7, 3.0), R, s, M)
    assert a.cumple and b.cumple and b.costo_cop_m > a.costo_cop_m and b.acero_kg_m > a.acero_kg_m


def test_pantalla_delgada_falla_por_cortante_o_flexion():
    f = _franja("x", 400.0, 400.0, 200.0, _recubrimiento, M)
    assert not f.cumple


def test_un_muro_inestable_no_cumple_aunque_el_acero_alcance():
    d = disenar_estructura(G, R, SueloApoyo(30.0, 200.0), M)        # el caso de mano falla solo por deslizamiento (Fase 1)
    assert not d.cumple and any("deslizamiento" in m for m in d.motivos)


def test_supuestos_incluyen_lo_no_verificado():
    d = disenar_estructura(GeometriaMuro(3.0, 0.5, 0.3, 0.4, 0.6, 2.6), R, SueloApoyo(30.0, 200.0, c_kpa=10.0), M)
    assert any("desarrollo" in s for s in d.supuestos) and FACTOR_H == 1.6
