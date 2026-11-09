"""Salida con contrato uniforme de motor-licuacion (#137): evaluación simplificada por SPT (NCEER) con LPI de Iwasaki."""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

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
_GAMMA_MAX = 30.0
_SIGMA_REF_KPA = 100.0         # presión de referencia del CRR: por encima, Kσ < 1 y su omisión es no conservadora
_LPI_RUIDO = 1e-6


class EstratoSPT(BaseModel):
    model_config = ConfigDict(strict=True)

    z_top_m: float = Field(..., ge=0, le=1000, allow_inf_nan=False)
    z_base_m: float = Field(..., gt=0, le=1000, allow_inf_nan=False)
    gamma_kn_m3: float = Field(..., gt=0, le=_GAMMA_MAX, allow_inf_nan=False, description="Peso unitario sobre el nivel freático")
    gamma_sat_kn_m3: float = Field(..., gt=0, le=_GAMMA_MAX, allow_inf_nan=False)
    n1_60: float = Field(..., ge=0, le=100, allow_inf_nan=False, description="(N1)60 ya corregido por energía, barra, diámetro y sobrecarga")
    finos_pct: float = Field(..., ge=0, le=100, allow_inf_nan=False)
    no_plastico: bool = Field(..., description="False si los finos son arcilla plástica (el método no aplica)")


class SolicitudLicuacionSPT(BaseModel):
    model_config = ConfigDict(strict=True)

    amax_g: float = Field(..., gt=0, le=2.0, allow_inf_nan=False, description="Aceleración máxima en superficie, en g")
    mw: float = Field(..., allow_inf_nan=False)
    nivel_freatico_m: Optional[float] = Field(..., ge=0, le=200, allow_inf_nan=False, description="null = sin nivel freático (queda declarado)")
    estratos: list[EstratoSPT] = Field(..., min_length=1, max_length=40)
    paso_m: float = Field(default=1.0, gt=0, le=2.0, allow_inf_nan=False, description="Espesor máximo de subcapa para integrar FS(z) y el LPI")


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
    if lpi < _LPI_RUIDO:
        return "ninguno"
    return "bajo" if lpi <= 5.0 else "alto" if lpi <= 15.0 else "muy alto"


def _fila(e: EstratoSPT, categoria: str, estado: str, **extra) -> dict:
    return {"z_top_m": e.z_top_m, "z_base_m": e.z_base_m, "categoria": categoria, "estado": estado, "fs": None, **extra}


def _subcapas(z_sat: float, z_base: float, paso: float) -> list[tuple[float, float]]:
    n = max(1, math.ceil((z_base - z_sat) / paso - 1e-9))
    h = (z_base - z_sat) / n
    return [(z_sat + k * h, z_sat + (k + 1) * h) for k in range(n)]


def _evaluar_estrato(e: EstratoSPT, s: SolicitudLicuacionSPT) -> tuple[dict, list[tuple], bool]:
    """(fila de resultado, intervalos (z0, z1, FS) para el LPI, en_borde por este estrato)."""
    nf = s.nivel_freatico_m
    borde = e.finos_pct > _FINOS_BORDE_PCT
    if nf is None:
        return _fila(e, "sin_nivel_freatico", "sin nivel freático: no saturado"), [], borde
    z_sat = max(e.z_top_m, nf)
    if z_sat >= e.z_base_m:
        return _fila(e, "sobre_nivel_freatico", "sobre el nivel freático"), [], borde
    if not e.no_plastico:
        return _fila(e, "fino_plastico", "fino plástico: método no aplicable (evaluar por otro criterio)"), [], True
    n_cs, borde_fc = corregir_finos(n1_60=e.n1_60, finos_pct=e.finos_pct)
    borde = borde or borde_fc
    if n_cs >= N_NO_LICUABLE:
        return _fila(e, "no_licuable", "no licuable ((N1)60cs ≥ 30)", n1_60cs=n_cs), [], borde
    msf = msf_idriss(s.mw)
    subcapas, intervalos = [], []
    for z0, z1 in _subcapas(z_sat, e.z_base_m, s.paso_m):
        zc = (z0 + z1) / 2.0
        if zc > Z_MAX_M:
            subcapas.append({"z_top_m": z0, "z_base_m": z1, "categoria": "fuera_de_dominio", "fs": None})
            borde = True
            continue
        sv, sve = _esfuerzos(s.estratos, zc, nf)
        csr = csr_seed_idriss(amax_g=s.amax_g, sigma_v_kpa=sv, sigma_v_efectivo_kpa=sve, z_m=zc)
        crr = crr_spt(n_cs)
        fs = crr * msf / csr
        borde = borde or sve > _SIGMA_REF_KPA
        subcapas.append({"z_top_m": z0, "z_base_m": z1, "categoria": "evaluado", "z_evaluacion_m": zc, "sigma_v_kpa": sv,
                         "sigma_v_efectivo_kpa": sve, "csr": csr, "crr": crr, "fs": fs})
        intervalos.append((z0, z1, fs))
    evaluadas = [c for c in subcapas if c["categoria"] == "evaluado"]
    if not evaluadas:
        fila = _fila(e, "fuera_de_dominio", f"fuera del dominio del método (> {Z_MAX_M:g} m)", n1_60cs=n_cs, subcapas=subcapas)
        return fila, [], True
    fs_min = min(c["fs"] for c in evaluadas)
    n_lic = sum(1 for c in evaluadas if c["fs"] < 1.0)
    estado = f"licuable en {n_lic} de {len(evaluadas)} subcapas" if n_lic else "no licúa"
    fila = _fila(e, "evaluado", estado, n1_60cs=n_cs, subcapas=subcapas)
    fila["fs"] = fs_min
    return fila, intervalos, borde


