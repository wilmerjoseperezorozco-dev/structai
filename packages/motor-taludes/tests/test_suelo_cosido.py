"""Verificación (no validación) del Bishop con clavos, versión 2 (#241): propiedades que deben cumplirse."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.suelo_cosido import EST, Capacidades, FilaClavos, analizar

SUELO = dict(gamma_kn_m3=19.0, c_kpa=5.0, phi_deg=32.0)
FILAS = [FilaClavos(d, 6.0) for d in (1.0, 2.5, 4.0, 5.5, 7.0)]


def _fs(cap, filas=FILAS, **kw):
    return analizar(altura_m=8.0, filas=filas, inclinacion_deg=15.0, sh_m=1.5, cap=cap, **SUELO, **kw)


def test_sin_capacidad_los_clavos_no_aportan():
    perfil = EST.perfil_talud(8.0, 90.0)
    base = EST.factor_seguridad_talud(perfil, EST.SueloExc(19.0, 5.0, 32.0), grieta_traccion=False,
                                      paramento_continuo=True).fs
    assert _fs(Capacidades(0.0, 0.0, 0.0))["fs"] == pytest.approx(base, rel=1e-3)


def test_mas_capacidad_mas_fs():
    fs = [_fs(Capacidades(t, t / 3.0, t))["fs"] for t in (20.0, 60.0, 120.0)]
    assert fs[0] < fs[1] < fs[2]


def test_paramento_continuo_no_sale_por_la_cara():
    r = _fs(Capacidades(150.0, 40.0, 150.0))
    c = r["circulo"]
    perfil = EST.perfil_talud(8.0, 90.0)
    # punto de salida izquierdo del círculo crítico: a la altura del pie o por debajo
    x_izq = c["xc"] - math.sqrt(max(c["radio"] ** 2 - c["yc"] ** 2, 0.0))
    assert perfil.terreno(x_izq) <= 1e-3 * 8.0 + 1e-9


def test_sin_paramento_continuo_puede_salir_por_la_cara_y_da_menos():
    perfil = EST.perfil_talud(8.0, 90.0)
    from src.suelo_cosido import refuerzos
    refs = refuerzos(8.0, FILAS, 15.0, 1.5, Capacidades(150.0, 40.0, 150.0))
    libre = EST.factor_seguridad_talud(perfil, EST.SueloExc(19.0, 5.0, 32.0), grieta_traccion=False, refuerzos=refs).fs
    assert libre <= _fs(Capacidades(150.0, 40.0, 150.0))["fs"] + 1e-6


def test_un_clavo_que_cruza_sube_el_fs_del_mismo_circulo():
    perfil = EST.perfil_talud(8.0, 90.0)
    suelo = EST.SueloExc(19.0, 5.0, 32.0)
    r = EST.Refuerzo(x_cabeza=1e-6, y_cabeza=2.0, inclinacion_deg=15.0, longitud_m=8.0, t_tension_kn_m=60.0,
                     adherencia_kn_m_por_m=30.0, t_cabeza_kn_m=60.0)
    args = (perfil, suelo, None, 0.0, (0.0, 0.0), 0.0, 0.0)
    xc, yc = -2.0, 9.0
    sin = EST._fs_circulo(xc, yc, math.hypot(xc, yc), *args, (), True)
    con = EST._fs_circulo(xc, yc, math.hypot(xc, yc), *args, (r,), True)
    assert EST.fuerza_refuerzo(r, xc, yc, math.hypot(xc, yc))[0] > 0
    assert sin < con < EST.FS_INVALIDO


def test_rechazos():
    with pytest.raises(ValueError):
        _fs(Capacidades(10, 10, 10), filas=[FilaClavos(9.0, 6.0)])
    with pytest.raises(ValueError):
        _fs(Capacidades(10, 10, 10), filas=[])
    with pytest.raises(ValueError):
        _fs(Capacidades(10, 10, 10), sobrecarga_kpa=10.0)
