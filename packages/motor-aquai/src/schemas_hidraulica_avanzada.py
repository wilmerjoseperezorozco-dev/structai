"""
AquaAI — Schemas Pydantic: Hidráulica Avanzada
  - Manning: alcantarillado a gravedad (RAS 2000 Título D / Res 0330/2017 Tít. D)
  - Golpe de ariete: transitorio hidráulico (RAS 2000 Título B)
  - Estación de bombeo: curva sistema, TDH, potencia, NPSH (RAS 2000 Tít. B §B.8)
"""
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ─── Enumeraciones ────────────────────────────────────────────────────────────

class MaterialTuberia(str, Enum):
    PVC       = "PVC"
    HDPE      = "HDPE"
    CONCRETO  = "concreto"
    CONCRETO_REFORZADO = "concreto_reforzado"
    ACERO     = "acero"
    GRP       = "grp"          # Fibra de vidrio (alcantarillado)
    GRES      = "gres"         # Vitrificado

class TipoBomba(str, Enum):
    CENTRIFUGA        = "centrifuga"
    CENTRIFUGA_MULTI  = "centrifuga_multietapa"
    AXIAL             = "axial"
    SUMERGIBLE        = "sumergible"

class TipoFluidoBombeo(str, Enum):
    AGUA_POTABLE  = "agua_potable"
    AGUA_CRUDA    = "agua_cruda"
    AGUA_RESIDUAL = "agua_residual"   # Ajusta eficiencia y NPSH


# ─── Manning ──────────────────────────────────────────────────────────────────

class ManningRequest(BaseModel):
    caudal_diseno_ls: float     = Field(..., gt=0, description="Caudal de diseño (L/s)")
    pendiente_m_m: float        = Field(..., gt=0, le=0.30,
                                        description="Pendiente longitudinal (m/m), ej. 0.005 = 5‰")
    material: MaterialTuberia   = MaterialTuberia.PVC
    diametro_nominal_mm: Optional[float] = Field(
        None, gt=0,
        description="Si se provee, verifica ese diámetro. Si no, el motor selecciona el mínimo."
    )
    relacion_tirante_max: float = Field(
        default=0.75,
        description="Relación máxima d/D de lámina (RAS D.3.4: máx 0.75 para saneamiento)"
    )


class ManningResponse(BaseModel):
    diametro_nominal_mm: float
    diametro_interno_mm: float
    caudal_llena_seccion_ls: float      = Field(description="Qf — caudal a sección llena (L/s)")
    velocidad_llena_seccion_ms: float   = Field(description="Vf a sección llena (m/s)")
    relacion_q_qf: float                = Field(description="Q/Qf — fracción de la sección utilizada")
    relacion_tirante_d_D: float         = Field(description="d/D — relación de tirante real")
    velocidad_real_ms: float            = Field(description="Velocidad real en el tubo (m/s)")
    cumple_velocidad_min: bool          = Field(description="V ≥ 0.45 m/s (autolimpieza RAS D.3.5)")
    cumple_velocidad_max: bool          = Field(description="V ≤ 3.0 m/s (PVC/HDPE) o 6.0 m/s (concreto)")
    cumple_tirante: bool                = Field(description="d/D ≤ relacion_tirante_max")
    pendiente_minima_m_m: float         = Field(description="Pendiente mínima para V=0.45 m/s con este diámetro")
    coeficiente_manning_n: float
    normas_aplicadas: list[str]
    advertencias: list[str]


# ─── Golpe de ariete ──────────────────────────────────────────────────────────

class ArieteRequest(BaseModel):
    caudal_ls: float            = Field(..., gt=0, description="Caudal circulante (L/s)")
    diametro_interno_mm: float  = Field(..., gt=0, description="Diámetro interno de la tubería (mm)")
    longitud_m: float           = Field(..., gt=0, description="Longitud de la línea (m)")
    velocidad_cierre_s: float   = Field(
        ..., gt=0,
        description="Tiempo de cierre de la válvula o paro de bomba (s)"
    )
    material: MaterialTuberia   = MaterialTuberia.PVC
    espesor_pared_mm: float     = Field(..., gt=0, description="Espesor de pared de la tubería (mm)")
    presion_estatica_m: float   = Field(
        ..., gt=0,
        description="Presión estática de trabajo (m.c.a.) — necesaria para verificar clase de tubería"
    )
    temperatura_agua_c: float   = Field(default=20.0, ge=0, le=40.0)


