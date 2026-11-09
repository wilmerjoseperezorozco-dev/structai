"""
REDES ROUTER: red de tuberías a presión mallada en estado permanente (método del gradiente, Todini y Pilati 1988),
con contrato uniforme de salida (`ResultadoMotor`). Entrada fuera de dominio o red que no converge responde 422
(regla 1 de docs/REGLAS_MOTORES_DE_CALCULO.md).
"""
# Sin "from __future__ import annotations" a propósito: ver la nota de routers/vias.py (slowapi + FastAPI).

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

ROOT = Path(__file__).resolve().parents[3]

import importlib.util as _ilu
_init = ROOT / "packages" / "motor-redes" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_redes", _init, submodule_search_locations=[str(_init.parent)])
motor_redes = _ilu.module_from_spec(_spec)
sys.modules["motor_redes"] = motor_redes
_spec.loader.exec_module(motor_redes)

from motor_redes.contrato_api import SolicitudRed, red_permanente_contrato  # noqa: E402
from motor_redes.contrato_periodo import SolicitudPeriodo, periodo_extendido_contrato  # noqa: E402

router = APIRouter(prefix="/redes", tags=["Redes hidráulicas"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Redes hidráulicas", "metodos": ["Gradiente (Todini y Pilati, 1988)", "Hazen-Williams"]}


@router.post("/permanente", summary="Red mallada en estado permanente: cargas, caudales, presiones y velocidades")
@limiter.limit("20/minute")
def endpoint_permanente(request: Request, req: SolicitudRed, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return red_permanente_contrato(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/periodo", summary="Periodo extendido con tanques de nivel variable y patrón de demanda")
@limiter.limit("10/minute")
def endpoint_periodo(request: Request, req: SolicitudPeriodo, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return periodo_extendido_contrato(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
