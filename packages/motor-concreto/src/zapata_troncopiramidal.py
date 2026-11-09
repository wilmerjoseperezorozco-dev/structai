"""Zapata cuadrada troncopiramidal (espesor variable) con carga concéntrica — comparación contra la zapata prismática de `zapata.py`.

Propósito: cuantificar, con las MISMAS verificaciones de NSR-10 que usa `zapata.py` (C.15, C.11.11, C.11.1.3.1, C.9.3.2.1, C.15.7),
cuánto concreto y acero se ahorra al variar el espesor de forma lineal entre la cara de la columna (h_c) y el borde (h_e).
Es una hipótesis de investigación, no un método de diseño aprobado: la NSR-10 se escribe para zapatas de espesor constante
y el espesor variable se verifica aquí sección por sección con las mismas fórmulas (supuesto, ver SUPUESTOS).

Geometría: columna cuadrada c × c, zapata cuadrada L × L; el espesor baja linealmente de h_c (en la cara de la columna) a h_e (en el borde).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .viga import AREA_MM2, DIAMETRO_MM, PHI_CORTANTE, PHI_FLEXION, Materiales  # noqa: F401
from .zapata import (H_MIN_D_MM, SEP_MAX_ABS_MM, CargasZapata, Suelo, _barras, _rho_min, presiones_servicio)

RECUBRIMIENTO_SUELO_MM = 75.0            # C.7.7.1(a): concreto colocado contra el suelo
RADIO_BARRA_MM = 10.0                    # radio de barra (#6 supuesta), igual que zapata.py
SEGUNDA_CAPA_MM = 19.1
MEDIA_CAPA_MM = 9.55                     # d promedio de ambas direcciones para punzonamiento


def _offsets(recub_mm: float) -> tuple[float, float, float]:
    """(offset dir. x, offset dir. y, offset punzonamiento) = recubrimiento + radio (+ capa)."""
    ox = recub_mm + RADIO_BARRA_MM
    return ox, ox + SEGUNDA_CAPA_MM, ox + MEDIA_CAPA_MM
ANGULO_SIN_CONTRAENCOFRADO_GRADOS = 25.0  # supuesto constructivo SIN fuente normativa: pendientes mayores requieren contraencofrado

SUPUESTOS = (
    "Espesor variable verificado sección por sección con las fórmulas de la zapata de espesor constante (la NSR-10 no trata el espesor variable de forma explícita en lo leído).",
    "Carga concéntrica, columna cuadrada, zapata cuadrada; sin momentos.",
    "Acero uniforme en cada dirección; As mínima de retracción sobre el espesor medio (supuesto).",
    "Pendiente máxima sin contraencofrado: supuesto constructivo sin fuente; solo se informa el ángulo, no se rechaza.",
    "Longitud de desarrollo, separación libre (C.7.6) y transferencia de momento (C.11.11.7) NO verificadas, igual que en zapata.py.",
)


@dataclass(frozen=True)
class ResultadoTroncopiramidal:
    L_mm: float
    h_c_mm: float
    h_e_mm: float
    cumple: bool
    motivo_fallo: str
    volumen_m3: float
    masa_acero_kg: float
    area_encofrado_m2: float
    angulo_talud_grados: float
    q_max_kpa: float
    barras_x: str
    barras_y: str


def volumen_m3(L_mm: float, c_mm: float, h_c_mm: float, h_e_mm: float) -> float:
    """Prisma de espesor h_e más el tronco de pirámide (bases L² y c², altura h_c − h_e)."""
    L, c = L_mm / 1000, c_mm / 1000
    H = (h_c_mm - h_e_mm) / 1000
    return L * L * h_e_mm / 1000 + H / 3 * (L * L + c * c + L * c)


def area_encofrado_m2(L_mm: float, c_mm: float, h_c_mm: float, h_e_mm: float) -> float:
    """Encofrado: caras laterales verticales (4·L·h_e). El talud superior es superficie libre y solo requiere contraencofrado si su
    pendiente supera ANGULO_SIN_CONTRAENCOFRADO_GRADOS (supuesto constructivo sin fuente); en ese caso se suma su área. Sin fondo."""
    L, c = L_mm / 1000, c_mm / 1000
    a = (L - c) / 2
    H = (h_c_mm - h_e_mm) / 1000
    vertical = 4 * L * h_e_mm / 1000
    if H > 1e-9 and math.degrees(math.atan2(H, a)) > ANGULO_SIN_CONTRAENCOFRADO_GRADOS:
        return vertical + 4 * (L + c) / 2 * math.sqrt(a * a + H * H)
    return vertical


def _espesor(s_mm: np.ndarray, a_mm: float, h_c: float, h_e: float) -> np.ndarray:
    return h_c - (h_c - h_e) * s_mm / a_mm


def _as_flexion_vec(M_knm: np.ndarray, b: float, d: np.ndarray, fc: float, fy: float) -> np.ndarray:
    """Versión vectorizada de zapata._as_flexion (misma fórmula, φ = 0,90); inf donde la sección no alcanza."""
    Mu = M_knm * 1e6 / PHI_FLEXION
    disc = (0.85 * fc * b * d) ** 2 - 2 * 0.85 * fc * b * Mu
    a = np.where(disc >= 0, (0.85 * fc * b * d - np.sqrt(np.maximum(disc, 0.0))) / (0.85 * fc * b), np.inf)
    return 0.85 * fc * b * a / fy


def _momento_seccion(p0: float, k: float, a_m: float, c_m: float, B_m: float, s_m: np.ndarray) -> np.ndarray:
    """Momento [kN·m] en la sección a distancia s de la cara de la columna, lado más cargado: p(ξ) = p0 + |k|(c/2 + ξ), ξ ∈ [s, a]."""
    k = abs(k)
    q0 = p0 + k * c_m / 2
    return B_m * (q0 * (a_m - s_m) ** 2 / 2 + k * (a_m**3 / 3 - s_m * a_m**2 / 2 + s_m**3 / 6))


def verificar(L_mm: float, h_c_mm: float, h_e_mm: float, c_mm: float, cargas: CargasZapata, suelo: Suelo, m: Materiales,
              *, lam: float = 1.0, recubrimiento_mm: float = RECUBRIMIENTO_SUELO_MM) -> ResultadoTroncopiramidal:
    """Verifica y diseña el refuerzo mínimo. Con momentos (Mx_u, My_u, Mx_serv, My_serv de `cargas`) usa presión lineal (sin despegue en servicio) y,
    como en zapata.verificar, la presión del lado más cargado para flexión y cortante. Con suelo.ks_kn_m3 > 0 verifica el asentamiento q_neta/ks."""
    fc, fy = m.fc, m.fy
    off_x, off_y, off_p = _offsets(recubrimiento_mm)
    a = (L_mm - c_mm) / 2
    Lm, cm, am = L_mm / 1000, c_mm / 1000, a / 1000
    fallos: list[str] = []
    A = Lm ** 2
    V = volumen_m3(L_mm, c_mm, h_c_mm, h_e_mm)
    h_med = V / A
    q, qmin = presiones_servicio(cargas, suelo, Lm, Lm, h_med)
    if q > suelo.q_adm_kpa:
        fallos.append("q > q_adm")
    if qmin < 0:
        fallos.append("despegue en servicio (q_min < 0)")
    if suelo.ks_kn_m3 > 0:
        w_mm = max(q - suelo.peso_unitario_relleno_kn_m3 * suelo.profundidad_desplante_m, 0.0) / suelo.ks_kn_m3 * 1000
        if w_mm > suelo.asentamiento_max_mm:
            fallos.append(f"asentamiento {w_mm:.1f} mm > {suelo.asentamiento_max_mm:.0f} mm")
    if h_e_mm - off_y < H_MIN_D_MM:
        fallos.append("d < 150 mm (C.15.7)")

    p0 = cargas.P_u / A                                   # kPa
    kx = 12 * cargas.My_u / (Lm ** 3 * Lm)                # kPa/m, variación lineal en x
    ky = 12 * cargas.Mx_u / (Lm ** 3 * Lm)
    if p0 - (abs(kx) + abs(ky)) * Lm / 2 < 0 and abs(kx) + abs(ky) > 0:
        pass                                              # despegue en el estado último: la presión del lado cargado ya es la envolvente usada
    s = np.linspace(0.0, a, 201)
    h_s = _espesor(s, a, h_c_mm, h_e_mm)
    rmin = _rho_min(fy)
    sep_max = min(3 * h_med * 1000, SEP_MAX_ABS_MM)
    barras = {}
    for eje, off, k in (("x", off_x, kx), ("y", off_y, ky)):
        M = _momento_seccion(p0, k, am, cm, Lm, s / 1000)
        req = float(np.max(_as_flexion_vec(M, L_mm, h_s - off, fc, fy)))
        nec = max(req, rmin * L_mm * h_med * 1000)
        barras[eje] = (None if math.isinf(nec) else _barras(nec, L_mm, h_med * 1000, fy, sep_max))
        if barras[eje] is None:
            fallos.append(f"flexión dir. {eje} sin solución")
    kk = (h_c_mm - h_e_mm) / a
    for eje, off, k in (("x", off_x, kx), ("y", off_y, ky)):                          # cortante como viga a d de la cara
        s_cr = (h_c_mm - off) / (1 + kk)
        if 0 < s_cr < a:
            sm = s_cr / 1000
            kq = abs(k)
            Vu = Lm * ((p0 + kq * cm / 2) * (am - sm) + kq * (am ** 2 - sm ** 2) / 2)
            Vc = PHI_CORTANTE * 0.17 * lam * math.sqrt(fc) * L_mm * s_cr / 1000
            if Vu > Vc:
                fallos.append(f"cortante viga dir. {eje}")
    s_p = (h_c_mm - off_p) / (2 + kk)                                                 # punzonamiento a d/2
    d_p = 2 * s_p
    b1 = c_mm + d_p
    bo = 4 * b1
    q_ref = max(p0 - (abs(kx) + abs(ky)) * Lm / 2, 0.0)
    Vu_p = cargas.P_u - q_ref * (b1 / 1000) ** 2
    vc = min(0.17 * 3.0, 0.083 * (40 * d_p / bo + 2), 0.33) * lam * math.sqrt(fc)
    if Vu_p > PHI_CORTANTE * vc * bo * d_p / 1000:
        fallos.append("punzonamiento")

    ang = math.degrees(math.atan2(h_c_mm - h_e_mm, a))
    enc = area_encofrado_m2(L_mm, c_mm, h_c_mm, h_e_mm)
    if fallos or barras["x"] is None or barras["y"] is None:
        return ResultadoTroncopiramidal(L_mm, h_c_mm, h_e_mm, False, "; ".join(fallos), V, math.inf, enc, ang, q, "-", "-")
    masa = 7850e-9 * (barras["x"][1] * (L_mm - 150) + barras["y"][1] * (L_mm - 150))
    return ResultadoTroncopiramidal(L_mm, h_c_mm, h_e_mm, True, "", V, masa, enc, ang, q, barras["x"][0], barras["y"][0])


def optimizar(c_mm: float, cargas: CargasZapata, suelo: Suelo, m: Materiales, *, paso_mm: float = 50.0, h_max_mm: float = 1000.0,
              h_e_min_mm: float = 300.0, holgura_L_mm: float = 600.0,
              recubrimiento_mm: float = RECUBRIMIENTO_SUELO_MM) -> ResultadoTroncopiramidal | None:
    """Mínimo de (volumen + masa_acero/7850) —la misma función objetivo de `zapata.disenar`— sobre L, h_c y h_e en rejilla."""
    A_min = cargas.P_serv / suelo.q_adm_kpa
    L0 = max(math.ceil(math.sqrt(A_min) * 1000 / paso_mm) * paso_mm, c_mm + 200.0)
    mejor, mejor_obj, primera = None, math.inf, None
    for L in np.arange(L0, 6000.0 + 1, paso_mm):
        if primera is not None and L > primera + holgura_L_mm:
            break
        for h_c in np.arange(h_e_min_mm, h_max_mm + 1, paso_mm):
            for h_e in np.arange(h_e_min_mm, h_c + 1, paso_mm):
                r = verificar(float(L), float(h_c), float(h_e), c_mm, cargas, suelo, m, recubrimiento_mm=recubrimiento_mm)
                if not r.cumple:
                    continue
                obj = r.volumen_m3 + r.masa_acero_kg / 7850.0
                primera = L if primera is None else primera
                if obj < mejor_obj:
                    mejor, mejor_obj = r, obj
    return mejor
