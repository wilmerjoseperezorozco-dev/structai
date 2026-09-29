"""
Consulta en vivo el servicio geográfico del IDEAM/SMByC (Sistema de
Monitoreo de Bosques y Carbono) con la clasificación oficial de cambio de
cobertura de bosque natural en Colombia, por punto -- deforestación,
regeneración, bosque estable, no bosque estable.

Encontrado 2026-09-29: el issue #67 asumía que este dato solo existía
como raster descargable (requiere GDAL, no una API por punto como el
resto de fuentes de StructAI) -- supuesto incorrecto, corregido con
evidencia real. Wilmer compartió el catálogo "Datos Abiertos" del SMByC
(visualizador.ideam.gov.co); investigando de dónde salía esa tabla
(embebida vía iframe desde un sitio estático independiente,
ecumelos.github.io/smbyc.github.io) se encontró el servicio real detrás:
un MapServer de capas ráster con operación `identify`, verificado en vivo
contra un punto real de Caquetá (-74.5, 2.0): devolvió
`"Raster.tipo_cob":"No bosque estable"` para el período 2020-2021.

Service URL:
    https://visualizador.ideam.gov.co/gisserver/rest/services/
    Dinamica_Cambio_Cobertura_Bosque/MapServer

16 capas reales (una por período: 1990-2000, 2000-2005, 2005-2010,
2010-2012, 2012-2013, 2013-2014, y anual 2014-2015 hasta 2023-2024).

Categorías: la leyenda oficial del servicio (`/MapServer/legend`) lista 5
etiquetas -- "Bosque Estable", "Deforestación", "Regeneración",
"No bosque estable", "Sin información" -- pero NO se asume que ese sea
el conjunto completo: una consulta real en selva profunda (Vaupés,
-70.5,0.8) devolvió la etiqueta **"Bosque"**, que no aparece en esa
leyenda de 5. La leyenda describe cómo se colorea el mapa de CAMBIO, no
necesariamente el dominio completo del campo `tipo_cob` de la tabla de
atributos del ráster -- este cliente nunca filtra por una lista cerrada
de categorías válidas (solo descarta `None`/"Sin información"), así que
una etiqueta no listada aquí simplemente se muestra tal cual, sin
romper.

Por qué se usa `_LAYER_MAS_RECIENTE_OFICIALIZADA = 12` por defecto: la
tabla de "Datos Abiertos" de IDEAM marca 2020-2021 como el último
período "Oficializada" (2021-2022 en adelante figuran "Sin oficializar"
a la fecha de esta verificación) -- usar un período no oficializado como
si fuera dato definitivo violaría la regla de honestidad de fuente del
proyecto. Esta constante es manual, no autodescubierta -- IDEAM oficializa
un nuevo período aproximadamente una vez al año; revisar la tabla de
Datos Abiertos (ver docstring de `_LAYERS`) y actualizarla cuando
corresponda, en vez de asumir que el período más reciente del servicio
ya es oficial.

Respaldo real si este servicio cambia o cae (ver issue #67): WMS/WCS en
el mismo host, y descarga FTP directa por año en
bart.ideam.gov.co/cneideam/Capasgeo/.
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

import divipola

log = logging.getLogger(__name__)

_SERVICE_URL = (
    "https://visualizador.ideam.gov.co/gisserver/rest/services/"
    "Dinamica_Cambio_Cobertura_Bosque/MapServer/identify"
)
_TIMEOUT_SEGUNDOS = 10.0

# id de capa -> periodo real, tal como los reporta el propio servicio
# (?f=json en la URL base) -- verificado en vivo 2026-09-29.
_LAYERS: dict[int, str] = {
    0: "1990-2000",
    1: "2000-2005",
    2: "2005-2010",
    3: "2010-2012",
    4: "2012-2013",
    5: "2013-2014",
    6: "2014-2015",
    7: "2015-2016",
    8: "2016-2017",
    9: "2017-2018",
    10: "2018-2019",
    11: "2019-2020",
    12: "2020-2021",
    13: "2021-2022",  # sin oficializar a la fecha de esta verificación
    14: "2022-2023",  # sin oficializar a la fecha de esta verificación
    15: "2023-2024",  # sin oficializar a la fecha de esta verificación
}
_LAYER_MAS_RECIENTE_OFICIALIZADA = 12  # "2020-2021" -- ver docstring del módulo

_CATEGORIAS_ALERTA = {"Deforestación"}


def consultar_cambio_bosque(
    municipio: str, departamento: Optional[str] = None, layer_id: int = _LAYER_MAS_RECIENTE_OFICIALIZADA
) -> Optional[dict]:
    """Resuelve el municipio a coordenadas reales (DIVIPOLA, vía
    divipola.py) y consulta la clasificación real de cambio de bosque en
    ese punto para el período dado. Devuelve
    {municipio, departamento, periodo, categoria} o None si el municipio
    no resuelve, el servicio no responde, o la categoría es "Sin
    información" -- nunca lanza, mismo contrato de "nunca romper el
    camino normal" que sgc_amenaza_sismica/sgc_movimientos_masa.

    Nota real sobre precisión: es UN punto (el centroide del municipio),
    no un agregado de toda el área municipal -- un municipio grande y
    heterogéneo puede tener zonas con clasificaciones distintas a las del
    centroide, mismo tipo de limitación ya documentado para el análisis a
    nivel de departamento en Perú (issue #20)."""
    resuelto = divipola.resolver_municipio(municipio, departamento)
    if not resuelto or resuelto.get("latitud") is None or resuelto.get("longitud") is None:
        return None
    lat, lon = resuelto["latitud"], resuelto["longitud"]
    try:
        resp = httpx.get(
            _SERVICE_URL,
            params={
                "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint",
                "sr": "4686",
                "layers": f"all:{layer_id}",
                "tolerance": 1,
                "mapExtent": f"{lon-0.5},{lat-0.5},{lon+0.5},{lat+0.5}",
                "imageDisplay": "400,400,96",
                "returnGeometry": "false",
                "f": "json",
            },
            timeout=_TIMEOUT_SEGUNDOS,
        )
        resp.raise_for_status()
        data = resp.json()
        resultados = data.get("results", [])
        if not resultados:
            return None
        categoria = resultados[0].get("attributes", {}).get("Raster.tipo_cob")
        if not categoria or categoria == "Sin información":
            return None
        return {
            "municipio": resuelto["municipio"],
            "departamento": resuelto["departamento"],
            "periodo": _LAYERS.get(layer_id, "período desconocido"),
            "categoria": categoria,
        }
    except Exception as e:
        log.warning(f"IDEAM/SMByC cambio de bosque: servicio no disponible ({e}) -- se sigue sin este dato")
        return None


def formatear_respuesta(resultado: dict) -> str:
    categoria = resultado["categoria"]
    alerta = " ⚠️" if categoria in _CATEGORIAS_ALERTA else ""
    return (
        f"Según el Sistema de Monitoreo de Bosques y Carbono del IDEAM (SMByC), "
        f"el punto central de {resultado['municipio']} ({resultado['departamento']}) "
        f"se clasificó como **{categoria}**{alerta} en el período {resultado['periodo']} "
        f"de cambio de cobertura de bosque natural. Es la clasificación de UN punto "
        f"(el centroide del municipio), no un promedio de toda el área municipal -- "
        f"para zonas grandes o heterogéneas puede no representar el municipio completo."
    )
