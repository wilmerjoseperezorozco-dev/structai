"""
══════════════════════════════════════════════════════════════
VIAS ROUTER — Diseño geométrico, pavimentos, mantenimiento y topografía vial
(Manuales INVIAS 2008/2016/2025) + verificación de materiales NTC.
Mismo patrón que motor-apu/motor-deformacion/motor-aquai/motor-geopot:
paquete propio en packages/, cargado vía importlib para evitar colisión
con el nombre genérico "src".
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Depends

# apps/api ya está en sys.path para cuando este módulo se importa (main.py lo
# agrega antes de hacer `from routers.vias import router`).
from auth import AuthenticatedUser, get_current_user

ROOT = Path(__file__).resolve().parents[3]  # monorepo/

import importlib.util as _ilu
_vias_init = ROOT / "packages" / "motor-vias" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_vias", _vias_init, submodule_search_locations=[str(_vias_init.parent)])
motor_vias = _ilu.module_from_spec(_spec)
sys.modules["motor_vias"] = motor_vias
_spec.loader.exec_module(motor_vias)

router = APIRouter(prefix="/vias", tags=["Vías"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Vías", "norma_base": "INVIAS 2008/2016/2025 · NTC 121/1299/1362/2017/3459/3493/3502/3760/4018/4024/4342/4924/5147/6008"}


# ── Diseño geométrico ───────────────────────────────────────────────────────

@router.post("/geometrico", summary="Validación de diseño geométrico (Manual INVIAS 2008/2025)")
def endpoint_geometrico(req: motor_vias.DisenoGeometricoRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.validar_diseno_geometrico(req)


# ── Pavimentos ───────────────────────────────────────────────────────────────

@router.post("/pavimentos", summary="Diseño estructural de pavimentos (AASHTO 93 adaptado)")
def endpoint_pavimentos(req: motor_vias.PavimentosRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.disenar_pavimento(req)


# ── Mantenimiento ────────────────────────────────────────────────────────────

@router.post("/mantenimiento", summary="Diagnóstico y planificación de mantenimiento (Manual INVIAS 2016)")
def endpoint_mantenimiento(req: motor_vias.MantenimientoRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.diagnosticar_mantenimiento(req)


# ── Topografía ───────────────────────────────────────────────────────────────

@router.post("/topografia/cierre", summary="Tolerancia de cierre en nivelación geométrica (INVIAS/IDU/IGAC)")
def endpoint_topografia_cierre(req: motor_vias.CierreNivelacionRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_cierre_nivelacion(req)


# ── NTC materiales ───────────────────────────────────────────────────────────

@router.post("/ntc/2017", summary="Adoquines de concreto para pavimentos (NTC 2017)")
def endpoint_ntc2017(req: motor_vias.NTC2017Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc2017(req)


@router.post("/ntc/4342", summary="Geotextiles — retención asfáltica (NTC 4342)")
def endpoint_ntc4342(req: motor_vias.NTC4342Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc4342(req)


@router.post("/ntc/121", summary="Cemento hidráulico — especificación de desempeño (NTC 121)")
def endpoint_ntc121(req: motor_vias.NTC121Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc121(req)


@router.post("/ntc/1299", summary="Aditivos químicos para concreto (NTC 1299 / ASTM C494)")
def endpoint_ntc1299(req: motor_vias.NTC1299Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc1299(req)


@router.post("/ntc/1362", summary="Cemento hidráulico blanco (NTC 1362)")
def endpoint_ntc1362(req: motor_vias.NTC1362Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc1362(req)


@router.post("/ntc/3459", summary="Agua para elaboración de concreto (NTC 3459)")
def endpoint_ntc3459(req: motor_vias.NTC3459Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc3459(req)


@router.post("/ntc/3493", summary="Cenizas volantes y puzolanas naturales — aditivo mineral (NTC 3493 / ASTM C618)")
def endpoint_ntc3493(req: motor_vias.NTC3493Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc3493(req)


@router.post("/ntc/3502", summary="Aditivos incorporadores de aire (NTC 3502 / ASTM C260)")
def endpoint_ntc3502(req: motor_vias.NTC3502Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc3502(req)


@router.post("/ntc/3760", summary="Pigmentos para concreto coloreado (NTC 3760 / ASTM C979)")
def endpoint_ntc3760(req: motor_vias.NTC3760Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc3760(req)


@router.post("/ntc/4018", summary="Escoria de alto horno granulada y molida (NTC 4018 / ASTM C989)")
def endpoint_ntc4018(req: motor_vias.NTC4018Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc4018(req)


@router.post("/ntc/4024", summary="Prefabricados de concreto — muestreo y ensayo (NTC 4024)")
def endpoint_ntc4024(req: motor_vias.NTC4024Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc4024(req)


@router.post("/ntc/4924/agregado", summary="Agregados livianos para mampostería (NTC 4924 / ASTM C331)")
def endpoint_ntc4924_agregado(req: motor_vias.NTC4924AgregadoRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc4924_agregado(req)


@router.post("/ntc/4924/mamposteria", summary="Unidad de mampostería con agregado liviano (NTC 4924)")
def endpoint_ntc4924_mamposteria(req: motor_vias.NTC4924MamposteriaRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc4924_mamposteria(req)


@router.post("/ntc/5147", summary="Resistencia a la abrasión — arena y disco metálico (NTC 5147)")
def endpoint_ntc5147(req: motor_vias.NTC5147Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.verificar_ntc5147(req)


@router.post("/ntc/6008", summary="Terminología y clasificación de adoquines y losetas (NTC 6008)")
def endpoint_ntc6008(req: motor_vias.NTC6008Request, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_vias.buscar_termino_ntc6008(req)
