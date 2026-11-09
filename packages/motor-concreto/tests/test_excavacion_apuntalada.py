"""Pantalla apoyada: empotramiento contra la ecuación de equilibrio de momentos en el apoyo (suelo granular, puntal en cabeza) y propiedades."""
import math

import pytest
from scipy.optimize import brentq

from src.excavacion_apuntalada import dimensionar_apuntalada
from src.excavacion_estabilidad import SueloExc


def test_empotramiento_coincide_con_cierre_granular_puntal_en_cabeza():
    # momentos en la cabeza (c=0, q=0): Ka*(H+D)^3/3 = (Kp/FS) * (H*D^2/2 + D^3/3)
    s, h, fs = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0), 4.0, 1.5
    ka, kp = 1 / 3, 3.0
    esperado = brentq(lambda d: ka * (h + d) ** 3 / 3 - (kp / fs) * (h * d**2 / 2 + d**3 / 3), 1e-3, 50.0)
    r = dimensionar_apuntalada(s, h, 0.0, 0.0, fs, factor_longitud=1.0)
    assert r.empotramiento_m == pytest.approx(esperado, rel=0.01)


def test_reaccion_cierra_el_equilibrio_horizontal_y_es_positiva():
    s = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0)
    h, fs = 4.0, 1.5
    r = dimensionar_apuntalada(s, h, 0.0, 0.0, fs, factor_longitud=1.0)
    d = r.empotramiento_m
    # fuerza = activo total - pasivo reducido
    esperado = 0.5 * (1 / 3) * 18.0 * (h + d) ** 2 - 0.5 * 3.0 * 18.0 * d**2 / fs
    assert r.reaccion_apoyo_kn_por_m == pytest.approx(esperado, rel=0.01) and r.reaccion_apoyo_kn_por_m > 0


def test_apoyo_reduce_el_empotramiento_respecto_del_voladizo_y_el_momento():
    from src.excavacion_contencion import dimensionar_voladizo
    s = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0)
    v = dimensionar_voladizo(s, 4.0, 0.0, 1.5, 6.0, 0.0, factor_longitud=1.0)
    a = dimensionar_apuntalada(s, 4.0, 0.0, 0.0, 1.5, factor_longitud=1.0)
    assert a.empotramiento_m < v.empotramiento_m and a.momento_max_knm_por_m < v.momento_max_knm_por_m


def test_apoyo_profundo_coincide_con_el_equilibrio_de_momentos_en_el_apoyo():
    # momentos respecto de z=a (c=0, q=0): integral_0^(H+D) Ka*g*z*(z-a) dz = integral_H^(H+D) (Kp*g/FS)*(z-H)*(z-a) dz
    from scipy.integrate import quad
    s, h, a, fs = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0), 5.0, 3.0, 1.5
    def resid(d):
        act = quad(lambda z: (1 / 3) * 18.0 * z * (z - a), 0.0, h + d)[0]
        pas = quad(lambda z: (3.0 * 18.0 / fs) * (z - h) * (z - a), h, h + d)[0]
        return act - pas
    esperado = brentq(resid, 1e-3, 60.0)
    assert dimensionar_apuntalada(s, h, a, 0.0, fs, factor_longitud=1.0).empotramiento_m == pytest.approx(esperado, rel=0.01)


def test_monotonia_altura_sobrecarga_y_profundidad_del_apoyo():
    s = SueloExc(gamma=18.0, c_kpa=0.0, phi_deg=30.0)
    base = dimensionar_apuntalada(s, 5.0, 1.0, 0.0, 1.5, factor_longitud=1.0)
    assert dimensionar_apuntalada(s, 7.0, 1.0, 0.0, 1.5, factor_longitud=1.0).empotramiento_m > base.empotramiento_m
    assert dimensionar_apuntalada(s, 5.0, 1.0, 20.0, 1.5, factor_longitud=1.0).empotramiento_m > base.empotramiento_m


def test_phi_cero_sin_solucion_y_validaciones():
    assert dimensionar_apuntalada(SueloExc(18.0, 30.0, 0.0), 5.0, 0.0, 10.0, 1.5, factor_longitud=1.0).sin_solucion
    with pytest.raises(ValueError):
        dimensionar_apuntalada(SueloExc(18.0, 0.0, 30.0), 5.0, 5.0, 0.0, 1.5, factor_longitud=1.0)
    with pytest.raises(TypeError):
        dimensionar_apuntalada(SueloExc(18.0, 0.0, 30.0), 5.0, 1.0, 0.0, 1.5)
    assert math.isfinite(dimensionar_apuntalada(SueloExc(18.0, 5.0, 28.0), 5.0, 1.0, 10.0, 1.5, factor_longitud=1.2).momento_max_knm_por_m)
