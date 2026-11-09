"""Simulación en periodo extendido con tanques cilíndricos de nivel variable.

En cada paso se resuelve la red en estado permanente con la carga de cada tanque fija en (cota de fondo + nivel); con el
caudal neto del tanque al inicio del paso se actualiza su nivel por Euler explícito (como EPANET): V' = Q_entrada.
Si en un paso el tanque cruzaría su nivel mínimo o máximo, la simulación se detiene y se informa el evento; no se
simula el cierre de tuberías ni la inversión de flujo que ocurriría después."""
import math
import time
from typing import Any, Dict, List, Optional

from .gradiente import BombaNoVence, _exigir, _finito, resolver_red

_MAX_PASOS = 2000
_MAX_TRABAJO = 200_000       # pasos × (nudos + tramos + bombas + válvulas): acota CPU y memoria (se guarda el estado de cada paso)
_PLAZO_S = 25.0              # tiempo de cómputo máximo de una simulación
_RAZON_OSCILACION = -0.3     # cociente de caudales de tanque entre pasos consecutivos; dos seguidos por debajo = oscilación numérica
_CLAVES_TANQUE = ("id", "cota_fondo_m", "area_m2", "nivel_inicial_m", "nivel_min_m", "nivel_max_m")


def _validar_tanques(nodos: List[dict], tanques: List[dict]) -> None:
    if not tanques:
        raise ValueError("la simulación en periodo extendido necesita al menos un tanque")
    por_id = {n["id"]: n for n in nodos if isinstance(n, dict) and "id" in n}
    vistos = set()
    for t in tanques:
        _exigir(t, _CLAVES_TANQUE, "tanque")
        if t["id"] in vistos:
            raise ValueError(f"tanque duplicado: {t['id']}")
        vistos.add(t["id"])
        if t["id"] not in por_id:
            raise ValueError(f"el tanque {t['id']} no corresponde a ningún nudo")
        n = por_id[t["id"]]
        if n.get("carga_fija_m") is not None or n.get("demanda_m3s", 0.0) != 0:
            raise ValueError(f"el nudo del tanque {t['id']} debe ser libre y sin demanda: el tanque fija su carga")
        for campo in _CLAVES_TANQUE[1:]:
            _finito(t[campo], f"{campo} del tanque {t['id']}")
        if t["area_m2"] <= 0:
            raise ValueError(f"el área del tanque {t['id']} debe ser positiva")
        if not (0 <= t["nivel_min_m"] <= t["nivel_inicial_m"] <= t["nivel_max_m"]):
            raise ValueError(f"el tanque {t['id']} necesita 0 ≤ nivel mínimo ≤ nivel inicial ≤ nivel máximo")


def _validar_tiempo(paso_s: Any, n_pasos: Any, patron: Optional[List[float]]) -> List[float]:
    if _finito(paso_s, "paso_s") <= 0:
        raise ValueError("paso_s debe ser positivo")
    if isinstance(n_pasos, bool) or not isinstance(n_pasos, int) or not (1 <= n_pasos <= _MAX_PASOS):
        raise ValueError(f"n_pasos debe ser un entero entre 1 y {_MAX_PASOS}")
    if patron is None:
        return [1.0]
    if not patron:
        raise ValueError("el patrón de demanda no puede estar vacío")
    for f in patron:
        if _finito(f, "factor del patrón de demanda") < 0:
            raise ValueError("los factores del patrón de demanda no pueden ser negativos")
    return [float(f) for f in patron]