def licuacion_spt_contrato(s: SolicitudLicuacionSPT) -> ResultadoMotor:
    _validar_perfil(s.estratos)
    msf_idriss(s.mw)                                   # valida la magnitud antes de cualquier cálculo
    filas, intervalos, borde = [], [], False
    for e in s.estratos:
        fila, ivs, bandera = _evaluar_estrato(e, s)
        filas.append(fila)
        borde = borde or bandera
        intervalos.extend(ivs)
    lpi = indice_potencial_licuacion(intervalos) if intervalos else 0.0
    fs_vals = [f["fs"] for f in filas if f["fs"] is not None]
    fs_min = min(fs_vals) if fs_vals else None
    if fs_min is not None and _FS_BORDE[0] <= fs_min <= _FS_BORDE[1]:
        borde = True
    supuestos = [
        "Solo SPT: (N1)60 ya corregido por energía, longitud de barra, diámetro y sobrecarga; el motor corrige solo por finos (Idriss y Seed, en NCEER).",
        "Procedimiento simplificado de Seed e Idriss (1971) con rd, MSF y CRR de NCEER (Youd et al., 2001); CRR para Mw 7,5 y σ'v = 100 kPa.",
        "No se aplican Kσ (σ'v > 100 kPa) ni Kα (terreno inclinado): ambas omisiones sobreestiman FS, es decir, sesgo no conservador. "
        "La marca de borde se activa donde σ'v supera 100 kPa.",
        "MSF de Idriss sin cota para Mw < 7,5 (Mw 5 da MSF 2,8): para magnitudes bajas los FS son optimistas.",
        f"FS(z) y LPI se integran por subcapas de a lo sumo {s.paso_m:g} m, evaluadas en su centro, como en el índice de Iwasaki; "
        f"dominio del método ≤ {Z_MAX_M:g} m: lo que quede más profundo se declara fuera de dominio y no se calcula.",
        "Nivel freático constante: no se analiza nivel alto ni estacional. Capilaridad ignorada: σ'v se calcula sin succión sobre el nivel freático.",
        "amax es la aceleración en superficie del estudio de respuesta de sitio o de la microzonificación; el motor no la calcula (NSR-10 Título A).",
        "Finos plásticos no se evalúan con este método y estratos con (N1)60cs ≥ 30 se declaran no licuables; el motor no tiene campo de "
        "granulometría y trata todo estrato no plástico como arena o limo arenoso.",
        "Los estratos no evaluados (secos, finos plásticos, N ≥ 30, fuera de dominio) aportan 0 al LPI: con finos plásticos saturados el LPI es una cota inferior.",
        "LPI de Iwasaki et al. (1978) hasta 20 m: ninguno 0 · bajo (0, 5] · alto (5, 15] · muy alto > 15. Mide potencial en superficie, no daño.",
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
