"""Descarga los insumos de H4 (#273) a _cache/ (ignorado por git). Solo biblioteca estándar.

- SIMMA (SGC), inventario de movimientos en masa, puntos: _cache/simma_puntos.json  [[lon, lat, tipo], ...]
- Polígonos municipales (ANH, ANH_ENTIDADES_TERRIT/MapServer/1), 21 departamentos del panel, simplificados
  a 0,0003°: _cache/poligonos_XX.geojson
Uso: python -I h4_descargar_insumos.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
SIMMA = ("https://services1.arcgis.com/Og2nrTKe5bptW02d/arcgis/rest/services/"
         "Inventario_de_movimientos_en_masa/FeatureServer/0/query")
ANH = "https://geovisor.anh.gov.co/server/rest/services/GEOVISOR_v32/ANH_ENTIDADES_TERRIT/MapServer/1/query"
DEPTOS_PANEL = ["05", "08", "13", "15", "17", "19", "20", "23", "25", "41", "44", "47", "50", "52", "54", "63", "66",
                "68", "70", "73", "76"]
UA = {"User-Agent": "structai-research/0.1"}


def _get(url: str, params: dict, intentos: int = 3) -> bytes:
    for i in range(intentos):
        try:
            req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}", headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if i == intentos - 1:
                raise
            print("  reintento", i + 1, type(e).__name__)
            time.sleep(5 * (i + 1))
    raise RuntimeError


def simma() -> None:
    f = CACHE / "simma_puntos.json"
    if f.exists():
        print(f, "ya existe")
        return
    pts, off = [], 0
    while True:
        d = json.loads(_get(SIMMA, {"where": "1=1", "outFields": "OBJECTID,TIPO", "outSR": 4326,
                                    "returnGeometry": "true", "resultOffset": off, "resultRecordCount": 2000,
                                    "orderByFields": "OBJECTID", "f": "json"}))
        fs = d.get("features", [])
        for x in fs:
            g = x.get("geometry") or {}
            if "x" in g and "y" in g:
                pts.append([round(float(g["x"]), 5), round(float(g["y"]), 5), str(x["attributes"].get("TIPO") or "")])
        print(f"  SIMMA offset {off}: {len(fs)}")
        if len(fs) < 2000 and not d.get("exceededTransferLimit"):
            break
        off += len(fs)
    f.write_text(json.dumps(pts), encoding="utf-8")
    print(f, len(pts), f"{f.stat().st_size / 1e6:.2f} MB")


def poligonos() -> None:
    total = 0
    for dep in DEPTOS_PANEL:
        f = CACHE / f"poligonos_{dep}.geojson"
        if not f.exists():
            b = _get(ANH, {"where": f"COD_DEPART='{dep}'", "outFields": "CODIGO,NOMBRE_ENT,DEPARTAMEN", "outSR": 4326,
                           "maxAllowableOffset": 0.0003, "f": "geojson"})
            n = len(json.loads(b)["features"])
            f.write_bytes(b)
            print(f"  {dep}: {n} municipios, {len(b) / 1e6:.1f} MB")
        total += f.stat().st_size
    print(f"polígonos: {total / 1e6:.1f} MB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    CACHE.mkdir(exist_ok=True)
    simma()
    poligonos()
