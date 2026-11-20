"""Optimizador multiobjetivo de pórtico plano: frontera de Pareto EXACTA por enumeración (L1, issue #167).

Fase 1 del protocolo (docs/investigacion/L1_OPTIMIZACION_ESTRUCTURAL_COSTO_SEGURIDAD_CARBONO.md): cada candidato factible de
`diseno_integral` sale con sus cantidades (acero, concreto), CO₂e A1–A3 y la razón demanda/capacidad máxima.
Fase 2: frontera de Pareto exacta sobre la rejilla (lado de columna) × (b, h de viga) × (f'c), sin barrido de pesos ni
metaheurística, y cuatro puntos con nombre fijados ANTES de cualquier corrida (ver PUNTOS_NOMBRADOS). Cada punto con nombre se
reanaliza con la ruta escalar de referencia.

Objetivos, todos a minimizar:
  costo_directo_cop      APU Barranquilla (el mismo costo de `diseno_integral`)
  masa_acero_kg          barras longitudinales + estribos (hipótesis de cuantificación de motor_concreto.cantidades_costo)
  volumen_concreto_m3    vigas con luz libre + columnas con altura de entrepiso (sin doble conteo en el nudo)
  co2e_kg                A1–A3: volumen × kgCO₂e/m³ de la mezcla + acero × 1,322 kgCO₂e/kg (economia_concreto)
  deriva_relativa        Δ/hp máxima con el factor de fisuración declarado del proyecto
  razon_dc_max           máximo demanda/capacidad de resistencia (flexión y cortante de viga, flexo-compresión y cortante de columna)

No es el experimento H1: los umbrales Δc/δ, la matriz de casos, la línea base B0 y el ejemplo de retro-validación son decisiones
abiertas del protocolo y no se fijan aquí.
"""
from __future__ import annotations

import dataclasses
import importlib
import math
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import diseno_integral as _di
from . import diseno_portico as _dp
from .diseno_inverso import FC_MPA_POR_CALIDAD

_cc = importlib.import_module("motor_concreto.cantidades_costo")

OBJETIVOS = ("costo_directo_cop", "masa_acero_kg", "volumen_concreto_m3", "co2e_kg", "deriva_relativa", "razon_dc_max")

# Fijados antes de la primera corrida (protocolo L1, Fase 0). Cambiarlos exige nueva versión del protocolo.
PUNTOS_NOMBRADOS = {
    "min_costo": "Mínimo costo directo (= línea base B1, el motor actual); desempate por CO₂e",
    "min_co2e": "Mínimo CO₂e A1–A3; desempate por costo",
    "mayor_holgura": "Menor razón demanda/capacidad máxima; desempate por costo",
    "compromiso": "Mínima distancia de Chebyshev al punto ideal con objetivos normalizados al rango de la frontera y pesos "
                  "iguales; desempate por costo",
}
# Verificaciones de RESISTENCIA que entran a la razón D/C (las geométricas y de detallado no miden holgura de resistencia)
_RX_RESISTENCIA = ("Flexión", "Cortante", "Flexo-compresión")
VERSION_PROTOCOLO = "L1-fase0-2026-11-16"

SUPUESTOS = _di.SUPUESTOS + (
    "Frontera exacta sobre la rejilla declarada: dentro de cada (c, b, h, f'c) el refuerzo es el de mínimo costo de diseno_integral; "
    "otro refuerzo de la misma sección podría bajar CO₂e o D/C y no se explora.",
    "Cantidades con las hipótesis de motor_concreto.cantidades_costo (sin traslapos ni figurado): subestiman el acero real 5–15 %; "
    "sirven para comparar alternativas, no para presupuestar.",
    "CO₂e solo A1–A3 (producto), factores de data/factores_emision/factores_emision_2026-11.json; sin transporte ni obra (A4–A5).",
)


