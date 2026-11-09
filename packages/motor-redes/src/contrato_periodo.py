"""Salida con contrato uniforme de motor-redes (#138): periodo extendido con tanques de nivel variable."""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .contrato_api import SolicitudRed, _verificar_limites
from .periodo import simular_periodo

import sys
from pathlib import Path

_RUTA = str(Path(__file__).resolve().parents[2] / "contrato-motor")
if _RUTA not in sys.path:
    sys.path.insert(0, _RUTA)

from contrato_motor import ResultadoMotor  # noqa: E402

_MARGEN_NIVEL = 0.10            # a menos de 10 % del recorrido útil de un límite, el veredicto es sensible


class TanqueRed(BaseModel):
    model_config = ConfigDict(strict=True)
    id: str = Field(..., min_length=1, max_length=40, description="Debe ser un nudo libre y sin demanda")
    cota_fondo_m: float = Field(..., ge=-500, le=6000, allow_inf_nan=False)
    area_m2: float = Field(..., gt=0, le=1e6, allow_inf_nan=False, description="Tanque cilíndrico: área constante")
    nivel_inicial_m: float = Field(..., ge=0, le=200, allow_inf_nan=False)
    nivel_min_m: float = Field(..., ge=0, le=200, allow_inf_nan=False)
    nivel_max_m: float = Field(..., gt=0, le=200, allow_inf_nan=False)


class SolicitudPeriodo(SolicitudRed):
    tanques: list[TanqueRed] = Field(..., min_length=1, max_length=50)
    paso_s: float = Field(..., gt=0, le=86400, allow_inf_nan=False)
    n_pasos: int = Field(..., ge=1, le=2000)
    patron_demanda: Optional[list[float]] = Field(default=None, min_length=1, max_length=2000,
                                                  description="Factores multiplicadores de la demanda, repetidos cíclicamente")


def periodo_extendido_contrato(s: SolicitudPeriodo) -> ResultadoMotor:
    sim = simular_periodo(
        [n.model_dump() for n in s.nodos], [t.model_dump() for t in s.tramos],
        tanques=[t.model_dump() for t in s.tanques], paso_s=s.paso_s, n_pasos=s.n_pasos, patron_demanda=s.patron_demanda,
        bombas=[b.model_dump() for b in s.bombas], valvulas=[v.model_dump() for v in s.valvulas])
    pasos = sim["pasos"]
    ids_tanque = {t.id for t in s.tanques}
    series = {tid: [p["tanques"][tid]["nivel_m"] for p in pasos] for tid in ids_tanque}
    extremos = {}
    for nid in pasos[0]["nodos"]:
        pres = [p["nodos"][nid]["presion_m"] for p in pasos]
        extremos[nid] = {"presion_min_m": min(pres), "presion_max_m": max(pres)}
    incumple, borde_lim = [], False
    vistos = set()
    # Para verificar límites, los nudos de tanque se marcan con carga fija: su «presión» es el nivel, no una presión de servicio.
    sin_tanques = s.model_copy(update={"nodos": [n.model_copy(update={"carga_fija_m": 0.0}) if n.id in ids_tanque else n
                                                 for n in s.nodos]})
    for p in pasos:
        inc, b = _verificar_limites({"nodos": p["nodos"], "tramos": p["tramos"]}, sin_tanques)
        borde_lim = borde_lim or b
        for m in inc:
            clave = m.split(":")[0]
            if clave not in vistos:
                vistos.add(clave)
                incumple.append(f"t = {p['t_s']:g} s, {m}")
    borde = borde_lim or not sim["completo"]
    for t in s.tanques:
        recorrido = max(t.nivel_max_m - t.nivel_min_m, 1e-9)
        for nivel in series[t.id]:
            if nivel - t.nivel_min_m < _MARGEN_NIVEL * recorrido or t.nivel_max_m - nivel < _MARGEN_NIVEL * recorrido:
                borde = True
    hay_limites = not (s.presion_min_m is None and s.presion_max_m is None and s.velocidad_max_ms is None)
    supuestos = [
        "Secuencia de estados permanentes: en cada paso se resuelve la red con Hazen-Williams y las demandas del paso; "
        "no hay transitorio hidráulico (inercia del agua) entre pasos.",
        "El nivel de cada tanque se actualiza por Euler explícito con el caudal neto al inicio del paso (como EPANET): el error crece "
        "con el paso de tiempo; reduzca el paso hasta que el resultado deje de cambiar.",
        "Tanques cilíndricos (área constante); sin rebose, sin válvulas de control por nivel ni controles simples o por reglas.",
        "Si un tanque cruzaría su nivel mínimo o máximo, la simulación se detiene y se reporta el evento: no se simula el cierre de "
        "tuberías ni la inversión de flujo posterior.",
        "El patrón de demanda multiplica todas las demandas y se repite cíclicamente cada paso; no hay patrones por nudo.",
        "Las bombas se modelan con la parábola H = h0 − a·Q²; las válvulas son de pérdida local (K constante). Sin pérdidas menores en tuberías.",
        "Los límites de presión y velocidad los fija quien consulta; el motor no asume valores de norma (verificar en RAS 2000 Título B).",
    ]
    if not hay_limites:
        supuestos.append("No se declaró ningún límite de servicio: no se verificó cumplimiento.")
    if not sim["completo"]:
        supuestos.append("La simulación terminó antes de lo pedido: " + "; ".join(sim["eventos"]))
    return ResultadoMotor(
        valor={"tiempos_s": [p["t_s"] for p in pasos], "niveles_tanque_m": series, "extremos_nodos": extremos,
               "eventos": sim["eventos"], "completo": sim["completo"], "incumplimientos": incumple,
               "limites_verificados": hay_limites, "cumple": (not incumple) if (hay_limites or incumple) else None},
        unidad_si="Tiempo en s; nivel, carga y presión en m",
        ecuacion="Σ Q_nudo = demanda·patrón en cada paso (gradiente, Hazen-Williams); A·dh/dt = Q_entrada del tanque (Euler explícito)",
        referencia_normativa="Todini y Pilati (1988) · Rossman (EPANET) · RAS 2000 Título B (límites a cargo del usuario)",
        supuestos=supuestos,
        en_borde_dominio=bool(borde),
    )
