"""Tests de motor-acero-frio/src/ancho_efectivo.py -- issue #81.

Valores esperados calculados a mano con la MISMA formula pero como
aritmetica independiente (no llamando al codigo bajo prueba), mismo
patron ya usado en motor-estructural para eta/factor B (issue #75/#77):
w=100mm, t=1mm (w/t=100), E=200000 MPa, mu=0.3 (acero estructural
estandar)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from ancho_efectivo import (
    ancho_efectivo_no_rigidizado,
    ancho_efectivo_rigidizado,
    esfuerzo_pandeo_critico,
    factor_esbeltez,
    factor_reduccion,
)

E = 200000.0
MU = 0.3
W, T = 100.0, 1.0  # w/t = 100


def _fcr_manual(k: float) -> float:
    return k * math.pi**2 * E / (12 * (1 - MU**2) * (W / T) ** 2)


def test_esfuerzo_pandeo_critico_rigidizado() -> None:
    """Fcr = k*pi^2*E / [12*(1-mu^2)*(w/t)^2], k=4 -- ecuacion F.4.2.2-5."""
    esperado = _fcr_manual(4.0)
    assert esfuerzo_pandeo_critico(4.0, W, T, E, MU) == pytest.approx(esperado, rel=1e-9)
    assert esperado == pytest.approx(72.3048, abs=1e-3)


def test_esfuerzo_pandeo_critico_no_rigidizado() -> None:
    """Mismo Fcr, k=0.43 -- proporcional a k, Fcr(0.43) = Fcr(4)*0.43/4."""
    esperado = _fcr_manual(0.43)
    assert esfuerzo_pandeo_critico(0.43, W, T, E, MU) == pytest.approx(esperado, rel=1e-9)
    assert esperado == pytest.approx(7.7728, abs=1e-3)


def test_factor_esbeltez_y_reduccion_valores_hechos_a_mano() -> None:
    """lambda=sqrt(f/Fcr) (F.4.2.2-4), rho=(1-0.22/lambda)/lambda (F.4.2.2-3) --
    f=0.9*Fcr da lambda=sqrt(0.9)=0.94868..., verificado independientemente."""
    fcr = _fcr_manual(4.0)
    f = 0.9 * fcr
    lam = factor_esbeltez(f, fcr)
    assert lam == pytest.approx(math.sqrt(0.9), abs=1e-9)
    rho = factor_reduccion(lam)
    assert rho == pytest.approx(0.80965, abs=1e-4)


def test_ancho_efectivo_rigidizado_lambda_bajo_da_b_igual_w() -> None:
    """Caso trivial (F.4.2.2-1): con f=0.3*Fcr, lambda=sqrt(0.3)=0.5477 <= 0.673
    -- el elemento no sufre reduccion, b=w exactamente."""
    fcr = _fcr_manual(4.0)
    f = 0.3 * fcr
    assert factor_esbeltez(f, fcr) <= 0.673  # confirma que este caso SÍ ejercita la rama b=w
    b = ancho_efectivo_rigidizado(f, W, T, E, MU)
    assert b == pytest.approx(W, abs=1e-9)


def test_ancho_efectivo_rigidizado_lambda_alto_reduce_b() -> None:
    """Caso real de reducción (F.4.2.2-2): f=0.9*Fcr -> lambda=0.9487 > 0.673
    -- b = rho*w = 0.80965*100 = 80.965mm, calculado a mano arriba."""
    fcr = _fcr_manual(4.0)
    f = 0.9 * fcr
    b = ancho_efectivo_rigidizado(f, W, T, E, MU)
    assert b == pytest.approx(80.9648, abs=1e-3)
    assert b < W  # confirma que sí hubo reducción por pandeo local


def test_ancho_efectivo_no_rigidizado_mismo_rho_que_rigidizado() -> None:
    """Con k=0.43 (F.4.2.3.1) y f escalado proporcionalmente (0.9*Fcr_norig),
    lambda y rho dan EXACTAMENTE los mismos valores que el caso rigidizado
    -- confirma que k solo entra a través de Fcr, la fórmula de rho/lambda
    es idéntica una vez conocido f/Fcr."""
    fcr_norig = _fcr_manual(0.43)
    f = 0.9 * fcr_norig
    b = ancho_efectivo_no_rigidizado(f, W, T, E, MU)
    assert b == pytest.approx(80.9648, abs=1e-3)


def test_ancho_efectivo_nunca_supera_w() -> None:
    """Invariante físico real: el ancho efectivo nunca puede ser mayor que
    el ancho plano real del elemento, sin importar el esfuerzo."""
    fcr = _fcr_manual(4.0)
    for frac in (0.1, 0.5, 0.9, 0.99):
        b = ancho_efectivo_rigidizado(frac * fcr, W, T, E, MU)
        assert b <= W + 1e-9
