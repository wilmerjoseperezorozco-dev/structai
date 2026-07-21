"""
Motor de Cargas Reales – NSR-10 Títulos A y B
===============================================
Implementa el pipeline: IFC (BIM) → extracción de geometría → demanda
sísmica → combinación de cargas → Vu real.

Zona de referencia: Atlántico / Barranquilla (Colombia)
Unidades          : mm, N, MPa
Referencia técnica: NSR-10 Títulos A (Sismo) y B (Cargas)
"""

import math
import ifcopenshell
import ifcopenshell.api
import numpy as np


# ---------------------------------------------------------------------------
# 1. PARÁMETROS SÍSMICOS NSR-10 TÍTULO A – Departamento del Atlántico
#    Fuente: Mapa de amenaza sísmica NSR-10 Figura A.2.3-1
# ---------------------------------------------------------------------------
ZONA_SISMICA_ATLANTICO = {
    "Aa": 0.15,   # Aceleración pico efectiva horizontal (zona intermedia)
    "Av": 0.20,   # Velocidad pico efectiva (zona intermedia)
    "Fa": 1.20,   # Coeficiente de sitio (perfil suelo tipo D – arcillas medias litoral)
    "Fv": 1.80,   # Coeficiente de velocidad de sitio (suelo D)
    "I":  1.00,   # Coeficiente de importancia (Grupo I – residencial/comercial)
    "R":  5.00,   # Capacidad de disipación de energía (pórtico concreto ordinario)
    "Ct": 0.047,  # Coeficiente período empírico (pórticos concreto – A.4.2-1)
    "alpha": 0.9, # Exponente período empírico NSR-10 ecuación A.4.2-2
}


# ---------------------------------------------------------------------------
# 2. CARGAS DE GRAVEDAD NSR-10 TÍTULO B
# ---------------------------------------------------------------------------
CARGAS_GRAVEDAD = {
    "peso_propio_losa":    4.80,   # kN/m²  (losa maciza 20 cm, γ=24 kN/m³)
    "carga_muerta_adicional": 1.50, # kN/m²  (acabados, instalaciones)
    "carga_viva_piso":     2.00,   # kN/m²  (uso residencial – Tabla B.4.2-1)
    "tributaria_viga":     4.00,   # m²     (área tributaria de la viga al nudo)
    "numero_pisos":        3,      # pisos que convergen al nudo
}


# ---------------------------------------------------------------------------
# 3. ESPECTRO DE DISEÑO NSR-10 (A.2.6)
# ---------------------------------------------------------------------------
def calcular_espectro_nsr10(params: dict) -> dict:
    """
    Construye los parámetros del espectro de diseño NSR-10 ecuaciones A.2.6-1 a A.2.6-6.
    Retorna Sa(T) para cualquier período T.
    """
    Aa  = params["Aa"]
    Av  = params["Av"]
    Fa  = params["Fa"]
    Fv  = params["Fv"]
    I   = params["I"]

    # Aceleraciones espectrales de meseta (ecuaciones A.2.6-1 y A.2.6-2)
    SDS = 2.5 * Aa * Fa * I   # Aceleración espectral período corto
    SD1 = Av * Fv * I          # Aceleración espectral período 1 segundo

    # Períodos de transición del espectro
    T0  = 0.2 * SD1 / SDS     # Período inicio de meseta
    Ts  = SD1 / SDS            # Período fin de meseta

    return {"SDS": SDS, "SD1": SD1, "T0": T0, "Ts": Ts}


def sa_en_periodo(T: float, espectro: dict, params: dict) -> float:
    """
    Aceleración espectral de diseño Sa(T) – NSR-10 ecuación A.2.6-3.
    """
    SDS = espectro["SDS"]
    SD1 = espectro["SD1"]
    T0  = espectro["T0"]
    Ts  = espectro["Ts"]

    if T < T0:
        return SDS * (0.4 + 0.6 * T / T0)
    elif T <= Ts:
        return SDS
    else:
        return SD1 / T


# ---------------------------------------------------------------------------
# 4. PERÍODO FUNDAMENTAL DE LA ESTRUCTURA (A.4.2)
# ---------------------------------------------------------------------------
def calcular_periodo_fundamental(params: dict, altura_total_mm: float) -> float:
    """
    Período empírico NSR-10 ecuación A.4.2-2:
        Ta = Ct * hn^alpha
    hn en metros.
    """
    hn_m = altura_total_mm / 1000.0
    Ta   = params["Ct"] * (hn_m ** params["alpha"])
    return Ta


# ---------------------------------------------------------------------------
# 5. FUERZA SÍSMICA BASAL (A.4.1) y DISTRIBUCIÓN VERTICAL (A.4.3)
# ---------------------------------------------------------------------------
def calcular_cortante_basal(
    peso_total_N: float,
    Sa: float,
    R: float,
) -> float:
    """
    Fuerza cortante basal NSR-10 ecuación A.4.1-1:
        Vs = Sa / R * W
    """
    return (Sa / R) * peso_total_N


