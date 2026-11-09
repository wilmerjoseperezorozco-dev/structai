"""Solver discretizado de Euler-Bernoulli por elementos finitos (Hermite cúbico).

Resuelve, adimensionalizando x -> xi = x/L en [0, 1]:

    flexión : (EI(xi) w'')'' + k(xi) w = q(xi)            ->  K u = F
    pandeo  : (EI(xi) w'')'' + P w'' + k(xi) w = 0         ->  K phi = lambda Kg phi

Escalas: w = (q0 L^4 / EI0) w_hat  y  lambda = P L^2 / EI0, con EI0 = EI de referencia.
Con EI constante y sin fundación, la solución nodal es exacta en los nodos para cargas
distribuidas polinómicas hasta grado 0 (propiedad del elemento cúbico), así que la
validación contra las fórmulas cerradas de `beam_theory.py` y `column_theory.py` es estricta.

Convención: unidades SI; x hacia la derecha, w positivo hacia arriba (cargas q positivas hacia
arriba), M positivo con fibra inferior en tracción (sagging). Apoyos: "fijo", "articulado",
"libre", "deslizante" (giro impedido, w libre).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy.linalg import eigh

APOYOS = ("fijo", "articulado", "libre", "deslizante")
_GAUSS_X, _GAUSS_W = np.polynomial.legendre.leggauss(4)


@dataclass(frozen=True)
class ResultadoFEM:
    x: np.ndarray          # m
    w: np.ndarray          # m
    theta: np.ndarray      # rad
    M: np.ndarray          # N·m (sagging +), valor a la izquierda del nodo (último nodo: derecha)
    V: np.ndarray          # N, ídem
    reacciones: dict       # {"x": [...], "Fy": [...]} en apoyos restringidos
    n_elem: int


@dataclass(frozen=True)
class ResultadoPandeoFEM:
    lambda_cr: float       # P L² / EI0
    P_cr: float            # N
    K_efectivo: float      # π / sqrt(lambda)
    modo_x: np.ndarray
    modo_w: np.ndarray     # normalizado a máx |w| = 1
    lambdas: np.ndarray    # primeros modos


def _malla(L: float, n: int, extra: Sequence[float]) -> np.ndarray:
    base = np.linspace(0.0, L, n + 1)
    pts = np.unique(np.round(np.concatenate([base, np.asarray(extra, float)]), 12))
    if pts[0] < 0 or pts[-1] > L + 1e-12:
        raise ValueError("posición fuera de la viga")
    return pts


def _hermite(xi: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """N, N', N'' (dimensionales en x local) para xi en [0,1], elemento de longitud h. Forma (len, 4)."""
    N = np.stack([1 - 3 * xi**2 + 2 * xi**3, h * (xi - 2 * xi**2 + xi**3), 3 * xi**2 - 2 * xi**3, h * (-xi**2 + xi**3)], axis=-1)
    d1 = np.stack([(-6 * xi + 6 * xi**2) / h, 1 - 4 * xi + 3 * xi**2, (6 * xi - 6 * xi**2) / h, -2 * xi + 3 * xi**2], axis=-1)
    d2 = np.stack([(-6 + 12 * xi) / h**2, (-4 + 6 * xi) / h, (6 - 12 * xi) / h**2, (-2 + 6 * xi) / h], axis=-1)
    return N, d1, d2


def _valor(f: float | Callable, x: np.ndarray) -> np.ndarray:
    return np.asarray(f(x), float) * np.ones_like(x) if callable(f) else np.full_like(x, float(f))


def _ensamblar(xs, EI, k, q, con_geom=False):
    nn = len(xs)
    K = np.zeros((2 * nn, 2 * nn))
    Kg = np.zeros_like(K)
    F = np.zeros(2 * nn)
    elems = []
    for e in range(nn - 1):
        h = xs[e + 1] - xs[e]
        xg = xs[e] + h * (_GAUSS_X + 1) / 2
        wg = _GAUSS_W * h / 2
        N, d1, d2 = _hermite((_GAUSS_X + 1) / 2, h)
        ei, kk, qq = _valor(EI, xg), _valor(k, xg), _valor(q, xg)
        Ke = (d2.T * (ei * wg)) @ d2 + (N.T * (kk * wg)) @ N
        fe = N.T @ (qq * wg)
        idx = slice(2 * e, 2 * e + 4)
        K[idx, idx] += Ke
        F[idx] += fe
        if con_geom:
            Kg[idx, idx] += (d1.T * wg) @ d1
        elems.append((Ke, fe))
    return K, Kg, F, elems


