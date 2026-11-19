"""H2c (#273): definición objetiva de "llanura" para la alarma de relieve de /sitio.

Protocolo: PROTOCOLO_ANALISIS.md §34 (fijado antes de cruzar la clase de terreno con el nivel medido).
Definición (fijada de la literatura, sin ajustar con estos datos): clases de relieve de Hammond (1964), con
vecindad circular de radio 5 km alrededor del lote (Hammond usó una ventana de ~9,6 km de lado):
  llanura  si  > 80 % de la vecindad tiene pendiente < 8 %  Y  relieve local (máx − mín) < 90 m
  (Hammond: "flat plains" relieve 0-30 m y "smooth plains" 30-90 m, ambas con > 80 % de pendiente suave).
DEM: Copernicus GLO-90. Pendiente por diferencias centrales en la malla de ~90 m.
Uso:
  python -I h2c_llanura_objetiva.py --conteo   # clase de terreno por capa; no usa niveles
  python -I h2c_llanura_objetiva.py            # análisis -> h2c_llanura_resultados.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import h2_saturacion_freatica as h2  # noqa: E402
import h3_socavacion_puentes as h3  # noqa: E402

SALIDA = AQUI / "h2c_llanura_resultados.json"
RADIO_KM, PEND_SUAVE, FRAC_SUAVE, RELIEVE_MAX_M = 5.0, 0.08, 0.80, 90.0
UMBRAL_S_M = 6.5
SOMERO_M = {"quindio": 5.0}          # resto: 2 m (umbrales de H2/H2b)
h3.RNG = np.random.default_rng(2734)


def hammond(dem: h2.DEM, lat: float, lon: float):
    src = dem._tesela(lat, lon)
    if src is None:
        return np.nan, np.nan
    r, c = src.index(lon, lat)
    dy = RADIO_KM / 111.32 / abs(src.res[1])
    dx = RADIO_KM / (111.32 * math.cos(math.radians(lat))) / abs(src.res[0])
    if r - dy < 1 or c - dx < 1 or r + dy > src.height - 2 or c + dx > src.width - 2:
        return np.nan, np.nan            # vecindad cortada por el borde de la tesela: se excluye (declarado)
    r0, r1, c0, c1 = int(r - dy) - 1, int(r + dy) + 2, int(c - dx) - 1, int(c + dx) + 2
    a = src.read(1, window=((r0, r1), (c0, c1))).astype(float)
    a[a < -100] = np.nan
    my = abs(src.res[1]) * 111320.0
    mx = abs(src.res[0]) * 111320.0 * math.cos(math.radians(lat))
    gy, gx = np.gradient(a, my, mx)
    pend = np.hypot(gx, gy)
    yy, xx = np.mgrid[r0:r1, c0:c1]
    dentro = ((yy - r) / dy) ** 2 + ((xx - c) / dx) ** 2 <= 1
    v = dentro & np.isfinite(pend)
    return float((pend[v] < PEND_SUAVE).mean()), float(np.nanmax(a[dentro]) - np.nanmin(a[dentro]))


def muestra():
    h2.NIVEL["casanare"] = lambda a: h2._num(a.get("PROFUNDI_4"))
    h2.NIVEL["quindio"] = lambda a: h2._num(a.get("Profundi_4"))
    h2.CAMPO_TIPO["quindio"] = "Tipo_de_pu"
    p = h2.predictores(h2.puntos(incluir_sensibilidad=False))
    p = p[np.isfinite(p["nivel_m"]) & np.isfinite(p["S"])].reset_index(drop=True)
    dem = h2.DEM()
    fr = [hammond(dem, la, lo) for la, lo in zip(p["lat"], p["lon"])]
    p["frac_suave"], p["relieve_5km"] = [x[0] for x in fr], [x[1] for x in fr]
    p = p[np.isfinite(p["frac_suave"])].reset_index(drop=True)
    p["llanura"] = (p["frac_suave"] > FRAC_SUAVE) & (p["relieve_5km"] < RELIEVE_MAX_M)
    p["y"] = (p["nivel_m"] <= p["capa"].map(SOMERO_M).fillna(2.0)).astype(int)
    return p


def bloque_auc(q):
    S, y, b = q["S"].values, q["y"].values, q["bloque"].values
    if not 0 < y.sum() < len(y):
        return None
    a = S <= UMBRAL_S_M
    return {"n": len(q), "n_bloques": int(len(set(b))), "prevalencia": float(y.mean()),
            "auc": float(h3.auc(-S, y)), "ic95": h3.boot(lambda ix: h3.auc(-S[ix], y[ix]), b),
            "sensibilidad": float(a[y == 1].mean()), "especificidad": float((~a[y == 0]).mean()),
            "vpp": float(y[a].mean()) if a.any() else None, "fraccion_alarma": float(a.mean())}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = muestra()
    if "--conteo" in sys.argv:
        print("puntos con vecindad completa:", len(p))
        for c, g in p.groupby("capa"):
            print(f"{c:9s} n {len(g):4d} | llanura {g['llanura'].mean():.2f} | frac_suave p50 "
                  f"{g['frac_suave'].median():.2f} | relieve 5 km p10/p50/p90 "
                  f"{np.percentile(g['relieve_5km'], [10, 50, 90]).round(0)}")
        print("total llanura:", int(p["llanura"].sum()), "| no llanura:", int((~p["llanura"]).sum()))
        return
    out = {"protocolo": "PROTOCOLO_ANALISIS.md §34",
           "definicion": f"Hammond: frac(pendiente<{PEND_SUAVE:.0%})>{FRAC_SUAVE} y relieve {RADIO_KM:.0f} km<{RELIEVE_MAX_M:.0f} m",
           "dentro_llanura": bloque_auc(p[p["llanura"]]), "fuera_llanura": bloque_auc(p[~p["llanura"]])}
    d = p["llanura"].values
    S, y, b = p["S"].values, p["y"].values, p["bloque"].values

    def dif(ix):
        di, Si, yi = d[ix], S[ix], y[ix]
        if not (0 < yi[di].sum() < di.sum() and 0 < yi[~di].sum() < (~di).sum()):
            return np.nan
        return h3.auc(-Si[di], yi[di]) - h3.auc(-Si[~di], yi[~di])
    if out["dentro_llanura"] and out["fuera_llanura"]:
        out["delta_auc_dentro_menos_fuera"] = {"valor": dif(np.arange(len(p))), "ic95": h3.boot(dif, b)}
    di = out["dentro_llanura"]
    out["C1_dentro"] = ("VALIDA" if di and di["ic95"][0] > 0.60 else
                        "NO VALIDA" if di and di["ic95"][1] < 0.55 else "NO CONCLUYENTE")
    dd = out.get("delta_auc_dentro_menos_fuera")
    out["C2_compuerta"] = ("UTIL" if dd and dd["ic95"][0] > 0 else
                           "NO CONCLUYENTE" if dd else "SIN CASOS FUERA")
    out["por_capa"] = {c: {"n": len(g), "frac_llanura": float(g["llanura"].mean()),
                           "dentro": bloque_auc(g[g["llanura"]]) if g["llanura"].sum() >= 30 else None,
                           "fuera": bloque_auc(g[~g["llanura"]]) if (~g["llanura"]).sum() >= 30 else None}
                       for c, g in p.groupby("capa")}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
