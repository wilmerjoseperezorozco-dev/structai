"""
AquaAI — Manning: Hidráulica de alcantarillado a gravedad
Referencia: RAS 2000 Título D / Resolución 0330/2017 Título D

Ecuación de Manning:
  Q = (1/n) · A · R^(2/3) · S^(1/2)
  V = (1/n) · R^(2/3) · S^(1/2)

Para tubo circular a sección parcial (θ en radianes):
  A  = (D²/8)(θ - sin θ)
  P  = D·θ/2
  R  = A/P
  Q/Qf y V/Vf se leen de curvas hidráulicas (tablas RAS)

Restricciones RAS D.3:
  - d/D ≤ 0.75 (tirante máximo)
  - V ≥ 0.45 m/s (autolimpieza mínima)
  - V ≤ 3.0 m/s para PVC/HDPE, ≤ 5.0 m/s para concreto
  - Diámetro mínimo colector: 200 mm
  - Diámetro mínimo ramal domiciliario: 150 mm
"""

import math
from .schemas_hidraulica_avanzada import ManningRequest, ManningResponse, MaterialTuberia

# ─── Coeficientes de Manning (n) ─────────────────────────────────────────────
MANNING_N = {
    MaterialTuberia.PVC:                0.010,
    MaterialTuberia.HDPE:               0.010,
    MaterialTuberia.GRP:                0.011,
    MaterialTuberia.GRES:               0.012,
    MaterialTuberia.CONCRETO:           0.013,
    MaterialTuberia.CONCRETO_REFORZADO: 0.013,
    MaterialTuberia.ACERO:              0.012,
}

# Velocidad máxima (m/s) para no erosionar
V_MAX = {
    MaterialTuberia.PVC:                3.0,
    MaterialTuberia.HDPE:               3.0,
    MaterialTuberia.GRP:                4.0,
    MaterialTuberia.GRES:               4.0,
    MaterialTuberia.CONCRETO:           5.0,
    MaterialTuberia.CONCRETO_REFORZADO: 6.0,
    MaterialTuberia.ACERO:              5.0,
}

V_MIN = 0.45   # m/s — autolimpieza (RAS D.3.5)

# Diámetros nominales comerciales de alcantarillado (mm)
DIAMETROS_SANEAMIENTO_MM = [
    150, 200, 250, 300, 350, 400, 450, 500, 600, 700,
    800, 900, 1000, 1100, 1200, 1400, 1600, 1800, 2000,
]

# Relación espesor pared / diámetro (factor SDR) para diámetro interno
# Aproximación: D_int ≈ D_nom * 0.955 para PVC SDR-41 en alcantarillado
FACTOR_DIAMETRO_INTERNO = {
    MaterialTuberia.PVC:                0.955,
    MaterialTuberia.HDPE:               0.940,
    MaterialTuberia.GRP:                0.960,
    MaterialTuberia.GRES:               0.960,
    MaterialTuberia.CONCRETO:           1.000,   # nominal = interno
    MaterialTuberia.CONCRETO_REFORZADO: 1.000,
    MaterialTuberia.ACERO:              0.960,
}


def _hidraulica_seccion_llena(D_int_m: float, S: float, n: float) -> tuple[float, float]:
    """Devuelve (Qf [m³/s], Vf [m/s]) para tubo circular a sección llena."""
    A  = math.pi * D_int_m**2 / 4.0
    R  = D_int_m / 4.0           # radio hidráulico a sección llena
    Vf = (1.0 / n) * R**(2/3) * S**0.5
    Qf = Vf * A
    return Qf, Vf


def _angulo_desde_relacion_q(q_qf: float) -> float:
    """
    Dado Q/Qf, calcula θ (ángulo central en radianes) por iteración.
    Relación: Q/Qf = (θ - sinθ) / (2π) · (4 / (1 - cosθ))^(2/3)
    Se resuelve por bisección.
    """
    def f(theta):
        area_ratio = (theta - math.sin(theta)) / (2 * math.pi)
        R_ratio    = ((theta - math.sin(theta)) / theta)**(2/3) if theta > 0 else 0
        return area_ratio * R_ratio - q_qf / (1.0)   # Q/Qf normalizado a Qf=1

    # Relación exacta: Q/Qf = [(θ-sinθ)^(5/3)] / [2π · θ^(2/3)]
    def q_ratio(theta):
        if theta < 1e-9:
            return 0.0
        num = (theta - math.sin(theta))**(5/3)
        den = 2 * math.pi * theta**(2/3)
        return num / den

    lo, hi = 0.001, 2 * math.pi - 0.001
    for _ in range(60):
        mid = (lo + hi) / 2
        if q_ratio(mid) < q_qf:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _relaciones_seccion_parcial(Q_m3s: float, Qf: float, Vf: float, D_int_m: float):
    """
    Dado Q/Qf, devuelve (d/D, V_real) usando la geometría de sección circular.
    """
    q_qf = Q_m3s / Qf
    if q_qf >= 1.0:
        return 1.0, Vf   # sección llena

    theta = _angulo_desde_relacion_q(q_qf)
    d_D   = (1 - math.cos(theta / 2)) / 2   # relación de tirante d/D
    # Velocidad relativa V/Vf = (R_parcial/R_lleno)^(2/3)
    R_parcial = D_int_m * (theta - math.sin(theta)) / (4 * theta) if theta > 0 else 0
    R_lleno   = D_int_m / 4.0
    v_ratio   = (R_parcial / R_lleno)**(2/3) if R_lleno > 0 else 1.0
    V_real    = Vf * v_ratio
    return d_D, V_real


