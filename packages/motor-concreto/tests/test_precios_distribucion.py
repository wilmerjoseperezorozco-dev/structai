"""Muestreo de escenarios de precio: mediana conservada, dispersión pedida, reproducibilidad y respaldo sin JSON."""
import math
from pathlib import Path

import numpy as np
import pytest

from src.economia_concreto import Economia
from src.precios_distribucion import SIGMAS_POR_DEFECTO, cargar_sigmas, muestrear

BASE = Economia()


def _muestras(n=20_000, sigmas=None):
    rng = np.random.default_rng(1)
    return [muestrear(BASE, rng, sigmas) for _ in range(n)]


def test_la_mediana_se_conserva_y_el_sigma_logaritmico_coincide():
    m = _muestras()
    for campo, fam in (("p_acero", "acero"), ("mult_concreto", "concreto"), ("p_perforacion_m", "perforacion_anclaje")):
        logs = np.log([getattr(e, campo) / getattr(BASE, campo) for e in m])
        assert abs(float(np.median(logs))) < 0.01
        assert float(np.std(logs)) == pytest.approx(SIGMAS_POR_DEFECTO[fam], rel=0.03)


def test_el_precio_del_cordon_sigue_al_del_acero_y_lo_demas_no_cambia():
    e = muestrear(BASE, np.random.default_rng(3))
    assert e.factor_precio_cordon == BASE.factor_precio_cordon and e.p_cabeza_anclaje == BASE.p_cabeza_anclaje and e.fe_cemento == BASE.fe_cemento


def test_misma_semilla_misma_muestra_y_la_base_no_se_muta():
    a = muestrear(BASE, np.random.default_rng(5))
    b = muestrear(BASE, np.random.default_rng(5))
    assert a == b and BASE == Economia()


def test_sigma_cero_devuelve_la_base():
    e = muestrear(BASE, np.random.default_rng(0), {"acero": 0.0, "concreto": 0.0, "perforacion_anclaje": 0.0})
    assert e == BASE


def test_sin_json_usa_la_copia_de_la_calibracion(tmp_path: Path):
    assert cargar_sigmas(tmp_path / "no_existe.json") == SIGMAS_POR_DEFECTO


def test_el_json_calibrado_es_coherente_con_la_copia():
    s = cargar_sigmas()
    for k, v in SIGMAS_POR_DEFECTO.items():
        assert math.isclose(s[k], v, rel_tol=0.05)
