"""Contrafuertes y tirantes del muro de contención: esperados a mano (geometría, equilibrio, momentos de losas y del contrafuerte, longitudes del anclaje)."""
import math
import warnings

import pytest

from src.economia_concreto import Economia
from src.muro_anclaje import (AREA_CORDON_MM2, D_PERFORACION_M, FPU_MPA, SEP_ANCLAJES_M, TAU_ADHERENCIA_KPA, costo_co2_anclaje, disenar_anclaje)
from src.muro_contencion import GeometriaMuro, Relleno, SueloApoyo, fuerza_anclaje, verificar_estabilidad
from src.muro_contencion_estructural import disenar_estructura
from src.muro_optimizador import CasoMuro, TIPOLOGIAS, TIPOLOGIAS_EXTENDIDAS, optimizar, optimizar_todas
from src.viga import Materiales

warnings.filterwarnings("ignore")
R = Relleno(18.0, 30.0)
S = SueloApoyo(30.0, 200.0)
M = Materiales(28.0, 420.0)
MU = math.tan(math.radians(20.0))
G0 = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6)
GCF = GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, contrafuerte_sep=3.0, contrafuerte_esp=0.3)


# ----------------------------------------------------------------------------------------------------------------------------------- contrafuertes
def test_contrafuerte_suma_el_peso_neto_y_el_volumen_del_triangulo():
    a = verificar_estabilidad(G0, R, S)
    b = verificar_estabilidad(GCF, R, S)
    cf = 0.5 * 3.0 * 1.6 * 0.3 / 3.0                     # m³ por metro de muro
    assert b.sum_v_kn_m == pytest.approx(a.sum_v_kn_m + cf * (24.0 - 18.0))
    assert b.volumen_concreto_m3_m == pytest.approx(a.volumen_concreto_m3_m + cf)
    assert b.empuje_kn_m == pytest.approx(a.empuje_kn_m)            # el plano virtual del talón no cambia


def test_contrafuerte_desplaza_el_momento_estabilizante_con_su_centroide():
    b = verificar_estabilidad(GCF, R, S)
    extra = 0.24 * 6.0 * (0.6 + 0.3 + 1.6 / 3.0)                    # peso neto × x del centroide del triángulo
    assert b.fs_volcamiento == pytest.approx((200.58 + extra) / (36.75 * 3.5 / 3.0), rel=1e-4)


def test_pantalla_con_contrafuerte_es_de_espesor_uniforme():
    assert float(GCF.espesor_pantalla(0.0)) == pytest.approx(0.3) and float(GCF.espesor_pantalla(3.0)) == pytest.approx(0.3)


def test_losa_de_pantalla_entre_contrafuertes_momento_wL2_sobre_12():
    d = disenar_estructura(GCF, R, S, M)
    w = 1.6 * (1.0 / 3.0) * 18.0 * 3.0                              # 1,6·Ka·γ·h en la base = 28,8 kPa
    luz = 3.0 - 0.3
    assert d.contrafuerte.luz_libre_m == pytest.approx(luz)
    assert d.contrafuerte.pantalla.mu_knm_m == pytest.approx(w * luz**2 / 12.0, rel=1e-6)
    assert d.contrafuerte.pantalla.vu_kn_m == pytest.approx(w * luz / 2.0, rel=1e-6)


def test_momento_del_contrafuerte_es_la_separacion_por_el_de_la_pantalla():
    d = disenar_estructura(GCF, R, S, M)
    m_base = 1.6 * 0.5 * (1.0 / 3.0) * 18.0 * 3.0**2 * 3.0 / 3.0     # 43,2 kN·m/m
    assert d.contrafuerte.mu_cf_knm == pytest.approx(3.0 * m_base, rel=1e-4)
    assert d.contrafuerte.vu_cf_kn == pytest.approx(3.0 * 1.6 * 27.0, rel=1e-4)
    assert d.contrafuerte.d_cf_mm == pytest.approx((0.3 + 1.6) * 1000.0 - 100.0)


