"""
motor-estructural — Motor de Análisis Estructural INFRACORTEX
=============================================================
Pipeline: IFC (BIM) → Topología → PINN float64 → Cargas NSR-10 → Chequeo Nudo
Empresa física: Infracortex | App: StructAI
"""
from .infracortex_core import InfracortexEngine, MultidisciplinaryPINN
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
    "MultidisciplinaryPINN",
    "calcular_demanda_cortante_nudo",
    "ZONA_SISMICA_ATLANTICO",
    "CARGAS_GRAVEDAD_DEFAULT",
    "InfracortexVisionSensor",
    "AnalisisNudoRequest",
    "AnalisisNudoResponse",
    "InspeccionEstribosResponse",
    "ResultadoEstriboItem",
]
