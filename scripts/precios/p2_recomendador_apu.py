"""P2 (PROTOCOLO_PRECIOS.md): recomendador del insumo que falta (P2a) y auditoría de proporciones por inyección de errores (P2b).
Datos: composición de las actividades INVIAS 2026-1 en una provincia de referencia. Reglas fijadas antes de correr."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "satelite"))
import _datos_caribe as dc  # noqa: E402

RNG = np.random.default_rng(20261107)
N_BOOT, K_VEC, REPETICIONES, N_INYECCIONES, FPR = 2000, 10, 5, 300, 0.05
PROVINCIA_REF = "0501"


def cargar() -> pd.DataFrame:
    f = AQUI / "_cache" / "p2_lineas_referencia.json"
    if f.exists():
        return pd.DataFrame(json.loads(f.read_text(encoding="utf-8")))
    sb = dc._sb()
    # provincia con más actividades distintas
    prov = PROVINCIA_REF   # elegida con SQL: una de las provincias con las 526 actividades
    filas, ini = [], 0
    while True:
        p = (sb.table("invias_actividad_insumos").select("numeral,insumo_codigo,tipo_insumo,cantidad_o_rendimiento,valor_unitario_linea")
             .eq("periodo", "2026-1").eq("provincia_codigo", prov).range(ini, ini + 999).execute().data or [])
        filas += p
        if len(p) < 1000:
            break
        ini += 1000
    d = pd.DataFrame(filas).dropna(subset=["numeral", "insumo_codigo"]); d["provincia_ref"] = prov
    f.parent.mkdir(exist_ok=True); f.write_text(d.to_json(orient="records", force_ascii=False), encoding="utf-8")
    return d


def matriz(d: pd.DataFrame):
    acts = sorted(d.numeral.unique()); ins = sorted(d.insumo_codigo.unique())
    ia = {a: i for i, a in enumerate(acts)}; ii = {x: i for i, x in enumerate(ins)}
    B = np.zeros((len(acts), len(ins))); V = np.zeros_like(B)
    for r in d.itertuples():
        B[ia[r.numeral], ii[r.insumo_codigo]] = 1
        V[ia[r.numeral], ii[r.insumo_codigo]] += max(float(r.valor_unitario_linea or 0), 0.0)
    return acts, ins, B, V


def capitulo(numeral: str) -> str:
    return str(numeral).replace(",", ".").split(".")[0][:3]


def tfidf(B: np.ndarray, excluir: int | None = None) -> np.ndarray:
    mask = np.ones(len(B), bool)
    if excluir is not None:
        mask[excluir] = False
    df = B[mask].sum(0)
    idf = np.log((mask.sum() + 1) / (df + 1)) + 1
    return B * idf


def coseno(v: np.ndarray, M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=1) * np.linalg.norm(v)
    return np.divide(M @ v, n, out=np.zeros(len(M)), where=n > 0)


def puntuaciones(modelo: str, B: np.ndarray, a: int, visible: np.ndarray) -> np.ndarray:
    otros = np.delete(np.arange(len(B)), a)
    Bo = B[otros]
    if modelo == "popularidad":
        return Bo.sum(0)
    if modelo == "coocurrencia":
        n = len(Bo); pj = Bo.sum(0) / n
        co = Bo.T @ Bo / n
        with np.errstate(divide="ignore", invalid="ignore"):
            pmi = np.log(np.divide(co, np.outer(pj, pj), out=np.zeros_like(co), where=np.outer(pj, pj) > 0) + 1e-9)
        pmi[~np.isfinite(pmi)] = 0
        idx = np.where(visible > 0)[0]
        return pmi[idx].sum(0) if len(idx) else np.zeros(B.shape[1])
    W = tfidf(B, excluir=a)[otros]
    idf = np.log((len(otros) + 1) / (Bo.sum(0) + 1)) + 1
    s = coseno(visible * idf, W)
    top = np.argsort(-s)[:K_VEC]
    return (s[top, None] * Bo[top]).sum(0)


def ic_bloques(valores: np.ndarray, bloques: np.ndarray) -> tuple[float, float]:
    u = np.unique(bloques); idx = {b: np.where(bloques == b)[0] for b in u}
    out = [np.mean(valores[np.concatenate([idx[b] for b in RNG.choice(u, len(u), replace=True)])]) for _ in range(N_BOOT)]
    return tuple(np.percentile(out, [2.5, 97.5]))


def p2a(acts, B) -> dict:
    modelos = ("popularidad", "coocurrencia", "vecinos")
    elegibles = [i for i in range(len(acts)) if B[i].sum() >= 4]
    print(f"\n== P2a: {len(elegibles)} actividades con ≥ 4 insumos; {REPETICIONES} repeticiones por actividad ==")
    res = {m: {"h5": [], "h10": [], "rr": []} for m in modelos}; bl = []
    for a in elegibles:
        for _ in range(REPETICIONES):
            presentes = np.where(B[a] > 0)[0]; oculto = RNG.choice(presentes)
            vis = B[a].copy(); vis[oculto] = 0
            for m in modelos:
                s = puntuaciones(m, B, a, vis); s = s.astype(float); s[vis > 0] = -np.inf
                rango = int((s > s[oculto]).sum()) + 1
                res[m]["h5"].append(rango <= 5); res[m]["h10"].append(rango <= 10); res[m]["rr"].append(1 / rango)
            bl.append(capitulo(acts[a]))
    bl = np.array(bl); out = {}
    for m in modelos:
        h5, h10, rr = (np.array(res[m][k], float) for k in ("h5", "h10", "rr"))
        out[m] = {k: [float(v.mean())] + [float(x) for x in ic_bloques(v, bl)] for k, v in (("acierto@5", h5), ("acierto@10", h10), ("MRR", rr))}
        print(f"  {m:<13} acierto@5 {out[m]['acierto@5'][0]:.3f} [{out[m]['acierto@5'][1]:.3f},{out[m]['acierto@5'][2]:.3f}] | acierto@10 {out[m]['acierto@10'][0]:.3f} "
              f"[{out[m]['acierto@10'][1]:.3f},{out[m]['acierto@10'][2]:.3f}] | MRR {out[m]['MRR'][0]:.3f} [{out[m]['MRR'][1]:.3f},{out[m]['MRR'][2]:.3f}]")
    d = np.array(res["vecinos"]["h10"], float) - np.array(res["popularidad"]["h10"], float)
    lo, hi = ic_bloques(d, bl)
    print(f"  Vecinos − popularidad en acierto@10 = {d.mean():+.3f} IC95% [{lo:+.3f}, {hi:+.3f}] -> {'CUMPLE el criterio' if lo > 0 else 'NO cumple'}")
    out["criterio_vecinos_vs_popularidad"] = {"dif": float(d.mean()), "ic": [float(lo), float(hi)], "cumple": bool(lo > 0)}
    return out


def z_linea(B, V, a, j, valor_a) -> float:
    """z robusto del log de la participación de la línea (a, j) frente a la del mismo insumo en las actividades más parecidas."""
    tot = valor_a.sum()
    if tot <= 0 or valor_a[j] <= 0:
        return 0.0
    W = tfidf(B, excluir=a); otros = np.delete(np.arange(len(B)), a)
    s = coseno((B[a] > 0) * W[a], W[otros]); orden = otros[np.argsort(-s)]
    vec = [k for k in orden[:60] if V[k, j] > 0 and V[k].sum() > 0][:K_VEC]
    if len(vec) < 3:
        return 0.0
    sh = np.log(np.array([V[k, j] / V[k].sum() for k in vec]))
    med = np.median(sh); mad = max(1.4826 * np.median(np.abs(sh - med)), 0.25)
    return float((np.log(valor_a[j] / tot) - med) / mad)


def p2b(acts, B, V) -> dict:
    print(f"\n== P2b: inyección de errores en {N_INYECCIONES} actividades (tasa de falsos positivos fijada en {FPR:.0%}) ==")
    elegibles = [i for i in range(len(acts)) if B[i].sum() >= 4 and V[i].sum() > 0]
    # calibración: |z| de líneas sin tocar (muestra de actividades)
    cal = RNG.choice(elegibles, size=min(200, len(elegibles)), replace=False)
    zs = []
    for a in cal:
        for j in np.where(V[a] > 0)[0]:
            z = z_linea(B, V, a, j, V[a])
            if z != 0.0:
                zs.append(abs(z))
    umbral = float(np.quantile(zs, 1 - FPR)); print(f"  líneas evaluables sin tocar: {len(zs)}; umbral |z| = {umbral:.2f} (FPR {FPR:.0%})")
    muestra = RNG.choice(elegibles, size=min(N_INYECCIONES, len(elegibles)), replace=False)
    res = {"x10": [], "x0.1": []}; bl = {"x10": [], "x0.1": []}
    for a in muestra:
        lineas = [j for j in np.where(V[a] > 0)[0] if z_linea(B, V, a, j, V[a]) != 0.0]
        if not lineas:
            continue
        j = RNG.choice(lineas)
        for clave, f in (("x10", 10.0), ("x0.1", 0.1)):
            va = V[a].copy(); va[j] *= f
            res[clave].append(abs(z_linea(B, V, a, j, va)) > umbral); bl[clave].append(capitulo(acts[a]))
    out = {"umbral": umbral, "n_calibracion": len(zs)}
    for clave in res:
        x = np.array(res[clave], float); lo, hi = ic_bloques(x, np.array(bl[clave]))
        out[clave] = {"n": int(len(x)), "sensibilidad": float(x.mean()), "ic": [float(lo), float(hi)]}
        print(f"  cantidad {clave}: sensibilidad {x.mean():.2f} IC95% [{lo:.2f}, {hi:.2f}] (n={len(x)})")
    ok = all(out[c]["sensibilidad"] >= 0.5 and out[c]["ic"][0] > 0.2 for c in ("x10", "x0.1"))
    print(f"  Criterio (sensibilidad ≥ 0,5 en ×10 y ×0,1 con IC inferior > 0,2): {'CUMPLE' if ok else 'NO cumple'}")
    out["cumple"] = bool(ok)
    return out


def main() -> None:
    d = cargar()
    print(f"Provincia de referencia {d.provincia_ref.iloc[0]}: {len(d)} líneas; actividades {d.numeral.nunique()}; insumos {d.insumo_codigo.nunique()}; "
          f"líneas por actividad (mediana) {d.groupby('numeral').size().median():.0f}; ejemplo de numerales {sorted(d.numeral.unique())[:4]}")
    acts, ins, B, V = matriz(d)
    out = {"p2a": p2a(acts, B), "p2b": p2b(acts, B, V)}
    (AQUI / "p2_resultados.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
