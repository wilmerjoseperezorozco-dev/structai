"""Nodos reales del DAG: diseño integral (orquestador) → análisis (pórtico) → zapata (motor-concreto).

Los motores se cargan con los mismos alias que usan los routers de la API (idempotente).
Cada parámetro físico es obligatorio: ninguno tiene valor por defecto (regla 1).
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field

from . import Artefacto, Nodo

_PAQUETES = Path(__file__).resolve().parents[2]
if str(_PAQUETES / "contrato-motor") not in sys.path:
    sys.path.insert(0, str(_PAQUETES / "contrato-motor"))

from contrato_motor import ResultadoMotor  # noqa: E402

VERSION_NODO = "1.0"
_CAMPOS_ORQUESTADOR = ("luces_m", "alturas_piso_m", "carga_muerta_kn_m", "carga_viva_kn_m", "calidad_concreto", "fy_mpa",
                       "recubrimiento_mm", "municipio", "departamento", "perfil_suelo", "grupo_uso", "capacidad",
                       "columnas_mm", "b_mm", "h_mm")
_CAMPOS_ANALISIS = ("luces_m", "alturas_piso_m", "carga_muerta_kn_m", "carga_viva_kn_m", "E_mpa")
_CAMPOS_ZAPATA = ("q_adm_kpa", "profundidad_desplante_m", "peso_unitario_relleno_kn_m3", "asentamiento_max_mm",
                  "ks_kn_m3", "fc_mpa", "fy_mpa")
PARAMETROS_REQUERIDOS = tuple(dict.fromkeys(_CAMPOS_ORQUESTADOR + _CAMPOS_ANALISIS + _CAMPOS_ZAPATA))
_FACTOR_CM, _FACTOR_CV = 1.2, 1.6      # NSR-10 B.2.4.2, combinación 1,2D + 1,6L


class SolicitudProyectoEstructural(BaseModel):
    """Proyecto de entrada del DAG estructural. Sin valores por defecto físicos; rejilla acotada como en el orquestador."""
    model_config = ConfigDict(extra="forbid")
    luces_m: list[float] = Field(..., min_length=1, max_length=6)
    alturas_piso_m: list[float] = Field(..., min_length=1, max_length=8)
    carga_muerta_kn_m: float = Field(..., ge=0)
    carga_viva_kn_m: float = Field(..., ge=0)
    calidad_concreto: str
    fy_mpa: float = Field(..., gt=0)
    recubrimiento_mm: float = Field(..., gt=0)
    municipio: Optional[str] = None
    departamento: Optional[str] = None
    perfil_suelo: str
    grupo_uso: str
    capacidad: Optional[str] = None
    columnas_mm: list[float] = Field(..., min_length=1, max_length=8)
    b_mm: list[float] = Field(..., min_length=1, max_length=8)
    h_mm: list[float] = Field(..., min_length=1, max_length=12)
    E_mpa: float = Field(..., gt=0)
    q_adm_kpa: float = Field(..., gt=0)
    profundidad_desplante_m: float = Field(..., gt=0)
    peso_unitario_relleno_kn_m3: float = Field(..., gt=0)
    asentamiento_max_mm: float = Field(..., gt=0)
    ks_kn_m3: Optional[float] = Field(...)
    fc_mpa: float = Field(..., gt=0)


def _cargar(carpeta: str, alias: str) -> ModuleType:
    if alias in sys.modules:
        return sys.modules[alias]
    init = _PAQUETES / carpeta / "src" / "__init__.py"
    spec = importlib.util.spec_from_file_location(alias, init, submodule_search_locations=[str(init.parent)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def _orquestador_fn(p: Mapping[str, Any], _ent: Mapping[str, Artefacto]) -> ResultadoMotor:
    _cargar("motor-concreto", "motor_concreto")
    _cargar("orquestador", "orquestador")
    api = importlib.import_module("orquestador.contrato_api")
    return api.disenar_integral_contrato(api.SolicitudDisenoIntegral(**{k: p[k] for k in _CAMPOS_ORQUESTADOR}))


def _malla(luces: list[float], alturas: list[float], c_m: float, b_m: float, h_m: float, e_kpa: float):
    xs = [0.0]
    for lz in luces:
        xs.append(xs[-1] + lz)
    ys = [0.0]
    for hp in alturas:
        ys.append(ys[-1] + hp)
    nx = len(xs)
    nodos = [(x, y) for y in ys for x in xs]
    idx = lambda i, j: j * nx + i  # noqa: E731
    col = dict(E=e_kpa, A=c_m * c_m, I=c_m ** 4 / 12.0)
    vig = dict(E=e_kpa, A=b_m * h_m, I=b_m * h_m ** 3 / 12.0)
    elementos, vigas = [], []
    for j in range(len(alturas)):
        for i in range(nx):
            elementos.append(dict(i=idx(i, j), j=idx(i, j + 1), **col))
    for j in range(1, len(ys)):
        for i in range(nx - 1):
            vigas.append(len(elementos))
            elementos.append(dict(i=idx(i, j), j=idx(i + 1, j), **vig))
    apoyos = {idx(i, 0): (True, True, True) for i in range(nx)}
    return nodos, elementos, vigas, apoyos


def _analisis_fn(p: Mapping[str, Any], ent: Mapping[str, Artefacto]) -> ResultadoMotor:
    _cargar("motor-analisis", "motor_analisis")
    api = importlib.import_module("motor_analisis.contrato_api")
    sec = ent["orquestador"].resultado["valor"]
    nodos, elementos, vigas, apoyos = _malla(list(p["luces_m"]), list(p["alturas_piso_m"]), sec["c_mm"] / 1000.0,
                                             sec["b_mm"] / 1000.0, sec["h_mm"] / 1000.0, p["E_mpa"] * 1000.0)
    casos = [dict(nombre="D", uniformes={k: p["carga_muerta_kn_m"] for k in vigas}),
             dict(nombre="L", uniformes={k: p["carga_viva_kn_m"] for k in vigas})]
    r = api.resolver_portico_contrato(api.SolicitudPortico(nodos=nodos, elementos=elementos, apoyos=apoyos, casos=casos))
    v = r.valor
    base = {c: max(react[1] for react in v["casos"][c]["reacciones"].values()) for c in ("D", "L")}
    return r.model_copy(update={
        "valor": {**v, "reaccion_base_max_kn": base},
        "supuestos": list(r.supuestos) + [
            "Solo cargas gravitacionales D y L sobre todas las vigas; sin sismo ni viento.",
            "Sección bruta (sin agrietamiento) con las dimensiones óptimas del diseño integral; bases empotradas.",
            "Reacción vertical máxima entre apoyos, tomada como carga de la zapata más cargada."]})


def _zapata_fn(p: Mapping[str, Any], ent: Mapping[str, Artefacto]) -> ResultadoMotor:
    _cargar("motor-concreto", "motor_concreto")
    api = importlib.import_module("motor_concreto.contrato_api")
    c = ent["orquestador"].resultado["valor"]["c_mm"]
    rd = ent["analisis"].resultado["valor"]["reaccion_base_max_kn"]
    p_serv, p_u = rd["D"] + rd["L"], _FACTOR_CM * rd["D"] + _FACTOR_CV * rd["L"]
    r = api.disenar_zapata_contrato(api.SolicitudZapata(
        c1_mm=c, c2_mm=c, P_serv=p_serv, P_u=p_u, **{k: p[k] for k in _CAMPOS_ZAPATA}))
    return r.model_copy(update={
        "valor": {**r.valor, "P_serv_kn": p_serv, "P_u_kn": p_u},
        "supuestos": list(r.supuestos) + [
            "Carga axial tomada de la reacción del análisis (artefacto aguas arriba); sin momentos en la base.",
            "Combinación 1,2D + 1,6L (NSR-10 B.2.4.2); sin sismo."]})


def nodos_estructurales() -> list[Nodo]:
    return [
        Nodo("orquestador", VERSION_NODO, (), _CAMPOS_ORQUESTADOR, _orquestador_fn),
        Nodo("analisis", VERSION_NODO, ("orquestador",), _CAMPOS_ANALISIS, _analisis_fn),
        Nodo("zapata", VERSION_NODO, ("orquestador", "analisis"), _CAMPOS_ZAPATA, _zapata_fn),
    ]
