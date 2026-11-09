"""Salida con contrato uniforme del orquestador (#130): diseño integral de pórtico (vigas + columnas + costo)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError

from src.contrato_api import SolicitudDisenoIntegral, disenar_integral_contrato

GRILLA_B = (250.0, 300.0, 350.0)
GRILLA_H = (500.0, 600.0, 700.0, 800.0)
COLS = (400.0, 500.0, 600.0)


def _sol(**kw):
    base = dict(luces_m=[6.0, 6.0], alturas_piso_m=[3.2, 3.0], carga_muerta_kn_m=22.0, carga_viva_kn_m=8.0,
                calidad_concreto="3000", fy_mpa=420.0, recubrimiento_mm=40.0, municipio="Pereira", departamento="Risaralda",
                perfil_suelo="D", grupo_uso="I", capacidad="DES", columnas_mm=list(COLS), b_mm=list(GRILLA_B), h_mm=list(GRILLA_H))
    base.update(kw)
    return SolicitudDisenoIntegral(**base)


@pytest.fixture(scope="module")
def r():
    return disenar_integral_contrato(_sol())


def test_contrato_completo(r):
    v = r.valor
    assert v["c_mm"] in COLS and v["b_mm"] in GRILLA_B and v["h_mm"] in GRILLA_H
    assert v["costo_directo_cop"] == pytest.approx(v["costo_vigas_cop"] + v["costo_columnas_cop"])
    assert v["factibles"] >= 1 and v["evaluadas"] >= v["factibles"]
    assert r.unidad_si and r.ecuacion and "NSR-10" in r.referencia_normativa
    assert r.supuestos and r.aviso_responsabilidad_profesional and isinstance(r.en_borde_dominio, bool)


def test_el_optimo_cumple_deriva_y_columna_fuerte_viga_debil(r):
    assert r.valor["deriva"] <= 0.010
    assert r.valor["razon_scwb"] >= 1.0


def test_sin_municipio_ni_capacidad_lanza_valueerror():
    with pytest.raises(ValueError, match="municipio|capacidad"):
        disenar_integral_contrato(_sol(municipio=None, departamento=None, capacidad=None))


def test_calidad_de_concreto_no_soportada_lanza_valueerror():
    with pytest.raises(ValueError, match="calidad_concreto"):
        disenar_integral_contrato(_sol(calidad_concreto="9999"))


def test_sin_solucion_lanza_valueerror_con_la_norma():
    with pytest.raises(ValueError, match="NSR-10"):
        disenar_integral_contrato(_sol(carga_muerta_kn_m=400.0, carga_viva_kn_m=200.0, b_mm=[250.0], h_mm=[500.0], columnas_mm=[300.0]))


def test_la_rejilla_pedida_esta_acotada():
    with pytest.raises(ValidationError):
        _sol(columnas_mm=[300.0 + 10 * k for k in range(40)])


def test_mas_carga_no_baja_el_costo():
    barato = disenar_integral_contrato(_sol(carga_viva_kn_m=6.0)).valor["costo_directo_cop"]
    caro = disenar_integral_contrato(_sol(carga_viva_kn_m=14.0)).valor["costo_directo_cop"]
    assert caro >= barato
