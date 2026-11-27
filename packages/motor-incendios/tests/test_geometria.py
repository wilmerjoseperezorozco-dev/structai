"""Geometría y colisiones (#336 F2), casos a mano: un vano de 5 × 5 m, piso de 3,0 m, columna 400, viga 300 × 500
(altura total), losa de 0,12 m."""
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import geometria as g  # noqa: E402


def _ed(pisos=1):
    p = SimpleNamespace(luces_x_m=(5.0,), luces_y_m=(5.0,), alturas_piso_m=(3.0,) * pisos,
                        columnas_mm=(400,) * pisos, vigas_mm=((300, 500),) * pisos)
    return g.desde_porticos(p, espesor_losa_m=0.12)


def test_conteo_de_obstaculos_y_area():
    e = _ed()
    tipos = [o.tipo for o in e.obstaculos]
    assert tipos.count("columna") == 4 and tipos.count("viga") == 4 and tipos.count("losa") == 1
    assert e.pisos[0].area_m2 == pytest.approx(5.4 ** 2)


def test_altura_libre_bajo_losa_y_bajo_viga():
    e = _ed()
    p = e.pisos[0]
    assert p.altura_bajo_losa_m == pytest.approx(2.88)                       # 3,00 − 0,12
    assert e.altura_libre(p, 2.5, 2.5) == pytest.approx(2.88)               # centro del vano
    assert e.altura_libre(p, 2.5, 0.0) == pytest.approx(2.50)               # sobre el eje de la viga: 3,00 − 0,50


def test_mapa_de_altura_libre():
    e = _ed()
    m = e.mapa_altura_libre(e.pisos[0], paso_m=0.1)
    assert m["minima_m"] == pytest.approx(2.50) and 0 < m["fraccion_bajo_obstaculo"] < 0.2
    assert all(not (-0.2 < x < 0.2 and -0.2 < y < 0.2) for x, y, _ in m["puntos"])   # dentro de la columna, excluido


def test_ducto_declarado_baja_la_altura_libre():
    e = _ed()
    e.agregar([g.Caja(1.0, 1.0, 2.2, 4.0, 1.6, 2.6, "ducto", "D1")])
    assert e.altura_libre(e.pisos[0], 2.0, 1.3) == pytest.approx(2.2)
    assert e.altura_libre(e.pisos[0], 2.0, 3.0) == pytest.approx(2.88)


def test_tubo_que_cruza_la_viga_colisiona_y_por_debajo_no():
    e = _ed()
    cruza = g.segmento((2.5, -1.0, 2.7), (2.5, 4.0, 2.7), 0.05)
    assert [o.id for o in e.colisiones(cruza)] == ["VX0-0-0"]
    debajo = g.segmento((2.5, -1.0, 2.3), (2.5, 4.0, 2.3), 0.05)
    assert e.colisiones(debajo) == []
    dentro = g.segmento((2.5, 1.0, 2.7), (2.5, 4.0, 2.7), 0.05)            # entre vigas, bajo la losa
    assert e.colisiones(dentro) == []


def test_holgura_declarada():
    e = _ed()
    s = g.segmento((2.5, -1.0, 2.45), (2.5, 4.0, 2.45), 0.05)              # corona en 2,475; fondo de viga en 2,50
    assert e.colisiones(s) == []
    assert [o.id for o in e.colisiones(s, holgura_m=0.05)] == ["VX0-0-0"]


def test_tocar_una_cara_no_es_colision():
    e = _ed()
    s = g.segmento((2.5, 1.0, 2.88 - 0.025), (2.5, 4.0, 2.88 - 0.025), 0.05)   # corona justo en la cara de la losa
    assert e.colisiones(s) == []


def test_bajante_vertical_choca_con_la_losa_salvo_que_se_ignore():
    e = _ed(pisos=2)
    s = g.segmento((2.5, 2.5, 1.0), (2.5, 2.5, 4.0), 0.10)
    assert {o.tipo for o in e.colisiones(s)} == {"losa"}
    assert e.colisiones(s, ignorar=("losa",)) == []                        # pase previsto en la losa


def test_entradas_invalidas():
    with pytest.raises(ValueError):
        g.segmento((0, 0, 0), (1, 1, 0), 0.05)                              # diagonal
    with pytest.raises(ValueError):
        g.Caja(1, 0, 0, 0, 1, 1)
    p = SimpleNamespace(luces_x_m=(5.0,), luces_y_m=(5.0,), alturas_piso_m=(3.0,), columnas_mm=(400,), vigas_mm=((300, 100),))
    with pytest.raises(ValueError):
        g.desde_porticos(p, espesor_losa_m=0.12)
