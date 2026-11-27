"""Cantidades de obra, presupuesto por APU y costo por m² (#336 F9).

1. Cantidades: salen del diseño (F3–F8). Son metros de tubería por diámetro, codos y tees por diámetro (detectados
   en F5), rociadores, riostras, colgadores y anclajes (F8), bombas (F7), volumen del tanque (F7) y área del cuarto
   (F7). Las partidas que el motor no diseña (gabinetes, siamesa, válvulas, extintores...) entran como cantidades
   declaradas.
2. Precios: un dict {clave: PrecioItem} con precio mínimo, más probable y máximo por unidad, y su fuente. Una
   partida sin precio NO se estima: se lista como "sin precio" y el total se declara PARCIAL, con su cobertura.
   Si la unidad del precio no coincide con la de la cantidad, el cálculo se detiene con error.
3. Monte Carlo con semilla fija. El precio y la cantidad de cada partida siguen distribuciones triangulares
   declaradas (la de la cantidad cubre el desperdicio y la incertidumbre del metrado). Se informan p05, p50 y p95
   del total y por m² con partidas independientes. También se informa la cota "todo correlacionado" (todas las
   partidas en el mismo percentil), porque la independencia subestima la dispersión cuando los precios se mueven
   juntos (inflación, TRM del acero).
4. Modelo fijo + variable: C = a0 + a1·(Q·H) + c1·A + c2·N_pisos + c3·N_gabinetes. Se ajusta por mínimos cuadrados
   sobre varios diseños y se informan R² y el error de validación cruzada dejando uno fuera. Si se calibra con
   diseños sintéticos del motor, NO equivale a precios de licitación. Sirve para comparar alternativas y para
   prefactibilidad.
Los precios de referencia reales (bases comerciales o de terceros) no se versionan: entran como datos en tiempo de
ejecución.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class Cantidad:
    clave: tuple                  # p. ej. ("tubo", "2in"), ("codo90", "2in"), ("rociador",), ("tanque_m3",)
    unidad: str
    cantidad: float
    origen: str


@dataclass(frozen=True)
class PrecioItem:
    unidad: str
    minimo: float
    moda: float
    maximo: float
    fuente: str

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente del precio")
        if not 0 <= self.minimo <= self.moda <= self.maximo:
            raise ValueError(f"precio incoherente: {self}")


def cantidades(tramos_h: list, n_rociadores: int, soportes: list = (), cuarto=None, tanque=None,
               anclajes_por_riostra: Optional[int] = None, anclajes_por_colgador: Optional[int] = None,
               declaradas: list = (), topologia: Optional[dict] = None) -> list[Cantidad]:
    """Cantidades a partir de los tramos de F5/F6 (hidraulica.TramoH), los soportes de F8, el cuarto y el tanque de
    F7. Accesorios: si se da `topologia` = {alimentacion, rociadores, longitud_tubo_m}, se cuentan por la red con
    acoples y torneado de extremos (accesorios_red). Si no, se usan los de F5, que omiten las tees de paso y las uniones.
    En el conteo de F5, cada tee lleva el diámetro del ramal que sale (el de su tramo aguas abajo)."""
    acc: dict = defaultdict(float)

    def sumar(clave, unidad, q, origen):
        acc[(clave, unidad, origen)] += q

    for t in tramos_h:
        sumar(("tubo", t.tuberia.dn), "m", t.largo_m, "F5/F6 tramos")
        if topologia is None:
            for a in t.accesorios:
                sumar((a, t.tuberia.dn), "und", 1, "F5 accesorios")
    if topologia is not None:
        for c in accesorios_red(tramos_h, topologia["alimentacion"], topologia["rociadores"],
                                topologia["longitud_tubo_m"]):
            sumar(c.clave, c.unidad, c.cantidad, c.origen)
    sumar(("rociador",), "und", n_rociadores, "F3")
    if soportes:
        if anclajes_por_riostra is None or anclajes_por_colgador is None:
            raise ValueError("declare cuántos anclajes lleva cada riostra y cada colgador")
        nr = sum(s.n_lateral + s.n_longitudinal for s in soportes)
        nc = sum(s.n_colgadores for s in soportes)
        sumar(("riostra",), "und", nr, "F8")
        sumar(("colgador",), "und", nc, "F8")
        sumar(("anclaje",), "und", nr * anclajes_por_riostra + nc * anclajes_por_colgador, "F8")
    if cuarto is not None:
        sumar(("bomba", cuarto.principal.bomba), "und", 1, "F7")
        sumar(("jockey",), "und", 1, "F7")
        sumar(("cuarto_m2",), "m2", cuarto.area_m2, "F7")
    if tanque is not None:
        sumar(("tanque_m3",), "m3", tanque.volumen_bruto_m3, "F7")
    out = [Cantidad(c, u, q, o) for (c, u, o), q in acc.items() if q > 0]
    return out + list(declaradas)


def accesorios_red(tramos_h: list, alimentacion: tuple, rociadores: list, longitud_tubo_m: float) -> list[Cantidad]:
    """Accesorios y uniones contados por la topología de la red: lo que se compra e instala, no solo lo que suma
    pérdidas en F5 (las tees de paso no tienen longitud equivalente, pero sí se compran).
    Por nodo, según los tramos que llegan:
      - 1 tramo: si es rociador, salida de rociador; si es la alimentación, conexión a la alimentación;
      - 2 tramos: con cambio de dirección, codo; colineales de distinto diámetro, reducción;
      - 3 tramos: te; 4 tramos: cruz (con el diámetro mayor que llega).
      - Un rociador en un nodo de paso (2 o más tramos) suma una salida de rociador.
    Cada extremo de un accesorio lleva un acople del diámetro del tramo que llega. Cada tramo se arma con
    ceil(L / longitud_tubo) tubos: lleva acoples intermedios entre ellos, y cada tubo tiene 2 extremos que se preparan
    en el torno (ranurado o roscado). La longitud comercial del tubo es un dato declarado."""
    if longitud_tubo_m <= 0:
        raise ValueError("declare la longitud comercial del tubo")
    ady: dict = {}
    for t in tramos_h:
        for n, otro in ((t.a, t.b), (t.b, t.a)):
            ady.setdefault(n, []).append((otro, t.tuberia))
    roc = set(rociadores)
    acc: dict = defaultdict(int)

    def sumar(clave, q=1):
        acc[clave] += q

    def d_(a, b):
        return tuple((bi > ai) - (bi < ai) for ai, bi in zip(a, b))

    for n, vec in ady.items():
        grado = len(vec)
        dn_mayor = max(vec, key=lambda v: v[1].d_int_m)[1].dn
        pieza = None
        if grado == 1:
            if n == alimentacion:
                pieza = ("conexion_alimentacion", dn_mayor)
            elif n in roc:
                pieza = ("salida_rociador", dn_mayor)
        elif grado == 2:
            (o1, t1), (o2, t2) = vec
            if d_(n, o1) != tuple(-x for x in d_(n, o2)):
                pieza = ("codo90", dn_mayor)
            elif t1.dn != t2.dn:
                pieza = ("reduccion", f"{t1.dn}x{t2.dn}" if t1.d_int_m >= t2.d_int_m else f"{t2.dn}x{t1.dn}")
        elif grado == 3:
            pieza = ("te", dn_mayor)
        else:
            pieza = ("cruz", dn_mayor)
        if pieza:
            sumar(pieza)
            for _, tub in vec:
                sumar(("acople", tub.dn))
        if grado >= 2 and n in roc:
            sumar(("salida_rociador", dn_mayor))
    for t in tramos_h:
        piezas = max(1, math.ceil(t.largo_m / longitud_tubo_m - 1e-9))
        if piezas > 1:
            sumar(("acople", t.tuberia.dn), piezas - 1)
        sumar(("torneado_extremo", t.tuberia.dn), 2 * piezas)
    return [Cantidad(k, "und", q, "topología de la red") for k, q in sorted(acc.items())]


def _tri(rng: random.Random, lo: float, moda: float, hi: float) -> float:
    return lo if hi == lo else rng.triangular(lo, hi, moda)


def _tri_ppf(p: float, lo: float, moda: float, hi: float) -> float:
    """Percentil p de la triangular (para la cota correlacionada)."""
    if hi == lo:
        return lo
    f = (moda - lo) / (hi - lo)
    if p < f:
        return lo + math.sqrt(p * (hi - lo) * (moda - lo))
    return hi - math.sqrt((1 - p) * (hi - lo) * (hi - moda))


@dataclass
class Linea:
    cantidad: Cantidad
    precio: Optional[PrecioItem]
    subtotal_moda: float


@dataclass
class Presupuesto:
    lineas: list
    sin_precio: list
    area_m2: float
    total_moda: float
    p05: float
    p50: float
    p95: float
    correlacionado_p05: float
    correlacionado_p95: float
    n_muestras: int

    @property
    def parcial(self) -> bool:
        return bool(self.sin_precio)

    @property
    def cobertura_partidas(self) -> float:
        n = len(self.lineas) + len(self.sin_precio)
        return len(self.lineas) / n if n else 1.0

    def por_m2(self) -> dict:
        return {k: getattr(self, k) / self.area_m2 for k in ("total_moda", "p05", "p50", "p95",
                                                             "correlacionado_p05", "correlacionado_p95")}

    def participacion(self) -> list:
        return sorted(((l.cantidad.clave, l.subtotal_moda / self.total_moda) for l in self.lineas),
                      key=lambda x: -x[1])


def presupuestar(cants: list, precios: dict, area_m2: float, incert_cantidad: dict,
                 n: int = 10000, semilla: int = 336) -> Presupuesto:
    """incert_cantidad: {clave[0]: (mín, moda, máx)} factor multiplicador de la cantidad (p. ej. desperdicio). Toda
    familia con precio necesita su entrada (declarar (1, 1, 1) si no hay incertidumbre)."""
    if area_m2 <= 0:
        raise ValueError("área protegida debe ser positiva")
    lineas, sin = [], []
    for c in cants:
        p = precios.get(c.clave)
        if p is None:
            sin.append(c)
            continue
        if p.unidad != c.unidad:
            raise ValueError(f"unidad del precio ({p.unidad}) distinta de la cantidad ({c.unidad}) en {c.clave}")
        if c.clave[0] not in incert_cantidad:
            raise ValueError(f"declare la incertidumbre de cantidad de la familia {c.clave[0]}")
        f = incert_cantidad[c.clave[0]]
        lineas.append(Linea(c, p, c.cantidad * f[1] * p.moda))
    rng = random.Random(semilla)
    tot = np.zeros(n)
    for k in range(n):
        tot[k] = sum(l.cantidad.cantidad * _tri(rng, *incert_cantidad[l.cantidad.clave[0]])
                     * _tri(rng, l.precio.minimo, l.precio.moda, l.precio.maximo) for l in lineas)
    p05, p50, p95 = (float(np.percentile(tot, q)) for q in (5, 50, 95))

    def corr(pc):
        return sum(l.cantidad.cantidad * _tri_ppf(pc, *incert_cantidad[l.cantidad.clave[0]])
                   * _tri_ppf(pc, l.precio.minimo, l.precio.moda, l.precio.maximo) for l in lineas)

    return Presupuesto(lineas, sin, area_m2, sum(l.subtotal_moda for l in lineas), p05, p50, p95,
                       corr(0.05), corr(0.95), n)


@dataclass
class ModeloCosto:
    coef: dict                     # a0, a1_QH, c1_area, c2_pisos, c3_gabinetes
    r2: float
    error_loo_rel: float           # error relativo medio de validación cruzada dejando uno fuera
    n: int

    def predecir(self, area_m2: float, pisos: int, gabinetes: int, q_lpm: float, p_kpa: float) -> float:
        c = self.coef
        return (c["a0"] + c["a1_QH"] * q_lpm * p_kpa + c["c1_area"] * area_m2 + c["c2_pisos"] * pisos
                + c["c3_gabinetes"] * gabinetes)


_NOMBRES = ("a0", "a1_QH", "c1_area", "c2_pisos", "c3_gabinetes")


def _matriz(m: list) -> np.ndarray:
    return np.array([[1.0, d["q_lpm"] * d["p_kpa"], d["area_m2"], d["pisos"], d["gabinetes"]] for d in m])


def ajustar_modelo(muestras: list) -> ModeloCosto:
    """muestras: [{costo, area_m2, pisos, gabinetes, q_lpm, p_kpa}]. Exige al menos 2 muestras más que parámetros."""
    if len(muestras) < len(_NOMBRES) + 2:
        raise ValueError(f"se necesitan al menos {len(_NOMBRES) + 2} diseños para ajustar {len(_NOMBRES)} parámetros")
    X, y = _matriz(muestras), np.array([d["costo"] for d in muestras])
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError("las muestras no varían lo suficiente (matriz de rango incompleto)")
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ beta
    r2 = 1 - float(np.sum((y - pred) ** 2)) / float(np.sum((y - y.mean()) ** 2))
    errs = []
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        b, *_ = np.linalg.lstsq(X[m], y[m], rcond=None)
        errs.append(abs(float(X[i] @ b) - y[i]) / abs(y[i]))
    return ModeloCosto(dict(zip(_NOMBRES, map(float, beta))), r2, float(np.mean(errs)), len(y))
