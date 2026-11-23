"""Contrato uniforme de motor-acero-frio (#81): perfiles C formados en frío según NSR-10 F.4.

Toda salida es un ResultadoMotor. Ninguna entrada física tiene valor por defecto salvo E (F.4.4.6.1.3) y μ
(F.4.3.3.2.1), que son valores de la propia norma. El resultado nunca reemplaza el diseño firmado por un ingeniero.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from .ancho_efectivo import E_ACERO_MPA, MU_ACERO  # noqa: E402
from .elementos import D_W_MAX_TABLA, H_T_MAX_ALMA, W_T_MAX_ALETA_PESTANA, W_T_MAX_NO_RIGIDIZADO  # noqa: E402
from .flexion import interaccion_flexion_cortante, resistencia_flexion_c  # noqa: E402
from .miembros import (  # noqa: E402
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
ADV_DISTORSIONAL = ("No se verificó el pandeo distorsional (F.4.3.3.1.4 en flexión, F.4.3.4.2 en compresión). En "
                    "secciones C con pestaña puede gobernar: verificarlo antes de usar el resultado.")
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


def flexion_perfil_c(perfil: PerfilC, *, aleta_comprimida_arriostrada: bool) -> ResultadoMotor:
    g = perfil.geometria()
    r = resistencia_flexion_c(g, perfil.Fy_MPa, aleta_comprimida_arriostrada=aleta_comprimida_arriostrada,
                              E=perfil.E_MPa, mu=MU_ACERO)
    borde, notas = _en_borde(g)
    return ResultadoMotor(
        valor={"phi_Mn_kNm": r.phi_b * r.Mn / 1e6, "Mn_kNm": r.Mn / 1e6, "phi_b": r.phi_b, "Se_mm3": r.Se,
               "Sx_bruto_mm3": r.Sx_bruto, "Se_sobre_Sx": r.Se / r.Sx_bruto, "y_eje_neutro_mm": r.y_eje_neutro,
               "fibra_que_fluye": r.fibra_que_fluye, "anchos_efectivos": r.anchos},
        unidad_si="kN·m",
        ecuacion="Mn = Se·Fy (F.4.3.3-1); anchos efectivos F.4.2.2.3, F.4.2.3.2 y F.4.2.4",
        referencia_normativa="NSR-10 F.4.3.3.1.1 (Procedimiento 1), F.4.2",
        supuestos=SUPUESTOS_SECCION + [
            "Flexión alrededor del eje fuerte con la aleta superior en compresión.",
            "Esfuerzo de la aleta comprimida igual al de la fibra extrema (conservador).",
            "Aleta comprimida arriostrada lateralmente de forma continua (declarado por quien llama): no se "
            "verifica pandeo lateral-torsional (F.4.3.3.1.2).",
        ],
        en_borde_dominio=borde,
        advertencias=notas + [ADV_DISTORSIONAL],
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
        advertencias=["No se verificó la rotura en la conexión (F.4.3.2 c): depende del diseño de la conexión "
                      "(F.4.5), que este motor no cubre todavía."],
    )


def compresion_perfil_c(perfil: PerfilC, KxLx_mm: float, KyLy_mm: float, KtLt_mm: float) -> ResultadoMotor:
    g = perfil.geometria()
    r = resistencia_compresion_c(g, perfil.Fy_MPa, KxLx_mm, KyLy_mm, KtLt_mm, perfil.E_MPa, MU_ACERO)
    borde, notas = _en_borde(g)
    if abs(r.lambda_c - 1.5) <= 0.03:
        borde, notas = True, notas + ["λc está en la frontera entre F.4.3.4-2 y F.4.3.4-3."]
    if r.esbeltez_max > 200:
        notas = notas + [f"KL/r = {r.esbeltez_max:.0f} > 200: esbeltez excesiva para un miembro en compresión."]
        borde = True
    return ResultadoMotor(
        valor={"phi_Pn_kN": r.phi_c * r.Pn / 1e3, "Pn_kN": r.Pn / 1e3, "phi_c": r.phi_c, "Fn_MPa": r.Fn,
               "Fe_MPa": r.Fe, "lambda_c": r.lambda_c, "modo": r.modo, "Ae_mm2": r.Ae, "A_mm2": r.A,
               "sigma_ey_MPa": r.sigma_ey, "sigma_ex_MPa": r.sigma_ex, "sigma_t_MPa": r.sigma_t},
        unidad_si="kN",
        ecuacion="Pn = Ae·Fn (F.4.3.4-1); Fn por F.4.3.4-2/-3; Fe = mín(F.4.3.4-5 eje débil ; F.4.3.4-6)",
        referencia_normativa="NSR-10 F.4.3.4.1, F.4.3.4.1.1, F.4.3.4.1.2, F.4.3.3-13 a -15",
        supuestos=SUPUESTOS_SECCION + [
            "Carga axial por el centroide de la sección efectiva (F.4.3.4.1).",
            "G = E/(2(1+μ)): el corpus no fija G para F.4.",
        ],
        en_borde_dominio=borde,
        advertencias=notas + [ADV_DISTORSIONAL],
    )


def verificar_viga_c(perfil: PerfilC, Mu_kNm: float, Vu_kN: float, *, aleta_comprimida_arriostrada: bool) -> ResultadoMotor:
    """Flexión, cortante e interacción (F.4.3.3-54) para una viga de alma no reforzada."""
    rf = flexion_perfil_c(perfil, aleta_comprimida_arriostrada=aleta_comprimida_arriostrada)
    rv = cortante_perfil_c(perfil)
    pm, pv = rf.valor["phi_Mn_kNm"], rv.valor["phi_Vn_kN"]
    inter = interaccion_flexion_cortante(Mu_kNm, Vu_kN, pm, pv)
    razones = {"flexion": Mu_kNm / pm, "cortante": Vu_kN / pv, "interaccion": inter}
    gobierna = max(razones, key=razones.get)
    return ResultadoMotor(
        valor={"cumple": all(v <= 1.0 for v in razones.values()), "razones": razones, "gobierna": gobierna,
               "phi_Mn_kNm": pm, "phi_Vn_kN": pv},
        unidad_si="adimensional (razón demanda/capacidad)",
        ecuacion="Mu ≤ φbMn ; Vu ≤ φvVn ; √[(Mu/φbMnxo)² + (Vu/φvVn)²] ≤ 1,0 (F.4.3.3-54)",
        referencia_normativa="NSR-10 F.4.3.3.1.1, F.4.3.3.2.1, F.4.3.3.3",
        supuestos=rf.supuestos + ["Alma no reforzada: aplica F.4.3.3-54 (no F.4.3.3-55)."],
        en_borde_dominio=rf.en_borde_dominio or rv.en_borde_dominio or abs(max(razones.values()) - 1.0) <= 0.02,
        advertencias=list(dict.fromkeys(rf.advertencias + rv.advertencias + [
            "No se verificó el arrugamiento del alma bajo cargas concentradas (F.4.3.3.4) ni deflexiones."])),
    )
