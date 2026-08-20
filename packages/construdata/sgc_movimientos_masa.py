"""
Consulta en vivo el Inventario Nacional de Movimientos en Masa (SIMMA,
Sistema de Información de Movimientos en Masa) del SGC -- deslizamientos,
flujos, caídas y reptación, escala 1:25.000.

Encontrado 2026-08-19/20 en el catálogo DCAT de datos.sgc.gov.co, junto con
el visor público simma.sgc.gov.co (misma fuente de datos, distinta UI).
A diferencia de la amenaza sísmica por municipio (sgc_amenaza_sismica.py),
este servicio NO tiene un campo de municipio ni departamento -- son puntos
geográficos de eventos individuales (esriGeometryPoint), sin atributo para
filtrar por nombre de lugar. Se consulta con una búsqueda espacial por
radio alrededor de un punto (lat/lon) -- normalmente el centroide del
municipio, reutilizando las coordenadas que ya trae
sgc_amenaza_sismica.detectar_municipio_en_texto() (campos 'latitud'/
'longitud' de ese módulo).

Verificado en vivo (2026-08-20) contra Barranquilla: 66 eventos reales
dentro de 15 km, mayoría 'Flujo de lodo'.
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

log = logging.getLogger(__name__)

_SERVICE_URL = (
    "https://services1.arcgis.com/Og2nrTKe5bptW02d/arcgis/rest/services/"
    "Inventario_de_movimientos_en_masa/FeatureServer/0/query"
)
_TIMEOUT_SEGUNDOS = 8.0
_RADIO_METROS_DEFECTO = 15000  # 15 km -- lo bastante amplio para dar contexto
# regional sin ser tan grande que pierda sentido como "cerca de tu municipio"
_MAX_REGISTROS = 2000  # maxRecordCount real del servicio (confirmado vía /0?f=json)


def consultar_movimientos_cercanos(
    lat: float, lon: float, radio_metros: int = _RADIO_METROS_DEFECTO
) -> Optional[dict]:
    """Busca eventos de movimiento en masa dentro de `radio_metros` del
    punto dado. Devuelve {total, truncado, por_tipo: {tipo: count},
    radio_km} o None si el servicio no responde -- nunca lanza, mismo
    contrato de "nunca romper el camino normal" que sgc_amenaza_sismica."""
    try:
        resp = httpx.get(
            _SERVICE_URL,
            params={
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "distance": radio_metros,
                "units": "esriSRUnit_Meter",
                "outFields": "TIPO,SUBTIPO",
                "returnGeometry": "false",
                "resultRecordCount": _MAX_REGISTROS,
                "f": "json",
            },
            timeout=_TIMEOUT_SEGUNDOS,
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            log.warning(f"SIMMA movimientos en masa: error del servicio ({data['error']})")
            return None
        features = data.get("features", [])
        por_tipo: dict[str, int] = {}
        for feat in features:
            tipo = (feat.get("attributes", {}).get("TIPO") or "Sin clasificar").strip()
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        return {
            "total": len(features),
            "truncado": len(features) >= _MAX_REGISTROS,
            "por_tipo": por_tipo,
            "radio_km": radio_metros / 1000,
        }
    except Exception as e:
        log.warning(f"SIMMA movimientos en masa: servicio no disponible ({e}) -- se sigue sin este dato")
        return None


def formatear_respuesta(resultado: dict, municipio: str) -> str:
    radio = f"{resultado['radio_km']:.0f} km"
    if resultado["total"] == 0:
        return (
            f"El Inventario Nacional de Movimientos en Masa del SGC (SIMMA) no registra "
            f"eventos catalogados dentro de {radio} de {municipio}. Esto no garantiza "
            f"ausencia de riesgo -- el inventario depende de reportes históricos, no de "
            f"un monitoreo exhaustivo -- pero no hay antecedentes documentados en la zona."
        )
    tipos_ordenados = sorted(resultado["por_tipo"].items(), key=lambda x: -x[1])
    tipos_txt = ", ".join(f"{v} de tipo {k.lower()}" for k, v in tipos_ordenados)
    total_txt = f"{resultado['total']}+" if resultado["truncado"] else str(resultado["total"])
    return (
        f"El Inventario Nacional de Movimientos en Masa del SGC (SIMMA) registra "
        f"{total_txt} evento(s) histórico(s) dentro de {radio} de {municipio} ({tipos_txt}). "
        f"Es un antecedente real de inestabilidad de terreno en la región -- no implica que "
        f"un punto específico esté en riesgo, pero sí que la zona tiene historial documentado "
        f"de movimientos en masa."
    )
