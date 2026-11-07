"""Piloto satelital, paso 3 (issue #95, Frente C): relieve Copernicus DEM GLO-30 por
POLIGONO municipal (IGAC, servicio ANH) para varios departamentos del Caribe.

Sustituye el circulo de 5 km de extraer_dem_piloto.py por estadistica zonal real.
Solo EXTRAE; no entrena nada.

Declarado:
- Poligonos IGAC via ANH, simplificados (maxAllowableOffset ~30 m) para reducir
  tamano. El servicio advierte que no son apropiados para areas/distancias
  exactas: sirven para estadistica zonal a escala municipal.
- DEM = modelo de SUPERFICIE (incluye edificios y vegetacion), 30 m.
- Pendiente por diferencias finitas con tamano de pixel en metros.
- Municipios muy grandes se leen decimados (tope ~MAX_PIXELES) para acotar costo.

Uso: python scripts/satelite/extraer_dem_poligonos.py [codigos_depto separados por coma]
Salida: scripts/satelite/dem_poligonos_caribe.json
"""
from __future__ import annotations

import io
import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from rasterio.merge import merge
from shapely.geometry import shape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
ANH = "https://geovisor.anh.gov.co/server/rest/services/GEOVISOR_v32/ANH_ENTIDADES_TERRIT/MapServer/1/query"
STAC = "https://earth-search.aws.element84.com/v1/search"
DEPTOS_CARIBE = ["08", "47", "13", "23", "70", "20", "44"]
M_POR_GRADO = 111_320.0
MAX_PIXELES = 4_000_000
GRADO_30M = 1 / 3600.0
BAJO_NIVEL_M = 10.0
UA = {"User-Agent": "structai-piloto/0.1", "Content-Type": "application/json"}


def poligonos(depto: str) -> list[dict]:
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"poligonos_{depto}.geojson"
    if not f.exists():
        q = urllib.parse.urlencode({"where": f"COD_DEPART='{depto}'", "outFields": "CODIGO,NOMBRE_ENT,DEPARTAMEN",
                                    "outSR": 4326, "maxAllowableOffset": 0.0003, "f": "geojson"})
        with urllib.request.urlopen(f"{ANH}?{q}", timeout=120) as r:
            f.write_bytes(r.read())
    return json.loads(f.read_text(encoding="utf-8"))["features"]


def hrefs_dem(bbox: list[float]) -> list[str]:
    req = urllib.request.Request(STAC, data=json.dumps({"collections": ["cop-dem-glo-30"], "bbox": bbox, "limit": 20}).encode(), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        hs = [f["assets"]["data"]["href"] for f in json.load(r)["features"]]
    return [("https://" + h[5:].split("/", 1)[0] + ".s3.amazonaws.com/" + h[5:].split("/", 1)[1]) if h.startswith("s3://") else h for h in hs]


def estadistica(geom_geojson: dict) -> dict | None:
    geom = shape(geom_geojson)
    minx, miny, maxx, maxy = geom.bounds
    bbox = [minx, miny, maxx, maxy]
    hs = hrefs_dem(bbox)
    if not hs:
        return None
    lat = (miny + maxy) / 2
    npix = ((maxx - minx) / GRADO_30M) * ((maxy - miny) / GRADO_30M)
    paso = GRADO_30M * max(1.0, math.sqrt(npix / MAX_PIXELES))
    with rasterio.Env(GDAL_HTTP_TIMEOUT=45, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=2, GDAL_HTTP_CONNECTTIMEOUT=20):
        datasets = [rasterio.open(h) for h in hs]
        try:
            z, tr = merge(datasets, bounds=tuple(bbox), res=(paso, paso), nodata=np.nan, resampling=rasterio.enums.Resampling.average)
        finally:
            for d in datasets:
                d.close()
    z = z[0].astype("float64")
    mask = features.geometry_mask([geom_geojson], out_shape=z.shape, transform=tr, invert=True)
    py = abs(tr.e) * M_POR_GRADO
    px = tr.a * M_POR_GRADO * math.cos(math.radians(lat))
    gy, gx = np.gradient(z, py, px)
    pend = np.hypot(gx, gy) * 100.0
    ok = mask & ~np.isnan(z) & ~np.isnan(pend)
    if ok.sum() < 30:
        return None
    v, p = z[ok], pend[ok]
    return {
        "n_pixeles": int(ok.sum()), "resolucion_m": round(paso * M_POR_GRADO, 1),
        "elev_media_m": float(v.mean()), "elev_p10_m": float(np.percentile(v, 10)), "elev_p90_m": float(np.percentile(v, 90)),
        "rango_elev_m": float(v.max() - v.min()),
        "pend_media_pct": float(p.mean()), "pend_mediana_pct": float(np.median(p)), "pend_p90_pct": float(np.percentile(p, 90)),
        "frac_bajo_10m": float((v < BAJO_NIVEL_M).mean()), "frac_pend_gt_15": float((p > 15).mean()),
    }


def main() -> None:
    deptos = sys.argv[1].split(",") if len(sys.argv) > 1 else DEPTOS_CARIBE
    out, fallas = [], 0
    for d in deptos:
        fs = poligonos(d)
        print(f"Departamento {d}: {len(fs)} municipios")
        for f in fs:
            pr = f["properties"]
            cf = CACHE / "dem_mun" / f"{pr['CODIGO']}.json"
            if cf.exists():
                est = json.loads(cf.read_text(encoding="utf-8"))
            else:
                est = None
                for intento in (1, 2):
                    try:
                        est = estadistica(f["geometry"])
                        break
                    except Exception as e:
                        print(f"  FALLA ({intento}) {pr['NOMBRE_ENT']}: {type(e).__name__}: {str(e)[:80]}")
                if est is None:
                    fallas += 1
                else:
                    cf.parent.mkdir(exist_ok=True)
                    cf.write_text(json.dumps(est), encoding="utf-8")
            out.append({"codigo": pr["CODIGO"], "municipio": pr["NOMBRE_ENT"], "depto": d, **(est or {"error": True})})
            if est:
                print(f"  {pr['NOMBRE_ENT']:<24} elev {est['elev_media_m']:6.0f} m  pend {est['pend_media_pct']:5.1f}%  <10m {est['frac_bajo_10m']*100:5.1f}%")
    ok = sum(1 for o in out if "error" not in o)
    print(f"\n{ok}/{len(out)} municipios con estadistica valida ({fallas} fallas)")
    (AQUI / "dem_poligonos_caribe.json").write_text(json.dumps({
        "fuente": "Copernicus DEM GLO-30 + poligonos IGAC (ANH, simplificados)", "max_pixeles": MAX_PIXELES, "municipios": out},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print("Guardado dem_poligonos_caribe.json")


if __name__ == "__main__":
    main()
