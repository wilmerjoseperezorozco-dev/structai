"""R5 de V1-Perú: controles negativos (PROTOCOLO_V1_PERU.md §6). EXPLORATORIO.

Mismo modelo que R1 con efectos fijos de departamento (`peru_r1_efectos_fijos.py`) y el Spearman parcial dentro de departamento,
pero con otros resultados en lugar de Y1/Y2, todos en viviendas dañadas (destruidas + afectadas) por 100 mil habitantes:
  (a) movimientos en masa: DESLIZAMIENTO, DERRUMBE DE CERRO, ALUD   (control negativo; ojo: dependen del relieve)
  (b) INCENDIO FORESTAL                                              (control negativo)
  (c) INUNDACION + HUAYCO (= Y3 del protocolo)                       (referencia: el peligro que la hipótesis sí vincula con terreno bajo)
Una asociación fuerte en (a) o (b) indicaría sesgo de reporte o de tamaño. Aquí 1.000 réplicas de remuestreo por modelo.

Uso: python -I peru_r5_controles_negativos.py <sinpad.csv> <limites.xlsx> <pob.xlsx> <hand.json> <vias.json> <relieve.json> <salida.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import peru_compuerta_datos as cd  # noqa: E402
import peru_exploratorias_sierra as ex  # noqa: E402
import peru_r1_efectos_fijos as r1  # noqa: E402

N_BOOT = 1000
SEMILLA = 20261108
GRUPOS = {
    "a_movimientos_en_masa": ("DESLIZAMIENTO", "DERRUMBE DE CERRO", "ALUD"),
    "b_incendio_forestal": ("INCENDIO FORESTAL",),
    "c_inundacion_y_huayco_Y3": ("INUNDACION", "HUAYCO"),
}


def viviendas_por_grupo(ruta: str) -> dict[str, pd.DataFrame]:
    s = pd.read_csv(ruta, encoding="latin-1", sep=";", dtype=str)
    s.columns = [c.strip() for c in s.columns]
    s = s.rename(columns={s.columns[2]: "ANO", s.columns[4]: "UBIGEO"})
    s = s[s.ANO.isin(cd.AÑOS)].copy()
    peligro = s[cd.columna(s, "PELIGRO")].str.strip()
    s["viv"] = cd.num(s[cd.columna(s, "VIVIENDAS DESTRUIDAS")]) + cd.num(s[cd.columna(s, "VIVIENDAS AFECTADAS")])
    return {g: s[peligro.isin(hz)].groupby("UBIGEO").agg(viv=("viv", "sum"), registros=("viv", "size")) for g, hz in GRUPOS.items()}


def main(sinpad, limites, poblacion, hand_json, vias_json, relieve_json, salida) -> None:
    r1.N_BOOT = N_BOOT
    rng = np.random.default_rng(SEMILLA)
    base = ex.construir(sinpad, limites, poblacion, hand_json, vias_json, relieve_json)
    grupos = viviendas_por_grupo(sinpad)
    res: dict = {}
    for g, tabla in grupos.items():
        d = base.drop(columns=["viv"]).merge(tabla, left_on="UBIGEO", right_index=True, how="left")
        d[["viv", "registros"]] = d[["viv", "registros"]].fillna(0.0)
        d["Y2"] = d.viv / d.pob * 1e5  # el Spearman parcial de r1 usa la columna Y2 como resultado
        res[g] = {"distritos_con_viviendas_danadas": round(float((d.viv > 0).mean()), 3),
                  "distritos_con_algun_registro": round(float((d.registros > 0).mean()), 3), "ambitos": {}}
        ambitos = {"PERU": d, **{r: d[d.reg == r].reset_index(drop=True) for r in ex.REGIONES_LISTA}}
        for nombre, sub in ambitos.items():
            res[g]["ambitos"][nombre] = {"RR_Poisson_efectos_fijos": r1.modelo(sub, "Y1", rng),
                                         "rho_parcial_dentro_de_departamento": r1.rho_dentro_de_depto(sub, rng)}
            print(g, nombre, json.dumps(res[g]["ambitos"][nombre], ensure_ascii=False), flush=True)
    Path(salida).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 8:
        sys.exit(__doc__)
    main(*sys.argv[1:])
