"""Contrato uniforme de motor-acero-frio (#81): perfiles C formados en frío según NSR-10 F.4.

Toda salida es un ResultadoMotor. Ninguna entrada física tiene valor por defecto salvo E (F.4.4.6.1.3) y μ
(F.4.3.3.2.1), que son valores de la propia norma. El resultado nunca reemplaza el diseño firmado por un ingeniero.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .ancho_efectivo import E_ACERO_MPA, MU_ACERO  # noqa: E402
from .elementos import D_W_MAX_TABLA, H_T_MAX_ALMA, W_T_MAX_ALETA_PESTANA, W_T_MAX_NO_RIGIDIZADO  # noqa: E402
from .arrugamiento import CoeficientesArrugamiento, arrugamiento_alma, interaccion_flexion_arrugamiento  # noqa: E402
from .combinada import PHI_T_COMBINADA, flexo_compresion_uniaxial, flexo_tension_uniaxial  # noqa: E402
from .distorsional import distorsional_compresion_c, distorsional_flexion_c  # noqa: E402
from .flexion import interaccion_flexion_cortante, resistencia_flexion_c, resistencia_ltb_c  # noqa: E402
from .miembros import (  # noqa: E402
    PHI_C,
    area_efectiva_compresion_c,
    coeficiente_kv,
    resistencia_compresion_c,
    resistencia_cortante,
    resistencia_tension,
)
from .seccion import GeometriaC  # noqa: E402

SUPUESTOS_SECCION = [
    "Propiedades por el método lineal (línea media × espesor), NSR-10 F.4.3.1.",
    "Esquinas rectas: no se modela el radio interior de doblez; los anchos planos son la dimensión externa − 2t.",
    "Pestañas a 90° respecto a la aleta.",
]
SUPUESTOS_DISTORSIONAL = [
    "Pandeo distorsional por el método general (b), aleta + pestaña por el método lineal (F.4.3.3.1.4(b), F.4.3.4.2(b)).",
    "En K̃φfg (F.4.3.3-42) se usa hx² donde el corpus transcribe «ho²» (errata: el término es el momento polar de la "
    "aleta respecto a la unión aleta-alma).",
    "kφwe en flexión según el corpus, E·t³/(12(1−μ²)·ho) (F.4.3.3-41): es menor que la expresión de AISI S100-07, "
    "del lado seguro. Pendiente cotejar con la NSR-10 impresa.",
]
ADV_CONEXION = ("No se verificó la rotura en la conexión (F.4.3.2 c): depende del diseño de la conexión (F.4.5), que este "
                "motor no cubre todavía.")
ADV_APOYOS = ("Verifique el arrugamiento del alma en apoyos y cargas concentradas con arrugamiento_perfil_c "
              "(F.4.3.3.4); no se verificaron deflexiones.")
BORDE = 0.95   # fracción del límite normativo a partir de la cual se informa en_borde_dominio


class PerfilC(BaseModel):
    """Perfil C formado en frío, dimensiones externas."""
    model_config = ConfigDict(strict=True, extra="forbid")

    H_mm: float = Field(..., gt=0, le=1000, allow_inf_nan=False, description="Altura total")
    B_mm: float = Field(..., gt=0, le=500, allow_inf_nan=False, description="Ancho total de la aleta")
    D_mm: float = Field(..., ge=0, le=200, allow_inf_nan=False, description="Longitud total de la pestaña; 0 = C sin pestaña")
    t_mm: float = Field(..., gt=0, le=25.4, allow_inf_nan=False, description="Espesor")
    Fy_MPa: float = Field(..., gt=0, le=700, allow_inf_nan=False, description="Esfuerzo de fluencia de diseño (F.4.1.6.1)")
    Fu_MPa: float = Field(..., gt=0, le=900, allow_inf_nan=False, description="Resistencia a tensión (F.4.1.2)")
    E_MPa: float = Field(E_ACERO_MPA, gt=0, allow_inf_nan=False, description="203 000 MPa según F.4.4.6.1.3")

    @model_validator(mode="after")
    def _coherencia(self):
        if self.Fu_MPa < self.Fy_MPa:
            raise ValueError("Fu no puede ser menor que Fy (NSR-10 F.4.1.2).")
        GeometriaC(self.H_mm, self.B_mm, self.D_mm, self.t_mm)   # valida la geometría
        return self

    def geometria(self) -> GeometriaC:
        return GeometriaC(self.H_mm, self.B_mm, self.D_mm, self.t_mm)


def _relaciones(g: GeometriaC) -> dict:
    r = {"h_t_alma": g.w_alma / g.t, "w_t_aleta": g.w_aleta / g.t}
    if g.con_pestana:
        r["d_t_pestana"] = g.d_pestana / g.t
        r["D_w"] = g.D / g.w_aleta
    return r


def _en_borde(g: GeometriaC) -> tuple[bool, list[str]]:
    rel, notas = _relaciones(g), []
    lim_aleta = W_T_MAX_ALETA_PESTANA if g.con_pestana else W_T_MAX_NO_RIGIDIZADO
    if rel["h_t_alma"] >= BORDE * H_T_MAX_ALMA:
        notas.append(f"h/t = {rel['h_t_alma']:.1f} cerca del máximo {H_T_MAX_ALMA:.0f} (F.4.2.1.2).")
    if rel["w_t_aleta"] >= BORDE * lim_aleta:
        notas.append(f"w/t de aleta = {rel['w_t_aleta']:.1f} cerca del máximo {lim_aleta:.0f} (F.4.2.1.1.1).")
    if g.con_pestana and rel["d_t_pestana"] >= BORDE * W_T_MAX_NO_RIGIDIZADO:
        notas.append(f"d/t de pestaña = {rel['d_t_pestana']:.1f} cerca del máximo 60 (F.4.2.1.1.1).")
    if g.con_pestana and rel["D_w"] >= BORDE * D_W_MAX_TABLA:
        notas.append(f"D/w = {rel['D_w']:.3f} cerca del límite {D_W_MAX_TABLA} de la Tabla F.4.2.4-1.")
    return bool(notas), notas


def propiedades_perfil_c(perfil: PerfilC) -> ResultadoMotor:
    g = perfil.geometria()
    p = g.propiedades()
    borde, notas = _en_borde(g)
    return ResultadoMotor(
        valor={"A_mm2": p.A, "Ix_mm4": p.Ix, "Iy_mm4": p.Iy, "rx_mm": p.rx, "ry_mm": p.ry, "xc_mm": p.xc,
               "xo_mm": p.xo, "ro_mm": p.ro, "J_mm4": p.J, "Cw_mm6": p.Cw, "relaciones": _relaciones(g)},
        unidad_si="mm (propiedades geométricas)",
        ecuacion="Método lineal; ro = √(rx² + ry² + xo²) (F.4.3.3-13); centro de cortante y Cw por coordenada sectorial",
        referencia_normativa="NSR-10 F.4.3.1, F.4.3.3-13",
        supuestos=SUPUESTOS_SECCION,
        en_borde_dominio=borde,
        advertencias=notas,
    )


@dataclass(frozen=True)
class _Flexion:
    """Los tres estados límite de flexión y el que gobierna (φ·Mn mínimo), en N·mm."""
    seccion: object
    ltb: object | None
    dist: object | None
    phi_Mn: float
    Mn: float
    phi_b: float
    gobierna: str
    borde: list[str]


def _flexion(perfil: PerfilC, *, Lm_mm: Optional[float], kphi_N: float, KyLy_mm: Optional[float],
             KtLt_mm: Optional[float], Cb: Optional[float], aleta_comprimida_arriostrada: bool) -> _Flexion:
    g, E, Fy = perfil.geometria(), perfil.E_MPa, perfil.Fy_MPa
    sec = resistencia_flexion_c(g, Fy, E, MU_ACERO)
    candidatos = {"seccion": (sec.phi_b * sec.Mn, sec.Mn, sec.phi_b)}
    borde: list[str] = []

    if aleta_comprimida_arriostrada is True:
        if any(v is not None for v in (KyLy_mm, KtLt_mm, Cb)):
            raise ValueError("Con la aleta comprimida arriostrada de forma continua no aplica el pandeo lateral-"
                             "torsional: no pase KyLy, KtLt ni Cb (F.4.3.3.1.2.1).")
        ltb = None
    elif aleta_comprimida_arriostrada is False:
        if any(v is None for v in (KyLy_mm, KtLt_mm, Cb)):
            raise ValueError("Sin arriostramiento lateral continuo de la aleta comprimida se exige KyLy, KtLt y Cb para "
                             "el pandeo lateral-torsional (F.4.3.3.1.2.1). Cb = 1 es conservador (F.4.3.3-12).")
        ltb = resistencia_ltb_c(g, Fy, KyLy_mm, KtLt_mm, Cb, E, MU_ACERO)
        candidatos["lateral_torsional"] = (ltb.phi_b * ltb.Mn, ltb.Mn, ltb.phi_b)
        for lim, nombre in ((2.78, "2,78·Fy"), (0.56, "0,56·Fy")):
            if abs(ltb.Fe / (lim * Fy) - 1) <= 0.03:
                borde.append(f"Fe del pandeo lateral-torsional cerca de {nombre}, frontera de F.4.3.3-8/-9.")
    else:
        raise ValueError("aleta_comprimida_arriostrada debe ser True o False (F.4.3.3.1.2).")

    if g.con_pestana:
        if Lm_mm is None:
            raise ValueError("La C con pestaña exige Lm, la distancia entre restricciones al pandeo distorsional "
                             "(F.4.3.3.1.4). Sin restricciones intermedias, Lm es la luz no arriostrada.")
        dist = distorsional_flexion_c(g, Fy, Lm_mm, kphi_N, E, MU_ACERO)
        candidatos["distorsional"] = (dist.phi * dist.nominal, dist.nominal, dist.phi)
        if abs(dist.lambda_d - 0.673) <= 0.02:
            borde.append("λd distorsional cerca de 0,673, frontera de F.4.3.3-28/-29.")
    else:
        if Lm_mm is not None or kphi_N != 0.0:
            raise ValueError("La C sin pestaña no tiene rigidizador de borde: el pandeo distorsional no aplica y no se "
                             "aceptan Lm ni kφ (F.4.3.3.1.4).")
        dist = None

    gob = min(candidatos, key=lambda k: candidatos[k][0])
    phi_Mn, Mn, phi = candidatos[gob]
    return _Flexion(sec, ltb, dist, phi_Mn, Mn, phi, gob, borde)


def flexion_perfil_c(perfil: PerfilC, *, Lm_mm: Optional[float] = None, kphi_N: float = 0.0,
                     KyLy_mm: Optional[float] = None, KtLt_mm: Optional[float] = None, Cb: Optional[float] = None,
                     aleta_comprimida_arriostrada: bool) -> ResultadoMotor:
    """φbMn = mín(sección; lateral-torsional; distorsional). kφ en N·mm/mm/rad (= N); 0 si la aleta comprimida no
    tiene restricción rotacional (F.4.3.3.1.4)."""
    g = perfil.geometria()
    f = _flexion(perfil, Lm_mm=Lm_mm, kphi_N=kphi_N, KyLy_mm=KyLy_mm, KtLt_mm=KtLt_mm, Cb=Cb,
                 aleta_comprimida_arriostrada=aleta_comprimida_arriostrada)
    borde, notas = _en_borde(g)
    s = f.seccion
    estados = {"seccion": {"phi_Mn_kNm": s.phi_b * s.Mn / 1e6, "Mn_kNm": s.Mn / 1e6, "phi_b": s.phi_b,
                           "Se_mm3": s.Se, "Se_sobre_Sx": s.Se / s.Sx_bruto, "y_eje_neutro_mm": s.y_eje_neutro,
                           "fibra_que_fluye": s.fibra_que_fluye, "anchos_efectivos": s.anchos}}
    supuestos = SUPUESTOS_SECCION + [
        "Flexión alrededor del eje fuerte con la aleta superior en compresión.",
        "Esfuerzo de la aleta comprimida igual al de la fibra extrema (conservador).",
    ]
    if f.ltb is not None:
        r = f.ltb
        estados["lateral_torsional"] = {"phi_Mn_kNm": r.phi_b * r.Mn / 1e6, "Mn_kNm": r.Mn / 1e6, "Fe_MPa": r.Fe,
                                        "Fc_MPa": r.Fc, "Sc_mm3": r.Sc, "rango": r.rango, "Cb": Cb}
        supuestos.append("G = E/(2(1+μ)): el corpus no fija G para F.4.")
    else:
        supuestos.append("Aleta comprimida arriostrada lateralmente de forma continua (declarado por quien llama): "
                         "no aplica el pandeo lateral-torsional (F.4.3.3.1.2).")
    if f.dist is not None:
        d = f.dist
        estados["distorsional"] = {"phi_Mn_kNm": d.phi * d.nominal / 1e6, "Mn_kNm": d.nominal / 1e6, "Fd_MPa": d.Fd,
                                   "Lcr_mm": d.Lcr, "L_mm": d.L, "beta": d.beta, "lambda_d": d.lambda_d,
                                   "rigideces": d.rigideces}
        supuestos += SUPUESTOS_DISTORSIONAL + [f"kφ = {kphi_N} N·mm/mm/rad declarado por quien llama."]
    return ResultadoMotor(
        valor={"phi_Mn_kNm": f.phi_Mn / 1e6, "Mn_kNm": f.Mn / 1e6, "phi_b": f.phi_b, "gobierna": f.gobierna,
               "Sx_bruto_mm3": s.Sx_bruto, "estados_limite": estados},
        unidad_si="kN·m",
        ecuacion="φbMn = mín[φb·Se·Fy (F.4.3.3-1); 0,90·Sc·Fc (F.4.3.3-7); 0,90·Mn distorsional (F.4.3.3-28/-29)]",
        referencia_normativa="NSR-10 F.4.3.3.1.1, F.4.3.3.1.2.1, F.4.3.3.1.4(b), F.4.2",
        supuestos=supuestos,
        en_borde_dominio=borde or bool(f.borde),
        advertencias=notas + f.borde,
    )


def cortante_perfil_c(perfil: PerfilC, a_sobre_h: Optional[float] = None) -> ResultadoMotor:
    g = perfil.geometria()
    kv = coeficiente_kv(a_sobre_h)
    r = resistencia_cortante(g.w_alma, g.t, perfil.Fy_MPa, kv, perfil.E_MPa, MU_ACERO)
    borde, notas = _en_borde(g)
    lim = math.sqrt(perfil.E_MPa * kv / perfil.Fy_MPa)
    esb = g.w_alma / g.t
    if any(abs(esb - c) <= 0.02 * c for c in (lim, 1.51 * lim)):
        borde, notas = True, notas + ["h/t está en la frontera entre dos rangos de Fv (F.4.3.3-45 a -47)."]
    return ResultadoMotor(
        valor={"phi_Vn_kN": r.phi_v * r.Vn / 1e3, "Vn_kN": r.Vn / 1e3, "phi_v": r.phi_v, "Fv_MPa": r.Fv,
               "kv": r.kv, "rango": r.rango},
        unidad_si="kN",
        ecuacion="Vn = Aw·Fv, Aw = h·t (F.4.3.3-44, -48); Fv por F.4.3.3-45 a -47",
        referencia_normativa="NSR-10 F.4.3.3.2.1",
        supuestos=SUPUESTOS_SECCION + ["Alma sin huecos, de una sola lámina."],
        en_borde_dominio=borde,
        advertencias=notas,
    )


def tension_perfil_c(perfil: PerfilC, An_mm2: float) -> ResultadoMotor:
    g = perfil.geometria()
    r = resistencia_tension(g.propiedades().A, An_mm2, perfil.Fy_MPa, perfil.Fu_MPa)
    return ResultadoMotor(
        valor={"phi_Tn_kN": r.phi_Tn / 1e3, "Tn_fluencia_kN": r.Tn_fluencia / 1e3, "Tn_rotura_kN": r.Tn_rotura / 1e3,
               "gobierna": r.gobierna},
        unidad_si="kN",
        ecuacion="φTn = mín(0,90·Ag·Fy ; 0,75·An·Fu) (F.4.3.2-1, -2)",
        referencia_normativa="NSR-10 F.4.3.2",
        supuestos=SUPUESTOS_SECCION + ["An es la que declara quien llama."],
        en_borde_dominio=False,
        advertencias=[ADV_CONEXION],
    )


@dataclass(frozen=True)
class _Compresion:
    global_local: object
    dist: object | None
    phi_Pn: float
    Pn: float
    gobierna: str


def _compresion(perfil: PerfilC, KxLx_mm: float, KyLy_mm: float, KtLt_mm: float, Lm_mm: Optional[float],
                kphi_N: float) -> _Compresion:
    g = perfil.geometria()
    r = resistencia_compresion_c(g, perfil.Fy_MPa, KxLx_mm, KyLy_mm, KtLt_mm, perfil.E_MPa, MU_ACERO)
    cand = {"global_y_local": (r.phi_c * r.Pn, r.Pn)}
    if g.con_pestana:
        if Lm_mm is None:
            raise ValueError("La C con pestaña exige Lm, la distancia entre restricciones al pandeo distorsional "
                             "(F.4.3.4.2). Sin restricciones intermedias, Lm es la longitud del miembro.")
        d = distorsional_compresion_c(g, perfil.Fy_MPa, Lm_mm, kphi_N, perfil.E_MPa, MU_ACERO)
        cand["distorsional"] = (d.phi * d.nominal, d.nominal)
    else:
        if Lm_mm is not None or kphi_N != 0.0:
            raise ValueError("La C sin pestaña no tiene rigidizador de borde: el pandeo distorsional no aplica y no se "
                             "aceptan Lm ni kφ (F.4.3.4.2).")
        d = None
    gob = min(cand, key=lambda k: cand[k][0])
    return _Compresion(r, d, cand[gob][0], cand[gob][1], gob)


def compresion_perfil_c(perfil: PerfilC, KxLx_mm: float, KyLy_mm: float, KtLt_mm: float, *,
                        Lm_mm: Optional[float] = None, kphi_N: float = 0.0) -> ResultadoMotor:
    g = perfil.geometria()
    c = _compresion(perfil, KxLx_mm, KyLy_mm, KtLt_mm, Lm_mm, kphi_N)
    r = c.global_local
    borde, notas = _en_borde(g)
    if abs(r.lambda_c - 1.5) <= 0.03:
        borde, notas = True, notas + ["λc está en la frontera entre F.4.3.4-2 y F.4.3.4-3."]
    if r.esbeltez_max > 200:
        notas = notas + [f"KL/r = {r.esbeltez_max:.0f} > 200: esbeltez excesiva para un miembro en compresión."]
        borde = True
    estados = {"global_y_local": {"phi_Pn_kN": r.phi_c * r.Pn / 1e3, "Pn_kN": r.Pn / 1e3, "phi_c": r.phi_c,
                                  "Fn_MPa": r.Fn, "Fe_MPa": r.Fe, "lambda_c": r.lambda_c, "modo": r.modo,
                                  "Ae_mm2": r.Ae, "sigma_ey_MPa": r.sigma_ey, "sigma_ex_MPa": r.sigma_ex,
                                  "sigma_t_MPa": r.sigma_t}}
    supuestos = SUPUESTOS_SECCION + [
        "Carga axial por el centroide de la sección efectiva (F.4.3.4.1).",
        "G = E/(2(1+μ)): el corpus no fija G para F.4.",
    ]
    if c.dist is not None:
        d = c.dist
        estados["distorsional"] = {"phi_Pn_kN": d.phi * d.nominal / 1e3, "Pn_kN": d.nominal / 1e3, "Fd_MPa": d.Fd,
                                   "Lcr_mm": d.Lcr, "L_mm": d.L, "beta": d.beta, "lambda_d": d.lambda_d,
                                   "rigideces": d.rigideces}
        supuestos += [SUPUESTOS_DISTORSIONAL[0], f"kφ = {kphi_N} N·mm/mm/rad declarado por quien llama."]
        if abs(d.lambda_d - 0.561) <= 0.02:
            borde, notas = True, notas + ["λd distorsional cerca de 0,561, frontera de F.4.3.4-12/-13."]
    return ResultadoMotor(
        valor={"phi_Pn_kN": c.phi_Pn / 1e3, "Pn_kN": c.Pn / 1e3, "phi_c": PHI_C, "gobierna": c.gobierna,
               "A_mm2": r.A, "estados_limite": estados},
        unidad_si="kN",
        ecuacion="φcPn = 0,85·mín[Ae·Fn (F.4.3.4-1); Pn distorsional (F.4.3.4-12/-13)]",
        referencia_normativa="NSR-10 F.4.3.4.1, F.4.3.4.2(b), F.4.3.3-13 a -15",
        supuestos=supuestos,
        en_borde_dominio=borde,
        advertencias=notas,
    )


def verificar_viga_c(perfil: PerfilC, Mu_kNm: float, Vu_kN: float, *, aleta_comprimida_arriostrada: bool,
                     Lm_mm: Optional[float] = None, kphi_N: float = 0.0, KyLy_mm: Optional[float] = None,
                     KtLt_mm: Optional[float] = None, Cb: Optional[float] = None) -> ResultadoMotor:
    """Flexión (los tres estados límite), cortante e interacción (F.4.3.3-54) para una viga de alma no reforzada.

    F.4.3.3-54 usa Mnxo, la resistencia de la sección (F.4.3.3.1.1); el pandeo lateral-torsional y el distorsional
    entran en la razón de flexión."""
    rf = flexion_perfil_c(perfil, Lm_mm=Lm_mm, kphi_N=kphi_N, KyLy_mm=KyLy_mm, KtLt_mm=KtLt_mm, Cb=Cb,
                          aleta_comprimida_arriostrada=aleta_comprimida_arriostrada)
    rv = cortante_perfil_c(perfil)
    pm, pv = rf.valor["phi_Mn_kNm"], rv.valor["phi_Vn_kN"]
    pmxo = rf.valor["estados_limite"]["seccion"]["phi_Mn_kNm"]
    inter = interaccion_flexion_cortante(Mu_kNm, Vu_kN, pmxo, pv)
    razones = {"flexion": Mu_kNm / pm, "cortante": Vu_kN / pv, "interaccion": inter}
    gobierna = max(razones, key=razones.get)
    return ResultadoMotor(
        valor={"cumple": all(v <= 1.0 for v in razones.values()), "razones": razones, "gobierna": gobierna,
               "phi_Mn_kNm": pm, "flexion_gobierna": rf.valor["gobierna"], "phi_Vn_kN": pv},
        unidad_si="adimensional (razón demanda/capacidad)",
        ecuacion="Mu ≤ φbMn ; Vu ≤ φvVn ; √[(Mu/φbMnxo)² + (Vu/φvVn)²] ≤ 1,0 (F.4.3.3-54)",
        referencia_normativa="NSR-10 F.4.3.3.1, F.4.3.3.2.1, F.4.3.3.3",
        supuestos=rf.supuestos + ["Alma no reforzada: aplica F.4.3.3-54 (no F.4.3.3-55)."],
        en_borde_dominio=rf.en_borde_dominio or rv.en_borde_dominio or abs(max(razones.values()) - 1.0) <= 0.02,
        advertencias=list(dict.fromkeys(rf.advertencias + rv.advertencias + [ADV_APOYOS])),
    )


def flexocompresion_perfil_c(perfil: PerfilC, Pu_kN: float, Mux_kNm: float, KxLx_mm: float, KyLy_mm: float,
                             KtLt_mm: float, Cmx: float, *, aleta_comprimida_arriostrada: bool,
                             Cb: Optional[float] = None, Lm_mm: Optional[float] = None,
                             kphi_N: float = 0.0) -> ResultadoMotor:
    """F.4.3.5.2, flexión alrededor del eje fuerte. Análisis elástico de primer orden: Cmx de coeficiente_cm."""
    g, p = perfil.geometria(), perfil.geometria().propiedades()
    c = _compresion(perfil, KxLx_mm, KyLy_mm, KtLt_mm, Lm_mm, kphi_N)
    lt = (KyLy_mm, KtLt_mm, Cb) if aleta_comprimida_arriostrada is False else (None, None, None)
    f = _flexion(perfil, Lm_mm=Lm_mm, kphi_N=kphi_N, KyLy_mm=lt[0], KtLt_mm=lt[1], Cb=lt[2],
                 aleta_comprimida_arriostrada=aleta_comprimida_arriostrada)
    Ae_fy = area_efectiva_compresion_c(g, perfil.Fy_MPa, perfil.E_MPa, MU_ACERO)
    phi_Pno = PHI_C * Ae_fy * perfil.Fy_MPa                                                 # Pno con Fn = Fy
    PEX = math.pi ** 2 * perfil.E_MPa * p.Ix / KxLx_mm ** 2                                  # F.4.3.5-9
    r = flexo_compresion_uniaxial(Pu_kN * 1e3, Mux_kNm * 1e6, c.phi_Pn, phi_Pno, f.phi_Mn, PEX, Cmx)
    borde, notas = _en_borde(g)
    return ResultadoMotor(
        valor={"cumple": r.razon <= 1.0, "razon": r.razon, "gobierna": r.gobierna, "ecuaciones": r.ecuaciones,
               "razones_individuales": r.razones_individuales, "phi_Pn_kN": c.phi_Pn / 1e3,
               "phi_Pno_kN": phi_Pno / 1e3, "phi_Mnx_kNm": f.phi_Mn / 1e6, "PEX_kN": PEX / 1e3,
               "alfa_x": 1 - Pu_kN * 1e3 / PEX, "compresion_gobierna": c.gobierna, "flexion_gobierna": f.gobierna},
        unidad_si="adimensional (razón demanda/capacidad)",
        ecuacion="P̄/φcPn + Cmx·M̄x/(φbMnx·αx) ≤ 1 (F.4.3.5-4); P̄/φcPno + M̄x/φbMnx ≤ 1 (F.4.3.5-5); "
                 "o F.4.3.5-6 si P̄/φcPn ≤ 0,15",
        referencia_normativa="NSR-10 F.4.3.5.2.1, F.4.3.4, F.4.3.3.1",
        supuestos=SUPUESTOS_SECCION + [
            "Solicitaciones de un análisis elástico de primer orden, con Cmx declarado por quien llama.",
            "Flexión solo alrededor del eje fuerte (M̄y = 0).",
            "No se agrega momento por el corrimiento del centroide efectivo: la norma lo exige solo en ángulos.",
        ],
        en_borde_dominio=borde or abs(r.razon - 1.0) <= 0.02,
        advertencias=notas + f.borde,
    )


def flexotension_perfil_c(perfil: PerfilC, Tu_kN: float, Mux_kNm: float, An_mm2: float, *,
                          aleta_comprimida_arriostrada: bool, KyLy_mm: Optional[float] = None,
                          KtLt_mm: Optional[float] = None, Cb: Optional[float] = None,
                          Lm_mm: Optional[float] = None, kphi_N: float = 0.0) -> ResultadoMotor:
    """F.4.3.5.1, flexión alrededor del eje fuerte. φt = 0,95 con Tn = Ag·Fy en las ecuaciones de interacción; la
    tensión sola se verifica además con F.4.3.2 (incluye la rotura en la sección neta)."""
    g, p = perfil.geometria(), perfil.geometria().propiedades()
    f = _flexion(perfil, Lm_mm=Lm_mm, kphi_N=kphi_N, KyLy_mm=KyLy_mm, KtLt_mm=KtLt_mm, Cb=Cb,
                 aleta_comprimida_arriostrada=aleta_comprimida_arriostrada)
    rt = resistencia_tension(p.A, An_mm2, perfil.Fy_MPa, perfil.Fu_MPa)
    Sft = p.Ix / (p.yc + g.t / 2)                                                            # fibra extrema a tensión
    phi_Mnxt = f.seccion.phi_b * Sft * perfil.Fy_MPa                                         # F.4.3.5-3
    r = flexo_tension_uniaxial(Tu_kN * 1e3, Mux_kNm * 1e6, PHI_T_COMBINADA * p.A * perfil.Fy_MPa, f.phi_Mn, phi_Mnxt)
    razon_t = Tu_kN * 1e3 / rt.phi_Tn
    razon = max(r.razon, razon_t)
    borde, notas = _en_borde(g)
    return ResultadoMotor(
        valor={"cumple": razon <= 1.0, "razon": razon, "ecuaciones": r.ecuaciones,
               "razon_tension_F_4_3_2": razon_t, "gobierna": r.gobierna if r.razon >= razon_t else "tension_F.4.3.2",
               "phi_Mnx_kNm": f.phi_Mn / 1e6, "phi_Mnxt_kNm": phi_Mnxt / 1e6, "flexion_gobierna": f.gobierna},
        unidad_si="adimensional (razón demanda/capacidad)",
        ecuacion="M̄x/φbMnxt + T̄/φtTn ≤ 1 (F.4.3.5-1); M̄x/φbMnx − T̄/φtTn ≤ 1 (F.4.3.5-2); Tu ≤ φTn (F.4.3.2)",
        referencia_normativa="NSR-10 F.4.3.5.1.1, F.4.3.2, F.4.3.3.1",
        supuestos=SUPUESTOS_SECCION + ["Flexión solo alrededor del eje fuerte (M̄y = 0).",
                                       "Tn = Ag·Fy en las ecuaciones de interacción; An declarada por quien llama."],
        en_borde_dominio=borde or abs(razon - 1.0) <= 0.02,
        advertencias=notas + f.borde + [ADV_CONEXION],
    )


def arrugamiento_perfil_c(perfil: PerfilC, Pu_kN: float, N_mm: float, R_mm: float, coeficientes: dict, *,
                          Mu_kNm: Optional[float] = None, Lo_mm: Optional[float] = None) -> ResultadoMotor:
    """Arrugamiento del alma bajo una carga concentrada o reacción (F.4.3.3-56/-57) y, con Mu, su interacción con la
    flexión (F.4.3.3-61). `coeficientes` = {C, CR, CN, Ch, phi_w, R_t_max, fila} de la Tabla F.4.3.3-2."""
    g = perfil.geometria()
    try:
        coef = CoeficientesArrugamiento(**coeficientes)
    except TypeError as exc:
        raise ValueError(f"Coeficientes de la Tabla F.4.3.3-2 incompletos o desconocidos: {exc}") from exc
    r = arrugamiento_alma(g.w_alma, g.t, perfil.Fy_MPa, N_mm, R_mm, coef, Lo=Lo_mm)
    phi_Pn = coef.phi_w * r.Pn
    razones = {"arrugamiento": Pu_kN * 1e3 / phi_Pn}
    valor = {"phi_Pn_kN": phi_Pn / 1e3, "Pn_kN": r.Pn / 1e3, "phi_w": coef.phi_w, "alfa_voladizo": r.alfa,
             "relaciones": r.relaciones, "fila_tabla": coef.fila}
    if Mu_kNm is not None:
        sec = resistencia_flexion_c(g, perfil.Fy_MPa, perfil.E_MPa, MU_ACERO)
        razones["flexion_seccion"] = Mu_kNm * 1e6 / (sec.phi_b * sec.Mn)
        razones["interaccion_F.4.3.3-61"] = interaccion_flexion_arrugamiento(Pu_kN * 1e3, Mu_kNm * 1e6, r.Pn, sec.Mn)
    gob = max(razones, key=razones.get)
    valor.update({"razones": razones, "gobierna": gob, "cumple": all(v <= 1.0 for v in razones.values())})
    borde, notas = _en_borde(g)
    return ResultadoMotor(
        valor=valor,
        unidad_si="kN",
        ecuacion="Pn = C·t²·Fy·senθ·(1 − CR√(R/t))(1 + CN√(N/t))(1 − Ch√(h/t)) (F.4.3.3-56); "
                 "0,91·P̄/Pn + M̄/Mnxo ≤ 1,33φ (F.4.3.3-61)",
        referencia_normativa="NSR-10 F.4.3.3.4.1, Tabla F.4.3.3-2, F.4.3.3.5.1(a)",
        supuestos=SUPUESTOS_SECCION + [
            f"Coeficientes de la Tabla F.4.3.3-2 declarados por quien llama: {coef.fila}.",
            "R es el radio interior real de doblez (las propiedades de sección sí usan esquinas rectas).",
            "Alma sin huecos, θ = 90°, alma sencilla no reforzada.",
        ],
        en_borde_dominio=borde or abs(max(razones.values()) - 1.0) <= 0.02,
        advertencias=notas,
    )
