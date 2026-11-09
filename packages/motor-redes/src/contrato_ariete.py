"""Salida con contrato uniforme de motor-redes (#138): golpe de ariete (MOC) en tubería simple."""
import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .ariete import _MAX_TRAMOS, celeridad_korteweg, coeficiente_anclaje, h_vapor_por_altitud, simular_ariete

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

_TOL_MALLA = 0.02              # diferencia relativa del pico entre n y 2n tramos que se tolera sin marcar borde
_BANDA_CRITICA = (0.8, 1.25)   # Tc cerca de 2L/a: la transición cierre rápido/lento hace sensible el pico


class SolicitudAriete(BaseModel):
    model_config = ConfigDict(strict=True)

    longitud_m: float = Field(..., ge=1e-2, le=200000, allow_inf_nan=False)
    diametro_m: float = Field(..., ge=1e-3, le=5, allow_inf_nan=False)
    celeridad_ms: Optional[float] = Field(default=None, gt=0, le=1500, allow_inf_nan=False,
                                          description="Celeridad de la onda; si se omite se calcula con espesor_m y e_tuberia_pa")
    espesor_m: Optional[float] = Field(default=None, gt=0, le=1, allow_inf_nan=False)
    e_tuberia_pa: Optional[float] = Field(default=None, gt=0, le=1e12, allow_inf_nan=False, description="Módulo de elasticidad de la pared")
    poisson: Optional[float] = Field(default=None, gt=0, lt=0.5, allow_inf_nan=False,
                                     description="Relación de Poisson de la pared; obligatoria si la celeridad se calcula")
    anclaje: Optional[Literal["todo", "aguas_arriba", "dilatacion"]] = Field(
        default=None, description="Condición de anclaje de la tubería; obligatoria si la celeridad se calcula")
    altitud_m: float = Field(default=0.0, ge=-500, le=6000, allow_inf_nan=False,
                             description="Altitud del sitio, para la carga de vapor (por defecto nivel del mar)")
    f_darcy: float = Field(..., ge=0, le=0.2, allow_inf_nan=False)
    caudal_m3s: float = Field(..., gt=0, le=100, allow_inf_nan=False, description="Caudal en régimen permanente antes del cierre")
    carga_embalse_m: float = Field(..., ge=-500, le=5000, allow_inf_nan=False, description="Carga manométrica del embalse sobre el eje")
    t_cierre_s: float = Field(..., ge=0, le=1e6, allow_inf_nan=False, description="0 = cierre instantáneo")
    t_fin_s: float = Field(..., gt=0, le=3600, allow_inf_nan=False)
    n_tramos: int = Field(default=50, ge=2, le=_MAX_TRAMOS)

    @model_validator(mode="after")
    def _celeridad_exactamente_una_via(self):
        directa = self.celeridad_ms is not None
        indirecta = self.espesor_m is not None and self.e_tuberia_pa is not None
        parcial = (self.espesor_m is None) != (self.e_tuberia_pa is None)
        if parcial or directa == indirecta:
            raise ValueError("declare la celeridad directamente, o bien espesor_m y e_tuberia_pa (no ambas vías ni ninguna)")
        if indirecta and (self.poisson is None or self.anclaje is None):
            raise ValueError("para calcular la celeridad declare también poisson y anclaje (el coeficiente c1 cambia la celeridad 4–15 %)")
        if directa and (self.poisson is not None or self.anclaje is not None):
            raise ValueError("poisson y anclaje solo se usan si la celeridad se calcula (omita celeridad_ms)")
        return self


