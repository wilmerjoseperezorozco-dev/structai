"""R1 de V1-Perú con efectos fijos de departamento (PROTOCOLO_V1_PERU.md §6, R1) y su análogo para Y2. EXPLORATORIO.

Modelos cuasi-Poisson (GLM Poisson con errores robustos) con efectos fijos de departamento:
  Y1: viviendas dañadas, desfase log(población).   Y2: km de carretera dañada, desfase log(área).
Covariables: E (por +0,10), T, log(área) [solo Y1; en Y2 es el desfase], elevación media (por 1.000 m), pendiente media (grados).
No se incluyen lluvia p95, % urbano ni NBI (no se obtuvieron). Se reporta la razón de tasas (RR) por +0,10 de E.
IC 95 %: (a) errores robustos agrupados por departamento (pocos grupos: poco confiable) y (b) remuestreo de departamentos
(2.000 réplicas), percentiles. Además R1b: correlación parcial de Spearman con efectos fijos de departamento
(rangos residualizados dentro de departamento), el análogo directo de C-2.

Uso: python -I peru_r1_efectos_fijos.py <sinpad.csv> <limites.xlsx> <pob.xlsx> <hand.json> <vias.json> <relieve.json> <salida.json>
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import peru_exploratorias_sierra as ex  # noqa: E402

N_BOOT = 2000
SEMILLA = 20261108
PASO_E = 0.10
warnings.filterwarnings("ignore")


def matriz(d: pd.DataFrame, resultado: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    x = pd.DataFrame({"E10": d.E / PASO_E, "T": d["T"], "elev_km": d.elev / 1000.0, "pend": d.pend})
    if resultado == "Y1":
        x["larea"] = d.larea
        y, off = d.viv.to_numpy(), np.log(d.pob).to_numpy()
    else:
        y, off = d.km_carr.to_numpy(), np.log(d.area).to_numpy()
    fe = pd.get_dummies(d.depto, prefix="d", drop_first=True, dtype=float)
    return pd.concat([x, fe], axis=1), y, off


def ajustar(x: pd.DataFrame, y: np.ndarray, off: np.ndarray, grupos=None):
    m = sm.GLM(y, sm.add_constant(x), family=sm.families.Poisson(), offset=off)
    return m.fit(cov_type="cluster", cov_kwds={"groups": grupos}) if grupos is not None else m.fit()


def rr_bootstrap(d: pd.DataFrame, resultado: str, rng: np.random.Generator) -> list[float]:
    idx = d.groupby("depto").indices
    claves = list(idx)
    out = []
    for _ in range(N_BOOT):
        partes = []
        for n, s in enumerate(rng.choice(len(claves), len(claves), replace=True)):
            g = d.iloc[idx[claves[s]]].copy()
            g["depto"] = f"{n:03d}"  # cada réplica de un departamento es un grupo distinto
            partes.append(g)
        b = pd.concat(partes, ignore_index=True)
        try:
            x, y, off = matriz(b, resultado)
            out.append(float(np.exp(ajustar(x, y, off).params["E10"])))
        except Exception:
            continue
    return out


def modelo(d: pd.DataFrame, resultado: str, rng: np.random.Generator) -> dict:
    x, y, off = matriz(d, resultado)
    r = ajustar(x, y, off, d.depto.to_numpy())
    b = np.exp(r.params["E10"])
    lo, hi = np.exp(r.conf_int().loc["E10"].to_numpy())
    boots = rr_bootstrap(d, resultado, rng)
    return {"n": len(d), "n_deptos": int(d.depto.nunique()), "RR_por_0.10_de_E": round(float(b), 4),
            "ic95_robusto_agrupado": [round(float(lo), 4), round(float(hi), 4)],
            "ic95_remuestreo_deptos": [round(float(np.percentile(boots, 2.5)), 4), round(float(np.percentile(boots, 97.5)), 4)],
            "replicas_validas": len(boots)}


def rho_dentro_de_depto(d: pd.DataFrame, rng: np.random.Generator) -> dict:
    """R1b: Spearman parcial con efectos fijos de departamento: rangos dentro de departamento, residuos tras controles."""
    def calc(df: pd.DataFrame) -> float:
        g = df.groupby("depto")
        z = {v: g[v].rank(method="average") for v in ("Y2", "E", "lpob", "larea", "T", "dens")}
        # restar la media del departamento (efecto fijo) y correlacionar residuos de regresiones sobre los controles
        w = pd.DataFrame({k: v - v.groupby(df.depto).transform("mean") for k, v in z.items()})
        c = w[["lpob", "larea", "T", "dens"]].to_numpy()
        ry = w.Y2.to_numpy() - c @ np.linalg.lstsq(c, w.Y2.to_numpy(), rcond=None)[0]
        re = w.E.to_numpy() - c @ np.linalg.lstsq(c, w.E.to_numpy(), rcond=None)[0]
        return float(np.corrcoef(ry, re)[0, 1]) if ry.std() > 0 and re.std() > 0 else float("nan")
    obs = calc(d)
    idx = d.groupby("depto").indices
    claves = list(idx)
    b = []
    for _ in range(N_BOOT):
        partes = []
        for n, s in enumerate(rng.choice(len(claves), len(claves), replace=True)):
            g = d.iloc[idx[claves[s]]].copy()
            g["depto"] = f"{n:03d}"
            partes.append(g)
        v = calc(pd.concat(partes, ignore_index=True))
        if not np.isnan(v):
            b.append(v)
    return {"n": len(d), "rho_dentro_de_departamento": round(obs, 4),
            "ic95_remuestreo_deptos": [round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)]}


def main(sinpad, limites, poblacion, hand_json, vias_json, relieve_json, salida) -> None:
    rng = np.random.default_rng(SEMILLA)
    d = ex.construir(sinpad, limites, poblacion, hand_json, vias_json, relieve_json)
    res: dict = {}
    ambitos = {"PERU": d, **{r: d[d.reg == r].reset_index(drop=True) for r in ex.REGIONES_LISTA}}
    for nombre, sub in ambitos.items():
        res[nombre] = {"R1_Y1_viviendas": modelo(sub, "Y1", rng), "R1_Y2_km_carretera": modelo(sub, "Y2", rng),
                       "R1b_spearman_parcial_dentro_de_departamento": rho_dentro_de_depto(sub, rng)}
        print(nombre, json.dumps(res[nombre], ensure_ascii=False), flush=True)
    Path(salida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 8:
        sys.exit(__doc__)
    main(*sys.argv[1:])
