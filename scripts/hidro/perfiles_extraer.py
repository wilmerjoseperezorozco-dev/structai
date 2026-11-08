"""Guarda el perfil longitudinal (longitud de tramo, cota y área acumulada por celda) de la ruta más larga de cada cuenca de E1.
Misma ruta que pendiente_cauce_extraer.py (D8, pysheds, DEM ~90 m); solo añade el área acumulada para F1-F4.
Uso: python scripts/hidro/perfiles_extraer.py [deptos]   Salida: scripts/hidro/_cache/perfiles/perfiles_<depto>.pkl"""
from __future__ import annotations

import gc
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import pendiente_cauce_extraer as pe  # noqa: E402  (reutiliza rutas, constantes y funciones de E1)

ce, ch, Grid, Raster = pe.ce, pe.ch, pe.Grid, pe.Raster
SALIDA = AQUI / "_cache" / "perfiles"


def perfil_con_area(fdir_arr, filled, acc, km2_celda, r0, c0, rs, cs, dx, dy):
    r, c = r0, c0
    L, Z, A = [], [float(filled[r, c])], [float(acc[r, c]) * km2_celda]
    for _ in range(filled.size):
        if (r, c) == (rs, cs):
            break
        d = int(fdir_arr[r, c])
        if d not in pe.PASOS:
            return None
        dr, dc = pe.PASOS[d]
        L.append(math.hypot(dr * dy, dc * dx))
        r, c = r + dr, c + dc
        Z.append(float(filled[r, c]))
        A.append(float(acc[r, c]) * km2_celda)
    else:
        return None
    return np.array(L), np.array(Z), np.array(A)


def procesar(depto: str, cuencas: pd.DataFrame) -> dict:
    t0 = time.time()
    pols = ce.dc.poligonos([depto])
    xs = [b for p in pols.values() for b in (p["geom"].bounds[0], p["geom"].bounds[2])]
    ys = [b for p in pols.values() for b in (p["geom"].bounds[1], p["geom"].bounds[3])]
    bbox = [min(xs) - ch.MARGEN, min(ys) - ch.MARGEN, max(xs) + ch.MARGEN, max(ys) + ch.MARGEN]
    f = ch.dem_departamento(depto, bbox)
    grid = Grid.from_raster(str(f))
    dem = grid.read_raster(str(f))
    z = np.array(dem, dtype="float32")
    validas = z != ch.NODATA
    rell = grid.fill_depressions(grid.fill_pits(dem))
    filled = np.where(validas, np.array(rell, dtype="float32"), np.nan)
    inflated = grid.resolve_flats(rell)
    fdir = grid.flowdir(inflated)
    fdir_arr = np.array(fdir)
    acc = np.array(grid.accumulation(fdir), dtype="float32")
    dy = ch.RES_GRADOS * ch.M_GRADO
    dx = dy * math.cos(math.radians((bbox[1] + bbox[3]) / 2))
    km2_celda = dx * dy / 1e6
    peso = Raster(pe.longitud_paso(fdir_arr, dx, dy), fdir.viewfinder)
    del inflated, rell, z
    gc.collect()
    out = {}
    for r in cuencas.itertuples():
        col, row = ~grid.affine * (r.lon, r.lat)
        ri, ci = int(math.floor(row)), int(math.floor(col))
        rad = int(math.ceil(1500.0 / dy))
        r0, r1, c0, c1 = max(0, ri - rad), min(acc.shape[0], ri + rad + 1), max(0, ci - rad), min(acc.shape[1], ci + rad + 1)
        v = acc[r0:r1, c0:c1]
        k = np.unravel_index(int(np.argmax(v)), v.shape)
        rs, cs = r0 + k[0], c0 + k[1]
        try:
            mascara = np.array(grid.catchment(cs, rs, fdir, xytype="index"), dtype=bool)
            dist = np.array(grid.distance_to_outlet(cs, rs, fdir, weights=peso, xytype="index"), dtype="float64")
            dist = np.where(mascara, dist, np.nan)
            kk = np.unravel_index(int(np.nanargmax(dist)), dist.shape)
            p = perfil_con_area(fdir_arr, filled, acc, km2_celda, int(kk[0]), int(kk[1]), rs, cs, dx, dy)
            if p is not None and len(p[0]) >= 3:
                out[r.codigo] = {"L": p[0], "Z": p[1], "A_km2": p[2]}
        except Exception as ex:  # no se oculta: se cuenta al final
            out[r.codigo] = {"error": f"{type(ex).__name__}: {str(ex)[:80]}"}
    print(f"  {depto}: {sum('L' in v for v in out.values())}/{len(cuencas)} perfiles ({time.time() - t0:.0f}s)", flush=True)
    del acc, fdir, fdir_arr, filled, peso
    gc.collect()
    return out


def main():
    c = pd.read_csv(ce.DESTINO, dtype={"codigo": str, "depto": str})
    c = c[(c["variante"] == pe.VARIANTE) & (c["motivo_exclusion"].fillna("") == "")]
    c = c.join(ce.estaciones().set_index("codigo")[["lat", "lon"]], on="codigo", how="inner")
    deptos = sys.argv[1].split(",") if len(sys.argv) > 1 else sorted(c["depto"].unique())
    SALIDA.mkdir(parents=True, exist_ok=True)
    for d in deptos:
        destino = SALIDA / f"perfiles_{d}.pkl"
        sub = c[c["depto"] == d]
        if sub.empty or (destino.exists() and destino.stat().st_size > 0):
            continue
        try:
            with open(destino, "wb") as fh:
                pickle.dump(procesar(d, sub), fh)
        except Exception as ex:
            destino.unlink(missing_ok=True)
            print(f"  FALLA {d}: {type(ex).__name__}: {str(ex)[:160]}", flush=True)
    print("FIN", flush=True)


if __name__ == "__main__":
    main()
