"""Figuras de acero de refuerzo (longitud de corte) y verificación de los mínimos de la NSR-10 con recomendación.

Verificado en el corpus nsr10_chunks: C.7.1.1 (gancho 180° + 4db ≥ 65 mm), C.7.1.2 (90° + 12db), C.7.1.3 (estribos #8 y menores: 135° + 6db),
C.7.2.2 y Tabla C.7.2 (diámetro de doblado: estribos #5 y menores 4db; #3 a #8 6db), C.12.2.1/.2 (ld ≥ 300 mm; denominadores 2,1/1,7 buenas
condiciones y 1,4/1,1 otros casos), C.12.5.1/.2 (ldh ≥ max(8db, 150 mm); 0,24·fy/(λ√f'c)·db), C.12.15.1 (traslapo en tracción clase A = 1,0 ld,
clase B = 1,3 ld, ≥ 300 mm), C.12.16.1 (compresión 0,071·fy·db ≥ 300 mm si fy ≤ 420; +1/3 si f'c < 21 MPa), C.15.8.2 (dovelas),
C.21.5.3.6 (estribo de dos piezas con gancho suplementario).
NO recuperado del corpus (hipótesis declaradas): Tabla C.7.2 para barras mayores que #8 (por eso solo se soportan #3 a #8),
extensión del gancho de 90° del gancho suplementario (se toma 6db), pendiente máxima del doblez de una barra en S (se advierte 1:6 del ACI 318).
Longitudes de corte: se mide por fuera de las dobleces y se descuenta cada doblez (2·ro·tan(θ/2) − θ·rc, con ro y rc radios exterior y del eje).
Para el estribo cerrado se usa la fórmula práctica de taller: perímetro exterior − 4 deducciones de 90° + 2 extensiones de gancho.
PRINCIPIO DE SEGURIDAD: la recomendación nunca baja de un mínimo de la NSR-10; optimizar (menos desperdicio) solo entre alternativas que cumplen.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .viga import DIAMETRO_MM

SOPORTADOS = ("3", "4", "5", "6", "7", "8")
EXT_90_DB, EXT_135_DB, EXT_180_DB = 12.0, 6.0, 4.0
EXT_135_MIN_MM, EXT_180_MIN_MM = 75.0, 65.0
MIN_TRASLAPO_MM = 300.0


def _db(dia: str) -> float:
    if dia not in SOPORTADOS:
        raise ValueError(f"barra #{dia} no soportada: la Tabla C.7.2 para barras mayores que #8 no está en el corpus verificado")
    return DIAMETRO_MM[dia]


def diametro_doblado_mm(dia: str, estribo: bool = False) -> float:
    db = _db(dia)
    return 4.0 * db if estribo and dia in ("3", "4", "5") else 6.0 * db


def _deduccion_mm(theta_deg: float, dia: str, estribo: bool = False) -> float:
    db = _db(dia)
    d_dob = diametro_doblado_mm(dia, estribo)
    ro, rc = d_dob / 2.0 + db, (d_dob + db) / 2.0
    th = math.radians(theta_deg)
    return 2.0 * ro * math.tan(th / 2.0) - th * rc


def extension_135_mm(dia: str) -> float:
    return max(EXT_135_DB * _db(dia), EXT_135_MIN_MM)


def extension_90_mm(dia: str) -> float:
    return EXT_90_DB * _db(dia)


@dataclass(frozen=True)
class Figura:
    tipo: str
    dia: str
    longitud_corte_m: float
    dobleces: int
    detalle: dict = field(default_factory=dict)
    advertencias: tuple[str, ...] = ()


def barra_recta(dia: str, largo_m: float) -> Figura:
    _db(dia)
    return Figura("recta", dia, largo_m, 0)


def barra_L(dia: str, tramo_m: float, pierna_m: float) -> Figura:
    """Dimensiones exteriores; un doblez de 90°."""
    return Figura("L", dia, tramo_m + pierna_m - _deduccion_mm(90, dia) / 1000.0, 1, {"tramo_m": tramo_m, "pierna_m": pierna_m})


def barra_C(dia: str, alma_m: float, pierna1_m: float, pierna2_m: float) -> Figura:
    """Alma y dos piernas del mismo lado (horquilla/estribo abierto); dos dobleces de 90°."""
    L = alma_m + pierna1_m + pierna2_m - 2 * _deduccion_mm(90, dia) / 1000.0
    return Figura("C", dia, L, 2, {"alma_m": alma_m, "piernas_m": (pierna1_m, pierna2_m)})


def barra_S(dia: str, tramo_inferior_m: float, tramo_superior_m: float, desfase_m: float, recorrido_m: float) -> Figura:
    """Barra con desfase (columna que cambia de sección o doblez en 'S'): dos dobleces de signo opuesto con el ángulo del tramo inclinado."""
    inclinado = math.hypot(desfase_m, recorrido_m)
    theta = math.degrees(math.atan2(desfase_m, recorrido_m))
    L = tramo_inferior_m + inclinado + tramo_superior_m - 2 * _deduccion_mm(theta, dia) / 1000.0
    adv = ("pendiente del tramo inclinado mayor que 1:6 (límite del ACI 318; no recuperado del corpus NSR-10)",) if desfase_m / recorrido_m > 1 / 6 else ()
    return Figura("S", dia, L, 2, {"angulo_deg": theta, "inclinado_m": inclinado}, adv)


def estribo_cerrado(dia: str, b_mm: float, h_mm: float, recubrimiento_mm: float = 40.0) -> Figura:
    """Estribo rectangular con ganchos sísmicos de 135°; b y h de la sección, el estribo se mide sobre el núcleo."""
    bo, ho = b_mm - 2 * recubrimiento_mm, h_mm - 2 * recubrimiento_mm
    L = 2 * (bo + ho) - 4 * _deduccion_mm(90, dia, estribo=True) + 2 * extension_135_mm(dia)
    return Figura("estribo", dia, L / 1000.0, 6, {"bo_mm": bo, "ho_mm": ho})


def gancho_suplementario(dia: str, tramo_mm: float) -> Figura:
    """Grapa: un extremo con 135° y el otro con 90° (C.21.5.3.6). Tramo = dimensión exterior entre los dos dobleces."""
    L = tramo_mm + extension_135_mm(dia) + EXT_135_DB * _db(dia) - _deduccion_mm(135, dia, True) - _deduccion_mm(90, dia, True)
    return Figura("gancho_suplementario", dia, L / 1000.0, 2, {"tramo_mm": tramo_mm},
                  ("extensión del gancho de 90° tomada como 6db (hipótesis; no recuperada del corpus)",))


def longitud_desarrollo_traccion_mm(dia: str, fc: float, fy: float, buenas_condiciones: bool = False) -> float:
    """ld de C.12.2.2 con ψt = ψe = λ = 1 (barra inferior sin epóxico, concreto normal). Por defecto el caso 'otros' (más largo, del lado seguro)."""
    den = {True: (2.1, 1.7), False: (1.4, 1.1)}[buenas_condiciones][0 if dia in ("3", "4", "5", "6") else 1]
    return max(fy / (den * math.sqrt(fc)) * _db(dia), 300.0)


def traslapo_traccion_mm(dia: str, fc: float, fy: float, clase: str = "B", buenas_condiciones: bool = False) -> float:
    if clase not in ("A", "B"):
        raise ValueError("clase 'A' o 'B'")
    return max((1.0 if clase == "A" else 1.3) * longitud_desarrollo_traccion_mm(dia, fc, fy, buenas_condiciones), MIN_TRASLAPO_MM)


def traslapo_compresion_mm(dia: str, fc: float, fy: float) -> float:
    db = _db(dia)
    L = 0.071 * fy * db if fy <= 420 else (0.13 * fy - 24) * db
    if fc < 21:
        L *= 4.0 / 3.0
    return max(L, MIN_TRASLAPO_MM)


def longitud_gancho_ldh_mm(dia: str, fc: float, fy: float) -> float:
    """ldh de C.12.5: 0,24·fy/√f'c·db, nunca menor que max(8db, 150 mm)."""
    db = _db(dia)
    return max(0.24 * fy / math.sqrt(fc) * db, 8.0 * db, 150.0)


