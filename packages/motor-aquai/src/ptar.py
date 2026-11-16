"""
AquaAI — Módulo PTAR: Planta de Tratamiento de Aguas Residuales (#236).

Norma de diseño: Resolución 0330 de 2017 (reemplazó al RAS 2000 Título E para diseño):
  art. 164 caudal de diseño · art. 189 UASB · art. 191 lodos activados · art. 192 filtros percoladores ·
  art. 197 laguna facultativa (el sistema lagunar completo está en `lagunas.py`).
Vertimiento: Resolución 0631 de 2015, art. 8 (`vertimientos.py`).

Fallo explícito (regla 1): la temperatura del agua es obligatoria para UASB y laguna, y la profundidad para la
laguna; el cuerpo receptor «suelo» lanza error porque la Res. 0631 no aplica al suelo.
Los valores de diseño que el motor elige (no son datos del usuario) quedan declarados en `supuestos` del contrato.
"""
from __future__ import annotations

from . import lagunas as _lag
from . import vertimientos
from .schemas_saneamiento import (
    PTARRequest, PTARResponse, BalanceLodos, TecnologiaPTAR,
)

RES0330 = "Resolución 0330 de 2017"

# ─── Estimación per cápita (solo si no hay caracterización) ─────────────────
# Valores típicos de literatura; el RAS 2000 Título E los tabulaba, pero fue derogado para diseño por la Res. 0330,
# que exige caracterización. Se usan solo como estimación preliminar, con advertencia.
DBO5_PER_CAPITA_G_HAB_DIA = 50.0
SST_PER_CAPITA_G_HAB_DIA = 60.0

# ─── UASB (Res. 0330 art. 189, tablas 31 y 32) ──────────────────────────────
UASB_PROFUNDIDAD = (4.5, 6.0)                 # m
UASB_V_CAUDAL_MEDIO = (0.5, 0.7)              # m/h (tabla 32)
UASB_V_CAUDAL_MAXIMO_MAX = 1.1                # m/h (tabla 32)
UASB_TRH_TABLA31 = ((16.0, 20.0, 10.0, 14.0),  # (T desde, T hasta excl., TRH mín, TRH máx) en °C y h
                    (20.0, 26.0 + 1e-9, 6.0, 9.0),
                    (26.0 + 1e-9, float("inf"), 6.0, float("inf")))
UASB_EFIC_DBO, UASB_EFIC_SST = 0.70, 0.65     # valores típicos; la tabla 29 de la Res. 0330 no está en el corpus

# ─── Filtro percolador de tasa intermedia (Res. 0330 art. 192, tabla 38) ────
FP_CARGA_HIDRAULICA = (4.0, 10.0)             # m³/m²·d
FP_CARGA_ORGANICA = (0.24, 0.48)              # kg DBO/m³·d
FP_PROFUNDIDAD = (1.8, 2.4)                   # m
FP_RECIRCULACION = (0.0, 1.0)
FP_REMOCION_DBO = (0.50, 0.80)                # se acredita el mínimo (conservador)

# ─── Lodos activados, aireación extendida (Res. 0330 art. 191) ──────────────
# La tabla 36 de la Res. 0330 no está en el corpus: parámetros de literatura (Metcalf & Eddy), declarados.
LA_SRT_D, LA_Y, LA_KD, LA_SSV_SST, LA_MLSS, LA_SE = 20.0, 0.5, 0.05, 0.80, 3500.0, 20.0
LA_EFIC_SST = 0.92

LODOS_CONCENTRACION_KG_M3 = 10.0              # 1 % de sólidos
UASB_PRODUCCION_LODOS_KG_SST_KG_DBO = 0.35    # sin respaldo en la Res. 0330 del corpus: estimación declarada


