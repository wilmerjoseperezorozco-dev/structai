"""motor-pilotes (#118). Referencias independientes: cálculo a mano de las ecuaciones de la NSR-10 (H.4.7-2/-3 y
Tablas H.4.7-1 y H.2.4-1), Converse-Labarre (valor de texto para 3×3 con s = 3D) y Nc de Skempton (9 para pilote
profundo cuadrado o circular). Más propiedades: monotonía, invariancia al partir estratos y fallas explícitas."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from pydantic import ValidationError

from contrato_motor.propiedades import verificar_monotonia
from src.axial import Estrato, Pilote, alfa_nsr10, capacidad_individual
from src.contrato_api import SolicitudPilotes, pilotes_contrato
from src.grupo import capacidad_grupo, eficiencia_converse_labarre, nc_skempton

ARCILLA = dict(espesor_m=20.0, gamma_kn_m3=18.0, gamma_sat_kn_m3=19.0, comportamiento="no_drenado", su_kpa=50.0)
ARENA = dict(gamma_kn_m3=18.0, gamma_sat_kn_m3=20.0, comportamiento="drenado", c_kpa=0.0, phi_deg=32.0, k_lateral=1.0,
             qp_ult_kpa=3000.0)


def _pil(L=15.0, D=0.5, seccion="circular"):
    return Pilote(seccion=seccion, ancho_m=D, longitud_m=L, tipo="excavado")


# --- Referencia 1: arcilla, método α de la NSR-10 a mano ----------------------------------------------------------
def test_alfa_a_mano_y_tope_en_1():
    assert alfa_nsr10(50.0) == pytest.approx(0.2 + 0.8 * math.exp(0.35 - 100.0 / 101.325))
    assert alfa_nsr10(10.0) == 1.0                       # 0.2 + 0.8·e^(0.35−0.197) = 1.13 → se acota a 1.0
    verificar_monotonia(alfa_nsr10, [30.0, 60.0, 120.0, 250.0], creciente=False)


def test_pilote_en_arcilla_coincide_con_el_calculo_a_mano():
    r = capacidad_individual([Estrato(**ARCILLA)], _pil(), nivel_freatico_m=None, combinacion="cm_cv_normal")
    a = 0.2 + 0.8 * math.exp(0.35 - 2 * 50.0 / 101.325)
    qs = a * 50.0 * math.pi * 0.5 * 15.0
    qp = 9.0 * 50.0 * math.pi * 0.5 ** 2 / 4.0
    assert r["qs_ult_kn"] == pytest.approx(qs)
    assert r["qs_adm_kn"] == pytest.approx(qs / 1.80)    # FSBUM, Tabla H.2.4-1
    assert r["qp_adm_kn"] == pytest.approx(qp / 3.0)     # F_SICP, Tabla H.4.7-1
    assert r["q_adm_kn"] == pytest.approx(qs / 1.80 + qp / 3.0)


# --- Referencia 2: arena con nivel freático, τL = 2/3·τF a mano ----------------------------------------------------
def test_pilote_en_arena_con_nivel_freatico_a_mano():
    r = capacidad_individual([Estrato(espesor_m=15.0, **ARENA)], _pil(L=10.0), nivel_freatico_m=2.0,
                             combinacion="cm_cv_maxima")
    s2 = 18.0 * 2.0
    s10 = s2 + (20.0 - 9.81) * 8.0
    integral = (0 + s2) / 2 * 2.0 + (s2 + s10) / 2 * 8.0
    qs = 2.0 / 3.0 * 1.0 * math.tan(math.radians(32.0)) * math.pi * 0.5 * integral
    assert r["qs_ult_kn"] == pytest.approx(qs)
    assert r["qs_adm_kn"] == pytest.approx(qs / 1.25)    # FSBM CM+CV máxima
    assert r["qp_adm_kn"] == pytest.approx(3000.0 * math.pi * 0.25 / 4.0 / 2.5)


# --- Referencia 3 y 4: eficiencia de grupo y Nc de Skempton ------------------------------------------------------
def test_converse_labarre_valor_de_texto():
    assert eficiencia_converse_labarre(3, 3, 1.5, 0.5) == pytest.approx(0.7268, abs=1e-4)
    assert eficiencia_converse_labarre(1, 1, 0.0, 0.5) == 1.0


def test_nc_skempton_profundo_cuadrado_es_9():
    assert nc_skempton(20.0, 2.0, 2.0) == pytest.approx(9.0)
    assert nc_skempton(0.0, 2.0, 2.0) == pytest.approx(6.0)


def test_grupo_en_arcilla_bloque_a_mano_y_modo_que_gobierna():
    estr, p = [Estrato(**ARCILLA)], _pil()
    junto = capacidad_grupo(estr, p, filas=3, columnas=3, separacion_m=0.6, nivel_freatico_m=None, combinacion="cm_cv_normal",
                            eficiencia="ninguna")
    bg = 2 * 0.6 + 0.5
    fuste, base = 4 * bg * 50.0 * 15.0, bg * bg * 9.0 * 50.0
    assert junto["bloque"]["q_ult_kn"] == pytest.approx(fuste + base)
    assert junto["bloque"]["q_adm_kn"] == pytest.approx(fuste / 1.80 + base / 3.0)
    assert junto["gobierna"] == "bloque"
    separado = capacidad_grupo(estr, p, filas=3, columnas=3, separacion_m=1.5, nivel_freatico_m=None, combinacion="cm_cv_normal",
                               eficiencia="ninguna")
    assert separado["gobierna"] == "suma_individuales"
    con_e = capacidad_grupo(estr, p, filas=3, columnas=3, separacion_m=1.5, nivel_freatico_m=None, combinacion="cm_cv_normal",
                            eficiencia="converse_labarre")
    assert con_e["modos_adm_kn"]["eficiencia"] == pytest.approx((1 - math.degrees(math.atan(1 / 3)) * 12 / 810) * 9 * con_e["individual"]["q_adm_kn"])
    assert con_e["q_adm_grupo_kn"] == min(con_e["modos_adm_kn"].values())


def test_eficiencia_sin_metodo_reconocido_falla():
    with pytest.raises(ValueError, match="eficiencia"):
        capacidad_grupo([Estrato(**ARCILLA)], _pil(), filas=2, columnas=2, separacion_m=1.5, nivel_freatico_m=None,
                        combinacion="cm_cv_normal", eficiencia="feld")


# --- Propiedades -------------------------------------------------------------------------------------------------
def test_monotonia_en_longitud_su_y_nivel_freatico():
    f_l = lambda L: capacidad_individual([Estrato(**ARCILLA)], _pil(L=L), nivel_freatico_m=None, combinacion="cm_cv_normal")["q_adm_kn"]
    verificar_monotonia(f_l, [5.0, 10.0, 15.0, 19.0], estricta=True)
    f_su = lambda su: capacidad_individual([Estrato(**{**ARCILLA, "su_kpa": su})], _pil(), nivel_freatico_m=None,
                                           combinacion="cm_cv_normal")["q_adm_kn"]
    verificar_monotonia(f_su, [20.0, 40.0, 80.0, 160.0], estricta=True)
    f_nf = lambda nf: capacidad_individual([Estrato(espesor_m=15.0, **ARENA)], _pil(L=10.0), nivel_freatico_m=nf,
                                           combinacion="cm_cv_normal")["q_adm_kn"]
    verificar_monotonia(f_nf, [0.0, 2.0, 5.0, 9.0, 12.0], estricta=True)   # nivel freático más profundo → más σ'v


def test_partir_un_estrato_en_dos_no_cambia_el_resultado():
    uno = capacidad_individual([Estrato(espesor_m=15.0, **ARENA)], _pil(L=10.0), nivel_freatico_m=3.3, combinacion="cm_cv_normal")
    dos = capacidad_individual([Estrato(espesor_m=6.1, **ARENA), Estrato(espesor_m=8.9, **ARENA)], _pil(L=10.0),
                               nivel_freatico_m=3.3, combinacion="cm_cv_normal")
    assert dos["q_adm_kn"] == pytest.approx(uno["q_adm_kn"])


def test_factores_de_seguridad_mas_altos_dan_menos_capacidad():
    caps = [capacidad_individual([Estrato(espesor_m=15.0, **ARENA)], _pil(L=10.0), nivel_freatico_m=2.0, combinacion=c)["q_adm_kn"]
            for c in ("cm_cv_normal", "cm_cv_maxima", "cm_cv_sismo")]
    assert caps[0] < caps[1] < caps[2]


# --- Fallas explícitas (regla 1) ---------------------------------------------------------------------------------
def test_su_con_sismo_no_se_permite():
    with pytest.raises(ValueError, match="seudo-estático"):
        capacidad_individual([Estrato(**ARCILLA)], _pil(), nivel_freatico_m=None, combinacion="cm_cv_sismo")


@pytest.mark.parametrize("estratos, L, nf, msg", [
    ([Estrato(**ARCILLA)], 25.0, None, "por debajo del perfil"),
    ([Estrato(espesor_m=15.0, **{**ARENA, "qp_ult_kpa": None})], 10.0, None, "qp_ult_kpa"),
    ([Estrato(espesor_m=15.0, **{**ARENA, "gamma_sat_kn_m3": None})], 10.0, 2.0, "gamma_sat"),
    ([Estrato(espesor_m=15.0, **{**ARENA, "k_lateral": None})], 10.0, None, "k_lateral"),
])
def test_entradas_incompletas_fallan_sin_valores_por_defecto(estratos, L, nf, msg):
    with pytest.raises(ValueError, match=msg):
        capacidad_individual(estratos, _pil(L=L), nivel_freatico_m=nf, combinacion="cm_cv_normal")


def test_combinacion_desconocida_falla():
    with pytest.raises(ValueError, match="Tabla H.4.7-1"):
        capacidad_individual([Estrato(**ARCILLA)], _pil(), nivel_freatico_m=None, combinacion="otra")


# --- Contrato ----------------------------------------------------------------------------------------------------
def _sol(**kw):
    base = dict(estratos=[ARCILLA], nivel_freatico_m=None, seccion="circular", ancho_m=0.5, longitud_m=15.0, tipo="excavado",
                filas=2, columnas=2, separacion_m=1.5, combinacion="cm_cv_normal", eficiencia_grupo="ninguna",
                reaccion_vertical_kn=800.0)
    base.update(kw)
    return SolicitudPilotes(**base)


def test_contrato_completo_y_razon_demanda_capacidad():
    r = pilotes_contrato(_sol())
    v = r.valor
    assert v["razon_demanda_capacidad"] == pytest.approx(800.0 / v["capacidad_grupo_kn"])
    assert v["cumple"] == (v["razon_demanda_capacidad"] <= 1.0)
    assert "H.4.7" in r.referencia_normativa and r.supuestos and r.aviso_responsabilidad_profesional
    assert isinstance(r.en_borde_dominio, bool)


def test_contrato_borde_de_dominio_y_avisos():
    assert pilotes_contrato(_sol(longitud_m=19.5)).en_borde_dominio                      # punta a < 3D de la base
    r = pilotes_contrato(_sol(estratos=[{**ARENA, "espesor_m": 20.0}], nivel_freatico_m=2.0))
    assert any("bloque" in a for a in r.advertencias)                                     # bloque drenado: próximamente
    assert pilotes_contrato(_sol(separacion_m=1.0)).en_borde_dominio                     # s/D = 2 < 2.5


def test_contrato_grupo_sin_separacion_falla():
    with pytest.raises(ValidationError):
        _sol(separacion_m=None)
