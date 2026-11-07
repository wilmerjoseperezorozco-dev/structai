"""H4 y H5 (protocolo §23) sobre los máximos anuales del IDEAM.

H4: GEV con localización μ(t) = μ0 + μ1·ONI̅(t), ONI̅ = media enero-diciembre del ONI del año del máximo (sensibilidad: año anterior).
    H4a significancia de campo: fracción de estaciones con razón de verosimilitud p < 0,05 > 5 % (IC de bloques por departamento).
    H4b predictiva: en el 30 % cronológico final, mayor log-verosimilitud predictiva que la GEV estacionaria en > 50 % de las estaciones.
H5: GEV con forma ξ fija en la mediana regional (calculada con el 70 % de calibración de las OTRAS estaciones de la región) frente a ξ libre.
    Mejora si la mediana de (loglik pred. ξ fijo − ξ libre) >= −0,5 y la mediana de (ancho IC Q50 ξ fijo / ancho ξ libre) < 1.
Estaciones: las mismas del §21 (>= 30 años con valor > 0, último año >= 2000). IC de Q50 con bootstrap paramétrico de 100 réplicas.
Uso: python hipotesis_h4_h5_crecientes.py [n_estaciones_prueba]
"""
from __future__ import annotations

import json
import math
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy import stats
from scipy.optimize import minimize

warnings.filterwarnings("ignore")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "macro"))
import frecuencia_crecientes_ideam as F  # noqa: E402  (leer, seleccionar, cargar_estaciones, ajustar_gev, inicio_lmom)
import enso_energia as E  # noqa: E402

REGIONES = {"Caribe": "08 13 20 23 44 47 70", "Andina": "05 11 15 17 25 41 54 63 66 68 73", "Pacifica": "19 27 52 76",
            "Orinoquia": "50 81 85 99", "Amazonia": "18 86 91 94 95 97"}
NOMBRE_A_REGION = {"ANTIOQUIA": "Andina", "BOYACA": "Andina", "CUNDINAMARCA": "Andina", "SANTANDER": "Andina", "NORTE DE SANTANDER": "Andina",
                   "TOLIMA": "Andina", "HUILA": "Andina", "CALDAS": "Andina", "QUINDIO": "Andina", "RISARALDA": "Andina", "BOGOTA D.C.": "Andina",
                   "BOGOTA": "Andina", "ATLANTICO": "Caribe", "BOLIVAR": "Caribe", "CESAR": "Caribe", "CORDOBA": "Caribe", "LA GUAJIRA": "Caribe",
                   "MAGDALENA": "Caribe", "SUCRE": "Caribe", "CAUCA": "Pacifica", "CHOCO": "Pacifica", "NARINO": "Pacifica", "VALLE DEL CAUCA": "Pacifica",
                   "META": "Orinoquia", "ARAUCA": "Orinoquia", "CASANARE": "Orinoquia", "VICHADA": "Orinoquia", "CAQUETA": "Amazonia",
                   "PUTUMAYO": "Amazonia", "AMAZONAS": "Amazonia", "GUAINIA": "Amazonia", "GUAVIARE": "Amazonia", "VAUPES": "Amazonia"}
N_BOOT_IC = 100
RNG = np.random.default_rng(20261107)


def oni_anual() -> dict[int, float]:
    s = E.oni()
    return {int(a): float(g.mean()) for a, g in s.groupby(s.index.year) if len(g) >= 10}


ONI_ANUAL = oni_anual()   # a nivel de módulo: los procesos hijos (Windows, 'spawn') lo recalculan al importar


def nll(theta, x, o):
    c, mu0, mu1, lsc = theta
    return -stats.genextreme.logpdf(x, c, loc=mu0 + mu1 * o, scale=math.exp(lsc)).sum()


def ajustar_h4(x, o, inicio):
    c0, loc0, sc0 = inicio
    r = minimize(nll, [c0, loc0, 0.0, math.log(max(sc0, 1e-9))], args=(x, o), method="Nelder-Mead", options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-8})
    return r.x, -r.fun


def ll_h4(theta, x, o):
    c, mu0, mu1, lsc = theta
    return float(stats.genextreme.logpdf(x, c, loc=mu0 + mu1 * o, scale=math.exp(lsc)).sum())


def procesar(args):
    f, xi_regional = args
    global RNG
    RNG = np.random.default_rng(int(f["codigo"]) % (2 ** 31))
    anios = np.array(f["anios"]); x = f["x"]
    if not all(int(a) in ONI_ANUAL for a in anios):
        ok = np.array([int(a) in ONI_ANUAL for a in anios]); anios, x = anios[ok], x[ok]
    if len(x) < 30:
        return None
    o = np.array([ONI_ANUAL[int(a)] for a in anios]); n = len(x); k = int(round(0.7 * n))
    # --- H4
    p0 = F.ajustar_gev(x)
    th1, ll1 = ajustar_h4(x, o, p0)
    ll0 = float(stats.genextreme.logpdf(x, *p0).sum())
    lr = 2 * (ll1 - ll0); p_lr = float(stats.chi2.sf(max(lr, 0.0), 1))
    p0_tr = F.ajustar_gev(x[:k]); th_tr, _ = ajustar_h4(x[:k], o[:k], p0_tr)
    pred0 = float(stats.genextreme.logpdf(x[k:], *p0_tr).sum()); pred1 = ll_h4(th_tr, x[k:], o[k:])
    # --- H5
    libre_tr = F.ajustar_gev(x[:k])
    fijo_tr = stats.genextreme.fit(x[:k], f0=xi_regional, loc=libre_tr[1], scale=libre_tr[2]) if xi_regional is not None else None
    res5 = None
    if fijo_tr is not None:
        pl = float(stats.genextreme.logpdf(x[k:], *libre_tr).sum()); pf = float(stats.genextreme.logpdf(x[k:], *fijo_tr).sum())
        def ancho(p, fija):
            v = []
            for _ in range(N_BOOT_IC):
                s = stats.genextreme.rvs(*p, size=k, random_state=int(RNG.integers(1 << 31)))
                try:
                    q = F.ajustar_gev(s) if not fija else stats.genextreme.fit(s, f0=xi_regional, loc=p[1], scale=p[2])
                    v.append(float(stats.genextreme.ppf(1 - 1 / 50, *q)))
                except Exception:
                    pass
            return np.subtract(*np.percentile(v, [97.5, 2.5])) if len(v) > 30 else np.nan
        wl, wf = ancho(libre_tr, False), ancho(fijo_tr, True)
        res5 = {"dll": pf - pl, "razon_ancho": float(wf / wl) if wl and np.isfinite(wl) and np.isfinite(wf) else None}
    return {"codigo": f["codigo"], "depto": f["depto"], "n": int(n), "mu1": float(th1[2]), "p_lr": p_lr, "dll_pred_h4": pred1 - pred0, "h5": res5}


