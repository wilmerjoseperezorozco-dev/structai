"""Tirantes preesforzados (anclajes al terreno) del muro de contención: dimensionamiento del anclaje y de sus cantidades por metro de muro.

El efecto sobre el equilibrio (componente horizontal que se opone al empuje y componente vertical que carga la base) está en `muro_contencion.fuerza_anclaje`
y `_resolver`. Aquí se dimensiona lo que el equilibrio exige: cordones, longitud libre, longitud fija y cantidades.

HIPÓTESIS de investigación (nada de esto viene de la NSR-10 del corpus; el título H solo menciona anclajes de pasada y no da criterios de diseño):
cordón de 15,2 mm grado 270 (fpu 1860 MPa, 140 mm²) con esfuerzo de servicio ≤ 0,60 fpu; adherencia última lechada-suelo τ SUPUESTA, FS 2,0 sobre la longitud fija;
la longitud libre llega hasta la superficie de falla de Rankine (45° + φ/2 desde el extremo del talón) más 1,5 m y nunca menos de 4,5 m; la fija nunca menos de 3 m;
perforación de 150 mm; separación horizontal entre tirantes constante (`SEP_ANCLAJES_M`). NO se verifica: capacidad de la pantalla para recibir la carga puntual
(punzonamiento, flexión local), fluencia/relajación del preesfuerzo, corrosión, ensayos de recepción, estabilidad general del conjunto muro-terreno-anclaje.
La reducción del momento de la pantalla por el tirante NO se aprovecha (conservador): la pantalla se diseña como si el tirante no existiera.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .economia_concreto import Economia
from .muro_contencion import GeometriaMuro, Relleno, fuerza_anclaje

FPU_MPA = 1860.0
AREA_CORDON_MM2 = 140.0
ESFUERZO_SERVICIO = 0.60
N_CORDONES_MAX = 12
SEP_ANCLAJES_M = 2.5
TAU_ADHERENCIA_KPA = 150.0           # SUPUESTO: arena densa / grava arcillosa inyectada
D_PERFORACION_M = 0.15
FS_ADHERENCIA = 2.0
L_LIBRE_MIN_M, L_FIJA_MIN_M, L_FIJA_MAX_M = 4.5, 3.0, 12.0
MARGEN_SUPERFICIE_FALLA_M = 1.5
CEMENTO_LECHADA_KG_M3 = 1250.0
DENSIDAD_ACERO_KG_M3 = 7850.0


@dataclass(frozen=True)
class DisenoAnclaje:
    cumple: bool
    motivos: tuple[str, ...]
    fuerza_kn_m: float            # fuerza axial de servicio por metro de muro
    fuerza_ancla_kn: float        # fuerza axial de servicio de cada tirante
    n_cordones: int
    l_libre_m: float
    l_fija_m: float
    kg_cordon_m: float            # kg de cordón por metro de muro
    cemento_kg_m: float           # kg de cemento de la lechada por metro de muro
    longitud_perforada_m_m: float  # metros de perforación por metro de muro


def disenar_anclaje(g: GeometriaMuro, r: Relleno) -> DisenoAnclaje | None:
    if not g.tiene_anclaje:
        return None
    _, _, x_a, y_a = fuerza_anclaje(g)
    ang = math.radians(g.anc_incl_deg)
    af = math.radians(45.0 + r.phi_deg / 2.0)
    B = g.ancho_base
    x_int = (y_a + x_a * math.tan(ang) + B * math.tan(af)) / (math.tan(ang) + math.tan(af))
    y_int = (x_int - B) * math.tan(af)
    f_ancla = g.anc_fuerza_kn_m * SEP_ANCLAJES_M
    cap_cordon = ESFUERZO_SERVICIO * FPU_MPA * AREA_CORDON_MM2 / 1000.0
    n = math.ceil(f_ancla / cap_cordon - 1e-9)
    l_libre = max((x_int - x_a) / math.cos(ang) + MARGEN_SUPERFICIE_FALLA_M, L_LIBRE_MIN_M)
    l_fija = max(f_ancla * FS_ADHERENCIA / (math.pi * D_PERFORACION_M * TAU_ADHERENCIA_KPA), L_FIJA_MIN_M)
    motivos = []
    if y_int < 0.0 or x_int < B:
        motivos.append("anclaje: la inclinación lleva el tirante por debajo de la zapata antes de cruzar la superficie de falla")
    if n > N_CORDONES_MAX:
        motivos.append(f"anclaje: {n} cordones > {N_CORDONES_MAX} por tirante")
    if l_fija > L_FIJA_MAX_M:
        motivos.append(f"anclaje: longitud fija requerida {l_fija:.1f} m > {L_FIJA_MAX_M:.0f} m (τ = {TAU_ADHERENCIA_KPA:.0f} kPa supuesta)")
    largo = l_libre + l_fija
    return DisenoAnclaje(not motivos, tuple(motivos), g.anc_fuerza_kn_m, f_ancla, n, l_libre, l_fija,
                         n * AREA_CORDON_MM2 * 1e-6 * largo * DENSIDAD_ACERO_KG_M3 / SEP_ANCLAJES_M,
                         math.pi / 4.0 * D_PERFORACION_M**2 * largo * CEMENTO_LECHADA_KG_M3 / SEP_ANCLAJES_M, largo / SEP_ANCLAJES_M)


def costo_co2_anclaje(a: DisenoAnclaje, eco: Economia) -> tuple[float, float]:
    """(COP, kg CO₂e) por metro de muro: perforación e inyección + cabezas + cordón; cordón y cemento de la lechada para el CO₂."""
    costo = a.longitud_perforada_m_m * eco.p_perforacion_m + eco.p_cabeza_anclaje / SEP_ANCLAJES_M + a.kg_cordon_m * eco.p_acero * eco.factor_precio_cordon
    return costo, a.kg_cordon_m * eco.fe_acero + a.cemento_kg_m * eco.fe_cemento
