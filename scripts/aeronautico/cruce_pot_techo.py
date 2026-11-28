"""Paso 4 de #332 fase 2: cruce de la altura del POT (U-16) con el techo aeronáutico de SKBQ.

Malla de 30 m en la cuadrícula del U-16 (la de clasificar_u16.py):
- techo aeronáutico (m s. n. m.): superficies.py con RWY 05 de precisión CAT I clave 4, RWY 23 que no es de
  precisión clave 4 y despegue clave 3/4;
- terreno: Copernicus DEM GLO-30, remuestreado bilineal a la malla. Es un modelo de superficie (DSM): en la ciudad
  incluye edificios y árboles, así que el techo sobre el terreno sale más bajo y la estimación queda del lado
  conservador;
- altura del POT: pisos × 3,0 m + 1,5 m, con sensibilidad de 2,8 y 3,5 m por piso (fijado en el preregistro);
- conflicto: altura del POT > techo − terreno.

Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided
under COPERNICUS by the European Union and ESA; all rights reserved. The organisations in charge of the Copernicus
programme by law or by delegation do not incur any liability for any use of the Copernicus WorldDEM-30.

Uso (entorno geo): python -I scripts/aeronautico/cruce_pot_techo.py <u16_pisos.npz> <dir_dem> <dir_salida>
"""
from __future__ import annotations

import glob
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

sys.path.insert(0, str(Path(__file__).resolve().parent))
from georef_u16 import A_U16, CRS_U16  # noqa: E402
from superficies import pista_skbq, techo  # noqa: E402

warnings.filterwarnings("ignore")
M_POR_PISO = {"central": 3.0, "bajo": 2.8, "alto": 3.5}
REMATE = 1.5


def dem_en_malla(dir_dem: str, E0: float, N1: float, celda: float, nfil: int, ncol: int) -> np.ndarray:
    fuentes = [rasterio.open(p) for p in sorted(glob.glob(str(Path(dir_dem) / "*.tif")))]
    mosaico, tr = merge(fuentes)
    destino = np.full((nfil, ncol), np.nan, dtype=np.float32)
    reproject(mosaico[0], destino, src_transform=tr, src_crs=fuentes[0].crs,
              dst_transform=from_origin(E0, N1, celda, celda), dst_crs=CRS_U16.to_wkt(),
              resampling=Resampling.bilinear, dst_nodata=np.nan)
    return destino


def rellenar_huecos(clase: np.ndarray, pisos_clase: np.ndarray, min_vecinos: int = 13) -> np.ndarray:
    """Sensibilidad (no es el resultado principal): una celda sin clase toma la clase mayoritaria de su vecindario de
    5×5 si al menos `min_vecinos` de los 24 vecinos tienen clase. Una sola pasada."""
    n_cls = int(clase.max()) + 1
    conteo = np.zeros((n_cls,) + clase.shape, dtype=np.int16)
    pad = np.pad(clase, 2, constant_values=-1)
    for dy in range(5):
        for dx in range(5):
            if dy == 2 and dx == 2:
                continue
            v = pad[dy:dy + clase.shape[0], dx:dx + clase.shape[1]]
            for k in range(n_cls):
                conteo[k] += v == k
    total = conteo.sum(axis=0)
    mejor = conteo.argmax(axis=0)
    nueva = np.where((clase < 0) & (total >= min_vecinos), mejor, clase)
    pisos = np.where(nueva >= 0, pisos_clase[np.clip(nueva, 0, None)], -1).astype(np.float32)
    pisos[pisos < 0] = np.nan
    return pisos


def resumen(pisos, libre, celda, nombres_pisos):
    ha = celda * celda / 1e4
    filas = []
    for p in sorted(set(np.unique(pisos[np.isfinite(pisos)]).tolist())):
        m = pisos == p
        filas.append({"pisos": int(p), "area_ha": round(float(m.sum() * ha), 1),
                      **{f"conflicto_ha_{k}": round(float((m & (p * v + REMATE > libre)).sum() * ha), 1)
                         for k, v in M_POR_PISO.items()}})
    return filas


def main(npz: str, dir_dem: str, dir_salida: str):
    sys.stdout.reconfigure(encoding="utf-8")
    out = Path(dir_salida); out.mkdir(parents=True, exist_ok=True)
    z = np.load(npz)
    clase, pisos = z["clase"], z["pisos"]
    E0, N1, celda = float(z["E0"]), float(z["N1"]), float(z["celda"])
    nfil, ncol = clase.shape
    E = E0 + (np.arange(ncol) + 0.5) * celda
    N = N1 - (np.arange(nfil) + 0.5) * celda
    EE, NN = np.meshgrid(E, N)

    pista, arp = pista_skbq(lambda lo, la: A_U16.transform(lo, la))
    kw = dict(pista=pista, aprox_a="precision_cat1_3_4", aprox_b="no_precision_4", despegue="clave_3_4")
    t_est, limita, _ = techo(EE, NN, forma_horizontal="estadio", detalle=True, **kw)
    t_cir = techo(EE, NN, forma_horizontal="circulo", arp=arp, **kw)
    dem = dem_en_malla(dir_dem, E0, N1, celda, nfil, ncol)
    libre_est = t_est - dem
    libre_cir = t_cir - dem

    resultados = {}
    for nombre, libre in (("estadio", libre_est), ("circulo", libre_cir)):
        resultados[nombre] = resumen(pisos, libre, celda, None)
    pisos_r = rellenar_huecos(clase, z["pisos_clase"].astype(np.float32))
    resultados["estadio_con_relleno"] = resumen(pisos_r, libre_est, celda, None)

    # Superficie que limita en las celdas en conflicto (escenario central, estadio)
    conf = np.isfinite(pisos) & (pisos * M_POR_PISO["central"] + REMATE > libre_est)
    sup_conf = {k: int(v) for k, v in zip(*np.unique(limita[conf], return_counts=True))}
    # Zonas de 40-50 pisos: margen mínimo hasta el techo
    alto = np.isfinite(pisos) & (pisos >= 40)
    margen = (libre_est - (pisos * M_POR_PISO["central"] + REMATE))[alto & np.isfinite(libre_est)]
    altas_cubiertas = int((alto & np.isfinite(libre_est)).sum())
    np.savez_compressed(out / "techo_malla.npz", techo_estadio=t_est.astype(np.float32),
                        techo_circulo=t_cir.astype(np.float32), dem=dem, pisos=pisos, limita=limita,
                        E0=E0, N1=N1, celda=celda)
    info = {
        "celdas_con_pisos": int(np.isfinite(pisos).sum()),
        "celdas_con_pisos_relleno": int(np.isfinite(pisos_r).sum()),
        "celdas_con_techo": int(np.isfinite(t_est).sum()),
        "celdas_pot_y_techo": int((np.isfinite(pisos) & np.isfinite(t_est)).sum()),
        "resultados": resultados,
        "superficie_que_limita_en_conflicto": sup_conf,
        "zonas_40_50_pisos": {"celdas": int(alto.sum()), "celdas_bajo_alguna_superficie": altas_cubiertas,
                              "margen_min_m": float(margen.min()) if margen.size else None},
        "techo_sobre_terreno_min_m_en_ciudad": float(np.nanmin(np.where(np.isfinite(pisos), libre_est, np.nan))),
    }
    (out / "cruce_pot_techo.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
