"""
AquaAI — Módulo hidráulica de tuberías
Referencia: RAS 2000 Título B, Sección B.6 / Resolución 0330-2017

Fórmula de Hazen-Williams:
    V  = 0.8492 · C · R^0.63 · S^0.54          (m/s)
    Q  = V · A                                    (m³/s)
    hf = 10.67 · L · Q^1.852 / (C^1.852 · D^4.87)  (m)

Donde:
    C  = coeficiente de rugosidad (adimensional)
    R  = radio hidráulico ≈ D/4 para tubería llena (m)
    S  = pendiente hidráulica (m/m)
    D  = diámetro interior (m)
    L  = longitud del tramo (m)

El motor calcula el diámetro mínimo que cumpla:
    - Velocidad mínima (0.45 m/s) — evitar sedimentación
    - Velocidad máxima (5.0 m/s)  — evitar erosión
    - Presión mínima en el punto de entrega
"""

import math
from .schemas import HazenWilliamsRequest, HazenWilliamsResponse
from .ras2000_tablas import (
    COEF_HAZEN_WILLIAMS,
    DIAMETROS_NOMINALES_MM,
    VELOCIDAD_MIN_MS,
    VELOCIDAD_MAX_MS,
)


def _hazen_perdida_total(Q_m3s: float, C: int, D_m: float, L_m: float) -> float:
    """Pérdida de carga total por Hazen-Williams (m)."""
    return 10.67 * L_m * (Q_m3s ** 1.852) / ((C ** 1.852) * (D_m ** 4.87))


def _velocidad(Q_m3s: float, D_m: float) -> float:
    """Velocidad media en sección circular llena (m/s)."""
    A = math.pi * (D_m / 2) ** 2
    return Q_m3s / A


def calcular_hazen_williams(req: HazenWilliamsRequest) -> HazenWilliamsResponse:
    material = req.material.upper()
    C = COEF_HAZEN_WILLIAMS.get(material, 130)
    Q_ls  = req.caudal_ls
    Q_m3s = Q_ls / 1000.0
    L     = req.longitud_m
    advertencias: list[str] = []

    if material not in COEF_HAZEN_WILLIAMS:
        advertencias.append(
            f"Material '{req.material}' no reconocido — se usó C=130 (acero moderado). "
            "Especifique: PVC, HDPE, ACERO, AC, CONCRETO, HIERRO o GRP."
        )

    # ── Si se especifica diámetro, solo verificar ──────────────────────────
    if req.diametro_mm is not None:
        D_calc_mm = req.diametro_mm
        # Seleccionar el nominal inmediato superior
        D_nom_mm = next(
            (d for d in DIAMETROS_NOMINALES_MM if d >= D_calc_mm),
            DIAMETROS_NOMINALES_MM[-1]
        )
        D_m = D_nom_mm / 1000.0
        V   = _velocidad(Q_m3s, D_m)
        hf  = _hazen_perdida_total(Q_m3s, C, D_m, L)

    # ── Calcular diámetro mínimo que cumpla velocidad ─────────────────────
    else:
        D_nom_mm = None
        D_m      = None
        V        = None
        hf       = None

        for D_try_mm in DIAMETROS_NOMINALES_MM:
            D_try_m  = D_try_mm / 1000.0
            V_try    = _velocidad(Q_m3s, D_try_m)
            hf_try   = _hazen_perdida_total(Q_m3s, C, D_try_m, L)
            P_salida = req.cota_inicio_m - hf_try

            if (VELOCIDAD_MIN_MS <= V_try <= VELOCIDAD_MAX_MS
                    and P_salida >= req.presion_minima_mca):
                D_nom_mm = D_try_mm
                D_m      = D_try_m
                V        = V_try
                hf       = hf_try
                break

        if D_nom_mm is None:
            # Usar el mayor disponible y avisar
            D_nom_mm = DIAMETROS_NOMINALES_MM[-1]
            D_m      = D_nom_mm / 1000.0
            V        = _velocidad(Q_m3s, D_m)
            hf       = _hazen_perdida_total(Q_m3s, C, D_m, L)
            advertencias.append(
                "⚠ Ningún diámetro de la lista comercial cumple todas las restricciones. "
                "Se usa el mayor disponible. Considere reducir la longitud del tramo, "
                "aumentar la presión aguas arriba, o revisar el caudal de diseño."
            )

        D_calc_mm = D_nom_mm

    # ── Verificaciones finales ─────────────────────────────────────────────
    hf_total  = _hazen_perdida_total(Q_m3s, C, D_m, L)
    V_final   = _velocidad(Q_m3s, D_m)
    P_salida  = req.cota_inicio_m - hf_total

    cumple_v = VELOCIDAD_MIN_MS <= V_final <= VELOCIDAD_MAX_MS
    cumple_p = req.presion_minima_mca <= P_salida <= req.presion_maxima_mca

    if not cumple_v:
        advertencias.append(
            f"Velocidad {V_final:.2f} m/s fuera del rango RAS [{VELOCIDAD_MIN_MS}–{VELOCIDAD_MAX_MS}] m/s."
        )
    if P_salida < req.presion_minima_mca:
        advertencias.append(
            f"Presión de salida {P_salida:.2f} m.c.a. < mínimo RAS ({req.presion_minima_mca} m.c.a.). "
            "Considere estación de bombeo o rediseño de trazado."
        )
    if P_salida > req.presion_maxima_mca:
        advertencias.append(
            f"Presión de salida {P_salida:.2f} m.c.a. > máximo RAS ({req.presion_maxima_mca} m.c.a.). "
            "Instale válvula reductora de presión (VRP)."
        )

    perdida_unitaria_mm = (hf_total / L) * 1000  # mm/m

    return HazenWilliamsResponse(
        diametro_calculado_mm=round(D_calc_mm, 1),
        diametro_nominal_mm=D_nom_mm,
        velocidad_ms=round(V_final, 3),
        perdida_unitaria_mm=round(perdida_unitaria_mm, 2),
        perdida_total_mca=round(hf_total, 3),
        presion_salida_mca=round(P_salida, 3),
        coeficiente_C=C,
        cumple_velocidad=cumple_v,
        cumple_presion=cumple_p,
        advertencias=advertencias,
        norma_ref=(
            "RAS 2000 / Res. 0330-2017 Sección B.6 — "
            "Hazen-Williams; velocidades B.6.3; presiones B.6.4"
        ),
    )
