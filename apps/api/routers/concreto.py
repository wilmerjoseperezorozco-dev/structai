"""
CONCRETO ROUTER — zapata aislada (NSR-10 C/H) y estabilidad de taludes de excavación (NSR-10 H.2.4),
con contrato uniforme de salida (`ResultadoMotor`). Cargado vía importlib como el resto de motores.
Un dato ausente o fuera de dominio responde 422 con la norma infringida (regla 1 de docs/REGLAS_MOTORES_DE_CALCULO.md).
"""
# Sin "from __future__ import annotations" a propósito: ver la nota de routers/vias.py (slowapi + FastAPI).

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

ROOT = Path(__file__).resolve().parents[3]

import importlib.util as _ilu
_init = ROOT / "packages" / "motor-concreto" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_concreto", _init, submodule_search_locations=[str(_init.parent)])
motor_concreto = _ilu.module_from_spec(_spec)
sys.modules["motor_concreto"] = motor_concreto
_spec.loader.exec_module(motor_concreto)

from motor_concreto.contrato_api import (  # noqa: E402
    SolicitudTalud, SolicitudZapata, disenar_zapata_contrato, evaluar_talud_contrato,
)

router = APIRouter(prefix="/concreto", tags=["Concreto y excavación"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Concreto", "norma_base": "NSR-10 Títulos C y H"}


@router.post("/zapata", summary="Diseño de zapata aislada (NSR-10 C.11, C.15, H.4)")
@limiter.limit("20/minute")
def endpoint_zapata(request: Request, req: SolicitudZapata, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return disenar_zapata_contrato(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/talud", summary="Estabilidad de talud de excavación por Bishop (NSR-10 H.2.4)")
@limiter.limit("20/minute")
def endpoint_talud(request: Request, req: SolicitudTalud, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return evaluar_talud_contrato(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
