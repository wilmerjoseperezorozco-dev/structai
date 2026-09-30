"""
Consulta la microzonificación sísmica LOCAL (tabla
microzonificacion_sismica_local, issue #76) -- reglamentación
sustitutiva de A.2.4/A.2.6 de NSR-10 que algunas ciudades colombianas
tienen APROBADA POR DECRETO y que, por A.2.9.1, es de carácter
OBLIGATORIO donde existe -- prima legalmente sobre el Aa/Av nacional
del Apéndice A-4.

Por qué esto NO reemplaza el Aa/Av nacional que ya muestra
sgc_amenaza_sismica.py: cada ciudad con microzonificación se divide en
varias zonas (16 en Bogotá, hasta 13 filas en Cali) según el suelo
local -- sin la geometría real de esas zonas (polígonos), no hay forma
de saber en cuál zona cae un predio específico solo a partir del
nombre del municipio. Mostrar UN valor cualquiera de zona como si fuera
"el" valor sería dar una falsa precisión, peor que no decir nada. Por
eso este módulo solo AVISA que existe una reglamentación sustitutiva
vigente y cuántas zonas tiene, con la fuente exacta -- nunca elige una
zona por el usuario.

Ciudades cargadas hoy (2026-09-30): Bogotá (Decreto 523/2010, 16
zonas), Santiago de Cali (Decreto 411.0.20.0158/2014, 10 zonas + 3 con
espectro de 2 tramos), Pereira (Decreto 932/2011, 7 zonas). Ver issue
#76 para el resto (Medellín, Popayán, Bucaramanga, Armenia, Manizales
-- ninguna con dato listo para ingestar todavía).
"""
from __future__ import annotations

import logging
import os
from typing import Optional

log = logging.getLogger(__name__)

_sb = None


def _cliente():
    global _sb
    if _sb is None:
        from supabase import create_client
        _sb = create_client(
            os.environ["SUPABASE_URL"],
            os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_KEY"],
        )
    return _sb


# Nombre de municipio (forma canónica que ya usa sgc_amenaza_sismica.py) ->
# nombre de ciudad tal como quedó guardado en microzonificacion_sismica_local.
# Se mantiene explícito (no un simple .upper()) porque las dos tablas no
# comparten la misma convención de nombre para todas las ciudades (ej.
# "Bogotá, D.C." vs "Bogotá, D.C." coinciden, pero "Santiago de Cali" en la
# tabla nueva vs "Cali" en sgc_amenaza_sismica_municipios NO).
_MAPA_MUNICIPIO_A_CIUDAD = {
    "Bogotá, D.C.": "Bogotá, D.C.",
    "Cali": "Santiago de Cali",
    "Pereira": "Pereira",
}

_cache_zonas: Optional[dict[str, list[dict]]] = None


def _cargar_cache() -> dict[str, list[dict]]:
    global _cache_zonas
    if _cache_zonas is not None:
        return _cache_zonas
    try:
        filas = (
            _cliente()
            .table("microzonificacion_sismica_local")
            .select("ciudad,zona,fuente,fecha_decreto")
            .execute()
            .data
            or []
        )
        cache: dict[str, list[dict]] = {}
        for f in filas:
            cache.setdefault(f["ciudad"], []).append(f)
        _cache_zonas = cache
        return cache
    except Exception as e:
        log.warning(f"microzonificación local: Supabase no disponible ({e}) -- se sigue sin este dato")
        return {}


def consultar_microzonificacion(municipio: str) -> Optional[dict]:
    """Si `municipio` (forma canónica de sgc_amenaza_sismica.py) tiene
    microzonificación sísmica local vigente, devuelve
    {ciudad, n_zonas, fuente, fecha_decreto} -- o None si no aplica o el
    servicio no responde. Nunca lanza."""
    ciudad = _MAPA_MUNICIPIO_A_CIUDAD.get(municipio)
    if not ciudad:
        return None
    cache = _cargar_cache()
    zonas = cache.get(ciudad)
    if not zonas:
        return None
    return {
        "ciudad": ciudad,
        "n_zonas": len(zonas),
        "fuente": zonas[0]["fuente"],
        "fecha_decreto": zonas[0]["fecha_decreto"],
    }


def formatear_aviso(resultado: dict) -> str:
    return (
        f"⚠️ **{resultado['ciudad']} tiene microzonificación sísmica local vigente** "
        f"({resultado['n_zonas']} zonas, decreto del {resultado['fecha_decreto']}) que "
        f"reemplaza legalmente los valores nacionales de Aa/Av/Fa/Fv de la sección A.2.4/A.2.6 "
        f"de NSR-10 mostrados arriba (A.2.9.1 -- carácter obligatorio y sustitutivo). "
        f"Los coeficientes exactos dependen de en cuál de las {resultado['n_zonas']} zonas "
        f"cae el predio específico -- StructAI todavía no ubica un predio dentro de esas zonas "
        f"automáticamente, así que **no se puede dar el valor exacto de zona desde aquí**. "
        f"Fuente: {resultado['fuente']}"
    )
