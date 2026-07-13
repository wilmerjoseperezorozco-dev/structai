"""
AquaAI — Golpe de Ariete (Transitorio Hidráulico)
Referencia: RAS 2000 Título B Sección B.7

Teoría de Joukowski:
  ΔH = a · ΔV / g        — sobrepresión por cierre instantáneo
  a  = √(K/ρ) / √(1 + K·D/(E·e))   — celeridad de onda de presión

Clasificación del cierre:
  Tc = 2L/a   — tiempo crítico de reflexión
  Si T_cierre < Tc  → cierre rápido (SEVERO) → usar ΔH = a·V0/g
  Si T_cierre ≥ Tc  → cierre lento  → ΔH = 2L·V0 / (g·T_cierre)

Presiones resultantes:
  H_max = H_estatica + ΔH   — frente de onda positivo (cierre)
  H_min = H_estatica - ΔH   — frente de onda negativo (apertura o paro)

Riesgo de cavitación si H_min < -10 m (presión absoluta nula al nivel del mar)
"""

import math
from .schemas_hidraulica_avanzada import ArieteRequest, ArieteResponse, MaterialTuberia

# ─── Módulo de elasticidad de la tubería E (Pa) ──────────────────────────────
E_TUBERIA = {
    MaterialTuberia.PVC:                2.7e9,    # 2.7 GPa
    MaterialTuberia.HDPE:               0.8e9,    # 0.8 GPa — muy flexible, ariete bajo
    MaterialTuberia.GRP:               35.0e9,
    MaterialTuberia.GRES:              70.0e9,
    MaterialTuberia.CONCRETO:          20.0e9,
    MaterialTuberia.CONCRETO_REFORZADO:25.0e9,
    MaterialTuberia.ACERO:            210.0e9,   # 210 GPa
}

# Módulo de compresibilidad del agua K (Pa) a 20°C
K_AGUA = 2.07e9   # Pa

# Densidad del agua (kg/m³)
RHO_AGUA = 1000.0

# Gravedad
G = 9.81   # m/s²

# Presión de vapor del agua a distintas temperaturas (Pa) — para NPSH / cavitación
def presion_vapor_pa(T_c: float) -> float:
    """Antoine simplificado para agua (20–40°C)."""
    return 611.0 * math.exp(17.27 * T_c / (T_c + 237.3))

def presion_atmosferica_pa(altitud_msnm: float = 0.0) -> float:
    """Presión atmosférica vs altitud (modelo ISA)."""
    return 101325 * (1 - 2.2558e-5 * altitud_msnm)**5.2559


# ─── Clases de presión NTC / ISO ─────────────────────────────────────────────
# Devuelve la clase mínima que soporta la presión máxima calculada
def _clase_presion(material: MaterialTuberia, presion_max_m: float) -> str:
    presion_bar = presion_max_m * RHO_AGUA * G / 1e5   # m.c.a. → bar

    if material in (MaterialTuberia.PVC, MaterialTuberia.HDPE):
        clases = [
            (6, "PN-6"),  (8, "PN-8"), (10, "PN-10"),
            (12, "PN-12"),(16, "PN-16"),(20, "PN-20"),
            (25, "PN-25"),
        ]
    else:
        clases = [
            (6, "K7/PN-6"), (9, "K9/PN-9"), (12, "K12/PN-12"),
        ]

    for limite, nombre in clases:
        if presion_bar <= limite:
            return nombre
    return "PN-25+ (verificar con fabricante)"


def calcular_ariete(req: ArieteRequest) -> ArieteResponse:
    advertencias: list[str] = []

    D_m  = req.diametro_interno_mm / 1000.0
    e_m  = req.espesor_pared_mm    / 1000.0
    L    = req.longitud_m
    Q_m3s = req.caudal_ls / 1000.0
    A    = math.pi * D_m**2 / 4.0
    V0   = Q_m3s / A         # velocidad inicial del flujo (m/s)
    E    = E_TUBERIA[req.material]
    T_c  = req.velocidad_cierre_s

    # ── Celeridad de onda ────────────────────────────────────────────────────
    # a = sqrt(K/ρ) / sqrt(1 + K·D/(E·e))
    # Factor de anclaje ≈ 1 (tubo libre para expandirse — caso más común)
    factor_elasticidad = 1 + (K_AGUA * D_m) / (E * e_m)
    a = math.sqrt(K_AGUA / RHO_AGUA) / math.sqrt(factor_elasticidad)

    # ── Tiempo crítico de reflexión ──────────────────────────────────────────
    Tc_reflexion = 2 * L / a

    cierre_rapido = T_c < Tc_reflexion

    # ── Sobrepresión Joukowski ────────────────────────────────────────────────
    if cierre_rapido:
        # Cierre instantáneo: ΔH = a·V0/g
        delta_H = a * V0 / G
    else:
        # Cierre lento: ΔH = 2·L·V0 / (g·T_c)
        delta_H = 2 * L * V0 / (G * T_c)

    H_max = req.presion_estatica_m + delta_H
    H_min = req.presion_estatica_m - delta_H

    riesgo_cavitacion = H_min < -10.0

    # ── Clase de presión recomendada ─────────────────────────────────────────
    clase = _clase_presion(req.material, H_max)

    # ── Medidas de mitigación ─────────────────────────────────────────────────
    medidas: list[str] = []
    if cierre_rapido:
        medidas.append(
            f"Cierre rápido detectado (T_cierre={T_c:.1f}s < Tc={Tc_reflexion:.1f}s): "
            "instalar válvula de cierre lento (T_cierre > Tc) o válvula anticipadora de onda."
        )
    if delta_H > 0.3 * req.presion_estatica_m:
        medidas.append(
            f"Sobrepresión {delta_H:.1f} m.c.a. > 30% de la presión estática. "
            "Evaluar calderín antiariete (vessel), válvula alivio de presión o by-pass."
        )
    if riesgo_cavitacion:
        medidas.append(
            f"⚠ H_min = {H_min:.1f} m.c.a.: riesgo de cavitación y colapso de la tubería. "
            "Instalar válvula admisión de aire (VAC) o aumentar presión mínima de operación."
        )
    if req.material == MaterialTuberia.HDPE:
        medidas.append(
            "HDPE: celeridad de onda baja (~200–400 m/s) — el ariete es menor que en PVC/acero. "
            "Ventaja para líneas largas."
        )

    if V0 > 2.5:
        advertencias.append(
            f"Velocidad de flujo {V0:.2f} m/s > 2.5 m/s: el golpe de ariete será elevado. "
            "Considerar reducir velocidad de operación."
        )

    return ArieteResponse(
        velocidad_flujo_ms=round(V0, 3),
        celeridad_onda_ms=round(a, 1),
        tiempo_critico_s=round(Tc_reflexion, 2),
        cierre_rapido=cierre_rapido,
        sobrepresion_maxima_m=round(delta_H, 2),
        presion_maxima_total_m=round(H_max, 2),
        presion_minima_m=round(H_min, 2),
        riesgo_cavitacion=riesgo_cavitacion,
        clase_presion_recomendada=clase,
        medidas_mitigacion=medidas,
        normas_aplicadas=[
            "RAS 2000 Título B Sección B.7 — Transitorios hidráulicos",
            "Joukowski (1898) — Teoría del golpe de ariete",
            "NTC 1360 / ISO 1452 — Clases de presión tuberías PVC",
            "NTC 4285 / ISO 4427 — Clases de presión tuberías HDPE",
        ],
    )
