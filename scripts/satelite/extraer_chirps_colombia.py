"""Precipitacion mensual CHIRPS v3.0 por municipio de TODA Colombia continental, 2019-2024
(issue #95/#98). Extension de extraer_chirps_caribe.py: mismo metodo, poligonos municipales IGAC
(servicio ANH, simplificados) de todos los departamentos.

San Andres y Providencia (88) quedan fuera: estan lejos del continente y requieren otra ventana.
Solo extrae; no asocia nada. Salida: scripts/satelite/chirps_mensual_colombia.json
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from rasterio.windows import from_bounds
from shapely.geometry import shape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
ANH = "https://geovisor.anh.gov.co/server/rest/services/GEOVISOR_v32/ANH_ENTIDADES_TERRIT/MapServer/1/query"
DEPTOS = ["05", "08", "11", "13", "15", "17", "18", "19", "20", "23", "25", "27", "41", "44", "47", "50", "52", "54",
          "63", "66", "68", "70", "73", "76", "81", "85", "86", "91", "94", "95", "97", "99"]
BASE = "/vsicurl/https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/tifs/chirps-v3.0.{a}.{m:02d}.tif"
BBOX = (-79.2, -4.4, -66.7, 13.5)
NODATA = -9999.0


def poligonos(d: str) -> list[dict]:
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"poligonos_nac_{d}.geojson"
    if not f.exists():
        q = urllib.parse.urlencode({"where": f"COD_DEPART='{d}'", "outFields": "CODIGO,NOMBRE_ENT", "outSR": 4326,
                                    "maxAllowableOffset": 0.0005, "f": "geojson"})
        with urllib.request.urlopen(f"{ANH}?{q}", timeout=180) as r:
            f.write_bytes(r.read())
    return json.loads(f.read_text(encoding="utf-8"))["features"]


def main() -> None:
    pols = {}
    for d in DEPTOS:
        for ft in poligonos(d):
            g = shape(ft["geometry"]).buffer(0)
            if not g.is_empty:
                pols[ft["properties"]["CODIGO"]] = (g, ft["properties"]["NOMBRE_ENT"])
    print(f"Municipios con poligono: {len(pols)}", flush=True)
    meses = [(a, m) for a in range(2019, 2025) for m in range(1, 13)]
    serie = {c: [] for c in pols}
    pix = {}
    t0 = time.time()
    with rasterio.Env(GDAL_HTTP_TIMEOUT=60, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=2,
                      GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
        for k, (a, m) in enumerate(meses):
            with rasterio.open(BASE.format(a=a, m=m)) as ds:
                w = from_bounds(*BBOX, transform=ds.transform).round_offsets().round_lengths()
                z = ds.read(1, window=w).astype("float64")
                tr = ds.window_transform(w)
            z[z <= NODATA + 1] = np.nan
            if not pix:
                for c, (g, _) in pols.items():
                    mk = features.geometry_mask([g.__geo_interface__], out_shape=z.shape, transform=tr, invert=True, all_touched=True)
                    if not mk.any():
                        x, y = g.centroid.x, g.centroid.y
                        r, cc = ~tr * (x, y)
                        mk = np.zeros(z.shape, bool)
                        if 0 <= int(r) < z.shape[0] and 0 <= int(cc) < z.shape[1]:
                            mk[int(r), int(cc)] = True
                    pix[c] = mk
            for c in pols:
                v = z[pix[c]]
                serie[c].append(float(np.nanmean(v)) if np.isfinite(v).any() else None)
            if k % 12 == 11:
                print(f"  {a}: listo ({time.time() - t0:.0f}s)", flush=True)
    faltan = {c for c in pols if any(v is None for v in serie[c])}
    out = {"fuente": "CHIRPS v3.0 mensual (mm/mes), 0.05 grados", "meses": [f"{a}-{m:02d}" for a, m in meses],
           "municipios": {c: {"nombre": pols[c][1], "depto": c[:2], "precip_mm": serie[c], "n_pixeles": int(pix[c].sum())}
                          for c in pols if c not in faltan}}
    (AQUI / "chirps_mensual_colombia.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(out['municipios'])} municipios con serie completa; {len(faltan)} descartados por pixeles sin dato", flush=True)


if __name__ == "__main__":
    main()
