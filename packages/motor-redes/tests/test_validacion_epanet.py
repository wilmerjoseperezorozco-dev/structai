"""Validación contra salidas publicadas de EPANET (software de referencia de la EPA; OWA, licencia MIT del código).

Fuentes de las redes: EPANET «Net1» (example-networks de OpenWaterAnalytics/EPANET, MIT) y «todinitest» (OpenWaterAnalytics/
epanet-example-networks). Los resultados esperados son las SALIDAS DE REGRESIÓN de EPANET 2.2.0-dev (release v1.0.2-dev.10 de
epanet-example-networks, archivo benchmark-linux-220dev1, .out decodificado), en un único periodo t = 0, y se citan aquí como
datos numéricos. Atención al alcance: es una verificación contra OTRO SOLVER, no contra la literatura; Net1 se resuelve con el
tanque a carga fija (duración 0), no la corrida de 24 h del manual.

Diferencia conocida y aceptada: este motor usa la constante SI de Hazen-Williams 10,67; EPANET usa 4,727 en unidades inglesas, que
equivale a 10,6669 en SI (0,03 % menos). Las tolerancias de abajo la absorben y se verifican explícitamente.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.gradiente import resolver_red

FT, IN, GPM, LPS = 0.3048, 0.0254, 6.30901964e-5, 1e-3

# ── todinitest (SI: LPS, m, mm) ────────────────────────────────────────────────────────────────────────────────────────
TODINI_EPANET_LPS = {"1": 50.2716, "2": 49.7284}


def _todini():
    z = {"2": 99, "3": 98, "4": 97, "5": 96}
    dem = {"2": 10, "3": 20, "4": 30, "5": 40}
    nodos = [dict(id="1", cota_m=0.0, demanda_m3s=0.0, carga_fija_m=100.0)] + [
        dict(id=k, cota_m=float(z[k]), demanda_m3s=dem[k] * LPS, carga_fija_m=None) for k in z]
    pares = {"1": ("1", "2"), "2": ("1", "3"), "3": ("2", "3"), "4": ("2", "5"), "5": ("2", "4"), "6": ("3", "5"), "7": ("4", "5")}
    tramos = [dict(id=i, desde=a, hasta=b, longitud_m=1000.0, diametro_m=0.5, c_hw=100.0) for i, (a, b) in pares.items()]
    return nodos, tramos


def test_todinitest_reproduce_los_caudales_de_epanet():
    nodos, tramos = _todini()
    red = resolver_red(nodos, tramos)
    for tid, esperado in TODINI_EPANET_LPS.items():
        assert red["tramos"][tid]["caudal_m3s"] / LPS == pytest.approx(esperado, abs=2e-3)    # EPANET publica 4 decimales (float32)
    assert sum(red["tramos"][t]["caudal_m3s"] for t in TODINI_EPANET_LPS) / LPS == pytest.approx(100.0, abs=1e-9)


# ── Net1 en t = 0 (unidades inglesas de origen → SI) ────────────────────────────────────────────────────────────────────
NET1_NODOS = {"10": (710, 0), "11": (710, 150), "12": (700, 150), "13": (695, 100), "21": (700, 150), "22": (695, 200),
              "23": (690, 0), "31": (700, 100), "32": (710, 100)}                                 # cota ft, demanda gpm
NET1_TUBOS = {"10p": ("10", "11", 10530, 18), "11p": ("11", "12", 5280, 14), "12p": ("12", "13", 5280, 10),
              "21p": ("21", "22", 5280, 10), "22p": ("22", "23", 5280, 12), "31p": ("31", "32", 5280, 6),
              "110p": ("2", "12", 200, 18), "111p": ("11", "21", 5280, 10), "112p": ("12", "22", 5280, 12),
              "113p": ("13", "23", 5280, 8), "121p": ("21", "31", 5280, 8), "122p": ("22", "32", 5280, 6)}   # L ft, D in; C = 100
NET1_EPANET_CARGA_FT = {"10": 1004.4989, "11": 985.4027, "12": 970.0970, "13": 969.6373, "21": 972.1088,
                        "22": 969.8004, "23": 969.7805, "31": 967.9904, "32": 966.3397}
NET1_EPANET_Q_GPM = {"pump": 1865.0793, "110p": -915.0793, "10p": 1865.0793, "11p": 1240.5732, "12p": 77.1438,
                     "21p": 184.3680, "22p": 22.8562, "31p": 40.1380}
# Curva de bomba de UN punto (1500 gpm, 250 ft): EPANET la completa con h0 = 4/3·H y Qmax = 2·Q → H = h0 − a·Q²
_H0_FT = 250.0 * 4.0 / 3.0
_A_FT_POR_GPM2 = (_H0_FT - 250.0) / 1500.0 ** 2


def _net1():
    nodos = [dict(id="9", cota_m=800 * FT, demanda_m3s=0.0, carga_fija_m=800 * FT),
             dict(id="2", cota_m=850 * FT, demanda_m3s=0.0, carga_fija_m=970 * FT)]       # tanque a nivel 120 ft, fijo en t = 0
    nodos += [dict(id=k, cota_m=z * FT, demanda_m3s=d * GPM, carga_fija_m=None) for k, (z, d) in NET1_NODOS.items()]
    tramos = [dict(id=i, desde=a, hasta=b, longitud_m=L * FT, diametro_m=D * IN, c_hw=100.0) for i, (a, b, L, D) in NET1_TUBOS.items()]
    bombas = [dict(id="pump", desde="9", hasta="10", h0_m=_H0_FT * FT, a_s2m5=_A_FT_POR_GPM2 * FT / GPM ** 2)]
    return nodos, tramos, bombas


def test_net1_t0_reproduce_cargas_de_epanet():
    nodos, tramos, bombas = _net1()
    red = resolver_red(nodos, tramos, bombas=bombas)
    for nid, esperado in NET1_EPANET_CARGA_FT.items():
        assert red["nodos"][nid]["carga_m"] / FT == pytest.approx(esperado, abs=0.012), nid      # medido: 0,0082 ft (0,03 % de la constante HW); EPANET publica float32


def test_net1_t0_reproduce_caudales_de_epanet_incluida_la_bomba():
    nodos, tramos, bombas = _net1()
    red = resolver_red(nodos, tramos, bombas=bombas)
    assert red["bombas"]["pump"]["caudal_m3s"] / GPM == pytest.approx(NET1_EPANET_Q_GPM["pump"], abs=0.1)
    for tid in ("110p", "10p", "11p", "12p", "21p", "22p", "31p"):
        assert red["tramos"][tid]["caudal_m3s"] / GPM == pytest.approx(NET1_EPANET_Q_GPM[tid], abs=0.1), tid


def test_net1_t0_balance_de_masa_y_curva_de_bomba_de_epanet():
    nodos, tramos, bombas = _net1()
    red = resolver_red(nodos, tramos, bombas=bombas)
    demanda = sum(d for _, d in NET1_NODOS.values())
    assert demanda == 950
    q_bomba = red["bombas"]["pump"]["caudal_m3s"] / GPM
    q_tanque = red["tramos"]["110p"]["caudal_m3s"] / GPM
    assert q_bomba + q_tanque == pytest.approx(demanda, abs=1e-6)               # el tanque se llena: toma 915 gpm
    assert red["bombas"]["pump"]["carga_m"] / FT == pytest.approx(_H0_FT - 250.0 / 3.0 * (q_bomba / 1500.0) ** 2, rel=1e-9)


def test_la_diferencia_de_constante_hazen_williams_con_epanet_es_de_0_03_por_ciento():
    constante_epanet_si = 4.727 * 0.0283168466 ** -1.852 * FT ** 4.871           # 4,727 (ft, cfs) llevado a SI
    assert constante_epanet_si == pytest.approx(10.667, abs=1e-3)
    assert abs(10.67 - constante_epanet_si) / constante_epanet_si < 4e-4
