"""Inventario de conjuntos de datos abiertos de Colombia (datos.gov.co) por tema de ingenieria civil.
Solo lectura del catalogo publico (Discovery API de Socrata). Salida: catalogo_datos_gov.json
"""
import json, sys, time
from pathlib import Path
import requests

TEMAS = {
    "lluvia_clima": ["precipitacion", "temperatura del aire", "humedad del suelo", "evapotranspiracion"],
    "hidrologia": ["caudal", "nivel del rio", "inundacion", "cuenca hidrografica"],
    "sismos_suelos": ["sismo", "acelerografo", "movimientos en masa", "amenaza sismica", "geotecnia"],
    "vivienda_poblacion": ["vivienda", "censo poblacion", "licencias de construccion", "sisben", "deficit habitacional"],
    "infraestructura_vial": ["vias", "puentes", "accidentalidad vial", "trafico vehicular", "peajes"],
    "contratacion_obras": ["contratos obra publica", "SECOP", "interventoria"],
    "energia_agua": ["acueducto", "alcantarillado", "calidad del agua", "consumo energia"],
    "minerales_materiales": ["canteras", "titulos mineros", "produccion de cemento", "materiales de construccion"],
    "precios": ["precios insumos construccion", "indice costos construccion", "salario minimo"],
    "riesgo_desastres": ["emergencias", "desastres", "incendios", "deslizamientos"],
}
URL = "https://api.us.socrata.com/api/catalog/v1"
out = {}
for tema, claves in TEMAS.items():
    vistos = {}
    for q in claves:
        try:
            r = requests.get(URL, timeout=60, params={"domains": "www.datos.gov.co", "search_context": "www.datos.gov.co",
                                                    "only": "datasets", "q": q, "limit": 12})
            r.raise_for_status()
        except Exception as e:
            print("ERR", q, e, file=sys.stderr); continue
        for x in r.json().get("results", []):
            m, c = x["resource"], x.get("classification", {})
            vistos[m["id"]] = {"id": m["id"], "nombre": m["name"], "entidad": c.get("domain_metadata", [{}])[0].get("value") if False else (m.get("attribution") or ""),
                               "filas": None, "columnas": m.get("columns_name", [])[:12], "actualizado": m.get("data_updated_at", "")[:10],
                               "descargas": m.get("download_count"), "q": q}
        time.sleep(0.5)
    out[tema] = sorted(vistos.values(), key=lambda d: -(d["descargas"] or 0))
    print(tema, len(out[tema]))
Path(__file__).with_name("catalogo_datos_gov.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
