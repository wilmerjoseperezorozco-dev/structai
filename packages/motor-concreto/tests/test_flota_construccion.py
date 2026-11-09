"""Flota de obra: viajes discretos, emisiones por km y contraste con fuentes."""
import pytest

from src.flota_construccion import (CATALOGO, FACTOR_TERRENO, co2_viajes, contraste_con_fuentes, emision_por_km, emision_por_ton_km,
                                    viajes, viajes_mixer)
from src.transporte_acero import planificar


def test_emision_por_km_es_factor_sobre_rendimiento():
    nhr = CATALOGO["C2_liviano"]
    assert emision_por_km(nhr) == pytest.approx(10.2765 / 16.0)


def test_emision_por_ton_km_decrece_con_el_tamano():
    orden = ["C2_liviano", "C2_sencillo", "C3", "minimula", "tractomula"]
    v = [emision_por_ton_km(CATALOGO[k]) for k in orden]
    assert v == sorted(v, reverse=True)


def test_viajes_es_una_funcion_escalon():
    assert viajes(0, 10) == 0
    assert viajes(10, 10) == 1
    assert viajes(10.01, 10) == 2
    with pytest.raises(ValueError):
        viajes(5, 0)


def test_mixer_por_volumen_zapata_16_2_y_21_toneladas():
    assert viajes_mixer(16.2 / 2.4) == 1           # 6,75 m³ (la tabla pegada decía 7,5 m³: eso son 18 t)
    assert viajes_mixer(21.0 / 2.4) == 2           # 8,75 m³ > 8 m³
    assert viajes_mixer(8.0) == 1 and viajes_mixer(8.01) == 2


def test_terreno_reduce_el_rendimiento_y_sube_el_co2():
    c = CATALOGO["tractomula"]
    assert co2_viajes(1, 100, c, terreno="montanoso") > co2_viajes(1, 100, c, terreno="ondulado") > co2_viajes(1, 100, c)
    assert FACTOR_TERRENO["camion"]["montanoso"] == pytest.approx(7.81 / 12.70)


def test_contraste_con_andi_y_sin_fuente():
    assert "dentro" in contraste_con_fuentes(CATALOGO["C2_sencillo"])
    assert "dentro" in contraste_con_fuentes(CATALOGO["tractomula"])
    assert contraste_con_fuentes(CATALOGO["C3"]) is None


def test_a_vehiculo_alimenta_el_plan_de_acero():
    v = CATALOGO["C2_liviano"].a_vehiculo(largo_carga_m=4.0)
    p = planificar([1.85] * 30, "4", v, km_ida_vuelta=10)
    assert p.estrategia == "corte en tienda" and p.co2_transporte_kg > 0 and not v.fuente.startswith("ANDI")
