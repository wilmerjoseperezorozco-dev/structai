"""Capacidad axial a compresión de un pilote individual en perfil mixto: cada estrato con su propio método (#118).

Caso típico colombiano (llanura del Cauca, Costa Caribe, aluvial de Bogotá): capas de arcilla y de arena alternadas en
el mismo fuste. Cada estrato se evalúa con el método que le corresponde y con su factor de seguridad:

  Estrato no drenado (arcilla)       α·Su, NSR-10 H.4.7-3                FSBUM (Tabla H.2.4-1)
  Estrato drenado con K y φ'          2/3·(c' + K·σ'v·tanφ'), H.4.7-2    FSBM
  EstratoSPT (arena, limo NP, grava)  Meyerhof (hincado) o β (excavado),  FSBM
                                      CCP-14 §10.7.3.8.6g / §10.8.3.5.2

Punta según el estrato de apoyo: 9·Su en arcilla, qp del estudio en drenado con K, o la del CCP-14 con SPT. En Meyerhof,
Db es la penetración dentro del estrato granular de apoyo (lo que atraviesa en arcilla no cuenta como empotramiento).
σ'v se calcula de forma continua en todo el perfil, sin importar el tipo de estrato.

Las funciones de una sola familia (`axial.capacidad_individual`, `arena_spt.capacidad_spt`) dan el mismo resultado que
esta con un perfil homogéneo en tipo; las pruebas lo verifican.
"""
from __future__ import annotations

from typing import Optional, Sequence, Union

from .arena_spt import EstratoSPT, _validar as _validar_spt, fuste_tramo_spt, punta_spt
from .axial import (FS_FRICCION_DRENADO, FS_PUNTA, Combinacion, Estrato, Pilote, _falla, _tramos, _validar_estrato, exigir,
                    fuste_tramo_nsr, punta_unitaria_nsr)

EstratoMixto = Union[Estrato, EstratoSPT]


def capacidad_mixta(estratos: Sequence[EstratoMixto], pilote: Pilote, *, nivel_freatico_m: Optional[float],
                    combinacion: Combinacion) -> dict:
    """Capacidad última y admisible a compresión (kN) en un perfil con estratos de distinto tipo."""
    if not estratos:
        _falla("Se requiere al menos un estrato")
    for i, e in enumerate(estratos):
        if isinstance(e, EstratoSPT):
            _validar_spt([e], pilote)
        elif isinstance(e, Estrato):
            _validar_estrato(e, i)
        else:
            _falla(f"Estrato {i}: tipo {type(e).__name__} no reconocido (Estrato o EstratoSPT)")
    if not (pilote.ancho_m > 0 and pilote.longitud_m > pilote.ancho_m):
        _falla("Se requiere longitud > ancho > 0")
    if nivel_freatico_m is not None and nivel_freatico_m < 0:
        _falla("El nivel freático no puede ser negativo (z medido desde la superficie)")
    fs_punta = exigir(combinacion, FS_PUNTA, "NSR-10 Tabla H.4.7-1", "Combinación de carga")
    L, p = pilote.longitud_m, pilote.perimetro_m
    tramos = _tramos(estratos, nivel_freatico_m, L)

    qs_ult = qs_adm = 0.0
    detalle = []
    por_estrato: dict[int, float] = {}
    for i, z0, z1, s0, s1 in tramos:
        e = estratos[i]
        if isinstance(e, EstratoSPT):
            fsl = exigir(combinacion, FS_FRICCION_DRENADO, "NSR-10 Tabla H.2.4-1 (FSBM)", "Combinación de carga")
            partes = [{**d, "fs_friccion": fsl} for d in fuste_tramo_spt(e, pilote, z0, z1, s0, s1)]
        else:
            partes = [fuste_tramo_nsr(e, p, z0, z1, s0, s1, combinacion)]
        for d in partes:
            qs_ult += d["qs_ult_kn"]
            qs_adm += d["qs_ult_kn"] / d["fs_friccion"]
            por_estrato[i] = por_estrato[i] + d["qs_ult_kn"] if i in por_estrato else d["qs_ult_kn"]
            detalle.append({"estrato": i, **d})

    i_punta, _, _, _, s_punta = tramos[-1]
    ep = estratos[i_punta]
    z_techo = sum(e.espesor_m for e in estratos[:i_punta])
    if isinstance(ep, EstratoSPT):
        qp_unit, punta = punta_spt(ep, pilote, s_punta, L - z_techo)
    else:
        qp_unit = punta_unitaria_nsr(ep)
        punta = {"metodo_punta": "9·Su (Skempton)" if ep.comportamiento == "no_drenado" else "qp del estudio geotécnico"}
    qp_ult = qp_unit * pilote.area_punta_m2

    return {"qs_ult_kn": qs_ult, "qs_adm_kn": qs_adm, "qp_ult_kn": qp_ult, "qp_adm_kn": qp_ult / fs_punta,
            "q_ult_kn": qs_ult + qp_ult, "q_adm_kn": qs_adm + qp_ult / fs_punta, "fs_punta": fs_punta,
            "qp_unitaria_kpa": qp_unit, "estrato_punta": i_punta, "sigma_v_ef_punta_kpa": s_punta,
            "distancia_punta_a_base_estrato_m": z_techo + ep.espesor_m - L,
            "qs_ult_por_estrato_kn": por_estrato, **punta, "tramos": detalle}

