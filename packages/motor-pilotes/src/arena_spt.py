"""Capacidad axial a compresión en suelo granular a partir del SPT (CCP-14 §10.4.6.2.4, §10.7.3.8.6g y §10.8.3.5.2).

Ecuaciones transcritas del CCP-14 (Sección 10), verificadas sobre las páginas del PDF oficial. Unidades del CCP-14:
MPa y mm; aquí se convierten a kPa y m.

  Corrección por sobrecarga (10.4.6.2.4-1):  N1 = CN·N,  CN = 0.77·log10(1.92/σ'v[MPa]) ≤ 2.0
  Pilote hincado, Meyerhof (10.7.3.8.6g):
    punta  (g-1):  qp = 0.038·N1_60·Db/D ≤ qℓ          [MPa; Db y D en mm]
           qℓ = 0.4·N1_60 en arena y 0.3·N1_60 en limo no plástico
           (errata del CCP-14: el texto en SI repite «ocho veces N1_60 ksf» de la versión en unidades inglesas;
            8 ksf ≈ 0.38 MPa, coherente con 0.4)
    fuste  (g-2):  qs = 0.0019·N̄1_60 MPa   pilotes de desplazamiento (todos los de este motor: sección llena)
           (g-3):  qs = 0.00096·N̄1_60 MPa  pilotes H, sin desplazamiento (no aplica a las secciones del motor)
  Pila excavada, método β (10.8.3.5.2b):
    qs = β·σ'v ≤ 0.19 MPa,  z en mm a mitad del tramo
      arena, N60 ≥ 15:  β = 1.5 − 7.7e-3·√z             0.25 ≤ β ≤ 1.2
      arena, N60 < 15:  β = (N60/15)·(1.5 − 7.7e-3·√z)  0.25 ≤ β ≤ 1.2
      grava:            β = 2.0 − 0.00082·z^0.75         0.25 ≤ β ≤ 1.8 (comentario C10.8.3.5.2b)
    punta (10.8.3.5.2c):  qp = 0.057·N60 MPa ≤ 3.0 MPa para N60 ≤ 50
      (errata del CCP-14: imprime «Para 0.057N60 ≤ 50, qp = 1.2N60», dimensionalmente imposible; la forma correcta es
       la de AASHTO LRFD. Con N60 > 50 el material es geomaterial intermedio: próximamente.)

Factores de seguridad: el CCP-14 es LRFD (factores de resistencia). Para mantener un solo criterio en el motor, la
capacidad admisible usa los factores de la NSR-10 (fricción FSBM de la Tabla H.2.4-1 y punta FS_ICP de la Tabla
H.4.7-1), igual que el camino drenado de `axial.py`. La capacidad última es la del CCP-14 sin factores.

Nordlund/Thurman (10.7.3.8.6f) queda próximamente: todos sus coeficientes (Kδ, CF, δ/φ, αt, N'q) salen de las figuras
10.7.3.8.6f-1 a -9, que solo existen como gráficas y hay que digitalizarlas antes de implementarlo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Optional, Sequence

from .axial import FS_FRICCION_DRENADO, FS_PUNTA, Combinacion, Pilote, _tramos, exigir

_REF = "CCP-14 §10.4.6.2.4 / §10.7.3.8.6g / §10.8.3.5.2"
CN_MAX = 2.0
QS_MAX_BETA_KPA = 190.0
QP_MAX_EXCAVADO_KPA = 3000.0
N60_MAX_EXCAVADO = 50.0
SUBTRAMO_M = 0.5          # el fuste se integra en subtramos de ≤ 0.5 m: CN y β no son lineales en z
SueloSPT = Literal["arena", "limo_no_plastico", "grava"]


@dataclass(frozen=True)
class EstratoSPT:
    espesor_m: float
    gamma_kn_m3: float                        # sobre el nivel freático
    n60: float                                # SPT corregido por energía al 60 %
    suelo: SueloSPT
    gamma_sat_kn_m3: Optional[float] = None   # obligatorio si el estrato queda (en parte) bajo el nivel freático


def _falla(msg: str) -> None:
    raise ValueError(f"{msg} ({_REF}).")


def cn_ccp14(sigma_v_ef_kpa: float) -> float:
    """CN de la ecuación 10.4.6.2.4-1, con σ'v en kPa; acotado a 2.0."""
    if not (math.isfinite(sigma_v_ef_kpa) and sigma_v_ef_kpa > 0):
        _falla(f"σ'v debe ser positivo; se recibió {sigma_v_ef_kpa!r}")
    return min(CN_MAX, 0.77 * math.log10(1.92 / (sigma_v_ef_kpa / 1000.0)))


def beta_ccp14(z_m: float, n60: float, suelo: SueloSPT) -> float:
    """β del método de las pilas excavadas (10.8.3.5.2b), z a mitad del tramo en m."""
    z_mm = z_m * 1000.0
    if suelo == "grava":
        return min(1.8, max(0.25, 2.0 - 0.00082 * z_mm ** 0.75))
    b = 1.5 - 7.7e-3 * math.sqrt(z_mm)
    if n60 < 15:
        b *= n60 / 15.0
    return min(1.2, max(0.25, b))


