"""Solver de redes de tuberías a presión por el método del gradiente (Todini y Pilati, 1988).

Estado permanente, pérdidas de Hazen-Williams en SI: h = r·q·|q|^0.852, r = 10.67·L / (C^1.852 · D^4.871).
Se resuelven simultáneamente caudales por tramo y cargas en nudos libres con Newton-Raphson:

    f1 = F(q) + A12·H + A10·H0 = 0     (energía por tramo; H_desde − H_hasta = h)
    f2 = A12ᵀ·q − d            = 0     (continuidad por nudo libre; entra − sale = demanda)

Cada paso resuelve el sistema reducido (A12ᵀ D⁻¹ A12)·dH = f2 − A12ᵀ D⁻¹ f1 con D = diag(n·r·|q|^0.852).
Si no converge en el máximo de iteraciones se lanza ValueError (nunca se devuelve un resultado a medio converger).
"""
import math
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

N_HW = 1.852
_COEF_HW = 10.67
_Q_MIN = 1e-14           # m³/s, piso del caudal en la derivada para evitar D = 0 (más alto estanca Newton cerca de q = 0)
_TOL_ENERGIA_M = 1e-9
_TOL_CONTINUIDAD = 1e-12
_TOL_Q_REL = 1e-9
_TOL_Q_ABS = 1e-12      # m³/s
_MAX_REDUCCIONES = 12


def _finito(valor: Any, nombre: str) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser un número finito (recibido {valor!r})")
    return float(valor)


_CLAVES_NODO = ("id", "cota_m")
_CLAVES_TRAMO = ("id", "desde", "hasta", "longitud_m", "diametro_m", "c_hw")


def _exigir(elem: Any, claves, tipo: str) -> None:
    if not isinstance(elem, dict):
        raise ValueError(f"cada {tipo} debe ser un diccionario")
    faltan = [c for c in claves if c not in elem]
    if faltan:
        raise ValueError(f"al {tipo} le faltan los campos {faltan}")
    for c in ("id", "desde", "hasta"):
        if c in elem and not isinstance(elem[c], str):
            raise ValueError(f"el campo {c} del {tipo} debe ser texto (recibido {elem[c]!r})")


def _validar(nodos: List[dict], tramos: List[dict]):
    if not nodos:
        raise ValueError("la red necesita al menos un nudo")
    if not tramos:
        raise ValueError("la red necesita al menos un tramo")
    for n in nodos:
        _exigir(n, _CLAVES_NODO, "nudo")
    for t in tramos:
        _exigir(t, _CLAVES_TRAMO, "tramo")
    ids = [n["id"] for n in nodos]
    if len(set(ids)) != len(ids):
        raise ValueError("hay identificadores de nudo duplicados")
    ids_t = [t["id"] for t in tramos]
    if len(set(ids_t)) != len(ids_t):
        raise ValueError("hay identificadores de tramo duplicados")
    for n in nodos:
        _finito(n["cota_m"], f"cota del nudo {n['id']}")
        if _finito(n.get("demanda_m3s", 0.0), f"demanda del nudo {n['id']}") < 0:
            raise ValueError(f"la demanda del nudo {n['id']} no puede ser negativa")
        if n.get("carga_fija_m") is not None:
            _finito(n["carga_fija_m"], f"carga fija del nudo {n['id']}")
            if n.get("demanda_m3s", 0.0) != 0:
                raise ValueError(f"el nudo {n['id']} tiene carga fija y demanda: el caudal de un nudo de carga fija "
                                 "sale de la solución, no es dato (declare la demanda en un nudo libre)")
    conocidos = set(ids)
    for t in tramos:
        for campo in ("longitud_m", "diametro_m", "c_hw"):
            if _finito(t[campo], f"{campo} del tramo {t['id']}") <= 0:
                raise ValueError(f"{campo} del tramo {t['id']} debe ser positivo")
        if t["desde"] not in conocidos or t["hasta"] not in conocidos:
            raise ValueError(f"el tramo {t['id']} referencia un nudo que no existe")
        if t["desde"] == t["hasta"]:
            raise ValueError(f"el tramo {t['id']} conecta un nudo consigo mismo")


