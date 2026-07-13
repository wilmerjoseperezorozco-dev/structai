"""
AquaAI — Estación de Bombeo
Referencia: RAS 2000 Título B Sección B.8

Curva del sistema:
  H_sistema = Hg + hf_succion + hf_descarga + hf_menores

Pérdidas por fricción — Hazen-Williams (líneas a presión):
  hf = 10.67 · L · Q^1.852 / (C^1.852 · D^4.87)

Pérdidas menores (codos, válvulas):
  hf_menor = K · V² / (2g)   con K estimado por accesorios

TDH (Total Dynamic Head):
  TDH = H_sistema

Potencia:
  P_hidráulica = ρ·g·Q·TDH           (W)
  P_freno      = P_hid / η_bomba      (W)
  P_instalada  = P_freno / η_motor    (W)

NPSH disponible:
  NPSHd = (P_atm - P_vapor) / (ρ·g) + Z_succion - hf_succion

  Si Z_succion < 0 (bomba sobre el nivel del agua): NPSHd disminuye.
  Regla práctica: NPSHd ≥ NPSHr + 0.5 m de margen (Hydraulic Institute).
"""

import math
from .schemas_hidraulica_avanzada import (
    BombeoRequest, BombeoResponse, MaterialTuberia, TipoFluidoBombeo
)
from .ariete import presion_vapor_pa, presion_atmosferica_pa

G   = 9.81
RHO = 1000.0

# Coeficientes Hazen-Williams por material
C_HW = {
    MaterialTuberia.PVC:                150,
    MaterialTuberia.HDPE:               150,
    MaterialTuberia.GRP:                140,
    MaterialTuberia.GRES:               110,
    MaterialTuberia.CONCRETO:           100,
    MaterialTuberia.CONCRETO_REFORZADO: 100,
    MaterialTuberia.ACERO:              120,
}

# Coeficientes de pérdidas menores estimadas
K_CODO_90    = 0.9
K_VALVULA_CH = 2.5   # válvula de cheque (retención)
K_VALVULA_CO = 0.3   # válvula de compuerta abierta
K_ENTRADA    = 0.5
K_SALIDA     = 1.0


def _hf_hw(Q_m3s: float, L: float, D_mm: float, C: int) -> float:
    """Pérdida de carga Hazen-Williams (m)."""
    D_m = D_mm / 1000.0
    if D_m <= 0 or Q_m3s <= 0:
        return 0.0
    return 10.67 * L * Q_m3s**1.852 / (C**1.852 * D_m**4.87)


def _hf_menores(Q_m3s: float, D_mm: float,
                n_codos: int, n_valvulas: int) -> float:
    """Pérdidas menores acumuladas (m)."""
    D_m = D_mm / 1000.0
    A   = math.pi * D_m**2 / 4.0
    V   = Q_m3s / A if A > 0 else 0
    K_total = (
        n_codos    * K_CODO_90
      + n_valvulas * (K_VALVULA_CH + K_VALVULA_CO)
      + K_ENTRADA
      + K_SALIDA
    )
    return K_total * V**2 / (2 * G)


