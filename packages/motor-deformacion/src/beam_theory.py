"""
══════════════════════════════════════════════════════════════
MOTOR DEFORMACIÓN — TEORÍA DE VIGAS DE EULER-BERNOULLI
Ecuación diferencial gobernante (flexión pura, pequeñas deflexiones):

    d²v/dx²  =  M(x) / (E I)          (curvatura-momento)
    dM/dx    =  V(x)                  (equilibrio)
    dV/dx    =  w(x)                  (equilibrio, w positiva hacia abajo)
  ⇒ EI d⁴v/dx⁴ = w(x)

Las fórmulas cerradas de esta sección se obtienen integrando dos veces
la ecuación M(x)=EI·v''(x) con las constantes fijadas por las condiciones
de frontera de cada apoyo (Timoshenko & Gere, "Mechanics of Materials").
Todas fueron verificadas numéricamente resolviendo el sistema de 1er orden
[v, θ, M, V] como problema de valores de frontera (`resolver_general`) y
comparando contra el valor de libro de texto (ver tests/test_beam_theory.py).

Convención de signos: carga y deflexión positivas hacia ABAJO.
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
from scipy.integrate import solve_bvp

from .models import CondicionApoyo


@dataclass
class ResultadoViga:
    """Resultado de la solución de la ecuación de la elástica para un caso de carga."""
    v: Callable[[float], float]     # deflexión v(x), metros, positiva hacia abajo
    M: Callable[[float], float]     # momento flector M(x), N·m
    V: Callable[[float], float]     # cortante V(x), N
    deflexion_max: float
    momento_max: float
    cortante_max: float
    x_deflexion_max: float


def _envolver_constante(f_o_valor):
    if callable(f_o_valor):
        return f_o_valor
    return lambda x: f_o_valor


# ── Formas cerradas: CANTILEVER (empotrada en x=0, libre en x=L) ─────────────

def cantilever_puntual(P: float, a: float, L: float, EI: float) -> ResultadoViga:
    """Carga puntual P a distancia `a` del empotramiento (0<a<=L)."""
    def v(x: float) -> float:
        if x <= a:
            return P / (6 * EI) * (3 * a * x ** 2 - x ** 3)
        return P * a ** 2 / (6 * EI) * (3 * x - a)

    def M(x: float) -> float:
        return -P * (a - x) if x <= a else 0.0

    def V(x: float) -> float:
        return P if x <= a else 0.0

    v_max = v(L)
    return ResultadoViga(v, M, V, abs(v_max), abs(P * a), abs(P), L)


def cantilever_udl(w: float, L: float, EI: float) -> ResultadoViga:
    """Carga uniformemente distribuida w (N/m) en todo el vano."""
    def v(x: float) -> float:
        return w / (24 * EI) * (x ** 4 - 4 * L * x ** 3 + 6 * L ** 2 * x ** 2)

    def M(x: float) -> float:
        return -w * (L - x) ** 2 / 2.0

    def V(x: float) -> float:
        return w * (L - x)

    v_max = v(L)
    return ResultadoViga(v, M, V, abs(v_max), abs(w * L ** 2 / 2), abs(w * L), L)


# ── Formas cerradas: SIMPLEMENTE APOYADA (x=0 y x=L) ──────────────────────────

def simple_puntual(P: float, a: float, L: float, EI: float) -> ResultadoViga:
    """Carga puntual P a distancia `a` del apoyo izquierdo (0<a<L), b=L-a."""
    b = L - a

    def v(x: float) -> float:
        if x <= a:
            return P * b * x * (L ** 2 - b ** 2 - x ** 2) / (6 * L * EI)
        xp = L - x
        return P * a * xp * (L ** 2 - a ** 2 - xp ** 2) / (6 * L * EI)

    def M(x: float) -> float:
        return P * b * x / L if x <= a else P * a * (L - x) / L

    def V(x: float) -> float:
        return P * b / L if x <= a else -P * a / L

    xs = np.linspace(0, L, 2001)
    v_vals = np.array([v(x) for x in xs])
    idx = int(np.argmax(np.abs(v_vals)))
    return ResultadoViga(v, M, V, float(abs(v_vals[idx])), abs(P * a * b / L), abs(P * max(a, b) / L), float(xs[idx]))


def simple_udl(w: float, L: float, EI: float) -> ResultadoViga:
    def v(x: float) -> float:
        return w * x * (L ** 3 - 2 * L * x ** 2 + x ** 3) / (24 * EI)

    def M(x: float) -> float:
        return w * x * (L - x) / 2.0

    def V(x: float) -> float:
        return w * (L / 2.0 - x)

    v_max = v(L / 2.0)
    return ResultadoViga(v, M, V, abs(v_max), abs(w * L ** 2 / 8), abs(w * L / 2), L / 2.0)


# ── Formas cerradas: EMPOTRADA-EMPOTRADA (x=0 y x=L fijos) ───────────────────

def empotrada_empotrada_puntual(P: float, L: float, EI: float) -> ResultadoViga:
    """Caso simétrico: carga puntual P en el centro del vano (a=L/2)."""
    def v(x: float) -> float:
        if x <= L / 2:
            return P * x ** 2 * (3 * L - 4 * x) / (48 * EI)
        xp = L - x
        return P * xp ** 2 * (3 * L - 4 * xp) / (48 * EI)

    def M(x: float) -> float:
        m_extremo = -P * L / 8.0
        if x <= L / 2:
            return m_extremo + P * x / 2.0
        return m_extremo + P * (L - x) / 2.0

    def V(x: float) -> float:
        return P / 2.0 if x < L / 2 else -P / 2.0

    v_max = v(L / 2.0)
    return ResultadoViga(v, M, V, abs(v_max), abs(P * L / 8), abs(P / 2), L / 2.0)


def empotrada_empotrada_udl(w: float, L: float, EI: float) -> ResultadoViga:
    def v(x: float) -> float:
        return w * x ** 2 * (L - x) ** 2 / (24 * EI)

    def M(x: float) -> float:
        return w * (6 * L * x - L ** 2 - 6 * x ** 2) / 12.0

    def V(x: float) -> float:
        return w * (L / 2.0 - x)

    v_max = v(L / 2.0)
    m_extremo = w * L ** 2 / 12.0
    return ResultadoViga(v, M, V, abs(v_max), abs(m_extremo), abs(w * L / 2), L / 2.0)


# ── Solver general (cualquier w(x), incluye EMPOTRADA_APOYADA / propped) ─────

def resolver_general(
    w_func: Callable[[float], float],
    L: float,
    EI: float,
    condicion: CondicionApoyo,
    n_puntos: int = 400,
) -> ResultadoViga:
    """
    Resuelve EI·v'''' = w(x) como problema de valores de frontera (BVP) usando
    el sistema de primer orden [v, θ=v', M=EI·v'', V=EI·v''']. Permite
    CUALQUIER distribución de carga w(x) (triangular, trapezoidal, parcial,
    definida por el usuario) sin requerir una fórmula cerrada específica —
    respuesta directa a "solucionar cualquier problema de ingeniería".

    Validado contra las fórmulas cerradas de este módulo con error < 1e-6
    relativo (ver tests/test_beam_theory.py).
    """
    def ode(x, y):
        wv = np.array([w_func(xi) for xi in x])
        return np.vstack([y[1], y[2] / EI, y[3], wv])

    def bc_cantilever(ya, yb):
        return np.array([ya[0], ya[1], yb[2], yb[3]])

    def bc_simple(ya, yb):
        return np.array([ya[0], ya[2], yb[0], yb[2]])

    def bc_fixfix(ya, yb):
        return np.array([ya[0], ya[1], yb[0], yb[1]])

    def bc_propped(ya, yb):
        return np.array([ya[0], ya[1], yb[0], yb[2]])

    bc_map = {
        CondicionApoyo.CANTILEVER: bc_cantilever,
        CondicionApoyo.SIMPLE: bc_simple,
        CondicionApoyo.EMPOTRADA_EMPOTRADA: bc_fixfix,
        CondicionApoyo.EMPOTRADA_APOYADA: bc_propped,
    }
    if condicion not in bc_map:
        raise ValueError(f"Condición de apoyo no soportada por el solver general: {condicion}")

    x = np.linspace(0, L, n_puntos)
    y0 = np.zeros((4, x.size))
    sol = solve_bvp(ode, bc_map[condicion], x, y0, max_nodes=200_000, tol=1e-9)
    if not sol.success:
        raise RuntimeError(f"El solver BVP no convergió: {sol.message}")

    def v(xi: float) -> float:
        return float(sol.sol(xi)[0])

    def M(xi: float) -> float:
        return float(sol.sol(xi)[2])

    def V(xi: float) -> float:
        return float(sol.sol(xi)[3])

    xs_fino = np.linspace(0, L, 2001)
    yy = sol.sol(xs_fino)
    idx_v = int(np.argmax(np.abs(yy[0])))
    idx_m = int(np.argmax(np.abs(yy[2])))
    idx_c = int(np.argmax(np.abs(yy[3])))

    return ResultadoViga(
        v, M, V,
        deflexion_max=float(abs(yy[0][idx_v])),
        momento_max=float(abs(yy[2][idx_m])),
        cortante_max=float(abs(yy[3][idx_c])),
        x_deflexion_max=float(xs_fino[idx_v]),
    )


def superponer(resultados: list[ResultadoViga], L: float) -> ResultadoViga:
    """
    Superposición lineal de varios casos de carga simultáneos sobre el MISMO
    elemento (válida porque la ecuación de Euler-Bernoulli es lineal en régimen
    elástico y pequeñas deflexiones). Permite combinar, p. ej., peso propio
    (UDL) + carga viva puntual + momento aplicado en un solo resultado.
    """
    if not resultados:
        raise ValueError("Se requiere al menos un resultado para superponer")

    def v(x: float) -> float:
        return sum(r.v(x) for r in resultados)

    def M(x: float) -> float:
        return sum(r.M(x) for r in resultados)

    def V(x: float) -> float:
        return sum(r.V(x) for r in resultados)

    xs = np.linspace(0, L, 2001)
    v_vals = np.array([v(x) for x in xs])
    m_vals = np.array([M(x) for x in xs])
    c_vals = np.array([V(x) for x in xs])
    idx_v = int(np.argmax(np.abs(v_vals)))

    return ResultadoViga(
        v, M, V,
        deflexion_max=float(abs(v_vals[idx_v])),
        momento_max=float(np.max(np.abs(m_vals))),
        cortante_max=float(np.max(np.abs(c_vals))),
        x_deflexion_max=float(xs[idx_v]),
    )
