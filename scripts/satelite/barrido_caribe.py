"""Barrido exploratorio de relaciones entre variables municipales del Caribe. Protocolo: PROTOCOLO_BARRIDO_CARIBE.md.

Genera hipotesis, no las confirma. Salidas: panel_caribe.csv y barrido_caribe_resultados.json.
"""
from __future__ import annotations

import io
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402

if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FAMILIA = {
    "elev_media_m": "T", "pend_media_pct": "T", "frac_bajo_10m": "T", "frac_hand_lt10": "T",
    "frac_inundable_igac": "S",
    "lluvia_anual_mm": "L", "lluvia_cv_mensual": "L", "lluvia_p95_mensual": "L",
    "inund_x100k": "E", "afectadas_x100k": "E", "viviendas_danadas_x100k": "E",
    "exposicion_vial": "I", "km_via_x100km2": "I", "puentes_x100km": "I",
    "pct_mat_vulnerable": "O", "pct_cabecera": "O",
    "amenaza_mm_alta": "A",
}
UMBRAL_Q = 0.10
UMBRAL_RHO = 0.20
MIN_N = 60


def construir_panel() -> pd.DataFrame:
    dem = {m["codigo"]: m for m in dc.dem() if "error" not in m}
    codigos = list(dem)
    pols = dc.poligonos()
    hand = {m["codigo"]: m for m in json.loads((AQUI / "hand_caribe.json").read_text(encoding="utf-8"))["municipios"]}
    vias = {m["codigo"]: m for m in json.loads((AQUI / "vias_hand_caribe.json").read_text(encoding="utf-8"))["municipios"]}
    chirps = json.loads((AQUI / "chirps_mensual_caribe.json").read_text(encoding="utf-8"))["municipios"]
    sus = json.loads((AQUI.parents[1] / "packages/construdata/data/susceptibilidad_municipal.json").read_text(encoding="utf-8"))["municipios"]
    pob = dc.poblacion_dane(codigos)
    igac = dc.igac(codigos)
    sis = dc.sisben(codigos)
    ung = pd.DataFrame(dc.ungrd(codigos))
    filas = []
    for c in codigos:
        if c not in pob or c not in pols:
            continue
        p, area = pob[c]["poblacion"], pols[c]["area_km2"]
        f = {"codigo": c, "municipio": dem[c]["municipio"], "depto": dem[c]["depto"], "poblacion": p, "area_km2": area,
             "elev_media_m": dem[c]["elev_media_m"], "pend_media_pct": dem[c]["pend_media_pct"], "frac_bajo_10m": dem[c]["frac_bajo_10m"],
             "pct_cabecera": pob[c]["pct_cabecera"]}
        h = hand.get(c, {})
        f["frac_hand_lt10"] = h.get("frac_hand_lt10_5") if h.get("n_validos_5", 0) >= 30 else None
        f["frac_inundable_igac"] = igac.get(c, {}).get("frac_inundable")
        if c in chirps:
            pm = np.array(chirps[c]["precip_mm"], float)
            f["lluvia_anual_mm"] = float(pm.sum() / (len(pm) / 12))
            f["lluvia_cv_mensual"] = float(pm.std() / pm.mean()) if pm.mean() > 0 else None
            f["lluvia_p95_mensual"] = float(np.percentile(pm, 95))
        u = ung[ung["codigo_municipio"] == c] if len(ung) else ung
        if len(u):
            inund = u[u["evento"].isin(dc.EVENTOS_INUNDACION)]
            f["inund_x100k"] = len(inund) / p * 1e5
            f["afectadas_x100k"] = float(pd.to_numeric(u["personas"], errors="coerce").fillna(0).sum()) / p * 1e5
            viv = pd.to_numeric(u["viviendas_destruidas"], errors="coerce").fillna(0).sum() + pd.to_numeric(u["viviendas_averiadas"], errors="coerce").fillna(0).sum()
            f["viviendas_danadas_x100k"] = float(viv) / p * 1e5
        else:
            f["inund_x100k"] = f["afectadas_x100k"] = f["viviendas_danadas_x100k"] = 0.0
        v = vias.get(c)
        if v and v["km_via"] >= 5:
            f["exposicion_vial"] = v["km_bajo"] / v["km_via"]
        if v:
            f["km_via_x100km2"] = v["km_via"] / area * 100
            if v["km_via"] >= 5:
                f["puentes_x100km"] = v["puentes"] / v["km_via"] * 100
        if c in sis and sis[c].get("pct_material_vulnerable") is not None:
            f["pct_mat_vulnerable"] = float(sis[c]["pct_material_vulnerable"])
        s = sus.get(c)
        if s and s.get("sgc_pct"):
            f["amenaza_mm_alta"] = s["sgc_pct"].get("alta", 0) + s["sgc_pct"].get("muy_alta", 0)
        filas.append(f)
    return pd.DataFrame(filas)


