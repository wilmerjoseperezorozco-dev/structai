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
# COG (no los GeoTIFF por franjas): mismas cifras (verificado: diferencia maxima 0,0 mm en 77 municipios, 2014-12) y
# lectura por bloques, sin los 429 del servidor.
BASE = "/vsicurl/https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/cogs/chirps-v3.0.{a}.{m:02d}.cog"
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


def leer_mes(a: int, m: int):
    """Lee la ventana de Colombia de un mes, con reintentos y espera creciente ante 429/errores de red."""
    for intento in range(7):
        try:
            with rasterio.open(BASE.format(a=a, m=m)) as ds:
                w = from_bounds(*BBOX, transform=ds.transform).round_offsets().round_lengths()
                z = ds.read(1, window=w).astype("float64")
                tr = ds.window_transform(w)
            z[z <= NODATA + 1] = np.nan
            return z, tr
        except rasterio.errors.RasterioIOError as e:
            espera = min(30 * 2 ** intento, 600)
            print(f"  {a}-{m:02d}: {str(e)[:50]}; espero {espera}s (intento {intento + 1})", flush=True)
            time.sleep(espera)
    raise RuntimeError(f"no se pudo leer {a}-{m:02d}")


def main() -> None:
    pols = {}
    for d in DEPTOS:
        for ft in poligonos(d):
            g = shape(ft["geometry"]).buffer(0)
            if not g.is_empty:
                pols[ft["properties"]["CODIGO"]] = (g, ft["properties"]["NOMBRE_ENT"])
    print(f"Municipios con poligono: {len(pols)}", flush=True)
    a0, a1 = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (2019, 2024)
    meses = [(a, m) for a in range(a0, a1 + 1) for m in range(1, 13)]
    serie = {c: [] for c in pols}
    pix = {}
    t0 = time.time()
    # NOTA: con cache por mes, el primer mes siempre se lee para construir las mascaras de pixeles.
    # El archivo mensual esta organizado en franjas de una fila (~29 KB) y GDAL pide por defecto trozos de 16 KB:
    # cada mes generaba cientos de solicitudes HTTP (causa probable de los 429). Con trozos de 16 MB bastan 1-2 por mes.
    with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=5,
                      GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.cog",
                      CPL_VSIL_CURL_CHUNK_SIZE="16777216", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", VSI_CACHE="FALSE"):
        for k, (a, m) in enumerate(meses):
            cf = CACHE / "chirps_mes" / f"{a}-{m:02d}.json"
            if cf.exists() and pix:                       # mes ya extraido (reanudable)
                vals = json.loads(cf.read_text(encoding="utf-8"))
                for c in pols:
                    serie[c].append(vals.get(c))
                continue
            z, tr = leer_mes(a, m)
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
            if cf.exists():                               # primer mes: solo se leyo para armar las mascaras
                vals = json.loads(cf.read_text(encoding="utf-8"))
                for c in pols:
                    serie[c].append(vals.get(c))
                continue
            vals = {}
            for c in pols:
                v = z[pix[c]]
                vals[c] = float(np.nanmean(v)) if np.isfinite(v).any() else None
                serie[c].append(vals[c])
            cf.parent.mkdir(exist_ok=True)
            cf.write_text(json.dumps(vals), encoding="utf-8")
            time.sleep(1.0)                               # cortesia con el servidor (evita el 429)
            if k % 12 == 11:
                print(f"  {a}: listo ({time.time() - t0:.0f}s)", flush=True)
    faltan = {c for c in pols if any(v is None for v in serie[c])}
    out = {"fuente": "CHIRPS v3.0 mensual (mm/mes), 0.05 grados", "meses": [f"{a}-{m:02d}" for a, m in meses],
           "municipios": {c: {"nombre": pols[c][1], "depto": c[:2], "precip_mm": serie[c], "n_pixeles": int(pix[c].sum())}
                          for c in pols if c not in faltan}}
    nombre = "chirps_mensual_colombia.json" if (a0, a1) == (2019, 2024) else f"chirps_mensual_colombia_{a0}_{a1}.json"
    (AQUI / nombre).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(out['municipios'])} municipios con serie completa; {len(faltan)} descartados por pixeles sin dato", flush=True)


if __name__ == "__main__":
    main()
