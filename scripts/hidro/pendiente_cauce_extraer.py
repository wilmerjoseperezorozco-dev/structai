"""Longitud y pendiente del cauce principal de las cuencas de la Etapa A (variante r1500). Protocolo: PROTOCOLO_PENDIENTE_CAUCE.md
Uso: python scripts/hidro/pendiente_cauce_extraer.py [codigos de departamento separados por coma]
Salida: scripts/hidro/pendiente_cauce.csv (se fusiona por departamento)."""
from __future__ import annotations

import gc
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cuencas_estaciones as ce  # noqa: E402  (configura rutas y UTF-8; pysheds)
from pysheds.grid import Grid  # noqa: E402
from pysheds.sview import Raster  # noqa: E402

ch = ce.ch
DESTINO = AQUI / "pendiente_cauce.csv"
VARIANTE = "r1500"
PISO_S = 0.0005                     # m/m, por tramo de celda (Enmienda 1)
DIRMAP = (64, 128, 1, 2, 4, 8, 16, 32)   # N, NE, E, SE, S, SO, O, NO
PASOS = {64: (-1, 0), 128: (-1, 1), 1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1)}


def longitud_paso(codigo_dir: np.ndarray, dx: float, dy: float) -> np.ndarray:
    w = np.full(codigo_dir.shape, np.nan, dtype="float32")
    for d, (dr, dc) in PASOS.items():
        w[codigo_dir == d] = math.hypot(dr * dy, dc * dx)
    return w


def perfil(fdir_arr, filled, r0, c0, rs, cs, dx, dy):
    """Sigue D8 desde (r0,c0) hasta el punto de aforo (rs,cs). Devuelve longitudes de tramo (m) y cotas de cada celda."""
    r, c = r0, c0
    L, Z = [], [float(filled[r, c])]
    for _ in range(filled.size):
        if (r, c) == (rs, cs):
            break
        d = int(fdir_arr[r, c])
        if d not in PASOS:
            return None
        dr, dc = PASOS[d]
        L.append(math.hypot(dr * dy, dc * dx))
        r, c = r + dr, c + dc
        Z.append(float(filled[r, c]))
    else:
        return None
    return np.array(L), np.array(Z)


def metricas(L: np.ndarray, Z: np.ndarray) -> dict:
    tot = L.sum()
    dz = np.maximum(Z[:-1] - Z[1:], 0.0)           # cota aguas arriba menos aguas abajo, sin negativos
    s_i = dz / L
    piso = s_i < PISO_S
    s_i = np.maximum(s_i, PISO_S)
    s_ts = (tot / np.sum(L / np.sqrt(s_i))) ** 2    # Taylor-Schwarz
    cum = np.concatenate([[0.0], np.cumsum(L[::-1])])   # distancia desde el aforo hacia aguas arriba, a cada celda de Z[::-1]
    zr = Z[::-1]
    z10, z85 = np.interp([0.10 * tot, 0.85 * tot], cum, zr)
    s_1085 = max((z85 - z10) / (0.75 * tot), PISO_S)
    return {"L_km": tot / 1000.0, "S_ts": float(s_ts), "S_1085": float(s_1085), "frac_tramos_piso": float(piso.mean()), "desnivel_m": float(Z[0] - Z[-1])}


def procesar(depto: str, cuencas: pd.DataFrame) -> list[dict]:
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
    lat0 = (bbox[1] + bbox[3]) / 2
    dy = ch.RES_GRADOS * ch.M_GRADO
    dx = dy * math.cos(math.radians(lat0))
    km2_celda = dx * dy / 1e6
    peso = Raster(longitud_paso(fdir_arr, dx, dy), fdir.viewfinder)
    del inflated, rell, z
    gc.collect()
    filas = []
    for r in cuencas.itertuples():
        fila = {"codigo": r.codigo, "depto": depto}
        col, row = ~grid.affine * (r.lon, r.lat)
        ri, ci = int(math.floor(row)), int(math.floor(col))
        rad = int(math.ceil(1500.0 / dy))
        r0, r1, c0, c1 = max(0, ri - rad), min(acc.shape[0], ri + rad + 1), max(0, ci - rad), min(acc.shape[1], ci + rad + 1)
        v = acc[r0:r1, c0:c1]
        k = np.unravel_index(int(np.argmax(v)), v.shape)
        rs, cs = r0 + k[0], c0 + k[1]
        mascara = np.array(grid.catchment(cs, rs, fdir, xytype="index"), dtype=bool)
        fila["area_recalculada_km2"] = float(mascara.sum() * km2_celda)
        try:
            dist = np.array(grid.distance_to_outlet(cs, rs, fdir, weights=peso, xytype="index"), dtype="float64")
            dist = np.where(mascara, dist, np.nan)
            kk = np.unravel_index(int(np.nanargmax(dist)), dist.shape)
            p = perfil(fdir_arr, filled, int(kk[0]), int(kk[1]), rs, cs, dx, dy)
            if p is None or len(p[0]) < 3:
                fila["motivo"] = "ruta_invalida"
            else:
                fila.update(metricas(*p))
                fila["L_pysheds_km"] = float(dist[kk] / 1000.0)
                fila["motivo"] = ""
        except Exception as ex:  # se registra, no se oculta
            fila["motivo"] = f"error:{type(ex).__name__}:{str(ex)[:80]}"
        filas.append(fila)
    print(f"  {depto}: {len(filas)} cuencas ({time.time() - t0:.0f}s)", flush=True)
    del acc, fdir, fdir_arr, filled, peso
    gc.collect()
    return filas


def main():
    c = pd.read_csv(ce.DESTINO, dtype={"codigo": str, "depto": str})
    c = c[(c["variante"] == VARIANTE) & (c["motivo_exclusion"].fillna("") == "")]
    est = ce.estaciones().set_index("codigo")
    c = c.join(est[["lat", "lon"]], on="codigo", how="inner")
    deptos = sys.argv[1].split(",") if len(sys.argv) > 1 else sorted(c["depto"].unique())
    prev = pd.read_csv(DESTINO, dtype={"codigo": str, "depto": str}) if DESTINO.exists() else pd.DataFrame()
    out = prev[~prev["depto"].isin(deptos)].to_dict("records") if len(prev) else []
    print(f"{len(c)} cuencas en {len(deptos)} departamentos", flush=True)
    for d in deptos:
        sub = c[c["depto"] == d]
        if sub.empty:
            continue
        try:
            out.extend(procesar(d, sub))
        except Exception as ex:
            print(f"  FALLA {d}: {type(ex).__name__}: {str(ex)[:160]}", flush=True)
        pd.DataFrame(out).to_csv(DESTINO, index=False)
    df = pd.DataFrame(out)
    print(f"\n{len(df)} filas; motivo: {df['motivo'].fillna('').value_counts().to_dict()}")


if __name__ == "__main__":
    main()
