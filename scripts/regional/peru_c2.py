"""C-2 de V1-Perú (PROTOCOLO_V1_PERU.md §5 y Enmienda 2): correlación parcial de Spearman entre E (exposición vial a terreno
bajo) y Y2 (km de carretera destruida + afectada por 100 km2), controlando log(población), log(área), T y densidad de vía.
IC95 % por remuestreo de departamentos. No calcula C-1 (declarada no concluyente en la compuerta de datos).

Uso: python -I peru_c2.py <sinpad.csv> <per_admin_boundaries.xlsx> <inei_pob_proy.xlsx> <hand_peru.json> <vias_hand_peru.json> <salida.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import peru_compuerta_datos as cd  # noqa: E402

N_BOOT = 5000
SEMILLA = 20261108
UMBRAL_REPLICA = 0.15
MIN_DEPTOS_IC = 10
REGIONES = {"COSTA": "COSTA", "SIERRA": "SIERRA", "SELVA ALTA": "SELVA", "SELVA BAJA": "SELVA"}


def rangos(x: np.ndarray) -> np.ndarray:
    return pd.Series(x).rank(method="average").to_numpy()


def parcial_spearman(y: np.ndarray, e: np.ndarray, controles: np.ndarray) -> float:
    ry, re = rangos(y), rangos(e)
    rc = np.column_stack([rangos(c) for c in controles.T])
    x = np.column_stack([np.ones(len(ry)), rc])
    res_y = ry - x @ np.linalg.lstsq(x, ry, rcond=None)[0]
    res_e = re - x @ np.linalg.lstsq(x, re, rcond=None)[0]
    if res_y.std() == 0 or res_e.std() == 0:
        return float("nan")
    return float(np.corrcoef(res_y, res_e)[0, 1])


def analizar(d: pd.DataFrame, rng: np.random.Generator) -> dict:
    y = d.Y2.to_numpy()
    e = d.E.to_numpy()
    c = d[["lpob", "larea", "T", "dens"]].to_numpy()
    rho = parcial_spearman(y, e, c)
    bloques = {k: g.index.to_numpy() for k, g in d.groupby("depto")}
    claves = list(bloques)
    pos = {i: n for n, i in enumerate(d.index)}
    boots = []
    for _ in range(N_BOOT):
        sel = rng.choice(len(claves), len(claves), replace=True)
        idx = np.concatenate([bloques[claves[s]] for s in sel])
        ii = [pos[i] for i in idx]
        r = parcial_spearman(y[ii], e[ii], c[ii])
        if not np.isnan(r):
            boots.append(r)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    if lo > 0 and rho >= UMBRAL_REPLICA:
        veredicto = "se replica"
    elif -UMBRAL_REPLICA < lo and hi < UMBRAL_REPLICA:
        veredicto = "no se replica (ausencia practica, equivalencia +-0,15)"
    else:
        veredicto = "no concluyente"
    return {"n_distritos": len(d), "n_departamentos": len(claves), "rho_parcial": round(rho, 4),
            "ic95": [round(float(lo), 4), round(float(hi), 4)], "veredicto": veredicto,
            "ic_poco_confiable_por_pocos_departamentos": len(claves) < MIN_DEPTOS_IC}


def main(sinpad: str, limites: str, poblacion: str, hand_json: str, vias_json: str, salida: str) -> None:
    pol = pd.read_excel(limites, sheet_name="per_admin3")
    pol["UBIGEO"] = pol["adm3_pcode"].astype(str).str.replace("PE", "", regex=False).str.zfill(6)
    area = pol.set_index("UBIGEO")["area_sqkm"]
    pob = cd.cargar_poblacion(poblacion)
    sin = cd.cargar_sinpad(sinpad)
    hand = pd.DataFrame(json.load(open(hand_json, encoding="utf-8"))["distritos"])
    hand["UBIGEO"] = hand["adm3_pcode"].str.replace("PE", "", regex=False)
    vias = pd.DataFrame(json.load(open(vias_json, encoding="utf-8"))["distritos"])
    vias["UBIGEO"] = vias["adm3_pcode"].str.replace("PE", "", regex=False)
    d = vias.merge(hand[["UBIGEO", "n_validos_5", "frac_hand_lt10_5"]], on="UBIGEO", how="left")
    d["pob"], d["area"] = d.UBIGEO.map(pob), d.UBIGEO.map(area)
    d = d.merge(sin, left_on="UBIGEO", right_index=True, how="left")
    d[["viv", "km_carr"]] = d[["viv", "km_carr"]].fillna(0.0)
    ok = (d.pob > 0) & d.area.notna() & d.frac_hand_lt10_5.notna() & (d.n_validos_5 >= cd.CELDAS_MIN) & (d.km_via >= cd.KM_VIA_MIN)
    d = d[ok].copy()
    d["E"] = d.km_bajo / d.km_via
    d["Y2"] = d.km_carr / d.area * 100
    d["lpob"], d["larea"] = np.log(d.pob), np.log(d.area)
    d["T"] = d.frac_hand_lt10_5
    d["dens"] = d.km_via / d.area * 100
    d["depto"] = d.UBIGEO.str[:2]
    d["reg"] = d.region.map(REGIONES)
    d = d.reset_index(drop=True)
    rng = np.random.default_rng(SEMILLA)
    res = {"C2_peru_completo": analizar(d, rng), "por_region_natural": {}, "omitidos_sin_region": int(d.reg.isna().sum())}
    for r in ("COSTA", "SIERRA", "SELVA"):
        sub = d[d.reg == r].reset_index(drop=True)
        res["por_region_natural"][r] = analizar(sub, rng) if len(sub) >= 30 else {"n_distritos": len(sub), "veredicto": "no evaluable"}
    Path(salida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    main(*sys.argv[1:])
