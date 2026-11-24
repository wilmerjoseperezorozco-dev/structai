"""Estabilidad global de un muro de suelo cosido con Bishop simplificado y la fuerza de cada clavo (#241).

El círculo crítico se busca con el Bishop de motor-concreto (`excavacion_estabilidad.py`, H.5.1.2.1 y Tabla H.2.4-1),
al que se le pasan los clavos como refuerzos. En cada círculo, la fuerza de un clavo es la menor de (GEC 7, Ec. 5.2):

  tensión admisible        RT / FST
  arrancamiento detrás     rPO·LP / FSPO            (LP: longitud detrás de la superficie de falla)
  paramento + delante      R_paramento / FS + rPO·(L − LP) / FSPO

todas por metro de frente (÷ SH). Versión 2 (#241), según la Ec. 12 de FHWA-NHI-17-068 (Bishop simplificado con el
Método A, la formulación de SNAP-2 y SLIDE): la fuerza reduce el momento motor con T·sin(α + θ) y su componente vertical
T·sinθ entra en la normal de la dovela que cruza, sin dividirse por el FS del suelo. El paramento es continuo: no se
aceptan superficies que salgan por la cara del muro sobre el pie.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence


def _cargar_estabilidad():
    ruta = Path(__file__).resolve().parents[2] / "motor-concreto" / "src" / "excavacion_estabilidad.py"
    spec = importlib.util.spec_from_file_location("motor_concreto_excavacion_estabilidad", ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod          # dataclasses con anotaciones diferidas buscan el módulo aquí
    spec.loader.exec_module(mod)
    return mod


EST = _cargar_estabilidad()
X_PARAMENTO = 1e-6        # perfil_talud con 90°: el paramento vertical queda en x ≈ 0


@dataclass(frozen=True)
class FilaClavos:
    profundidad_m: float          # de la cabeza, bajo la corona
    longitud_m: float
    inclinacion_deg: Optional[float] = None     # None: la inclinación común de `analizar`


@dataclass(frozen=True)
class Capacidades:
    """Capacidades admisibles por clavo (kN y kN/m de clavo), ya divididas por sus FS."""
    tension_kn: float
    adherencia_kn_m: float
    paramento_kn: float


@dataclass(frozen=True)
class EstratoCosido:
    """Estrato horizontal bajo la corona (#241): rige desde `prof_techo_m` hacia abajo hasta el techo del siguiente.
    `adherencia_kn_m` es la adherencia admisible por metro de clavo en este estrato (π·qu·DDH / FSPO)."""
    prof_techo_m: float
    gamma_kn_m3: float
    c_kpa: float
    phi_deg: float
    adherencia_kn_m: float
    gamma_sat_kn_m3: Optional[float] = None


def _validar_estratos(altura_m: float, estratos: Sequence[EstratoCosido]) -> None:
    profs = [e.prof_techo_m for e in estratos]
    if any(p <= 0 for p in profs) or profs != sorted(profs) or len(set(profs)) != len(profs):
        raise ValueError("Estratos: profundidades de techo positivas, distintas y ascendentes (FHWA GEC 7, Apéndice D).")


def refuerzos(altura_m: float, filas: Sequence[FilaClavos], inclinacion_deg: float, sh_m: float,
              cap: Capacidades, estratos: Sequence[EstratoCosido] = ()) -> tuple:
    _validar_estratos(altura_m, estratos)
    adh_estr = tuple((altura_m - e.prof_techo_m, e.adherencia_kn_m / sh_m) for e in estratos)
    if not filas:
        raise ValueError("Se necesita al menos una fila de clavos (FHWA GEC 7).")
    out = []
    for f in filas:
        if not 0.0 < f.profundidad_m < altura_m:
            raise ValueError(f"La cabeza del clavo a {f.profundidad_m} m debe quedar entre la corona y el pie (FHWA GEC 7).")
        out.append(EST.Refuerzo(x_cabeza=X_PARAMENTO, y_cabeza=altura_m - f.profundidad_m,
                                inclinacion_deg=inclinacion_deg if f.inclinacion_deg is None else f.inclinacion_deg,
                                longitud_m=f.longitud_m,
                                t_tension_kn_m=cap.tension_kn / sh_m, adherencia_kn_m_por_m=cap.adherencia_kn_m / sh_m,
                                t_cabeza_kn_m=cap.paramento_kn / sh_m, adherencia_estratos=adh_estr))
    return tuple(out)


def analizar(*, altura_m: float, filas: Sequence[FilaClavos], inclinacion_deg: float, sh_m: float, cap: Capacidades,
             gamma_kn_m3: float, c_kpa: float, phi_deg: float, gamma_sat_kn_m3: Optional[float] = None,
             prof_freatico_m: Optional[float] = None, sobrecarga_kpa: float = 0.0,
             ancho_sobrecarga_m: Optional[float] = None, kh: float = 0.0, grieta_traccion: bool = False,
             prof_estrato_firme_m: Optional[float] = None, estratos: Sequence[EstratoCosido] = (),
             metodo: str = "A") -> dict:
    """`gamma_kn_m3`, `c_kpa`, `phi_deg` y `cap.adherencia_kn_m` son los del estrato superior; `estratos` agrega los de abajo.
    `metodo`: "A" con capacidades admisibles (por defecto, SNAP-2 y GEC 7 de 2015) o "B" con capacidades últimas divididas por
    el FS global (modo "Ultimate" de SNAIL, GEC 7 de 2003)."""
    perfil = EST.perfil_talud(altura_m, 90.0)
    suelo = EST.SueloExc(gamma_kn_m3, c_kpa, phi_deg, gamma_sat_kn_m3)
    refs = refuerzos(altura_m, filas, inclinacion_deg, sh_m, cap, estratos)
    estr = tuple(EST.EstratoExc(altura_m - e.prof_techo_m, EST.SueloExc(e.gamma_kn_m3, e.c_kpa, e.phi_deg, e.gamma_sat_kn_m3))
                 for e in estratos)
    franja = None
    if sobrecarga_kpa > 0:
        if ancho_sobrecarga_m is None or ancho_sobrecarga_m <= 0:
            raise ValueError("Sobrecarga sin ancho de franja (FHWA GEC 7, Apéndice C).")
        franja = (perfil.x_cresta, perfil.x_cresta + ancho_sobrecarga_m)
    r = EST.factor_seguridad_talud(perfil, suelo, prof_freatico=prof_freatico_m, sobrecarga_kpa=sobrecarga_kpa,
                                   sobrecarga_x=franja, kh=kh, grieta_traccion=grieta_traccion,
                                   prof_estrato_firme=prof_estrato_firme_m, refuerzos=refs,
                                   paramento_continuo=True, estratos=estr, metodo_refuerzo=metodo)
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
