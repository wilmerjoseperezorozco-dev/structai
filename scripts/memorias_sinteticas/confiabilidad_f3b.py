"""F3b (#275, #276): β sin censura por FORM + muestreo por importancia. Ver docs/memoria_calculo/PRERREGISTRO_F3B_SIN_CENSURA.md.

Misma física que la F3 (se importa de confiabilidad_f3.py): mismas secciones críticas, funciones de estado límite y
variantes. Solo cambia el estimador de Pf: punto de diseño u* (HL-RF) y muestreo por importancia centrado en u*.

Uso:  python -I scripts/memorias_sinteticas/confiabilidad_f3b.py [--piloto 3] [--hilos 6] [--hasta 22:45]
Salida: data/memorias_sinteticas/f3b/{beta_por_edificio.csv, resultados_f3b.json}
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import csv
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.special import log_ndtr, ndtri

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confiabilidad_f3 as f3  # noqa: E402

RAIZ = f3.RAIZ
SEMILLA = f3.SEMILLA
VARIANTES = f3.VARIANTES
VARS = ("fc", "fy", "D", "L", "thR_flex", "thR_col", "thS")
N_IS = 200_000
N_IS_REPETICION = 1_000_000
COV_MAX = 0.10
BETA_TECHO = 8.0
FORM_ITER, FORM_TOL, FORM_H = 60, 1e-3, 1e-4
BETA_REFERENCIA = 3.8


# ---------------------------------------------------------------- espacio normal estándar
def _x_de_u(var: dict, u: np.ndarray) -> dict:
    """u (n, 7) ~ N(0, I) → variables físicas (multiplicadores del nominal), con la misma parametrización que la F3."""
    out = {}
    for j, k in enumerate(VARS):
        lam, v = var[k]
        if k == "D":
            out[k] = lam * (1 + v * u[:, j])
        elif k == "L":
            escala = math.sqrt(6) * lam * v / math.pi
            loc = lam - 0.5772156649 * escala
            out[k] = loc - escala * np.log(-log_ndtr(u[:, j]))       # CDF inversa de Gumbel de máximos
        else:
            s = math.sqrt(math.log(1 + v * v))
            out[k] = lam * np.exp(-s * s / 2 + s * u[:, j])
    return out


# ---------------------------------------------------------------- funciones de estado límite (de la F3)
def _g_viga(n_barras_area, b, dd, mD, mL, fc_nom, fy_nom):
    def g(x):
        R = x["thR_flex"] * f3._mn_viga_vec(n_barras_area, b, dd, fc_nom * x["fc"], fy_nom * x["fy"])
        return R - x["thS"] * (x["D"] * mD + x["L"] * mL)
    return g


def _g_col(tabla, PD, PL, mxD, mxL, myD, myL, fc_nom, fy_nom):
    """Mismo dominio de falla que la F3 (P ≥ P₀ o M > Mn(P)), escrito como min(1 − M/Mn, 1 − P/P₀) para que g sea
    continua y FORM tenga gradiente cuando la falla es por carga axial (enmienda del prerregistro tras el piloto)."""
    _, _, _, ast, d = tabla

    def g(x):
        fc, fy = fc_nom * x["fc"], fy_nom * x["fy"]
        P = x["thS"] * (x["D"] * PD + x["L"] * PL)
        Mx = x["thS"] * np.abs(x["D"] * mxD + x["L"] * mxL)
        My = x["thS"] * np.abs(x["D"] * myD + x["L"] * myL)
        Mn = x["thR_col"] * f3._interp_col(tabla, fc, fy, P)
        g_ax = 1.0 - P / ((0.85 * fc * (d.h * d.b - ast) + fy * ast) / 1e3)
        with np.errstate(divide="ignore", invalid="ignore"):
            g_m = np.where(Mn > 0, 1.0 - (Mx + My) / np.where(Mn > 0, Mn, 1.0), g_ax - 1.0)   # Mn ≤ 0 → falla
        return np.minimum(g_m, g_ax)
    return g


# ---------------------------------------------------------------- FORM + muestreo por importancia
def _form(g, var) -> tuple[np.ndarray, bool]:
    u = np.zeros(len(VARS))
    for _ in range(FORM_ITER):
        pts = np.vstack([u, u + FORM_H * np.eye(len(VARS))])
        gv = g(_x_de_u(var, pts))
        g0, grad = gv[0], (gv[1:] - gv[0]) / FORM_H
        n2 = float(grad @ grad)
        if n2 == 0 or not np.isfinite(n2):
            return u, False
        u_new = (grad @ u - g0) / n2 * grad
        if np.linalg.norm(u_new) > 3 * BETA_TECHO:               # divergencia: se detiene lejos (techo)
            return u_new, False
        if np.linalg.norm(u_new - u) < FORM_TOL:
            return u_new, True
        u = u_new
    return u, False


def _is(g, var, u_star, n, rng) -> tuple[float, float]:
    z = rng.standard_normal((n, len(VARS)))
    w = np.exp(-z @ u_star - 0.5 * float(u_star @ u_star))
    iw = (g(_x_de_u(var, u_star + z)) < 0) * w
    pf = float(iw.mean())
    cov = float(iw.std(ddof=1) / (math.sqrt(n) * pf)) if pf > 0 else float("inf")
    return pf, cov


def _beta_elemento(g, var, rng) -> dict:
    u_star, convergio = _form(g, var)
    nu = float(np.linalg.norm(u_star))
    signo = -1.0 if g(_x_de_u(var, np.zeros((1, len(VARS)))))[0] < 0 else 1.0   # falla en la mediana → β < 0
    alpha2 = (u_star / nu) ** 2 if nu > 0 else np.zeros(len(VARS))
    if signo > 0 and nu > BETA_TECHO:
        if not convergio:            # FORM divergió: Monte Carlo directo de resguardo para no esconder un elemento débil
            fallas = int((g(_x_de_u(var, rng.standard_normal((N_IS, len(VARS))))) < 0).sum())
            if fallas:
                pf = fallas / N_IS
                cov = math.sqrt((1 - pf) / (N_IS * pf))
                return {"beta": float(-ndtri(pf)), "techo": False, "cov": cov, "impreciso": cov > COV_MAX,
                        "form": False, "alpha2": alpha2}
        return {"beta": BETA_TECHO, "techo": True, "cov": 0.0, "impreciso": False, "form": convergio, "alpha2": alpha2}
    pf, cov = _is(g, var, u_star, N_IS, rng)
    if cov > COV_MAX:
        pf, cov = _is(g, var, u_star, N_IS_REPETICION, rng)
    if pf <= 0:
        return {"beta": BETA_TECHO, "techo": True, "cov": cov, "impreciso": True, "form": convergio, "alpha2": alpha2}
    beta = float(-ndtri(min(pf, 1 - 1e-16)))
    return {"beta": min(beta, BETA_TECHO), "techo": beta >= BETA_TECHO, "cov": cov, "impreciso": cov > COV_MAX,
            "form": convergio, "alpha2": alpha2}


# ---------------------------------------------------------------- por edificio
def evaluar(c: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de
    p = f3._proyecto(de, c)
    inf = de.disenar_edificio(p)
    fila = {k: c[k] for k in ("id", "N", "zona", "perfil", "uso", "grupo_uso", "fc_mpa", "aa", "capacidad")}
    if not inf.cumple:
        return {**fila, "estado": "no_reproduce", "motivo": "; ".join(inf.fallas[:2])[:200]}
    m = de.construir_modelo(p)
    sis = de.analisis_sismico(p, m)
    der = de._s3.analizar_fhe(m.portico, m.pisos, sis["x"]["Fs_deriva_kn"], sis["y"]["Fs_deriva_kn"], "general", True)
    F, _ = de._resolver_casos(p, m, sis, der["Ax"])
    rec, fc_nom, fy_nom = p.recubrimiento_mm, p.fc_mpa, p.fy_mpa
    elementos = []                                                # (g, tipo, nivel/piso)
    for fv in inf.vigas:
        d = fv["diseno"]
        crit = f3._vigas_criticas(de, p, m, F, fv["nivel"])
        dd = de._dv._d(d.h, d.dia, d.estribo_dia, rec)
        area = de._vg.AREA_MM2[d.dia]
        for signo, n_barras in (("neg", d.n_sup), ("pos", d.n_inf)):
            _, mD, mL = crit[signo]
            if mD + mL > 0:
                elementos.append((_g_viga(n_barras * area, d.b, dd, mD, mL, fc_nom, fy_nom), "viga", fv["nivel"]))
    tablas = {}
    for fcol in inf.columnas:
        d, piso = fcol["diseno"], fcol["piso"] - 1
        clave = (d.h, d.b, d.n_cara, d.dia, d.estribo)
        if clave not in tablas:
            tablas[clave] = f3._tabla_col(de._col, d, rec, fc_nom, fy_nom)
        for PD, PL, (mxD, mxL), (myD, myL) in f3._columnas_criticas(m, F, piso):
            elementos.append((_g_col(tablas[clave], PD, PL, mxD, mxL, myD, myL, fc_nom, fy_nom), "columna", fcol["piso"]))
    sal = {**fila, "estado": "ok", "n_elementos": len(elementos)}
    for iv, (nom_var, var) in enumerate(VARIANTES.items()):
        res = []
        for ie, (g, tipo, nivel) in enumerate(elementos):
            rng = np.random.default_rng([SEMILLA, int(c["id"]), iv, ie])
            res.append((_beta_elemento(g, var, rng), tipo, nivel))
        r, tipo, nivel = min(res, key=lambda t: t[0]["beta"])
        sal[f"beta_{nom_var}"] = round(r["beta"], 4)
        sal[f"techo_{nom_var}"] = r["techo"]
        sal[f"cov_{nom_var}"] = round(r["cov"], 4)
        sal[f"form_{nom_var}"] = r["form"]
        sal[f"critico_{nom_var}"] = f"{tipo}@{nivel}"
        sal[f"dominante_{nom_var}"] = VARS[int(np.argmax(r["alpha2"]))]
        sal[f"alpha2_{nom_var}"] = ";".join(f"{a:.3f}" for a in r["alpha2"])
        sal[f"imprecisos_{nom_var}"] = sum(t[0]["impreciso"] for t in res)
    return sal


CAMPOS = (["id", "estado", "motivo", "N", "zona", "perfil", "uso", "grupo_uso", "fc_mpa", "aa", "capacidad", "n_elementos"]
          + [f"{c}_{v}" for v in VARIANTES
             for c in ("beta", "techo", "cov", "form", "critico", "dominante", "alpha2", "imprecisos")])


def _leer(ruta: Path) -> list[dict]:
    filas = []
    with ruta.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for k, v in list(r.items()):
                if k.startswith(("beta_", "cov_")) and v not in ("", None):
                    r[k] = float(v)
                elif k.startswith(("techo_", "form_")):
                    r[k] = v == "True"
                elif k.startswith(("imprecisos_", "n_elementos")) and v not in ("", None):
                    r[k] = int(v)
            filas.append(r)
    return sorted(filas, key=lambda r: int(r["id"]))


# ---------------------------------------------------------------- resumen
def _bootstrap(est_fn, grupos, reps=2000, semilla=SEMILLA):
    rng = np.random.default_rng(semilla)
    grupos = [np.asarray(g, float) for g in grupos]
    est = float(est_fn(*grupos))
    bs = [est_fn(*[g[rng.integers(0, len(g), len(g))] for g in grupos]) for _ in range(reps)]
    return est, [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def _iqr(a):
    return float(np.percentile(a, 75) - np.percentile(a, 25))


def _desc(b):
    b = np.asarray(b, float)
    return {"n": len(b), "mediana": float(np.median(b)), "p10": float(np.percentile(b, 10)),
            "frac_menor_3_8": float((b < BETA_REFERENCIA).mean())} if len(b) else {"n": 0}


def calidad(filas: list[dict]) -> dict:
    """Q1: concordancia con el Monte Carlo de la F3 donde tuvo ≥ 100 fallas; Q2: fracción de elementos imprecisos."""
    ruta_f3 = RAIZ / "data" / "memorias_sinteticas" / "f3" / "beta_por_edificio.csv"
    mc = {r["id"]: r for r in f3._leer(ruta_f3)}
    umbral = float(-ndtri(100 / f3.N_MC))                          # β_MC con 100 fallas en 10⁶ ≈ 3,72
    dif = []
    for f in filas:
        if f["estado"] != "ok" or f["id"] not in mc:
            continue
        for v in VARIANTES:
            r = mc[f["id"]]
            if not r[f"censurado_{v}"] and r[f"beta_{v}"] <= umbral:
                dif.append(abs(f[f"beta_{v}"] - r[f"beta_{v}"]))
    dif = np.array(dif)
    n_elem = sum(f["n_elementos"] * len(VARIANTES) for f in filas if f["estado"] == "ok")
    impr = sum(f[f"imprecisos_{v}"] for f in filas if f["estado"] == "ok" for v in VARIANTES)
    q1 = {"n_pares": int(len(dif)), "frac_dif_menor_0_10": float((dif <= 0.10).mean()) if len(dif) else None,
          "mediana_dif": float(np.median(dif)) if len(dif) else None, "p95_dif": float(np.percentile(dif, 95)) if len(dif) else None}
    q1["cumple"] = bool(len(dif) and q1["frac_dif_menor_0_10"] >= 0.95 and q1["mediana_dif"] <= 0.03)
    q2 = {"elementos": n_elem, "imprecisos": int(impr), "frac": impr / max(1, n_elem)}
    q2["cumple"] = q2["frac"] <= 0.01
    return {"Q1": q1, "Q2": q2, "cumple": q1["cumple"] and q2["cumple"]}


def resumir(filas: list[dict]) -> dict:
    ok = [f for f in filas if f["estado"] == "ok"]
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_F3B_SIN_CENSURA.md", "n_edificios": len(filas),
           "n_ok": len(ok), "no_reproduce": [f["id"] for f in filas if f["estado"] != "ok"],
           "N_IS": N_IS, "beta_techo": BETA_TECHO, "variantes": VARIANTES, "calidad": calidad(filas)}
    if not out["calidad"]["cumple"]:
        out["veredicto"] = "NO EVALUADO: falla la puerta de calidad"
        return out
    veredictos = {"H-F3b-1": [], "H-F3b-2": [], "H-F3b-3": []}
    out["hipotesis"], out["descriptivo"] = {}, {}
    for v in VARIANTES:
        beta = lambda pred: [f[f"beta_{v}"] for f in ok if pred(f)]  # noqa: E731
        todos = beta(lambda f: True)
        r = {"techos": int(sum(f[f"techo_{v}"] for f in ok)), "global": _desc(todos)}
        alta, baja = beta(lambda f: f["zona"] == "alta"), beta(lambda f: f["zona"] == "baja")
        est, ic = _bootstrap(lambda a, b: np.median(a) - np.median(b), [alta, baja])
        r["H-F3b-1"] = {"alta_menos_baja": est, "ic95": ic, "n": [len(alta), len(baja)], "cumple": est >= 0.5 and ic[0] > 0}
        est, ic = _bootstrap(_iqr, [todos])
        r["H-F3b-2"] = {"iqr": est, "ic95": ic, "cumple": est >= 0.75 and ic[0] >= 0.5}
        altos = beta(lambda f: f["zona"] == "baja" and int(f["N"]) >= 9)
        bajos = beta(lambda f: f["zona"] == "baja" and int(f["N"]) <= 5)
        est, ic = _bootstrap(lambda a, b: np.median(a) - np.median(b), [altos, bajos])
        r["H-F3b-3"] = {"altos_menos_bajos": est, "ic95": ic, "n": [len(altos), len(bajos)], "cumple": est > 0 and ic[0] > 0}
        out["hipotesis"][v] = r
        for h in veredictos:
            veredictos[h].append(r[h]["cumple"])
        d = {}
        for campo, valores in (("zona", ("baja", "intermedia", "alta")), ("perfil", ("C", "D", "E")),
                               ("fc_mpa", ("21.0", "28.0", "35.0")), ("grupo_uso", ("I", "II", "III", "IV"))):
            d[campo] = {x: _desc(beta(lambda f, x=x, campo=campo: str(f[campo]) == x)) for x in valores}
            d[campo] = {k: s for k, s in d[campo].items() if s["n"]}
        d["N"] = {g: _desc(beta(lambda f, lo=lo, hi=hi: lo <= int(f["N"]) <= hi))
                  for g, (lo, hi) in {"1-5": (1, 5), "6-8": (6, 8), "9+": (9, 99)}.items()}
        dom = [f[f"dominante_{v}"] for f in ok]
        d["variable_dominante"] = {k: dom.count(k) / len(dom) for k in VARS if dom.count(k)}
        d["critico_columna_frac"] = float(np.mean([f[f"critico_{v}"].startswith("columna") for f in ok]))
        d["reserva_sobre_3_8"] = {q: float(np.percentile(np.array(todos) - BETA_REFERENCIA, q)) for q in (10, 25, 50, 75, 90)}
        d["form_no_convergio"] = int(sum(not f[f"form_{v}"] for f in ok))
        out["descriptivo"][v] = d
    out["veredicto"] = {h: ("CONFIRMADA" if all(c) else "DEPENDE DEL SUPUESTO" if c[0] else "REFUTADA")
                        for h, c in veredictos.items()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, default=0)
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--hasta", default=None, help="HH:MM: se detiene a esa hora (reanudable)")
    ap.add_argument("--salida", default=str(RAIZ / "data" / "memorias_sinteticas" / "f3b"))
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    with (RAIZ / "data" / "memorias_sinteticas" / "corpus.csv").open(encoding="utf-8") as f:
        casos = [r for r in csv.DictReader(f) if r["estado"] == "ok"]
    if a.piloto:
        casos = casos[:a.piloto]
    out = Path(a.salida if not a.piloto else Path(a.salida) / "piloto")
    out.mkdir(parents=True, exist_ok=True)
    ruta = out / "beta_por_edificio.csv"
    hechos = set()
    if ruta.exists():
        with ruta.open(encoding="utf-8") as f:
            hechos = {r["id"] for r in csv.DictReader(f)}
    pendientes = [c for c in casos if c["id"] not in hechos]
    print(f"{len(hechos)} hechos, {len(pendientes)} pendientes, {a.hilos} procesos", flush=True)
    t0 = time.time()
    if pendientes:
        with Pool(a.hilos, initializer=f3._iniciar) as pool, ruta.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
            if not hechos:
                w.writeheader()
            for k, fila in enumerate(pool.imap_unordered(evaluar, pendientes, chunksize=1), 1):
                w.writerow(fila)
                f.flush()
                if k % 25 == 0 or a.piloto:
                    print(f"{k}/{len(pendientes)} en {time.time() - t0:.0f} s", flush=True)
                if a.hasta and time.strftime("%H:%M") >= a.hasta:
                    print("hora límite: se detiene (reanudable)", flush=True)
                    pool.terminate()
                    return
    filas = _leer(ruta)
    if a.piloto:                     # el piloto solo verifica que corre y la puerta de calidad; no mira hipótesis
        print(json.dumps({"piloto": len(filas), "segundos": round(time.time() - t0), "calidad": calidad(filas)},
                         ensure_ascii=False))
        return
    res = resumir(filas)
    res["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_f3b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"calidad": res["calidad"]["cumple"], "veredicto": res["veredicto"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
