"""Optimización de diámetros comerciales (#336 F6), con el tanque subterráneo y la bomba en el problema.

Problema: asignar a cada tramo un diámetro del catálogo declarado para minimizar
    costo = Σ L_tramo · c(d)  +  costo_tanque_m3 · V_requerido
sujeto a:
    v ≤ v_max en todo tramo;
    P ≥ P_req en todo rociador que opera (lo garantiza F5 al fijar el gobernante);
    V_requerido = (Q_rociadores + Q_mangueras) · duración ≤ V_útil del tanque, si el tanque existe;
    P_bomba = P_alim + γ·(z_alim − z_agua_mín) + pérdidas de succión ≤ P_bomba_máx, si se declara;
    (opcional) diámetros que no crecen aguas abajo (telescópico).
Por qué importan los diámetros para el tanque: con la presión justa en el rociador gobernante, los demás quedan por
encima y descargan de más. Una red estrecha desbalancea más, sube el caudal total y con él el volumen del tanque. El
optimizador ve ese costo cuando se declara el costo por m³ de tanque, o la restricción cuando el tanque ya existe.

Método:
  1. Construcción voraz: todo en el diámetro mayor. Luego, mientras se pueda, se reduce un paso el tramo que más
     ahorra sin volverse infactible.
  2. Recocido simulado (semilla fija, reproducible): mueve un tramo un paso arriba o abajo (y repara la regla
     telescópica), con penalización por violaciones. Guarda la mejor solución factible.
  El informe trae las dos soluciones (voraz y recocido) para que se vea cuánto aporta la metaheurística.
  Ninguna de las dos garantiza el óptimo global. Las pruebas lo comparan con búsqueda exhaustiva en redes pequeñas.

Ningún valor normativo vive aquí. Catálogo y costos (p. ej. de apu_precios_referencia), v_max, duración, niveles del
tanque, pérdidas de succión y límites de la bomba son datos del proyecto con su fuente. El optimizador NO aprueba el
diseño: entrega una propuesta que el ingeniero revisa.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional

from . import hidraulica as h


@dataclass(frozen=True)
class Opcion:
    tuberia: h.Tuberia
    costo_m: float                      # COP/m (o la moneda declarada), instalado según el APU que se use


@dataclass(frozen=True)
class Tanque:
    duracion_min: float                 # duración exigida del suministro (de la norma aplicable)
    z_agua_min_m: float                 # cota del nivel mínimo útil de agua (negativa si el tanque es subterráneo)
    volumen_util_m3: Optional[float]    # tanque existente; None si se va a dimensionar
    costo_m3: float                     # costo por m³ de tanque, para dimensionarlo; 0 si no entra en el objetivo
    perdidas_succion_kpa: float         # pérdidas en la succión de la bomba (declaradas o calculadas aparte)
    fuente: str

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente de los datos del tanque")
        if self.duracion_min <= 0 or self.costo_m3 < 0 or self.perdidas_succion_kpa < 0 or \
                (self.volumen_util_m3 is not None and self.volumen_util_m3 <= 0):
            raise ValueError(f"tanque incoherente: {self}")


@dataclass(frozen=True)
class Restricciones:
    v_max_m_s: float
    p_bomba_max_kpa: Optional[float]    # presión máxima que entrega la bomba elegida; None si no se limita
    telescopico: bool                   # diámetros que no crecen aguas abajo
    fuente: str

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente de las restricciones")
        if self.v_max_m_s <= 0:
            raise ValueError("v_max debe ser positiva")


@dataclass
class Evaluacion:
    asignacion: tuple                   # índice de catálogo por tramo (en el orden de `tramos` orientados)
    costo_tuberia: float
    volumen_m3: float
    costo_tanque: float
    p_alimentacion_kpa: float
    p_bomba_kpa: float
    v_max_m_s: float
    violaciones: list

    @property
    def costo(self) -> float:
        return self.costo_tuberia + self.costo_tanque

    @property
    def factible(self) -> bool:
        return not self.violaciones


@dataclass
class Solucion:
    voraz: Optional[Evaluacion]
    mejor: Optional[Evaluacion]
    tramos: list                        # [(a, b)] orientados desde la alimentación
    catalogo: list
    evaluaciones: int
    motivo: str = ""

    def tuberias(self, ev: Optional[Evaluacion] = None) -> dict:
        ev = ev or self.mejor
        return {frozenset(t): self.catalogo[i].tuberia for t, i in zip(self.tramos, ev.asignacion)}


class _Problema:
    def __init__(self, tramos, alimentacion, operan, demanda, catalogo, long_eq, tanque, restr):
        self.cat = sorted(catalogo, key=lambda o: o.tuberia.d_int_m)
        if len({o.tuberia.dn for o in self.cat}) != len(self.cat):
            raise ValueError("diámetros nominales repetidos en el catálogo")
        self.alim, self.operan, self.dem, self.le, self.tq, self.rs = alimentacion, operan, demanda, long_eq, tanque, restr
        orden, _ = h._orientar(tramos, alimentacion)
        self.tramos = orden
        self.largos = [math.dist(a, b) for a, b in orden]
        idx = {b: k for k, (a, b) in enumerate(orden)}
        self.padre = [idx.get(a) for a, b in orden]          # tramo aguas arriba de cada tramo (None si sale de la raíz)
        self.hijos = [[k for k, p in enumerate(self.padre) if p == j] for j in range(len(orden))]
        self.cache: dict = {}

    def evaluar(self, asig: tuple) -> Evaluacion:
        if asig in self.cache:
            return self.cache[asig]
        tubs = {frozenset(t): self.cat[i].tuberia for t, i in zip(self.tramos, asig)}
        viol = []
        try:
            res = h.calcular(self.tramos, self.alim, self.operan, self.dem, tubs, self.le)
        except (RuntimeError, np_error()) as e:                # sin solución hidráulica (presiones absurdas, etc.)
            ev = Evaluacion(asig, math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, [f"hidráulica: {e}"])
            self.cache[asig] = ev
            return ev
        c_tub = sum(L * self.cat[i].costo_m for L, i in zip(self.largos, asig))
        vol = res.q_total_lpm * self.tq.duracion_min / 1000.0
        p_bomba = res.p_alimentacion_kpa + h.GAMMA_AGUA_KPA_M * (self.alim[2] - self.tq.z_agua_min_m) + self.tq.perdidas_succion_kpa
        exceso_v = sum(max(0.0, t.v_m_s - self.rs.v_max_m_s) for t in res.tramos)
        if exceso_v > 1e-9:
            viol.append(("velocidad", exceso_v / self.rs.v_max_m_s))
        if self.tq.volumen_util_m3 is not None and vol > self.tq.volumen_util_m3 + 1e-9:
            viol.append(("tanque", (vol - self.tq.volumen_util_m3) / self.tq.volumen_util_m3))
        if self.rs.p_bomba_max_kpa is not None and p_bomba > self.rs.p_bomba_max_kpa + 1e-9:
            viol.append(("bomba", (p_bomba - self.rs.p_bomba_max_kpa) / self.rs.p_bomba_max_kpa))
        if self.rs.telescopico and any(p is not None and asig[k] > asig[p] for k, p in enumerate(self.padre)):
            viol.append(("telescópico", 1.0))
        ev = Evaluacion(asig, c_tub, vol, self.tq.costo_m3 * vol, res.p_alimentacion_kpa, p_bomba, res.v_max_m_s, viol)
        self.cache[asig] = ev
        return ev

    def reparar(self, asig: list, k: int) -> list:
        """Tras mover el tramo k, ajusta los vecinos para mantener la regla telescópica (si aplica)."""
        if not self.rs.telescopico:
            return asig
        pila = [k]
        while pila:                                          # hacia aguas abajo: los hijos no pueden ser mayores
            j = pila.pop()
            for c in self.hijos[j]:
                if asig[c] > asig[j]:
                    asig[c] = asig[j]
                    pila.append(c)
        j = k
        while self.padre[j] is not None:                     # hacia aguas arriba: el padre no puede ser menor
            p = self.padre[j]
            if asig[p] < asig[j]:
                asig[p] = asig[j]
            j = p
        return asig


def np_error():
    import numpy as np
    return np.linalg.LinAlgError


def _penalizado(ev: Evaluacion, escala: float) -> float:
    if math.isinf(ev.costo):
        return math.inf
    return ev.costo + escala * sum(10.0 * (1.0 + v) for _, v in ev.violaciones)


def optimizar(tramos: list, alimentacion: tuple, operan: list, demanda: h.Demanda, catalogo: list,
              long_equivalente: dict, tanque: Tanque, restricciones: Restricciones,
              iteraciones: int = 2000, semilla: int = 336) -> Solucion:
    pb = _Problema(tramos, alimentacion, operan, demanda, catalogo, long_equivalente, tanque, restricciones)
    n, top = len(pb.tramos), len(pb.cat) - 1
    sol = Solucion(None, None, pb.tramos, pb.cat, 0)

    # 1. Voraz: desde el mayor diámetro, reducir mientras sea factible y ahorre.
    asig = [top] * n
    ev = pb.evaluar(tuple(asig))
    if not ev.factible:
        sol.evaluaciones = len(pb.cache)
        sol.motivo = f"infactible aun con el diámetro mayor del catálogo: {ev.violaciones}"
        return sol
    while True:
        mejor_mov = None
        for k in range(n):
            if asig[k] == 0:
                continue
            cand = pb.reparar(asig[:k] + [asig[k] - 1] + asig[k + 1:], k)
            e = pb.evaluar(tuple(cand))
            if e.factible and e.costo < ev.costo - 1e-9 and (mejor_mov is None or e.costo < mejor_mov[1].costo):
                mejor_mov = (cand, e)
        if mejor_mov is None:
            break
        asig, ev = mejor_mov
    sol.voraz = ev
    mejor = ev

    # 2. Recocido simulado desde la solución voraz.
    rng = random.Random(semilla)
    escala = max(ev.costo, 1.0)
    actual, e_act = list(asig), ev
    t0 = 0.05 * escala
    for it in range(iteraciones):
        T = t0 * (1 - it / iteraciones) + 1e-9
        k = rng.randrange(n)
        d = rng.choice((-1, 1))
        if not 0 <= actual[k] + d <= top:
            continue
        cand = pb.reparar(actual[:k] + [actual[k] + d] + actual[k + 1:], k)
        e = pb.evaluar(tuple(cand))
        delta = _penalizado(e, escala) - _penalizado(e_act, escala)
        if delta <= 0 or (not math.isinf(delta) and rng.random() < math.exp(-delta / T)):
            actual, e_act = cand, e
            if e.factible and e.costo < mejor.costo - 1e-9:
                mejor = e
    sol.mejor = mejor
    sol.evaluaciones = len(pb.cache)
    return sol


def exhaustivo(tramos, alimentacion, operan, demanda, catalogo, long_equivalente, tanque, restricciones):
    """Óptimo por enumeración completa (solo para redes pequeñas: |catálogo|^n evaluaciones). Sirve de referencia."""
    import itertools
    pb = _Problema(tramos, alimentacion, operan, demanda, catalogo, long_equivalente, tanque, restricciones)
    mejor = None
    for asig in itertools.product(range(len(pb.cat)), repeat=len(pb.tramos)):
        e = pb.evaluar(asig)
        if e.factible and (mejor is None or e.costo < mejor.costo):
            mejor = e
    return mejor