def _pendiente_minima(D_int_m: float, n: float) -> float:
    """Pendiente mínima para alcanzar V=0.45 m/s a sección llena."""
    R = D_int_m / 4.0
    return (V_MIN * n / R**(2/3))**2


def calcular_manning(req: ManningRequest) -> ManningResponse:
    n_mann = MANNING_N[req.material]
    S      = req.pendiente_m_m
    Q_m3s  = req.caudal_diseno_ls / 1000.0
    advertencias: list[str] = []

    candidatos = DIAMETROS_SANEAMIENTO_MM.copy()

    # Si se especifica diámetro, usar solo ese
    if req.diametro_nominal_mm:
        candidatos = [req.diametro_nominal_mm]

    diametro_elegido  = None
    resultado_elegido = None

    for D_nom_mm in candidatos:
        # Diámetro interno
        f_int = FACTOR_DIAMETRO_INTERNO[req.material]
        D_int_mm = D_nom_mm * f_int
        D_int_m  = D_int_mm / 1000.0

        Qf, Vf = _hidraulica_seccion_llena(D_int_m, S, n_mann)
        q_qf   = Q_m3s / Qf

        if q_qf > 1.0:
            continue   # tubo insuficiente — probar el siguiente

        d_D, V_real = _relaciones_seccion_parcial(Q_m3s, Qf, Vf, D_int_m)

        if d_D > req.relacion_tirante_max:
            continue   # tirante excedido

        # Diámetro mínimo RAS D.3.3
        if D_nom_mm < 200:
            advertencias.append(
                f"Diámetro nominal {D_nom_mm} mm < 200 mm mínimo para colectores (RAS D.3.3). "
                "Usar 200 mm como mínimo."
            )

        diametro_elegido  = D_nom_mm
        resultado_elegido = (D_int_mm, Qf, Vf, q_qf, d_D, V_real)
        break

    if diametro_elegido is None:
        # Usar el mayor diámetro disponible y advertir
        D_nom_mm  = DIAMETROS_SANEAMIENTO_MM[-1]
        f_int     = FACTOR_DIAMETRO_INTERNO[req.material]
        D_int_mm  = D_nom_mm * f_int
        D_int_m   = D_int_mm / 1000.0
        Qf, Vf    = _hidraulica_seccion_llena(D_int_m, S, n_mann)
        d_D, V_real = _relaciones_seccion_parcial(min(Q_m3s, Qf * 0.99), Qf, Vf, D_int_m)
        q_qf       = Q_m3s / Qf
        diametro_elegido  = D_nom_mm
        resultado_elegido = (D_int_mm, Qf, Vf, q_qf, d_D, V_real)
        advertencias.append(
            f"El caudal de diseño supera la capacidad del diámetro máximo disponible "
            f"({D_nom_mm} mm). Considerar colector doble o canal abierto."
        )

    D_int_mm, Qf, Vf, q_qf, d_D, V_real = resultado_elegido
    D_int_m = D_int_mm / 1000.0
    v_max   = V_MAX[req.material]
    S_min   = _pendiente_minima(D_int_m, n_mann)

    cumple_v_min = V_real >= V_MIN
    cumple_v_max = V_real <= v_max
    cumple_tir   = d_D    <= req.relacion_tirante_max

    if not cumple_v_min:
        advertencias.append(
            f"⚠ Velocidad {V_real:.2f} m/s < {V_MIN} m/s mínimo de autolimpieza (RAS D.3.5). "
            f"Aumentar pendiente a S ≥ {S_min*1000:.1f}‰ o reducir diámetro."
        )
    if not cumple_v_max:
        advertencias.append(
            f"⚠ Velocidad {V_real:.2f} m/s > {v_max} m/s máximo para {req.material.value}. "
            "Reducir pendiente o aumentar diámetro."
        )
    if d_D > 0.85:
        advertencias.append(
            "Tirante d/D > 0.85: el colector estará casi lleno. Verificar con caudales punta "
            "incluyendo aguas de infiltración (RAS D.3.4)."
        )

    return ManningResponse(
        diametro_nominal_mm=diametro_elegido,
        diametro_interno_mm=round(D_int_mm, 1),
        caudal_llena_seccion_ls=round(Qf * 1000, 3),
        velocidad_llena_seccion_ms=round(Vf, 3),
        relacion_q_qf=round(q_qf, 4),
        relacion_tirante_d_D=round(d_D, 4),
        velocidad_real_ms=round(V_real, 3),
        cumple_velocidad_min=cumple_v_min,
        cumple_velocidad_max=cumple_v_max,
        cumple_tirante=cumple_tir,
        pendiente_minima_m_m=round(S_min, 6),
        coeficiente_manning_n=n_mann,
        normas_aplicadas=[
            "RAS 2000 Título D — Sistemas de recolección y evacuación de aguas residuales",
            "Resolución 0330/2017 Título D — Alcantarillado",
        ],
        advertencias=advertencias,
    )
