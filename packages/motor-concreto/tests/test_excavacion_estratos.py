"""Estratos horizontales y Método B de refuerzos en el Bishop de excavaciones (#241): retrocompatibilidad, cálculos a mano y monotonía."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src.excavacion_estabilidad import (EstratoExc, Refuerzo, SueloExc, _capas, _fs_circulo, _peso_y_resistencia, factor_seguridad_talud,
                                        perfil_talud)

ARENA = SueloExc(18.0, 5.0, 30.0)
H = 6.0


def _fs(estratos=(), **kw):
    return factor_seguridad_talud(perfil_talud(H, 60.0), ARENA, grieta_traccion=False, estratos=estratos, **kw).fs


def test_estrato_identico_no_cambia_el_fs():
    assert _fs((EstratoExc(2.0, ARENA),)) == pytest.approx(_fs(), rel=1e-9)


def test_estrato_fuera_del_dominio_no_cambia_el_fs():
    assert _fs((EstratoExc(-50.0, SueloExc(20.0, 0.0, 10.0)),)) == pytest.approx(_fs(), rel=1e-9)


def test_estrato_inferior_mas_resistente_sube_el_fs_y_mas_debil_lo_baja():
    base = _fs()
    assert _fs((EstratoExc(2.0, SueloExc(18.0, 5.0, 40.0)),)) > base
    assert _fs((EstratoExc(2.0, SueloExc(18.0, 2.0, 22.0)),)) < base


def test_peso_y_resistencia_a_mano():
    # Columna de y = 10 a y = 0 con techos en 6 y 2; agua en y = 4; ancho 0,5 m.
    capas = _capas(SueloExc(18.0, 0.0, 33.0), (EstratoExc(6.0, SueloExc(19.0, 3.0, 35.0, 21.0)),
                                               EstratoExc(2.0, SueloExc(20.0, 0.0, 39.0, 22.0))))
    w, c, tf = _peso_y_resistencia(np.array([10.0]), np.array([0.0]), 0.5, 4.0, capas)
    # 4 m × 18 + (2 m × 19 sobre el agua + 2 m × 21 bajo) + 2 m × 22, todo × 0,5
    assert w[0] == pytest.approx((4 * 18 + 2 * 19 + 2 * 21 + 2 * 22) * 0.5)
    assert c[0] == 0.0 and tf[0] == pytest.approx(math.tan(math.radians(39.0)))
    w2, c2, tf2 = _peso_y_resistencia(np.array([10.0]), np.array([3.0]), 1.0, None, capas)
    assert w2[0] == pytest.approx(4 * 18 + 3 * 19) and c2[0] == 3.0 and tf2[0] == pytest.approx(math.tan(math.radians(35.0)))


def test_adherencia_por_estratos_a_mano():
    # Clavo a 30° desde y = 5, 8 m de largo: cruza y = 3 en s = 4 m. Arriba 10 kN/m/m, abajo 25.
    r = Refuerzo(0.0, 5.0, 30.0, 8.0, 1e3, 10.0, 1e3, adherencia_estratos=((3.0, 25.0),))
    assert r.adherencia_tramo(0.0, 8.0) == pytest.approx(4 * 10 + 4 * 25)
    assert r.adherencia_tramo(2.0, 6.0) == pytest.approx(2 * 10 + 2 * 25)
    assert r.adherencia_tramo(5.0, 7.0) == pytest.approx(2 * 25)
    plano = Refuerzo(0.0, 5.0, 0.0, 8.0, 1e3, 10.0, 1e3, adherencia_estratos=((3.0, 25.0),))
    assert plano.adherencia_tramo(0.0, 8.0) == pytest.approx(80.0)        # horizontal sobre el techo: no lo cruza


def test_rechazos():
    with pytest.raises(ValueError):
        _fs((EstratoExc(1.0, ARENA), EstratoExc(3.0, ARENA)))           # orden ascendente
    with pytest.raises(ValueError):
        Refuerzo(0.0, 5.0, 15.0, 8.0, 1.0, 1.0, 1.0, adherencia_estratos=((1.0, 2.0), (3.0, 2.0)))
    with pytest.raises(ValueError):
        Refuerzo(0.0, 5.0, 15.0, 8.0, 1.0, 1.0, 1.0, adherencia_estratos=((3.0, -2.0),))


def test_metodo_b_relacion_exacta_con_el_a_en_phi_cero():
    # φ = 0 y clavo horizontal: mα = cos α y no hay término normal. Con S, D y R (resistente del suelo, motor y aporte
    # del clavo): FS0 = S/D, FS_A = S/(D − R), FS_B = (S + R)/D  →  FS_B = FS0 + 1 − FS0/FS_A.
    perfil = perfil_talud(6.0, 90.0)
    arcilla = SueloExc(18.0, 30.0, 0.0)
    clavo = Refuerzo(1e-6, 3.0, 0.0, 9.0, 60.0, 15.0, 60.0)
    xc, yc, r = 1.0, 8.0, 8.06
    args = (perfil, arcilla, None, 0.0, (0.0, 0.0), 0.0, 0.0)
    fs0 = _fs_circulo(xc, yc, r, *args, (), True)
    fa = _fs_circulo(xc, yc, r, *args, (clavo,), True)
    fb = _fs_circulo(xc, yc, r, *args, (clavo,), True, (), "B")
    assert fs0 < fb < fa
    assert fb == pytest.approx(fs0 + 1.0 - fs0 / fa, rel=1e-9)


def test_metodo_invalido():
    with pytest.raises(ValueError):
        factor_seguridad_talud(perfil_talud(H, 60.0), ARENA, metodo_refuerzo="C")