def _restricciones(izq: str, der: str, apoyos: Sequence[float], xs: np.ndarray) -> np.ndarray:
    for a in (izq, der):
        if a not in APOYOS:
            raise ValueError(f"apoyo '{a}' no soportado; use {APOYOS}")
    fijos: list[int] = []
    n = len(xs) - 1
    for nodo, tipo in ((0, izq), (n, der)):
        if tipo == "fijo":
            fijos += [2 * nodo, 2 * nodo + 1]
        elif tipo == "articulado":
            fijos += [2 * nodo]
        elif tipo == "deslizante":
            fijos += [2 * nodo + 1]
    for xa in apoyos:
        fijos.append(2 * int(np.argmin(np.abs(xs - xa))))
    return np.unique(fijos)


def flexion(L: float, EI: float | Callable, *, q: float | Callable = 0.0, cargas_puntuales: Sequence[tuple[float, float]] = (),
            izquierdo: str = "articulado", derecho: str = "articulado", apoyos_intermedios: Sequence[float] = (),
            k_fundacion: float | Callable = 0.0, n_elem: int = 40) -> ResultadoFEM:
    """Viga de longitud L. EI y q pueden ser constantes o funciones de x (m). cargas_puntuales: [(x, P)], P>0 hacia arriba."""
    if L <= 0 or n_elem < 2:
        raise ValueError("L>0 y n_elem>=2")
    extra = [x for x, _ in cargas_puntuales] + list(apoyos_intermedios)
    xs = _malla(L, n_elem, extra)
    EI_ref = float(_valor(EI, np.array([L / 2]))[0])
    if EI_ref <= 0:
        raise ValueError("EI debe ser > 0")
    K, _, F, elems = _ensamblar(xs, EI, k_fundacion, q)
    for xp, P in cargas_puntuales:
        F[2 * int(np.argmin(np.abs(xs - xp)))] += P
    fijos = _restricciones(izquierdo, derecho, apoyos_intermedios, xs)
    libres = np.setdiff1d(np.arange(len(F)), fijos)
    if len(libres) == len(F) and not np.any(_valor(k_fundacion, xs) > 0):
        raise ValueError("viga sin apoyos: mecanismo")
    u = np.zeros(len(F))
    try:
        u[libres] = np.linalg.solve(K[np.ix_(libres, libres)], F[libres])
    except np.linalg.LinAlgError as exc:  # mecanismo
        raise ValueError("sistema singular: apoyos insuficientes") from exc
    R = K @ u - F
    nn = len(xs)
    M = np.zeros(nn)
    V = np.zeros(nn)
    for e, (Ke, fe) in enumerate(elems):
        fint = Ke @ u[2 * e:2 * e + 4] - fe
        if e == 0 or True:
            M[e], V[e] = -fint[1], fint[0]
        if e == nn - 2:
            M[e + 1], V[e + 1] = fint[3], -fint[2]
    rx = [xs[i // 2] for i in fijos if i % 2 == 0]
    ry = [float(R[i]) for i in fijos if i % 2 == 0]
    return ResultadoFEM(xs, u[0::2], u[1::2], M, V, {"x": rx, "Fy": ry}, len(xs) - 1)


def pandeo(L: float, EI: float | Callable, *, izquierdo: str = "articulado", derecho: str = "articulado",
           apoyos_intermedios: Sequence[float] = (), k_fundacion: float | Callable = 0.0, n_elem: int = 40, n_modos: int = 3) -> ResultadoPandeoFEM:
    """Carga crítica de Euler por el problema de autovalores K phi = lambda Kg phi (P constante a lo largo de L)."""
    xs = _malla(L, n_elem, apoyos_intermedios)
    EI_ref = float(_valor(EI, np.array([L / 2]))[0])
    K, Kg, _, _ = _ensamblar(xs, EI, k_fundacion, 0.0, con_geom=True)
    fijos = _restricciones(izquierdo, derecho, apoyos_intermedios, xs)
    libres = np.setdiff1d(np.arange(K.shape[0]), fijos)
    vals, vecs = eigh(K[np.ix_(libres, libres)], Kg[np.ix_(libres, libres)])
    pos = [i for i, v in enumerate(vals) if v > 1e-9]
    if not pos:
        raise ValueError("sin modo de pandeo positivo (apoyos insuficientes)")
    lam_p = vals[pos]                       # P (N) para cada modo
    i0 = pos[0]
    phi = np.zeros(K.shape[0])
    phi[libres] = vecs[:, i0]
    w = phi[0::2]
    w = w / np.max(np.abs(w))
    P_cr = float(vals[i0])
    return ResultadoPandeoFEM(P_cr * L**2 / EI_ref, P_cr, float(np.pi / np.sqrt(P_cr * L**2 / EI_ref)) if P_cr > 0 else float("inf"),
                              xs, w, lam_p[:n_modos] * L**2 / EI_ref)
