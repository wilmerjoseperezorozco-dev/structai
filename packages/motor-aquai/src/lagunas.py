"""Sistema lagunar en serie (#236): anaerobia → facultativa → n lagunas de maduración, con contrato uniforme.

Norma de diseño: Resolución 0330 de 2017 (reemplazó al RAS 2000), artículos 196 (anaerobia), 197 (facultativa),
198 (maduración), 199 (borde libre), 200 (consideraciones comunes) y 216 (remoción de lodos al 50 % del volumen).
Vertimiento: Resolución 0631 de 2015, art. 8 (ver `vertimientos.py`).

La Res. 0330 fija rangos, no el método de dimensionamiento. Las ecuaciones de diseño son las del método de Mara
(Mara, D. 2003, *Domestic Wastewater Treatment in Developing Countries*, Earthscan, cap. 11), con la constante de
decaimiento de coliformes de Marais (1974). Las constantes de Mara quedan declaradas en `supuestos` y deben
contrastarse con la edición citada antes del diseño definitivo:
- anaerobia: λv = 20T − 100 (10 ≤ T ≤ 20 °C), 10T + 100 (20 < T ≤ 25), 350 g/m³·d (T > 25); remoción de DBO5
  = 2T + 20 % (T ≤ 25) o 70 % (T > 25);
- facultativa: λs = 350·(1,107 − 0,002T)^(T − 25) kg/ha·d; DBO5 del efluente por primer orden en mezcla completa con
  k1 = 0,3·1,05^(T − 20) d⁻¹;
- coliformes: N = N0 / [(1 + kT·θa)(1 + kT·θf)·Π(1 + kT·θi)], kT = 2,6·1,19^(T − 20) d⁻¹;
- maduración: θi ≥ 3 d, y la carga superficial de la primera ≤ 0,75 de la carga real de la facultativa.

Optimización (regla 6): minimizar Σθi (área total de maduración, a profundidad común) sujeto a Π(1 + kT·θi) ≥ R,
θ1 ≥ a = máx(3, θcarga) y θi ≥ 3 para i ≥ 2. El problema es convexo (Σ ln(1 + kT·θi) es cóncava). Por KKT, las
lagunas no acotadas tienen el mismo θ, así que el óptimo es uno de dos: todas iguales si ese θ común ya cumple
θ ≥ a, o θ1 = a con las demás iguales (forma cerrada). Se recorre n ∈ [0, N_MAX] de forma exhaustiva, y el
resultado se marca en borde de dominio si el óptimo cae en la cota.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from . import vertimientos  # noqa: E402

RES0330 = "Resolución 0330 de 2017"
T_MIN_C, T_MAX_C = 10.0, 35.0           # dominio del método de Mara para λv y λs
N_MAX_MADURACION = 8
THETA_MIN_MADURACION_D = 3.0            # Mara (2003)
FRACCION_CARGA_MADURACION = 0.75        # Mara (2003): λs de la 1.ª de maduración ≤ 0,75 λs facultativa
PERIODO_MIN_LODOS_ANOS = 1.0            # menos de un año entre remociones: diseño no operable (se rechaza)
DBO_PER_CAPITA_COHERENTE = (10.0, 200.0)  # g/hab·d: fuera de esto, población y carga no son del mismo sistema
DBO_PER_CAPITA_TIPICA = (30.0, 80.0)      # g/hab·d: fuera de esto, borde de dominio

# Rangos de la Res. 0330 (solo los números de los artículos).
PROF_ANAEROBIA = (2.5, 5.0)             # art. 196, num. 1
CARGA_VOL_ANAEROBIA = (100.0, 500.0)    # art. 196, num. 2 (g DBO5/m³·d)
TRH_ANAEROBIA = (1.0, 3.0)              # art. 196, num. 3 (d)
PROF_FACULTATIVA = (1.5, 2.5)           # art. 197
TRH_FACULTATIVA = (5.0, 30.0)           # art. 197 (d)
CARGA_SUP_FACULTATIVA = (100.0, 350.0)  # art. 197 (kg DBO5/ha·d)
PROF_MADURACION = (0.9, 1.0)            # art. 198
BORDE_LIBRE = (0.3, 0.5)                # art. 199
BORDE_LIBRE_TURBULENCIA = (0.51, 0.8)   # art. 199
FRACCION_LODOS_REMOCION = 0.5           # art. 216, num. 1

_EPS = 1e-9


class SolicitudLagunas(BaseModel):
    model_config = ConfigDict(strict=True)

    caudal_medio_m3_dia: float = Field(..., gt=0, le=500_000, allow_inf_nan=False,
                                       description="Caudal medio de diseño (Res. 0330 art. 164)")
    poblacion_equivalente: int = Field(..., gt=0, le=10_000_000, description="Para el balance de lodos")
    dbo5_afluente_mg_l: float = Field(..., gt=0, le=2000, allow_inf_nan=False)
    coliformes_afluente_nmp_100ml: float = Field(..., gt=0, le=1e12, allow_inf_nan=False)
    coliformes_objetivo_nmp_100ml: float = Field(..., gt=0, allow_inf_nan=False,
                                                 description="Objetivo fijado por la autoridad o por el reúso")
    temperatura_agua_c: float = Field(..., allow_inf_nan=False, description="Media del mes más frío")
    incluir_anaerobia: bool
    profundidad_anaerobia_m: Optional[float] = Field(..., allow_inf_nan=False,
                                                     description="Obligatoria si incluir_anaerobia; si no, null")
    profundidad_facultativa_m: float = Field(..., allow_inf_nan=False)
    profundidad_maduracion_m: float = Field(..., allow_inf_nan=False)
    borde_libre_m: float = Field(..., allow_inf_nan=False)
    alta_turbulencia_atmosferica: bool = Field(..., description="Res. 0330 art. 199: cambia el rango del borde libre")
    tasa_acumulacion_lodos_m3_hab_ano: float = Field(..., gt=0, le=0.2, allow_inf_nan=False,
                                                     description="Mara (2003) usa 0,04 m³/hab·año en anaerobias")
    area_disponible_m2: Optional[float] = Field(..., gt=0, allow_inf_nan=False,
                                                description="Espejo de agua disponible; null = sin restricción")
    cuerpo_receptor: str = Field(..., description="rio | quebrada | lago (Res. 0631 no aplica al suelo)")


def _en_rango(valor: float, rango: tuple[float, float], que: str, articulo: str) -> bool:
    """Lanza ValueError fuera del rango normativo; devuelve True si toca un extremo (borde de dominio)."""
    lo, hi = rango
    if valor < lo - _EPS or valor > hi + _EPS:
        raise ValueError(f"{que} = {valor:g} fuera del rango {lo:g}–{hi:g} del {RES0330}, {articulo}.")
    return _toca(valor, lo) or _toca(valor, hi)


def _toca(valor: float, limite: float) -> bool:
    return abs(valor - limite) <= 1e-6 * max(1.0, abs(limite))


def carga_volumetrica_anaerobia_mara(t: float) -> float:
    """λv de diseño (g DBO5/m³·d) según Mara (2003)."""
    if t <= 20.0:
        return 20.0 * t - 100.0
    if t <= 25.0:
        return 10.0 * t + 100.0
    return 350.0


def remocion_dbo_anaerobia_mara(t: float) -> float:
    """Fracción de DBO5 removida en la laguna anaerobia según Mara (2003)."""
    return (2.0 * t + 20.0) / 100.0 if t <= 25.0 else 0.70


def carga_superficial_facultativa_mara(t: float) -> float:
    """λs de diseño (kg DBO5/ha·d) según Mara (2003)."""
    return 350.0 * (1.107 - 0.002 * t) ** (t - 25.0)


def k1_dbo_facultativa(t: float) -> float:
    return 0.3 * 1.05 ** (t - 20.0)


def k_coliformes_marais(t: float) -> float:
    return 2.6 * 1.19 ** (t - 20.0)


def validar_temperatura(t: float, borde: list) -> None:
    if not (T_MIN_C <= t <= T_MAX_C):
        raise ValueError(f"Temperatura del agua {t:g} °C fuera del dominio del método de Mara ({T_MIN_C:g}–{T_MAX_C:g} °C); "
                         f"la {RES0330} (arts. 196–198) no fija un método fuera de él.")
    if _toca(t, T_MIN_C) or _toca(t, T_MAX_C):
        borde.append("temperatura en el extremo del dominio del método de Mara")


def facultativa(q: float, lf: float, t: float, df: float, borde: list) -> dict:
    """Laguna facultativa por Mara (2003) dentro del art. 197. La usan el sistema lagunar y la PTAR."""
    if _en_rango(df, PROF_FACULTATIVA, "Profundidad de la laguna facultativa (m)", "art. 197"):
        borde.append("profundidad facultativa en el extremo del art. 197")
    lam_s_mara = carga_superficial_facultativa_mara(t)
    lam_s = min(lam_s_mara, CARGA_SUP_FACULTATIVA[1])
    if lam_s_mara > CARGA_SUP_FACULTATIVA[1]:
        borde.append("λs de Mara limitada al máximo de 350 kg/ha·d del art. 197")
    af = 10.0 * lf * q / lam_s
    theta_f = af * df / q
    if theta_f < TRH_FACULTATIVA[0]:
        theta_f = TRH_FACULTATIVA[0]
        af = q * theta_f / df
        borde.append("TRH facultativo llevado al mínimo de 5 d del art. 197")
    if theta_f > TRH_FACULTATIVA[1] + _EPS:
        raise ValueError(f"La laguna facultativa necesitaría θ = {theta_f:.1f} d > 30 d ({RES0330}, art. 197). "
                         "Reduzca la profundidad o incluya una laguna anaerobia previa.")
    if _toca(theta_f, TRH_FACULTATIVA[0]) and "TRH facultativo llevado al mínimo de 5 d del art. 197" not in borde:
        borde.append("TRH facultativo en el mínimo de 5 d del art. 197")
    if _toca(theta_f, TRH_FACULTATIVA[1]):
        borde.append("TRH facultativo en el máximo de 30 d del art. 197")
    lam_s_real = 10.0 * lf * q / af
    if lam_s_real < CARGA_SUP_FACULTATIVA[0] - _EPS:
        raise ValueError(f"Carga superficial {lam_s_real:.0f} kg/ha·d < 100 ({RES0330}, art. 197) con θ = 5 d: "
                         "reduzca la profundidad facultativa o revise la DBO5 afluente.")
    if _toca(lam_s_real, CARGA_SUP_FACULTATIVA[0]) or _toca(lam_s_real, CARGA_SUP_FACULTATIVA[1]):
        borde.append("carga superficial facultativa en un extremo del art. 197")
    le = lf / (1.0 + k1_dbo_facultativa(t) * theta_f)
    return dict(area_m2=af, profundidad_m=df, volumen_m3=af * df, trh_d=theta_f, carga_superficial_kg_ha_d=lam_s_real,
                dbo5_entrada_mg_l=lf, dbo5_salida_mg_l=le, lambda_s_mara=lam_s_mara)


def maduracion_optima(n_entrada: float, objetivo: float, kt: float, theta_carga: float) -> tuple[int, list[float]]:
    """(n, [θ1..θn]) de mínima Σθ. Ver la cabecera del módulo: problema convexo resuelto por KKT en forma cerrada."""
    if n_entrada <= objetivo * (1 + 1e-12):
        return 0, []
    r = n_entrada / objetivo
    a = max(THETA_MIN_MADURACION_D, theta_carga)
    mejor: Optional[tuple[int, list[float]]] = None
    for n in range(1, N_MAX_MADURACION + 1):
        theta_eq = (r ** (1.0 / n) - 1.0) / kt
        if theta_eq >= a:
            thetas = [theta_eq] * n
        elif n == 1:
            thetas = [a]
        else:
            resto = max(THETA_MIN_MADURACION_D, ((r / (1.0 + kt * a)) ** (1.0 / (n - 1)) - 1.0) / kt)
            thetas = [a] + [resto] * (n - 1)
        if mejor is None or sum(thetas) < sum(mejor[1]) - 1e-9:
            mejor = (n, thetas)
    return mejor


def disenar_lagunas(req: SolicitudLagunas) -> ResultadoMotor:
    t = req.temperatura_agua_c
    borde: list[str] = []
    advertencias: list[str] = []
    validar_temperatura(t, borde)
    q, li = req.caudal_medio_m3_dia, req.dbo5_afluente_mg_l
    supuestos = [
        "Constantes del método de Mara (2003) y kT de Marais (1974), declaradas en la cabecera del módulo: "
        "contrastarlas con la edición citada antes del diseño definitivo.",
        "Flujo en mezcla completa en cada laguna; no se descuenta la evaporación (θ calculado con el caudal "
        "afluente, lo que subestima θ y es conservador).",
        "La DBO5 del efluente es la de la laguna facultativa: no se acredita remoción adicional de DBO5 en las "
        "lagunas de maduración (conservador). El efluente contiene algas; la DBO5 total debe confirmarse con "
        "caracterización.",
        "No se modelan SST ni DQO del efluente: el cumplimiento de esos parámetros de la Res. 0631 no se verifica.",
        "Áreas al nivel del agua; no incluyen taludes, diques ni vías (Res. 0330 art. 200).",
        "El tramo de carga del art. 8 de la Res. 0631 se elige con la carga de DBO5 del afluente crudo.",
        f"Se rechaza un diseño cuya laguna receptora llegue al 50 % de lodos en menos de {PERIODO_MIN_LODOS_ANOS:g} año.",
    ]

    # Coherencia entre la población y la carga (el balance de lodos depende de ambas)
    g_hab = li * q / req.poblacion_equivalente      # mg/L · m³/d / hab = g/hab·d
    if not (DBO_PER_CAPITA_COHERENTE[0] <= g_hab <= DBO_PER_CAPITA_COHERENTE[1]):
        raise ValueError(f"La carga equivale a {g_hab:.1f} g DBO5/hab·d con la población dada: fuera de "
                         f"{DBO_PER_CAPITA_COHERENTE[0]:g}–{DBO_PER_CAPITA_COHERENTE[1]:g}. Población, caudal y DBO5 "
                         "no describen el mismo sistema; revíselos.")
    if not (DBO_PER_CAPITA_TIPICA[0] <= g_hab <= DBO_PER_CAPITA_TIPICA[1]):
        borde.append(f"carga per cápita atípica ({g_hab:.1f} g DBO5/hab·d)")

    # Borde libre (art. 199)
    rango_bl = BORDE_LIBRE_TURBULENCIA if req.alta_turbulencia_atmosferica else BORDE_LIBRE
    if _en_rango(req.borde_libre_m, rango_bl, "Borde libre (m)", "art. 199"):
        borde.append("borde libre en el extremo del rango del art. 199")

    lagunas: list[dict] = []
    theta_a = 0.0
    lf = li
    vol_receptora = None

    # ── Anaerobia (art. 196) ─────────────────────────────────────────────
    if req.incluir_anaerobia:
        if req.profundidad_anaerobia_m is None:
            raise ValueError(f"Con laguna anaerobia, la profundidad es obligatoria ({RES0330}, art. 196: 2,5 a 5 m). "
                             "No se asume ningún valor.")
        da = req.profundidad_anaerobia_m
        if _en_rango(da, PROF_ANAEROBIA, "Profundidad de la laguna anaerobia (m)", "art. 196, num. 1"):
            borde.append("profundidad anaerobia en el extremo del art. 196")
        lam_v = carga_volumetrica_anaerobia_mara(t)
        theta_a = li / lam_v
        if theta_a < TRH_ANAEROBIA[0]:
            theta_a = TRH_ANAEROBIA[0]
            borde.append("TRH anaerobio llevado al mínimo de 1 d del art. 196")
        if theta_a > TRH_ANAEROBIA[1] + _EPS:
            raise ValueError(f"La laguna anaerobia necesitaría θ = {theta_a:.2f} d > 3 d ({RES0330}, art. 196, num. 3) "
                             f"con λv = {lam_v:.0f} g/m³·d a {t:g} °C. Reduzca la DBO5 afluente con pretratamiento.")
        if _toca(theta_a, TRH_ANAEROBIA[0]) and "TRH anaerobio llevado al mínimo de 1 d del art. 196" not in borde:
            borde.append("TRH anaerobio en el mínimo de 1 d del art. 196")
        if _toca(theta_a, TRH_ANAEROBIA[1]):
            borde.append("TRH anaerobio en el máximo de 3 d del art. 196")
        lam_v_real = li / theta_a
        if lam_v_real < CARGA_VOL_ANAEROBIA[0] - _EPS:
            raise ValueError(f"Carga volumétrica {lam_v_real:.0f} g/m³·d < 100 g/m³·d ({RES0330}, art. 196, num. 2): "
                             "el afluente es demasiado diluido para una laguna anaerobia; omítala.")
        if _toca(lam_v_real, CARGA_VOL_ANAEROBIA[0]) or _toca(lam_v_real, CARGA_VOL_ANAEROBIA[1]):
            borde.append("carga volumétrica anaerobia en un extremo del art. 196")
        va = q * theta_a
        lf = li * (1.0 - remocion_dbo_anaerobia_mara(t))
        vol_receptora = va
        lagunas.append(dict(tipo="anaerobia", cantidad=1, area_m2=va / da, profundidad_m=da,
                            profundidad_total_m=da + req.borde_libre_m, volumen_m3=va, trh_d=theta_a,
                            carga_volumetrica_g_m3_d=lam_v_real, dbo5_entrada_mg_l=li, dbo5_salida_mg_l=lf))
    elif req.profundidad_anaerobia_m is not None:
        raise ValueError("Se dio profundidad anaerobia sin incluir la laguna anaerobia: dato contradictorio.")

    # ── Facultativa (art. 197) ───────────────────────────────────────────
    fac = facultativa(q, lf, t, req.profundidad_facultativa_m, borde)
    theta_f, le, lam_s_mara = fac["trh_d"], fac["dbo5_salida_mg_l"], fac.pop("lambda_s_mara")
    if vol_receptora is None:
        vol_receptora = fac["volumen_m3"]
    lagunas.append(dict(tipo="facultativa", cantidad=1, profundidad_total_m=fac["profundidad_m"] + req.borde_libre_m, **fac))

    # ── Maduración (art. 198) ────────────────────────────────────────────
    dm = req.profundidad_maduracion_m
    if _en_rango(dm, PROF_MADURACION, "Profundidad de la laguna de maduración (m)", "art. 198"):
        borde.append("profundidad de maduración en el extremo del art. 198")
    kt = k_coliformes_marais(t)
    n0 = req.coliformes_afluente_nmp_100ml
    n_fac = n0 / ((1.0 + kt * theta_a) * (1.0 + kt * theta_f))
    # Mara: la primera de maduración no debe recibir más de 0,75 de la carga real de la facultativa.
    theta_carga = 10.0 * le * dm / (FRACCION_CARGA_MADURACION * fac["carga_superficial_kg_ha_d"])
    n_mad, thetas = maduracion_optima(n_fac, req.coliformes_objetivo_nmp_100ml, kt, theta_carga)
    if n_mad == N_MAX_MADURACION:
        borde.append(f"el óptimo cae en la cota de búsqueda de {N_MAX_MADURACION} lagunas de maduración")
    if any(_toca(th, THETA_MIN_MADURACION_D) or _toca(th, theta_carga) for th in thetas):
        borde.append("al menos una laguna de maduración en su TRH mínimo (3 d o el de carga superficial)")
    n_actual = n_fac
    for i, th in enumerate(thetas, start=1):
        n_sale = n_actual / (1.0 + kt * th)
        lagunas.append(dict(tipo=f"maduracion_{i}", cantidad=1, area_m2=q * th / dm, profundidad_m=dm,
                            profundidad_total_m=dm + req.borde_libre_m, volumen_m3=q * th, trh_d=th,
                            coliformes_entrada_nmp_100ml=n_actual, coliformes_salida_nmp_100ml=n_sale))
        n_actual = n_sale
    n_final = n_actual

    area_total = sum(l["area_m2"] * l["cantidad"] for l in lagunas)
    if req.area_disponible_m2 is not None:
        if area_total > req.area_disponible_m2 * (1 + 1e-12):
            raise ValueError(f"Con estas profundidades y esta configuración, el diseño de área mínima necesita "
                             f"{area_total:,.0f} m² de espejo de agua y hay {req.area_disponible_m2:,.0f} m² disponibles "
                             f"({RES0330}, arts. 196–198). Pruebe a {'cambiar' if req.incluir_anaerobia else 'incluir una laguna anaerobia o cambiar'} "
                             "las profundidades, o a revisar el objetivo de coliformes con la autoridad.")
        if area_total >= 0.95 * req.area_disponible_m2:
            borde.append("el área requerida está a menos del 5 % del área disponible")

    # ── Vertimiento (Res. 0631 art. 8) ───────────────────────────────────
    carga_kg_d = li * q / 1000.0
    limites = vertimientos.limites_art8(carga_kg_d, req.cuerpo_receptor)
    if vertimientos.en_borde_de_tramo(carga_kg_d):
        borde.append("la carga de DBO5 está a menos del 5 % del cambio de tramo de la Res. 0631 art. 8")
    cumple_dbo = le <= limites["DBO5"]
    if not cumple_dbo:
        advertencias.append(f"DBO5 del efluente {le:.1f} mg/L > {limites['DBO5']:g} mg/L ({vertimientos.NORMA}).")

    # ── Lodos (art. 216) ─────────────────────────────────────────────────
    acumulacion = req.poblacion_equivalente * req.tasa_acumulacion_lodos_m3_hab_ano
    periodo = FRACCION_LODOS_REMOCION * vol_receptora / acumulacion
    receptora = lagunas[0]["tipo"]
    if periodo < PERIODO_MIN_LODOS_ANOS:
        raise ValueError(f"La laguna {receptora} llegaría al 50 % de lodos ({RES0330}, art. 216) en {periodo:.2f} años, "
                         f"menos de {PERIODO_MIN_LODOS_ANOS:g}: revise la tasa de acumulación, la población o el tamaño.")
    advertencias.append(f"{RES0330} art. 216: después de 5 años, medir la capa de lodos al menos una vez al año.")

    valor = {
        "lagunas": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in l.items()} for l in lagunas],
        "n_lagunas_maduracion": n_mad,
        "area_espejo_total_m2": round(area_total, 2),
        "dbo5_efluente_mg_l": round(le, 3),
        "coliformes_efluente_nmp_100ml": n_final,
        "cumple_objetivo_coliformes": n_final <= req.coliformes_objetivo_nmp_100ml * (1 + 1e-9),
        "limites_res0631_mg_l": limites,
        "cumple_res0631_dbo5": cumple_dbo,
        "lodos": {"laguna_receptora": receptora, "acumulacion_m3_ano": round(acumulacion, 3),
                  "periodo_remocion_anos": round(periodo, 3), "criterio": "50 % del volumen (Res. 0330 art. 216)"},
        "constantes": {"kT_coliformes_d": round(kt, 6), "k1_dbo_facultativa_d": round(k1_dbo_facultativa(t), 6),
                       "lambda_s_mara_kg_ha_d": round(lam_s_mara, 3), "theta_carga_maduracion_d": round(theta_carga, 4)},
        "borde_dominio": borde,
    }
    return ResultadoMotor(
        valor=valor,
        unidad_si="m², m, m³, d, mg/L, NMP/100 mL",
        ecuacion=("Va = Li·Q/λv; Af = 10·L·Q/λs; Le = L/(1 + k1·θf); "
                  "N = N0/[(1 + kT·θa)(1 + kT·θf)·Π(1 + kT·θi)]; mín Σθi con θ1 ≥ máx(3, θcarga), θi ≥ 3 (KKT)"),
        referencia_normativa=(f"{RES0330}, arts. 164, 196–200 y 216; {vertimientos.NORMA}; Mara (2003) cap. 11; "
                              "Marais (1974)"),
        supuestos=supuestos,
        en_borde_dominio=bool(borde),
        advertencias=advertencias,
    )
