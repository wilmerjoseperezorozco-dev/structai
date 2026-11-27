"""Soportes sismorresistentes y anclajes de la red contra incendio (#336 F8), NSR-10 A.9, B.2.4 y Apéndice C-D.

Números de la NSR-10, cotejados con el PDF oficial el 2026-11-26 (solo números y ecuaciones, sin texto):
  - A.9.4-1: Fp = (ax · ap / Rp) · g · Mp ≥ (Aa · I / 2) · g · Mp
  - A.9.4-2: ax = As + (Sa − As) · hx/heq si hx ≤ heq; ax = Sa · hx/heq si hx ≥ heq; se permite heq ≈ 0,75 hn
  - A.9.4.8: en la base de la estructura, por debajo o por fuera de ella: ax = Aa · I
  - A.9.4.4: fuerza vertical adicional de ±W/3 para elementos mecánicos y eléctricos, sin amplificar por ax ni ap ni
    dividir por Rp
  - A.9.4.9: Rp = 6 (especiales F-DES, o dúctiles: químicos o vaciados profundos con embebido/diámetro > 8, o C.21);
    Rp = 1,5 (no dúctiles: expansión, tiros, superficiales con relación ≤ 8); Rp = 0,5 (húmedos)
  - A.9.1.3: exentas las edificaciones de los grupos de uso I y II en zona de amenaza sísmica baja
  - Tabla A.9.2-1: grado de desempeño mínimo IV y III superior, II bueno, I bajo
  - Tabla A.9.6-1: tubería del sistema contra incendio ap = 2,5 con anclaje dúctil (superior) o no dúctil
    (bueno, bajo). Equipo en general (bombas hidráulicas) ap = 1,0 con dúctil, no dúctil o no requerido. La nota (d),
    que exime los soportes de tuberías pequeñas o colgadas de soportes cortos, es SOLO para "otros sistemas de
    tuberías": no aplica a la red contra incendio.
  - B.2.4-1: 1,4D; B.2.4-5: 1,2D + 1,0E + 1,0L; B.2.4-7: 0,9D + 1,0E
  - C-D.3.3.3: en DMO y DES, los modos de falla del concreto se toman como 0,75φNn y 0,75φVn
  - C-D.3.3.4 a 6: el anclaje debe estar controlado por un acero dúctil, o la fijación debe fluir antes, o la
    resistencia se toma como 0,4 veces la de C-D.3.3.3
  - C-D.7: si Vua ≤ 0,2φVn basta φNn ≥ Nua; si Nua ≤ 0,2φNn basta φVn ≥ Vua; si no, Nua/φNn + Vua/φVn ≤ 1,2
Interpretaciones declaradas (en la hoja de verificación):
  - As = Aa · Fa · I: es la ordenada en T = 0 del espectro de la figura A.2.6-1, porque 2,5 · Aa · Fa · I · 0,4.
  - La nota (b) de la tabla A.9.6-1 (ap vertical +33 %) frente a A.9.4.4 (W/3 sin amplificar): v1 usa A.9.4.4 e
    informa también el valor de la nota (b).
  - El agua dentro de la tubería se trata como carga muerta D.
Datos del proyecto, sin valores por defecto: separaciones máximas de riostras laterales y longitudinales y de
colgadores, diámetro mínimo que se arriostra, ángulo de la riostra, masa de la tubería por diámetro, resistencias de
los anclajes (φNsa, φN del concreto, φVsa, φV del concreto, según C-D o el fabricante con ACI 355.2) y la ruta de
C-D.3.3. Las separaciones y el criterio de qué se arriostra salen de la norma de rociadores aplicable (p. ej. NFPA 13).
v1 asigna a cada tramo su propia carga tributaria. NO suma la de los ramales que cuelgan de él: si ese aporte
importa, hay que declararlo en la masa por metro. Tampoco diseña el perfil de la riostra.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

G = 9.81
AP = {"tuberia_incendio": 2.5, "bomba": 1.0}                               # Tabla A.9.6-1
GRADO_MINIMO = {"I": "bajo", "II": "bueno", "III": "superior", "IV": "superior"}   # Tabla A.9.2-1
ANCLAJE_REQUERIDO = {                                                       # Tabla A.9.6-1
    "tuberia_incendio": {"superior": "ductil", "bueno": "no_ductil", "bajo": "no_ductil"},
    "bomba": {"superior": "ductil", "bueno": "no_ductil", "bajo": None},
}
RP = {"especial": 6.0, "ductil": 6.0, "no_ductil": 1.5, "humedo": 0.5}      # A.9.4.9
_NIVEL = {"humedo": 0, "no_ductil": 1, "ductil": 2, "especial": 2}
_GRADOS = ("bajo", "bueno", "superior")


@dataclass(frozen=True)
class Sismo:
    aa: float
    fa: float
    i: float                    # coeficiente de importancia
    sa: float                   # Sa de la estructura (la mayor de las dos direcciones, A.9.4.2.1)
    hn_m: float
    zona: str                   # "baja", "intermedia" o "alta"
    grupo_uso: str              # "I" a "IV"
    capacidad: str              # "DMI", "DMO" o "DES"
    heq_m: Optional[float] = None    # si no se da, 0,75·hn (A.9.4.2.1)

    @property
    def a_s(self) -> float:
        return self.aa * self.fa * self.i

    @property
    def heq(self) -> float:
        return self.heq_m if self.heq_m is not None else 0.75 * self.hn_m


def exento(s: Sismo) -> bool:
    return s.grupo_uso in ("I", "II") and s.zona == "baja"                 # A.9.1.3


def ax(s: Sismo, hx_m: float) -> float:
    if hx_m <= 0:
        return s.aa * s.i                                                   # A.9.4.8
    if hx_m <= s.heq:
        return s.a_s + (s.sa - s.a_s) * hx_m / s.heq                        # A.9.4-2
    return s.sa * hx_m / s.heq


def coef_fp(s: Sismo, hx_m: float, ap: float, rp: float) -> float:
    """Fp / (g·Mp) según A.9.4-1, con el mínimo Aa·I/2."""
    return max(ax(s, hx_m) * ap / rp, s.aa * s.i / 2)


def clasificar_anclaje(tipo: str, embebido_sobre_d: Optional[float] = None) -> str:
    """Tipo de anclaje de A.9.4.9 a partir de su descripción."""
    if tipo == "especial_f_des":
        return "especial"
    if tipo == "c21":
        return "ductil"
    if tipo in ("quimico", "vaciado"):
        if embebido_sobre_d is None:
            raise ValueError("declare la relación embebido/diámetro del anclaje químico o vaciado")
        return "ductil" if embebido_sobre_d > 8 else "no_ductil"
    if tipo in ("expansion", "tiro"):
        return "no_ductil"
    if tipo == "mortero":
        return "humedo"
    raise ValueError(f"tipo de anclaje desconocido: {tipo}")


def grado(s: Sismo, grado_declarado: Optional[str] = None) -> str:
    m = GRADO_MINIMO[s.grupo_uso]
    if grado_declarado is None:
        return m
    if _GRADOS.index(grado_declarado) < _GRADOS.index(m):
        raise ValueError(f"grado {grado_declarado} menor que el mínimo {m} de la tabla A.9.2-1")
    return grado_declarado


def rp_admisible(s: Sismo, elemento: str, clase_anclaje: str, grado_declarado: Optional[str] = None) -> tuple:
    """(Rp, observación). Rp es None si el anclaje no cumple lo que exige la tabla A.9.6-1 para el grado."""
    req = ANCLAJE_REQUERIDO[elemento][grado(s, grado_declarado)]
    if req is None:
        return None, "no requiere diseño sísmico (tabla A.9.6-1, nota g)"
    if _NIVEL[clase_anclaje] < _NIVEL[req]:
        return None, f"exige anclaje {req} y se declaró {clase_anclaje}"
    return RP[clase_anclaje], "ok"


@dataclass(frozen=True)
class CapacidadAnclaje:
    phi_nsa_kn: float           # acero en tracción
    phi_nc_kn: float            # el menor de los modos del concreto en tracción (arrancamiento, extracción, adherencia)
    phi_vsa_kn: float
    phi_vc_kn: float            # el menor de los modos del concreto en cortante (desprendimiento, palanqueo)
    ruta_cd33: str              # "acero_ductil" (C-D.3.3.4) o "factor_04" (C-D.3.3.6)
    fuente: str

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente de las resistencias del anclaje")
        if self.ruta_cd33 not in ("acero_ductil", "factor_04"):
            raise ValueError("ruta C-D.3.3 no implementada (C-D.3.3.5 se verifica aparte)")


def resistencia_diseno(c: CapacidadAnclaje, s: Sismo) -> tuple:
    """(φNn, φVn) con C-D.3.3 cuando la estructura es DMO o DES."""
    if s.capacidad == "DMI":
        return min(c.phi_nsa_kn, c.phi_nc_kn), min(c.phi_vsa_kn, c.phi_vc_kn)
    nc, vc = 0.75 * c.phi_nc_kn, 0.75 * c.phi_vc_kn                       # C-D.3.3.3
    n, v = min(c.phi_nsa_kn, nc), min(c.phi_vsa_kn, vc)
    if c.ruta_cd33 == "acero_ductil":                                       # C-D.3.3.4: debe gobernar el acero
        if c.phi_nsa_kn > nc or c.phi_vsa_kn > vc:
            raise ValueError("C-D.3.3.4 no se cumple: el concreto gobierna sobre el acero; use otra ruta")
        return n, v
    return 0.4 * n, 0.4 * v                                                 # C-D.3.3.6


def interaccion(nua: float, vua: float, phi_nn: float, phi_vn: float) -> tuple:
    """(cumple, índice) según C-D.7."""
    if vua <= 0.2 * phi_vn:
        return nua <= phi_nn, nua / phi_nn
    if nua <= 0.2 * phi_nn:
        return vua <= phi_vn, vua / phi_vn
    r = nua / phi_nn + vua / phi_vn
    return r <= 1.2, r / 1.2


@dataclass(frozen=True)
class CriteriosSoporte:
    s_lateral_max_m: float
    s_longitudinal_max_m: float
    s_colgador_max_m: float
    d_min_arriostrar_m: float           # diámetro interior desde el cual se arriostra (criterio de la norma de rociadores)
    angulo_riostra_desde_vertical_deg: float
    masa_tuberia_kg_m: dict             # {dn: kg/m de la tubería vacía}
    fuente: str

    def __post_init__(self):
        if not self.fuente.strip():
            raise ValueError("declare la fuente de los criterios de soporte")
        if not 0 < self.angulo_riostra_desde_vertical_deg < 90:
            raise ValueError("ángulo de riostra fuera de (0, 90)")


@dataclass
class Soporte:
    tramo: tuple
    hx_m: float
    w_kn_m: float
    coef: float
    n_lateral: int
    n_longitudinal: int
    n_colgadores: int
    h_lateral_kn: float                 # fuerza horizontal por riostra lateral
    h_longitudinal_kn: float
    anclaje_riostra: tuple              # (Nua, Vua) de la riostra más cargada
    t_colgador_kn: float
    fv_nota_b_kn: float                 # referencia: vertical con la nota (b) de la tabla A.9.6-1
    verificacion: tuple = ()            # (cumple riostra, índice, cumple colgador, índice)
    observaciones: list = field(default_factory=list)


def arriostrar(tramos: list, tuberias: dict, s: Sismo, c: CriteriosSoporte, clase_anclaje: str,
               cap_riostra: CapacidadAnclaje, cap_colgador: CapacidadAnclaje, z_base_m: float = 0.0,
               grado_declarado: Optional[str] = None) -> list[Soporte]:
    """Riostras y colgadores de cada tramo horizontal. tuberias: {frozenset((a, b)): Tuberia}. hx se mide desde
    z_base_m (base de la estructura) hasta el punto de soporte (losa superior del tramo: se toma la cota del tubo)."""
    if exento(s):
        return []
    rp, obs = rp_admisible(s, "tuberia_incendio", clase_anclaje, grado_declarado)
    if rp is None:
        raise ValueError(f"anclaje no admisible: {obs}")
    ap = AP["tuberia_incendio"]
    th = math.radians(c.angulo_riostra_desde_vertical_deg)
    phin_r, phiv_r = resistencia_diseno(cap_riostra, s)
    phin_c, _ = resistencia_diseno(cap_colgador, s)
    out = []
    for a, b in tramos:
        if abs(a[2] - b[2]) > 1e-9:
            continue                                                        # bajantes y subidas: fuera de v1
        tub = tuberias[frozenset((a, b))]
        L = math.dist(a, b)
        masa = c.masa_tuberia_kg_m.get(tub.dn)
        if masa is None:
            raise ValueError(f"falta la masa por metro de {tub.dn}")
        w = (masa + 1000.0 * math.pi * tub.d_int_m ** 2 / 4) * G / 1000.0  # kN/m, tubería llena
        hx = a[2] - z_base_m
        k = coef_fp(s, hx, ap, rp)
        n_col = max(1, math.ceil(L / c.s_colgador_max_m - 1e-9))
        wt = w * L / n_col
        t_col = max(1.4 * wt, 1.2 * wt + wt / 3)                            # B.2.4-1 y B.2.4-5 con Ev = W/3
        fvb = ax(s, hx) * (1.33 * ap) / rp * wt
        sp = Soporte((a, b), hx, w, k, 0, 0, n_col, 0.0, 0.0, (0.0, 0.0), t_col, fvb)
        if tub.d_int_m >= c.d_min_arriostrar_m - 1e-9:
            sp.n_lateral = max(1, math.ceil(L / c.s_lateral_max_m - 1e-9))
            sp.n_longitudinal = max(1, math.ceil(L / c.s_longitudinal_max_m - 1e-9))
            sp.h_lateral_kn = k * w * L / sp.n_lateral
            sp.h_longitudinal_kn = k * w * L / sp.n_longitudinal
            hmax = max(sp.h_lateral_kn, sp.h_longitudinal_kn)
            sp.anclaje_riostra = (hmax / math.tan(th), hmax)                # tracción por la componente vertical
        else:
            sp.observaciones.append("diámetro menor que el mínimo declarado para arriostrar: solo colgadores")
        ok_r, ir = interaccion(*sp.anclaje_riostra, phin_r, phiv_r) if sp.n_lateral else (True, 0.0)
        ok_c, ic = t_col <= phin_c, t_col / phin_c
        sp.verificacion = (ok_r, ir, ok_c, ic)
        out.append(sp)
    return out


@dataclass
class AnclajeEquipo:
    fp_kn: float
    tension_por_anclaje_kn: float
    cortante_por_anclaje_kn: float
    cumple: bool
    indice: float


def anclar_equipo(peso_kn: float, h_cg_m: float, b_entre_lineas_m: float, n_por_linea: int, hx_m: float, s: Sismo,
                  clase_anclaje: str, cap: CapacidadAnclaje, grado_declarado: Optional[str] = None) -> Optional[AnclajeEquipo]:
    """Anclaje de una bomba (tabla A.9.6-1, equipo en general) a su base: vuelco con 0,9D − W/3 resistente (B.2.4-7
    con la vertical de A.9.4.4) y cortante repartido por igual entre las dos líneas de anclajes."""
    if exento(s):
        return None
    rp, obs = rp_admisible(s, "bomba", clase_anclaje, grado_declarado)
    if rp is None:
        if "no requiere" in obs:
            return None
        raise ValueError(f"anclaje no admisible: {obs}")
    fp = coef_fp(s, hx_m, AP["bomba"], rp) * peso_kn
    resistente = 0.9 * peso_kn - peso_kn / 3
    t_linea = max(0.0, fp * h_cg_m / b_entre_lineas_m - resistente / 2)
    nua, vua = t_linea / n_por_linea, fp / (2 * n_por_linea)
    phin, phiv = resistencia_diseno(cap, s)
    ok, ind = interaccion(nua, vua, phin, phiv)
    return AnclajeEquipo(fp, nua, vua, ok, ind)
