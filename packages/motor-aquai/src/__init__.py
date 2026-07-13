from .schemas import (
    NivelComplejidad, ClimaRegion, MetodoPoblacion,
    PoblacionRequest, PoblacionResponse,
    CaudalesRequest, CaudalesResponse,
    HazenWilliamsRequest, HazenWilliamsResponse,
    HidrologiaRequest, HidrologiaResponse, MetodoConcentracion,
    RegistroConsultaRequest, RegistroConsultaResponse,
)
from .schemas_hidraulica_avanzada import (
    MaterialTuberia, TipoFluidoBombeo,
    ManningRequest, ManningResponse,
    ArieteRequest, ArieteResponse,
    BombeoRequest, BombeoResponse,
)
from .schemas_saneamiento import (
    CoagulanteType, TecnologiaPTAR, TipoCuerpoReceptor,
    PTAPRequest, PTAPResponse,
    PTARRequest, PTARResponse, BalanceLodos,
)
from .schemas_tarifario import (
    TipoPrestador, Estrato, ServicioTarifario,
    TarifaRequest, TarifaResponse,
    ReporteSUIRequest, ReporteSUIResponse,
)

from .poblacion import proyectar_poblacion
from .caudales import calcular_caudales
from .hidraulica import calcular_hazen_williams
from .hidrologia import calcular_hidrologia
from .manning import calcular_manning
from .ariete import calcular_ariete
from .bombeo import calcular_bombeo
from .ptap import calcular_ptap
from .ptar import calcular_ptar
from .tarifario import calcular_tarifa
from .sui_reporte import generar_reporte_sui

__all__ = [
    "NivelComplejidad", "ClimaRegion", "MetodoPoblacion",
    "PoblacionRequest", "PoblacionResponse",
    "CaudalesRequest", "CaudalesResponse",
    "HazenWilliamsRequest", "HazenWilliamsResponse",
    "HidrologiaRequest", "HidrologiaResponse", "MetodoConcentracion",
    "RegistroConsultaRequest", "RegistroConsultaResponse",
    "MaterialTuberia", "TipoFluidoBombeo",
    "ManningRequest", "ManningResponse",
    "ArieteRequest", "ArieteResponse",
    "BombeoRequest", "BombeoResponse",
    "CoagulanteType", "TecnologiaPTAR", "TipoCuerpoReceptor",
    "PTAPRequest", "PTAPResponse",
    "PTARRequest", "PTARResponse", "BalanceLodos",
    "TipoPrestador", "Estrato", "ServicioTarifario",
    "TarifaRequest", "TarifaResponse",
    "ReporteSUIRequest", "ReporteSUIResponse",
    "proyectar_poblacion", "calcular_caudales", "calcular_hazen_williams",
    "calcular_hidrologia", "calcular_manning", "calcular_ariete",
    "calcular_bombeo", "calcular_ptap", "calcular_ptar",
    "calcular_tarifa", "generar_reporte_sui",
]
