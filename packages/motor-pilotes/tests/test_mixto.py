"""motor-pilotes, perfil mixto (#118). Referencias: equivalencia exacta con las funciones de una sola familia en perfiles
homogéneos, y cálculo a mano (α de la NSR-10 + Meyerhof/β del CCP-14, fuste granular con scipy.integrate.quad)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from scipy.integrate import quad

from src.arena_spt import EstratoSPT, beta_ccp14, capacidad_spt
from src.axial import Estrato, Pilote, alfa_nsr10, capacidad_individual
from src.mixto import capacidad_mixta


def _cn(sv):
    return min(2.0, 0.77 * math.log10(1.92 / (sv / 1000.0)))


def _pil(tipo, L=12.0, D=0.4):
    return Pilote(seccion="circular", ancho_m=D, longitud_m=L, tipo=tipo)


def _arcilla(espesor, su=40.0):
    return Estrato(espesor_m=espesor, gamma_kn_m3=17.0, gamma_sat_kn_m3=17.5, comportamiento="no_drenado", su_kpa=su)


def _arena(espesor, n60=25.0):
    return EstratoSPT(espesor_m=espesor, gamma_kn_m3=19.0, gamma_sat_kn_m3=20.0, n60=n60, suelo="arena")


@pytest.mark.parametrize("tipo", ["hincado", "excavado"])
def test_equivale_a_las_funciones_de_una_familia(tipo):
    arc = [_arcilla(8.0), _arcilla(12.0, su=70.0)]
    a = capacidad_individual(arc, _pil(tipo), nivel_freatico_m=2.0, combinacion="cm_cv_normal")
    b = capacidad_mixta(arc, _pil(tipo), nivel_freatico_m=2.0, combinacion="cm_cv_normal")
    assert (b["q_ult_kn"], b["q_adm_kn"]) == pytest.approx((a["q_ult_kn"], a["q_adm_kn"]), rel=1e-12)
    are = [_arena(5.0, 12.0), _arena(15.0, 30.0)]
    a = capacidad_spt(are, _pil(tipo), nivel_freatico_m=2.0, combinacion="cm_cv_sismo")
    b = capacidad_mixta(are, _pil(tipo), nivel_freatico_m=2.0, combinacion="cm_cv_sismo")
    assert (b["q_ult_kn"], b["q_adm_kn"]) == pytest.approx((a["q_ult_kn"], a["q_adm_kn"]), rel=1e-12)


def test_arcilla_sobre_arena_hincado_a_mano():
    r = capacidad_mixta([_arcilla(6.0), _arena(14.0)], _pil("hincado"), nivel_freatico_m=None,
                        combinacion="cm_cv_normal")
    p = math.pi * 0.4
    q_arc = alfa_nsr10(40.0) * 40.0 * p * 6.0
    q_are, _ = quad(lambda z: 1.9 * _cn(102.0 + 19.0 * (z - 6.0)) * 25.0 * p, 6.0, 12.0, limit=200)
    n1 = _cn(102.0 + 19.0 * 6.0) * 25.0                    # σ'v punta = 216 kPa
    qp = min(38.0 * n1 * 6.0 / 0.4, 400.0 * n1) * math.pi * 0.16 / 4.0
    assert r["qs_ult_por_estrato_kn"][0] == pytest.approx(q_arc)
    assert r["qs_ult_por_estrato_kn"][1] == pytest.approx(q_are, rel=2e-3)
    assert r["qp_ult_kn"] == pytest.approx(qp)
    assert r["q_adm_kn"] == pytest.approx(q_arc / 1.8 + r["qs_ult_por_estrato_kn"][1] / 1.5 + qp / 3.0)


def test_db_cuenta_solo_dentro_del_estrato_granular():
    r = capacidad_mixta([_arcilla(11.0), _arena(9.0)], _pil("hincado"), nivel_freatico_m=None,
                        combinacion="cm_cv_normal")
    n1 = _cn(17.0 * 11.0 + 19.0 * 1.0) * 25.0
    assert r["db_m"] == pytest.approx(1.0)
    assert r["qp_unitaria_kpa"] == pytest.approx(38.0 * n1 * 1.0 / 0.4)    # 2.5·D de empotramiento: no llega a qℓ
    assert r["limitada"] is False


def test_arena_sobre_arcilla_excavado_punta_9su():
    r = capacidad_mixta([_arena(5.0, 20.0), _arcilla(15.0, su=60.0)], _pil("excavado", D=0.8), nivel_freatico_m=None,
                        combinacion="cm_cv_normal")
    p = math.pi * 0.8
    q_are, _ = quad(lambda z: min(190.0, beta_ccp14(z, 20.0, "arena") * 19.0 * z) * p, 0.0, 5.0, limit=200)
    assert r["qs_ult_por_estrato_kn"][0] == pytest.approx(q_are, rel=2e-3)
    assert r["qs_ult_por_estrato_kn"][1] == pytest.approx(alfa_nsr10(60.0) * 60.0 * p * 7.0)
    assert r["qp_unitaria_kpa"] == pytest.approx(9.0 * 60.0)
    assert r["metodo_punta"].startswith("9·Su")


def test_sismo_con_arcilla_se_rechaza_y_tipo_desconocido():
    with pytest.raises(ValueError, match="seudo-estático"):
        capacidad_mixta([_arena(6.0), _arcilla(14.0)], _pil("hincado"), nivel_freatico_m=None,
                        combinacion="cm_cv_sismo")
    with pytest.raises(ValueError, match="no reconocido"):
        capacidad_mixta([{"espesor_m": 20.0}], _pil("hincado"), nivel_freatico_m=None, combinacion="cm_cv_normal")


def test_invariancia_al_partir_un_estrato_mixto():
    a = capacidad_mixta([_arcilla(6.0), _arena(14.0)], _pil("excavado"), nivel_freatico_m=3.0,
                        combinacion="cm_cv_normal")
    b = capacidad_mixta([_arcilla(2.5), _arcilla(3.5), _arena(14.0)], _pil("excavado"), nivel_freatico_m=3.0,
                        combinacion="cm_cv_normal")
    assert b["q_adm_kn"] == pytest.approx(a["q_adm_kn"], rel=1e-9)


def test_contrato_con_perfil_mixto():
    from pydantic import ValidationError
    from src.contrato_api import SolicitudPilotes, pilotes_contrato
    base = dict(nivel_freatico_m=None, seccion="circular", ancho_m=0.4, longitud_m=12.0, tipo="hincado", filas=1,
                columnas=1, separacion_m=None, combinacion="cm_cv_normal", eficiencia_grupo="ninguna",
                reaccion_vertical_kn=300.0)
    est = [dict(espesor_m=6.0, gamma_kn_m3=17.0, comportamiento="no_drenado", su_kpa=40.0),
           dict(espesor_m=14.0, gamma_kn_m3=19.0, comportamiento="granular_spt", n60=25.0, suelo_spt="arena")]
    r = pilotes_contrato(SolicitudPilotes(estratos=est, **base))
    directo = capacidad_mixta([_arcilla(6.0), _arena(14.0)], _pil("hincado"), nivel_freatico_m=None,
                              combinacion="cm_cv_normal")
    assert r.valor["capacidad_pilote_kn"] == pytest.approx(directo["q_adm_kn"])
    assert any("CYCU" in a for a in r.advertencias)
    with pytest.raises(ValidationError):
        SolicitudPilotes(estratos=[dict(espesor_m=20.0, gamma_kn_m3=19.0, comportamiento="granular_spt")], **base)
