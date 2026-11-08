"""Cuencas de las estaciones de caudal del IDEAM con DEM de ~90 m: area, pendiente media, lluvia media anual y elevacion media.
Protocolo: PROTOCOLO_REGIONALIZACION_CAUDALES.md (fijado antes de delinear).

Uso: python scripts/hidro/cuencas_estaciones.py [codigos de departamento separados por coma]
Salida: scripts/hidro/cuencas_estaciones.csv (se fusiona por departamento; reintentar uno no borra los demas).
"""
from __future__ import annotations

import gc
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.validation import make_valid

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "satelite"))
import calcular_hand_caribe as ch  # noqa: E402  (tuberia HAND/DEM; configura UTF-8)
import _datos_caribe as dc  # noqa: E402
from pysheds.grid import Grid  # noqa: E402

if not hasattr(np, "in1d"):
    np.in1d = np.isin

DEPTOS = ["08", "13", "20", "23", "44", "47", "70", "63", "66", "17", "15", "25", "41", "73", "68", "54", "76", "19", "52", "50", "05"]
RADIOS_SNAP_M = (1500.0, 500.0, 0.0)
AREA_MIN_KM2 = 5.0
MARGEN_BORDE_CELDAS = 3     # enmienda 1: se excluye la cuenca si su mascara llega a menos de 3 celdas del borde del DEM
DESTINO = AQUI / "cuencas_estaciones.csv"
LLUVIA = AQUI / "_cache" / "lluvia_media_anual_1991_2020.npz"


def estaciones() -> pd.DataFrame:
    fq = json.loads((AQUI.parent / "satelite" / "frecuencia_crecientes_ideam.json").read_text(encoding="utf-8"))
    fq = [e for e in fq if e["rep"] <= 0.10 and e["n"] >= 30]
    sb, filas, ini = dc._sb(), [], 0
    while True:
        p = sb.table("ideam_estaciones_caudal").select("codigo,nombre,corriente,categoria,latitud,longitud,altitud").range(ini, ini + 999).execute().data
        filas += p
        if len(p) < 1000:
            break
        ini += 1000
    cat = pd.DataFrame(filas).set_index("codigo")
    out = []
    for e in fq:
        if e["codigo"] in cat.index:
            c = cat.loc[e["codigo"]]
            out.append({"codigo": e["codigo"], "corriente": c["corriente"], "categoria": c["categoria"], "lat": c["latitud"], "lon": c["longitud"], "altitud": c["altitud"],
                        "n": e["n"], "xi": e["xi"], **{f"q{t}": e["q_gev"][str(t)] for t in (2, 5, 10, 25, 50)},
                        **{f"qlp{t}": e["q_lp3"][str(t)] for t in (2, 5, 10, 25, 50)}})
    return pd.DataFrame(out).dropna(subset=["lat", "lon"])


def lluvia_en(lon, lat, lluvia):
    mm, tr = lluvia["mm"], lluvia["transform"]
    col = np.floor((lon - tr[2]) / tr[0]).astype(int)
    row = np.floor((lat - tr[5]) / tr[4]).astype(int)
    ok = (row >= 0) & (row < mm.shape[0]) & (col >= 0) & (col < mm.shape[1])
    v = np.full(lon.shape, np.nan, dtype="float64")
    v[ok] = mm[row[ok], col[ok]]
    return v