def _uasb(q_m3dia: float, temperatura: float | None, factor_pico: float | None, advertencias: list, borde: list) -> dict:
    """Optimiza TRH y velocidad ascensional dentro de las tablas 31 y 32 y la profundidad del art. 189.

    Volumen mínimo ⇒ TRH mínimo. Con H = v·TRH ∈ [4,5; 6] y v ≤ v_máx: TRH* = máx(TRH_tabla, 4,5 / v_máx);
    luego v = mín(v_máx, 6 / TRH*) da el área mínima. Forma cerrada: el problema tiene dos variables acotadas.
    """
    if temperatura is None:
        raise ValueError(f"UASB: la temperatura del agua residual es obligatoria ({RES0330}, art. 189, tabla 31). "
                         "No se asume ningún valor.")
    tramo = next((f for f in UASB_TRH_TABLA31 if f[0] <= temperatura < f[1]), None)
    if tramo is None:
        raise ValueError(f"UASB: temperatura {temperatura:g} °C por debajo de 16 °C, fuera de la tabla 31 del {RES0330}, "
                         "art. 189: el reactor anaerobio no está respaldado por la norma a esa temperatura.")
    trh_lo, trh_hi = tramo[2], tramo[3]
    v_max = UASB_V_CAUDAL_MEDIO[1]
    if factor_pico is not None:
        v_max = min(v_max, UASB_V_CAUDAL_MAXIMO_MAX / factor_pico)
    else:
        advertencias.append("UASB: sin factor pico no se verificó la velocidad a caudal máximo (≤ 1,1 m/h, tabla 32).")
    if v_max < UASB_V_CAUDAL_MEDIO[0]:
        raise ValueError(f"UASB: con factor pico {factor_pico:g} la velocidad a caudal medio debería ser < 0,5 m/h "
                         f"({RES0330}, art. 189, tabla 32): no hay diseño que cumpla ambas velocidades.")
    trh = max(trh_lo, UASB_PROFUNDIDAD[0] / v_max)
    if trh > trh_hi + 1e-9:
        raise ValueError(f"UASB: el TRH necesario para la profundidad mínima ({trh:.2f} h) supera el de la tabla 31 "
                         f"({trh_hi:g} h) del {RES0330}, art. 189.")
    v = min(v_max, UASB_PROFUNDIDAD[1] / trh)
    if trh == trh_lo:
        borde.append("UASB: TRH en el mínimo de la tabla 31")
    q_m3h = q_m3dia / 24.0
    area = q_m3h / v
    vol = q_m3h * trh
    return {
        "tecnologia": "UASB",
        "area_m2": round(area, 2),
        "altura_util_m": round(vol / area, 3),
        "volumen_m3": round(vol, 2),
        "trh_h": round(trh, 3),
        "velocidad_ascensional_m_h": round(v, 4),
        "eficiencia_dbo_pct": UASB_EFIC_DBO * 100,
        "eficiencia_sst_pct": UASB_EFIC_SST * 100,
        "norma_ref": f"{RES0330}, art. 189, tablas 31 y 32",
        "nota": "El efluente de un UASB suele requerir postratamiento para cumplir la Res. 0631 de 2015.",
        "_efic_dbo": UASB_EFIC_DBO, "_efic_sst": UASB_EFIC_SST,
    }


def _lodos_activados(q_m3dia: float, dbo_mg_l: float, advertencias: list) -> dict:
    s0, se = dbo_mg_l, LA_SE
    if s0 <= se:
        raise ValueError(f"Lodos activados: la DBO5 afluente ({s0:g} mg/L) no supera la de diseño del efluente ({se:g}).")
    efic_dbo = (s0 - se) / s0
    pxv = (LA_Y * (s0 - se) * q_m3dia / 1000) / (1 + LA_KD * LA_SRT_D)
    px = pxv / LA_SSV_SST
    vol = (px * LA_SRT_D * 1000) / LA_MLSS
    trh_h = vol / (q_m3dia / 24.0)
    if trh_h < 18:
        advertencias.append("Lodos activados: TRH < 18 h en aireación extendida; revisar MLSS o SRT.")
    return {
        "tecnologia": "Lodos activados — aireación extendida",
        "volumen_reactor_m3": round(vol, 2),
        "trh_h": round(trh_h, 1),
        "SRT_dias": LA_SRT_D,
        "MLSS_mg_l": LA_MLSS,
        "produccion_lodos_kg_sst_dia": round(px, 2),
        "dbo_efluente_mg_l": se,
        "eficiencia_dbo_pct": round(efic_dbo * 100, 1),
        "eficiencia_sst_pct": round(LA_EFIC_SST * 100, 1),
        "norma_ref": f"{RES0330}, art. 191",
        "_efic_dbo": efic_dbo, "_efic_sst": LA_EFIC_SST, "_Px": px,
    }


