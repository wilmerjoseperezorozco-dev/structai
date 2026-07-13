"""
AquaAI — Módulo PTAR: Planta de Tratamiento de Aguas Residuales
Referencia:
  - RAS 2000 Título E — Tratamiento de aguas residuales (VIGENTE)
  - Resolución 0631/2015 MADS — Valores máximos permisibles vertimientos
  - Decreto 1076/2015 Art. 2.2.3.3 — Permisos de vertimiento

Tecnologías implementadas:
  UASB              — Reactor Anaerobio de Flujo Ascendente (nivel bajo/medio)
  Lodos activados   — Convencional aireación extendida (nivel medio-alto/alto)
  Filtro percolador — Nivel medio, comunidades con restricciones de energía
  Laguna facultativa — Nivel bajo, disponibilidad de terreno amplio

Cargas per cápita (RAS Título E Tabla E.4.1):
  DBO₅ = 40–60 g/hab/día  → diseño: 50 g/hab/día
  SST  = 50–70 g/hab/día  → diseño: 60 g/hab/día
"""

import math
from .schemas_saneamiento import (
    PTARRequest, PTARResponse, BalanceLodos, TecnologiaPTAR, TipoCuerpoReceptor,
)

# ─── Cargas per cápita (RAS Título E) ────────────────────────────────────────
DBO5_PER_CAPITA_G_HAB_DIA = 50.0
SST_PER_CAPITA_G_HAB_DIA  = 60.0

# ─── Límites de vertimiento Res 0631/2015 (mg/L) ─────────────────────────────
# Cuerpo receptor: río / quebrada / lago / suelo
LIMITES_RES0631: dict[str, dict[str, float]] = {
    "rio":       {"DBO5": 90.0, "SST": 90.0,  "pH_min": 6.0, "pH_max": 9.0},
    "quebrada":  {"DBO5": 90.0, "SST": 90.0,  "pH_min": 6.0, "pH_max": 9.0},
    "lago":      {"DBO5": 30.0, "SST": 30.0,  "pH_min": 6.5, "pH_max": 8.5},
    "suelo":     {"DBO5": 300.0,"SST": 300.0, "pH_min": 6.0, "pH_max": 9.0},
}

# ─── Parámetros de diseño por tecnología (RAS Título E) ──────────────────────

def _calcular_uasb(Q_m3dia: float, dbo_mg_l: float, sst_mg_l: float, advertencias: list) -> dict:
    """
    UASB — Upflow Anaerobic Sludge Blanket
    Referencia: RAS Título E Sección E.9
    """
    # Velocidad ascensional: 0.5–0.8 m/h para aguas residuales domésticas
    v_asc = 0.6        # m/h — valor central
    Q_m3h = Q_m3dia / 24.0
    area   = Q_m3h / v_asc
    # TRH mínimo 4–8 h
    trh_h  = 6.0
    vol    = Q_m3h * trh_h
    altura = vol / area
    if altura > 6.0:
        # Ajustar: dividir en celdas o aumentar área
        n_reactores = math.ceil(altura / 5.0)
        area *= n_reactores
        altura = vol / area
        advertencias.append(
            f"Altura UASB calculada > 6 m — se distribuye en {n_reactores} reactores en paralelo."
        )

    efic_dbo  = 0.70   # 70% remoción DBO en UASB doméstico típico
    efic_sst  = 0.65

    return {
        "tecnologia":          "UASB",
        "area_m2":             round(area, 2),
        "altura_util_m":       round(min(altura, 5.5), 2),
        "volumen_m3":          round(vol, 2),
        "trh_h":               trh_h,
        "velocidad_ascensional_m_h": v_asc,
        "eficiencia_dbo_pct":  efic_dbo * 100,
        "eficiencia_sst_pct":  efic_sst * 100,
        "norma_ref":           "RAS 2000 Título E Sección E.9 — UASB doméstico",
        "nota":                "Requiere postratamiento (filtro biológico o laguna de pulimiento) si el cuerpo receptor exige DBO < 90 mg/L.",
        "_efic_dbo": efic_dbo, "_efic_sst": efic_sst,
    }


