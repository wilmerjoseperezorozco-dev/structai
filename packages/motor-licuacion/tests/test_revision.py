"""Correcciones de la revisión adversaria (2026-11-09) de motor-licuacion: integración por subcapas (Iwasaki evalúa FS(z)),
dominio ≤ 30 m, borde por σ'v > 100 kPa, supuestos honestos, entradas estrictas y propiedades faltantes."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from pydantic import ValidationError

from src.contrato_api import EstratoSPT, SolicitudLicuacionSPT, _clasificar_lpi, licuacion_spt_contrato
from src.spt import crr_spt, csr_seed_idriss


def _e(a, b, n=20.0, **kw):
    base = dict(z_top_m=a, z_base_m=b, gamma_kn_m3=18.0, gamma_sat_kn_m3=20.0, n1_60=n, finos_pct=3.0, no_plastico=True)
    base.update(kw)
    return EstratoSPT(**base)


def _s(estratos, nf=0.0, **kw):
    return SolicitudLicuacionSPT(**{**dict(amax_g=0.3, mw=7.5, nivel_freatico_m=nf, estratos=estratos), **kw})


def _v(estratos, nf=0.0, **kw):
    return licuacion_spt_contrato(_s(estratos, nf, **kw)).valor


# ── Hallazgo 1 (ALTA): un estrato grueso no puede esconder la licuación superficial ────────────────────────────────────
def test_estrato_grueso_de_60_m_ya_no_declara_ninguno():
    v = _v([_e(0, 60)])
    assert v["lpi"] > 30.0 and v["clasificacion_lpi"] == "muy alto" and v["fs_minimo"] < 0.7


def test_lpi_es_invariante_a_la_discretizacion_del_perfil():
    una = _v([_e(0, 20)])["lpi"]
    veinte = _v([_e(i, i + 1) for i in range(20)])["lpi"]
    assert una == pytest.approx(veinte, rel=1e-9)


def test_perfil_de_referencia_por_subcapas_calculado_a_mano_con_aritmetica_independiente():
    # 0–10 m, γ=18 / γsat=20, nf=2, (N1)60=15, FC=3 %, amax=0,3 g, Mw=7,5; subcapas de 1 m entre 2 y 10 m
    crr = 1 / 19 + 15 / 135 + 50 / (10 * 15 + 45) ** 2 - 1 / 200
    msf = 10 ** 2.24 / 7.5 ** 2.56
    lpi, fs_min = 0.0, 9e9
    for z0 in range(2, 10):
        zc = z0 + 0.5
        sv = 18 * 2 + 20 * (zc - 2)
        sve = sv - 9.81 * (zc - 2)
        rd = 1 - 0.00765 * zc if zc <= 9.15 else 1.174 - 0.0267 * zc
        fs = crr * msf / (0.65 * 0.3 * sv / sve * rd)
        fs_min = min(fs_min, fs)
        lpi += (1 - fs) * (10 * 1 - 0.25 * ((z0 + 1) ** 2 - z0 ** 2)) if fs < 1 else 0.0
    r = _v([_e(0, 10, n=15.0)], nf=2.0)
    assert r["lpi"] == pytest.approx(lpi, rel=1e-9) and r["fs_minimo"] == pytest.approx(fs_min, rel=1e-9)
    assert len(r["estratos"][0]["subcapas"]) == 8


def test_lpi_monotono_decreciente_al_profundizar_el_nivel_freatico():
    lpis = [_v([_e(0, 20, n=14.0)], nf=nf)["lpi"] for nf in (0.0, 2.0, 5.0, 10.0, 15.0)]
    assert all(b <= a for a, b in zip(lpis, lpis[1:])) and lpis[0] > lpis[-1] >= 0.0


def test_lpi_monotono_en_finos_para_n_fijo():
    # más finos (5–35 %) elevan (N1)60cs → menos licuación
    lpis = [_v([_e(0, 15, n=10.0, finos_pct=fc)])["lpi"] for fc in (0.0, 10.0, 20.0, 30.0)]
    assert all(b <= a for a, b in zip(lpis, lpis[1:]))


# ── Hallazgo 2: nada se «inventa» fuera del dominio de 30 m ────────────────────────────────────────────────────────────
def test_subcapa_bajo_30_m_queda_fuera_de_dominio_sin_cifras_inventadas():
    r = licuacion_spt_contrato(_s([_e(0, 35, n=40.0), _e(35, 40, n=8.0)]))
    e = r.valor["estratos"][1]
    assert e["categoria"] == "fuera_de_dominio" and e["fs"] is None and r.en_borde_dominio is True


def test_estrato_que_cruza_30_m_evalua_solo_la_parte_dentro_del_dominio():
    v = _v([_e(0, 40, n=12.0)])
    z_eval = [s["z_evaluacion_m"] for s in v["estratos"][0]["subcapas"] if s["categoria"] == "evaluado"]
    assert max(z_eval) < 30.0
    assert any(s["categoria"] == "fuera_de_dominio" for s in v["estratos"][0]["subcapas"])


# ── Hallazgo 3: Kσ omitido → borde cuando σ'v > 100 kPa ─────────────────────────────────────────────────────────────────
def test_borde_cuando_el_esfuerzo_efectivo_supera_100_kpa_aunque_z_sea_menor_a_15():
    r = licuacion_spt_contrato(_s([_e(0, 24, n=20.0)], nf=2.0))
    assert r.en_borde_dominio is True


def test_perfil_somero_con_fs_lejos_de_uno_no_marca_borde():
    assert licuacion_spt_contrato(_s([_e(0, 6, n=15.0)], nf=2.0)).en_borde_dominio is False


# ── Hallazgo 4/5/9/10: honestidad del contrato ──────────────────────────────────────────────────────────────────────────
def test_los_supuestos_declaran_las_omisiones_y_no_prometen_lo_que_no_hacen():
    s = " ".join(licuacion_spt_contrato(_s([_e(0, 10)])).supuestos).lower()
    for palabra in ("capilaridad", "constante", "cota inferior", "no conservador", "sin cota"):
        assert palabra in s
    assert "grava" not in s.lower()


def test_cada_fila_trae_categoria_enumerada():
    cats = {e["categoria"] for e in _v([_e(0, 2), _e(2, 4, n=40.0), _e(4, 6, no_plastico=False, finos_pct=60.0)], nf=1.0)["estratos"]}
    assert cats <= {"evaluado", "no_licuable", "sobre_nivel_freatico", "sin_nivel_freatico", "fino_plastico", "fuera_de_dominio"}
    assert {"no_licuable", "fino_plastico"} <= cats


def test_lpi_de_ruido_numerico_se_clasifica_como_ninguno():
    assert _clasificar_lpi(1e-12) == "ninguno" and _clasificar_lpi(0.5) == "bajo" and _clasificar_lpi(5.0) == "bajo"
    assert _clasificar_lpi(5.1) == "alto" and _clasificar_lpi(15.0) == "alto" and _clasificar_lpi(15.1) == "muy alto"


# ── Hallazgos 6/7/8: entradas estrictas ─────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("nf", [float("inf"), 1e308, 500.0])
def test_nivel_freatico_no_finito_o_absurdo_se_rechaza(nf):
    with pytest.raises(ValidationError):
        _s([_e(0, 10)], nf=nf)


def test_tipos_laxos_se_rechazan():
    with pytest.raises(ValidationError):
        _e(0, 10, n=True)
    with pytest.raises(ValidationError):
        _s([_e(0, 10)], mw="7.5")


@pytest.mark.parametrize("campo", ["gamma_kn_m3", "gamma_sat_kn_m3"])
def test_peso_unitario_absurdo_se_rechaza(campo):
    with pytest.raises(ValidationError):
        _e(0, 10, **{campo: 1e308})


# ── Propiedades faltantes ───────────────────────────────────────────────────────────────────────────────────────────────
def test_csr_es_homogeneo_de_grado_cero_en_los_esfuerzos():
    a = csr_seed_idriss(amax_g=0.3, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0, z_m=5.0)
    b = csr_seed_idriss(amax_g=0.3, sigma_v_kpa=900.0, sigma_v_efectivo_kpa=600.0, z_m=5.0)
    assert a == pytest.approx(b, rel=1e-12)


@pytest.mark.parametrize("n,publicado", [(10.0, 0.11), (20.0, 0.21)])
def test_crr_cerca_de_la_curva_publicada_de_youd_2001(n, publicado):
    assert crr_spt(n) == pytest.approx(publicado, abs=0.01)
