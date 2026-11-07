"""Umbrales E-D de lluvia para movimientos en masa (protocolo seccion 19): UNGRD + CHIRPS diario."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import _datos_caribe as dc  # noqa: E402

DUR = [1, 2, 3, 5, 7, 10, 15, 30]
REGIONES = {"Caribe": "08 13 20 23 44 47 70", "Andina": "05 11 15 17 25 41 54 63 66 68 73", "Pacifica": "19 27 52 76",
            "Orinoquia": "50 81 85 99", "Amazonia": "18 86 91 94 95 97"}
REG = {d: r for r, ds in REGIONES.items() for d in ds.split()}
RNG = np.random.default_rng(20261107)
N_BOOT, MIN_EV_REGION = 2000, 100


def auc(pos, neg):
    r = rankdata(np.concatenate([pos, neg]))
    return (r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def eventos():
    sb, filas, ini = dc._sb(), [], 0
    while True:
        p = sb.table("ungrd_emergencias").select("fecha,codigo_municipio").ilike("evento", "%MOVIMIENTO%").range(ini, ini + 999).execute().data or []
        filas += p
        if len(p) < 1000:
            return filas
        ini += 1000


def acumulados(R, D):
    c = np.cumsum(np.nan_to_num(R), axis=1)
    out = c.copy()
    out[:, D:] = c[:, D:] - c[:, :-D]
    out[:, :D - 1] = np.nan                      # ventana incompleta
    return out


def boot_dept(dept, estad, grupos):
    """estad(lista de indices de grupo remuestreados) -> valor; grupos = departamentos unicos."""
    v = []
    for _ in range(N_BOOT):
        s = estad(RNG.choice(grupos, len(grupos), replace=True))
        if np.isfinite(s):
            v.append(s)
    return np.percentile(v, [2.5, 97.5]) if v else (np.nan, np.nan)


def main() -> None:
    ch = json.loads((AQUI / "chirps_diario_colombia.json").read_text(encoding="utf-8"))
    dias = [dt.date.fromisoformat(d) for d in ch["dias"]]
    cods = list(ch["municipios"])
    R = np.array([ch["municipios"][c] for c in cods], float)
    idx_m = {c: i for i, c in enumerate(cods)}
    idx_d = {d: i for i, d in enumerate(dias)}
    MAP = R.mean(axis=1) * 365.25
    ev = np.zeros(R.shape, bool)
    for e in eventos():
        c, f = e["codigo_municipio"], dt.date.fromisoformat(str(e["fecha"])[:10])
        if c in idx_m and f in idx_d:
            ev[idx_m[c], idx_d[f]] = True
    con_ev = ev.any(axis=1)
    cerca = ev.copy()
    for s in (1, 2):
        cerca[:, s:] |= ev[:, :-s]; cerca[:, :-s] |= ev[:, s:]
    anio = np.array([d.year for d in dias])
    dept = np.array([c[:2] for c in cods])
    elegible = np.zeros(R.shape, bool); elegible[con_ev] = True
    pos, neg = ev & elegible, elegible & ~cerca
    cal = (anio <= 2022)[None, :]; test = (anio >= 2023)[None, :]
    print(f"Municipios con eventos: {int(con_ev.sum())}; positivos {int(pos.sum())} (cal {int((pos & cal).sum())}, prueba {int((pos & test).sum())}); negativos {int(neg.sum())}")
    A = {D: acumulados(R, D) / MAP[:, None] * 100 for D in DUR}   # % de la lluvia anual media
    ok = lambda D, m: m & np.isfinite(A[D])
    # T1: D* con calibracion
    aucs = {D: auc(A[D][ok(D, pos & cal)], A[D][ok(D, neg & cal)]) for D in DUR}
    Dstar = max(aucs, key=aucs.get)
    print("AUC calibracion por D:", {D: round(a, 3) for D, a in aucs.items()}, "-> D* =", Dstar)
    deptos = np.unique(dept[con_ev])
    def auc_dept(sel):
        pm = np.concatenate([A[Dstar][ok(Dstar, pos & test) & (dept == d)[:, None]] for d in sel])
        nm = np.concatenate([A[Dstar][ok(Dstar, neg & test) & (dept == d)[:, None]] for d in sel])
        return auc(pm, nm) if len(pm) > 5 and len(nm) > 5 else np.nan
    a_t = auc(A[Dstar][ok(Dstar, pos & test)], A[Dstar][ok(Dstar, neg & test)])
    lo, hi = boot_dept(dept, auc_dept, deptos)
    print(f"T1 AUC prueba (D*={Dstar}) = {a_t:.3f}  IC95% bloques [{lo:.3f}, {hi:.3f}]  -> {'cumple' if lo > 0.5 else 'NO cumple'}")
    # T2: curva E-D (percentil 5 de positivos de calibracion)
    def curva(mask_pos):
        thr = {D: np.percentile(A[D][ok(D, mask_pos)], 5) for D in DUR}
        b, la = np.polyfit(np.log(DUR), np.log([max(thr[D], 1e-6) for D in DUR]), 1)
        return thr, float(np.exp(la)), float(b)
    def alerta(thr, a, b):
        al = np.zeros(R.shape, bool)
        for D in DUR:
            al |= np.nan_to_num(A[D], nan=-1) >= a * D ** b
        return al
    thr, a, b = curva(pos & cal)
    print(f"Curva global (% de la lluvia anual): E = {a:.2f} * D^{b:.2f}")
    def tss_sel(sel, al):
        tp = fn = fp = tn = 0
        for d in sel:
            m = (dept == d)[:, None]
            P, N = pos & test & m, neg & test & m
            tp += (al & P).sum(); fn += (~al & P).sum(); fp += (al & N).sum(); tn += (~al & N).sum()
        return tp / max(tp + fn, 1) - fp / max(fp + tn, 1), tp / max(tp + fn, 1), fp / max(fp + tn, 1)
    al = alerta(thr, a, b)
    t2, sens, fa = tss_sel(deptos, al)
    lo2, hi2 = boot_dept(dept, lambda s: tss_sel(s, al)[0], deptos)
    print(f"T2 regla E-D en prueba: TSS = {t2:+.3f} (sensibilidad {sens:.2f}, falsas alarmas {fa:.2f}) IC95% [{lo2:+.3f}, {hi2:+.3f}] -> {'cumple' if lo2 > 0 else 'NO cumple'}")
    al1 = np.nan_to_num(A[Dstar], nan=-1) >= thr[Dstar]
    t3, s3, f3 = tss_sel(deptos, al1)
    print(f"T3 regla de un solo D* = {Dstar}: TSS = {t3:+.3f} (sens {s3:.2f}, FA {f3:.2f}) -> la curva E-D {'mejora' if t2 > t3 else 'NO mejora'} la regla simple")
    res = {"global": {"a": a, "b": b, "AUC_prueba": a_t, "TSS": t2, "sens": sens, "fa": fa, "TSS_IC": [lo2, hi2]}}
    print("\nPor region:")
    for r, ds in REGIONES.items():
        mr = np.isin(dept, ds.split())[:, None]
        n_cal = int((pos & cal & mr).sum())
        if n_cal < MIN_EV_REGION:
            print(f"  {r:<10} eventos de calibracion {n_cal} (< {MIN_EV_REGION}): no se ajusta")
            continue
        thr_r, ar, br = curva(pos & cal & mr)
        alr = alerta(thr_r, ar, br)
        sel = [d for d in deptos if d in ds.split()]
        tr_, se_, fr_ = tss_sel(sel, alr)
        lo_, hi_ = boot_dept(dept, lambda s: tss_sel(s, alr)[0], np.array(sel))
        print(f"  {r:<10} E = {ar:.2f}*D^{br:.2f} | TSS {tr_:+.3f} (sens {se_:.2f}, FA {fr_:.2f}) IC [{lo_:+.3f},{hi_:+.3f}] eventos cal {n_cal}")
        res[r] = {"a": ar, "b": br, "TSS": tr_, "sens": se_, "fa": fr_, "TSS_IC": [lo_, hi_], "n_cal": n_cal}
    (AQUI / "umbrales_lluvia_movimientos.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
