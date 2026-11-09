"""Optimizador de referencia del muro: todo lo que devuelve debe cumplir según el propio verificador, y los casos imposibles se reportan como tales."""
import pytest

from src.muro_contencion import Relleno, SueloApoyo, verificar_estabilidad, verificar_estabilidad_sismica
from src.muro_optimizador import CasoMuro, ahorro_frente_a_tradicional, optimizar, optimizar_todas

C = CasoMuro(3.0, Relleno(18.0, 30.0, 5.0, 10.0), SueloApoyo(30.0, 200.0), a_max_g=0.15)


def test_la_solucion_cumple_con_el_verificador_independiente():
    s = optimizar(C, "estandar")
    assert s is not None and s.diseno.cumple
    assert verificar_estabilidad(s.geometria, C.relleno, C.apoyo).cumple
    assert verificar_estabilidad_sismica(s.geometria, C.relleno, C.apoyo, 0.15).cumple


def test_el_dentellon_resuelve_el_deslizamiento_con_menos_base():
    e, d = optimizar(C, "estandar"), optimizar(C, "dentellon")
    assert d.geometria.b_talon < e.geometria.b_talon and d.geometria.dentellon_prof >= 0.30


def test_el_ahorro_pareado_del_tradicional_es_cero_y_se_calcula_para_las_demas():
    sols = optimizar_todas(C, perfiles=("lineal",))
    ah = ahorro_frente_a_tradicional(sols)
    assert ah["tradicional"] == pytest.approx(0.0)
    assert ah["estandar"] == pytest.approx(0.0, abs=1e-9)
    assert ah["dentellon"] is not None and ah["dentellon"] > 0


def test_caso_imposible_devuelve_none_no_una_geometria_insegura():
    imposible = CasoMuro(8.0, Relleno(16.0, 24.0, 20.0, 20.0), SueloApoyo(24.0, 80.0), a_max_g=0.40)
    assert all(v is None for v in optimizar_todas(imposible, perfiles=("lineal",)).values())


def test_lambda_de_carbono_no_aumenta_el_co2():
    base = optimizar(C, "estandar")
    verde = optimizar(CasoMuro(C.altura, C.relleno, C.apoyo, a_max_g=C.a_max_g, lam_co2=3000.0), "estandar")
    assert verde.diseno.co2_kg_m <= base.diseno.co2_kg_m + 1e-6
