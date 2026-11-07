"""Pruebas de las funciones puras de metricas_sin_llm.py y anotacion_experto.py (sin red, sin LLM)."""
import numpy as np
import pandas as pd

import anotacion_experto as ae
import metricas_sin_llm as m


def test_claves_extrae_numeros_codigos_y_palabras():
    k = m.claves("El recubrimiento minimo es 50 mm segun C.7.7.1 para elementos expuestos al suelo")
    assert "n:50" in k and "c:c.7.7.1" in k and "w:recubrimiento" in k
    assert "w:segun" not in k  # palabra vacía


def test_cobertura_completa_y_nula():
    k = m.claves("Valor 0.25 en la tabla A.2.3-1 para edificaciones")
    assert m.cobertura(k, "Valor 0.25 en la tabla A.2.3-1 para edificaciones") == 1.0
    assert m.cobertura(k, "texto sin relacion alguna") == 0.0


def test_numeros_ignora_digitos_sueltos():
    assert m.numeros("hay 3 vigas y 15 columnas de 0.5 m") == {"15", "0.5"}


def test_codigos_normaliza_espacios_y_mayusculas():
    assert "c.7.7.1" in m.codigos("ver C.7.7.1") and "tablaa.2.3-1" in m.codigos("Tabla A.2.3-1")


def test_wilson_cubre_proporcion_y_n_cero():
    lo, hi = m.wilson(10, 20)
    assert lo < 0.5 < hi and 0 <= lo and hi <= 1
    assert np.isnan(m.wilson(0, 0)[0])


def test_abstencion_ampliada_incluye_a_priori():
    assert set(m.ABSTENCION) <= set(m.ABSTENCION_AMPLIADA)


def test_kappa_cohen_acuerdo_perfecto_y_azar():
    a = pd.Series([0, 1, 2, 1, 0, 2])
    assert ae.kappa_cohen(a, a)[0] == 1.0
    b = pd.Series([1, 1, 1, 1, 1, 1])
    assert ae.kappa_cohen(a, b)[0] <= 0.0


def test_kappa_fleiss_acuerdo_perfecto():
    tabla = np.array([[3, 0], [0, 3], [3, 0], [0, 3]])
    assert ae.kappa_fleiss(tabla) == 1.0
