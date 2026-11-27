"""Zapatas aisladas bajo las columnas del edificio 3D (#324-C): reacciones por caso, combinaciones de servicio (B.2.3) y
últimas (B.2.4), y diseño con motor-concreto.zapata_troncopiramidal sobre todas las combinaciones representativas.

Es una herramienta de MEDICIÓN, no de diseño de cimentaciones:
  - zapata aislada cuadrada por columna; si no cabe entre columnas vecinas se marca (haría falta zapata combinada, losa
    o pilotes, que aquí no se diseñan);
  - criterio del motor: sin despegue en servicio (q_min ≥ 0, resultante en el núcleo central) y q_máx ≤ q_adm;
  - E = Fs/R de la FHE del edificio (sin Ω0 ni reducción especial para cimentaciones);
  - momentos de la reacción en el apoyo empotrado, sin el cortante por la altura del pedestal;
  - q_adm es un DATO del estudio de suelos que el corpus no tiene: se recorre como estrato declarado.
"""
from __future__ import annotations

import importlib
import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import diseno_edificio_3d as de

_zt = importlib.import_module("motor_concreto.zapata_troncopiramidal")
_zp = importlib.import_module("motor_concreto.zapata")

PASO_MM = 50.0
H_MAX_MM = 1500.0
H_MIN_MM = 300.0
SEPARACION_MIN_MM = 300.0          # holgura libre mínima entre zapatas vecinas (HIPÓTESIS de medición)


def reacciones_por_caso(p: de.ProyectoEdificio3D) -> tuple[list[dict], dict[str, dict[int, np.ndarray]]]:
    """(nodos de base [{k, x, y}], {caso: {k: (P, Mx, My)}}) con P > 0 en compresión. Casos: D, L, Ex±e, Ey±e y los de
    viento del proyecto (mismos nombres que la memoria)."""
    m = de.construir_modelo(p)
    sis = de.analisis_sismico(p, m)
    der = de._s3.analizar_fhe(m.portico, m.pisos, sis["x"]["Fs_deriva_kn"], sis["y"]["Fs_deriva_kn"], "general", True)
    _F, res = de._resolver_casos(p, m, sis, der["Ax"])
    nombres = ["D", "L", "Ex+e", "Ex-e", "Ey+e", "Ey-e"]
    pares = list(zip(nombres, res))
    if p.viento is not None:
        cw, _info = de._casos_viento(p, m, sis)
        pares += [(nom, m.portico.resolver(caso)) for nom, caso, _w in cw]
    base = sorted(m.portico.apoyos)
    nodos = [{"k": k, "x": m.portico.nodos[k].x, "y": m.portico.nodos[k].y} for k in base]
    out = {}
    for nom, r in pares:
        out[nom] = {k: np.array([r.reacciones[k][2], r.reacciones[k][3], r.reacciones[k][4]]) for k in base}
    return nodos, out


def combinaciones(casos: list[str]) -> list[tuple[str, dict, dict]]:
    """(nombre, coeficientes de servicio B.2.3, coeficientes últimos B.2.4) emparejados por la misma acción lateral."""
    out = [("D+L", {"D": 1, "L": 1}, {"D": 1.2, "L": 1.6}), ("D", {"D": 1}, {"D": 1.4})]
    sismo = [c for c in casos if c.startswith("E")]
    viento = [c for c in casos if c.startswith("W")]
    for s in sismo:
        for sg in (1, -1):
            # A.3.6.3: 100 % en una dirección + 30 % en la otra (con el mismo signo de excentricidad)
            perp = [c for c in sismo if c[1] != s[1] and c[2:] == s[2:]]
            for sp in (1, -1):
                e = {s: sg, perp[0]: 0.3 * sp} if perp else {s: sg}
                nom = f"{s}{'+' if sg > 0 else '-'}0.3{perp[0] if perp else ''}{'+' if sp > 0 else '-'}"
                out.append((f"D+0.7E[{nom}]", {"D": 1, **{k: 0.7 * v for k, v in e.items()}}, {"D": 1.2, "L": 1.0, **e}))
                out.append((f"D+0.75L+0.525E[{nom}]", {"D": 1, "L": 0.75, **{k: 0.525 * v for k, v in e.items()}},
                            {"D": 1.2, "L": 1.0, **e}))
                out.append((f"0.6D+0.7E[{nom}]", {"D": 0.6, **{k: 0.7 * v for k, v in e.items()}}, {"D": 0.9, **e}))
    for w in viento:
        out.append((f"D+W[{w}]", {"D": 1, w: 1}, {"D": 1.2, "L": 1.0, w: 1.6}))                          # B.2.3-5 / B.2.4-4
        out.append((f"D+0.75L+0.75W[{w}]", {"D": 1, "L": 0.75, w: 0.75}, {"D": 1.2, "L": 1.6, w: 0.8}))   # B.2.3-7 / B.2.4-3
        out.append((f"0.6D+W[{w}]", {"D": 0.6, w: 1}, {"D": 0.9, w: 1.6}))                               # B.2.3-9 / B.2.4-6
    return out


