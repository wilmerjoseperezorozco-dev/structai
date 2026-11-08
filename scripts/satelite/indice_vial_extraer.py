"""Extrae, por tramo de via terciaria (OSM) y por departamento, las variables geomorfometricas del DEM.
Protocolo: PROTOCOLO_INDICE_VIAL_GEOMORFOMETRICO.md. Uso: python indice_vial_extraer.py 08,13,...
Salida: _cache/ivg_<depto>.pkl (un DataFrame por tramo). Reanudable: si el pkl existe, se salta."""
from __future__ import annotations

import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import distance_transform_edt
from shapely.geometry import LineString, Point, shape
from shapely.strtree import STRtree

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import calcular_hand_caribe as ch  # noqa: E402
from pysheds.grid import Grid  # noqa: E402

CACHE = AQUI / "_cache"
OVERPASS = "https://overpass-api.de/api/interpreter"
UA = "structai-research/1.0 (academic research; github wilmerjoseperezorozco-dev)"
PASO_M = 90.0
UMBRAL_RED_KM2 = 5.0
TAN_MIN = 0.001
PEND_UMBRALES = (10, 15, 25)
DIST_UMBRALES = (50, 100, 200)
TIPOS = "tertiary|unclassified|track"


def poligonos(depto: str) -> dict:
    f = CACHE / f"poligonos_{depto}.geojson"
    if not f.exists():
        f = CACHE / f"poligonos_nac_{depto}.geojson"
    out = {}
    for ft in json.loads(f.read_text(encoding="utf-8"))["features"]:
        out[ft["properties"]["CODIGO"]] = {"geom": shape(ft["geometry"]), "nombre": ft["properties"]["NOMBRE_ENT"]}
    return {c: p for c, p in out.items() if c.startswith(depto)}


def osm_vias(depto: str, bb) -> dict:
    ruta = CACHE / f"osm_terciarias_{depto}.json"
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    q = f'[out:json][timeout:300];way["highway"~"^({TIPOS})$"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});out geom tags;'
    for intento in range(4):
        try:
            req = urllib.request.Request(OVERPASS, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=700) as r:
                datos = json.load(r)
            break
        except Exception as ex:
            print(f"  Overpass intento {intento + 1}: {type(ex).__name__}", flush=True)
            time.sleep(40 * (intento + 1))
    else:
        raise RuntimeError("Overpass no respondio")
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    time.sleep(10)
    return datos


def terreno(depto: str, mun: dict):
    xs = [b for p in mun.values() for b in (p["geom"].bounds[0], p["geom"].bounds[2])]
    ys = [b for p in mun.values() for b in (p["geom"].bounds[1], p["geom"].bounds[3])]
    bbox = [min(xs) - ch.MARGEN, min(ys) - ch.MARGEN, max(xs) + ch.MARGEN, max(ys) + ch.MARGEN]
    f = ch.dem_departamento(depto, bbox)
    grid = Grid.from_raster(str(f))
    dem = np.array(grid.read_raster(str(f)), dtype="float64")
    validas = dem != ch.NODATA
    infl = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(grid.read_raster(str(f)))))
    fdir = grid.flowdir(infl)
    acc = np.array(grid.accumulation(fdir), dtype="float64")
    lat = (bbox[1] + bbox[3]) / 2
    dy = ch.RES_GRADOS * ch.M_GRADO
    dx = dy * math.cos(math.radians(lat))
    z = np.where(validas, dem, np.nan)
    gy, gx = np.gradient(z, dy, dx)
    tan_b = np.hypot(gx, gy)
    pend_deg = np.degrees(np.arctan(tan_b))
    twi = np.log((acc * math.sqrt(dx * dy)) / np.maximum(tan_b, TAN_MIN))
    red = acc > (UMBRAL_RED_KM2 * 1e6 / (dx * dy))
    dist = distance_transform_edt(~red, sampling=(dy, dx))
    for a in (pend_deg, twi, dist):
        a[~validas] = np.nan
    return grid, pend_deg, twi, dist, dem.shape


def puntos(coords):
    if len(coords) < 2:
        return [], 0.0
    k = math.cos(math.radians(np.mean([c[1] for c in coords])))
    largo = LineString([(x * k, y) for x, y in coords]).length * ch.M_GRADO
    n = max(1, int(largo // PASO_M))
    ln = LineString(coords)
    return [(p.x, p.y) for p in (ln.interpolate((i + 0.5) / n, normalized=True) for i in range(n))], largo / n / 1000.0


def procesar(depto: str) -> pd.DataFrame:
    t0 = time.time()
    mun = poligonos(depto)
    grid, pend, twi, dist, forma = terreno(depto, mun)
    print(f"  terreno listo ({time.time() - t0:.0f}s)", flush=True)
    bb = [min(p["geom"].bounds[0] for p in mun.values()), min(p["geom"].bounds[1] for p in mun.values()),
          max(p["geom"].bounds[2] for p in mun.values()), max(p["geom"].bounds[3] for p in mun.values())]
    datos = osm_vias(depto, bb)
    vias = [e for e in datos.get("elements", []) if e.get("type") == "way" and e.get("geometry")]
    print(f"  OSM: {len(vias)} tramos; base {datos.get('osm3s', {}).get('timestamp_osm_base')} ({time.time() - t0:.0f}s)", flush=True)
    cods = list(mun)
    arbol = STRtree([mun[c]["geom"] for c in cods])
    filas = []
    for v in vias:
        tags = v.get("tags", {})
        if tags.get("bridge", "no") not in ("no", ""):
            continue
        coords = [(g["lon"], g["lat"]) for g in v["geometry"]]
        pts, km_pt = puntos(coords)
        vp, vw, vd = [], [], []
        for x, y in pts:
            col, row = ~grid.affine * (x, y)
            r, c = int(math.floor(row)), int(math.floor(col))
            if 0 <= r < forma[0] and 0 <= c < forma[1] and not np.isnan(pend[r, c]):
                vp.append(pend[r, c]); vw.append(twi[r, c]); vd.append(dist[r, c])
        if not vp:
            continue
        mid = pts[len(pts) // 2]
        m = next((cods[int(i)] for i in arbol.query(Point(*mid), predicate="intersects")), None)
        if m is None:
            continue
        vp, vw, vd = np.array(vp), np.array(vw), np.array(vd)
        fila = {"way_id": v["id"], "highway": tags.get("highway"), "codigo": m, "depto": depto, "km": len(vp) * km_pt,
                "twi_p90": float(np.percentile(vw, 90)), "pend_p90": float(np.percentile(vp, 90)), "lat": mid[1], "lon": mid[0]}
        for u in PEND_UMBRALES:
            fila[f"C{u}"] = float((vp >= u).mean())
        for u in DIST_UMBRALES:
            fila[f"D{u}"] = float((vd < u).mean())
        filas.append(fila)
    df = pd.DataFrame(filas)
    print(f"  {len(df)} tramos con datos, {df['km'].sum():.0f} km ({time.time() - t0:.0f}s)", flush=True)
    return df


def main() -> None:
    for d in sys.argv[1].split(","):
        out = CACHE / f"ivg_{d}.pkl"
        if out.exists():
            print(f"{d} ya existe", flush=True)
            continue
        print(f"Departamento {d}", flush=True)
        try:
            procesar(d).to_pickle(out)
        except Exception as ex:
            print(f"  FALLA {d}: {type(ex).__name__}: {str(ex)[:200]}", flush=True)


if __name__ == "__main__":
    main()
