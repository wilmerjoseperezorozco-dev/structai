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
    """Espectro elastico de aceleraciones NSR-10 A.2.6 (formulas
    verbatim, ver NSR10-A2-A_2_6_r1/r2/r3 en nsr10_chunks). Corregido
    2026-09-30: la version anterior usaba la convencion ASCE7/IBC
    (SDS/SD1/T0=0.2*SD1/SDS/Ts=SD1/SDS) en vez de las ecuaciones
    oficiales colombianas -- daba un periodo de transicion
    Ts=0.40*Av*Fv/(Aa*Fa), distinto del TC=0.48*Av*Fv/(Aa*Fa) real
    (ecuacion A.2.6-2), y omitia el factor 1.2 de la ecuacion A.2.6-1
    (Sa=1.2*Av*Fv*I/T), subestimando Sa hasta ~17% para periodos largos
    -- un error del lado inseguro (no conservador) para edificios de
    periodo medio/alto, justo donde mas importa. Los nombres de campo
    (SDS/SD1/T0/Ts) se mantienen por compatibilidad con EspectroDiseno
    (schema real de /estructural/analizar-nudo), pero SD1 y Ts ahora
    contienen los valores NSR-10 correctos (1.2*Av*Fv*I y TC), no los
    de la convencion estadounidense.

    La rama T<T0 (ecuaciones A.2.6-6/7) es exclusiva de modos SUPERIORES
    en analisis dinamico segun el propio texto verificado de la norma
    (NSR10-A2-A_2_6_r3: "solo para modos diferentes al fundamental") --
    no se usa en _sa(), donde T es el periodo FUNDAMENTAL para fuerza
    estatica equivalente. T0 se calcula con su formula real (A.2.6-6)
    solo por completitud del schema, no se aplica como rama en _sa().
    TL (A.2.6-4) es la rama de periodo largo, ausente antes -- ahora
    implementada (ecuacion A.2.6-5)."""
    Aa, Av, Fa, Fv, I = p["Aa"], p["Av"], p["Fa"], p["Fv"], p["I"]
    SDS = 2.5 * Aa * Fa * I
    SD1 = 1.2 * Av * Fv * I
    T0  = 0.1 * Aa * Fa / (Av * Fv)   # A.2.6-6 -- informativo, no usado en _sa()
    Ts  = 0.48 * Av * Fv / (Aa * Fa)  # TC real, A.2.6-2
    TL  = 2.4 * Fv                    # A.2.6-4
    return {"SDS": SDS, "SD1": SD1, "T0": T0, "Ts": Ts, "TL": TL}


def _eta_amortiguamiento(xi_pct: float) -> float:
    """Factor de correccion por amortiguamiento del Eurocodigo 8 (EN
    1998-1 SS3.2.2.2, verificado en vivo 2026-09-30 contra
    eurocodeapplied.com) -- NSR-10 A.2.6 no tiene ningun mecanismo
    nativo equivalente, asume 5% de amortiguamiento critico fijo
    siempre (ver issue #75). Extension de ingenieria NO normativa,
    pensada para aislamiento sismico/disipadores de energia donde el
    amortiguamiento real difiere del 5% estandar -- StructAI no calcula
    ese xi_pct, debe venir de un estudio aparte del usuario.

    eta = max(sqrt(10/(5+xi_pct)), 0.55)

    Con xi_pct=5.0 (caso normal, sin aislamiento) da exactamente 1.0 --
    el espectro no cambia, cero regresion para el 99% de los usuarios
    que nunca pasan este parametro."""
    return max((10.0 / (5.0 + xi_pct)) ** 0.5, 0.55)


# Tabla N.5 de la NTE E.031 "Aislamiento Sismico" de Peru (DS-030-2019-VIVIENDA,
# El Peruano, 6-nov-2019) -- misma familia normativa que ASCE/SEI 7-05 y FEMA 450,
# los DOS documentos que NSR-10 A.3.8.1 exige textualmente para aislamiento sismico
# en Colombia (verificado contra nsr10_chunks, ids NSR10-A-A_3_8_aislamiento_sismico_base_p1-p4,
# issue #77). A diferencia de eta (Eurocodigo, issue #75, extension NO normativa),
# esta tabla SI es trazable a lo que la norma colombiana nombra por documento y
# edicion -- aunque no se confirmo byte a byte contra el PDF original de ASCE 7-05/
# FEMA 450 (escaneos sin capa de texto, sin acceso), solo contra esta fuente
# primaria legible de la misma familia normativa.
_TABLA_B_AMORTIGUAMIENTO: tuple[tuple[float, float], ...] = (
    (2.0, 0.8),
    (5.0, 1.0),
    (10.0, 1.2),
    (20.0, 1.5),
    (30.0, 1.7),
    (40.0, 1.9),
)


