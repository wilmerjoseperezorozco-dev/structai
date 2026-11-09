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


def _con_bomba(h0=60.0, a=2000.0, demanda=0.03):
    return _s(nodos=[dict(id="R", cota_m=10.0, carga_fija_m=10.0), dict(id="B", cota_m=10.0),
                     dict(id="N", cota_m=30.0, demanda_m3s=demanda)],
              tramos=[_tramo(id="t", desde="B", hasta="N", longitud_m=800.0, diametro_m=0.25, c_hw=120.0)],
              bombas=[dict(id="bomba", desde="R", hasta="B", h0_m=h0, a_s2m5=a)])


def test_bomba_en_el_contrato_reporta_caudal_y_carga():
    r = red_permanente_contrato(_con_bomba())
    assert r.valor["bombas"]["bomba"]["caudal_m3s"] == pytest.approx(0.03, rel=1e-8)
    assert r.valor["bombas"]["bomba"]["carga_m"] == pytest.approx(60.0 - 2000.0 * 0.03 ** 2, rel=1e-8)
    assert any("curva" in x.lower() for x in r.supuestos)


def test_bomba_lejos_del_punto_de_diseno_de_la_curva_activa_borde():
    # Q_cierre-cero = sqrt(h0/a) = 0.1732; con 0.15 m3/s se opera en el tramo final de la curva parabólica extrapolada
    r = red_permanente_contrato(_con_bomba(demanda=0.15))
    assert r.en_borde_dominio is True


def test_bomba_que_no_vence_la_carga_estatica_es_valueerror():
    with pytest.raises(ValueError, match="no vence"):
        red_permanente_contrato(_con_bomba(h0=5.0, demanda=0.0))


def test_valvula_en_el_contrato_reporta_perdida_y_baja_la_presion_aguas_abajo():
    nodos = [dict(id="R", cota_m=0.0, carga_fija_m=50.0), dict(id="V1", cota_m=0.0), dict(id="V2", cota_m=0.0),
             dict(id="N", cota_m=0.0, demanda_m3s=0.05)]
    tramos = [_tramo(id="a", desde="R", hasta="V1", longitud_m=300.0, diametro_m=0.25),
              _tramo(id="b", desde="V2", hasta="N", longitud_m=300.0, diametro_m=0.25)]
    sin = red_permanente_contrato(_s(nodos=[n for n in nodos if n["id"] != "V2"], tramos=[_tramo(id="a", desde="R", hasta="V1", longitud_m=300.0, diametro_m=0.25),
                                                          _tramo(id="b", desde="V1", hasta="N", longitud_m=300.0, diametro_m=0.25)]))
    con = red_permanente_contrato(_s(nodos=nodos, tramos=tramos, valvulas=[dict(id="v", desde="V1", hasta="V2", diametro_m=0.25, k=50.0)]))
    assert con.valor["valvulas"]["v"]["perdida_m"] > 0
    assert con.valor["nodos"]["N"]["presion_m"] < sin.valor["nodos"]["N"]["presion_m"]