@dataclass(frozen=True)
class CandidatoPareto:
    calidad_concreto: str
    fc_mpa: float
    c_mm: float
    b_mm: float
    h_mm: float
    costo_directo_cop: float
    masa_acero_kg: float
    volumen_concreto_m3: float
    co2e_kg: float
    deriva_relativa: float
    razon_dc_max: float
    razon_scwb: float
    q_max: float
    base: object = field(repr=False, compare=False, default=None)     # CandidatoIntegral

    def vector(self) -> tuple[float, ...]:
        return tuple(getattr(self, k) for k in OBJETIVOS)


@dataclass(frozen=True)
class InformePareto:
    capacidad: str
    factibles: tuple[CandidatoPareto, ...]
    frontera: tuple[CandidatoPareto, ...]
    puntos: dict
    evaluadas: int
    paridad: dict
    diagnostico: dict
    supuestos: tuple[str, ...] = field(default_factory=lambda: SUPUESTOS)


# ---------------------------------------------------------------- Fase 1: cantidades, CO₂e y D/C de un candidato

def cantidades_portico(p: _dp.ProyectoPortico, o) -> "_cc.Cantidades":
    """Cantidades de todo el pórtico: una viga por vano y nivel (luz libre L − c) y nx columnas por entrepiso (altura hp)."""
    dv, dc = o.viga, o.columna
    total = _cc.Cantidades(0.0, 0.0, 0.0)
    for L in p.luces_m:
        ln_mm = L * 1000.0 - o.c
        n_est = max(2, _di._dv.contar_estribos(ln_mm, dv.h, dv.s_conf, dv.s_centro, dv.nivel != "DMI"))   # = _costo_nivel
        q = _cc.cantidades_viga(dataclasses.replace(dv, n_estribos=n_est), ln_mm / 1000.0, p.recubrimiento_mm)
        for _ in p.alturas_piso_m:
            total = total + q
    nx = len(p.luces_m) + 1
    for hp in p.alturas_piso_m:
        q = _cc.cantidades_columna(dc, hp, p.recubrimiento_mm)
        for _ in range(nx):
            total = total + q
    return total


def razon_dc(*disenos) -> float:
    """Máximo demanda/capacidad de las verificaciones de resistencia de los diseños dados (≤ 1 si cumplen)."""
    razones = [v.razon for d in disenos for v in d.verificaciones if v.nombre.startswith(_RX_RESISTENCIA)]
    if not razones:
        raise ValueError("El diseño no trae verificaciones de resistencia (flexión, cortante o flexo-compresión): no hay D/C")
    return float(max(razones))


def evaluar(p: _dp.ProyectoPortico, o) -> CandidatoPareto:
    fc = FC_MPA_POR_CALIDAD[p.calidad_concreto]
    q = cantidades_portico(p, o)
    _cop, co2 = _cc.costo_co2(q, fc)
    deriva = o.deriva * p.factor_deriva_fisurada if o.deriva == o.deriva else math.nan
    return CandidatoPareto(p.calidad_concreto, fc, o.c, o.b, o.h, float(o.costo_directo), float(q.acero_kg), float(q.volumen_m3),
                           float(co2), float(deriva), razon_dc(o.viga, o.columna), float(o.razon_scwb), float(o.q_max), o)


# ---------------------------------------------------------------- Fase 2: frontera exacta y puntos con nombre

def no_dominados(F: np.ndarray) -> np.ndarray:
    """Máscara de filas no dominadas (minimización). a domina a b si a ≤ b en todo y a < b en alguno. Duplicados exactos se conservan."""
    F = np.asarray(F, dtype=float)
    if F.ndim != 2 or not np.isfinite(F).all():
        raise ValueError("La matriz de objetivos debe ser 2D y finita (sin NaN): un objetivo indefinido no se puede ordenar")
    le = (F[:, None, :] <= F[None, :, :]).all(axis=2)
    lt = (F[:, None, :] < F[None, :, :]).any(axis=2)
    domina = le & lt                                   # domina[i, j]: i domina a j
    return ~domina.any(axis=0)


def _elegir(frontera: list[CandidatoPareto], clave) -> CandidatoPareto:
    return min(frontera, key=lambda c: (clave(c), c.costo_directo_cop, c.co2e_kg))


