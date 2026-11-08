"""Verificador de la Resolución 0330/2017 y marco normativo (valores verificados en el texto de la norma, Arts. 135, 142, 151, 153, 255)."""
import pytest

from src.marco_normativo import REGLAS, regla, vigencia_ras2000
from src.verificador_res0330 import (
    verificar_caida, verificar_metodo_racional, verificar_suds, verificar_velocidad,
)
from src import HidrologiaRequest, ManningRequest, MaterialTuberia, calcular_hidrologia, calcular_manning


def test_registro_tiene_fuente_y_articulo_en_cada_regla():
    assert REGLAS
    for r in REGLAS.values():
        assert r.fuente and r.articulo and r.enunciado


def test_ras2000_figura_como_derogada_por_art_255():
    v = vigencia_ras2000()
    assert v["estado"] == "derogada"
    assert "255" in v["derogada_por"]


@pytest.mark.parametrize("area_ha,estado", [(10, "cumple"), (79.99, "cumple"), (80, "no_cumple"), (1000, "no_cumple")])
def test_metodo_racional_limite_80_ha(area_ha, estado):
    assert verificar_metodo_racional(area_ha).estado == estado


@pytest.mark.parametrize("v,s_terreno,d,q,estado", [
    (3.0, 0.05, 300, 40, "cumple"),
    (5.0, 0.05, 300, 40, "cumple"),
    (6.0, 0.05, 300, 40, "no_cumple"),            # supera 5 m/s sin condición especial
    (6.0, 0.35, 300, 40, "requiere_criterio"),    # terreno > 30 %
    (6.0, 0.05, 600, 40, "requiere_criterio"),    # diámetro >= 600 mm
    (6.0, 0.05, 300, 600, "requiere_criterio"),   # caudal > 500 L/s
    (6.0, None, 300, 40, "no_cumple"),            # sin dato de terreno no se asume la excepción
])
def test_velocidad_maxima_y_excepcion_pendiente_fuerte(v, s_terreno, d, q, estado):
    assert verificar_velocidad(v, s_terreno, d, q).estado == estado


def test_velocidad_con_excepcion_exige_disipacion():
    r = verificar_velocidad(7.0, 0.40, 300, 40)
    assert "disipación" in r.detalle.lower()


@pytest.mark.parametrize("dz,estado", [(0.5, "cumple"), (0.75, "cumple"), (1.0, "requiere_criterio"), (7.0, "requiere_criterio"), (8.0, "requiere_criterio")])
def test_caida_estructuras_por_desnivel(dz, estado):
    assert verificar_caida(dz).estado == estado


def test_caida_mayor_7_m_exige_disipacion_y_menor_no():
    assert "disipación" in verificar_caida(8.0).detalle.lower()
    assert "cámara de caída" in verificar_caida(1.0).detalle.lower()
    assert "disipación" not in verificar_caida(1.0).detalle.lower()


@pytest.mark.parametrize("red,estado", [(25, "cumple"), (30, "cumple"), (24.9, "no_cumple")])
def test_suds_reduccion_minima_25_pct(red, estado):
    assert verificar_suds(red).estado == estado


def test_hidrologia_agrega_verificacion_y_sensibilidad_sin_cambiar_el_caudal():
    base = dict(longitud_cauce_m=800, pendiente_media=0.02, periodo_retorno=25, coeficiente_escorrentia=0.6, region_idf="caribe")
    peq = calcular_hidrologia(HidrologiaRequest(area_cuenca_ha=50, **base))
    grande = calcular_hidrologia(HidrologiaRequest(area_cuenca_ha=300, **base))
    assert peq.verificaciones_normativas[0].estado == "cumple"
    assert grande.verificaciones_normativas[0].estado == "no_cumple"
    assert set(peq.sensibilidad_tc) == {"tc_3_min", "tc_10_min"}
    assert peq.sensibilidad_tc["tc_3_min"]["caudal_m3s"] >= peq.sensibilidad_tc["tc_10_min"]["caudal_m3s"]
    # el caudal principal conserva la fórmula previa: Q = C·I·A/360
    assert peq.caudal_diseno_m3s == pytest.approx(0.6 * peq.intensidad_mm_h * 50 / 360.0, rel=1e-3)


def test_manning_pendiente_de_terreno_fuerte_habilita_criterio_en_vez_de_incumplir():
    base = dict(caudal_diseno_ls=60, pendiente_m_m=0.20, material=MaterialTuberia.CONCRETO if hasattr(MaterialTuberia, "CONCRETO") else list(MaterialTuberia)[0])
    sin_dato = calcular_manning(ManningRequest(**base))
    con_dato = calcular_manning(ManningRequest(pendiente_terreno_m_m=0.35, **base))
    assert sin_dato.verificaciones_normativas
    est_sin = sin_dato.verificaciones_normativas[0].estado
    est_con = con_dato.verificaciones_normativas[0].estado
    if sin_dato.velocidad_real_ms > 5.0:
        assert est_sin == "no_cumple" and est_con == "requiere_criterio"
    else:
        assert est_sin == est_con == "cumple"
