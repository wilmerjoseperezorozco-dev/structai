"""Hipotesis 1: clima y retrasos de obra (SECOP II + CHIRPS) en el Caribe (issue #95/#98).
Diseno en scripts/satelite/PROTOCOLO_ANALISIS.md seccion 12, fijado antes de correr.
Solo columnas no personales; no se nombran entidades ni contratistas en la salida.
"""
from __future__ import annotations

import io
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "packages" / "construdata"))
import divipola  # noqa: E402

CACHE = AQUI / "_cache"
AMBITO = sys.argv[1] if len(sys.argv) > 1 else "colombia"      # "caribe" (piloto) o "colombia" (enmienda 12b)
MODO = sys.argv[2] if len(sys.argv) > 2 else "alcaldias"      # "alcaldias" (12/12b) o "ubicacion" (12c)
CHIRPS = RAIZ / "scripts" / "satelite" / f"chirps_mensual_{AMBITO}.json"
DEPTOS = {"Atlántico": "08", "Magdalena": "47", "Bolívar": "13", "Córdoba": "23", "Sucre": "70", "Cesar": "20", "La Guajira": "44"}
EXCLUIR_ESTADO = {"En ejecución", "Aprobado", "En aprobación", "enviado Proveedor"}
N_BOOT = 1000
RNG = np.random.default_rng(20261106)


def jl(f):
    return [json.loads(x) for x in (CACHE / f).read_text(encoding="utf-8").splitlines() if x.strip()]


def fecha(x):
    s = str(x or "")
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def dias(d):
    m = re.match(r"(\d+)\s*(Dia|Mes)", str(d or ""))
    return int(m.group(1)) * (30 if m.group(2) == "Mes" else 1) if m else None


