"""
AquaAI — Módulo hidrología: caudal de diseño
Referencia: RAS 2000 Título D / Resolución 0330-2017

Implementa:
  1. Tiempo de concentración (Tc):
       - Kirpich (1940)       : cuencas pequeñas (A < 200 ha), pendientes > 0.01
       - Témez (1978)         : cuencas medianas, ampliamente usado en Colombia
       - Bransby-Williams     : cuencas rurales planas

  2. Intensidad de diseño (I) via curvas IDF regionales Colombia
       I = a / (Tc^n + b)    [mm/h]

  3. Caudal de diseño — Método Racional:
       Q = C · I · A / 360   [m³/s]   (A en ha, I en mm/h)

Importante: el Método Racional es válido para cuencas ≤ 1000 ha (aprox.).
Para cuencas mayores usar SCS-CN o Santa Bárbara (fuera del alcance de Etapa 2).
"""

import math
from .schemas import (
    HidrologiaRequest,
    HidrologiaResponse,
    MetodoConcentracion,
)
from .ras2000_tablas import (
    CURVAS_IDF,
    PERIODOS_RETORNO_DISPONIBLES,
    NOTAS_REGIONALES,
)


# ── Tiempos de concentración ───────────────────────────────────────────────────

def _tc_kirpich(L_m: float, S_mm: float) -> float:
    """
    Kirpich (1940): Tc en minutos
        Tc = 0.0195 · (L^0.77) / (S^0.385)
    L en metros, S en m/m (pendiente media)
    Válido para cuencas rurales pequeñas.
    """
    return 0.0195 * (L_m ** 0.77) / (S_mm ** 0.385)


def _tc_temez(L_km: float, S_mm: float) -> float:
    """
    Témez (1978): Tc en horas → convertir a min
        Tc [h] = 0.3 · (L / S^0.25)^0.76
    L en km, S en m/m
    Recomendado por IGEMMET / UNGRD Colombia.
    """
    tc_h = 0.3 * ((L_km / (S_mm ** 0.25)) ** 0.76)
    return tc_h * 60.0


def _tc_bransby(A_km2: float, L_km: float, S_mm: float) -> float:
    """
    Bransby-Williams: Tc en minutos
        Tc = 14.6 · L / (A^0.1 · S^0.2)
    L en km, A en km², S en m/m
    Adecuado para cuencas rurales planas.
    """
    return 14.6 * L_km / ((A_km2 ** 0.1) * (S_mm ** 0.2))


# ── Intensidad IDF ────────────────────────────────────────────────────────────

def _intensidad_idf(region: str, TR: int, Tc_min: float) -> tuple[float, dict]:
    """
    Calcula intensidad I (mm/h) de la curva IDF regional para el TR y Tc dados.
    Interpola entre TR disponibles si TR no está exactamente en la tabla.
    """
    idf_region = CURVAS_IDF.get(region)
    if idf_region is None:
        raise ValueError(
            f"Región IDF '{region}' no reconocida. "
            f"Opciones: {list(CURVAS_IDF.keys())}"
        )

    # Seleccionar TR más cercano por arriba (conservador)
    TR_usar = next(
        (t for t in sorted(PERIODOS_RETORNO_DISPONIBLES) if t >= TR),
        max(PERIODOS_RETORNO_DISPONIBLES)
    )
    coef = idf_region[TR_usar]
    a, b, n = coef["a"], coef["b"], coef["n"]

    # Fórmula: I = a / (Tc^n + b)
    I = a / ((Tc_min ** n) + b)
    return round(I, 2), {"TR_usado": TR_usar, "a": a, "b": b, "n": n, "formula": f"I = {a} / (Tc^{n} + {b})"}


# ── Motor principal ───────────────────────────────────────────────────────────

def calcular_hidrologia(req: HidrologiaRequest) -> HidrologiaResponse:
    A_ha  = req.area_cuenca_ha
    L_m   = req.longitud_cauce_m
    S     = req.pendiente_media   # m/m
    TR    = req.periodo_retorno
    C     = req.coeficiente_escorrentia
    region = req.region_idf.lower().replace(" ", "_")

    # Advertencia cuenca grande
    advertencia_cuenca = ""
    if A_ha > 1000:
        advertencia_cuenca = (
            f"⚠ Área {A_ha} ha > 1000 ha: el Método Racional pierde precisión. "
            "Se recomienda SCS-CN o Santa Bárbara para esta escala."
        )

    # Conversiones
    L_km  = L_m / 1000.0
    A_km2 = A_ha / 100.0

    # 1. Tiempo de concentración
    metodo_tc = req.metodo_tc
    if metodo_tc == MetodoConcentracion.KIRPICH:
        Tc = _tc_kirpich(L_m, S)
        metodo_usado = "Kirpich (1940)"
    elif metodo_tc == MetodoConcentracion.TEMEZ:
        Tc = _tc_temez(L_km, S)
        metodo_usado = "Témez (1978)"
    elif metodo_tc == MetodoConcentracion.BRANSBY:
        Tc = _tc_bransby(A_km2, L_km, S)
        metodo_usado = "Bransby-Williams"
    else:
        raise ValueError(f"Método de Tc no reconocido: {metodo_tc}")

    # Tc mínimo práctico: 5 min (evitar sobreestimación de I en cuencas muy pequeñas)
    Tc = max(Tc, 5.0)

    # 2. Intensidad de diseño
    I, params_idf = _intensidad_idf(region, TR, Tc)

    # 3. Caudal de diseño — Método Racional
    # Q [m³/s] = C · I [mm/h] · A [ha] / 360
    Q_m3s = (C * I * A_ha) / 360.0
    Q_ls  = Q_m3s * 1000.0

    formula_racional = (
        f"Q = C·I·A/360 = {C}·{I}·{A_ha}/360 = {Q_m3s:.4f} m³/s = {Q_ls:.2f} L/s"
    )

    nota_region = NOTAS_REGIONALES.get(region, "")
    if advertencia_cuenca:
        nota_region = advertencia_cuenca + " | " + nota_region

    return HidrologiaResponse(
        tiempo_concentracion_min=round(Tc, 2),
        intensidad_mm_h=I,
        caudal_diseno_m3s=round(Q_m3s, 5),
        caudal_diseno_ls=round(Q_ls, 2),
        metodo_tc_usado=metodo_usado,
        parametros_idf=params_idf,
        formula_racional=formula_racional,
        notas_region=nota_region,
    )
