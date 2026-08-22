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

Caudales medios mensuales de los rios de Colombia -- verificado en vivo
2026-08-22 (el dataset gih4-w7rj de datos.gov.co en si NO es tabular via
Socrata, da 403 "no row or column access to non-tabular tables" -- pero
la pagina real del dataset apunta a un bucket S3 PUBLICO real y sin
autenticacion en datos.ideam.gov.co, API estandar ListObjectsV2, con un
archivo CSV por estacion hidrologica). El codigo de estacion de estos CSV
coincide exactamente con el campo "codigo" del catalogo hp9r-jxuu para
estaciones categoria "Limnimétrica"/"Limnigráfica" (medicion de
nivel/caudal de rio) -- confirmado en vivo con la estacion 0011017010
(Aguasal, Chocó, Lloró): serie historica real 1965-2026, estado de
aprobacion Preliminar/En revisión/Definitivo por dato. Ver
caudal_por_municipio() más abajo.

Encontrado pero SIN verificar (pendiente investigar antes de usarlo):
- Humedad relativa: xh2z-7kiv

Uso:
    from ideam_client import buscar_estaciones, precipitacion_por_municipio, caudal_por_municipio

    estaciones = buscar_estaciones(departamento="Atlántico")
    precip = precipitacion_por_municipio("REPELÓN", limit=100)
    caudal = caudal_por_municipio("Lloró", "Chocó")