def _factor_B_amortiguamiento(xi_pct: float) -> float:
    """Factor B de ASCE 7-05/FEMA 450 (via Tabla N.5 de Peru E.031, issue #77)
    -- interpolacion lineal entre puntos de la tabla, tal como la propia norma
    indica ("para valores intermedios... se obtendra por interpolacion
    lineal"). Fuera de la tabla (xi_pct<2% o >40%) se clampea al extremo mas
    cercano (0.8/1.9) en vez de extrapolar, porque la norma no define esos
    rangos.

    Con xi_pct=5.0 (default, caso normal) da exactamente 1.0 -- mismo
    contrato de cero-regresion que _eta_amortiguamiento(). Se usa como
    DIVISOR de Sa (Sa_efectivo = Sa_5% / B), no como multiplicador --
    convencion real de la tabla (B=razon entre Sa al 5% y Sa al
    amortiguamiento efectivo)."""
    if xi_pct <= _TABLA_B_AMORTIGUAMIENTO[0][0]:
        return _TABLA_B_AMORTIGUAMIENTO[0][1]
    if xi_pct >= _TABLA_B_AMORTIGUAMIENTO[-1][0]:
        return _TABLA_B_AMORTIGUAMIENTO[-1][1]
    for (xi_lo, b_lo), (xi_hi, b_hi) in zip(_TABLA_B_AMORTIGUAMIENTO, _TABLA_B_AMORTIGUAMIENTO[1:]):
        if xi_lo <= xi_pct <= xi_hi:
            frac = (xi_pct - xi_lo) / (xi_hi - xi_lo)
            return b_lo + frac * (b_hi - b_lo)
    raise AssertionError("xi_pct fuera de rango tras los chequeos de clamp -- no deberia ocurrir")


def _sa(T: float, esp: dict, xi_pct: float = 5.0, metodo_amortiguamiento: str = "eurocodigo") -> float:
    """T es el periodo fundamental -- la rama T<T0 no aplica (ver
    docstring de _espectro). T<=Ts(=TC real): meseta constante
    (A.2.6-3). Ts<T<=TL: rama descendente 1/T (A.2.6-1). T>TL: rama de
    periodo largo 1/T^2 (A.2.6-5). xi_pct escala las 3 ramas -- con el
    default 5.0 el factor es exactamente 1.0 sin importar el metodo.

    metodo_amortiguamiento (issue #77) elige COMO se escala:
    - "eurocodigo" (default, issue #75): multiplica por
      _eta_amortiguamiento(xi_pct) -- extension de ingenieria NO
      normativa, NSR-10 no reconoce Eurocodigo 8.
    - "asce_fema": divide por _factor_B_amortiguamiento(xi_pct) -- SI
      trazable a NSR-10 A.3.8.1, que exige literalmente ASCE/SEI 7-05 o
      FEMA 450 para aislamiento sismico en Colombia."""
    if metodo_amortiguamiento == "asce_fema":
        factor = 1.0 / _factor_B_amortiguamiento(xi_pct)
    else:
        factor = _eta_amortiguamiento(xi_pct)
    if T <= esp["Ts"]:
        return factor * esp["SDS"]
    elif T <= esp["TL"]:
        return factor * esp["SD1"] / T
    return factor * esp["SD1"] * esp["TL"] / T**2


def _periodo(p: dict, h_mm: float) -> float:
    return p["Ct"] * ((h_mm / 1000.0) ** p["alpha"])


def calcular_demanda_cortante_nudo(
    cargas: dict,
    zona: dict,
    altura_piso_mm: float = 3000.0,
    xi_pct: float = 5.0,
    metodo_amortiguamiento: str = "eurocodigo",
) -> dict:
    """
    Calcula Vu de diseño combinando gravedad + sismo NSR-10 C.9.2.
    Retorna diccionario con todos los valores intermedios y finales.

    xi_pct: amortiguamiento viscoso real de la estructura en %, solo
    relevante con aislamiento sismico/disipadores. Default 5.0 =
    comportamiento NSR-10 estandar, sin cambio alguno.

    metodo_amortiguamiento: "eurocodigo" (default, issue #75, extension
    NO normativa) o "asce_fema" (issue #77, trazable a NSR-10 A.3.8.1).
    Ver docstring de _sa().
    """
    At    = cargas["tributaria_viga"]
    CM    = (cargas["peso_propio_losa"] + cargas["carga_muerta_adicional"]) * At * 1000
    CV    = cargas["carga_viva_piso"] * At * 1000
    n     = cargas["numero_pisos"]
    W     = (CM + CV) * n

    esp   = _espectro(zona)
    T     = _periodo(zona, altura_piso_mm * n)
    Sa    = _sa(T, esp, xi_pct, metodo_amortiguamiento)
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
        "xi_pct":                xi_pct,
        "metodo_amortiguamiento": metodo_amortiguamiento,
        "eta_amortiguamiento":   _eta_amortiguamiento(xi_pct),
        "factor_B_amortiguamiento": _factor_B_amortiguamiento(xi_pct),
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