def _calcular_lodos_activados(Q_m3dia: float, dbo_mg_l: float, sst_mg_l: float, advertencias: list) -> dict:
    """
    Lodos activados — aireación extendida
    Referencia: RAS Título E Sección E.7, Metcalf & Eddy
    """
    # Parámetros de diseño — aireación extendida (SRT largo, sin digestión separada)
    SRT = 20.0          # días — tiempo de retención celular (aireación extendida)
    Y   = 0.5           # kg SSV / kg DBO — coeficiente de producción
    Kd  = 0.05          # 1/día — coeficiente de decaimiento endógeno
    SSV_SST = 0.80      # relación SSV/SST en licor mezcla
    MLSS = 3500.0       # mg/L — sólidos en suspensión licor mezcla
    Q_m3h = Q_m3dia / 24.0

    S0  = dbo_mg_l
    Se  = 20.0          # DBO efluente objetivo (mg/L) — aireación extendida
    efic_dbo = (S0 - Se) / S0

    # Producción neta de lodos (kg SSV/día)
    Pxv = (Y * (S0 - Se) * Q_m3dia / 1000) / (1 + Kd * SRT)
    Px  = Pxv / SSV_SST   # kg SST/día

    # Volumen del reactor
    vol_reactor = (Px * SRT * 1000) / MLSS   # m³

    # TRH
    trh_h = (vol_reactor / Q_m3h)

    efic_sst = 0.92   # lodos activados: alta remoción SST

    if trh_h < 18:
        advertencias.append(
            "TRH < 18 h en aireación extendida — revisar MLSS o SRT. "
            "RAS Título E recomienda TRH ≥ 18–24 h para aireación extendida."
        )

    return {
        "tecnologia":         "Lodos activados — Aireación extendida",
        "volumen_reactor_m3": round(vol_reactor, 2),
        "trh_h":              round(trh_h, 1),
        "SRT_dias":           SRT,
        "MLSS_mg_l":          MLSS,
        "produccion_lodos_kg_sst_dia": round(Px, 2),
        "dbo_efluente_mg_l":  Se,
        "eficiencia_dbo_pct": round(efic_dbo * 100, 1),
        "eficiencia_sst_pct": round(efic_sst * 100, 1),
        "norma_ref":          "RAS 2000 Título E Sección E.7 — Lodos activados aireación extendida",
        "_efic_dbo": efic_dbo, "_efic_sst": efic_sst,
        "_Px": Px,
    }


def _calcular_laguna_facultativa(Q_m3dia: float, dbo_mg_l: float, advertencias: list) -> dict:
    """
    Laguna facultativa de estabilización
    Referencia: RAS Título E Sección E.10, McGarry & Pescod
    """
    # Diseño: carga superficial según temperatura (Colombia clima templado promedio 20°C)
    T_agua = 20.0
    # Carga superficial kg DBO₅/ha/día (McGarry & Pescod modificado para Colombia)
    Cs = 357.4 * 1.107 ** (T_agua - 20)   # ≈ 357 kg DBO/ha/día a 20°C
    carga_dbo_kg_dia = dbo_mg_l * Q_m3dia / 1000.0
    area_ha = carga_dbo_kg_dia / Cs
    area_m2 = area_ha * 10000

    profundidad = 1.5   # m — laguna facultativa típica Colombia
    vol = area_m2 * profundidad
    trh_dias = vol / Q_m3dia

    efic_dbo = 0.75
    efic_sst = 0.60

    advertencias.append(
        f"Laguna facultativa requiere {area_ha:.2f} ha de terreno disponible. "
        "Verificar disponibilidad y distancia a zonas pobladas (≥ 500 m, RAS Título E Sección E.10.5)."
    )

    return {
        "tecnologia":         "Laguna facultativa de estabilización",
        "area_ha":            round(area_ha, 3),
        "area_m2":            round(area_m2, 0),
        "profundidad_m":      profundidad,
        "volumen_m3":         round(vol, 0),
        "trh_dias":           round(trh_dias, 1),
        "carga_superficial_kg_dbo_ha_dia": round(Cs, 1),
        "eficiencia_dbo_pct": efic_dbo * 100,
        "eficiencia_sst_pct": efic_sst * 100,
        "norma_ref":          "RAS 2000 Título E Sección E.10 — Lagunas de estabilización",
        "_efic_dbo": efic_dbo, "_efic_sst": efic_sst, "_Px": 0,
    }


