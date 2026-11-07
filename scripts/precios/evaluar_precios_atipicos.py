"""Evaluación del módulo packages/motor-apu/src/precios_atipicos.py (reglas fijadas antes de correr):

E1 — Emparejamiento: descripción con ruido (se descarta cada palabra con prob. 0,25, minúsculas, sin acentos) -> ¿el ítem correcto es el primero (top-1) o está
     entre los 3 primeros (top-3)? Criterio: top-1 ≥ 0,80.
E2 — Detección con referencia construida con el 80 % de las cotizaciones de cada ítem y prueba con el 20 % restante (separado por proveedor):
     (a) tasa de marca sobre cotizaciones reales sin tocar (incluye errores naturales; NO es una tasa de falsos positivos), criterio ≤ 5 %;
     (b) sensibilidad al inyectar factores ×2, ×3, ×5, ×10 y ×0,1 en cotizaciones de prueba, criterio ≥ 0,90 para ×10 y ×0,1.
IC95 % por bootstrap de ítems.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1] / "packages" / "motor-apu"))
from src.precios_atipicos import PISO_ESCALA, UMBRAL_Z, ReferenciaPrecios, normalizar  # noqa: E402

RNG = np.random.default_rng(20261107)
N_BOOT = 2000


def ic(valores: np.ndarray, grupos: np.ndarray) -> tuple[float, float]:
    u = np.unique(grupos); idx = {g: np.where(grupos == g)[0] for g in u}
    out = [valores[np.concatenate([idx[g] for g in RNG.choice(u, len(u), replace=True)])].mean() for _ in range(N_BOOT)]
    return tuple(np.percentile(out, [2.5, 97.5]))


def main() -> None:
    q = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_precios_nacional_detalle.json").read_text(encoding="utf-8")))
    it = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_items_nacional.json").read_text(encoding="utf-8")))[["item_no", "item_nombre", "unidad"]]
    q["p"] = pd.to_numeric(q.precio_sin_iva, errors="coerce")
    q = q[(q.p > 0) & (q.precio_valido.astype(bool))].merge(it, on="item_no")
    # ---------- E1
    ref_total = ReferenciaPrecios.desde_json()
    nombres = {i["item_no"]: i["nombre"] for i in ref_total.items}
    top1, top3, grupos = [], [], []
    for item_no, nombre in nombres.items():
        toks = nombre.split(); mantener = [w for w in toks if RNG.random() > 0.25] or toks[:2]
        desc = " ".join(mantener).lower()
        r = ref_total.buscar(desc, 3)
        top1.append(r[0][0]["item_no"] == item_no); top3.append(any(x[0]["item_no"] == item_no for x in r)); grupos.append(item_no)
    top1, top3, grupos = np.array(top1, float), np.array(top3, float), np.array(grupos)
    print(f"E1 emparejamiento con ruido (n={len(top1)} ítems): top-1 {top1.mean():.3f} IC95% [{ic(top1, grupos % 50)[0]:.3f}, {ic(top1, grupos % 50)[1]:.3f}] | "
          f"top-3 {top3.mean():.3f} -> criterio top-1 ≥ 0,80: {'CUMPLE' if top1.mean() >= 0.8 else 'NO cumple'}")
    # ---------- E2: referencia con 80 % de proveedores por ítem, prueba con el resto
    provs = q.proveedor_id.unique(); RNG.shuffle(provs); prueba_p = set(provs[: int(0.2 * len(provs))])
    ent = q[~q.proveedor_id.isin(prueba_p)]; prue = q[q.proveedor_id.isin(prueba_p)]
    items = []
    for item_no, g in ent.groupby("item_no"):
        l = np.log(g.p.to_numpy())
        if len(l) < 20:
            continue
        med = float(np.median(l)); mad = float(np.median(np.abs(l - med)) * 1.4826)
        r = it[it.item_no == item_no].iloc[0]
        items.append({"item_no": int(item_no), "nombre": r.item_nombre, "unidad": r.unidad, "n": len(l), "mediana": float(np.exp(med)), "mad_log": mad, "q05": 0, "q95": 0})
    ref = ReferenciaPrecios(items)
    med = {i["item_no"]: i["mediana"] for i in items}; esc = {i["item_no"]: max(i["mad_log"], PISO_ESCALA) for i in items}
    prue = prue[prue.item_no.isin(med)].copy()
    prue["z"] = (np.log(prue.p) - np.log(prue.item_no.map(med))) / prue.item_no.map(esc)
    sin_tocar = (prue.z.abs() > UMBRAL_Z).to_numpy(float); g = prue.item_no.to_numpy()
    lo, hi = ic(sin_tocar, g)
    print(f"\nE2a cotizaciones de prueba reales sin tocar: n={len(prue)}; marcadas {100 * sin_tocar.mean():.2f} % IC95% [{100 * lo:.2f}, {100 * hi:.2f}] "
          f"(incluye errores naturales) -> criterio ≤ 5 %: {'CUMPLE' if sin_tocar.mean() <= 0.05 else 'NO cumple'}")
    res = {}
    base = prue[prue.z.abs() <= UMBRAL_Z]    # se inyecta sobre cotizaciones que NO eran atípicas, para no contar errores naturales como aciertos
    for f in (2, 3, 5, 10, 0.1):
        z = (np.log(base.p * f) - np.log(base.item_no.map(med))) / base.item_no.map(esc)
        det = (z.abs() > UMBRAL_Z).to_numpy(float); lo, hi = ic(det, base.item_no.to_numpy())
        res[f] = (float(det.mean()), float(lo), float(hi))
        print(f"E2b factor ×{f:<4}: sensibilidad {det.mean():.3f} IC95% [{lo:.3f}, {hi:.3f}] (n={len(det)})")
    ok = res[10][0] >= 0.9 and res[0.1][0] >= 0.9
    print(f"Criterio (sensibilidad ≥ 0,90 en ×10 y ×0,1): {'CUMPLE' if ok else 'NO cumple'}")
    (AQUI / "evaluacion_precios_atipicos.json").write_text(json.dumps({"top1": float(top1.mean()), "top3": float(top3.mean()), "marca_sin_tocar": float(sin_tocar.mean()),
                                                                       "sensibilidad": {str(k): v for k, v in res.items()}, "cumple": bool(ok)}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
