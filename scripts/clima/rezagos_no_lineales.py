"""Experimento de PROTOCOLO_REZAGOS_NO_LINEALES.md: ONI (x1) y TNA (x2) con rezagos h..h+8 -> lluvia (y1) y temperatura (y2) del Caribe colombiano.
Modelos M0..M4 fijos; validación cruzada por bloques contiguos con purga de 12 meses; IC por bootstrap de bloques móviles. Uso: python rezagos_no_lineales.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "macro"))
import enso_energia as E  # noqa: E402  (oni())

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CARIBE = ("08", "13", "20", "23", "44", "47", "70")
HORIZONTES, NLAG, K_BLOQUES, PURGA, ALFA, N_BOOT, BLOQUE = (1, 3), 9, 6, 12, 10.0, 2000, 12
MIN_EST, MIN_N_OBS = 5, 200
RNG = np.random.default_rng(20261108)


# ---------------------------------------------------------------- datos
def tna() -> pd.Series:
    out = {}
    for ln in (AQUI / "_cache" / "tna.data").read_text(encoding="utf-8").splitlines()[1:]:
        p = ln.split()
        if len(p) == 13 and p[0].isdigit():
            for m, v in enumerate(p[1:], 1):
                if float(v) > -90:
                    out[pd.Timestamp(int(p[0]), m, 1)] = float(v)
    return pd.Series(out).sort_index()


def lluvia_regional() -> pd.Series:
    serie = {}
    for f in ("chirps_mensual_colombia_1981_2018.json", "chirps_mensual_colombia.json"):
        d = json.loads((RAIZ / "scripts" / "satelite" / f).read_text(encoding="utf-8"))
        mun = [v["precip_mm"] for k, v in d["municipios"].items() if k[:2] in CARIBE]
        for i, m in enumerate(d["meses"]):
            serie[pd.Timestamp(m + "-01")] = float(np.mean([x[i] for x in mun]))
    return pd.Series(serie).sort_index()


def matriz_temperatura() -> pd.DataFrame:
    d = pd.DataFrame(json.loads((AQUI / "_cache" / "temperatura_caribe_max.json").read_text(encoding="utf-8")))
    d["f"] = pd.to_datetime(d.mes).dt.to_period("M").dt.to_timestamp(); d["t"] = d.t.astype(float); d["n"] = d.n.astype(int)
    d = d[d.n >= MIN_N_OBS]
    return d.pivot_table(index="f", columns="nombreestacion", values="t").sort_index()


def y_estandarizada(kind: str, crudo, idx_ent: np.ndarray) -> pd.Series:
    """Anomalía estandarizada por mes calendario usando SOLO los meses de entrenamiento `idx_ent` (posiciones en el índice de `crudo`)."""
    if kind == "lluvia":
        s = crudo.copy()
    else:   # cada estación respecto de su climatología de entrenamiento, luego media regional con >= MIN_EST estaciones
        T = crudo; ent = T.iloc[idx_ent]; an = T.copy()
        for c in T.columns:
            clim = ent[c].groupby(ent.index.month).agg(["mean", "count"])
            ok = clim["count"] >= 3
            an[c] = T[c] - T.index.month.map(clim["mean"].where(ok)).to_numpy()
        s = an.mean(axis=1).where(an.notna().sum(axis=1) >= MIN_EST)
    ent = s.iloc[idx_ent]; media = ent.groupby(ent.index.month).mean(); sd = ent.groupby(ent.index.month).std().clip(lower=1e-6)
    return (s - s.index.month.map(media).to_numpy()) / s.index.month.map(sd).to_numpy()


def construir_X(idx: pd.DatetimeIndex, x1: pd.Series, x2: pd.Series, h: int) -> pd.DataFrame:
    cols = {}
    for nombre, x in (("oni", x1), ("tna", x2)):
        for L in range(h, h + NLAG):
            cols[f"{nombre}_L{L}"] = x.reindex(idx - pd.DateOffset(months=L)).to_numpy()
    X = pd.DataFrame(cols, index=idx)
    X["sin"] = np.sin(2 * np.pi * idx.month / 12); X["cos"] = np.cos(2 * np.pi * idx.month / 12)
    return X


def variantes(X: pd.DataFrame) -> dict[str, pd.DataFrame]:
    lags = [c for c in X.columns if c.startswith(("oni_", "tna_"))]
    M1 = X.copy()
    M1s = X.copy()
    for c in lags:
        M1s[c + "_s"] = X[c] * X["sin"]; M1s[c + "_c"] = X[c] * X["cos"]
    m1 = X[[c for c in lags if c.startswith("oni_")]].mean(axis=1); m2 = X[[c for c in lags if c.startswith("tna_")]].mean(axis=1)
    M4 = X.copy(); M4["oni_m"], M4["tna_m"], M4["prod"], M4["oni2"], M4["tna2"] = m1, m2, m1 * m2, m1 ** 2, m2 ** 2
    return {"M1": M1, "M1s": M1s, "M2": X, "M3": X, "M4": M4}


def modelo(nombre: str):
    if nombre in ("M1", "M1s", "M4"):
        return make_pipeline(StandardScaler(), Ridge(alpha=ALFA))
    if nombre == "M2":
        return make_pipeline(SplineTransformer(n_knots=4, degree=3, include_bias=False), StandardScaler(), Ridge(alpha=ALFA))
    return HistGradientBoostingRegressor(max_depth=3, max_iter=150, learning_rate=0.05, min_samples_leaf=20, random_state=0)


def bloques_movil(n: int):
    nb = int(np.ceil(n / BLOQUE))
    for _ in range(B := N_BOOT):
        ini = RNG.integers(0, max(1, n - BLOQUE + 1), nb)
        yield np.concatenate([np.arange(i, min(i + BLOQUE, n)) for i in ini])[:n]


def holm(p: dict) -> dict:
    orden = sorted(p, key=p.get); out, prev = {}, 0.0
    for i, k in enumerate(orden):
        prev = max(prev, min(1.0, p[k] * (len(orden) - i))); out[k] = prev
    return out


# ---------------------------------------------------------------- experimento
def correr(kind: str, crudo, x1: pd.Series, x2: pd.Series, h: int) -> dict:
    idx_all = crudo.index
    X = construir_X(idx_all, x1, x2, h); validos = np.where(X.notna().all(axis=1).to_numpy() & ~pd.isna(y_estandarizada(kind, crudo, np.arange(len(idx_all)))).to_numpy())[0]
    n = len(validos); tam = int(np.ceil(n / K_BLOQUES)); nombres = ["M1", "M1s", "M2", "M3", "M4"]
    pred = {m: np.full(n, np.nan) for m in nombres}; objetivo = np.full(n, np.nan); mes = idx_all[validos].month.to_numpy()
    for b in range(K_BLOQUES):
        test_pos = np.arange(b * tam, min((b + 1) * tam, n)); t0, t1 = test_pos[0], test_pos[-1]
        ent_pos = np.array([i for i in range(n) if i < t0 - PURGA or i > t1 + PURGA])
        ent_idx = validos[ent_pos]; test_idx = validos[test_pos]
        y = y_estandarizada(kind, crudo, ent_idx).to_numpy()
        # Regla preregistrada (>= MIN_EST estaciones): los meses sin objetivo definido DENTRO de la partición se excluyen del entrenamiento y de la evaluación de todos los modelos.
        ent_idx = ent_idx[~np.isnan(y[ent_idx])]; test_ok = ~np.isnan(y[test_idx])
        test_pos, test_idx = test_pos[test_ok], test_idx[test_ok]; objetivo[test_pos] = y[test_idx]
        V = variantes(X)
        for m in nombres:
            mod = modelo(m).fit(V[m].iloc[ent_idx].to_numpy(), y[ent_idx]); pred[m][test_pos] = mod.predict(V[m].iloc[test_idx].to_numpy())
    ok = ~np.isnan(objetivo); e0 = objetivo[ok] ** 2; mse0 = e0.mean()
    ee = {m: (objetivo[ok] - pred[m][ok]) ** 2 for m in nombres}; mes = mes[ok]; m_ = len(e0)
    boots = list(bloques_movil(m_))
    def pvalor(d: np.ndarray) -> tuple[float, float, float]:
        bs = np.array([d[ix].mean() for ix in boots]); return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), float((np.sum(bs >= 0) + 1) / (len(bs) + 1))
    res = {"n": int(m_), "mse0": float(mse0), "skill": {m: float(1 - ee[m].mean() / mse0) for m in nombres}}
    res["vs_M0"] = {m: dict(zip(("dif", "lo", "hi", "p"), pvalor(ee[m] - e0))) for m in nombres}
    res["vs_M1s"] = {m: dict(zip(("dif", "lo", "hi", "p"), pvalor(ee[m] - ee["M1s"]))) for m in ("M2", "M3", "M4")}
    est = {"DEF": (12, 1, 2), "MAM": (3, 4, 5), "JJA": (6, 7, 8), "SON": (9, 10, 11)}
    res["estacion"] = {s: {m: float(1 - ee[m][np.isin(mes, ms)].mean() / e0[np.isin(mes, ms)].mean()) for m in ("M1s", "M2", "M3")} for s, ms in est.items()}
    return res


def respuesta_por_rezago(kind: str, crudo, x1, x2, h: int) -> dict:
    idx = crudo.index; X = construir_X(idx, x1, x2, h); y = y_estandarizada(kind, crudo, np.arange(len(idx))).to_numpy(); ok = X.notna().all(axis=1).to_numpy() & ~np.isnan(y)
    Z = X.iloc[:, :2 * NLAG]; mod = make_pipeline(StandardScaler(), Ridge(alpha=ALFA)).fit(Z[ok], y[ok])
    c = mod[-1].coef_; return {"oni": c[:NLAG].round(3).tolist(), "tna": c[NLAG:].round(3).tolist()}


def tendencia(crudo_temp: pd.DataFrame) -> dict:
    s = (crudo_temp - crudo_temp.groupby(crudo_temp.index.month).transform("mean")).mean(axis=1).where(crudo_temp.notna().sum(axis=1) >= MIN_EST).dropna()
    t = (s.index.year + (s.index.month - 0.5) / 12).to_numpy(); v = s.to_numpy(); pend = []
    for i in range(0, len(t), 1):
        pass
    from scipy.stats import theilslopes
    sl = theilslopes(v, t)[0]; bs = []
    for ix in bloques_movil(len(v)):
        bs.append(theilslopes(v[ix], t[ix])[0])
    lo, hi = np.percentile(bs, [2.5, 97.5]); se = np.std(bs)
    return {"pendiente_decada": float(10 * sl), "ic": [float(10 * lo), float(10 * hi)], "se_decada": float(10 * se), "mde_decada": float(10 * 2.8 * se), "n_meses": int(len(v))}


def main() -> None:
    x1 = E.oni(); x2 = tna(); lluvia = lluvia_regional(); T = matriz_temperatura()
    print(f"ONI {x1.index.min():%Y-%m}..{x1.index.max():%Y-%m}; TNA {x2.index.min():%Y-%m}..{x2.index.max():%Y-%m}; lluvia Caribe {len(lluvia)} meses ({lluvia.index.min():%Y-%m}..{lluvia.index.max():%Y-%m}); "
          f"temperatura: {T.shape[1]} estaciones, {len(T)} meses ({T.index.min():%Y-%m}..{T.index.max():%Y-%m})")
    resultados = {}
    for kind, crudo in (("lluvia", lluvia), ("temperatura", T)):
        for h in HORIZONTES:
            r = correr(kind, crudo, x1, x2, h); resultados[f"{kind}|{h}"] = r
            print(f"\n=== {kind.upper()}, horizonte {h} mes(es): n = {r['n']} meses fuera de muestra; MSE de la climatología (M0) = {r['mse0']:.3f}")
            print("   Habilidad (1 − MSE/MSE_M0): " + "  ".join(f"{m} {v:+.3f}" for m, v in r["skill"].items()))
            h1 = holm({m: r["vs_M0"][m]["p"] for m in ("M1s",)})
            x = r["vs_M0"]["M1s"]; print(f"   Confirmatoria 1, M1s vs M0: ΔMSE {x['dif']:+.4f} [{x['lo']:+.4f}, {x['hi']:+.4f}] p = {x['p']:.4f}")
            h2 = holm({m: r["vs_M1s"][m]["p"] for m in ("M2", "M3", "M4")})
            for m in ("M2", "M3", "M4"):
                x = r["vs_M1s"][m]; r["vs_M1s"][m]["holm"] = h2[m]
                print(f"   Confirmatoria 2, {m} vs M1s: ΔMSE {x['dif']:+.4f} [{x['lo']:+.4f}, {x['hi']:+.4f}] p Holm = {h2[m]:.3f}")
            print("   Habilidad por estación (M1s/M2/M3): " + "; ".join(f"{s}: " + "/".join(f"{v:+.2f}" for v in d.values()) for s, d in r["estacion"].items()))
    # Holm de la confirmatoria 1 sobre las 4 combinaciones
    p1 = holm({k: v["vs_M0"]["M1s"]["p"] for k, v in resultados.items()})
    print("\nConfirmatoria 1, Holm sobre las 4 combinaciones: " + "; ".join(f"{k}: p {v:.3f}{' ✔' if v < 0.05 else ''}" for k, v in p1.items()))
    print("Conclusión no lineal: " + "; ".join(f"{k}: " + ("SÍ" if any(r['vs_M1s'][m]['holm'] < 0.05 and r['vs_M1s'][m]['dif'] < 0 and r['skill'][m] > 0 for m in ('M2', 'M3', 'M4')) else "no") for k, r in resultados.items()))
    print("\nRespuesta lineal por rezago (coeficientes estandarizados; rezagos h..h+8):")
    for kind, crudo in (("lluvia", lluvia), ("temperatura", T)):
        rr = respuesta_por_rezago(kind, crudo, x1, x2, 1); print(f"   {kind} h=1  ONI: {rr['oni']}\n   {kind} h=1  TNA: {rr['tna']}")
    tr = tendencia(T); print(f"\nTendencia de la temperatura máxima horaria del Caribe: {tr['pendiente_decada']:+.2f} °C/década IC95 % [{tr['ic'][0]:+.2f}, {tr['ic'][1]:+.2f}]; efecto mínimo detectable ≈ {tr['mde_decada']:.2f} °C/década ({tr['n_meses']} meses)")
    (AQUI / "rezagos_no_lineales_resultados.json").write_text(json.dumps({"resultados": resultados, "holm_c1": p1, "tendencia": tr}, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
