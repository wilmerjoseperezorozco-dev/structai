"""H5 (#273): asimetría entre la amenaza sísmica normativa (NSR-10 A-4) y el daño estructural empírico contemporáneo
(UNGRD 2019-2024). Protocolo: PROTOCOLO_ANALISIS.md §28, fijado antes de calcular el índice de daño.

Índice de daño D (fijo): media de rangos percentiles de
  V = viviendas destruidas + averiadas por 100 mil habitantes
  R = vías averiadas por 100 km²
  P = puentes vehiculares + peatonales averiados por 100 km²
con todos los eventos de la UNGRD 2019-2024. Descomposición del daño por mecanismo: hídrico, remoción en masa, sísmico,
otros.

Uso (con python -I; insumos de h3_descargar_insumos.py):
  python h5_asimetria_normativa.py --conteo   # muestra y distribución de Aa/zona; no calcula D
  python h5_asimetria_normativa.py            # análisis confirmatorio
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import h3_socavacion_puentes as h3  # noqa: E402  (insumos, cargar_ungrd, preparar, auc, parcial, REG, ESTRUCTURALES)

N_BOOT = 2000
RNG = np.random.default_rng(2735)
UMBRAL_EQUIVALENCIA = 0.20
MECANISMOS = {"hidrico": {"INUNDACION", "CRECIENTE SUBITA", "AVENIDA TORRENCIAL"}, "remocion": {"MOVIMIENTO EN MASA"}}


def mecanismo(ev: str) -> str:
    if "SISMO" in ev or "TERREMOTO" in ev:
        return "sismico"
    for k, v in MECANISMOS.items():
        if ev in v:
            return k
    return "otros"


def boot(fun, bloques):
    et = np.unique(bloques)
    idx = {b: np.where(bloques == b)[0] for b in et}
    vals = []
    for _ in range(N_BOOT):
        ix = np.concatenate([idx[b] for b in RNG.choice(et, len(et), replace=True)])
        try:
            v = fun(ix)
        except Exception:
            continue
        if np.isfinite(v):
            vals.append(v)
    return [float(v) for v in np.percentile(vals, [2.5, 97.5])]


def preparar():
    ins = h3.insumos()
    p, _, ung = h3.preparar(ins)            # mismo panel, pendiente S, P_A y log_pob que H3
    a4 = {f["codigo"]: f for f in ins["a4"]}
    p = p[p["codigo"].isin(a4)].copy()
    p["aa"] = [float(a4[c]["aa"]) for c in p["codigo"]]
    p["zona"] = [a4[c]["zona"] for c in p["codigo"]]
    for c in ("viviendas_destruidas", "viviendas_averiadas", "vias_averiadas"):
        ung[c] = pd.to_numeric(ung[c], errors="coerce").fillna(0)
    ung["mec"] = ung["ev"].map(mecanismo)
    return p.reset_index(drop=True), ung


def indice_dano(p: pd.DataFrame, ung: pd.DataFrame) -> pd.DataFrame:
    u = ung.assign(viv=ung["viviendas_destruidas"] + ung["viviendas_averiadas"],
                   pte=ung["puentes_vehiculares"] + ung["puentes_peatonales"])
    g = u.groupby("codigo_municipio")[["viv", "vias_averiadas", "pte"]].sum()
    p = p.copy()
    for col, src in (("viv", "viv"), ("vias", "vias_averiadas"), ("pte", "pte")):
        p[col] = p["codigo"].map(g[src]).fillna(0)
    p["V"] = p["viv"] / p["poblacion"] * 1e5
    p["R"] = p["vias"] / p["area_km2"] * 100
    p["P"] = p["pte"] / p["area_km2"] * 100
    pr = lambda x: (rankdata(x) - 0.5) / len(x)  # noqa: E731
    p["D"] = (pr(p["V"].values) + pr(p["R"].values) + pr(p["P"].values)) / 3
    return p


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--conteo", action="store_true")
    a = ap.parse_args()
    p, ung = preparar()
    if a.conteo:
        print(f"municipios: {len(p)} en {p['depto2'].nunique()} departamentos")
        print("zona NSR-10:", p["zona"].value_counts().to_dict())
        print("Aa:", p["aa"].describe()[["min", "50%", "max"]].round(3).to_dict())
        print("ρ(Aa, pendiente):", round(float(spearmanr(p["aa"], p["S"])[0]), 2),
              "| Aa por región (mediana):", p.groupby("region")["aa"].median().round(2).to_dict())
        return
    p = indice_dano(p, ung)
    b = p["depto2"].values
    D, AA = p["D"].values, p["aa"].values
    Z = [p["log_pob"].values, p["P_A"].values, p["S"].values]
    R = {"n": len(p)}
    R["A0_rho_bruto"] = [float(spearmanr(AA, D)[0]), boot(lambda i: spearmanr(AA[i], D[i])[0], b)]
    R["A1_rho_parcial_pob_reporte_pendiente"] = [float(h3.parcial(AA, D, Z)),
                                                 boot(lambda i: h3.parcial(AA[i], D[i], [z[i] for z in Z]), b)]
    lo, hi = R["A1_rho_parcial_pob_reporte_pendiente"][1]
    if -UMBRAL_EQUIVALENCIA < lo and hi < UMBRAL_EQUIVALENCIA:
        R["veredicto_A1"] = "ASIMETRÍA: el IC95 del ρ parcial queda dentro de (−0,20; 0,20)"
    elif lo >= UMBRAL_EQUIVALENCIA:
        R["veredicto_A1"] = "ALINEADAS: el IC95 queda por encima de 0,20"
    elif hi <= -UMBRAL_EQUIVALENCIA:
        R["veredicto_A1"] = "INVERSA: el IC95 queda por debajo de −0,20"
    else:
        R["veredicto_A1"] = "NO CONCLUYENTE: el IC95 cruza ±0,20"
    # A2: fracción del daño por mecanismo (viviendas, vías, puentes), con IC por departamento
    u = ung[ung["codigo_municipio"].isin(set(p["codigo"]))].copy()
    u["dano"] = (u["viviendas_destruidas"] + u["viviendas_averiadas"] + u["vias_averiadas"]
                 + u["puentes_vehiculares"] + u["puentes_peatonales"])
    u["depto2"] = u["codigo_municipio"].str[:2]
    tot = u.groupby(["depto2", "mec"])["dano"].sum().unstack(fill_value=0)
    deptos = tot.index.values
    R["A2_fraccion_dano_por_mecanismo"] = {}
    for mec in ("hidrico", "remocion", "sismico", "otros"):
        col = tot[mec].values if mec in tot else np.zeros(len(tot))
        f = lambda i: col[i].sum() / tot.values[i].sum()  # noqa: E731
        R["A2_fraccion_dano_por_mecanismo"][mec] = [float(f(np.arange(len(tot)))), boot(f, deptos)]
    # A3: cuadrantes de asimetría (descriptivo)
    terc = pd.qcut(p["D"], 3, labels=["bajo", "medio", "alto"])
    R["A3_tabla_zona_vs_tercil_dano"] = pd.crosstab(p["zona"], terc).to_dict()
    R["A3_alta_con_dano_bajo"] = int(((p["zona"] == "Alta") & (terc == "bajo")).sum())
    R["A3_baja_con_dano_alto"] = int(((p["zona"] == "Baja") & (terc == "alto")).sum())
    R["componentes_rho_bruto_con_aa"] = {k: float(spearmanr(AA, p[k])[0]) for k in ("V", "R", "P")}
    R["rho_parcial_por_region"] = {}
    for reg, g in p.groupby("region"):
        if len(g) >= 30 and g["aa"].nunique() > 1:
            i = g.index.values
            R["rho_parcial_por_region"][reg] = [len(g), float(h3.parcial(AA[i], D[i], [z[i] for z in Z]))]
    print(json.dumps(R, ensure_ascii=False, indent=1, default=str))
    (AQUI / "h5_asimetria_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str),
                                                       encoding="utf-8")


if __name__ == "__main__":
    main()
