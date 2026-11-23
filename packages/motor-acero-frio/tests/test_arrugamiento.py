"""Pruebas de arrugamiento del alma (#81). Los coeficientes de estas pruebas son ficticios, elegidos para evaluar a
mano: NO son valores de la Tabla F.4.3.3-2."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "contrato-motor"))

import pytest

from src.arrugamiento import (
    TABLA_F_4_3_3_2,
    CoeficientesArrugamiento,
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


def test_la_tabla_no_trae_valores_de_memoria():
    """Hasta transcribirla de la norma impresa, la tabla debe seguir vacía (no se aceptan coeficientes de memoria)."""
    assert TABLA_F_4_3_3_2 == {}


def test_contrato_arrugamiento():
    pf = PerfilC(H_mm=229.0, B_mm=63.5, D_mm=19.0, t_mm=1.5, Fy_MPa=345.0, Fu_MPa=450.0)
    r = arrugamiento_perfil_c(pf, 5.0, 75.0, 3.0, FICTICIOS, Mu_kNm=4.0)
    assert set(r.valor["razones"]) == {"arrugamiento", "flexion_seccion", "interaccion_F.4.3.3-61"}
    assert r.valor["cumple"] is all(v <= 1 for v in r.valor["razones"].values())
    assert any("ficticia" in s for s in r.supuestos)
    with pytest.raises(ValueError, match="incompletos"):
        arrugamiento_perfil_c(pf, 5.0, 75.0, 3.0, {"C": 4.0})
