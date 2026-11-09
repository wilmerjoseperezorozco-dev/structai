"""Verificador de la Resolución 0330/2017 y marco normativo.
Valores y numeración verificados en el texto consolidado del Gestor Normativo de la CRA (Arts. 135, 142, 150, 153, 155, 159, 258)."""
import pytest

from src.marco_normativo import REGLAS, TABLA_16, TABLA_20, regla, vigencia_ras2000
from src.verificador_res0330 import (
    diametro_camara_minimo, verificar_caida, verificar_metodo_racional, verificar_periodo_retorno,
    verificar_suds, verificar_velocidad,
)
from src import HidrologiaRequest, ManningRequest, MaterialTuberia, calcular_hidrologia, calcular_manning


def test_registro_tiene_fuente_y_articulo_en_cada_regla():
    assert REGLAS
    for r in REGLAS.values():
        assert r.fuente and r.articulo and r.enunciado


def test_ras2000_figura_como_derogada_por_art_258_del_texto_consolidado():
    v = vigencia_ras2000()
    assert v["estado"] == "derogada"
    assert "258" in v["derogada_por"]


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
    (10.0, 0.35, 300, 40, "requiere_criterio"),   # justo en el tope
    (10.5, 0.35, 300, 40, "no_cumple"),           # el tope de 10 m/s no admite excepción
])
def test_velocidad_maxima_excepcion_y_tope_de_10_ms(v, s_terreno, d, q, estado):
    assert verificar_velocidad(v, s_terreno, d, q).estado == estado


def test_velocidad_con_excepcion_exige_revestimiento_y_disipacion():
    det = verificar_velocidad(7.0, 0.40, 300, 40).detalle.lower()
    assert "disipación" in det and "revestimiento" in det


@pytest.mark.parametrize("dz,estado", [(0.5, "cumple"), (0.75, "cumple"), (1.0, "requiere_criterio"), (7.0, "requiere_criterio"), (8.0, "requiere_criterio")])
def test_caida_estructuras_por_desnivel(dz, estado):
    assert verificar_caida(dz).estado == estado


def test_caida_mayor_7_m_exige_disipacion_y_menor_no():
    assert "disipación" in verificar_caida(8.0).detalle.lower()
    assert "cámara de caída" in verificar_caida(1.0).detalle.lower()
    assert "disipación" not in verificar_caida(1.0).detalle.lower()


@pytest.mark.parametrize("d_entrada,minimo", [(200, 170), (300, 170), (301, 280), (450, 280), (451, 360), (900, 360)])
def test_tabla_20_diametro_de_camara_de_caida(d_entrada, minimo):
    assert diametro_camara_minimo(d_entrada) == minimo


def test_tabla_20_sobre_900_mm_pide_transicion():
    assert diametro_camara_minimo(1000) is None
    assert "transición" in verificar_caida(1.0, diametro_entrada_mm=1000).detalle.lower()


@pytest.mark.parametrize("red,viable,estado", [(30, True, "cumple"), (45, True, "cumple"), (25, True, "no_cumple"), (29.9, None, "no_cumple"), (0, False, "cumple")])
def test_suds_reduccion_minima_30_pct_si_es_viable(red, viable, estado):
    assert verificar_suds(red, viable).estado == estado


def test_tabla_16_transcrita_completa():
    assert len(TABLA_16) == 7
    assert sorted(v[1] for v in TABLA_16.values()) == [3, 5, 5, 10, 50, 100, 100]


@pytest.mark.parametrize("tr,tramo,estado", [(3, "residencial_inicial_menor_2ha", "cumple"), (2, "residencial_inicial_menor_2ha", "no_cumple"),
                                              (25, "canal_menor_1000ha", "no_cumple"), (100, "canal_montanoso_mayor_1000ha", "cumple")])
def test_periodo_de_retorno_minimo_tabla_16(tr, tramo, estado):
    assert verificar_periodo_retorno(tr, tramo).estado == estado


def test_periodo_de_retorno_tipo_de_tramo_desconocido_falla_claro():
    with pytest.raises(ValueError):
        verificar_periodo_retorno(10, "marte")


def test_hidrologia_agrega_verificacion_y_sensibilidad_sin_cambiar_el_caudal():
    base = dict(longitud_cauce_m=800, pendiente_media=0.02, periodo_retorno=25, coeficiente_escorrentia=0.6, region_idf="caribe")
    peq = calcular_hidrologia(HidrologiaRequest(area_cuenca_ha=50, acepta_idf_referencial=True, **base))
    grande = calcular_hidrologia(HidrologiaRequest(area_cuenca_ha=300, acepta_idf_referencial=True, **base))
    assert peq.verificaciones_normativas[0].estado == "cumple"
    assert grande.verificaciones_normativas[0].estado == "no_cumple"
    assert set(peq.sensibilidad_tc) == {"tc_3_min", "tc_10_min"}
    assert peq.sensibilidad_tc["tc_3_min"]["caudal_m3s"] >= peq.sensibilidad_tc["tc_10_min"]["caudal_m3s"]
    assert peq.caudal_diseno_m3s == pytest.approx(0.6 * peq.intensidad_mm_h * 50 / 360.0, rel=1e-3)


def test_hidrologia_con_tipo_de_tramo_verifica_periodo_de_retorno():
    base = dict(area_cuenca_ha=50, longitud_cauce_m=800, pendiente_media=0.02, coeficiente_escorrentia=0.6, region_idf="caribe")
    bajo = calcular_hidrologia(HidrologiaRequest(periodo_retorno=10, acepta_idf_referencial=True, tipo_tramo="canal_menor_1000ha", **base))
    ok = calcular_hidrologia(HidrologiaRequest(periodo_retorno=50, acepta_idf_referencial=True, tipo_tramo="canal_menor_1000ha", **base))
    assert [v.regla for v in bajo.verificaciones_normativas] == ["racional_area_max", "periodo_retorno_minimo"]
    assert bajo.verificaciones_normativas[1].estado == "no_cumple"
    assert ok.verificaciones_normativas[1].estado == "cumple"


def test_manning_pendiente_de_terreno_fuerte_habilita_criterio_en_vez_de_incumplir():
    base = dict(caudal_diseno_ls=60, pendiente_m_m=0.30, material=MaterialTuberia.CONCRETO)
    sin_dato = calcular_manning(ManningRequest(**base))
    con_dato = calcular_manning(ManningRequest(pendiente_terreno_m_m=0.35, **base))
    assert sin_dato.velocidad_real_ms > 5.0, "el caso de prueba debe superar 5 m/s"
    assert sin_dato.verificaciones_normativas[0].estado == "no_cumple"
    assert con_dato.verificaciones_normativas[0].estado == "requiere_criterio"


def test_verificar_res0330_solo_evalua_lo_informado_y_trae_vigencia():
    from src import verificar_res0330
    r = verificar_res0330(desnivel_caida_m=1.2, diametro_entrada_mm=400, reduccion_pico_suds_pct=20.0, suds_viable=True)
    assert [v.regla for v in r["verificaciones_normativas"]] == ["camara_caida_desnivel", "suds_reduccion_pico"]
    assert r["verificaciones_normativas"][1].estado == "no_cumple"
    assert r["vigencia"]["estado"] == "derogada" and r["no_verificado"]
    assert verificar_res0330()["verificaciones_normativas"] == []


def test_vigencia_incluye_cadena_de_modificaciones_de_la_0330():
    cadena = vigencia_ras2000()["cadena_0330"]
    assert any("0799" in c[0] for c in cadena) and any("0548" in c[0] for c in cadena)
