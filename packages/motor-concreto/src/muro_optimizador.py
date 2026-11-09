"""Optimizador de referencia («exacto») del muro de contención en voladizo por tipología: estándar, con dentellón o con bandeja de alivio.

Búsqueda local por coordenadas sobre una rejilla de 50 mm (100 mm para la cota de la bandeja) partiendo de una geometría factible que se obtiene inflando una
geometría de regla de dedo. NO es un óptimo global: es la mejor solución encontrada con límites declarados en `LIMITES`; el sustituto de aprendizaje hereda estos
sesgos. Se registra el número de evaluaciones y si alguna variable quedó pegada a su límite.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .economia_concreto import Economia
from .muro_contencion import GeometriaMuro, Relleno, SueloApoyo
from .muro_contencion_estructural import DisenoMuro, disenar_estructura
from .viga import Materiales

TIPOLOGIAS = ("estandar", "dentellon", "bandeja")
PASO = 0.05
T_CORONA = 0.25      # CONSTANTE de diseño (no es variable de búsqueda): ancho mínimo constructivo para vaciar y vibrar el concreto en la corona
# (mín., máx.) de las variables de búsqueda. Los mínimos son PISOS CONSTRUCTIVOS declarados (formaleta, recubrimientos 75 mm de C.7.7.1, ganchos); un óptimo
# sobre un piso es una regla de práctica, no un hallazgo del optimizador, por eso se reporta aparte en `Solucion.en_piso_constructivo`.
LIMITES = {"h_zapata": (0.30, 1.20), "t_base": (0.30, 1.20), "b_puntera": (0.10, 2.00), "b_talon": (0.30, 7.00),
           "dentellon_prof": (0.10, 1.00), "bandeja_y": (0.50, 6.00), "bandeja_vuelo": (0.40, 2.50)}
MAX_INFLADO = 80
MAX_BARRIDOS = 12


@dataclass(frozen=True)
class CasoMuro:
    altura: float                       # H = altura libre de la pantalla (m)
    relleno: Relleno
    apoyo: SueloApoyo
    materiales: Materiales = Materiales(28.0, 420.0)
    economia: Economia = Economia()
    a_max_g: float | None = None
    lam_co2: float = 0.0                # COP por kg CO2e para el objetivo mixto
    x_ceniza: float = 0.0               # fracción de ceniza volante del ligante (mezcla de economia_concreto)


@dataclass(frozen=True)
class Solucion:
    tipologia: str
    perfil: str
    geometria: GeometriaMuro
    diseno: DisenoMuro
    objetivo: float
    evaluaciones: int
    variables_en_limite: tuple[str, ...]        # pegadas al TECHO de búsqueda (señal de límite artificial)
    en_piso_constructivo: tuple[str, ...] = ()  # pegadas al piso constructivo declarado (regla de práctica, no hallazgo)


def _redondear(x: float, paso: float = PASO) -> float:
    return round(round(x / paso) * paso, 4)


def _inicial(caso: CasoMuro, tip: str, perfil: str) -> GeometriaMuro:
    h = caso.altura
    base = GeometriaMuro(h_pantalla=h, h_zapata=_redondear(max(0.4, h / 12.0)), t_corona=T_CORONA, t_base=_redondear(max(0.30, h / 10.0)),
                         b_puntera=_redondear(max(0.3, 0.12 * h)), b_talon=_redondear(max(0.8, 0.45 * h)), perfil=perfil)
    if tip == "dentellon":
        return replace(base, dentellon_prof=0.40, dentellon_ancho=0.40)
    if tip == "bandeja":
        return replace(base, bandeja_y=_redondear(0.5 * h, 0.1), bandeja_vuelo=_redondear(0.35 * h, 0.1), bandeja_esp=0.25)
    return base


def _evaluar(g: GeometriaMuro, caso: CasoMuro) -> DisenoMuro | None:
    try:
        return disenar_estructura(g, caso.relleno, caso.apoyo, caso.materiales, caso.economia, a_max_g=caso.a_max_g, x_ceniza=caso.x_ceniza)
    except ValueError:
        return None


def _objetivo(d: DisenoMuro, caso: CasoMuro) -> float:
    return d.costo_cop_m + caso.lam_co2 * d.co2_kg_m


def _corregir(g: GeometriaMuro, d: DisenoMuro | None) -> GeometriaMuro:
    """Un paso de inflado según la causa del incumplimiento."""
    if d is None:
        return replace(g, t_base=g.t_base + PASO)
    txt = " ".join(d.motivos)
    out = g
    if any(k in txt for k in ("volcamiento", "deslizamiento", "excentricidad", "presión", "equilibrio", "resultante")):
        out = replace(out, b_talon=out.b_talon + 0.2)
    if "pantalla" in txt or "Mononobe" in txt:
        out = replace(out, t_base=out.t_base + PASO)
    if "puntera" in txt or "talon" in txt:
        out = replace(out, h_zapata=out.h_zapata + PASO)
    if "bandeja" in txt:
        out = replace(out, bandeja_esp=out.bandeja_esp + PASO)
    if "dentellon" in txt:
        out = replace(out, dentellon_ancho=out.dentellon_ancho + PASO)
    return out if out != g else replace(g, b_talon=g.b_talon + 0.2)


def _acotar(g: GeometriaMuro) -> GeometriaMuro:
    """Fuerza t_corona ≤ t_base y respeta límites inferiores."""
    tb = max(g.t_base, g.t_corona)
    return replace(g, t_base=_redondear(tb), t_corona=_redondear(g.t_corona))


def _hacer_factible(g: GeometriaMuro, caso: CasoMuro) -> tuple[GeometriaMuro, DisenoMuro, int] | None:
    n = 0
    for _ in range(MAX_INFLADO):
        g = _acotar(g)
        d = _evaluar(g, caso)
        n += 1
        if d is not None and d.cumple:
            return g, d, n
        if g.b_talon > LIMITES["b_talon"][1] or g.h_zapata > LIMITES["h_zapata"][1] or g.t_base > LIMITES["t_base"][1]:
            return None
        g = _corregir(g, d)
    return None


def _variables(tip: str) -> list[str]:
    base = ["h_zapata", "t_base", "b_puntera", "b_talon"]
    return base + {"dentellon": ["dentellon_prof"], "bandeja": ["bandeja_y", "bandeja_vuelo"], "estandar": []}[tip]


def _mover(g: GeometriaMuro, nombre: str, signo: int) -> GeometriaMuro | None:
    paso = 0.1 if nombre.startswith("bandeja_") else PASO
    v = _redondear(getattr(g, nombre) + signo * paso, paso)
    lo, hi = LIMITES[nombre]
    return replace(g, **{nombre: v}) if lo - 1e-9 <= v <= hi + 1e-9 else None


def optimizar(caso: CasoMuro, tipologia: str, perfil: str = "lineal", inicio: GeometriaMuro | None = None) -> Solucion | None:
    """Mejor diseño factible de la tipología (y perfil) o None si no se encontró ninguno dentro de LIMITES. `inicio` permite arrancar desde una propuesta (p. ej. del sustituto)."""
    ini = _hacer_factible(inicio if inicio is not None else _inicial(caso, tipologia, perfil), caso)
    if ini is None:
        return None
    g, d, n = ini
    mejor = _objetivo(d, caso)
    for _ in range(MAX_BARRIDOS):
        mejora = False
        for var in _variables(tipologia):
            for signo in (-1, 1):
                while True:
                    cand = _mover(g, var, signo)
                    if cand is None or cand.t_corona > cand.t_base:
                        break
                    dc = _evaluar(cand, caso)
                    n += 1
                    if dc is None or not dc.cumple or _objetivo(dc, caso) >= mejor - 1.0:
                        break
                    g, d, mejor, mejora = cand, dc, _objetivo(dc, caso), True
        if not mejora:
            break
    techo = tuple(v for v in _variables(tipologia) if abs(getattr(g, v) - LIMITES[v][1]) < 1e-6)
    piso = tuple(v for v in _variables(tipologia) if abs(getattr(g, v) - LIMITES[v][0]) < 1e-6)
    return Solucion(tipologia, perfil, g, d, mejor, n, techo, piso)


def optimizar_todas(caso: CasoMuro, perfiles=("lineal", "parabolico")) -> dict[str, Solucion | None]:
    """Mejor solución por tipología (mejor perfil por tipología) más la clave 'tradicional' = estándar de perfil lineal."""
    out: dict[str, Solucion | None] = {"tradicional": optimizar(caso, "estandar", "lineal")}
    for tip in TIPOLOGIAS:
        sols = [s for s in (optimizar(caso, tip, p) for p in perfiles) if s is not None]
        out[tip] = min(sols, key=lambda s: s.objetivo) if sols else None
    return out


def ahorro_frente_a_tradicional(sols: dict[str, Solucion | None]) -> dict[str, float | None]:
    """Fracción de ahorro de cada tipología frente al estándar de perfil lineal del MISMO caso (diseño pareado)."""
    ref = sols.get("tradicional")
    if ref is None:
        return {k: None for k in sols}
    return {k: (None if s is None else 1.0 - s.objetivo / ref.objetivo) for k, s in sols.items()}
