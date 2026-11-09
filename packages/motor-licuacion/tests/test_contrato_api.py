"""Contrato ResultadoMotor de motor-licuacion (SPT). Perfil de referencia calculado a mano:
0–10 m, γ=18 sobre el nivel freático (2 m), γsat=20, (N1)60=15, FC=3 %, amax=0,3 g, Mw=7,5.
Punto de evaluación = centro de la parte saturada (z=6 m): σv=116, σ'v=76,76, rd=0,9541, CSR=0,2811587, CRR=0,1600576, FS=0,5690730."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import math

import pytest
from pydantic import ValidationError

from src.contrato_api import EstratoSPT, SolicitudLicuacionSPT, licuacion_spt_contrato


def _estrato(**kw):
    base = dict(z_top_m=0.0, z_base_m=10.0, gamma_kn_m3=18.0, gamma_sat_kn_m3=20.0, n1_60=15.0, finos_pct=3.0, no_plastico=True)
    base.update(kw)
    return EstratoSPT(**base)


def _sol(**kw):
    base = dict(amax_g=0.3, mw=7.5, nivel_freatico_m=2.0, estratos=[_estrato()])
    base.update(kw)
    return SolicitudLicuacionSPT(**base)


def test_primera_subcapa_coincide_con_el_calculo_a_mano():
    # subcapa 2–3 m (centro 2,5 m): σv = 18·2 + 20·0,5 = 46 · σ'v = 46 − 9,81·0,5 · rd = 1 − 0,00765·2,5
    r = licuacion_spt_contrato(_sol())
    e = r.valor["estratos"][0]
    c = e["subcapas"][0]
    sv, sve, rd = 46.0, 46.0 - 9.81 * 0.5, 1.0 - 0.00765 * 2.5
    csr = 0.65 * 0.3 * sv / sve * rd
    crr = 1 / 19 + 15 / 135 + 50 / 195 ** 2 - 1 / 200
    assert c["z_evaluacion_m"] == pytest.approx(2.5) and c["sigma_v_kpa"] == pytest.approx(sv)
    assert c["sigma_v_efectivo_kpa"] == pytest.approx(sve) and c["csr"] == pytest.approx(csr, rel=1e-12)
    assert c["crr"] == pytest.approx(crr, rel=1e-12) and c["fs"] == pytest.approx(crr * (10 ** 2.24 / 7.5 ** 2.56) / csr, rel=1e-12)
    assert r.valor["fs_minimo"] == pytest.approx(min(s["fs"] for s in e["subcapas"])) and r.valor["clasificacion_lpi"] == "muy alto"


def test_contrato_completo():
    r = licuacion_spt_contrato(_sol())
    assert r.unidad_si and r.ecuacion and "Youd" in r.referencia_normativa and "NSR-10" in r.referencia_normativa
    assert r.aviso_responsabilidad_profesional and r.supuestos and isinstance(r.en_borde_dominio, bool)
    assert any("SPT" in s for s in r.supuestos) and any("Kσ" in s or "Ksigma" in s for s in r.supuestos)


def test_sin_nivel_freatico_no_hay_licuacion_y_se_declara():
    r = licuacion_spt_contrato(_sol(nivel_freatico_m=None))
    assert r.valor["lpi"] == 0.0 and r.valor["estratos"][0]["estado"] == "sin nivel freático: no saturado"
    assert r.valor["fs_minimo"] is None and r.valor["clasificacion_lpi"] == "ninguno"


def test_estrato_sobre_el_nivel_freatico_no_se_evalua():
    r = licuacion_spt_contrato(_sol(nivel_freatico_m=12.0))
    assert r.valor["estratos"][0]["estado"] == "sobre el nivel freático" and r.valor["lpi"] == 0.0


def test_finos_plasticos_no_se_evaluan_con_este_metodo():
    r = licuacion_spt_contrato(_sol(estratos=[_estrato(no_plastico=False, finos_pct=60.0)]))
    e = r.valor["estratos"][0]
    assert e["estado"].startswith("fino plástico") and e["fs"] is None and r.valor["lpi"] == 0.0
    assert r.en_borde_dominio is True


def test_n_alto_es_no_licuable_con_fs_infinito_representado_como_none():
    r = licuacion_spt_contrato(_sol(estratos=[_estrato(n1_60=40.0)]))
    e = r.valor["estratos"][0]
    assert e["estado"] == "no licuable ((N1)60cs ≥ 30)" and e["fs"] is None and r.valor["lpi"] == 0.0


def test_dos_estratos_el_lpi_suma_y_el_minimo_es_el_menor_fs():
    r = licuacion_spt_contrato(_sol(estratos=[_estrato(z_base_m=5.0, n1_60=8.0), _estrato(z_top_m=5.0, z_base_m=10.0, n1_60=22.0)]))
    f0, f1 = (e["fs"] for e in r.valor["estratos"])
    assert f0 < f1 and r.valor["fs_minimo"] == pytest.approx(f0)
    assert r.valor["lpi"] > 0


def test_fs_monotono_en_amax_y_en_n():
    f = lambda **k: licuacion_spt_contrato(_sol(**k)).valor["fs_minimo"]
    assert f(amax_g=0.4) < f(amax_g=0.3) < f(amax_g=0.2)
    g = lambda n: licuacion_spt_contrato(_sol(estratos=[_estrato(n1_60=n)])).valor["fs_minimo"]
    assert g(8.0) < g(15.0) < g(22.0)


def test_borde_cuando_el_fs_minimo_esta_cerca_de_uno_o_hay_finos_altos_o_prof_grande():
    base = licuacion_spt_contrato(_sol(estratos=[_estrato(z_base_m=6.0)]))
    assert base.en_borde_dominio is False
    assert licuacion_spt_contrato(_sol(estratos=[_estrato(finos_pct=50.0)])).en_borde_dominio is True
    assert licuacion_spt_contrato(_sol(estratos=[_estrato(z_base_m=40.0)])).en_borde_dominio is True


def test_estratos_deben_ser_contiguos_desde_cero():
    with pytest.raises(ValueError, match="contigu"):
        licuacion_spt_contrato(_sol(estratos=[_estrato(z_top_m=1.0)]))
    with pytest.raises(ValueError, match="contigu"):
        licuacion_spt_contrato(_sol(estratos=[_estrato(z_base_m=4.0), _estrato(z_top_m=5.0, z_base_m=9.0)]))


def test_gamma_sat_debe_superar_al_agua_y_a_gamma():
    with pytest.raises(ValueError, match="saturado"):
        licuacion_spt_contrato(_sol(estratos=[_estrato(gamma_sat_kn_m3=9.0)]))
    with pytest.raises(ValueError, match="saturado"):
        licuacion_spt_contrato(_sol(estratos=[_estrato(gamma_kn_m3=21.0, gamma_sat_kn_m3=20.0)]))


def test_entradas_obligatorias_y_rangos():
    with pytest.raises(ValidationError):
        SolicitudLicuacionSPT(amax_g=0.3, mw=7.5, estratos=[_estrato()])      # nivel freático obligatorio (puede ser null)
    for kw in (dict(amax_g=0.0), dict(amax_g=float("nan")), dict(mw=float("inf"))):
        with pytest.raises(ValidationError):
            _sol(**kw)
    with pytest.raises(ValueError, match="magnitud"):
        licuacion_spt_contrato(_sol(mw=4.0))
