"""P1 bancos A (curva de crecimiento) y B (anomalías) de PROTOCOLO_VALOR_INFORMATIVO.md. Fracciones 2, 5, 10, 25, 50 y 100 %.
E1 aleatoria, E2 estratificada por departamento (muestreo sistemático sobre la lista ordenada), E3 cobertura espacial (punto más lejano), oráculo.
Uso: python p1_estaciones.py"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FR = (0.02, 0.05, 0.10, 0.25, 0.50, 1.0)
TS = [2, 5, 10, 25, 50, 100]
N_SORTEOS, N_BOOT = 200, 300
DELTA_A, DELTA_B = 0.05, 0.20
RNG = np.random.default_rng(20261108)
norm = lambda s: unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().upper().strip()


def coords() -> pd.DataFrame:
    m = pd.DataFrame(json.loads((RAIZ / "scripts" / "hidro" / "_cache" / "estaciones_meta.json").read_text(encoding="utf-8"))).set_index("codigo")
    m.index = m.index.astype(str)
    return m


def punto_mas_lejano(lat: np.ndarray, lon: np.ndarray, k: int) -> list[int]:
    """Selección determinista por cobertura espacial (farthest-point sampling) en coordenadas planas aproximadas."""
    xy = np.c_[lon * np.cos(np.radians(np.nanmean(lat))), lat]
    sel = [int(np.argmin(((xy - xy.mean(0)) ** 2).sum(1)))]
    d = ((xy - xy[sel[0]]) ** 2).sum(1)
    while len(sel) < k:
        j = int(np.argmax(d)); sel.append(j); d = np.minimum(d, ((xy - xy[j]) ** 2).sum(1))
    return sel


def sistematico(dep: np.ndarray, k: int) -> np.ndarray:
    orden = np.argsort(dep, kind="stable"); n = len(dep); paso = n / k; ini = RNG.random() * paso
    return orden[np.minimum((ini + paso * np.arange(k)).astype(int), n - 1)]


# ---------------------------------------------------------------- banco A
def limpias() -> pd.DataFrame:
    est = json.loads((RAIZ / "scripts" / "satelite" / "frecuencia_crecientes_ideam.json").read_text(encoding="utf-8"))
    filas = []
    for e in est:
        q = e.get("q_gev") or {}
        if (e["n"] >= 30 and e["p_ks"] is not None and e["p_ks"] >= 0.10 and e["mk_p"] is not None and e["mk_p"] >= 0.10 and e["rep"] <= 0.10
                and all(str(t) in q and np.isfinite(q[str(t)]) and q[str(t)] > 0 for t in TS)):
            filas.append({"codigo": str(e["codigo"]), "depto": e["depto"], **{f"x{t}": q[str(t)] / q["2"] for t in TS}})
    return pd.DataFrame(filas)


def banco_a() -> dict:
    d = limpias(); m = coords(); d["lat"] = d.codigo.map(m.latitud.astype(float)); d["lon"] = d.codigo.map(m.longitud.astype(float))
    d = d.dropna(subset=["lat", "lon"]).reset_index(drop=True); n = len(d)
    full = {t: float(np.median(d[f"x{t}"])) for t in (25, 100)}
    X = d[["x25", "x100"]].to_numpy(); dep = d.depto.to_numpy()
    err = lambda idx: np.abs(np.median(X[idx], axis=0) / np.array([full[25], full[100]]) - 1)
    print(f"\n=== Banco A: curva de crecimiento ({n} estaciones limpias con coordenadas; x_25 = {full[25]:.3f}, x_100 = {full[100]:.3f}) ===")
    print("Error relativo absoluto (percentil 95 sobre sorteos para E1/E2; valor único para E3 y oráculo); no inferior si <= 5 % en T=25 y T=100")
    res = {}
    for f in FR:
        k = max(3, int(round(f * n))); fila = {}
        for est in ("E1", "E2"):
            e = []
            for _ in range(N_SORTEOS):
                idx = RNG.choice(n, k, replace=False) if est == "E1" else sistematico(dep, k)
                e.append(err(idx).max())
            fila[est] = float(np.percentile(e, 95))
        fila["E3"] = float(err(np.array(punto_mas_lejano(d.lat.to_numpy(), d.lon.to_numpy(), k))).max())
        sel, rest = [], list(range(n))      # oráculo: voraz que usa la respuesta completa
        for _ in range(k):
            mejor = min(rest, key=lambda j: err(np.array(sel + [j])).max()); sel.append(mejor); rest.remove(mejor)
        fila["oraculo"] = float(err(np.array(sel)).max())
        res[f] = fila
        print(f"   {100 * f:>5.0f} % (k={k:>3}): " + "  ".join(f"{e}: {100 * v:5.1f} %{'*' if v <= DELTA_A else ' '}" for e, v in fila.items()))
    print("   (* = no inferior)")
    return {"n": n, "res": res}


# ---------------------------------------------------------------- banco B
def banco_b() -> dict:
    R = pd.read_csv(RAIZ / "scripts" / "hidro" / "anomalias_por_estacion.csv", index_col=0, dtype={"Unnamed: 0": str}); R.index = R.index.astype(str).str.zfill(10)
    m = coords(); R["dep"] = [norm(m.loc[c, "departamento"]) if c in m.index else "SIN" for c in R.index]
    R["lat"] = [float(m.loc[c, "latitud"]) if c in m.index else np.nan for c in R.index]; R["lon"] = [float(m.loc[c, "longitud"]) if c in m.index else np.nan for c in R.index]
    R = R.dropna(subset=["lat", "lon"]); dif = (R["M2_2.0"] - R["M1_2.0"]).to_numpy(float); dep = R.dep.to_numpy(); n = len(R)
    full = dif.mean()
    def ci_inf(idx):
        g = dep[idx]; u = np.unique(g); ix = {x: np.where(g == x)[0] for x in u}; v = dif[idx]
        b = [v[np.concatenate([ix[x] for x in RNG.choice(u, len(u))])].mean() for _ in range(N_BOOT)]
        return np.percentile(b, 2.5)
    ok = lambda idx: abs(dif[idx].mean() / full - 1) <= DELTA_B and ci_inf(idx) > 0
    print(f"\n=== Banco B: detección de anomalías, conclusión C2 ({n} estaciones; Δ AUC completo = {full:+.4f}) ===")
    print("Proporción de sorteos que conservan la conclusión (estimación dentro de ±20 % y IC95 % por departamento > 0); no inferior si >= 95 %")
    res = {}
    for f in FR:
        k = max(3, int(round(f * n))); fila = {}
        for est in ("E1", "E2"):
            fila[est] = float(np.mean([ok(RNG.choice(n, k, replace=False) if est == "E1" else sistematico(dep, k)) for _ in range(N_SORTEOS)]))
        fila["E3"] = float(ok(np.array(punto_mas_lejano(R.lat.to_numpy(), R.lon.to_numpy(), k))))
        sel, rest = [], list(range(n))
        for _ in range(k):          # oráculo (cota trivial: elige estaciones que igualan la media completa)
            j = min(rest, key=lambda j: abs(dif[sel + [j]].mean() - full)); sel.append(j); rest.remove(j)
        fila["oraculo"] = float(ok(np.array(sel)))
        res[f] = fila
        print(f"   {100 * f:>5.0f} % (k={k:>3}): " + "  ".join(f"{e}: {100 * v:5.1f} %{'*' if v >= 0.95 else ' '}" for e, v in fila.items()))
    print("   (* = no inferior)")
    return {"n": n, "res": res}


def resumen(nombre: str, b: dict, es_a: bool) -> None:
    print(f"\nMenor fracción con no inferioridad, banco {nombre}:")
    for est in ("E1", "E2", "E3", "oraculo"):
        f = next((f for f in FR if (b["res"][f][est] <= DELTA_A if es_a else b["res"][f][est] >= 0.95)), None)
        print(f"   {est}: {('%.0f %% del costo -> ahorro %.0f %%' % (100 * f, 100 * (1 - f))) if f else 'ninguna fracción cumple'}")


if __name__ == "__main__":
    A, B = banco_a(), banco_b()
    resumen("A", A, True); resumen("B", B, False)
    (AQUI / "p1_estaciones_resultados.json").write_text(json.dumps({"A": {"n": A["n"], "res": {str(k): v for k, v in A["res"].items()}}, "B": {"n": B["n"], "res": {str(k): v for k, v in B["res"].items()}}}, indent=1), encoding="utf-8")
