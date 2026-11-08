"""Bloque exploratorio de la sierra de V1-Perú (PROTOCOLO_V1_PERU.md §6: R1, R7, R9a; S2 y S3 son POSTERIORES al resultado).

Todo es exploratorio: se reporta completo y no se interpreta como confirmatorio. Holm dentro del bloque en las diferencias de R7.
S2 (terciles de elevación) y S3 (por departamento) se añaden DESPUÉS de ver que C-2 dio signo negativo en la sierra y positivo
en la costa: son análisis post hoc y se rotulan así.

Uso: python -I peru_exploratorias_sierra.py <sinpad.csv> <per_admin_boundaries.xlsx> <inei_pob_proy.xlsx> <hand_peru.json>
                                              <vias_hand_peru.json> <relieve_peru.json> <salida.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import peru_c2 as c2  # noqa: E402
import peru_compuerta_datos as cd  # noqa: E402

N_BOOT = 5000
SEMILLA = 20261108
MIN_DISTRITOS_DEPTO = 30
CTRL_C2 = ["lpob", "larea", "T", "dens"]
CTRL_RELIEVE = CTRL_C2 + ["elev", "pend"]
REGIONES_LISTA = ("COSTA", "SIERRA", "SELVA")


def _json(ruta: str) -> pd.DataFrame:
    d = pd.DataFrame(json.load(open(ruta, encoding="utf-8"))["distritos"])
    d["UBIGEO"] = d["adm3_pcode"].str.replace("PE", "", regex=False)
    return d


def construir(sinpad, limites, poblacion, hand_json, vias_json, relieve_json, años=None) -> pd.DataFrame:
    if años:
        cd.AÑOS = años
    pol = pd.read_excel(limites, sheet_name="per_admin3")
    pol["UBIGEO"] = pol["adm3_pcode"].astype(str).str.replace("PE", "", regex=False).str.zfill(6)
    area = pol.set_index("UBIGEO")["area_sqkm"]
    pob, sin = cd.cargar_poblacion(poblacion), cd.cargar_sinpad(sinpad)
    hand, vias, rel = _json(hand_json), _json(vias_json), _json(relieve_json)
    d = vias.merge(hand[["UBIGEO", "n_validos_5", "frac_hand_lt10_5"]], on="UBIGEO", how="left")
    d = d.merge(rel[["UBIGEO", "elev_media_m", "pend_media_grados"]], on="UBIGEO", how="left")
    d["pob"], d["area"] = d.UBIGEO.map(pob), d.UBIGEO.map(area)
    d = d.merge(sin, left_on="UBIGEO", right_index=True, how="left")
    d[["viv", "km_carr"]] = d[["viv", "km_carr"]].fillna(0.0)
    ok = ((d.pob > 0) & d.area.notna() & d.frac_hand_lt10_5.notna() & (d.n_validos_5 >= cd.CELDAS_MIN)
          & (d.km_via >= cd.KM_VIA_MIN) & d.elev_media_m.notna() & d.pend_media_grados.notna())
    d = d[ok].copy()
    d["E"], d["Y2"] = d.km_bajo / d.km_via, d.km_carr / d.area * 100
    d["lpob"], d["larea"], d["T"] = np.log(d.pob), np.log(d.area), d.frac_hand_lt10_5
    d["dens"], d["elev"], d["pend"] = d.km_via / d.area * 100, d.elev_media_m, d.pend_media_grados
    d["depto"] = d.UBIGEO.str[:2]
    d["reg"] = d.region.map(c2.REGIONES)
    return d.reset_index(drop=True)


def rho(d: pd.DataFrame, ctrl: list[str]) -> float:
    return c2.parcial_spearman(d.Y2.to_numpy(), d.E.to_numpy(), d[ctrl].to_numpy())


def ic_bloques(d: pd.DataFrame, ctrl: list[str], rng: np.random.Generator) -> dict:
    deptos = d.groupby("depto").indices
    claves = list(deptos)
    y, e, c = d.Y2.to_numpy(), d.E.to_numpy(), d[ctrl].to_numpy()
    b = []
    for _ in range(N_BOOT):
        ii = np.concatenate([deptos[claves[s]] for s in rng.choice(len(claves), len(claves), replace=True)])
        r = c2.parcial_spearman(y[ii], e[ii], c[ii])
        if not np.isnan(r):
            b.append(r)
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {"n": len(d), "n_deptos": len(claves), "rho": round(rho(d, ctrl), 4),
            "ic95": [round(float(lo), 4), round(float(hi), 4)]}


def diferencias_region(d: pd.DataFrame, rng: np.random.Generator) -> dict:
    """R7: diferencia de rho entre regiones, remuestreando departamentos del conjunto completo."""
    deptos = d.groupby("depto").indices
    claves = list(deptos)
    reg = d.reg.to_numpy()
    y, e, c = d.Y2.to_numpy(), d.E.to_numpy(), d[CTRL_C2].to_numpy()
    obs = {r: c2.parcial_spearman(y[reg == r], e[reg == r], c[reg == r]) for r in REGIONES_LISTA}
    dif: dict[str, list[float]] = {"COSTA-SIERRA": [], "SELVA-SIERRA": []}
    for _ in range(N_BOOT):
        ii = np.concatenate([deptos[claves[s]] for s in rng.choice(len(claves), len(claves), replace=True)])
        rr = reg[ii]
        r = {k: c2.parcial_spearman(y[ii][rr == k], e[ii][rr == k], c[ii][rr == k]) for k in REGIONES_LISTA}
        if not any(np.isnan(v) for v in r.values()):
            dif["COSTA-SIERRA"].append(r["COSTA"] - r["SIERRA"])
            dif["SELVA-SIERRA"].append(r["SELVA"] - r["SIERRA"])
    out: dict[str, dict] = {}
    for k, v in dif.items():
        v = np.array(v)
        p = float(min(1.0, 2 * min((v <= 0).mean(), (v >= 0).mean())))
        out[k] = {"diferencia": round(float(obs[k.split("-")[0]] - obs["SIERRA"]), 4),
                  "ic95": [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)],
                  "p_bootstrap": round(p, 4)}
    for i, k in enumerate(sorted(out, key=lambda k: out[k]["p_bootstrap"])):  # Holm sobre 2
        out[k]["p_holm"] = round(min(1.0, out[k]["p_bootstrap"] * (len(out) - i)), 4)
    return out


def main(sinpad, limites, poblacion, hand_json, vias_json, relieve_json, salida) -> None:
    rng = np.random.default_rng(SEMILLA)
    args = (sinpad, limites, poblacion, hand_json, vias_json, relieve_json)
    d = construir(*args)
    s = d[d.reg == "SIERRA"].reset_index(drop=True)
    res: dict = {"distritos_con_relieve": len(d), "sierra_n": len(s)}
    for r in REGIONES_LISTA:
        res[f"R1_{r.lower()}_con_elevacion_y_pendiente"] = ic_bloques(d[d.reg == r].reset_index(drop=True), CTRL_RELIEVE, rng)
    res["R7_diferencias_entre_regiones_controles_C2"] = diferencias_region(d, rng)
    s["tercil"] = pd.qcut(s.elev, 3, labels=["bajo", "medio", "alto"])
    res["S2_post_hoc_terciles_elevacion"] = {
        str(t): {**ic_bloques(g.reset_index(drop=True), CTRL_C2 + ["pend"], rng),
                 "elev_rango_m": [round(float(g.elev.min())), round(float(g.elev.max()))]}
        for t, g in s.groupby("tercil", observed=True)}
    res["S3_post_hoc_por_departamento_sierra"] = {
        dep: {"n": len(g), "rho": round(rho(g.reset_index(drop=True), CTRL_C2), 3)}
        for dep, g in s.groupby("depto") if len(g) >= MIN_DISTRITOS_DEPTO}
    res["S3_dejando_un_departamento_fuera"] = {
        dep: round(rho(s[s.depto != dep].reset_index(drop=True), CTRL_C2), 3) for dep in sorted(s.depto.unique())}
    res["descriptivo_sierra"] = {
        "spearman_E_elevacion": round(float(s.E.corr(s.elev, method="spearman")), 3),
        "spearman_Y2_elevacion": round(float(s.Y2.corr(s.elev, method="spearman")), 3),
        "spearman_E_pendiente": round(float(s.E.corr(s.pend, method="spearman")), 3),
        "Y2_mayor_0_por_cuartil_de_E": {str(q): round(float((g.Y2 > 0).mean()), 3)
                                         for q, g in s.groupby(pd.qcut(s.E, 4, duplicates="drop"), observed=True)}}
    d23 = construir(*args, años=[str(y) for y in range(2019, 2025) if y != 2023])
    res["R9a_sin_2023"] = {r: ic_bloques(d23[d23.reg == r].reset_index(drop=True), CTRL_C2, rng) for r in REGIONES_LISTA}
    Path(salida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    if len(sys.argv) != 8:
        sys.exit(__doc__)
    main(*sys.argv[1:])
