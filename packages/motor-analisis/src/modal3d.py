"""Análisis modal y dinámico elástico espectral de edificios 3D con diafragma rígido (#274, F2).

Numerales leídos en el corpus `nsr10_chunks` (2026-11-19):
  A.5.2.1.1  modelo 3D con diafragma rígido: la masa de cada diafragma se concentra en su centro de masa
             (ux, uy y giro rz con la inercia rotacional de la planta).
  A.5.3.2    espectro de diseño de A.2.6 (lo entrega el llamador: motor-geopot).
  A.5.4-1/2  M̄j = Σ M̄mj ≥ 0,90·M en cada dirección;  M̄mj = (Σ mi·φij)² / Σ mi·φij².
  A.5.4-3    Vmj = Sam·g·M̄mj.
  A.5.4.4    combinación estadística de las respuestas modales máximas (CQC; SRSS si no hay interacción modal).
  A.5.4.5    Vtj ≥ 0,80·Vs (regular) o 0,90·Vs (irregular); si no, todos los resultados se multiplican por
             0,80·Vs/Vtj o 0,90·Vs/Vtj (A.5.4-4/-5). Si Vtj ya es mayor, no se reduce.
  A.3.6.7    en el análisis dinámico la torsión accidental queda a opción del diseñador: aquí se modela, si se pide,
             corriendo el centro de masa ±5 % de la dimensión perpendicular (cuatro modelos adicionales).
Las masas se condensan estáticamente sobre los grados de libertad de los maestros (exacto con masas solo en ellos).
Las derivas se combinan modo a modo (la deriva de cada modo se combina, no la diferencia de desplazamientos
combinados), como pide A.5.4.1 (c).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.linalg import eigh

from .portico3d import Diafragma, Portico3D
from .sismo3d import EXCENTRICIDAD_ACCIDENTAL, FACTOR_FISURADA, LIMITE_DERIVA, Q_INESTABLE, Q_PDELTA, Piso

G = 9.8                      # m/s², A.5.0
AMORTIGUAMIENTO = 0.05       # el espectro de A.2.6 es para 5 % del crítico
MASA_MIN = 0.90
AJUSTE = {"regular": 0.80, "irregular": 0.90}


@dataclass(frozen=True)
class Modos:
    periodos: np.ndarray        # (p,) s
    omega: np.ndarray           # (p,) rad/s
    phi: np.ndarray             # (3n, p) normalizados a la masa, orden [ux, uy, rz] por piso
    gamma: np.ndarray           # (p, 2) factores de participación en X e Y
    masa_efectiva: np.ndarray   # (p, 2) M̄mj
    masa_total: float


def masas_piso(pisos: list[Piso]) -> list[tuple[float, float]]:
    """(m, Jm) por piso: m = W/g; inercia rotacional de una planta rectangular uniforme m·(a² + b²)/12."""
    return [(p.carga_vertical_kn / G, p.carga_vertical_kn / G * (p.dim_x_m**2 + p.dim_y_m**2) / 12.0) for p in pisos]


def modos(modelo: Portico3D, masas: list[tuple[float, float]]) -> Modos:
    if len(masas) != len(modelo.diafragmas):
        raise ValueError("Debe haber una masa por diafragma (A.5.2.1.1)")
    if any(m <= 0 or j <= 0 for m, j in masas):
        raise ValueError("Las masas y las inercias rotacionales deben ser positivas")
    idx = [g for d in modelo.diafragmas for g in modelo._maestro_idx[d.nombre]]
    otros = np.setdiff1d(np.arange(modelo._nred), idx)
    K = modelo._Kr
    Kmm = K[np.ix_(idx, idx)]
    if otros.size:
        Kms = K[np.ix_(idx, otros)]
        Kmm = Kmm - Kms @ np.linalg.solve(K[np.ix_(otros, otros)], Kms.T)
    Kc = 0.5 * (Kmm + Kmm.T)
    M = np.diag([v for m, j in masas for v in (m, m, j)])
    w2, phi = eigh(Kc, M)
    if np.any(w2 <= 0):
        raise ValueError("Modo con frecuencia no positiva: el modelo lateral es inestable")
    omega = np.sqrt(w2)
    n = len(masas)
    r = np.zeros((3 * n, 2))
    r[0::3, 0] = 1.0
    r[1::3, 1] = 1.0
    gamma = phi.T @ M @ r
    return Modos(2 * math.pi / omega, omega, phi, gamma, gamma**2, float(sum(m for m, _ in masas)))


def cqc(valores: np.ndarray, omega: np.ndarray, z: float = AMORTIGUAMIENTO) -> np.ndarray:
    """Combinación cuadrática completa (Der Kiureghian) sobre el eje 0 (modos)."""
    r = omega[None, :] / omega[:, None]
    rho = 8 * z**2 * (1 + r) * r**1.5 / ((1 - r**2) ** 2 + 4 * z**2 * r * (1 + r) ** 2)
    v = np.asarray(valores, float)
    if v.ndim == 1:
        return float(np.sqrt(max(v @ rho @ v, 0.0)))
    return np.sqrt(np.maximum(np.einsum("i...,ij,j...->...", v, rho, v), 0.0))


def _respuestas(modelo: Portico3D, pisos: list[Piso], md: Modos, sa: Callable[[float], float], j: int, pares):
    """Respuestas modales (p, ...) en la dirección de excitación j: desplazamientos de maestros, cortantes y derivas."""
    n = len(pisos)
    sa_m = np.array([sa(T) for T in md.periodos])
    A = md.gamma[:, j] * sa_m * G / md.omega**2           # amplitud modal
    U = md.phi * A[None, :]                               # (3n, p)
    ux, uy, th = U[0::3].T, U[1::3].T, U[2::3].T          # (p, n)
    masas = masas_piso(pisos)
    fuerzas = np.array([[masas[i][0] * md.omega[m] ** 2 * (ux if j == 0 else uy)[m, i] for i in range(n)]
                        for m in range(len(md.omega))])     # fuerzas inerciales en la dirección j
    cort = np.cumsum(fuerzas[:, ::-1], axis=1)[:, ::-1]   # cortante de piso por modo
    dcm = np.diff(np.concatenate([np.zeros((len(md.omega), 1)), ux if j == 0 else uy], axis=1), axis=1)
    puntos = []                                           # por piso: (p, k, 2) derivas de punto (x, y)
    for i, p in enumerate(pisos):
        d = next(dd for dd in modelo.diafragmas if dd.nombre == p.diafragma)
        filas = []
        for k, kb in pares[i]:
            xk, yk = modelo.nodos[k].x - d.x_cm, modelo.nodos[k].y - d.y_cm
            sup = np.stack([ux[:, i] - yk * th[:, i], uy[:, i] + xk * th[:, i]], axis=1)
            if i > 0 and kb is not None:
                db = next(dd for dd in modelo.diafragmas if dd.nombre == pisos[i - 1].diafragma)
                xb, yb = modelo.nodos[kb].x - db.x_cm, modelo.nodos[kb].y - db.y_cm
                inf = np.stack([ux[:, i - 1] - yb * th[:, i - 1], uy[:, i - 1] + xb * th[:, i - 1]], axis=1)
            else:
                inf = 0.0
            filas.append(sup - inf)
        puntos.append(np.stack(filas, axis=1))
    vbase = sa_m * G * md.masa_efectiva[:, j]             # A.5.4-3
    return {"vbase": vbase, "cortante": cort, "deriva_cm": dcm, "puntos": puntos, "sa": sa_m}


def _con_cm_corrido(modelo: Portico3D, pisos: list[Piso], dx: float, dy: float) -> Portico3D:
    nuevos = [Diafragma(d.nombre, d.nodos, d.x_cm + dx * p.dim_x_m, d.y_cm + dy * p.dim_y_m)
              for d, p in zip(modelo.diafragmas, pisos)]
    return Portico3D(modelo.nodos, modelo.elementos, modelo.apoyos, nuevos)


def espectral(modelo: Portico3D, pisos: list[Piso], sa: Callable[[float], float], vs: tuple[float, float],
              regularidad: str, sistema: str, secciones_fisuradas: bool, torsion_accidental: bool = False) -> dict:
    """Análisis dinámico elástico espectral (A.5.4) con ajuste A.5.4.5 y derivas A.6."""
    if regularidad not in AJUSTE:
        raise ValueError(f"Regularidad '{regularidad}' no reconocida; válidas: {', '.join(AJUSTE)}")
    if sistema not in LIMITE_DERIVA:
        raise ValueError(f"Sistema '{sistema}' no reconocido (Tabla A.6.4-1)")
    if [p.diafragma for p in pisos] != [d.nombre for d in modelo.diafragmas]:
        raise ValueError("Los pisos deben darse de abajo hacia arriba, uno por diafragma y en el mismo orden")
    from .sismo3d import _ejes
    pares = _ejes(modelo, pisos)
    masas = masas_piso(pisos)
    variantes = [("centro", modelo)]
    if torsion_accidental:
        e = EXCENTRICIDAD_ACCIDENTAL
        variantes += [(f"cm{nm}", _con_cm_corrido(modelo, pisos, dx, dy))
                      for nm, dx, dy in (("+x", e, 0), ("-x", -e, 0), ("+y", 0, e), ("-y", 0, -e))]
    md0 = modos(modelo, masas)
    frac = md0.masa_efectiva.sum(axis=0) / md0.masa_total
    if np.any(frac < MASA_MIN - 1e-9):
        raise ValueError("Los modos no alcanzan el 90 % de la masa (A.5.4.2)")
    n = len(pisos)
    limite = LIMITE_DERIVA[sistema]
    fis = FACTOR_FISURADA if secciones_fisuradas else 1.0
    P = np.cumsum([p.carga_vertical_kn for p in pisos][::-1])[::-1]
    out_dir = {}
    for j, nombre in ((0, "x"), (1, "y")):
        vt = cqc(_respuestas(modelo, pisos, md0, sa, j, pares)["vbase"], md0.omega)
        factor = max(1.0, AJUSTE[regularidad] * vs[j] / vt) if vt > 0 else 1.0
        peor_punto = np.zeros(n)
        peor_cm = np.zeros(n)
        cort = np.zeros(n)
        for _, mod in variantes:
            md = md0 if mod is modelo else modos(mod, masas)
            r = _respuestas(mod, pisos, md, sa, j, _ejes(mod, pisos))
            cm = factor * cqc(r["deriva_cm"], md.omega)
            cort = np.maximum(cort, factor * cqc(r["cortante"], md.omega))
            pt = np.array([factor * np.max(np.hypot(*cqc(r["puntos"][i], md.omega).T)) for i in range(n)])
            peor_cm, peor_punto = np.maximum(peor_cm, cm), np.maximum(peor_punto, pt)
        filas = []
        for i, p in enumerate(pisos):
            Q = P[i] * peor_cm[i] / (cort[i] * p.altura_entrepiso_m) if cort[i] > 0 else 0.0
            filas.append({"piso": p.diafragma, "deriva_cm_m": float(peor_cm[i]), "deriva_punto_m": float(peor_punto[i]),
                          "uso_limite_cm": float(fis * peor_cm[i] / p.altura_entrepiso_m / limite),
                          "uso_limite_punto": float(fis * peor_punto[i] / p.altura_entrepiso_m / limite),
                          "cortante_kn": float(cort[i]), "Qi": float(Q),
                          "p_delta": "inestable" if Q > Q_INESTABLE else ("requerido" if Q > Q_PDELTA else "no")})
        out_dir[nombre] = {"Vt_sin_ajuste_kn": float(vt), "Vs_kn": float(vs[j]), "razon_Vt_Vs": float(vt / vs[j]),
                           "factor_ajuste": float(factor), "pisos": filas}
    return {"periodos_s": md0.periodos.tolist(),
            "masa_participante": {"x": float(frac[0]), "y": float(frac[1])},
            "masa_efectiva_modal": md0.masa_efectiva.tolist(), "direcciones": out_dir,
            "torsion_accidental": torsion_accidental, "limite_deriva": limite, "factor_fisuradas": fis,
            "uso_max_punto": max(f["uso_limite_punto"] for d in out_dir.values() for f in d["pisos"]),
            "uso_max_cm": max(f["uso_limite_cm"] for d in out_dir.values() for f in d["pisos"]),
            "Qi_max": max(f["Qi"] for d in out_dir.values() for f in d["pisos"])}
