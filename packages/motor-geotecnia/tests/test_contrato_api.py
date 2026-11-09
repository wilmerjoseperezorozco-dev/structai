"""Salida con contrato uniforme de motor-geotecnia (#136): asentamiento por consolidación y capacidad portante."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from pydantic import ValidationError

from contrato_motor.propiedades import verificar_monotonia
from src.consolidacion import asentamiento_primario
from src.contrato_api import (EstratoArcilla, SolicitudAsentamiento, SolicitudPortante, asentamiento_contrato,
                              portante_contrato)
from src.esfuerzos import esfuerzo_boussinesq_centro_rect


def _estrato(**kw):
    base = dict(espesor_m=4.0, z_medio_m=4.0, sigma0_kpa=100.0, sigma_p_kpa=100.0, cc=0.3, cr=0.03, e0=1.0, cv_m2_dia=0.002, hdr_m=2.0)
    base.update(kw)
    return EstratoArcilla(**base)


def _asent(**kw):
    base = dict(q_kpa=150.0, B_m=2.0, L_m=3.0, estratos=[_estrato()], metodo="boussinesq", tipo_cimentacion="aislada")
    base.update(kw)
    return SolicitudAsentamiento(**base)


def _portante(**kw):
    base = dict(c_kpa=10.0, phi_deg=25.0, gamma_kn_m3=18.0, B_m=2.0, L_m=2.0, Df_m=1.0, nivel_freatico_m=None,
                factor_seguridad=3.0, q_aplicada_kpa=150.0)
    base.update(kw)
    return SolicitudPortante(**base)


def test_asentamiento_devuelve_el_contrato_completo_y_coincide_con_el_calculo_directo():
    r = asentamiento_contrato(_asent())
    delta = esfuerzo_boussinesq_centro_rect(150.0, 2.0, 3.0, 4.0)
    esperado = asentamiento_primario(cc=0.3, cr=0.03, e0=1.0, espesor_m=4.0, sigma0_kpa=100.0, delta_kpa=delta, sigma_p_kpa=100.0)
    assert r.valor["asentamiento_total_mm"] == pytest.approx(esperado * 1000.0)
    assert r.unidad_si and r.ecuacion and "NSR-10" in r.referencia_normativa and r.aviso_responsabilidad_profesional
    assert isinstance(r.en_borde_dominio, bool) and r.supuestos
    assert r.valor["estratos"][0]["t90_dias"] == pytest.approx(0.848 * 4.0 / 0.002, rel=2e-3)


def test_asentamiento_suma_los_estratos():
    uno = asentamiento_contrato(_asent(estratos=[_estrato()])).valor["asentamiento_total_mm"]
    dos = asentamiento_contrato(_asent(estratos=[_estrato(), _estrato()])).valor["asentamiento_total_mm"]
    assert dos == pytest.approx(2 * uno)


def test_asentamiento_monotono_en_la_carga_de_la_zapata():
    f = lambda q: asentamiento_contrato(_asent(q_kpa=q)).valor["asentamiento_total_mm"]
    verificar_monotonia(f, [20.0, 60.0, 120.0, 240.0, 480.0])


def test_asentamiento_contra_el_limite_de_nsr10_h49():
    r = asentamiento_contrato(_asent(q_kpa=600.0, estratos=[_estrato(espesor_m=10.0, z_medio_m=5.0)]))
    assert r.valor["limite_total_mm"] == 300.0
    assert r.valor["cumple_asentamiento_total"] == (r.valor["asentamiento_total_mm"] <= 300.0)
    assert any("H.4.9" in s for s in r.supuestos) or "H.4.9" in r.referencia_normativa


def test_asentamiento_cerca_del_limite_activa_el_borde_de_dominio():
    base = asentamiento_contrato(_asent(q_kpa=300.0, estratos=[_estrato(espesor_m=8.0, z_medio_m=4.0)]))
    s = base.valor["asentamiento_total_mm"]
    # calibra una carga que deje el asentamiento en ~97 % del límite de 150 mm (medianera)
    r = asentamiento_contrato(_asent(q_kpa=300.0, estratos=[_estrato(espesor_m=8.0, z_medio_m=4.0)], tipo_cimentacion="medianera"))
    util = s / 150.0
    assert r.en_borde_dominio == (util >= 0.95)


def test_asentamiento_metodo_2_a_1_es_distinto_de_boussinesq():
    a = asentamiento_contrato(_asent(metodo="boussinesq")).valor["asentamiento_total_mm"]
    b = asentamiento_contrato(_asent(metodo="2a1")).valor["asentamiento_total_mm"]
    assert a > 0 and b > 0 and a != b


def test_asentamiento_exige_datos_sin_defectos():
    with pytest.raises(ValidationError):
        SolicitudAsentamiento(q_kpa=150.0, B_m=2.0, estratos=[_estrato()])


def test_estrato_con_preconsolidacion_menor_que_sigma0_lanza_valueerror():
    with pytest.raises(ValueError, match="preconsolidaci"):
        asentamiento_contrato(_asent(estratos=[_estrato(sigma_p_kpa=50.0)]))


def test_portante_devuelve_el_contrato_y_aplica_el_factor_de_seguridad():
    r = portante_contrato(_portante())
    assert r.valor["q_adm_kpa"] == pytest.approx(r.valor["q_ult_kpa"] / 3.0)
    assert r.valor["cumple"] == (150.0 <= r.valor["q_adm_kpa"])
    assert "Vesić" in r.referencia_normativa and "NSR-10" in r.referencia_normativa
    assert isinstance(r.en_borde_dominio, bool) and r.aviso_responsabilidad_profesional


def test_portante_declara_la_limitacion_de_la_presion_con_el_ancho():
    r = portante_contrato(_portante())
    assert any("Df/B" in s for s in r.supuestos) and any("vertical" in s.lower() for s in r.supuestos)


def test_portante_en_el_limite_de_utilizacion_activa_el_borde():
    r0 = portante_contrato(_portante())
    q_adm = r0.valor["q_adm_kpa"]
    assert portante_contrato(_portante(q_aplicada_kpa=0.97 * q_adm)).en_borde_dominio is True
    assert portante_contrato(_portante(q_aplicada_kpa=0.5 * q_adm)).en_borde_dominio is False


def test_portante_phi_alto_activa_el_borde():
    assert portante_contrato(_portante(phi_deg=42.0, q_aplicada_kpa=10.0)).en_borde_dominio is True


def test_portante_con_agua_exige_peso_saturado():
    with pytest.raises(ValueError, match="saturado"):
        portante_contrato(_portante(nivel_freatico_m=1.0))


def test_portante_fs_menor_a_uno_es_rechazado():
    with pytest.raises(ValidationError):
        _portante(factor_seguridad=0.9)