def ariete_contrato(s: SolicitudAriete) -> ResultadoMotor:
    a = s.celeridad_ms if s.celeridad_ms is not None else celeridad_korteweg(
        s.diametro_m, s.espesor_m, s.e_tuberia_pa, c1=coeficiente_anclaje(s.poisson, s.anclaje))
    h_vapor = h_vapor_por_altitud(s.altitud_m)
    kw = dict(longitud_m=s.longitud_m, diametro_m=s.diametro_m, celeridad_ms=a, f_darcy=s.f_darcy, caudal_m3s=s.caudal_m3s,
              carga_embalse_m=s.carga_embalse_m, t_cierre_s=s.t_cierre_s, t_fin_s=s.t_fin_s, h_vapor_m=h_vapor)
    r = simular_ariete(**kw, n_tramos=s.n_tramos)
    borde, notas = False, []
    if r["cavitacion"]:
        borde = True
        notas.append(f"Cavitación: la carga mínima ({min(r['envolvente']['h_min_m']):.1f} m) baja de la carga de "
                     f"vapor ({r['h_vapor_m']:.1f} m): el modelo no simula separación de columna y los resultados posteriores no son válidos.")
    if _BANDA_CRITICA[0] * r["tiempo_critico_s"] <= s.t_cierre_s <= _BANDA_CRITICA[1] * r["tiempo_critico_s"]:
        borde = True
        notas.append("El tiempo de cierre está cerca del tiempo crítico 2L/a: el pico depende mucho de la ley de cierre real.")
    if s.t_fin_s < s.t_cierre_s + r["periodo_s"]:
        borde = True
        notas.append(f"Horizonte corto: t_fin ({s.t_fin_s:g} s) es menor que el cierre más un periodo 4L/a ({s.t_cierre_s + r['periodo_s']:g} s); "
                     "el pico máximo puede ocurrir después y estar subestimado.")
    malla = None
    try:
        if 2 * s.n_tramos > _MAX_TRAMOS:
            raise ValueError("más de {} tramos".format(_MAX_TRAMOS))
        r2 = simular_ariete(**kw, n_tramos=2 * s.n_tramos)
        pico, pico2 = r["valvula"]["h_max_m"], r2["valvula"]["h_max_m"]
        dif = abs(pico2 - pico) / max(abs(pico2), 1e-9)
        malla = {"pico_malla_doble_m": pico2, "diferencia_relativa": dif}
        if dif > _TOL_MALLA:
            borde = True
            notas.append(f"El pico cambia {dif * 100:.1f} % al duplicar los tramos: la discretización no es suficiente, use más tramos.")
    except ValueError:
        borde = True
        notas.append("Verificación de malla omitida: la malla del doble de tramos excede el límite de cómputo; "
                     "la convergencia de la discretización no está comprobada.")
    supuestos = [
        "Tubería simple, horizontal, de diámetro y celeridad constantes, con embalse de nivel constante aguas arriba y una válvula aguas abajo.",
        "Método de las características con Courant = 1 y fricción de Darcy-Weisbach cuasi-permanente concentrada (primer orden): "
        "no captura la fricción dependiente de la frecuencia (Zielke).",
        "Cierre lineal de la válvula con caudal ∝ τ·√H; la ley de cierre real de la válvula puede diferir (cierre no lineal cambia el pico).",
        "Sin separación de columna, sin aire atrapado, sin cámaras de aire ni ventosas ni válvulas de alivio; sin interacción con redes ni bombas.",
        "Celeridad: pared delgada (Korteweg) con K = 2,07 GPa y coeficiente c1 de anclaje; el aire disuelto o la deformación del suelo la "
        "reducen. Materiales viscoelásticos (PE, PVC) no están cubiertos: su módulo depende de la velocidad de carga y del tiempo.",
        f"Cargas manométricas sobre el eje; la presión de vapor corresponde a agua a 20 °C a {s.altitud_m:g} m de altitud (atmósfera estándar): "
        f"carga de vapor {h_vapor:.2f} m.",
        "Es una verificación de análisis, no una norma: el diseño de protección contra transitorios requiere criterio profesional y las "
        "presiones de trabajo y de prueba de la tubería.",
    ] + notas
    if s.celeridad_ms is None:
        supuestos.append(f"Celeridad calculada con Korteweg (anclaje «{s.anclaje}», ν = {s.poisson:g}): {a:.0f} m/s.")
    return ResultadoMotor(
        valor={**{k: v for k, v in r.items() if k != "tiempos_s"}, "tiempos_s": r["tiempos_s"], "celeridad_ms": a, "malla": malla},
        unidad_si="Tiempo en s; carga en m; caudal en m³/s; celeridad en m/s",
        ecuacion="ΔH = a·V0/g (Joukowsky); C+: H_P = C_P − B·Q_P, C−: H_P = C_M + B·Q_P, B = a/(g·A); a = √(K/ρ)/√(1 + K·D/(E·e))",
        referencia_normativa="Joukowsky (1898) · Wylie y Streeter (1993) · Chaudhry (2014) · RAS 2000 Título B (verificación de transitorios)",
        supuestos=supuestos,
        en_borde_dominio=bool(borde),
    )
