"""P1 (PROTOCOLO_PRECIOS.md): precios atípicos en las cotizaciones del catálogo IAD MIPYMES. Reglas fijadas antes de correr."""
from __future__ import annotations

import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
RNG = np.random.default_rng(20261107)
MIN_COTIZ, Z_UMBRAL = 20, 3.5


def cargar() -> pd.DataFrame:
    q = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_precios_nacional_detalle.json").read_text(encoding="utf-8")))
    it = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_items_nacional.json").read_text(encoding="utf-8")))[["item_no", "item_nombre", "unidad"]]
    q["p"] = pd.to_numeric(q.precio_sin_iva, errors="coerce")
    q["prov"] = q.proveedor_id.map(lambda s: hashlib.sha1(str(s).encode()).hexdigest()[:6])   # identificador anónimo
    return q.merge(it, on="item_no", how="left")


def z_robusto(x: pd.Series) -> pd.Series:
    l = np.log(x)
    med = l.median(); mad = (l - med).abs().median()
    if mad > 0:
        return (l - med) / (1.4826 * mad)
    ric = l.quantile(0.75) - l.quantile(0.25)
    return (l - med) / (ric / 1.349) if ric > 0 else pd.Series(0.0, index=x.index)


def fuera_de_cercas(x: pd.Series) -> pd.Series:
    l = np.log(x); q1, q3 = l.quantile(0.25), l.quantile(0.75); r = q3 - q1
    return (l < q1 - 3 * r) | (l > q3 + 3 * r)


def efectos_aditivos(df: pd.DataFrame, iteraciones: int = 25) -> tuple[pd.Series, pd.Series, pd.Series]:
    """ln p = a_item + b_prov + e por mínimos cuadrados alternados."""
    l = np.log(df.p.to_numpy()); a = pd.Series(0.0, index=df.item_no.unique()); b = pd.Series(0.0, index=df.prov.unique())
    for _ in range(iteraciones):
        a = pd.Series(l - df.prov.map(b).to_numpy()).groupby(df.item_no.to_numpy()).mean()
        b = pd.Series(l - df.item_no.map(a).to_numpy()).groupby(df.prov.to_numpy()).mean()
    resid = l - df.item_no.map(a).to_numpy() - df.prov.map(b).to_numpy()
    return a, b, pd.Series(resid, index=df.index)


