"""Columna rectangular de concreto reforzado a flexo-compresión uniaxial (en el plano del pórtico) con detallado DMI/DMO/DES.

Diagrama de interacción por compatibilidad de deformaciones (C.10.2, C.10.3): bloque rectangular de Whitney, εcu = 0,003,
acero elastoplástico (Es = 200 GPa), barras perimetrales con n barras por cara (4n − 4 en total). Unidades: mm, MPa, kN, kN·m;
compresión positiva. Todo el chequeo contra las demandas es vectorial (np.interp sobre todas las combinaciones y columnas).

Verificado en el corpus nsr10_chunks (2026-11-08):
  C.10.2/C.10.3.3/.4 (límites 0,002 y 0,005), C.9.3.2.2 (φ = 0,65 con estribos, hasta 0,90 lineal en 0,002–0,005), C.9.3.2.3
  (φ cortante = 0,75), C.10.9.1/.2 (1 %–4 %, mínimo 4 barras), C.10.10.1.1/.2 y C.10-6 (kℓu/r ≤ 22, r = 0,3·h),
  C.21.6.1.1/.2 (≥ 300 mm y relación ≥ 0,4, DES), C.21.6.2.2 (ΣMnc ≥ 1,2·ΣMnb), C.21.6.3.1 (1 %–4 %), C.21.6.4.1 (ℓo ≥ máx(h; ℓn/6; 450)),
  C.21.6.4.3 y C-21-5 (so), C.21.6.4.5 (resto: ≤ mín(6db; 150)), C.21.6.5.1/.2 (Ve por Mpr; Vc = 0 si Pu < Ag·f'c/20),
  C.21.3.5.1/.2/.7/.9/.10/.11 y C-21-2/-3 (DMO: ≥ 250 mm, 1–4 %, Ash, so/2, 2·so fuera de ℓo).
NO verificado en el corpus (declarado en cada verificación):
  - Pn,max: el corpus da 0,75·φ·Po para estribos (C.10-2); el ACI 318-08 da 0,80. Se usa 0,75 (el menor, conservador).
  - Ecuaciones C.21-7/-8 (Ash en DES): no se extrajeron; se usan 0,3·(Ag/Ach − 1) y 0,09 del ACI 318-08 (= 3/2 de las
    C.21-2/-3 de DMO, que sí se verificaron: 0,2 y 0,06).
  - so en DMO: C.21.3.5.6 está truncado en el corpus; solo se recuperó 8·db. Se usa mín(8db; 24·dest; c/2; 300) del ACI.
  - Mpr = 1,25·fy con φ = 1,0; Vc = 0,17·√f'c·b·d sin beneficio de la compresión axial (conservador); espaciamiento en DMI
    mín(16db; 48·dest; c) del ACI (C.7.10.5.2 no recuperado).
  - Esbeltez: factor k por Jackson–Moreland y magnificación de momentos (δns con 0,4·Ec·Ig/(1+βdns), δs = 1/(1−Q)) son del
    ACI 318-08 (C.10.10.5–7 truncadas en el corpus); Cm = 1,0 (conservador); momento mínimo Pu(15+0,03h).
Supuestos: sección con refuerzo simétrico perimetral, recubrimiento libre al estribo, sin torsión, sin biaxial (pórtico plano).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

import numpy as np

from .viga import AREA_MM2, DIAMETRO_MM, PHI_CORTANTE, Materiales, Verificacion, beta1

ES = 200_000.0
EPS_CU = 0.003
PHI_COMPRESION = 0.65            # C.9.3.2.2(b), estribos
PHI_TRACCION = 0.90
EPS_COMPRESION = 0.002           # C.10.3.3, Grado 420
EPS_TRACCION = 0.005             # C.10.3.4
FACTOR_PN_MAX = 0.75             # C.10-2 según el corpus (ACI: 0,80) — ver docstring
RHO_MIN, RHO_MAX = 0.01, 0.04
FACTOR_MPR = 1.25
NIVELES = ("DMI", "DMO", "DES")
BARRAS_COL = ("5", "6", "7", "8")
N_CARA = (2, 3, 4, 5, 6)
ESTRIBOS_COL = ("3", "4")
PASO_S = 25.0
S_MIN = 50.0
ESBELTEZ_SIN_EFECTO = 22.0
ESBELTEZ_MAX = 100.0
PHI_RIGIDEZ = 0.75
Q_SIN_AMPLIFICAR = 0.05
RATIO_NUDO = 1.2


@dataclass(frozen=True)
class SeccionColumna:
    h: float                 # canto en el plano de flexión (mm)
    b: float                 # ancho perpendicular (mm)
    n_cara: int              # barras por cara (≥ 2)
    dia: str
    estribo: str
    recubrimiento: float = 40.0

    @property
    def n_barras(self) -> int:
        return 4 * self.n_cara - 4

    @property
    def ast(self) -> float:
        return self.n_barras * AREA_MM2[self.dia]

    @property
    def rho(self) -> float:
        return self.ast / (self.h * self.b)

    @property
    def d_borde(self) -> float:
        return self.recubrimiento + DIAMETRO_MM[self.estribo] + DIAMETRO_MM[self.dia] / 2

    @property
    def sep_barras(self) -> float:
        """Separación centro a centro entre barras adyacentes de una cara (mm), dirección del lado menor."""
        return (min(self.h, self.b) - 2 * self.d_borde) / (self.n_cara - 1)

    @property
    def separacion_libre(self) -> float:
        return self.sep_barras - DIAMETRO_MM[self.dia]


@dataclass(frozen=True)
class Curva:
    P_n: np.ndarray            # kN, nominal (creciente)
    M_n: np.ndarray            # kN·m, nominal
    Pf: np.ndarray             # kN, frontera de diseño φPn (creciente, truncada en φPn,max)
    Mf: np.ndarray             # kN·m, φMn en la frontera
    po: float                  # kN
    p_max_phi: float           # kN, φPn,max
    p_min: float               # kN, tracción pura (negativa)


@lru_cache(maxsize=16384)
def curva(h: float, b: float, n_cara: int, dia: str, estribo: str, rec: float, fc: float, fy: float, fy_factor: float = 1.0,
          con_phi: bool = True) -> Curva:
    """Curva de interacción. fy_factor = 1,25 y con_phi = False para la resistencia probable Mpr."""
    sec = SeccionColumna(h, b, n_cara, dia, estribo, rec)
    A1 = AREA_MM2[dia]
    ys = np.linspace(sec.d_borde, h - sec.d_borde, n_cara)
    idx = np.arange(n_cara)
    as_fila = np.where((idx == 0) | (idx == n_cara - 1), n_cara * A1, 2 * A1)
    fye = fy * fy_factor
    b1 = beta1(fc)
    c = np.concatenate([[1e-3 * h], np.geomspace(0.01 * h, 1.0 * h, 70), np.linspace(1.0 * h, 8.0 * h, 50)[1:]])
    eps = EPS_CU * (c[:, None] - ys[None, :]) / c[:, None]
    fs = np.clip(ES * eps, -fye, fye)
    a = np.minimum(b1 * c, h)
    dentro = ys[None, :] < a[:, None]
    fuerzas = as_fila[None, :] * (fs - 0.85 * fc * dentro)
    cc = 0.85 * fc * b * a
    Pn = (cc + fuerzas.sum(axis=1)) / 1e3
    Mn = (cc * (h / 2 - a / 2) + (fuerzas * (h / 2 - ys[None, :])).sum(axis=1)) / 1e6
    eps_t = EPS_CU * (ys[-1] - c) / c
    if con_phi:
        phi = np.clip(PHI_COMPRESION + (PHI_TRACCION - PHI_COMPRESION) * (eps_t - EPS_COMPRESION) / (EPS_TRACCION - EPS_COMPRESION),
                      PHI_COMPRESION, PHI_TRACCION)
    else:
        phi = np.ones_like(c)
    po = (0.85 * fc * (h * b - sec.ast) + fye * sec.ast) / 1e3
    p_min = -fye * sec.ast / 1e3
    Pn = np.maximum.accumulate(np.concatenate([[p_min], Pn, [po]]))
    Mn = np.concatenate([[0.0], Mn, [0.0]])
    phi = np.concatenate([[phi[0]], phi, [phi[-1]]])
    Pphi = np.maximum.accumulate(phi * Pn)
    Mphi = phi * Mn
    p_max = FACTOR_PN_MAX * (PHI_COMPRESION if con_phi else 1.0) * po
    ok = Pphi < p_max
    m_cierre = float(np.interp(p_max, Pphi, Mphi))
    Pf, Mf = np.append(Pphi[ok], p_max), np.append(Mphi[ok], m_cierre)
    return Curva(Pn, Mn, Pf, Mf, po, p_max, p_min)


def phi_mn_arr(cv: Curva, P: np.ndarray) -> np.ndarray:
    """φMn (kN·m) con φPn = P; NaN donde P > φPn,max o P < −φ·fy·Ast."""
    P = np.asarray(P, dtype=float)
    out = np.interp(P, cv.Pf, cv.Mf)
    return np.where((P > cv.p_max_phi + 1e-9) | (P < cv.Pf[0] - 1e-9), np.nan, out)


def mn_arr(cv: Curva, P: np.ndarray) -> np.ndarray:
    """Mn nominal (φ = 1) con Pn = P (C.21.6.2.2: fuerza axial mayorada); NaN fuera de rango."""
    P = np.asarray(P, dtype=float)
    out = np.interp(P, cv.P_n, cv.M_n)
    return np.where((P > cv.po + 1e-9) | (P < cv.p_min - 1e-9), np.nan, out)


def phi_mn_a(cv: Curva, Pu: float) -> float:
    return float(phi_mn_arr(cv, np.array([Pu]))[0])


def mn_a(cv: Curva, Pu: float) -> float:
    return float(mn_arr(cv, np.array([Pu]))[0])


@dataclass(frozen=True)
class DemandaColumna:
    """Demandas del análisis para TODAS las columnas (ambos extremos) y combinaciones, en el eje del nudo."""
    P: np.ndarray                 # (m,) Pu (kN, compresión +) de cada punto combinación×columna
    M_ns: np.ndarray              # (m, 2) momentos de cargas gravitacionales en los extremos (kN·m, con signo)
    M_s: np.ndarray               # (m, 2) momentos de sismo (kN·m, con signo)
    V: float                      # kN, cortante máximo de las combinaciones (ya con δs)
    V_sismo: float                # kN, cortante máximo producido solo por E (con δs)
    delta_s: float                # 1/(1−Q) máximo de los entrepisos (1,0 si Q ≤ 0,05)
    k_lu_max_m: float             # máx k·ℓu (m), k de Jackson–Moreland
    lu_min_m: float
    lu_max_m: float
    beta_dns: float               # 1,2D / (1,2D + 1,6L)
    nudos: tuple                  # ((interior: bool, p_inf (nE,), p_sup (nE,) | None), ...)
    P_sismo: Optional[np.ndarray] = None    # Pu de las combinaciones con E (para Ve); None = todas


@dataclass(frozen=True)
class DisenoColumna:
    h: float
    b: float
    n_cara: int
    dia: str
    estribo: str
    nivel: str
    s_conf: float
    s_fuera: float
    lo_mm: float
    n_estribos: int
    verificaciones: tuple[Verificacion, ...]

    @property
    def n_barras(self) -> int:
        return 4 * self.n_cara - 4

    @property
    def cumple(self) -> bool:
        return all(v.cumple for v in self.verificaciones)


def _redondeo(s: float) -> float:
    return math.floor(s / PASO_S) * PASO_S


def ash_requerido(sec: SeccionColumna, s: float, m: Materiales, nivel: str) -> float:
    """Área total de estribos por dirección (mm²). DES: ACI 318-08 (C.21-7/-8 no extraídas); DMO: C.21-2/-3 (verificadas)."""
    cov = sec.recubrimiento
    bc = max(sec.h, sec.b) - 2 * (cov + DIAMETRO_MM[sec.estribo] / 2)
    ag, ach = sec.h * sec.b, (sec.h - 2 * cov) * (sec.b - 2 * cov)
    k1, k2 = (0.3, 0.09) if nivel == "DES" else (0.2, 0.06)
    return max(k1 * s * bc * m.fc / m.fyt * (ag / ach - 1), k2 * s * bc * m.fc / m.fyt)


def so_des(hx: float) -> float:
    """C.21.6.4.3 con la ecuación C-21-5: so = 100 + (350 − hx)/3, entre 100 y 150 mm."""
    return min(150.0, max(100.0, 100.0 + (350.0 - hx) / 3.0))


def contar_estribos_col(altura_mm: float, lo: float, s_conf: float, s_fuera: float) -> int:
    if lo <= 0:
        return math.ceil(altura_mm / s_conf) + 1
    lo = min(lo, altura_mm / 2)
    n_conf = 2 * (math.ceil((lo - 25.0) / s_conf) + 1)
    return n_conf + max(0, math.ceil((altura_mm - 2 * lo) / s_fuera) - 1)


def momentos_diseno(h: float, b: float, dem: DemandaColumna, m: Materiales) -> Optional[tuple[np.ndarray, float]]:
    """(Mu de diseño por punto, esbeltez) con magnificación; None si la columna es demasiado esbelta o inestable."""
    r = 0.3 * h
    esb = dem.k_lu_max_m * 1000 / r
    if esb > ESBELTEZ_MAX:
        return None
    ms = dem.M_ns + dem.delta_s * dem.M_s
    if esb <= ESBELTEZ_SIN_EFECTO:
        return np.abs(ms).max(axis=1), esb
    ec = 4700.0 * math.sqrt(m.fc)
    ei = 0.4 * ec * (b * h**3 / 12) / (1 + dem.beta_dns)
    pc = math.pi**2 * ei / (dem.k_lu_max_m * 1000) ** 2 / 1e3          # kN
    pu = np.maximum(dem.P, 0.0)
    den = 1.0 - pu / (PHI_RIGIDEZ * pc)
    if (den <= 0.05).any():
        return None
    dns = np.maximum(1.0 / den, 1.0)
    mdes = np.abs(dns[:, None] * ms).max(axis=1)
    m_min = pu * (15.0 + 0.03 * h) / 1e3
    return np.maximum(mdes, m_min), esb


def _geometria(h: float, b: float, nivel: str) -> Optional[list[Verificacion]]:
    geom: list[Verificacion] = []
    if nivel == "DES":
        geom.append(Verificacion("Dimensión menor ≥ 300 mm", 300.0, min(h, b), "mm", min(h, b) >= 300.0, "C.21.6.1.1"))
        geom.append(Verificacion("Relación menor/mayor ≥ 0,4", 0.4, min(h, b) / max(h, b), "-", min(h, b) / max(h, b) >= 0.4, "C.21.6.1.2"))
    elif nivel == "DMO":
        geom.append(Verificacion("Dimensión menor ≥ 250 mm", 250.0, min(h, b), "mm", min(h, b) >= 250.0, "C.21.3.5.1"))
    return None if any(not g.cumple for g in geom) else geom


def _scwb(cv: Curva, dem: DemandaColumna, mnb_int: float, mnb_ext: float, cv_sup: Optional[Curva] = None) -> float:
    """Menor cociente ΣMnc/(1,2·ΣMnb) sobre todos los nudos y combinaciones con sismo; NaN si algún Mn no existe."""
    peor = math.inf
    for interior, p_inf, p_sup in dem.nudos:
        mc = mn_arr(cv, p_inf)
        if p_sup is not None:
            mc = mc + mn_arr(cv_sup if cv_sup is not None else cv, p_sup)
        if np.isnan(mc).any():
            return math.nan
        mnb = mnb_int if interior else mnb_ext
        peor = min(peor, float(mc.min()) / (RATIO_NUDO * max(mnb, 1e-9)))
    return peor


def disenar_columna(h: float, b: float, dem: DemandaColumna, nivel: str, m: Materiales, *, recubrimiento: float = 40.0,
                    mnb_int: float = 0.0, mnb_ext: float = 0.0, cv_sup: Optional[Curva] = None) -> list[DisenoColumna]:
    """Diseños factibles (uno por combinación de barras y estribo que cumple) para una columna h×b; vacío si ninguno.

    mnb_int / mnb_ext: ΣMnb de las vigas que llegan a un nudo interior / exterior (kN·m), solo se usa en DES (C.21.6.2.2).
    cv_sup: curva de la columna del piso superior (si difiere de esta); None = misma sección."""
    if nivel not in NIVELES:
        raise ValueError(f"nivel '{nivel}' no válido: {NIVELES}")
    geom = _geometria(h, b, nivel)
    if geom is None:
        return []
    md = momentos_diseno(h, b, dem, m)
    if md is None:
        return []
    Mu, esb = md
    P = dem.P
    raiz = math.sqrt(m.fc)
    lu_min, lu_max = dem.lu_min_m * 1000, dem.lu_max_m * 1000
    Pv = dem.P_sismo if (dem.P_sismo is not None and dem.P_sismo.size) else P
    salida: list[DisenoColumna] = []
    for n in N_CARA:
        for dia in BARRAS_COL:
            for est in ESTRIBOS_COL:
                sec = SeccionColumna(h, b, n, dia, est, recubrimiento)
                if not (RHO_MIN <= sec.rho <= RHO_MAX) or sec.separacion_libre < max(40.0, 1.5 * DIAMETRO_MM[dia]):
                    continue
                cv = curva(h, b, n, dia, est, recubrimiento, m.fc, m.fy)
                cap = phi_mn_arr(cv, P)
                if np.isnan(cap).any() or (cap + 1e-9 < Mu).any():
                    continue
                verifs = list(geom)
                verifs.append(Verificacion("Flexo-compresión φMn(Pu) ≥ Mu (todas las combinaciones y columnas)",
                                           float(np.max(Mu / np.maximum(cap, 1e-9))), 1.0, "-", True, "C.10.3 / C.9.3.2.2",
                                           "demanda/capacidad máxima; Mu incluye magnificación"))
                verifs.append(Verificacion("Cuantía 1 % ≤ ρ ≤ 4 %", sec.rho, RHO_MAX, "-", True,
                                           "C.21.6.3.1" if nivel == "DES" else "C.21.3.5.2 / C.10.9.1"))
                verifs.append(Verificacion("Esbeltez kℓu/r (magnificada si > 22)", esb, ESBELTEZ_MAX, "-", True, "C.10-6",
                                           "k de Jackson–Moreland y magnificación del ACI 318-08, no verificados en el corpus"))
                if nivel == "DES":
                    razon = _scwb(cv, dem, mnb_int, mnb_ext, cv_sup)
                    if math.isnan(razon) or razon < 1.0 - 1e-9:
                        continue
                    verifs.append(Verificacion("ΣMnc ≥ 1,2·ΣMnb (columna fuerte–viga débil)", 1.0, razon, "-", True, "C.21.6.2.2",
                                               "capacidad/demanda mínima sobre todos los nudos y sentidos; sin aporte de losa"))
                d_cort = h - sec.d_borde
                d_est, a_leg = DIAMETRO_MM[est], AREA_MM2[est]
                av = n * a_leg                                  # n ramas en el plano (ganchos en todas las barras perimetrales)
                vc_pleno = 0.17 * raiz * b * d_cort / 1000
                lim_vs = 0.66 * raiz * b * d_cort / 1000
                s_ties = min(16 * DIAMETRO_MM[dia], 48 * d_est, min(h, b))
                if nivel == "DMI":
                    lo = 0.0
                    vs_req = max(0.0, dem.V / PHI_CORTANTE - vc_pleno)
                    if vs_req > lim_vs:
                        continue
                    s_sh = math.inf if vs_req == 0 else av * m.fyt * d_cort / (vs_req * 1000)
                    s_conf = s_fuera = _redondeo(min(s_ties, s_sh))
                    ref_c, nota_c = "C.11.2.1.1 / C.11.4.7.2", "espaciamiento DMI del ACI (C.7.10.5.2 no recuperado)"
                    ve = dem.V
                    vc = vc_pleno
                else:
                    cv_pr = curva(h, b, n, dia, est, recubrimiento, m.fc, m.fy, FACTOR_MPR if nivel == "DES" else 1.0, False)
                    mom = mn_arr(cv_pr, Pv)
                    if np.isnan(mom).any():
                        continue
                    ve = max(2 * float(mom.max()) / (lu_min / 1000), dem.V)
                    sismo_domina = dem.V_sismo >= 0.5 * ve and float(Pv.max()) < (h * b * m.fc / 20) / 1000
                    vc = 0.0 if (nivel == "DES" and sismo_domina) else vc_pleno
                    vs_req = max(0.0, ve / PHI_CORTANTE - vc)
                    if vs_req > lim_vs:
                        continue
                    s_sh = math.inf if vs_req == 0 else av * m.fyt * d_cort / (vs_req * 1000)
                    vs_req_f = max(0.0, ve / PHI_CORTANTE - vc_pleno)
                    s_sh_f = math.inf if vs_req_f == 0 else av * m.fyt * d_cort / (vs_req_f * 1000)
                    lo = max(h, lu_max / 6, 450.0)
                    if nivel == "DES":
                        hx = sec.sep_barras
                        if hx > 350.0:
                            continue
                        s_norma = min(min(h, b) / 4, 6 * DIAMETRO_MM[dia], so_des(hx))
                        s_fuera_norma = min(6 * DIAMETRO_MM[dia], 150.0)
                        ref_c, nota_c = "C.21.6.5.1/.2", "Mpr=1,25fy no verificado"
                    else:
                        s_norma = min(8 * DIAMETRO_MM[dia], 24 * d_est, min(h, b) / 2, 300.0)
                        s_fuera_norma = 2 * s_norma
                        ref_c, nota_c = "C.21.3.3", "C.21.3.3 (a)/(b) y C.21.3.5.6 no recuperados"
                    s_ash = av / ash_requerido(sec, 1.0, m, nivel)
                    s_conf = _redondeo(min(s_norma, s_sh, s_ash))
                    s_fuera = _redondeo(min(s_fuera_norma, s_sh_f, s_ties))
                    verifs.append(Verificacion("s en ℓo ≤ so", s_conf, s_norma, "mm", s_conf <= s_norma + 1e-9,
                                               "C.21.6.4.3 / C-21-5" if nivel == "DES" else "C.21.3.5.6"))
                    verifs.append(Verificacion("Ash,prov ≥ Ash,req", av, ash_requerido(sec, s_conf, m, nivel), "mm²",
                                               av + 1e-9 >= ash_requerido(sec, s_conf, m, nivel),
                                               "C.21-7/-8 (ACI 318-08)" if nivel == "DES" else "C.21-2/-3"))
                    verifs.append(Verificacion("s fuera de ℓo", s_fuera, s_fuera_norma, "mm", s_fuera <= s_fuera_norma + 1e-9,
                                               "C.21.6.4.5" if nivel == "DES" else "C.21.3.5.11"))
                if s_conf < S_MIN or s_fuera < S_MIN:
                    continue
                phi_vn = PHI_CORTANTE * (vc + av * m.fyt * d_cort / s_conf / 1000)
                verifs.append(Verificacion("Cortante φ(Vc+Vs) ≥ Ve", ve, phi_vn, "kN", phi_vn + 1e-9 >= ve, ref_c, nota_c))
                d = DisenoColumna(h, b, n, dia, est, nivel, s_conf, s_fuera, lo,
                                  contar_estribos_col(lu_max, lo, s_conf, s_fuera), tuple(verifs))
                if d.cumple:
                    salida.append(d)
    return salida