def distribuir_fuerza_sismica(
    Vs: float,
    pesos_piso: list[float],
    alturas_piso: list[float],
    T: float,
) -> list[float]:
    """
    Distribución vertical de fuerzas sísmicas NSR-10 ecuación A.4.3-1.
    k = 1 si T≤0.5s, k=2 si T≥2.5s, interpolación lineal entre medio.
    """
    if T <= 0.5:
        k = 1.0
    elif T >= 2.5:
        k = 2.0
    else:
        k = 1.0 + (T - 0.5) / 2.0

    denominador = sum(w * (h ** k) for w, h in zip(pesos_piso, alturas_piso))
    fuerzas = [
        Vs * w * (h ** k) / denominador
        for w, h in zip(pesos_piso, alturas_piso)
    ]
    return fuerzas


# ---------------------------------------------------------------------------
# 6. CORTANTE EN EL NUDO (demanda real Vu)
# ---------------------------------------------------------------------------
def calcular_demanda_cortante_nudo(
    cargas: dict,
    zona_sismica: dict,
    altura_piso_mm: float = 3000.0,
) -> dict:
    """
    Calcula la demanda de cortante real en el nudo crítico combinando:
      - Cargas de gravedad (CM + CV)
      - Demanda sísmica NSR-10

    Combinación de cargas NSR-10 C.9.2:
      Caso 1 (governa): 1.2D + 1.0E + 1.0L
      Caso 2:           1.4D
    """
    # -- Cargas de gravedad (N) --
    At    = cargas["tributaria_viga"]                           # m²
    CM    = (cargas["peso_propio_losa"] + cargas["carga_muerta_adicional"]) * At * 1000  # N/m² → N
    CV    = cargas["carga_viva_piso"] * At * 1000               # N
    n     = cargas["numero_pisos"]
    W_total = (CM + CV) * n                                     # N – peso tributario total

    # -- Período y espectro --
    h_total_mm = altura_piso_mm * n
    espectro   = calcular_espectro_nsr10(zona_sismica)
    T          = calcular_periodo_fundamental(zona_sismica, h_total_mm)
    Sa         = sa_en_periodo(T, espectro, zona_sismica)

    # -- Cortante basal sísmico --
    Vs_basal  = calcular_cortante_basal(W_total, Sa, zona_sismica["R"])

    # -- Distribución vertical (un piso por nivel) --
    alturas_m = [(i + 1) * (altura_piso_mm / 1000.0) for i in range(n)]
    pesos_m   = [W_total / n] * n
    fuerzas   = distribuir_fuerza_sismica(Vs_basal, pesos_m, alturas_m, T)

    # Cortante sísmico acumulado en el piso más bajo (nudo crítico)
    Ve = sum(fuerzas)

    # -- Combinación de carga de diseño NSR-10 C.9.2 --
    Vu_gravedad = 1.2 * CM + 1.6 * CV                          # komb. solo gravedad
    Vu_sismo    = 1.2 * CM + 1.0 * Ve + 1.0 * CV              # komb. sismo governa

    Vu_diseno   = max(Vu_gravedad, Vu_sismo)                   # demanda real [N]

    return {
        "CM_N":          CM,
        "CV_N":          CV,
        "W_total_N":     W_total,
        "T_seg":         T,
        "Sa":            Sa,
        "Vs_basal_N":    Vs_basal,
        "Ve_nudo_N":     Ve,
        "Vu_gravedad_N": Vu_gravedad,
        "Vu_sismo_N":    Vu_sismo,
        "Vu_diseno_N":   Vu_diseno,
        "espectro":      espectro,
    }


# ---------------------------------------------------------------------------
# 7. REPORTE TÉCNICO
# ---------------------------------------------------------------------------
def imprimir_reporte(resultado: dict, Vn_disponible_N: float) -> None:
    r = resultado
    print("\n" + "=" * 60)
    print("  INFRACORTEX ENGINE – REPORTE DE DEMANDA SÍSMICA")
    print("  NSR-10 Títulos A y B | Departamento del Atlántico")
    print("=" * 60)
    print(f"  Peso tributario total         W = {r['W_total_N']/1000:>8.2f} kN")
    print(f"  Período fundamental           T = {r['T_seg']:>8.4f} s")
    print(f"  Aceleración espectral        Sa = {r['Sa']:>8.4f} g")
    print(f"  SDS (meseta corto período)     = {r['espectro']['SDS']:>8.4f} g")
    print(f"  SD1 (meseta 1 segundo)         = {r['espectro']['SD1']:>8.4f} g")
    print(f"  Cortante basal sísmico     Vs = {r['Vs_basal_N']/1000:>8.2f} kN")
    print(f"  Cortante en nudo crítico   Ve = {r['Ve_nudo_N']/1000:>8.2f} kN")
    print("-" * 60)
    print(f"  Vu (1.2D + 1.6L)              = {r['Vu_gravedad_N']/1000:>8.2f} kN")
    print(f"  Vu (1.2D + 1.0E + 1.0L) ←GOB = {r['Vu_sismo_N']/1000:>8.2f} kN")
    print(f"  Vu diseño (máximo)             = {r['Vu_diseno_N']/1000:>8.2f} kN")
    print("-" * 60)
    print(f"  φVn disponible (NSR-10 C.21)   = {Vn_disponible_N/1000:>8.2f} kN")
    margen = (Vn_disponible_N - r['Vu_diseno_N']) / Vn_disponible_N * 100
    if r["Vu_diseno_N"] <= Vn_disponible_N:
        print(f"  RESULTADO → ✓ PASA  (margen = {margen:.1f}%)")
    else:
        print(f"  RESULTADO → ✗ FALLA (déficit = {-margen:.1f}%)")
    print("=" * 60)
