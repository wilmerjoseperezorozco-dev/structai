"""Verificación (no validación) del motor de viento B.6 v1: valores de tabla, cálculos a mano y propiedades."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src import b6


def test_kz_formula_y_minimos():
    # Exposición C a 10,06 m (33 ft): 2,01·(10,06/274,3)^(2/9,5) ≈ 1,00
    assert b6.kz(10.06, "C") == pytest.approx(1.002, abs=2e-3)
    # Debajo de 4,0 m se toma 4,0 m
    assert b6.kz(2.0, "C") == pytest.approx(b6.kz(4.0, "C"))
    # Caso 1, exposición B: Z ≥ 9,0 m → ≈ 0,70 (el 0,70 de ASCE 7-05 Tabla 6-3 bajo 30 ft)
    assert b6.kz(3.0, "B", caso=1) == pytest.approx(0.70, abs=5e-3)
    assert b6.kz(3.0, "B", caso=2) < b6.kz(3.0, "B", caso=1)
    assert b6.kz(10.0, "B") < b6.kz(10.0, "C") < b6.kz(10.0, "D")
    assert b6.kz(1e4, "C") == pytest.approx(2.01)
    with pytest.raises(ValueError):
        b6.kz(10.0, "A")


def test_qz_a_mano():
    # 0,613·1·1·0,85·28²·1,0
    assert b6.qz(28.0, 1.0) == pytest.approx(0.613 * 0.85 * 784.0)
    assert b6.qz(28.0, 1.0, importancia=1.15) == pytest.approx(1.15 * b6.qz(28.0, 1.0))
    with pytest.raises(ValueError):
        b6.qz(0.0, 1.0)


def test_gcpf_tabla_e_interpolacion():
    assert b6.gcpf("2E", 3.0) == -1.07
    assert b6.gcpf("1", 20.0) == 0.53
    assert b6.gcpf("3", 12.5) == pytest.approx((-0.37 + -0.48) / 2)
    assert b6.gcpf("2", 25.0) == pytest.approx((-0.69 + 0.21) / 2)
    assert b6.gcpf("1E", 40.0) == 0.69
    with pytest.raises(ValueError):
        b6.gcpf("7", 10.0)


def test_gcp_cubierta_mesetas_y_log():
    assert b6.gcp_cubierta("3", 0.5, 20.0) == -2.6
    assert b6.gcp_cubierta("3", 50.0, 20.0) == -2.0
    # a mitad en log (A = √10): promedio de los extremos
    assert b6.gcp_cubierta("2", 10 ** 0.5, 20.0) == pytest.approx((-1.7 - 1.2) / 2)
    assert b6.gcp_cubierta("1", 0.5, 5.0, "+") == 0.3
    assert b6.gcp_cubierta("3", 0.5, 35.0) == -1.2
    # alero θ ≤ 7°: zona 2 tiene dos tramos
    assert b6.gcp_cubierta("2", 10.0, 5.0, alero=True) == pytest.approx(-1.6)
    assert b6.gcp_cubierta("2", 100.0, 5.0, alero=True) == pytest.approx(-1.1)
    assert b6.gcp_cubierta("3", 0.5, 20.0, alero=True) == -3.7
    assert b6.figura_cubierta(7.0) == "8B" and b6.figura_cubierta(27.0) == "8C" and b6.figura_cubierta(27.1) == "8D"


def test_gcp_muro_y_reduccion():
    assert b6.gcp_muro("5", 0.5) == -1.4
    assert b6.gcp_muro("5", 60.0) == -0.8
    assert b6.gcp_muro("5", 0.5, theta_deg=5.0) == pytest.approx(-1.26)
    assert b6.gcp_muro("4", 0.5, "+") == 1.0


def test_presiones_netas():
    pmax, pmin = b6.presiones_netas(1000.0, -2.6, 0.18)
    assert pmin == pytest.approx(-2780.0) and pmax == pytest.approx(-2420.0)


def test_levantamiento_a_mano_sin_aleros():
    # θ = 20°, borde: 2E = −1,07, 3E = −0,69, GCpi = +0,18. Sin aleros y con carga simétrica por mitades:
    # R_barlovento = q·L·(3/8·(1,07+0,18) + 1/8·(0,69+0,18)) por regla de palanca.
    q, L = 1000.0, 8.0
    r = b6.levantamiento_cubierta(q, 20.0, L, 0.0, 0.0, factor_w=1.0, factor_d=0.0)
    esperado = q * L * (3 / 8 * 1.25 + 1 / 8 * 0.87)
    assert r.viento_barlovento_n_m == pytest.approx(esperado)
    assert r.reaccion_barlovento_n_m + r.reaccion_sotavento_n_m == pytest.approx(q * L / 2 * (1.25 + 0.87))


def test_levantamiento_alero_y_muerta():
    q, L, a, D = 1000.0, 8.0, 0.6, 500.0
    sin = b6.levantamiento_cubierta(q, 20.0, L, 0.0, D, factor_w=1.0, factor_d=1.0)
    con = b6.levantamiento_cubierta(q, 20.0, L, a, D, factor_w=1.0, factor_d=1.0)
    assert con.viento_barlovento_n_m > sin.viento_barlovento_n_m        # el alero a barlovento levanta más
    assert con.muerta_barlovento_n_m == pytest.approx(D * (L + 2 * a) / 2)
    # 0,9D + 1,6W por defecto
    r = b6.levantamiento_cubierta(q, 20.0, L, a, D)
    assert r.reaccion_barlovento_n_m == pytest.approx(1.6 * con.viento_barlovento_n_m - 0.9 * con.muerta_barlovento_n_m)
    # la cara inferior a sotavento con succión del muro reduce el levantamiento total
    inf = b6.levantamiento_cubierta(q, 20.0, L, a, D, alero_sotavento_inferior=True)
    assert inf.reaccion_barlovento_n_m + inf.reaccion_sotavento_n_m < r.reaccion_barlovento_n_m + r.reaccion_sotavento_n_m


def test_interior_levanta_menos_que_borde():
    b = b6.levantamiento_cubierta(1000.0, 20.0, 8.0, 0.6, 400.0)
    i = b6.levantamiento_cubierta(1000.0, 20.0, 8.0, 0.6, 400.0, borde=False)
    assert i.reaccion_barlovento_n_m < b.reaccion_barlovento_n_m