def test_acero_principal_del_contrafuerte_cubre_la_demanda_inclinada():
    c = disenar_estructura(GCF, R, S, M).contrafuerte
    cos_psi = 3.0 / math.hypot(3.0, 1.6)
    as_v = c.as_req_cf_mm2 * cos_psi                                  # componente vertical de la fuerza de la barra inclinada
    a = as_v * 420.0 / (0.85 * 28.0 * 300.0)
    assert 0.9 * as_v * 420.0 * (c.d_cf_mm - a / 2.0) / 1e6 == pytest.approx(c.mu_cf_knm, rel=1e-6)      # equilibrio de momentos con el bloque rectangular
    assert c.as_prov_cf_mm2 >= c.as_req_cf_mm2 and c.n_barras_cf >= 2


def test_contrafuerte_exige_pantalla_uniforme_y_sin_bandeja():
    with pytest.raises(ValueError):
        verificar_estabilidad(GeometriaMuro(3.0, 0.5, 0.2, 0.3, 0.6, 1.6, contrafuerte_sep=3.0), R, S)
    with pytest.raises(ValueError):
        verificar_estabilidad(GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, contrafuerte_sep=3.0, bandeja_y=1.2, bandeja_vuelo=0.8), R, S)
    with pytest.raises(ValueError):
        verificar_estabilidad(GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, contrafuerte_sep=0.2, contrafuerte_esp=0.3), R, S)


# ----------------------------------------------------------------------------------------------------------------------------------------- anclajes
def _ancla(t=10.0, y=2.0, ang=20.0):
    return GeometriaMuro(3.0, 0.5, 0.3, 0.3, 0.6, 1.6, anc_fuerza_kn_m=t, anc_y=y, anc_incl_deg=ang)


def test_componentes_del_tirante():
    th, tv, x, y = fuerza_anclaje(_ancla())
    assert th == pytest.approx(10.0 * math.cos(math.radians(20.0))) and tv == pytest.approx(10.0 * math.sin(math.radians(20.0)))
    assert x == pytest.approx(0.9) and y == pytest.approx(2.5)
    assert fuerza_anclaje(G0) == (0.0, 0.0, 0.0, 0.0)


def test_equilibrio_con_tirante_caso_de_mano():
    th, tv = 10.0 * math.cos(math.radians(20.0)), 10.0 * math.sin(math.radians(20.0))
    r = verificar_estabilidad(_ancla(), R, S)
    assert r.fs_deslizamiento == pytest.approx(MU * (138.0 + tv) / (36.75 - th), rel=1e-6)
    assert r.fs_volcamiento == pytest.approx((200.58 + tv * 0.9) / (36.75 * 3.5 / 3.0 - th * 2.5), rel=1e-4)
    assert r.sum_v_kn_m == pytest.approx(138.0 + tv)


def test_el_tirante_mejora_deslizamiento_y_volcamiento_de_forma_monotona():
    fs = [verificar_estabilidad(_ancla(t), R, S) for t in (0.0, 4.0, 8.0, 12.0)]
    assert all(a.fs_deslizamiento < b.fs_deslizamiento and a.fs_volcamiento < b.fs_volcamiento for a, b in zip(fs[:-1], fs[1:]))


def test_tirante_muy_fuerte_deja_volcamiento_infinito_sin_dividir_por_cero():
    assert math.isinf(verificar_estabilidad(_ancla(200.0, 2.9, 5.0), R, S).fs_volcamiento)


def test_dimensionamiento_del_anclaje_longitudes_y_cordones():
    g = _ancla(60.0, 2.0, 15.0)
    a = disenar_anclaje(g, R)
    f = 60.0 * SEP_ANCLAJES_M
    assert a.fuerza_ancla_kn == pytest.approx(f)
    assert a.n_cordones == math.ceil(f / (0.6 * FPU_MPA * AREA_CORDON_MM2 / 1000.0))
    assert a.l_fija_m == pytest.approx(max(f * 2.0 / (math.pi * D_PERFORACION_M * TAU_ADHERENCIA_KPA), 3.0))
    x_a, y_a, B = 0.6 + 0.3, 0.5 + 2.0, g.ancho_base
    t, tf = math.tan(math.radians(15.0)), math.tan(math.radians(45.0 + 15.0))
    x_int = (y_a + x_a * t + B * tf) / (t + tf)
    assert a.l_libre_m == pytest.approx(max((x_int - x_a) / math.cos(math.radians(15.0)) + 1.5, 4.5))
    assert y_a - (x_int - x_a) * t == pytest.approx((x_int - B) * tf)      # el cruce está sobre el tirante y sobre la superficie de falla


