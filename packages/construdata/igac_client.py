"""
Cliente ligero para el dataset abierto de Unidades Físicas Homogéneas (UFH)
del IGAC/UPRA, expuesto vía la plataforma Socrata de datos.gov.co (API SODA,
JSON, sin API key ni cuenta -- mismo patrón que ideam_client.py).

Contexto: el usuario pidió "restricciones geográficas y suelos típicos" por
región para GeoPot. El geovisor interactivo real del IGAC ("Colombia en
Mapas") consulta un backend propio no documentado
(serviciosgeovisor.igac.gov.co:8080/Geovisor) -- no una API REST pública
como SGC/IDEAM/INVIAS, así que forzarlo sería frágil y no verificable.
En su lugar, el dataset real usado aquí es un producto oficial de datos
abiertos (IGAC/UPRA) publicado en la MISMA plataforma que IDEAM
(datos.gov.co), con cobertura nacional verificada en vivo el 2026-08-21
(los 31 departamentos rurales de Colombia -- no incluye Bogotá D.C. ni San
Andrés, coherente con que este dataset es de suelo RURAL, no urbano).

Dataset: "Unidades físicas homogéneas en Colombia para el cálculo de la
Unidad Agrícola Familiar - UAF" (IGAC/UPRA), resource id fy2r-gwsd.
Combina clima + relieve + material parental + suelos -- da taxonomía de
suelo, textura, drenaje, inundabilidad, profundidad radicular,
pedregosidad, salinidad, pH y altitud por polígono dentro de cada
municipio. Es justo el tipo de "restricción geográfica/suelo típico" que
un ingeniero necesita como primer indicio antes de un estudio geotécnico
real (H.1 NSR-10 sigue siendo obligatorio -- esto NO lo reemplaza, es
contexto adicional).

Desde 2026-08-22 el dataset completo (169.088 filas) también está cargado
en Supabase (igac_suelos_ufh, ver
scripts/ingesta/igac_suelos/cargar_suelos_ufh.py) -- este módulo consulta
ahí PRIMERO (más rápido, no depende de datos.gov.co en el camino crítico
de cada pregunta) y solo cae a la consulta en vivo por Socrata si Supabase
no responde o no tiene el municipio (tabla vacía, credenciales ausentes).
El dato en sí es esencialmente estático (taxonomía de suelo no cambia con
el tiempo, a diferencia del caudal del IDEAM), así que no hace falta
recargar seguido -- solo si el IGAC/UPRA publica una versión nueva.

Uso:
    from igac_client import consultar_suelos_municipio

    unidades = consultar_suelos_municipio("Repelón", "Atlántico")
"""
from __future__ import annotations

import os
import unicodedata
from typing import Optional

import httpx

BASE_URL = "https://www.datos.gov.co/resource"
DATASET_UFH = "fy2r-gwsd"  # Unidades Físicas Homogéneas (IGAC/UPRA)

_TIMEOUT = 15.0

_CAMPOS = (
    "municipio,departamen,taxonomia,textura,pendiente,drenaje,inund,"
    "profundi,pedrego,salinidad,ph,alt_msnm,clase_ufh,area_ha"
)


def _get(params: dict) -> list[dict]:
    url = f"{BASE_URL}/{DATASET_UFH}.json"
    with httpx.Client(timeout=_TIMEOUT) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _where_exacto(campo: str, valor: str) -> str:
    """Igualdad exacta -- NUNCA LIKE para departamento: 'Cauca' matchearía
    'Valle Del Cauca' por substring, mismo bug real encontrado y corregido
    en ideam_client.py 2026-08-21. Este dataset viene con tildes consistentes
    en los 31 departamentos rurales (verificado en vivo), así que la
    igualdad exacta case-insensitive es suficiente sin normalizador aparte."""
    escapado = valor.replace("'", "''")
    return f"upper({campo}) = upper('{escapado}')"


_CAMPOS_SUPABASE = (
    "municipio,departamento,taxonomia,textura,pendiente,drenaje,inund,"
    "profundi,pedrego,salinidad,ph,alt_msnm,clase_ufh,area_ha"
)

_sb_client = None  # cacheado a nivel de módulo -- ver _obtener_cliente_supabase()


def _obtener_cliente_supabase():
    """A diferencia de sgc_amenaza_sismica.py (que solo consulta Supabase
    UNA vez por vida del proceso, al llenar su caché en memoria), esta
    ruta se ejecuta en CADA pregunta del chat que menciona un municipio --
    crear un cliente nuevo (y su handshake TLS) cada vez era un costo real
    e innecesario. Se cachea una sola vez; None si no hay credenciales o
    falla la creación, para que el caller siga con el respaldo en vivo."""
    global _sb_client
    if _sb_client is not None:
        return _sb_client
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            return None
        from supabase import create_client
        _sb_client = create_client(url, key)
        return _sb_client
    except Exception:
        return None


