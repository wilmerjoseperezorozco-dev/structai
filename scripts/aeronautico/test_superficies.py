"""Pruebas de superficies.py con una pista sintética alineada al eje este (no depende de proyecciones).

La prueba del 2 % está fijada en el preregistro de #332: sobre el eje de la RWY 05, la aproximación de precisión
categoría I clave 4 sube exactamente 2 % desde 60 m antes del umbral (tolerancia 0,1 m).
"""
import numpy as np
import pytest

from superficies import Pista, techo

# Pista de 3 001 m sobre el eje x; umbral A en (0, 0), elevaciones como SKBQ
P = Pista((0.0, 0.0), (3001.0, 0.0), elev_a=28.96, elev_b=16.15, elev_referencia=29.0)
KW = dict(pista=P, aprox_a="precision_cat1_3_4", aprox_b="no_precision_4", despegue="clave_3_4")


@pytest.mark.parametrize("d", [0.0, 500.0, 1000.0, 2000.0, 3000.0])
def test_aproximacion_rwy05_dos_por_ciento(d):
    x = -60.0 - d
    h, _, sup = techo(np.array([x]), np.array([0.0]), detalle=True, **KW)
    assert sup["aproximacion_a"][0] == pytest.approx(28.96 + 0.02 * d, abs=0.1)
    # El techo es la superficie más baja: la aproximación manda mientras esté por debajo de la horizontal interna
    # (74 m); más lejos manda la horizontal interna.
    assert h[0] == pytest.approx(min(28.96 + 0.02 * d, 74.0), abs=0.1)


def test_segunda_seccion_y_horizontal():
    # 3 000 m al 2 % = 60 m; después 2,5 % hasta 150 m sobre el umbral (3 600 m), luego horizontal
    for d, esperado in ((4000.0, 60 + 0.025 * 1000), (6600.0, 150.0), (12000.0, 150.0)):
        h, limita, sup = techo(np.array([-60.0 - d]), np.array([0.0]), detalle=True, **KW)
        assert sup["aproximacion_a"][0] == pytest.approx(28.96 + esperado, abs=0.1)


def test_horizontal_interna_74_m():
    # Al costado de la pista, a 2 km del eje: horizontal interna = 29 + 45
    h, limita, _ = techo(np.array([1500.0]), np.array([2000.0]), detalle=True, **KW)
    assert h[0] == pytest.approx(74.0)
    assert limita[0] == "horizontal_interna"


def test_conica_5_por_ciento_y_fin():
    # A 5 km del eje (1 km pasado el radio de 4 km): 74 + 50 m; más allá de 6 km no hay superficie
    h = techo(np.array([1500.0, 1500.0]), np.array([5000.0, 6500.0]), **KW)
    assert h[0] == pytest.approx(124.0)
    assert np.isinf(h[1])


def test_transicion_14_3_por_ciento_desde_la_franja():
    # En la mitad de la pista, 50 m fuera de la franja (y = 200): base = elevación del eje
    s = 1500.0
    base = 28.96 + (16.15 - 28.96) * s / 3001
    h, limita, _ = techo(np.array([s]), np.array([200.0]), detalle=True, **KW)
    assert h[0] == pytest.approx(base + 0.143 * 50, abs=0.01)
    assert limita[0] == "transicion"


def test_despegue_hacia_el_noreste_desde_extremo():
    # Despegue por la RWY 05 hacia B: empieza 60 m después del extremo B; altura base = umbral B
    d = 2000.0
    h, limita, sup = techo(np.array([3001.0 + 60 + d]), np.array([0.0]), detalle=True, **KW)
    assert sup["despegue_hacia_b"][0] == pytest.approx(16.15 + 0.02 * d, abs=0.01)
    # La aproximación a la 23 (no precisión) tiene el mismo 2 %: el techo es el menor de los dos
    assert h[0] == pytest.approx(16.15 + 0.02 * d, abs=0.01)


def test_estadio_vs_circulo():
    # En la prolongación del eje a 4,5 km del extremo A, el estadio todavía cubre (cónica), el círculo desde el
    # centro de la pista también; lateralmente a 4,2 km del centro solo el círculo da cónica.
    h_e = techo(np.array([1500.0]), np.array([4200.0]), **KW)
    h_c = techo(np.array([1500.0]), np.array([4200.0]), forma_horizontal="circulo", arp=(1500.0, 0.0), **KW)
    assert h_e[0] == pytest.approx(74 + 0.05 * 200)
    assert h_c[0] == pytest.approx(74 + 0.05 * 200)
    h_e2 = techo(np.array([-4100.0]), np.array([0.0]), **KW)
    h_c2 = techo(np.array([-4100.0]), np.array([0.0]), forma_horizontal="circulo", arp=(1500.0, 0.0), **KW)
    assert h_e2[0] <= h_c2[0]
