"""
Cliente ligero para los datos abiertos hidrometeorológicos del IDEAM,
expuestos via la plataforma Socrata de datos.gov.co (API SODA, JSON, sin
API key ni cuenta -- de acceso publico y gratuito).

Contexto: el usuario pidio "capacidad de buscar mas" pensando en instalar
una herramienta externa de scraping de redes sociales (agent-reach) para
"lo del IDEAM" -- esa herramienta no tenia ningun conector a datos
gubernamentales y traia riesgo real (credenciales de redes sociales,
posible baneo de cuenta). En su lugar, esto conecta directo a la fuente
oficial: no requiere instalar nada, no expone ninguna cuenta.

Datasets verificados en vivo el 2026-08-20 (funcionan, JSON real,
cobertura nacional incluyendo Atlantico):
- Precipitacion: s54a-sgyg
- Temperatura del aire (2m): sbwg-7ju4
- Catalogo Nacional de Estaciones IDEAM: hp9r-jxuu (da lat/lon/departamento/
  municipio de cada estacion -- clave para encontrar la estacion mas
  cercana a un proyecto)

Encontrados pero SIN verificar (la URL no respondio con datos tabulares en
la prueba, pendiente investigar antes de usarlos):
- Caudales medios mensuales de los rios de Colombia: gih4-w7rj
- Humedad relativa: xh2z-7kiv

Uso:
    from ideam_client import buscar_estaciones, precipitacion_por_municipio

    estaciones = buscar_estaciones(departamento="Atlántico")
    precip = precipitacion_por_municipio("REPELÓN", limit=100)
"""
from __future__ import annotations

import unicodedata
from typing import Optional

import httpx

BASE_URL = "https://www.datos.gov.co/resource"

DATASETS = {
    "precipitacion": "s54a-sgyg",
    "temperatura": "sbwg-7ju4",
    "estaciones": "hp9r-jxuu",
}

_TIMEOUT = 15.0


def _get(dataset_id: str, params: dict) -> list[dict]:
    url = f"{BASE_URL}/{dataset_id}.json"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _where_ilike(campo: str, valor: str) -> str:
    """SoQL case/acento-insensible: la escritura de departamento/municipio
    es inconsistente entre datasets del IDEAM (ej. 'Atlantico' SIN tilde en
    el catálogo de estaciones, 'ATLANTICO' en mayúsculas en precipitación) --
    confirmado probando ambas formas en vivo. Un match exacto (o incluso
    ILIKE con tilde) falla silenciosamente (devuelve lista vacía sin error),
    así que se quita la tilde del término de búsqueda antes de armar el
    patrón -- SoQL no tiene unaccent() nativo, así que la normalización se
    hace acá, no en el servidor."""
    escapado = _sin_tildes(valor).replace("'", "''")
    return f"upper({campo}) like upper('%{escapado}%')"


def buscar_estaciones(
    departamento: Optional[str] = None,
    municipio: Optional[str] = None,
    categoria: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    """Catálogo nacional de estaciones IDEAM (código, nombre, lat/lon,
    departamento, municipio, categoría, estado activa/inactiva). Útil para
    encontrar la estación hidrometeorológica más cercana a un proyecto."""
    params: dict = {"$limit": limit}
    wheres = []
    if departamento:
        wheres.append(_where_ilike("departamento", departamento))
    if municipio:
        wheres.append(_where_ilike("municipio", municipio))
    if categoria:
        wheres.append(_where_ilike("categoria", categoria))
    if wheres:
        params["$where"] = " and ".join(wheres)
    return _get(DATASETS["estaciones"], params)


def precipitacion_por_municipio(municipio: str, limit: int = 100) -> list[dict]:
    """Observaciones de precipitación (mm) crudas, sin validar por IDEAM
    (dato en tiempo casi real, no el dato oficial validado del DHIME)."""
    return _get(
        DATASETS["precipitacion"],
        {"$where": _where_ilike("municipio", municipio), "$limit": limit},
    )


def temperatura_por_municipio(municipio: str, limit: int = 100) -> list[dict]:
    """Observaciones de temperatura del aire a 2m (°C), sin validar."""
    return _get(
        DATASETS["temperatura"],
        {"$where": _where_ilike("municipio", municipio), "$limit": limit},
    )


if __name__ == "__main__":
    import json

    print("Estaciones en Atlántico:")
    print(json.dumps(buscar_estaciones(departamento="Atlántico", limit=5), ensure_ascii=False, indent=2))
