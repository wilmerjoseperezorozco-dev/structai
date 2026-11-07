"""Muestreo de variables condicionantes para la susceptibilidad a movimientos en masa (protocolo seccion 22).

Presencias: puntos SIMMA (SGC). Fondo: puntos aleatorios sobre tierra (razon 5:1, semilla fija).
Variables: pendiente (%), curvatura (laplaciano), elevacion (Copernicus GLO-30 promediado a ~90 m),
edad de la unidad geologica (Mapa Geologico de Colombia V2023), distancia a la falla mas cercana (km).
Salida: scripts/satelite/susceptibilidad_muestras.csv. Reanudable por tesela DEM en _cache/susc_teselas/.
"""
from __future__ import annotations

import csv
import glob
import io
import json
import math
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.enums import Resampling
from shapely import STRtree
from shapely.geometry import Point, shape

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
RAZON_FONDO, SEMILLA = 5, 20261107
LADO_PX = 1200                       # 3600 px de 30 m / 3 -> ~90 m
M_GRADO = 111_320.0
DEM_URL = "https://copernicus-dem-30m.s3.amazonaws.com/{n}/{n}.tif"

GRUPOS_EDAD = [  # el primero que coincide gana (cada palabra clave es una raiz sin acentos)
    ("Cuaternario", ("cuatern", "holoc", "pleistoc")),
    ("Neogeno", ("mioc", "plioc", "serravall", "tortonian", "mesinian", "zancl", "langhian", "burdigal", "aquitan", "messin")),
    ("Paleogeno", ("paleoc", "eoc", "oligoc", "bartonian", "lutetian", "thanetian", "ypresian", "priabon", "rupelian", "chattian", "danian", "selandian")),
    ("Cretacico", ("cretac", "albian", "aptian", "barremian", "berriasian", "cenomanian", "turonian", "coniacian", "santonian", "campanian", "maastricht", "hauterivian", "valanginian")),
    ("Jurasico", ("juras",)),
    ("Triasico", ("trias",)),
    ("Paleozoico", ("ordov", "silur", "devon", "carbon", "permic", "cambri", "llandover", "paleozoic")),
    ("Precambrico", ("proteroz", "steniano", "toniano", "arqueano", "precamb", "ectasian", "calymm", "mesoprot")),
]


def sin_acentos(s: str) -> str:
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()


def grupo_edad(edad: str) -> str:
    t = sin_acentos(edad)
    for nombre, claves in GRUPOS_EDAD:
        if any(c in t for c in claves):
            return nombre
    return "Otro"


def cargar(prefijo: str) -> list[dict]:
    fs: list[dict] = []
    for f in sorted(glob.glob(str(CACHE / "igac" / f"{prefijo}_*.geojson"))):
        fs += json.loads(Path(f).read_text(encoding="utf-8"))["features"]
    return fs


def municipios():
    geoms, cods = [], []
    for f in sorted(glob.glob(str(CACHE / "poligonos_nac_*.geojson"))):
        for ft in json.loads(Path(f).read_text(encoding="utf-8"))["features"]:
            g = shape(ft["geometry"]).buffer(0)
            if not g.is_empty:
                geoms.append(g); cods.append(ft["properties"]["CODIGO"])
    return geoms, cods


def construir_puntos(geoms, cods):
    rng = np.random.default_rng(SEMILLA)
    arbol = STRtree(geoms)
    pres = []
    for ft in cargar("simma_puntos"):
        x, y = ft["geometry"]["coordinates"]
        pres.append((x, y, ft["properties"]["TIPO"]))
    xs = np.array([p[0] for p in pres]); ys = np.array([p[1] for p in pres])
    pts = [Point(x, y) for x, y in zip(xs, ys)]
    idx = arbol.query(pts, predicate="within")          # (2, n): [punto, municipio]
    primero = {}
    for i, j in zip(idx[0], idx[1]):
        primero.setdefault(int(i), int(j))
    filas = [{"tipo": pres[i][2], "presencia": 1, "lon": pres[i][0], "lat": pres[i][1], "mun": cods[j]} for i, j in primero.items()]
    n_pres = len(filas)
    print(f"Presencias SIMMA: {len(pres)}; dentro de municipios continentales: {n_pres}", flush=True)
    objetivo, fondo = RAZON_FONDO * n_pres, []
    while len(fondo) < objetivo:
        lon = rng.uniform(-79.2, -66.8, 20000); lat = rng.uniform(-4.3, 13.5, 20000)
        cand = [Point(a, b) for a, b in zip(lon, lat)]
        idx = arbol.query(cand, predicate="within")
        vistos = set()
        for i, j in zip(idx[0], idx[1]):
            if int(i) not in vistos and len(fondo) < objetivo:
                vistos.add(int(i)); fondo.append({"tipo": "fondo", "presencia": 0, "lon": float(lon[i]), "lat": float(lat[i]), "mun": cods[int(j)]})
    print(f"Puntos de fondo: {len(fondo)}", flush=True)
    return filas + fondo


