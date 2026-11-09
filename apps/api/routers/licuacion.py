"""
LICUACION ROUTER: evaluación simplificada por SPT (NCEER, Youd et al. 2001) con LPI de Iwasaki, con contrato uniforme
de salida (`ResultadoMotor`). Un dato ausente o fuera de dominio responde 422 con la norma (regla 1 de
docs/REGLAS_MOTORES_DE_CALCULO.md).
"""
# Sin "from __future__ import annotations" a propósito: ver la nota de routers/vias.py (slowapi + FastAPI).

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

ROOT = Path(__file__).resolve().parents[3]

import importlib.util as _ilu
_init = ROOT / "packages" / "motor-licuacion" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_licuacion", _init, submodule_search_locations=[str(_init.parent)])
motor_licuacion = _ilu.module_from_spec(_spec)
sys.modules["motor_licuacion"] = motor_licuacion
_spec.loader.exec_module(motor_licuacion)

from motor_licuacion.contrato_api import SolicitudLicuacionSPT, licuacion_spt_contrato  # noqa: E402

router = APIRouter(prefix="/licuacion", tags=["Licuación"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Licuación", "metodos": ["SPT simplificado NCEER (Youd et al. 2001)", "LPI de Iwasaki"]}


@router.post("/spt", summary="Licuación por SPT: CSR, CRR, FS por estrato y LPI")
@limiter.limit("20/minute")
def endpoint_spt(request: Request, req: SolicitudLicuacionSPT, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return licuacion_spt_contrato(req)
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=str(e))
