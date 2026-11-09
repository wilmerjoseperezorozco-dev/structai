"""Métricas de excavación: identidades aritméticas y propiedades de monotonía; no hay cifras de la literatura."""
import pytest

from src.excavacion_estabilidad import SueloExc
from src.excavacion_metricas import (costo_riesgo_geotecnico, indice_eficiencia_geometrica, intensidad_energetica, tasa_reutilizacion)


def test_ieg_vertical_es_uno_y_talud_es_menor():
    assert indice_eficiencia_geometrica(30.0, 30.0) == 1.0
    assert indice_eficiencia_geometrica(30.0, 40.0) == pytest.approx(0.75)
    with pytest.raises(ValueError):
        indice_eficiencia_geometrica(30.0, 20.0)


def test_intensidad_es_consumo_sobre_rendimiento():
    r = intensidad_energetica(consumo_gal_h=6.0, rendimiento_m3_h=40.0, factor_kgco2e_por_gal=10.0)
    assert r.gal_por_m3 == pytest.approx(0.15) and r.kg_co2e_por_m3 == pytest.approx(1.5)
    with pytest.raises(ValueError):
        intensidad_energetica(6.0, 0.0, 10.0)


def test_reutilizacion_limitada_por_oferta_y_por_demanda():
    assert tasa_reutilizacion(1000, 600, 800) == pytest.approx(60.0)
    assert tasa_reutilizacion(1000, 600, 200) == pytest.approx(20.0)
    with pytest.raises(ValueError):
        tasa_reutilizacion(1000, 1200, 800)


def test_riesgo_crece_al_empinar_el_talud_y_es_pf_por_consecuencia():
    s = SueloExc(gamma=18.0, c_kpa=12.0, phi_deg=28.0)
    suave = costo_riesgo_geotecnico(5.0, 35.0, s, 0.3, 0.1, 1e6, grieta_traccion=False)
    firme = costo_riesgo_geotecnico(5.0, 60.0, s, 0.3, 0.1, 1e6, grieta_traccion=False)
    assert firme.fs_medio < suave.fs_medio and firme.prob_falla > suave.prob_falla
    assert firme.costo_riesgo == pytest.approx(firme.prob_falla * 1e6)
    assert 0.0 <= suave.prob_falla <= 1.0
