"""Geometría para la red contra incendio (#336 F2): pisos, alturas libres y mapa de obstáculos con detección de colisiones.

Modelo: cajas alineadas con los ejes (AABB) en metros, en coordenadas globales (z = 0 en el nivel del primer piso).
  - vigas y columnas: del modelo de pórticos (adaptador `desde_porticos`, que no importa el orquestador: lee los campos);
  - ductos, bandejas, tuberías de otros sistemas: entrada declarada (`Caja` con tipo) o, en F2b, desde IFC;
  - la losa: su cara inferior define el techo de cada piso (z_techo = z del nivel superior − espesor de losa).
Convención declarada: la altura h de la viga es TOTAL (incluye la losa), así que el fondo de la viga está en
z_nivel − h, y la viga ocupa de z_nivel − h a z_nivel.
Las colisiones se revisan con una holgura declarada por el usuario (no hay valor normativo aquí).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, Optional

TIPOS = ("viga", "columna", "losa", "muro", "ducto", "bandeja", "tuberia", "otro")


@dataclass(frozen=True)
class Caja:
    """Caja alineada con los ejes, m."""
    xmin: float
    ymin: float
    zmin: float
    xmax: float
    ymax: float
    zmax: float
    tipo: str = "otro"
    id: str = ""

    def __post_init__(self):
        if not (self.xmin <= self.xmax and self.ymin <= self.ymax and self.zmin <= self.zmax):
            raise ValueError(f"caja invertida: {self}")
        if self.tipo not in TIPOS:
            raise ValueError(f"tipo desconocido: {self.tipo}")

    def inflada(self, h: float) -> "Caja":
        return Caja(self.xmin - h, self.ymin - h, self.zmin - h, self.xmax + h, self.ymax + h, self.zmax + h, self.tipo, self.id)

    def interseca(self, o: "Caja") -> bool:
        """Intersección con volumen positivo (tocarse en una cara no es colisión)."""
        return (self.xmin < o.xmax and o.xmin < self.xmax and self.ymin < o.ymax and o.ymin < self.ymax
                and self.zmin < o.zmax and o.zmin < self.zmax)


@dataclass
class Piso:
    indice: int
    z_piso: float                 # nivel de piso terminado (aprox. cara superior de la losa inferior)
    z_techo: float                # cara inferior de la losa superior
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def area_m2(self) -> float:
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)

    @property
    def altura_bajo_losa_m(self) -> float:
        return self.z_techo - self.z_piso


@dataclass
class Edificio:
    pisos: list[Piso]
    obstaculos: list[Caja] = field(default_factory=list)
    celda_m: float = 1.0
    _rejilla: dict = field(default_factory=dict, repr=False)

    def __post_init__(self):
        self._indexar()

    def _celdas(self, c: Caja):
        f = self.celda_m
        for i in range(math.floor(c.xmin / f), math.floor(c.xmax / f) + 1):
            for j in range(math.floor(c.ymin / f), math.floor(c.ymax / f) + 1):
                for k in range(math.floor(c.zmin / f), math.floor(c.zmax / f) + 1):
                    yield (i, j, k)

    def _indexar(self):
        self._rejilla = {}
        for n, c in enumerate(self.obstaculos):
            for cel in self._celdas(c):
                self._rejilla.setdefault(cel, []).append(n)

    def agregar(self, cajas: Iterable[Caja]) -> None:
        self.obstaculos.extend(cajas)
        self._indexar()

    def candidatos(self, c: Caja) -> list[Caja]:
        idx = set()
        for cel in self._celdas(c):
            idx.update(self._rejilla.get(cel, ()))
        return [self.obstaculos[i] for i in sorted(idx)]

    def colisiones(self, c: Caja, holgura_m: float = 0.0, ignorar: tuple = ()) -> list[Caja]:
        """Obstáculos que invaden la caja `c` inflada en la holgura (excepto los tipos en `ignorar`)."""
        ci = c.inflada(holgura_m)
        return [o for o in self.candidatos(ci) if o.tipo not in ignorar and o.interseca(ci)]

    def altura_libre(self, piso: Piso, x: float, y: float, tipos: tuple = ("viga", "ducto", "bandeja", "tuberia", "otro")) -> float:
        """Altura libre en (x, y) del piso: del piso a la cara inferior del obstáculo más bajo sobre ese punto, o a la
        losa si no hay ninguno. Columnas y muros no cuentan (cubren el punto entero: no hay techo libre allí)."""
        z = piso.z_techo
        sonda = Caja(x, y, piso.z_piso, x, y, piso.z_techo)
        for o in self.candidatos(sonda):
            if o.tipo in tipos and o.xmin <= x <= o.xmax and o.ymin <= y <= o.ymax and piso.z_piso < o.zmin < z:
                z = o.zmin
        return z - piso.z_piso

    def mapa_altura_libre(self, piso: Piso, paso_m: float = 0.25) -> dict:
        """Rejilla de alturas libres del piso (puntos dentro de columnas excluidos) y su resumen."""
        cols = [o for o in self.obstaculos if o.tipo in ("columna", "muro") and o.zmin < piso.z_techo and o.zmax > piso.z_piso]
        nx = max(int(round((piso.xmax - piso.xmin) / paso_m)), 1)
        ny = max(int(round((piso.ymax - piso.ymin) / paso_m)), 1)
        vals = []
        for i in range(nx + 1):
            x = piso.xmin + i * (piso.xmax - piso.xmin) / nx
            for j in range(ny + 1):
                y = piso.ymin + j * (piso.ymax - piso.ymin) / ny
                if any(c.xmin < x < c.xmax and c.ymin < y < c.ymax for c in cols):
                    continue
                vals.append((x, y, self.altura_libre(piso, x, y)))
        hs = sorted(v[2] for v in vals)
        return {"puntos": vals, "minima_m": hs[0], "bajo_losa_m": piso.altura_bajo_losa_m,
                "fraccion_bajo_obstaculo": sum(h < piso.altura_bajo_losa_m - 1e-9 for h in hs) / len(hs)}


def segmento(p0: tuple, p1: tuple, diametro_m: float, id: str = "") -> Caja:
    """Tramo recto de tubería alineado con un eje, como caja con su diámetro exterior."""
    if sum(abs(a - b) > 1e-9 for a, b in zip(p0, p1)) > 1:
        raise ValueError("el tramo debe ser paralelo a un eje (trazado rectilíneo)")
    r = diametro_m / 2
    lo = [min(a, b) for a, b in zip(p0, p1)]
    hi = [max(a, b) for a, b in zip(p0, p1)]
    return Caja(lo[0] - r, lo[1] - r, lo[2] - r, hi[0] + r, hi[1] + r, hi[2] + r, "tuberia", id)


def _acumulado(luces) -> list[float]:
    v = [0.0]
    for l in luces:
        v.append(v[-1] + l)
    return v


def ejes(p) -> tuple[list[float], list[float], list[float]]:
    """Coordenadas de los ejes x, y y de los niveles z de un modelo de pórticos."""
    return _acumulado(p.luces_x_m), _acumulado(p.luces_y_m), _acumulado(p.alturas_piso_m)


def desde_porticos(p, espesor_losa_m: float) -> Edificio:
    """Edificio a partir de un modelo de pórticos con campos luces_x_m, luces_y_m, alturas_piso_m, columnas_mm (lado de la
    columna cuadrada por piso) y vigas_mm ((b, h) por nivel), p. ej. orquestador.ProyectoEdificio3D. El espesor de losa
    es un dato declarado (el modelo de pórticos no lo tiene)."""
    xs, ys, zs = ejes(p)
    obs: list[Caja] = []
    pisos: list[Piso] = []
    for k in range(len(p.alturas_piso_m)):
        c = p.columnas_mm[k] / 1000
        b, hv = (v / 1000 for v in p.vigas_mm[k])
        if hv < espesor_losa_m:
            raise ValueError("la altura total de la viga debe ser ≥ el espesor de la losa")
        z0, z1 = zs[k], zs[k + 1]
        pisos.append(Piso(k, z0, z1 - espesor_losa_m, xs[0] - c / 2, ys[0] - c / 2, xs[-1] + c / 2, ys[-1] + c / 2))
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                obs.append(Caja(x - c / 2, y - c / 2, z0, x + c / 2, y + c / 2, z1 - hv, "columna", f"C{k}-{i}-{j}"))
        for j, y in enumerate(ys):                                   # vigas en dirección x
            for i in range(len(xs) - 1):
                obs.append(Caja(xs[i], y - b / 2, z1 - hv, xs[i + 1], y + b / 2, z1, "viga", f"VX{k}-{i}-{j}"))
        for i, x in enumerate(xs):                                   # vigas en dirección y
            for j in range(len(ys) - 1):
                obs.append(Caja(x - b / 2, ys[j], z1 - hv, x + b / 2, ys[j + 1], z1, "viga", f"VY{k}-{i}-{j}"))
        obs.append(Caja(xs[0] - c / 2, ys[0] - c / 2, z1 - espesor_losa_m, xs[-1] + c / 2, ys[-1] + c / 2, z1, "losa", f"L{k}"))
    return Edificio(pisos, obs)