def _verificar_conectividad(nodos: List[dict], tramos: List[dict]) -> None:
    fijos = [n["id"] for n in nodos if n.get("carga_fija_m") is not None]
    if not fijos:
        raise ValueError("la red necesita al menos un nudo de carga fija (embalse o tanque)")
    vecinos: Dict[str, List[str]] = {n["id"]: [] for n in nodos}
    for t in tramos:
        vecinos[t["desde"]].append(t["hasta"])
        vecinos[t["hasta"]].append(t["desde"])
    visto, pila = set(fijos), list(fijos)
    while pila:
        for v in vecinos[pila.pop()]:
            if v not in visto:
                visto.add(v)
                pila.append(v)
    huerfanos = sorted(set(vecinos) - visto)
    if huerfanos:
        raise ValueError(f"nudos no conectados a ningún nudo de carga fija: {huerfanos}")


def _residuos(q, r, a12, a10_h0, demanda):
    return r * q * np.abs(q) ** (N_HW - 1.0), a12.T @ q - demanda


def resolver_red(nodos: List[dict], tramos: List[dict], *, max_iteraciones: int = 100) -> Dict[str, Any]:
    """Resuelve cargas y caudales de la red. Nudo: id, cota_m, demanda_m3s, carga_fija_m (None si es libre).
    Tramo: id, desde, hasta, longitud_m, diametro_m, c_hw. Caudal positivo de «desde» hacia «hasta»."""
    if isinstance(max_iteraciones, bool) or not isinstance(max_iteraciones, int) or max_iteraciones < 1:
        raise ValueError("max_iteraciones debe ser un entero positivo")
    _validar(nodos, tramos)
    _verificar_conectividad(nodos, tramos)

    libres = [n for n in nodos if n.get("carga_fija_m") is None]
    fijos = [n for n in nodos if n.get("carga_fija_m") is not None]
    ind_libre = {n["id"]: i for i, n in enumerate(libres)}
    ind_fijo = {n["id"]: i for i, n in enumerate(fijos)}
    n_t, n_l, n_f = len(tramos), len(libres), len(fijos)

    # Incidencia: −1 en «desde», +1 en «hasta»  →  (A·H)_tramo = H_hasta − H_desde = −h
    f12, c12, v12, f10, c10, v10 = [], [], [], [], [], []
    for k, t in enumerate(tramos):
        for nid, signo in ((t["desde"], -1.0), (t["hasta"], 1.0)):
            if nid in ind_libre:
                f12.append(k); c12.append(ind_libre[nid]); v12.append(signo)
            else:
                f10.append(k); c10.append(ind_fijo[nid]); v10.append(signo)
    a12 = sparse.csr_matrix((v12, (f12, c12)), shape=(n_t, n_l))
    a10 = sparse.csr_matrix((v10, (f10, c10)), shape=(n_t, n_f))
    h0 = np.array([n["carga_fija_m"] for n in fijos], dtype=float)
    a10_h0 = a10 @ h0
    demanda = np.array([n.get("demanda_m3s", 0.0) for n in libres], dtype=float)
    r = np.array([_COEF_HW * t["longitud_m"] / (t["c_hw"] ** N_HW * t["diametro_m"] ** 4.871) for t in tramos])
    area = np.array([math.pi * t["diametro_m"] ** 2 / 4.0 for t in tramos])

    q = area * 1.0                                   # arranque: 1 m/s en el sentido declarado
    h_libre = np.zeros(n_l)

    def evaluar(qv, hv):
        h_perd = r * qv * np.abs(qv) ** (N_HW - 1.0)
        f1 = h_perd + a12 @ hv + a10_h0
        f2 = a12.T @ qv - demanda
        return f1, f2

    def merito(f1, f2):
        return float(np.max(np.abs(f1))) + 1e3 * float(np.max(np.abs(f2), initial=0.0))

    f1, f2 = evaluar(q, h_libre)
    pasos = 0
    convergio = False
    for _ in range(max_iteraciones + 1):
        d_diag = N_HW * r * np.maximum(np.abs(q), _Q_MIN) ** (N_HW - 1.0)
        dinv = sparse.diags(1.0 / d_diag)
        matriz = (a12.T @ dinv @ a12).tocsc()
        rhs = f2 - a12.T @ (dinv @ f1)
        dh = np.atleast_1d(spsolve(matriz, rhs)) if n_l else np.zeros(0)
        dq = -(dinv @ (f1 + a12 @ dh))
        if not (np.all(np.isfinite(dh)) and np.all(np.isfinite(dq))):
            raise ValueError("el sistema de la red es singular o mal condicionado (no converge)")
        # Convergencia: residuos pequeños Y paso de Newton despreciable. Solo los residuos no bastan cerca de caudal nulo
        # (un caudal espurio de 1e-2 m³/s puede dar residuo de energía < 1e-9 m en tuberías cortas y anchas).
        paso_q = float(np.max(np.abs(dq), initial=0.0))
        if (float(np.max(np.abs(f1))) < _TOL_ENERGIA_M and float(np.max(np.abs(f2), initial=0.0)) < _TOL_CONTINUIDAD
                and paso_q <= _TOL_Q_REL * float(np.max(np.abs(q), initial=0.0)) + _TOL_Q_ABS):
            convergio = True
            break
        if pasos >= max_iteraciones:
            break
        m0 = merito(f1, f2)
        alfa = 1.0
        for _red in range(_MAX_REDUCCIONES):
            q_n, h_n = q + alfa * dq, h_libre + alfa * dh
            f1_n, f2_n = evaluar(q_n, h_n)
            if merito(f1_n, f2_n) <= m0 or m0 < _TOL_ENERGIA_M:
                break
            alfa *= 0.5
        q, h_libre, f1, f2 = q_n, h_n, f1_n, f2_n
        pasos += 1
    if not convergio:
        cota = np.array([n["cota_m"] for n in libres], dtype=float)
        p_min = float(np.min(h_libre - cota)) if n_l else 0.0
        pista = (f"; la presión mínima de la última iteración es {p_min:.0f} m: red inviable, la demanda excede la "
                 "capacidad de las tuberías") if p_min < -10.0 else ""
        raise ValueError(
            f"el solver de la red no converge en {max_iteraciones} iteraciones "
            f"(residuo de energía {float(np.max(np.abs(f1))):.3e} m){pista}")

    carga: Dict[str, float] = {n["id"]: float(h_libre[ind_libre[n["id"]]]) for n in libres}
    carga.update({n["id"]: float(n["carga_fija_m"]) for n in fijos})
    neto = {n["id"]: 0.0 for n in nodos}
    for k, t in enumerate(tramos):
        neto[t["desde"]] += float(q[k])
        neto[t["hasta"]] -= float(q[k])
    perdida = r * q * np.abs(q) ** (N_HW - 1.0)
    return {
        "nodos": {n["id"]: {"carga_m": carga[n["id"]], "presion_m": carga[n["id"]] - float(n["cota_m"]),
                            "caudal_neto_m3s": neto[n["id"]]} for n in nodos},
        "tramos": {t["id"]: {"caudal_m3s": float(q[k]), "perdida_m": float(perdida[k]),
                             "velocidad_ms": float(abs(q[k]) / area[k])} for k, t in enumerate(tramos)},
        "iteraciones": pasos,
        "residuo_continuidad_m3s": float(np.max(np.abs(f2), initial=0.0)),
        "residuo_energia_m": float(np.max(np.abs(f1))),
    }
