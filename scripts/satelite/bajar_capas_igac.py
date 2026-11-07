"""Descarga paginada y reanudable de capas del IGAC (ArcGIS REST) a GeoJSON en _cache/igac/. Uso: python bajar_capas_igac.py <nombre> <url_capa> [pagina=500]"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

DEST = Path(__file__).resolve().parent / "_cache" / "igac"


def pedir(url: str, intentos: int = 8) -> dict:
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "structai-research/0.1"}), timeout=120) as r:
                d = json.load(r)
            if "error" in d:
                raise RuntimeError(str(d["error"])[:100])
            return d
        except Exception as e:  # servidor lento: espera creciente
            print(f"   reintento {i + 1}: {str(e)[:60]}", flush=True)
            time.sleep(min(10 * 2 ** i, 120))
    raise RuntimeError(f"sin respuesta: {url[:90]}")


def main() -> None:
    nombre, capa = sys.argv[1], sys.argv[2]
    pag = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    DEST.mkdir(parents=True, exist_ok=True)
    ids = pedir(f"{capa}/query?where=1%3D1&returnIdsOnly=true&f=json")
    oid, lista = ids["objectIdFieldName"], sorted(ids["objectIds"])
    print(f"{nombre}: {len(lista)} objetos", flush=True)
    for k in range(0, len(lista), pag):
        f = DEST / f"{nombre}_{k // pag:05d}.geojson"
        if f.exists():
            continue
        q = urllib.parse.urlencode({"objectIds": ",".join(map(str, lista[k:k + pag])), "outFields": "*", "outSR": 4326,
                                    "maxAllowableOffset": 0.0003, "f": "geojson"})
        f.write_bytes(json.dumps(pedir(f"{capa}/query?{q}")).encode())
        print(f"  {nombre}: {min(k + pag, len(lista))}/{len(lista)}", flush=True)
    print(f"{nombre}: listo", flush=True)


if __name__ == "__main__":
    main()