def bloques(res, estad, N=2000):
    dep = np.array([r["depto"] for r in res]); u = np.unique(dep); out = []
    for _ in range(N):
        ix = np.concatenate([np.where(dep == d)[0] for d in RNG.choice(u, len(u), replace=True)])
        out.append(estad(ix))
    return np.percentile(out, [2.5, 97.5]), np.array(out)


def p_contra(muestras, nulo, N=2000):
    """p bootstrap bilateral de H0: estadístico = nulo, a partir de la distribución de bloques."""
    return float(min(1.0, 2 * min((np.sum(muestras <= nulo) + 1) / (N + 1), (np.sum(muestras >= nulo) + 1) / (N + 1))))


def main() -> None:
    filas = F.seleccionar(F.cargar_estaciones())
    if len(sys.argv) > 1:
        filas = filas[:int(sys.argv[1])]
    region_de = lambda d: NOMBRE_A_REGION.get(d, "Andina")
    # ξ regional con el 70 % de calibración de las demás estaciones de la región (convención scipy: c = -ξ_hosking... se usa c de scipy tal cual)
    c_estacion = {}
    for f in filas:
        k = int(round(0.7 * len(f["x"])))
        try:
            c_estacion[f["codigo"]] = F.ajustar_gev(f["x"][:k])[0]
        except Exception:
            pass
    tareas = []
    for f in filas:
        r = region_de(f["depto"])
        otros = [c_estacion[g["codigo"]] for g in filas if g["codigo"] != f["codigo"] and region_de(g["depto"]) == r and g["codigo"] in c_estacion]
        tareas.append((f, float(np.median(otros)) if len(otros) >= 5 else None))
    with ProcessPoolExecutor(3) as ex:
        res = [r for r in ex.map(procesar, tareas, chunksize=2) if r]
    print(f"Estaciones analizadas: {len(res)}")
    sig = np.array([r["p_lr"] < 0.05 for r in res], float)
    (lo, hi), m4a = bloques(res, lambda ix: sig[ix].mean())
    print(f"H4a fracción con RV p<0,05 = {sig.mean():.3f} IC95% bloques [{lo:.3f}, {hi:.3f}] (azar 0,05) -> {'cumple' if lo > 0.05 else 'NO cumple'}")
    gana = np.array([r["dll_pred_h4"] > 0 for r in res], float)
    (lo2, hi2), m4b = bloques(res, lambda ix: gana[ix].mean())
    print(f"H4b candidata gana en predicción reservada en {gana.mean():.3f} IC95% [{lo2:.3f}, {hi2:.3f}] -> {'cumple' if lo2 > 0.5 else 'NO cumple'}")
    mu1 = np.array([r["mu1"] for r in res]); print(f"   mu1 mediano {np.median(mu1):+.2f} m3/s por °C de ONI; mu1 < 0 en {(mu1 < 0).mean():.1%} de las estaciones")
    # FDR Benjamini-Hochberg (q = 0,10) sobre el listado por estación
    p = np.array([r["p_lr"] for r in res]); orden = np.argsort(p); m = len(p)
    umbral = max([(i + 1) / m * 0.10 for i, j in enumerate(orden) if p[j] <= (i + 1) / m * 0.10], default=0)
    print(f"   estaciones que sobreviven FDR (q=0,10): {int((p <= umbral).sum()) if umbral else 0} de {m}")
    h5 = [r for r in res if r["h5"] and r["h5"]["razon_ancho"] is not None]
    if h5:
        dll = np.array([r["h5"]["dll"] for r in h5]); rz = np.array([r["h5"]["razon_ancho"] for r in h5])
        ok = np.median(dll) >= -0.5 and np.median(rz) < 1
        print(f"H5 ({len(h5)} estaciones): mediana Δloglik pred. = {np.median(dll):+.2f}; mediana razón de ancho IC(Q50) = {np.median(rz):.2f} -> {'mejora' if ok else 'NO mejora'}")
    resumen = {"H4a": {"estadistico": float(sig.mean()), "ic": [float(lo), float(hi)], "p": p_contra(m4a, 0.05)},
               "H4b": {"estadistico": float(gana.mean()), "ic": [float(lo2), float(hi2)], "p": p_contra(m4b, 0.5)}}
    with open(os.path.join(AQUI, "hipotesis_h4_h5.json"), "w", encoding="utf-8") as fh:
        json.dump({"resumen": resumen, "estaciones": res}, fh, ensure_ascii=False)


if __name__ == "__main__":
    main()
