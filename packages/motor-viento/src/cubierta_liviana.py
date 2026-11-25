"""Cubierta liviana (lámina sobre correas apoyadas en vigas) bajo succión de viento, componentes y revestimientos
(NSR-10 B.6.5.12.4, Figs. B.6.5-8B a 8D), v1 (#292).

Por zona de cubierta (1, 2, 3 y aleros) verifica, con 0,9D + 1,6W (B.2.4-6) por defecto:
  1. fijación lámina–correa: Tu = (1,6·|p| − 0,9·peso)·A_trib ≤ φRn_fijación, con A_trib = s_correas · s_fijaciones
     (el área efectiva de una fijación es su área aferente);
  2. correa a flexión invertida (ala inferior en compresión): Mu = wu·L²/8 ≤ φMn_inversa (apoyo simple, conservador
     frente a la continuidad), wu = (1,6·|p| − 0,9·peso)·s_correas, con GCp en el área efectiva máx(L·s, L²/3);
  3. anclaje correa–viga: Ru = wu·L (apoyo interior de dos vanos simples) ≤ φRn_anclaje.
p = qh·(GCp − GCpi) con la succión más desfavorable; en aleros, GCp ya incluye las dos caras y no se suma GCpi.

Las capacidades φRn y φMn son DATOS que declara el usuario (fabricante, ensayo o cálculo aparte): el motor no calcula
la resistencia de tornillos, ganchos, correas de acero formado en frío ni su pandeo lateral-torsional.
No verifica: la lámina misma (flexión entre correas), el desgarre de la lámina alrededor de la fijación, la fatiga por
ciclos de viento, la corrosión ni la conexión de las vigas de concreto hacia abajo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from . import b6


@dataclass(frozen=True)
class CubiertaLiviana:
    theta_deg: float                     # pendiente
    peso_kpa: float                      # peso propio de lámina + correas (favorable, se factoriza por factor_d)
    separacion_correas_m: float
    luz_correas_m: float                 # distancia entre vigas o cerchas que soportan las correas
    separacion_fijaciones_m: float       # a lo largo de la correa
    phi_rn_fijacion_kn: float            # capacidad de diseño a extracción/arrancamiento de una fijación
    phi_mn_correa_inversa_knm: float     # capacidad de diseño de la correa con el ala inferior en compresión
    phi_rn_anclaje_kn: float             # capacidad de diseño del anclaje correa–viga
    alero_m: float = 0.0

    def __post_init__(self):
        if not 0.0 <= self.theta_deg <= 45.0:
            raise ValueError("θ entre 0° y 45°")
        if min(self.separacion_correas_m, self.luz_correas_m, self.separacion_fijaciones_m) <= 0:
            raise ValueError("separaciones y luz positivas")
        if self.peso_kpa < 0 or self.alero_m < 0:
            raise ValueError("peso y alero no negativos")
        if min(self.phi_rn_fijacion_kn, self.phi_mn_correa_inversa_knm, self.phi_rn_anclaje_kn) <= 0:
            raise ValueError("capacidades positivas")


@dataclass(frozen=True)
class RevisionZona:
    zona: str
    p_kpa: float                         # presión neta de succión (negativa) para la fijación
    tu_fijacion_kn: float
    mu_correa_knm: float
    ru_anclaje_kn: float
    s_max_fijaciones_m: float            # separación máxima de fijaciones que cumple
    cumple: bool


def succion(qh_kpa: float, zona: str, area_m2: float, theta_deg: float, gcpi: float, alero: bool = False) -> float:
    """Presión neta de succión (negativa), kN/m²."""
    gcp = b6.gcp_cubierta(zona, area_m2, theta_deg, "-", alero=alero)
    return qh_kpa * gcp if alero else b6.presiones_netas(qh_kpa, gcp, gcpi)[1]


def separacion_maxima(p_kpa: float, s_correas_m: float, phi_rn_kn: float, peso_kpa: float = 0.0,
                      factor_w: float = 1.6, factor_d: float = 0.9) -> float:
    """Separación máxima de fijaciones a lo largo de la correa: φRn / ((fw·|p| − fd·peso)·s_correas). inf si no hay
    levantamiento neto."""
    neta = factor_w * abs(p_kpa) - factor_d * peso_kpa
    return math.inf if neta <= 0 else phi_rn_kn / (neta * s_correas_m)


def verificar(qh_kpa: float, c: CubiertaLiviana, gcpi: float = b6.GCPI["cerrado"], factor_w: float = 1.6,
              factor_d: float = 0.9) -> list[RevisionZona]:
    s, L = c.separacion_correas_m, c.luz_correas_m
    a_fij = s * c.separacion_fijaciones_m
    a_corr = max(L * s, L * L / 3.0)
    zonas = [("1", False), ("2", False), ("3", False)] + ([("2", True), ("3", True)] if c.alero_m > 0 else [])
    out = []
    for z, alero in zonas:
        p_f = succion(qh_kpa, z, a_fij, c.theta_deg, gcpi, alero)
        p_c = succion(qh_kpa, z, a_corr, c.theta_deg, gcpi, alero)
        tu = max(factor_w * abs(p_f) - factor_d * c.peso_kpa, 0.0) * a_fij
        wu = max(factor_w * abs(p_c) - factor_d * c.peso_kpa, 0.0) * s
        mu, ru = wu * L * L / 8.0, wu * L
        smax = separacion_maxima(p_f, s, c.phi_rn_fijacion_kn, c.peso_kpa, factor_w, factor_d)
        ok = tu <= c.phi_rn_fijacion_kn and mu <= c.phi_mn_correa_inversa_knm and ru <= c.phi_rn_anclaje_kn
        out.append(RevisionZona(("alero " if alero else "") + z, p_f, tu, mu, ru, smax, ok))
    return out
