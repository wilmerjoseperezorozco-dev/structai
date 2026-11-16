"""Salida con contrato uniforme (`ResultadoMotor`) de PTAP, PTAR y sistema lagunar (#236).

`valor` conserva la respuesta detallada de siempre (PTAPResponse / PTARResponse), así la web la sigue mostrando; el
contrato agrega ecuación, referencia normativa, supuestos declarados, borde de dominio y aviso profesional.
"""
from __future__ import annotations

import sys
from pathlib import Path

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .lagunas import SolicitudLagunas, disenar_lagunas  # noqa: E402
from .ptap import calcular_ptap_detalle  # noqa: E402
from .ptar import calcular_ptar_detalle  # noqa: E402
from .schemas_saneamiento import PTAPRequest, PTARRequest  # noqa: E402


def ptap_contrato(req: PTAPRequest) -> ResultadoMotor:
    resp, supuestos, borde = calcular_ptap_detalle(req)
    valor = resp.model_dump()
    valor["borde_dominio"] = borde
    return ResultadoMotor(
        valor=valor,
        unidad_si="L/s, m², m³, min, mg/L",
        ecuacion="V = Q·t; A = Q/tasa superficial; t_contacto = máx(CT/C, 20 min)",
        referencia_normativa="Resolución 0330 de 2017, arts. 111 a 114 y 121; Resolución 2115 de 2007",
        supuestos=supuestos,
        en_borde_dominio=bool(borde),
        advertencias=list(resp.advertencias),
    )


def ptar_contrato(req: PTARRequest) -> ResultadoMotor:
    resp, supuestos, borde = calcular_ptar_detalle(req)
    valor = resp.model_dump()
    valor["borde_dominio"] = borde
    return ResultadoMotor(
        valor=valor,
        unidad_si="L/s, m³/d, m², m³, h, d, mg/L, kg/d",
        ecuacion="Q = Qmd·f_retorno; carga = C·Q; C_efluente = C·(1 − η); límite según carga (Res. 0631 art. 8)",
        referencia_normativa=("Resolución 0330 de 2017, arts. 164, 189, 191, 192 y 197; "
                              "Resolución 0631 de 2015, art. 8"),
        supuestos=supuestos,
        en_borde_dominio=bool(borde),
        advertencias=list(resp.advertencias),
    )


def lagunas_contrato(req: SolicitudLagunas) -> ResultadoMotor:
    return disenar_lagunas(req)
