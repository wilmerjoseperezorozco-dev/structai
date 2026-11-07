"""Comparación 2 de PROTOCOLO_COMPARATIVO.md: detectores nuevos (M1b IQR, M3 AR(2), M4 bosque de aislamiento) frente a M2, con el diseño de inyección de
PROTOCOLO_ANOMALIAS.md (entrenamiento hasta 2009, prueba desde 2010, factor ×2 en un mes, AUC por estación) y bootstrap por departamento. Uso: python comparativo_detectores.py"""
from __future__ import annotations

import json
import sys
import unicodedata
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import anomalias_caudal_ideam as A  # noqa: E402  (cargar, auc, CORTE)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FACTORES = (1.5, 2.0, 3.0)
METODOS = ("B0", "M1", "M2", "M1b", "M3", "M4")
RNG = np.random.default_rng(20261109)
norm = lambda s: unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().upper().strip()


def estacion2(g: pd.DataFrame):
    g = g.dropna().sort_values("fecha"); g = g[g.q > 0]
    if len(g) < 240:
        return None
    if len(g) / ((g.fecha.max().to_period("M") - g.fecha.min().to_period("M")).n + 1) < 0.85:
        return None
    ent, pru = g[g.fecha < A.CORTE], g[g.fecha >= A.CORTE]
    if len(ent) < 120 or len(pru) < 24:
        return None
    lq = np.log(ent.q.to_numpy()); mes_e = ent.fecha.dt.month.to_numpy()
    med = {m: np.median(lq[mes_e == m]) for m in range(1, 13) if (mes_e == m).sum() >= 8}
    if len(med) < 12:
        return None
    mad = {m: max(1.4826 * np.median(np.abs(lq[mes_e == m] - med[m])), 0.05) for m in med}
    iqr = {m: max((np.quantile(lq[mes_e == m], 0.75) - np.quantile(lq[mes_e == m], 0.25)) / 1.349, 0.05) for m in med}
    p90 = {m: np.quantile(ent.q.to_numpy()[mes_e == m], 0.90) for m in med}
    zent = np.array([(l - med[m]) / mad[m] for l, m in zip(lq, mes_e)])
    if len(zent) < 40:
        return None
    r = [np.corrcoef(zent[:-k], zent[k:])[0, 1] for k in (1, 2)]          # Yule-Walker para AR(2)
    phi1, phi2 = np.linalg.solve(np.array([[1, r[0]], [r[0], 1]]), np.array(r))
    phi = r[0]
    iso = IsolationForest(n_estimators=100, random_state=0).fit(np.c_[zent[1:], zent[:-1]])
    pru = pru.copy(); pru["mes"] = pru.fecha.dt.month
    for k in (1, 2):
        pru[f"q{k}"] = pru.q.shift(k); pru[f"f{k}"] = pru.fecha.shift(k)
    per = pru.fecha.dt.to_period("M")
    pru = pru[((per - pru.f1.dt.to_period("M")).map(lambda x: getattr(x, "n", 99)) == 1) & ((per - pru.f2.dt.to_period("M")).map(lambda x: getattr(x, "n", 99)) == 2)]
    if len(pru) < 24:
        return None
    mes = pru.mes.to_numpy(); q = pru.q.to_numpy(); m1 = (mes - 2) % 12 + 1; m2 = (mes - 3) % 12 + 1
    zp = np.array([(np.log(a) - med[m]) / mad[m] for a, m in zip(pru.q1.to_numpy(), m1)])
    zpp = np.array([(np.log(a) - med[m]) / mad[m] for a, m in zip(pru.q2.to_numpy(), m2)])

    def puntajes(qv):
        z = np.array([(np.log(a) - med[m]) / mad[m] for a, m in zip(qv, mes)])
        return {"B0": qv / np.array([p90[m] for m in mes]), "M1": z, "M2": z - phi * zp, "M1b": np.array([(np.log(a) - med[m]) / iqr[m] for a, m in zip(qv, mes)]),
                "M3": z - phi1 * zp - phi2 * zpp, "M4": -iso.score_samples(np.c_[z, zp])}
    base = puntajes(q); out = {"n_prueba": int(len(pru))}
    for f in FACTORES:
        inj = puntajes(q * f)
        for k in METODOS:
            out[f"{k}_{f}"] = A.auc(inj[k], base[k])
    return out


def cluster_ic(dif: np.ndarray, dep: np.ndarray, B: int = 4000):
    u = np.unique(dep); ix = {x: np.where(dep == x)[0] for x in u}
    b = np.array([dif[np.concatenate([ix[x] for x in RNG.choice(u, len(u))])].mean() for _ in range(B)])
    p = min(1.0, 2 * min((np.sum(b <= 0) + 1) / (B + 1), (np.sum(b >= 0) + 1) / (B + 1)))
    return np.percentile(b, [2.5, 97.5]), p


def main() -> None:
    d = A.cargar(); d["fecha"] = pd.to_datetime(d.fecha); d["q"] = pd.to_numeric(d.caudal_m3s, errors="coerce")
    res = {}
    for cod, g in d.groupby("codigo_estacion"):
        r = estacion2(g[["fecha", "q"]])
        if r:
            res[str(cod).zfill(10)] = r
    R = pd.DataFrame(res).T
    m = pd.DataFrame(json.loads((AQUI / "_cache" / "estaciones_meta.json").read_text(encoding="utf-8"))).set_index("codigo"); m.index = m.index.astype(str)
    dep = np.array([norm(m.loc[c, "departamento"]) if c in m.index else "SIN" for c in R.index])
    print(f"Estaciones evaluables con 2 rezagos consecutivos: {len(R)}; departamentos: {len(np.unique(dep))}")
    print("\nAUC medio por método (inyección ×2) y por factor:")
    for f in FACTORES:
        print(f"   ×{f}: " + "  ".join(f"{k} {R[f'{k}_{f}'].astype(float).mean():.4f}" for k in METODOS))
    print("\nConfirmatorio (×2): ΔAUC frente a M2, IC95 % por departamento")
    pv = {}
    for k in ("M1b", "M3", "M4"):
        dif = (R[f"{k}_2.0"] - R["M2_2.0"]).to_numpy(float); (lo, hi), p = cluster_ic(dif, dep); pv[k] = p
        print(f"   {k} − M2: Δ = {dif.mean():+.4f} [{lo:+.4f}, {hi:+.4f}] p = {p:.4f}; mejoran en {100 * (dif > 0).mean():.0f} % de las estaciones")
    orden = sorted(pv, key=pv.get); prev = 0.0
    for i, k in enumerate(orden):
        prev = max(prev, min(1.0, pv[k] * (len(orden) - i))); print(f"   Holm {k}: p ajustado {prev:.4f} -> {'SUPERA a M2' if prev < 0.05 and (R[f'{k}_2.0'] - R['M2_2.0']).mean() > 0 else 'no supera a M2'}")
    dif = (R["M2_2.0"] - R["M4_2.0"]).to_numpy(float); (lo, hi), _ = cluster_ic(dif, dep)
    print(f"\nNo inferioridad de M2 frente al bosque de aislamiento (margen 0,005): M2 − M4 = {dif.mean():+.4f} [{lo:+.4f}, {hi:+.4f}] -> {'M2 es no inferior' if lo > -0.005 else 'no concluyente'}")
    R.to_csv(AQUI / "comparativo_detectores.csv")


if __name__ == "__main__":
    main()
