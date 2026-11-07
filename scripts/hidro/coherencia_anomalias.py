"""Coherencia espacio-temporal de las anomalías de caudal IDEAM (PROTOCOLO_COHERENCIA.md, fijado antes de correr).
C1 sincronía (razón de varianzas + permutación), C2 dependencia de ENSO, C3 alcance espacial. Uso: python coherencia_anomalias.py"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "satelite"))
sys.path.insert(0, str(AQUI.parent / "macro"))
import _datos_caribe as dc  # noqa: E402
import enso_energia as E  # noqa: E402
from hipotesis_h4_h5_crecientes import NOMBRE_A_REGION  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RNG = np.random.default_rng(20261109)
MIN_MESES, MIN_EST, UMBRAL, N_PERM, N_BOOT, BLOQUE = 240, 8, 2.0, 500, 2000, 12
BINS = [0, 50, 100, 200, 400, 800, 1e9]


def norm(s) -> str:
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().upper().strip()


def meta() -> pd.DataFrame:
    f = AQUI / "_cache" / "estaciones_meta.json"
    if not f.exists():
        filas, ini = [], 0
        while True:
            p = dc._sb().table("ideam_estaciones_caudal").select("codigo,departamento,latitud,longitud").range(ini, ini + 999).execute().data or []
            filas += p
            if len(p) < 1000:
                break
            ini += 1000
        f.write_text(json.dumps(filas), encoding="utf-8")
    return pd.DataFrame(json.loads(f.read_text(encoding="utf-8"))).set_index("codigo")


def matriz_z() -> pd.DataFrame:
    d = pd.read_pickle(AQUI / "_cache" / "caudal_historico.pkl")
    d = d[d.caudal_m3s > 0].copy(); d["f"] = pd.to_datetime(d.fecha); d["l"] = np.log(d.caudal_m3s.astype(float))
    P = d.pivot_table(index="f", columns="codigo_estacion", values="l")
    P = P.loc[:, P.notna().sum() >= MIN_MESES]
    Z = pd.DataFrame(index=P.index, columns=P.columns, dtype=float)
    for m in range(1, 13):
        sub = P[P.index.month == m]; med = sub.median(); mad = (1.4826 * (sub - med).abs().median()).clip(lower=0.05)
        Z.loc[sub.index] = ((sub - med) / mad).to_numpy()
    return Z


def vr_terminos(H: np.ndarray, p: np.ndarray):
    """Por mes: (K − μ)², v y N a partir de H (NaN = sin dato)."""
    ok = ~np.isnan(H); N = ok.sum(1); K = np.nansum(H, 1); mu = (ok * p).sum(1); v = (ok * p * (1 - p)).sum(1)
    sel = N >= MIN_EST
    return ((K - mu) ** 2)[sel], v[sel], (K / np.maximum(N, 1)), sel


def permutar(H: np.ndarray, mes: np.ndarray) -> np.ndarray:
    out = H.copy()
    for m in range(1, 13):
        r = np.where(mes == m)[0]
        o = np.argsort(RNG.random((len(r), H.shape[1])), axis=0)
        out[r] = np.take_along_axis(H[r], o, axis=0)
    return out


def boot_bloques(n: int, B: int):
    nb = int(np.ceil(n / BLOQUE))
    for _ in range(B):
        ini = RNG.integers(0, max(1, n - BLOQUE + 1), nb)
        yield np.concatenate([np.arange(i, min(i + BLOQUE, n)) for i in ini])[:n]


def holm(p: dict) -> dict:
    orden = sorted(p, key=p.get); out, prev = {}, 0.0
    for i, k in enumerate(orden):
        prev = max(prev, min(1.0, p[k] * (len(orden) - i))); out[k] = prev
    return out


def main() -> None:
    Z = matriz_z(); mt = meta()
    est = [c for c in Z.columns if c in mt.index]; Z = Z[est]
    reg = pd.Series({c: NOMBRE_A_REGION.get(norm(mt.loc[c, "departamento"]), "Andina") for c in est})
    print(f"Estaciones con >= {MIN_MESES} meses: {len(est)}; meses {Z.index.min():%Y-%m} a {Z.index.max():%Y-%m}; por región: {reg.value_counts().to_dict()}")
    mes = Z.index.month.to_numpy(); oni = E.oni().reindex(Z.index)
    Hh = np.where(Z.isna(), np.nan, (Z >= UMBRAL).astype(float).to_numpy()); Hl = np.where(Z.isna(), np.nan, (Z <= -UMBRAL).astype(float).to_numpy())
    res, pC1, pC2, info = {}, {}, {}, {}
    print("\nC1 sincronía de anomalías ALTAS (VR = 1 si fueran independientes):")
    for r in sorted(reg.unique()):
        cols = np.where(reg.to_numpy() == r)[0]
        if len(cols) < MIN_EST:
            continue
        H = Hh[:, cols]; p = np.nanmean(H, 0)
        d, v, f, sel = vr_terminos(H, p); vr = d.sum() / v.sum()
        nulo = []
        for _ in range(N_PERM):
            dn, vn, _, _ = vr_terminos(permutar(H, mes), p); nulo.append(dn.sum() / vn.sum())
        pc1 = (np.sum(np.array(nulo) >= vr) + 1) / (N_PERM + 1)
        bs = [d[ix[ix < len(d)]].sum() / v[ix[ix < len(v)]].sum() for ix in boot_bloques(len(d), N_BOOT)]
        lo, hi = np.percentile(bs, [2.5, 97.5]); pC1[r] = pc1
        ft = pd.Series(np.where(sel, f, np.nan), index=Z.index)
        fn = ft[(oni <= -0.5)].mean(); fneu = ft[(oni.abs() < 0.5)].mean()
        # C2: Niña − neutral, bootstrap de bloques sobre la línea de tiempo completa
        fa, oa = ft.to_numpy(), oni.to_numpy(); nina, neu = (oa <= -0.5), (np.abs(oa) < 0.5)
        dif = lambda ix: np.nanmean(fa[ix][nina[ix]]) - np.nanmean(fa[ix][neu[ix]])
        bd = np.array([dif(ix) for ix in boot_bloques(len(fa), 1000)]); d0 = dif(np.arange(len(fa)))
        pC2[r] = (np.sum(bd <= 0) + 1) / (len(bd) + 1)
        res[r] = {"n_est": int(len(cols)), "meses": int(sel.sum()), "VR": float(vr), "ic": [float(lo), float(hi)], "p_perm": float(pc1), "VR_nulo_mediana": float(np.median(nulo)),
                  "f_nina": float(fn), "f_neutral": float(fneu), "dif_nina_neutral": float(d0), "ic_dif": [float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))]}
        print(f"   {r:>9}: {len(cols):>3} estaciones, {sel.sum():>3} meses; VR = {vr:.2f} IC95% [{lo:.2f}, {hi:.2f}]; nulo (mediana permutación) = {np.median(nulo):.2f}; p = {pc1:.3f}")
    h1, h2 = holm(pC1), holm(pC2)
    print("\nHolm C1 (VR > 1): " + "; ".join(f"{k}: {v:.3f}{' ✔' if v < 0.05 else ''}" for k, v in h1.items()))
    print("\nC2 fracción media de estaciones en anomalía alta por mes, La Niña vs neutral:")
    for r, x in res.items():
        print(f"   {r:>9}: Niña {100 * x['f_nina']:.1f} % | neutral {100 * x['f_neutral']:.1f} % | diferencia {100 * x['dif_nina_neutral']:+.1f} pp IC95% [{100 * x['ic_dif'][0]:+.1f}, {100 * x['ic_dif'][1]:+.1f}]; p Holm = {h2[r]:.3f}{' ✔' if h2[r] < 0.05 else ''}")
        x["holm_C1"], x["holm_C2"] = h1[r], h2[r]
    # exploratorio: anomalía BAJA, El Niño − neutral
    print("\nExploratorio (sin ajuste): anomalías BAJAS, El Niño (ONI >= 0,5) menos neutral:")
    for r in res:
        cols = np.where(reg.to_numpy() == r)[0]; H = Hl[:, cols]; p = np.nanmean(H, 0); d, v, f, sel = vr_terminos(H, p)
        ft = np.where(sel, f, np.nan); oa = oni.to_numpy()
        a, b = np.nanmean(ft[oa >= 0.5]), np.nanmean(ft[np.abs(oa) < 0.5]); print(f"   {r:>9}: El Niño {100 * a:.1f} % | neutral {100 * b:.1f} % | diferencia {100 * (a - b):+.1f} pp; VR bajas = {d.sum() / v.sum():.2f}")
    # C3 alcance espacial
    C = Z.corr(min_periods=120).to_numpy(); lat = np.radians(mt.loc[est, "latitud"].astype(float).to_numpy()); lon = np.radians(mt.loc[est, "longitud"].astype(float).to_numpy())
    a = np.sin((lat[:, None] - lat[None]) / 2) ** 2 + np.cos(lat)[:, None] * np.cos(lat)[None] * np.sin((lon[:, None] - lon[None]) / 2) ** 2
    D = 2 * 6371 * np.arcsin(np.sqrt(a)); iu = np.triu_indices(len(est), 1); c, dd = C[iu], D[iu]; ok = np.isfinite(c) & np.isfinite(dd)
    print(f"\nC3 correlación de los z mensuales entre pares de estaciones ({ok.sum()} pares):")
    rango = None
    for lo_, hi_ in zip(BINS[:-1], BINS[1:]):
        s = ok & (dd >= lo_) & (dd < hi_)
        if s.sum():
            med = float(np.median(c[s])); print(f"   {lo_:>4.0f}-{(hi_ if hi_ < 1e8 else float('inf')):>5.0f} km: mediana {med:+.2f} (n={s.sum()})")
            if rango is None and med < 0.10:
                rango = lo_
    print(f"   Distancia a partir de la cual la mediana cae bajo 0,10: {rango if rango is not None else '> 800'} km")
    for r in res:
        idx = np.where(reg.to_numpy() == r)[0]; sub = C[np.ix_(idx, idx)]; off = sub[np.triu_indices(len(idx), 1)]; rho = float(np.nanmean(off)); n = len(idx)
        res[r]["rho_medio"] = rho; res[r]["n_efectivo"] = float(n / (1 + (n - 1) * max(rho, 0)))
        print(f"   {r:>9}: correlación media intra-región {rho:+.2f}; {n} estaciones ≈ {res[r]['n_efectivo']:.1f} independientes")
    (AQUI / "coherencia_resultados.json").write_text(json.dumps({"regiones": res, "rango_km": rango}, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