def _filtro_percolador(q_m3dia: float, carga_dbo_kg_dia: float, borde: list) -> dict:
    """Volumen mínimo con la carga orgánica máxima de tasa intermedia; profundidad y recirculación para la carga
    hidráulica de la tabla 38. q_h = Q(1+R)·D/V crece con D y R: se elige D máximo y R mínimo que la cumplan."""
    vol = carga_dbo_kg_dia / FP_CARGA_ORGANICA[1]
    d = FP_PROFUNDIDAD[1]
    qh = q_m3dia * d / vol                      # R = 0
    r = 0.0
    if qh > FP_CARGA_HIDRAULICA[1]:
        d = max(FP_PROFUNDIDAD[0], FP_CARGA_HIDRAULICA[1] * vol / q_m3dia)
        qh = q_m3dia * d / vol
        if qh > FP_CARGA_HIDRAULICA[1] + 1e-9:  # ni con la profundidad mínima: se agranda el volumen
            vol = q_m3dia * d / FP_CARGA_HIDRAULICA[1]
            qh = FP_CARGA_HIDRAULICA[1]
            borde.append("filtro percolador: el volumen lo fija la carga hidráulica máxima, no la orgánica")
    elif qh < FP_CARGA_HIDRAULICA[0]:
        r = FP_CARGA_HIDRAULICA[0] / qh - 1.0
        if r > FP_RECIRCULACION[1] + 1e-9:
            raise ValueError(f"Filtro percolador: la carga hidráulica exigiría recirculación {r:.2f} > 1 "
                             f"({RES0330}, art. 192, tabla 38, tasa intermedia).")
        qh = FP_CARGA_HIDRAULICA[0]
        borde.append("filtro percolador: carga hidráulica en el mínimo de la tabla 38")
    area = vol / d
    efic = FP_REMOCION_DBO[0]
    return {
        "tecnologia": "Filtro percolador de tasa intermedia",
        "volumen_medio_filtrante_m3": round(vol, 2),
        "profundidad_m": round(d, 3),
        "area_m2": round(area, 2),
        "relacion_recirculacion": round(r, 3),
        "carga_hidraulica_m3_m2_dia": round(qh, 3),
        "carga_organica_kg_dbo_m3_dia": round(carga_dbo_kg_dia / vol, 4),
        "eficiencia_dbo_pct": efic * 100,
        "eficiencia_sst_pct": 65.0,
        "norma_ref": f"{RES0330}, art. 192, tabla 38 (tasa intermedia)",
        "_efic_dbo": efic, "_efic_sst": 0.65, "_Px": carga_dbo_kg_dia * 0.3,
    }


def _laguna_facultativa(q_m3dia: float, dbo_mg_l: float, temperatura: float | None, profundidad: float | None,
                        advertencias: list, borde: list) -> dict:
    if temperatura is None or profundidad is None:
        raise ValueError(f"Laguna facultativa: la temperatura del agua y la profundidad son obligatorias ({RES0330}, "
                         "art. 197: profundidad 1,5 a 2,5 m). No se asume ningún valor.")
    if not (_lag.T_MIN_C <= temperatura <= _lag.T_MAX_C):
        raise ValueError(f"Temperatura {temperatura:g} °C fuera del dominio del método de Mara "
                         f"({_lag.T_MIN_C:g}–{_lag.T_MAX_C:g} °C).")
    if _lag._en_rango(profundidad, _lag.PROF_FACULTATIVA, "Profundidad de la laguna facultativa (m)", "art. 197"):
        borde.append("profundidad facultativa en el extremo del art. 197")
    lam_mara = _lag.carga_superficial_facultativa_mara(temperatura)
    lam = min(lam_mara, _lag.CARGA_SUP_FACULTATIVA[1])
    if lam_mara > lam:
        borde.append("λs de Mara limitada a 350 kg/ha·d (art. 197)")
    area = 10.0 * dbo_mg_l * q_m3dia / lam
    trh = area * profundidad / q_m3dia
    if trh < _lag.TRH_FACULTATIVA[0]:
        trh = _lag.TRH_FACULTATIVA[0]
        area = q_m3dia * trh / profundidad
        borde.append("TRH facultativo llevado al mínimo de 5 d (art. 197)")
    if trh > _lag.TRH_FACULTATIVA[1] + 1e-9:
        raise ValueError(f"Laguna facultativa: θ = {trh:.1f} d > 30 d ({RES0330}, art. 197). Reduzca la profundidad o "
                         "use el sistema lagunar con laguna anaerobia (/aquai/saneamiento/lagunas).")
    le = dbo_mg_l / (1.0 + _lag.k1_dbo_facultativa(temperatura) * trh)
    efic = 1.0 - le / dbo_mg_l
    advertencias.append(f"Laguna facultativa: {area / 10000:.2f} ha de espejo de agua; verificar distancias mínimas "
                        f"({RES0330}, art. 181). Para anaerobia + maduración use /aquai/saneamiento/lagunas.")
    return {
        "tecnologia": "Laguna facultativa de estabilización",
        "area_ha": round(area / 10000, 4),
        "area_m2": round(area, 1),
        "profundidad_m": profundidad,
        "volumen_m3": round(area * profundidad, 1),
        "trh_dias": round(trh, 2),
        "carga_superficial_kg_dbo_ha_dia": round(10.0 * dbo_mg_l * q_m3dia / area, 2),
        "eficiencia_dbo_pct": round(efic * 100, 2),
        "eficiencia_sst_pct": 60.0,
        "norma_ref": f"{RES0330}, art. 197; método de Mara (2003)",
        "_efic_dbo": efic, "_efic_sst": 0.60, "_Px": 0,
    }


