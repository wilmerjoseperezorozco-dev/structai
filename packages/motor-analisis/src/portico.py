"""Análisis matricial de pórticos planos por el método de rigidez directa (elementos de viga-columna 1D, Euler-Bernoulli).

3 grados de libertad por nodo (ux, uy, rz). Unidades consistentes: kN, m (E en kN/m², A en m², I en m⁴).
Convención de signos de los diagramas (vigas horizontales): momento positivo = tracción en la fibra inferior (sagging),
cortante positivo = el de una reacción izquierda hacia arriba, axial positivo = tracción.

Alcance: elementos prismáticos, cargas nodales y uniformes transversales sobre elementos horizontales, apoyos
rígidos (ux, uy, rz restringidos o libres). Sin efectos de segundo orden, sin deformación por cortante, sin
no linealidad del material: los efectos de agrietamiento se representan reduciendo I desde fuera.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class Nodo:
    x: float
    y: float


@dataclass(frozen=True)
class Elemento:
    i: int
    j: int
    E: float
    A: float
    I: float


@dataclass
class Caso:
    """Un caso de carga (D, L, E...): cargas nodales (fx, fy, mz) y uniformes hacia abajo w (kN/m) por elemento."""
    nombre: str
    nodales: dict[int, tuple[float, float, float]] = field(default_factory=dict)
    uniformes: dict[int, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ResultadoCaso:
    nombre: str
    u: np.ndarray                 # (n, 3) desplazamientos globales
    reacciones: dict[int, tuple[float, float, float]]
    f_extremos: dict[int, np.ndarray]   # fuerzas sobre el elemento en ejes locales [N1,V1,M1,N2,V2,M2]
    q_local: dict[int, float]


class Portico:
    def __init__(self, nodos: list[Nodo], elementos: list[Elemento], apoyos: dict[int, tuple[bool, bool, bool]]):
        if not apoyos:
            raise ValueError("El modelo necesita al menos un apoyo")
        self.nodos, self.elementos, self.apoyos = nodos, elementos, apoyos
        for e in elementos:
            if e.i == e.j or self.longitud(e) <= 0:
                raise ValueError("Elemento de longitud nula")
        self._K = self._ensamblar()
        self._libres = np.array([3 * n + k for n in range(len(nodos)) for k in range(3)
                                 if not (n in apoyos and apoyos[n][k])])
        if self._libres.size and np.linalg.cond(self._K[np.ix_(self._libres, self._libres)]) > 1e14:
            raise ValueError("Modelo inestable o mal restringido (matriz de rigidez singular)")

    # ---- geometría y matrices -------------------------------------------------
    def longitud(self, e: Elemento) -> float:
        a, b = self.nodos[e.i], self.nodos[e.j]
        return math.hypot(b.x - a.x, b.y - a.y)

    def _angulo(self, e: Elemento) -> float:
        a, b = self.nodos[e.i], self.nodos[e.j]
        return math.atan2(b.y - a.y, b.x - a.x)

    @staticmethod
    def _k_local(e: Elemento, L: float) -> np.ndarray:
        EA, EI = e.E * e.A / L, e.E * e.I
        a, b, c, d = 12 * EI / L**3, 6 * EI / L**2, 4 * EI / L, 2 * EI / L
        return np.array([[EA, 0, 0, -EA, 0, 0],
                         [0, a, b, 0, -a, b],
                         [0, b, c, 0, -b, d],
                         [-EA, 0, 0, EA, 0, 0],
                         [0, -a, -b, 0, a, -b],
                         [0, b, d, 0, -b, c]])

    def _T(self, e: Elemento) -> np.ndarray:
        c, s = math.cos(self._angulo(e)), math.sin(self._angulo(e))
        R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T = np.zeros((6, 6))
        T[:3, :3], T[3:, 3:] = R, R
        return T

    def _gdl(self, e: Elemento) -> list[int]:
        return [3 * e.i, 3 * e.i + 1, 3 * e.i + 2, 3 * e.j, 3 * e.j + 1, 3 * e.j + 2]

    def _ensamblar(self) -> np.ndarray:
        K = np.zeros((3 * len(self.nodos),) * 2)
        for e in self.elementos:
            T = self._T(e)
            kg = T.T @ self._k_local(e, self.longitud(e)) @ T
            g = self._gdl(e)
            K[np.ix_(g, g)] += kg
        return K

    # ---- solución -------------------------------------------------------------
    def _q_local(self, idx: int, w_abajo: float) -> float:
        ang = self._angulo(self.elementos[idx])
        if abs(math.sin(ang)) > 1e-9:
            raise ValueError("Las cargas uniformes solo se admiten en elementos horizontales")
        return -w_abajo * math.cos(ang)       # local +y coincide con +y global (ang=0) y se invierte si ang=pi

    @staticmethod
    def _f0(q: float, L: float) -> np.ndarray:
        """Reacciones de empotramiento sobre el elemento por carga uniforme local q."""
        return np.array([0.0, -q * L / 2, -q * L**2 / 12, 0.0, -q * L / 2, q * L**2 / 12])

    def resolver(self, caso: Caso) -> ResultadoCaso:
        n = len(self.nodos)
        F = np.zeros(3 * n)
        for nodo, (fx, fy, mz) in caso.nodales.items():
            F[3 * nodo: 3 * nodo + 3] += (fx, fy, mz)
        qs: dict[int, float] = {}
        for idx, w in caso.uniformes.items():
            e = self.elementos[idx]
            q = self._q_local(idx, w)
            qs[idx] = q
            f0g = self._T(e).T @ self._f0(q, self.longitud(e))
            F[self._gdl(e)] -= f0g           # carga nodal equivalente = -T'·f0
        u = np.zeros(3 * n)
        lib = self._libres
        if lib.size:
            u[lib] = np.linalg.solve(self._K[np.ix_(lib, lib)], F[lib])
        R = self._K @ u - F
        fext = {}
        for idx, e in enumerate(self.elementos):
            L = self.longitud(e)
            f = self._k_local(e, L) @ (self._T(e) @ u[self._gdl(e)])
            if idx in qs:
                f = f + self._f0(qs[idx], L)
            fext[idx] = f
        reac = {nodo: tuple(float(R[3 * nodo + k]) if self.apoyos[nodo][k] else 0.0 for k in range(3))
                for nodo in self.apoyos}
        return ResultadoCaso(caso.nombre, u.reshape(n, 3), reac, fext, qs)

    # ---- diagramas ------------------------------------------------------------
    def diagrama(self, r: ResultadoCaso, idx: int, xs: np.ndarray) -> dict[str, np.ndarray]:
        """N(x), V(x), M(x) a lo largo del elemento (x desde el nodo i, en m)."""
        f = r.f_extremos[idx]
        q = r.q_local.get(idx, 0.0)
        xs = np.asarray(xs, dtype=float)
        return {"N": -f[0] * np.ones_like(xs),
                "V": f[1] + q * xs,
                "M": -f[2] + f[1] * xs + q * xs**2 / 2}
