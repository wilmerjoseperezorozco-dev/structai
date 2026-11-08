"""Sesgo de reporte de la UNGRD y su efecto sobre V1. Protocolo: PROTOCOLO_SESGO_REPORTE.md (fijado antes de calcular).

Entradas: v1_panel.csv (v1_analisis.py) y la tabla ungrd_emergencias (Supabase; cache local en _cache/ungrd_todas.pkl).
Salida: sesgo_reporte_resultados.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import v1_analisis as v1  # noqa: E402  (funciones estadisticas y listas de departamentos del protocolo V1)

ESTRUCTURALES = {"INCENDIO ESTRUCTURAL", "COLAPSO ESTRUCTURAL"}
PELIGRO = ["INUND", "CRECIENTE", "TORRENCIAL", "MOVIMIENTO EN MASA", "VENDAVAL", "TEMPORAL", "LLUVIA", "GRANIZ", "TORMENTA", "SEQU",
           "FORESTAL", "COBERTURA VEGETAL", "EROSION", "CICLON", "HELADA", "INMERSION", "SISMO", "DESLIZ", "AVALANCHA"]
MIN_EVENTOS_PC = 3
CACHE = AQUI / "_cache" / "ungrd_todas.pkl"


def cargar_ungrd() -> pd.DataFrame:
    if CACHE.exists():
        return pd.read_pickle(CACHE)
    import _datos_caribe as dc
    sb, filas, ini = dc._sb(), [], 0
    while True:
        p = sb.table("ungrd_emergencias").select("fecha,evento,codigo_municipio,personas,familias,viviendas_destruidas,viviendas_averiadas,hectareas,fuente").range(ini, ini + 999).execute().data
        filas += p
        if len(p) < 1000:
            break
        ini += 1000
    d = pd.DataFrame(filas)
    d["anio"] = pd.to_datetime(d["fecha"], errors="coerce").dt.year
    d.to_pickle(CACHE)
    return d


def indicadores(ung: pd.DataFrame) -> pd.DataFrame:
    u = ung.copy()
    for c in ("personas", "familias", "viviendas_destruidas", "viviendas_averiadas", "hectareas"):
        u[c] = pd.to_numeric(u[c], errors="coerce").fillna(0)
    u["ev"] = u["evento"].fillna("").str.upper()
    u["estructural"] = u["ev"].isin(ESTRUCTURALES)
    u["no_peligro"] = ~u["ev"].apply(lambda s: any(k in s for k in PELIGRO))
    u["sin_efecto"] = (u[["personas", "familias", "viviendas_destruidas", "viviendas_averiadas", "hectareas"]].sum(axis=1) == 0)
    g = u.groupby("codigo_municipio")
    return pd.DataFrame({"n_estructural": g["estructural"].sum(), "n_no_peligro": g["no_peligro"].sum(), "n_total": g.size(),
                         "frac_sin_efecto": g["sin_efecto"].mean()})


def main():
    panel = pd.read_csv(AQUI / "v1_panel.csv", dtype={"codigo": str})
    ung = cargar_ungrd()
    ind = indicadores(ung)
    panel = panel.merge(ind, left_on="codigo", right_index=True, how="left")
    for c in ("n_estructural", "n_no_peligro", "n_total"):
        panel[c] = panel[c].fillna(0)
    panel["P_A"] = np.log1p(panel["n_estructural"] / panel["poblacion"] * 1e5)
    panel["P_B"] = np.log1p(panel["n_no_peligro"] / panel["poblacion"] * 1e5)
    panel["P_C"] = panel["frac_sin_efecto"].where(panel["n_total"] >= MIN_EVENTOS_PC)
    panel["log_area"] = np.log(panel["area_km2"])
    panel["log_pob"] = np.log(panel["poblacion"])
    panel["km_via_x100km2"] = panel["km_via"] / panel["area_km2"] * 100
    R = {}
    print(f"Panel: {len(panel)} municipios. Mediana de P_A por region:")
    print(panel.groupby("region")[["P_A", "P_B"]].median().round(2).to_string())

    print("\n== S1: capacidad de reporte (P_A) frente a capacidad socioeconomica (efectos fijos de departamento; errores agrupados) ==")
    x = panel.dropna(subset=["P_A", "nbi2018", "pct_cabecera", "log_pob", "log_area"])
    X = sm.add_constant(pd.concat([x[["nbi2018", "pct_cabecera", "log_pob", "log_area"]],
                                   pd.get_dummies(x["depto"], prefix="d", drop_first=True).astype(float)], axis=1))
    m = sm.OLS(x["P_A"], X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(x["depto"])[0]})
    for v in ("nbi2018", "pct_cabecera", "log_pob", "log_area"):
        ic = m.conf_int().loc[v]
        R[f"S1|{v}"] = {"coef": float(m.params[v]), "ic95": [float(ic[0]), float(ic[1])], "p": float(m.pvalues[v])}
        print(f"  {v:<14} coef={m.params[v]:+.4f} IC95 [{ic[0]:+.4f}, {ic[1]:+.4f}] p={m.pvalues[v]:.3f}")
    print(f"  n={len(x)}, R2={m.rsquared:.2f}")

    print("\n== S2: P_A frente a la red vial (correlacion parcial de Spearman; controles: log poblacion y log area) ==")
    for nombre, d in (("Caribe", panel[panel["region"] == "Caribe"]), ("confirmacion", panel[panel["depto"].isin(v1.CONFIRMACION)]), ("conjunta", panel)):
        for var in ("expo_vial", "km_via_x100km2"):
            r = v1.parcial_ic(d, "P_A", var, [])
            R[f"S2|{nombre}|{var}"] = r
            if r:
                print(f"  {nombre:<13}{var:<16} rho={r['rho']:+.2f} n={r['n']} deptos={r['n_deptos']} IC95 [{r['ic95'][0]:+.2f}, {r['ic95'][1]:+.2f}]")

    print("\n== S3: atenuacion del efecto de la exposicion vial al controlar la capacidad de reporte (cuasi-Poisson, efectos fijos) ==")
    cov = ["expo_vial", "frac_hand", "pct_cabecera", "pct_mat_vulnerable", "nbi2018", "lluvia_p95", "log_area"]
    for nombre, d in (("Caribe", panel[panel["region"] == "Caribe"]), ("conjunta", panel)):
        for ind_ in ("P_A", "P_B", "P_C"):
            dd = d.dropna(subset=cov + [ind_, "viv_danadas"])
            r0, n = v1.glm(dd, "viv_danadas", cov)
            r1, _ = v1.glm(dd, "viv_danadas", cov + [ind_])
            b0, b1 = r0.params["expo_vial"], r1.params["expo_vial"]
            aten = 1 - b1 / b0 if b0 else None
            rr0, rr1 = v1.rr(r0, "expo_vial", 0.10), v1.rr(r1, "expo_vial", 0.10)
            R[f"S3|{nombre}|{ind_}"] = {"n": n, "rr_sin": rr0, "rr_con": rr1, "atenuacion": None if aten is None else float(aten),
                                         "coef_indicador": float(r1.params[ind_]), "p_indicador": float(r1.pvalues[ind_])}
            print(f"  {nombre:<9}{ind_}: n={n} RR sin={rr0['rr']:.2f} [{rr0['ic95'][0]:.2f},{rr0['ic95'][1]:.2f}] con={rr1['rr']:.2f} [{rr1['ic95'][0]:.2f},{rr1['ic95'][1]:.2f}]"
                  f"  atenuacion={100 * aten:.0f} %  (coef. del indicador {r1.params[ind_]:+.3f}, p={r1.pvalues[ind_]:.3f})")
    car = R["S3|Caribe|P_A"]
    R["veredicto_S3"] = "el sesgo de reporte explica al menos la mitad" if car["atenuacion"] is not None and car["atenuacion"] >= 0.5 else "no explica la mitad del efecto"
    print(f"\n>>> S3 (principal, Caribe, P_A): atenuacion {100 * car['atenuacion']:.0f} % -> {R['veredicto_S3']}")

    print("\n== S4: reporte por region y ano (fraccion de municipios del panel con al menos un evento / eventos por 100 mil hab.) ==")
    u = ung.merge(panel[["codigo", "region", "poblacion"]], left_on="codigo_municipio", right_on="codigo", how="inner")
    base = panel.groupby("region").agg(n_mun=("codigo", "count"), pob=("poblacion", "sum"))
    tabla = {}
    for reg, dd in u.groupby("region"):
        for anio, da in dd.groupby("anio"):
            tabla[(reg, int(anio))] = (da["codigo"].nunique() / base.loc[reg, "n_mun"], len(da) / base.loc[reg, "pob"] * 1e5)
    for reg in base.index:
        print("  " + f"{reg:<10}" + "  ".join(f"{a}: {100 * tabla.get((reg, a), (0, 0))[0]:4.0f}% / {tabla.get((reg, a), (0, 0))[1]:5.1f}" for a in range(2019, 2025)))
    R["S4"] = {f"{k[0]}|{k[1]}": list(v) for k, v in tabla.items()}
    (AQUI / "sesgo_reporte_resultados.json").write_text(json.dumps(R, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
