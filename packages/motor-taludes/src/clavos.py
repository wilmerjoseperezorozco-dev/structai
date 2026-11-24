"""Resistencias de un clavo de suelo cosido y de su paramento (FHWA GEC 7, FHWA-NHI-14-007, 2015), en unidades SI.

La NSR-10 (H.5.1.2.3 y H.8.2.5) exige revisar la falla del tensor, la adherencia lechada–terreno y el funcionamiento
estructural del anclaje, pero no da ecuaciones ni factores. Se usan los de GEC 7, cotejados con el PDF oficial:

  Arrancamiento por metro (Ec. 6.1):   rPO = π·qu·DDH;  RPO = rPO·LP (Ec. 6.2)
  Tensión del tendón (Ec. 6.5):        RT = At·fy
  Carga en la cabeza (Ec. 5.1):        To = Tmax·[0.6 + 0.057·(Smax[ft] − 3)]
  Flexión del paramento (Ec. 6.9–6.14): m = a·fy·(h/2 − a·fy/(1.7·f'c)), a por unidad de ancho;
                                        RFF = CF·(m_vm + m_vn)·8·SH/SV  y  CF·(m_hm + m_hn)·8·SV/SH, el menor
  CF (Tabla 6.5):                      inicial 100 mm → 2.0, 150 mm → 1.5, 200 mm → 1.0; final → 1.0
  Punzonamiento (Ec. 6.20–6.25):       RFP = CP·VF,  VF = 0.58·√f'c[psi]·π·D'c·hc [kip, ft]
                                        inicial: D'c = LBP + hi, hc = hi
                                        final:   hc = LS + tP − tSH, D'c = mín(SSH + hc, 2·hc)
  Pernos con cabeza (Ec. 6.26):        RFH = N·As·fy
  Factores de seguridad ASD mínimos:   Tabla 5.1
"""
from __future__ import annotations

import math
from typing import Literal

_REF = "FHWA GEC 7 (FHWA-NHI-14-007)"
PIE_M = 0.3048
# VF = 0.58·√(f'c [psi])·π·D'c·hc [kip, ft]  →  kPa·√MPa: 0.58·√145.0377·47.880 = 334.445
COEF_PUNZONAMIENTO_KPA = 0.58 * math.sqrt(145.0377377) * 47.880259
CP_POR_DEFECTO = 1.0                       # GEC 7: conservador, sin apoyo del suelo bajo la cabeza

Condicion = Literal["estatica", "sismica"]
# Tabla 5.1 (mínimos recomendados, ASD)
FS_GEC7 = {
    "estatica": {"global": 1.5, "arrancamiento": 2.0, "tension_g60_75": 1.8, "tension_g95_150": 2.0,
                 "flexion_paramento": 1.5, "punzonamiento": 1.5, "perno_a307": 2.0, "perno_a325": 1.7},
    "sismica": {"global": 1.1, "arrancamiento": 1.5, "tension_g60_75": 1.35, "tension_g95_150": 1.50,
                "flexion_paramento": 1.1, "punzonamiento": 1.1, "perno_a307": 1.5, "perno_a325": 1.3},
}
# Tabla 5.1: grados 60 y 75 (fy ≤ 75 ksi ≈ 517 MPa) contra 95 y 150
FY_LIMITE_GRADO_75_MPA = 520.0
# Tabla 6.5, paramento inicial: espesor (m) → CF
CF_INICIAL = ((0.1016, 2.0), (0.1524, 1.5), (0.2032, 1.0))


def _falla(msg: str) -> None:
    raise ValueError(f"{msg} ({_REF}).")


def _positivo(nombre: str, v: float) -> None:
    if not (isinstance(v, (int, float)) and math.isfinite(v) and v > 0):
        _falla(f"{nombre} debe ser positivo y finito; se recibió {v!r}")


def arrancamiento_por_metro_kn(qu_kpa: float, d_perforacion_m: float) -> float:
    """rPO = π·qu·DDH (kN por metro de clavo), Ec. 6.1."""
    _positivo("qu", qu_kpa)
    _positivo("DDH", d_perforacion_m)
    return math.pi * qu_kpa * d_perforacion_m


def tension_tendon_kn(area_m2: float, fy_mpa: float) -> float:
    """RT = At·fy (kN), Ec. 6.5."""
    _positivo("At", area_m2)
    _positivo("fy", fy_mpa)
    return area_m2 * fy_mpa * 1000.0


def fs_tension(fy_mpa: float, condicion: Condicion = "estatica") -> float:
    clave = "tension_g60_75" if fy_mpa <= FY_LIMITE_GRADO_75_MPA else "tension_g95_150"
    return FS_GEC7[condicion][clave]


