"""ESA CCI Soil Moisture v09.2 COMBINED (diario, 0.25 grados): recorta Colombia y descarta el archivo global.

NO EJECUTAR sin autorizacion del usuario (descarga archivos). Fuente anonima: dap.ceda.ac.uk (CEDA).
Licencia: ver 00README_catalogue_and_licence.txt (terminos ESA CCI Soil Moisture v2; citar segun el catalogo CEDA).
Cada archivo global pesa 0,5-2,4 MB; se baja, se recorta a Colombia y se borra. Reanudable (guarda un .npz por anio).

Uso: python bajar_esa_cci_humedad.py PRUEBA            # 1 archivo, mide tamano y velocidad
     python bajar_esa_cci_humedad.py 2019 2024         # anios completos (ambos inclusive)
"""
from __future__ import annotations

import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import rasterio
import requests
from rasterio.windows import from_bounds

BASE = "https://dap.ceda.ac.uk/neodc/esacci/soil_moisture/data/daily_files/COMBINED/v09.2"
SALIDA = Path(__file__).resolve().parent / "_cache" / "esa_cci_sm"
LAT = (-4.5, 13.5)
LON = (-82.0, -66.5)
PAUSA_S = 0.5
TIMEOUT_S = 120


def url_dia(d: date) -> str:
    return f"{BASE}/{d.year}/ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{d:%Y%m%d}000000-fv09.2.nc"


def recortar(ruta: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Lee la variable `sm` con GDAL (rasterio) y recorta Colombia. Devuelve (sm, lat, lon)."""
    with rasterio.open(f'NETCDF:"{ruta}":sm') as src:
        ventana = from_bounds(LON[0], LAT[0], LON[1], LAT[1], src.transform).round_offsets().round_lengths()
        arr = src.read(1, window=ventana, masked=True)
        tr = src.window_transform(ventana)
        sm = np.ma.filled(arr.astype("float32"), np.nan)
        lon = tr.c + tr.a * (np.arange(sm.shape[1]) + 0.5)
        lat = tr.f + tr.e * (np.arange(sm.shape[0]) + 0.5)
    return sm, lat, lon


def bajar_dia(d: date, tmp: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, int] | None:
    r = requests.get(url_dia(d), timeout=TIMEOUT_S)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    ruta = tmp / f"{d:%Y%m%d}.nc"
    ruta.write_bytes(r.content)
    try:
        return (*recortar(ruta), len(r.content))
    finally:
        ruta.unlink(missing_ok=True)


def main(args: list[str]) -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        if args and args[0] == "PRUEBA":
            t0 = time.time()
            sm, lat, lon, n = bajar_dia(date(2022, 6, 1), tmp)
            dt = time.time() - t0
            print(f"1 archivo: {n/1e6:.2f} MB en {dt:.1f} s ({n/1e6/dt:.2f} MB/s); recorte {sm.shape}; "
                  f"celdas con dato {int(np.isfinite(sm).sum())} de {sm.size}")
            return
        for anio in range(int(args[0]), int(args[1]) + 1):
            destino = SALIDA / f"sm_{anio}.npz"
            if destino.exists():
                continue
            dias, cubos, lat, lon, total = [], [], None, None, 0
            d = date(anio, 1, 1)
            while d.year == anio:
                r = bajar_dia(d, tmp)
                if r is not None:
                    sm, lat, lon, n = r
                    dias.append(d.toordinal())
                    cubos.append(sm)
                    total += n
                d += timedelta(days=1)
                time.sleep(PAUSA_S)
            np.savez_compressed(destino, dias=np.array(dias), sm=np.stack(cubos), lat=lat, lon=lon)
            print(f"{anio}: {len(dias)} dias, {total/1e9:.2f} GB bajados", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
