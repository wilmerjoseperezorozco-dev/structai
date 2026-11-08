"""Etapa B: sesgo de CHIRPS frente a pluviometros automaticos del IDEAM y correccion por cuantiles.
Protocolo: PROTOCOLO_SESGO_CHIRPS.md (fijado antes de descargar). Entradas: pluviometros_seleccion.json y _cache/pluviometros/*.json
(pluviometros_descarga.py). Salida: sesgo_chirps_resultados.json
"""
from __future__ import annotations

import datetime as dt
import io
import json
import math
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.stats import spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "satelite"))
import extraer_chirps_diario_colombia as cd  # noqa: E402  (leer_dia)
import extraer_chirps_colombia as mc  # noqa: E402

warnings.filterwarnings("ignore")
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CACHE = AQUI / "_cache"
PUNTOS = CACHE / "chirps_puntos.json"
PERCENTILES = (50, 75, 90, 95, 99)
UMBRAL_LLUVIA_MM = 1.0
N_BOOT = 4000
RNG = np.random.default_rng(20261108)
DIAS = [dt.date(2022, 1, 1) + dt.timedelta(days=k) for k in range((dt.date(2024, 12, 31) - dt.date(2022, 1, 1)).days + 1)]


def extraer_chirps(estaciones: list[dict]) -> dict:
    """Serie diaria de CHIRPS en el pixel de cada estacion (central y media 3x3). Resumible: cache por dia."""
    cache = json.loads(PUNTOS.read_text(encoding="utf-8")) if PUNTOS.exists() else {"dias": {}}
    falta = [d for d in DIAS if d.isoformat() not in cache["dias"]]
    if falta:
        t0 = time.time()
        with rasterio.Env(GDAL_HTTP_TIMEOUT=120, GDAL_HTTP_MAX_RETRY=3, GDAL_HTTP_RETRY_DELAY=5, GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
                          CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", CPL_VSIL_CURL_CHUNK_SIZE="16777216", GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES", VSI_CACHE="FALSE"):
            for k, f in enumerate(falta):
                time.sleep(0.5)   # amortiguar el limite de solicitudes del servidor (HTTP 429)
                z, tr = cd.leer_dia(f)
                fila = {}
                for e in estaciones:
                    c, r = ~tr * (float(e["longitud"]), float(e["latitud"]))
                    r, c = int(math.floor(r)), int(math.floor(c))
                    if 0 <= r < z.shape[0] and 0 <= c < z.shape[1]:
                        v3 = z[max(0, r - 1):r + 2, max(0, c - 1):c + 2]
                        fila[e["codigo"]] = [None if np.isnan(z[r, c]) else round(float(z[r, c]), 2), None if np.isnan(v3).all() else round(float(np.nanmean(v3)), 2)]
                cache["dias"][f.isoformat()] = fila
                if (k + 1) % 100 == 0:
                    PUNTOS.write_text(json.dumps(cache), encoding="utf-8")
                    print(f"  CHIRPS {k + 1}/{len(falta)} dias ({time.time() - t0:.0f}s)", flush=True)
        PUNTOS.write_text(json.dumps(cache), encoding="utf-8")
    return cache["dias"]


def pares(codigo: str, h: str, chirps: dict, col: int) -> pd.DataFrame:
    g = json.loads((CACHE / "pluviometros" / f"{codigo}.json").read_text(encoding="utf-8"))["diario"][h]
    filas = []
    for dia, (suma, valido) in g.items():
        c = chirps.get(dia, {}).get(codigo)
        if valido and c and c[col] is not None:
            filas.append((dia, suma, c[col]))
    return pd.DataFrame(filas, columns=["dia", "pluv", "chirps"])


def cuantiles_lluviosos(x: np.ndarray) -> np.ndarray:
    return np.percentile(x[x >= UMBRAL_LLUVIA_MM], PERCENTILES) if (x >= UMBRAL_LLUVIA_MM).sum() >= 30 else np.full(len(PERCENTILES), np.nan)


def corregir(chirps: np.ndarray, factores: np.ndarray, ref_chirps: np.ndarray) -> np.ndarray:
    """Multiplica cada valor lluvioso de CHIRPS por el factor interpolado segun su percentil dentro de la distribucion lluviosa de CHIRPS de la estacion."""
    out = chirps.copy()
    lluv = chirps >= UMBRAL_LLUVIA_MM
    if lluv.sum() < 30:
        return out
    ref = np.sort(chirps[lluv])
    pct = np.searchsorted(ref, chirps[lluv], side="right") / len(ref) * 100
    out[lluv] = chirps[lluv] * np.interp(pct, PERCENTILES, factores)
    return out


