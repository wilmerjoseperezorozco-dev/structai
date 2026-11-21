"""F3 (#275, #276): confiabilidad a gravedad de los pórticos del corpus F1. Ver docs/memoria_calculo/PRERREGISTRO_F3_CONFIABILIDAD.md.

Por edificio con solución: rehace el diseño F4 con las secciones óptimas del corpus, toma las fuerzas D y L del análisis 3D
y estima por Monte Carlo el β a 50 años de las vigas (flexión en la sección crítica de cada signo y nivel) y de las columnas
(flexo-compresión biaxial con la curva NOMINAL, sin φ). Reporta β del elemento crítico (mínimo) por edificio, en tres
variantes de los supuestos probabilísticos, y la deriva ante el sismo de diseño con rigidez y espectro inciertos.

Uso:  python -I scripts/memorias_sinteticas/confiabilidad_f3.py [--piloto 3] [--hilos 8]
Salida: data/memorias_sinteticas/f3/{beta_por_edificio.csv, resultados_f3.json}
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):   # antes de importar numpy: 1 hilo por proceso
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

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = 2753
N_MC = 1_000_000
N_DERIVA = 100_000
BETA_CENSURA = 4.5                     # 0 fallas en 10⁶ → Pf < 3·10⁻⁶ (95 %)
FC_GRID = np.linspace(0.45, 2.0, 11)   # multiplicadores de f'c nominal para la rejilla de curvas de columna
FY_GRID = np.linspace(0.85, 1.45, 6)
N_P = 400                              # puntos de la tabla Mn(P) por nodo (f'c, fy)
BLOQUE = 1 << 16

# (λ, V) por variable; "baja" = menos incertidumbre (más favorable), "alta" = más
VARIANTES = {
    "central": {"fc": (1.20, 0.15), "fy": (1.13, 0.05), "D": (1.05, 0.10), "L": (1.00, 0.18),
                "thR_flex": (1.02, 0.06), "thR_col": (1.00, 0.08), "thS": (1.00, 0.10)},
    "baja":    {"fc": (1.30, 0.10), "fy": (1.15, 0.03), "D": (1.03, 0.08), "L": (0.95, 0.15),
                "thR_flex": (1.05, 0.05), "thR_col": (1.02, 0.06), "thS": (1.00, 0.08)},
    "alta":    {"fc": (1.10, 0.20), "fy": (1.10, 0.08), "D": (1.08, 0.12), "L": (1.05, 0.25),
                "thR_flex": (1.00, 0.10), "thR_col": (0.98, 0.12), "thS": (1.00, 0.15)},
}
KAPPA = (0.7, 1.3)                     # rigidez efectiva / modelo fisurado (deriva)
SIGMA_SA = 0.3                         # error epistémico del espectro (deriva)


def _lognormal(rng, lam, v, n):
    s = math.sqrt(math.log(1 + v * v))
    return rng.lognormal(math.log(lam) - s * s / 2, s, n)


def _muestras(rng, var: dict, n: int) -> dict:
    lamD, vD = var["D"]
    lamL, vL = var["L"]
    escala = math.sqrt(6) * lamL * vL / math.pi           # Gumbel de máximos con media λ y CoV V
    return {"fc": _lognormal(rng, *var["fc"], n), "fy": _lognormal(rng, *var["fy"], n),
            "D": rng.normal(lamD, lamD * vD, n), "L": rng.gumbel(lamL - 0.5772156649 * escala, escala, n),
            "thR_flex": _lognormal(rng, *var["thR_flex"], n), "thR_col": _lognormal(rng, *var["thR_col"], n),
            "thS": _lognormal(rng, *var["thS"], n)}


def _beta(fallas: int, n: int) -> tuple[float, bool]:
    from scipy.stats import norm
    if fallas == 0:
        return BETA_CENSURA, True
    return float(-norm.ppf(fallas / n)), False


def _proyecto(de, c: dict):
    n = int(c["N"])
    abajo = math.ceil(n / 2)
    cols = tuple(float(c["c_inferior_mm"]) if i < abajo else float(c["c_superior_mm"]) for i in range(n))
    vigas = ((float(c["b_viga_mm"]), float(c["h_viga_mm"])),) * n
    return de.ProyectoEdificio3D(
        luces_x_m=(float(c["Lx_m"]),) * int(c["vanos_x"]), luces_y_m=(float(c["Ly_m"]),) * int(c["vanos_y"]),
        alturas_piso_m=(float(c["hp_m"]),) * n, columnas_mm=cols, vigas_mm=vigas, carga_muerta_kpa=float(c["D_kpa"]),
        carga_viva_kpa=float(c["L_kpa"]), aa=float(c["aa"]), av=float(c["av"]), perfil_suelo=c["perfil"],
        grupo_uso=c["grupo_uso"], capacidad=c["capacidad"], fc_mpa=float(c["fc_mpa"]), nombre=f"F3 {int(c['id']):05d}",
        uso=c["uso"])


def _vigas_criticas(de, p, m, F, nivel: int):
    """Por signo: (M_D, M_L) en la sección con mayor momento nominal D+L del nivel (kN·m; negativo = tracción arriba)."""
    piso = nivel - 1
    c = p.columnas_mm[piso] / 1000
    mejor = {"neg": (0.0, 0.0, 0.0), "pos": (0.0, 0.0, 0.0)}
    for k, t in enumerate(m.meta):
        if t[0] not in ("vx", "vy") or t[1] != nivel:
            continue
        L = m.portico.longitud(m.portico.elementos[k])
        wD, wL = m.w_viga[k]
        xs = np.concatenate([[c / 2, L - c / 2], np.linspace(c / 2, L - c / 2, 21)[1:-1]])
        md = -F[0, k, 5] + F[0, k, 1] * xs - wD * xs ** 2 / 2
        ml = -F[1, k, 5] + F[1, k, 1] * xs - wL * xs ** 2 / 2
        tot = md + ml
        i_neg, i_pos = int(np.argmin(tot)), int(np.argmax(tot))
        if -tot[i_neg] > mejor["neg"][0]:
            mejor["neg"] = (-tot[i_neg], -md[i_neg], -ml[i_neg])
        if tot[i_pos] > mejor["pos"][0]:
            mejor["pos"] = (tot[i_pos], md[i_pos], ml[i_pos])
    return mejor


def _mn_viga_vec(As, b, d, fc, fy):
    a = As * fy / (0.85 * fc * b)
    return As * fy * (d - a / 2) / 1e6


def _columnas_criticas(m, F, piso: int):
    """Columna más cargada y la de mayor momento de gravedad: (P_D, P_L, (MxD, MxL), (MyD, MyL)) con el extremo que
    gobierna con D+L nominal."""
    cols = [k for k, t in enumerate(m.meta) if t[0] == "col" and t[1] == piso]
    filas = []
    for k in cols:
        def peor(a, b):
            ext = [(F[0, k, a], F[1, k, a]), (F[0, k, b], F[1, k, b])]
            return max(ext, key=lambda e: abs(e[0] + e[1]))
        mx, my = peor(5, 11), peor(4, 10)
        filas.append((F[0, k, 0], F[1, k, 0], mx, my))
    por_p = max(filas, key=lambda f: f[0] + f[1])
    por_m = max(filas, key=lambda f: abs(sum(f[2])) + abs(sum(f[3])))
    return [por_p] if por_m is por_p else [por_p, por_m]


def _tabla_col(col_mod, d, rec, fc_nom, fy_nom):
    """Tabla Mn nominal en la rejilla (f'c, fy, u = P/P₀). Se construye una vez por diseño de columna."""
    fcg, fyg = fc_nom * FC_GRID, fy_nom * FY_GRID
    curvas = [[col_mod.curva(d.h, d.b, d.n_cara, d.dia, d.estribo, rec, float(round(a, 4)), float(round(bb, 4)),
                             con_phi=False) for bb in fyg] for a in fcg]
    ug = np.linspace(0.0, 1.0, N_P)                       # u = P / P₀(f'c, fy): la frontera P₀ queda fija en u = 1
    tab = np.array([[np.nan_to_num(col_mod.mn_arr(cv, ug * cv.po), nan=0.0) for cv in fila] for fila in curvas])
    ast = col_mod.SeccionColumna(d.h, d.b, d.n_cara, d.dia, d.estribo, rec).ast
    return fcg, fyg, tab.ravel(), ast, d


def _mn_col_vec(col_mod, d, rec, fc_nom, fy_nom, fc, fy, P):
    """Mn nominal(P) por interpolación trilineal en la rejilla (f'c, fy, u); 0 fuera de rango (P > P₀ → falla)."""
    return _interp_col(_tabla_col(col_mod, d, rec, fc_nom, fy_nom), fc, fy, P)


def _interp_col(tabla, fc, fy, P):
    fcg, fyg, plano, ast, d = tabla
    sj, si = N_P, len(fyg) * N_P
    out = np.empty(len(P))
    for a in range(0, len(P), BLOQUE):                    # por bloques: los índices aleatorios caben en caché
        z = slice(a, a + BLOQUE)
        po = (0.85 * fc[z] * (d.h * d.b - ast) + fy[z] * ast) / 1e3
        u = P[z] / po
        fi = np.clip(np.interp(fc[z], fcg, np.arange(len(fcg))), 0, len(fcg) - 1 - 1e-9)
        fj = np.clip(np.interp(fy[z], fyg, np.arange(len(fyg))), 0, len(fyg) - 1 - 1e-9)
        fk = np.clip(u * (N_P - 1), 0, N_P - 1 - 1e-9)
        i0, j0, k0 = fi.astype(np.int64), fj.astype(np.int64), fk.astype(np.int64)
        ti, tj, tk = fi - i0, fj - j0, fk - k0
        base = i0 * si + j0 * sj + k0
        acc = np.zeros(len(u))
        for di, wi in ((0, 1 - ti), (1, ti)):
            for dj, wj in ((0, 1 - tj), (1, tj)):
                w = wi * wj
                b0 = base + di * si + dj * sj
                acc += w * ((1 - tk) * plano[b0] + tk * plano[b0 + 1])
        out[z] = np.where(u >= 1.0, 0.0, acc)
    return out


def _iniciar():
    os.environ["OMP_NUM_THREADS"] = "1"


def evaluar(c: dict) -> dict:
    sys.path.insert(0, str(RAIZ / "packages" / "orquestador"))
    from src import diseno_edificio_3d as de
    p = _proyecto(de, c)
    inf = de.disenar_edificio(p)
    fila = {k: c[k] for k in ("id", "N", "zona", "perfil", "uso", "grupo_uso", "fc_mpa", "aa", "capacidad")}
    if not inf.cumple:
        return {**fila, "estado": "no_reproduce", "motivo": "; ".join(inf.fallas[:2])[:200]}
    m = de.construir_modelo(p)
    sis = de.analisis_sismico(p, m)
    der = de._s3.analizar_fhe(m.portico, m.pisos, sis["x"]["Fs_deriva_kn"], sis["y"]["Fs_deriva_kn"], "general", True)
    F, _ = de._resolver_casos(p, m, sis, der["Ax"])
    rec, fc_nom, fy_nom = p.recubrimiento_mm, p.fc_mpa, p.fy_mpa
    n = len(p.alturas_piso_m)
    sal = {**fila, "estado": "ok"}
    for nom_var, var in VARIANTES.items():
        rng = np.random.default_rng([SEMILLA, int(c["id"]), list(VARIANTES).index(nom_var)])
        s = _muestras(rng, var, N_MC)
        fc, fy = fc_nom * s["fc"], fy_nom * s["fy"]
        criticos = []                                          # (β, censurado, tipo, piso)
        for fv in inf.vigas:
            d = fv["diseno"]
            crit = _vigas_criticas(de, p, m, F, fv["nivel"])
            dd = de._dv._d(d.h, d.dia, d.estribo_dia, rec)
            area = de._vg.AREA_MM2[d.dia]
            for signo, n_barras in (("neg", d.n_sup), ("pos", d.n_inf)):
                _, mD, mL = crit[signo]
                if mD + mL <= 0:
                    continue
                R = s["thR_flex"] * _mn_viga_vec(n_barras * area, d.b, dd, fc, fy)
                S = s["thS"] * (s["D"] * mD + s["L"] * mL)
                b_, cens = _beta(int((R - S < 0).sum()), N_MC)
                criticos.append((b_, cens, "viga", fv["nivel"]))
        for fcol in inf.columnas:
            d, piso = fcol["diseno"], fcol["piso"] - 1
            for PD, PL, (mxD, mxL), (myD, myL) in _columnas_criticas(m, F, piso):
                P = s["thS"] * (s["D"] * PD + s["L"] * PL)
                Mx = s["thS"] * np.abs(s["D"] * mxD + s["L"] * mxL)
                My = s["thS"] * np.abs(s["D"] * myD + s["L"] * myL)
                Mn = s["thR_col"] * _mn_col_vec(de._col, d, rec, fc_nom, fy_nom, fc, fy, P)
                with np.errstate(divide="ignore", invalid="ignore"):
                    falla = (Mn <= 0) | ((Mx + My) / Mn > 1.0)
                b_, cens = _beta(int(falla.sum()), N_MC)
                criticos.append((b_, cens, "columna", fcol["piso"]))
        b_min = min(criticos, key=lambda t: t[0])
        sal[f"beta_{nom_var}"] = round(b_min[0], 4)
        sal[f"censurado_{nom_var}"] = all(t[1] for t in criticos if t[0] == b_min[0])
        sal[f"critico_{nom_var}"] = f"{b_min[2]}@{b_min[3]}"
        sal[f"n_elementos_{nom_var}"] = len(criticos)
    # deriva ante el sismo de diseño (descriptivo)
    rng = np.random.default_rng([SEMILLA, int(c["id"]), 99])
    kappa = rng.uniform(*KAPPA, N_DERIVA)
    eps = rng.lognormal(0.0, SIGMA_SA, N_DERIVA)
    fa, fv_ = sis["fa"], sis["fv"]
    uso_real = np.zeros(N_DERIVA)
    reserva_cuta = []
    for eje in ("x", "y"):
        T_mod, T_dis = sis[eje]["T_modelo_s"], sis[eje]["T_s"]
        sa_dis = de._gp.sa_espectro(T_dis, p.aa, p.av, fa, fv_, 1.0)
        T_real = T_mod / np.sqrt(kappa)
        sa_real = np.array([de._gp.sa_espectro(float(t), p.aa, p.av, fa, fv_, 1.0) for t in T_real[:2000]])
        sa_real = np.interp(T_real, np.sort(T_real[:2000]), sa_real[np.argsort(T_real[:2000])])
        uso_real = np.maximum(uso_real, der["uso_max_limite"] * eps * sa_real / sa_dis / kappa)
        reserva_cuta.append(de._gp.sa_espectro(T_mod, p.aa, p.av, fa, fv_, 1.0) / sa_dis)
    sal["uso_deriva_diseno"] = round(float(der["uso_max_limite"]), 4)
    sal["P_deriva_excede"] = round(float((uso_real > 1.0).mean()), 5)
    sal["Sa_Tmodelo_sobre_Sa_diseno"] = round(float(min(reserva_cuta)), 4)
    sal["gobierna_CuTa"] = bool(sis["x"]["gobierna_CuTa"] or sis["y"]["gobierna_CuTa"])
    return sal


CAMPOS = (["id", "estado", "motivo", "N", "zona", "perfil", "uso", "grupo_uso", "fc_mpa", "aa", "capacidad"]
          + [f"{c}_{v}" for v in VARIANTES for c in ("beta", "censurado", "critico", "n_elementos")]
          + ["uso_deriva_diseno", "P_deriva_excede", "Sa_Tmodelo_sobre_Sa_diseno", "gobierna_CuTa"])


def _leer(ruta: Path) -> list[dict]:
    """Filas del CSV con sus tipos (el resumen opera sobre números y booleanos)."""
    filas = []
    with ruta.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for k, v in list(r.items()):
                if k.startswith(("beta_", "P_deriva", "Sa_T", "uso_deriva")) and v not in ("", None):
                    r[k] = float(v)
                elif k.startswith(("censurado_", "gobierna_")):
                    r[k] = v == "True"
            filas.append(r)
    return sorted(filas, key=lambda r: int(r["id"]))


def _bootstrap_mediana(a, b=None, reps=2000, semilla=SEMILLA):
    rng = np.random.default_rng(semilla)
    a = np.asarray(a, float)
    if b is None:
        est = float(np.median(a))
        bs = np.median(rng.choice(a, (reps, len(a))), axis=1)
    else:
        b = np.asarray(b, float)
        est = float(np.median(a) - np.median(b))
        bs = np.median(rng.choice(a, (reps, len(a))), axis=1) - np.median(rng.choice(b, (reps, len(b))), axis=1)
    return est, [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def resumir(filas: list[dict]) -> dict:
    ok = [f for f in filas if f["estado"] == "ok"]
    out = {"prerregistro": "docs/memoria_calculo/PRERREGISTRO_F3_CONFIABILIDAD.md", "n_edificios": len(filas),
           "n_ok": len(ok), "no_reproduce": [f["id"] for f in filas if f["estado"] != "ok"], "N_MC": N_MC,
           "beta_censura": BETA_CENSURA, "variantes": VARIANTES, "hipotesis": {}}
    veredictos = {"H-F3a": [], "H-F3b": [], "H-F3c": []}
    for v in VARIANTES:
        b = np.array([f[f"beta_{v}"] for f in ok])
        r = {"mediana_beta": float(np.median(b)), "censurados": int(sum(f[f"censurado_{v}"] for f in ok)),
             "frac_beta_menor_3": float((b < 3.0).mean()), "frac_beta_menor_3_8": float((b < 3.8).mean())}
        est, ic = _bootstrap_mediana(b)
        r["H-F3a"] = {"mediana": est, "ic95": ic, "cumple": est >= 3.8 and ic[0] >= 3.5}
        alta = [f[f"beta_{v}"] for f in ok if f["zona"] == "alta"]
        baja = [f[f"beta_{v}"] for f in ok if f["zona"] == "baja"]
        est, ic = _bootstrap_mediana(alta, baja)
        r["H-F3b"] = {"diferencia_alta_menos_baja": est, "ic95": ic, "n": [len(alta), len(baja)],
                      "cumple": est >= 0.5 and ic[0] > 0}
        bajos = [f[f"beta_{v}"] for f in ok if f["zona"] == "baja" and int(f["N"]) <= 5]
        altos = [f[f"beta_{v}"] for f in ok if f["zona"] == "baja" and int(f["N"]) >= 9]
        est, ic = _bootstrap_mediana(bajos, altos)
        r["H-F3c"] = {"diferencia_bajos_menos_altos": est, "ic95": ic, "n": [len(bajos), len(altos)],
                      "cumple": est > 0 and ic[0] > 0}
        tipos = [f[f"critico_{v}"].split("@")[0] for f in ok]
        r["critico_columna_frac"] = float(np.mean([t == "columna" for t in tipos]))
        r["mediana_por_zona"] = {z: float(np.median([f[f"beta_{v}"] for f in ok if f["zona"] == z]))
                                 for z in ("baja", "intermedia", "alta") if any(f["zona"] == z for f in ok)}
        r["mediana_por_perfil"] = {s: float(np.median([f[f"beta_{v}"] for f in ok if f["perfil"] == s]))
                                   for s in ("C", "D", "E") if any(f["perfil"] == s for f in ok)}
        r["mediana_por_fc"] = {str(x): float(np.median([f[f"beta_{v}"] for f in ok if float(f["fc_mpa"]) == x]))
                               for x in (21.0, 28.0, 35.0) if any(float(f["fc_mpa"]) == x for f in ok)}
        out["hipotesis"][v] = r
        for h in veredictos:
            veredictos[h].append(r[h]["cumple"])
    out["veredicto"] = {h: ("CONFIRMADA" if all(c) else "DEPENDE DEL SUPUESTO" if c[0] else "REFUTADA")
                        for h, c in veredictos.items()}
    pd = np.array([f["P_deriva_excede"] for f in ok])
    cuta = [f for f in ok if f["gobierna_CuTa"]]
    out["deriva"] = {"mediana_P_excede": float(np.median(pd)), "frac_P_excede_mayor_10": float((pd > 0.10).mean()),
                     "frac_gobierna_CuTa": len(cuta) / max(1, len(ok)),
                     "mediana_Sa_Tmodelo_sobre_Sa_diseno_si_CuTa": float(np.median([f["Sa_Tmodelo_sobre_Sa_diseno"] for f in cuta])) if cuta else None}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piloto", type=int, default=0, help="solo los primeros k edificios ok (verificar que corre)")
    ap.add_argument("--hilos", type=int, default=6)
    ap.add_argument("--hasta", default=None, help="HH:MM: se detiene a esa hora (reanudable)")
    ap.add_argument("--salida", default=str(RAIZ / "data" / "memorias_sinteticas" / "f3"))
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
    if ruta.exists():                                      # reanudable: cada edificio se escribe al terminar
        with ruta.open(encoding="utf-8") as f:
            hechos = {r["id"] for r in csv.DictReader(f)}
    pendientes = [c for c in casos if c["id"] not in hechos]
    print(f"{len(hechos)} hechos, {len(pendientes)} pendientes, {a.hilos} procesos", flush=True)
    t0 = time.time()
    if pendientes:
        with Pool(a.hilos, initializer=_iniciar) as pool, ruta.open("a", encoding="utf-8", newline="") as f:
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
    if a.piloto:
        print(f"piloto: {len(filas)} edificios en {time.time() - t0:.0f} s; estados {[f['estado'] for f in filas]}")
        return
    res = resumir(filas)
    res["segundos"] = round(time.time() - t0, 1)
    (out / "resultados_f3.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"veredicto": res["veredicto"], "n_ok": res["n_ok"], "no_reproduce": len(res["no_reproduce"])},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
