"""Estabilidad global de un muro de suelo cosido con dos cuñas planas por el pie y equilibrio de fuerzas (v3, #241).

Formulación (FHWA GEC 7 de 2003, §5.8.2 y Apéndice F; FHWA-NHI-17-068, §6.2 y Figura 8, modelo de SNAIL):
- La superficie va del pie (0, 0) a un quiebre B = (xb, yb) y de ahí a la corona en E = (xe, H). La interfaz entre la cuña
  inferior (delantera) y la superior (trasera) es vertical, en x = xb.
- Cada cuña cumple equilibrio de fuerzas horizontal y vertical con el mismo FS. En la base:
  S = (C + N'·tanφ) / FS, con C = Σ c·ℓ y tanφ promediado con el peso de cada columna (estratos horizontales).
- En la interfaz actúan una fuerza E con inclinación β, con tanβ = tanφ_int / FS, y una cohesión movilizada
  c_int·h / FS. Es lo que muestra la Figura 8 (R a un ángulo β más CV). La alternativa "horizontal" toma β = 0 sin
  cohesión.
- Los clavos que cruzan la base de una cuña tiran de ella con T = mín(tensión, adherencia detrás, cabeza + adherencia
  delante). Método A, por defecto: T son capacidades admisibles (últimas ÷ su FS propio, como el modo FLAGT = 0 de SNAIL)
  y no se dividen por el FS global. Método B: T se divide por el FS global.
- Sismo: fuerza horizontal kh·W hacia la excavación en cada cuña.
- Se descartan las soluciones con normal de base negativa (tracción en el suelo). Si el quiebre está sobre la recta del
  pie a la corona, la superficie es un plano y se resuelve como un solo bloque (la interfaz es interna).

HIPÓTESIS (no están en la norma ni en GEC 7): perfil del terreno cualquiera sobre el pie (paramento con o sin
inclinación, talud en la corona), con el pie en (0, 0); la normal de la base se reparte en
proporción al peso de cada columna para promediar tanφ; sin grieta de tracción; agua con presión hidrostática bajo
una freática horizontal. No incluye la cuña triple bajo el pie de SNAIL: las superficies bajo el pie se cubren con los
círculos de Bishop (ver `suelo_cosido.analizar`).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.optimize import brentq, minimize

N_COL = 40
FS_INVALIDO = 1.0e3
FS_MIN, FS_MAX = 0.05, 50.0


@dataclass(frozen=True)
class ResultadoCunas:
    fs: float
    xb: float
    yb: float
    xe: float


def _perfil(est, geo):
    """Acepta la altura de un muro vertical con corona horizontal o un `Perfil` (pie en (0, 0), terreno arriba)."""
    return est.perfil_talud(float(geo), 90.0) if isinstance(geo, (int, float)) else geo


def _cruce_clavo(r, xb, yb, xe, H):
    """(s, cuña) del primer cruce del clavo con la superficie bilineal; cuña 1 = inferior, 2 = superior."""
    ux, uy = math.cos(math.radians(r.inclinacion_deg)), -math.sin(math.radians(r.inclinacion_deg))
    mejor = None
    for cuna, (ax, ay, bx, by) in ((1, (0.0, 0.0, xb, yb)), (2, (xb, yb, xe, H))):
        dx, dy = bx - ax, by - ay
        det = ux * (-dy) - uy * (-dx)
        if abs(det) < 1e-12:
            continue
        rx, ry = ax - r.x_cabeza, ay - r.y_cabeza
        s = (rx * (-dy) - ry * (-dx)) / det
        t = (ux * ry - uy * rx) / det
        if s > 1e-9 and -1e-9 <= t <= 1.0 + 1e-9 and (mejor is None or s < mejor[0]):
            mejor = (s, cuna)
    return mejor


def fuerza_clavo(r, xb, yb, xe, H):
    """(T por metro de frente, cuña, modo) de un clavo para la superficie dada."""
    c = _cruce_clavo(r, xb, yb, xe, H)
    if c is None or c[0] >= r.longitud_m:
        return 0.0, 0, "no_cruza"
    s, cuna = c
    modos = {"tension": r.t_tension_kn_m, "arrancamiento": r.adherencia_tramo(s, r.longitud_m),
             "paramento": r.t_cabeza_kn_m + r.adherencia_tramo(0.0, s)}
    g = min(modos, key=modos.get)
    return modos[g], cuna, g


def _cuna(est, capas, x0, x1, y_base0, y_base1, perfil, y_agua, q, q_x):
    """Peso, C, tanφ ponderado, U y longitud de la base de una cuña limitada por x0..x1 y la base recta dada."""
    b = (x1 - x0) / N_COL
    xm = x0 + b * (np.arange(N_COL) + 0.5)
    yb = y_base0 + (y_base1 - y_base0) * (xm - x0) / (x1 - x0)
    yt = perfil.terreno(xm)
    if (yt - yb <= 0.0).any():
        return None                    # la base sale del terreno: no es un mecanismo
    w, c, tf = est._peso_y_resistencia(yt, yb, b, y_agua, capas)
    if q > 0.0:
        w = w + q * b * ((xm >= q_x[0]) & (xm <= q_x[1]))
    largo = math.hypot(x1 - x0, y_base1 - y_base0)
    ell = largo / N_COL
    u = np.zeros_like(xm) if y_agua is None else est.GAMMA_AGUA_KN_M3 * np.maximum(y_agua - yb, 0.0)
    wt = float(w.sum())
    tan_phi = float((w * tf).sum() / wt) if wt > 0 else 0.0
    return wt, float((c * ell).sum()), tan_phi, float((u * ell).sum())


def _interfaz(capas, xb_y0, H):
    """(Σ c·h, tanφ medio por espesor) sobre la interfaz vertical de y0 a H."""
    ch, tf, h = 0.0, 0.0, 0.0
    for y_inf, y_sup, s in capas:
        e = max(min(H, y_sup) - max(xb_y0, y_inf), 0.0)
        ch += s.c_kpa * e
        tf += math.tan(math.radians(s.phi_deg)) * e
        h += e
    return ch, (tf / h if h > 0 else 0.0)


def fs_cunas(est, geo, capas, xb, yb, xe, *, y_agua=None, q=0.0, q_x=(0.0, 0.0), kh=0.0, refuerzos=(),
             metodo="A", interfaz="movilizada") -> float:
    perfil = _perfil(est, geo)
    if not (0.0 < xb < xe):
        return FS_INVALIDO
    H = float(perfil.terreno(xe))         # cota de salida en la corona
    if not 0.0 <= yb < min(H, float(perfil.terreno(xb))):
        return FS_INVALIDO
    th1, th2 = math.atan2(yb, xb), math.atan2(H - yb, xe - xb)
    if not (0.0 <= th1 < math.pi / 2 and 0.0 < th2 < math.pi / 2):
        return FS_INVALIDO
    k1 = _cuna(est, capas, 0.0, xb, 0.0, yb, perfil, y_agua, q, q_x)
    k2 = _cuna(est, capas, xb, xe, yb, H, perfil, y_agua, q, q_x)
    if k1 is None or k2 is None:
        return FS_INVALIDO
    w1, c1, tf1, u1 = k1
    w2, c2, tf2, u2 = k2
    ch, tfi = _interfaz(capas, yb, float(perfil.terreno(xb)))
    colineal = abs(yb * xe - H * xb) <= 1e-9 * max(H * xe, 1.0)
    if interfaz == "horizontal" or colineal:
        ch, tfi = 0.0, 0.0             # plano único: las fuerzas de la interfaz son internas y el FS no depende de ellas
    tx, ty = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
    for r in refuerzos:
        t, cuna, _ = fuerza_clavo(r, xb, yb, xe, H)
        if t > 0.0:
            i = math.radians(r.inclinacion_deg)
            tx[cuna] += t * math.cos(i)
            ty[cuna] -= t * math.sin(i)

    if colineal:                       # un solo bloque: suma de las dos cuñas
        wt = w1 + w2
        tf1 = (w1 * tf1 + w2 * tf2) / wt if wt > 0 else 0.0
        w1, c1, u1 = wt, c1 + c2, u1 + u2
        tx[1], ty[1] = tx[1] + tx[2], ty[1] + ty[2]

    def residuo(F):
        k = 1.0 if metodo == "A" else 1.0 / F
        if colineal:
            s1, c1_ = math.sin(th1), math.cos(th1)
            n1 = (w1 - u1 * c1_ - c1 / F * s1 - k * ty[1]) / (c1_ + tf1 / F * s1)
            return -n1 * s1 - u1 * s1 + (c1 + n1 * tf1) / F * c1_ + k * tx[1] - kh * w1
        s2, c2_ = math.sin(th2), math.cos(th2)
        tb = tfi / F
        # Cuña 2, incógnitas N' y E:
        #   x: −N'·s2 − U2·s2 + (C2 + N'·tf2)/F·c2 + E + k·Tx2 − kh·W2 = 0
        #   y:  N'·c2 + U2·c2 + (C2 + N'·tf2)/F·s2 + E·tb + ch/F + k·Ty2 − W2 = 0
        a = np.array([[-s2 + tf2 / F * c2_, 1.0], [c2_ + tf2 / F * s2, tb]])
        rhs = np.array([u2 * s2 - c2 / F * c2_ - k * tx[2] + kh * w2,
                        w2 - u2 * c2_ - c2 / F * s2 - ch / F - k * ty[2]])
        try:
            n2, e = np.linalg.solve(a, rhs)
        except np.linalg.LinAlgError:
            return None
        s1, c1_ = math.sin(th1), math.cos(th1)
        # Cuña 1: fuerzas de la interfaz con signo opuesto. De y se despeja N1'; el residuo es la suma en x.
        den = c1_ + tf1 / F * s1
        n1 = (w1 - u1 * c1_ - c1 / F * s1 + e * tb + ch / F - k * ty[1]) / den
        if n1 < -1e-6 * max(w1, 1.0) or n2 < -1e-6 * max(w2, 1.0):
            return None
        return -n1 * s1 - u1 * s1 + (c1 + n1 * tf1) / F * c1_ - e + k * tx[1] - kh * w1

    fs_grid = np.geomspace(FS_MIN, FS_MAX, 60)
    vals = [residuo(F) for F in fs_grid]
    for (fa, va), (fb, vb) in zip(zip(fs_grid, vals), zip(fs_grid[1:], vals[1:])):
        if va is not None and vb is not None and va * vb <= 0:
            try:
                return float(brentq(lambda F: residuo(F), fa, fb, xtol=1e-9))
            except (ValueError, TypeError):
                return FS_INVALIDO
    return FS_INVALIDO


def buscar(est, geo, capas, *, y_agua=None, q=0.0, q_x=(0.0, 0.0), kh=0.0, refuerzos=(), metodo="A",
           interfaz="movilizada", xe_max: Optional[float] = None) -> ResultadoCunas:
    """Busca la superficie bilineal crítica: rejilla en (xe, xb/xe, yb/H) y refinamiento con Nelder-Mead."""
    perfil = _perfil(est, geo)
    H = perfil.altura
    kw = dict(y_agua=y_agua, q=q, q_x=q_x, kh=kh, refuerzos=tuple(refuerzos), metodo=metodo, interfaz=interfaz)
    if xe_max is None:
        largo = max((r.longitud_m for r in refuerzos), default=H)
        xe_max = perfil.x_cresta + 1.2 * largo + H
    cand = []
    for xe in np.linspace(0.1 * H, xe_max, 16):
        for fb in (0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 0.95):
            for fy in (0.0, 0.1, 0.25, 0.4, 0.55, 0.7, 0.85):
                v = fs_cunas(est, perfil, capas, fb * xe, fy * H, xe, **kw)
                if v < FS_INVALIDO:
                    cand.append((v, xe, fb, fy))
    if not cand:
        raise ValueError("no se halló ninguna cuña bilineal válida (FHWA GEC 7, §5.8.2)")
    cand.sort()
    mejor = cand[0]

    def f(p):
        xe, fb, fy = p
        if not (0.0 < fb < 1.0 and 0.0 <= fy < 0.999 and 0.0 < xe <= xe_max):
            return FS_INVALIDO
        return fs_cunas(est, perfil, capas, fb * xe, fy * H, xe, **kw)
    for v0, xe0, fb0, fy0 in cand[:6]:
        r = minimize(f, [xe0, fb0, fy0], method="Nelder-Mead", options={"xatol": 1e-4, "fatol": 1e-7, "maxiter": 400})
        if r.fun < mejor[0]:
            mejor = (float(r.fun), *map(float, r.x))
    v, xe, fb, fy = mejor
    return ResultadoCunas(v, fb * xe, fy * H, xe)
