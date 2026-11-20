"""Salida con contrato uniforme de motor-exploracion (#273): pre-diseño del estudio geotécnico."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

from . import alertas, sondeos  # noqa: E402
from . import categoria as cat_mod  # noqa: E402

Cimentacion = Literal["zapatas", "losa", "pilote_excavado", "pilote_hincado"]
Suelo = Literal["cohesivo", "granular", "mixto", "desconocido"]


class TerrenoLote(BaseModel):
    """Métricas del lote ya calculadas por /sitio. El motor nunca recibe coordenadas."""
    model_config = ConfigDict(strict=True)

    ubicacion: Literal["lote", "municipio"] = Field(..., description="'municipio' si el usuario no dio el punto del lote")
    relieve_local_1km_m: Optional[float] = Field(None, ge=0, le=5000, allow_inf_nan=False,
                                                 description="Cota del lote − cota mínima a ≤ 1 km (DEM GLO-90)")
    fraccion_pendiente_suave_5km: Optional[float] = Field(None, ge=0, le=1, allow_inf_nan=False,
                                                          description="Fracción de la vecindad de 5 km con pendiente < 8 %")
    relieve_5km_m: Optional[float] = Field(None, ge=0, le=9000, allow_inf_nan=False,
                                           description="Máximo − mínimo en la vecindad de 5 km")
    nivel_freatico_medido_m: Optional[float] = Field(None, ge=0, le=200, allow_inf_nan=False)
    eventos_remocion_5km: Optional[int] = Field(None, ge=0, le=100000)

    @model_validator(mode="after")
    def _municipio_sin_metricas(self):
        if self.ubicacion == "municipio" and any(v is not None for v in (
                self.relieve_local_1km_m, self.fraccion_pendiente_suave_5km, self.relieve_5km_m,
                self.eventos_remocion_5km)):
            raise ValueError("Con ubicación 'municipio' no se aceptan métricas del lote: serían de la cabecera (H8).")
        return self


class SolicitudExploracion(BaseModel):
    model_config = ConfigDict(strict=True)

    niveles: int = Field(..., ge=1, le=200, description="Total de niveles, incluidos sótanos, terrazas y pisos técnicos")
    carga_max_servicio_kn: float = Field(..., gt=0, le=1e6, allow_inf_nan=False,
                                         description="Carga máxima de servicio (muerta + viva), Tabla H.3.1-1")
    planta_ancho_m: Optional[float] = Field(None, gt=0, le=1000, allow_inf_nan=False)
    planta_largo_m: Optional[float] = Field(None, gt=0, le=1000, allow_inf_nan=False)
    profundidad_excavacion_m: float = Field(..., ge=0, le=100, allow_inf_nan=False)
    cimentacion: Cimentacion
    suelo: Suelo = Field(..., description="Lo que se sabe del suelo antes del estudio; 'desconocido' es válido")
    amenaza_sismica: Literal["baja", "intermedia", "alta"]
    terreno: TerrenoLote

    @model_validator(mode="after")
    def _planta_completa(self):
        if (self.planta_ancho_m is None) != (self.planta_largo_m is None):
            raise ValueError("Dé el ancho y el largo de la planta, o ninguno (NSR-10 H.3.2.5).")
        if self.cimentacion == "losa" and self.planta_ancho_m is None:
            raise ValueError("Con losa de cimentación hay que dar el ancho y el largo de la planta (NSR-10 H.3.2.5).")
        return self


def pre_disenar_exploracion(s: SolicitudExploracion) -> dict[str, ResultadoMotor]:
    c = cat_mod.categoria(s.niveles, s.carga_max_servicio_kn)
    adv_cat = []
    if s.planta_largo_m is not None and max(s.planta_ancho_m, s.planta_largo_m) > 40.0:
        adv_cat.append("La planta supera 40 m: puede requerir dividirse en varias unidades de construcción (NSR-10 "
                       "H.3.1; hasta 80 m solo para construcciones adosadas de categoría baja). Cada unidad lleva su "
                       "exploración.")
    r_cat = ResultadoMotor(
        valor=c, unidad_si="adimensional", ecuacion="categoría = máx(categoría por niveles, categoría por carga)",
        referencia_normativa=cat_mod.REF,
        supuestos=["La carga es la máxima de servicio (muerta + viva por uso) de la unidad de construcción.",
                   "Se evalúa una sola unidad de construcción."],
        en_borde_dominio=c["en_borde"], advertencias=adv_cat)

    e = sondeos.exploracion_minima(c["categoria"], s.planta_ancho_m, s.planta_largo_m, s.cimentacion == "losa",
                                   s.profundidad_excavacion_m)
    adv = ["H.3.2.5 puede incluir criterios adicionales de profundidad que no están transcritos en el corpus de "
           "StructAI: verifíquelos en la norma."]
    if s.cimentacion in ("pilote_excavado", "pilote_hincado"):
        adv.append("Con pilotes, la exploración debe extenderse por debajo de la punta prevista: la profundidad de la "
                   "tabla es un mínimo, no la profundidad del estudio.")
    if s.planta_ancho_m is None:
        adv.append("Sin las dimensiones de la planta no se evaluó el criterio del 10 % del incremento de esfuerzo "
                   "(H.3.2.5 a).")
    r_exp = ResultadoMotor(
        valor=e, unidad_si="m", ecuacion="z = máx(z_tabla, z(Δσ/q = 0,10) Boussinesq centro de planta, 1,5·B losa)",
        referencia_normativa=sondeos.REF,
        supuestos=["Δσ bajo el centro de la planta con carga uniforme (Boussinesq, motor-geotecnia).",
                   "La profundidad se mide desde el nivel inferior de excavación; también se da desde el terreno."],
        en_borde_dominio=c["en_borde"], advertencias=adv)

    t = s.terreno
    nf = alertas.nivel_freatico(t.ubicacion, t.relieve_local_1km_m, t.fraccion_pendiente_suave_5km, t.relieve_5km_m,
                                t.nivel_freatico_medido_m)
    r_nf = ResultadoMotor(
        valor=nf, unidad_si="m", ecuacion="alarma = llanura_Hammond(5 km) ∧ (cota − mín 1 km ≤ 6,5 m)",
        referencia_normativa=alertas.REF_ALERTAS,
        supuestos=["Métricas del DEM Copernicus GLO-90 calculadas en el lote (no en la cabecera).",
                   "Validado solo con niveles medidos en la Orinoquía; otras llanuras quedan sin validar."],
        en_borde_dominio=nf["estado"] in ("alarma", "sin_alarma"),
        advertencias=["La alarma prioriza la medición; no la reemplaza."])

    rec = alertas.recomendaciones(s.cimentacion, s.suelo, s.amenaza_sismica, nf, t.eventos_remocion_5km)
    r_rec = ResultadoMotor(
        valor=rec, unidad_si="adimensional", ecuacion="reglas de decisión con evidencia preregistrada (#273)",
        referencia_normativa=alertas.REF_ALERTAS,
        supuestos=["Los valores en pesos son de los escenarios de H1 y H7 (30 pilotes, INVIAS 2026-1), no del proyecto.",
                   "El suelo declarado antes del estudio puede cambiar con la exploración."],
        en_borde_dominio=s.suelo == "desconocido",
        advertencias=["Socavación (H3) y contexto vial (H6): próximamente."])
    return {"categoria": r_cat, "exploracion_minima": r_exp, "nivel_freatico": r_nf, "recomendaciones": r_rec}