def parcial(df, a, b):
    d = df[[a, b, "poblacion", "area_km2", "depto"]].dropna()
    if len(d) < MIN_N or d[a].nunique() < 5 or d[b].nunique() < 5:
        return None
    rk = lambda s: stats.rankdata(s)
    Z = np.column_stack([rk(np.log(d["poblacion"])), rk(np.log(d["area_km2"])), np.ones(len(d))])
    res = lambda y: y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
    ra, rb = res(rk(d[a])), res(rk(d[b]))
    r = float(np.corrcoef(ra, rb)[0, 1])
    gl = len(d) - 2 - 2
    t = r * math.sqrt(gl / max(1e-12, 1 - r * r))
    p = float(2 * stats.t.sf(abs(t), gl))
    signos = []
    for dep in d["depto"].unique():
        m = (d["depto"] != dep).values
        if m.sum() >= 30:
            x, y = ra[m], rb[m]
            signos.append(np.sign(np.corrcoef(x, y)[0, 1]))
    estable = len(signos) >= 6 and all(s == np.sign(r) for s in signos)
    return {"n": len(d), "rho": r, "p": p, "estable_por_depto": bool(estable)}


def bh(ps):
    m = len(ps)
    orden = np.argsort(ps)
    q = np.empty(m)
    previo = 1.0
    for rango in range(m, 0, -1):
        i = orden[rango - 1]
        previo = min(previo, ps[i] * m / rango)
        q[i] = previo
    return q


def main():
    panel = construir_panel()
    panel.to_csv(AQUI / "panel_caribe.csv", index=False)
    print(f"Panel: {len(panel)} municipios; cobertura por variable:")
    for v in FAMILIA:
        print(f"  {v:<26}{panel[v].notna().sum():>4}" if v in panel else f"  {v:<26}   0")
    cruzados, internos = [], []
    for a, b in itertools.combinations([v for v in FAMILIA if v in panel], 2):
        r = parcial(panel, a, b)
        if not r:
            continue
        r.update({"a": a, "b": b, "fam": FAMILIA[a] + FAMILIA[b]})
        (internos if FAMILIA[a] == FAMILIA[b] else cruzados).append(r)
    q = bh(np.array([r["p"] for r in cruzados]))
    for r, qq in zip(cruzados, q):
        r["q"] = float(qq)
        r["candidato"] = bool(qq < UMBRAL_Q and abs(r["rho"]) >= UMBRAL_RHO and r["estable_por_depto"])
    cruzados.sort(key=lambda r: r["q"])
    print(f"\nPares entre familias evaluados: {len(cruzados)}; candidatos: {sum(r['candidato'] for r in cruzados)}")
    print("\nTop 25 por q (marca * = candidato segun el protocolo):")
    for r in cruzados[:25]:
        print(f"{'*' if r['candidato'] else ' '} {r['a']:<24}{r['b']:<26} rho={r['rho']:+.2f} n={r['n']:<4} q={r['q']:.4f} estable={r['estable_por_depto']}")
    print("\nComprobacion de consistencia (pares dentro de la misma familia; mecanicos):")
    for r in sorted(internos, key=lambda r: -abs(r["rho"]))[:8]:
        print(f"  {r['a']:<24}{r['b']:<26} rho={r['rho']:+.2f} n={r['n']}")
    (AQUI / "barrido_caribe_resultados.json").write_text(json.dumps({"n_panel": len(panel), "cruzados": cruzados, "internos": internos}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
