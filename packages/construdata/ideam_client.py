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

# Cache en memoria de proceso del valor REAL almacenado para cada
# departamento (con o sin tilde según el dato original) -- ver
# _resolver_departamento. Se llena una sola vez por proceso con una
# consulta barata (33 filas), no en cada request.
_CACHE_DEPARTAMENTOS: Optional[dict[str, str]] = None


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
    es inconsistente NO SOLO entre datasets del IDEAM sino DENTRO del mismo
    dataset (confirmado en vivo el 2026-08-20 sobre el catálogo nacional de
    estaciones, hp9r-jxuu: la mayoría de departamentos están sin tilde
    -- 'Atlantico', 'Choco', 'Cordoba', 'Caqueta' -- pero 5 SÍ conservan
    tilde/eñe -- 'Bogotá', 'Boyacá', 'Guainía', 'Nariño', 'Quindío'. Filtrar
    solo por la versión sin tildes (como hacía esta función antes) deja a
    esos 5 con 0 resultados siempre, silenciosamente -- Nariño (Tumaco,
    región Pacífico) y Bogotá quedaban invisibles para este cliente pese a
    tener estaciones reales. SoQL no tiene unaccent() nativo, así que se
    prueban ambas variantes con OR: la tal cual la escribió quien llama, y
    la versión sin tildes -- cubre los dos estilos de almacenamiento
    observados sin tener que traer el dataset completo (28615 filas) para
    filtrar en cliente."""
    original = valor.replace("'", "''")
    sin_tildes = _sin_tildes(valor).replace("'", "''")
    if original == sin_tildes:
        return f"upper({campo}) like upper('%{original}%')"
    return (
        f"(upper({campo}) like upper('%{original}%') "
        f"or upper({campo}) like upper('%{sin_tildes}%'))"
    )


def _where_exacto(campo: str, valor: str) -> str:
    """Igualdad exacta (no LIKE) -- usar SOLO cuando 'valor' ya es la forma
    canónica exacta almacenada (ej. la salida de _resolver_departamento).
    Un LIKE '%valor%' sobre un nombre de departamento es un riesgo real de
    falso positivo por substring: 'Cauca' matchea 'Valle Del Cauca',
    'Santander' matchea 'Norte De Santander' -- confirmado en vivo con
    Cauca/Valle Del Cauca 2026-08-21."""
    escapado = valor.replace("'", "''")
    return f"upper({campo}) = upper('{escapado}')"


def _resolver_departamento(valor: str) -> str:
    """Resuelve 'valor' (como lo escribió quien llama, con o sin tilde) a la
    forma EXACTA almacenada en el catálogo de estaciones (ej. 'Narino' ->
    'Nariño', 'Bogota' -> 'Bogotá'), consultando una sola vez por proceso el
    listado de los 33 departamentos distintos (consulta barata, se cachea en
    _CACHE_DEPARTAMENTOS). Esto reemplaza el intento de adivinar tildes con
    LIKE/$q -- deterministico y no depende de que el buscador de texto
    completo de Socrata normalice bien el término (confirmado en vivo que
    NO lo hace siempre: 'Guainia' no encontraba 'Guainía' via $q pese a que
    la estación existe). Si no hay match conocido, devuelve 'valor' tal
    cual (deja que _where_ilike intente su patrón normal)."""
    global _CACHE_DEPARTAMENTOS
    if _CACHE_DEPARTAMENTOS is None:
        filas = _get(DATASETS["estaciones"], {"$select": "distinct departamento", "$limit": 100})
        _CACHE_DEPARTAMENTOS = {
            _sin_tildes(f["departamento"]).upper(): f["departamento"]
            for f in filas if f.get("departamento")
        }
    return _CACHE_DEPARTAMENTOS.get(_sin_tildes(valor).upper(), valor)


def _coincide(valor_fila: Optional[str], valor_buscado: str) -> bool:
    """Compara ambos lados ya sin tildes/mayúsculas -- usado en el fallback
    de _buscar_estaciones_fulltext, donde SÍ podemos normalizar los dos
    lados en Python (a diferencia de _where_ilike, que corre contra SoQL)."""
    if not valor_fila:
        return False
    return _sin_tildes(valor_buscado).upper() in _sin_tildes(valor_fila).upper()


def buscar_estaciones(
    departamento: Optional[str] = None,
    municipio: Optional[str] = None,
    categoria: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    """Catálogo nacional de estaciones IDEAM (código, nombre, lat/lon,
    departamento, municipio, categoría, estado activa/inactiva). Útil para
    encontrar la estación hidrometeorológica más cercana a un proyecto.

    Departamento/municipio con tilde/eñe en el dato real (Bogotá, Boyacá,
    Guainía, Nariño, Quindío -- ver nota en _where_ilike) no hacen match
    contra ningún patrón LIKE armado en Python, sea cual sea la forma en que
    el llamador escriba el término (con o sin tilde) -- SoQL no tiene
    unaccent() ni translate() (confirmado en vivo, error
    'no-such-function'). Por eso, si el filtro $where normal devuelve 0
    filas y se pidió departamento o municipio, se reintenta con $q
    (búsqueda de texto completo de Socrata, que sí es insensible a
    tildes/mayúsculas del lado del servidor) y se filtra el resultado en
    Python comparando ya sin tildes de ambos lados -- $q solo no basta
    porque busca en TODAS las columnas de texto (falsos positivos: buscar
    'Nariño' matchea también municipios llamados Nariño en otros
    departamentos). $q con varios términos a la vez (ej. 'Narino Tumaco')
    devuelve 0 filas aunque cada término por separado sí matchee -- el
    buscador de texto completo de Socrata exige que TODOS los términos
    aparezcan literalmente, y no aplica su normalización de tildes de
    forma consistente entre términos combinados (confirmado en vivo). Por
    eso el fallback usa un solo término (el más específico disponible)."""
    if departamento:
        departamento = _resolver_departamento(departamento)

    params: dict = {"$limit": limit}
    wheres = []
    if departamento:
        # Igualdad EXACTA, no LIKE: _resolver_departamento ya dio la forma
        # canónica exacta almacenada, así que un LIKE '%...%' aquí es
        # innecesario Y peligroso -- bug real encontrado en vivo 2026-08-21:
        # buscar departamento="Cauca" con LIKE devolvía estaciones de "Valle
        # Del Cauca" (Cauca es substring literal de Valle Del Cauca). Mismo
        # riesgo existe para "Santander" vs "Norte De Santander".
        wheres.append(_where_exacto("departamento", departamento))
    if municipio:
        wheres.append(_where_ilike("municipio", municipio))
    if categoria:
        wheres.append(_where_ilike("categoria", categoria))
    if wheres:
        params["$where"] = " and ".join(wheres)
    resultado = _get(DATASETS["estaciones"], params)
    if resultado or not (departamento or municipio):
        return resultado

    termino_q = municipio or departamento
    candidatos = _get(DATASETS["estaciones"], {"$q": termino_q, "$limit": max(limit * 6, 200)})
    filtrados = [
        fila for fila in candidatos
        # Departamento: igualdad exacta (mismo motivo que _where_exacto
        # arriba -- _coincide es substring y "Cauca" in "Valle Del Cauca"
        # da True). Municipio/categoría sí quedan como substring a propósito
        # (conveniencia real: buscar "Repelón" debe encontrar variantes de
        # escritura del mismo municipio).
        if (not departamento or _sin_tildes(departamento).upper() == _sin_tildes(fila.get("departamento") or "").upper())
        and (not municipio or _coincide(fila.get("municipio"), municipio))
        and (not categoria or _coincide(fila.get("categoria"), categoria))
    ]
    return filtrados[:limit]


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
