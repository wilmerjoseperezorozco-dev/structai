"""Hallazgos de la segunda revisión adversarial (bombas, válvulas, periodo extendido, ariete)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pydantic import ValidationError

from src.ariete import celeridad_korteweg, simular_ariete
from src.contrato_api import SolicitudRed, red_permanente_contrato
from src.contrato_ariete import SolicitudAriete, ariete_contrato
from src.contrato_periodo import SolicitudPeriodo, periodo_extendido_contrato
from src.gradiente import resolver_red
from src.periodo import simular_periodo


def _tanque(id="T", area=50.0, nivel=100.0, nmin=0.0, nmax=200.0, fondo=0.0):
    return dict(id=id, cota_fondo_m=fondo, area_m2=area, nivel_inicial_m=nivel, nivel_min_m=nmin, nivel_max_m=nmax)


# ── A1: tope de trabajo y memoria en periodo extendido ──────────────────────────────────────────────────────────────────
def test_periodo_con_trabajo_excesivo_se_rechaza_antes_de_calcular():
    n = 300
    nodos = [dict(id="T", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None)] + [
        dict(id=f"n{i}", cota_m=0.0, demanda_m3s=1e-6, carga_fija_m=None) for i in range(n)]
    tramos = [dict(id="p0", desde="T", hasta="n0", longitud_m=10.0, diametro_m=0.3, c_hw=130.0)] + [
        dict(id=f"p{i}", desde=f"n{i - 1}", hasta=f"n{i}", longitud_m=10.0, diametro_m=0.3, c_hw=130.0) for i in range(1, n)]
    with pytest.raises(ValueError, match="trabajo|reduzca"):
        simular_periodo(nodos, tramos, tanques=[_tanque(area=1e6, nivel=50.0)], paso_s=60.0, n_pasos=2000)


# ── A2: inestabilidad de Euler explícito con paso grande ─────────────────────────────────────────────────────────────────
def test_euler_con_paso_grande_entre_dos_tanques_se_detecta_en_vez_de_oscilar_en_silencio():
    nodos = [dict(id="A", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None), dict(id="B", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None)]
    tramos = [dict(id="p", desde="A", hasta="B", longitud_m=500.0, diametro_m=0.2, c_hw=130.0)]
    with pytest.raises(ValueError, match="oscil|paso"):
        simular_periodo(nodos, tramos, tanques=[_tanque("A", nivel=100.0), _tanque("B", nivel=95.0)], paso_s=5000.0, n_pasos=40)


def test_el_mismo_caso_con_paso_pequeno_converge_sin_error():
    nodos = [dict(id="A", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None), dict(id="B", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None)]
    tramos = [dict(id="p", desde="A", hasta="B", longitud_m=500.0, diametro_m=0.2, c_hw=130.0)]
    s = simular_periodo(nodos, tramos, tanques=[_tanque("A", nivel=100.0), _tanque("B", nivel=95.0)], paso_s=100.0, n_pasos=40)
    d0 = s["pasos"][0]["tanques"]["A"]["nivel_m"] - s["pasos"][0]["tanques"]["B"]["nivel_m"]
    d1 = s["pasos"][-1]["tanques"]["A"]["nivel_m"] - s["pasos"][-1]["tanques"]["B"]["nivel_m"]
    assert abs(d1) < abs(d0)


# ── M1: altitud en la cavitación ────────────────────────────────────────────────────────────────────────────────────────
def _ariete(**kw):
    base = dict(longitud_m=1000.0, diametro_m=0.5, celeridad_ms=1000.0, f_darcy=0.0, caudal_m3s=0.3, carga_embalse_m=400.0,
                t_cierre_s=0.0, t_fin_s=8.0)
    base.update(kw)
    return SolicitudAriete(**base)


def test_la_altitud_baja_la_carga_de_vapor_con_la_atmosfera_estandar():
    p = 101325.0 * (1 - 2.25577e-5 * 2600.0) ** 5.25588
    esperado = -(p - 2339.0) / (1000.0 * 9.80665)
    r = ariete_contrato(_ariete(altitud_m=2600.0))
    assert r.valor["h_vapor_m"] == pytest.approx(esperado, rel=1e-9) and -8.0 < esperado < -6.5
    assert ariete_contrato(_ariete()).valor["h_vapor_m"] == pytest.approx(-10.0932, abs=1e-3)


def test_cavitacion_que_solo_ocurre_en_altitud_se_marca():
    # carga mínima ≈ 400 − ΔH. Se ajusta el embalse para que la mínima caiga entre −7,3 m y −10,09 m
    dh = 1000.0 * (0.3 / (math.pi * 0.25 ** 2)) / 9.80665
    h_emb = dh - 9.0
    assert ariete_contrato(_ariete(carga_embalse_m=h_emb)).valor["cavitacion"] is False
    assert ariete_contrato(_ariete(carga_embalse_m=h_emb, altitud_m=2600.0)).valor["cavitacion"] is True


# ── M2: horizonte insuficiente ──────────────────────────────────────────────────────────────────────────────────────────
def test_t_fin_menor_que_cierre_mas_periodo_marca_borde_y_se_declara():
    r = ariete_contrato(_ariete(t_cierre_s=5.0, t_fin_s=2.0))
    assert r.en_borde_dominio is True and any("horizonte" in x.lower() for x in r.supuestos)
    assert ariete_contrato(_ariete(t_cierre_s=5.0, t_fin_s=20.0)).en_borde_dominio is False


# ── M3: Korteweg con Poisson y anclaje ──────────────────────────────────────────────────────────────────────────────────
def test_korteweg_con_coeficiente_de_anclaje():
    d, e, E, nu = 0.2, 0.01, 3e9, 0.38
    c1 = 1 - nu ** 2
    esperado = math.sqrt(2.07e9 / 1000.0) / math.sqrt(1 + 2.07e9 * d / (E * e) * c1)
    assert celeridad_korteweg(d, e, E, c1=c1) == pytest.approx(esperado, rel=1e-12)
    assert celeridad_korteweg(d, e, E, c1=c1) > celeridad_korteweg(d, e, E, c1=1.0)


def test_el_contrato_exige_poisson_y_anclaje_en_la_via_indirecta():
    with pytest.raises(ValidationError):
        _ariete(celeridad_ms=None, espesor_m=0.01, e_tuberia_pa=3e9)
    r = ariete_contrato(_ariete(celeridad_ms=None, espesor_m=0.01, e_tuberia_pa=3e9, poisson=0.38, anclaje="todo"))
    esperado = math.sqrt(2.07e9 / 1000.0) / math.sqrt(1 + 2.07e9 * 0.5 / (3e9 * 0.01) * (1 - 0.38 ** 2))
    assert r.valor["celeridad_ms"] == pytest.approx(esperado, rel=1e-12)
    assert any("viscoel" in x.lower() for x in r.supuestos)


# ── M4: verificación de malla que no debe convertirse en 422 ────────────────────────────────────────────────────────────
def test_la_verificacion_de_malla_que_excede_el_limite_se_omite_con_nota_y_borde():
    r = ariete_contrato(_ariete(n_tramos=50, t_fin_s=3600.0, celeridad_ms=1000.0))
    assert r.valor["malla"] is None and r.en_borde_dominio is True and any("malla" in x.lower() for x in r.supuestos)


# ── M5: banderas compartidas, válvulas en límites, extremos sin tanques ────────────────────────────────────────────────
def test_velocidad_maxima_se_verifica_tambien_en_valvulas():
    nodos = [dict(id="R", cota_m=0.0, carga_fija_m=100.0), dict(id="V", cota_m=0.0), dict(id="N", cota_m=0.0, demanda_m3s=0.05)]
    tramos = [dict(id="a", desde="R", hasta="V", longitud_m=100.0, diametro_m=0.3, c_hw=130.0)]
    valv = [dict(id="v", desde="V", hasta="N", diametro_m=0.05, k=2.0)]
    r = red_permanente_contrato(SolicitudRed(nodos=nodos, tramos=tramos, valvulas=valv, velocidad_max_ms=3.0))
    assert r.valor["cumple"] is False and any("válvula v" in x for x in r.valor["incumplimientos"])


def _periodo(**kw):
    base = dict(nodos=[dict(id="T", cota_m=40.0), dict(id="N", cota_m=30.0, demanda_m3s=0.01)],
                tramos=[dict(id="p", desde="T", hasta="N", longitud_m=500.0, diametro_m=0.04, c_hw=190.0)],
                tanques=[dict(id="T", cota_fondo_m=40.0, area_m2=100.0, nivel_inicial_m=5.0, nivel_min_m=0.5, nivel_max_m=10.0)],
                paso_s=600.0, n_pasos=3)
    base.update(kw)
    return SolicitudPeriodo(**base)


def test_el_periodo_hereda_las_banderas_del_permanente():
    r = periodo_extendido_contrato(_periodo())
    assert r.en_borde_dominio is True
    texto = " ".join(r.supuestos)
    assert "50 mm" in texto and "60" in texto           # diámetro < 50 mm y C fuera de rango


def test_el_periodo_no_incluye_el_nudo_del_tanque_en_los_extremos_de_presion():
    r = periodo_extendido_contrato(_periodo(tramos=[dict(id="p", desde="T", hasta="N", longitud_m=500.0, diametro_m=0.2, c_hw=130.0)]))
    assert "T" not in r.valor["extremos_nodos"] and "N" in r.valor["extremos_nodos"]


# ── M6: bomba sin retención en periodo → resultado parcial, no 422 ───────────────────────────────────────────────────────
def test_bomba_que_deja_de_vencer_en_periodo_devuelve_resultado_parcial_con_evento():
    nodos = [dict(id="R", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=0.0), dict(id="B", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None),
             dict(id="T", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=None)]
    tramos = [dict(id="p", desde="B", hasta="T", longitud_m=50.0, diametro_m=0.3, c_hw=130.0)]
    bombas = [dict(id="P", desde="R", hasta="B", h0_m=80.0, a_s2m5=5000.0)]
    s = simular_periodo(nodos, tramos, bombas=bombas, tanques=[_tanque("T", area=2.0, nivel=10.0, nmax=200.0)], paso_s=600.0, n_pasos=30)
    assert s["completo"] is False and any("retención" in e for e in s["eventos"]) and len(s["pasos"]) >= 1


# ── M7: entradas extremas → ValueError / 422, nunca ZeroDivisionError ───────────────────────────────────────────────────
@pytest.mark.parametrize("campo,valor", [("diametro_m", 1e-100), ("c_hw", 1e-200), ("longitud_m", 1e-100)])
def test_tramo_con_valores_degenerados_da_valueerror_en_el_solver(campo, valor):
    t = dict(id="p", desde="R", hasta="N", longitud_m=100.0, diametro_m=0.2, c_hw=130.0)
    t[campo] = valor
    with pytest.raises(ValueError):
        resolver_red([dict(id="R", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=50.0), dict(id="N", cota_m=0.0, demanda_m3s=0.01, carga_fija_m=None)], [t])


def test_el_esquema_impone_cotas_fisicas_inferiores():
    n = [dict(id="R", cota_m=0.0, carga_fija_m=50.0), dict(id="N", cota_m=0.0, demanda_m3s=0.01)]
    t = dict(id="p", desde="R", hasta="N", longitud_m=100.0, diametro_m=0.2, c_hw=130.0)
    for campo, valor in (("diametro_m", 1e-5), ("c_hw", 1.0), ("longitud_m", 1e-4)):
        with pytest.raises(ValidationError):
            SolicitudRed(nodos=n, tramos=[{**t, campo: valor}])
    with pytest.raises(ValidationError):
        _ariete(diametro_m=1e-5)


# ── B1: tipos enteros en ariete ─────────────────────────────────────────────────────────────────────────────────────────
def test_ariete_con_caudal_entero_no_trunca_los_caudales():
    ent = simular_ariete(longitud_m=1000, diametro_m=1.0, celeridad_ms=1000, f_darcy=0.02, caudal_m3s=1, carga_embalse_m=100,
                         t_cierre_s=8, t_fin_s=20, n_tramos=20)
    flo = simular_ariete(longitud_m=1000.0, diametro_m=1.0, celeridad_ms=1000.0, f_darcy=0.02, caudal_m3s=1.0, carga_embalse_m=100.0,
                         t_cierre_s=8.0, t_fin_s=20.0, n_tramos=20)
    assert ent["valvula"]["h_max_m"] == pytest.approx(flo["valvula"]["h_max_m"], rel=1e-12)


# ── B4/B5: el peor caso por elemento ────────────────────────────────────────────────────────────────────────────────────
def test_el_periodo_reporta_el_peor_paso_de_cada_incumplimiento_no_el_primero():
    nodos = [dict(id="T", cota_m=40.0), dict(id="N", cota_m=30.0, demanda_m3s=0.02)]
    tramos = [dict(id="p", desde="T", hasta="N", longitud_m=500.0, diametro_m=0.2, c_hw=130.0)]
    tq = [dict(id="T", cota_fondo_m=40.0, area_m2=20.0, nivel_inicial_m=9.0, nivel_min_m=0.5, nivel_max_m=10.0)]
    r = periodo_extendido_contrato(SolicitudPeriodo(nodos=nodos, tramos=tramos, tanques=tq, paso_s=300.0, n_pasos=20,
                                                    presion_min_m=100.0))
    pres = [x for x in r.valor["incumplimientos"] if "nudo N" in x]
    assert len(pres) == 1
    peor = r.valor["extremos_nodos"]["N"]["presion_min_m"]
    assert f"{peor:.2f}" in pres[0]
