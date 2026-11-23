"""Pruebas de la ecuación AASHTO-93 de pavimento rígido (#106).

Oráculo externo: ejemplo resuelto de Pavement Interactive («Rigid Pavement Empirical Design Example»). Datos:
k efectivo ≈ 250 pci, Ec = 4 500 000 psi, S'c = 750 psi, J = 3,2, p0 − pt = 4,5 − 3,0, So = 0,40, Cd = 1,0. Su tabla 3
da D leído de nomogramas en incrementos de 0,5 in; se acepta ±0,5 in.
"""
import math

import pytest

from src import rigido_aashto93 as rig

PSI = rig.PSI_POR_MPA
EJEMPLO = dict(k_MPa_m=250 * rig.MPA_M_POR_PCI, Sc_MPa=750 / PSI, Ec_MPa=4.5e6 / PSI, J=3.2, Cd=1.0, So=0.40,
               p0=4.5, pt=3.0)


@pytest.mark.parametrize("w18,R,D_publicado_pulg", [
    (22.0, 90, 11.0), (22.0, 95, 12.0), (22.0, 99, 13.0),
    (36.0, 90, 12.0), (36.0, 95, 12.5), (36.0, 99, 14.0),
    (54.0, 90, 13.0), (54.0, 95, 13.5), (54.0, 99, 15.0),
])
def test_reproduce_el_ejemplo_publicado(w18, R, D_publicado_pulg):
    r = rig.espesor_losa(w18, confiabilidad_pct=R, **EJEMPLO)
    assert abs(r.D_pulg - D_publicado_pulg) <= 0.5
    assert r.D_cm == pytest.approx(r.D_pulg * 2.54)


def test_la_solucion_satisface_la_ecuacion():
    r = rig.espesor_losa(22.0, confiabilidad_pct=90, **EJEMPLO)
    assert rig.log10_w18(r.D_pulg, **r.entradas_psi_pci) == pytest.approx(math.log10(22e6), abs=1e-9)
    assert rig.w18_admisible_millones(r.D_cm, confiabilidad_pct=90, **EJEMPLO) == pytest.approx(22.0, rel=1e-8)


def test_zr_y_conversiones():
    assert rig.z_r(90) == pytest.approx(-1.2816, abs=1e-4)
    assert rig.z_r(95) == pytest.approx(-1.6449, abs=1e-4)
    assert 1 / rig.MPA_M_POR_PCI == pytest.approx(3.684, abs=1e-3)       # 1 MPa/m ≈ 3,684 pci
    assert rig.EC_POR_DEFECTO_MPA == pytest.approx(27579, abs=1)
    with pytest.raises(ValueError, match="Confiabilidad"):
        rig.z_r(100)


BASE = dict(k_MPa_m=60.0, Sc_MPa=4.2, confiabilidad_pct=90.0)


def test_monotonicidad_fisica():
    d = lambda **kw: rig.espesor_losa(kw.pop("w", 10.0), **{**BASE, **kw}).D_cm
    assert d(w=1.0) < d(w=10.0) < d(w=50.0)                              # más tránsito, losa más gruesa
    assert d(confiabilidad_pct=80.0) < d() < d(confiabilidad_pct=99.0)
    assert d(Sc_MPa=4.8) < d() < d(Sc_MPa=3.8)                           # concreto más resistente, losa más delgada
    assert d(k_MPa_m=150.0) < d() < d(k_MPa_m=30.0)                      # soporte más rígido, losa algo más delgada
    assert d(J=2.7) < d() < d(J=3.8)                                     # sin dovelas, losa más gruesa
    assert d(pt=2.0) < d() < d(pt=3.0)


def test_k_influye_menos_que_el_modulo_de_rotura():
    """Rasgo conocido de AASHTO-93: duplicar k cambia D bastante menos que subir S'c en la misma proporción."""
    d0 = rig.espesor_losa(10.0, **BASE).D_cm
    dk = rig.espesor_losa(10.0, **{**BASE, "k_MPa_m": 120.0}).D_cm
    ds = rig.espesor_losa(10.0, **{**BASE, "Sc_MPa": 8.4}).D_cm
    assert 0 < d0 - dk < d0 - ds


@pytest.mark.parametrize("malo", [dict(k_MPa_m=0.0), dict(Sc_MPa=-1.0), dict(Sc_MPa=float("nan")),
                                  dict(J=float("inf")), dict(pt=4.6), dict(p0=5.5)])
def test_entradas_invalidas(malo):
    with pytest.raises(ValueError):
        rig.espesor_losa(10.0, **{**BASE, **malo})


def test_transito_imposible_falla_explicito():
    with pytest.raises(ValueError, match="Ninguna losa"):
        rig.espesor_losa(1e9, **{**BASE, "Sc_MPa": 1.0})


def test_sabotaje_constante_7_35_se_detecta():
    """Si alguien cambia una constante de la ecuación, el ejemplo publicado deja de reproducirse."""
    original = rig.log10_w18

    def saboteada(D, **e):
        return original(D, **e) - 7.35 * math.log10(D + 1) + 7.0 * math.log10(D + 1)

    rig.log10_w18 = saboteada
    try:
        r = rig.espesor_losa(22.0, confiabilidad_pct=90, **EJEMPLO)
        assert abs(r.D_pulg - 11.0) > 0.5
    finally:
        rig.log10_w18 = original


def test_la_rama_espuria_de_losas_delgadas_se_descarta():
    """Junto a la singularidad la ecuación da capacidades enormes a losas delgadas: no es física y no se usa."""
    r = rig.espesor_losa(0.001, **BASE)
    assert r.D_cm > 5.0
    with pytest.raises(ValueError):
        rig.w18_admisible_millones(r.D_cm * 0.5, **BASE)


def test_wrapper_de_la_api_pasa_k_y_modulo_de_rotura():
    from src import PavimentosRequest, disenar_pavimento
    base = dict(tipo_pavimento="concreto", tipo_via="primaria", tpd=8000, esals_millones=10.0, cbr_subrasante=8)
    sin = disenar_pavimento(PavimentosRequest(**base))
    assert sin["cumple"] is False and "modulo_reaccion_k" in sin["mensaje"]
    con = disenar_pavimento(PavimentosRequest(**base, modulo_reaccion_k=60.0, modulo_rotura_concreto=4.2))
    assert con["cumple"] is True and con["espesor_rodadura"] >= 15.0
    assert con["espesor_rodadura"] == math.ceil(rig.espesor_losa(10.0, **BASE, So=0.35).D_cm)