def calcular_ptar_detalle(req: PTARRequest) -> tuple[PTARResponse, list[str], list[str]]:
    """Cálculo de la PTAR. Devuelve (respuesta, supuestos, bordes); el contrato lo arma `contrato_saneamiento`."""
    advertencias: list[str] = []
    borde: list[str] = []
    supuestos: list[str] = []

    q_ar_ls = req.caudal_acueducto_ls * req.factor_retorno
    q_ar_m3dia = q_ar_ls * 86400 / 1000.0
    supuestos.append("Caudal de aguas residuales = Qmd del acueducto × factor de retorno; no incluye infiltración "
                     f"(0,1 L/s·ha, {RES0330} art. 164): agregarla si aplica.")

    if req.dbo5_cruda_mg_l is not None:
        dbo_mg_l = req.dbo5_cruda_mg_l
    else:
        dbo_mg_l = DBO5_PER_CAPITA_G_HAB_DIA * req.poblacion_diseno / q_ar_m3dia
        advertencias.append("DBO₅ estimada per cápita (50 g/hab/día, valor típico de literatura). "
                            f"El {RES0330} exige caracterizar el agua residual antes del diseño final.")
        supuestos.append("DBO5 estimada con 50 g/hab·d (sin caracterización).")
    if req.sst_crudo_mg_l is not None:
        sst_mg_l = req.sst_crudo_mg_l
    else:
        sst_mg_l = SST_PER_CAPITA_G_HAB_DIA * req.poblacion_diseno / q_ar_m3dia
        supuestos.append("SST estimados con 60 g/hab·d (sin caracterización).")

    carga_dbo_kg_dia = dbo_mg_l * q_ar_m3dia / 1000.0
    carga_sst_kg_dia = sst_mg_l * q_ar_m3dia / 1000.0

    t = req.tecnologia
    if t == TecnologiaPTAR.UASB:
        dim = _uasb(q_ar_m3dia, req.temperatura_agua_c, req.factor_pico, advertencias, borde)
        supuestos.append("UASB: eficiencias 70 % DBO5 y 65 % SST (valores típicos; la tabla 29 de la Res. 0330 no "
                         "está en el corpus) y lodos 0,35 kg SST/kg DBO5 aplicada.")
    elif t == TecnologiaPTAR.LODOS_ACTIVADOS:
        dim = _lodos_activados(q_ar_m3dia, dbo_mg_l, advertencias)
        supuestos.append("Lodos activados: SRT 20 d, Y 0,5, kd 0,05 d⁻¹, MLSS 3.500 mg/L, DBO5 efluente 20 mg/L "
                         "(Metcalf & Eddy). Verificar contra la tabla 36 de la Res. 0330 (art. 191: en clima "
                         "tropical, F/M y Lv altos).")
    elif t == TecnologiaPTAR.LAGUNA_FACULTATIVA:
        dim = _laguna_facultativa(q_ar_m3dia, dbo_mg_l, req.temperatura_agua_c, req.profundidad_laguna_m,
                                  advertencias, borde)
        supuestos.append("Laguna facultativa por el método de Mara (2003), mezcla completa, sin evaporación.")
    else:
        dim = _filtro_percolador(q_ar_m3dia, carga_dbo_kg_dia, borde)
        supuestos.append("Filtro percolador de tasa intermedia: se acredita la remoción mínima de la tabla 38 "
                         "(50 %); SST 65 % y lodos 0,3 kg/kg DBO5, valores típicos.")

    efic_dbo = dim.pop("_efic_dbo")
    efic_sst = dim.pop("_efic_sst")
    if "_Px" in dim:
        px = dim.pop("_Px")
    else:
        px = carga_dbo_kg_dia * UASB_PRODUCCION_LODOS_KG_SST_KG_DBO

    dbo_efluente = dbo_mg_l * (1 - efic_dbo)
    sst_efluente = sst_mg_l * (1 - efic_sst)

    limites = vertimientos.limites_art8(carga_dbo_kg_dia, req.tipo_cuerpo_receptor.value)
    if vertimientos.en_borde_de_tramo(carga_dbo_kg_dia):
        borde.append("carga de DBO5 a menos del 5 % de un cambio de tramo de la Res. 0631 art. 8")
    supuestos.append("Tramo de la Res. 0631 art. 8 elegido con la carga de DBO5 del afluente crudo.")
    efic_req = 1.0 - limites["DBO5"] / dbo_mg_l
    if req.eficiencia_requerida_dbo_pct is not None:
        efic_req = max(efic_req, req.eficiencia_requerida_dbo_pct / 100.0)
    cumple = (dbo_efluente <= limites["DBO5"] and sst_efluente <= limites["SST"]
              and efic_dbo >= efic_req - 1e-12)
    if not cumple:
        advertencias.append(
            f"⚠ El efluente NO cumple: DBO₅ {dbo_efluente:.1f} mg/L (límite {limites['DBO5']:g}) / SST "
            f"{sst_efluente:.1f} mg/L (límite {limites['SST']:g}) / eficiencia DBO₅ {efic_dbo * 100:.1f} % "
            f"(requerida {max(efic_req, 0) * 100:.1f} %). {vertimientos.NORMA}. Considere postratamiento.")

    vol_lodos_m3_dia = px / LODOS_CONCENTRACION_KG_M3
    supuestos.append("Volumen de lodos al 1 % de sólidos (10 kg/m³).")
    destino = (
        "Secado y aprovechamiento o disposición según la normativa ambiental vigente (Res. 0330 art. 189, parágrafo)"
        if req.nivel_complejidad in ("bajo", "medio")
        else "Digestión aerobia + deshidratación mecánica (centrífuga o filtro banda)"
    )

    resp = PTARResponse(
        caudal_ar_ls=round(q_ar_ls, 3),
        caudal_ar_m3_dia=round(q_ar_m3dia, 2),
        dbo5_cruda_mg_l=round(dbo_mg_l, 1),
        sst_crudo_mg_l=round(sst_mg_l, 1),
        carga_dbo_kg_dia=round(carga_dbo_kg_dia, 2),
        carga_sst_kg_dia=round(carga_sst_kg_dia, 2),
        tecnologia=dim["tecnologia"],
        dimensionamiento=dim,
        eficiencia_dbo_pct=round(efic_dbo * 100, 1),
        eficiencia_requerida_dbo_pct=round(max(efic_req, 0.0) * 100, 1),
        dbo_efluente_mg_l=round(dbo_efluente, 1),
        sst_efluente_mg_l=round(sst_efluente, 1),
        limite_res0631_dbo=limites["DBO5"],
        limite_res0631_sst=limites["SST"],
        cumple_res0631=cumple,
        balance_lodos=BalanceLodos(
            produccion_lodos_kg_dia=round(px, 2),
            volumen_lodos_m3_dia=round(vol_lodos_m3_dia, 2),
            destino_recomendado=destino,
        ),
        normas_aplicadas=[
            f"{RES0330} — arts. 164, 181, 189, 191, 192 y 197",
            f"{vertimientos.NORMA} — límites para prestadores del servicio de alcantarillado",
            "Decreto 1076 de 2015, art. 2.2.3.3 — permisos de vertimiento",
        ],
        advertencias=advertencias,
    )
    return resp, supuestos, borde


def calcular_ptar(req: PTARRequest) -> PTARResponse:
    return calcular_ptar_detalle(req)[0]
