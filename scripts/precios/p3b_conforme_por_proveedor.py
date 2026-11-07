"""P3b: umbral conforme para el uso REAL del módulo (el precio revisado viene de un proveedor que el catálogo no conoce).

Se divide a los proveedores en 5 grupos. Para cada grupo, la referencia (mediana y escala contraída por ítem) se construye con los otros cuatro y se puntúan
las cotizaciones del grupo dejado fuera: puntaje = |ln p − ln mediana_ítem| / escala_ítem. Con los puntajes de los cinco grupos se fija el umbral conforme (α = 5 %,
cuantil (1 − α)(1 + 1/n)) y se mide la sensibilidad por inyección (×2, ×3, ×5, ×10, ×0,1) con ese umbral. IC95 % por bootstrap de ítems.
Regla fijada antes de correr: el umbral resultante es el que usa el módulo; criterio de sensibilidad ≥ 0,90 en ×10 y ×0,1 (el mismo de antes).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RNG = np.random.default_rng(20261107)
ALFA, K, CONT, N_BOOT = 0.05, 5, 5, 2000


def referencia(ent: pd.DataFrame) -> pd.DataFrame:
    res_glob = np.concatenate([g.l.to_numpy() - np.median(g.l.to_numpy()) for _, g in ent.groupby("item_no") if len(g) >= 20])
    glob = float(np.median(np.abs(res_glob)) * 1.4826)
    filas = {}
    for item, g in ent.groupby("item_no"):
        if len(g) < 20:
            continue
        l = g.l.to_numpy(); m = float(np.median(l)); mad = float(np.median(np.abs(l - m)) * 1.4826)
        filas[item] = (m, float(np.sqrt((len(l) * mad ** 2 + CONT * glob ** 2) / (len(l) + CONT))))
    return pd.DataFrame(filas, index=["med", "esc"]).T


def main() -> None:
    q = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_precios_nacional_detalle.json").read_text(encoding="utf-8")))
    q["p"] = pd.to_numeric(q.precio_sin_iva, errors="coerce")
    q = q[(q.p > 0) & (q.precio_valido.astype(bool))][["item_no", "proveedor_id", "p"]].reset_index(drop=True); q["l"] = np.log(q.p)
    provs = np.array(sorted(q.proveedor_id.unique())); RNG.shuffle(provs); grupo = {p: i % K for i, p in enumerate(provs)}
    q["g"] = q.proveedor_id.map(grupo)
    pun, items, ref_por_g, test = [], [], {}, {}
    for g in range(K):
        ref = referencia(q[q.g != g]); ref_por_g[g] = ref
        t = q[(q.g == g) & q.item_no.isin(ref.index)].copy()
        t["s"] = np.abs(t.l - t.item_no.map(ref.med)) / t.item_no.map(ref.esc)
        test[g] = t; pun.append(t.s.to_numpy()); items.append(t.item_no.to_numpy())
    pun = np.concatenate(pun); items = np.concatenate(items)
    n = len(pun); umbral = float(np.sort(pun)[int(np.ceil((n + 1) * (1 - ALFA))) - 1])
    print(f"Puntajes de {n} cotizaciones de proveedores dejados fuera (5 grupos). Umbral conforme (α = 5 %): |z| > {umbral:.2f}; tasa de marca {100 * (pun > umbral).mean():.2f} %")
    # tasa de marca por grupo (variabilidad entre grupos de proveedores)
    tasas = [float((test[g].s > umbral).mean()) for g in range(K)]
    print("Tasa de marca por grupo de proveedores: " + ", ".join(f"{100 * x:.1f} %" for x in tasas) + f" (rango {100 * (max(tasas) - min(tasas)):.1f} puntos)")
    res = {}
    for f in (2, 3, 5, 10, 0.1):
        det = []
        for g in range(K):
            t = test[g]; t = t[t.s <= umbral]; ref = ref_por_g[g]
            det.append((np.abs(t.l + np.log(f) - t.item_no.map(ref.med)) / t.item_no.map(ref.esc) > umbral).to_numpy(float));
        d = np.concatenate(det); it = np.concatenate([test[g][test[g].s <= umbral].item_no.to_numpy() for g in range(K)])
        u = np.unique(it); idx = {i: np.where(it == i)[0] for i in u}
        boots = [d[np.concatenate([idx[i] for i in RNG.choice(u, len(u), replace=True)])].mean() for _ in range(N_BOOT)]
        lo, hi = np.percentile(boots, [2.5, 97.5]); res[str(f)] = (float(d.mean()), float(lo), float(hi))
        print(f"  ×{f:<4} sensibilidad {d.mean():.3f} IC95% [{lo:.3f}, {hi:.3f}] (n={len(d)})")
    ok = res["10"][0] >= 0.9 and res["0.1"][0] >= 0.9
    print(f"Criterio (sensibilidad ≥ 0,90 en ×10 y ×0,1): {'CUMPLE' if ok else 'NO cumple'}")
    (AQUI / "p3b_resultados.json").write_text(json.dumps({"umbral": umbral, "marca": float((pun > umbral).mean()), "tasas_por_grupo": tasas, "sensibilidad": res, "cumple": bool(ok)}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
