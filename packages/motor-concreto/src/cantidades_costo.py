"""Cantidades de obra, costo APU y CO₂ de vigas y columnas (módulo común con zapata, pedestal y muro).

Antes de este módulo solo la zapata con pedestal y el muro de contención tenían costo y CO₂; viga y columna entregaban refuerzo sin cantidades.
Todo lo de abajo son HIPÓTESIS de cuantificación declaradas (sin traslapos, sin ganchos suplementarios, sin figurado real):
- Barras longitudinales de la viga: luz libre + 40 diámetros de anclaje por extremo.
- Barras de la columna: altura del elemento, sin traslapos ni anclaje en la cimentación o en el nudo.
- Estribo: perímetro del núcleo (b − 2·rec, h − 2·rec) más dos ganchos de 135° de max(6·db, 75 mm); sin amarres suplementarios.
- Encofrado: viga = fondo + 2 caras (la losa cubre la cara superior); columna = 4 caras.
Estas simplificaciones subestiman el acero real entre 5 y 15 %; el optimizador las usa para comparar alternativas, no para presupuestar.
"""
from __future__ import annotations

from dataclasses import dataclass

from .columna import DisenoColumna
from .diseno_viga import DisenoViga
from .economia_concreto import Economia, co2_m3, costo_m3
from .viga import AREA_MM2, DIAMETRO_MM

DENSIDAD_ACERO_KG_M3 = 7850.0
ANCLAJE_DIAMETROS = 40.0
GANCHO_MIN_MM = 75.0
GANCHO_DIAMETROS = 6.0


@dataclass(frozen=True)
class Cantidades:
    volumen_m3: float
    acero_kg: float
    encofrado_m2: float

    def __add__(self, o: "Cantidades") -> "Cantidades":
        return Cantidades(self.volumen_m3 + o.volumen_m3, self.acero_kg + o.acero_kg, self.encofrado_m2 + o.encofrado_m2)


def _kg(area_mm2: float, largo_m: float) -> float:
    return area_mm2 * 1e-6 * largo_m * DENSIDAD_ACERO_KG_M3


def longitud_estribo_m(b_mm: float, h_mm: float, rec_mm: float, estribo: str) -> float:
    db = DIAMETRO_MM[estribo]
    gancho = max(GANCHO_DIAMETROS * db, GANCHO_MIN_MM)
    return (2.0 * (b_mm - 2.0 * rec_mm) + 2.0 * (h_mm - 2.0 * rec_mm) + 2.0 * gancho) / 1000.0


def cantidades_viga(d: DisenoViga, luz_libre_m: float, recubrimiento_mm: float = 40.0) -> Cantidades:
    ancl = 2.0 * ANCLAJE_DIAMETROS * DIAMETRO_MM[d.dia] / 1000.0
    longitudinal = _kg(AREA_MM2[d.dia], luz_libre_m + ancl) * (d.n_sup + d.n_inf)
    estribos = _kg(AREA_MM2[d.estribo_dia], longitud_estribo_m(d.b, d.h, recubrimiento_mm, d.estribo_dia)) * d.n_estribos
    return Cantidades(d.b * d.h * 1e-6 * luz_libre_m, longitudinal + estribos, (d.b + 2.0 * d.h) * 1e-3 * luz_libre_m)


def cantidades_columna(d: DisenoColumna, altura_m: float, recubrimiento_mm: float = 40.0) -> Cantidades:
    longitudinal = _kg(AREA_MM2[d.dia], altura_m) * d.n_barras
    estribos = _kg(AREA_MM2[d.estribo], longitud_estribo_m(d.b, d.h, recubrimiento_mm, d.estribo)) * d.n_estribos
    return Cantidades(d.b * d.h * 1e-6 * altura_m, longitudinal + estribos, 2.0 * (d.b + d.h) * 1e-3 * altura_m)


def costo_co2(q: Cantidades, fc: float, eco: Economia | None = None, ceniza: float = 0.0) -> tuple[float, float]:
    """(COP, kg CO₂e) de unas cantidades con la misma mezcla, precios y factores que la zapata y el muro. `ceniza` = fracción de reemplazo x."""
    e = eco or Economia()
    cop = q.volumen_m3 * costo_m3(fc, ceniza, e.p_ceniza, e.mult_concreto) + q.acero_kg * e.p_acero + q.encofrado_m2 * e.p_encofrado
    co2 = q.volumen_m3 * co2_m3(fc, ceniza, e.fe_cemento) + q.acero_kg * e.fe_acero
    return cop, co2
