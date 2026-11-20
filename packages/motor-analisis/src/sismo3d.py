"""Fuerza horizontal equivalente en 3D con torsión accidental, desplazamientos y derivas NSR-10 (#274, F1).

Numerales leídos en el corpus `nsr10_chunks` (2026-11-19):
  A.3.6.7.1  torsión accidental: la masa se desplaza ±0,05 de la dimensión del piso perpendicular a la dirección.
  A.3.6.7.2  la excentricidad centro de masa - centro de rigidez la refleja el propio modelo (diafragma rígido con el
             maestro en el centro de masa).
  A.3.6-2    Ax = [δmax / (1,2·δprom)]² ≤ 3,0 con irregularidad torsional 1aP o 1bP (Tabla A.3-6: 1aP si
             1,2 < δmax/δprom ≤ 1,4; 1bP si > 1,4; derivas de los extremos incluyendo la torsión accidental).
  A.6.2-1    δt = r·θ;   A.6.2-4  δtot = |δcm| + |δt| + |δpd|   (δpd: F3, aquí solo se evalúa Qi).
  A.6.2-2    Qi = Pi·Δcm / (Vi·hpi): P-Δ obligatorio si Qi > 0,10; potencialmente inestable si Qi > 0,30.
  A.6.3.1.1  sin 1aP/1bP: deriva = diferencia de δcm entre pisos consecutivos (mayor de las dos direcciones).
  A.6.3-1    con 1aP/1bP: Δmax = √Σj (δtot,j^i − δtot,j^(i−1))² en todos los ejes de columna.
  A.6.4.1    Tabla A.6.4-1: 1,0 % hpi (concreto, acero, madera, mampostería que falla por flexión); 0,5 % hpi
             (mampostería que falla por cortante). A.6.4.1.1: con secciones fisuradas, deriva × 0,7.
             A.6.4.1.5: sin límite en edificaciones de un piso.
Las fuerzas por piso son Fs sin dividir por R (las de A.4.3, que entran a la deriva); las calcula motor-geopot.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .portico3d import Caso3D, Portico3D

EXCENTRICIDAD_ACCIDENTAL = 0.05
AX_MAX = 3.0
RAZON_1AP, RAZON_1BP = 1.2, 1.4
Q_PDELTA, Q_INESTABLE = 0.10, 0.30
LIMITE_DERIVA = {"general": 0.010, "mamposteria_cortante": 0.005}
FACTOR_FISURADA = 0.7


@dataclass(frozen=True)
class Piso:
    """Datos de un piso, de abajo hacia arriba, en el mismo orden que sus diafragmas."""
    diafragma: str
    altura_entrepiso_m: float          # hpi
    dim_x_m: float                     # dimensión de la planta en X (para la excentricidad de las fuerzas en Y)
    dim_y_m: float                     # dimensión de la planta en Y (para las fuerzas en X)
    carga_vertical_kn: float           # carga muerta + viva del piso (para Pi de A.6.2-2)


def _ejes(modelo: Portico3D, pisos: list[Piso]) -> list[list[tuple[int, int | None]]]:
    """Por piso: pares (nodo del piso, nodo del mismo eje vertical en el piso de abajo o None si es la base)."""
    dia = {d.nombre: d for d in modelo.diafragmas}
    pares = []
    for i, p in enumerate(pisos):
        abajo = {}
        if i > 0:
            abajo = {(round(modelo.nodos[k].x, 6), round(modelo.nodos[k].y, 6)): k for k in dia[pisos[i - 1].diafragma].nodos}
        fila = []
        for k in dia[p.diafragma].nodos:
            clave = (round(modelo.nodos[k].x, 6), round(modelo.nodos[k].y, 6))
            if i > 0 and clave not in abajo:
                continue                 # eje que nace en este piso: sin punto homólogo abajo
            fila.append((k, abajo.get(clave)))
        pares.append(fila)
    return pares


def _casos(pisos: list[Piso], fx: list[float], fy: list[float], ax: dict[str, list[float]]):
    casos = []
    for dirn, fuerzas in (("x", fx), ("y", fy)):
        for signo in (+1, -1):
            maes = {}
            for i, (p, F) in enumerate(zip(pisos, fuerzas)):
                dim = p.dim_y_m if dirn == "x" else p.dim_x_m
                mz = signo * ax[dirn][i] * EXCENTRICIDAD_ACCIDENTAL * dim * F
                # fuerza en +x con la masa corrida en +y produce Mz = −F·e; en +y con masa en +x, Mz = +F·e
                maes[p.diafragma] = (F, 0.0, -mz) if dirn == "x" else (0.0, F, mz)
            casos.append((f"E{dirn}{'+' if signo > 0 else '-'}e", dirn, Caso3D(f"E{dirn}", maestros=maes)))
    return casos


def _desplazamientos(modelo: Portico3D, r, piso: Piso, k: int | None):
    """(δtot,x, δtot,y, δcm,x, δcm,y) del punto k del piso según A.6.2-4 (sin P-Δ). k None → base."""
    if k is None:
        return 0.0, 0.0, 0.0, 0.0
    d = next(dd for dd in modelo.diafragmas if dd.nombre == piso.diafragma)
    ux, uy, th = r.maestros[piso.diafragma]
    rx = modelo.nodos[k].y - d.y_cm     # brazo perpendicular a X
    ry = modelo.nodos[k].x - d.x_cm     # brazo perpendicular a Y
    return abs(ux) + abs(rx * th), abs(uy) + abs(ry * th), ux, uy


def analizar_fhe(modelo: Portico3D, pisos: list[Piso], fx: list[float], fy: list[float], sistema: str,
                 secciones_fisuradas: bool, max_iter: int = 20) -> dict:
    if len(pisos) != len(fx) or len(pisos) != len(fy):
        raise ValueError("Debe haber una fuerza por piso en cada dirección (NSR-10 A.4.3)")
    if sistema not in LIMITE_DERIVA:
        raise ValueError(f"Sistema '{sistema}' no reconocido (Tabla A.6.4-1); válidos: {', '.join(LIMITE_DERIVA)}")
    nombres = [d.nombre for d in modelo.diafragmas]
    if [p.diafragma for p in pisos] != nombres:
        raise ValueError("Los pisos deben darse de abajo hacia arriba, uno por diafragma y en el mismo orden")
    for p in pisos:
        if min(p.altura_entrepiso_m, p.dim_x_m, p.dim_y_m) <= 0 or p.carga_vertical_kn < 0:
            raise ValueError("Altura de entrepiso y dimensiones de planta deben ser positivas")
    pares = _ejes(modelo, pisos)
    n = len(pisos)
    ax = {"x": [1.0] * n, "y": [1.0] * n}
    for it in range(max_iter):
        resultados = [(nom, d, modelo.resolver(c)) for nom, d, c in _casos(pisos, fx, fy, ax)]
        nuevo = {"x": [1.0] * n, "y": [1.0] * n}
        razones = {"x": [0.0] * n, "y": [0.0] * n}
        for _, d, r in resultados:
            j = 0 if d == "x" else 1
            for i, p in enumerate(pisos):
                der = []
                for k, kb in pares[i]:
                    # deriva de extremo incluyendo torsión, con signo (A.3-6 compara extremos)
                    ux, uy, th = r.maestros[p.diafragma]
                    dd = next(x for x in modelo.diafragmas if x.nombre == p.diafragma)
                    brazo = -(modelo.nodos[k].y - dd.y_cm) if j == 0 else (modelo.nodos[k].x - dd.x_cm)
                    sup = (ux if j == 0 else uy) + brazo * th
                    if i > 0 and kb is not None:
                        ub, vb, tb = r.maestros[pisos[i - 1].diafragma]
                        db = next(x for x in modelo.diafragmas if x.nombre == pisos[i - 1].diafragma)
                        brazo_b = -(modelo.nodos[kb].y - db.y_cm) if j == 0 else (modelo.nodos[kb].x - db.x_cm)
                        inf = (ub if j == 0 else vb) + brazo_b * tb
                    else:
                        inf = 0.0
                    der.append(sup - inf)
                der = np.abs(der)
                prom = 0.5 * (der.max() + der.min())
                razon = float(der.max() / prom) if prom > 0 else 1.0
                razones[d][i] = max(razones[d][i], razon)
                if razon > RAZON_1AP:
                    nuevo[d][i] = max(nuevo[d][i], min((razon / RAZON_1AP) ** 2, AX_MAX))
        if all(abs(nuevo[d][i] - ax[d][i]) < 1e-3 for d in ax for i in range(n)):
            break
        ax = {d: [max(a, b) for a, b in zip(ax[d], nuevo[d])] for d in ax}
    irregular = max(max(razones["x"]), max(razones["y"]))
    tipo = "1bP" if irregular > RAZON_1BP else "1aP" if irregular > RAZON_1AP else "ninguna"

    limite = LIMITE_DERIVA[sistema]
    factor = FACTOR_FISURADA if secciones_fisuradas else 1.0
    P = np.cumsum([p.carga_vertical_kn for p in pisos][::-1])[::-1]
    filas, peor = [], 0.0
    for nom, d, r in resultados:
        V = np.cumsum((fx if d == "x" else fy)[::-1])[::-1]
        for i, p in enumerate(pisos):
            j = 0 if d == "x" else 1
            cm = r.maestros[p.diafragma][j] - (r.maestros[pisos[i - 1].diafragma][j] if i > 0 else 0.0)
            if tipo == "ninguna":
                deriva = abs(cm)
                regla = "A.6.3.1.1 (centro de masa)"
            else:
                deriva = 0.0
                for k, kb in pares[i]:
                    a = _desplazamientos(modelo, r, p, k)
                    b = _desplazamientos(modelo, r, pisos[i - 1], kb) if i > 0 else (0.0,) * 4
                    deriva = max(deriva, math.hypot(a[0] - b[0], a[1] - b[1]))
                regla = "A.6.3-1 (ejes de columna, δtot de A.6.2-4)"
            Q = P[i] * abs(cm) / (V[i] * p.altura_entrepiso_m) if V[i] > 0 else 0.0
            razon = factor * deriva / p.altura_entrepiso_m
            uso = razon / limite
            peor = max(peor, uso)
            filas.append({"caso": nom, "piso": p.diafragma, "deriva_m": deriva, "deriva_cm_m": abs(cm),
                          "deriva_relativa": razon, "uso_limite": uso, "regla": regla, "Qi": Q,
                          "p_delta": "inestable" if Q > Q_INESTABLE else ("requerido" if Q > Q_PDELTA else "no")})
    un_piso = n == 1
    return {"derivas": filas, "uso_max_limite": peor, "cumple_deriva": True if un_piso else peor <= 1.0,
            "sin_limite_un_piso": un_piso, "limite_deriva": limite, "factor_fisuradas": factor,
            "irregularidad_torsional": tipo, "razon_torsional_max": irregular, "Ax": ax, "iteraciones_Ax": it + 1,
            "Qi_max": max(f["Qi"] for f in filas)}
