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

from orquestador.contrato_api import (  # noqa: E402
    SolicitudDisenoIntegral, SolicitudParetoPortico, disenar_integral_contrato, optimizar_portico_contrato)

_init_dag = ROOT / "packages" / "dag-proyecto" / "dag_proyecto" / "__init__.py"
if "dag_proyecto" not in sys.modules:
    _spec_dag = _ilu.spec_from_file_location("dag_proyecto", _init_dag, submodule_search_locations=[str(_init_dag.parent)])
    _mod_dag = _ilu.module_from_spec(_spec_dag)
    sys.modules["dag_proyecto"] = _mod_dag
    _spec_dag.loader.exec_module(_mod_dag)

from contrato_motor import ResultadoMotor  # noqa: E402
from dag_proyecto.flujo import AlmacenAcotado, Flujo, Paso, huella_de_archivos  # noqa: E402

# --- Flujo atómico (#221, fase 2). Las dos cadenas son puras y deterministas (sin BD, sin LLM, sin red): dependen solo del código
# de los motores y de los datos de norma que leen. Esa es la llave: cualquier cambio de código o de norma cambia la huella y la
# caché deja de responder con resultados viejos (#193). Caché del proceso, acotada; compartida entre instancias es otra decisión.
_P = ROOT / "packages"
VERSION_MOTORES = huella_de_archivos(_P / "orquestador" / "src", _P / "motor-concreto" / "src", _P / "motor-apu" / "src",
                                     _P / "motor-geopot" / "src", _P / "contrato-motor" / "contrato_motor")
VERSION_NORMA = huella_de_archivos(_P / "motor-geopot" / "data", _P / "motor-apu" / "data", patron="*.json")
CACHE_PORTICO = AlmacenAcotado(max_artefactos=128)


def _paso(nombre: str, modelo, fn) -> Paso:
    def correr(params, _ent):
        return fn(modelo.model_validate(params["solicitud"]))
    return Paso(nombre, VERSION_MOTORES, (), ("solicitud",), correr)


FLUJO_INTEGRAL = Flujo("portico-integral", "1", [_paso("diseno_integral", SolicitudDisenoIntegral, disenar_integral_contrato)],
                       VERSION_NORMA, almacen=CACHE_PORTICO, max_hilos=1)
FLUJO_PARETO = Flujo("portico-pareto", "1", [_paso("frontera_pareto", SolicitudParetoPortico, optimizar_portico_contrato)],
                     VERSION_NORMA, almacen=CACHE_PORTICO, max_hilos=1)
_FLUJOS = {disenar_integral_contrato: (FLUJO_INTEGRAL, "diseno_integral"), optimizar_portico_contrato: (FLUJO_PARETO, "frontera_pareto")}


def _por_flujo(fn, req) -> ResultadoMotor:
    """Corre `fn(req)` dentro de su flujo. La función va como primer argumento (como `submit(fn, ...)`) para que el inventario
    estático (scripts/inventario/cadenas_ejecucion.py) siga viendo la cadena. La solicitud ya validada, en su forma canónica JSON,
    es la entrada del paso: dos peticiones con el mismo contenido comparten artefacto aunque lleguen con otro orden de claves."""
    flujo, paso = _FLUJOS[fn]
    r = flujo.ejecutar({"solicitud": req.model_dump(mode="json")})
    return ResultadoMotor.model_validate(r.artefactos[paso].resultado)

router = APIRouter(prefix="/orquestador", tags=["Diseño integral"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Orquestador", "diseno": "pórtico integral"}


@router.post("/portico-integral", summary="Diseño integral de pórtico: mínimo costo sobre una rejilla acotada")
@limiter.limit("5/minute")
def endpoint_portico(request: Request, req: SolicitudDisenoIntegral, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return _por_flujo(disenar_integral_contrato, req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/portico-pareto", summary="Optimizador de pórtico: frontera de Pareto exacta (costo, acero, concreto, CO₂e, deriva, D/C)")
@limiter.limit("3/minute")
def endpoint_pareto(request: Request, req: SolicitudParetoPortico, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return _por_flujo(optimizar_portico_contrato, req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
