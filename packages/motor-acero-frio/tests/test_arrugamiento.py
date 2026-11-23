"""Pruebas de arrugamiento del alma (#81). FICTICIOS son coeficientes para evaluar a mano (no son de la norma); la
Tabla F.4.3.3-2 se prueba contra valores leídos de la NSR-10 impresa, pág. F-344."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest

from src.arrugamiento import (
    TABLA_F_4_3_3_2,
    CoeficientesArrugamiento,
    coeficientes_tabla,
    alfa_voladizo,
    arrugamiento_alma,
    interaccion_flexion_arrugamiento,
)
from src.contrato_api import PerfilC, arrugamiento_perfil_c

FICTICIOS = dict(C=4.0, CR=0.1, CN=0.3, Ch=0.02, phi_w=0.85, R_t_max=9.0, fila="ficticia para prueba")


def test_pn_a_mano():
    c = CoeficientesArrugamiento(**FICTICIOS)
    h, t, Fy, N, R = 200.0, 2.0, 340.0, 100.0, 4.0
    esperado = 4.0 * 4.0 * 340.0 * (1 - 0.1 * math.sqrt(2)) * (1 + 0.3 * math.sqrt(50)) * (1 - 0.02 * 10)
    assert arrugamiento_alma(h, t, Fy, N, R, c).Pn == pytest.approx(esperado, rel=1e-12)


def test_pn_monotono():
    c = CoeficientesArrugamiento(**FICTICIOS)
    base = arrugamiento_alma(200, 2, 340, 100, 4, c).Pn
    assert arrugamiento_alma(200, 2, 340, 150, 4, c).Pn > base       # más apoyo, más resistencia
    assert arrugamiento_alma(200, 2, 340, 100, 8, c).Pn < base       # más radio, menos resistencia
    assert arrugamiento_alma(200, 2.5, 340, 100, 4, c).Pn > base     # más espesor, más resistencia


def test_limites_de_la_tabla():
    c = CoeficientesArrugamiento(**FICTICIOS)
    with pytest.raises(ValueError, match="mínima"):
        arrugamiento_alma(200, 2, 340, 15, 4, c)
    with pytest.raises(ValueError, match="R/t"):
        arrugamiento_alma(200, 2, 340, 100, 20, c)
    with pytest.raises(ValueError, match="N/h"):
        arrugamiento_alma(100, 2, 340, 210, 4, c)
    with pytest.raises(ValueError, match="θ = 90"):
        arrugamiento_alma(200, 2, 340, 100, 4, c, theta_grados=60.0)


def test_alfa_voladizo():
    assert alfa_voladizo(Lo=50, h=200, t=2) == 1.0                      # Lo/h = 0,25 fuera de rango
    a = alfa_voladizo(Lo=200, h=200, t=2)                                # Lo/h = 1, h/t = 100
    assert a == pytest.approx(max(1.0, 1.34 / (0.9 + 0.3)), rel=1e-12)
    assert alfa_voladizo(Lo=320, h=320, t=2) == 1.0                     # h/t = 160 > 154


def test_interaccion_a_mano():
    assert interaccion_flexion_arrugamiento(10.0, 50.0, 20.0, 100.0) == pytest.approx((0.455 + 0.5) / 1.197)


def test_coeficientes_exigen_fila_citada():
    with pytest.raises(ValueError, match="fila"):
        CoeficientesArrugamiento(**{**FICTICIOS, "fila": " "})
    with pytest.raises(ValueError, match="φw"):
        CoeficientesArrugamiento(**{**FICTICIOS, "phi_w": 1.2})


def test_tabla_f_4_3_3_2_transcrita():
    """12 filas: sujeta+rigidizada (4), no sujeta+rigidizada (4), no sujeta+no rigidizada (4). Puntos de control
    leídos de la pág. F-344 de la NSR-10 impresa."""
    assert len(TABLA_F_4_3_3_2) == 12
    assert TABLA_F_4_3_3_2[("sujeta", "rigidizada", "una_aleta", "extremo")] == (4.0, 0.14, 0.35, 0.02, 0.85, 9.0)
    assert TABLA_F_4_3_3_2[("sujeta", "rigidizada", "dos_aletas", "extremo")] == (7.5, 0.08, 0.12, 0.048, 0.85, 12.0)
    assert TABLA_F_4_3_3_2[("no_sujeta", "rigidizada", "dos_aletas", "interior")] == (24.0, 0.52, 0.15, 0.001, 0.80, 3.0)
    assert TABLA_F_4_3_3_2[("no_sujeta", "no_rigidizada", "dos_aletas", "extremo")] == (2.0, 0.11, 0.37, 0.01, 0.75, 1.0)
    for C, CR, CN, Ch, phi, rt in TABLA_F_4_3_3_2.values():
        assert C > 0 and 0 < phi <= 0.90 and rt >= 1 and 0 <= Ch < 0.06


def test_tabla_sin_fila_para_no_rigidizada_sujeta():
    with pytest.raises(ValueError, match="no hay fila"):
        coeficientes_tabla("sujeta", "no_rigidizada", "una_aleta", "extremo")
    assert "Tabla F.4.3.3-2" in coeficientes_tabla("sujeta", "rigidizada", "una_aleta", "interior").fila


def test_contrato_arrugamiento():
    pf = PerfilC(H_mm=229.0, B_mm=63.5, D_mm=19.0, t_mm=1.5, Fy_MPa=345.0, Fu_MPa=450.0)
    r = arrugamiento_perfil_c(pf, 5.0, 75.0, 3.0, apoyo="sujeta", carga="una_aleta", posicion="extremo", Mu_kNm=4.0)
    assert set(r.valor["razones"]) == {"arrugamiento", "flexion_seccion", "interaccion_F.4.3.3-61"}
    assert r.valor["cumple"] is all(v <= 1 for v in r.valor["razones"].values())
    # Valor a mano con la fila (sujeta, rigidizada, una aleta, extremo): h = 229 − 3 = 226, t = 1,5.
    h, t = 226.0, 1.5
    pn = 4 * t * t * 345 * (1 - 0.14 * (3 / t) ** 0.5) * (1 + 0.35 * (75 / t) ** 0.5) * (1 - 0.02 * (h / t) ** 0.5)
    assert r.valor["Pn_kN"] == pytest.approx(pn / 1e3, rel=1e-12) and r.valor["phi_w"] == 0.85
    # C sin pestaña sujeta al apoyo: la tabla no tiene fila → falla explícito.
    sin = PerfilC(H_mm=150.0, B_mm=50.0, D_mm=0.0, t_mm=1.5, Fy_MPa=345.0, Fu_MPa=450.0)
    with pytest.raises(ValueError, match="no hay fila"):
        arrugamiento_perfil_c(sin, 5.0, 75.0, 1.0, apoyo="sujeta", carga="una_aleta", posicion="extremo")
    with pytest.raises(ValueError, match="voladizo"):
        arrugamiento_perfil_c(pf, 5.0, 75.0, 3.0, apoyo="sujeta", carga="dos_aletas", posicion="extremo", Lo_mm=150.0)
