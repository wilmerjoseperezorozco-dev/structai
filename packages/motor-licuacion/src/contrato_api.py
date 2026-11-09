"""Salida con contrato uniforme de motor-licuacion (#137): evaluación simplificada por SPT (NCEER) con LPI de Iwasaki."""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .spt import (corregir_finos, crr_spt, csr_seed_idriss, indice_potencial_licuacion, msf_idriss,  # noqa: E402
                  N_NO_LICUABLE, Z_MAX_M)

GAMMA_AGUA_KN_M3 = 9.81
_FS_BORDE = (0.9, 1.2)          # FS cercano a 1: el resultado cambia de veredicto con incertidumbres pequeñas
_FINOS_BORDE_PCT = 35.0
_Z_KSIGMA_M = 15.0              # NCEER: por debajo de ~15 m el factor Kσ deja de ser despreciable
_REF = "NSR-10 Título H"


class EstratoSPT(BaseModel):
    z_top_m: float = Field(..., ge=0, allow_inf_nan=False)
    z_base_m: float = Field(..., gt=0, allow_inf_nan=False)
    gamma_kn_m3: float = Field(..., gt=0, allow_inf_nan=False, description="Peso unitario sobre el nivel freático")
    gamma_sat_kn_m3: float = Field(..., gt=0, allow_inf_nan=False)
    n1_60: float = Field(..., ge=0, allow_inf_nan=False, description="(N1)60 ya corregido por energía, barra, diámetro y sobrecarga")
    finos_pct: float = Field(..., ge=0, le=100, allow_inf_nan=False)
    no_plastico: bool = Field(..., description="False si los finos son arcilla plástica (el método no aplica)")


class SolicitudLicuacionSPT(BaseModel):
    amax_g: float = Field(..., gt=0, le=2.0, allow_inf_nan=False, description="Aceleración máxima en superficie, en g")
    mw: float = Field(..., allow_inf_nan=False)
    nivel_freatico_m: Optional[float] = Field(..., ge=0, description="null = sin nivel freático (queda declarado)")
    estratos: list[EstratoSPT] = Field(..., min_length=1, max_length=40)


def _validar_perfil(estratos: list[EstratoSPT]) -> None:
    previo = 0.0
    for e in estratos:
        if abs(e.z_top_m - previo) > 1e-9 or e.z_base_m <= e.z_top_m:
            raise ValueError(f"Los estratos deben ser contiguos desde 0 m y de espesor positivo ({_REF}).")
        if not (e.gamma_sat_kn_m3 > GAMMA_AGUA_KN_M3 and e.gamma_sat_kn_m3 >= e.gamma_kn_m3):
            raise ValueError(f"El peso unitario saturado debe ser mayor que el del agua ({GAMMA_AGUA_KN_M3} kN/m³) y no menor que γ ({_REF}).")
        previo = e.z_base_m


def _esfuerzos(estratos: list[EstratoSPT], z: float, nf: Optional[float]) -> tuple[float, float]:
    """(σv, σ'v) a la profundidad z integrando γ sobre el nivel freático y γsat bajo él."""
    sigma = 0.0
    for e in estratos:
        a, b = e.z_top_m, min(e.z_base_m, z)
        if b <= a:
            break
        seco = (b - a) if nf is None else max(0.0, min(b, nf) - a)
        sigma += e.gamma_kn_m3 * seco + e.gamma_sat_kn_m3 * ((b - a) - seco)
    u = 0.0 if nf is None else GAMMA_AGUA_KN_M3 * max(0.0, z - nf)
    return sigma, sigma - u


def _clasificar_lpi(lpi: float) -> str:
    if lpi <= 0.0:
        return "ninguno"
    return "bajo" if lpi <= 5.0 else "alto" if lpi <= 15.0 else "muy alto"


