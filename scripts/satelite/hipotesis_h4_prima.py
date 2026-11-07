"""H4′ (protocolo §25): ventanas de ONI y agrupación regional de la respuesta de los máximos anuales a ENSO, con validación cronológica 70/30.
Candidatos: por estación (μ0 + μ1·ONI_W) y agrupado regional (μ0·exp(s_r·ONI_W), s_r de efectos fijos con años <= el corte de la estación).
Uso: python hipotesis_h4_prima.py [n_estaciones_prueba]"""
from __future__ import annotations

import json
import math
import os
import sys
import warnings
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

warnings.filterwarnings("ignore")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "macro"))
import frecuencia_crecientes_ideam as F  # noqa: E402
import enso_energia as E  # noqa: E402
import hipotesis_h4_h5_crecientes as H4  # noqa: E402  (ajustar_h4, ll_h4, NOMBRE_A_REGION)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ONI_M = E.oni()
VENT = {"W0": lambda a: [(a, m) for m in range(1, 13)], "W1": lambda a: [(a - 1, 12), (a, 1), (a, 2)],
        "W2": lambda a: [(a, 9), (a, 10), (a, 11)], "W3": lambda a: [(a - 1, m) for m in range(1, 13)]}
CONF = [("W1", "estacion"), ("W2", "estacion"), ("W1", "regional"), ("W2", "regional")]
EXPLO = [("W3", "estacion"), ("W0", "regional")]
POOL_W = ("W0", "W1", "W2")
NB = 2000
RNG = np.random.default_rng(20261108)


def oni_ventana(a: int, w: str) -> float:
    v = [ONI_M.get(pd.Timestamp(y, m, 1), np.nan) for y, m in VENT[w](a)]
    return float(np.mean(v)) if not np.any(np.isnan(v)) else float("nan")


ONI_W = {w: {a: oni_ventana(a, w) for a in range(1945, 2030)} for w in VENT}   # a nivel de módulo (procesos 'spawn')


def nll_reg(theta, x, o, s):
    c, mu0, lsc = theta
    loc = mu0 * np.exp(s * o)
    v = stats.genextreme.logpdf(x, c, loc=loc, scale=math.exp(lsc)).sum()
    return -v if np.isfinite(v) else 1e12


def procesar(t):
    x, o, k, slopes, p0 = np.array(t["x"]), {w: np.array(v) for w, v in t["o"].items()}, t["k"], t["slopes"], None
    out = {"codigo": t["codigo"], "depto": t["depto"], "region": t["region"], "dll": {}, "sd": {}}
    try:
        p0 = F.ajustar_gev(x[:k])
        pred0 = float(stats.genextreme.logpdf(x[k:], *p0).sum())
    except Exception:
        return None
    for w in ("W1", "W2", "W3"):
        try:
            th, _ = H4.ajustar_h4(x[:k], o[w][:k], p0)
            out["dll"][f"{w}|estacion"] = H4.ll_h4(th, x[k:], o[w][k:]) - pred0
        except Exception:
            out["dll"][f"{w}|estacion"] = None
    for w in POOL_W:
        try:
            s = slopes[w]
            r = minimize(nll_reg, [p0[0], p0[1], math.log(max(p0[2], 1e-9))], args=(x[:k], o[w][:k], s), method="Nelder-Mead",
                         options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-8})
            c, mu0, lsc = r.x
            out["dll"][f"{w}|regional"] = float(stats.genextreme.logpdf(x[k:], c, loc=mu0 * np.exp(s * o[w][k:]), scale=math.exp(lsc)).sum()) - pred0
        except Exception:
            out["dll"][f"{w}|regional"] = None
    for w in ("W1", "W2"):
        out["sd"][w] = [float(np.std(o[w][:k])), float(np.std(o[w][k:]))]
    return out


def pendientes(est: list[dict]) -> None:
    """s_r por estación y ventana: efectos fijos con las observaciones de la región con año <= último año de calibración de la estación."""
    por_region = defaultdict(list)
    for e in est:
        por_region[e["region"]].append(e)
    for e in est:
        corte = e["anios"][e["k"] - 1]; e["slopes"] = {}
        for w in POOL_W:
            num = den = 0.0
            for g in por_region[e["region"]]:
                m = g["anios"] <= corte
                if m.sum() < 10:
                    continue
                z = np.log(g["x"][m]); z = z - z.mean(); o = g["o"][w][m]; o = o - o.mean()
                num += float((o * z).sum()); den += float((o * o).sum())
            e["slopes"][w] = num / den if den > 0 else 0.0


def cluster_boot(dep: np.ndarray, v: np.ndarray):
    u = np.unique(dep); idx = {d: np.where(dep == d)[0] for d in u}
    m = np.array([v[np.concatenate([idx[d] for d in RNG.choice(u, len(u), replace=True)])].mean() for _ in range(NB)])
    return np.percentile(m, [2.5, 97.5]), m


def p_bilat(m: np.ndarray, nulo: float) -> float:
    return float(min(1.0, 2 * min((np.sum(m <= nulo) + 1) / (NB + 1), (np.sum(m >= nulo) + 1) / (NB + 1))))


