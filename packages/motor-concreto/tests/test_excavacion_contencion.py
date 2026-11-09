"""Voladizo: cierre analítico para suelo granular (c=0, sin sobrecarga) y propiedades de monotonía."""
import math

import pytest

from src.excavacion_contencion import dimensionar_voladizo
from src.excavacion_estabilidad import SueloExc


def test_empotramiento_coincide_con_cierre_granular():
    # equilibrio de momentos en la base: Ka (H+D)^3 = Kp D^3 / FS  ->  (H+D)/D = (Kp/(Ka FS))^(1/3)
    s = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0)
    ka, kp, fs, h = 1 / 3, 3.0, 1.5, 4.0
    r = (kp / (ka * fs)) ** (1 / 3)
    esperado = h / (r - 1.0)
    p = dimensionar_voladizo(s, h, 0.0, fs, h_max_voladizo=6.0, empotramiento_min_m=0.0, factor_longitud=1.0)
    assert p.empotramiento_m == pytest.approx(esperado, rel=0.01)
    assert p.longitud_total_m == pytest.approx(h + p.empotramiento_m)


def test_momento_maximo_cierre_granular():
    # Para c=0 y q=0: M(z) = Ka*gamma*z^3/6 en la zona libre; el máximo está bajo la excavación y es positivo y finito
    s = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0)
    p = dimensionar_voladizo(s, 4.0, 0.0, 1.5, 6.0, 0.0, factor_longitud=1.0)
    cota = (1 / 3) * 18.0 * 4.0**3 / 6.0       # momento a nivel del fondo: 64 kN·m/m, cota inferior del máximo
    assert p.momento_max_knm_por_m >= cota * 0.99


def test_monotonia_altura_sobrecarga_y_fs():
    s = SueloExc(gamma=18.0, c_kpa=5.0, phi_deg=28.0)
    base = dimensionar_voladizo(s, 3.0, 0.0, 1.5, 6.0, 0.0, factor_longitud=1.0)
    assert dimensionar_voladizo(s, 4.0, 0.0, 1.5, 6.0, 0.0, factor_longitud=1.0).empotramiento_m > base.empotramiento_m
    assert dimensionar_voladizo(s, 3.0, 20.0, 1.5, 6.0, 0.0, factor_longitud=1.0).empotramiento_m > base.empotramiento_m
    assert dimensionar_voladizo(s, 3.0, 0.0, 2.0, 6.0, 0.0, factor_longitud=1.0).empotramiento_m > base.empotramiento_m
    assert dimensionar_voladizo(SueloExc(18.0, 10.0, 28.0), 3.0, 0.0, 1.5, 6.0, 0.0, factor_longitud=1.0).empotramiento_m < base.empotramiento_m


def test_altura_mayor_al_limite_requiere_apoyos_y_validacion():
    s = SueloExc(gamma=18.0, c_kpa=5.0, phi_deg=28.0)
    r = dimensionar_voladizo(s, 7.0, 0.0, 1.5, h_max_voladizo=5.0, empotramiento_min_m=0.0, factor_longitud=1.0)
    assert r.requiere_apoyos and r.longitud_total_m is None
    with pytest.raises(ValueError):
        dimensionar_voladizo(s, 3.0, 0.0, 0.9, 5.0, 0.0, factor_longitud=1.0)


def test_cohesion_que_anula_el_empuje_activo_deja_el_piso_practico():
    s = SueloExc(gamma=18.0, c_kpa=20.0, phi_deg=28.0)        # 2c*sqrt(Ka) > Ka*gamma*H: sin empuje neto
    assert dimensionar_voladizo(s, 3.0, 0.0, 1.5, 6.0, empotramiento_min_m=1.0, factor_longitud=1.0).empotramiento_m == pytest.approx(1.0)


def test_phi_cero_sin_resistencia_pasiva_suficiente_pide_apoyos_en_vez_de_lanzar():
    r = dimensionar_voladizo(SueloExc(gamma=18.0, c_kpa=30.0, phi_deg=0.0), 5.0, 10.0, 1.5, 6.0, 1.0, factor_longitud=1.0)
    assert r.requiere_apoyos and r.empotramiento_m is None


def test_factor_longitud_escala_el_empotramiento_y_es_obligatorio():
    s = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0)
    a = dimensionar_voladizo(s, 4.0, 0.0, 1.5, 6.0, 0.0, factor_longitud=1.0)
    b = dimensionar_voladizo(s, 4.0, 0.0, 1.5, 6.0, 0.0, factor_longitud=1.3)
    assert b.empotramiento_m == pytest.approx(1.3 * a.empotramiento_m)
    with pytest.raises(TypeError):
        dimensionar_voladizo(s, 4.0, 0.0, 1.5, 6.0, 0.0)
