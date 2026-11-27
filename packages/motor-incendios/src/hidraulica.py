"""Cálculo hidráulico de la red de rociadores (#336 F5).

Física (no normativa):
  - Hazen-Williams en SI: h_f [m] = 10,67 · L · Q^1,852 / (C^1,852 · d^4,8704), con Q en m³/s y d interior en m.
  - Presión estática: ΔP = γ · Δz, con γ = 9,81 kPa/m (agua; dato declarable).
  - Rociador: Q = K · √P, con K en L/(min·√bar) y P en bar. Internamente P está en kPa (1 bar = 100 kPa).
Datos del proyecto, sin valores por defecto:
  - K, presión mínima y caudal mínimo por rociador (de la densidad × área de cobertura de la norma aplicable);
  - C y diámetro interior de cada tubería;
  - longitudes equivalentes de accesorios por (tipo, diámetro nominal);
  - caudal de mangueras que se suma en la alimentación;
  - qué rociadores operan (el área de diseño que eligió el diseñador).

Método: la red de F4 es un árbol, así que el caudal de cada tramo es la suma exacta de lo que descargan los rociadores
aguas abajo. Las descargas dependen de la presión, y se resuelven con iteración de punto fijo amortiguada: presiones,
luego caudales de rociador, luego caudales de tramo y de nuevo presiones desde la alimentación. Encima, una bisección
sobre la presión de alimentación hace que el rociador más exigido quede justo en su requisito
max(P_min, (q_min/K)²); los demás quedan por encima.
Accesorios: un cambio de dirección en un nodo de paso es un "codo90". Un ramal que sale girando de un nodo con 3 o
más tramos es una "te_lateral". El tramo recto que atraviesa una te no suma longitud equivalente. La longitud
equivalente se suma al tramo aguas abajo, con su diámetro.
Lo que v1 NO hace: seleccionar automáticamente el área de diseño más remota, redes en anillo o malla, ni el
equilibrio por ramales con factor K equivalente (no hace falta: la solución es exacta sobre el árbol).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Union

GAMMA_AGUA_KPA_M = 9.81


@dataclass(frozen=True)
class Tuberia:
    dn: str                     # designación nominal (p. ej. "1in", "DN25"), clave de la tabla de accesorios
    d_int_m: float
    c_hw: float                 # coeficiente de Hazen-Williams declarado

    def __post_init__(self):
        if self.d_int_m <= 0 or self.c_hw <= 0:
            raise ValueError(f"tubería incoherente: {self}")


@dataclass(frozen=True)
class Demanda:
    k_lpm_bar05: float          # factor K del rociador, L/(min·√bar)
    p_min_kpa: float            # presión mínima en el rociador
    q_min_lpm: float            # caudal mínimo por rociador (densidad × área de cobertura); 0 si no aplica
    q_mangueras_lpm: float      # caudal de mangueras sumado en la alimentación
    fuente: str

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente de la demanda (norma, edición, numeral)")
        if self.k_lpm_bar05 <= 0 or self.p_min_kpa <= 0 or self.q_min_lpm < 0 or self.q_mangueras_lpm < 0:
            raise ValueError(f"demanda incoherente: {self}")

    @property
    def p_requerida_kpa(self) -> float:
        return max(self.p_min_kpa, 100.0 * (self.q_min_lpm / self.k_lpm_bar05) ** 2)

    def caudal_lpm(self, p_kpa: float) -> float:
        return self.k_lpm_bar05 * math.sqrt(max(p_kpa, 0.0) / 100.0)


def perdida_hw_kpa(q_lpm: float, d_m: float, c: float, largo_m: float, gamma: float = GAMMA_AGUA_KPA_M) -> float:
    q = abs(q_lpm) / 60000.0
    return gamma * 10.67 * largo_m * q ** 1.852 / (c ** 1.852 * d_m ** 4.8704)


@dataclass
class TramoH:
    a: tuple                    # nodo aguas arriba
    b: tuple                    # nodo aguas abajo
    tuberia: Tuberia
    largo_m: float
    accesorios: list = field(default_factory=list)
    largo_eq_m: float = 0.0
    q_lpm: float = 0.0
    v_m_s: float = 0.0
    dp_friccion_kpa: float = 0.0


@dataclass
class Resultado:
    p_alimentacion_kpa: float
    q_rociadores_lpm: float
    q_total_lpm: float                  # con mangueras
    rociadores: list                    # [(punto, P kPa, Q L/min)]
    tramos: list                        # [TramoH]
    gobernante: tuple
    iteraciones: int

    @property
    def v_max_m_s(self) -> float:
        return max(t.v_m_s for t in self.tramos)


def _resolver_lineal(A: list, b: list) -> list:
    """Eliminación de Gauss con pivoteo parcial (sistemas pequeños; sin dependencias)."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-300:
            raise RuntimeError("jacobiano singular")
        M[c], M[piv] = M[piv], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            if f:
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (M[r][n] - sum(M[r][k] * x[k] for k in range(r + 1, n))) / M[r][r]
    return x


