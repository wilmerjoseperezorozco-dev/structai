"""
Noticias relevantes de Colombia vía Google News RSS -- desastres/sismos y
normativa de construcción, con búsquedas dirigidas (no "Colombia" a
secas, eso traería ruido de política/deportes/entretenimiento sin
ningún valor para StructAI).

Por qué Google News RSS y no scraping directo de RCN/Caracol: ninguno de
los dos expone un feed RSS público accesible (verificado 2026-08-20,
Caracol ni siquiera es alcanzable, RCN no muestra un link de
sindicación), y reproducir el texto completo de sus artículos sería un
problema real de derechos de autor -- son medios con contenido
protegido, no normas técnicas de acceso público como el SGC/IDEAM.
Google News RSS da exactamente el nivel correcto de uso: título +
resumen corto + link al original, con atribución a la fuente real.
Verificado en vivo: sí trae medios colombianos (El Tiempo, Semana) junto
con cobertura internacional (France 24, DW).

Uso:
    from noticias_colombia import actualizar_noticias, noticias_recientes
    resumen = actualizar_noticias(sb)          # trae y guarda lo nuevo
    ultimas = noticias_recientes(sb, categoria="desastre", limite=5)
"""
from __future__ import annotations

import html
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Literal, Optional
from urllib.parse import quote

import httpx

log = logging.getLogger(__name__)

_TIMEOUT_SEGUNDOS = 10.0
_USER_AGENT = "Mozilla/5.0 (compatible; StructAI/1.0; +https://structai.online)"

Categoria = Literal["desastre", "regulatoria"]

# Consultas curadas a propósito -- el objetivo es trazabilidad de lo que
# afecta directamente ingeniería civil/gestión del riesgo en Colombia, no
# ser un agregador de noticias general (eso compite mal con Google mismo).
_QUERIES: dict[Categoria, list[str]] = {
    "desastre": [
        "sismo Colombia",
        "terremoto Colombia",
        "derrumbe Colombia",
        "deslizamiento Colombia",
        "emergencia gestión del riesgo Colombia",
    ],
    "regulatoria": [
        "NSR-10 norma sismorresistente",
        "decreto construcción sismorresistente Colombia",
        "Servicio Geológico Colombiano decreto",
        "Ministerio de Vivienda norma construcción Colombia",
    ],
}


_TAG_HTML = re.compile(r"<[^>]+>")


def _limpiar_resumen(html_texto: str) -> str:
    """El campo <description> de Google News RSS trae un <a href=...> con el
    mismo título más el nombre de la fuente en <font> -- no prosa real que
    valga la pena guardar aparte del título. Se limpian las etiquetas para
    no meter HTML crudo al contexto que después lee Groq (o una futura UI)."""
    sin_tags = _TAG_HTML.sub(" ", html_texto)
    return " ".join(html.unescape(sin_tags).split())


def _rss_url(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=es-CO&gl=CO&ceid=CO:es"


def _parsear_fecha(pub_date: Optional[str]) -> Optional[datetime]:
    if not pub_date:
        return None
    try:
        return parsedate_to_datetime(pub_date)
    except Exception:
        return None


def _consultar_query(query: str, categoria: Categoria) -> Optional[list[dict]]:
    """Trae y parsea un feed RSS de Google News para una consulta puntual.
    Nunca lanza -- una consulta fallida devuelve None (para poder
    distinguirla de una consulta exitosa con 0 resultados reales) en vez
    de tumbar el resto del ciclo de actualización."""
    try:
        # follow_redirects=True es necesario: Google normaliza hl=es-CO a
        # hl=es-419 (español latinoamericano genérico) vía 302 -- sin esto,
        # httpx no sigue el redirect por defecto (a diferencia de un
        # navegador) y CADA consulta fallaba con RedirectNotFollowed,
        # encontrado real probando este módulo (2026-08-20).
        resp = httpx.get(
            _rss_url(query),
            timeout=_TIMEOUT_SEGUNDOS,
            headers={"User-Agent": _USER_AGENT},
            follow_redirects=True,
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items: list[dict] = []
        for item in root.findall(".//item"):
            titulo = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            if not titulo or not link:
                continue
            fuente_el = item.find("source")
            fuente = (fuente_el.text or "").strip() if fuente_el is not None and fuente_el.text else "Desconocida"
            fecha = _parsear_fecha(item.findtext("pubDate"))
            resumen = _limpiar_resumen(item.findtext("description") or "")
            items.append({
                "titulo": titulo,
                "link": link,
                "fuente": fuente,
                "categoria": categoria,
                "fecha_publicacion": fecha.isoformat() if fecha else None,
                "resumen": resumen[:500],
                "query_origen": query,
            })
        return items
    except Exception as e:
        log.warning(f"Noticias Colombia: fallo consultando '{query}' ({e})")
        return None


def actualizar_noticias(sb) -> dict:
    """Consulta todas las queries curadas (desastre + regulatoria) y hace
    upsert en noticias_relevantes (dedupe real por `link`, que tiene
    constraint UNIQUE). Devuelve {desastre: N, regulatoria: N, errores: N}
    -- nunca lanza, cada query/guardado que falla solo resta al contador,
    no tumba el resto del ciclo."""
    resumen = {"desastre": 0, "regulatoria": 0, "errores": 0}
    for categoria, queries in _QUERIES.items():
        for query in queries:
            items = _consultar_query(query, categoria)
            if items is None:
                resumen["errores"] += 1
                continue
            if not items:
                continue
            try:
                sb.table("noticias_relevantes").upsert(items, on_conflict="link").execute()
                resumen[categoria] += len(items)
            except Exception as e:
                log.warning(f"Noticias Colombia: fallo guardando resultados de '{query}' ({e})")
                resumen["errores"] += 1
    return resumen


def noticias_recientes(
    sb, categoria: Optional[Categoria] = None, limite: int = 10
) -> list[dict]:
    """Lee las noticias más recientes ya guardadas en Supabase -- NO vuelve
    a consultar Google (eso lo hace actualizar_noticias(), corrido aparte
    por el scheduler de apps/api). Nunca lanza; sin datos o con el
    servicio caído, devuelve lista vacía."""
    try:
        query = (
            sb.table("noticias_relevantes")
            .select("*")
            .order("fecha_publicacion", desc=True)
            .limit(limite)
        )
        if categoria:
            query = query.eq("categoria", categoria)
        result = query.execute()
        return result.data or []
    except Exception as e:
        log.warning(f"Noticias Colombia: fallo leyendo noticias recientes ({e})")
        return []
