"""Requisitos sísmicos de vigas de pórtico (NSR-10 C.21.5), aplicados como cota conservadora a DMO y DES.

Verificado contra el corpus: C.21.5.1.2, C.21.5.1.3, C.21.5.2.1, C.21.5.2.2, C.21.5.3.1, C.21.5.3.2, C.21.5.4.1, C.21.5.4.2.
NO verificado / aproximado (declarado):
  - (Mpr = 1,25·fy con φ = 1,0: VERIFICADO en la notación C.2; C.21.5.4.1/.2 recuperados en la etapa 1.)
  - DMO tiene sus propios requisitos (C.21.3.4); aquí se exige lo de DES, que es más estricto, como cota conservadora.
  - Refuerzo simétrico (igual superior e inferior): cumple C.21.5.2.2 y simplifica; puede sobredimensionar.
  - Estribos uniformes en toda la luz con el espaciamiento de confinamiento (conservador: el código lo exige solo en 2h).
  - No se revisan empalmes (C.21.5.2.3), nudos (C.21.7) ni deflexión.
  - La demanda sísmica de flexión NO se calcula aquí: llega del análisis del pórtico como `momento_apoyo` (envolvente
    en la cara del nudo, ya con las combinaciones B.2.4-5/-7). Sin ella solo se verifican detallado y cortante por capacidad.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .viga import (DIAMETRO_MM, PHI_CORTANTE, Cargas, Materiales, Seccion, Verificacion,
                   momento_nominal, peso_propio_kn_m)

FACTOR_FY_PROBABLE = 1.25
RHO_MAX_SISMICO = 0.025       # C.21.5.2.1
SEPARACION_MAX_ABS_MM = 300.0  # C.21.5.3.2(d)


@dataclass(frozen=True)
class DemandaSismica:
    luz_libre_m: float                       # ln, entre caras de apoyo
    momento_apoyo_kn_m: Optional[float] = None   # envolvente del análisis en la cara del nudo; None = no disponible


def momento_probable(s: Seccion, m: Materiales) -> float:
    """Mpr en kN·m con 1,25·fy y φ = 1."""
    fy = FACTOR_FY_PROBABLE * m.fy
    a = s.As * fy / (0.85 * m.fc * s.b)
    return s.As * fy * (s.d - a / 2) / 1e6


def verificar_sismico(s: Seccion, m: Materiales, c: Cargas, dem: DemandaSismica) -> list[Verificacion]:
    ln = dem.luz_libre_m
    v: list[Verificacion] = []

    v.append(Verificacion("Luz libre ln ≥ 4d", 4 * s.d / 1000, ln, "m", ln >= 4 * s.d / 1000, "C.21.5.1.2"))
    bmin = min(0.3 * s.h, 250.0)
    v.append(Verificacion("Ancho b ≥ mín(0,3h; 250 mm)", bmin, s.b, "mm", s.b >= bmin, "C.21.5.1.3"))

    rho = s.As / (s.b * s.d)
    v.append(Verificacion("ρ ≤ 0,025", rho, RHO_MAX_SISMICO, "-", rho <= RHO_MAX_SISMICO, "C.21.5.2.1"))
    n_inf, n_sup = s.barras_n, s.barras_sup_n
    v.append(Verificacion("≥ 2 barras continuas arriba y abajo", 2, min(n_inf, n_sup), "barras",
                          n_inf >= 2 and n_sup >= 2, "C.21.5.2.1", "refuerzo simétrico asumido (barras_sup_n)"))
    v.append(Verificacion("Mto. positivo ≥ ½ mto. negativo en la cara", 0.5 * n_sup, n_inf, "barras",
                          n_inf >= 0.5 * n_sup, "C.21.5.2.2", "mismo diámetro: proporcional al número de barras"))

    # Estribos de confinamiento (C.21.5.3.2): s ≤ mín(d/4; 8·db_menor; 24·d_estribo; 300)
    db, dst = DIAMETRO_MM[s.barras_dia], DIAMETRO_MM[s.estribo_dia]
    s_conf = min(s.d / 4, 8 * db, 24 * dst, SEPARACION_MAX_ABS_MM)
    v.append(Verificacion("Separación de confinamiento s ≤ mín(d/4; 8db; 24dest; 300)", s.estribo_s, s_conf, "mm",
                          s.estribo_s <= s_conf, "C.21.5.3.2", "aplicada en toda la luz (conservador)"))

    # Cortante por capacidad (C.21.5.4.1): Mpr en ambas caras con signo opuesto + cargas gravitacionales mayoradas
    mpr = momento_probable(s, m)
    wu_grav = 1.2 * (c.muerta + peso_propio_kn_m(s.b, s.h)) + 1.0 * c.viva    # B.2.4-5 sin E
    v_sismo = 2 * mpr / ln
    v_grav = wu_grav * ln / 2
    ve = v_sismo + v_grav
    # C.21.5.4.2: Vc = 0 si el cortante sísmico ≥ la mitad del máximo requerido (y Pu < Ag·f'c/20, sin axial aquí)
    raiz = math.sqrt(m.fc)
    vc = 0.0 if v_sismo >= 0.5 * ve else 0.17 * raiz * s.b * s.d / 1000
    vs = s.Av * m.fyt * s.d / s.estribo_s / 1000
    phi_vn = PHI_CORTANTE * (vc + vs)
    v.append(Verificacion("Cortante por capacidad φ(Vc+Vs) ≥ Ve", ve, phi_vn, "kN", phi_vn >= ve,
                          "C.21.5.4.1 / C.21.5.4.2", "Mpr=1,25fy con φ=1,0 verificado (notación C.2); φ cortante 0,75 C.9.3.2.3"))

    if dem.momento_apoyo_kn_m is not None:
        phi_mn, _, _ = momento_nominal(s, m)
        v.append(Verificacion("Flexión en el apoyo φMn ≥ M del análisis", dem.momento_apoyo_kn_m, phi_mn, "kN·m",
                              phi_mn >= dem.momento_apoyo_kn_m, "B.2.4-5/-7 + C.10.2", "demanda proviene del análisis del pórtico"))
    return v