def simular_periodo(nodos: List[dict], tramos: List[dict], *, tanques: List[dict], paso_s: float, n_pasos: int,
                    patron_demanda: Optional[List[float]] = None, bombas: Optional[List[dict]] = None,
                    valvulas: Optional[List[dict]] = None) -> Dict[str, Any]:
    """Devuelve estados en t = 0, Δt, …, n_pasos·Δt (o hasta el evento que detenga la simulación)."""
    patron = _validar_tiempo(paso_s, n_pasos, patron_demanda)
    _validar_tanques(nodos, tanques)
    trabajo = n_pasos * (len(nodos) + len(tramos) + len(bombas or []) + len(valvulas or []))
    if trabajo > _MAX_TRABAJO:
        raise ValueError(f"la simulación pide un trabajo de {trabajo} (pasos × elementos), sobre el máximo de {_MAX_TRABAJO}: "
                         "reduzca n_pasos o el tamaño de la red")
    inicio = time.monotonic()
    previo: Dict[str, float] = {}
    racha: Dict[str, int] = {}
    niveles = {t["id"]: float(t["nivel_inicial_m"]) for t in tanques}
    por_tanque = {t["id"]: t for t in tanques}
    pasos: List[Dict[str, Any]] = []
    eventos: List[str] = []
    completo = True
    for k in range(n_pasos + 1):
        factor = patron[k % len(patron)]
        nodos_k = []
        for n in nodos:
            copia = dict(n)
            if n["id"] in por_tanque:
                copia["carga_fija_m"] = por_tanque[n["id"]]["cota_fondo_m"] + niveles[n["id"]]
            else:
                copia["demanda_m3s"] = n.get("demanda_m3s", 0.0) * factor
            nodos_k.append(copia)
        if time.monotonic() - inicio > _PLAZO_S:
            raise ValueError(f"la simulación superó el plazo de cómputo de {_PLAZO_S:g} s en el paso {k}: reduzca la red o n_pasos")
        try:
            res = resolver_red(nodos_k, tramos, bombas=bombas, valvulas=valvulas)
        except BombaNoVence as e:
            if k == 0:
                raise
            eventos.append(f"{e}; en el paso {k} (t = {k * paso_s:g} s) el sistema empujaría agua en sentido inverso por la bomba, "
                           "lo que exigiría una válvula de retención, que no se modela")
            completo = False
            break
        except ValueError as e:
            raise ValueError(f"paso {k} (t = {k * paso_s:g} s): {e}") from e
        entrada = {tid: -res["nodos"][tid]["caudal_neto_m3s"] for tid in niveles}
        for tid, q_in in entrada.items():
            q_prev = previo.get(tid)
            patron_estable = k >= 2 and patron[k % len(patron)] == patron[(k - 1) % len(patron)] == patron[(k - 2) % len(patron)]
            if q_prev is not None and abs(q_prev) > 1e-12 and patron_estable and q_in / q_prev < _RAZON_OSCILACION:
                racha[tid] = racha.setdefault(tid, 0) + 1
                if racha[tid] >= 2:
                    raise ValueError(f"oscilación numérica en el tanque {tid} en el paso {k}: el caudal cambia de signo en pasos "
                                     "consecutivos, señal de que el paso de tiempo es demasiado grande para Euler explícito; reduzca paso_s")
            else:
                racha[tid] = 0
            previo[tid] = q_in
        pasos.append({"t_s": k * paso_s, "factor_demanda": factor, "nodos": res["nodos"], "tramos": res["tramos"],
                      "bombas": res.get("bombas", {}), "valvulas": res.get("valvulas", {}),
                      "tanques": {tid: {"nivel_m": niveles[tid], "caudal_entrada_m3s": entrada[tid]} for tid in niveles}})
        if k == n_pasos:
            break
        nuevos = {tid: niveles[tid] + entrada[tid] * paso_s / por_tanque[tid]["area_m2"] for tid in niveles}
        for tid, nivel in nuevos.items():
            t = por_tanque[tid]
            if nivel < t["nivel_min_m"] - 1e-12:
                eventos.append(f"el tanque {tid} se vacía: alcanzaría {nivel:.3f} m, bajo su nivel mínimo "
                               f"({t['nivel_min_m']:g} m), entre t = {k * paso_s:g} s y t = {(k + 1) * paso_s:g} s")
            elif nivel > t["nivel_max_m"] + 1e-12:
                eventos.append(f"el tanque {tid} se llena: alcanzaría {nivel:.3f} m, sobre su nivel máximo "
                               f"({t['nivel_max_m']:g} m), entre t = {k * paso_s:g} s y t = {(k + 1) * paso_s:g} s")
        if eventos:
            completo = False
            break
        niveles = nuevos
    return {"pasos": pasos, "eventos": eventos, "completo": completo, "paso_s": float(paso_s)}
