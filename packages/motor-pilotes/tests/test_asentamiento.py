"""Asentamiento de grupos de pilotes (NSR-10 H.4.4.2, CCP-14 §10.7.2.3). Valores esperados calculados a mano:

Grupo 3×3, D = 0,40 m cuadrado, s = 1,20 m → B = L = 2·1,20 + 0,40 = 2,80 m; Q = 4000 kN → q = 510,204 kPa.
  Granular, Db = 15 m, N1_60 = 20: D' = 10 000 mm, I = 1 − 0,125·10 000/2 800 = 0,553571,
      ρ = 30·0,510204·0,553571·√2800 / 20 = 22,4175 mm.
  Acortamiento: (4000/9)·15 / (0,16·25 000 000) = 1,66667 mm.
  Cohesivo NC (z_tope = 0, H = 4 m, σ'0 = σ'p = 150, Cc = 0,30, e0 = 0,90): Δσ(2 m) = 510,204·2,8²/4,8² = 173,611 kPa,
      S = 4/1,9·0,30·log10(323,611/150) = 210,905 mm.
  Sobreconsolidado (σ'p = 200, Cr = 0,05): S = 4/1,9·[0,05·log10(200/150) + 0,30·log10(323,611/200)] = 145,147 mm.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest
from pydantic import ValidationError

from src.asentamiento import (acortamiento_elastico_m, asentamiento_granular_spt_mm, asentamiento_grupo,
                              planta_grupo, profundidad_zapata_equivalente)
from src.contrato_api import (LIMITES_ASENT_TOTAL_MM, SolicitudAsentamientoPilotes,
                              asentamiento_pilotes_contrato)

GRUPO = dict(filas=3, columnas=3, separacion_m=1.2, ancho_m=0.4, area_m2=0.16, longitud_m=15.0, ep_mpa=25000.0)
CAPA_NC = dict(z_tope_m=0.0, espesor_m=4.0, sigma0_kpa=150.0, sigma_p_kpa=150.0, cc=0.30, cr=0.05, e0=0.90)


def test_limites_transcritos_de_h492():
    assert LIMITES_ASENT_TOTAL_MM == {"aislada": 300.0, "medianera": 150.0}


def test_planta_y_profundidad_de_la_zapata_equivalente():
    assert planta_grupo(3, 3, 1.2, 0.4) == pytest.approx((2.8, 2.8))
    assert planta_grupo(2, 4, 1.0, 0.3) == pytest.approx((1.3, 3.3))
    assert planta_grupo(1, 1, 0.0, 0.5) == pytest.approx((0.5, 0.5))
    assert profundidad_zapata_equivalente(20.0, 6.0, "a_punta") == pytest.approx(20.0)
    assert profundidad_zapata_equivalente(20.0, 6.0, "b_friccion_arcilla") == pytest.approx(18.0)
    assert profundidad_zapata_equivalente(20.0, 6.0, "c_friccion_arena_sobre_arcilla") == pytest.approx(14.0 + 16.0 / 3.0)
    assert profundidad_zapata_equivalente(20.0, 6.0, "d_capas") == pytest.approx(18.0)


def test_acortamiento_a_mano():
    assert acortamiento_elastico_m(4000.0 / 9.0, 15.0, 0.16, 25000.0) * 1000 == pytest.approx(1.666667, rel=1e-6)


def test_granular_spt_a_mano():
    rho, i = asentamiento_granular_spt_mm(4000.0 / 2.8 ** 2 / 1000.0, 2.8, 15.0, 20.0)
    assert i == pytest.approx(0.553571, rel=1e-5)
    assert rho == pytest.approx(22.4175, rel=1e-5)


def test_granular_i_tiene_minimo_05():
    _, i = asentamiento_granular_spt_mm(0.3, 1.0, 30.0, 20.0)
    assert i == 0.5


def test_grupo_granular_suma_acortamiento_y_suelo():
    r = asentamiento_grupo(carga_permanente_kn=4000.0, db_m=15.0, caso="d_capas", suelo_bajo_zapata="granular_spt",
                           n1_60_bajo_zapata=20.0, **GRUPO)
    assert r["q_kpa"] == pytest.approx(510.204, rel=1e-5)
    assert r["asentamiento_suelo_m"] * 1000 == pytest.approx(22.4175, rel=1e-5)
    assert r["asentamiento_total_m"] * 1000 == pytest.approx(22.4175 + 1.666667, rel=1e-5)


def test_grupo_cohesivo_normalmente_consolidado_a_mano():
    r = asentamiento_grupo(carga_permanente_kn=4000.0, db_m=10.0, caso="b_friccion_arcilla",
                           suelo_bajo_zapata="cohesivo", estratos_cohesivos=[CAPA_NC], **GRUPO)
    capa = r["detalle"]["estratos"][0]
    assert capa["delta_sigma_kpa"] == pytest.approx(173.611, rel=1e-5)
    assert r["asentamiento_suelo_m"] * 1000 == pytest.approx(210.905, rel=1e-5)


def test_grupo_cohesivo_sobreconsolidado_a_mano():
    capa = dict(CAPA_NC, sigma_p_kpa=200.0)
    r = asentamiento_grupo(carga_permanente_kn=4000.0, db_m=10.0, caso="b_friccion_arcilla",
                           suelo_bajo_zapata="cohesivo", estratos_cohesivos=[capa], **GRUPO)
    assert r["asentamiento_suelo_m"] * 1000 == pytest.approx(145.147, rel=1e-5)


def test_mas_carga_mas_asentamiento():
    vals = [asentamiento_grupo(carga_permanente_kn=q, db_m=10.0, caso="b_friccion_arcilla",
                               suelo_bajo_zapata="cohesivo", estratos_cohesivos=[CAPA_NC], **GRUPO)
            ["asentamiento_total_m"] for q in (1000.0, 2000.0, 4000.0, 8000.0)]
    assert vals == sorted(vals) and len(set(vals)) == 4


def test_capa_mas_profunda_asienta_menos():
    s = [asentamiento_grupo(carga_permanente_kn=4000.0, db_m=10.0, caso="b_friccion_arcilla",
                            suelo_bajo_zapata="cohesivo", estratos_cohesivos=[dict(CAPA_NC, z_tope_m=z)], **GRUPO)
         ["asentamiento_suelo_m"] for z in (0.0, 2.0, 6.0)]
    assert s[0] > s[1] > s[2]


def test_rechazos_de_dominio():
    with pytest.raises(ValueError):
        profundidad_zapata_equivalente(10.0, 12.0, "a_punta")
    with pytest.raises(ValueError):
        asentamiento_grupo(carga_permanente_kn=4000.0, db_m=10.0, caso="b_friccion_arcilla",
                           suelo_bajo_zapata="granular_spt", **GRUPO)
    with pytest.raises(ValueError):
        acortamiento_elastico_m(100.0, 10.0, 0.1, 0.0)


SOL = dict(carga_permanente_kn=4000.0, seccion="cuadrada", ancho_m=0.4, longitud_m=15.0, ep_mpa=25000.0, filas=3,
           columnas=3, separacion_m=1.2, db_m=10.0, caso_zapata_equivalente="b_friccion_arcilla",
           suelo_bajo_zapata="cohesivo", estratos_compresibles=[CAPA_NC], tipo_cimentacion="aislada")


def test_contrato_cohesivo_contra_limite():
    r = asentamiento_pilotes_contrato(SolicitudAsentamientoPilotes(**SOL))
    total = 210.905 + 1.666667
    assert r.valor["asentamiento_total_mm"] == pytest.approx(total, rel=1e-5)
    assert r.valor["limite_total_mm"] == 300.0 and r.valor["cumple"] is True
    r2 = asentamiento_pilotes_contrato(SolicitudAsentamientoPilotes(**dict(SOL, tipo_cimentacion="medianera")))
    assert r2.valor["cumple"] is False and r2.en_borde_dominio is True
    assert "H.4.4.2" in r.referencia_normativa and r.supuestos


def test_contrato_granular_advierte_sobreprediccion():
    r = asentamiento_pilotes_contrato(SolicitudAsentamientoPilotes(**dict(
        SOL, suelo_bajo_zapata="granular_spt", estratos_compresibles=None, n1_60_bajo_zapata=20.0, db_m=15.0)))
    assert r.valor["asentamiento_suelo_mm"] == pytest.approx(22.4175, rel=1e-5)
    assert any("sobrepredecir" in a for a in r.advertencias)


@pytest.mark.parametrize("cambio", [
    dict(estratos_compresibles=None),
    dict(suelo_bajo_zapata="granular_spt", estratos_compresibles=None),
    dict(db_m=20.0),
    dict(separacion_m=None),
    dict(ep_mpa=0.0),
])
def test_contrato_rechaza_datos_faltantes(cambio):
    with pytest.raises(ValidationError):
        SolicitudAsentamientoPilotes(**dict(SOL, **cambio))