def _dir(a, b):
    return tuple((bi > ai) - (bi < ai) for ai, bi in zip(a, b))


def _orientar(tramos: list, raiz: tuple) -> tuple[list, dict]:
    """Ordena los tramos desde la raíz (BFS): devuelve [(a, b)] con a aguas arriba y el padre de cada nodo."""
    ady: dict = {}
    for p, q in tramos:
        ady.setdefault(p, []).append(q)
        ady.setdefault(q, []).append(p)
    if raiz not in ady:
        raise ValueError("la alimentación no está en la red")
    orden, padre, cola = [], {raiz: None}, [raiz]
    while cola:
        n = cola.pop(0)
        for v in ady[n]:
            if v not in padre:
                padre[v] = n
                orden.append((n, v))
                cola.append(v)
    if len(orden) != len(tramos):
        raise ValueError("la red no es un árbol conexo desde la alimentación")
    return orden, ady


def calcular(tramos: list, alimentacion: tuple, operan: list, demanda: Demanda,
             tuberias: Union[Tuberia, dict], long_equivalente: dict,
             gamma: float = GAMMA_AGUA_KPA_M, tol_kpa: float = 1e-6, max_iter: int = 100) -> Resultado:
    """tramos: [(p, q)] de Red.tramos(). operan: rociadores del área de diseño (puntos que son nodos de la red).
    tuberias: una Tuberia para toda la red o un dict {frozenset((p, q)): Tuberia}.
    long_equivalente: {(tipo, dn): m}, con tipo "codo90" o "te_lateral"; si falta una entrada que se necesita, error."""
    orden, ady = _orientar(tramos, alimentacion)
    padre = {b: a for a, b in orden}
    ops = set(operan)
    faltan = [p for p in ops if p not in padre]
    if faltan:
        raise ValueError(f"rociadores que no son nodos de la red: {faltan[:3]}")
    th: list[TramoH] = []
    for a, b in orden:
        tub = tuberias if isinstance(tuberias, Tuberia) else tuberias[frozenset((a, b))]
        t = TramoH(a, b, tub, math.dist(a, b))
        pa = padre.get(a)
        if pa is not None and _dir(pa, a) != _dir(a, b):
            t.accesorios.append("codo90" if len(ady[a]) == 2 else "te_lateral")
        for acc in t.accesorios:
            if (acc, tub.dn) not in long_equivalente:
                raise ValueError(f"falta la longitud equivalente de {acc} en {tub.dn}")
            t.largo_eq_m += long_equivalente[(acc, tub.dn)]
        th.append(t)
    hijos: dict = {}
    for t in th:
        hijos.setdefault(t.a, []).append(t)

    lista_ops = list(dict.fromkeys(operan))
    idx_tramo = {t.b: k for k, t in enumerate(th)}             # tramo que llega a cada nodo
    caminos = []
    for n in lista_ops:                                         # tramos entre la alimentación y cada rociador
        c, x = [], n
        while x != alimentacion:
            c.append(idx_tramo[x])
            x = th[idx_tramo[x]].a
        caminos.append(set(c))
    comun = [[sorted(ci & cj) for cj in caminos] for ci in caminos]

    def bajar(p0: float, q_roc: dict) -> dict:
        q_sal = {n: q_roc.get(n, 0.0) for n in ady}
        for t in reversed(th):                                 # caudales: de las hojas hacia la raíz (exacto en árbol)
            t.q_lpm = q_sal[t.b] + sum(x.q_lpm for x in hijos.get(t.b, ()))
        p = {alimentacion: p0}
        for t in th:                                           # presiones: de la raíz hacia las hojas
            t.dp_friccion_kpa = perdida_hw_kpa(t.q_lpm, t.tuberia.d_int_m, t.tuberia.c_hw, t.largo_m + t.largo_eq_m, gamma)
            p[t.b] = p[t.a] - t.dp_friccion_kpa - gamma * (t.b[2] - t.a[2])
        return p

    def resolver(p0: float):
        """Newton sobre las presiones de los rociadores que operan: F(P) = P − P'(P) = 0."""
        P = [p0] * len(lista_ops)

        def residuo(P):
            p = bajar(p0, {n: demanda.caudal_lpm(Pi) for n, Pi in zip(lista_ops, P)})
            return [Pi - p[n] for n, Pi in zip(lista_ops, P)], p

        F, p = residuo(P)
        m = len(P)
        for it in range(1, max_iter + 1):
            nF = max(abs(f) for f in F)
            if nF < tol_kpa:
                return p, it
            dh = [1.852 * t.dp_friccion_kpa / t.q_lpm if t.q_lpm > 0 else 0.0 for t in th]
            dq = [demanda.k_lpm_bar05 / (200.0 * math.sqrt(max(Pj, 1e-9) / 100.0)) if Pj > 0 else 0.0 for Pj in P]
            J = [[(1.0 if i == j else 0.0) + sum(dh[k] for k in comun[i][j]) * dq[j] for j in range(m)] for i in range(m)]
            paso = _resolver_lineal(J, [-f for f in F])
            a = 1.0
            while True:                                        # búsqueda lineal: el residuo debe bajar
                Pn = [Pi + a * s for Pi, s in zip(P, paso)]
                Fn, pn = residuo(Pn)
                if max(abs(f) for f in Fn) < nF or a < 1e-6:
                    break
                a *= 0.5
            P, F, p = Pn, Fn, pn
        raise RuntimeError(f"el cálculo hidráulico no convergió en {max_iter} iteraciones")

    preq = demanda.p_requerida_kpa

    def holgura(p0):
        p, it = resolver(p0)
        return min(p[n] for n in ops) - preq, p, it

    lo, hi = preq, 2 * preq
    while holgura(hi)[0] < 0:
        lo, hi = hi, 2 * hi
        if hi > 1e6:
            raise RuntimeError("no hay presión de alimentación razonable que cumpla la demanda")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if holgura(mid)[0] < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol_kpa:
            break
    _, p, it = holgura(hi)
    for t in th:
        t.v_m_s = (t.q_lpm / 60000.0) / (math.pi * t.tuberia.d_int_m ** 2 / 4)
    roc = [(n, p[n], demanda.caudal_lpm(p[n])) for n in operan]
    q_roc = sum(r[2] for r in roc)
    gob = min(roc, key=lambda r: r[1])[0]
    return Resultado(hi, q_roc, q_roc + demanda.q_mangueras_lpm, roc, th, gob, it)


