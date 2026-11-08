"""Elevación media y pendiente media por distrito de Perú (Copernicus GLO-90), insumo de R1 y del bloque exploratorio de la sierra.

Uso: python -I relieve_distrito_peru.py <dir_mosaicos_dem> <per_admin3.shp> <salida.json>
Solo calcula covariables; no las asocia con nada. Pendiente = gradiente D8 simple en grados sobre celdas de ~90 m.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio import features
from rasterio.merge import merge

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calcular_hand_peru as hp  # noqa: E402


def procesar(adm1: str, distritos: dict, directorio: str) -> list[dict]:
    lims = [d["geom"].bounds for d in distritos.values()]
    bbox = [min(b[0] for b in lims) - hp.MARGEN, min(b[1] for b in lims) - hp.MARGEN,
            max(b[2] for b in lims) + hp.MARGEN, max(b[3] for b in lims) + hp.MARGEN]
    ds = [rasterio.open(r) for r in hp.mosaicos_que_cubren(directorio, bbox)]
    try:
        z, tr = merge(ds, bounds=tuple(bbox), res=(hp.RES_GRADOS, hp.RES_GRADOS), nodata=np.nan,
                      resampling=rasterio.enums.Resampling.average)
    finally:
        for d in ds:
            d.close()
    z = z[0].astype("float64")
    z[z == 0] = np.nan  # océano
    lat0 = (bbox[1] + bbox[3]) / 2
    dy = hp.RES_GRADOS * hp.M_GRADO
    dx = dy * math.cos(math.radians(lat0))
    gy, gx = np.gradient(z, dy, dx)
    pend = np.degrees(np.arctan(np.hypot(gx, gy)))
    out = []
    for pcode, p in distritos.items():
        m = features.geometry_mask([p["geom"].__geo_interface__], out_shape=z.shape, transform=tr, invert=True)
        v, s = z[m & ~np.isnan(z)], pend[m & ~np.isnan(pend)]
        out.append({"adm3_pcode": pcode, "adm1": adm1, "n_celdas": int(len(v)),
                    "elev_media_m": float(v.mean()) if len(v) >= hp.MIN_CELDAS else None,
                    "pend_media_grados": float(s.mean()) if len(s) >= hp.MIN_CELDAS else None})
    return out


def main(directorio: str, shp: str, salida: str) -> None:
    por_adm1 = hp.leer_distritos(shp)
    filas = []
    for adm1 in sorted(por_adm1):
        print(adm1, flush=True)
        try:
            filas.extend(procesar(adm1, por_adm1[adm1], directorio))
        except Exception as e:
            print(f"  FALLA {adm1}: {type(e).__name__}: {str(e)[:150]}", flush=True)
    Path(salida).write_text(json.dumps({"distritos": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{sum(1 for f in filas if f['elev_media_m'] is not None)}/{len(filas)} distritos con relieve")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
