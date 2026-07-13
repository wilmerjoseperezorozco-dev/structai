"""
══════════════════════════════════════════════════════════════
GEOPOT ROUTER — Clasificación sísmica NSR-10 + Laboratorio (concreto/suelos/agregados)
Complementario de StructAI, montado bajo el prefijo /geopot. Mismo patrón
que motor-apu/motor-deformacion/motor-aquai: paquete propio en packages/,
cargado vía importlib para evitar colisión con el nombre genérico "src".
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

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
def endpoint_sismica(req: motor_geopot.ZonaSismicaRequest):
    resultado = motor_geopot.consultar_zona_sismica(req)
    if "error" in resultado:
        raise HTTPException(status_code=404, detail=resultado["error"])
    return resultado


@router.get("/sismica/resumen", summary="Resumen nacional de zonas sísmicas")
def endpoint_sismica_resumen():
    return motor_geopot.resumen_zonas_sismicas()


# ── Laboratorio: concreto ────────────────────────────────────────────────────

@router.post("/laboratorio/concreto", summary="Informe completo de ensayo de concreto (NTC 673/396, conformidad ACI 318/NSR-10)")
def endpoint_concreto(req: motor_geopot.ConcretoRequest):
    return motor_geopot.analizar_concreto(req)


# ── Laboratorio: suelos ───────────────────────────────────────────────────────

@router.post("/laboratorio/suelos/uscs", summary="Clasificación USCS (ASTM D2487)")
def endpoint_uscs(req: motor_geopot.USCSRequest):
    return motor_geopot.clasificar_suelo_uscs(req)


@router.post("/laboratorio/suelos/aashto", summary="Clasificación AASHTO M145")
def endpoint_aashto(req: motor_geopot.AASHTORequest):
    return motor_geopot.clasificar_suelo_aashto(req)


@router.post("/laboratorio/suelos/proctor", summary="Compactación Proctor (INV E-141/142)")
def endpoint_proctor(req: motor_geopot.ProctorRequest):
    resultado = motor_geopot.analizar_proctor(req)
    if "error" in resultado:
        raise HTTPException(status_code=422, detail=resultado["error"])
    return resultado


@router.post("/laboratorio/suelos/cbr", summary="CBR de laboratorio (INV E-148) + espesor referencial de pavimento")
def endpoint_cbr(req: motor_geopot.CBRRequest):
    return motor_geopot.analizar_cbr(req)


@router.post("/laboratorio/suelos/granulometria", summary="Granulometría por tamizado (INV E-123 / NTC 77)")
def endpoint_granulometria(req: motor_geopot.GranulometriaRequest):
    return motor_geopot.analizar_granulometria(req)


# ── Laboratorio: agregados y mezcla ──────────────────────────────────────────

@router.post("/laboratorio/agregados/grueso", summary="Verificación de agregado grueso (NTC 174/237/218)")
def endpoint_agregado_grueso(req: motor_geopot.AgregadoGruesoRequest):
    return motor_geopot.verificar_agregado_grueso(req)


@router.post("/laboratorio/agregados/fino", summary="Verificación de agregado fino / arena (NTC 174/237/77)")
def endpoint_agregado_fino(req: motor_geopot.AgregadoFinoRequest):
    return motor_geopot.verificar_agregado_fino(req)


@router.post("/laboratorio/mezcla", summary="Diseño de mezcla de concreto (ACI 211.1, referencial)")
def endpoint_mezcla(req: motor_geopot.MezclaACIRequest):
    return motor_geopot.disenar_mezcla_aci(req)
