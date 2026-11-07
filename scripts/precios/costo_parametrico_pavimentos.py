"""Ítem 4 (PROTOCOLO_COSTO_PARAMETRICO.md): costo directo de referencia por m² de pavimento = espesores de motor-vias × precios INVIAS 2026-1.
Reglas fijadas en el protocolo antes de correr; este script no elige actividades ni supuestos nuevos.
Salida: costo_parametrico_pavimentos.json y un resumen por consola. Uso: python costo_parametrico_pavimentos.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "motor-vias"))
sys.path.insert(0, str(AQUI.parent / "satelite"))
import _datos_caribe as dc  # noqa: E402
from src.pavimentos import DisenadorPavimentos, ManualPavimentos, ParametrosPavimento, TipoPavimento, TipoVia  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CACHE = AQUI / "_cache" / "costo_parametrico_precios.json"
NUM = {"subbase": "320,1,1", "base": "330,1,1", "rodadura": "450,01", "imprimacion": "420,1",
       "ca40": "410,1", "ca60": "410,2", "ca80": "410,3", "concreto_pav": "500,1,1"}
DENSIDAD_MEZCLA, CONTENIDO_CA = 2350.0, 0.055       # kg/m³ y fracción en peso (supuestos del protocolo)
DISENO_REF = (5.0, 8)                                 # ESAL (millones), CBR (%) del contraste geográfico
N_BOOT = 2000
RNG = np.random.default_rng(20261107)


def bajar_precios() -> pd.DataFrame:
    if CACHE.exists():
        return pd.DataFrame(json.loads(CACHE.read_text(encoding="utf-8")))
    sb, filas, ini = dc._sb(), [], 0
    cols = "numeral,provincia_codigo,periodo,costo_equipo,costo_materiales,costo_transporte,costo_mano_obra,costo_directo_total"
    while True:
        p = (sb.table("invias_actividad_costos").select(cols).in_("numeral", list(NUM.values()))
             .order("numeral").order("provincia_codigo").range(ini, ini + 999).execute().data or [])
        filas += p
        if len(p) < 1000:
            break
        ini += 1000
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(filas), encoding="utf-8")
    return pd.DataFrame(filas)


def provincias() -> pd.DataFrame:
    sb = dc._sb()
    return pd.DataFrame(sb.table("invias_provincias").select("codigo,departamento,provincia,region_natural").execute().data)


def disenar(esal: float, cbr: int, tipo: TipoPavimento):
    p = ParametrosPavimento(tipo_pavimento=tipo, tipo_via=TipoVia.SECUNDARIA, tpd=1000, esals_millones=esal, cbr_subrasante=float(cbr))
    return DisenadorPavimentos(ManualPavimentos()).disenar(p)


def costo_flexible(r, P: dict, ca: str = "ca60", contenido: float = CONTENIDO_CA, f_rod: float = 1.0) -> dict:
    d1 = r.espesor_rodadura * f_rod / 100
    kg_ca = d1 * DENSIDAD_MEZCLA * contenido
    c = {"rodadura": d1 * P["rodadura"], "cemento_asfaltico": kg_ca * P[ca], "imprimacion": P["imprimacion"],
         "base": r.espesor_base / 100 * P["base"], "subbase": r.espesor_subbase / 100 * P["subbase"]}
    c["total"] = sum(c.values())
    return c


def costo_rigido(r, P: dict) -> dict:
    c = {"losa": r.espesor_rodadura / 100 * P["concreto_pav"], "base": r.espesor_base / 100 * P["base"], "subbase": r.espesor_subbase / 100 * P["subbase"]}
    c["total"] = sum(c.values())
    return c


def main() -> None:
    df, prov = bajar_precios(), provincias()
    print(f"Precios descargados: {len(df)} filas; periodos: {sorted(df.periodo.unique())}")
    # S1: cada actividad con precio en las 140 provincias
    n_prov = df.groupby("numeral").provincia_codigo.nunique()
    print("S1 provincias con precio por actividad:", n_prov.to_dict())
    # S2: costo_directo_total vs suma de componentes
    comp = df[["costo_equipo", "costo_materiales", "costo_transporte", "costo_mano_obra"]].astype(float).sum(axis=1)
    rel = ((comp - df.costo_directo_total.astype(float)).abs() / df.costo_directo_total.astype(float))
    print(f"S2 |suma componentes − total| / total: mediana {rel.median():.4f}; máx {rel.max():.4f}; filas con diferencia > 1 %: {(rel > 0.01).sum()}")
    # S3: precios > 3× la mediana nacional de su actividad
    piv = df.pivot(index="provincia_codigo", columns="numeral", values="costo_directo_total").astype(float)
    razon = piv / piv.median()
    flag = (razon > 3)
    print("S3 provincias con precio > 3× mediana nacional por actividad:", {k: int(v) for k, v in flag.sum().items() if v})
    nombres = {v: k for k, v in NUM.items()}
    piv = piv.rename(columns=nombres)
    # provincia de referencia: Atlántico, la de menor código (todas tienen las 12 actividades con precio)
    atl = prov[prov.departamento.str.upper().str.contains("ATL")].sort_values("codigo")
    ref = atl.codigo.iloc[0]
    print(f"Provincia de referencia: {ref} ({atl.provincia.iloc[0]}, {atl.departamento.iloc[0]}); provincias del Atlántico: {len(atl)}")
    P = piv.loc[ref].to_dict()
    print("Precios de referencia (COP por unidad): " + ", ".join(f"{k}={v:,.0f}" for k, v in P.items()))

    # 1) malla ESAL × CBR en la provincia de referencia
    esals = sorted(ManualPavimentos().sn_requerido.keys()); cbrs = sorted(ManualPavimentos().sn_requerido[esals[0]].keys())
    filas = []
    for e in esals:
        for c in cbrs:
            rf, rr = disenar(e, c, TipoPavimento.ASFALTICO), disenar(e, c, TipoPavimento.CONCRETO)
            cf, cr = costo_flexible(rf, P), costo_rigido(rr, P)
            filas.append({"esal": e, "cbr": c, "d_rod": rf.espesor_rodadura, "d_base": rf.espesor_base, "d_sub": rf.espesor_subbase, "cumple_flex": rf.cumple,
                          "flex_total": cf["total"], "flex_sub_pct": cf["subbase"] / cf["total"], "flex_asf_pct": (cf["rodadura"] + cf["cemento_asfaltico"]) / cf["total"],
                          "d_losa": rr.espesor_rodadura, "rig_total": cr["total"], "cumple_rig": rr.cumple})
    malla = pd.DataFrame(filas)
    print("\n1) Malla en la provincia de referencia (COP/m², costo directo de referencia):")
    print(malla.assign(flex_total=lambda d: d.flex_total.round(0), rig_total=lambda d: d.rig_total.round(0),
                       flex_sub_pct=lambda d: (100 * d.flex_sub_pct).round(0), flex_asf_pct=lambda d: (100 * d.flex_asf_pct).round(0))
          .to_string(index=False))
    print(f"Diseños flexibles que el motor marca como no cumple: {(~malla.cumple_flex).sum()} de {len(malla)}; rígidos: {(~malla.cumple_rig).sum()} de {len(malla)}")
    cruce = []
    for c in cbrs:
        m = malla[malla.cbr == c].sort_values("esal")
        menor = m[m.rig_total <= m.flex_total]
        cruce.append({"cbr": c, "esal_cruce": float(menor.esal.iloc[0]) if len(menor) else None})
    print("ESAL desde el cual el rígido cuesta menos que el flexible (costo inicial), por CBR:", cruce)

    # 2) dispersión geográfica del diseño de referencia
    rf = disenar(*DISENO_REF, TipoPavimento.ASFALTICO)
    tot = np.array([costo_flexible(rf, piv.loc[p].to_dict())["total"] for p in piv.index])
    p10, p50, p90 = np.percentile(tot, [10, 50, 90])
    med = piv.median()
    cf = np.array([costo_flexible(rf, {**piv.loc[p].to_dict(), "subbase": med["subbase"], "base": med["base"]})["total"] for p in piv.index])
    frac = 1 - np.var(np.log(cf)) / np.var(np.log(tot))
    bs = [np.percentile(s, 90) / np.percentile(s, 10) for s in (tot[RNG.integers(0, len(tot), len(tot))] for _ in range(N_BOOT))]
    print(f"\n2) Diseño de referencia ESAL {DISENO_REF[0]} M, CBR {DISENO_REF[1]} % (espesores {rf.espesor_rodadura}/{rf.espesor_base}/{rf.espesor_subbase} cm) en 140 provincias:")
    print(f"   costo por m²: P10 {p10:,.0f}; mediana {p50:,.0f}; P90 {p90:,.0f}; P90/P10 = {p90 / p10:.2f} (IC95 % bootstrap {np.percentile(bs, 2.5):.2f}-{np.percentile(bs, 97.5):.2f})")
    print(f"   fracción de la varianza logarítmica que desaparece al fijar subbase y base en su mediana nacional: {100 * frac:.0f} %")

    # 3) sensibilidad en la provincia de referencia
    base = costo_flexible(rf, P)["total"]
    sens = {}
    for nombre, kw in [("asfalto 4,5 %", {"contenido": 0.045}), ("asfalto 6,5 %", {"contenido": 0.065}), ("CA 40-50", {"ca": "ca40"}), ("CA 80-100", {"ca": "ca80"}),
                       ("rodadura −20 %", {"f_rod": 0.8}), ("rodadura +20 %", {"f_rod": 1.2})]:
        sens[nombre] = costo_flexible(rf, P, **kw)["total"] / base - 1
    print("\n3) Sensibilidad del costo por m² (diseño de referencia, provincia de referencia): " + "; ".join(f"{k}: {100 * v:+.1f} %" for k, v in sens.items()))

    salida = {"provincia_ref": ref, "precios_ref": P, "malla": malla.to_dict("records"), "cruce_rigido": cruce,
              "dispersion": {"p10": p10, "p50": p50, "p90": p90, "p90_p10": p90 / p10, "fraccion_granular": frac}, "sensibilidad": sens,
              "s2": {"mediana_rel": float(rel.median()), "max_rel": float(rel.max())}}
    (AQUI / "costo_parametrico_pavimentos.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
