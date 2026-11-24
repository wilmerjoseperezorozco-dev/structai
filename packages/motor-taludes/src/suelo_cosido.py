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

Versión 3 (#241): la v2 no pasó contra GEC 7 de 2003 porque los círculos son menos críticos que las cuñas en cortes
verticales. Ahora también se buscan dos cuñas planas por el pie con equilibrio de fuerzas (`cunas.py`, modelo de SNAIL) y
gobierna el menor FS. El control de salida por el paramento es analítico. Sin validar hasta tener un caso independiente.
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
from . import cunas as CUNAS  # noqa: E402
X_PARAMENTO = 1e-6        # perfil_talud con 90°: el paramento vertical queda en x ≈ 0


def perfil_muro(altura_m: float, bateria_deg: float = 0.0, talud_corona_deg: float = 0.0,
                ancho_talud_corona_m: float = 0.0):
    """Perfil con el pie en (0, 0): paramento inclinado `bateria_deg` respecto de la vertical (hacia el terreno) y, sobre
    la corona, un talud de `talud_corona_deg` en un ancho horizontal `ancho_talud_corona_m`, luego horizontal."""
    if not 0.0 <= bateria_deg < 45.0 or not 0.0 <= talud_corona_deg < 60.0 or ancho_talud_corona_m < 0:
        raise ValueError("Geometría del muro: batería en [0°, 45°), talud en la corona en [0°, 60°) y ancho ≥ 0 (FHWA GEC 7).")
    if bateria_deg == 0.0 and (talud_corona_deg == 0.0 or ancho_talud_corona_m == 0.0):
        return EST.perfil_talud(altura_m, 90.0)
    xc = max(altura_m * math.tan(math.radians(bateria_deg)), X_PARAMENTO)
    pts = [(0.0, 0.0), (xc, altura_m)]
    if talud_corona_deg > 0.0 and ancho_talud_corona_m > 0.0:
        pts.append((xc + ancho_talud_corona_m, altura_m + ancho_talud_corona_m * math.tan(math.radians(talud_corona_deg))))
    ext = 100.0 * altura_m
    pts = [(-ext, 0.0)] + pts + [(pts[-1][0] + ext, pts[-1][1])]
    return EST.Perfil(tuple(x for x, _ in pts), tuple(y for _, y in pts), altura_m, xc)


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
              cap: Capacidades, estratos: Sequence[EstratoCosido] = (), bateria_deg: float = 0.0) -> tuple:
    _validar_estratos(altura_m, estratos)
    adh_estr = tuple((altura_m - e.prof_techo_m, e.adherencia_kn_m / sh_m) for e in estratos)
    if not filas:
        raise ValueError("Se necesita al menos una fila de clavos (FHWA GEC 7).")
    out = []
    for f in filas:
        if not 0.0 < f.profundidad_m < altura_m:
            raise ValueError(f"La cabeza del clavo a {f.profundidad_m} m debe quedar entre la corona y el pie (FHWA GEC 7).")
        yc = altura_m - f.profundidad_m
        out.append(EST.Refuerzo(x_cabeza=max(yc * math.tan(math.radians(bateria_deg)), X_PARAMENTO), y_cabeza=yc,
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
             metodo: str = "A", superficie: str = "ambas", inicio_sobrecarga_m: float = 0.0,
             interfaz: str = "movilizada", bateria_deg: float = 0.0, talud_corona_deg: float = 0.0,
             ancho_talud_corona_m: float = 0.0) -> dict:
    """`gamma_kn_m3`, `c_kpa`, `phi_deg` y `cap.adherencia_kn_m` son los del estrato superior; `estratos` agrega los de abajo.
    `metodo`: "A" con capacidades admisibles (por defecto, SNAP-2 y GEC 7 de 2015) o "B" con capacidades últimas divididas por
    el FS global.
    `superficie` (v3): "circulo" (Bishop, también por debajo del pie), "cuna" (dos cuñas por el pie, `cunas.py`) o "ambas"
    (por defecto: gobierna el menor FS). `inicio_sobrecarga_m`: distancia de la corona al inicio de la franja cargada."""
    if superficie not in ("circulo", "cuna", "ambas"):
        raise ValueError("superficie: 'circulo', 'cuna' o 'ambas' (FHWA GEC 7).")
    if superficie != "circulo" and grieta_traccion:
        raise ValueError("Las cuñas no modelan grieta de tracción: use superficie='circulo' (FHWA GEC 7, §5.8.2).")
    perfil = perfil_muro(altura_m, bateria_deg, talud_corona_deg, ancho_talud_corona_m)
    suelo = EST.SueloExc(gamma_kn_m3, c_kpa, phi_deg, gamma_sat_kn_m3)
    refs = refuerzos(altura_m, filas, inclinacion_deg, sh_m, cap, estratos, bateria_deg)
    estr = tuple(EST.EstratoExc(altura_m - e.prof_techo_m, EST.SueloExc(e.gamma_kn_m3, e.c_kpa, e.phi_deg, e.gamma_sat_kn_m3))
                 for e in estratos)
    franja = None
    if sobrecarga_kpa > 0:
        if ancho_sobrecarga_m is None or ancho_sobrecarga_m <= 0:
            raise ValueError("Sobrecarga sin ancho de franja (FHWA GEC 7, Apéndice C).")
        franja = (perfil.x_cresta + inicio_sobrecarga_m, perfil.x_cresta + inicio_sobrecarga_m + ancho_sobrecarga_m)
    if superficie == "cuna":
        return _analizar_cunas(perfil, suelo, estr, refs, filas, sh_m, prof_freatico_m, sobrecarga_kpa, franja, kh,
                               metodo, interfaz)
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
    circ = {"fs": r.fs, "superficie": "circulo", "circulo": {"xc": r.xc, "yc": r.yc, "radio": r.radio}, "clavos": clavos,
            "en_borde_dominio": r.en_borde_dominio, "profundidad_grieta_m": r.profundidad_grieta_m}
    if superficie == "circulo":
        return circ
    cun = _analizar_cunas(perfil, suelo, estr, refs, filas, sh_m, prof_freatico_m, sobrecarga_kpa, franja, kh, metodo,
                          interfaz)
    gana = cun if cun["fs"] < circ["fs"] else circ
    return {**gana, "fs_circulo": circ["fs"], "fs_cuna": cun["fs"]}


def _analizar_cunas(perfil, suelo, estr, refs, filas, sh_m, prof_freatico_m, q, franja, kh, metodo, interfaz) -> dict:
    altura_m = perfil.altura
    capas = EST._capas(suelo, estr)
    y_agua = None if prof_freatico_m is None else altura_m - prof_freatico_m
    r = CUNAS.buscar(EST, perfil, capas, y_agua=y_agua, q=q, q_x=franja or (0.0, 0.0), kh=kh, refuerzos=refs,
                     metodo=metodo, interfaz=interfaz)
    clavos = []
    for f, ref in zip(filas, refs):
        t_m, _, modo = CUNAS.fuerza_clavo(ref, r.xb, r.yb, r.xe, float(perfil.terreno(r.xe)))
        clavos.append({"profundidad_m": f.profundidad_m, "longitud_m": f.longitud_m, "t_kn": t_m * sh_m, "gobierna": modo})
    return {"fs": r.fs, "superficie": "cuna", "cuna": {"xb": r.xb, "yb": r.yb, "xe": r.xe}, "clavos": clavos,
            "en_borde_dominio": False, "profundidad_grieta_m": 0.0}


def _longitud_delante(ref, xc: float, yc: float, radio: float) -> Optional[float]:
    ux, uy = math.cos(math.radians(ref.inclinacion_deg)), -math.sin(math.radians(ref.inclinacion_deg))
    dx, dy = ref.x_cabeza - xc, ref.y_cabeza - yc
    c = dx * dx + dy * dy - radio * radio
    if c >= 0:
        return None
    b = dx * ux + dy * uy
    s = -b + math.sqrt(b * b - c)
    return s if s < ref.longitud_m else None
