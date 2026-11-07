"""P3 (transmisión) y P4 (Monte Carlo del costo) según PROTOCOLO_PRECIOS.md, sección «P3 y P4 — reglas fijadas ANTES de correr».
Datos: ICOCIV (DANE) mensual 2021-01..2026-09 (Anexos 1 y 16) + TRM, IPC, WTI, ONI. Un regresor a la vez, HAC con 6 rezagos.
Uso: python p3_p4_transmision_montecarlo.py   (requiere _cache/icociv/anex-ICOCIV-sep2026.xlsx)"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "macro"))
import enso_energia as ee  # noqa: E402  (oni(), wti(), newey_west())

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
HORIZONTE, LAG_HAC, BLOQUE, N_SIM, ORIGEN_MIN = 6, 6, 3, 5000, 30
RNG = np.random.default_rng(20261107)
ARCH = AQUI / "_cache" / "icociv" / "anex-ICOCIV-sep2026.xlsx"


def cargar_icociv() -> pd.DataFrame:
    wb = openpyxl.load_workbook(ARCH, read_only=True, data_only=True)
    filas, anio = {}, None
    for r in wb["Anexo 1"].iter_rows(values_only=True, max_row=90):
        if r[0] not in (None, "") and str(r[0]).strip().isdigit():
            anio = int(str(r[0]).strip())
        m = MESES.get(str(r[1]).strip().lower()) if r[1] else None
        if anio and m and r[2] not in (None, "", "-"):
            filas[pd.Timestamp(anio, m, 1)] = float(r[2])
    out = pd.DataFrame({"total": pd.Series(filas)})
    r16 = list(wb["Anexo 16"].iter_rows(values_only=True, max_row=14))
    anios, meses = r16[5], r16[6]   # filas 6 y 7 (años en la primera columna de cada bloque, meses debajo)
    fechas, a = {}, None
    for j in range(3, len(meses)):
        if anios[j] not in (None, ""):
            try:
                a = int(str(anios[j]).strip())
            except ValueError:
                a = None
        m = MESES.get(str(meses[j]).strip().lower()) if meses[j] else None
        if a and m:
            fechas[j] = pd.Timestamp(a, m, 1)
    for fila in r16[8:13]:
        nombre = {"530201": "carreteras", "530203": "tuberias"}.get(str(fila[0]).strip())
        if nombre:
            out[nombre] = pd.Series({f: float(fila[j]) for j, f in fechas.items() if fila[j] not in (None, "", "-")})
    return out.sort_index()


def cargar_externas(idx: pd.DatetimeIndex) -> pd.DataFrame:
    trm = pd.DataFrame(json.loads((AQUI / "_cache" / "trm_historica.json").read_text(encoding="utf-8")))
    trm["f"] = pd.to_datetime(trm.vigenciadesde).dt.to_period("M").dt.to_timestamp(); trm["v"] = trm.valor.astype(float)
    trm = trm.groupby("f").v.mean()
    ipc = pd.read_csv(AQUI.parent / "macro" / "ipc_mensual.csv", parse_dates=["fecha"]).set_index("fecha")["indice"]
    return pd.DataFrame({"trm": trm, "wti": ee.wti(), "ipc": ipc, "oni": ee.oni()}).reindex(idx)


def hac(y, X, L=LAG_HAC):
    b, se = ee.newey_west(y, X, L)
    return b, se


def proyeccion_local(dl: pd.DataFrame, y_col: str, x: pd.Series, h: int, regimen=None):
    ln = np.log(dl[y_col + "_nivel"])
    yh = (ln.shift(-h) - ln.shift(1)).rename("yh")
    d = pd.concat([yh, x.rename("x"), dl[y_col].shift(1).rename("ar")], axis=1)
    if regimen is not None:
        d["rx"] = regimen * d.x
        d["r"] = regimen
    d = d.dropna()
    cols = ["x", "ar"] + (["r", "rx"] if regimen is not None else [])
    X = np.column_stack([np.ones(len(d))] + [d[c].to_numpy() for c in cols])
    b, se = hac(d.yh.to_numpy(), X, max(LAG_HAC, h + 1))
    return {c: (float(b[i + 1]), float(se[i + 1])) for i, c in enumerate(cols)}, len(d)


def p_normal(b, se):
    from math import erf, sqrt
    z = abs(b / se)
    return 1 - erf(z / sqrt(2))


def bloques(v: np.ndarray, n: int) -> np.ndarray:
    nb = int(np.ceil(n / BLOQUE)); ini = RNG.integers(0, len(v) - BLOQUE + 1, nb)
    return np.concatenate([v[i:i + BLOQUE] for i in ini])[:n]


def simular(v: np.ndarray, h: int, n_sim: int = N_SIM) -> np.ndarray:
    return np.array([np.exp(bloques(v, h).sum()) for _ in range(n_sim)])


def main() -> None:
    ic = cargar_icociv()
    print(f"ICOCIV: {len(ic)} meses ({ic.index.min():%Y-%m} a {ic.index.max():%Y-%m}); columnas: {list(ic.columns)}")
    ex = cargar_externas(ic.index)
    print("Externas con datos en el periodo:", {c: int(ex[c].notna().sum()) for c in ex})
    dl = pd.DataFrame(index=ic.index)
    for c in ic.columns:
        dl[c] = np.log(ic[c]).diff(); dl[c + "_nivel"] = ic[c]
    ext = pd.DataFrame({"trm": np.log(ex.trm).diff(), "wti": np.log(ex.wti).diff(), "ipc": np.log(ex.ipc).diff(), "oni": ex.oni})
    car = dl["carreteras"].dropna()

    # ---------- P3.1 descriptivo
    print("\nP3.1 Variación logarítmica mensual de ICOCIV-carreteras (en %):")
    per = {"2021-2022": car[:"2022-12"], "2023-2026": car["2023-01":], "todo": car}
    for k, s in per.items():
        ac = [float(s.autocorr(l)) for l in range(1, 7)]
        print(f"   {k:>9}: n={len(s):>2}; media {100 * s.mean():+.2f}; desv {100 * s.std():.2f}; autocorr(1..6) = " + ", ".join(f"{a:+.2f}" for a in ac))

    # ---------- P3.2 confirmatorio: TRM y WTI -> carreteras, h = 6, Holm sobre 2
    res = {}
    print(f"\nP3.2 Proyecciones locales (respuesta acumulada de ln ICOCIV-carreteras a +1 en la variación log del regresor), HAC:")
    for nombre in ("trm", "wti"):
        res[nombre] = {}
        for h in range(0, HORIZONTE + 1):
            r, n = proyeccion_local(dl, "carreteras", ext[nombre], h)
            b, se = r["x"]; res[nombre][h] = {"b": b, "se": se, "n": n, "p": p_normal(b, se)}
        r6 = res[nombre][HORIZONTE]
        print(f"   {nombre.upper()}: h=0..6 coef = " + ", ".join(f"{res[nombre][h]['b']:+.3f}" for h in range(7)) + f"; h=6: {r6['b']:+.3f} (EE {r6['se']:.3f}, p {r6['p']:.3f}, n {r6['n']}); efecto mínimo detectable (80 %) ≈ {2.8 * r6['se']:.3f}")
    ps = sorted([(res[k][HORIZONTE]["p"], k) for k in res]); holm = {}
    for i, (p, k) in enumerate(ps):
        holm[k] = min(1.0, p * (len(ps) - i)) if i == 0 else max(holm[ps[i - 1][1]], min(1.0, p * (len(ps) - i)))
    for k in res:
        sig = res[k][HORIZONTE]["p"] < 0.05 and holm[k] < 0.05 and res[k][HORIZONTE]["b"] > 0
        print(f"   {k.upper()} h=6: p Holm {holm[k]:.3f} -> {'significativo y positivo' if sig else 'NO significativo (o signo no esperado)'}")
        res[k]["holm_p"] = holm[k]

    # ---------- P3.3 exploratorio
    print("\nP3.3 EXPLORATORIO (sin ajuste por múltiples pruebas):")
    for nombre in ("ipc", "oni"):
        r, n = proyeccion_local(dl, "carreteras", ext[nombre], HORIZONTE); b, se = r["x"]
        print(f"   {nombre.upper()} h=6: {b:+.3f} (EE {se:.3f}, p {p_normal(b, se):.3f}, n {n})")
    reg = pd.Series((dl.index < "2023-01-01").astype(float), index=dl.index)
    r, n = proyeccion_local(dl, "carreteras", ext["trm"], HORIZONTE, regimen=reg)
    bi, sei = r["rx"]
    print(f"   Interacción 2021-2022 × TRM (h=6): coef TRM 2023+ {r['x'][0]:+.3f}; diferencia en 2021-2022 {bi:+.3f} (EE {sei:.3f}, p {p_normal(bi, sei):.3f}, n {n})")

    # ---------- P4 Monte Carlo
    print("\nP4 Monte Carlo (bootstrap por bloques de 3 meses) — multiplicador de costo:")
    vc = {"completa": car.to_numpy(), "solo 2023-2026": car["2023-01":].to_numpy()}
    mc = {}
    for nombre, v in vc.items():
        for h in (6, 12):
            m = simular(v, h); q5, q50, q95 = np.percentile(m, [5, 50, 95])
            mc[f"{nombre}|{h}"] = {"p5": q5, "p50": q50, "p95": q95, "car": q95 - q50}
            print(f"   {nombre:>15}, {h:>2} meses: P5 {q5:.3f}  P50 {q50:.3f}  P95 {q95:.3f}  | costo en riesgo (P95−P50) = {100 * (q95 - q50):.1f} % del presupuesto")
    # validación fuera de muestra: origen móvil, horizonte 6, intervalo nominal 80 %
    arr = car.to_numpy(); orig = range(ORIGEN_MIN, len(arr) - HORIZONTE + 1)
    cob_b, cob_n, ancho_b, ancho_n = [], [], [], []
    for t in orig:
        hist, real = arr[:t], float(np.exp(arr[t:t + HORIZONTE].sum()))
        m = simular(hist, HORIZONTE, 1500); lo, hi = np.percentile(m, [10, 90]); cob_b.append(lo <= real <= hi); ancho_b.append(hi - lo)
        mu, sd = hist.mean() * HORIZONTE, hist.std() * np.sqrt(HORIZONTE)       # referencia ingenua: normal iid
        lo2, hi2 = np.exp(mu - 1.2816 * sd), np.exp(mu + 1.2816 * sd); cob_n.append(lo2 <= real <= hi2); ancho_n.append(hi2 - lo2)
    n_or = len(list(orig)); n_ef = n_or / HORIZONTE
    cb, cn = float(np.mean(cob_b)), float(np.mean(cob_n))
    print(f"\n   Validación fuera de muestra, intervalo nominal 80 % a 6 meses, {n_or} orígenes (tamaño efectivo ≈ {n_ef:.0f} por solapamiento):")
    print(f"   cobertura bootstrap por bloques: {cb:.2f} (ancho medio {np.mean(ancho_b):.3f}) | referencia normal iid: {cn:.2f} (ancho {np.mean(ancho_n):.3f}) | criterio [0,65; 0,95]: {'CUMPLE' if 0.65 <= cb <= 0.95 else 'intervalos NO calibrados'}")

    # cota de cemento asfáltico: 1 a 1 con WTI x TRM
    pa = json.loads((AQUI / "costo_parametrico_pavimentos.json").read_text(encoding="utf-8"))["precios_ref"]
    tot = 0.05 * pa["rodadura"] + 0.05 * 2350 * 0.055 * pa["ca60"] + pa["imprimacion"] + 0.15 * pa["base"] + 0.15 * pa["subbase"]
    cs = 0.05 * 2350 * 0.055 * pa["ca60"] / tot
    petro = np.log(ex.wti * ex.trm).diff().reindex(car.index)
    ok = petro.notna().to_numpy() & np.ones(len(car), bool)
    v2, p2 = car.to_numpy()[ok], petro.to_numpy()[ok]
    ms = []
    for _ in range(N_SIM):
        nb = int(np.ceil(12 / BLOQUE)); ini = RNG.integers(0, len(v2) - BLOQUE + 1, nb)
        a = np.concatenate([v2[i:i + BLOQUE] for i in ini])[:12].sum(); b = np.concatenate([p2[i:i + BLOQUE] for i in ini])[:12].sum()
        ms.append((1 - cs) * np.exp(a) + cs * np.exp(b))
    q5, q50, q95 = np.percentile(ms, [5, 50, 95])
    print(f"\n   Cota (no estimación): con el cemento asfáltico ({100 * cs:.0f} % del costo por m²) moviéndose 1:1 con WTI×TRM, 12 meses: P5 {q5:.3f}  P50 {q50:.3f}  P95 {q95:.3f}  (P95−P50 = {100 * (q95 - q50):.1f} %) vs {100 * mc['completa|12']['car']:.1f} % sin esa cota")
    (AQUI / "p3_p4_resultados.json").write_text(json.dumps({"p3": res, "mc": mc, "cobertura": {"bloques": cb, "normal": cn, "n_origenes": n_or},
                                                              "cota_asfalto": {"p5": q5, "p50": q50, "p95": q95, "cuota_ca": cs}}, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
