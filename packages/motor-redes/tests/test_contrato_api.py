import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError

from src.contrato_api import SolicitudRed, red_permanente_contrato


def _tramo(**kw):
    t = dict(id="p", desde="R", hasta="N", longitud_m=1000.0, diametro_m=0.3, c_hw=130.0)
    t.update(kw)
    return t


def _s(**kw):
    base = dict(nodos=[dict(id="R", cota_m=50.0, carga_fija_m=100.0), dict(id="N", cota_m=40.0, demanda_m3s=0.1)],
                tramos=[_tramo()])
    base.update(kw)
    return SolicitudRed(**base)


def test_contrato_basico_y_supuestos():
    r = red_permanente_contrato(_s())
    assert r.valor["cumple"] is None and r.valor["incumplimientos"] == []
    assert r.en_borde_dominio is False and len(r.supuestos) >= 6


def test_incumplimiento_de_presion_minima_se_reporta():
    r = red_permanente_contrato(_s(presion_min_m=100.0))
    assert r.valor["cumple"] is False and "nudo N" in r.valor["incumplimientos"][0]


def test_cerca_del_limite_activa_borde():
    base = red_permanente_contrato(_s()).valor["nodos"]["N"]["presion_m"]
    r = red_permanente_contrato(_s(presion_min_m=base / 1.05))
    assert r.valor["cumple"] and r.en_borde_dominio is True


def test_velocidad_maxima():
    assert not red_permanente_contrato(_s(velocidad_max_ms=0.5)).valor["cumple"]


def test_c_atipico_activa_borde():
    assert red_permanente_contrato(_s(tramos=[_tramo(c_hw=190.0)])).en_borde_dominio is True


def test_presion_negativa_activa_borde_y_se_declara():
    s = _s(nodos=[dict(id="R", cota_m=50.0, carga_fija_m=60.0), dict(id="N", cota_m=80.0, demanda_m3s=0.05)])
    r = red_permanente_contrato(s)
    assert r.en_borde_dominio and any("negativa" in x for x in r.supuestos)


def test_red_sin_embalse_levanta_valueerror():
    with pytest.raises(ValueError, match="carga fija"):
        red_permanente_contrato(_s(nodos=[dict(id="R", cota_m=1.0), dict(id="N", cota_m=1.0, demanda_m3s=0.1)]))


@pytest.mark.parametrize("campo,valor", [("longitud_m", float("nan")), ("diametro_m", -1.0), ("c_hw", "130")])
def test_entradas_invalidas_se_rechazan_por_esquema(campo, valor):
    with pytest.raises(ValidationError):
        _s(tramos=[_tramo(**{campo: valor})])


def test_sin_limites_declarados_cumple_es_none_no_true():
    r = red_permanente_contrato(_s())
    assert r.valor["cumple"] is None and r.valor["limites_verificados"] is False


def test_con_limites_declarados_cumple_es_booleano():
    r = red_permanente_contrato(_s(presion_min_m=1.0))
    assert r.valor["cumple"] is True and r.valor["limites_verificados"] is True


def test_presion_negativa_es_incumplimiento_aunque_no_haya_limites():
    s = _s(nodos=[dict(id="R", cota_m=50.0, carga_fija_m=60.0), dict(id="N", cota_m=80.0, demanda_m3s=0.05)])
    r = red_permanente_contrato(s)
    assert r.valor["cumple"] is False and any("negativa" in x for x in r.valor["incumplimientos"])


def test_diametro_menor_a_50mm_activa_borde():
    assert red_permanente_contrato(_s(tramos=[_tramo(diametro_m=0.04)], nodos=[
        dict(id="R", cota_m=50.0, carga_fija_m=100.0), dict(id="N", cota_m=40.0, demanda_m3s=0.0005)])).en_borde_dominio is True


def test_velocidad_muy_baja_activa_borde():
    r = red_permanente_contrato(_s(nodos=[dict(id="R", cota_m=50.0, carga_fija_m=100.0),
                                          dict(id="N", cota_m=40.0, demanda_m3s=0.0001)]))
    assert r.en_borde_dominio is True
