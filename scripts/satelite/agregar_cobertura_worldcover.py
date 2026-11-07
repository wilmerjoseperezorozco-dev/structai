"""Agrega a susceptibilidad_muestras.csv la cobertura del suelo (ESA WorldCover v200, 2021) y la lluvia anual media municipal (CHIRPS 1981-2024).

Salida: susceptibilidad_muestras_wc.csv. WorldCover se lee por teselas de 3 grados desde AWS (COG) con una vista de resumen de ~90 m.
Reanudable: _cache/wc_teselas/{tesela}.json. Uso: python agregar_cobertura_worldcover.py
"""
from __future__ import annotations

import io
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache" / "wc_teselas"
URL = "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{n}_Map.tif"
LADO = 3600          # 3 grados / 3600 px = ~93 m


def nombre_tesela(lat: float, lon: float) -> tuple[str, int, int]:
    la, lo = math.floor(lat / 3) * 3, math.floor(lon / 3) * 3
    return f"{'N' if la >= 0 else 'S'}{abs(la):02d}{'E' if lo >= 0 else 'W'}{abs(lo):03d}", la, lo


def muestrear_tesela(nombre: str, la: int, lo: int, puntos: pd.DataFrame) -> dict[int, int]:
    cf = CACHE / f"{nombre}.json"
    if cf.exists():
        return {int(k): v for k, v in json.loads(cf.read_text(encoding="utf-8")).items()}
    z = None
    for intento in range(5):
        try:
            with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
                with rasterio.open(URL.format(n=nombre)) as ds:
                    z = ds.read(1, out_shape=(LADO, LADO), resampling=Resampling.nearest)
                    tr = ds.transform * ds.transform.scale(ds.width / LADO, ds.height / LADO)
            break
        except Exception as e:
            print(f"  {nombre}: {str(e)[:70]}; reintento {intento + 1}", flush=True)
            time.sleep(10 * (intento + 1))
    if z is None:
        return {}
    out = {}
    for i, lon, lat in zip(puntos.index, puntos.lon, puntos.lat):
        col, row = ~tr * (lon, lat)
        r, c = int(row), int(col)
        if 0 <= r < LADO and 0 <= c < LADO:
            out[int(i)] = int(z[r, c])
    CACHE.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps(out), encoding="utf-8")
    return out


def lluvia_media_municipal() -> dict[str, float]:
    mm = {}
    for f, clave in (("chirps_mensual_colombia_1981_2018.json", "a"), ("chirps_mensual_colombia.json", "b")):
        d = json.loads((AQUI / f).read_text(encoding="utf-8"))
        for c, v in d["municipios"].items():
            s = [x for x in v["precip_mm"] if x is not None]
            mm.setdefault(c, []).append((len(s), float(np.sum(s))))
    return {c: sum(t for _, t in v) / sum(n for n, _ in v) * 12 for c, v in mm.items()}


def main() -> None:
    df = pd.read_csv(AQUI / "susceptibilidad_muestras.csv", dtype={"mun": str})
    por = {}
    for i, (lat, lon) in enumerate(zip(df.lat, df.lon)):
        n, la, lo = nombre_tesela(lat, lon)
        por.setdefault((n, la, lo), []).append(i)
    print(f"Puntos {len(df)}; teselas WorldCover: {len(por)}", flush=True)
    cober = {}
    for k, ((n, la, lo), idx) in enumerate(sorted(por.items())):
        cober.update(muestrear_tesela(n, la, lo, df.loc[idx, ["lon", "lat"]]))
        if k % 5 == 4:
            print(f"  teselas {k + 1}/{len(por)}", flush=True)
    df["cobertura"] = pd.Series(cober)
    mm = lluvia_media_municipal()
    df["lluvia_anual_mm"] = df.mun.map(mm)
    print(f"Con cobertura: {int(df.cobertura.notna().sum())}/{len(df)}; con lluvia: {int(df.lluvia_anual_mm.notna().sum())}/{len(df)}")
    print("Clases de cobertura:", df.cobertura.value_counts().sort_index().to_dict())
    df.to_csv(AQUI / "susceptibilidad_muestras_wc.csv", index=False)


if __name__ == "__main__":
    main()
