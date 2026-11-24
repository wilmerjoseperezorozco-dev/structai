"""Verificación (no validación) de las dos cuñas con equilibrio de fuerzas, v3 (#241): soluciones cerradas y propiedades."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.cunas import buscar, fs_cunas
from src.suelo_cosido import EST, Capacidades, FilaClavos, analizar

H = 6.0


def _capas(g=18.0, c=10.0, phi=30.0, estratos=()):
    return EST._capas(EST.SueloExc(g, c, phi), estratos)


def _plano(xe, g, c, phi, H=H):
    """FS de un plano del pie a (xe, H) por Culmann: (c·L + W·cosθ·tanφ) / (W·sinθ)."""
    th = math.atan2(H, xe)
    w = 0.5 * g * H * xe
    return (c * math.hypot(xe, H) + w * math.cos(th) * math.tan(math.radians(phi))) / (w * math.sin(th))


@pytest.mark.parametrize("interfaz", ["movilizada", "horizontal"])
def test_quiebre_sobre_la_recta_es_un_plano(interfaz):
    xe = 4.0
    for fb in (0.3, 0.6):
        xb, yb = fb * xe, fb * H
        assert fs_cunas(EST, H, _capas(), xb, yb, xe, interfaz=interfaz) == pytest.approx(_plano(xe, 18, 10, 30), rel=1e-7)


def test_clavo_en_plano_con_phi_cero_a_mano():
    # Plano por el pie, φ = 0: proyectando sobre la base, Método A: F = cL / (W·sinθ − T·cos(θ + i));
    # Método B: F = (cL + T·cos(θ + i)) / (W·sinθ).
    xe, c, g, i = 4.0, 20.0, 18.0, 15.0
    clavo = EST.Refuerzo(1e-6, 3.0, i, 10.0, 30.0, 1e3, 1e3)        # gobierna la tensión: T = 30 kN/m
    th = math.atan2(H, xe)
    w, L = 0.5 * g * H * xe, math.hypot(xe, H)
    tproj = 30.0 * math.cos(th + math.radians(i))
    capas = _capas(g, c, 0.0)
    fa = fs_cunas(EST, H, capas, 0.5 * xe, 0.5 * H, xe, refuerzos=(clavo,))
    fb = fs_cunas(EST, H, capas, 0.5 * xe, 0.5 * H, xe, refuerzos=(clavo,), metodo="B")
    assert fa == pytest.approx(c * L / (w * math.sin(th) - tproj), rel=1e-7)
    assert fb == pytest.approx((c * L + tproj) / (w * math.sin(th)), rel=1e-7)


def test_busqueda_no_supera_el_mejor_plano():
    mejor_plano = min(_plano(xe, 18, 10, 30) for xe in [0.05 * k for k in range(4, 200)])
    r = buscar(EST, H, _capas())
    assert r.fs <= mejor_plano + 1e-6


def test_sin_clavos_menor_que_bishop_en_corte_vertical():
    # Corte vertical sin refuerzo: la cuña crítica es más severa que el mejor círculo (motivo de la v3).
    bishop = EST.factor_seguridad_talud(EST.perfil_talud(H, 90.0), EST.SueloExc(18, 10, 30), grieta_traccion=False).fs
    assert buscar(EST, H, _capas()).fs < bishop


def test_estrato_identico_y_monotonia():
    identico = _capas(estratos=(EST.EstratoExc(2.0, EST.SueloExc(18, 10, 30)),))
    for xb, yb, xe in ((1.0, 1.0, 4.0), (2.0, 3.5, 3.0), (0.5, 0.0, 5.0)):          # exacto en una superficie fija
        assert fs_cunas(EST, H, identico, xb, yb, xe) == pytest.approx(fs_cunas(EST, H, _capas(), xb, yb, xe), rel=1e-9)
    base = buscar(EST, H, _capas()).fs
    assert buscar(EST, H, identico).fs == pytest.approx(base, rel=5e-3)     # la búsqueda converge a ~0,1 %
    fuerte = buscar(EST, H, _capas(estratos=(EST.EstratoExc(2.0, EST.SueloExc(18, 10, 40)),))).fs
    assert fuerte > base


def test_analizar_con_cunas_mas_capacidad_mas_fs_y_gobierna_el_menor():
    filas = [FilaClavos(d, 5.0) for d in (1.0, 2.5, 4.0, 5.5)]
    kw = dict(altura_m=H, filas=filas, inclinacion_deg=15.0, sh_m=1.5, gamma_kn_m3=18.0, c_kpa=5.0, phi_deg=30.0)
    bajo = analizar(cap=Capacidades(60.0, 15.0, 60.0), **kw)
    alto = analizar(cap=Capacidades(150.0, 40.0, 150.0), **kw)
    assert bajo["fs"] < alto["fs"]
    assert alto["fs"] == pytest.approx(min(alto["fs_circulo"], alto["fs_cuna"]))
    with pytest.raises(ValueError):
        analizar(cap=Capacidades(60.0, 15.0, 60.0), grieta_traccion=True, **kw)
    with pytest.raises(ValueError):
        analizar(cap=Capacidades(60.0, 15.0, 60.0), superficie="espiral", **kw)


def test_sismo_baja_el_fs():
    assert buscar(EST, H, _capas(), kh=0.15).fs < buscar(EST, H, _capas()).fs


def test_perfil_muro_y_plano_con_bateria_a_mano():
    from src.suelo_cosido import perfil_muro
    p = perfil_muro(9.5, 10.0, 20.0, 6.0)
    xc = 9.5 * math.tan(math.radians(10.0))
    assert p.x_cresta == pytest.approx(xc) and float(p.terreno(xc + 6.0)) == pytest.approx(9.5 + 6.0 * math.tan(math.radians(20)))
    assert float(p.terreno(xc + 50.0)) == pytest.approx(9.5 + 6.0 * math.tan(math.radians(20)))
    # Paramento con batería y corona horizontal: plano del pie a (xe, H), área = H·(xe − xc)/2.
    q = perfil_muro(H, 10.0)
    xc, xe, g, c, phi = H * math.tan(math.radians(10.0)), 5.0, 18.0, 10.0, 30.0
    th, w = math.atan2(H, xe), 0.5 * g * H * (xe - H * math.tan(math.radians(10.0)))
    esperado = (c * math.hypot(xe, H) + w * math.cos(th) * math.tan(math.radians(phi))) / (w * math.sin(th))
    assert fs_cunas(EST, q, _capas(g, c, phi), 0.4 * xe, 0.4 * H, xe) == pytest.approx(esperado, rel=1e-3)


def test_base_que_sale_del_terreno_se_descarta():
    from src.suelo_cosido import perfil_muro
    q = perfil_muro(H, 30.0)
    # quiebre por encima del paramento inclinado: la base inferior sale por la cara
    assert fs_cunas(EST, q, _capas(), 0.5, 5.0, 6.0) == 1.0e3


def test_cabezas_sobre_el_paramento_inclinado():
    from src.suelo_cosido import refuerzos
    refs = refuerzos(9.5, [FilaClavos(1.0, 7.7)], 15.0, 1.5, Capacidades(118.0, 30.0, 90.0), bateria_deg=10.0)
    assert refs[0].x_cabeza == pytest.approx(8.5 * math.tan(math.radians(10.0))) and refs[0].y_cabeza == 8.5
