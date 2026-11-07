"""Frecuencia de crecientes con Q_MX_A del IDEAM (protocolo seccion 21)."""
from __future__ import annotations

import csv
import glob
import json
import os
import sys
import unicodedata
import warnings
from collections import Counter

import numpy as np
from scipy import stats

warnings.filterwarnings("ignore")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import _datos_caribe as dc  # noqa: E402

RNG = np.random.default_rng(20261107)
T_RET = [2, 5, 10, 25, 50, 100]
N_BOOT_IC, N_BOOT_KS, N_BOOT_BLOQ, MIN_ANIOS = 300, 200, 2000, 30
CARIBE = {"ATLANTICO", "MAGDALENA", "BOLIVAR", "CORDOBA", "SUCRE", "CESAR", "LA GUAJIRA"}


def leer(f):
    s = {}
    for r in csv.DictReader(open(f, encoding="utf-8")):
        try:
            s[int(r["fechaObservacion"][:4])] = float(r["valorObservado"])
        except (ValueError, KeyError):
            pass
    return s


def ajustar_gev(x):
    return stats.genextreme.fit(x)


def q_gev(p, T):
    return stats.genextreme.ppf(1 - 1 / np.asarray(T, float), *p)


def ajustar_lp3(x):
    y = np.log10(x)
    return stats.skew(y, bias=False), y.mean(), y.std(ddof=1)


def q_lp3(p, T):
    g, m, s = p
    return 10 ** stats.pearson3.ppf(1 - 1 / np.asarray(T, float), g, loc=m, scale=s)


def ll_lp3(p, x):
    g, m, s = p
    y = np.log10(x)
    return float((stats.pearson3.logpdf(y, g, loc=m, scale=s) - np.log(x * np.log(10))).sum())


def ks_boot(x, p):
    d0 = stats.kstest(x, stats.genextreme.cdf, args=p).statistic
    n = 0
    for _ in range(N_BOOT_KS):
        s = stats.genextreme.rvs(*p, size=len(x), random_state=int(RNG.integers(1 << 31)))
        try:
            n += stats.kstest(s, stats.genextreme.cdf, args=ajustar_gev(s)).statistic >= d0
        except Exception:
            pass
    return (n + 1) / (N_BOOT_KS + 1)


def ic_q50(x, p):
    v = []
    for _ in range(N_BOOT_IC):
        s = stats.genextreme.rvs(*p, size=len(x), random_state=int(RNG.integers(1 << 31)))
        try:
            v.append(float(q_gev(ajustar_gev(s), 50)))
        except Exception:
            pass
    return tuple(np.percentile(v, [2.5, 97.5])) if len(v) > 50 else (np.nan, np.nan)


def cargar_estaciones():
    sb, est, ini = dc._sb(), {}, 0
    while True:
        pg = sb.table("ideam_estaciones_caudal").select("codigo,departamento").range(ini, ini + 999).execute().data or []
        est.update({e["codigo"]: e for e in pg})
        if len(pg) < 1000:
            return est
        ini += 1000


def seleccionar(est):
    norm = lambda s: unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().upper()
    filas, descartes = [], Counter()
    for f in sorted(glob.glob(os.path.join(AQUI, "_cache", "ideam", "Q_MX_A", "*.csv"))):
        cod = os.path.basename(f).split("-")[0]
        s = {a: v for a, v in leer(f).items() if v > 0}
        if len(s) < MIN_ANIOS or max(s) < 2000:
            descartes["registro corto o sin datos desde 2000"] += 1
            continue
        anios = sorted(s)
        x = np.array([s[a] for a in anios])
        rep = 1 - len(set(np.round(x, 6))) / len(x)
        filas.append({"codigo": cod, "depto": norm(est.get(cod, {}).get("departamento", "SIN")), "anios": anios, "x": x, "rep": rep})
    print(f"Estaciones incluidas: {len(filas)}; descartadas: {dict(descartes)}; con >10% de valores repetidos: {sum(f['rep'] > 0.10 for f in filas)}", flush=True)
    return filas


