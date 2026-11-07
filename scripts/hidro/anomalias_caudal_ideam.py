"""Evaluación de detectores de anomalía de caudal mensual IDEAM (PROTOCOLO_ANOMALIAS.md, fijado antes de correr)."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[0] / "satelite"))
import _datos_caribe as dc  # noqa: E402  (envuelve stdout)

RNG = np.random.default_rng(20261107)
N_BOOT = 2000
FACTORES = (1.5, 2.0, 3.0)
CORTE = pd.Timestamp("2010-01-01")


def cargar() -> pd.DataFrame:
    f = AQUI / "_cache" / "caudal_historico.pkl"
    f.parent.mkdir(exist_ok=True)
    if f.exists():
        return pd.read_pickle(f)
    sb, filas, ini = dc._sb(), [], 0
    while True:
        p = sb.table("ideam_caudal_historico").select("codigo_estacion,fecha,caudal_m3s").order("id").range(ini, ini + 999).execute().data or []
        filas += p
        if len(p) < 1000:
            break
        ini += 1000
        if ini % 50000 == 0:
            print(f"  descargadas {ini}", flush=True)
    d = pd.DataFrame(filas); d.to_pickle(f); return d


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    r = pd.Series(np.concatenate([pos, neg])).rank().to_numpy()
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def estacion(g: pd.DataFrame):
    """Devuelve los AUC por factor y método para una estación, o None si no cumple las condiciones del protocolo."""
    g = g.dropna().sort_values("fecha")
    g = g[g.q > 0]
    if len(g) < 240:
        return None
    meses_tramo = (g.fecha.max().to_period("M") - g.fecha.min().to_period("M")).n + 1
    if len(g) / meses_tramo < 0.85:
        return None
    ent, pru = g[g.fecha < CORTE], g[g.fecha >= CORTE]
    if len(ent) < 120 or len(pru) < 24:
        return None
    lq = np.log(ent.q.to_numpy()); mes_e = ent.fecha.dt.month.to_numpy()
    med = {m: np.median(lq[mes_e == m]) for m in range(1, 13) if (mes_e == m).sum() >= 8}
    mad = {m: max(1.4826 * np.median(np.abs(lq[mes_e == m] - med[m])), 0.05) for m in med}
    p90 = {m: np.quantile(ent.q.to_numpy()[mes_e == m], 0.90) for m in med}
    if len(med) < 12:
        return None
    zent = np.array([(l - med[m]) / mad[m] for l, m in zip(lq, mes_e)])
    phi = float(np.corrcoef(zent[:-1], zent[1:])[0, 1]) if len(zent) > 30 else 0.0
    pru = pru.copy(); pru["mes"] = pru.fecha.dt.month
    pru["prev"] = pru.q.shift(1); pru["fprev"] = pru.fecha.shift(1)
    pru = pru[(pru.fecha.dt.to_period("M") - pru.fprev.dt.to_period("M")).map(lambda x: getattr(x, "n", 99) == 1)]
    if len(pru) < 24:
        return None
    mes = pru.mes.to_numpy(); q = pru.q.to_numpy(); qprev = pru.prev.to_numpy(); mprev = (pru.mes.to_numpy() - 2) % 12 + 1

    def puntajes(qv: np.ndarray) -> dict[str, np.ndarray]:
        z = np.array([(np.log(a) - med[m]) / mad[m] for a, m in zip(qv, mes)])
        zp = np.array([(np.log(a) - med[m]) / mad[m] for a, m in zip(qprev, mprev)])
        return {"B0": qv / np.array([p90[m] for m in mes]), "M1": z, "M2": z - phi * zp}
    base = puntajes(q)
    out = {"B0_flag_normales": float((base["B0"] > 1).mean())}
    for f in FACTORES:
        inj = puntajes(q * f)
        for k in ("B0", "M1", "M2"):
            out[f"{k}_{f}"] = auc(inj[k], base[k])
        out[f"B0_sens_{f}"] = float((inj["B0"] > 1).mean())
    out["n_prueba"] = int(len(pru)); out["phi"] = phi
    return out


def main() -> None:
    d = cargar()
    d["fecha"] = pd.to_datetime(d.fecha); d["q"] = pd.to_numeric(d.caudal_m3s, errors="coerce")
    print(f"Filas {len(d)}; estaciones {d.codigo_estacion.nunique()}", flush=True)
    res = {}
    for cod, g in d.groupby("codigo_estacion"):
        r = estacion(g[["fecha", "q"]])
        if r:
            res[cod] = r
    R = pd.DataFrame(res).T
    print(f"Estaciones evaluables: {len(R)}; meses de prueba por estación (mediana) {R.n_prueba.median():.0f}; φ mediano {R.phi.median():.2f}")
    print(f"Regla de producción (caudal > P90 del mes): marca {100 * R.B0_flag_normales.mean():.1f} % de los meses normales de prueba")
    for f in FACTORES:
        print(f"\n--- factor ×{f} ---  sensibilidad de la regla de producción tal cual: {100 * R[f'B0_sens_{f}'].mean():.1f} %")
        for k in ("B0", "M1", "M2"):
            v = R[f"{k}_{f}"].to_numpy(float); idx = np.arange(len(v))
            boots = [v[RNG.choice(idx, len(idx))].mean() for _ in range(N_BOOT)]
            print(f"  AUC {k}: {v.mean():.3f} IC95% [{np.percentile(boots, 2.5):.3f}, {np.percentile(boots, 97.5):.3f}]")
    resultados = {}
    print("\nPruebas confirmatorias (f = 2; diferencia de AUC por estación; Holm sobre dos):")
    pares = (("C1 M1−B0", "M1_2.0", "B0_2.0"), ("C2 M2−M1", "M2_2.0", "M1_2.0"))
    ps = []
    for nombre, a, b in pares:
        dif = (R[a] - R[b]).to_numpy(float); idx = np.arange(len(dif))
        boots = np.array([dif[RNG.choice(idx, len(idx))].mean() for _ in range(N_BOOT)])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        p = float(min(1.0, 2 * min((np.sum(boots <= 0) + 1) / (N_BOOT + 1), (np.sum(boots >= 0) + 1) / (N_BOOT + 1))))
        ps.append((nombre, p)); resultados[nombre] = {"dif": float(dif.mean()), "ic": [float(lo), float(hi)], "p": p, "estaciones_que_mejoran": float((dif > 0).mean())}
        print(f"  {nombre}: Δ AUC = {dif.mean():+.4f} IC95% [{lo:+.4f}, {hi:+.4f}] p = {p:.4f}; estaciones que mejoran: {100 * (dif > 0).mean():.0f} %")
    sigue = True
    for i, (n, p) in enumerate(sorted(ps, key=lambda x: x[1])):
        aj = min(1.0, p * (len(ps) - i)); rech = sigue and aj < 0.05; sigue = rech
        resultados[n]["p_holm"] = aj; resultados[n]["significativo"] = bool(rech)
        print(f"  Holm {n}: p ajustado = {aj:.4f} -> {'SIGNIFICATIVO' if rech else 'no significativo'}")
    R.to_csv(AQUI / "anomalias_por_estacion.csv")
    (AQUI / "anomalias_resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
