"""Licuación por SPT, procedimiento simplificado NCEER (Youd et al., 2001). Referencias calculadas a mano, con aritmética
independiente del módulo: rd, CSR, MSF (Idriss), (N1)60cs (Idriss y Boulanger), CRR (Rauch) y LPI (Iwasaki et al., 1978)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.spt import (corregir_finos, crr_spt, csr_seed_idriss, factor_seguridad_estrato, indice_potencial_licuacion,
                     msf_idriss, rd_nceer)


# ── rd ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("z,esperado", [(5.0, 0.96175), (9.15, 0.9300025), (12.0, 0.8536), (23.0, 0.5599), (25.0, 0.544),
                                        (30.0, 0.504)])
def test_rd_por_tramos(z, esperado):
    assert rd_nceer(z) == pytest.approx(esperado, rel=1e-9)


def test_rd_decrece_con_la_profundidad_y_es_continuo_en_los_cortes():
    zs = [0.0, 3.0, 9.15, 15.0, 23.0, 27.0, 30.0]
    vals = [rd_nceer(z) for z in zs]
    assert all(b < a for a, b in zip(vals, vals[1:]))
    for corte in (9.15, 23.0):
        assert rd_nceer(corte - 1e-9) == pytest.approx(rd_nceer(corte + 1e-9), abs=5e-4)  # la fórmula publicada salta ~3e-4 en 9,15 m


@pytest.mark.parametrize("z", [-1.0, float("nan"), float("inf"), 35.0])
def test_rd_rechaza_profundidad_invalida_o_fuera_del_metodo(z):
    with pytest.raises(ValueError):
        rd_nceer(z)


# ── CSR ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_csr_valor_a_mano():
    assert csr_seed_idriss(amax_g=0.3, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0, z_m=5.0) == pytest.approx(0.281311875, rel=1e-9)


def test_csr_lineal_en_amax_y_en_la_razon_de_esfuerzos():
    base = csr_seed_idriss(amax_g=0.2, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0, z_m=5.0)
    assert csr_seed_idriss(amax_g=0.4, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0, z_m=5.0) == pytest.approx(2 * base)
    assert csr_seed_idriss(amax_g=0.2, sigma_v_kpa=180.0, sigma_v_efectivo_kpa=60.0, z_m=5.0) == pytest.approx(2 * base)


@pytest.mark.parametrize("kw", [dict(amax_g=0.0), dict(amax_g=2.5), dict(sigma_v_efectivo_kpa=0.0), dict(sigma_v_kpa=40.0),
                                dict(amax_g=float("nan")), dict(z_m=-1.0)])
def test_csr_rechaza_entradas_invalidas(kw):
    base = dict(amax_g=0.3, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0, z_m=5.0)
    base.update(kw)
    with pytest.raises(ValueError):
        csr_seed_idriss(**base)


# ── MSF ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("mw,esperado", [(7.5, 0.9996389409), (6.0, 1.7698350800), (8.0, 0.8474022900)])
def test_msf_idriss(mw, esperado):
    assert msf_idriss(mw) == pytest.approx(esperado, rel=1e-8)


@pytest.mark.parametrize("mw", [4.0, 9.6, float("nan")])
def test_msf_rechaza_magnitud_fuera_de_rango(mw):
    with pytest.raises(ValueError, match="magnitud"):
        msf_idriss(mw)


# ── Corrección por finos ────────────────────────────────────────────────────────────────────────────────────────────
def test_finos_menores_a_5_no_corrigen():
    assert corregir_finos(n1_60=12.0, finos_pct=3.0) == (12.0, False)


def test_finos_intermedios_usan_alfa_beta():
    n, borde = corregir_finos(n1_60=12.0, finos_pct=15.0)
    assert n == pytest.approx(15.075299737, rel=1e-8) and borde is False


def test_finos_mayores_a_35_suman_5_y_escalan_1_2_y_marcan_borde():
    n, borde = corregir_finos(n1_60=10.0, finos_pct=50.0)
    assert n == pytest.approx(5.0 + 1.2 * 10.0) and borde is True


def test_correccion_por_finos_continua_en_los_cortes():
    for fc in (5.0, 35.0):
        a, _ = corregir_finos(n1_60=12.0, finos_pct=fc - 1e-6)
        b, _ = corregir_finos(n1_60=12.0, finos_pct=fc + 1e-6)
        assert a == pytest.approx(b, abs=0.1)  # las fórmulas publicadas de α y β tienen saltos de ~0,02–0,06 golpes en 5 % y 35 %


@pytest.mark.parametrize("kw", [dict(finos_pct=-1.0), dict(finos_pct=101.0), dict(n1_60=-1.0), dict(n1_60=float("nan"))])
def test_finos_rechaza_entradas_invalidas(kw):
    base = dict(n1_60=12.0, finos_pct=15.0)
    base.update(kw)
    with pytest.raises(ValueError):
        corregir_finos(**base)


# ── CRR ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_crr_valor_a_mano():
    assert crr_spt(15.0) == pytest.approx(0.16005761445, rel=1e-9)


def test_crr_crece_con_n():
    vals = [crr_spt(n) for n in (2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 29.0)]
    assert all(b > a for a, b in zip(vals, vals[1:]))


def test_crr_para_n_de_30_o_mas_no_es_licuable_y_se_rechaza_con_mensaje():
    with pytest.raises(ValueError, match="no licuable|30"):
        crr_spt(30.0)


@pytest.mark.parametrize("n", [-1.0, float("nan"), float("inf")])
def test_crr_rechaza_n_invalido(n):
    with pytest.raises(ValueError):
        crr_spt(n)


# ── Factor de seguridad ─────────────────────────────────────────────────────────────────────────────────────────────
def test_fs_valor_a_mano_con_n_corregido_15():
    fs = factor_seguridad_estrato(n1_60cs=15.0, amax_g=0.3, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0, z_m=5.0, mw=7.5)
    assert fs == pytest.approx(0.5687631359, rel=1e-8)


def test_fs_decrece_con_la_aceleracion_y_crece_con_n():
    f = lambda **k: factor_seguridad_estrato(**{**dict(n1_60cs=15.0, amax_g=0.3, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0,
                                                       z_m=5.0, mw=7.5), **k})
    assert f(amax_g=0.4) < f(amax_g=0.3) < f(amax_g=0.2)
    assert f(n1_60cs=10.0) < f(n1_60cs=15.0) < f(n1_60cs=20.0)


def test_fs_n_no_licuable_devuelve_infinito_en_vez_de_error():
    # (N1)60cs ≥ 30: el método de Youd et al. lo clasifica como no licuable (FS = ∞), no es un fallo de entrada
    assert factor_seguridad_estrato(n1_60cs=32.0, amax_g=0.3, sigma_v_kpa=90.0, sigma_v_efectivo_kpa=60.0, z_m=5.0, mw=7.5) == math.inf


# ── LPI ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_lpi_un_estrato_a_mano():
    # FS=0.5 entre 4 y 6 m: F=0.5, w(z)=10-0.5z; ∫ w dz de 4 a 6 = 10·2 − 0.25·(36−16) = 15  → LPI = 0.5·15 = 7.5
    assert indice_potencial_licuacion([(4.0, 6.0, 0.5)]) == pytest.approx(7.5, rel=1e-12)


def test_lpi_ignora_estratos_con_fs_mayor_o_igual_a_1_y_la_parte_bajo_20_m():
    assert indice_potencial_licuacion([(2.0, 4.0, 1.2), (6.0, 8.0, 1.0)]) == 0.0
    # estrato 18–24 m con FS=0: solo cuenta 18–20: ∫ (10−0.5z) dz = 10·2 − 0.25·(400−324) = 1.0
    assert indice_potencial_licuacion([(18.0, 24.0, 0.0)]) == pytest.approx(1.0, rel=1e-12)


def test_lpi_aditivo_y_monotono_en_fs():
    a = indice_potencial_licuacion([(1.0, 3.0, 0.4)])
    b = indice_potencial_licuacion([(5.0, 7.0, 0.7)])
    assert indice_potencial_licuacion([(1.0, 3.0, 0.4), (5.0, 7.0, 0.7)]) == pytest.approx(a + b)
    assert indice_potencial_licuacion([(1.0, 3.0, 0.2)]) > indice_potencial_licuacion([(1.0, 3.0, 0.8)])


@pytest.mark.parametrize("estratos", [[], [(3.0, 2.0, 0.5)], [(-1.0, 2.0, 0.5)], [(1.0, 2.0, -0.1)], [(1.0, float("nan"), 0.5)],
                                      [(1.0, 4.0, 0.5), (3.0, 6.0, 0.5)]])
def test_lpi_rechaza_estratos_invalidos_o_solapados(estratos):
    with pytest.raises(ValueError):
        indice_potencial_licuacion(estratos)
