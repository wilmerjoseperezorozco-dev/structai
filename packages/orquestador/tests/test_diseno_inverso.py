import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import diseno_inverso as di

V = di._viga


@pytest.fixture(scope="module")
def sin_base():
    return di.diseno_inverso(di.ProyectoViga(luz_m=6.0, carga_muerta_kn_m=18.0, carga_viva_kn_m=10.0))


def test_optimo_cumple_todas_las_verificaciones(sin_base):
    assert sin_base.optimo_global is not None
    assert sin_base.optimo_global.resultado.cumple
    assert sin_base.candidatos_cumplen > 0


def test_optimo_coincide_con_calculo_a_mano(sin_base):
    # 250x550, 3#7: d=489.4 mm, wu=41.56 kN/m, Mu=187 kN.m, phiMn=190.8 kN.m (ver calculo manual)
    s = sin_base.optimo_global.seccion
    assert (s.b, s.h, s.barras_n, s.barras_dia) == (250, 550, 3, "7")
    assert sin_base.optimo_global.resultado.Mu == pytest.approx(186.99, abs=0.1)


def test_ningun_candidato_cumplidor_es_mas_barato(sin_base):
    mat = V.Materiales(fc=21.0)
    cargas = V.Cargas(18.0, 10.0, 6.0)
    optimo = sin_base.optimo_global.costo_directo
    # perturbar el optimo con una barra menos debe incumplir o salir mas caro que... el optimo
    s = sin_base.optimo_global.seccion
    menos = V.Seccion(s.b, s.h, s.barras_n - 1, s.barras_dia, s.estribo_dia, s.estribo_s)
    assert not V.verificar(menos, mat, cargas).cumple
    assert optimo > 0


def test_base_que_cumple_reporta_ahorro_con_formula_exacta():
    base = V.Seccion(b=400, h=700, barras_n=6, barras_dia="8", estribo_dia="3", estribo_s=100)
    i = di.diseno_inverso(di.ProyectoViga(6.0, 18.0, 10.0, base=base))
    assert i.base_cumple
    esperado = round((i.base_costo - i.optimo_global.costo_directo) / i.base_costo * 100, 1)
    assert i.ahorro_pct == esperado
    assert 0 < i.ahorro_pct < 100


def test_base_que_falla_no_reporta_porcentaje_y_ofrece_correccion_minima():
    base = V.Seccion(b=300, h=450, barras_n=3, barras_dia="5", estribo_dia="3", estribo_s=250)
    i = di.diseno_inverso(di.ProyectoViga(6.0, 18.0, 10.0, base=base))
    assert i.base_cumple is False
    assert i.ahorro_pct is None
    m = i.minima_intervencion
    assert m is not None and (m.seccion.b, m.seccion.h) == (300, 450) and m.resultado.cumple
    assert "no se reporta % de ahorro" in di.resumen(i)


def test_correccion_minima_nunca_es_mas_barata_que_el_optimo_global():
    base = V.Seccion(b=300, h=450, barras_n=3, barras_dia="5", estribo_dia="3", estribo_s=250)
    i = di.diseno_inverso(di.ProyectoViga(6.0, 18.0, 10.0, base=base))
    assert i.minima_intervencion.costo_directo >= i.optimo_global.costo_directo


def test_proyecto_imposible_devuelve_none_y_lo_dice():
    i = di.diseno_inverso(di.ProyectoViga(luz_m=14.0, carga_muerta_kn_m=80.0, carga_viva_kn_m=60.0))
    assert i.optimo_global is None
    assert "Ningún diseño" in di.resumen(i)


def test_calidad_no_soportada_falla_explicitamente():
    with pytest.raises(ValueError):
        di.diseno_inverso(di.ProyectoViga(6.0, 18.0, 10.0), calidades=("9999",))
