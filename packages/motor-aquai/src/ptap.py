"""
AquaAI — Módulo PTAP: Planta de Tratamiento de Agua Potable
Referencia: Resolución 0330 de 2017 — art. 111 coagulación, 112 floculación, 113 sedimentación, 114 filtración,
121 desinfección (#236: artículos corregidos; antes citaba 125-145, que tratan de lodos y arranque).
Las tablas 7 a 13 de la Res. 0330 no están en el corpus: los parámetros de diseño de este módulo son valores de
literatura declarados en `supuestos` del contrato y deben contrastarse con esas tablas.

Unidades de tratamiento implementadas:
  1. Coagulación    — dosificación de coagulante según turbidez y color
  2. Floculación    — gradiente G, tiempo de retención, volumen de cámara
  3. Sedimentación  — tasa superficial, área y volumen del sedimentador
  4. Filtración     — tasa, área de filtros, número de unidades
  5. Desinfección   — concentración-tiempo CT, dosis de cloro, cloro residual

El objetivo del sistema es producir agua que cumpla la Resolución 2115/2007:
  - Turbidez efluente ≤ 2 NTU (ideal ≤ 1 NTU)
  - Color aparente ≤ 15 UC
  - Cloro residual libre 0,3 – 2,0 mg/L (art. 9)
  - pH 6.5 – 9.0
"""

import math
import sys
from pathlib import Path

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import exigir  # noqa: E402

from .schemas_saneamiento import (
    PTAPRequest, PTAPResponse, UnidadPTAP, CoagulanteType,
)

# ─── Tablas de diseño (Res 0330/2017 Título C + bibliografía RAS) ─────────────

# Dosis orientativa de coagulante según turbidez (mg/L)
# Estructura: [(turbidez_max, dosis_min, dosis_max, dosis_tipica)]
DOSIS_ALUMBRE = [
    (10,   5,  20, 10),
    (50,  20,  40, 28),
    (100, 35,  60, 45),
    (300, 50,  90, 65),
    (500, 80, 130, 100),
    (float('inf'), 100, 200, 140),
]

# Factor coagulante alternativo respecto al alumbre
FACTOR_COAGULANTE = {
    "alumbre":         1.00,
    "pac":             0.55,   # PAC ~45% más eficiente que alumbre
    "sulfato_ferrico": 0.70,
    "cloruro_ferrico": 0.65,
}

# Parámetros floculación (Res 0330/2017 art. 112; tabla no disponible en el corpus)
G_FLOCULACION      = 40.0   # s⁻¹ — gradiente de velocidad recomendado
T_FLOCULACION_MIN  = 20.0   # minutos
T_FLOCULACION_MAX  = 30.0   # minutos
T_FLOCULACION      = 25.0   # minutos — valor de diseño

# Parámetros sedimentación (Res 0330/2017 art. 113, tablas 8 y 9; no disponibles en el corpus)
TASA_SUPERFICIAL_CONV  = 20.0   # m³/m²/día — sedimentador convencional
TASA_SUPERFICIAL_LAMI  = 60.0   # m³/m²/día — sedimentador laminar (placas/tubos)
T_RETENCION_SEDIM_H    = 3.0    # horas

# Parámetros filtración rápida (Res 0330/2017 art. 114, tabla 10; no disponible en el corpus)
TASA_FILTRACION        = 150.0  # m³/m²/día — tasa media
TASA_FILTRACION_MAX    = 180.0
N_FILTROS_MIN          = 4      # Res 0330 art. 114 parágrafo: 4 con lavado mutuo (3 con tanque de lavado)

# Desinfección con cloro (Res 0330/2017 art. 121 + Res 2115/2007)
CLORO_RESIDUAL_MIN     = 0.3    # mg/L — Res 2115/2007 art. 9 (cloro residual libre)
CLORO_RESIDUAL_MAX     = 2.0    # mg/L — Res 2115/2007 art. 9
CT_GIARDIA_3LOG        = 165.0  # mg·min/L — inactivación 3-log Giardia a pH7, T=15°C (EPA)
T_CONTACTO_MIN         = 20.0   # minutos — Res 0330 art. 121, parágrafo 2