class ArieteResponse(BaseModel):
    velocidad_flujo_ms: float
    celeridad_onda_ms: float        = Field(description="a — velocidad de propagación de la onda (m/s)")
    tiempo_critico_s: float         = Field(description="Tc = 2L/a — tiempo crítico de reflexión (s)")
    cierre_rapido: bool             = Field(description="True si T_cierre < Tc (golpe severo)")
    sobrepresion_maxima_m: float    = Field(description="ΔH = a·ΔV/g (m.c.a.) — Joukowski")
    presion_maxima_total_m: float   = Field(description="H_max = H_estatica + ΔH (m.c.a.)")
    presion_minima_m: float         = Field(description="H_min = H_estatica - ΔH (puede ser negativa → cavitación)")
    riesgo_cavitacion: bool         = Field(description="True si H_min < -10 m (presión absoluta < 0)")
    clase_presion_recomendada: str  = Field(description="Clase de presión mínima de la tubería según norma NTC")
    medidas_mitigacion: list[str]
    normas_aplicadas: list[str]


# ─── Estación de bombeo ───────────────────────────────────────────────────────

class BombeoRequest(BaseModel):
    caudal_diseno_ls: float     = Field(..., gt=0)
    altura_geometrica_m: float  = Field(..., description="Hg — diferencia de cotas succión-descarga (m)")
    longitud_succion_m: float   = Field(default=10.0, ge=0, description="Longitud línea de succión (m)")
    longitud_descarga_m: float  = Field(..., gt=0, description="Longitud línea de impulsión (m)")
    diametro_succion_mm: float  = Field(..., gt=0, description="Diámetro interno tubería succión (mm)")
    diametro_descarga_mm: float = Field(..., gt=0, description="Diámetro interno tubería impulsión (mm)")
    material_succion: MaterialTuberia  = MaterialTuberia.HDPE
    material_descarga: MaterialTuberia = MaterialTuberia.HDPE
    n_accesorios_codos: int     = Field(default=2, ge=0)
    n_accesorios_valvulas: int  = Field(default=2, ge=0)
    altitud_msnm: float         = Field(default=1000.0, ge=0,
                                        description="Altitud de la estación (msnm) — afecta NPSH y presión de vapor")
    tipo_fluido: TipoFluidoBombeo = TipoFluidoBombeo.AGUA_POTABLE
    eficiencia_bomba_pct: float  = Field(default=75.0, ge=40.0, le=95.0,
                                         description="Eficiencia hidráulica de la bomba (%)")
    eficiencia_motor_pct: float  = Field(default=92.0, ge=70.0, le=97.0,
                                         description="Eficiencia del motor eléctrico (%)")
    n_bombas_paralelo: int       = Field(default=1, ge=1, le=6,
                                         description="Número de bombas en paralelo (una bomba de reserva recomendada)")


class BombeoResponse(BaseModel):
    caudal_por_bomba_ls: float
    # Curva del sistema
    perdidas_friccion_succion_m: float
    perdidas_friccion_descarga_m: float
    perdidas_menores_m: float
    perdidas_totales_m: float
    tdh_m: float                = Field(description="TDH — Altura Dinámica Total (m)")
    # Potencia
    potencia_hidraulica_kw: float
    potencia_al_freno_kw: float = Field(description="Potencia en el eje de la bomba (kW)")
    potencia_instalada_kw: float= Field(description="Potencia del motor: P_freno / η_motor (kW)")
    consumo_kwh_mes: float      = Field(description="Estimado de consumo eléctrico (kWh/mes)")
    # NPSH
    npsh_disponible_m: float    = Field(description="NPSHd — disponible en la estación (m)")
    npsh_recomendado_min_m: float
    alerta_cavitacion: bool
    # Configuración
    n_bombas_operacion: int
    n_bombas_reserva: int
    configuracion: str
    normas_aplicadas: list[str]
    advertencias: list[str]