def _evaluar_estrato(e: EstratoSPT, s: SolicitudLicuacionSPT) -> tuple[dict, Optional[tuple], bool]:
    """(fila de resultado, intervalo para el LPI o None, en_borde por este estrato)."""
    nf = s.nivel_freatico_m
    fila: dict = {"z_top_m": e.z_top_m, "z_base_m": e.z_base_m, "fs": None, "estado": ""}
    borde = e.finos_pct > _FINOS_BORDE_PCT or e.z_base_m > Z_MAX_M
    if nf is None:
        fila["estado"] = "sin nivel freático: no saturado"
        return fila, None, borde
    z_sat = max(e.z_top_m, nf)
    if z_sat >= e.z_base_m:
        fila["estado"] = "sobre el nivel freático"
        return fila, None, borde
    if not e.no_plastico:
        fila["estado"] = "fino plástico: método no aplicable (evaluar por otro criterio)"
        return fila, None, True
    z_eval = min((z_sat + e.z_base_m) / 2.0, Z_MAX_M)
    sv, sve = _esfuerzos(s.estratos, z_eval, nf)
    n_cs, borde_fc = corregir_finos(n1_60=e.n1_60, finos_pct=e.finos_pct)
    fila.update(z_evaluacion_m=z_eval, sigma_v_kpa=sv, sigma_v_efectivo_kpa=sve, n1_60cs=n_cs)
    borde = borde or borde_fc or z_eval > _Z_KSIGMA_M
    if n_cs >= N_NO_LICUABLE:
        fila["estado"] = "no licuable ((N1)60cs ≥ 30)"
        return fila, None, borde
    csr = csr_seed_idriss(amax_g=s.amax_g, sigma_v_kpa=sv, sigma_v_efectivo_kpa=sve, z_m=z_eval)
    crr = crr_spt(n_cs)
    fs = crr * msf_idriss(s.mw) / csr
    fila.update(csr=csr, crr=crr, fs=fs, estado="licuable" if fs < 1.0 else "no licúa")
    return fila, (z_sat, e.z_base_m, fs), borde


def licuacion_spt_contrato(s: SolicitudLicuacionSPT) -> ResultadoMotor:
    _validar_perfil(s.estratos)
    msf_idriss(s.mw)                                   # valida la magnitud antes de cualquier cálculo
    filas, intervalos, borde = [], [], False
    for e in s.estratos:
        fila, intervalo, b = _evaluar_estrato(e, s)
        filas.append(fila)
        borde = borde or b
        if intervalo:
            intervalos.append(intervalo)
    lpi = indice_potencial_licuacion(intervalos) if intervalos else 0.0
    fs_vals = [f["fs"] for f in filas if f["fs"] is not None]
    fs_min = min(fs_vals) if fs_vals else None
    if fs_min is not None and _FS_BORDE[0] <= fs_min <= _FS_BORDE[1]:
        borde = True
    supuestos = [
        "Solo SPT: (N1)60 ya corregido por energía, longitud de barra, diámetro y sobrecarga; el motor corrige solo por finos.",
        "Procedimiento simplificado de Seed e Idriss (1971) con rd, MSF y CRR de NCEER (Youd et al., 2001); CRR para Mw 7,5 y σ'v = 100 kPa. "
        "No se aplican los factores Kσ (σ'v > 100 kPa) ni Kα (terreno inclinado): la marca de borde se activa bajo 15 m.",
        "amax es la aceleración en superficie del estudio de respuesta de sitio o de la microzonificación; el motor no la calcula (NSR-10 Título A).",
        "Cada estrato se evalúa en el centro de su parte saturada (tope en el nivel freático si lo cruza).",
        "Finos plásticos (arcilla) y gravas no se evalúan con este método. Estratos con (N1)60cs ≥ 30 se declaran no licuables.",
        "LPI de Iwasaki et al. (1978) hasta 20 m: ninguno 0 · bajo (0,5] · alto (5,15] · muy alto > 15. Mide potencial en superficie, no daño.",
        "No incluye asentamiento post-licuación ni desplazamiento lateral, ni CPT.",
    ]
    if s.nivel_freatico_m is None:
        supuestos.append("Sin nivel freático declarado: ningún estrato se considera saturado y no se evalúa licuación.")
    return ResultadoMotor(
        valor={"estratos": filas, "lpi": lpi, "clasificacion_lpi": _clasificar_lpi(lpi), "fs_minimo": fs_min},
        unidad_si="Esfuerzos en kPa; profundidades en m; CSR, CRR y FS adimensionales",
        ecuacion="CSR = 0,65·(amax/g)·(σv/σ'v)·rd; FS = CRR7,5·MSF/CSR; CRR = 1/(34−N) + N/135 + 50/(10N+45)² − 1/200; "
                 "MSF = 10^2,24/Mw^2,56; LPI = ∫₀²⁰ (1−FS)·(10−0,5z) dz",
        referencia_normativa="Youd et al. (2001) NCEER · Seed e Idriss (1971) · Iwasaki et al. (1978) · NSR-10 Título H",
        supuestos=supuestos,
        en_borde_dominio=bool(borde),
    )
