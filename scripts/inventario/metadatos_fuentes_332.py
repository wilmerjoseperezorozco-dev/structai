"""Inventario verificado de fuentes abiertas para #332, fase 1. Solo lectura de METADATOS, sin descargar datos.

- datos.gov.co (Socrata): para cada conjunto, /api/views/<id>.json (licencia exacta, entidad, cobertura, frecuencia,
  última actualización, columnas) y /resource/<id>.json?$select=count(*) (filas). Los conjuntos salen de una lista fija
  (los que ya usa o nombra el proyecto) y de búsquedas en el catálogo por tema del issue.
- ArcGIS REST (SGC y otros): solo el índice de servicios y el conteo de registros (returnCountOnly), sin geometrías.

Salida: metadatos_fuentes_332.json junto a este script. Uso: python -I scripts/inventario/metadatos_fuentes_332.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

SOCRATA = "https://www.datos.gov.co"
CATALOGO = "https://api.us.socrata.com/api/catalog/v1"
UA = {"User-Agent": "inventario-datos-abiertos/1.0"}

# Conjuntos que el proyecto ya usa o que nombra docs/INVENTARIO_DATOS_COLOMBIA.md, con el issue que los usaría.
FIJOS = {
    "gdxc-w37w": "#332 DIVIPOLA",
    "s54a-sgyg": "#320 lluvia 10 min",
    "hp9r-jxuu": "#320 estaciones",
    "57sv-p2fu": "#320 estaciones IDEAM y terceros",
    "nsz2-kzcq": "#320 normales climatológicas",
    "bdmn-sqnh": "hidrología nivel instantáneo",
    "ie7y-asdn": "#106 red vial INVIAS",
    "68qj-5xux": "#106 peajes",
    "8yi9-t44c": "#106 tráfico ANI",
    "7y2j-43cv": "#196-#200 transacciones IGAC",
    "jbjy-vk9h": "#196-#200 SECOP II contratos",
    "cb9c-h8sn": "#196-#200 SECOP II adiciones",
    "7fsy-xzzb": "#325 licencias de construcción (Fusagasugá)",
}
# Búsquedas por tema del issue (se guardan los 8 primeros de cada una).
BUSQUEDAS = {
    "aerocivil": ["aerodromos", "aeropuertos Aerocivil", "pistas aeropuerto"],
    "ideam_viento": ["velocidad del viento", "direccion del viento"],
    "ungrd": ["emergencias UNGRD", "consolidado de emergencias"],
    "dane": ["licencias de construccion DANE", "indice de costos de la construccion", "marco geoestadistico"],
    "pot": ["plan de ordenamiento territorial Barranquilla", "alturas edificaciones", "tratamientos urbanisticos"],
    "sgc": ["Servicio Geologico Colombiano", "sismos"],
    "igac": ["catastro IGAC", "cartografia basica IGAC"],
}
# Servicios ArcGIS públicos (solo índice y conteos).
ARCGIS = {
    "sgc": "https://srvags.sgc.gov.co/arcgis/rest/services",
}


def _get(url: str, **params):
    for intento in range(3):
        try:
            r = requests.get(url, params=params or None, headers=UA, timeout=60)
            if r.status_code == 200:
                return r.json()
            return {"_error": f"HTTP {r.status_code}"}
        except (requests.RequestException, ValueError) as e:
            if intento == 2:
                return {"_error": type(e).__name__}
            time.sleep(3)


def metadatos_socrata(id_: str) -> dict:
    d = _get(f"{SOCRATA}/api/views/{id_}.json")
    if "_error" in d:
        return {"id": id_, "error": d["_error"]}
    lic = d.get("license") or {}
    custom = (d.get("metadata") or {}).get("custom_fields") or {}
    info_datos = custom.get("Información de Datos", {})
    info_ent = custom.get("Información de la Entidad", {})
    filas = None
    if d.get("viewType") == "tabular":
        c = _get(f"{SOCRATA}/resource/{id_}.json", **{"$select": "count(*)"})
        if isinstance(c, list) and c:
            filas = int(c[0].get("count", 0))
    actualizado = d.get("rowsUpdatedAt") or d.get("viewLastModified")
    return {
        "id": id_,
        "nombre": d.get("name"),
        "entidad": info_ent.get("Nombre de la Entidad") or d.get("attribution"),
        "url": f"{SOCRATA}/d/{id_}",
        "licencia_id": d.get("licenseId"),
        "licencia_texto": lic.get("name"),
        "licencia_terminos": lic.get("termsLink"),
        "tipo": d.get("viewType"),
        "cobertura": info_datos.get("Cobertura Geográfica"),
        "frecuencia": info_datos.get("Frecuencia de Actualización"),
        "actualizado": time.strftime("%Y-%m-%d", time.gmtime(actualizado)) if actualizado else None,
        "columnas": len(d.get("columns", [])),
        "filas": filas,
        # Estimación gruesa del CSV: ~15 bytes por celda. Orden de magnitud, no tamaño exacto.
        "mb_csv_aprox": round(filas * len(d.get("columns", [])) * 15 / 1e6, 1) if filas else None,
    }


def buscar(q: str, n: int = 8) -> list[str]:
    r = _get(CATALOGO, domains="www.datos.gov.co", search_context="www.datos.gov.co", only="datasets", q=q, limit=n)
    return [x["resource"]["id"] for x in r.get("results", [])] if isinstance(r, dict) else []


def indice_arcgis(base: str) -> dict:
    raiz = _get(base, f="json")
    if "_error" in raiz:
        return {"error": raiz["_error"]}
    return {"carpetas": raiz.get("folders", []), "servicios_raiz": [s.get("name") for s in raiz.get("services", [])]}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    salida: dict = {"fecha": time.strftime("%Y-%m-%d"), "socrata": {}, "busquedas": {}, "arcgis": {}}
    for id_, uso in FIJOS.items():
        m = metadatos_socrata(id_)
        m["uso"] = uso
        salida["socrata"][id_] = m
        print(id_, m.get("licencia_id"), m.get("filas"), m.get("nombre"))
        time.sleep(0.4)
    for tema, qs in BUSQUEDAS.items():
        ids: list[str] = []
        for q in qs:
            ids += [i for i in buscar(q) if i not in ids]
            time.sleep(0.4)
        salida["busquedas"][tema] = []
        for id_ in ids:
            if id_ not in salida["socrata"]:
                salida["socrata"][id_] = metadatos_socrata(id_)
                time.sleep(0.4)
            salida["busquedas"][tema].append(id_)
        print(tema, len(ids))
    for nombre, base in ARCGIS.items():
        salida["arcgis"][nombre] = indice_arcgis(base)
    Path(__file__).with_name("metadatos_fuentes_332.json").write_text(
        json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
