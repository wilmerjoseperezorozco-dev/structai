"""Construye packages/motor-apu/data/composicion_invias_2026_1.json: composición (insumos) de las actividades INVIAS 2026-1 para el recomendador.
Toma la provincia de referencia 0501 (la composición es la misma entre provincias; varían los precios). Solo códigos y descripciones, sin precios.
Requiere _cache/p2_lineas_referencia.json (lo crea p2_recomendador_apu.py). Uso: python construir_composicion_invias.py"""
import json
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "satelite"))
import _datos_caribe as dc  # noqa: E402

SALIDA = AQUI.parents[1] / "packages" / "motor-apu" / "data" / "composicion_invias_2026_1.json"


def bajar(tabla: str, cols: str, orden: str) -> pd.DataFrame:
    sb, filas, ini = dc._sb(), [], 0
    while True:
        p = sb.table(tabla).select(cols).order(orden).range(ini, ini + 999).execute().data or []
        filas += p
        if len(p) < 1000:
            return pd.DataFrame(filas)
        ini += 1000


def main() -> None:
    lineas = pd.DataFrame(json.loads((AQUI / "_cache" / "p2_lineas_referencia.json").read_text(encoding="utf-8")))
    acts = bajar("invias_actividades", "numeral,descripcion,unidad", "numeral")
    ins = bajar("invias_insumos", "codigo,descripcion,unidad,tipo_insumo", "codigo")
    comp = lineas.groupby("numeral").insumo_codigo.apply(lambda s: sorted(set(s))).to_dict()
    a = acts[acts.numeral.isin(comp)]
    out = {"fuente": "INVIAS, análisis de precios unitarios regionalizados, periodo 2026-1; composición de referencia (provincia 0501); sin precios",
           "actividades": [{"numeral": r.numeral, "descripcion": r.descripcion, "unidad": r.unidad, "insumos": comp[r.numeral]} for r in a.itertuples()],
           "insumos": {r.codigo: {"descripcion": r.descripcion, "unidad": r.unidad, "tipo": r.tipo_insumo} for r in ins.itertuples()}}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"{len(out['actividades'])} actividades, {len(out['insumos'])} insumos -> {SALIDA} ({SALIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
