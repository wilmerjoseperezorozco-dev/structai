import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError

from src.contrato_ariete import SolicitudAriete, ariete_contrato


def _s(**kw):
    base = dict(longitud_m=1000.0, diametro_m=0.5, celeridad_ms=1000.0, f_darcy=0.0, caudal_m3s=0.3, carga_embalse_m=400.0,
                t_cierre_s=0.0, t_fin_s=8.0)
    base.update(kw)
    return SolicitudAriete(**base)


def test_contrato_basico_joukowsky_y_supuestos():
    r = ariete_contrato(_s())
    v0 = 0.3 / (math.pi * 0.25 ** 2)
    assert r.valor["joukowsky_m"] == pytest.approx(1000.0 * v0 / 9.80665, rel=1e-12)
    assert r.valor["valvula"]["h_max_m"] == pytest.approx(400.0 + r.valor["joukowsky_m"], rel=1e-9)
    assert any("Courant" in x for x in r.supuestos) and r.valor["cavitacion"] is False


def test_celeridad_por_korteweg_cuando_se_dan_espesor_y_modulo():
    r = ariete_contrato(_s(celeridad_ms=None, espesor_m=0.01, e_tuberia_pa=210e9, poisson=0.3, anclaje="dilatacion"))
    esperado = math.sqrt(2.07e9 / 1000.0) / math.sqrt(1 + 2.07e9 * 0.5 / (210e9 * 0.01))
    assert r.valor["celeridad_ms"] == pytest.approx(esperado, rel=1e-12)
    assert any("Korteweg" in x for x in r.supuestos)


@pytest.mark.parametrize("kw", [dict(celeridad_ms=None), dict(espesor_m=0.01), dict(celeridad_ms=None, espesor_m=0.01),
                                dict(celeridad_ms=None, e_tuberia_pa=210e9)])
def test_la_celeridad_debe_darse_por_una_sola_via(kw):
    with pytest.raises(ValidationError):
        _s(**kw)


def test_cavitacion_activa_borde_y_se_declara():
    r = ariete_contrato(_s(carga_embalse_m=30.0))
    assert r.valor["cavitacion"] is True and r.en_borde_dominio is True and any("Cavitación" in x for x in r.supuestos)


def test_tiempo_de_cierre_cerca_del_critico_activa_borde():
    assert ariete_contrato(_s(t_cierre_s=2.0)).en_borde_dominio is True       # 2L/a = 2 s


def test_malla_insuficiente_activa_borde():
    r = ariete_contrato(_s(t_cierre_s=3.0, n_tramos=2, t_fin_s=12.0))
    assert r.valor["malla"] is not None and (r.en_borde_dominio is True or r.valor["malla"]["diferencia_relativa"] <= 0.02)


def test_malla_fina_con_cierre_lento_converge_sin_borde_por_malla():
    r = ariete_contrato(_s(t_cierre_s=8.0, n_tramos=100, t_fin_s=20.0))
    assert r.valor["malla"]["diferencia_relativa"] < 0.02 and r.en_borde_dominio is False


def test_carga_insuficiente_es_valueerror():
    with pytest.raises(ValueError, match="carga"):
        ariete_contrato(_s(f_darcy=0.05, carga_embalse_m=1.0))
