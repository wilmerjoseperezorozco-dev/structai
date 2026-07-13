"""Tests de geometría analítica de secciones (integración sobre polígono)."""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.geometry import propiedades_poligono, seccion_rectangular, seccion_circular, seccion_desde_poligono


def test_rectangulo_area_y_centroide():
    b, h = 0.3, 0.5
    verts = [(0, 0), (b, 0), (b, h), (0, h)]
    props = propiedades_poligono(verts)
    assert abs(props["area"] - b * h) < 1e-12
    assert abs(props["cx"] - b / 2) < 1e-9
    assert abs(props["cy"] - h / 2) < 1e-9


def test_rectangulo_momento_inercia_vs_formula_cerrada():
    b, h = 0.3, 0.5
    verts = [(0, 0), (b, 0), (b, h), (0, h)]
    props = propiedades_poligono(verts)
    Ix_esperado = b * h ** 3 / 12.0
    Iy_esperado = h * b ** 3 / 12.0
    assert abs(props["Ix"] - Ix_esperado) / Ix_esperado < 1e-9
    assert abs(props["Iy"] - Iy_esperado) / Iy_esperado < 1e-9
    assert abs(props["Ixy"]) < 1e-12  # sección simétrica: producto de inercia nulo


def test_rectangulo_orientacion_horaria_da_mismo_resultado():
    b, h = 0.3, 0.5
    verts_ccw = [(0, 0), (b, 0), (b, h), (0, h)]
    verts_cw = list(reversed(verts_ccw))
    p1 = propiedades_poligono(verts_ccw)
    p2 = propiedades_poligono(verts_cw)
    assert abs(p1["Ix"] - p2["Ix"]) < 1e-12
    assert abs(p1["area"] - p2["area"]) < 1e-12


def test_circulo_aproximado_por_poligono_vs_formula_cerrada():
    r = 0.2
    n = 720
    verts = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    props = propiedades_poligono(verts)
    area_esperada = math.pi * r ** 2
    I_esperado = math.pi * r ** 4 / 4.0
    assert abs(props["area"] - area_esperada) / area_esperada < 1e-4
    assert abs(props["Ix"] - I_esperado) / I_esperado < 1e-4
    assert abs(props["Iy"] - I_esperado) / I_esperado < 1e-4


def test_seccion_rectangular_factory_consistente_con_poligono():
    b, h = 0.25, 0.45
    sec_cerrada = seccion_rectangular(b, h)
    sec_poligono = seccion_desde_poligono("test", [(0, 0), (b, 0), (b, h), (0, h)])
    assert abs(sec_cerrada.Ix - sec_poligono.Ix) / sec_cerrada.Ix < 1e-9
    assert abs(sec_cerrada.area - sec_poligono.area) < 1e-12


def test_seccion_circular_radio_giro():
    r = 0.15
    sec = seccion_circular(r)
    # radio de giro de un círculo sólido: r_g = r/2
    assert abs(sec.radio_giro_x - r / 2) / (r / 2) < 1e-9


def test_ejes_principales_seccion_simetrica_iguales_a_ix_iy():
    b, h = 0.3, 0.3  # sección cuadrada: Ix=Iy, sin producto de inercia
    props = propiedades_poligono([(0, 0), (b, 0), (b, h), (0, h)])
    assert abs(props["I1"] - props["Ix"]) < 1e-9
    assert abs(props["I2"] - props["Iy"]) < 1e-9


def test_poligono_menos_de_3_vertices_lanza_error():
    import pytest
    with pytest.raises(ValueError):
        propiedades_poligono([(0, 0), (1, 0)])
