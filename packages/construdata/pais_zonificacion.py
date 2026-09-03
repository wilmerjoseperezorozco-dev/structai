"""
Detecta si una pregunta menciona una localidad de Perú o Ecuador ya
cargada en las tablas de zonificación sísmica exacta (ver
scripts/ingesta/peru_e030/cargar_zonificacion_anexo2_completo.py y
scripts/ingesta/ecuador_nec_se_ds/cargar_tabla16_poblaciones_factor_z.py)
y devuelve el registro correspondiente para enriquecer el contexto del
LLM -- mismo espíritu que sgc_amenaza_sismica.py para Colombia, pero sin
servicio en vivo externo: ambas tablas ya están completas en Supabase,
así que el caché se carga una sola vez por proceso directamente de ahí.

Deliberadamente separado del enriquecimiento SGC: solo se activa dentro
de las ramas "peru_e030"/"ecuador_nec_se_ds" de route_motores_multiples()
(ver rag_multi_norma.py), nunca de forma ambiental sobre CUALQUIER
pregunta -- muchos nombres de distrito/población son palabras comunes
(ej. "San Juan" existe en Perú, Ecuador Y Colombia) y activarlo sin que
la pregunta ya haya mencionado el país/norma explícitamente arriesgaría
enrutar mal una pregunta colombiana.

Perú (peru_e030_zonificacion_distrital): columna "distrito" ya es un
nombre limpio de un solo campo -- se indexa igual que los municipios de
Colombia (ver sgc_amenaza_sismica._normalizar/_agrupar).

Ecuador (ecuador_nec_se_ds_zonificacion_poblacion): la columna
"poblacion" combina POBLACIÓN+PARROQUIA+CANTÓN en un solo texto (ver
docstring de cargar_tabla16_poblaciones_factor_z.py -- el PDF fuente no
trae un delimitador confiable entre esas 3 celdas). Como el nombre de
POBLACIÓN real siempre es el primero, se indexa por PREFIJOS de 1 a 4
palabras de ese campo (ej. "MANTA MONTECRISTI MONTECRISTI" registra las
claves "MANTA", "MANTA MONTECRISTI" y "MANTA MONTECRISTI MONTECRISTI")
-- así una pregunta que solo dice "Manta" sí matchea, sin tener que
adivinar dónde termina el campo población dentro del texto fusionado.
"""
from __future__ import annotations

import logging
import os
import unicodedata
from typing import Optional

log = logging.getLogger(__name__)

_VENTANA_MAX_PALABRAS = 5  # el nombre compuesto más largo visto (Ecuador) cabe en 5 palabras

_cache_peru: Optional[dict[str, list[dict]]] = None
_cache_ecuador: Optional[dict[str, list[dict]]] = None


def _normalizar(texto: str) -> str:
    """Mismo criterio que sgc_amenaza_sismica._normalizar: sin tildes, sin
    puntuación, mayúsculas, espacios simples."""
    nfkd = unicodedata.normalize("NFKD", texto.upper())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    solo_alfanumerico = "".join(c if c.isalnum() or c.isspace() else " " for c in sin_tildes)
    return " ".join(solo_alfanumerico.split())


def _get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


_TAMANO_PAGINA_SUPABASE = 1000  # límite real de PostgREST por página, confirmado en vivo


def _fetch_paginado(sb, tabla: str) -> list[dict]:
    """`.select('*').execute()` sin paginar se trunca en silencio al límite
    de PostgREST (confirmado en vivo: 1.000 de 1.884 filas reales de
    peru_e030_zonificacion_distrital, perdiendo el 47% de los distritos sin
    ningún error -- así fue como Coracora/Parinacochas, provincia real del
    sismo M6.7-7.2 de Ayacucho del 2026-08-20, nunca se detectaba pese a
    estar cargada en la tabla desde el 2026-08-26). Pagina con .range()
    hasta agotar la tabla."""
    filas: list[dict] = []
    inicio = 0
    while True:
        pagina = (
            sb.table(tabla)
            .select("*")
            .range(inicio, inicio + _TAMANO_PAGINA_SUPABASE - 1)
            .execute()
            .data
            or []
        )
        filas.extend(pagina)
        if len(pagina) < _TAMANO_PAGINA_SUPABASE:
            break
        inicio += _TAMANO_PAGINA_SUPABASE
    return filas


def _cargar_cache_peru() -> dict[str, list[dict]]:
    global _cache_peru
    if _cache_peru is not None:
        return _cache_peru
    try:
        sb = _get_supabase_client()
        if sb is None:
            return {}
        filas = _fetch_paginado(sb, "peru_e030_zonificacion_distrital")
        cache: dict[str, list[dict]] = {}
        for f in filas:
            clave = _normalizar(f["distrito"])
            cache.setdefault(clave, []).append(f)
        _cache_peru = cache
        log.info(f"Perú zonificación: {len(filas)} distritos cargados desde Supabase")
        return cache
    except Exception as e:
        log.warning(f"Perú zonificación: Supabase no disponible ({e})")
        return {}