def procesar(depto: str, est: pd.DataFrame, lluvia) -> list[dict]:
    t0 = time.time()
    pols = dc.poligonos([depto])
    union = unary_union([make_valid(p["geom"]) for p in pols.values()])
    dentro = est[[union.contains(Point(r.lon, r.lat)) for r in est.itertuples()]]
    if dentro.empty:
        print(f"  sin estaciones en {depto}", flush=True)
        return []
    xs = [b for p in pols.values() for b in (p["geom"].bounds[0], p["geom"].bounds[2])]
    ys = [b for p in pols.values() for b in (p["geom"].bounds[1], p["geom"].bounds[3])]
    bbox = [min(xs) - ch.MARGEN, min(ys) - ch.MARGEN, max(xs) + ch.MARGEN, max(ys) + ch.MARGEN]
    f = ch.dem_departamento(depto, bbox)
    grid = Grid.from_raster(str(f))
    dem = grid.read_raster(str(f))
    z = np.array(dem, dtype="float32")
    validas = z != ch.NODATA
    inflated = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dem)))
    fdir = grid.flowdir(inflated)
    acc = np.array(grid.accumulation(fdir), dtype="float32")
    lat0 = (bbox[1] + bbox[3]) / 2
    km2_celda = (ch.RES_GRADOS * ch.M_GRADO) ** 2 * math.cos(math.radians(lat0)) / 1e6
    zz = np.where(validas, z, np.nan)
    dy = ch.RES_GRADOS * ch.M_GRADO
    dzdy, dzdx = np.gradient(zz, dy, dy * math.cos(math.radians(lat0)))
    pend = (100 * np.hypot(dzdx, dzdy)).astype("float32")
    del dzdx, dzdy, inflated
    gc.collect()
    print(f"  DEM, flujo y pendiente listos ({time.time() - t0:.0f}s); {len(dentro)} estaciones", flush=True)
    filas = []
    for r in dentro.itertuples():
        col, row = ~grid.affine * (r.lon, r.lat)
        ri, ci = int(math.floor(row)), int(math.floor(col))
        for radio in RADIOS_SNAP_M:
            fila = {"codigo": r.codigo, "depto": depto, "variante": f"r{int(radio)}", "altitud_cat": r.altitud}
            if not (0 <= ri < acc.shape[0] and 0 <= ci < acc.shape[1]):
                fila["motivo_exclusion"] = "fuera_dem"
                filas.append(fila)
                continue
            rad = int(math.ceil(radio / dy))
            r0, r1, c0, c1 = max(0, ri - rad), min(acc.shape[0], ri + rad + 1), max(0, ci - rad), min(acc.shape[1], ci + rad + 1)
            ventana = acc[r0:r1, c0:c1]
            k = np.unravel_index(int(np.argmax(ventana)), ventana.shape)
            rs, cs = r0 + k[0], c0 + k[1]
            fila["snap_m"] = float(math.hypot((rs - ri) * dy, (cs - ci) * dy * math.cos(math.radians(lat0))))
            fila["elev_snap_m"] = float(zz[rs, cs]) if np.isfinite(zz[rs, cs]) else None
            a_km2 = float(acc[rs, cs] * km2_celda)
            fila["area_acc_km2"] = a_km2
            if a_km2 < AREA_MIN_KM2:
                fila["motivo_exclusion"] = "area_menor_5km2"
                filas.append(fila)
                continue
            mascara = np.array(grid.catchment(cs, rs, fdir, xytype="index"), dtype=bool)
            rr, cc = np.nonzero(mascara)
            margen = int(min(rr.min(), cc.min(), mascara.shape[0] - 1 - rr.max(), mascara.shape[1] - 1 - cc.max()))
            fila["margen_borde_celdas"] = margen
            if margen < MARGEN_BORDE_CELDAS:     # la ultima fila/columna del DEM puede ser NODATA: la cuenca se detiene una celda antes
                fila["motivo_exclusion"] = "toca_borde_dem"
                filas.append(fila)
                continue
            lon_c, lat_c = grid.affine * (cc + 0.5, rr + 0.5)
            fila.update({"area_km2": float(mascara.sum() * km2_celda), "pend_media_pct": float(np.nanmean(pend[rr, cc])),
                         "elev_media_m": float(np.nanmean(zz[rr, cc])),
                         "lluvia_media_mm": float(np.nanmean(lluvia_en(np.asarray(lon_c), np.asarray(lat_c), lluvia))), "motivo_exclusion": ""})
            filas.append(fila)
    print(f"  listo ({time.time() - t0:.0f}s)", flush=True)
    del acc, fdir, pend, zz, z
    gc.collect()
    return filas


def main():
    deptos = sys.argv[1].split(",") if len(sys.argv) > 1 else DEPTOS
    lluvia = dict(np.load(LLUVIA))
    est = estaciones()
    print(f"Estaciones candidatas: {len(est)}", flush=True)
    prev = pd.read_csv(DESTINO, dtype={"codigo": str, "depto": str}) if DESTINO.exists() else pd.DataFrame()
    out = prev[~prev["depto"].isin(deptos)].to_dict("records") if len(prev) else []
    for d in deptos:
        print(f"Departamento {d}", flush=True)
        try:
            out.extend(procesar(d, est, lluvia))
        except Exception as ex:
            print(f"  FALLA {d}: {type(ex).__name__}: {str(ex)[:160]}", flush=True)
        pd.DataFrame(out).to_csv(DESTINO, index=False)
    df = pd.DataFrame(out)
    print(f"\n{len(df)} estaciones procesadas; utilizables: {(df['motivo_exclusion'] == '').sum()}")
    print(df["motivo_exclusion"].value_counts().to_string())


if __name__ == "__main__":
    main()
