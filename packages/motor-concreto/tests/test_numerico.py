"""La API en producción fija NumPy 1.26 (sin np.trapezoid): la integración debe funcionar con cualquiera de los dos nombres."""
import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from src import numerico


def test_trapezoid_integra_una_recta_exactamente():
    x = np.linspace(0.0, 4.0, 9)
    assert numerico.trapezoid(2.0 * x, x) == 16.0  # ∫0..4 2x dx


def test_usa_trapz_cuando_numpy_no_tiene_trapezoid(monkeypatch):
    original = np.trapezoid
    monkeypatch.setattr(np, "trapz", original, raising=False)
    monkeypatch.delattr(np, "trapezoid")
    try:
        recargado = importlib.reload(numerico)
        assert recargado.trapezoid is np.trapz
    finally:
        monkeypatch.undo()
        importlib.reload(numerico)