def puntos_nombrados(frontera: list[CandidatoPareto], objetivos=OBJETIVOS) -> dict:
    if not frontera:
        raise ValueError("Frontera vacía: no hay puntos que nombrar")
    F = np.array([[getattr(c, k) for k in objetivos] for c in frontera])
    ideal, nadir = F.min(axis=0), F.max(axis=0)
    rango = np.where(nadir > ideal, nadir - ideal, 1.0)
    cheb = ((F - ideal) / rango).max(axis=1)
    idx = {id(c): i for i, c in enumerate(frontera)}
    return {
        "min_costo": min(frontera, key=lambda c: (c.costo_directo_cop, c.co2e_kg)),
        "min_co2e": _elegir(frontera, lambda c: c.co2e_kg),
        "mayor_holgura": _elegir(frontera, lambda c: c.razon_dc_max),
        "compromiso": _elegir(frontera, lambda c: float(cheb[idx[id(c)]])),
    }


def optimizar_portico(p: _dp.ProyectoPortico, calidades: tuple[str, ...] = ("3000", "4000"), *, columnas_mm=_di.COLUMNAS_MM,
                      grilla: Optional[tuple] = None, verificar_escalar: bool = True) -> InformePareto:
    """Frontera de Pareto exacta de (costo, acero, concreto, CO₂e, deriva, D/C) sobre (c, b, h, f'c). Exige perfil_suelo o fuerzas."""
    t0 = time.perf_counter()
    if not calidades:
        raise ValueError("Se requiere al menos una calidad de concreto (f'c es variable de diseño en L1)")
    for k in calidades:
        if k not in FC_MPA_POR_CALIDAD:
            raise ValueError(f"calidad_concreto '{k}' no soportada: {sorted(FC_MPA_POR_CALIDAD)}")
    factibles: list[CandidatoPareto] = []
    evaluadas, capacidad, por_calidad = 0, None, {}
    for k in dict.fromkeys(calidades):
        pk = dataclasses.replace(p, calidad_concreto=k)
        inf = _di.diseno_integral(pk, top=10**9, columnas_mm=columnas_mm, grilla=grilla, verificar_escalar=verificar_escalar)
        evaluadas += inf.evaluadas
        capacidad = inf.capacidad
        por_calidad[k] = inf.factibles
        factibles += [evaluar(dataclasses.replace(pk, columna_mm=(o.c, o.c)), o) for o in inf.ranking]
    if not factibles:
        raise ValueError(
            f"Ninguna combinación de la rejilla cumple deriva (NSR-10 A.6.4), estabilidad (C.10.10.5.2), flexo-compresión y columna "
            f"fuerte–viga débil (C.21.6.2) ({evaluadas} evaluadas): ampliar la rejilla o reducir las cargas.")
    sin_deriva = any(c.deriva_relativa != c.deriva_relativa for c in factibles)
    objetivos = tuple(k for k in OBJETIVOS if not (sin_deriva and k == "deriva_relativa"))
    F = np.array([[getattr(c, k) for k in objetivos] for c in factibles])
    mascara = no_dominados(F)
    frontera = sorted((c for c, m in zip(factibles, mascara) if m), key=lambda c: (c.costo_directo_cop, c.co2e_kg))
    puntos = puntos_nombrados(frontera, objetivos)
    paridad = {}
    cap, info = _dp._capacidad(p)
    ctx = _dp._ctx_sismico(p, cap, info)
    for nombre, c in puntos.items():
        po = dataclasses.replace(p, calidad_concreto=c.calidad_concreto, columna_mm=(c.c_mm, c.c_mm))
        paridad[nombre], _basal = _di._verificar_optimo(po, ctx, c.base, verificar_escalar)
    diag = {"evaluadas": evaluadas, "factibles": len(factibles), "en_frontera": len(frontera), "factibles_por_calidad": por_calidad,
            "objetivos": list(objetivos), "version_protocolo": VERSION_PROTOCOLO, "t_total_s": round(time.perf_counter() - t0, 3)}
    return InformePareto(capacidad, tuple(factibles), tuple(frontera), puntos, evaluadas, paridad, diag)
