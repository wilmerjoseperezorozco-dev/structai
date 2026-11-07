"""Precipitacion DIARIA CHIRPS v3.0 (sat, final) por municipio de Colombia continental, 2019-2024 (bloque de umbrales).
Misma mascara de pixeles que la extraccion mensual. Reanudable: cache por dia en _cache/chirps_dia/AAAA-MM-DD.json.
Salida: chirps_diario_colombia.json {"dias": [...], "municipios": {cod: [mm...]}} (valores redondeados a 0,1 mm).
Uso: python extraer_chirps_diario_colombia.py [a0 a1]
"""
from __future__ import annotations

import datetime as dt
import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from rasterio.windows import from_bounds

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extraer_chirps_colombia as mc  # noqa: E402  (poligonos, BBOX, NODATA, DEPTOS)
from shapely.geometry import shape  # noqa: E402

AQUI = mc.AQUI
CACHE = mc.CACHE / "chirps_dia"
BASE = "/vsicurl/https://data.chc.ucsb.edu/products/CHIRPS/v3.0/daily/final/sat/{a}/chirps-v3.0.sat.{a}.{m:02d}.{d:02d}.tif"


def leer_dia(f: dt.date):
    for intento in range(8):
        try:
            with rasterio.open(BASE.format(a=f.year, m=f.month, d=f.day)) as ds:
                w = from_bounds(*mc.BBOX, transform=ds.transform).round_offsets().round_lengths()
                z = ds.read(1, window=w).astype("float64")
                tr = ds.window_transform(w)
            z[z <= mc.NODATA + 1] = np.nan
            return z, tr
        except rasterio.errors.RasterioIOError as e:
            espera = min(30 * 2 ** intento, 900)
            print(f"  {f}: {str(e)[:50]}; espero {espera}s (intento {intento + 1})", flush=True)
            time.sleep(espera)
    raise RuntimeError(f"no se pudo leer {f}")


def main() -> None:
    a0, a1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (2019, 2024)
    pols = {}
    for d in mc.DEPTOS:
        for ft in mc.poligonos(d):
            g = shape(ft["geometry"]).buffer(0)
            if not g.is_empty:
                pols[ft["properties"]["CODIGO"]] = g
    dias = [dt.date(a0, 1, 1) + dt.timedelta(days=k) for k in range((dt.date(a1, 12, 31) - dt.date(a0, 1, 1)).days + 1)]
    CACHE.mkdir(parents=True, exist_ok=True)
    pix, serie, t0 = {}, {c: [] for c in pols}, time.time()
    with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=5, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", CPL_VSIL_CURL_CHUNK_SIZE="16777216",
                      GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", VSI_CACHE="FALSE"):
        for k, f in enumerate(dias):
            cf = CACHE / f"{f.isoformat()}.json"
            if cf.exists() and pix:
                vals = json.loads(cf.read_text(encoding="utf-8"))
            else:
                z, tr = leer_dia(f)
                if not pix:
                    for c, g in pols.items():
                        mk = features.geometry_mask([g.__geo_interface__], out_shape=z.shape, transform=tr, invert=True, all_touched=True)
                        if not mk.any():
                            r, cc = ~tr * (g.centroid.x, g.centroid.y)
                            mk = np.zeros(z.shape, bool)
                            if 0 <= int(r) < z.shape[0] and 0 <= int(cc) < z.shape[1]:
                                mk[int(r), int(cc)] = True
                        pix[c] = mk
                if cf.exists():
                    vals = json.loads(cf.read_text(encoding="utf-8"))
                else:
                    vals = {c: (round(float(np.nanmean(z[pix[c]])), 1) if np.isfinite(z[pix[c]]).any() else None) for c in pols}
                    cf.write_text(json.dumps(vals), encoding="utf-8")
                    time.sleep(0.5)
            for c in pols:
                serie[c].append(vals.get(c))
            if k % 90 == 89:
                print(f"  {f}: {k + 1}/{len(dias)} ({time.time() - t0:.0f}s)", flush=True)
    ok = {c: s for c, s in serie.items() if all(v is not None for v in s)}
    out = {"fuente": "CHIRPS v3.0 sat final diario (mm/dia)", "dias": [d.isoformat() for d in dias], "municipios": ok}
    (AQUI / "chirps_diario_colombia.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"{len(ok)} municipios con serie diaria completa de {len(pols)}", flush=True)


if __name__ == "__main__":
    main()
