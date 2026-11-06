"""Tests de eval-stats/src/estadistica.py (issue #95, A0).

Los valores esperados se calcularon aparte, a mano o con fórmulas cerradas,
no llamando al código bajo prueba."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pytest
from scipy import stats

import estadistica as e

NAN = float("nan")


def test_resumen_cuenta_faltantes_en_vez_de_esconderlos() -> None:
    r = e.resumen([1.0, 2.0, 3.0, NAN])
    assert (r["n_total"], r["n_validos"], r["n_faltantes"]) == (4, 3, 1)
    assert r["pct_faltante"] == pytest.approx(25.0)
    assert r["media"] == pytest.approx(2.0)
    assert r["de"] == pytest.approx(1.0)       # DE muestral de [1,2,3]
    assert r["mediana"] == pytest.approx(2.0)


def test_resumen_es_reproducible_y_el_ic_contiene_la_media() -> None:
    datos = [0.2, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.0, 0.4, 0.3]
    r1, r2 = e.resumen(datos), e.resumen(datos)
    assert (r1["ic_inf"], r1["ic_sup"]) == (r2["ic_inf"], r2["ic_sup"])
    assert r1["ic_inf"] < r1["media"] < r1["ic_sup"]


def test_ic_de_datos_constantes_es_degenerado_no_nan() -> None:
    assert e.ic_bootstrap_media([0.7, 0.7, 0.7]) == (pytest.approx(0.7), pytest.approx(0.7))


def test_banda_de_sensibilidad_acota_la_media_con_faltantes() -> None:
    b = e.banda_sensibilidad_faltantes([1.0, NAN])
    assert b["media_observada"] == pytest.approx(1.0)
    assert b["media_peor_caso"] == pytest.approx(0.5)
    assert b["media_mejor_caso"] == pytest.approx(1.0)


def test_wilson_0_de_10_cota_superior_conocida() -> None:
    """Cota superior de Wilson para 0/10 = z^2/(n+z^2) = 3.8416/13.8416 = 0.2775."""
    lo, hi = e.ic_wilson(0, 10)
    assert lo == pytest.approx(0.0, abs=1e-9)
    assert hi == pytest.approx(0.2775, abs=1e-3)


def test_holm_valores_calculados_a_mano() -> None:
    # ordenados: 0.01*3=0.03, 0.03*2=0.06, 0.04*1=0.04 -> monótono: 0.03, 0.06, 0.06
    assert e.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert e.holm([0.01, None, 0.04]) == [pytest.approx(0.02), None, pytest.approx(0.04)]
    assert e.holm([0.6, 0.9]) == pytest.approx([1.0, 1.0])  # tope en 1


def test_mcnemar_exacto_p_calculado_a_mano() -> None:
    """n10=1, n01=5: p = 2*P(X<=1 | n=6, 0.5) = 2*7/64 = 0.21875; RM = 5."""
    a = [1] * 1 + [0] * 5 + [1] * 4 + [0] * 3     # solo-a: 1 ; solo-b: 5 ; ambos: 4 ; ninguno: 3
    b = [0] * 1 + [1] * 5 + [1] * 4 + [0] * 3
    r = e.mcnemar_exacto(a, b)
    assert (r["n10_solo_a"], r["n01_solo_b"], r["n11"], r["n00"]) == (1, 5, 4, 3)
    assert r["p"] == pytest.approx(0.21875)
    assert r["razon_momios"] == pytest.approx(5.0)
    assert r["diff_prop"] == pytest.approx((9 - 5) / 13)


def test_mcnemar_sin_discordantes_no_inventa_diferencia() -> None:
    r = e.mcnemar_exacto([1, 0, 1], [1, 0, 1])
    assert r["p"] == 1.0 and r["n01_solo_b"] == 0 and r["n10_solo_a"] == 0


def test_pareado_normal_elige_t_y_coincide_con_scipy() -> None:
    a = np.arange(1, 11, dtype=float)
    d = np.arange(1, 11) * 0.01                    # diferencias distintas, sin ceros
    b = a + d
    r = e.comparar_pareado(a, b)
    assert r["n_pares"] == 10 and r["n_descartados"] == 0
    assert r["prueba"] == "t_pareada"
    assert r["p"] == pytest.approx(stats.ttest_rel(b, a).pvalue)
    assert r["dz"] == pytest.approx(d.mean() / d.std(ddof=1))
    assert r["p_wilcoxon"] == pytest.approx(2 / 1024)   # todas positivas: p exacto = 2/2^10
    assert r["r_biserial"] == pytest.approx(1.0)
    assert (r["n_mejoran"], r["n_empeoran"], r["n_iguales"]) == (10, 0, 0)


def test_pareado_descarta_pares_con_faltantes_y_lo_informa() -> None:
    a = [0.1, 0.2, NAN, 0.4, 0.5]
    b = [0.2, 0.3, 0.9, 0.5, 0.7]
    r = e.comparar_pareado(a, b)
    assert r["n_pares"] == 4 and r["n_descartados"] == 1


def test_pareado_no_normal_elige_wilcoxon() -> None:
    a = np.zeros(10)
    b = np.array([0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 5.0, 9.0])
    r = e.comparar_pareado(a, b)
    assert r["shapiro_p"] < 0.05
    assert r["prueba"] == "wilcoxon" and r["efecto_nombre"] == "r_biserial"


def test_pareado_muestra_insuficiente() -> None:
    assert e.comparar_pareado([1.0, 2.0], [2.0, 3.0])["prueba"] == "insuficiente"


def test_pareado_sin_cambios_no_da_efecto_ni_significancia() -> None:
    x = [0.3, 0.6, 0.9, 1.0]
    r = e.comparar_pareado(x, x)
    assert r["p_wilcoxon"] == 1.0 and r["r_biserial"] == 0.0 and r["n_iguales"] == 4


def test_pareado_longitudes_distintas_es_error() -> None:
    with pytest.raises(ValueError):
        e.comparar_pareado([1.0, 2.0, 3.0], [1.0, 2.0])


def test_bootstrap_por_cluster_reproducible_y_mas_ancho_que_por_pregunta() -> None:
    valores = [1.0] * 5 + [0.0] * 5 + [0.5] * 5       # tres clústeres muy distintos entre sí
    clusters = ["A"] * 5 + ["B"] * 5 + ["C"] * 5
    r1 = e.bootstrap_por_cluster(valores, clusters)
    r2 = e.bootstrap_por_cluster(valores, clusters)
    assert r1 == r2 and r1["n_clusters"] == 3 and r1["media"] == pytest.approx(0.5)
    ic_plano = e.ic_bootstrap_media(valores)
    assert (r1["ic_sup"] - r1["ic_inf"]) > (ic_plano[1] - ic_plano[0])
