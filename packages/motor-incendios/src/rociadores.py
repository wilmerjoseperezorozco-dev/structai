"""Ubicación de rociadores (#336 F3): empaquetamiento en malla rectangular por paño, con criterios declarados.

Ningún valor normativo vive aquí. Las distancias máximas y mínimas entre rociadores, las distancias a muros, el área
máxima por rociador y la distancia del deflector al techo son CRITERIOS DEL PROYECTO. El diseñador los toma de la norma
aplicable (NFPA 13, NTC 2301 u otra), según el riesgo de la ocupación y el tipo de rociador, y declara la fuente.

Algoritmo (v1, paños rectangulares): en un paño Lx × Ly, la malla uniforme con nx × ny rociadores tiene separación
S = L/n y distancia a muro S/2. Se enumeran nx y ny y se elige el menor nx·ny que cumpla todos los criterios. Si hay
empate, gana la malla más cuadrada. Con la malla uniforme no se puede tener menos rociadores que la cota
ceil(A / área_max); el informe reporta las dos cifras.
Lo que v1 NO hace:
  - paños irregulares (en L, con huecos), que se descomponen en rectángulos (F3b);
  - las reglas de obstrucción de la norma (vigas, ductos, luminarias bajo el rociador), que se señalan para revisión y
    no se resuelven;
  - el desplazamiento de un rociador para salvar un obstáculo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from .geometria import Caja, Edificio, ejes


@dataclass(frozen=True)
class Criterios:
    """Criterios del proyecto, todos obligatorios (m, m²)."""
    s_max_m: float              # separación máxima entre rociadores en una línea
    s_min_m: float              # separación mínima entre rociadores
    d_muro_max_m: float         # distancia máxima de un rociador al muro (o a la cara de la viga que limita el paño)
    d_muro_min_m: float
    area_max_m2: float          # área máxima de cobertura por rociador
    deflector_m: float          # distancia del deflector bajo el techo, elegida dentro del rango de la norma
    fuente: str                 # norma, edición y numeral de donde salen los criterios

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente de los criterios (norma, edición, numeral)")
        if not (0 < self.s_min_m <= self.s_max_m and 0 <= self.d_muro_min_m <= self.d_muro_max_m
                and self.area_max_m2 > 0 and self.deflector_m >= 0):
            raise ValueError(f"criterios incoherentes: {self}")


@dataclass(frozen=True)
class Pano:
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    z_techo: float
    id: str = ""
    z_piso: float = 0.0

    @property
    def lx(self) -> float:
        return self.xmax - self.xmin

    @property
    def ly(self) -> float:
        return self.ymax - self.ymin


@dataclass
class Malla:
    pano: Pano
    nx: int
    ny: int
    puntos: list = field(default_factory=list)       # (x, y, z)

    @property
    def sx(self) -> float:
        return self.pano.lx / self.nx

    @property
    def sy(self) -> float:
        return self.pano.ly / self.ny

    @property
    def area_por_rociador_m2(self) -> float:
        return self.sx * self.sy


def _n_validos(L: float, c: Criterios) -> list[int]:
    """Números de rociadores en una dirección que cumplen separación y distancia a muro."""
    out = []
    n = max(1, math.ceil(L / c.s_max_m - 1e-9), math.ceil(L / (2 * c.d_muro_max_m) - 1e-9))
    while True:
        s = L / n
        if s / 2 < c.d_muro_min_m - 1e-9 or (n > 1 and s < c.s_min_m - 1e-9):
            break                                   # al subir n, s solo disminuye: ya no hay más válidos
        if s <= c.s_max_m + 1e-9 and s / 2 <= c.d_muro_max_m + 1e-9:
            out.append(n)
        n += 1
    return out


def malla(pano: Pano, c: Criterios) -> tuple[Optional[Malla], str]:
    """Malla uniforme con el menor número de rociadores que cumple los criterios, o (None, motivo)."""
    nxs, nys = _n_validos(pano.lx, c), _n_validos(pano.ly, c)
    if not nxs or not nys:
        eje = "x" if not nxs else "y"
        return None, f"paño {pano.id}: ninguna malla cumple separación y distancia a muro en {eje}"
    mejor = None
    for nx in nxs:
        for ny in nys:
            if (pano.lx / nx) * (pano.ly / ny) > c.area_max_m2 + 1e-9:
                continue
            clave = (nx * ny, abs(pano.lx / nx - pano.ly / ny))
            if mejor is None or clave < mejor[0]:
                mejor = (clave, nx, ny)
    if mejor is None:
        return None, f"paño {pano.id}: ninguna malla cumple el área máxima por rociador sin violar la separación mínima"
    _, nx, ny = mejor
    m = Malla(pano, nx, ny)
    z = pano.z_techo - c.deflector_m
    for i in range(nx):
        for j in range(ny):
            m.puntos.append((pano.xmin + (i + 0.5) * m.sx, pano.ymin + (j + 0.5) * m.sy, z))
    return m, "ok"


def panos_entre_vigas(p, piso: int, espesor_losa_m: float) -> list[Pano]:
    """Paños del techo de un piso de pórticos, limitados por las caras de las vigas (las vigas se tratan como límite del
    paño: es la hipótesis del diseñador cuando su peralte obliga a tratarlas así según la norma que aplique)."""
    xs, ys, zs = ejes(p)
    b = p.vigas_mm[piso][0] / 1000
    z_techo = zs[piso + 1] - espesor_losa_m
    return [Pano(xs[i] + b / 2, ys[j] + b / 2, xs[i + 1] - b / 2, ys[j + 1] - b / 2, z_techo, f"P{piso}-{i}-{j}", zs[piso])
            for i in range(len(xs) - 1) for j in range(len(ys) - 1)]


@dataclass
class Distribucion:
    mallas: list[Malla]
    fallidos: list[str]
    cota_inferior: int                   # Σ ceil(A_paño / área_max), mínimo teórico ignorando la geometría
    observaciones: list[str] = field(default_factory=list)

    @property
    def puntos(self) -> list:
        return [pt for m in self.mallas for pt in m.puntos]

    @property
    def n(self) -> int:
        return len(self.puntos)


def distribuir(panos: list[Pano], c: Criterios, edificio: Optional[Edificio] = None) -> Distribucion:
    """Mallas por paño. Si se da el edificio, señala los rociadores con un obstáculo entre el deflector y el piso (ducto,
    bandeja, tubería u otro bajo el rociador) o dentro de una columna o muro. Esos casos quedan para revisión: v1 no
    aplica las reglas de obstrucción."""
    mallas, fallidos = [], []
    cota = 0
    for pn in panos:
        cota += math.ceil(pn.lx * pn.ly / c.area_max_m2 - 1e-9)
        m, motivo = malla(pn, c)
        (mallas.append(m) if m else fallidos.append(motivo))
    d = Distribucion(mallas, fallidos, cota)
    if edificio is not None:
        for m in mallas:
            for x, y, z in m.puntos:
                for o in edificio.candidatos(Caja(x, y, m.pano.z_piso, x, y, z)):
                    if not (o.xmin <= x <= o.xmax and o.ymin <= y <= o.ymax):
                        continue
                    if o.tipo in ("columna", "muro") and o.zmin < z < o.zmax:
                        d.observaciones.append(f"rociador ({x:.2f}, {y:.2f}) dentro de {o.tipo} {o.id}")
                    elif o.tipo in ("ducto", "bandeja", "tuberia", "otro") and m.pano.z_piso < o.zmax <= z + 1e-9:
                        d.observaciones.append(f"rociador ({x:.2f}, {y:.2f}) con {o.tipo} {o.id} debajo: revisar obstrucción")
    return d


def verificar(d: Distribucion, c: Criterios) -> list[str]:
    """Revisión independiente de la malla. Comprueba separación mínima entre todos los pares (también entre paños),
    separación máxima con el vecino de la misma línea, distancias a los bordes y área por rociador. Devuelve los
    incumplimientos."""
    errores = []
    pts = d.puntos
    for a in range(len(pts)):
        for b in range(a + 1, len(pts)):
            dist = math.dist(pts[a][:2], pts[b][:2])
            if dist < c.s_min_m - 1e-9:
                errores.append(f"separación {dist:.3f} m < mínima entre {pts[a][:2]} y {pts[b][:2]}")
    for m in d.mallas:
        if m.nx > 1 and m.sx > c.s_max_m + 1e-9 or m.ny > 1 and m.sy > c.s_max_m + 1e-9:
            errores.append(f"{m.pano.id}: separación mayor que la máxima")
        if m.area_por_rociador_m2 > c.area_max_m2 + 1e-9:
            errores.append(f"{m.pano.id}: área por rociador {m.area_por_rociador_m2:.2f} m² > máxima")
        pn = m.pano
        filas: dict = {}                                   # líneas paralelas a x (misma y) y a y (misma x)
        cols: dict = {}
        for x, y, _ in m.puntos:
            filas.setdefault(round(y, 6), []).append(x)
            cols.setdefault(round(x, 6), []).append(y)
        for linea, lo, hi in [(v, pn.xmin, pn.xmax) for v in filas.values()] + [(v, pn.ymin, pn.ymax) for v in cols.values()]:
            for dm in (min(linea) - lo, hi - max(linea)):  # el rociador extremo de la línea frente a cada borde
                if dm < c.d_muro_min_m - 1e-9:
                    errores.append(f"{pn.id}: rociador a {dm:.3f} m del borde < mínima")
                if dm > c.d_muro_max_m + 1e-9:
                    errores.append(f"{pn.id}: rociador a {dm:.3f} m del borde > máxima")
    return errores
