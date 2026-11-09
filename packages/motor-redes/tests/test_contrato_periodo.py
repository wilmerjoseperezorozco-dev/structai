import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError

from src.contrato_periodo import SolicitudPeriodo, periodo_extendido_contrato


def _s(**kw):
    base = dict(
        nodos=[dict(id="T", cota_m=40.0), dict(id="N", cota_m=30.0, demanda_m3s=0.01)],
        tramos=[dict(id="p", desde="T", hasta="N", longitud_m=500.0, diametro_m=0.2, c_hw=130.0)],
        tanques=[dict(id="T", cota_fondo_m=40.0, area_m2=100.0, nivel_inicial_m=5.0, nivel_min_m=0.5, nivel_max_m=10.0)],
        paso_s=600.0, n_pasos=6)
    base.update(kw)
    return SolicitudPeriodo(**base)


def test_contrato_basico_series_y_supuestos():
    r = periodo_extendido_contrato(_s())
    niv = r.valor["niveles_tanque_m"]["T"]
    assert len(niv) == 7 and niv[0] == 5.0 and niv[-1] == pytest.approx(5.0 - 0.01 * 3600 / 100.0, rel=1e-9)
    assert r.valor["completo"] is True and r.valor["cumple"] is None
    assert any("Euler" in x for x in r.supuestos) and r.en_borde_dominio is False


def test_limite_de_presion_se_verifica_en_nudos_de_demanda_no_en_el_tanque():
    r = periodo_extendido_contrato(_s(presion_min_m=400.0))
    assert r.valor["cumple"] is False
    assert all("nudo N" in x for x in r.valor["incumplimientos"]) and r.valor["incumplimientos"]


def test_evento_de_tanque_vacio_activa_borde_y_se_declara():
    r = periodo_extendido_contrato(_s(demanda_m3s=None) if False else _s(
        nodos=[dict(id="T", cota_m=40.0), dict(id="N", cota_m=30.0, demanda_m3s=0.05)],
        tanques=[dict(id="T", cota_fondo_m=40.0, area_m2=10.0, nivel_inicial_m=1.0, nivel_min_m=0.5, nivel_max_m=10.0)], paso_s=60.0, n_pasos=20))
    assert r.valor["completo"] is False and r.en_borde_dominio is True and r.valor["eventos"]


def test_tanque_cerca_de_su_limite_activa_borde():
    r = periodo_extendido_contrato(_s(tanques=[dict(id="T", cota_fondo_m=40.0, area_m2=100.0, nivel_inicial_m=5.0,
                                                    nivel_min_m=0.5, nivel_max_m=5.2)]))
    assert r.en_borde_dominio is True


def test_nivel_maximo_menor_que_inicial_es_valueerror():
    with pytest.raises(ValueError):
        periodo_extendido_contrato(_s(tanques=[dict(id="T", cota_fondo_m=40.0, area_m2=100.0, nivel_inicial_m=5.0,
                                                    nivel_min_m=0.5, nivel_max_m=4.0)]))


@pytest.mark.parametrize("kw", [dict(paso_s=float("nan")), dict(n_pasos=0), dict(n_pasos=10 ** 6), dict(patron_demanda=[])])
def test_parametros_invalidos_se_rechazan_por_esquema(kw):
    with pytest.raises(ValidationError):
        _s(**kw)
