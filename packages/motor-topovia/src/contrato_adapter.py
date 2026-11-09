"""Salida con contrato uniforme (contrato_motor) para las funciones públicas de motor-topovia."""
import sys
from pathlib import Path

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .engine import SN_MAX, SN_MIN, calcular_sn_flexible  # noqa: E402

_FRACCION_BORDE_SN = 0.9  # SN > 90 % del tope de búsqueda se considera borde del dominio


def sn_flexible_con_contrato(w18, mr_psi, confiabilidad=0.85, so=0.45, po=4.2, pt=2.0) -> ResultadoMotor:
    sn = calcular_sn_flexible(w18, mr_psi, confiabilidad, so, po, pt)
    borde = sn <= SN_MIN or sn >= _FRACCION_BORDE_SN * SN_MAX
    return ResultadoMotor(
        valor=sn,
        unidad_si="adimensional (SN en unidades de pulgada por definición AASHTO)",
        ecuacion="log10(W18) = ZR·So + 9,36·log10(SN+1) − 0,20 + log10(ΔPSI/(po−1,5))/(0,40+1094/(SN+1)^5,19) + 2,32·log10(MR) − 8,07",
        referencia_normativa="AASHTO Guide for Design of Pavement Structures 1993; INVIAS, Manual de Diseño de Pavimentos Asfálticos",
        supuestos=[f"confiabilidad={confiabilidad}", f"So={so}", f"po={po}, pt={pt}", f"MR={mr_psi} psi", f"W18={w18:.4g}"],
        en_borde_dominio=bool(borde),
    )
