"""Capacidad axial a compresión de un pilote individual en suelo estratificado (NSR-10 H.4.4 y H.4.7).

Fricción y punta se evalúan por separado, cada una con su factor de seguridad (H.4.4.1, último párrafo):

  Fricción, suelo drenado  (H.2.4-4, H.4.7-2):  τF = c' + K·σ'v·tanφ'     τL = 2/3·τF
  Fricción, suelo no drenado (H.2-6, H.4.7-3):  τF = Su                   τL = α·Su,
                                                α = 0.2 + 0.8·exp[0.35 − 2·Su/PA] ≤ 1.0
  Admisible por fricción:  Qs,adm = Σ τL·p·Δz / FSL     FSL = F_SB de la Tabla H.2.4-1
  Punta:                   Qp,adm = qp,ult·Ap / F_SICP  F_SICP de la Tabla H.4.7-1

La NSR-10 no da fórmula de resistencia por punta. En arcilla se usa qp,ult = 9·Su (Skempton, 1951). En suelo drenado
la resistencia por punta debe venir del estudio geotécnico; con SPT, el camino del CCP-14 (Meyerhof y método β) está en
`arena_spt.py`. La roca (H.4.7-4) queda fuera hasta verificar la ecuación con el PDF oficial.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Sequence

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import exigir  # noqa: E402

PA_KPA = 101.325          # presión atmosférica, H.4.7-3
GAMMA_W = 9.81            # kN/m³
NC_PUNTA_ARCILLA = 9.0    # Skempton (1951), pilote profundo
FACTOR_TAU_L = 2.0 / 3.0  # H.4.7-2

Combinacion = Literal["cm_cv_normal", "cm_cv_maxima", "cm_cv_sismo"]
# Tabla H.4.7-1: F_SICP mínimos (diseño), capacidad por punta de cimentaciones profundas
FS_PUNTA = {"cm_cv_normal": 3.0, "cm_cv_maxima": 2.5, "cm_cv_sismo": 1.5}
# Tabla H.2.4-1, diseño: FSBM (análisis en esfuerzos efectivos) y FSBUM (con Su; no se permite en seudo-estático)
FS_FRICCION_DRENADO = {"cm_cv_normal": 1.50, "cm_cv_maxima": 1.25, "cm_cv_sismo": 1.10}
FS_FRICCION_NO_DRENADO = {"cm_cv_normal": 1.80, "cm_cv_maxima": 1.40}

_REF = "NSR-10 H.4.4 / H.4.7"


@dataclass(frozen=True)
class Estrato:
    espesor_m: float
    gamma_kn_m3: float                      # peso unitario sobre el nivel freático
    comportamiento: Literal["drenado", "no_drenado"]
    gamma_sat_kn_m3: Optional[float] = None  # obligatorio si el estrato queda (en parte) bajo el nivel freático
    su_kpa: Optional[float] = None           # no drenado
    c_kpa: Optional[float] = None            # drenado: c'
    phi_deg: Optional[float] = None          # drenado: φ'
    k_lateral: Optional[float] = None        # drenado: K = σ'h/σ'v en el fuste (sin valor por defecto)
    qp_ult_kpa: Optional[float] = None       # drenado: resistencia última por punta del estudio geotécnico


@dataclass(frozen=True)
class Pilote:
    seccion: Literal["circular", "cuadrada"]
    ancho_m: float                           # diámetro o lado
    longitud_m: float                        # cabeza en z = 0 (superficie del perfil)
    tipo: Literal["hincado", "excavado"]

    @property
    def perimetro_m(self) -> float:
        return math.pi * self.ancho_m if self.seccion == "circular" else 4.0 * self.ancho_m

    @property
    def area_punta_m2(self) -> float:
        return math.pi * self.ancho_m ** 2 / 4.0 if self.seccion == "circular" else self.ancho_m ** 2


def _falla(msg: str) -> None:
    raise ValueError(f"{msg} ({_REF}).")


def alfa_nsr10(su_kpa: float) -> float:
    """α de la ecuación H.4.7-3, acotado a 1.0."""
    if not (math.isfinite(su_kpa) and su_kpa > 0):
        _falla(f"Su debe ser positivo y finito; se recibió {su_kpa!r}")
    return min(1.0, 0.2 + 0.8 * math.exp(0.35 - 2.0 * su_kpa / PA_KPA))


def _validar_estrato(e: Estrato, i: int) -> None:
    for nombre in ("espesor_m", "gamma_kn_m3"):
        v = getattr(e, nombre)
        if not (isinstance(v, (int, float)) and math.isfinite(v) and v > 0):
            _falla(f"Estrato {i}: {nombre} debe ser positivo; se recibió {v!r}")
    if e.comportamiento == "no_drenado":
        if e.su_kpa is None:
            _falla(f"Estrato {i} no drenado: falta Su")
        alfa_nsr10(e.su_kpa)
    elif e.comportamiento == "drenado":
        for nombre in ("c_kpa", "phi_deg", "k_lateral"):
            if getattr(e, nombre) is None:
                _falla(f"Estrato {i} drenado: falta {nombre} (no se asume valor por defecto)")
        if e.c_kpa < 0 or not (0 < e.phi_deg < 50) or not (0 < e.k_lateral <= 5):
            _falla(f"Estrato {i}: c' ≥ 0, 0 < φ' < 50° y 0 < K ≤ 5")
    else:
        _falla(f"Estrato {i}: comportamiento '{e.comportamiento}' no reconocido")


def _tramos(estratos: Sequence[Estrato], nivel_freatico_m: Optional[float], hasta_m: float):
    """Divide el perfil en tramos con σ'v lineal (cortes en bordes de estrato, nivel freático y punta).
    Devuelve [(i_estrato, z0, z1, σ'v en z0, σ'v en z1)]."""
    cortes = {0.0, hasta_m}
    z = 0.0
    limites = []
    for e in estratos:
        limites.append((z, z + e.espesor_m))
        z += e.espesor_m
        cortes.add(min(z, hasta_m))
    if nivel_freatico_m is not None and 0 < nivel_freatico_m < hasta_m:
        cortes.add(nivel_freatico_m)
    zs = sorted(c for c in cortes if c <= hasta_m)

    def estrato_en(zm: float) -> int:
        for i, (a, b) in enumerate(limites):
            if a <= zm < b:
                return i
        _falla(f"La punta (z = {hasta_m} m) queda por debajo del perfil definido ({limites[-1][1]} m)")

    sv, out = 0.0, []
    for z0, z1 in zip(zs, zs[1:]):
        i = estrato_en((z0 + z1) / 2.0)
        e = estratos[i]
        bajo_nf = nivel_freatico_m is not None and z0 >= nivel_freatico_m - 1e-12
        if bajo_nf and e.gamma_sat_kn_m3 is None:
            _falla(f"Estrato {i} queda bajo el nivel freático: falta gamma_sat_kn_m3")
        g = e.gamma_sat_kn_m3 if bajo_nf else e.gamma_kn_m3
        u0 = GAMMA_W * max(0.0, z0 - nivel_freatico_m) if nivel_freatico_m is not None else 0.0
        u1 = GAMMA_W * max(0.0, z1 - nivel_freatico_m) if nivel_freatico_m is not None else 0.0
        s0 = sv - u0
        sv += g * (z1 - z0)
        s1 = sv - u1
        if s1 <= 0:
            _falla(f"σ'v no positivo en z = {z1} m: revise pesos unitarios y nivel freático")
        out.append((i, z0, z1, s0, s1))
    return out


def fuste_tramo_nsr(e: Estrato, perimetro_m: float, z0: float, z1: float, s0: float, s1: float,
                    combinacion: Combinacion) -> dict:
    """Fricción última de un tramo con σ'v lineal (H.4.7-2 / H.4.7-3) y su factor de seguridad (Tabla H.2.4-1)."""
    if e.comportamiento == "no_drenado":
        fsl = exigir(combinacion, FS_FRICCION_NO_DRENADO, "NSR-10 H.2.4.2 y Tabla H.2.4-1 (FSBUM)",
                     "Combinación con Su (no se permite en análisis seudo-estático)")
        a = alfa_nsr10(e.su_kpa)
        tau_l = a * e.su_kpa
    else:
        fsl = exigir(combinacion, FS_FRICCION_DRENADO, "NSR-10 Tabla H.2.4-1 (FSBM)", "Combinación de carga")
        a = None
        tau_l = FACTOR_TAU_L * (e.c_kpa + e.k_lateral * 0.5 * (s0 + s1) * math.tan(math.radians(e.phi_deg)))
    return {"metodo": "α NSR-10 H.4.7-3" if a is not None else "K·σ'v·tanφ' NSR-10 H.4.7-2", "z0_m": z0, "z1_m": z1,
            "sigma_v_ef_medio_kpa": 0.5 * (s0 + s1), "alfa": a, "tau_l_kpa": tau_l, "fs_friccion": fsl,
            "qs_ult_kn": tau_l * perimetro_m * (z1 - z0)}