def main() -> None:
    q = cargar()
    total = len(q)
    invalidas = q.p.isna() | (q.p <= 0)
    v = q[~invalidas].copy()
    n_item = v.groupby("item_no").p.transform("size")
    v = v[n_item >= MIN_COTIZ].copy()
    print(f"Cotizaciones: {total}; no válidas (nulas o ≤ 0): {int(invalidas.sum())}; analizables (ítems con ≥ {MIN_COTIZ}): {len(v)}; ítems {v.item_no.nunique()}")
    v["z"] = v.groupby("item_no", group_keys=False).p.apply(z_robusto)
    v["A"] = v.z.abs() > Z_UMBRAL
    v["B"] = v.groupby("item_no", group_keys=False).p.apply(fuera_de_cercas)
    ref = v.groupby("item_no").p.transform("median")
    v["razon"] = v.p / ref
    lg = np.log10(v.razon)
    v["pot10"] = (np.abs(lg - lg.round()) < 0.05) & (lg.round().abs().between(1, 3))
    existente = v.precio_sospechoso.astype(bool)
    print(f"\nDetector A (|z robusto| > {Z_UMBRAL}): {int(v.A.sum())} ({100 * v.A.mean():.1f} %); detector B (cercas extremas): {int(v.B.sum())} ({100 * v.B.mean():.1f} %); "
          f"marca existente precio_sospechoso: {int(existente.sum())} ({100 * existente.mean():.1f} %)")
    both = int((v.A & v.B).sum()); print(f"A y B coinciden en {both} cotizaciones ({100 * both / max(int(v.A.sum()), 1):.0f} % de las de A)")
    tp = int((v.A & existente).sum())
    prec = tp / max(int(v.A.sum()), 1); sens = tp / max(int(existente.sum()), 1)
    po = float(((v.A == existente).mean())); pe = float(v.A.mean() * existente.mean() + (1 - v.A.mean()) * (1 - existente.mean()))
    kappa = (po - pe) / (1 - pe)
    print(f"Concordancia de A con la marca existente: precisión {prec:.2f}, sensibilidad {sens:.2f}, κ de Cohen {kappa:.2f}")
    atip = v[v.A]
    print(f"De las {len(atip)} marcadas por A: cercanas a una potencia de diez (posible error de unidad o decimal) {int(atip.pot10.sum())} ({100 * atip.pot10.mean():.0f} %); "
          f"por encima de la mediana {int((atip.z > 0).sum())}, por debajo {int((atip.z < 0).sum())}")
    # efectos ítem y proveedor
    a, b, e = efectos_aditivos(v)
    l = np.log(v.p.to_numpy())
    tot = np.var(l); var_item = np.var(v.item_no.map(a).to_numpy()); var_prov = np.var(v.prov.map(b).to_numpy()); var_res = np.var(e.to_numpy())
    print(f"\nDescomposición de la varianza de ln(precio): total {tot:.3f}; efecto ítem {100 * var_item / tot:.1f} %; efecto proveedor {100 * var_prov / tot:.1f} %; residuo {100 * var_res / tot:.1f} %")
    med_prov = v.groupby("prov").z.median()
    sesg = med_prov[med_prov.abs() > 1]
    print(f"Proveedores con sesgo sistemático (|mediana de z| > 1): {len(sesg)} de {v.prov.nunique()} (altos {int((sesg > 0).sum())}, bajos {int((sesg < 0).sum())})")
    por_prov = v.groupby("prov").A.mean().sort_values(ascending=False)
    print("Fracción marcada por proveedor (anónimos): p50 {:.1%}, p90 {:.1%}, máx {:.1%}; los 5 mayores: {}".format(
        por_prov.median(), por_prov.quantile(0.9), por_prov.max(), [f"{k}:{x:.0%}" for k, x in por_prov.head(5).items()]))
    por_item = v.groupby("item_no").A.mean()
    print(f"Fracción marcada por ítem: mediana {por_item.median():.1%}; ítems con > 10 % marcado: {int((por_item > 0.10).sum())}")
    # muestra descriptiva: marcadas por A y no por la marca existente
    cand = v[v.A & ~existente]
    muestra = cand.sample(n=min(30, len(cand)), random_state=1)
    print(f"\nMuestra aleatoria de {len(muestra)} cotizaciones marcadas por A y NO por la marca existente (de {len(cand)}):")
    for _, r in muestra.sort_values("razon").iterrows():
        print(f"  {r.item_nombre[:46]:<46} {str(r.unidad):<5} precio {r.p:>14,.0f}  mediana del ítem {r.p / r.razon:>12,.0f}  razón {r.razon:>9.3f}  {'(potencia de 10)' if r.pot10 else ''}")
    out = {"cotizaciones": total, "no_validas": int(invalidas.sum()), "analizables": int(len(v)), "A": int(v.A.sum()), "B": int(v.B.sum()),
           "existente": int(existente.sum()), "precision_A": prec, "sensibilidad_A": sens, "kappa": float(kappa), "pot10_en_A": float(atip.pot10.mean()),
           "var_item": float(var_item / tot), "var_prov": float(var_prov / tot), "var_res": float(var_res / tot), "prov_sesgados": int(len(sesg))}
    (AQUI / "p1_resultados.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    v[v.A][["item_no", "item_nombre", "unidad", "prov", "p", "razon", "z", "pot10"]].to_csv(AQUI / "p1_cotizaciones_atipicas.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
