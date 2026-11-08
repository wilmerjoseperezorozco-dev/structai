"""F1: cribado de potencial hidroeléctrico a filo de agua sobre los perfiles longitudinales. Protocolo: PROTOCOLOS_PERFILES_LONGITUDINALES.md (F1 + Enmienda 1).
Uso: python scripts/hidro/f1_filo_de_agua_analisis.py
Salida: f1_tramos.csv, f1_resultados.json"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cuencas_estaciones as ce  # noqa: E402

PISO_S = 0.0005
MIN_MESES = 120
LONGITUDES_KM = (1.0, 2.0, 5.0)
LONG_PRINCIPAL = 2.0
KS = (1.0, 0.8)
RATIO_PRIMARIO, RATIO_SENSIBILIDAD = 0.25, 0.05
P_CANDIDATO_KW = 100.0
G = 9.81
REPLICAS, SEMILLA = 2000, 20261108
CARIBE = {"08", "13", "20", "23", "44", "47", "70"}
PACIFICO = {"27"}
ORINOQUIA_AMAZONIA = {"50", "85", "81", "99", "95", "94", "97", "18", "86", "91"}


def region(d: str) -> str:
    return "Caribe" if d in CARIBE else "Pacifico" if d in PACIFICO else "Orinoquia_Amazonia" if d in ORINOQUIA_AMAZONIA else "Andina"


def caudales() -> pd.DataFrame:
    d = pd.read_pickle(AQUI / "_cache" / "caudal_historico.pkl").dropna(subset=["caudal_m3s"])
    d = d[d["caudal_m3s"] > 0]
    g = d.groupby("codigo_estacion")["caudal_m3s"]
    out = pd.DataFrame({"n_meses": g.size(), "q_medio": g.mean(), "q_p10": g.quantile(0.10), "q_p30": g.quantile(0.30), "q_p50": g.quantile(0.50)})
    out.index = out.index.astype(str).str.zfill(10)
    return out


def tramos(L: np.ndarray, Z: np.ndarray, A: np.ndarray, long_m: float) -> list[dict]:
    """Recorre el perfil desde la estación (aguas abajo) hacia aguas arriba en tramos sin traslape; descarta el último incompleto."""
    L, Z, A = L[::-1], Z[::-1], A[::-1]            # índice 0 = estación
    dz_cel = np.maximum(Z[1:] - Z[:-1], 0.0)       # cota aguas arriba menos aguas abajo, celda a celda
    piso_cel = (dz_cel / L) < PISO_S
    cum = np.concatenate([[0.0], np.cumsum(L)])    # distancia desde la estación a cada nodo
    A_est = A[0]
    out, i0, k = [], 0, 1
    while True:
        i1 = int(np.searchsorted(cum, k * long_m))
        if i1 >= len(cum):
            break
        if i1 > i0:
            lreal = cum[i1] - cum[i0]
            h = max(Z[i1] - Z[i0], 0.0)
            out.append({"i0": i0, "i1": i1, "L_real_m": lreal, "H_m": h, "S": h / lreal, "frac_piso": float(piso_cel[i0:i1].mean()),
                        "ratio_area": float(np.mean([A[i0], A[i1]]) / A_est)})
        i0, k = i1, k + 1
    return out


def main():
    q = caudales()
    est = ce.estaciones().set_index("codigo")
    filas, sin_q, pocas = [], 0, 0
    perfiles = {}
    for f in sorted((AQUI / "_cache" / "perfiles").glob("perfiles_*.pkl")):
        with open(f, "rb") as fh:
            perfiles.update({k: v | {"depto": f.stem.split("_")[1]} for k, v in pickle.load(fh).items() if "L" in v})
    for cod, p in perfiles.items():
        if cod not in q.index:
            sin_q += 1
            continue
        if q.loc[cod, "n_meses"] < MIN_MESES:
            pocas += 1
            continue
        for long_km in LONGITUDES_KM:
            for t in tramos(p["L"], p["Z"], p["A_km2"], long_km * 1000):
                filas.append({"codigo": cod, "depto": p["depto"], "region": region(p["depto"]), "lat": est.loc[cod, "lat"], "lon": est.loc[cod, "lon"],
                              "long_km": long_km, **{k: t[k] for k in ("L_real_m", "H_m", "S", "frac_piso", "ratio_area")},
                              **{c: q.loc[cod, c] for c in ("q_medio", "q_p10", "q_p30", "q_p50")}})
    df = pd.DataFrame(filas)
    df["utilizable"] = (df["S"] > PISO_S) & (df["frac_piso"] < 0.5)
    for k in KS:
        esc = df["ratio_area"].clip(upper=1.0) ** k
        df[f"P_mediana_k{k}"] = G * df["q_p50"] * esc * df["H_m"]
        df[f"P_p10_k{k}"] = G * df["q_p10"] * esc * df["H_m"]
        df[f"P_medio_k{k}"] = G * df["q_medio"] * esc * df["H_m"]
    df["en_rango"] = df["ratio_area"] >= RATIO_PRIMARIO
    df["en_rango_amplio"] = df["ratio_area"] >= RATIO_SENSIBILIDAD
    df["candidato"] = df["utilizable"] & df["en_rango"] & (df["P_p10_k1.0"] >= P_CANDIDATO_KW) & (df["P_p10_k0.8"] >= P_CANDIDATO_KW)
    df["candidato_amplio"] = df["utilizable"] & df["en_rango_amplio"] & (df["P_p10_k1.0"] >= P_CANDIDATO_KW) & (df["P_p10_k0.8"] >= P_CANDIDATO_KW)
    df.to_csv(AQUI / "f1_tramos.csv", index=False)

    rng = np.random.default_rng(SEMILLA)
    res = {"perfiles_total": len(perfiles), "excluidos_sin_caudal": sin_q, "excluidos_menos_de_120_meses": pocas,
           "cuencas_analizadas": int(df["codigo"].nunique()), "por_longitud": {}}
    for long_km in LONGITUDES_KM:
        d = df[df["long_km"] == long_km]
        por_c = d.groupby("codigo").agg(region=("region", "first"), bloque=("lat", lambda s: 0), lat=("lat", "first"), lon=("lon", "first"),
                                        cand=("candidato", "any"), cand_amplio=("candidato_amplio", "any"),
                                        pmax=("P_p10_k1.0", lambda s: float(s[d.loc[s.index, "utilizable"] & d.loc[s.index, "en_rango"]].max()) if (d.loc[s.index, "utilizable"] & d.loc[s.index, "en_rango"]).any() else np.nan),
                                        n_tr=("S", "size"), n_ut=("utilizable", "sum"))
        bloques = (np.floor(por_c["lat"]).astype(int).astype(str) + "_" + np.floor(por_c["lon"]).astype(int).astype(str)).to_numpy()
        ub = np.unique(bloques)
        idx = {b: np.where(bloques == b)[0] for b in ub}
        cand, pm = por_c["cand"].to_numpy(float), por_c["pmax"].to_numpy(float)
        bs_c, bs_p = [], []
        for _ in range(REPLICAS):
            ii = np.concatenate([idx[b] for b in rng.choice(ub, size=len(ub), replace=True)])
            bs_c.append(cand[ii].mean())
            bs_p.append(np.nanmedian(pm[ii]))
        ci = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]  # noqa: E731
        res["por_longitud"][str(long_km)] = {
            "tramos": int(len(d)), "tramos_utilizables": int(d["utilizable"].sum()), "frac_utilizables": float(d["utilizable"].mean()),
            "cuencas_con_algun_tramo_utilizable_en_rango": int(por_c["pmax"].notna().sum()),
            "frac_cuencas_con_candidato": float(cand.mean()), "ic95_frac_cuencas_con_candidato": ci(bs_c),
            "n_tramos_candidatos": int(d["candidato"].sum()), "n_tramos_candidatos_rango_amplio": int(d["candidato_amplio"].sum()),
            "mediana_Pmax_p10_por_cuenca_kW": float(np.nanmedian(pm)), "ic95_mediana_Pmax": ci(bs_p),
            "por_region": {r: {"cuencas": int((por_c["region"] == r).sum()), "frac_con_candidato": float(por_c.loc[por_c["region"] == r, "cand"].mean()),
                               "mediana_Pmax_kW": float(np.nanmedian(por_c.loc[por_c["region"] == r, "pmax"])) if por_c.loc[por_c["region"] == r, "pmax"].notna().any() else None}
                           for r in sorted(por_c["region"].unique())},
        }
    top = df[(df["long_km"] == LONG_PRINCIPAL) & df["candidato"]].sort_values("P_p10_k1.0", ascending=False).head(10)
    res["top10_2km"] = top[["codigo", "depto", "H_m", "S", "frac_piso", "ratio_area", "q_p10", "q_medio", "P_p10_k1.0", "P_medio_k1.0"]].round(4).to_dict("records")
    (AQUI / "f1_resultados.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "top10_2km"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