def _prefijos(texto_normalizado: str, max_palabras: int = 4) -> list[str]:
    """Todas las claves-prefijo de 1..max_palabras palabras de un texto
    normalizado, ej. 'MANTA MONTECRISTI MONTECRISTI' con max=4 ->
    ['MANTA', 'MANTA MONTECRISTI', 'MANTA MONTECRISTI MONTECRISTI']."""
    palabras = texto_normalizado.split()
    claves = []
    for tam in range(1, min(max_palabras, len(palabras)) + 1):
        claves.append(" ".join(palabras[:tam]))
    return claves


def _cargar_cache_ecuador() -> dict[str, list[dict]]:
    global _cache_ecuador
    if _cache_ecuador is not None:
        return _cache_ecuador
    try:
        sb = _get_supabase_client()
        if sb is None:
            return {}
        filas = _fetch_paginado(sb, "ecuador_nec_se_ds_zonificacion_poblacion")
        cache: dict[str, list[dict]] = {}
        for f in filas:
            texto_normalizado = _normalizar(f["poblacion"])
            for clave in _prefijos(texto_normalizado, max_palabras=4):
                if len(clave.split()) == 1 and len(clave) < 4:
                    continue  # nombres de 1-3 letras dan demasiados falsos positivos
                cache.setdefault(clave, []).append(f)
        _cache_ecuador = cache
        log.info(f"Ecuador zonificación: {len(filas)} poblaciones cargadas desde Supabase")
        return cache
    except Exception as e:
        log.warning(f"Ecuador zonificación: Supabase no disponible ({e})")
        return {}


def detectar_distrito_peru_en_texto(texto: str) -> Optional[dict]:
    """Busca si alguno de los distritos de Perú (peru_e030_zonificacion_distrital,
    1.851 registros) aparece mencionado en el texto. Mismo algoritmo de
    escaneo por ventana de palabras que sgc_amenaza_sismica.detectar_municipio_en_texto
    (probar ventanas largas primero para no partir un nombre compuesto)."""
    cache = _cargar_cache_peru()
    if not cache:
        return None
    texto_normalizado = _normalizar(texto)
    palabras = texto_normalizado.split()
    for i in range(len(palabras)):
        for tam in range(min(_VENTANA_MAX_PALABRAS, len(palabras) - i), 0, -1):
            candidato = " ".join(palabras[i:i + tam])
            if tam == 1 and len(candidato) < 4:
                continue
            registros = cache.get(candidato)
            if registros:
                return registros[0]
    return None


def detectar_poblacion_ecuador_en_texto(texto: str) -> Optional[dict]:
    """Busca si alguna población de Ecuador (ecuador_nec_se_ds_zonificacion_poblacion,
    512 registros) aparece mencionada en el texto, usando el índice de
    prefijos (ver _cargar_cache_ecuador)."""
    cache = _cargar_cache_ecuador()
    if not cache:
        return None
    texto_normalizado = _normalizar(texto)
    palabras = texto_normalizado.split()
    for i in range(len(palabras)):
        for tam in range(min(_VENTANA_MAX_PALABRAS, len(palabras) - i), 0, -1):
            candidato = " ".join(palabras[i:i + tam])
            if tam == 1 and len(candidato) < 4:
                continue
            registros = cache.get(candidato)
            if registros:
                return registros[0]
    return None


def formatear_dato_peru(registro: dict) -> str:
    return (
        f"Según el Anexo II de la Norma E.030 (Perú), el distrito de "
        f"{registro['distrito']} (provincia de {registro['provincia']}, "
        f"región {registro['region']}) está en la **zona sísmica "
        f"{registro['zona_sismica']}** (ámbito: {registro.get('ambito') or 'no especificado'}). "
        "Fuente: Anexo II de la E.030, cargado verbatim en Supabase "
        "(cobertura: las 24 regiones + Callao, 1.851 distritos)."
    )


def formatear_dato_ecuador(registro: dict) -> str:
    return (
        f"Según la Tabla 16 (Sección 10.2) de la NEC-SE-DS (Ecuador), "
        f"{registro['poblacion']} (provincia de {registro['provincia']}) "
        f"tiene un **factor de zona Z = {registro['factor_z']}**. "
        "Fuente: Tabla 16 de la NEC-SE-DS, cargada verbatim en Supabase "
        "-- listado de apoyo del propio MIDUVI, no exhaustivo (el método "
        "principal de Ecuador es el mapa de zonas sísmicas, Figura 1)."
    )
