"""Propiedades de sección de pared delgada por el método lineal (línea media × espesor), issue #81.

NSR-10 F.4.3.1: las propiedades se calculan por métodos convencionales del diseño estructural. Aquí se usa el método
lineal: cada elemento es un segmento recto de la línea media con espesor uniforme t; se desprecian los términos en t³
salvo en la constante de Saint-Venant J = Σ l·t³/3.

Perfil abierto de UNA sola rama (C, C con pestaña, ángulo, Z). Las propiedades sectoriales (centro de cortante y Cw)
se obtienen integrando la coordenada sectorial ω a lo largo de la rama, con las condiciones ∫ω_s·x dA = ∫ω_s·y dA = 0
(centro de cortante) y ∫ω_n dA = 0 (normalización). Las integrales de productos de funciones lineales por segmento
son exactas: ∫f·g dA = t·l·(2·fi·gi + fi·gj + fj·gi + 2·fj·gj)/6.

Convención: ejes x (horizontal) e y (vertical) centroidales; Ix = ∫(y − yc)² dA, Iy = ∫(x − xc)² dA.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class Propiedades:
    A: float      # mm²
    xc: float     # mm
    yc: float     # mm
    Ix: float     # mm⁴, respecto al eje centroidal horizontal
    Iy: float     # mm⁴, respecto al eje centroidal vertical
    Ixy: float    # mm⁴
    J: float      # mm⁴
    xs: float     # mm, centro de cortante
    ys: float     # mm
    Cw: float     # mm⁶

    @property
    def rx(self) -> float:
        return math.sqrt(self.Ix / self.A)

    @property
    def ry(self) -> float:
        return math.sqrt(self.Iy / self.A)

    @property
    def xo(self) -> float:
        """Distancia centro de cortante – centroide en x (F.4.3.3-13 la toma negativa; aquí solo entra al cuadrado)."""
        return self.xs - self.xc

    @property
    def ro(self) -> float:
        """Radio polar de giro respecto al centro de cortante, F.4.3.3-13 (con yo = ys − yc, nulo en secciones C)."""
        return math.sqrt(self.rx ** 2 + self.ry ** 2 + self.xo ** 2 + (self.ys - self.yc) ** 2)


def _int2(fi: float, fj: float, gi: float, gj: float, l: float, t: float) -> float:
    return t * l * (2 * fi * gi + fi * gj + fj * gi + 2 * fj * gj) / 6.0


def propiedades_brutas(nodos: Sequence[tuple[float, float]], t: float) -> Propiedades:
    """Propiedades de la línea poligonal `nodos` (mm) con espesor t (mm). Falla si la geometría es degenerada."""
    if not (t > 0 and math.isfinite(t)):
        raise ValueError(f"Espesor t = {t} inválido: debe ser positivo (NSR-10 F.4.3.1).")
    if len(nodos) < 2:
        raise ValueError("Se necesitan al menos 2 nodos para definir la sección (NSR-10 F.4.3.1).")
    p = np.asarray(nodos, dtype=float)
    if not np.all(np.isfinite(p)):
        raise ValueError("Coordenadas de nodos no finitas (NSR-10 F.4.3.1).")
    long = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
    if np.any(long <= 0):
        raise ValueError("Hay segmentos de longitud nula en la sección (NSR-10 F.4.3.1).")

    A = float(t * long.sum())
    xc = float(np.sum(t * long * (p[:-1, 0] + p[1:, 0]) / 2) / A)
    yc = float(np.sum(t * long * (p[:-1, 1] + p[1:, 1]) / 2) / A)
    X, Y = p[:, 0] - xc, p[:, 1] - yc

    w = np.zeros(len(p))                        # coordenada sectorial con polo en el centroide
    for k in range(len(p) - 1):
        w[k + 1] = w[k] + X[k] * Y[k + 1] - X[k + 1] * Y[k]

    def integral(f: np.ndarray, g: np.ndarray) -> float:
        return float(sum(_int2(f[k], f[k + 1], g[k], g[k + 1], long[k], t) for k in range(len(long))))

    Ixx, Iyy, Ixy = integral(Y, Y), integral(X, X), integral(X, Y)
    Iwx, Iwy = integral(w, X), integral(w, Y)
    # ω_s = ω − xs·Y + ys·X ;  ∫ω_s·X = 0  y  ∫ω_s·Y = 0
    M = np.array([[-Ixy, Iyy], [-Ixx, Ixy]])
    if abs(np.linalg.det(M)) <= 1e-12 * max(Ixx * Iyy, 1.0):
        raise ValueError("Sección sin rigidez a flexión en algún eje: no se puede ubicar el centro de cortante.")
    xs_rel, ys_rel = np.linalg.solve(M, np.array([-Iwx, -Iwy]))
    ws = w - xs_rel * Y + ys_rel * X
    ws = ws - integral(ws, np.ones(len(p))) / A
    Cw = integral(ws, ws)
    J = float(np.sum(long * t ** 3 / 3))
    return Propiedades(A=A, xc=xc, yc=yc, Ix=Ixx, Iy=Iyy, Ixy=Ixy, J=J,
                       xs=float(xc + xs_rel), ys=float(yc + ys_rel), Cw=float(Cw))


@dataclass(frozen=True)
class GeometriaC:
    """Perfil C (con o sin pestaña) a 90°, esquinas rectas (radio interior 0). Dimensiones externas en mm.

    H = altura total, B = ancho total de aleta, D = longitud total de la pestaña (0 = C sin pestaña), t = espesor.
    Línea media: alma hc = H − t, aleta bc = B − t, pestaña dc = D − t/2.
    Anchos planos (para pandeo local): alma H − 2t, aleta B − 2t, pestaña D − t.
    """
    H: float
    B: float
    D: float
    t: float

    def __post_init__(self) -> None:
        for nombre, v in (("H", self.H), ("B", self.B), ("t", self.t)):
            if not (v > 0 and math.isfinite(v)):
                raise ValueError(f"{nombre} = {v} inválido: debe ser positivo (NSR-10 F.4.3.1).")
        if not (self.D >= 0 and math.isfinite(self.D)):
            raise ValueError(f"D = {self.D} inválido: 0 para C sin pestaña o positivo (NSR-10 F.4.2.4).")
        if self.H <= 2 * self.t or self.B <= 2 * self.t:
            raise ValueError("H y B deben exceder 2t para que existan anchos planos (NSR-10 F.4.2).")
        if 0 < self.D <= self.t:
            raise ValueError("D debe exceder t para que la pestaña tenga ancho plano (NSR-10 F.4.2.4).")

    @property
    def con_pestana(self) -> bool:
        return self.D > 0

    @property
    def hc(self) -> float:
        return self.H - self.t

    @property
    def bc(self) -> float:
        return self.B - self.t

    @property
    def dc(self) -> float:
        return self.D - self.t / 2 if self.con_pestana else 0.0

    @property
    def w_alma(self) -> float:
        return self.H - 2 * self.t

    @property
    def w_aleta(self) -> float:
        return self.B - 2 * self.t

    @property
    def d_pestana(self) -> float:
        return self.D - self.t if self.con_pestana else 0.0

    def nodos(self) -> list[tuple[float, float]]:
        """Línea media con el alma en x = 0 y la abertura hacia +x; y = 0 en la aleta inferior."""
        hc, bc, dc = self.hc, self.bc, self.dc
        cuerpo = [(bc, 0.0), (0.0, 0.0), (0.0, hc), (bc, hc)]
        if not self.con_pestana:
            return cuerpo
        return [(bc, dc)] + cuerpo + [(bc, hc - dc)]

    def propiedades(self) -> Propiedades:
        return propiedades_brutas(self.nodos(), self.t)
