"""Salida con contrato uniforme de motor-redes (#138): red mallada en estado permanente (método del gradiente)."""
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .gradiente import resolver_red  # noqa: E402

_MARGEN_BORDE = 0.10           # a menos de 10 % de un límite declarado, el veredicto es sensible a la incertidumbre
_D_MIN_HW_M = 0.05             # Hazen-Williams: diámetros < 50 mm fuera de validez
_V_MIN_HW_MS = 0.1             # a muy baja velocidad Hazen-Williams subestima la pérdida
_C_HW_RANGO = (60.0, 160.0)    # rango práctico de Hazen-Williams; fuera de él el coeficiente es sospechoso


class NudoRed(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str = Field(..., min_length=1, max_length=40)
    cota_m: float = Field(..., ge=-500, le=6000, allow_inf_nan=False)
    demanda_m3s: float = Field(default=0.0, ge=0, le=100, allow_inf_nan=False)
    carga_fija_m: Optional[float] = Field(default=None, ge=-500, le=7000, allow_inf_nan=False,
                                          description="Carga total (cota piezométrica) de un embalse o tanque de nivel constante")


class TramoRed(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str = Field(..., min_length=1, max_length=40)
    desde: str = Field(..., min_length=1, max_length=40)
    hasta: str = Field(..., min_length=1, max_length=40)
    longitud_m: float = Field(..., gt=0, le=200000, allow_inf_nan=False)
    diametro_m: float = Field(..., gt=0, le=5, allow_inf_nan=False)
    c_hw: float = Field(..., gt=0, le=200, allow_inf_nan=False, description="Coeficiente de Hazen-Williams")


class SolicitudRed(BaseModel):
    model_config = ConfigDict(strict=True)
    nodos: list[NudoRed] = Field(..., min_length=2, max_length=2000)
    tramos: list[TramoRed] = Field(..., min_length=1, max_length=4000)
    presion_min_m: Optional[float] = Field(default=None, ge=0, le=500, allow_inf_nan=False,
                                           description="Presión mínima de servicio exigida (m.c.a.); null = no se verifica")
    presion_max_m: Optional[float] = Field(default=None, gt=0, le=500, allow_inf_nan=False)
    velocidad_max_ms: Optional[float] = Field(default=None, gt=0, le=20, allow_inf_nan=False)


def _verificar_limites(res: dict, s: SolicitudRed):
    incumple, borde = [], False
    libres = [n.id for n in s.nodos if n.carga_fija_m is None]
    for nid in libres:
        p = res["nodos"][nid]["presion_m"]
        if s.presion_min_m is not None:
            if p < s.presion_min_m:
                incumple.append(f"nudo {nid}: presión {p:.2f} m < mínima {s.presion_min_m:g} m")
            elif p < s.presion_min_m * (1 + _MARGEN_BORDE):
                borde = True
        if s.presion_max_m is not None:
            if p > s.presion_max_m:
                incumple.append(f"nudo {nid}: presión {p:.2f} m > máxima {s.presion_max_m:g} m")
            elif p > s.presion_max_m * (1 - _MARGEN_BORDE):
                borde = True
    if s.velocidad_max_ms is not None:
        for tid, v in res["tramos"].items():
            vel = v["velocidad_ms"]
            if vel > s.velocidad_max_ms:
                incumple.append(f"tramo {tid}: velocidad {vel:.2f} m/s > máxima {s.velocidad_max_ms:g} m/s")
            elif vel > s.velocidad_max_ms * (1 - _MARGEN_BORDE):
                borde = True
    return incumple, borde


def red_permanente_contrato(s: SolicitudRed) -> ResultadoMotor:
    res = resolver_red([n.model_dump() for n in s.nodos], [t.model_dump() for t in s.tramos])
    incumple, borde = _verificar_limites(res, s)
    fuera_c = [t.id for t in s.tramos if not (_C_HW_RANGO[0] <= t.c_hw <= _C_HW_RANGO[1])]
    presiones_neg = [nid for nid, v in res["nodos"].items() if v["presion_m"] < 0]
    incumple.extend(f"nudo {nid}: presión negativa ({res['nodos'][nid]['presion_m']:.2f} m), inalcanzable sin cavitación o entrada de aire"
                    for nid in presiones_neg)
    finos = [t.id for t in s.tramos if t.diametro_m < _D_MIN_HW_M]
    lentos = [tid for tid, v in res["tramos"].items() if v["velocidad_ms"] < _V_MIN_HW_MS]
    borde = borde or bool(fuera_c) or bool(presiones_neg) or bool(finos) or bool(lentos)
    hay_limites = not (s.presion_min_m is None and s.presion_max_m is None and s.velocidad_max_ms is None)
    supuestos = [
        "Estado permanente con demandas constantes en los nudos; sin bombas, válvulas, tanques de nivel variable ni periodo extendido.",
        "Pérdidas por fricción de Hazen-Williams en SI (h = 10,67·L·Q^1,852/(C^1,852·D^4,871)); sin pérdidas menores (accesorios).",
        "Hazen-Williams es válido para agua a temperatura ambiente en flujo turbulento y diámetros ≥ 50 mm; a velocidades muy bajas subestima la pérdida.",
        "Los nudos con carga fija son embalses o tanques de nivel constante: el caudal que entregan sale de la solución, no es dato.",
        "El caudal es positivo de «desde» hacia «hasta»; el signo no es un error si el sentido real es inverso.",
        "Las presiones son carga de presión (carga total − cota); presión negativa indica nudo por encima de la línea piezométrica.",
        "Límites de presión y velocidad: los fija quien consulta; el motor no asume valores de norma (verificar en RAS 2000 Título B).",
        "Resolución numérica: caudales cuya pérdida de carga queda bajo ~1e-12 m (redondeo de una carga de decenas de metros) no se distinguen de cero.",
        "Método del gradiente (Todini y Pilati, 1988) con Newton-Raphson y reducción de paso; si no converge falla con error.",
    ]
    if not hay_limites:
        supuestos.append("No se declaró ningún límite de servicio: no se verificó cumplimiento.")
    if fuera_c:
        supuestos.append(f"Coeficiente C fuera de {_C_HW_RANGO[0]:g}–{_C_HW_RANGO[1]:g} en los tramos {fuera_c}: revisar material y edad de la tubería.")
    if presiones_neg:
        supuestos.append(f"Presión negativa en {presiones_neg}: no es alcanzable sin cavitación o entrada de aire.")
    if finos:
        supuestos.append(f"Diámetro < {_D_MIN_HW_M * 1000:g} mm en los tramos {finos}: fuera del dominio de validez de Hazen-Williams.")
    if lentos:
        supuestos.append(f"Velocidad < {_V_MIN_HW_MS:g} m/s en los tramos {lentos}: Hazen-Williams subestima la pérdida a velocidades muy bajas.")
    return ResultadoMotor(
        valor={**res, "incumplimientos": incumple, "limites_verificados": hay_limites,
               "cumple": (not incumple) if (hay_limites or incumple) else None},
        unidad_si="Caudal en m³/s; carga y presión en m; velocidad en m/s",
        ecuacion="h = r·Q·|Q|^0,852, r = 10,67·L/(C^1,852·D^4,871); continuidad ΣQ = demanda en cada nudo libre; Σh = 0 en cada malla",
        referencia_normativa="Todini y Pilati (1988) · Hazen-Williams · RAS 2000 Título B (límites a cargo del usuario)",
        supuestos=supuestos,
        en_borde_dominio=bool(borde),
    )
