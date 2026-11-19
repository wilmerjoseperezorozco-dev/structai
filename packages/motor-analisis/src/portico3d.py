"""Análisis matricial de pórticos espaciales (3D) por rigidez directa, con diafragmas rígidos por piso (#274, F1).

6 grados de libertad por nodo (ux, uy, uz, rx, ry, rz). Unidades consistentes: kN, m (E y G en kN/m², A en m², I y J en m⁴).
Ejes locales del elemento: x del nodo i al j.
  Elemento no vertical: z_local = x × Z_global (horizontal) e y_local = z_local × x (en el plano vertical que contiene
  al elemento). En una viga horizontal, Iz resiste la flexión vertical (eje fuerte si el alma es vertical).
  Elemento vertical (columna): y_local = X_global, z_local = x × y. Así, en una columna, Iz resiste el desplazamiento
  en X global e Iy el desplazamiento en Y global.
  `eje_ref` (opcional) reemplaza la referencia: y_local se toma en el plano (x, eje_ref).
Diafragma rígido (NSR-10 A.3.6.7.2 b): los nodos del piso comparten ux, uy y rz de un nodo maestro (centro de masa):
  ux_s = ux_m − (y_s − y_m)·rz_m,  uy_s = uy_m + (x_s − x_m)·rz_m,  rz_s = rz_m.
Alcance: elementos prismáticos de Euler-Bernoulli, material lineal, sin segundo orden ni deformación por cortante.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

COND_MAX = 1e14


@dataclass(frozen=True)
class Nodo3D:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Elemento3D:
    i: int
    j: int
    E: float
    G: float
    A: float
    Iy: float
    Iz: float
    J: float
    eje_ref: Optional[tuple[float, float, float]] = None


@dataclass(frozen=True)
class Diafragma:
    """Piso con diafragma rígido: nodos esclavos y posición (x, y) del nodo maestro (centro de masa)."""
    nombre: str
    nodos: tuple[int, ...]
    x_cm: float
    y_cm: float


@dataclass
class Caso3D:
    nombre: str
    nodales: dict[int, tuple[float, float, float, float, float, float]] = field(default_factory=dict)
    maestros: dict[str, tuple[float, float, float]] = field(default_factory=dict)   # diafragma → (Fx, Fy, Mz)
    uniformes: dict[int, tuple[float, float, float]] = field(default_factory=dict)   # elemento → (wx, wy, wz) kN/m global


@dataclass(frozen=True)
class Resultado3D:
    nombre: str
    u: np.ndarray                              # (n, 6) desplazamientos globales de los nodos
    maestros: dict[str, tuple[float, float, float]]   # diafragma → (ux, uy, rz) del centro de masa
    reacciones: dict[int, np.ndarray]
    f_extremos: dict[int, np.ndarray]          # fuerzas sobre el elemento en ejes locales (12)


class Portico3D:
    def __init__(self, nodos: list[Nodo3D], elementos: list[Elemento3D], apoyos: dict[int, tuple[bool, ...]],
                 diafragmas: list[Diafragma] | None = None):
        if not apoyos:
            raise ValueError("El modelo necesita al menos un apoyo")
        self.nodos, self.elementos, self.apoyos = nodos, elementos, apoyos
        self.diafragmas = list(diafragmas or [])
        n = len(nodos)
        for k, r in apoyos.items():
            if not (0 <= k < n) or len(r) != 6:
                raise ValueError("Cada apoyo debe referir un nodo existente y dar 6 restricciones (ux, uy, uz, rx, ry, rz)")
        for e in elementos:
            if not (0 <= e.i < n and 0 <= e.j < n) or e.i == e.j or self.longitud(e) <= 0:
                raise ValueError("Elemento con nodos inexistentes o de longitud nula")
            if min(e.E, e.G, e.A, e.Iy, e.Iz, e.J) <= 0:
                raise ValueError("E, G, A, Iy, Iz y J deben ser positivos")
        vistos: set[int] = set()
        nombres = set()
        for d in self.diafragmas:
            if d.nombre in nombres:
                raise ValueError(f"Diafragma repetido: {d.nombre}")
            nombres.add(d.nombre)
            if len(d.nodos) < 1:
                raise ValueError("Un diafragma necesita al menos un nodo")
            zs = {round(nodos[k].z, 6) for k in d.nodos}
            if len(zs) != 1:
                raise ValueError(f"Los nodos del diafragma {d.nombre} deben estar a la misma cota")
            for k in d.nodos:
                if k in vistos:
                    raise ValueError("Un nodo no puede pertenecer a dos diafragmas")
                if k in apoyos and any(apoyos[k][g] for g in (0, 1, 5)):
                    raise ValueError("Un nodo de diafragma no puede restringir ux, uy ni rz (los gobierna el maestro)")
                vistos.add(k)
        self._C, self._nred, self._maestro_idx = self._restricciones()
        self._K = self._ensamblar()
        self._Kr = self._C.T @ self._K @ self._C
        if self._nred and np.linalg.cond(self._Kr) > COND_MAX:
            raise ValueError("Modelo inestable o mal restringido (matriz de rigidez singular)")

    # ---- geometría y matrices -------------------------------------------------
    def longitud(self, e: Elemento3D) -> float:
        a, b = self.nodos[e.i], self.nodos[e.j]
        return math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))

    def rotacion(self, e: Elemento3D) -> np.ndarray:
        a, b = self.nodos[e.i], self.nodos[e.j]
        x = np.array([b.x - a.x, b.y - a.y, b.z - a.z]) / self.longitud(e)
        if e.eje_ref is not None:
            v = np.asarray(e.eje_ref, float)
            z = np.cross(x, v)
            if np.linalg.norm(z) < 1e-9:
                raise ValueError("eje_ref no puede ser paralelo al elemento")
            z /= np.linalg.norm(z)
            y = np.cross(z, x)
        elif abs(x[2]) > 1 - 1e-9:           # vertical
            y = np.array([1.0, 0.0, 0.0])
            z = np.cross(x, y)
        else:
            z = np.cross(x, [0.0, 0.0, 1.0])
            z /= np.linalg.norm(z)
            y = np.cross(z, x)
        return np.vstack([x, y, z])

    def _T(self, e: Elemento3D) -> np.ndarray:
        R = self.rotacion(e)
        T = np.zeros((12, 12))
        for b in range(4):
            T[3 * b:3 * b + 3, 3 * b:3 * b + 3] = R
        return T

    @staticmethod
    def k_local(e: Elemento3D, L: float) -> np.ndarray:
        k = np.zeros((12, 12))
        EA, GJ = e.E * e.A / L, e.G * e.J / L
        k[0, 0] = k[6, 6] = EA
        k[0, 6] = -EA
        k[3, 3] = k[9, 9] = GJ
        k[3, 9] = -GJ
        a, b, c, d = 12 * e.E * e.Iz / L**3, 6 * e.E * e.Iz / L**2, 4 * e.E * e.Iz / L, 2 * e.E * e.Iz / L
        k[1, 1] = k[7, 7] = a
        k[1, 7] = -a
        k[1, 5] = k[1, 11] = b
        k[5, 7] = k[7, 11] = -b
        k[5, 5] = k[11, 11] = c
        k[5, 11] = d
        a, b, c, d = 12 * e.E * e.Iy / L**3, 6 * e.E * e.Iy / L**2, 4 * e.E * e.Iy / L, 2 * e.E * e.Iy / L
        k[2, 2] = k[8, 8] = a
        k[2, 8] = -a
        k[2, 4] = k[2, 10] = -b
        k[4, 8] = k[8, 10] = b
        k[4, 4] = k[10, 10] = c
        k[4, 10] = d
        return np.triu(k) + np.triu(k, 1).T

    def _gdl(self, e: Elemento3D) -> list[int]:
        return [6 * e.i + k for k in range(6)] + [6 * e.j + k for k in range(6)]

    def _ensamblar(self) -> np.ndarray:
        K = np.zeros((6 * len(self.nodos),) * 2)
        for e in self.elementos:
            T = self._T(e)
            g = self._gdl(e)
            K[np.ix_(g, g)] += T.T @ self.k_local(e, self.longitud(e)) @ T
        return K

    def _restricciones(self):
        """u_completo = C · u_reducido (apoyos eliminados, esclavos expresados con su maestro)."""
        n = len(self.nodos)
        esclavo = {k: d for d in self.diafragmas for k in d.nodos}
        idx = 0
        mapa: dict[int, int] = {}
        for nodo in range(n):
            for g in range(6):
                if nodo in esclavo and g in (0, 1, 5):
                    continue
                if nodo in self.apoyos and self.apoyos[nodo][g]:
                    continue
                mapa[6 * nodo + g] = idx
                idx += 1
        maestro_idx = {}
        for d in self.diafragmas:
            maestro_idx[d.nombre] = (idx, idx + 1, idx + 2)
            idx += 3
        C = np.zeros((6 * n, idx))
        for gfull, r in mapa.items():
            C[gfull, r] = 1.0
        for k, d in esclavo.items():
            mx, my, mr = maestro_idx[d.nombre]
            dx, dy = self.nodos[k].x - d.x_cm, self.nodos[k].y - d.y_cm
            C[6 * k, mx], C[6 * k, mr] = 1.0, -dy
            C[6 * k + 1, my], C[6 * k + 1, mr] = 1.0, dx
            C[6 * k + 5, mr] = 1.0
        return C, idx, maestro_idx

    # ---- cargas de elemento ---------------------------------------------------
    def _f0(self, e: Elemento3D, w_global) -> np.ndarray:
        """Fuerzas de empotramiento (ejes locales) por carga uniforme w (kN/m, ejes globales)."""
        L = self.longitud(e)
        qx, qy, qz = self.rotacion(e) @ np.asarray(w_global, float)
        f = np.zeros(12)
        f[0] = f[6] = -qx * L / 2
        f[1], f[5], f[7], f[11] = -qy * L / 2, -qy * L**2 / 12, -qy * L / 2, qy * L**2 / 12
        f[2], f[4], f[8], f[10] = -qz * L / 2, qz * L**2 / 12, -qz * L / 2, -qz * L**2 / 12
        return f

    # ---- solución -------------------------------------------------------------
    def resolver(self, caso: Caso3D) -> Resultado3D:
        n = len(self.nodos)
        F = np.zeros(6 * n)
        for nodo, v in caso.nodales.items():
            if not 0 <= nodo < n:
                raise ValueError(f"Carga en nodo inexistente: {nodo}")
            F[6 * nodo:6 * nodo + 6] += v
        f0s = {}
        for idx, w in caso.uniformes.items():
            e = self.elementos[idx]
            f0 = self._f0(e, w)
            f0s[idx] = f0
            F[self._gdl(e)] -= self._T(e).T @ f0
        Fr = self._C.T @ F
        for nombre, (fx, fy, mz) in caso.maestros.items():
            if nombre not in self._maestro_idx:
                raise ValueError(f"Diafragma inexistente: {nombre}")
            a, b, c = self._maestro_idx[nombre]
            Fr[a] += fx
            Fr[b] += fy
            Fr[c] += mz
        ur = np.linalg.solve(self._Kr, Fr) if self._nred else np.zeros(0)
        u = self._C @ ur
        R = self._K @ u - F
        reac = {k: np.where(np.array(r, bool), R[6 * k:6 * k + 6], 0.0) for k, r in self.apoyos.items()}
        fext = {}
        for idx, e in enumerate(self.elementos):
            f = self.k_local(e, self.longitud(e)) @ (self._T(e) @ u[self._gdl(e)])
            fext[idx] = f + f0s.get(idx, 0.0)
        maes = {nm: (float(ur[a]), float(ur[b]), float(ur[c])) for nm, (a, b, c) in self._maestro_idx.items()}
        return Resultado3D(caso.nombre, u.reshape(n, 6), maes, reac, fext)

    def numero_condicion(self) -> float:
        return float(np.linalg.cond(self._Kr)) if self._nred else 1.0
