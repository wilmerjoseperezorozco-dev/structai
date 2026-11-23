"""Resistencia nominal a flexión de un perfil C por iniciación de la fluencia, NSR-10 F.4.3.3.1.1 Procedimiento 1.

Mn = Se·Fy (F.4.3.3-1). Flexión alrededor del eje fuerte (horizontal) con la aleta superior en compresión.
Se se obtiene de la sección efectiva: los anchos efectivos dependen de los esfuerzos, que dependen del eje neutro
de la sección efectiva. Ese punto fijo se resuelve con brentq sobre g(y) = y − ycg_efectivo(y) (regla 3: nada de
iteraciones con paso fijo). La fibra que alcanza Fy es la más alejada del eje neutro efectivo.

Solo resistencia de la sección. NO verifica pandeo lateral-torsional (F.4.3.3.1.2) ni pandeo distorsional
(F.4.3.3.1.4): por eso la función exige declarar que la aleta comprimida está arriostrada lateralmente de forma
continua, y el contrato deja la advertencia del pandeo distorsional.

Supuestos de cálculo (se reportan en la salida):
- método lineal y esquinas rectas (radio interior 0), ver seccion.py;
- el esfuerzo en la aleta comprimida se toma igual al de la fibra extrema (conservador);
- los elementos en tensión son totalmente efectivos.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.optimize import brentq

from .ancho_efectivo import E_ACERO_MPA, MU_ACERO
from .elementos import alma_gradiente, aleta_con_pestana, no_rigidizado_gradiente, no_rigidizado_uniforme
from .seccion import GeometriaC

PHI_B_RIGIDIZADA = 0.95      # F.4.3.3.1.1, aleta comprimida rigidizada o parcialmente rigidizada
PHI_B_NO_RIGIDIZADA = 0.90   # F.4.3.3.1.1, aleta comprimida no rigidizada

Tramo = tuple[float, float, float, float]   # (x1, y1, x2, y2) en la línea media


@dataclass(frozen=True)
class ResultadoFlexion:
    Mn: float                 # N·mm
    phi_b: float
    Se: float                 # mm³
    Sx_bruto: float           # mm³ (respecto a la fibra extrema superior)
    y_eje_neutro: float       # mm, en coordenadas de la línea media (y = 0 en la aleta inferior)
    fibra_que_fluye: str      # "compresion" | "tension"
    f_aleta: float            # MPa, esfuerzo de la aleta comprimida
    anchos: dict              # porciones efectivas por elemento (mm)
    tramos: list[Tramo]


def _props_tramos(tramos: list[Tramo], t: float) -> tuple[float, float, float]:
    """Área, centroide y e Ix (respecto al centroide) de un conjunto de tramos rectos por el método lineal."""
    A = sum(math.hypot(x2 - x1, y2 - y1) * t for x1, y1, x2, y2 in tramos)
    ycg = sum(math.hypot(x2 - x1, y2 - y1) * t * (y1 + y2) / 2 for x1, y1, x2, y2 in tramos) / A
    Ix = 0.0
    for x1, y1, x2, y2 in tramos:
        l = math.hypot(x2 - x1, y2 - y1)
        a, b = y1 - ycg, y2 - ycg
        Ix += t * l * (a * a + a * b + b * b) / 3
    return A, ycg, Ix


def _seccion_efectiva(g: GeometriaC, f_ext: float, y_na: float, E: float, mu: float) -> tuple[list[Tramo], dict, float]:
    """Tramos efectivos dados el esfuerzo de compresión en la fibra extrema superior y el eje neutro."""
    t, hc, bc, dc = g.t, g.hc, g.bc, g.dc
    y_ext = hc + t / 2

    def f(y: float) -> float:
        return f_ext * (y - y_na) / (y_ext - y_na)

    f_aleta = f_ext
    tramos: list[Tramo] = []
    anchos: dict = {}

    # Aleta inferior y pestaña inferior: en tensión → totalmente efectivas.
    tramos.append((0.0, 0.0, bc, 0.0))
    if g.con_pestana:
        tramos.append((bc, 0.0, bc, dc))

    # Alma (línea media de y = 0 a y = hc; ancho plano de y = t/2 a y = hc − t/2).
    y_sup, y_inf = hc - t / 2, t / 2
    f1, f2 = f(y_sup), f(y_inf)
    a = alma_gradiente(f1, f2, g.w_alma, t, ho=g.H, bo=g.B, E=E, mu=mu)
    anchos["alma"] = {"b1": a.b1, "b2": a.b2, "comprimida": a.comprimida, "totalmente_efectiva": a.totalmente_efectiva}
    if a.totalmente_efectiva:
        tramos.append((0.0, 0.0, 0.0, hc))
    else:
        if f2 < 0:   # hueco entre b1 (desde arriba) y b2 (sobre el eje neutro)
            hueco_sup, hueco_inf = y_sup - a.b1, y_sup - a.comprimida + a.b2
        else:        # todo el alma comprimida: b2 desde el borde inferior del ancho plano
            hueco_sup, hueco_inf = y_sup - a.b1, y_inf + a.b2
        tramos.append((0.0, 0.0, 0.0, hueco_inf))
        tramos.append((0.0, hueco_sup, 0.0, hc))

    # Aleta superior comprimida (ancho plano de x = t/2 a x = bc − t/2) y su pestaña.
    x_ini, x_fin = t / 2, bc - t / 2
    if g.con_pestana:
        fp1, fp2 = f(hc - t / 2), f(hc - dc)
        ds_prima = no_rigidizado_gradiente(fp1, fp2, g.d_pestana, t, E, mu)
        al = aleta_con_pestana(f_aleta, g.w_aleta, t, g.d_pestana, g.D, ds_prima, E, mu)
        anchos["aleta_comprimida"] = {"b1": al.b1, "b2": al.b2, "R1": al.R1, "k": al.k, "Is": al.Is, "Ia": al.Ia}
        anchos["pestana_comprimida"] = {"ds_prima": ds_prima, "ds": al.ds}
        tramos.append((0.0, hc, x_ini + al.b1, hc))
        tramos.append((x_fin - al.b2, hc, bc, hc))
        tramos.append((bc, hc, bc, hc - t / 2 - al.ds))
    else:
        b = no_rigidizado_uniforme(f_aleta, g.w_aleta, t, E, mu)
        anchos["aleta_comprimida"] = {"b": b}
        tramos.append((0.0, hc, x_ini + b, hc))
    return tramos, anchos, f_aleta


def _estado(g: GeometriaC, y_na: float, Fy: float, E: float, mu: float):
    t = g.t
    d_comp, d_tens = (g.hc + t / 2) - y_na, y_na + t / 2
    if d_comp >= d_tens:
        f_ext, fibra = Fy, "compresion"
    else:
        f_ext, fibra = Fy * d_comp / d_tens, "tension"
    tramos, anchos, f_aleta = _seccion_efectiva(g, f_ext, y_na, E, mu)
    A, ycg, Ix = _props_tramos(tramos, t)
    return ycg, Ix, fibra, d_comp, d_tens, tramos, anchos, f_aleta


def resistencia_flexion_c(g: GeometriaC, Fy: float, *, aleta_comprimida_arriostrada: bool,
                          E: float = E_ACERO_MPA, mu: float = MU_ACERO) -> ResultadoFlexion:
    """Mn = Se·Fy (F.4.3.3-1) para un perfil C en flexión alrededor del eje fuerte."""
    if aleta_comprimida_arriostrada is not True:
        raise ValueError("Solo se calcula la resistencia de la sección (F.4.3.3.1.1). Sin arriostramiento lateral continuo "
                         "de la aleta comprimida gobierna el pandeo lateral-torsional (F.4.3.3.1.2), que este motor "
                         "todavía no implementa.")
    if not (Fy > 0 and math.isfinite(Fy)):
        raise ValueError(f"Fy = {Fy} inválido (NSR-10 F.4.1.6.1).")
    t, hc = g.t, g.hc
    eps = 1e-6 * hc

    def residuo(y: float) -> float:
        return y - _estado(g, y, Fy, E, mu)[0]

    lo, hi = eps, hc - t / 2 - eps     # el eje neutro debe cortar el alma por debajo de su borde comprimido
    if residuo(lo) * residuo(hi) > 0:
        raise ValueError("No se encontró el eje neutro de la sección efectiva en el alma (F.4.3.3.1.1).")
    y_na = brentq(residuo, lo, hi, xtol=1e-9 * hc, rtol=1e-12, maxiter=200)
    if abs(residuo(y_na)) > 1e-6 * hc:
        raise ValueError("La iteración de la sección efectiva no convergió (F.4.3.3.1.1).")
    ycg, Ix, fibra, d_comp, d_tens, tramos, anchos, f_aleta = _estado(g, y_na, Fy, E, mu)
    Se = Ix / (d_comp if fibra == "compresion" else d_tens)
    pb = g.propiedades()
    Sx = pb.Ix / ((hc + t / 2) - pb.yc)
    phi = PHI_B_RIGIDIZADA if g.con_pestana else PHI_B_NO_RIGIDIZADA
    return ResultadoFlexion(Mn=Se * Fy, phi_b=phi, Se=Se, Sx_bruto=Sx, y_eje_neutro=y_na, fibra_que_fluye=fibra,
                            f_aleta=f_aleta, anchos=anchos, tramos=tramos)


def interaccion_flexion_cortante(Mu: float, Vu: float, phi_Mnxo: float, phi_Vn: float) -> float:
    """√[(Mu/φbMnxo)² + (Vu/φvVn)²] (F.4.3.3-54), almas no reforzadas. Debe ser ≤ 1.0."""
    for nombre, v in (("Mu", Mu), ("Vu", Vu)):
        if not (v >= 0 and math.isfinite(v)):
            raise ValueError(f"{nombre} = {v} inválido: use el valor absoluto de la solicitación (F.4.3.3.3).")
    for nombre, v in (("φbMnxo", phi_Mnxo), ("φvVn", phi_Vn)):
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{nombre} = {v} inválido (F.4.3.3.3).")
    return math.sqrt((Mu / phi_Mnxo) ** 2 + (Vu / phi_Vn) ** 2)