def punta_unitaria_nsr(ep: Estrato) -> float:
    """qp,ult (kPa): 9·Su en arcilla; en suelo drenado, el valor del estudio geotécnico."""
    if ep.comportamiento == "no_drenado":
        return NC_PUNTA_ARCILLA * ep.su_kpa
    if ep.qp_ult_kpa is None or not (ep.qp_ult_kpa > 0):
        _falla("Punta en suelo drenado: la NSR-10 no da fórmula; ingrese qp_ult_kpa del estudio geotécnico "
               "(con SPT use arena_spt.capacidad_spt, CCP-14 §10.7.3.8.6g / §10.8.3.5.2)")
    return ep.qp_ult_kpa


def capacidad_individual(estratos: Sequence[Estrato], pilote: Pilote, *, nivel_freatico_m: Optional[float],
                         combinacion: Combinacion) -> dict:
    """Capacidad última y admisible a compresión (kN) de un pilote individual."""
    if not estratos:
        _falla("Se requiere al menos un estrato")
    for i, e in enumerate(estratos):
        _validar_estrato(e, i)
    if not (pilote.ancho_m > 0 and pilote.longitud_m > 0):
        _falla("Ancho y longitud del pilote deben ser positivos")
    if nivel_freatico_m is not None and nivel_freatico_m < 0:
        _falla("El nivel freático no puede ser negativo (z medido desde la superficie)")
    fs_punta = exigir(combinacion, FS_PUNTA, "NSR-10 Tabla H.4.7-1", "Combinación de carga")
    p, L = pilote.perimetro_m, pilote.longitud_m
    tramos = _tramos(estratos, nivel_freatico_m, L)

    qs_ult = qs_adm = 0.0
    detalle = []
    for i, z0, z1, s0, s1 in tramos:
        d = fuste_tramo_nsr(estratos[i], p, z0, z1, s0, s1, combinacion)
        qs_ult += d["qs_ult_kn"]
        qs_adm += d["qs_ult_kn"] / d["fs_friccion"]
        detalle.append({"estrato": i, **d})

    i_punta = tramos[-1][0]
    ep = estratos[i_punta]
    qp_unit = punta_unitaria_nsr(ep)
    qp_ult = qp_unit * pilote.area_punta_m2
    qp_adm = qp_ult / fs_punta

    z_base_estrato = sum(e.espesor_m for e in estratos[: i_punta + 1])
    return {"qs_ult_kn": qs_ult, "qs_adm_kn": qs_adm, "qp_ult_kn": qp_ult, "qp_adm_kn": qp_adm,
            "q_ult_kn": qs_ult + qp_ult, "q_adm_kn": qs_adm + qp_adm, "fs_punta": fs_punta,
            "qp_unitaria_kpa": qp_unit, "estrato_punta": i_punta,
            "distancia_punta_a_base_estrato_m": z_base_estrato - L, "tramos": detalle}
