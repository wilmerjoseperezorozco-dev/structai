"""Espacio de diseño de motor-acero-frio para la épica de optimización #311.

Lo que un optimizador necesita saber del motor, declarado en un solo lugar:
- variables con tipo y límites;
- dominio de validez (restricción dura: fuera de él el motor falla y el punto es infactible, no «malo»);
- restricciones: las razones demanda/capacidad de verificar_viga_c;
- objetivos disponibles;
- costo por evaluación medido, que decide el método según la tabla de #311.

Reglas de #311 que se aplican aquí: el optimizador propone y el motor dispone; se reporta el margen y no solo «cumple»;
la enumeración exacta es el oráculo cuando cabe en menos de 10 s.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Iterable

from .contrato_api import PerfilC, verificar_viga_c
from .elementos import D_W_MAX_TABLA, H_T_MAX_ALMA, W_T_MAX_ALETA_PESTANA, W_T_MAX_NO_RIGIDIZADO

DENSIDAD_ACERO_KG_M3 = 7850.0

ESPACIO_DISENO = {
    "motor": "motor-acero-frio",
    "funcion_evaluada": "verificar_viga_c",
    "variables": {
        "H_mm": {"tipo": "continua", "min": 50.0, "max": 400.0},
        "B_mm": {"tipo": "continua", "min": 25.0, "max": 120.0},
        "D_mm": {"tipo": "continua", "min": 0.0, "max": 40.0, "nota": "0 = C sin pestaña"},
        "t_mm": {"tipo": "catalogo", "valores": [0.9, 1.2, 1.5, 1.9, 2.0, 2.5, 3.0],
                 "nota": "calibres de referencia; reemplazar por el catálogo del proveedor"},
    },
    "parametros_fijos": ["Fy_MPa", "Fu_MPa", "Mu_kNm", "Vu_kN", "Lm_mm", "KyLy_mm", "KtLt_mm", "Cb",
                         "aleta_comprimida_arriostrada"],
    "dominio_validez": {
        "h/t del alma": f"≤ {H_T_MAX_ALMA:.0f} (F.4.2.1.2)",
        "w/t de la aleta": f"≤ {W_T_MAX_ALETA_PESTANA:.0f} con pestaña, ≤ {W_T_MAX_NO_RIGIDIZADO:.0f} sin ella (F.4.2.1.1.1)",
        "D/w": f"< {D_W_MAX_TABLA} (Tabla F.4.2.4-1)",
        "regla": "fuera del dominio el motor lanza ValueError y el punto es infactible",
    },
    "restricciones": "todas las razones de verificar_viga_c ≤ 1 (flexión con los tres estados límite, cortante, "
                     "interacción F.4.3.3-54)",
    "objetivos": {"masa_kg_m": "minimizar", "margen": "maximizar (1 − razón máxima)"},
    "costo_por_evaluacion": {"orden": "milisegundos", "medido_ms": 0.64, "equipo": "Ryzen 5 8640HS, 1 hilo"},
    "metodo_sugerido_311": "enumeración exacta para catálogos pequeños (oráculo); NSGA-II para espacios grandes (#305)",
}


@dataclass(frozen=True)
class Evaluacion:
    perfil: dict
    factible: bool
    masa_kg_m: float | None
    razon_max: float | None
    margen: float | None
    gobierna: str | None
    motivo: str | None


def masa_por_metro(perfil: PerfilC) -> float:
    return perfil.geometria().propiedades().A * 1e-6 * DENSIDAD_ACERO_KG_M3


def evaluar(dims: dict, fijos: dict) -> Evaluacion:
    """Evalúa un punto. Infactible si sale del dominio de validez o no cumple; nunca aprueba un diseño."""
    datos = {**dims, "Fy_MPa": fijos["Fy_MPa"], "Fu_MPa": fijos["Fu_MPa"]}
    try:
        perfil = PerfilC(**datos)
        r = verificar_viga_c(perfil, fijos["Mu_kNm"], fijos["Vu_kN"], Lm_mm=fijos.get("Lm_mm"),
                             KyLy_mm=fijos.get("KyLy_mm"), KtLt_mm=fijos.get("KtLt_mm"), Cb=fijos.get("Cb"),
                             aleta_comprimida_arriostrada=fijos["aleta_comprimida_arriostrada"])
    except ValueError as exc:
        return Evaluacion(dims, False, None, None, None, None, f"fuera de dominio: {exc}")
    rmax = max(r.valor["razones"].values())
    return Evaluacion(dims, r.valor["cumple"], masa_por_metro(perfil), rmax, 1 - rmax, r.valor["gobierna"],
                      None if r.valor["cumple"] else "no cumple")


def enumerar(candidatos: Iterable[dict], fijos: dict) -> list[Evaluacion]:
    """Oráculo exacto: evalúa todos los candidatos y ordena los factibles por masa (empate: mayor margen)."""
    evs = [evaluar(c, fijos) for c in candidatos]
    return sorted(evs, key=lambda e: (not e.factible, e.masa_kg_m if e.masa_kg_m is not None else math.inf,
                                      -(e.margen or 0)))


def malla(H: Iterable[float], B: Iterable[float], D: Iterable[float], t: Iterable[float]) -> list[dict]:
    return [dict(H_mm=h, B_mm=b, D_mm=d, t_mm=e) for h, b, d, e in itertools.product(H, B, D, t)]
