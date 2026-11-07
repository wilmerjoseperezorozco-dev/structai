"""H1 y H2 (protocolo §23) sobre los umbrales de lluvia–duración del §19 (UNGRD + CHIRPS diario 2019-2024).

H1: log(E/MAP) = log a + b·log D frente a log E = log a + b·log D. Transferencia: ajuste con las otras cuatro regiones (calibración 2019-2022),
    prueba en la región dejada fuera (2023-2024). Mejora si ΔTSS (normalizado − bruto), agrupado, tiene IC95 % de bloques por departamento que excluye 0.
H2: regresión cuantil τ = 0,05 de log(E/MAP) sobre log D + log(1 + pendiente p90 municipal) + ONI del mes (2 parámetros adicionales), calibración
    2019-2022; línea base = curva global normalizada de H1. Mejora si ΔTSS reservado (2023-2024) tiene IC que excluye 0.
Requiere chirps_diario_colombia.json y dem_poligonos_colombia.json.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys

import numpy as np
from sklearn.linear_model import QuantileRegressor

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "macro"))
import umbrales_lluvia_movimientos as U  # noqa: E402  (eventos, acumulados, DUR, REGIONES, REG)
import enso_energia as E  # noqa: E402

N_BOOT = 2000
RNG = np.random.default_rng(20261107)


def cargar():
    ch = json.loads(open(os.path.join(AQUI, "chirps_diario_colombia.json"), encoding="utf-8").read())
    dias = [dt.date.fromisoformat(d) for d in ch["dias"]]
    cods = list(ch["municipios"])
    R = np.array([ch["municipios"][c] for c in cods], float)
    idx_m = {c: i for i, c in enumerate(cods)}; idx_d = {d: i for i, d in enumerate(dias)}
    MAP = R.mean(axis=1) * 365.25
    ev = np.zeros(R.shape, bool)
    for e in U.eventos():
        c, f = e["codigo_municipio"], dt.date.fromisoformat(str(e["fecha"])[:10])
        if c in idx_m and f in idx_d:
            ev[idx_m[c], idx_d[f]] = True
    con_ev = ev.any(axis=1)
    cerca = ev.copy()
    for s in (1, 2):
        cerca[:, s:] |= ev[:, :-s]; cerca[:, :-s] |= ev[:, s:]
    elegible = np.zeros(R.shape, bool); elegible[con_ev] = True
    pos, neg = ev & elegible, elegible & ~cerca
    anio = np.array([d.year for d in dias])
    dem = {m["codigo"]: m for m in json.loads(open(os.path.join(AQUI, "dem_poligonos_colombia.json"), encoding="utf-8").read())["municipios"] if "error" not in m}
    pend = np.array([np.log1p(dem[c]["pend_p90_pct"]) if c in dem else np.nan for c in cods])
    s = E.oni()
    oni_mes = {(t.year, t.month): float(v) for t, v in s.items()}
    oni = np.array([oni_mes.get((d.year, d.month), np.nan) for d in dias])
    return dict(R=R, MAP=MAP, pos=pos, neg=neg, dept=np.array([c[:2] for c in cods]), anio=anio, pend=pend, oni=oni, cods=cods)


def curva(An, mask_pos):
    thr = {D: np.nanpercentile(An[D][mask_pos & np.isfinite(An[D])], 5) for D in U.DUR}
    b, la = np.polyfit(np.log(U.DUR), np.log([max(thr[D], 1e-6) for D in U.DUR]), 1)
    return float(np.exp(la)), float(b)


def alerta_curva(An, a, b):
    al = np.zeros(An[U.DUR[0]].shape, bool)
    for D in U.DUR:
        al |= np.nan_to_num(An[D], nan=-1) >= a * D ** b
    return al


def conf_por_depto(al, pos, neg, dept, test):
    out = {}
    for d in np.unique(dept):
        m = (dept == d)[:, None]
        P, N = pos & test & m, neg & test & m
        out[d] = np.array([(al & P).sum(), (~al & P).sum(), (al & N).sum(), (~al & N).sum()], float)
    return out


def tss(c):
    tp, fn, fp, tn = c
    return tp / max(tp + fn, 1) - fp / max(fp + tn, 1)


def dif_boot(c_cand, c_base):
    deptos = sorted(c_cand)
    pt = tss(sum(c_cand[d] for d in deptos)) - tss(sum(c_base[d] for d in deptos))
    v = []
    for _ in range(N_BOOT):
        sel = RNG.choice(deptos, len(deptos), replace=True)
        v.append(tss(sum(c_cand[d] for d in sel)) - tss(sum(c_base[d] for d in sel)))
    v = np.array(v)
    pval = float(min(1.0, 2 * min((np.sum(v <= 0) + 1) / (N_BOOT + 1), (np.sum(v >= 0) + 1) / (N_BOOT + 1))))
    return pt, np.percentile(v, [2.5, 97.5]), pval


def main() -> None:
    d = cargar()
    R, MAP, pos, neg, dept, anio = d["R"], d["MAP"], d["pos"], d["neg"], d["dept"], d["anio"]
    cal = (anio <= 2022)[None, :]; test = (anio >= 2023)[None, :]
    Araw = {D: U.acumulados(R, D) for D in U.DUR}
    An = {D: Araw[D] / MAP[:, None] * 100 for D in U.DUR}
    print(f"Positivos: calibración {int((pos & cal).sum())}, prueba {int((pos & test).sum())}; negativos {int(neg.sum())}")
    # ---------------- H1: dejar una región fuera
    c_norm, c_raw = {}, {}
    for r, ds in U.REGIONES.items():
        m_r = np.isin(dept, ds.split())[:, None]
        if (pos & cal & ~m_r).sum() < 100 or (pos & test & m_r).sum() < 10:
            print(f"  H1: región {r} sin eventos suficientes; se omite"); continue
        a_n, b_n = curva(An, pos & cal & ~m_r); a_r, b_r = curva(Araw, pos & cal & ~m_r)
        cn = conf_por_depto(alerta_curva(An, a_n, b_n), pos, neg, np.where(m_r[:, 0], dept, "xx"), test)
        cr = conf_por_depto(alerta_curva(Araw, a_r, b_r), pos, neg, np.where(m_r[:, 0], dept, "xx"), test)
        for k in list(cn):
            if k == "xx":
                continue
            c_norm[k], c_raw[k] = cn[k], cr[k]
        print(f"  H1 región fuera = {r}: curva normalizada E = {a_n:.2f}·D^{b_n:.2f} (%MAP); bruta E = {a_r:.1f}·D^{b_r:.2f} (mm)")
    pt, ic, p1 = dif_boot(c_norm, c_raw)
    print(f"H1 ΔTSS (normalizado − bruto) = {pt:+.3f} IC95% [{ic[0]:+.3f}, {ic[1]:+.3f}] -> {'MEJORA' if ic[0] > 0 else ('PEOR' if ic[1] < 0 else 'sin diferencia demostrada')}")
    # ---------------- H2: regresión cuantil con covariables
    a_g, b_g = curva(An, pos & cal)
    base = conf_por_depto(alerta_curva(An, a_g, b_g), pos, neg, dept, test)
    filas = []
    pm = np.argwhere(pos & cal)
    for D in U.DUR:
        v = An[D][pm[:, 0], pm[:, 1]]
        ok = np.isfinite(v) & (v > 0) & np.isfinite(d["pend"][pm[:, 0]]) & np.isfinite(d["oni"][pm[:, 1]])
        filas.append(np.c_[np.log(v[ok]), np.full(ok.sum(), np.log(D)), d["pend"][pm[ok, 0]], d["oni"][pm[ok, 1]]])
    M = np.vstack(filas)
    if len(M) > 60000:
        M = M[RNG.choice(len(M), 60000, replace=False)]
    qr = QuantileRegressor(quantile=0.05, alpha=0.0, solver="highs").fit(M[:, 1:], M[:, 0])
    print(f"  H2 coeficientes (log E = c0 + c1·log D + c2·log(1+pend p90) + c3·ONI): {qr.intercept_:+.3f}, {qr.coef_.round(3).tolist()}")
    al = np.zeros(R.shape, bool)
    for D in U.DUR:
        thr = qr.intercept_ + qr.coef_[0] * np.log(D) + qr.coef_[1] * d["pend"][:, None] + qr.coef_[2] * d["oni"][None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            al |= np.log(np.where(An[D] > 0, An[D], np.nan)) >= thr
    cand = conf_por_depto(al, pos, neg, dept, test)
    pt2, ic2, p2 = dif_boot(cand, base)
    print(f"H2 ΔTSS (con covariables − curva global) = {pt2:+.3f} IC95% [{ic2[0]:+.3f}, {ic2[1]:+.3f}] -> {'MEJORA' if ic2[0] > 0 else ('PEOR' if ic2[1] < 0 else 'sin diferencia demostrada')}")
    print(f"   TSS reservado: línea base {tss(sum(base.values())):+.3f}; candidata {tss(sum(cand.values())):+.3f}")
    json.dump({"H1": {"dif": pt, "ic": ic.tolist(), "p": p1}, "H2": {"dif": pt2, "ic": ic2.tolist(), "p": p2, "coef": [float(qr.intercept_)] + qr.coef_.tolist()}},
              open(os.path.join(AQUI, "hipotesis_h1_h2.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
