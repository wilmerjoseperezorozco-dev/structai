"""Baja los poligonos de amenaza por movimientos en masa de SIMMA (SGC) a 1:25.000 y 1:100.000, simplificados.
Salida: _cache/simma_amenaza_<escala>.json (lista de {catame, mapa, esri_rings}). Solo lectura, pausa de 0,4 s."""
import json
import sys
import time
from pathlib import Path

import requests

BASE = "https://srvags.sgc.gov.co/arcgis/rest/services/SIMMA/ZonificacionAmenazaCache/MapServer"
CAPAS = {"25K": 9, "100K": 11}
OFFSET = {"25K": 0.0015, "100K": 0.006}   # ~150 m y ~600 m: suficiente para estimar areas municipales
LOTE = {"25K": 200, "100K": 25}
SALIDA = Path(__file__).resolve().parent / "_cache"


def main(escala: str) -> None:
    q = f"{BASE}/{CAPAS[escala]}/query"
    ids = sorted(requests.get(q, params={"where": "1=1", "returnIdsOnly": "true", "f": "json"}, timeout=90).json()["objectIds"])
    out, total = [], 0
    for i in range(0, len(ids), LOTE[escala]):
        lote = ids[i:i + LOTE[escala]]
        r = requests.post(q, data={"objectIds": ",".join(map(str, lote)), "outFields": "CATAME", "returnGeometry": "true",
                                    "maxAllowableOffset": OFFSET[escala], "geometryPrecision": 4, "outSR": 4326, "f": "json"}, timeout=240)
        total += len(r.content)
        for f in r.json().get("features", []):
            out.append({"id": f["attributes"].get("OBJECTID"), "catame": f["attributes"].get("CATAME"), "rings": f["geometry"]["rings"]})
        print(f"{escala}: {len(out)}/{len(ids)} poligonos, {total/1e6:.1f} MB", flush=True)
        time.sleep(0.4)
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / f"simma_amenaza_{escala}.json").write_text(json.dumps(out), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
