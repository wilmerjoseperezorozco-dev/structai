"""DIAGNOSTICO POSTERIOR (post hoc) de la validacion temporal de la hipotesis 13.

NO rescata ni cambia el veredicto: la regla fija ya dio "no se afirma" porque el error en el periodo
reservado no bajo. Este script solo investiga POR QUE, y queda rotulado como exploratorio.

Sospecha: el diseno declarado extrapola una tendencia cuadratica del periodo de ajuste (2003-2018) a
2019-2026, lo que domina el error y puede distorsionar la comparacion con/sin ONI.
Diagnosticos: (a) mismo corte reservado sin tendencia; (b) origen movil anual sin tendencia;
(c) estabilidad del coeficiente de ONI antes y despues de 2019; (d) sesgo medio de cada modelo.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import enso_energia as e   # reutiliza lectores y utilidades; configura la salida UTF-8


def cargar() -> pd.DataFrame:
    xm = pd.read_csv(e.AQUI / "xm_energia_mensual.csv", parse_dates=["fecha"]).set_index("fecha")
    ipc = pd.read_csv(e.AQUI / "ipc_mensual.csv", parse_dates=["fecha"]).set_index("fecha")["indice"]
    df = pd.DataFrame({"precio": xm["PPPrecBolsNaci"], "ipc": ipc, "oni": e.oni()}).dropna()
    df = df[(df.index >= "2003-01-01") & (df.index <= "2026-09-01")]
    df["y"] = np.log(df["precio"] * ipc.iloc[-1] / df["ipc"])
    return df


def mats(df):
    mes = pd.get_dummies(df.index.month, drop_first=True).to_numpy(float)
    base = np.column_stack([np.ones(len(df)), mes])
    return base, np.column_stack([df["oni"].to_numpy(float), base])


def main() -> None:
    df = cargar()
    y = df["y"].to_numpy(float)
    base, con = mats(df)
    anio = df.index.year.to_numpy()

    print("== (a) Corte reservado 2019-2026 SIN tendencia (solo mes calendario) ==")
    tr = anio <= 2018
    ea = np.abs(y[~tr] - base[~tr] @ e.ols(y[tr], base[tr]))
    eo = np.abs(y[~tr] - con[~tr] @ e.ols(y[tr], con[tr]))
    sa = (y[~tr] - base[~tr] @ e.ols(y[tr], base[tr])).mean()
    so = (y[~tr] - con[~tr] @ e.ols(y[tr], con[tr])).mean()
    print(f"   MAE sin ONI {ea.mean():.3f} | con ONI {eo.mean():.3f} | mejora {ea.mean() - eo.mean():+.3f}; sesgo medio sin ONI {sa:+.3f}, con ONI {so:+.3f} (n={int((~tr).sum())})")

    print("\n== (b) Origen movil anual sin tendencia: ajustar con todo lo anterior a cada año Y y predecir Y ==")
    ra, ro, n = [], [], 0
    for Y in range(2010, 2027):
        t = anio < Y
        p = anio == Y
        if p.sum() == 0:
            continue
        ra += list(np.abs(y[p] - base[p] @ e.ols(y[t], base[t])))
        ro += list(np.abs(y[p] - con[p] @ e.ols(y[t], con[t])))
    ra, ro = np.array(ra), np.array(ro)
    dif = ra - ro
    nt = len(dif)
    bs = []
    for _ in range(3000):
        ini = e.RNG.integers(0, nt - e.BLOQUE + 1, int(np.ceil(nt / e.BLOQUE)))
        idx = np.concatenate([np.arange(i, i + e.BLOQUE) for i in ini])[:nt]
        bs.append(dif[idx].mean())
    lo, hi = e.ic(np.array(bs))
    print(f"   {nt} predicciones mensuales (2010-2026): MAE sin ONI {ra.mean():.3f} | con ONI {ro.mean():.3f} | mejora {dif.mean():+.3f}  IC95% bloques [{lo:+.3f}, {hi:+.3f}]")

    print("\n== (c) Estabilidad del coeficiente de ONI (sin tendencia) ==")
    for nombre, m in [("2003-2018", anio <= 2018), ("2019-2026", anio >= 2019), ("2003-2012", anio <= 2012), ("2013-2026", anio >= 2013)]:
        X, yy = con[m], y[m]
        bs = e.boot_bloques(yy, X, lambda a, b: e.ols(a, b)[0], B=2000)
        l, h = e.ic(bs)
        b = e.ols(yy, X)[0]
        print(f"   {nombre}: beta ONI {b:+.3f} ({100 * (np.exp(b) - 1):+.0f} % por C)  IC95% [{100 * (np.exp(l) - 1):+.0f} %, {100 * (np.exp(h) - 1):+.0f} %] (n={int(m.sum())})")

    print("\n== Nivel del precio real por periodo (mediana, COP/kWh de sep-2026) ==")
    for nombre, m in [("2003-2010", anio <= 2010), ("2011-2018", (anio >= 2011) & (anio <= 2018)), ("2019-2026", anio >= 2019)]:
        print(f"   {nombre}: {np.exp(np.median(y[m])):.0f}")
    print("\nEXPLORATORIO, posterior al veredicto: no cambia la conclusion segun la regla fija.")


if __name__ == "__main__":
    main()
