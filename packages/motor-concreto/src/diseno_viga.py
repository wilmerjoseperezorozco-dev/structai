"""Diseño de una viga de pórtico a partir de DEMANDAS de un análisis (no de una fórmula de viga simple).

Entrada: envolvente de momentos y cortantes en la cara del apoyo y en el vano (motor-analisis) + nivel de disipación
de energía (DMI, DMO, DES). Salida: refuerzo superior e inferior independientes, estribos en dos zonas (confinamiento en
2h de cada extremo y zona central) y la lista de verificaciones con su numeral. Unidades: mm, MPa, kN, kN·m.

Verificado en el corpus nsr10_chunks: C.10.5.1; C.11.2.1.1; C.11.4.5.1; C.11.4.6.3; C.11.4.7.9; C.21.3.4.1/.3/.4/.6/.8;
C.21.5.1.2/.3/.4; C.21.5.2.1/.2; C.21.5.3.1/.2; C.21.5.4.1/.2.
NO recuperado del corpus (declarado en cada verificación): C.21.3.3 (a)/(b) (cortante DMO; se aplica el equivalente del ACI 318-08
con Mn, conservador), φ de cortante 0,75, Mpr = 1,25·fy con φ = 1,0.
Supuestos: una capa de barras por cara, mismo diámetro arriba y abajo, barras continuas en toda la luz, estribos #3 o #4 de
2 ramas, sin axial, sin torsión, sin empalmes ni anclajes, sin deflexiones.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from .viga import (AREA_MM2, DIAMETRO_MM, PHI_CORTANTE, PHI_FLEXION, Materiales, Verificacion, beta1)

NIVELES = ("DMI", "DMO", "DES")
RHO_MAX = 0.025                      # C.21.3.4.3 y C.21.5.2.1
FACTOR_MPR = 1.25
BARRAS = ("4", "5", "6", "7", "8")
BARRAS_N = range(2, 9)
ESTRIBOS = ("3", "4")
PASO_S = 25.0
S_MIN = 50.0
RATIO_POS_NEG = {"DMO": 1 / 3, "DES": 1 / 2}     # C.21.3.4.4 y C.21.5.2.2 (cara del nudo)
RATIO_VANO = {"DMO": 1 / 5, "DES": 1 / 4}        # idem, cualquier sección de la luz


@dataclass(frozen=True)
class DemandaViga:
    luz_libre_m: float       # ln entre caras de columna
    M_neg_apoyo: float       # kN·m, |hogging| máximo en la cara de cualquier apoyo
    M_pos_apoyo: float       # kN·m, sagging máximo en la cara del apoyo (inversión por sismo)
    M_pos_vano: float        # kN·m, sagging máximo en la luz
    V_max: float             # kN, |V| máximo de las combinaciones del análisis en la cara del apoyo
    V_gravedad: float        # kN, |V| de 1.2D+1.0L en la cara (para Ve por capacidad)
    w_grav: float            # kN/m, 1.2D+1.0L sobre la viga (para Ve por capacidad)
    V_centro: float          # kN, |V| máximo del análisis a 2h de la cara (zona central)


@dataclass(frozen=True)
class DisenoViga:
    b: float
    h: float
    dia: str
    n_sup: int
    n_inf: int
    estribo_dia: str
    s_conf: float
    s_centro: float
    n_estribos: int
    nivel: str
    verificaciones: tuple[Verificacion, ...]

    @property
    def cumple(self) -> bool:
        return all(v.cumple for v in self.verificaciones)


def _d(h: float, dia: str, est: str, rec: float) -> float:
    return h - rec - DIAMETRO_MM[est] - DIAMETRO_MM[dia] / 2


def _mn_nominal(As: float, b: float, d: float, fc: float, fy: float) -> tuple[float, float]:
    """(Mn kN·m con la resistencia fy dada, εt)."""
    a = As * fy / (0.85 * fc * b)
    c = a / beta1(fc)
    eps = 0.003 * (d - c) / c
    return As * fy * (d - a / 2) / 1e6, eps


def _n_max(b: float, dia: str, est: str, rec: float) -> int:
    db = DIAMETRO_MM[dia]
    libre_ancho = b - 2 * (rec + DIAMETRO_MM[est])
    sep = max(db, 25.0)
    return int((libre_ancho + sep) // (db + sep))


def _n_min_para(M: float, b: float, d: float, dia: str, m: Materiales, n_hasta: int) -> Optional[int]:
    """Menor número de barras con φMn ≥ M, As ≥ As,mín (C.10.5.1) y εt ≥ 0,005; None si no cabe."""
    for n in BARRAS_N:
        if n > n_hasta:
            return None
        As = n * AREA_MM2[dia]
        mn, eps = _mn_nominal(As, b, d, m.fc, m.fy)
        as_min = max(math.sqrt(m.fc) / (4 * m.fy), 1.4 / m.fy) * b * d
        if PHI_FLEXION * mn >= M and As >= as_min and eps >= 0.005:
            return n
    return None


def _s_redondeo(s: float) -> float:
    return max(S_MIN, math.floor(s / PASO_S) * PASO_S)


def contar_estribos(ln_mm: float, h: float, s_conf: float, s_centro: float, sismico: bool) -> int:
    """Número de estribos de una viga de luz libre ln: confinamiento en 2h de cada extremo (primero a 50 mm) + zona central."""
    if not sismico:
        return math.ceil(ln_mm / s_centro) + 1
    len_conf = min(2 * h, ln_mm / 2)
    n_conf = 2 * (math.ceil((len_conf - 50.0) / s_conf) + 1)
    return n_conf + max(0, math.ceil((ln_mm - 2 * len_conf) / s_centro) - 1)


def disenar(b: float, h: float, dem: DemandaViga, nivel: str, m: Materiales, *, recubrimiento: float = 40.0,
            columna_c1: Optional[float] = None, columna_c2: Optional[float] = None) -> list[DisenoViga]:
    """Diseños factibles (uno por diámetro de barra y estribo viable) para la sección b×h; vacío si ninguno cumple.

    columna_c1: dimensión de la columna paralela a la viga; columna_c2: perpendicular (para C.21.5.1.4).
    """
    if nivel not in NIVELES:
        raise ValueError(f"nivel '{nivel}' no válido: {NIVELES}")
    sismico = nivel in ("DMO", "DES")
    ln_mm = dem.luz_libre_m * 1000
    geom: list[Verificacion] = []
    if nivel == "DMO":
        geom.append(Verificacion("Ancho b ≥ 200 mm", 200.0, b, "mm", b >= 200.0, "C.21.3.4.1"))
    if nivel == "DES":
        bmin = min(0.3 * h, 250.0)
        geom.append(Verificacion("Ancho b ≥ mín(0,3h; 250 mm)", bmin, b, "mm", b >= bmin, "C.21.5.1.3"))
        if columna_c1 and columna_c2:
            bmax = columna_c2 + 2 * min(columna_c2, 0.75 * columna_c1)
            geom.append(Verificacion("Ancho b ≤ c2 + 2·mín(c2; 0,75·c1)", b, bmax, "mm", b <= bmax, "C.21.5.1.4",
                                     "demanda=b, capacidad=bmax"))
    if any(not g.cumple for g in geom):
        return []

    salida: list[DisenoViga] = []
    for dia in BARRAS:
        for est in ESTRIBOS:
            d = _d(h, dia, est, recubrimiento)
            if d <= 0 or (sismico and ln_mm < 4 * d):
                continue
            n_cap = _n_max(b, dia, est, recubrimiento)
            n_sup = _n_min_para(dem.M_neg_apoyo, b, d, dia, m, n_cap)
            n_inf = _n_min_para(max(dem.M_pos_vano, dem.M_pos_apoyo), b, d, dia, m, n_cap)
            if n_sup is None or n_inf is None:
                continue
            A1 = AREA_MM2[dia]
            if sismico:
                # relación momento positivo / negativo en la cara y mínimo en cualquier sección (todas las barras continuas)
                k_cara, k_luz = RATIO_POS_NEG[nivel], RATIO_VANO[nivel]
                mn_s = _mn_nominal(n_sup * A1, b, d, m.fc, m.fy)[0]
                while n_inf <= n_cap and _mn_nominal(n_inf * A1, b, d, m.fc, m.fy)[0] < k_cara * mn_s:
                    n_inf += 1
                while n_sup <= n_cap and _mn_nominal(n_sup * A1, b, d, m.fc, m.fy)[0] < k_luz * _mn_nominal(n_inf * A1, b, d, m.fc, m.fy)[0]:
                    n_sup += 1
                if n_sup > n_cap or n_inf > n_cap:
                    continue
                if max(n_sup, n_inf) * A1 / (b * d) > RHO_MAX:
                    continue
            d_est = DIAMETRO_MM[est]
            Av = 2 * AREA_MM2[est]
            raiz = math.sqrt(m.fc)
            vc = 0.17 * raiz * b * d / 1000
            if nivel == "DES":
                fy_pr = FACTOR_MPR * m.fy
                m_a = _mn_nominal(n_sup * A1, b, d, m.fc, fy_pr)[0]
                m_b = _mn_nominal(n_inf * A1, b, d, m.fc, fy_pr)[0]
            elif nivel == "DMO":
                m_a, m_b = _mn_nominal(n_sup * A1, b, d, m.fc, m.fy)[0], _mn_nominal(n_inf * A1, b, d, m.fc, m.fy)[0]
            else:
                m_a = m_b = 0.0
            v_sismo = (m_a + m_b) / dem.luz_libre_m if sismico else 0.0
            ve = v_sismo + dem.w_grav * dem.luz_libre_m / 2 if sismico else dem.V_max
            v_diseno_ext = max(ve, dem.V_max)
            vc_ext = 0.0 if (nivel == "DES" and v_sismo >= 0.5 * ve) else vc
            vs_req_ext = max(0.0, v_diseno_ext / PHI_CORTANTE - vc_ext)
            vs_max = 0.66 * raiz * b * d / 1000
            if vs_req_ext > vs_max:
                continue
            fyt = m.fyt
            s_shear_ext = math.inf if vs_req_ext == 0 else Av * fyt * d / (vs_req_ext * 1000)
            av_min_s = Av * fyt / max(0.062 * raiz * b, 0.35 * b)         # s máx por Av,mín (C.11.4.6.3)
            if sismico:
                s_conf_norma = min(d / 4, 8 * DIAMETRO_MM[dia], 24 * d_est, 300.0)         # C.21.5.3.2 / C.21.3.4.6
                s_conf = _s_redondeo(min(s_conf_norma, s_shear_ext, av_min_s))
                if s_conf > s_conf_norma + 1e-9 or s_conf < S_MIN:
                    continue
                v_centro = max(dem.V_centro, ve - dem.w_grav * 2 * h / 1000) if nivel != "DMI" else dem.V_centro
                vs_req_c = max(0.0, v_centro / PHI_CORTANTE - vc)
                s_shear_c = math.inf if vs_req_c == 0 else Av * fyt * d / (vs_req_c * 1000)
                s_max_c = min(d / 2, 600.0) if vs_req_c <= 0.33 * raiz * b * d / 1000 else min(d / 4, 300.0)
                s_centro = _s_redondeo(min(s_max_c, s_shear_c, av_min_s, d / 2))
                if s_centro < S_MIN or vs_req_c > vs_max:
                    continue
                n_est = contar_estribos(ln_mm, h, s_conf, s_centro, True)
            else:
                s_max = min(d / 2, 600.0) if vs_req_ext <= 0.33 * raiz * b * d / 1000 else min(d / 4, 300.0)
                s_conf = s_centro = _s_redondeo(min(s_max, s_shear_ext, av_min_s))
                if s_centro < S_MIN:
                    continue
                n_est = contar_estribos(ln_mm, h, s_centro, s_centro, False)
            v: list[Verificacion] = list(geom)
            v.extend(_verificaciones(b, h, d, dia, est, n_sup, n_inf, s_conf, s_centro, dem, nivel, m, ve, v_sismo,
                                     vc_ext, vc, Av, sismico))
            salida.append(DisenoViga(b, h, dia, n_sup, n_inf, est, s_conf, s_centro, n_est, nivel, tuple(v)))
    return [x for x in salida if x.cumple]


def _verificaciones(b, h, d, dia, est, n_sup, n_inf, s_conf, s_centro, dem, nivel, m, ve, v_sismo, vc_ext, vc, Av, sismico):
    A1 = AREA_MM2[dia]
    v: list[Verificacion] = []
    for nombre, n, M in (("superior", n_sup, dem.M_neg_apoyo), ("inferior", n_inf, max(dem.M_pos_vano, dem.M_pos_apoyo))):
        mn, eps = _mn_nominal(n * A1, b, d, m.fc, m.fy)
        v.append(Verificacion(f"Flexión {nombre} φMn ≥ Mu", M, PHI_FLEXION * mn, "kN·m", PHI_FLEXION * mn >= M, "C.10.2 / C.9.3.2.1"))
        v.append(Verificacion(f"εt ≥ 0,005 ({nombre})", 0.005, eps, "-", eps >= 0.005, "C.10.3.4"))
        rho = n * A1 / (b * d)
        rho_min = max(math.sqrt(m.fc) / (4 * m.fy), 1.4 / m.fy)
        v.append(Verificacion(f"ρ ≥ ρmín ({nombre})", rho_min, rho, "-", rho >= rho_min, "C.10.5.1"))
        if sismico:
            v.append(Verificacion(f"ρ ≤ 0,025 ({nombre})", rho, RHO_MAX, "-", rho <= RHO_MAX, "C.21.3.4.3 / C.21.5.2.1"))
    if sismico:
        v.append(Verificacion("≥ 2 barras continuas arriba y abajo", 2, min(n_sup, n_inf), "barras", min(n_sup, n_inf) >= 2,
                              "C.21.3.4.3 / C.21.5.2.1"))
        v.append(Verificacion("Luz libre ln ≥ 4d", 4 * d / 1000, dem.luz_libre_m, "m", dem.luz_libre_m * 1000 >= 4 * d, "C.21.5.1.2"))
        mn_s = _mn_nominal(n_sup * A1, b, d, m.fc, m.fy)[0]
        mn_i = _mn_nominal(n_inf * A1, b, d, m.fc, m.fy)[0]
        k1, k2 = RATIO_POS_NEG[nivel], RATIO_VANO[nivel]
        c1, c2 = ("C.21.3.4.4", "C.21.3.4.4") if nivel == "DMO" else ("C.21.5.2.2", "C.21.5.2.2")
        v.append(Verificacion(f"Mn⁺ ≥ {k1:.2f}·Mn⁻ en la cara", k1 * mn_s, mn_i, "kN·m", mn_i >= k1 * mn_s, c1))
        mayor = max(mn_s, mn_i)
        v.append(Verificacion(f"Mn en cualquier sección ≥ {k2:.2f}·Mn,máx", k2 * mayor, min(mn_s, mn_i), "kN·m",
                              min(mn_s, mn_i) >= k2 * mayor, c2))
        s_norma = min(d / 4, 8 * DIAMETRO_MM[dia], 24 * DIAMETRO_MM[est], 300.0)
        v.append(Verificacion("s confinamiento ≤ mín(d/4; 8db; 24dest; 300) en 2h", s_conf, s_norma, "mm", s_conf <= s_norma,
                              "C.21.5.3.2 / C.21.3.4.6"))
        fi = "C.21.5.4.1/.2" if nivel == "DES" else "C.21.3.3"
        nota = "Mpr=1,25fy no verificado en el corpus (φ=0,75 sí, C.9.3.2.3)" if nivel == "DES" else "C.21.3.3(a)/(b) no recuperado; se usa Mn (ACI 318-08)"
        s_cap = Av * m.fyt * d / s_conf / 1000
        phi_vn = PHI_CORTANTE * (vc_ext + s_cap)
        v.append(Verificacion("Cortante por capacidad φ(Vc+Vs) ≥ Ve (zona de confinamiento)", max(ve, dem.V_max), phi_vn, "kN",
                              phi_vn >= max(ve, dem.V_max), fi, nota))
        s_cap_c = Av * m.fyt * d / s_centro / 1000
        v_centro = max(dem.V_centro, ve - dem.w_grav * 2 * h / 1000)
        phi_vn_c = PHI_CORTANTE * (vc + s_cap_c)
        v.append(Verificacion("Cortante zona central φ(Vc+Vs) ≥ Vu", v_centro, phi_vn_c, "kN", phi_vn_c >= v_centro, "C.11.2.1.1 / C.11.4.7.2"))
        v.append(Verificacion("s zona central ≤ d/2", s_centro, d / 2, "mm", s_centro <= d / 2 + 1e-9, "C.21.3.4.8 / C.11.4.5.1"))
    else:
        phi_vn = PHI_CORTANTE * (vc + Av * m.fyt * d / s_centro / 1000)
        v.append(Verificacion("Cortante φ(Vc+Vs) ≥ Vu", dem.V_max, phi_vn, "kN", phi_vn >= dem.V_max, "C.11.2.1.1 / C.11.4.7.2"))
    return v
