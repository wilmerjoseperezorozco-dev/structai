"""Hipotesis 13: El Nino (ONI) y la energia electrica en Colombia (XM). Diseno en
scripts/satelite/PROTOCOLO_ANALISIS.md seccion 13, fijado antes de correr.

Confirmatorio 1: ONI -> aportes hidricos (beta < 0). Confirmatorio 2: ONI -> precio de bolsa real (beta > 0).
Confirmatorio 3: asimetria (|beta+| - |beta-|). Validacion temporal reservada 2019-2026.
Inferencia: bootstrap de bloques moviles de 12 meses; errores Newey-West como complemento.
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
CACHE = AQUI / "_cache"
N_BOOT = 5000
BLOQUE = 12
RNG = np.random.default_rng(20261106)
CENTRO = {"DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6, "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12}


def bajar(url: str, nombre: str) -> str:
    f = CACHE / nombre
    if not f.exists():
        CACHE.mkdir(exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "structai-research/0.1"}), timeout=90) as r:
            f.write_text(r.read().decode("utf-8", "replace"), encoding="utf-8")
    return f.read_text(encoding="utf-8")


def oni() -> pd.Series:
    filas = {}
    for ln in bajar("https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt", "oni.txt").splitlines()[1:]:
        p = ln.split()
        if len(p) == 4 and p[0] in CENTRO:
            anio = int(p[1]) - (1 if p[0] == "NDJ" else 0)
            filas[pd.Timestamp(year=anio, month=CENTRO[p[0]], day=1)] = float(p[3])
    return pd.Series(filas).sort_index()


def wti() -> pd.Series:
    t = bajar("https://fred.stlouisfed.org/graph/fredgraph.csv?id=MCOILWTICO", "wti_mensual.csv").splitlines()[1:]
    d = {}
    for ln in t:
        f, v = ln.split(",")
        if v not in (".", ""):
            d[pd.Timestamp(f)] = float(v)
    return pd.Series(d).sort_index()


def ols(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b


def newey_west(y, X, L=12):
    b = ols(y, X)
    e = y - X @ b
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    S = (X * e[:, None]).T @ (X * e[:, None])
    for l in range(1, L + 1):
        w = 1 - l / (L + 1)
        G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None])
        S += w * (G + G.T)
    cov = XtXi @ S @ XtXi
    return b, np.sqrt(np.diag(cov))


def boot_bloques(y, X, funcion, B=N_BOOT):
    n = len(y)
    out = []
    nb = int(np.ceil(n / BLOQUE))
    for _ in range(B):
        ini = RNG.integers(0, n - BLOQUE + 1, nb)
        idx = np.concatenate([np.arange(i, i + BLOQUE) for i in ini])[:n]
        try:
            out.append(funcion(y[idx], X[idx]))
        except np.linalg.LinAlgError:
            continue
    return np.array(out)


def ic(v):
    return np.percentile(v, [2.5, 97.5])


def main() -> None:
    xm = pd.read_csv(AQUI / "xm_energia_mensual.csv", parse_dates=["fecha"]).set_index("fecha")
    ipc = pd.read_csv(AQUI / "ipc_mensual.csv", parse_dates=["fecha"]).set_index("fecha")["indice"]
    o = oni()
    try:
        w = wti()
    except Exception as e:           # FRED es intermitente; la robustez con WTI es secundaria y no bloquea lo confirmatorio
        print(f"AVISO: no se pudo obtener el WTI de FRED ({type(e).__name__}); se omite la prueba de robustez con WTI.")
        w = pd.Series(dtype=float, index=pd.DatetimeIndex([]))
    df = pd.DataFrame({"precio": xm["PPPrecBolsNaci"], "aportes": xm["AporEner"], "media_hist": xm["AporEnerMediHist"],
                       "embalse": xm["PorcVoluUtilDiar"], "ipc": ipc, "oni": o, "wti": w}).dropna(subset=["precio", "aportes", "media_hist", "ipc", "oni"])
    df = df[(df.index >= "2000-01-01") & (df.index <= "2026-09-01")]
    df["y_aportes"] = np.log(df["aportes"] / df["media_hist"])
    df["precio_real"] = df["precio"] * ipc.iloc[-1] / df["ipc"]
    df["y_precio"] = np.log(df["precio_real"])
    n = len(df)
    print(f"Meses analizados: {n} ({df.index.min():%Y-%m} a {df.index.max():%Y-%m}); ONI de {df.oni.min():+.1f} a {df.oni.max():+.1f}")
    print(f"Precio real medio (COP/kWh de sep-2026): {df.precio_real.mean():.0f}; mediana {df.precio_real.median():.0f}; max {df.precio_real.max():.0f} ({df.precio_real.idxmax():%Y-%m})")
    fase = np.where(df.oni >= 0.5, "El Nino (ONI>=+0.5)", np.where(df.oni <= -0.5, "La Nina (ONI<=-0.5)", "Neutral"))
    print("\nDescriptivo por fase ENSO (mes a mes):")
    for f in ["El Nino (ONI>=+0.5)", "Neutral", "La Nina (ONI<=-0.5)"]:
        m = fase == f
        print(f"  {f:<22} n={int(m.sum()):>3}  precio real mediano {df.precio_real[m].median():>7.0f}  | razon aportes/media historica mediana {np.exp(df.y_aportes[m]).median():.2f}")

    t = (np.arange(n) - n / 2) / n
    meses = pd.get_dummies(df.index.month, drop_first=True).to_numpy(float)
    base = np.column_stack([np.ones(n), meses, t, t ** 2])
    xo = df["oni"].to_numpy(float)

    print("\n== CONFIRMATORIO 1: ONI -> aportes hidricos (log de aportes / media historica) ==")
    y1 = df["y_aportes"].to_numpy(float)
    X1 = np.column_stack([xo, base])
    b1, se1 = newey_west(y1, X1)
    bs1 = boot_bloques(y1, X1, lambda y, X: ols(y, X)[0])
    lo1, hi1 = ic(bs1)
    print(f"   beta = {b1[0]:+.3f} por +1 C de ONI  (aportes x{np.exp(b1[0]):.2f})  IC95% bloques [{lo1:+.3f}, {hi1:+.3f}] | NW EE {se1[0]:.3f}")
    c1 = hi1 < 0
    print(f"   -> {'se cumple: beta negativo y el IC excluye 0' if c1 else 'NO se cumple'}")

    print("\n== CONFIRMATORIO 2: ONI -> precio de bolsa real (log) ==")
    y2 = df["y_precio"].to_numpy(float)
    X2 = np.column_stack([xo, base])
    b2, se2 = newey_west(y2, X2)
    bs2 = boot_bloques(y2, X2, lambda y, X: ols(y, X)[0])
    lo2, hi2 = ic(bs2)
    print(f"   beta = {b2[0]:+.3f}  = {100 * (np.exp(b2[0]) - 1):+.0f} % en el precio real por +1 C de ONI | IC95% bloques [{100 * (np.exp(lo2) - 1):+.0f} %, {100 * (np.exp(hi2) - 1):+.0f} %] | NW EE {se2[0]:.3f}")
    c2 = lo2 > 0
    print(f"   -> {'se cumple: beta positivo y el IC excluye 0' if c2 else 'NO se cumple'}")

    print("\n== CONFIRMATORIO 3: asimetria El Nino vs La Nina ==")
    xp, xn = np.maximum(xo, 0), np.minimum(xo, 0)
    X3 = np.column_stack([xp, xn, base])
    b3, _ = newey_west(y2, X3)
    bs3 = boot_bloques(y2, X3, lambda y, X: abs(ols(y, X)[0]) - abs(ols(y, X)[1]))
    lo3, hi3 = ic(bs3)
    print(f"   pendiente El Nino (ONI+): {b3[0]:+.3f} | pendiente La Nina (ONI-): {b3[1]:+.3f} (signo: positivo = La Nina baja el precio)")
    print(f"   |beta+| - |beta-| = {abs(b3[0]) - abs(b3[1]):+.3f}  IC95% bloques [{lo3:+.3f}, {hi3:+.3f}] -> {'asimetria detectada' if lo3 > 0 or hi3 < 0 else 'no se rechaza simetria'}")

    print("\n== VALIDACION TEMPORAL RESERVADA (ajuste 2003-2018, prueba 2019-2026) ==")
    print("   (Desviacion declarada: el protocolo decia 2000-2018; el IPC del DANE empieza en 2003-01 y se usa para deflactar.)")
    ent = np.asarray(df.index <= "2018-12-01")
    Xc, Xo = base, np.column_stack([xo, base])
    pc = Xc[~ent] @ ols(y2[ent], Xc[ent])
    po = Xo[~ent] @ ols(y2[ent], Xo[ent])
    ea, eo = np.abs(y2[~ent] - pc), np.abs(y2[~ent] - po)
    mae_c, mae_o = ea.mean(), eo.mean()
    nt = len(ea)
    dif = []
    for _ in range(N_BOOT):
        ini = RNG.integers(0, nt - BLOQUE + 1, int(np.ceil(nt / BLOQUE)))
        idx = np.concatenate([np.arange(i, i + BLOQUE) for i in ini])[:nt]
        dif.append(ea[idx].mean() - eo[idx].mean())
    l4, h4 = ic(np.array(dif))
    print(f"   MAE (log del precio real) sin ONI: {mae_c:.3f} | con ONI: {mae_o:.3f} | mejora = {mae_c - mae_o:+.3f}  IC95% bloques [{l4:+.3f}, {h4:+.3f}] (n prueba = {nt})")
    c4 = (mae_c - mae_o) > 0
    print(f"   -> {'el error baja en el periodo reservado' if c4 else 'el error NO baja en el periodo reservado'}")

    print("\n== REZAGOS (descriptivo, no confirmatorio): beta de ONI(t-L) sobre aportes y precio ==")
    for L in (0, 1, 2, 3):
        xl = df["oni"].shift(L).to_numpy(float)
        ok = ~np.isnan(xl)
        fila = []
        for nombre, y in [("aportes", y1), ("precio", y2)]:
            Xl = np.column_stack([xl[ok], base[ok]])
            b, _ = newey_west(y[ok], Xl)
            bs = boot_bloques(y[ok], Xl, lambda yy, XX: ols(yy, XX)[0], B=1500)
            lo, hi = ic(bs)
            fila.append(f"{nombre}: {b[0]:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        print(f"   rezago {L}: " + " | ".join(fila))

    print("\n== ROBUSTEZ: controlar por el WTI (proxy del combustible de la generacion termica) ==")
    d2 = df.dropna(subset=["wti"]) if "wti" in df and df["wti"].notna().any() else df.iloc[0:0]
    n2 = len(d2)
    if n2 < 100:
        print("   omitida: sin serie del WTI suficiente (FRED no respondio).")
    else:
        t2 = (np.arange(n2) - n2 / 2) / n2
        base2 = np.column_stack([np.ones(n2), pd.get_dummies(d2.index.month, drop_first=True).to_numpy(float), t2, t2 ** 2, np.log(d2["wti"].to_numpy(float))])
        X5 = np.column_stack([d2["oni"].to_numpy(float), base2])
        y5 = d2["y_precio"].to_numpy(float)
        b5, _ = newey_west(y5, X5)
        lo5, hi5 = ic(boot_bloques(y5, X5, lambda yy, XX: ols(yy, XX)[0], B=2000))
        print(f"   beta ONI = {b5[0]:+.3f} ({100 * (np.exp(b5[0]) - 1):+.0f} %) IC95% [{100 * (np.exp(lo5) - 1):+.0f} %, {100 * (np.exp(hi5) - 1):+.0f} %] (n={n2}); beta del log WTI: {b5[-1]:+.2f}")

    print("\n== EPISODIOS DE EL NINO (ONI >= +0.5 en >= 5 meses consecutivos), precio real ==")
    activo = (df["oni"] >= 0.5).to_numpy()
    eps, i = [], 0
    while i < n:
        if activo[i]:
            j = i
            while j + 1 < n and activo[j + 1]:
                j += 1
            if j - i + 1 >= 5:
                eps.append((i, j))
            i = j + 1
        else:
            i += 1
    print(f"   {'episodio':<18}{'ONI pico':>9}{'precio pico':>13}{'media 12m previos':>19}{'razon':>8}")
    for i, j in eps:
        seg = df.iloc[i:j + 1]
        previo = df.iloc[max(0, i - 12):i].precio_real
        r = seg.precio_real.max() / previo.mean() if len(previo) == 12 else np.nan
        print(f"   {seg.index[0]:%Y-%m} a {seg.index[-1]:%Y-%m}  {seg.oni.max():>+7.1f}{seg.precio_real.max():>13.0f}{previo.mean() if len(previo) else float('nan'):>19.0f}{r:>8.1f}")

    veredicto = []
    veredicto.append("1 (hidrologia): " + ("SE CUMPLE" if c1 else "NO se cumple"))
    veredicto.append("2 (precio): " + ("SE CUMPLE" if c2 else "NO se cumple"))
    veredicto.append("validacion temporal: " + ("el error baja" if c4 else "el error NO baja"))
    afecta = c2 and c4
    print("\nVEREDICTO (regla fija): " + " | ".join(veredicto))
    print(f"   => ENSO afecta el precio de bolsa: {'SI (confirmatorio 2 y validacion reservada)' if afecta else 'NO se afirma'}"
          + ("" if c1 else "; mecanismo hidrologico NO afirmado"))
    print("\nLIMITES: pocos episodios independientes de ENSO (la inferencia efectiva es mucho menor que n); cambios regulatorios y de mercado "
          "no modelados; el precio depende del gas y la demanda; el IPC total es un deflactor imperfecto; cifras recientes provisionales.")
    (AQUI / "enso_energia_resultados.json").write_text(json.dumps({
        "n": n, "aportes": {"beta": b1[0], "ic": [lo1, hi1]}, "precio": {"beta": b2[0], "ic": [lo2, hi2]},
        "asimetria": {"b_pos": b3[0], "b_neg": b3[1], "ic_dif_abs": [lo3, hi3]},
        "reservado": {"mae_sin": mae_c, "mae_con": mae_o, "ic_mejora": [l4, h4]}, "veredicto": veredicto}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