def dovela(dia: str, embebido_m: float, proyeccion_m: float) -> Figura:
    """Pasador en L: tramo vertical (embebido + proyección) y pata horizontal de 12db dentro de la zapata."""
    pata = extension_90_mm(dia) / 1000.0
    f = barra_L(dia, embebido_m + proyeccion_m, pata)
    return Figura("dovela", dia, f.longitud_corte_m, 1, {"embebido_m": embebido_m, "proyeccion_m": proyeccion_m})


@dataclass(frozen=True)
class Hallazgo:
    cumple: bool
    norma: str
    mensaje: str
    valor_recomendado: float | None = None


def verificar_traslapo(dia: str, usuario_mm: float, fc: float, fy: float, compresion: bool = False, clase: str = "B") -> Hallazgo:
    minimo = traslapo_compresion_mm(dia, fc, fy) if compresion else traslapo_traccion_mm(dia, fc, fy, clase)
    norma = "C.12.16.1" if compresion else "C.12.15.1"
    if usuario_mm + 1e-9 >= minimo:
        return Hallazgo(True, norma, f"traslapo {usuario_mm:.0f} mm ≥ mínimo {minimo:.0f} mm")
    rec = math.ceil(minimo / 50.0) * 50.0
    return Hallazgo(False, norma, f"traslapo {usuario_mm:.0f} mm < mínimo {minimo:.0f} mm: aumentar a {rec:.0f} mm o evitar el empalme con una barra más larga", rec)


def verificar_gancho(dia: str, angulo_deg: int, extension_usuario_mm: float, estribo: bool = False) -> Hallazgo:
    db = _db(dia)
    if angulo_deg == 90:
        minimo, norma = EXT_90_DB * db, "C.7.1.2"
    elif angulo_deg == 135:
        minimo, norma = max(EXT_135_DB * db, EXT_135_MIN_MM if estribo else 0.0), "C.7.1.3"
    elif angulo_deg == 180:
        minimo, norma = max(EXT_180_DB * db, EXT_180_MIN_MM), "C.7.1.1"
    else:
        return Hallazgo(False, "C.7.1", f"gancho de {angulo_deg}° no es estándar (90°, 135° o 180°)", None)
    if extension_usuario_mm + 1e-9 >= minimo:
        return Hallazgo(True, norma, f"extensión {extension_usuario_mm:.0f} mm ≥ {minimo:.0f} mm")
    return Hallazgo(False, norma, f"extensión {extension_usuario_mm:.0f} mm < {minimo:.0f} mm: llevar a {math.ceil(minimo / 5) * 5:.0f} mm", math.ceil(minimo / 5) * 5.0)


def verificar_diametro_doblado(dia: str, usuario_mm: float, estribo: bool = False) -> Hallazgo:
    minimo = diametro_doblado_mm(dia, estribo)
    if usuario_mm + 1e-9 >= minimo:
        return Hallazgo(True, "C.7.2", f"diámetro de doblado {usuario_mm:.0f} mm ≥ {minimo:.0f} mm")
    return Hallazgo(False, "C.7.2", f"diámetro de doblado {usuario_mm:.0f} mm < {minimo:.0f} mm (riesgo de rotura del acero o aplastamiento del concreto)", minimo)