def _comb(r: dict, coef: dict, k: int) -> np.ndarray:
    return sum(v * r[c][k] for c, v in coef.items())


@dataclass
class Zapata:
    k: int
    x: float
    y: float
    cumple: bool
    L_mm: float = math.nan
    h_c_mm: float = math.nan
    h_e_mm: float = math.nan
    volumen_m3: float = 0.0
    acero_kg: float = 0.0
    encofrado_m2: float = 0.0
    L_portante_mm: float = math.nan     # menor L con q_máx ≤ q_adm en todas las combinaciones
    L_nucleo_mm: float = math.nan       # menor L con q_mín ≥ 0 (sin despegue) en todas las combinaciones
    gobierna: str = ""                  # "portante" | "excentricidad" | "estructural"
    traccion_neta: bool = False         # alguna combinación de servicio con P < 0 (levantamiento)
    comb_gobierna: str = ""
    motivo: str = ""


@dataclass
class ResultadoCimentacion:
    q_adm_kpa: float
    zapatas: list[Zapata] = field(default_factory=list)
    costo_cop: float = 0.0
    no_caben: int = 0                   # zapatas cuya L supera el espacio entre columnas vecinas
    sin_solucion: int = 0


def _l_minimo(cargas: list, suelo, h_med_m: float, cond) -> float:
    for L in np.arange(500.0, 12000.0 + 1, PASO_MM):
        if all(cond(_zp.presiones_servicio(c, suelo, L / 1000, L / 1000, h_med_m)) for c in cargas):
            return float(L)
    return math.inf


def _representativas(cargas: list, suelo, L_mm: float, n: int = 3) -> list[int]:
    """Índices de las combinaciones que pueden gobernar: mayores q_máx, menores q_mín, mayor P_u y mayores momentos
    últimos por eje. El diseño elegido se verifica después con todas."""
    L = L_mm / 1000
    q = [_zp.presiones_servicio(c, suelo, L, L, 0.6) for c in cargas]
    claves = [lambda i: -q[i][0], lambda i: q[i][1], lambda i: -cargas[i].P_u, lambda i: -abs(cargas[i].Mx_u),
              lambda i: -abs(cargas[i].My_u), lambda i: -(cargas[i].P_u + 6 * (abs(cargas[i].Mx_u) + abs(cargas[i].My_u)) / L)]
    sel = set()
    for f in claves:
        sel |= set(sorted(range(len(cargas)), key=f)[:n])
    return sorted(sel)


def _buscar(L0: float, sub: list, c_mm: float, suelo, mat):
    """Primera L (desde L0) con alguna (h_c, h_e) que cumple todas las combinaciones de `sub`; en ella, la de menor
    volumen + acero. Devuelve (objetivo, L, h_c, h_e) o None."""
    for L in np.arange(L0, L0 + 2500.0 + 1, PASO_MM):
        mejor = None
        for h_c in np.arange(H_MIN_MM, H_MAX_MM + 1, PASO_MM):
            for h_e in np.arange(H_MIN_MM, h_c + 1, PASO_MM):
                rs = [_zt.verificar(float(L), float(h_c), float(h_e), c_mm, c, suelo, mat) for c in sub]
                if all(x.cumple for x in rs):
                    obj = max(x.volumen_m3 for x in rs) + max(x.masa_acero_kg for x in rs) / 7850.0
                    if mejor is None or obj < mejor[0]:
                        mejor = (obj, float(L), float(h_c), float(h_e))
                    break                                            # h_e mayor solo encarece con este h_c
        if mejor is not None:
            return mejor
    return None