def muestrear_dem(puntos: list[dict]) -> None:
    (CACHE / "susc_teselas").mkdir(exist_ok=True)
    por_tesela: dict[str, list[int]] = {}
    for i, p in enumerate(puntos):
        la, lo = math.floor(p["lat"]), math.floor(p["lon"])
        n = f"Copernicus_DSM_COG_10_{'N' if la >= 0 else 'S'}{abs(la):02d}_00_{'E' if lo >= 0 else 'W'}{abs(lo):03d}_00_DEM"
        por_tesela.setdefault(n, []).append(i)
    print(f"Teselas DEM: {len(por_tesela)}", flush=True)
    for k, (n, ids) in enumerate(sorted(por_tesela.items())):
        cf = CACHE / "susc_teselas" / f"{n}.json"
        if cf.exists():
            vals = json.loads(cf.read_text(encoding="utf-8"))
        else:
            z = None
            for intento in range(5):
                try:
                    with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
                        with rasterio.open(DEM_URL.format(n=n)) as ds:
                            z = ds.read(1, out_shape=(LADO_PX, LADO_PX), resampling=Resampling.average).astype("float64")
                            tr = ds.transform * ds.transform.scale(ds.width / LADO_PX, ds.height / LADO_PX)
                    break
                except Exception as e:
                    print(f"  {n}: {str(e)[:60]}; reintento {intento + 1}", flush=True)
                    time.sleep(10 * (intento + 1))
            if z is None:
                print(f"  {n}: sin lectura tras reintentos; se omite", flush=True)
                continue
            dy = M_GRADO * abs(tr.e)
            lat_c = tr.f + tr.e * LADO_PX / 2
            dx = M_GRADO * tr.a * math.cos(math.radians(lat_c))
            gy, gx = np.gradient(z, dy, dx)
            pend = np.hypot(gx, gy) * 100.0
            lap = np.full_like(z, np.nan)
            lap[1:-1, 1:-1] = (z[:-2, 1:-1] + z[2:, 1:-1]) / dy**2 + (z[1:-1, :-2] + z[1:-1, 2:]) / dx**2 - 2 * z[1:-1, 1:-1] * (1 / dy**2 + 1 / dx**2)
            vals = {}
            for i in ids:
                col, row = ~tr * (puntos[i]["lon"], puntos[i]["lat"])
                r, c = int(row), int(col)
                if 1 <= r < LADO_PX - 1 and 1 <= c < LADO_PX - 1 and np.isfinite(pend[r, c]) and np.isfinite(lap[r, c]):
                    vals[str(i)] = [float(z[r, c]), float(pend[r, c]), float(lap[r, c] * 100.0)]
            cf.write_text(json.dumps(vals), encoding="utf-8")
        for i in ids:
            v = vals.get(str(i))
            if v:
                puntos[i]["elev"], puntos[i]["pend"], puntos[i]["curv"] = v
        if k % 10 == 9:
            print(f"  teselas {k + 1}/{len(por_tesela)}", flush=True)


def muestrear_geologia(puntos: list[dict]) -> None:
    unidades = cargar("unidades_sgc")
    geoms = [shape(u["geometry"]).buffer(0) for u in unidades]
    grupos = [grupo_edad(u["properties"].get("Edad") or "") for u in unidades]
    arbol = STRtree(geoms)
    pts = [Point(p["lon"], p["lat"]) for p in puntos]
    idx = arbol.query(pts, predicate="within")
    asignado = {}
    for i, j in zip(idx[0], idx[1]):
        asignado.setdefault(int(i), grupos[int(j)])
    for i, p in enumerate(puntos):
        p["edad"] = asignado.get(i, "Sin unidad")
    fallas = [shape(f["geometry"]) for f in cargar("fallas_sgc")]
    tr = Transformer.from_crs(4326, 9377, always_xy=True)
    from shapely.ops import transform as sh_transform
    fal_m = [sh_transform(tr.transform, g) for g in fallas]
    arb_f = STRtree(fal_m)
    pts_m = [Point(*tr.transform(p["lon"], p["lat"])) for p in puntos]
    _, dist = arb_f.query_nearest(pts_m, return_distance=True, all_matches=False)
    for p, d in zip(puntos, dist):
        p["dist_falla_km"] = float(d) / 1000.0


def main() -> None:
    geoms, cods = municipios()
    puntos = construir_puntos(geoms, cods)
    muestrear_geologia(puntos)
    muestrear_dem(puntos)
    campos = ["tipo", "presencia", "lon", "lat", "mun", "elev", "pend", "curv", "edad", "dist_falla_km"]
    completos = [p for p in puntos if "pend" in p]
    with open(AQUI / "susceptibilidad_muestras.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader(); w.writerows(completos)
    print(f"Muestras completas: {len(completos)} de {len(puntos)} (presencias {sum(p['presencia'] for p in completos)})", flush=True)


if __name__ == "__main__":
    main()
