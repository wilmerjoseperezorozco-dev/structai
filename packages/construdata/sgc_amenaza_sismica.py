"""
Consulta en vivo el servicio geográfico del SGC (Servicio Geológico
Colombiano) con los valores oficiales de amenaza sísmica NSR-10 (Aa, Av,
Ae, Ad, zona de amenaza) por municipio -- cobertura de los 1.122
municipios de Colombia, no solo las ciudades que ya tenemos troceadas a
mano en NSR-10/motor_chunks.

Encontrado 2026-08-20 investigando los links de Drive/SGC que compartió
el usuario: el visor público "Zonas de Amenaza Sísmica" del Hub de datos
abiertos del SGC (datos.sgc.gov.co) no expone descarga en su catálogo
DCAT (solo un link a la página web del visor), pero SÍ tiene un
MapServer real detrás -- no documentado públicamente en el catálogo,
encontrado inspeccionando el JSON de definición del Web Map
(items/{id}/data?f=json -> operationalLayers[].url). Verificado en vivo
contra Barranquilla: Aa=0.10, Av=0.10, zona="Baja" -- coincide
exactamente con el valor oficial de NSR-10 ya usado en
test_rag_nsr10_regresion.py::A-Aa-Av-Barranquilla.

Riesgo real y por qué este módulo nunca puede romper nada: es un
endpoint no documentado oficialmente (srvags.sgc.gov.co, HTTP no HTTPS,
fuera del dominio datos.sgc.gov.co que sí es soportado), puede cambiar o
caerse sin aviso. Por eso: (a) el dato se lee primero de Supabase
(sgc_amenaza_sismica_municipios, cargada una vez por
scripts/ingesta/sgc_amenaza_sismica/cargar_municipios.py) -- rápido y no
depende de ese endpoint en el camino crítico; el endpoint en vivo queda
solo como respaldo si la tabla estuviera vacía; (b) una vez leído (de
donde sea), caché en memoria del proceso -- los valores de Aa/Av por
municipio no cambian en la práctica, así que basta con traerlos una vez
por vida del proceso; (c) timeout corto en la ruta en vivo; (d) NUNCA
lanza una excepción hacia el caller -- cualquier fallo (timeout, 404,
JSON inválido, servicio caído, Supabase no disponible) devuelve None/{}
y quien llama sigue con el camino normal de motor_chunks/RAG sin este
dato adicional.

Bug real encontrado 2026-08-22 al cargar esta tabla por primera vez: el
servicio del SGC reporta 1.123 municipios, pero 68 nombres se repiten en
más de un departamento (Candelaria existe en Valle del Cauca Y Atlántico;
Armenia en Quindío Y Antioquia; etc.) -- una clave de caché por nombre
solamente pierde silenciosamente 86 de esos 1.123. Por eso el caché
agrupa por nombre pero guarda una LISTA de registros (uno por
departamento) en vez de sobrescribir.
"""
from __future__ import annotations

import logging
import os
import unicodedata
from typing import Optional

import httpx

log = logging.getLogger(__name__)

_SERVICE_URL = (
    "http://srvags.sgc.gov.co/arcgis/rest/services/"
    "Zonas_amenaza_Sismica_NR10/Municipios_Amenaza_NR10/MapServer/0/query"
)
_TIMEOUT_SEGUNDOS = 6.0

_cache: Optional[dict[str, list[dict]]] = None  # nombre normalizado -> [registro, ...]


def _normalizar(texto: str) -> str:
    """Sin tildes, sin puntuación, mayúsculas, espacios simples -- para
    matchear nombres de municipio contra texto libre sin depender de que
    el usuario escriba tildes correctamente (ej. 'Sincelejo' vs
    'SINCELEJO', 'Bogota' vs 'Bogotá') ni de que el nombre quede pegado a
    signos de puntuación (ej. 'Tuchín,' con coma al final de una frase --
    encontrado real probando este módulo: sin este paso 'TUCHIN,' nunca
    matcheaba contra la clave de caché 'TUCHIN')."""
    nfkd = unicodedata.normalize("NFKD", texto.upper())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    solo_alfanumerico = "".join(c if c.isalnum() or c.isspace() else " " for c in sin_tildes)
    return " ".join(solo_alfanumerico.split())


_PAGINA = 1000  # el servicio reporta maxRecordCount=1000 pese a tener 1.123 registros


def _agrupar(registros: list[dict]) -> dict[str, list[dict]]:
    """Agrupa por nombre de municipio normalizado, preservando TODOS los
    registros por nombre (no solo el último) -- 68 nombres de municipio se
    repiten entre departamentos, sobrescribir con una clave simple pierde
    86 de los 1.123 municipios reales (bug encontrado 2026-08-22)."""
    agrupado: dict[str, list[dict]] = {}
    for r in registros:
        agrupado.setdefault(_normalizar(r["municipio"]), []).append(r)
    return agrupado


