import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import diseno_inverso as di

P = dict(luz_m=6.0, carga_muerta_kn_m=18.0, carga_viva_kn_m=10.0)


@pytest.fixture(scope="module")
def tubara():
    return di.diseno_inverso(di.ProyectoViga(**P, municipio="Tubará"))


@pytest.fixture(scope="module")
def pereira():
    return di.diseno_inverso(di.ProyectoViga(**P, municipio="Pereira"))


def test_municipio_determina_zona_y_capacidad(tubara, pereira):
    assert tubara.sismo["zona_calculada"] == "Baja" and tubara.sismo["capacidad_aplicada"] == "DMI"
    assert pereira.sismo["zona_calculada"] == "Alta" and pereira.sismo["capacidad_aplicada"] == "DES"


def test_baja_amenaza_no_agrega_requisitos_sismicos(tubara):
    nombres = [v.nombre for v in tubara.optimo_global.resultado.verificaciones]
    assert not any("confinamiento" in n.lower() for n in nombres)


def test_alta_amenaza_cuesta_mas_que_baja_con_las_mismas_cargas(tubara, pereira):
    assert pereira.optimo_global.costo_directo > tubara.optimo_global.costo_directo


def test_alta_amenaza_incluye_refuerzo_simetrico_y_cortante_por_capacidad(pereira):
    s = pereira.optimo_global.seccion
    assert s.barras_sup_n == s.barras_n
    nombres = [v.nombre for v in pereira.optimo_global.resultado.verificaciones]
    assert any("Cortante por capacidad" in n for n in nombres)
    assert pereira.optimo_global.resultado.cumple


def test_no_se_permite_bajar_la_capacidad_exigida_por_la_zona():
    with pytest.raises(ValueError, match="no se permite bajarla"):
        di.diseno_inverso(di.ProyectoViga(**P, municipio="Pereira", capacidad="DMI"))


def test_se_permite_subir_la_capacidad():
    i = di.diseno_inverso(di.ProyectoViga(**P, municipio="Tubará", capacidad="DES"))
    assert i.sismo["capacidad_aplicada"] == "DES"
    assert i.optimo_global.seccion.barras_sup_n > 0


def test_municipio_ambiguo_se_rechaza_con_mensaje_util():
    with pytest.raises(Exception, match="ambiguo"):
        di.diseno_inverso(di.ProyectoViga(**P, municipio="Argelia"))


def test_resumen_menciona_aa_av_zona_y_capacidad(pereira):
    t = di.resumen(pereira)
    assert "Aa=0.25" in t and "Alta" in t and "DES" in t


def test_momento_de_apoyo_alto_del_analisis_puede_dejar_sin_solucion():
    i = di.diseno_inverso(di.ProyectoViga(**P, municipio="Pereira", momento_apoyo_kn_m=5000.0))
    assert i.optimo_global is None