def _dosis_coagulante(turbidez: float, coagulante: CoagulanteType) -> tuple[float, float, float]:
    """Devuelve (dosis_min, dosis_max, dosis_tipica) en mg/L para el coagulante dado."""
    f = exigir(coagulante.value, FACTOR_COAGULANTE, "Res 0330/2017 art. 111", "Coagulante")
    for t_max, d_min, d_max, d_tip in DOSIS_ALUMBRE:
        if turbidez <= t_max:
            return d_min * f, d_max * f, d_tip * f
    raise AssertionError("tabla de dosis sin tramo final")  # inalcanzable: el último tramo es infinito


def calcular_ptap_detalle(req: PTAPRequest) -> tuple[PTAPResponse, list[str], list[str]]:
    Q_ls    = req.caudal_diseno_ls
    Q_m3s   = Q_ls / 1000.0
    Q_m3h   = Q_m3s * 3600.0
    Q_m3dia = Q_m3s * 86400.0
    advertencias: list[str] = []
    unidades: list[UnidadPTAP] = []
    borde: list[str] = []

    # ── 1. COAGULACIÓN ────────────────────────────────────────────────────────
    d_min, d_max, dosis = _dosis_coagulante(req.turbidez_cruda_ntu, req.coagulante)
    consumo_kg_dia = dosis * Q_m3dia / 1000.0   # mg/L × m³/día ÷ 1000 = kg/día

    if req.color_crudo_uc > 50 and req.coagulante == CoagulanteType.ALUMBRE:
        advertencias.append(
            f"Color crudo {req.color_crudo_uc} UC > 50 UC: considerar sulfato férrico o PAC "
            "para mejor remoción de color (Res 0330/2017 art. 111)."
        )
    if req.ph_crudo < 6.0 or req.ph_crudo > 8.0:
        advertencias.append(
            f"pH crudo {req.ph_crudo} fuera del rango óptimo de coagulación (6.0–8.0). "
            "Puede requerirse ajuste de pH previo con cal o CO₂."
        )

    unidades.append(UnidadPTAP(
        nombre="Dosificación de coagulante",
        dimensiones={"dosis_tipica_mg_l": round(dosis, 1),
                     "rango_mg_l": f"{round(d_min,1)}–{round(d_max,1)}"},
        parametros_diseno={
            "coagulante": req.coagulante.value,
            "consumo_kg_dia": round(consumo_kg_dia, 2),
            "consumo_kg_mes": round(consumo_kg_dia * 30, 1),
            "punto_aplicacion": "Canal de mezcla rápida antes del floculador",
        },
        norma_ref="Res 0330/2017 art. 111 (dosis óptima por ensayo de jarras, parágrafos 2 y 3)",
    ))

    # ── 2. FLOCULACIÓN ───────────────────────────────────────────────────────
    t_floc_s  = T_FLOCULACION * 60          # segundos
    vol_floc  = Q_m3s * t_floc_s            # m³
    # Número de cámaras: 3 (valor de diseño declarado en supuestos)
    n_camaras = 3
    vol_camara = vol_floc / n_camaras

    unidades.append(UnidadPTAP(
        nombre="Floculador hidráulico de flujo horizontal",
        dimensiones={"volumen_total_m3": round(vol_floc, 2),
                     "n_camaras": n_camaras,
                     "vol_camara_m3": round(vol_camara, 2)},
        parametros_diseno={
            "tiempo_retencion_min": T_FLOCULACION,
            "gradiente_G_s": G_FLOCULACION,
            "Camp_number_GT": round(G_FLOCULACION * t_floc_s),
        },
        norma_ref="Res 0330/2017 art. 112",
    ))

    # ── 3. SEDIMENTACIÓN ─────────────────────────────────────────────────────
    # Usar sedimentación laminar si turbidez alta o espacio limitado
    usar_laminar = req.turbidez_cruda_ntu > 200
    tasa = TASA_SUPERFICIAL_LAMI if usar_laminar else TASA_SUPERFICIAL_CONV
    area_sedim = Q_m3dia / tasa
    vol_sedim  = Q_m3h * T_RETENCION_SEDIM_H
    # Relación largo:ancho = 4:1 (recomendada RAS)
    ancho = math.sqrt(area_sedim / 4)
    largo = 4 * ancho
    profundidad = vol_sedim / area_sedim

    unidades.append(UnidadPTAP(
        nombre=f"Sedimentador {'laminar (placas inclinadas)' if usar_laminar else 'convencional'}",
        dimensiones={
            "area_m2":        round(area_sedim, 2),
            "largo_m":        round(largo, 2),
            "ancho_m":        round(ancho, 2),
            "profundidad_m":  round(profundidad, 2),
            "volumen_m3":     round(vol_sedim, 2),
        },
        parametros_diseno={
            "tasa_superficial_m3_m2_dia": tasa,
            "tiempo_retencion_h":         T_RETENCION_SEDIM_H,
            "tipo":                       "laminar" if usar_laminar else "convencional",
        },
        norma_ref="Res 0330/2017 art. 113, tablas 8 y 9",
    ))

    # ── 4. FILTRACIÓN RÁPIDA ─────────────────────────────────────────────────
    area_filtracion = Q_m3dia / TASA_FILTRACION
    n_filtros = max(N_FILTROS_MIN, math.ceil(area_filtracion / 50))  # máx 50 m² por filtro
    area_filtro = area_filtracion / n_filtros
    lado_filtro = math.sqrt(area_filtro)

    if area_filtro > 50:
        advertencias.append(
            f"Área por filtro {area_filtro:.1f} m² > 50 m²: aumentar número de unidades "
            "(Res 0330/2017 art. 114)."
        )

    unidades.append(UnidadPTAP(
        nombre="Filtros rápidos de arena (doble capa arena-antracita)",
        dimensiones={
            "n_filtros":        n_filtros,
            "area_total_m2":    round(area_filtracion, 2),
            "area_filtro_m2":   round(area_filtro, 2),
            "lado_filtro_m":    round(lado_filtro, 2),
        },
        parametros_diseno={
            "tasa_filtracion_m3_m2_dia": TASA_FILTRACION,
            "profundidad_lecho_arena_m":  0.60,
            "profundidad_antracita_m":    0.30,
            "ciclo_lavado_h":            24,
            "duracion_lavado_min":        15,
        },
        norma_ref="Res 0330/2017 art. 114 — mínimo 4 unidades con lavado mutuo (parágrafo)",
    ))

    # ── 5. DESINFECCIÓN CON CLORO ────────────────────────────────────────────
    # Concentración de trabajo en el tanque de contacto
    c_cloro = CLORO_RESIDUAL_MIN + (CLORO_RESIDUAL_MAX - CLORO_RESIDUAL_MIN) / 2   # 1,15 mg/L, centro del rango
    t_contacto = max(CT_GIARDIA_3LOG / c_cloro, T_CONTACTO_MIN)   # minutos (art. 121: ≥ 20 min)
    if t_contacto == T_CONTACTO_MIN:
        borde.append("tiempo de contacto en el mínimo de 20 min del art. 121")
    vol_tanque_contacto = Q_m3s * (t_contacto * 60)  # m³

    # Demanda de cloro estimada: 1–3 mg/L según calidad (turbidez + materia orgánica)
    demanda_cloro = 1.5 if req.turbidez_cruda_ntu <= 50 else 2.5
    dosis_cloro = demanda_cloro + c_cloro

    unidades.append(UnidadPTAP(
        nombre="Sistema de desinfección con cloro gas / hipoclorito",
        dimensiones={
            "vol_tanque_contacto_m3": round(vol_tanque_contacto, 2),
            "t_contacto_min":         round(t_contacto, 1),
        },
        parametros_diseno={
            "CT_requerido_mg_min_l":  CT_GIARDIA_3LOG,
            "dosis_cloro_mg_l":       round(dosis_cloro, 2),
            "cloro_residual_red_mg_l":f"{CLORO_RESIDUAL_MIN}–{CLORO_RESIDUAL_MAX}",
            "consumo_cloro_kg_dia":   round(dosis_cloro * Q_m3dia / 1000, 2),
            "pH_optimo_desinfeccion": "6.5–7.5 (HOCl dominante)",
        },
        norma_ref=(
            "Res 0330/2017 art. 121 (CT = K, tabla 13; contacto ≥ 20 min) + Res 2115/2007 — "
            "cloro residual libre 0,3–2,0 mg/L (Res 2115 art. 9)"
        ),
    ))

    if req.temperatura_c < 10:
        borde.append("temperatura < 10 °C: el CT de 165 mg·min/L deja de ser conservador")
        advertencias.append(
            f"Temperatura {req.temperatura_c}°C: el CT requerido para inactivación de Giardia "
            "aumenta significativamente por debajo de 10°C. Verificar tablas CT de la EPA para T baja."
        )

    return PTAPResponse(
        caudal_diseno_ls=Q_ls,
        dosis_coagulante_mg_l=round(dosis, 1),
        consumo_coagulante_kg_dia=round(consumo_kg_dia, 2),
        unidades=unidades,
        cloro_residual_min_mg_l=CLORO_RESIDUAL_MIN,
        cloro_residual_max_mg_l=CLORO_RESIDUAL_MAX,
        ct_requerido_mg_min_l=CT_GIARDIA_3LOG,
        dosis_cloro_mg_l=round(dosis_cloro, 2),
        cumple_res2115=None,  # un diseño no demuestra calidad del agua: se verifica con muestreo
        normas_aplicadas=[
            "Resolución 0330 de 2017 — arts. 111 a 114 y 121",
            "Resolución 2115 de 2007 — Parámetros calidad agua potable",
            "Decreto 1575 de 2007 — Sistema protección y control calidad del agua",
        ],
        advertencias=advertencias,
    ), [
        "Dosis de coagulante orientativa por tramos de turbidez (literatura); la dosis óptima se fija por ensayo de "
        "jarras (Res 0330 art. 111, parágrafos 2 y 3).",
        f"Floculación: G = {G_FLOCULACION:g} s⁻¹, {T_FLOCULACION:g} min, 3 cámaras (literatura; tabla del art. 112 no "
        "disponible en el corpus).",
        f"Sedimentación: {TASA_SUPERFICIAL_CONV:g} m³/m²·d convencional, {TASA_SUPERFICIAL_LAMI:g} m³/m²·d laminar, "
        f"{T_RETENCION_SEDIM_H:g} h (literatura; tablas 8 y 9 no disponibles). Laminar si turbidez > 200 NTU.",
        f"Filtración rápida a {TASA_FILTRACION:g} m³/m²·d, ≤ 50 m² por filtro y ≥ {N_FILTROS_MIN} unidades (lavado mutuo).",
        f"CT = {CT_GIARDIA_3LOG:g} mg·min/L (EPA, 3-log Giardia, pH 7, 15 °C) con cloro de trabajo en el centro del rango "
        "de la Res 2115 (1,15 mg/L); la "
        "Res 0330 art. 121 exige K de su tabla 13 según T y pH, que no está en el corpus.",
        "Demanda de cloro 1,5 mg/L (turbidez ≤ 50 NTU) o 2,5 mg/L (mayor), estimación sin ensayo.",
    ], borde


def calcular_ptap(req: PTAPRequest) -> PTAPResponse:
    return calcular_ptap_detalle(req)[0]
