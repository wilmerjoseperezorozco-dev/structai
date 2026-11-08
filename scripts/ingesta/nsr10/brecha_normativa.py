"""Brecha A-4 vs SGC y poblacion expuesta. Protocolo: PROTOCOLO_BRECHA_NORMATIVA.md"""
import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

AQUI = Path(__file__).resolve().parent
PANEL = AQUI.parents[1] / "satelite" / "v1_panel.csv"
RNG = np.random.default_rng(7)
N_BOOT = 2000


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def main() -> None:
    d = json.loads((AQUI / "auditoria_a4_vs_sgc.json").read_text(encoding="utf-8"))
    dif = [r for r in d["diferencias"] if "aa" in r["difs"] or "av" in r["difs"]]
    panel = {r["codigo"].zfill(5): r for r in csv.DictReader(open(PANEL, encoding="utf-8"))}
    filas = []
    for r in dif:
        f = {"codigo": r["codigo"], "municipio": r["municipio"], "depto": r["departamento"], "cambia_zona": "zona" in r["difs"]}
        for k in ("aa", "av"):
            if k in r["difs"]:
                a4, sgc = r["difs"][k]
                f[k] = {"a4": a4, "sgc": sgc, "brecha_rel": round((max(a4, sgc) - min(a4, sgc)) / min(a4, sgc), 3), "sgc_mayor": sgc > a4}
        p = panel.get(r["codigo"])
        f["poblacion"] = num(p["poblacion"]) if p else None
        f["pct_mat_vulnerable"] = num(p["pct_mat_vulnerable"]) if p else None
        f["nbi"] = num(p["nbi2018"]) if p else None
        filas.append(f)

    out = {"n": len(filas), "con_aa": sum("aa" in f for f in filas), "con_av": sum("av" in f for f in filas),
           "cambian_zona": sum(f["cambia_zona"] for f in filas), "en_panel": sum(f["poblacion"] is not None for f in filas)}
    for k in ("aa", "av"):
        b = [f[k]["brecha_rel"] for f in filas if k in f]
        out[f"brecha_{k}"] = {"n": len(b), "min": min(b), "mediana": float(np.median(b)), "max": max(b)}
    # escenarios
    def pob(cond):
        return float(sum(f["poblacion"] for f in filas if f["poblacion"] is not None and cond(f)))
    sgc_may = lambda f: any(f[k]["sgc_mayor"] for k in ("aa", "av") if k in f)  # noqa: E731
    a4_may = lambda f: any(not f[k]["sgc_mayor"] for k in ("aa", "av") if k in f)  # noqa: E731
    out["poblacion_total_en_panel"] = pob(lambda f: True)
    out["pob_sgc_mayor"] = pob(sgc_may)
    out["pob_a4_mayor"] = pob(a4_may)
    out["n_sgc_mayor"] = sum(sgc_may(f) for f in filas)
    out["n_a4_mayor"] = sum(a4_may(f) for f in filas)
    # solo Aa
    out["pob_aa_sgc_mayor"] = pob(lambda f: "aa" in f and f["aa"]["sgc_mayor"])
    out["pob_aa_a4_mayor"] = pob(lambda f: "aa" in f and not f["aa"]["sgc_mayor"])

    # B1
    cods = {f["codigo"] for f in filas}
    gA = np.array([f["pct_mat_vulnerable"] for f in filas if f["pct_mat_vulnerable"] is not None and not np.isnan(f["pct_mat_vulnerable"])])
    rest = [(num(r["pct_mat_vulnerable"]), r["codigo"][:2].zfill(2)) for c, r in panel.items() if c not in cods and r["pct_mat_vulnerable"]]
    gB = np.array([v for v, _ in rest]); gBd = np.array([d_ for _, d_ in rest])
    u = mannwhitneyu(gA, gB, alternative="two-sided")
    dif_med = float(np.median(gA) - np.median(gB))
    deptoA = np.array([f["codigo"][:2] for f in filas if f["pct_mat_vulnerable"] is not None and not np.isnan(f["pct_mat_vulnerable"])])
    deps = np.unique(np.concatenate([deptoA, gBd]))
    bs = []
    for _ in range(N_BOOT):
        ds = RNG.choice(deps, len(deps), replace=True)
        a = np.concatenate([gA[deptoA == x] for x in ds]); b = np.concatenate([gB[gBd == x] for x in ds])
        if len(a) and len(b):
            bs.append(np.median(a) - np.median(b))
    out["B1"] = {"n_29": int(len(gA)), "n_resto": int(len(gB)), "mediana_29": float(np.median(gA)), "mediana_resto": float(np.median(gB)),
                 "dif_medianas": dif_med, "IC95": [float(x) for x in np.percentile(bs, [2.5, 97.5])], "p_MW": float(u.pvalue),
                 "cumple": bool(u.pvalue < 0.05)}
    top = sorted((f for f in filas if f["poblacion"]), key=lambda f: -f["poblacion"] * max(f[k]["brecha_rel"] for k in ("aa", "av") if k in f))[:10]
    out["top10"] = [{"municipio": f["municipio"], "depto": f["depto"], "poblacion": f["poblacion"], "aa": f.get("aa"), "av": f.get("av"), "cambia_zona": f["cambia_zona"]} for f in top]
    out["sin_panel"] = [f"{f['municipio']} ({f['depto']})" for f in filas if f["poblacion"] is None]
    out["tabla"] = filas
    (AQUI / "brecha_normativa.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "tabla"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
