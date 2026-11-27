"""Pruebas del régimen del acero, solo con datos sintéticos. Desde scripts/precios: python -m pytest test_regimen_acero.py -q"""
from __future__ import annotations

import math

import numpy as np
import pytest

import regimen_acero as ra


def _simular(n, A, mu, sd, semilla=1):
    rng = np.random.default_rng(semilla)
    s, x, est = 0, [], []
    for _ in range(n):
        s = rng.choice(2, p=A[s])
        est.append(s)
        x.append(rng.normal(mu[s], sd[s]))
    return np.array(x), np.array(est)


A_REAL = np.array([[0.95, 0.05], [0.10, 0.90]])
MU, SD = np.array([-0.01, 0.03]), np.array([0.01, 0.01])


def test_hmm_recupera_parametros_de_una_cadena_conocida():
    x, _ = _simular(600, A_REAL, MU, SD)
    m = ra.ajustar_hmm(x)
    assert m["mu"] == pytest.approx(MU, abs=0.004)
    assert np.diag(m["A"]) == pytest.approx(np.diag(A_REAL), abs=0.05)
    assert m["mu"][0] < m["mu"][1]                     # estados ordenados por media


def test_hmm_con_transicion_fija_no_la_cambia():
    x, _ = _simular(200, A_REAL, MU, SD)
    A = np.array([[0.8, 0.2], [0.3, 0.7]])
    assert ra.ajustar_hmm(x, A_fija=A)["A"] == pytest.approx(A)


def test_prob_evento_sube_cuando_el_ultimo_estado_es_de_alza():
    m = {"pi": np.array([0.5, 0.5]), "A": A_REAL, "mu": MU, "sd": SD}
    alza = np.array([0.03] * 6)
    baja = np.array([-0.01] * 6)
    assert ra.prob_evento_hmm(alza, m) > 0.8 > 0.2 > ra.prob_evento_hmm(baja, m)


def test_prob_evento_con_un_solo_estado_es_la_normal_exacta():
    m = {"pi": np.array([1.0, 0.0]), "A": np.array([[1.0, 0.0], [0.0, 1.0]]), "mu": np.array([0.01, 0.5]),
         "sd": np.array([0.01, 0.01])}
    p = ra.prob_evento_hmm(np.array([0.01, 0.0, 0.02]), m)
    z = (ra.UMBRAL - 0.03) / (0.01 * math.sqrt(3))       # tres meses en el estado 0: suma N(0,03; 0,01·√3)
    assert p == pytest.approx(1 - 0.5 * (1 + math.erf(z / math.sqrt(2))), abs=1e-6)


def test_eventos_y_estado_observado():
    logI = np.log(np.array([100, 101, 102, 103, 99, 98, 97]))
    e = ra.eventos(logI)                   # 100→103 (+3 %): 1 ; 101→99: 0 ; ...
    assert list(e) == [1, 0, 0, 0]
    assert ra.estado_observado(logI, 3) == 2 and ra.estado_observado(logI, 6) == 0


def test_referencias_solo_usan_eventos_ya_conocidos():
    logI = np.log(np.linspace(100, 130, 20))       # sube siempre > 2 % en 3 meses
    p0 = ra.climatologia(logI)
    assert p0 == pytest.approx((17 + 1) / (17 + 2))
    assert ra.markov_observada(logI) > 0.9


def test_dm_y_holm():
    rng = np.random.default_rng(3)
    d = rng.normal(-0.05, 0.02, 30)
    assert ra.dm_perdidas(d)[1] < 0.01
    assert ra.dm_perdidas(np.zeros(30)) == (0.0, 0.5)
    assert ra.holm({"a": 0.01, "b": 0.03}) == {"a": True, "b": True}     # umbrales 0,025 y 0,05
    assert ra.holm({"a": 0.03, "b": 0.04}) == {"a": False, "b": False}   # falla el primero: se detiene


def test_evaluar_de_punta_a_punta_no_mira_el_futuro():
    x, _ = _simular(50, A_REAL, MU, SD, semilla=5)
    obj = list(100 * np.exp(np.cumsum(x)))
    iccp = list(100 * np.exp(np.cumsum(_simular(150, A_REAL, MU / 3, SD / 3, semilla=6)[0])))
    res = ra.evaluar(obj, iccp)
    assert len(res["filas"]) == 50 - ra.H - (ra.ENTRENAMIENTO_INICIAL - 1)
    # cambiar el futuro no cambia ninguna probabilidad emitida en el primer origen
    obj2 = obj[: ra.ENTRENAMIENTO_INICIAL] + [v * 3 for v in obj[ra.ENTRENAMIENTO_INICIAL:]]
    f1, f2 = res["filas"][0], ra.evaluar(obj2, iccp)["filas"][0]
    assert all(f1[m] == pytest.approx(f2[m]) for m in ra.MODELOS)
    resumen, texto = ra.resumir(res)
    assert "Regla de integración" in texto
