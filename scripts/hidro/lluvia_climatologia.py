"""Lluvia media anual 1991-2020 sobre Colombia continental (CHIRPS v3.0 mensual), para la regionalizacion de caudales.
Protocolo: PROTOCOLO_REGIONALIZACION_CAUDALES.md. Salida: scripts/hidro/_cache/lluvia_media_anual_1991_2020.npz
(matriz mm/ano, transformacion afin, ventana BBOX). Reanudable: cache por ano en _cache/lluvia_anual/AAAA.npy.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import rasterio

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "satelite"))
import extraer_chirps_colombia as mc  # noqa: E402  (leer_mes, BBOX)

DEST = AQUI / "_cache"
ANUAL = DEST / "lluvia_anual"
ANOS = range(1991, 2021)


def main():
    ANUAL.mkdir(parents=True, exist_ok=True)
    tr = None
    with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=5, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                      CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.cog", CPL_VSIL_CURL_CHUNK_SIZE="16777216",
                      GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", VSI_CACHE="FALSE"):
        for a in ANOS:
            f = ANUAL / f"{a}.npy"
            if f.exists():
                continue
            meses = []
            for m in range(1, 13):
                z, tr = mc.leer_mes(a, m)
                meses.append(z)
            np.save(f, np.nansum(np.stack(meses), axis=0).astype("float32") * np.where(np.all(np.isnan(np.stack(meses)), axis=0), np.nan, 1.0))
            print(f"{a} listo", flush=True)
    if tr is None:
        z, tr = mc.leer_mes(1991, 1)
    pila = np.stack([np.load(ANUAL / f"{a}.npy") for a in ANOS])
    media = np.nanmean(pila, axis=0).astype("float32")
    np.savez(DEST / "lluvia_media_anual_1991_2020.npz", mm=media, transform=np.array(tr)[:6], bbox=np.array(mc.BBOX))
    v = media[np.isfinite(media)]
    print(f"Media anual 1991-2020: celdas validas {v.size}, mediana {np.median(v):.0f} mm, p5 {np.percentile(v, 5):.0f}, p95 {np.percentile(v, 95):.0f}")


if __name__ == "__main__":
    main()
