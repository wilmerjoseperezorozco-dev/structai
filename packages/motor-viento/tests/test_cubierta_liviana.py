"""Verificación (no validación) de la cubierta liviana bajo succión: cálculos a mano y propiedades."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import b6
from src.cubierta_liviana import CubiertaLiviana, separacion_maxima, succion, verificar


def cub(**kw):
    base = dict(theta_deg=5.0, peso_kpa=0.1, separacion_correas_m=1.0, luz_correas_m=5.0, separacion_fijaciones_m=0.3,
                phi_rn_fijacion_kn=1.5, phi_mn_correa_inversa_knm=4.0, phi_rn_anclaje_kn=8.0)
    base.update(kw)
    return CubiertaLiviana(**base)


def test_fijacion_a_mano():
    qh = 0.73
    r = {z.zona: z for z in verificar(qh, cub())}
    a = 0.3                                                   # < 1 m²: meseta de la Fig. B.6.5-8B
    p3 = qh * (-2.8 - 0.18)
    assert r["3"].p_kpa == pytest.approx(p3)
    assert r["3"].tu_fijacion_kn == pytest.approx((1.6 * abs(p3) - 0.9 * 0.1) * a)
    assert r["3"].s_max_fijaciones_m == pytest.approx(1.5 / ((1.6 * abs(p3) - 0.9 * 0.1) * 1.0))


def test_correa_y_anclaje_a_mano():
    qh, L, s = 0.73, 5.0, 1.0
    r = {z.zona: z for z in verificar(qh, cub())}
    area = max(L * s, L * L / 3)                              # 8,33 m²
    gcp = b6.gcp_cubierta("2", area, 5.0)
    wu = (1.6 * qh * (abs(gcp) + 0.18) - 0.9 * 0.1) * s
    assert r["2"].mu_correa_knm == pytest.approx(wu * L * L / 8)
    assert r["2"].ru_anclaje_kn == pytest.approx(wu * L)


def test_esquina_gobierna_y_peso_alto_anula():
    r = verificar(0.73, cub())
    assert max(r, key=lambda z: z.tu_fijacion_kn).zona == "3"
    pesada = verificar(0.73, cub(peso_kpa=10.0))
    assert all(z.tu_fijacion_kn == 0 and z.cumple for z in pesada)
    assert separacion_maxima(-0.5, 1.0, 1.0, peso_kpa=5.0) == math.inf


def test_alero_sin_presion_interna():
    r = {z.zona: z for z in verificar(0.73, cub(alero_m=0.6))}
    assert r["alero 3"].p_kpa == pytest.approx(0.73 * -2.8)
    assert succion(0.73, "2", 0.3, 20.0, 0.18, alero=True) == pytest.approx(0.73 * -2.2)


def test_capacidad_insuficiente_no_cumple():
    assert not all(z.cumple for z in verificar(0.73, cub(phi_rn_fijacion_kn=0.2)))
    with pytest.raises(ValueError):
        cub(separacion_correas_m=0.0)
