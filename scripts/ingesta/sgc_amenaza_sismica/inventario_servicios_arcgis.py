"""Inventario de servicios publicos del ArcGIS REST del SGC (solo lectura).

Lista carpetas, servicios y, para cada MapServer/FeatureServer, sus capas con
el conteo de registros. No descarga geometrias. Salida: JSON + resumen.
Uso: python inventario_servicios_arcgis.py [salida.json]
"""
import json
import sys
import time

import requests

BASE = "https://srvags.sgc.gov.co/arcgis/rest/services"
PAUSA_S = 0.3
TIMEOUT_S = 30
# Carpetas que el propio servidor marca como privadas o de sistema: no se tocan.
OMITIR = {"SIMMA_PRIVADA", "System", "Utilities", "Reactor_SGC"}


def get_json(url: str, params: dict | None = None) -> dict | None:
    try:
        r = requests.get(url, params={**(params or {}), "f": "json"}, timeout=TIMEOUT_S)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as exc:
        return {"_error": str(exc)[:120]}
    time.sleep(PAUSA_S)
    return data


def contar(url_capa: str) -> int | str | None:
    d = get_json(f"{url_capa}/query", {"where": "1=1", "returnCountOnly": "true"})
    if not d or "_error" in d or "error" in d:
        return None
    return d.get("count")


def main(salida: str) -> None:
    raiz = get_json(BASE)
    carpetas = [c for c in raiz.get("folders", []) if c not in OMITIR]
    resultado = []
    for carpeta in carpetas:
        d = get_json(f"{BASE}/{carpeta}")
        for s in d.get("services", []):
            if s["type"] not in ("MapServer", "FeatureServer"):
                continue
            url = f"{BASE}/{s['name']}/{s['type']}"
            info = get_json(url)
            capas = []
            for c in info.get("layers", []) or []:
                capas.append({"id": c["id"], "nombre": c["name"], "n": contar(f"{url}/{c['id']}")})
            resultado.append({"servicio": s["name"], "tipo": s["type"], "capas": capas,
                              "error": info.get("_error")})
            print(s["name"], s["type"], len(capas), flush=True)
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "sgc_inventario_servicios.json")
