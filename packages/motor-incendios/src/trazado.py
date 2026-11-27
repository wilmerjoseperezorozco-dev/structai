"""Trazado de tubería (#336 F4): árbol de Steiner rectilíneo en 3D que esquiva obstáculos.

Método:
  1. Rejilla de Hanan extendida. Sus coordenadas son las de los terminales (rociadores y alimentación), los pases de
     losa declarados y las caras de cada obstáculo ensanchadas por (radio del tubo + holgura). Con eso, todo camino
     rectilíneo que esquiva los obstáculos tiene un equivalente de igual longitud sobre la rejilla. Para el árbol de
     Steiner rectilíneo sin obstáculos esto es exacto (Hanan, 1966); con obstáculos es la generalización usual.
  2. Heurística del camino más corto (Takahashi y Matsuyama, 1980). Parte de la alimentación y une, cada vez, el
     terminal más cercano al árbol con Dijkstra. Garantiza un costo ≤ 2·(1 − 1/T) veces el óptimo sobre la rejilla.
  3. Toda arista se revisa contra el mapa de obstáculos de F2, con el diámetro exterior y la holgura declarada. Una
     arista vertical solo atraviesa una losa en los pases declarados.

Ningún valor normativo vive aquí. Diámetro de trazado, holgura, pases y penalización vertical son datos del proyecto.
Lo que v1 NO hace:
  - imponer la topología de ramales y troncales que exige la norma (sale un árbol general);
  - optimizar diámetros (eso es F5/F6: aquí se traza con un diámetro envolvente);
  - las uniones del rociador (sprig, drop): la tubería llega al punto del rociador.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Optional

from .geometria import Edificio, segmento

Punto = tuple  # (x, y, z)
TOL = 1e-7     # m: coordenadas más cercanas que esto son la misma


@dataclass(frozen=True)
class ParametrosTrazado:
    diametro_m: float                    # diámetro exterior envolvente para el trazado
    holgura_m: float                     # holgura libre a obstáculos (declarada por el diseñador)
    pases_losa: tuple = ()               # (x, y) donde una bajante o subida puede atravesar losas
    penalizacion_vertical: float = 1.0   # multiplicador de costo para tramos verticales (preferencia, no norma)

    def __post_init__(self):
        if self.diametro_m <= 0 or self.holgura_m < 0 or self.penalizacion_vertical <= 0:
            raise ValueError(f"parámetros incoherentes: {self}")


@dataclass
class Red:
    aristas: list                        # [(p, q)] con p, q puntos de la rejilla
    terminales: list
    no_conectados: list = field(default_factory=list)

    @property
    def longitud_m(self) -> float:
        return sum(math.dist(p, q) for p, q in self.aristas)

    @property
    def longitud_vertical_m(self) -> float:
        return sum(abs(p[2] - q[2]) for p, q in self.aristas)

    def tramos(self) -> list:
        """Aristas colineales unidas a través de nodos de grado 2 (tramos rectos entre uniones)."""
        ady: dict = {}
        for p, q in self.aristas:
            ady.setdefault(p, []).append(q)
            ady.setdefault(q, []).append(p)
        term = set(self.terminales)

        def dir_(a, b):
            return tuple((bi > ai) - (bi < ai) for ai, bi in zip(a, b))

        vistos = set()
        out = []
        for p, q in self.aristas:
            if (p, q) in vistos:
                continue
            a, b = p, q
            vistos.update({(p, q), (q, p)})
            while len(ady[b]) == 2 and b not in term:          # extender hacia adelante
                nxt = [n for n in ady[b] if n != a][0]
                if dir_(b, nxt) != dir_(a, b):
                    break
                vistos.update({(b, nxt), (nxt, b)})
                a, b = b, nxt
            fin = b
            a, b = q, p
            while len(ady[b]) == 2 and b not in term:          # y hacia atrás
                nxt = [n for n in ady[b] if n != a][0]
                if dir_(b, nxt) != dir_(a, b):
                    break
                vistos.update({(b, nxt), (nxt, b)})
                a, b = b, nxt
            out.append((b, fin))
        return out


class _Rejilla:
    def __init__(self, ed: Edificio, terminales: list, par: ParametrosTrazado):
        self.ed, self.par = ed, par
        m = par.diametro_m / 2 + par.holgura_m + 1e-6
        xs, ys, zs = set(), set(), set()
        for x, y, z in terminales:
            xs.add(x); ys.add(y); zs.add(z)
        for x, y in par.pases_losa:
            xs.add(x); ys.add(y)
        for o in ed.obstaculos:
            xs.update((o.xmin - m, o.xmax + m)); ys.update((o.ymin - m, o.ymax + m)); zs.update((o.zmin - m, o.zmax + m))
        bx = (min(p.xmin for p in ed.pisos), max(p.xmax for p in ed.pisos))
        by = (min(p.ymin for p in ed.pisos), max(p.ymax for p in ed.pisos))
        bz = (min(p.z_piso for p in ed.pisos) + m, max(p.z_techo for p in ed.pisos))
        self.ejes = []
        for s, (lo, hi) in ((xs, bx), (ys, by), (zs, bz)):
            eje: list = []
            for v in sorted(v for v in s if lo - 1e-9 <= v <= hi + 1e-9):
                if not eje or v - eje[-1] > TOL:          # fusiona coordenadas que solo difieren por redondeo
                    eje.append(v)
            self.ejes.append(eje)
        self.pases = {(round(x, 6), round(y, 6)) for x, y in par.pases_losa}
        self._libre: dict = {}

    def punto(self, n) -> Punto:
        return tuple(self.ejes[a][n[a]] for a in range(3))

    def nodo(self, p: Punto):
        try:
            return tuple(next(i for i, v in enumerate(self.ejes[a]) if abs(v - p[a]) <= TOL) for a in range(3))
        except StopIteration:
            return None

    def _arista_libre(self, n1, n2) -> bool:
        k = (n1, n2) if n1 < n2 else (n2, n1)
        if k not in self._libre:
            p, q = self.punto(n1), self.punto(n2)
            ign = ()
            if p[2] != q[2] and (round(p[0], 6), round(p[1], 6)) in self.pases:
                ign = ("losa",)
            s = segmento(p, q, self.par.diametro_m)
            self._libre[k] = not self.ed.colisiones(s, self.par.holgura_m, ignorar=ign)
        return self._libre[k]

    def vecinos(self, n):
        for a in range(3):
            for d in (-1, 1):
                i = n[a] + d
                if 0 <= i < len(self.ejes[a]):
                    v = list(n); v[a] = i; v = tuple(v)
                    if self._arista_libre(n, v):
                        largo = abs(self.ejes[a][i] - self.ejes[a][n[a]])
                        yield v, largo * (self.par.penalizacion_vertical if a == 2 else 1.0)


def trazar(ed: Edificio, alimentacion: Punto, rociadores: list, par: ParametrosTrazado, raices: int = 20) -> Red:
    """Árbol de Steiner rectilíneo entre la alimentación y los rociadores. Repite la heurística del camino más corto
    desde varias raíces: la alimentación y hasta `raices` terminales repartidos en la lista. El árbol no tiene
    dirección, así que la raíz solo cambia el orden de construcción. Se queda con la red más corta (y, a igual
    longitud, con la de menos terminales sin conectar)."""
    g = _Rejilla(ed, [alimentacion, *rociadores], par)
    terms = [g.punto(n) if (n := g.nodo(x)) is not None else x for x in (alimentacion, *rociadores)]   # ajuste a la rejilla
    alimentacion, rociadores = terms[0], terms[1:]
    paso = max(1, len(rociadores) // max(raices, 1))
    candidatas = [alimentacion] + rociadores[::paso][:raices]
    mejor = None
    for raiz in candidatas:
        red = _sph(g, ed, raiz, terms, par)
        clave = (len(red.no_conectados), red.longitud_m)
        if mejor is None or clave < mejor[0]:
            mejor = (clave, red)
    return mejor[1]


def _sph(g: "_Rejilla", ed: Edificio, origen: Punto, terms: list, par: ParametrosTrazado) -> Red:
    arbol = {g.nodo(origen)}
    pendientes = {g.nodo(r): r for r in terms if r != origen}
    red = Red([], list(terms))
    for n, r in list(pendientes.items()):
        if n is None or ed.colisiones(segmento(r, r, par.diametro_m), par.holgura_m):
            red.no_conectados.append(r)
            pendientes.pop(n, None)
    while pendientes:
        dist = {n: 0.0 for n in arbol}
        prev: dict = {}
        cola = [(0.0, n) for n in arbol]
        heapq.heapify(cola)
        llegado = None
        while cola:
            d, n = heapq.heappop(cola)
            if d > dist.get(n, math.inf):
                continue
            if n in pendientes:
                llegado = n
                break
            for v, w in g.vecinos(n):
                if d + w < dist.get(v, math.inf) - 1e-12:
                    dist[v], prev[v] = d + w, n
                    heapq.heappush(cola, (d + w, v))
        if llegado is None:                         # los que quedan no tienen camino libre
            red.no_conectados.extend(pendientes.values())
            break
        n = llegado
        while n not in arbol:
            red.aristas.append((g.punto(prev[n]), g.punto(n)))
            arbol.add(n)
            n = prev[n]
        pendientes.pop(llegado)
    return red


def verificar_red(ed: Edificio, red: Red, par: ParametrosTrazado) -> list[str]:
    """Revisión independiente: rectilínea, sin colisiones (salvo pases), es árbol y conecta todos los terminales."""
    errores = []
    pases = {(round(x, 6), round(y, 6)) for x, y in par.pases_losa}
    for p, q in red.aristas:
        try:
            s = segmento(p, q, par.diametro_m)
        except ValueError:
            errores.append(f"arista no rectilínea {p}–{q}")
            continue
        ign = ("losa",) if p[2] != q[2] and (round(p[0], 6), round(p[1], 6)) in pases else ()
        for o in ed.colisiones(s, par.holgura_m, ignorar=ign):
            errores.append(f"tramo {p}–{q} choca con {o.tipo} {o.id}")
    nodos = {n for a in red.aristas for n in a}
    if red.aristas and len(red.aristas) != len(nodos) - 1:
        errores.append(f"no es árbol: {len(red.aristas)} aristas para {len(nodos)} nodos")
    padre = {n: n for n in nodos}

    def raiz(n):
        while padre[n] != n:
            padre[n] = padre[padre[n]]
            n = padre[n]
        return n

    for p, q in red.aristas:
        padre[raiz(p)] = raiz(q)
    conectados = [t for t in red.terminales if t not in red.no_conectados]
    if red.aristas and len({raiz(t) if t in padre else ("suelto", t) for t in conectados}) > 1:
        errores.append("hay terminales en componentes separadas")
    return errores
