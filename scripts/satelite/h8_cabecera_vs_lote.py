"""H8 (#273): ¿cuánto pierde la alarma de relieve de H2b si /sitio no conoce el lote?

Protocolo: PROTOCOLO_ANALISIS.md §33 (fijado antes de cruzar las ubicaciones alternativas con el nivel medido).
Regla fija (H2): relieve local S (cota DEM − mínima a ≤ 1 km) ≤ 6,5 m -> alarma de nivel freático somero.
Ubicaciones donde se evalúa S para cada pozo/aljibe medido:
  lote      coordenada del punto (referencia; es lo validado en H2/H2b)
  r001      coordenada redondeada a 0,01° (lo máximo que guarda /sitio por la regla de privacidad)
  cabecera  coordenada DIVIPOLA del municipio del punto (lo que /sitio sabe si el usuario solo da el municipio)
Uso:
  python -I h8_cabecera_vs_lote.py --conteo   # cobertura y concordancia de alarmas; no usa niveles
  python -I h8_cabecera_vs_lote.py            # análisis -> h8_cabecera_resultados.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import h2_saturacion_freatica as h2  # noqa: E402
import h3_socavacion_puentes as h3  # noqa: E402

SALIDA = AQUI / "h8_cabecera_resultados.json"
UMBRAL_S_M = 6.5
SOMERO_M = {"llanura": 2.0, "quindio": 5.0}
DELTA_MAX = 0.05
h3.RNG = np.random.default_rng(2788)


def muestra() -> pd.DataFrame:
    h2.NIVEL["casanare"] = lambda a: h2._num(a.get("PROFUNDI_4"))
    h2.NIVEL["quindio"] = lambda a: h2._num(a.get("Profundi_4"))
    h2.CAMPO_TIPO["quindio"] = "Tipo_de_pu"
    p = h2.puntos(incluir_sensibilidad=False)
    p = h2.predictores(p)
    p = p[np.isfinite(p["nivel_m"]) & np.isfinite(p["S"]) & p["codigo_municipio"].notna()].reset_index(drop=True)
    dem = h2.DEM()

    def S(lat, lon):
        z, zmin = dem.ventana(lat, lon, h2.RADIO_RELIEVE_KM)
        return z - zmin

    p["S_r001"] = [S(round(la, 2), round(lo, 2)) for la, lo in zip(p["lat"], p["lon"])]
    cent = pd.DataFrame(h3.insumos()["centroides"]).drop_duplicates("codigo")
    cent["codigo"] = cent["codigo"].astype(str).str.zfill(5)
    cent = cent.set_index("codigo")
    la_c = p["codigo_municipio"].map(cent["lat"]).astype(float).values
    lo_c = p["codigo_municipio"].map(cent["lon"]).astype(float).values
    Sc = {c: S(cent.at[c, "lat"], cent.at[c, "lon"]) for c in p["codigo_municipio"].unique() if c in cent.index}
    p["S_cabecera"] = p["codigo_municipio"].map(Sc).astype(float)
    p["km_cabecera"] = h3._km(p["lat"].values, p["lon"].values, la_c, lo_c)
    p["zona"] = np.where(p["capa"] == "quindio", "quindio", "llanura")
    return p


def auc_ic(S, y, b):
    return {"valor": float(h3.auc(-S, y)), "ic95": h3.boot(lambda ix: h3.auc(-S[ix], y[ix]), b)}


def regla(S, y):
    a = S <= UMBRAL_S_M
    return {"sensibilidad": float(a[y == 1].mean()), "especificidad": float((~a[y == 0]).mean()),
            "vpp": float(y[a].mean()) if a.any() else None, "fraccion_alarma": float(a.mean())}


def analizar(q: pd.DataFrame) -> dict:
    y = (q["nivel_m"] <= SOMERO_M[q["zona"].iloc[0]]).astype(int).values
    b = q["bloque"].values
    r = {"n": len(q), "n_municipios": int(q["codigo_municipio"].nunique()), "n_bloques": int(len(set(b))),
         "prevalencia": float(y.mean())}
    if not 0 < y.sum() < len(y):
        return r
    for k in ("S", "S_r001", "S_cabecera"):
        r[k] = {"auc": auc_ic(q[k].values, y, b), "regla": regla(q[k].values, y)}
    for k in ("S_r001", "S_cabecera"):
        r[f"delta_auc_lote_menos_{k}"] = {
            "valor": r["S"]["auc"]["valor"] - r[k]["auc"]["valor"],
            "ic95": h3.boot(lambda ix, k=k: h3.auc(-q["S"].values[ix], y[ix]) - h3.auc(-q[k].values[ix], y[ix]), b)}
    lo, hi = r["delta_auc_lote_menos_S_r001"]["ic95"]
    r["C1_r001"] = "EQUIVALENTE" if hi < DELTA_MAX else ("PIERDE" if lo > 0 else "NO CONCLUYENTE")
    lo, hi = r["delta_auc_lote_menos_S_cabecera"]["ic95"]
    a_lo = r["S_cabecera"]["auc"]["ic95"][0]
    r["C2_cabecera"] = ("BASTA" if hi < DELTA_MAX else
                        "NO BASTA" if (lo > DELTA_MAX or r["S_cabecera"]["auc"]["ic95"][1] < 0.60) else
                        "NO CONCLUYENTE")
    r["auc_cabecera_ic_inferior"] = a_lo
    cerca = q["km_cabecera"].values <= 5
    r["por_distancia_cabecera"] = {
        g: {"n": int(m.sum()), "auc_lote": float(h3.auc(-q["S"].values[m], y[m])),
            "auc_cabecera": float(h3.auc(-q["S_cabecera"].values[m], y[m]))}
        for g, m in (("<=5km", cerca), (">5km", ~cerca)) if 0 < y[m].sum() < m.sum()}
    return r


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = muestra()
    ok = p[np.isfinite(p["S_r001"]) & np.isfinite(p["S_cabecera"])]
    if "--conteo" in sys.argv:
        print("puntos con nivel y S en el lote:", len(p), "| con S en las 3 ubicaciones:", len(ok))
        print("por capa:", ok["capa"].value_counts().to_dict(), "| municipios:", ok["codigo_municipio"].nunique())
        print("sin S en cabecera (cabecera fuera de las teselas DEM):",
              int(p["S_cabecera"].isna().sum()), "puntos")
        print("km a la cabecera p10/p50/p90:", np.percentile(ok["km_cabecera"], [10, 50, 90]).round(1))
        for z, g in ok.groupby("zona"):
            a = g["S"] <= UMBRAL_S_M
            print(z, "n", len(g), "| alarma lote", round(a.mean(), 2),
                  "| concordancia lote-r001", round(((g["S_r001"] <= UMBRAL_S_M) == a).mean(), 2),
                  "| concordancia lote-cabecera", round(((g["S_cabecera"] <= UMBRAL_S_M) == a).mean(), 2))
        return
    out = {"protocolo": "PROTOCOLO_ANALISIS.md §33", "regla": f"S(1 km) <= {UMBRAL_S_M} m",
           "excluidos_sin_S_cabecera": int(len(p) - len(ok))}
    for z, g in ok.groupby("zona"):
        out[z] = analizar(g.reset_index(drop=True))
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
