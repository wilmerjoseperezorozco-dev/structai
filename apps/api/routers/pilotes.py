"""
PILOTES ROUTER — capacidad axial de pilotes y grupos (NSR-10 H.4.4 / H.4.7, CCP-14 con SPT) y asentamiento de grupos
por zapata equivalente (NSR-10 H.4.4.2, CCP-14 §10.7.2.3), con contrato uniforme de salida (`ResultadoMotor`). Un dato
ausente o fuera de dominio responde 422 con la norma (regla 1 de docs/REGLAS_MOTORES_DE_CALCULO.md).
"""
# Sin "from __future__ import annotations" a propósito: ver la nota de routers/vias.py (slowapi + FastAPI).

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

ROOT = Path(__file__).resolve().parents[3]

import importlib.util as _ilu
_init = ROOT / "packages" / "motor-pilotes" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_pilotes", _init, submodule_search_locations=[str(_init.parent)])
motor_pilotes = _ilu.module_from_spec(_spec)
sys.modules["motor_pilotes"] = motor_pilotes
_spec.loader.exec_module(motor_pilotes)

from motor_pilotes.contrato_api import (  # noqa: E402
    SolicitudAsentamientoPilotes, SolicitudPilotes, asentamiento_pilotes_contrato, pilotes_contrato,
)

router = APIRouter(prefix="/pilotes", tags=["Pilotes"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Pilotes", "metodos": ["capacidad axial α·Su y τL drenado (NSR-10 H.4.7-2/-3)",
                                                           "SPT del CCP-14 (Meyerhof hincados, β excavados)",
                                                           "grupo: Σ individuales, bloque y Converse-Labarre",
                                                           "asentamiento por zapata equivalente (CCP-14 §10.7.2.3)"]}


@router.post("/capacidad", summary="Capacidad axial a compresión de un grupo de pilotes (NSR-10 H.4.4.1, H.4.7)")
@limiter.limit("20/minute")
def endpoint_capacidad(request: Request, req: SolicitudPilotes, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return pilotes_contrato(req)
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/asentamiento", summary="Asentamiento de un grupo de pilotes por zapata equivalente (NSR-10 H.4.4.2, H.4.9.2)")
@limiter.limit("20/minute")
def endpoint_asentamiento(request: Request, req: SolicitudAsentamientoPilotes, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return asentamiento_pilotes_contrato(req)
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=str(e))
