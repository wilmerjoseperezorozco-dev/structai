"""motor-pilotes, suelo granular con SPT (#118). Referencias independientes: valores a mano de las ecuaciones del CCP-14
(10.4.6.2.4-1, 10.7.3.8.6g-1/-2, 10.8.3.5.2b/c) e integral del fuste con scipy.integrate.quad sobre la función
continua (el motor integra en subtramos de 0.5 m). Más propiedades: monotonía, invariancia y fallas explícitas."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from scipy.integrate import quad

from src.arena_spt import EstratoSPT, beta_ccp14, capacidad_spt, cn_ccp14
from src.axial import Pilote


def _cn_mano(sv_kpa):
    return min(2.0, 0.77 * math.log10(1.92 / (sv_kpa / 1000.0)))


def _pil(tipo, L=10.0, D=0.4):
    return Pilote(seccion="circular", ancho_m=D, longitud_m=L, tipo=tipo)


def _arena(n60=20.0, espesor=20.0, suelo="arena", gamma=18.0):
    return EstratoSPT(espesor_m=espesor, gamma_kn_m3=gamma, gamma_sat_kn_m3=20.0, n60=n60, suelo=suelo)


# --- CN (10.4.6.2.4-1) -------------------------------------------------------------------------------------------
def test_cn_a_mano_y_tope():
    assert cn_ccp14(100.0) == pytest.approx(0.77 * math.log10(19.2))      # 0.988
    assert cn_ccp14(10.0) == pytest.approx(0.77 * math.log10(192.0))      # 1.758
    assert cn_ccp14(1.0) == 2.0                                            # tope CN < 2.0
    with pytest.raises(ValueError):
        cn_ccp14(0.0)


# --- β (10.8.3.5.2b) ---------------------------------------------------------------------------------------------
def test_beta_a_mano():
    assert beta_ccp14(10.0, 30, "arena") == pytest.approx(1.5 - 7.7e-3 * 100.0)          # 0.73
    assert beta_ccp14(1.0, 30, "arena") == 1.2                                           # tope superior
    assert beta_ccp14(1.0, 7.5, "arena") == pytest.approx(0.5 * (1.5 - 7.7e-3 * math.sqrt(1000.0)))
    assert beta_ccp14(30.0, 30, "arena") == 0.25                                         # tope inferior
    assert beta_ccp14(10.0, 30, "grava") == pytest.approx(2.0 - 0.00082 * 1000.0)        # 1.18


# --- Hincado, Meyerhof (10.7.3.8.6g) ------------------------------------------------------------------------------
def test_hincado_meyerhof_a_mano():
    r = capacidad_spt([_arena(20.0)], _pil("hincado"), nivel_freatico_m=None, combinacion="cm_cv_normal")
    p = math.pi * 0.4
    fuste, _ = quad(lambda z: 1.9 * _cn_mano(18.0 * z) * 20.0 * p, 0.0, 10.0, points=[0.27], limit=200)
    assert r["qs_ult_kn"] == pytest.approx(fuste, rel=2e-3)
    n1 = 0.77 * math.log10(1.92 / 0.18) * 20.0                # σ'v punta = 180 kPa → N1_60 = 15.83
    assert r["n1_60_punta"] == pytest.approx(n1)
    assert r["qp_unitaria_kpa"] == pytest.approx(min(38.0 * n1 * 10.0 / 0.4, 400.0 * n1))  # gobierna qℓ = 0.4·N1_60
    assert r["limitada"] is True
    assert r["qp_ult_kn"] == pytest.approx(400.0 * n1 * math.pi * 0.16 / 4.0)
    assert r["qs_adm_kn"] == pytest.approx(r["qs_ult_kn"] / 1.5)
    assert r["qp_adm_kn"] == pytest.approx(r["qp_ult_kn"] / 3.0)


def test_hincado_penetracion_corta_no_limitada_y_limo():
    # 1 m dentro del estrato de apoyo: Db/D = 2.5 → qp = 0.038·N1·2.5 MPa < 0.4·N1
    est = [_arena(5.0, espesor=9.0), _arena(30.0, espesor=10.0)]
    r = capacidad_spt(est, _pil("hincado"), nivel_freatico_m=None, combinacion="cm_cv_normal")
    n1 = _cn_mano(180.0) * 30.0
    assert r["db_m"] == pytest.approx(1.0)
    assert r["qp_unitaria_kpa"] == pytest.approx(38.0 * n1 * 2.5)
    assert r["limitada"] is False
    limo = capacidad_spt([_arena(20.0, suelo="limo_no_plastico")], _pil("hincado"), nivel_freatico_m=None,
                         combinacion="cm_cv_normal")
    assert limo["qp_unitaria_kpa"] == pytest.approx(300.0 * _cn_mano(180.0) * 20.0)


# --- Excavado, β y punta (10.8.3.5.2b/c) ---------------------------------------------------------------------------
def test_excavado_beta_a_mano():
    D = 1.0
    r = capacidad_spt([_arena(30.0)], _pil("excavado", D=D), nivel_freatico_m=None, combinacion="cm_cv_normal")
    fuste, _ = quad(lambda z: min(190.0, beta_ccp14(z, 30.0, "arena") * 18.0 * z) * math.pi * D, 0.0, 10.0, limit=200)
    assert r["qs_ult_kn"] == pytest.approx(fuste, rel=2e-3)
    assert r["qp_unitaria_kpa"] == pytest.approx(57.0 * 30.0)                # 0.057·N60 MPa
    assert r["qp_ult_kn"] == pytest.approx(1710.0 * math.pi / 4.0)


def test_excavado_topes_qs_y_qp():
    g = capacidad_spt([_arena(50.0, suelo="grava")], _pil("excavado", L=12.0, D=1.0), nivel_freatico_m=None,
                      combinacion="cm_cv_normal")
    assert max(t["qs_kpa"] for t in g["tramos"]) == pytest.approx(190.0)    # qs ≤ 0.19 MPa
    assert g["qp_unitaria_kpa"] == pytest.approx(57.0 * 50.0)                # 2.85 MPa < 3.0
    with pytest.raises(ValueError, match="geomaterial intermedio"):
        capacidad_spt([_arena(60.0)], _pil("excavado"), nivel_freatico_m=None, combinacion="cm_cv_normal")


# --- Propiedades ----------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("tipo", ["hincado", "excavado"])
def test_monotonia_en_n60_y_nivel_freatico(tipo):
    caps = [capacidad_spt([_arena(n)], _pil(tipo), nivel_freatico_m=None, combinacion="cm_cv_normal")["q_ult_kn"]
            for n in (5, 10, 20, 40)]
    assert caps == sorted(caps) and len(set(caps)) == 4
    seco = capacidad_spt([_arena(20.0)], _pil(tipo), nivel_freatico_m=None, combinacion="cm_cv_normal")
    humedo = capacidad_spt([_arena(20.0)], _pil(tipo), nivel_freatico_m=2.0, combinacion="cm_cv_normal")
    # con el nivel freático baja σ'v: en β baja el fuste; en Meyerhof sube CN pero la punta cambia de forma acotada
    assert humedo["sigma_v_ef_punta_kpa"] < seco["sigma_v_ef_punta_kpa"]
    if tipo == "excavado":
        assert humedo["q_ult_kn"] < seco["q_ult_kn"]


def test_invariancia_al_partir_estrato_excavado():
    a = capacidad_spt([_arena(25.0)], _pil("excavado"), nivel_freatico_m=3.0, combinacion="cm_cv_normal")
    b = capacidad_spt([_arena(25.0, espesor=4.0), _arena(25.0, espesor=16.0)], _pil("excavado"), nivel_freatico_m=3.0,
                      combinacion="cm_cv_normal")
    assert b["q_ult_kn"] == pytest.approx(a["q_ult_kn"], rel=2e-3)


def test_fallas_explicitas():
    with pytest.raises(ValueError, match="limo"):
        capacidad_spt([_arena(20.0, suelo="limo_no_plastico")], _pil("excavado"), nivel_freatico_m=None,
                      combinacion="cm_cv_normal")
    with pytest.raises(ValueError, match="n60"):
        capacidad_spt([_arena(0.0)], _pil("hincado"), nivel_freatico_m=None, combinacion="cm_cv_normal")
    with pytest.raises(ValueError, match="gamma_sat"):
        capacidad_spt([EstratoSPT(espesor_m=20.0, gamma_kn_m3=18.0, n60=20.0, suelo="arena")], _pil("hincado"),
                      nivel_freatico_m=2.0, combinacion="cm_cv_normal")
    with pytest.raises(ValueError):
        capacidad_spt([_arena(20.0)], _pil("hincado"), nivel_freatico_m=None, combinacion="desconocida")
