"""
ANÁLISIS ROUTER — pórtico plano por rigidez directa, con contrato uniforme de salida (`ResultadoMotor`).
Modelo inestable o datos inconsistentes responden 422 (regla 1 de docs/REGLAS_MOTORES_DE_CALCULO.md).
"""
# Sin "from __future__ import annotations" a propósito: ver la nota de routers/vias.py (slowapi + FastAPI).

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

ROOT = Path(__file__).resolve().parents[3]

import importlib.util as _ilu
_init = ROOT / "packages" / "motor-analisis" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_analisis", _init, submodule_search_locations=[str(_init.parent)])
motor_analisis = _ilu.module_from_spec(_spec)
sys.modules["motor_analisis"] = motor_analisis
_spec.loader.exec_module(motor_analisis)

from motor_analisis.contrato_api import SolicitudPortico, resolver_portico_contrato  # noqa: E402

router = APIRouter(prefix="/analisis", tags=["Análisis estructural"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Análisis de pórticos", "metodo": "rigidez directa 2D"}


@router.post("/portico", summary="Pórtico plano por rigidez directa")
@limiter.limit("20/minute")
def endpoint_portico(request: Request, req: SolicitudPortico, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return resolver_portico_contrato(req)
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=str(e))
