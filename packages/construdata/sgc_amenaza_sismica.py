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
caerse sin aviso. Por eso: (a) caché en memoria del proceso -- los
valores de Aa/Av por municipio no cambian en la práctica, así que basta
con traerlos una vez por vida del proceso; (b) timeout corto; (c) NUNCA
lanza una excepción hacia el caller -- cualquier fallo (timeout, 404,
JSON inválido, servicio caído) devuelve None/{} y quien llama sigue con
el camino normal de motor_chunks/RAG sin este dato adicional.
"""
from __future__ import annotations

import logging
import unicodedata
from typing import Optional

import httpx

log = logging.getLogger(__name__)

_SERVICE_URL = (
    "http://srvags.sgc.gov.co/arcgis/rest/services/"
    "Zonas_amenaza_Sismica_NR10/Municipios_Amenaza_NR10/MapServer/0/query"
)
_TIMEOUT_SEGUNDOS = 6.0

_cache: Optional[dict[str, dict]] = None  # nombre normalizado -> registro


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


def _cargar_cache() -> dict[str, dict]:
    global _cache
    if _cache is not None:
        return _cache
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
        cache: dict[str, dict] = {}
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
            cache[_normalizar(nombre)] = {
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
            }
        if not cache:
            log.warning("SGC amenaza sísmica: respuesta sin features, no se cachea vacío")
            return {}
        _cache = cache
        log.info(f"SGC amenaza sísmica: {len(cache)} municipios cacheados desde srvags.sgc.gov.co")
        return cache
    except Exception as e:
        log.warning(f"SGC amenaza sísmica: servicio no disponible ({e}) -- se sigue sin este dato")
        return {}


_VENTANA_MAX_PALABRAS = 4  # el municipio compuesto más largo (ej. "San Jose De Ure") cabe en 4 palabras


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
    palabras = _normalizar(texto).split()
    for i in range(len(palabras)):
        for tam in range(min(_VENTANA_MAX_PALABRAS, len(palabras) - i), 0, -1):
            candidato = " ".join(palabras[i:i + tam])
            if tam == 1 and len(candidato) < 4:
                continue  # nombres de 1-2-3 letras dan demasiados falsos positivos
            registro = cache.get(candidato)
            if registro:
                return registro
    return None


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
        "(Zonas_amenaza_Sismica_NR10), consultado en vivo -- cubre los "
        "1.122 municipios de Colombia, no solo las ciudades cargadas "
        "manualmente en el resto del corpus."
    )
    return "".join(partes)