def meses_ventana(a: date, dur: int) -> list[str]:
    fin = date.fromordinal(a.toordinal() + dur)
    out, y, m = [], a.year, a.month
    while (y, m) <= (fin.year, fin.month):
        out.append(f"{y}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def ajustar(X, y):
    return LogisticRegression(C=np.inf, max_iter=2000).fit(X, y).coef_[0][0]     # C=inf = sin penalizacion


def razon_momios(X, y, cl, B=N_BOOT):
    b0 = ajustar(X, y)
    ids = np.unique(cl)
    bs = []
    for _ in range(B):
        idx = np.concatenate([np.where(cl == c)[0] for c in RNG.choice(ids, len(ids), replace=True)])
        if y[idx].min() == y[idx].max():
            continue
        try:
            bs.append(ajustar(X[idx], y[idx]))
        except Exception:
            continue
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return math.exp(b0), math.exp(lo), math.exp(hi)


def main() -> None:
    ch = json.loads(CHIRPS.read_text(encoding="utf-8"))
    meses = ch["meses"]
    idx = {m: i for i, m in enumerate(meses)}
    P = {c: np.array(v["precip_mm"], float) for c, v in ch["municipios"].items()}
    # anomalia respecto del mismo mes calendario y z estacional
    anom, zraw = {}, {}
    mes_cal = np.array([int(m[5:]) for m in meses])
    for c, p in P.items():
        a = p.copy()
        for k in range(1, 13):
            a[mes_cal == k] -= p[mes_cal == k].mean()
        anom[c] = a / a.std(ddof=1)
        zraw[c] = (p - p.mean()) / p.std(ddof=1)

    cs = jl("contratos_obra.jsonl")
    susp = defaultdict(int)
    for a in jl("adiciones.jsonl"):
        if a.get("tipo") == "Suspensión":
            susp[a["id_contrato"]] += 1

    # Modo "ubicacion" (enmienda 12c): usa la ubicacion de EJECUCION del contrato (gra4-pcp2) para todas
    # las entidades, solo si el contrato tiene exactamente UN municipio de ejecucion.
    ubic = {}
    if MODO == "ubicacion":
        tmp = defaultdict(set)
        for r in jl("ubicaciones.jsonl"):
            partes = [p.strip() for p in str(r.get("localizaci_n", "")).split(";")]
            if len(partes) >= 3 and partes[1] and partes[2]:
                tmp[r["id_contrato"]].add((partes[1], partes[2]))
        ubic = {k: next(iter(v)) for k, v in tmp.items() if len(v) == 1}
        print(f"Contratos con un unico municipio de ejecucion: {len(ubic)} de {len(cs)}")

    filas, descartes = [], Counter()
    for x in cs:
        if MODO == "ubicacion":
            if x.get("id_contrato") not in ubic:
                descartes["sin municipio de ejecucion unico"] += 1
                continue
            d, ciudad = ubic[x["id_contrato"]]
        else:
            d, ciudad = x.get("departamento"), x.get("ciudad")
            if not d or d == "No Definido" or (AMBITO == "caribe" and d not in DEPTOS):
                continue
            if not str(x.get("nombre_entidad", "")).upper().startswith("ALCALD"):
                descartes["no es alcaldia"] += 1
                continue
        if x.get("estado_contrato") in EXCLUIR_ESTADO:
            descartes["estado sin resultado"] += 1
            continue
        a, dur = fecha(x.get("fecha_de_inicio_del_contrato")), dias(x.get("duraci_n_del_contrato"))
        v = float(x.get("valor_del_contrato") or 0)
        if a is None or dur is None or dur <= 0 or not (0 < v < 1e13):
            descartes["fecha/duracion/valor invalidos"] += 1
            continue
        if not (date(2020, 1, 1) <= a <= date(2024, 12, 31)):
            descartes["inicio fuera de 2020-2024"] += 1
            continue
        mv = meses_ventana(a, dur)
        if mv[-1] > "2024-12":
            descartes["ventana fuera de 2024-12"] += 1
            continue
        r = divipola.resolver_municipio(str(ciudad or ""), d)
        cod = (r or {}).get("codigo_municipio")
        if not cod or cod not in anom:
            descartes["municipio no resuelto"] += 1
            continue
        ii = [idx[m] for m in mv if m in idx]
        filas.append({"cod": cod, "depto": d, "anio": a.year, "valor": v, "dur": dur,
                      "prorroga": float(x.get("dias_adicionados") or 0) > 0, "susp": susp[x["id_contrato"]] > 0,
                      "x_anom": float(anom[cod][ii].mean()), "x_raw": float(zraw[cod][ii].mean()), "x_max": float(zraw[cod][ii].max())})
    n = len(filas)
    print(f"Contratos analizados: {n} en {len(set(f['cod'] for f in filas))} municipios")
    print("Descartes:", dict(descartes))
    y = np.array([f["prorroga"] for f in filas], int)
    ys = np.array([f["susp"] for f in filas], int)
    print(f"Prorrogas: {int(y.sum())} ({100 * y.mean():.1f} %) | suspensiones: {int(ys.sum())} ({100 * ys.mean():.1f} %)")
    cl = np.array([f["cod"] for f in filas])

    def disenio(clave):
        x = np.array([f[clave] for f in filas], float)
        x = (x - x.mean()) / x.std(ddof=1)
        ctrl = [np.log([f["valor"] for f in filas]), np.log([f["dur"] for f in filas])]
        ctrl = [(c - c.mean()) / c.std() for c in ctrl]
        anios = sorted(set(f["anio"] for f in filas))[1:]
        dum = [np.array([f["anio"] == a for f in filas], float) for a in anios]
        dums = sorted(set(f["depto"] for f in filas))[1:]
        dum += [np.array([f["depto"] == d for f in filas], float) for d in dums]
        return np.column_stack([x] + ctrl + dum)

    p = y.mean()
    mde = math.exp(2.8 / math.sqrt(n * p * (1 - p)))
    print(f"\nRazon de momios MINIMA detectable por +1 DE (potencia 80 %, Wald aprox.): {mde:.2f}")
    print(f"\n{'especificacion':<58}{'RM por +1 DE':>14}{'IC95% (municipios)':>24}")
    res = {}
    for nombre, clave, yy in [("PRINCIPAL: anomalia estacional -> prorroga", "x_anom", y),
                              ("anomalia estacional -> suspension", "x_anom", ys),
                              ("sens.: z sin quitar estacionalidad -> prorroga", "x_raw", y),
                              ("sens.: maximo mensual de la ventana -> prorroga", "x_max", y)]:
        rm, lo, hi = razon_momios(disenio(clave), yy, cl)
        res[nombre] = (rm, lo, hi)
        print(f"{nombre:<58}{rm:14.2f}   [{lo:6.2f}, {hi:6.2f}]")

    xa = np.array([f["x_anom"] for f in filas])
    t = np.percentile(xa, [33.3, 66.7])
    print("\nPrevalencia de prorroga por tercil de exposicion (descriptivo):")
    for nom, m in [("menos lluvia que lo normal", xa <= t[0]), ("normal", (xa > t[0]) & (xa <= t[1])), ("mas lluvia que lo normal", xa > t[1])]:
        print(f"  {nom:<30} {100 * y[m].mean():5.1f} % (n={int(m.sum())})")
    rm, lo, hi = res["PRINCIPAL: anomalia estacional -> prorroga"]
    if lo > 1:
        v = "ASOCIACION: la lluvia anomala se asocia con MAS prorrogas (IC excluye 1)"
    elif hi < 1:
        v = "ASOCIACION INVERSA: la lluvia anomala se asocia con MENOS prorrogas (IC excluye 1)"
    else:
        v = f"NO hay evidencia de asociacion (IC incluye 1); con n={n} solo se detectarian RM >= {mde:.2f}"
    print(f"\nVEREDICTO (regla fija): {v}")
    print("LIMITES: muestra pequena; prorrogas con muchas causas; fechas autorreportadas e inconsistentes; CHIRPS ~5 km mensual; "
          "asociacion != causalidad. Solo alcaldias (sitio ~ ciudad).")
    (AQUI / f"clima_retrasos_obras_{AMBITO}{'_ubicacion' if MODO == 'ubicacion' else ''}.json").write_text(json.dumps(
        {"n": n, "prorrogas": int(y.sum()), "mde": mde, "veredicto": v,
         "resultados": {k: {"rm": r[0], "ic": [r[1], r[2]]} for k, r in res.items()}}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
