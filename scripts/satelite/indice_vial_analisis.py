"""Indice geomorfometrico vial: construccion y validacion municipal. Protocolo: PROTOCOLO_INDICE_VIAL_GEOMORFOMETRICO.md
Entrada: _cache/ivg_<depto>.pkl (indice_vial_extraer.py). Salida: indice_vial_resultados.json"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import contraste_sgc_vs_ungrd as cs  # noqa: E402

CACHE = AQUI / "_cache"
KM_MIN = 5.0
AMBITOS = {"Caribe": ["08", "13", "20", "23", "44", "47", "70"], "Andes": ["05", "25", "68"]}


def cargar(deptos: list[str]) -> pd.DataFrame:
    fs = [pd.read_pickle(CACHE / f"ivg_{d}.pkl") for d in deptos if (CACHE / f"ivg_{d}.pkl").exists()]
    d = pd.concat(fs, ignore_index=True)
    return d[np.isfinite(d["twi_p90"]) & (d["km"] > 0)].reset_index(drop=True)


def pr(x) -> np.ndarray:
    return (rankdata(x, method="average") - 1) / (len(x) - 1)


def indices(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["I1"] = pr(d["C15"])
    d["I3"] = (pr(d["C15"]) + pr(d["twi_p90"]) + pr(d["D100"])) / 3
    d["I2"] = (pr(d["C15"]) + pr(d["D100"])) / 2
    d["I3_C10"] = (pr(d["C10"]) + pr(d["twi_p90"]) + pr(d["D100"])) / 3
    d["I3_C25"] = (pr(d["C25"]) + pr(d["twi_p90"]) + pr(d["D100"])) / 3
    d["I3_D50"] = (pr(d["C15"]) + pr(d["twi_p90"]) + pr(d["D50"])) / 3
    d["I3_D200"] = (pr(d["C15"]) + pr(d["twi_p90"]) + pr(d["D200"])) / 3
    d["I3_p90"] = (pr(d["pend_p90"]) + pr(d["twi_p90"]) + pr(d["D100"])) / 3
    d["I1_p90"] = pr(d["pend_p90"])
    return d


def municipal(d: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    g = d.groupby("codigo")
    out = pd.DataFrame({"km_terciaria": g["km"].sum()})
    for c in cols:
        out[c] = g.apply(lambda x: np.average(x[c], weights=x["km"]), include_groups=False)
    return out[out["km_terciaria"] >= KM_MIN].reset_index()


def panel_eventos() -> pd.DataFrame:
    p = cs.preparar()
    p["n_ev"] = p["n_mm"] + p["n_inund"]
    p["y1"] = (p["n_ev"] >= 1).astype(int)
    p["y2"] = p["n_ev"] / p["area_km2"] * 100
    p["y1_mm"] = (p["n_mm"] >= 1).astype(int)
    p["y1_in"] = (p["n_inund"] >= 1).astype(int)
    return p


def validar(m: pd.DataFrame, cols_sens: list[str]) -> dict:
    out = {"n_municipios": int(len(m)), "n_deptos": int(m["depto2"].nunique()), "n_con_evento": int(m["y1"].sum())}
    if m["y1"].nunique() < 2 or len(m) < 15:
        return {**out, "nota": "muestra insuficiente"}
    bl = m["depto2"].values
    z = [m["log_pob"].values, m["P_A"].values]
    y1, y2 = m["y1"].values, m["y2"].values

    def ic(f):
        v = f(np.arange(len(m)))
        return [float(v)] + cs.boot(f, bl)

    for c in ["I3", "I1"] + cols_sens:
        x = m[c].values
        out[f"auc_{c}"] = ic(lambda i, x=x: cs.auc(x[i], y1[i]))
        out[f"rho_{c}"] = ic(lambda i, x=x: spearmanr(x[i], y2[i])[0])
        out[f"parcial_{c}"] = ic(lambda i, x=x: cs.parcial(x[i], y2[i], [q[i] for q in z]))
    a, b = m["I3"].values, m["I1"].values
    out["V2_dAUC_I3_menos_I1"] = ic(lambda i: cs.auc(a[i], y1[i]) - cs.auc(b[i], y1[i]))
    out["V1_cumple"] = bool(out["parcial_I3"][1] > 0)
    out["V2_cumple"] = bool(out["V2_dAUC_I3_menos_I1"][1] > 0)
    s = m["pend_p90"].values
    out["auc_pendiente_municipal_p90"] = float(cs.auc(s, y1))
    out["dAUC_I3_menos_pendiente_municipal"] = ic(lambda i: cs.auc(a[i], y1[i]) - cs.auc(s[i], y1[i]))
    out["auc_I3_solo_mm"] = float(cs.auc(a, m["y1_mm"].values)) if m["y1_mm"].nunique() > 1 else None
    out["auc_I3_solo_inundacion"] = float(cs.auc(a, m["y1_in"].values)) if m["y1_in"].nunique() > 1 else None
    return out


def main() -> None:
    P = panel_eventos()
    R = {}
    sens = ["I2", "I3_C10", "I3_C25", "I3_D50", "I3_D200", "I3_p90", "I1_p90"]
    for nombre, deptos in AMBITOS.items():
        d = cargar(deptos)
        if d.empty:
            continue
        d = indices(d)
        r = {"deptos_con_datos": sorted(d["depto"].unique()), "tramos": int(len(d)), "km": float(d["km"].sum()),
             "por_tipo": d["highway"].value_counts().to_dict(),
             "redundancia_spearman": {"C15_vs_TWI": float(spearmanr(d["C15"], d["twi_p90"])[0]), "C15_vs_D100": float(spearmanr(d["C15"], d["D100"])[0]),
                                      "TWI_vs_D100": float(spearmanr(d["twi_p90"], d["D100"])[0])},
             "frac_tramos_C15_cero": float((d["C15"] == 0).mean())}
        cols = ["I3", "I1"] + sens
        m = municipal(d, cols).merge(P, on="codigo", how="inner")
        r["validacion"] = validar(m, sens)
        top_m = m.sort_values("I3", ascending=False).head(20)
        r["top20_municipios"] = [{"codigo": x.codigo, "I3": round(x.I3, 3), "km": round(x.km_terciaria, 1)} for x in top_m.itertuples()]
        top_t = d.sort_values("I3", ascending=False).head(20)
        r["top20_tramos"] = [{"way_id": int(x.way_id), "codigo": x.codigo, "highway": x.highway, "km": round(x.km, 2), "I3": round(x.I3, 3)} for x in top_t.itertuples()]
        R[nombre] = r
    (AQUI / "indice_vial_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: {a: b for a, b in v.items() if not a.startswith("top20")} for k, v in R.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
