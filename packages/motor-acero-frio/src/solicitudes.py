"""Cuerpos de las solicitudes HTTP de motor-acero-frio (#81). Cada uno llama a una función de contrato_api."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .contrato_api import (
    PerfilC,
    arrugamiento_perfil_c,
    compresion_perfil_c,
    flexion_perfil_c,
    flexocompresion_perfil_c,
    flexotension_perfil_c,
    tension_perfil_c,
    verificar_viga_c,
)

_CFG = ConfigDict(extra="forbid")
_L = dict(gt=0, le=30000, allow_inf_nan=False)           # longitudes en mm


class _ConDistorsional(BaseModel):
    model_config = _CFG
    Lm_mm: Optional[float] = Field(None, description="Distancia entre restricciones al pandeo distorsional", **_L)
    kphi_N: float = Field(0.0, ge=0, le=1e6, allow_inf_nan=False,
                          description="Rigidez rotacional de restricción (N·mm/mm/rad); 0 sin restricción")


class _ConLTB(_ConDistorsional):
    aleta_comprimida_arriostrada: bool
    KyLy_mm: Optional[float] = Field(None, **_L)
    KtLt_mm: Optional[float] = Field(None, **_L)
    Cb: Optional[float] = Field(None, ge=1.0, le=5.0, allow_inf_nan=False)
    M1_M2: Optional[float] = Field(None, ge=-1.0, le=1.0, allow_inf_nan=False,
                                   description="β distorsional por gradiente (F.4.3.3-38); sin él, β = 1")


class SolicitudFlexion(_ConLTB):
    perfil: PerfilC

    def ejecutar(self):
        return flexion_perfil_c(self.perfil, Lm_mm=self.Lm_mm, kphi_N=self.kphi_N, KyLy_mm=self.KyLy_mm,
                                KtLt_mm=self.KtLt_mm, Cb=self.Cb, M1_M2=self.M1_M2,
                                aleta_comprimida_arriostrada=self.aleta_comprimida_arriostrada)


class SolicitudViga(_ConLTB):
    perfil: PerfilC
    Mu_kNm: float = Field(..., ge=0, le=1e4, allow_inf_nan=False)
    Vu_kN: float = Field(..., ge=0, le=1e4, allow_inf_nan=False)

    def ejecutar(self):
        return verificar_viga_c(self.perfil, self.Mu_kNm, self.Vu_kN, Lm_mm=self.Lm_mm, kphi_N=self.kphi_N,
                                KyLy_mm=self.KyLy_mm, KtLt_mm=self.KtLt_mm, Cb=self.Cb, M1_M2=self.M1_M2,
                                aleta_comprimida_arriostrada=self.aleta_comprimida_arriostrada)


class SolicitudCompresion(_ConDistorsional):
    perfil: PerfilC
    KxLx_mm: float = Field(..., **_L)
    KyLy_mm: float = Field(..., **_L)
    KtLt_mm: float = Field(..., **_L)

    def ejecutar(self):
        return compresion_perfil_c(self.perfil, self.KxLx_mm, self.KyLy_mm, self.KtLt_mm, Lm_mm=self.Lm_mm,
                                   kphi_N=self.kphi_N)


class SolicitudTension(BaseModel):
    model_config = _CFG
    perfil: PerfilC
    An_mm2: float = Field(..., gt=0, le=1e5, allow_inf_nan=False)

    def ejecutar(self):
        return tension_perfil_c(self.perfil, self.An_mm2)


class SolicitudFlexocompresion(_ConDistorsional):
    perfil: PerfilC
    Pu_kN: float = Field(..., ge=0, le=1e4, allow_inf_nan=False)
    Mux_kNm: float = Field(..., ge=0, le=1e4, allow_inf_nan=False)
    KxLx_mm: float = Field(..., **_L)
    KyLy_mm: float = Field(..., **_L)
    KtLt_mm: float = Field(..., **_L)
    Cmx: float = Field(..., gt=0, le=1.0, allow_inf_nan=False, description="F.4.3.5.2.1; use coeficiente_cm")
    aleta_comprimida_arriostrada: bool
    Cb: Optional[float] = Field(None, ge=1.0, le=5.0, allow_inf_nan=False)

    def ejecutar(self):
        return flexocompresion_perfil_c(self.perfil, self.Pu_kN, self.Mux_kNm, self.KxLx_mm, self.KyLy_mm,
                                        self.KtLt_mm, self.Cmx, aleta_comprimida_arriostrada=self.aleta_comprimida_arriostrada,
                                        Cb=self.Cb, Lm_mm=self.Lm_mm, kphi_N=self.kphi_N)


class SolicitudFlexotension(_ConLTB):
    perfil: PerfilC
    Tu_kN: float = Field(..., ge=0, le=1e4, allow_inf_nan=False)
    Mux_kNm: float = Field(..., ge=0, le=1e4, allow_inf_nan=False)
    An_mm2: float = Field(..., gt=0, le=1e5, allow_inf_nan=False)

    def ejecutar(self):
        return flexotension_perfil_c(self.perfil, self.Tu_kN, self.Mux_kNm, self.An_mm2,
                                     aleta_comprimida_arriostrada=self.aleta_comprimida_arriostrada,
                                     KyLy_mm=self.KyLy_mm, KtLt_mm=self.KtLt_mm, Cb=self.Cb, Lm_mm=self.Lm_mm,
                                     kphi_N=self.kphi_N)


class SolicitudArrugamiento(BaseModel):
    model_config = _CFG
    perfil: PerfilC
    Pu_kN: float = Field(..., ge=0, le=1e4, allow_inf_nan=False)
    N_mm: float = Field(..., gt=0, le=2000, allow_inf_nan=False)
    R_mm: float = Field(..., ge=0, le=100, allow_inf_nan=False)
    apoyo: Literal["sujeta", "no_sujeta"]
    carga: Literal["una_aleta", "dos_aletas"]
    posicion: Literal["extremo", "interior"]
    Mu_kNm: Optional[float] = Field(None, ge=0, le=1e4, allow_inf_nan=False)
    Lo_mm: Optional[float] = Field(None, **_L)

    def ejecutar(self):
        return arrugamiento_perfil_c(self.perfil, self.Pu_kN, self.N_mm, self.R_mm, apoyo=self.apoyo,
                                     carga=self.carga, posicion=self.posicion, Mu_kNm=self.Mu_kNm, Lo_mm=self.Lo_mm)


ESTADOS: dict[str, type[BaseModel]] = {
    "flexion": SolicitudFlexion,
    "viga": SolicitudViga,
    "compresion": SolicitudCompresion,
    "tension": SolicitudTension,
    "flexocompresion": SolicitudFlexocompresion,
    "flexotension": SolicitudFlexotension,
    "arrugamiento": SolicitudArrugamiento,
}
