"""CONTROL EXPLORATORIO de P2a (no estaba en el protocolo; se agrega tras ver 84 % de acierto@10 y sospechar fuga por variantes).

Las actividades INVIAS vienen en familias de variantes (p. ej. 200,1,1 y 200,1,2 comparten casi todos los insumos). Aquí, al predecir el insumo
oculto de una actividad, se EXCLUYEN de los vecinos, de la popularidad y de la co-ocurrencia todas las actividades de su mismo subcapítulo
(primeros dos componentes del numeral). Mide cuánto acierto sobrevive cuando la actividad no tiene una variante cercana en el catálogo.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p2_recomendador_apu as P  # noqa: E402  (cargar, matriz, capitulo, tfidf, coseno, ic_bloques, constantes)


def subcapitulo(numeral: str) -> str:
    return ",".join(str(numeral).replace(".", ",").split(",")[:2])


def punt(modelo: str, B: np.ndarray, a: int, visible: np.ndarray, otros: np.ndarray) -> np.ndarray:
    Bo = B[otros]
    if modelo == "popularidad":
        return Bo.sum(0)
    if modelo == "coocurrencia":
        n = len(Bo); pj = Bo.sum(0) / n; co = Bo.T @ Bo / n; den = np.outer(pj, pj)
        pmi = np.log(np.divide(co, den, out=np.zeros_like(co), where=den > 0) + 1e-9); pmi[~np.isfinite(pmi)] = 0
        idx = np.where(visible > 0)[0]
        return pmi[idx].sum(0) if len(idx) else np.zeros(B.shape[1])
    df = Bo.sum(0); idf = np.log((len(otros) + 1) / (df + 1)) + 1
    s = P.coseno(visible * idf, Bo * idf)
    top = np.argsort(-s)[:P.K_VEC]
    return (s[top, None] * Bo[top]).sum(0)


def main() -> None:
    d = P.cargar(); acts, ins, B, V = P.matriz(d)
    sub = np.array([subcapitulo(a) for a in acts])
    elegibles = [i for i in range(len(acts)) if B[i].sum() >= 4]
    tamanos = [int((sub == sub[i]).sum()) for i in elegibles]
    print(f"Actividades elegibles {len(elegibles)}; tamaño de la familia (mismo subcapítulo): mediana {int(np.median(tamanos))}, máx. {max(tamanos)}")
    modelos = ("popularidad", "coocurrencia", "vecinos"); res = {m: {"h10": [], "h5": [], "rr": []} for m in modelos}; bl = []
    for a in elegibles:
        otros = np.where(sub != sub[a])[0]
        for _ in range(P.REPETICIONES):
            presentes = np.where(B[a] > 0)[0]; oculto = P.RNG.choice(presentes); vis = B[a].copy(); vis[oculto] = 0
            for m in modelos:
                s = punt(m, B, a, vis, otros).astype(float); s[vis > 0] = -np.inf
                r = int((s > s[oculto]).sum()) + 1
                res[m]["h5"].append(r <= 5); res[m]["h10"].append(r <= 10); res[m]["rr"].append(1 / r)
            bl.append(P.capitulo(acts[a]))
    bl = np.array(bl)
    print("\nCONTROL (sin las actividades de la misma familia):")
    for m in modelos:
        h5, h10, rr = (np.array(res[m][k], float) for k in ("h5", "h10", "rr"))
        print(f"  {m:<13} acierto@5 {h5.mean():.3f} [{P.ic_bloques(h5, bl)[0]:.3f},{P.ic_bloques(h5, bl)[1]:.3f}] | acierto@10 {h10.mean():.3f} "
              f"[{P.ic_bloques(h10, bl)[0]:.3f},{P.ic_bloques(h10, bl)[1]:.3f}] | MRR {rr.mean():.3f}")
    dif = np.array(res["vecinos"]["h10"], float) - np.array(res["popularidad"]["h10"], float); lo, hi = P.ic_bloques(dif, bl)
    print(f"  Vecinos − popularidad (acierto@10) = {dif.mean():+.3f} IC95% [{lo:+.3f}, {hi:+.3f}]")


if __name__ == "__main__":
    main()