def _cargar_desde_supabase() -> dict[str, list[dict]]:
    """Ruta primaria: leer el catálogo ya persistido (ver
    scripts/ingesta/sgc_amenaza_sismica/cargar_municipios.py). Rápido y no
    depende del endpoint no oficial del SGC en el camino crítico. Cualquier
    fallo (credenciales ausentes, tabla vacía, red) devuelve {} para que
    _cargar_cache() intente la ruta en vivo como respaldo."""
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            return {}
        from supabase import create_client
        sb = create_client(url, key)
        # `.select("*").execute()` sin paginar se trunca en silencio al
        # límite de PostgREST (1.000 filas) -- Colombia tiene 1.121
        # municipios reales en esta tabla (confirmado con `select count(*)`
        # el 2026-09-03, mismo bug encontrado ese día en
        # pais_zonificacion.py para Perú), así que sin paginar se perdían
        # ~121 municipios (~11%) del lookup de Aa/Av en silencio. Pagina
        # con .range() hasta agotar la tabla.
        _TAMANO_PAGINA = 1000
        filas: list[dict] = []
        inicio = 0
        while True:
            pagina = (
                sb.table("sgc_amenaza_sismica_municipios")
                .select("*")
                .range(inicio, inicio + _TAMANO_PAGINA - 1)
                .execute()
                .data
                or []
            )
            filas.extend(pagina)
            if len(pagina) < _TAMANO_PAGINA:
                break
            inicio += _TAMANO_PAGINA
        if not filas:
            return {}
        registros = [
            {
                "municipio": f["municipio"],
                "departamento": f.get("departamento") or "",
                "aa": f.get("aa"),
                "av": f.get("av"),
                "ae": f.get("ae"),
                "ad": f.get("ad"),
                "zona": f.get("zona"),
                "longitud": f.get("longitud"),
                "latitud": f.get("latitud"),
            }
            for f in filas
        ]
        cache = _agrupar(registros)
        log.info(f"SGC amenaza sísmica: {len(filas)} municipios cargados desde Supabase (caché persistido)")
        return cache
    except Exception as e:
        log.warning(f"SGC amenaza sísmica: Supabase no disponible ({e}) -- se intenta el servicio en vivo")
        return {}


def _cargar_desde_servicio_vivo() -> dict[str, list[dict]]:
    """Ruta de respaldo: el endpoint no oficial srvags.sgc.gov.co, solo si
    Supabase no tiene el dato (tabla vacía o sin credenciales)."""
    try:
        features: list[dict] = []
        offset = 0
        while True:
            resp = httpx.get(
                _SERVICE_URL,
                params={
                    "where": "1=1",
                    "outFields": "NOMBRE_MUNICIPIO,NOMBRE_DEPARTAMENTO,AA,AV,AE,AD,ZONA_AMENAZA_SÍSMICA,LONGITUD,LATITUD",
                    "f": "json",
                    "returnGeometry": "false",
                    "resultOffset": offset,
                    "resultRecordCount": _PAGINA,
                },
                timeout=_TIMEOUT_SEGUNDOS,
            )
            resp.raise_for_status()
            data = resp.json()
            pagina = data.get("features", [])
            features.extend(pagina)
            # ArcGIS marca exceededTransferLimit=True solo cuando hay más páginas
            # -- confiar en ese flag, no en el tamaño de la página (una página
            # intermedia podría venir justo con 1000 y aun así ser la última).
            if not data.get("exceededTransferLimit") or not pagina:
                break
            offset += _PAGINA
        registros: list[dict] = []
        for feat in features:
            attrs = feat.get("attributes", {})
            nombre = attrs.get("NOMBRE_MUNICIPIO")
            if not nombre:
                continue
            zona = None
            for k, v in attrs.items():
                if k.upper().startswith("ZONA_AMENAZA"):
                    zona = v
                    break
            registros.append({
                "municipio": nombre.title(),
                "departamento": (attrs.get("NOMBRE_DEPARTAMENTO") or "").title(),
                "aa": attrs.get("AA"),
                "av": attrs.get("AV"),
                "ae": attrs.get("AE"),
                "ad": attrs.get("AD"),
                "zona": zona,
                # Coordenadas del municipio -- se reutilizan para la consulta
                # espacial de movimientos en masa (SIMMA), que no tiene campo
                # de municipio propio, solo geometría de punto. Ver
                # sgc_movimientos_masa.py.
                "longitud": attrs.get("LONGITUD"),
                "latitud": attrs.get("LATITUD"),
            })
        if not registros:
            log.warning("SGC amenaza sísmica: respuesta sin features, no se cachea vacío")
            return {}
        cache = _agrupar(registros)
        log.info(f"SGC amenaza sísmica: {len(registros)} municipios cacheados desde srvags.sgc.gov.co (servicio en vivo)")
        return cache
    except Exception as e:
        log.warning(f"SGC amenaza sísmica: servicio no disponible ({e}) -- se sigue sin este dato")
        return {}