def factor_carga_cabeza(s_max_m: float) -> float:
    """To / Tmax = 0.6 + 0.057·(Smax[ft] − 3), Ec. 5.1 (Clouterre 2002)."""
    _positivo("Smax", s_max_m)
    return 0.6 + 0.057 * (s_max_m / PIE_M - 3.0)


def cf_paramento(espesor_m: float, paramento: Literal["inicial", "final"]) -> float:
    """Tabla 6.5. Entre filas se toma el CF de la fila más gruesa (el menor, del lado conservador)."""
    _positivo("espesor", espesor_m)
    if paramento == "final":
        return 1.0
    if espesor_m < CF_INICIAL[0][0] - 1e-6:
        _falla("Paramento inicial más delgado que 100 mm: fuera de la Tabla 6.5")
    for h, cf in CF_INICIAL:
        if espesor_m <= h + 1e-6:
            return cf
    return 1.0


def _m(a_m2_m: float, fy_mpa: float, h_m: float, fc_mpa: float) -> float:
    """Momento resistente por unidad de ancho (kN·m/m), Ec. 6.9–6.12, con a en m²/m."""
    if a_m2_m < 0:
        _falla("El área de refuerzo por unidad de ancho no puede ser negativa")
    brazo = h_m / 2.0 - a_m2_m * fy_mpa / (1.7 * fc_mpa)
    if brazo <= 0:
        _falla("Refuerzo excesivo para el espesor: el bloque de compresión supera la mitad del paramento")
    return a_m2_m * fy_mpa * 1000.0 * brazo


def flexion_paramento_kn(*, espesor_m: float, fc_mpa: float, fy_mpa: float, a_vn: float, a_vm: float, a_hn: float,
                         a_hm: float, sh_m: float, sv_m: float, cf: float) -> float:
    """RFF (kN), el menor de las Ec. 6.13 y 6.14. Áreas de refuerzo por unidad de ancho en m²/m."""
    for n, v in (("h", espesor_m), ("f'c", fc_mpa), ("fy", fy_mpa), ("SH", sh_m), ("SV", sv_m), ("CF", cf)):
        _positivo(n, v)
    vertical = cf * (_m(a_vm, fy_mpa, espesor_m, fc_mpa) + _m(a_vn, fy_mpa, espesor_m, fc_mpa)) * 8.0 * sh_m / sv_m
    horizontal = cf * (_m(a_hm, fy_mpa, espesor_m, fc_mpa) + _m(a_hn, fy_mpa, espesor_m, fc_mpa)) * 8.0 * sv_m / sh_m
    return min(vertical, horizontal)


def punzonamiento_kn(fc_mpa: float, d_cono_m: float, h_cono_m: float, cp: float = CP_POR_DEFECTO) -> float:
    """RFP = CP·VF (kN), Ec. 6.20 y 6.21."""
    for n, v in (("f'c", fc_mpa), ("D'c", d_cono_m), ("hc", h_cono_m), ("CP", cp)):
        _positivo(n, v)
    if cp > 1.15:
        _falla("CP no puede superar 1,15")
    return cp * COEF_PUNZONAMIENTO_KPA * math.sqrt(fc_mpa) * math.pi * d_cono_m * h_cono_m


def cono_inicial(lado_placa_m: float, espesor_m: float) -> tuple[float, float]:
    """(D'c, hc) del paramento inicial con placa de apoyo, Ec. 6.22 y 6.23."""
    _positivo("LBP", lado_placa_m)
    _positivo("hi", espesor_m)
    return lado_placa_m + espesor_m, espesor_m


def cono_final(largo_perno_m: float, espesor_placa_m: float, espesor_cabeza_perno_m: float,
               separacion_pernos_m: float) -> tuple[float, float]:
    """(D'c, hc) del paramento final con pernos de cabeza, Ec. 6.24 y 6.25."""
    for n, v in (("LS", largo_perno_m), ("tP", espesor_placa_m), ("tSH", espesor_cabeza_perno_m),
                 ("SSH", separacion_pernos_m)):
        _positivo(n, v)
    hc = largo_perno_m + espesor_placa_m - espesor_cabeza_perno_m
    _positivo("hc", hc)
    return min(separacion_pernos_m + hc, 2.0 * hc), hc


def pernos_cabeza_kn(n_pernos: int, d_vastago_m: float, fy_mpa: float) -> float:
    """RFH = N·As·fy (kN), Ec. 6.26."""
    if n_pernos < 1:
        _falla("Se necesita al menos un perno")
    _positivo("DSC", d_vastago_m)
    _positivo("fy", fy_mpa)
    return n_pernos * math.pi * d_vastago_m ** 2 / 4.0 * fy_mpa * 1000.0
