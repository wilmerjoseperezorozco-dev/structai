"""Tests de teoría de pandeo de columnas (Euler / Johnson)."""
import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import column_theory as ct


def test_carga_critica_euler_formula():
    E, I, K, L = 200e9, 8.5e-6, 1.0, 3.0
    Pcr = ct.carga_critica_euler(E, I, K, L)
    esperado = math.pi ** 2 * E * I / (K * L) ** 2
    assert abs(Pcr - esperado) < 1e-6


def test_johnson_tangente_a_euler_en_esbeltez_transicion():
    """La parábola de Johnson debe ser tangente (mismo valor) a la hipérbola
    de Euler en λ=λc: σcr = fy/2 en ambas formulaciones."""
    E, fy = 200e9, 250e6
    lam_c = ct.esbeltez_transicion(E, fy)
    sigma_johnson = ct.esfuerzo_critico_johnson(E, fy, lam_c)
    sigma_euler = math.pi ** 2 * E / lam_c ** 2
    assert abs(sigma_johnson - sigma_euler) / sigma_euler < 1e-6
    assert abs(sigma_johnson - fy / 2) / (fy / 2) < 1e-6


def test_columna_corta_regimen_johnson():
    # Columna robusta (esbeltez baja) -> régimen inelástico
    r = ct.analizar_columna(P_aplicada=100e3, E=200e9, I=8.5e-6, A=6.4e-3, fy=250e6, K=1.0, L=1.0)
    assert r.regimen == "johnson"
    assert r.esbeltez < r.esbeltez_transicion


def test_columna_esbelta_regimen_euler():
    r = ct.analizar_columna(P_aplicada=5e3, E=200e9, I=8.5e-6, A=6.4e-3, fy=250e6, K=1.0, L=10.0)
    assert r.regimen == "euler"
    assert r.esbeltez > r.esbeltez_transicion


def test_factor_seguridad_columna():
    r = ct.analizar_columna(P_aplicada=100e3, E=200e9, I=8.5e-6, A=6.4e-3, fy=250e6, K=1.0, L=3.0)
    assert abs(r.factor_seguridad - r.carga_critica / 100e3) < 1e-6


def test_factor_amplificacion_p_delta():
    Pcr = 1_000_000.0
    P = 300_000.0
    factor = 1.0 / (1.0 - P / Pcr)
    sigma, factor_calc = ct.esfuerzo_combinado_viga_columna(P, 0.01, 5000, 0.001, Pcr)
    assert abs(factor_calc - factor) < 1e-9
    esperado_sigma = P / 0.01 + (5000 * factor) / 0.001
    assert abs(sigma - esperado_sigma) < 1e-3


def test_columna_inestable_p_mayor_que_pcr():
    sigma, factor = ct.esfuerzo_combinado_viga_columna(P=2_000_000, A=0.01, M0=1000, S=0.001, Pcr=1_000_000)
    assert sigma == float("inf")
    assert factor == float("inf")