def test_cantidades_y_costo_por_metro_de_muro():
    a = disenar_anclaje(_ancla(60.0, 2.0, 15.0), R)
    largo = a.l_libre_m + a.l_fija_m
    assert a.longitud_perforada_m_m == pytest.approx(largo / SEP_ANCLAJES_M)
    assert a.kg_cordon_m == pytest.approx(a.n_cordones * 140e-6 * largo * 7850.0 / SEP_ANCLAJES_M)
    eco = Economia()
    c, co2 = costo_co2_anclaje(a, eco)
    assert c == pytest.approx(a.longitud_perforada_m_m * 180_000.0 + 450_000.0 / SEP_ANCLAJES_M + a.kg_cordon_m * eco.p_acero * 2.5)
    assert co2 == pytest.approx(a.kg_cordon_m * eco.fe_acero + a.cemento_kg_m * eco.fe_cemento)


def test_anclaje_demasiado_fuerte_falla_por_longitud_fija():
    a = disenar_anclaje(_ancla(180.0, 2.0, 15.0), R)
    assert not a.cumple and any("longitud fija" in m for m in a.motivos)


def test_diseno_con_tirante_suma_su_costo_y_su_acero():
    rel = Relleno(18.0, 30.0, 0.0, 10.0)
    g = GeometriaMuro(6.0, 0.6, 0.25, 0.6, 0.8, 2.6, anc_fuerza_kn_m=60.0, anc_y=4.8, anc_incl_deg=15.0)
    d = disenar_estructura(g, rel, S, M)
    assert d.anclaje is not None and d.anclaje.cumple
    sin = disenar_estructura(GeometriaMuro(6.0, 0.6, 0.25, 0.6, 0.8, 2.6), rel, S, M)
    c, _ = costo_co2_anclaje(d.anclaje, Economia())
    assert d.costo_cop_m > c and d.acero_kg_m > d.anclaje.kg_cordon_m
    assert d.estabilidad.fs_deslizamiento > sin.estabilidad.fs_deslizamiento


def test_anclaje_invalido_lanza_error():
    with pytest.raises(ValueError):
        verificar_estabilidad(_ancla(10.0, 3.5), R, S)           # cota fuera de la pantalla
    with pytest.raises(ValueError):
        verificar_estabilidad(_ancla(10.0, 2.0, 70.0), R, S)


# ------------------------------------------------------------------------------------------------------------------------------------- optimizador
CASO_FACIL = CasoMuro(5.0, Relleno(18.0, 30.0, 0.0, 10.0), SueloApoyo(30.0, 200.0), a_max_g=0.2)


def test_las_tipologias_nuevas_no_cambian_el_conjunto_por_defecto():
    assert set(optimizar_todas(CASO_FACIL)) == {"tradicional", *TIPOLOGIAS}
    assert set(optimizar_todas(CASO_FACIL, tipologias=TIPOLOGIAS_EXTENDIDAS)) == {"tradicional", *TIPOLOGIAS_EXTENDIDAS}


@pytest.mark.parametrize("tip", ["contrafuerte", "anclaje"])
def test_optimizador_encuentra_diseno_que_cumple(tip):
    s = optimizar(CASO_FACIL, tip)
    assert s is not None and s.diseno.cumple
    if tip == "contrafuerte":
        assert s.geometria.tiene_contrafuerte and s.geometria.t_corona == s.geometria.t_base
    else:
        assert s.geometria.tiene_anclaje and s.diseno.anclaje.cumple
