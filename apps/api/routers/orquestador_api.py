"""
ORQUESTADOR ROUTER — diseño integral de pórtico (vigas + columnas + costo APU), con contrato uniforme (`ResultadoMotor`). Rejilla acotada.
Datos faltantes, sin solución o fuera de dominio responden 422 (regla 1 de docs/REGLAS_MOTORES_DE_CALCULO.md).
"""
# Sin "from __future__ import annotations" a propósito: ver la nota de routers/vias.py (slowapi + FastAPI).

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

ROOT = Path(__file__).resolve().parents[3]

import importlib.util as _ilu
_init = ROOT / "packages" / "orquestador" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("orquestador", _init, submodule_search_locations=[str(_init.parent)])
orquestador = _ilu.module_from_spec(_spec)
sys.modules["orquestador"] = orquestador
_spec.loader.exec_module(orquestador)

from orquestador.contrato_api import SolicitudDisenoIntegral, disenar_integral_contrato  # noqa: E402

router = APIRouter(prefix="/orquestador", tags=["Diseño integral"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Orquestador", "diseno": "pórtico integral"}


@router.post("/portico-integral", summary="Diseño integral de pórtico: mínimo costo sobre una rejilla acotada")
@limiter.limit("5/minute")
def endpoint_portico(request: Request, req: SolicitudDisenoIntegral, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return disenar_integral_contrato(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
