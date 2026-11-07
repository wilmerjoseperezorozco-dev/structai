"""Construye packages/motor-apu/data/referencia_precios_iad.json: estadísticos robustos por ítem del catálogo IAD MIPYMES.
Solo agregados (sin proveedores). Usa las cotizaciones válidas (> 0, marcadas válidas). Uso: python construir_referencia_iad.py"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parents[1] / "packages" / "motor-apu" / "data" / "referencia_precios_iad.json"


def main() -> None:
    q = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_precios_nacional_detalle.json").read_text(encoding="utf-8")))
    it = pd.DataFrame(json.loads((AQUI / "_cache" / "apu_items_nacional.json").read_text(encoding="utf-8")))[["item_no", "item_nombre", "unidad"]]
    q["p"] = pd.to_numeric(q.precio_sin_iva, errors="coerce")
    q = q[(q.p > 0) & (q.precio_valido.astype(bool))]
    # escala global (MAD de los residuos respecto de la mediana de cada ítem) para contraer las escalas de los ítems con pocas cotizaciones
    res_glob = np.concatenate([np.log(g.p.to_numpy()) - np.median(np.log(g.p.to_numpy())) for _, g in q.groupby("item_no") if len(g) >= 20])
    glob = float(np.median(np.abs(res_glob)) * 1.4826)
    filas = []
    for item_no, g in q.groupby("item_no"):
        l = np.log(g.p.to_numpy())
        if len(l) < 20:
            continue
        med = float(np.median(l))
        mad = float(np.median(np.abs(l - med)) * 1.4826)
        n = len(l)
        mad = float(np.sqrt((n * mad ** 2 + 5 * glob ** 2) / (n + 5)))   # escala contraída hacia la global (5 observaciones de peso)
        r = it[it.item_no == item_no].iloc[0]
        filas.append({"item_no": int(item_no), "nombre": r.item_nombre, "unidad": r.unidad, "n": int(len(l)), "mediana": float(np.exp(med)),
                      "mad_log": round(mad, 4), "q05": float(np.exp(np.quantile(l, 0.05))), "q95": float(np.exp(np.quantile(l, 0.95)))})
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps({"fuente": "Catálogo IAD MIPYMES (Colombia Compra Eficiente), cotizaciones sin IVA cargadas el 2026-08-20; "
                                           "estadísticos robustos por ítem; precios de referencia, no de mercado", "items": filas}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(filas)} ítems -> {SALIDA} ({SALIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
