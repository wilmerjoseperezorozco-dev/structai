"""Pruebas de la membrana QM6 (F3, #274) con soluciones cerradas: movimientos de cuerpo rígido, parche de esfuerzo
constante, flexión pura exacta, voladizo de Timoshenko y convergencia al diafragma rígido."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from src.portico3d import Caso3D, Diafragma, Elemento3D, Membrana, Nodo3D, Portico3D, k_membrana

E, NU, T = 2.0e7, 0.2, 0.1


def _malla(L, h, nx, ny):
    xs = np.linspace(0, L, nx + 1)
    ys = np.linspace(0, h, ny + 1)
    nodo = {(i, j): i * (ny + 1) + j for i in range(nx + 1) for j in range(ny + 1)}
    xy = np.array([[xs[i], ys[j]] for i in range(nx + 1) for j in range(ny + 1)])
    els = [(nodo[i, j], nodo[i + 1, j], nodo[i + 1, j + 1], nodo[i, j + 1]) for i in range(nx) for j in range(ny)]
    return xy, els, nodo


def _ensamblar(xy, els, E=E, nu=NU, t=T):
    K = np.zeros((2 * len(xy),) * 2)
    for el in els:
        g = [2 * k + c for k in el for c in (0, 1)]
        K[np.ix_(g, g)] += k_membrana(xy[list(el)], E, nu, t)
    return K


def test_cuerpo_rigido_sin_energia_en_cuadrilatero_distorsionado():
    xy = np.array([[0.0, 0.0], [2.0, 0.3], [2.4, 1.9], [-0.2, 1.4]])
    k = k_membrana(xy, E, NU, T)
    for u in (np.tile([1.0, 0.0], 4), np.tile([0.0, 1.0], 4), np.column_stack([-xy[:, 1], xy[:, 0]]).ravel()):
        assert np.abs(k @ u).max() < 1e-6 * np.abs(k).max()
    assert np.allclose(k, k.T)
    assert np.linalg.matrix_rank(k, tol=1e-8 * np.abs(k).max()) == 5


def test_parche_esfuerzo_constante():
    xy, els, nodo = _malla(3.0, 1.0, 3, 2)
    K = _ensamblar(xy, els)
    eps = 1e-4
    u = np.column_stack([eps * xy[:, 0], -NU * eps * xy[:, 1]]).ravel()   # σx uniforme, σy = 0
    F = K @ u
    sigma = E * eps
    derecha = [nodo[3, j] for j in range(3)]
    assert sum(F[2 * k] for k in derecha) == pytest.approx(sigma * T * 1.0, rel=1e-9)
    interiores = [nodo[i, j] for i in (1, 2) for j in range(3)]
    assert np.abs(F[[2 * k for k in interiores]]).max() < 1e-6 * sigma * T


def _resolver(K, fijos, F):
    libres = np.setdiff1d(np.arange(len(F)), fijos)
    u = np.zeros(len(F))
    u[libres] = np.linalg.solve(K[np.ix_(libres, libres)], F[libres])
    return u


def test_flexion_pura_exacta_con_un_elemento_en_el_canto():
    L, h, M = 4.0, 0.5, 10.0
    xy, els, nodo = _malla(L, h, 4, 1)
    K = _ensamblar(xy, els, nu=0.0)
    F = np.zeros(2 * len(xy))
    F[2 * nodo[4, 1]], F[2 * nodo[4, 0]] = -M / h, M / h       # par en el extremo
    fijos = [2 * nodo[0, 0], 2 * nodo[0, 0] + 1, 2 * nodo[0, 1], 2 * nodo[0, 1] + 1]
    u = _resolver(K, fijos, F)
    I = T * h**3 / 12
    assert u[2 * nodo[4, 0] + 1] == pytest.approx(M * L**2 / (2 * E * I), rel=1e-9)


def test_voladizo_con_cortante_cerca_de_timoshenko():
    L, h, P, nu = 8.0, 1.0, 5.0, 0.25
    xy, els, nodo = _malla(L, h, 16, 4)
    K = _ensamblar(xy, els, nu=nu)
    F = np.zeros(2 * len(xy))
    for j in range(5):
        F[2 * nodo[16, j] + 1] = -P / 4 * (0.5 if j in (0, 4) else 1.0)
    fijos = [2 * nodo[0, j] + c for j in range(5) for c in (0, 1)]
    u = _resolver(K, fijos, F)
    I, A, G = T * h**3 / 12, T * h, E / (2 * (1 + nu))
    timo = P * L**3 / (3 * E * I) + P * L / (5 / 6 * G * A)
    assert -u[2 * nodo[16, 2] + 1] == pytest.approx(timo, rel=0.03)


# ── integración con el pórtico 3D ──────────────────────────────────────────────────────────────────────────────────

def _nave(nvanos=4, L=6.0, B=6.0, h=3.0, con_diafragma=False, E_losa=2.0e7, t=0.1):
    """Un piso, una fila de vanos en X (nvanos+1 pórticos transversales); muros rígidos simulados con columnas
    rígidas en los pórticos de los extremos."""
    Ec, Gc = 2.5e7, 1.0e7
    nodos, els, apoyos = [], [], {}
    base, cab = {}, {}
    for i in range(nvanos + 1):
        for j, y in enumerate((0.0, B)):
            base[i, j] = len(nodos); nodos.append(Nodo3D(i * L, y, 0.0))
            cab[i, j] = len(nodos); nodos.append(Nodo3D(i * L, y, h))
            apoyos[base[i, j]] = (True,) * 6
            I = 0.5 if i in (0, nvanos) else 0.004          # extremos muy rígidos (como muros)
            els.append(Elemento3D(base[i, j], cab[i, j], Ec, Gc, 0.16, I, I, 0.003))
    for i in range(nvanos + 1):
        els.append(Elemento3D(cab[i, 0], cab[i, 1], Ec, Gc, 0.12, 0.0016, 0.0016, 0.001))
    for i in range(nvanos):
        for j in (0, 1):
            els.append(Elemento3D(cab[i, j], cab[i + 1, j], Ec, Gc, 0.12, 0.0016, 0.0016, 0.001))
    dia = [Diafragma("P1", tuple(cab.values()), nvanos * L / 2, B / 2)] if con_diafragma else []
    mem = [] if con_diafragma else [Membrana((cab[i, 0], cab[i + 1, 0], cab[i + 1, 1], cab[i, 1]), E_losa, 0.2, t)
                                     for i in range(nvanos)]
    return Portico3D(nodos, els, apoyos, dia, mem), cab


def _cortantes_y(m, cab, F_total, nvanos=4):
    """Fuerza en Y repartida por área tributaria (rígido: resultante en el centro de masa)."""
    if m.diafragmas:
        r = m.resolver(Caso3D("y", maestros={"P1": (0.0, F_total, 0.0)}))
    else:
        trib = {i: (0.5 if i in (0, nvanos) else 1.0) / nvanos for i in range(nvanos + 1)}
        r = m.resolver(Caso3D("y", nodales={cab[i, j]: (0, F_total * trib[i] / 2, 0, 0, 0, 0)
                                            for i in range(nvanos + 1) for j in (0, 1)}))
    return np.array([sum(r.reacciones[2 * (2 * i + j)][1] for j in (0, 1)) for i in range(nvanos + 1)])


def test_losa_muy_rigida_reproduce_el_diafragma_rigido():
    m_r, cab = _nave(con_diafragma=True)
    m_s, cab_s = _nave(E_losa=2.0e12)
    v_r = _cortantes_y(m_r, cab, 100.0)
    v_s = _cortantes_y(m_s, cab_s, 100.0)
    assert v_s == pytest.approx(v_r, rel=1e-3, abs=1e-3)
    assert v_r.sum() == pytest.approx(-100.0, rel=1e-9)


def test_losa_flexible_pasa_cortante_a_los_porticos_intermedios():
    m_r, cab = _nave(con_diafragma=True)
    m_s, cab_s = _nave(E_losa=2.0e5, t=0.05)
    v_r = _cortantes_y(m_r, cab, 100.0)
    v_s = _cortantes_y(m_s, cab_s, 100.0)
    assert abs(v_s[2]) > abs(v_r[2]) * 1.5                 # el pórtico del centro toma más con losa flexible
    assert v_s.sum() == pytest.approx(-100.0, rel=1e-9)


def test_membrana_invalida():
    with pytest.raises(ValueError):
        _nave(E_losa=-1.0)
    with pytest.raises(ValueError):
        k_membrana(np.array([[0, 0], [0, 1], [1, 1], [1, 0]], float), E, NU, T)   # horario