def calcular_ptar(req: PTARRequest) -> PTARResponse:
    advertencias: list[str] = []

    # ── 1. Caudal de aguas residuales ─────────────────────────────────────
    Q_ar_ls    = req.caudal_acueducto_ls * req.factor_retorno
    Q_ar_m3dia = Q_ar_ls * 86400 / 1000.0

    # ── 2. Cargas contaminantes ───────────────────────────────────────────
    # Usar datos medidos si se proveen; si no, estimar per cápita
    if req.dbo5_cruda_mg_l is not None:
        dbo_mg_l = req.dbo5_cruda_mg_l
    else:
        # g/hab/día × hab / m³/día = g/m³ = mg/L
        dbo_mg_l = DBO5_PER_CAPITA_G_HAB_DIA * req.poblacion_diseno / Q_ar_m3dia
        advertencias.append(
            "DBO₅ estimada per cápita (50 g/hab/día — RAS Título E Tabla E.4.1). "
            "Para mayor precisión, medir en campo antes del diseño final."
        )

    if req.sst_crudo_mg_l is not None:
        sst_mg_l = req.sst_crudo_mg_l
    else:
        sst_mg_l = SST_PER_CAPITA_G_HAB_DIA * req.poblacion_diseno / Q_ar_m3dia

    carga_dbo_kg_dia = dbo_mg_l * Q_ar_m3dia / 1000.0
    carga_sst_kg_dia = sst_mg_l * Q_ar_m3dia / 1000.0

    # ── 3. Dimensionamiento según tecnología ──────────────────────────────
    t = req.tecnologia
    if t == TecnologiaPTAR.UASB:
        dim = _calcular_uasb(Q_ar_m3dia, dbo_mg_l, sst_mg_l, advertencias)
    elif t == TecnologiaPTAR.LODOS_ACTIVADOS:
        dim = _calcular_lodos_activados(Q_ar_m3dia, dbo_mg_l, sst_mg_l, advertencias)
    elif t == TecnologiaPTAR.LAGUNA_FACULTATIVA:
        dim = _calcular_laguna_facultativa(Q_ar_m3dia, dbo_mg_l, advertencias)
    else:
        # Filtro percolador — simplificado
        efic_dbo = 0.70; efic_sst = 0.65
        vol = Q_ar_m3dia * 0.25
        dim = {
            "tecnologia": "Filtro percolador de tasa media",
            "volumen_medio_filtrante_m3": round(vol, 2),
            "carga_hidraulica_m3_m2_dia": 4.0,
            "area_m2": round(vol / 2.0, 2),
            "eficiencia_dbo_pct": efic_dbo * 100,
            "eficiencia_sst_pct": efic_sst * 100,
            "norma_ref": "RAS 2000 Título E Sección E.8",
            "_efic_dbo": efic_dbo, "_efic_sst": efic_sst, "_Px": carga_dbo_kg_dia * 0.3,
        }

    efic_dbo = dim.pop("_efic_dbo")
    efic_sst = dim.pop("_efic_sst")
    Px       = dim.pop("_Px", carga_dbo_kg_dia * 0.35)

    # ── 4. Calidad del efluente ───────────────────────────────────────────
    dbo_efluente = dbo_mg_l * (1 - efic_dbo)
    sst_efluente = sst_mg_l * (1 - efic_sst)

    # ── 5. Verificar Res 0631/2015 ────────────────────────────────────────
    limites = LIMITES_RES0631.get(req.tipo_cuerpo_receptor.value, LIMITES_RES0631["rio"])
    cumple = (dbo_efluente <= limites["DBO5"] and sst_efluente <= limites["SST"])

    if not cumple:
        advertencias.append(
            f"⚠ Efluente NO cumple Res 0631/2015 para {req.tipo_cuerpo_receptor.value}: "
            f"DBO₅ {dbo_efluente:.1f} mg/L (límite {limites['DBO5']}) / "
            f"SST {sst_efluente:.1f} mg/L (límite {limites['SST']}). "
            "Considerar tecnología de mayor eficiencia o postratamiento."
        )

    # ── 6. Balance de lodos ───────────────────────────────────────────────
    # Px = producción de lodos secos; convertir a volumen al 1% de sólidos
    vol_lodos_m3_dia = Px / (0.01 * 1000)   # 1% sólidos = 10 kg/m³

    destino = (
        "Compostaje o aplicación agrícola con licencia ambiental (Decreto 1076/2015 Art. 2.2.3.3.5)"
        if req.nivel_complejidad in ("bajo", "medio")
        else "Digestión aerobia + deshidratación mecánica (centrífuga o filtro banda)"
    )

    return PTARResponse(
        caudal_ar_ls=round(Q_ar_ls, 3),
        caudal_ar_m3_dia=round(Q_ar_m3dia, 2),
        dbo5_cruda_mg_l=round(dbo_mg_l, 1),
        sst_crudo_mg_l=round(sst_mg_l, 1),
        carga_dbo_kg_dia=round(carga_dbo_kg_dia, 2),
        carga_sst_kg_dia=round(carga_sst_kg_dia, 2),
        tecnologia=dim.get("tecnologia", t.value),
        dimensionamiento=dim,
        eficiencia_dbo_pct=round(efic_dbo * 100, 1),
        dbo_efluente_mg_l=round(dbo_efluente, 1),
        sst_efluente_mg_l=round(sst_efluente, 1),
        limite_res0631_dbo=limites["DBO5"],
        cumple_res0631=cumple,
        balance_lodos=BalanceLodos(
            produccion_lodos_kg_dia=round(Px, 2),
            volumen_lodos_m3_dia=round(vol_lodos_m3_dia, 2),
            destino_recomendado=destino,
        ),
        normas_aplicadas=[
            "RAS 2000 Título E — Tratamiento de aguas residuales (VIGENTE)",
            "Resolución 0631/2015 MADS — Valores máximos permisibles vertimientos",
            "Decreto 1076/2015 Art. 2.2.3.3 — Permisos de vertimiento",
        ],
        advertencias=advertencias,
    )