def ic_mediana(v: np.ndarray):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    bs = [np.median(v[RNG.integers(0, len(v), len(v))]) for _ in range(N_BOOT)]
    return float(np.median(v)), [float(x) for x in np.percentile(bs, [2.5, 97.5])]


def main():
    sel = json.loads((AQUI / "pluviometros_seleccion.json").read_text(encoding="utf-8"))
    ests = [dict(e, region=r) for r, lst in sel.items() for e in lst]
    print(f"Estaciones aceptadas: {len(ests)} ({ {r: len(l) for r, l in sel.items()} })")
    chirps = extraer_chirps(ests)
    R = {"n_estaciones": len(ests), "por_region": {r: len(l) for r, l in sel.items()}}
    # alineacion horaria: mediana de Spearman diaria
    med = {}
    for h in ("0", "5"):
        rs = []
        for e in ests:
            p = pares(e["codigo"], h, chirps, 0)
            if len(p) >= 100:
                rs.append(spearmanr(p["pluv"], p["chirps"])[0])
        med[h] = float(np.nanmedian(rs))
    h = max(med, key=med.get)
    R["alineacion"] = {"mediana_spearman_por_desplazamiento_h": med, "elegida_h": int(h)}
    print(f"Alineacion horaria: mediana de Spearman {med} -> desplazamiento elegido {h} h")
    for col, nombre in ((0, "pixel central"), (1, "media 3x3")):
        print(f"\n== Sesgo antes de corregir ({nombre}) ==")
        filas = []
        for e in ests:
            p = pares(e["codigo"], h, chirps, col)
            if len(p) < 300:
                continue
            fila = {"codigo": e["codigo"], "region": e["region"], "n": len(p), "spearman": spearmanr(p["pluv"], p["chirps"])[0],
                    "razon_total": p["chirps"].sum() / max(p["pluv"].sum(), 1e-9),
                    "dias_lluvia_pluv": float((p["pluv"] >= UMBRAL_LLUVIA_MM).mean()), "dias_lluvia_chirps": float((p["chirps"] >= UMBRAL_LLUVIA_MM).mean())}
            qp, qc = cuantiles_lluviosos(p["pluv"].values), cuantiles_lluviosos(p["chirps"].values)
            for k, q in enumerate(PERCENTILES):
                fila[f"razon_p{q}"] = qc[k] / qp[k] if np.isfinite(qp[k]) and np.isfinite(qc[k]) else np.nan
            fila["razon_max"] = p["chirps"].max() / max(p["pluv"].max(), 1e-9)
            filas.append(fila)
        df = pd.DataFrame(filas)
        R[f"sesgo|{nombre}"] = {}
        for reg, g in list(df.groupby("region")) + [("TODAS", df)]:
            r = {"n_estaciones": len(g)}
            for v in ("spearman", "razon_total", "razon_p50", "razon_p90", "razon_p99", "razon_max"):
                m, ic = ic_mediana(g[v].values)
                r[v] = {"mediana": m, "ic95": ic}
            r["dias_lluvia_pluv"], r["dias_lluvia_chirps"] = float(g["dias_lluvia_pluv"].median()), float(g["dias_lluvia_chirps"].median())
            R[f"sesgo|{nombre}"][reg] = r
            print(f"  {reg:<10} n={len(g):>2}  rho={r['spearman']['mediana']:.2f}  razon total={r['razon_total']['mediana']:.2f} [{r['razon_total']['ic95'][0]:.2f},{r['razon_total']['ic95'][1]:.2f}]"
                  f"  p50={r['razon_p50']['mediana']:.2f}  p90={r['razon_p90']['mediana']:.2f}  p99={r['razon_p99']['mediana']:.2f} [{r['razon_p99']['ic95'][0]:.2f},{r['razon_p99']['ic95'][1]:.2f}]"
                  f"  dias lluvia: pluv {r['dias_lluvia_pluv']:.2f} / CHIRPS {r['dias_lluvia_chirps']:.2f}")
    # correccion por cuantiles, dejando una estacion fuera, dentro de la region
    print("\n== Correccion por cuantiles (dejando una estacion fuera; factores de la misma region) ==")
    datos = {}
    for e in ests:
        p = pares(e["codigo"], h, chirps, 0)
        if len(p) >= 300:
            datos[e["codigo"]] = (e["region"], p)
    fact = {c: cuantiles_lluviosos(p["pluv"].values) / cuantiles_lluviosos(p["chirps"].values) for c, (_, p) in datos.items()}
    res = []
    for c, (reg, p) in datos.items():
        otros = [fact[o] for o, (r2, _) in datos.items() if o != c and r2 == reg and np.all(np.isfinite(fact[o]))]
        if len(otros) < 3 or not np.all(np.isfinite(fact[c])):
            continue
        f = np.median(np.array(otros), axis=0)
        corr = corregir(p["chirps"].values, f, p["chirps"].values)
        qp, qr, qc = cuantiles_lluviosos(p["pluv"].values), cuantiles_lluviosos(p["chirps"].values), cuantiles_lluviosos(corr)
        fila = {"codigo": c, "region": reg, "razon_total_antes": p["chirps"].sum() / p["pluv"].sum(), "razon_total_despues": corr.sum() / p["pluv"].sum()}
        for k, q in enumerate(PERCENTILES):
            fila[f"err_antes_p{q}"], fila[f"err_despues_p{q}"] = abs(math.log(qr[k] / qp[k])), abs(math.log(qc[k] / qp[k]))
        fila["err_antes_total"], fila["err_despues_total"] = abs(math.log(fila["razon_total_antes"])), abs(math.log(fila["razon_total_despues"]))
        res.append(fila)
    rv = pd.DataFrame(res)
    R["correccion"] = {"n_estaciones": len(rv)}
    print(f"  estaciones evaluadas: {len(rv)}")
    for q in list(PERCENTILES) + ["total"]:
        a, b = rv[f"err_antes_p{q}" if q != "total" else "err_antes_total"], rv[f"err_despues_p{q}" if q != "total" else "err_despues_total"]
        m, ic = ic_mediana((b - a).values)
        R["correccion"][f"p{q}" if q != "total" else "total"] = {"mediana_err_antes": float(a.median()), "mediana_err_despues": float(b.median()), "dif_mediana": m, "ic95": ic}
        print(f"  {('p' + str(q)) if q != 'total' else 'total':<6} |ln razon|: antes {a.median():.2f} -> despues {b.median():.2f}   dif {m:+.3f} [{ic[0]:+.3f}, {ic[1]:+.3f}]")
    ok = R["correccion"]["p99"]["ic95"][1] < 0
    R["primario_cumple"] = bool(ok)
    print(f"\n>>> Criterio primario (p99 mejora, IC95 por estaciones que excluye 0): {'SE CUMPLE' if ok else 'NO se cumple'}")
    R["factores_por_region"] = {}
    for reg in sorted({r for r, _ in datos.values()}):
        f = np.array([fact[c] for c, (r2, _) in datos.items() if r2 == reg and np.all(np.isfinite(fact[c]))])
        if len(f):
            R["factores_por_region"][reg] = {"n": int(len(f)), "mediana": [float(x) for x in np.median(f, axis=0)], "percentiles": list(PERCENTILES)}
            print(f"  factores {reg:<10} (n={len(f)}): " + "  ".join(f"p{q}={v:.2f}" for q, v in zip(PERCENTILES, np.median(f, axis=0))))
    # efecto sobre la Etapa A
    print("\n== Efecto sobre la regionalizacion de la Etapa A (escenario) ==")
    import regionalizacion_validacion as rg
    d = rg.cargar()
    razon = {reg: R["sesgo|pixel central"][reg]["razon_total"]["mediana"] for reg in sel if reg in R["sesgo|pixel central"]}
    base = rg.resumen(rg.validar(d, "q10"))
    d2 = d.copy()
    d2["lluvia_media_mm"] = d2.apply(lambda r: r["lluvia_media_mm"] / razon.get(r["region"], 1.0), axis=1)
    d2["lP"] = np.log(d2["lluvia_media_mm"])
    corr = rg.resumen(rg.validar(d2, "q10"))
    R["etapa_a"] = {"razon_total_por_region": razon, "sin_correccion": {m: base[m]["factor_tipico"] for m in ("B1", "M1", "M2", "M3")},
                    "con_correccion": {m: corr[m]["factor_tipico"] for m in ("B1", "M1", "M2", "M3")}}
    print("  razon CHIRPS/pluviometro (total) por region:", {k: round(v, 2) for k, v in razon.items()})
    print("  factor de error tipico a T=10, sin -> con correccion:", {m: f"{base[m]['factor_tipico']:.2f} -> {corr[m]['factor_tipico']:.2f}" for m in ("B1", "M1", "M2", "M3")})
    (AQUI / "sesgo_chirps_resultados.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
