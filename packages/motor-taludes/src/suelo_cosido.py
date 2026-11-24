"""Estabilidad global de un muro de suelo cosido con Bishop simplificado y la fuerza de cada clavo (#241).

El círculo crítico se busca con el Bishop de motor-concreto (`excavacion_estabilidad.py`, H.5.1.2.1 y Tabla H.2.4-1),
al que se le pasan los clavos como refuerzos. En cada círculo, la fuerza de un clavo es la menor de (GEC 7, Ec. 5.2):

  tensión admisible        RT / FST
  arrancamiento detrás     rPO·LP / FSPO            (LP: longitud detrás de la superficie de falla)
  paramento + delante      R_paramento / FS + rPO·(L − LP) / FSPO

todas por metro de frente (÷ SH). Esa fuerza reduce el momento motor sin dividirse por el FS del suelo (GEC 7, Ec. 5.9).
No se incluye el aumento de la normal en la base de las dovelas por la componente del clavo.
"""
from __future__ import annotations

import importlib.util
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence


def _cargar_estabilidad():
    ruta = Path(__file__).resolve().parents[2] / "motor-concreto" / "src" / "excavacion_estabilidad.py"
    spec = importlib.util.spec_from_file_location("motor_concreto_excavacion_estabilidad", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


EST = _cargar_estabilidad()
X_PARAMENTO = 1e-6        # perfil_talud con 90°: el paramento vertical queda en x ≈ 0


@dataclass(frozen=True)
class FilaClavos:
    profundidad_m: float          # de la cabeza, bajo la corona
    longitud_m: float


@dataclass(frozen=True)
class Capacidades:
    """Capacidades admisibles por clavo (kN y kN/m de clavo), ya divididas por sus FS."""
    tension_kn: float
    adherencia_kn_m: float
    paramento_kn: float


def refuerzos(altura_m: float, filas: Sequence[FilaClavos], inclinacion_deg: float, sh_m: float,
              cap: Capacidades) -> tuple:
    if not filas:
        raise ValueError("Se necesita al menos una fila de clavos (FHWA GEC 7).")
    out = []
    for f in filas:
        if not 0.0 < f.profundidad_m < altura_m:
            raise ValueError(f"La cabeza del clavo a {f.profundidad_m} m debe quedar entre la corona y el pie (FHWA GEC 7).")
        out.append(EST.Refuerzo(x_cabeza=X_PARAMENTO, y_cabeza=altura_m - f.profundidad_m,
                                inclinacion_deg=inclinacion_deg, longitud_m=f.longitud_m,
                                t_tension_kn_m=cap.tension_kn / sh_m, adherencia_kn_m_por_m=cap.adherencia_kn_m / sh_m,
                                t_cabeza_kn_m=cap.paramento_kn / sh_m))
    return tuple(out)


def analizar(*, altura_m: float, filas: Sequence[FilaClavos], inclinacion_deg: float, sh_m: float, cap: Capacidades,
             gamma_kn_m3: float, c_kpa: float, phi_deg: float, gamma_sat_kn_m3: Optional[float] = None,
             prof_freatico_m: Optional[float] = None, sobrecarga_kpa: float = 0.0,
             ancho_sobrecarga_m: Optional[float] = None, kh: float = 0.0, grieta_traccion: bool = False,
             prof_estrato_firme_m: Optional[float] = None) -> dict:
    perfil = EST.perfil_talud(altura_m, 90.0)
    suelo = EST.SueloExc(gamma_kn_m3, c_kpa, phi_deg, gamma_sat_kn_m3)
    refs = refuerzos(altura_m, filas, inclinacion_deg, sh_m, cap)
    franja = None
    if sobrecarga_kpa > 0:
        if ancho_sobrecarga_m is None or ancho_sobrecarga_m <= 0:
            raise ValueError("Sobrecarga sin ancho de franja (FHWA GEC 7, Apéndice C).")
        franja = (perfil.x_cresta, perfil.x_cresta + ancho_sobrecarga_m)
    r = EST.factor_seguridad_talud(perfil, suelo, prof_freatico=prof_freatico_m, sobrecarga_kpa=sobrecarga_kpa,
                                   sobrecarga_x=franja, kh=kh, grieta_traccion=grieta_traccion,
                                   prof_estrato_firme=prof_estrato_firme_m, refuerzos=refs)
    clavos = []
    for f, ref in zip(filas, refs):
        t_m, _, modo = EST.fuerza_refuerzo(ref, r.xc, r.yc, r.radio)
        lfail = _longitud_delante(ref, r.xc, r.yc, r.radio)
        clavos.append({"profundidad_m": f.profundidad_m, "longitud_m": f.longitud_m, "t_kn": t_m * sh_m,
                       "gobierna": modo, "l_delante_m": lfail,
                       "l_detras_m": None if lfail is None else f.longitud_m - lfail})
    return {"fs": r.fs, "circulo": {"xc": r.xc, "yc": r.yc, "radio": r.radio}, "clavos": clavos,
            "en_borde_dominio": r.en_borde_dominio, "profundidad_grieta_m": r.profundidad_grieta_m}


def _longitud_delante(ref, xc: float, yc: float, radio: float) -> Optional[float]:
    ux, uy = math.cos(math.radians(ref.inclinacion_deg)), -math.sin(math.radians(ref.inclinacion_deg))
    dx, dy = ref.x_cabeza - xc, ref.y_cabeza - yc
    c = dx * dx + dy * dy - radio * radio
    if c >= 0:
        return None
    b = dx * ux + dy * uy
    s = -b + math.sqrt(b * b - c)
    return s if s < ref.longitud_m else None
