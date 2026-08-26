"""
motor-estructural — Motor de Análisis Estructural INFRACORTEX
=============================================================
Pipeline: IFC (BIM) → Topología → Cargas NSR-10 → Chequeo Nudo
Empresa física: Infracortex | App: StructAI

(La PINN de PyTorch que este pipeline mencionaba se eliminó el 2026-08-26:
era código muerto, nunca se llamaba desde ningún camino real. Ver
infracortex_core.py para el detalle.)
"""
from .infracortex_core import InfracortexEngine
from .load_engine import (
    calcular_demanda_cortante_nudo,
    ZONA_SISMICA_ATLANTICO,
    CARGAS_GRAVEDAD_DEFAULT,
)
from .vision_engine import InfracortexVisionSensor
from .models import (
    AnalisisNudoRequest,
    AnalisisNudoResponse,
    InspeccionEstribosResponse,
    ResultadoEstriboItem,
)

__all__ = [
    "InfracortexEngine",
    "calcular_demanda_cortante_nudo",
    "ZONA_SISMICA_ATLANTICO",
    "CARGAS_GRAVEDAD_DEFAULT",
    "InfracortexVisionSensor",
    "AnalisisNudoRequest",
    "AnalisisNudoResponse",
    "InspeccionEstribosResponse",
    "ResultadoEstriboItem",
]