def disenar_zapatas(p: de.ProyectoEdificio3D, q_adm_kpa: float, *, desplante_m: float = 1.5,
                    reac: Optional[tuple] = None) -> ResultadoCimentacion:
    nodos, r = reac or reacciones_por_caso(p)
    combs = combinaciones(list(r))
    suelo = _zp.Suelo(q_adm_kpa=q_adm_kpa, profundidad_desplante_m=desplante_m)
    mat = de._vg.Materiales(fc=p.fc_mpa, fy=p.fy_mpa, fyt=p.fy_mpa)
    c_mm = p.columnas_mm[0]
    xs = sorted({n["x"] for n in nodos})
    ys = sorted({n["y"] for n in nodos})
    out = ResultadoCimentacion(q_adm_kpa)
    for nd in nodos:
        k = nd["k"]
        cargas, nombres = [], []
        z = Zapata(k, nd["x"], nd["y"], False)
        for nom, cs, cu in combs:
            s, u = _comb(r, cs, k), _comb(r, cu, k)
            if s[0] <= 0:
                z.traccion_neta = True
                continue
            cargas.append(_zp.CargasZapata(P_serv=float(s[0]), P_u=float(max(u[0], 1e-6)), Mx_serv=float(s[1]),
                                           My_serv=float(s[2]), Mx_u=float(u[1]), My_u=float(u[2])))
            nombres.append(nom)
        # espacio disponible: mitad de la distancia a cada vecino, menos la holgura
        dx = [abs(x - nd["x"]) for x in xs if x != nd["x"]]
        dy = [abs(y - nd["y"]) for y in ys if y != nd["y"]]
        espacio = min(min(dx, default=math.inf), min(dy, default=math.inf)) * 1000 - SEPARACION_MIN_MM
        # gobierno geométrico con un espesor de referencia (h_med = 0,6 m); el diseño final lo recalcula
        z.L_portante_mm = _l_minimo(cargas, suelo, 0.6, lambda qq: qq[0] <= q_adm_kpa)
        z.L_nucleo_mm = _l_minimo(cargas, suelo, 0.6, lambda qq: qq[1] >= 0)
        L0 = max(z.L_portante_mm, z.L_nucleo_mm, c_mm + 200.0)
        mejor = None
        activas = _representativas(cargas, suelo, L0) if math.isfinite(L0) else []
        for _intento in range(6 if math.isfinite(L0) else 0):
            mejor = _buscar(L0, [cargas[i] for i in activas], c_mm, suelo, mat)
            if mejor is None:
                break
            todas = [_zt.verificar(mejor[1], mejor[2], mejor[3], c_mm, c, suelo, mat) for c in cargas]   # todas las combinaciones
            faltan = [i for i, x in enumerate(todas) if not x.cumple]
            mejor = (mejor[0], mejor[1], mejor[2], mejor[3], todas)
            if not faltan:
                break
            activas, mejor = sorted(set(activas) | set(faltan)), None
        if mejor is None:
            z.motivo = "sin solución en la rejilla"
            out.sin_solucion += 1
            out.zapatas.append(z)
            continue
        _o, L, h_c, h_e, rs = mejor
        i_q = int(np.argmax([x.q_max_kpa for x in rs]))
        z.cumple, z.L_mm, z.h_c_mm, z.h_e_mm = True, L, h_c, h_e
        z.volumen_m3 = rs[0].volumen_m3
        z.acero_kg = max(x.masa_acero_kg for x in rs)
        z.encofrado_m2 = rs[0].area_encofrado_m2
        z.comb_gobierna = nombres[i_q]
        if z.L_nucleo_mm > z.L_portante_mm and L <= z.L_nucleo_mm + PASO_MM:
            z.gobierna = "excentricidad"
        elif L <= z.L_portante_mm + PASO_MM:
            z.gobierna = "portante"
        else:
            z.gobierna = "estructural"
        if L > espacio:
            out.no_caben += 1
            z.motivo = f"no cabe: L = {L:.0f} mm > espacio {espacio:.0f} mm"
        q = de._cc.Cantidades(z.volumen_m3, z.acero_kg, z.encofrado_m2)
        out.costo_cop += de._cc.costo_co2(q, p.fc_mpa)[0]
        out.zapatas.append(z)
    return out
