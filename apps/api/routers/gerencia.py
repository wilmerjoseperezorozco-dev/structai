"""
══════════════════════════════════════════════════════════════
GERENCIA ROUTER — Earned Value Management (EVM) + ML predictivo
Capa gerencial/ciencia de datos, complementaria de StructAI, montada bajo
el prefijo /gerencia. Mismo patrón que motor-apu/motor-aquai/motor-geopot/
motor-vias: paquete propio en packages/, cargado vía importlib para evitar
colisión con el nombre genérico "src".
══════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

# apps/api ya está en sys.path para cuando este módulo se importa (main.py lo
# agrega antes de hacer `from routers.gerencia import router`).
from auth import AuthenticatedUser, get_current_user

ROOT = Path(__file__).resolve().parents[3]  # monorepo/

import importlib.util as _ilu
_gerencia_init = ROOT / "packages" / "motor-gerencia" / "src" / "__init__.py"
_spec = _ilu.spec_from_file_location("motor_gerencia", _gerencia_init, submodule_search_locations=[str(_gerencia_init.parent)])
motor_gerencia = _ilu.module_from_spec(_spec)
sys.modules["motor_gerencia"] = motor_gerencia
_spec.loader.exec_module(motor_gerencia)

router = APIRouter(prefix="/gerencia", tags=["Gerencia"])


@router.get("/salud")
def salud():
    return {"estado": "ok", "motor": "Gerencia", "base": "EVM (PMBOK) + ML predictivo sobre series de avance"}


@router.get("/glosario", summary="Metadatos de los KPIs EVM (fórmula, unidad, rangos)")
def endpoint_glosario():
    return motor_gerencia.KPI_META


# ── EVM ────────────────────────────────────────────────────────────────────

@router.post("/evm/snapshot", summary="KPIs EVM (CPI/SPI/QPI/PPI/SV/CV/TCPI/EAC) de un único período")
def endpoint_snapshot(req: motor_gerencia.SnapshotKPIRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_gerencia.calcular_snapshot(req)


@router.post("/evm/portafolio", summary="Trazabilidad cruzada multi-obra: rankings, agregados y alertas")
def endpoint_portafolio(req: motor_gerencia.PortfolioRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_gerencia.analizar_portafolio(req)


# ── ML predictivo ────────────────────────────────────────────────────────────

@router.post("/ml/riesgo", summary="Score de riesgo compuesto 0-100 basado en tendencias de CPI/SPI/QPI/PPI")
def endpoint_riesgo(req: motor_gerencia.ProjectSeriesRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return motor_gerencia.calcular_riesgo(req)


@router.post("/ml/forecast", summary="Proyección de KPIs para los próximos N períodos (regresión lineal)")
def endpoint_forecast(req: motor_gerencia.ProjectSeriesRequest, user: AuthenticatedUser = Depends(get_current_user)):
    resultado = motor_gerencia.calcular_forecast_kpis(req)
    if not resultado:
        raise HTTPException(status_code=422, detail="Se requieren al menos 3 snapshots para proyectar")
    return resultado


@router.post("/ml/fecha-termino", summary="Estimación de fecha de término revisada según SPI actual")
def endpoint_fecha_termino(req: motor_gerencia.ProjectSeriesRequest, user: AuthenticatedUser = Depends(get_current_user)):
    resultado = motor_gerencia.calcular_fecha_termino(req)
    if "error" in resultado:
        raise HTTPException(status_code=422, detail=resultado["error"])
    return resultado


@router.post("/ml/anomalias", summary="Detección de anomalías (z-score) en la serie de un KPI")
def endpoint_anomalias(req: motor_gerencia.ProjectSeriesRequest, user: AuthenticatedUser = Depends(get_current_user)):
    resultado = motor_gerencia.detectar_anomalias(req)
    if "error" in resultado:
        raise HTTPException(status_code=422, detail=resultado["error"])
    return resultado


@router.post("/ml/correlacion", summary="Matriz de correlación de Pearson entre CPI/SPI/QPI/PPI")
def endpoint_correlacion(req: motor_gerencia.ProjectSeriesRequest, user: AuthenticatedUser = Depends(get_current_user)):
    resultado = motor_gerencia.calcular_correlacion(req)
    if "error" in resultado:
        raise HTTPException(status_code=422, detail=resultado["error"])
    return resultado
