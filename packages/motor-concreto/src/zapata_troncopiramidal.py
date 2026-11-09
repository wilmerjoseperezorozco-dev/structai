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
from .zapata import (H_MIN_D_MM, PESO_CONCRETO_KN_M3, SEP_MAX_ABS_MM, CargasZapata, Suelo, _as_flexion, _barras, _rho_min)

OFFSET_D_X_MM = 75.0 + 10.0              # recubrimiento + radio de barra (#6 supuesta), igual que zapata.py
OFFSET_D_Y_MM = OFFSET_D_X_MM + 19.1     # segunda capa
OFFSET_D_PUNZ_MM = OFFSET_D_X_MM + 9.55  # d promedio de ambas direcciones
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


def verificar(L_mm: float, h_c_mm: float, h_e_mm: float, c_mm: float, cargas: CargasZapata, suelo: Suelo, m: Materiales,
              *, lam: float = 1.0) -> ResultadoTroncopiramidal:
    fc, fy = m.fc, m.fy
    a = (L_mm - c_mm) / 2
    fallos: list[str] = []
    A = (L_mm / 1000) ** 2
    V = volumen_m3(L_mm, c_mm, h_c_mm, h_e_mm)
    h_med = V / A
    q = cargas.P_serv / A + PESO_CONCRETO_KN_M3 * h_med + suelo.peso_unitario_relleno_kn_m3 * max(suelo.profundidad_desplante_m - h_med, 0.0)
    if q > suelo.q_adm_kpa:
        fallos.append("q > q_adm")
    if h_e_mm - OFFSET_D_Y_MM < H_MIN_D_MM:
        fallos.append("d < 150 mm (C.15.7)")

    pu = cargas.P_u / A                                   # kPa, presión neta última (igual que zapata.py)
    s = np.linspace(0.0, a, 201)
    M = pu * (L_mm / 1000) * ((a - s) / 1000) ** 2 / 2    # kN·m en cada sección del voladizo
    h_s = _espesor(s, a, h_c_mm, h_e_mm)
    rmin = _rho_min(fy)
    sep_max = min(3 * h_med * 1000, SEP_MAX_ABS_MM)
    barras = {}
    for eje, off in (("x", OFFSET_D_X_MM), ("y", OFFSET_D_Y_MM)):
        d_s = h_s - off
        req = max(_as_flexion(float(Mi), L_mm, float(di), fc, fy) for Mi, di in zip(M, d_s))
        nec = max(req, rmin * L_mm * h_med * 1000)
        barras[eje] = (None if math.isinf(nec) else _barras(nec, L_mm, h_med * 1000, fy, sep_max))
        if barras[eje] is None:
            fallos.append(f"flexión dir. {eje} sin solución")
    k = (h_c_mm - h_e_mm) / a
    for eje, off in (("x", OFFSET_D_X_MM), ("y", OFFSET_D_Y_MM)):                       # cortante como viga a d de la cara
        s_cr = (h_c_mm - off) / (1 + k)
        if 0 < s_cr < a:
            Vu = pu * (L_mm / 1000) * (a - s_cr) / 1000
            Vc = PHI_CORTANTE * 0.17 * lam * math.sqrt(fc) * L_mm * s_cr / 1000
            if Vu > Vc:
                fallos.append(f"cortante viga dir. {eje}")
    s_p = (h_c_mm - OFFSET_D_PUNZ_MM) / (2 + k)                                         # punzonamiento a d/2
    d_p = 2 * s_p
    b1 = c_mm + d_p
    bo = 4 * b1
    Vu_p = cargas.P_u - pu * (b1 / 1000) ** 2
    vc = min(0.17 * 3.0, 0.083 * (40 * d_p / bo + 2), 0.33) * lam * math.sqrt(fc)
    if Vu_p > PHI_CORTANTE * vc * bo * d_p / 1000:
        fallos.append("punzonamiento")

    if fallos or barras["x"] is None or barras["y"] is None:
        return ResultadoTroncopiramidal(L_mm, h_c_mm, h_e_mm, False, "; ".join(fallos), V, math.inf, area_encofrado_m2(L_mm, c_mm, h_c_mm, h_e_mm),
                                        math.degrees(math.atan2(h_c_mm - h_e_mm, a)), q, "-", "-")
    masa = 7850e-9 * (barras["x"][1] * (L_mm - 150) + barras["y"][1] * (L_mm - 150))
    return ResultadoTroncopiramidal(L_mm, h_c_mm, h_e_mm, True, "", V, masa, area_encofrado_m2(L_mm, c_mm, h_c_mm, h_e_mm),
                                    math.degrees(math.atan2(h_c_mm - h_e_mm, a)), q, barras["x"][0], barras["y"][0])


def optimizar(c_mm: float, cargas: CargasZapata, suelo: Suelo, m: Materiales, *, paso_mm: float = 50.0, h_max_mm: float = 1000.0,
              h_e_min_mm: float = 300.0, holgura_L_mm: float = 600.0) -> ResultadoTroncopiramidal | None:
    """Mínimo de (volumen + masa_acero/7850) —la misma función objetivo de `zapata.disenar`— sobre L, h_c y h_e en rejilla."""
    A_min = cargas.P_serv / suelo.q_adm_kpa
    L0 = max(math.ceil(math.sqrt(A_min) * 1000 / paso_mm) * paso_mm, c_mm + 200.0)
    mejor, mejor_obj, primera = None, math.inf, None
    for L in np.arange(L0, 6000.0 + 1, paso_mm):
        if primera is not None and L > primera + holgura_L_mm:
            break
        for h_c in np.arange(h_e_min_mm, h_max_mm + 1, paso_mm):
            for h_e in np.arange(h_e_min_mm, h_c + 1, paso_mm):
                r = verificar(float(L), float(h_c), float(h_e), c_mm, cargas, suelo, m)
                if not r.cumple:
                    continue
                obj = r.volumen_m3 + r.masa_acero_kg / 7850.0
                primera = L if primera is None else primera
                if obj < mejor_obj:
                    mejor, mejor_obj = r, obj
    return mejor