"""
from __future__ import annotations

import csv
import io
import unicodedata
from typing import Optional

import httpx

BASE_URL = "https://www.datos.gov.co/resource"

DATASETS = {
    "precipitacion": "s54a-sgyg",
    "temperatura": "sbwg-7ju4",
    "estaciones": "hp9r-jxuu",
}

# Bucket S3 público del IDEAM (sin API key, sin autenticación -- verificado
# en vivo 2026-08-22 vía la interfaz "Objects Browser" de datos.ideam.gov.co,
# que internamente pega directo contra la API estándar de S3
# ListObjectsV2). Los archivos vienen organizados por variable
# (Q_MEDIA_M = caudal medio mensual) y por estación.
S3_BASE = "https://datos.ideam.gov.co/s3-estacionesideam"
S3_PREFIJO_CAUDAL = "observaciones/historicos/csv/Q_MEDIA_M/"

_TIMEOUT = 15.0
_TIMEOUT_S3 = 20.0  # los CSV historicos pueden pesar varias decenas de KB

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


def _descargar_csv_caudal(codigo_estacion: str) -> Optional[list[dict]]:
    """Descarga y parsea el CSV histórico de caudal (Q_MEDIA_M, m³/s) de UNA
    estación desde el bucket S3 público del IDEAM. None si la estación no
    tiene archivo de caudal (404 -- pasa con estaciones que están en el
    catálogo pero no miden caudal pese a la categoría, o cuyo código no
    tiene datos publicados todavía), nunca lanza.

    codigo_estacion se rellena a 10 dígitos con ceros a la izquierda antes
    de armar la URL -- bug real encontrado en vivo 2026-08-22: el catálogo
    hp9r-jxuu trae la MISMA estación duplicada con dos formatos de código
    ('11017010' y '0011017010'), pero el bucket S3 solo usa la forma
    rellenada a 10 dígitos ('0011017010-Q_MEDIA_M.csv') -- sin este zfill,
    la mitad de las estaciones devolvían 404 según qué duplicado llegara
    primero en la lista."""
    codigo_estacion = codigo_estacion.zfill(10)
    url = f"{S3_BASE}/{S3_PREFIJO_CAUDAL}{codigo_estacion}-Q_MEDIA_M.csv"
    try:
        with httpx.Client(timeout=_TIMEOUT_S3) as client:
            resp = client.get(url)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
    except httpx.HTTPError:
        return None
    lector = csv.DictReader(io.StringIO(resp.text))
    return list(lector)


def caudal_por_municipio(
    municipio: str,
    departamento: Optional[str] = None,
    max_estaciones: int = 2,
    meses_recientes: int = 6,
) -> list[dict]:
    """Caudal medio mensual (m³/s) reciente de los ríos monitoreados cerca
    de un municipio -- útil para contexto de riesgo de inundación (un
    caudal muy por encima del histórico del mismo mes es indicio de
    crecida). Busca estaciones categoría Limnimétrica/Limnigráfica
    (medición de nivel/caudal, ver buscar_estaciones) en el municipio dado,
    y para cada una descarga su serie histórica real del bucket S3 del
    IDEAM, devolviendo solo los últimos `meses_recientes` registros.

    Devuelve lista vacía si no hay estación de caudal en ese municipio (la
    red hidrológica es más rala que la de precipitación/temperatura -- esto
    es normal, no un error) o si ninguna de las estaciones candidatas tiene
    archivo publicado. Nunca lanza ni inventa un caudal."""
    estaciones = buscar_estaciones(departamento=departamento, municipio=municipio, categoria="Limn")

    # El catálogo duplica cada estación con dos formatos de código (ver
    # _descargar_csv_caudal) -- deduplicar por código normalizado (10
    # dígitos) antes de recortar a max_estaciones, para no gastar 2 de los
    # cupos en la MISMA estación dos veces.
    vistos: set[str] = set()
    estaciones_unicas = []
    for est in estaciones:
        codigo = (est.get("codigo") or "").zfill(10)
        if codigo and codigo not in vistos:
            vistos.add(codigo)
            estaciones_unicas.append(est)

    resultado: list[dict] = []
    for est in estaciones_unicas[:max_estaciones]:
        codigo = est.get("codigo")
        if not codigo:
            continue
        filas = _descargar_csv_caudal(codigo)
        if not filas:
            continue
        recientes = filas[-meses_recientes:]
        for f in recientes:
            resultado.append({
                "codigo_estacion": codigo,
                "nombre_estacion": est.get("nombre"),
                "corriente": est.get("corriente"),  # nombre del río
                "municipio": est.get("municipio"),
                "departamento": est.get("departamento"),
                "fecha": f.get("fechaObservacion"),
                "caudal_m3s": f.get("valorObservado"),
                "estado_aprobacion": f.get("nivelAprobacion"),
            })
    return resultado


def formatear_caudal(registros: list[dict]) -> str:
    """Arma un bloque de texto legible para inyectar en el RAG -- mismo
    espíritu que los formatear_respuesta() de sgc_amenaza_sismica.py/
    igac_client.py. Agrupa por estación/río, muestra solo el dato más
    reciente de cada una más el estado de aprobación (Preliminar/En
    revisión/Definitivo -- un dato Preliminar puede cambiar)."""
    if not registros:
        return ""
    por_estacion: dict[str, list[dict]] = {}
    for r in registros:
        por_estacion.setdefault(r["codigo_estacion"], []).append(r)

    lineas = ["Caudal medio mensual reciente (IDEAM, estaciones hidrológicas en vivo):"]
    for codigo, filas in por_estacion.items():
        filas_ordenadas = sorted(filas, key=lambda f: f["fecha"] or "")
        ultimo = filas_ordenadas[-1]
        rio = ultimo.get("corriente") or "río sin identificar"
        nombre_est = ultimo.get("nombre_estacion") or codigo
        fecha = (ultimo.get("fecha") or "")[:7]  # solo año-mes
        try:
            caudal = f"{float(ultimo.get('caudal_m3s')):.1f}"
        except (TypeError, ValueError):
            caudal = ultimo.get("caudal_m3s")  # dato crudo no numérico -- mostrar tal cual, no ocultarlo
        estado = ultimo.get("estado_aprobacion") or "sin estado"
        lineas.append(
            f"- Río {rio} (estación {nombre_est}, {ultimo.get('municipio')}): "
            f"{caudal} m³/s en {fecha} [{estado}]"
        )
    lineas.append(
        "Un caudal muy por encima de lo típico para ese mes/río es indicio de "
        "crecida -- esto NO es una alerta oficial de inundación, para eso "
        "consulta directamente al IDEAM/UNGRD."
    )
    return "\n".join(lineas)


if __name__ == "__main__":
    import json

    print("Estaciones en Atlántico:")
    print(json.dumps(buscar_estaciones(departamento="Atlántico", limit=5), ensure_ascii=False, indent=2))

    print("\nCaudal reciente en Lloró, Chocó:")
    print(formatear_caudal(caudal_por_municipio("Lloró", "Chocó")))