def verificar(res: Resultado, demanda: Demanda, v_max_m_s: Optional[float] = None, tol: float = 1e-3) -> list[str]:
    """Revisión independiente: requisito en cada rociador, balance de caudal en cada nodo, energía tramo a tramo y,
    si se declara, la velocidad máxima."""
    err = []
    pres = {n: P for n, P, _ in res.rociadores}
    for n, P, Q in res.rociadores:
        if P < demanda.p_requerida_kpa - tol:
            err.append(f"rociador {n}: {P:.2f} kPa < requerida {demanda.p_requerida_kpa:.2f}")
    sale: dict = {}
    entra: dict = {}
    for t in res.tramos:
        sale[t.a] = sale.get(t.a, 0.0) + t.q_lpm
        entra[t.b] = t.q_lpm
    qroc = {n: Q for n, _, Q in res.rociadores}
    for n, qin in entra.items():
        if abs(qin - sale.get(n, 0.0) - qroc.get(n, 0.0)) > tol:
            err.append(f"balance de caudal no cierra en {n}")
    p = {res.tramos[0].a: res.p_alimentacion_kpa}
    for t in res.tramos:
        p[t.b] = p[t.a] - perdida_hw_kpa(t.q_lpm, t.tuberia.d_int_m, t.tuberia.c_hw, t.largo_m + t.largo_eq_m) \
                 - GAMMA_AGUA_KPA_M * (t.b[2] - t.a[2])
    for n, P in pres.items():
        if abs(p[n] - P) > 1e-2:
            err.append(f"energía no cierra en {n}: {p[n]:.3f} vs {P:.3f}")
    if v_max_m_s is not None:
        for t in res.tramos:
            if t.v_m_s > v_max_m_s + 1e-9:
                err.append(f"velocidad {t.v_m_s:.2f} m/s > máxima en {t.a}–{t.b}")
    return err
