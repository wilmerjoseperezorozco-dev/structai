"""
Cliente en vivo para la API REST de INVIAS — Análisis de Precios Unitarios
(APU) Regionalizados de Referencia.

Mismo espíritu que `ideam_client.py` y `sgc_amenaza_sismica.py`: consultar
una fuente de datos abiertos oficial en vivo, sin API key, degradando con
honestidad cuando el dato no está — en vez de duplicar todo localmente.

Este cliente complementa (no reemplaza) los datos ya cargados en Supabase
por `scripts/ingesta/invias_apu/cargar_invias_apu.py`: sirve para consultar
en vivo provincias/departamentos que todavía no se han descargado e
ingestado en bloque, o para verificar que el dato cargado sigue vigente.

Fuente: https://www.invias.gov.co/publicaciones/4149/analisis-de-precios-unitarios-apu-regionalizados-de-referencia/
API real (sin autenticación, descubierta inspeccionando la app detrás del
iframe público hermes2.invias.gov.co/APUs/filtroAPU/):
  - Departamentos:  {BASE}/DivisionPolitica/DivisionPolitica/MapServer/4/query
  - Municipios:     {BASE}/DivisionPolitica/DivisionPolitica/MapServer/6/query
  - Precios APU:    {BASE}/apu/APU/MapServer/3/query
  - Excel por provincia (descarga masiva, no vía este cliente):
    https://hermes2.invias.gov.co/APUs/Provincias/<anio>_<periodo>/APU_<codigoprovincia>_<DEPTO>__<PROVINCIA>_<anio>_<periodo>.xlsx
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://hermes2.invias.gov.co/server/rest/services"
TIMEOUT_SEGUNDOS = 20.0


@dataclass(frozen=True)
class PrecioInsumoInvias:
    nombre_insumo: str
    precio: float
    unidad: str | None
    codigo: str | None
    departamento: str
    provincia: str
    codigo_departamento: str
    codigo_provincia: str
    tipo_insumo: str | None
    numeral: str | None
    anio: int | None
    periodo: int | None


def _query_arcgis(servicio: str, capa: int, where: str, out_fields: str = "*") -> list[dict]:
    """Consulta genérica a una capa ArcGIS MapServer de INVIAS. Devuelve
    lista vacía (nunca lanza) si el servicio no responde — degradar con
    honestidad, no reventar el flujo del RAG por una fuente externa caída."""
    url = f"{BASE_URL}/{servicio}/MapServer/{capa}/query"
    params = {
        "f": "json",
        "where": where,
        "returnGeometry": "false",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": out_fields,
    }
    try:
        resp = httpx.get(url, params=params, timeout=TIMEOUT_SEGUNDOS)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("invias_apu_client: fallo consultando %s (%s): %s", servicio, where, exc)
        return []

    if "error" in data:
        logger.warning("invias_apu_client: ArcGIS devolvió error para %s: %s", where, data["error"])
        return []

    return [f.get("attributes", {}) for f in data.get("features", [])]


def listar_departamentos() -> list[dict]:
    """Departamentos disponibles en la regionalización APU de INVIAS
    (140 provincias, todo el país excepto Bogotá D.C.)."""
    filas = _query_arcgis(
        "DivisionPolitica/DivisionPolitica", 4, where="1=1", out_fields="departamento,codigodepartamento"
    )
    vistos: dict[str, dict] = {}
    for f in filas:
        cod = f.get("codigodepartamento")
        if cod and cod not in vistos:
            vistos[cod] = {"codigo": cod, "departamento": f.get("departamento")}
    return sorted(vistos.values(), key=lambda d: d["departamento"] or "")


def listar_provincias(codigo_departamento: str) -> list[dict]:
    """Provincias de un departamento, con su código real de provincia
    (ej. Meta -> Ariari 5001, Capital 5002, Piedemonte 5003, Río Meta 5004).
    Se deriva de la capa de precios (la única que trae codigoprovincia),
    no de la capa de municipios (esa es por municipio, no por provincia)."""
    filas = _query_arcgis(
        "apu/APU",
        3,
        where=f"codigodepartamento = '{codigo_departamento}'",
        out_fields="nombredepartamento,nombreprovincia,codigoprovincia",
    )
    vistos: dict[str, dict] = {}
    for f in filas:
        cod = f.get("codigoprovincia")
        if cod and cod not in vistos:
            vistos[cod] = {
                "codigo": cod,
                "departamento": f.get("nombredepartamento"),
                "provincia": f.get("nombreprovincia"),
            }
    return sorted(vistos.values(), key=lambda p: p["codigo"])


def buscar_precio_insumo(
    texto: str, codigo_departamento: str | None = None, limite: int = 20
) -> list[PrecioInsumoInvias]:
    """Busca insumos por texto libre en el nombre (LIKE, sin acentos exactos
    porque ArcGIS no tiene un operador de texto completo aquí). Si se pasa
    codigo_departamento, filtra a ese departamento.

    Uso típico: verificación puntual en vivo de un precio ya cargado, o
    consulta de un departamento que todavía no se ha ingestado en bloque.
    """
    texto_normalizado = texto.strip().replace("'", "''")
    where = f"nombreinsumo LIKE '%{texto_normalizado}%'"
    if codigo_departamento:
        where += f" AND codigodepartamento = '{codigo_departamento}'"

    filas = _query_arcgis("apu/APU", 3, where=where)
    resultados = []
    for f in filas[:limite]:
        resultados.append(
            PrecioInsumoInvias(
                nombre_insumo=f.get("nombreinsumo", ""),
                precio=f.get("precio") or 0.0,
                unidad=f.get("unidad"),
                codigo=f.get("codigo"),
                departamento=f.get("nombredepartamento", ""),
                provincia=f.get("nombreprovincia", ""),
                codigo_departamento=f.get("codigodepartamento", ""),
                codigo_provincia=f.get("codigoprovincia", ""),
                tipo_insumo=f.get("tipoinsumo"),
                numeral=str(f.get("numeral")) if f.get("numeral") is not None else None,
                anio=f.get("anio"),
                periodo=f.get("periodo"),
            )
        )
    return resultados


def verificar_cobertura_departamento(codigo_departamento: str) -> dict:
    """Chequeo rápido y honesto de si un departamento tiene datos reales en
    la API de INVIAS antes de intentar descargar/ingestar sus provincias —
    evita asumir cobertura nacional completa sin comprobarla primero (la
    página dice 140 provincias / todo el país excepto Bogotá D.C., pero eso
    se verifica por departamento, no se da por hecho)."""
    provincias = listar_provincias(codigo_departamento)
    return {
        "codigo_departamento": codigo_departamento,
        "tiene_datos": len(provincias) > 0,
        "provincias_encontradas": provincias,
    }