def _consultar_supabase(municipio: str, departamento: Optional[str], limit: int) -> list[dict]:
    """Ruta primaria: leer el catálogo ya persistido (ver
    scripts/ingesta/igac_suelos/cargar_suelos_ufh.py). Cualquier fallo
    (credenciales ausentes, tabla vacía, sin match, red) devuelve [] para
    que consultar_suelos_municipio() intente Socrata en vivo como
    respaldo.

    Igualdad exacta sobre municipio_norm/departamento_norm (columnas
    generadas = upper(municipio)/upper(departamento)), NO ilike: bug de
    rendimiento real encontrado al verificar esta consulta -- ILIKE nunca
    usa un índice funcional sobre upper() aunque el valor no tenga
    comodines (Parallel Seq Scan sobre 169.088 filas, ~215ms verificado
    con EXPLAIN ANALYZE). Con igualdad exacta + índice normal, la misma
    consulta baja a ~0.4ms server-side."""
    try:
        sb = _obtener_cliente_supabase()
        if sb is None:
            return []

        def _query(con_departamento: bool):
            q = sb.table("igac_suelos_ufh").select(_CAMPOS_SUPABASE).eq("municipio_norm", municipio.upper())
            if con_departamento and departamento:
                q = q.eq("departamento_norm", departamento.upper())
            return q.order("area_ha", desc=True).limit(limit).execute().data or []

        filas = _query(con_departamento=True)
        if not filas and departamento:
            filas = _query(con_departamento=False)
        # Renombrar departamento -> departamen para igualar la forma que
        # devuelve _get() (nombre de campo real del dataset en Socrata) --
        # formatear_respuesta() no lo usa, pero otros consumidores podrían.
        return [
            {**{k: v for k, v in f.items() if k != "departamento"}, "departamen": f.get("departamento")}
            for f in filas
        ]
    except Exception:
        return []


def consultar_suelos_municipio(
    municipio: str,
    departamento: Optional[str] = None,
    limit: int = 8,
) -> list[dict]:
    """Unidades físicas homogéneas (taxonomía de suelo, textura, drenaje,
    inundabilidad, profundidad, pedregosidad, salinidad, pH, altitud) para
    un municipio. Un municipio real tiene varios polígonos/unidades de
    suelo distintas -- se devuelven hasta `limit`, ordenadas por área
    descendente (las unidades más grandes son las más representativas del
    municipio). Devuelve lista vacía si no hay match (municipio urbano sin
    cobertura rural, o nombre no reconocido) -- nunca lanza, degrada según
    el mismo patrón que ideam_client.py/sgc_amenaza_sismica.py."""
    filas = _consultar_supabase(municipio, departamento, limit)
    if filas:
        return filas

    # Respaldo: Supabase no tuvo match (o no está disponible) -- consulta
    # en vivo por Socrata, igual que antes de tener la tabla cargada.
    wheres = [_where_exacto("municipio", municipio)]
    if departamento:
        wheres.append(_where_exacto("departamen", departamento))
    params = {
        "$select": _CAMPOS,
        "$where": " and ".join(wheres),
        "$order": "area_ha DESC",
        "$limit": limit,
    }
    try:
        resultado = _get(params)
    except httpx.HTTPError:
        return []

    if resultado or not departamento:
        return resultado

    # Reintento sin filtro de departamento: cubre el caso en que el nombre
    # de departamento resuelto por otro módulo (ej. sgc_amenaza_sismica)
    # no coincide carácter a carácter con la forma almacenada aquí (fuentes
    # distintas, mismo dato geográfico). Municipio solo, exacto, sigue
    # siendo lo bastante específico -- los nombres de municipio colombianos
    # rara vez se repiten entre departamentos con la misma grafía exacta.
    params_sin_depto = {**params, "$where": _where_exacto("municipio", municipio)}
    try:
        return _get(params_sin_depto)
    except httpx.HTTPError:
        return []


def formatear_respuesta(unidades: list[dict], municipio: str) -> str:
    """Arma el bloque de contexto en vivo del IGAC para inyectar en el RAG
    -- mismo espíritu que sgc_amenaza_sismica.formatear_respuesta()."""
    if not unidades:
        return ""
    lineas = [
        f"Unidades físicas homogéneas de suelo en {municipio} (IGAC/UPRA, "
        "dataset nacional de suelos rurales):"
    ]
    for u in unidades:
        taxonomia = u.get("taxonomia") or "sin dato"
        if taxonomia.strip().lower() == "cuerpos de agua":
            continue  # no aporta como "suelo típico" -- es agua, no terreno
        partes = [f"- Taxonomía {taxonomia}"]
        if u.get("textura") and u["textura"] != "No aplica":
            partes.append(f"textura {u['textura']}")
        if u.get("drenaje") and u["drenaje"] != "No aplica":
            partes.append(f"drenaje {u['drenaje']}")
        if u.get("inund") and u["inund"] not in ("No aplica", "No hay"):
            partes.append(f"⚠️ inundabilidad: {u['inund']}")
        if u.get("profundi") and u["profundi"] != "No aplica":
            partes.append(f"profundidad radicular {u['profundi']}")
        if u.get("pedrego") and u["pedrego"] not in ("No aplica", "No pedregoso"):
            partes.append(f"⚠️ {u['pedrego']}")
        if u.get("salinidad") and u["salinidad"] not in ("No aplica", "No salino"):
            partes.append(f"⚠️ {u['salinidad']}")
        if u.get("ph") and u["ph"] not in ("0.0", "0"):
            partes.append(f"pH {u['ph']}")
        area = u.get("area_ha")
        if area:
            try:
                partes.append(f"~{float(area):,.0f} ha")
            except (TypeError, ValueError):
                pass
        lineas.append("  " + ", ".join(partes))
    lineas.append(
        "Esto es una referencia general por zona, NO reemplaza el estudio "
        "geotécnico obligatorio (NSR-10 Título H) para ningún proyecto real."
    )
    return "\n".join(lineas)


if __name__ == "__main__":
    print(formatear_respuesta(consultar_suelos_municipio("Repelón", "Atlántico"), "Repelón"))
