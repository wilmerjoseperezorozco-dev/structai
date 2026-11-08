"""Compuerta de datos de V1-Perú (PROTOCOLO_V1_PERU.md §4). Solo descriptiva: NO calcula ninguna asociación.

Uso: python -I peru_compuerta_datos.py <sinpad.csv> <per_admin_boundaries.xlsx> <inei_pob_proy.xlsx> <hand_peru.json> <vias_hand_peru.json>
Imprime un JSON con los conteos de la compuerta y la evaluación de las cuatro condiciones de «no concluyente».
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

AÑOS = [str(y) for y in range(2019, 2025)]
KM_VIA_MIN = 5.0
CELDAS_MIN = 30
COL_POB_2021 = 5  # tabla INEI: columna 2 = 2018, 5 = 2021 (año central de 2019-2024)
MIN_DISTRITOS = 300
MIN_DEPTOS = 15
MIN_POR_DEPTO = 10
IQR_MIN = 0.05
TASA_MAX, TASA_MIN = 0.90, 0.10


def num(serie: pd.Series) -> pd.Series:
    return pd.to_numeric(serie.astype(str).str.replace(",", ".").str.strip(), errors="coerce").fillna(0.0)


def columna(df: pd.DataFrame, prefijo: str) -> str:
    return next(c for c in df.columns if c.strip().upper().startswith(prefijo))


def cargar_sinpad(ruta: str) -> pd.DataFrame:
    s = pd.read_csv(ruta, encoding="latin-1", sep=";", dtype=str)
    s.columns = [c.strip() for c in s.columns]
    s = s.rename(columns={s.columns[2]: "ANO", s.columns[4]: "UBIGEO"})
    s = s[s.ANO.isin(AÑOS)].copy()
    reg = columna(s, "REGI")
    s["viv"] = num(s[columna(s, "VIVIENDAS DESTRUIDAS")]) + num(s[columna(s, "VIVIENDAS AFECTADAS")])
    s["km_carr"] = num(s[columna(s, "CARRETERA DESTRUIDA")]) + num(s[columna(s, "CARRETERA AFECTADA")])
    g = s.groupby("UBIGEO").agg(viv=("viv", "sum"), km_carr=("km_carr", "sum"),
                                region=(reg, lambda x: x.mode().iat[0] if len(x.mode()) else None))
    return g


def cargar_poblacion(ruta: str) -> pd.Series:
    p = pd.read_excel(ruta, header=None, skiprows=5)
    p[0] = p[0].astype(str).str.strip()
    p = p[p[0].str.fullmatch(r"\d{6}") & ~p[0].str.endswith("00")]
    return pd.to_numeric(p[COL_POB_2021], errors="coerce").set_axis(p[0])


def main(sinpad: str, limites: str, poblacion: str, hand_json: str, vias_json: str) -> None:
    pol = pd.read_excel(limites, sheet_name="per_admin3")
    pol["UBIGEO"] = pol["adm3_pcode"].astype(str).str.replace("PE", "", regex=False).str.zfill(6)
    area = pol.set_index("UBIGEO")["area_sqkm"]
    pob = cargar_poblacion(poblacion)
    sin = cargar_sinpad(sinpad)
    hand = pd.DataFrame(json.load(open(hand_json, encoding="utf-8"))["distritos"])
    hand["UBIGEO"] = hand["adm3_pcode"].str.replace("PE", "", regex=False)
    vias = pd.DataFrame(json.load(open(vias_json, encoding="utf-8"))["distritos"])
    vias["UBIGEO"] = vias["adm3_pcode"].str.replace("PE", "", regex=False)

    d = vias.merge(hand[["UBIGEO", "n_validos_5", "frac_hand_lt10_5"]], on="UBIGEO", how="left")
    d["pob"] = d.UBIGEO.map(pob)
    d["area"] = d.UBIGEO.map(area)
    d = d.merge(sin, left_on="UBIGEO", right_index=True, how="left")
    d["viv"] = d["viv"].fillna(0.0)
    d["km_carr"] = d["km_carr"].fillna(0.0)
    d["E"] = d.km_bajo / d.km_via.where(d.km_via > 0)
    d["tiene_registro"] = d.UBIGEO.isin(sin.index)

    completo = d.pob.notna() & (d.pob > 0) & d.area.notna() & d.frac_hand_lt10_5.notna() & (d.n_validos_5 >= CELDAS_MIN)
    con_via = d.km_via >= KM_VIA_MIN
    inc = d[completo & con_via].copy()
    inc["Y1"] = inc.viv / inc.pob * 1e5
    inc["Y2"] = inc.km_carr / inc.area * 100

    deptos_ok = int((inc.groupby("adm1").size() >= MIN_POR_DEPTO).sum())
    q1, q3 = inc.E.quantile([0.25, 0.75])
    tasa_y1, tasa_y2 = float((inc.Y1 > 0).mean()), float((inc.Y2 > 0).mean())
    por_region = {}
    for r, g in inc.groupby(inc.region.fillna("(sin registro)")):
        por_region[str(r)] = {"distritos": len(g), "E_p25": round(float(g.E.quantile(.25)), 3),
                              "E_mediana": round(float(g.E.median()), 3), "E_p75": round(float(g.E.quantile(.75)), 3)}
    res = {
        "distritos_procesados": len(d), "con_vias_5km": int(con_via.sum()),
        "con_datos_completos": int(completo.sum()), "incluidos": len(inc),
        "poblacion_incluida": int(inc.pob.sum()), "poblacion_total_distritos": int(d.pob.sum()),
        "excluidos_por_regla_5km_o_datos": len(d) - len(inc),
        "poblacion_excluida": int(d.pob.sum() - inc.pob.sum()),
        "incluidos_sin_ningun_registro_sinpad": int((~inc.tiene_registro).sum()),
        "departamentos_con_10_o_mas_incluidos": deptos_ok,
        "E_cuartiles": [round(float(x), 3) for x in inc.E.quantile([.25, .5, .75])],
        "E_IQR": round(float(q3 - q1), 3),
        "tasa_Y1_mayor_0": round(tasa_y1, 3), "tasa_Y2_mayor_0": round(tasa_y2, 3),
        "E_por_region_natural": por_region,
        "condiciones_no_concluyente": {
            "menos_de_300_distritos": len(inc) < MIN_DISTRITOS,
            "menos_de_15_departamentos_con_10": deptos_ok < MIN_DEPTOS,
            "tasa_Y1_fuera_de_10_90": not (TASA_MIN <= tasa_y1 <= TASA_MAX),
            "E_IQR_menor_0_05": (q3 - q1) < IQR_MIN,
        },
    }
    print(json.dumps(res, ensure_ascii=False, indent=1, default=lambda o: int(o) if isinstance(o, (np.integer,)) else float(o)))


if __name__ == "__main__":
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    main(*sys.argv[1:])
