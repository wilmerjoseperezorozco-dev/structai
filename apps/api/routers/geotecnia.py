"""
GEOTECNIA ROUTER — asentamiento por consolidación (Terzaghi, Boussinesq/2:1) y capacidad portante (Vesić),
con contrato uniforme de salida (`ResultadoMotor`). Un dato ausente o fuera de dominio responde 422 con la norma
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
_init = ROOT / "packages" / "motor-geotecnia" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_geotecnia", _init, submodule_search_locations=[str(_init.parent)])
motor_geotecnia = _ilu.module_from_spec(_spec)
sys.modules["motor_geotecnia"] = motor_geotecnia
_spec.loader.exec_module(motor_geotecnia)

from motor_geotecnia.contrato_api import (  # noqa: E402
    SolicitudAsentamiento, SolicitudPortante, asentamiento_contrato, portante_contrato,
)

router = APIRouter(prefix="/geotecnia", tags=["Geotecnia"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Geotecnia", "metodos": ["consolidación unidimensional de Terzaghi", "capacidad portante de Vesić"]}


@router.post("/asentamiento", summary="Asentamiento por consolidación primaria y tiempo (NSR-10 H.4.9)")
@limiter.limit("20/minute")
def endpoint_asentamiento(request: Request, req: SolicitudAsentamiento, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return asentamiento_contrato(req)
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/portante", summary="Capacidad portante de cimentación superficial (Vesić)")
@limiter.limit("20/minute")
def endpoint_portante(request: Request, req: SolicitudPortante, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return portante_contrato(req)
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=str(e))
