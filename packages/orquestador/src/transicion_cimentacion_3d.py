"""#333: transición de cimentación cuando la zapata aislada cuadrada de #324-C no cabe.

Escalera declarada: cuadrada (cimentacion_edificio_3d) → rectangular prismática (motor_concreto.zapata) → losa de
cimentación maciza RÍGIDA. Pilotes y losa aligerada quedan fuera de esta versión: el corpus no tiene perfil SPT.

Es una herramienta de MEDICIÓN, no de diseño:
  - losa rígida: presión lineal q = P/A ± M/S (sin interacción suelo-estructura), sin despegue en servicio;
  - momentos de la losa por franja con coeficiente declarado m_u = q_u,máx·L²/10 en las dos caras y las dos direcciones
    (refuerzo uniforme: cota superior del acero);
  - punzonamiento C.11.11.2.1 sin transferencia de momento (C.11.11.7 no modelado), con la presión media mínima;
  - cortante como viga por metro de ancho;
  - voladizo de la losa más allá de la cara de las columnas de borde: HIPÓTESIS (lo limitan los linderos);
  - q_adm BRUTA, el mismo dato declarado por estrato de #324-C (sin losa compensada).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from . import cimentacion_edificio_3d as ci
from . import diseno_edificio_3d as de

_zp = ci._zp

VOLADIZOS_LOSA_M = (0.0, 0.5, 1.0)       # más allá de la cara de las columnas de borde (HIPÓTESIS)
H_LOSA_MM = tuple(range(300, 2501, 50))
COEF_MOMENTO_LOSA = 10.0                 # m_u = q_u,máx·L²/10 por franja (método rígido, coeficiente declarado)
ALFA_S = {4: 40.0, 3: 30.0, 2: 20.0}     # C.11.11.2.1 por número de lados del perímetro crítico
PHI_CORTANTE = 0.75
GAMMA_CONCRETO, GAMMA_RELLENO = 24.0, 17.0   # kN/m³, los mismos de motor_concreto.zapata


@dataclass
class Losa:
    cumple: bool
    h_mm: float = math.nan
    voladizo_m: float = math.nan
    Bx_m: float = math.nan
    By_m: float = math.nan
    q_max_serv_kpa: float = math.nan
    q_min_serv_kpa: float = math.nan
    As_cara_x_mm2_m: float = math.nan
    As_cara_y_mm2_m: float = math.nan
    volumen_m3: float = 0.0
    acero_kg: float = 0.0
    encofrado_m2: float = 0.0
    costo_cop: float = 0.0
    motivo: str = ""


def resultantes(nodos: list, r: dict, coef: dict, xc: float, yc: float) -> tuple[float, float, float]:
    """(ΣP, M_y, M_x) de una combinación respecto al centro de la losa. M_y = ΣP·x′ − ΣMy y M_x = ΣP·y′ + ΣMx: con la
    convención de signos de las reacciones del pórtico los dos términos se suman (comprobado con Ex y Ey simétricos)."""
    P = My = Mx = 0.0
    for n in nodos:
        s = ci._comb(r, coef, n["k"])
        P += s[0]
        My += s[0] * (n["x"] - xc) - s[2]
        Mx += s[0] * (n["y"] - yc) + s[1]
    return float(P), float(My), float(Mx)


def presiones_losa(res: list, Bx: float, By: float) -> tuple[float, float]:
    """(q_máx, q_mín) de contacto sin peso propio, kPa: q = P/A ± |M_y|·(Bx/2)/I_y ± |M_x|·(By/2)/I_x."""
    A, Iy, Ix = Bx * By, By * Bx ** 3 / 12, Bx * By ** 3 / 12
    qs = [(P / A + abs(My) * Bx / 2 / Iy + abs(Mx) * By / 2 / Ix, P / A - abs(My) * Bx / 2 / Iy - abs(Mx) * By / 2 / Ix)
          for P, My, Mx in res]
    return max(q[0] for q in qs), min(q[1] for q in qs)


def punzonamiento(Pu: float, q_ref: float, c: float, d: float, lados_abiertos: int, v: float, fc: float) -> tuple[float, float]:
    """(Vu, φVc) en kN; c, d, v en mm. Un lado del perímetro crítico queda abierto si el voladizo desde la cara < d/2."""
    b_int = c + d
    b_ab = c + d / 2 + v                                   # lado perpendicular a un borde abierto
    if lados_abiertos == 0:
        bo, area, n = 4 * b_int, b_int ** 2, 4
    elif lados_abiertos == 1:
        bo, area, n = b_int + 2 * b_ab, b_int * b_ab, 3
    else:
        bo, area, n = 2 * b_ab, b_ab ** 2, 2
    vc = min(0.33, 0.083 * (ALFA_S[n] * d / bo + 2)) * math.sqrt(fc)   # columna cuadrada: 0,17(1+2/β) = 0,51 no gobierna
    return Pu - max(q_ref, 0.0) * area / 1e6, PHI_CORTANTE * vc * bo * d / 1000


def disenar_losa(p: de.ProyectoEdificio3D, q_adm_kpa: float, *, desplante_m: float = 1.5,
                 reac: Optional[tuple] = None) -> Losa:
    """Losa maciza rígida bajo todo el edificio: la de menor costo entre voladizos y espesores que cumplen."""
    nodos, r = reac or ci.reacciones_por_caso(p)
    combs = ci.combinaciones(list(r))
    xs, ys = sorted({n["x"] for n in nodos}), sorted({n["y"] for n in nodos})
    xc, yc = (xs[0] + xs[-1]) / 2, (ys[0] + ys[-1]) / 2
    c, fc, fy = p.columnas_mm[0], p.fc_mpa, p.fy_mpa
    luz_x = max((b - a for a, b in zip(xs, xs[1:])), default=0.0)
    luz_y = max((b - a for a, b in zip(ys, ys[1:])), default=0.0)
    serv = [resultantes(nodos, r, cs, xc, yc) for _n, cs, _cu in combs]
    ult = [resultantes(nodos, r, cu, xc, yc) for _n, _cs, cu in combs]
    pu_col = {n["k"]: max(float(ci._comb(r, cu, n["k"])[0]) for _n, _cs, cu in combs) for n in nodos}
    rho = _zp._rho_min(fy)
    mejor = Losa(False, motivo="q_máx > q_adm con todos los voladizos (haría falta pilotes o losa compensada)")
    for v in VOLADIZOS_LOSA_M:
        Bx, By = xs[-1] - xs[0] + c / 1000 + 2 * v, ys[-1] - ys[0] + c / 1000 + 2 * v
        A = Bx * By
        q_s = presiones_losa(serv, Bx, By)
        qu_max, _ = presiones_losa(ult, Bx, By)
        q_ref = max(min(P / A for P, _a, _b in ult), 0.0)
        candidatos = []
        for h in H_LOSA_MM:
            extra = GAMMA_CONCRETO * h / 1000 + GAMMA_RELLENO * max(desplante_m - h / 1000, 0.0)
            qmax, qmin = q_s[0] + extra, q_s[1] + extra
            if qmax > q_adm_kpa or qmin < 0:
                break                                      # más espesor solo sube la presión
            d = h - 75.0 - 19.0
            punz = True
            for n in nodos:
                abiertos = int(n["x"] in (xs[0], xs[-1]) and v * 1000 < d / 2) + int(n["y"] in (ys[0], ys[-1]) and v * 1000 < d / 2)
                vu, fvc = punzonamiento(pu_col[n["k"]], q_ref, c, d, abiertos, v * 1000, fc)
                if vu > fvc:
                    punz = False
                    break
            if not punz:
                continue
            vc_m = PHI_CORTANTE * 0.17 * math.sqrt(fc) * d                           # kN por metro de ancho
            vu_m = qu_max * max(max(luz_x, luz_y) / 2 - c / 2000 - d / 1000, v - d / 1000, 0.0)
            if vu_m > vc_m:
                continue
            As = {}
            for eje, L in (("x", luz_x), ("y", luz_y)):
                m = max(qu_max * L ** 2 / COEF_MOMENTO_LOSA, qu_max * v ** 2 / 2)
                As[eje] = max(_zp._as_flexion(m, 1000.0, d, fc, fy), rho * 1000.0 * h)
            if not all(math.isfinite(a) for a in As.values()):
                continue
            vol = A * h / 1000
            acero = 7850.0 * 2 * 1e-6 * (As["x"] + As["y"]) * Bx * By               # dos caras, dos direcciones
            enc = 2 * (Bx + By) * h / 1000
            costo = de._cc.costo_co2(de._cc.Cantidades(vol, acero, enc), fc)[0]
            candidatos.append(Losa(True, float(h), v, Bx, By, qmax, qmin, As["x"], As["y"], vol, acero, enc, costo))
            if len(candidatos) >= 5:                       # el primer h que cumple y cuatro más (puede bajar el acero)
                break
        if candidatos:
            mas_barata = min(candidatos, key=lambda x: x.costo_cop)
            if not mejor.cumple or mas_barata.costo_cop < mejor.costo_cop:
                mejor = mas_barata
    return mejor


def rectangular(cargas: list, c_mm: float, esp_x: float, esp_y: float, suelo, mat):
    """Zapata rectangular prismática con Lx ≤ esp_x y Ly ≤ esp_y (mm), de menor volumen + acero/7850, que cumple todas
    las combinaciones (motor_concreto.zapata.verificar). Devuelve (Lx, Ly, h, volumen, acero, encofrado) o None."""
    p_max = max(cg.P_serv for cg in cargas)
    pares = []
    for Lx in np.arange(c_mm + 200.0, esp_x + 1, ci.PASO_MM):
        for Ly in np.arange(c_mm + 200.0, esp_y + 1, ci.PASO_MM):
            if Lx * Ly / 1e6 * suelo.q_adm_kpa < p_max:
                continue
            q = [_zp.presiones_servicio(cg, suelo, Lx / 1000, Ly / 1000, 0.6) for cg in cargas]
            if all(a <= suelo.q_adm_kpa and b >= 0 for a, b in q):
                pares.append((Lx * Ly, float(Lx), float(Ly)))
    # el peso propio sube con h, así que las áreas mínimas (filtradas con h = 0,6 m) pueden no cumplir con el h real:
    # se recorren por área hasta tener 8 pares con solución
    mejor, con_solucion = None, 0
    for _a, Lx, Ly in sorted(pares)[:200]:
        for h in np.arange(ci.H_MIN_MM, ci.H_MAX_MM + 1, ci.PASO_MM):
            rs = [_zp.verificar(Lx / 1000, Ly / 1000, float(h), c_mm, c_mm, cg, suelo, mat) for cg in cargas]
            if not all(x.q_max_serv <= suelo.q_adm_kpa for x in rs):
                break                                      # más espesor solo sube la presión
            if all(x.cumple for x in rs):
                vol = rs[0].volumen_concreto_m3
                acero = max(x.masa_acero_kg for x in rs)
                obj = vol + acero / 7850.0
                if mejor is None or obj < mejor[0]:
                    mejor = (obj, Lx, Ly, float(h), vol, acero, 2 * (Lx + Ly) / 1000 * h / 1000)
                con_solucion += 1
                break
        if con_solucion >= 8:
            break
    return None if mejor is None else mejor[1:]


@dataclass
class Transicion:
    q_adm_kpa: float
    solucion: str                        # "aisladas" | "rectangulares" | "losa" | "sin_solucion"
    costo_cop: float
    costo_aisladas_cop: float            # todas cuadradas aunque no quepan (la aproximación de #324-C)
    costo_rectangulares_cop: float = math.nan
    costo_losa_cop: float = math.nan
    no_caben: int = 0
    rectangulares: int = 0
    losa: Optional[Losa] = None
    motivo: str = ""


def _costo(vol: float, acero: float, enc: float, fc: float) -> float:
    return de._cc.costo_co2(de._cc.Cantidades(vol, acero, enc), fc)[0]


def disenar_transicion(p: de.ProyectoEdificio3D, q_adm_kpa: float, *, desplante_m: float = 1.5,
                       reac: Optional[tuple] = None, con_losa: bool = True) -> Transicion:
    """La cimentación más barata de la escalera declarada que cumple y cabe."""
    reac = reac or ci.reacciones_por_caso(p)
    nodos, r = reac
    z = ci.disenar_zapatas(p, q_adm_kpa, desplante_m=desplante_m, reac=reac)
    t = Transicion(q_adm_kpa, "aisladas", z.costo_cop, z.costo_cop, no_caben=z.no_caben)
    if z.no_caben == 0 and z.sin_solucion == 0:
        return t
    combs = ci.combinaciones(list(r))
    suelo = _zp.Suelo(q_adm_kpa=q_adm_kpa, profundidad_desplante_m=desplante_m)
    mat = de._vg.Materiales(fc=p.fc_mpa, fy=p.fy_mpa, fyt=p.fy_mpa)
    c_mm = p.columnas_mm[0]
    xs, ys = sorted({n["x"] for n in nodos}), sorted({n["y"] for n in nodos})
    costo_rect, ok_rect = z.costo_cop, True
    for zp_ in z.zapatas:
        if zp_.cumple and not zp_.motivo.startswith("no cabe"):
            continue
        cargas = []
        for _nom, cs, cu in combs:
            s, u = ci._comb(r, cs, zp_.k), ci._comb(r, cu, zp_.k)
            if s[0] > 0:
                cargas.append(_zp.CargasZapata(P_serv=float(s[0]), P_u=float(max(u[0], 1e-6)), Mx_serv=float(s[1]),
                                               My_serv=float(s[2]), Mx_u=float(u[1]), My_u=float(u[2])))
        dx = min((abs(x - zp_.x) for x in xs if x != zp_.x), default=12.3) * 1000 - ci.SEPARACION_MIN_MM
        dy = min((abs(y - zp_.y) for y in ys if y != zp_.y), default=12.3) * 1000 - ci.SEPARACION_MIN_MM
        rect = rectangular(cargas, c_mm, dx, dy, suelo, mat)
        if rect is None:
            ok_rect = False
            break
        if zp_.cumple:
            costo_rect -= _costo(zp_.volumen_m3, zp_.acero_kg, zp_.encofrado_m2, p.fc_mpa)
        costo_rect += _costo(*rect[3:], p.fc_mpa)
        t.rectangulares += 1
    t.costo_rectangulares_cop = costo_rect if ok_rect else math.nan
    if con_losa:
        t.losa = disenar_losa(p, q_adm_kpa, desplante_m=desplante_m, reac=reac)
        t.costo_losa_cop = t.losa.costo_cop if t.losa.cumple else math.nan
    opciones = [(c, s) for c, s in ((t.costo_rectangulares_cop, "rectangulares"), (t.costo_losa_cop, "losa")) if math.isfinite(c)]
    if not opciones:
        t.solucion, t.costo_cop = "sin_solucion", math.nan
        t.motivo = "ni rectangulares ni losa" + (": " + t.losa.motivo if t.losa else "")
    else:
        t.costo_cop, t.solucion = min(opciones)
    return t