def main() -> None:
    filas = F.seleccionar(F.cargar_estaciones())
    if len(sys.argv) > 1:
        filas = filas[:int(sys.argv[1])]
    est = []
    for f in filas:
        anios = np.array(f["anios"]); x = np.array(f["x"], float)
        ok = np.array([all(np.isfinite(ONI_W[w].get(int(a), np.nan)) for w in VENT) for a in anios])
        anios, x = anios[ok], x[ok]
        if len(x) < 30:
            continue
        o = {w: np.array([ONI_W[w][int(a)] for a in anios]) for w in VENT}
        est.append({"codigo": f["codigo"], "depto": f["depto"], "region": H4.NOMBRE_A_REGION.get(f["depto"], "Andina"), "anios": anios, "x": x, "o": o, "k": int(round(0.7 * len(x)))})
    print(f"Estaciones con >= 30 años y ONI completo en las 4 ventanas: {len(est)}", flush=True)
    pendientes(est)
    print("Pendiente regional s_r (ln x por °C de ONI), mediana entre estaciones de cada región, ventana W1: " +
          ", ".join(f"{r}: {np.median([e['slopes']['W1'] for e in est if e['region'] == r]):+.3f}" for r in sorted({e['region'] for e in est})), flush=True)
    tareas = [{"codigo": e["codigo"], "depto": e["depto"], "region": e["region"], "x": e["x"].tolist(), "o": {w: v.tolist() for w, v in e["o"].items()}, "k": e["k"], "slopes": e["slopes"]} for e in est]
    with ProcessPoolExecutor(3) as ex:
        res = [r for r in ex.map(procesar, tareas, chunksize=2) if r]
    dep = np.array([r["depto"] for r in res]); reg = np.array([r["region"] for r in res])
    print(f"Estaciones evaluadas: {len(res)} en {len(np.unique(dep))} departamentos\n", flush=True)
    sal, pvals = {}, {}
    for fam, lista in (("CONFIRMATORIA", CONF), ("EXPLORATORIA", EXPLO)):
        print(f"{fam}:")
        for w, tipo in lista:
            k = f"{w}|{tipo}"; v = np.array([r["dll"].get(k) for r in res], dtype=object)
            val = np.array([x is not None for x in v])
            d = np.array([x if ok else np.nan for x, ok in zip(v, val)], float)
            fin = np.isfinite(d)
            gana = (d > 0).astype(float)[val]; (lo, hi), m = cluster_boot(dep[val], gana)   # convención de H4: Δ=+inf gana, nan/-inf pierde
            p = p_bilat(m, 0.5); sal[k] = {"gana": float(gana.mean()), "ic": [float(lo), float(hi)], "p": p, "mediana_dll": float(np.median(d[fin])) if fin.any() else None,
                                           "n": int(val.sum()), "fallos": int((~val).sum()), "delta_no_finito": int((val & ~fin).sum())}
            if fam == "CONFIRMATORIA":
                pvals[k] = p
            print(f"   {w} {tipo:>8}: gana {gana.mean():.3f} IC95% bloques [{lo:.3f}, {hi:.3f}]; mediana Δ (finitos) = {sal[k]['mediana_dll']:+.3f}; n = {val.sum()} (ajuste fallido {(~val).sum()}; Δ no finito {(val & ~fin).sum()}); p = {p:.3f}", flush=True)
    orden = sorted(pvals, key=pvals.get); ajust, prev = {}, 0.0
    for i, k in enumerate(orden):
        prev = max(prev, min(1.0, pvals[k] * (len(orden) - i))); ajust[k] = prev
    print("\nHolm (4 pruebas confirmatorias):")
    for k in orden:
        cumple = ajust[k] < 0.05 and sal[k]["ic"][0] > 0.5
        sal[k]["holm"] = ajust[k]; sal[k]["cumple"] = bool(cumple)
        print(f"   {k:>16}: p ajustado {ajust[k]:.3f}; límite inferior {sal[k]['ic'][0]:.3f} -> {'CUMPLE' if cumple else 'no cumple'}")
    print("\nDesglose por región (fracción que gana):")
    for k in [f"{w}|{t}" for w, t in CONF + EXPLO]:
        fila = []
        for r in sorted(set(reg)):
            d = np.array([x["dll"].get(k) for x in res if x["region"] == r], dtype=object)
            d = np.array([v for v in d if v is not None and np.isfinite(v)], float)
            fila.append(f"{r} {np.mean(d > 0):.2f} (n={len(d)})" if len(d) else f"{r} -")
        print(f"   {k:>16}: " + "; ".join(fila))
    sd = {w: np.median([[r["sd"][w][0], r["sd"][w][1]] for r in res], axis=0) for w in ("W1", "W2")}
    print("\nDiagnóstico de régimen (mediana de la desviación estándar del ONI, calibración vs prueba): " +
          "; ".join(f"{w}: {a:.2f} vs {b:.2f}" for w, (a, b) in sd.items()))
    with open(os.path.join(AQUI, "hipotesis_h4_prima.json"), "w", encoding="utf-8") as fh:
        json.dump({"resumen": sal, "n": len(res)}, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