def calcular_bombeo(req: BombeoRequest) -> BombeoResponse:
    advertencias: list[str] = []

    # Bombas en operación + 1 de reserva (RAS B.8.4: siempre reserva)
    n_op  = req.n_bombas_paralelo
    n_res = 1
    Q_total_m3s = req.caudal_diseno_ls / 1000.0
    Q_bomba     = Q_total_m3s / n_op     # caudal por bomba

    C_suc = C_HW[req.material_succion]
    C_des = C_HW[req.material_descarga]

    # ── Pérdidas de fricción ────────────────────────────────────────────────
    hf_suc = _hf_hw(Q_bomba, req.longitud_succion_m,
                    req.diametro_succion_mm, C_suc)
    hf_des = _hf_hw(Q_bomba, req.longitud_descarga_m,
                    req.diametro_descarga_mm, C_des)

    # ── Pérdidas menores (solo en descarga — la succión se computa en NPSH)
    hf_men = _hf_menores(Q_bomba, req.diametro_descarga_mm,
                         req.n_accesorios_codos, req.n_accesorios_valvulas)

    hf_total = hf_suc + hf_des + hf_men
    TDH      = req.altura_geometrica_m + hf_total

    # ── Potencias ────────────────────────────────────────────────────────────
    eta_b = req.eficiencia_bomba_pct / 100.0
    eta_m = req.eficiencia_motor_pct / 100.0

    # Fluidos residuales tienen menor eficiencia efectiva
    if req.tipo_fluido == TipoFluidoBombeo.AGUA_RESIDUAL:
        eta_b *= 0.92
        advertencias.append(
            "Agua residual: eficiencia bomba reducida 8% para considerar desgaste y sólidos. "
            "Especificar bomba de aguas residuales con paso de sólidos ≥ 50 mm (RAS B.8.3)."
        )

    P_hid       = RHO * G * Q_bomba * TDH       # W
    P_freno     = P_hid / eta_b                  # W
    P_instalada = P_freno / eta_m                # W — potencia del motor

    # Agregar 15% de margen de seguridad en el motor (norma práctica)
    P_instalada_final = P_instalada * 1.15

    horas_dia = 20.0   # bombeo típico 20 h/día en Colombia
    kwh_mes   = (P_instalada_final / 1000.0) * horas_dia * 30 * n_op

    # ── NPSH disponible ───────────────────────────────────────────────────────
    T_agua    = 20.0   # temperatura nominal
    P_atm     = presion_atmosferica_pa(req.altitud_msnm)
    P_vap     = presion_vapor_pa(T_agua)

    # Altura de aspiración: convención positiva si bomba SOBRE el agua
    # Para NPSHd: Z_s positiva = bomba sobre agua (reduce NPSHd)
    # Asumimos que la altura geométrica de succión = longitud_succion * sin(ángulo)
    # Aproximación conservadora: Z_s = longitud_succion * 0.3 (ángulo 17°)
    Z_succion  = req.longitud_succion_m * 0.3   # m — estimado

    NPSHd = (P_atm - P_vap) / (RHO * G) - Z_succion - hf_suc

    # NPSHr típico para bombas centrífugas domésticas: 2–4 m
    # NPSHr de diseño conservador: TDH/10 (aproximación Hydraulic Institute)
    NPSHr_min = max(2.0, TDH / 10.0)
    alerta_cav = NPSHd < (NPSHr_min + 0.5)

    if alerta_cav:
        advertencias.append(
            f"⚠ NPSHd={NPSHd:.2f} m < NPSHr_mín+0.5={NPSHr_min+0.5:.2f} m: "
            "riesgo de cavitación. Reducir la altura de aspiración, usar bomba sumergible "
            "o aumentar la presión en la entrada (RAS B.8.6)."
        )

    if req.altitud_msnm > 2000:
        advertencias.append(
            f"Altitud {req.altitud_msnm:.0f} msnm: P_atm reducida a "
            f"{P_atm/1e5:.3f} bar. El NPSHd disminuye significativamente "
            "respecto al nivel del mar — crítico en municipios andinos."
        )

    if TDH > 100:
        advertencias.append(
            f"TDH={TDH:.1f} m > 100 m: evaluar bomba multietapa o partición de la línea "
            "en tramos con estaciones intermedias (RAS B.8.2)."
        )

    # ── Configuración recomendada ─────────────────────────────────────────────
    config = (
        f"{n_op} bomba(s) en operación + {n_res} bomba(s) de reserva "
        f"(RAS B.8.4: mínimo 100% de reserva instalada)"
    )

    return BombeoResponse(
        caudal_por_bomba_ls=round(Q_bomba * 1000, 3),
        perdidas_friccion_succion_m=round(hf_suc, 3),
        perdidas_friccion_descarga_m=round(hf_des, 3),
        perdidas_menores_m=round(hf_men, 3),
        perdidas_totales_m=round(hf_total, 3),
        tdh_m=round(TDH, 2),
        potencia_hidraulica_kw=round(P_hid / 1000, 3),
        potencia_al_freno_kw=round(P_freno / 1000, 3),
        potencia_instalada_kw=round(P_instalada_final / 1000, 2),
        consumo_kwh_mes=round(kwh_mes, 1),
        npsh_disponible_m=round(NPSHd, 2),
        npsh_recomendado_min_m=round(NPSHr_min, 2),
        alerta_cavitacion=alerta_cav,
        n_bombas_operacion=n_op,
        n_bombas_reserva=n_res,
        configuracion=config,
        normas_aplicadas=[
            "RAS 2000 Título B Sección B.8 — Estaciones de bombeo",
            "RAS 2000 Título B Sección B.7 — Líneas de impulsión",
            "Hydraulic Institute Standards — NPSHd / NPSHr",
            "NTC-IEC 60034 — Motores eléctricos",
        ],
        advertencias=advertencias,
    )
