"""
══════════════════════════════════════════════════════════════
GEOPOT ROUTER — Clasificación sísmica NSR-10 + Laboratorio (concreto/suelos/agregados)
Complementario de StructAI, montado bajo el prefijo /geopot. Mismo patrón
que motor-apu/motor-deformacion/motor-aquai: paquete propio en packages/,
cargado vía importlib para evitar colisión con el nombre genérico "src".
══════════════════════════════════════════════════════════════
"""
# NOTA: sin "from __future__ import annotations" a proposito (igual que
# main.py) -- con PEP 563 activo, @limiter.limit() de slowapi rompe la
# resolucion de forward-refs de FastAPI para tipos no builtin (UploadFile,
# los *Request de motor_*). Reproducido en vivo el 2026-08-02 al agregar
# rate limiting a este router: analizar_nudo() (UploadFile) fallaba con
# FastAPIError en el import; los endpoints con tipos custom (motor_X.Y)
# "funcionaban" solo por coincidencia de que Python 3.10+ ya resuelve
# list/dict/X|None nativamente sin necesitar el future import de todos modos.

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

# apps/api ya está en sys.path para cuando este módulo se importa (main.py lo
# agrega antes de hacer `from routers.geopot import router`).
from auth import AuthenticatedUser, get_current_user
from rate_limit import limiter

ROOT = Path(__file__).resolve().parents[3]  # monorepo/

import importlib.util as _ilu
_geopot_init = ROOT / "packages" / "motor-geopot" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_geopot", _geopot_init, submodule_search_locations=[str(_geopot_init.parent)])
motor_geopot = _ilu.module_from_spec(_spec)
sys.modules["motor_geopot"] = motor_geopot
_spec.loader.exec_module(motor_geopot)

router = APIRouter(prefix="/geopot", tags=["GeoPot"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "GeoPot", "norma_base": "NSR-10 · INV E-1xx · NTC 174/673/396"}


# ── Sísmica ────────────────────────────────────────────────────────────────

@router.post("/sismica", summary="Clasificación sísmica NSR-10 por departamento")
@limiter.limit("30/minute")
def endpoint_sismica(request: Request, req: motor_geopot.ZonaSismicaRequest, user: AuthenticatedUser = Depends(get_current_user)):
    resultado = motor_geopot.consultar_zona_sismica(req)
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado


@router.get("/sismica/resumen", summary="Resumen nacional de zonas sísmicas")
@limiter.limit("60/minute")
def endpoint_sismica_resumen(request: Request):
    return motor_geopot.resumen_zonas_sismicas()


# ── Laboratorio: concreto ────────────────────────────────────────────────────

@router.post("/laboratorio/concreto", summary="Informe completo de ensayo de concreto (NTC 673/396, conformidad ACI 318/NSR-10)")
@limiter.limit("30/minute")
def endpoint_concreto(request: Request, req: motor_geopot.ConcretoRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.analizar_concreto(req)


# ── Laboratorio: suelos ───────────────────────────────────────────────────────

@router.post("/laboratorio/suelos/uscs", summary="Clasificación USCS (ASTM D2487)")
@limiter.limit("30/minute")
def endpoint_uscs(request: Request, req: motor_geopot.USCSRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.clasificar_suelo_uscs(req)


@router.post("/laboratorio/suelos/aashto", summary="Clasificación AASHTO M145")
@limiter.limit("30/minute")
def endpoint_aashto(request: Request, req: motor_geopot.AASHTORequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.clasificar_suelo_aashto(req)


@router.post("/laboratorio/suelos/proctor", summary="Compactación Proctor (INV E-141/142)")
@limiter.limit("30/minute")
def endpoint_proctor(request: Request, req: motor_geopot.ProctorRequest, user: AuthenticatedUser = Depends(get_current_user)):
    resultado = motor_geopot.analizar_proctor(req)
    if "error" in resultado:
        raise HTTPException(status_code=422, detail=resultado["error"])
    return resultado


@router.post("/laboratorio/suelos/cbr", summary="CBR de laboratorio (INV E-148) + espesor referencial de pavimento")
@limiter.limit("30/minute")
def endpoint_cbr(request: Request, req: motor_geopot.CBRRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.analizar_cbr(req)


@router.post("/laboratorio/suelos/granulometria", summary="Granulometría por tamizado (INV E-123 / NTC 77)")
@limiter.limit("30/minute")
def endpoint_granulometria(request: Request, req: motor_geopot.GranulometriaRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.analizar_granulometria(req)


# ── Laboratorio: agregados y mezcla ──────────────────────────────────────────

@router.post("/laboratorio/agregados/grueso", summary="Verificación de agregado grueso (NTC 174/237/218)")
@limiter.limit("30/minute")
def endpoint_agregado_grueso(request: Request, req: motor_geopot.AgregadoGruesoRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.verificar_agregado_grueso(req)


@router.post("/laboratorio/agregados/fino", summary="Verificación de agregado fino / arena (NTC 174/237/77)")
@limiter.limit("30/minute")
def endpoint_agregado_fino(request: Request, req: motor_geopot.AgregadoFinoRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.verificar_agregado_fino(req)


@router.post("/laboratorio/mezcla", summary="Diseño de mezcla de concreto (ACI 211.1, referencial)")
@limiter.limit("30/minute")
def endpoint_mezcla(request: Request, req: motor_geopot.MezclaACIRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_geopot.disenar_mezcla_aci(req)
