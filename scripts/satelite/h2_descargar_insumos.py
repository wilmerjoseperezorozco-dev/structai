"""Descarga los insumos de H2 (#273) a _cache/ (ignorado por git). Solo biblioteca estándar.

- Inventarios de puntos de agua subterránea del SGC (CC BY 4.0), 6 capas: _cache/h2_puntos_agua_<capa>.json
- Teselas del DEM Copernicus GLO-90 (AWS Open Data) que cubren esos puntos: _cache/dem90/<tesela>.tif
Uso: python -I h2_descargar_insumos.py [--solo-puntos]
"""
from __future__ import annotations

import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
BASE = "https://services1.arcgis.com/Og2nrTKe5bptW02d/arcgis/rest/services"
CAPAS = {
    "guaviare": "Puntos_agua_San_Jose",
    "meta": "Hidro_Meta_Puntos_Agua",
    "casanare": "Inventario_puntos_de_agua",
    "quindio": "Inventario_de_Puntos_de_agua_Quindio",
    "inirida": "Puntos_de_agua_Inirida",
    "santurban": "Inventario_puntos_de_agua_del_Paramo_de_Santurbán",
}
DEM = "https://copernicus-dem-90m.s3.amazonaws.com"
UA = {"User-Agent": "structai-research/0.1"}


def _get(url: str, intentos: int = 3) -> bytes:
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError:
            raise
        except Exception as e:  # noqa: BLE001
            if i == intentos - 1:
                raise
            print("  reintento", type(e).__name__)
            time.sleep(5 * (i + 1))
    raise RuntimeError


def puntos() -> list[tuple[float, float]]:
    coords = []
    for nombre, servicio in CAPAS.items():
        f = CACHE / f"h2_puntos_agua_{nombre}.json"
        if not f.exists():
            feats, off = [], 0
            while True:
                q = urllib.parse.urlencode({"where": "1=1", "outFields": "*", "outSR": 4326, "returnGeometry": "true",
                                            "resultOffset": off, "resultRecordCount": 1000, "f": "json"})
                d = json.loads(_get(f"{BASE}/{urllib.parse.quote(servicio)}/FeatureServer/0/query?{q}"))
                fs = d.get("features", [])
                feats += fs
                if not d.get("exceededTransferLimit") or not fs:
                    break
                off += len(fs)
            f.write_text(json.dumps({"servicio": servicio, "licencia": "CC BY 4.0 (Servicio Geológico Colombiano)",
                                     "features": feats}, ensure_ascii=False), encoding="utf-8")
            print(f"  {nombre}: {len(feats)} puntos, {f.stat().st_size / 1e6:.2f} MB")
        for x in json.loads(f.read_text(encoding="utf-8"))["features"]:
            g = x.get("geometry") or {}
            if "x" in g:
                coords.append((g["x"], g["y"]))
    return coords


def nombre_tesela(lat: int, lon: int) -> str:
    ns = f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}_00"
    ew = f"{'E' if lon >= 0 else 'W'}{abs(lon):03d}_00"
    return f"Copernicus_DSM_COG_30_{ns}_{ew}_DEM"


def dem(coords) -> None:
    d = CACHE / "dem90"
    d.mkdir(exist_ok=True)
    teselas = set()
    for lon, lat in coords:     # tesela del punto y vecinas (el cauce más cercano puede caer al lado)
        for dla in (-1, 0, 1):
            for dlo in (-1, 0, 1):
                la, lo = math.floor(lat + dla * 0.05), math.floor(lon + dlo * 0.05)
                teselas.add((la, lo))
    total = 0
    for la, lo in sorted(teselas):
        n = nombre_tesela(la, lo)
        f = d / f"{n}.tif"
        if not f.exists():
            try:
                b = _get(f"{DEM}/{n}/{n}.tif")
            except urllib.error.HTTPError as e:
                print(f"  {n}: HTTP {e.code} (sin tesela: océano o fuera de cobertura)")
                continue
            f.write_bytes(b)
            print(f"  {n}: {len(b) / 1e6:.1f} MB")
        total += f.stat().st_size
    print(f"DEM: {len(teselas)} teselas pedidas, {total / 1e6:.0f} MB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    CACHE.mkdir(exist_ok=True)
    c = puntos()
    print("puntos con geometría:", len(c))
    if "--solo-puntos" not in sys.argv:
        dem(c)