def _validar(estratos: Sequence[EstratoSPT], pilote: Pilote) -> None:
    if not estratos:
        _falla("Se requiere al menos un estrato")
    for i, e in enumerate(estratos):
        for nombre in ("espesor_m", "gamma_kn_m3", "n60"):
            v = getattr(e, nombre)
            if not (isinstance(v, (int, float)) and math.isfinite(v) and v > 0):
                _falla(f"Estrato {i}: {nombre} debe ser positivo; se recibió {v!r}")
        if e.suelo not in ("arena", "limo_no_plastico", "grava"):
            _falla(f"Estrato {i}: suelo '{e.suelo}' no reconocido (arena, limo_no_plastico o grava)")
        if pilote.tipo == "excavado" and e.suelo == "limo_no_plastico":
            _falla(f"Estrato {i}: el método β del CCP-14 §10.8.3.5.2 es para arena y grava; limo próximamente")
    if not (pilote.ancho_m > 0 and pilote.longitud_m > pilote.ancho_m):
        _falla("Se requiere longitud > ancho > 0")


def capacidad_spt(estratos: Sequence[EstratoSPT], pilote: Pilote, *, nivel_freatico_m: Optional[float],
                  combinacion: Combinacion) -> dict:
    """Capacidad última y admisible a compresión (kN) de un pilote individual en suelo granular con SPT."""
    _validar(estratos, pilote)
    if nivel_freatico_m is not None and nivel_freatico_m < 0:
        _falla("El nivel freático no puede ser negativo (z medido desde la superficie)")
    fs_punta = exigir(combinacion, FS_PUNTA, "NSR-10 Tabla H.4.7-1", "Combinación de carga")
    fs_fuste = exigir(combinacion, FS_FRICCION_DRENADO, "NSR-10 Tabla H.2.4-1 (FSBM)", "Combinación de carga")
    L, D, p = pilote.longitud_m, pilote.ancho_m, pilote.perimetro_m
    tramos = _tramos(estratos, nivel_freatico_m, L)

    qs_ult, detalle = 0.0, []
    for i, z0, z1, s0, s1 in tramos:
        e = estratos[i]
        n = max(1, math.ceil((z1 - z0) / SUBTRAMO_M - 1e-9))
        for k in range(n):
            a, b = z0 + (z1 - z0) * k / n, z0 + (z1 - z0) * (k + 1) / n
            zm = 0.5 * (a + b)
            sm = s0 + (s1 - s0) * (zm - z0) / (z1 - z0)   # σ'v es lineal dentro del tramo
            if pilote.tipo == "hincado":
                n1 = cn_ccp14(sm) * e.n60
                q_unit, coef = 1.9 * n1, {"n1_60": n1}     # 0.0019·N1_60 MPa = 1.9·N1_60 kPa
            else:
                beta = beta_ccp14(zm, e.n60, e.suelo)
                q_unit, coef = min(QS_MAX_BETA_KPA, beta * sm), {"beta": beta}
            q = q_unit * p * (b - a)
            qs_ult += q
            detalle.append({"estrato": i, "z0_m": a, "z1_m": b, "sigma_v_ef_kpa": sm, "qs_kpa": q_unit,
                            "qs_ult_kn": q, **coef})

    i_punta, _, _, _, s_punta = tramos[-1]
    ep = estratos[i_punta]
    z_techo = sum(e.espesor_m for e in estratos[:i_punta])
    if pilote.tipo == "hincado":
        n1p = cn_ccp14(s_punta) * ep.n60
        db = L - z_techo                                    # penetración en el estrato de apoyo
        q_lim = (300.0 if ep.suelo == "limo_no_plastico" else 400.0) * n1p
        qp_unit = min(38.0 * n1p * db / D, q_lim)          # 0.038·N1_60·Db/D MPa = 38·… kPa
        punta = {"metodo_punta": "Meyerhof (CCP-14 10.7.3.8.6g-1)", "n1_60_punta": n1p, "db_m": db,
                 "q_limite_kpa": q_lim, "limitada": qp_unit >= q_lim}
    else:
        if ep.n60 > N60_MAX_EXCAVADO:
            _falla(f"N60 = {ep.n60} > 50 en la punta: geomaterial intermedio (CCP-14 §10.8.3.5.4), próximamente")
        qp_unit = min(57.0 * ep.n60, QP_MAX_EXCAVADO_KPA)  # 0.057·N60 MPa = 57·N60 kPa
        punta = {"metodo_punta": "CCP-14 10.8.3.5.2c-1", "limitada": qp_unit >= QP_MAX_EXCAVADO_KPA}
    qp_ult = qp_unit * pilote.area_punta_m2

    return {"metodo_fuste": ("Meyerhof SPT (CCP-14 10.7.3.8.6g-2)" if pilote.tipo == "hincado"
                             else "β (CCP-14 10.8.3.5.2b)"),
            "qs_ult_kn": qs_ult, "qs_adm_kn": qs_ult / fs_fuste, "qp_ult_kn": qp_ult, "qp_adm_kn": qp_ult / fs_punta,
            "q_ult_kn": qs_ult + qp_ult, "q_adm_kn": qs_ult / fs_fuste + qp_ult / fs_punta,
            "fs_friccion": fs_fuste, "fs_punta": fs_punta, "qp_unitaria_kpa": qp_unit, "estrato_punta": i_punta,
            "sigma_v_ef_punta_kpa": s_punta,
            "distancia_punta_a_base_estrato_m": z_techo + ep.espesor_m - L, **punta, "tramos": detalle}
