"""
PROYECTO ROUTER — DAG estructural (diseño integral → análisis → zapata) con artefactos versionados y hash (#150).
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
_init = ROOT / "packages" / "dag-proyecto" / "dag_proyecto" / "__init__.py"
if "dag_proyecto" not in sys.modules:
    _spec = _ilu.spec_from_file_location("dag_proyecto", _init, submodule_search_locations=[str(_init.parent)])
    _mod = _ilu.module_from_spec(_spec)
    sys.modules["dag_proyecto"] = _mod
    _spec.loader.exec_module(_mod)

from dag_proyecto import Orquestador  # noqa: E402
from dag_proyecto.motores import SolicitudProyectoEstructural, nodos_estructurales  # noqa: E402

NORMA_VERSION = "NSR-10 (Decreto 926 de 2010)"

router = APIRouter(prefix="/proyecto", tags=["Proyecto (DAG)"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "DAG de proyecto", "nodos": [n.nombre for n in nodos_estructurales()]}


@router.post("/estructural", summary="Diseño integral → análisis → zapata con artefactos versionados")
@limiter.limit("5/minute")
def endpoint_estructural(request: Request, req: SolicitudProyectoEstructural, user: AuthenticatedUser = Depends(get_current_user)):
    try:
        arts = Orquestador(nodos_estructurales(), norma_version=NORMA_VERSION).ejecutar(req.model_dump())
    except (ValueError, IndexError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"norma_version": NORMA_VERSION, "artefactos": {k: a.a_dict() for k, a in arts.items()}}
