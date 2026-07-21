"""
Motor de Cargas — NSR-10 Títulos A y B
Zona: Departamento del Atlántico (Colombia)
Unidades: mm, N, MPa
"""
from __future__ import annotations
import math


ZONA_SISMICA_ATLANTICO: dict = {
    "Aa":    0.15,
    "Av":    0.20,
    "Fa":    1.20,
    "Fv":    1.80,
    "I":     1.00,
    "R":     5.00,
    "Ct":    0.047,
    "alpha": 0.9,
}

CARGAS_GRAVEDAD_DEFAULT: dict = {
    "peso_propio_losa":       4.80,
    "carga_muerta_adicional": 1.50,
    "carga_viva_piso":        2.00,
    "tributaria_viga":        4.00,
    "numero_pisos":           3,
}


def _espectro(p: dict) -> dict:
    SDS = 2.5 * p["Aa"] * p["Fa"] * p["I"]
    SD1 = p["Av"] * p["Fv"] * p["I"]
    T0  = 0.2 * SD1 / SDS
    Ts  = SD1 / SDS
    return {"SDS": SDS, "SD1": SD1, "T0": T0, "Ts": Ts}


def _sa(T: float, esp: dict) -> float:
    if T < esp["T0"]:
        return esp["SDS"] * (0.4 + 0.6 * T / esp["T0"])
    elif T <= esp["Ts"]:
        return esp["SDS"]
    return esp["SD1"] / T


def _periodo(p: dict, h_mm: float) -> float:
    return p["Ct"] * ((h_mm / 1000.0) ** p["alpha"])


def calcular_demanda_cortante_nudo(
    cargas: dict,
    zona: dict,
    altura_piso_mm: float = 3000.0,
) -> dict:
    """
    Calcula Vu de diseño combinando gravedad + sismo NSR-10 C.9.2.
    Retorna diccionario con todos los valores intermedios y finales.
    """
    At    = cargas["tributaria_viga"]
    CM    = (cargas["peso_propio_losa"] + cargas["carga_muerta_adicional"]) * At * 1000
    CV    = cargas["carga_viva_piso"] * At * 1000
    n     = cargas["numero_pisos"]
    W     = (CM + CV) * n

    esp   = _espectro(zona)
    T     = _periodo(zona, altura_piso_mm * n)
    Sa    = _sa(T, esp)
    Vs    = (Sa / zona["R"]) * W

    # Distribución vertical k=1 (T<0.5s — típico Atlántico)
    alturas = [(i + 1) * (altura_piso_mm / 1000.0) for i in range(n)]
    pesos   = [W / n] * n
    den     = sum(w * h for w, h in zip(pesos, alturas))
    fuerzas = [Vs * w * h / den for w, h in zip(pesos, alturas)]
    Ve      = sum(fuerzas)

    Vu_grav  = 1.2 * CM + 1.6 * CV
    Vu_sismo = 1.2 * CM + 1.0 * Ve + 1.0 * CV
    Vu       = max(Vu_grav, Vu_sismo)

    return {
        "CM_N":          CM,
        "CV_N":          CV,
        "W_total_N":     W,
        "T_seg":         T,
        "Sa":            Sa,
        "espectro":      esp,
        "Vs_basal_N":    Vs,
        "Ve_nudo_N":     Ve,
        "Vu_gravedad_N": Vu_grav,
        "Vu_sismo_N":    Vu_sismo,
        "Vu_diseno_N":   Vu,
        "combinacion_governa": "1.2D+1.0E+1.0L" if Vu_sismo > Vu_grav else "1.2D+1.6L",
    }


def chequeo_nsr10_nudo(props: dict, Vu_N: float) -> dict:
    """
    Evalúa capacidad por cortante en el nudo — NSR-10 Título C artículos
    C.11.3.1.1, C.11.4.7.2 y C.21.7.4.1.
    """
    phi  = 0.75
    fc   = props["fc"]
    Vc   = 0.17 * math.sqrt(fc) * props["b"] * props["d"]
    Vs   = props["Av"] * props["fy"] * props["d"] / props["s"]
    Vn   = 1.7 * math.sqrt(fc) * props["b"] * props["h"]
    phi_Vn = phi * min(Vc + Vs, Vn)

    margen = (phi_Vn - Vu_N) / phi_Vn * 100
    return {
        "Vc_kN":    round(Vc / 1000, 2),
        "Vs_kN":    round(Vs / 1000, 2),
        "Vn_max_kN": round(Vn / 1000, 2),
        "phi_Vn_kN": round(phi_Vn / 1000, 2),
        "Vu_diseno_kN": round(Vu_N / 1000, 2),
        "margen_pct": round(margen, 1),
        "cumple": Vu_N <= phi_Vn,
    }
