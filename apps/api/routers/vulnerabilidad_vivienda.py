"""
══════════════════════════════════════════════════════════════
VULNERABILIDAD VIVIENDA ROUTER — Evaluación de vulnerabilidad sísmica de
vivienda de mampostería (1-2 pisos), checklist AIS Título E NSR-10.
Montado bajo el prefijo /vulnerabilidad-vivienda. Mismo patrón que
motor-geopot/motor-apu: paquete propio en packages/, cargado vía
importlib para evitar colisión con el nombre genérico "src".
══════════════════════════════════════════════════════════════
"""
# NOTA: sin "from __future__ import annotations" a proposito, mismo motivo
# documentado en routers/geopot.py -- rompe la resolucion de forward-refs
# de @limiter.limit() de slowapi para tipos no builtin (los *Request de
# motor_vulnerabilidad_vivienda).

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

# apps/api ya está en sys.path para cuando este módulo se importa (main.py lo
# agrega antes de hacer `from routers.vulnerabilidad_vivienda import router`).
from auth import AuthenticatedUser, get_current_user
from cache import TTLCache
from rate_limit import limiter

# El aviso de responsabilidad profesional (issue #18) NO se genera nunca
# por el LLM -- se inyecta determinísticamente desde el backend. Este
# router no pasa por ask_delegado()/_generar_respuesta() (es una
# calculadora pura), así que hay que agregarlo a mano aquí, igual que
# hacen /ask y /consultar en main.py.
from rag_multi_norma import AVISO_RESPONSABILIDAD_PROFESIONAL

try:
    import sgc_amenaza_sismica
    _SGC_DISPONIBLE = True
except Exception:
    _SGC_DISPONIBLE = False

ROOT = Path(__file__).resolve().parents[3]  # monorepo/

import importlib.util as _ilu
_motor_init = ROOT / "packages" / "motor-vulnerabilidad-vivienda" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location(
    "motor_vulnerabilidad_vivienda", _motor_init, submodule_search_locations=[str(_motor_init.parent)]
)
motor_vulnerabilidad_vivienda = _ilu.module_from_spec(_spec)
sys.modules["motor_vulnerabilidad_vivienda"] = motor_vulnerabilidad_vivienda
_spec.loader.exec_module(motor_vulnerabilidad_vivienda)

router = APIRouter(prefix="/vulnerabilidad-vivienda", tags=["Vulnerabilidad Vivienda"])


@router.get("/salud")
def salud():
    return {
        "estado": "ok",
        "motor": "Vulnerabilidad Vivienda",
        "norma_base": "NSR-10 Título E · AIS 2004 (checklist ponderado)",
        "fase": "v0 — checklist determinístico, sin fotos, sin ML",
    }


# checklist() es contenido estático (15 criterios con sus descripciones) --
# no depende de ningún input de usuario, así que cachearlo es seguro sin
# ninguna clave más que "la única respuesta posible" (mismo patrón que
# /geopot/sismica/resumen).
_cache_checklist = TTLCache(ttl_seconds=24 * 3600, max_size=1)


@router.get("/checklist", summary="Los 15 criterios del checklist AIS, con sus 3 descripciones cada uno")
@limiter.limit("60/minute")
def endpoint_checklist(request: Request):
    cacheado = _cache_checklist.get("checklist")
    if cacheado is not None:
        return cacheado
    resultado = motor_vulnerabilidad_vivienda.consultar_checklist()
    _cache_checklist.set("checklist", resultado)
    return resultado


@router.post("/evaluar", summary="Calcula la vulnerabilidad sísmica ponderada a partir de las 15 respuestas del checklist")
@limiter.limit("30/minute")
def endpoint_evaluar(
    request: Request,
    req: motor_vulnerabilidad_vivienda.EvaluacionVulnerabilidadRequest,
    user: AuthenticatedUser = Depends(get_current_user),
):
    resultado = motor_vulnerabilidad_vivienda.evaluar(req)
    if "error" in resultado:
        raise HTTPException(status_code=422, detail=resultado["error"])

    resultado["aviso_responsabilidad"] = AVISO_RESPONSABILIDAD_PROFESIONAL

    if req.municipio and _SGC_DISPONIBLE:
        amenaza = sgc_amenaza_sismica.detectar_municipio_en_texto(req.municipio)
        resultado["amenaza_sismica_sgc"] = amenaza

    return resultado