def procesar(f):
    x, n = f["x"], len(f["x"])
    k = int(round(0.7 * n))
    pg_all, pg_tr = ajustar_gev(x), ajustar_gev(x[:k])
    pl_all, pl_tr = ajustar_lp3(x), ajustar_lp3(x[:k])
    gum_tr = stats.gumbel_r.fit(x[:k])
    test = x[k:]
    tau = stats.kendalltau(f["anios"], x)
    lo, hi = ic_q50(x, pg_all)
    return {"codigo": f["codigo"], "depto": f["depto"], "n": n, "rep": f["rep"], "xi": float(-pg_all[0]), "p_ks": ks_boot(x, pg_all),
            "exc2": float((test > q_gev(pg_tr, 2)).mean()), "exc10": float((test > q_gev(pg_tr, 10)).mean()), "n_test": len(test),
            "llg": float(stats.genextreme.logpdf(test, *pg_tr).sum()), "lll": ll_lp3(pl_tr, test),
            "llgum": float(stats.gumbel_r.logpdf(test, *gum_tr).sum()), "mk_p": float(tau.pvalue), "mk_tau": float(tau.statistic),
            "q_gev": dict(zip(map(str, T_RET), map(float, q_gev(pg_all, T_RET)))),
            "q_lp3": dict(zip(map(str, T_RET), map(float, q_lp3(pl_all, T_RET)))), "q50_ic": [float(lo), float(hi)]}


def bloques(res, estad):
    dep = np.array([r["depto"] for r in res])
    u, out = np.unique(dep), []
    for _ in range(N_BOOT_BLOQ):
        ix = np.concatenate([np.where(dep == d)[0] for d in RNG.choice(u, len(u), replace=True)])
        out.append(estad(ix))
    return np.percentile(out, [2.5, 97.5])


def resumen(R, etiqueta):
    print(f"\n===== {etiqueta}: {len(R)} estaciones =====")
    w = np.array([r["n_test"] for r in R], float)
    for k, T in (("exc2", 2), ("exc10", 10)):
        e = np.array([r[k] for r in R])
        pt = float((e * w).sum() / w.sum())
        lo, hi = bloques(R, lambda ix: (e[ix] * w[ix]).sum() / w[ix].sum())
        print(f"C1 fraccion de anios de prueba que supera Q{T}: {pt:.3f} IC95% [{lo:.3f}, {hi:.3f}] (esperado {1 / T:.2f}) -> {'calibrado' if lo <= 1 / T <= hi else 'NO calibrado'}")
    rech = np.array([r["p_ks"] < 0.05 for r in R])
    print(f"C2 estaciones con GEV rechazado (KS bootstrap p<0.05): {rech.mean():.1%} (criterio <= 15%) -> {'cumple' if rech.mean() <= 0.15 else 'NO cumple'}")
    d = np.array([r["llg"] - r["lll"] for r in R])
    gana = (d > 0).astype(float)
    lo, hi = bloques(R, lambda ix: gana[ix].mean())
    print(f"C3 GEV vs LP3 (log-verosimilitud predictiva): GEV gana en {gana.mean():.1%} IC95% [{lo:.1%}, {hi:.1%}]; mediana diferencia {np.median(d):+.2f}")
    dg = np.array([r["llg"] - r["llgum"] for r in R])
    print(f"   (referencia) GEV vs Gumbel: GEV gana en {(dg > 0).mean():.1%}")
    mk = np.array([r["mk_p"] < 0.05 for r in R])
    pos = np.array([r["mk_tau"] > 0 for r in R])
    print(f"Tendencia significativa (Mann-Kendall 5%): {mk.mean():.1%} (azar ~5%); de ellas al alza {pos[mk].mean() if mk.any() else float('nan'):.0%}")
    ra = np.array([(r["q50_ic"][1] - r["q50_ic"][0]) / r["q_gev"]["50"] for r in R if np.isfinite(r["q50_ic"][0])])
    print(f"Incertidumbre: mediana (ancho IC95% de Q50 / Q50) = {np.median(ra):.2f}; xi fuera de [-0.5, 0.5]: {np.mean([abs(r['xi']) > 0.5 for r in R]):.1%}")
    rr = np.array([r["q_gev"]["100"] / r["q_gev"]["10"] for r in R])
    print(f"Razon Q100/Q10 (GEV) mediana {np.median(rr):.2f}")


def main() -> None:
    filas = seleccionar(cargar_estaciones())
    res = []
    for i, f in enumerate(filas):
        try:
            res.append(procesar(f))
        except Exception as e:
            print("  falla", f["codigo"], str(e)[:60])
        if i % 50 == 49:
            print(f"  {i + 1}/{len(filas)}", flush=True)
    with open(os.path.join(AQUI, "frecuencia_crecientes_ideam.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False)
    resumen(res, "TODAS las estaciones incluidas")
    limpias = [r for r in res if r["rep"] <= 0.10]
    if len(limpias) < len(res):
        resumen(limpias, "SIN valores repetidos (> 10%)")
    caribe = [r for r in res if r["depto"] in CARIBE]
    if len(caribe) >= 30:
        resumen(caribe, "Caribe")


if __name__ == "__main__":
    main()
