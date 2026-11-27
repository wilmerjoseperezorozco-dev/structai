"""
ACERO FORMADO EN FRÍO ROUTER (#81): perfiles C según NSR-10 F.4, con contrato uniforme de salida (`ResultadoMotor`).
Un dato ausente, fuera de dominio o incoherente con la norma responde 422 con la norma citada (regla 1 de
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
_init = ROOT / "packages" / "motor-acero-frio" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_acero_frio", _init, submodule_search_locations=[str(_init.parent)])
motor_acero_frio = _ilu.module_from_spec(_spec)
sys.modules["motor_acero_frio"] = motor_acero_frio
_spec.loader.exec_module(motor_acero_frio)

from motor_acero_frio.contrato_api import PerfilC, propiedades_perfil_c  # noqa: E402
from motor_acero_frio.solicitudes import (  # noqa: E402
    SolicitudArrugamiento,
    SolicitudCompresion,
    SolicitudFlexion,
    SolicitudFlexocompresion,
    SolicitudFlexotension,
    SolicitudTension,
    SolicitudViga,
)

router = APIRouter(prefix="/acero-frio", tags=["Acero formado en frío"])
LIMITE = "20/minute"


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Acero formado en frío (NSR-10 F.4)",
            "estados_limite": ["propiedades", "flexion (seccion, lateral-torsional, distorsional)", "viga",
                               "compresion (global, local, distorsional)", "tension", "flexocompresion",
                               "flexotension", "arrugamiento"]}


@router.post("/perfil-c/propiedades", summary="Propiedades brutas y sectoriales de una C")
@limiter.limit(LIMITE)
def endpoint_propiedades(request: Request, req: PerfilC, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return propiedades_perfil_c(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/perfil-c/flexion", summary="φbMn: sección, pandeo lateral-torsional y distorsional")
@limiter.limit(LIMITE)
def endpoint_flexion(request: Request, req: SolicitudFlexion, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return req.ejecutar()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/perfil-c/viga", summary="Flexión, cortante e interacción (F.4.3.3-54)")
@limiter.limit(LIMITE)
def endpoint_viga(request: Request, req: SolicitudViga, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return req.ejecutar()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/perfil-c/compresion", summary="φcPn: pandeo global, local y distorsional")
@limiter.limit(LIMITE)
def endpoint_compresion(request: Request, req: SolicitudCompresion, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return req.ejecutar()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/perfil-c/tension", summary="φTn: fluencia y rotura en la sección neta")
@limiter.limit(LIMITE)
def endpoint_tension(request: Request, req: SolicitudTension, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return req.ejecutar()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/perfil-c/flexocompresion", summary="Carga axial a compresión y momento (F.4.3.5.2)")
@limiter.limit(LIMITE)
def endpoint_flexocompresion(request: Request, req: SolicitudFlexocompresion,
                             user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return req.ejecutar()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/perfil-c/flexotension", summary="Carga axial a tensión y momento (F.4.3.5.1)")
@limiter.limit(LIMITE)
def endpoint_flexotension(request: Request, req: SolicitudFlexotension,
                          user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return req.ejecutar()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/perfil-c/arrugamiento", summary="Arrugamiento del alma (F.4.3.3-56) e interacción con flexión")
@limiter.limit(LIMITE)
def endpoint_arrugamiento(request: Request, req: SolicitudArrugamiento,
                          user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return req.ejecutar()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