def _cargar_cache() -> dict[str, list[dict]]:
    global _cache
    if _cache is not None:
        return _cache
    cache = _cargar_desde_supabase() or _cargar_desde_servicio_vivo()
    if cache:
        _cache = cache
    return cache


_VENTANA_MAX_PALABRAS = 4  # el municipio compuesto más largo (ej. "San Jose De Ure") cabe en 4 palabras

# Nombres de un municipio real que coinciden con una palabra tan común en
# cualquier pregunta sobre el país que el match nunca es el que el usuario
# quiso decir. Bug real encontrado 2026-08-20 con Groq en vivo: existe un
# municipio llamado "Colombia" (Huila) -- una pregunta como "noticias
# recientes de desastres en Colombia... cerca de Barranquilla" matcheaba
# "COLOMBIA" (por aparecer primero en el texto) en vez de "BARRANQUILLA",
# devolviendo Aa/Av de un municipio de Huila irrelevante y silenciando la
# pregunta real. "Colombia" como nombre de país nunca debe interceptarse
# como municipio -- si alguna vez alguien pregunta específicamente por el
# municipio de Colombia, Huila, tendrá que ser más explícito.
_EXCLUIDOS = {"COLOMBIA"}


def detectar_municipio_en_texto(texto: str) -> Optional[dict]:
    """Busca si alguno de los 1.123 municipios de Colombia aparece
    mencionado en el texto (pregunta del usuario). Devuelve el registro
    de amenaza sísmica del PRIMER municipio que aparece leyendo el texto
    de izquierda a derecha, o None si no hay match o el servicio no
    respondió.

    Por qué escanear por posición y no solo buscar en el diccionario:
    Colombia repite nombres de lugar entre departamento y municipio (ej.
    'Córdoba' es tanto un departamento como, aparte, un municipio real de
    Bolívar) -- una pregunta como 'municipio de Tuchín, Córdoba' contiene
    dos nombres de municipio válidos ('Tuchín' y 'Córdoba'), y el usuario
    casi siempre nombra el lugar específico ANTES del departamento que lo
    aclara. Iterar el diccionario de caché en vez de la posición real en
    el texto devolvía 'Córdoba' en vez de 'Tuchín' en ese caso real
    (encontrado probando este módulo) -- se corrigió escaneando palabra
    por palabra en el orden en que aparecen y devolviendo la primera
    coincidencia, probando ventanas de varias palabras primero (para no
    partir un nombre compuesto como 'SAN ANDRES') antes de una sola
    palabra."""
    cache = _cargar_cache()
    if not cache:
        return None
    texto_normalizado = _normalizar(texto)
    palabras = texto_normalizado.split()
    for i in range(len(palabras)):
        for tam in range(min(_VENTANA_MAX_PALABRAS, len(palabras) - i), 0, -1):
            candidato = " ".join(palabras[i:i + tam])
            if tam == 1 and len(candidato) < 4:
                continue  # nombres de 1-2-3 letras dan demasiados falsos positivos
            if candidato in _EXCLUIDOS:
                continue
            registros = cache.get(candidato)
            if registros:
                return _desambiguar(registros, texto_normalizado)
    return None


def _desambiguar(registros: list[dict], texto_normalizado: str) -> dict:
    """Cuando un nombre de municipio existe en más de un departamento (68
    casos reales, ver docstring del módulo), busca si el departamento
    correcto también aparece en el texto (patrón real: 'Tuchín, Córdoba')
    para elegir el registro correcto. Si no hay match de departamento (o
    solo hay un registro), devuelve el primero -- mismo comportamiento que
    antes de este fix, ahora explícito en vez de accidental."""
    if len(registros) == 1:
        return registros[0]
    for r in registros:
        depto_normalizado = _normalizar(r.get("departamento") or "")
        if depto_normalizado and depto_normalizado in texto_normalizado:
            return r
    return registros[0]


def formatear_respuesta(registro: dict) -> str:
    zona = registro.get("zona") or "no especificada"
    partes = [
        f"Según el Servicio Geológico Colombiano (SGC), el municipio de "
        f"{registro['municipio']} ({registro['departamento']}) tiene zona de "
        f"amenaza sísmica **{zona}** según NSR-10, con Aa = {registro['aa']} "
        f"y Av = {registro['av']}"
    ]
    if registro.get("ae") is not None:
        partes.append(f", Ae = {registro['ae']}")
    if registro.get("ad") is not None:
        partes.append(f", Ad = {registro['ad']}")
    partes.append(
        ". Fuente: servicio geográfico oficial del SGC "
        "(Zonas_amenaza_Sismica_NR10) -- cubre 1.121 municipios de "
        "Colombia (catálogo cargado en Supabase, con el servicio en vivo "
        "como respaldo), no solo las ciudades cargadas manualmente en el "
        "resto del corpus."
    )
    return "".join(partes)
