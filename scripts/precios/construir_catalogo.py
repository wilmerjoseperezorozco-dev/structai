"""Catálogo de precios unitarios por elemento estructural, con procedencia y dispersión, desde las tablas INVIAS APU 2026-1 ya descargadas.

Entrada: data/precios_elementos/_cache/*.csv (ver descargar_invias.py).
Salida:  data/precios_elementos/catalogo_precios_2026-1.csv y .json

Por cada ítem canónico se reporta: precio en la provincia de referencia (Atlántico Norte, 0802), mediana nacional, cuartiles y n de provincias.
Los ítems son costo DIRECTO (sin AIU). La dispersión entre provincias es la incertidumbre de localización; no incluye la de especificación ni la de fecha.
Uso:  python scripts/precios/construir_catalogo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
CACHE = RAIZ / "data" / "precios_elementos" / "_cache"
SALIDA = RAIZ / "data" / "precios_elementos"
PROV_REF = "0802"

# (elemento, ítem canónico, numeral INVIAS, nota)
ACTIVIDADES = [
    ("anclaje", "anclaje activo postensado en roca (por m perforado)", "623,1", "incluye torón, perforación, lechada y cabeza; en suelo el rendimiento es otro"),
    ("anclaje", "prueba de carga de anclaje", "623,2", ""),
    ("acero", "acero de refuerzo", "640,1", "suministro, corte, figurado y colocación"),
    ("acero", "malla de refuerzo", "640,2", ""),
    ("acero", "acero de preesfuerzo instalado", "641,2", "por kg"),
    ("pilote", "pilote prefabricado de concreto (variante 1)", "620,1,1", "sección en descripción incompleta"),
    ("pilote", "pilote prefabricado de concreto (variante 2)", "620,1,2", ""),
    ("pilote", "pilote vaciado in situ (variante 1)", "621,1,1", "diámetro en descripción incompleta"),
    ("pilote", "pilote vaciado in situ (variante 2)", "621,1,2", ""),
    ("pilote", "base acampanada", "621,2", ""),
    ("pilote", "camisa permanente de concreto", "621,5,1", ""),
    ("pilote", "descabece de pilotes", "621,8", ""),
    ("pilote", "prueba de integridad (baja deformación)", "621,7,1", ""),
    ("tablestaca", "tablestacado de madera", "622,1", "por m2 de pantalla"),
    ("tablestaca", "tablestacado metálico", "622,2", ""),
    ("tablestaca", "tablestacado de concreto reforzado", "622,3", ""),
    ("tablestaca", "tablestacado de concreto preesforzado", "622,4", ""),
    ("concreto", "concreto estructural premezclado (630,1,1)", "630,1,1", "tipo en descripción incompleta"),
    ("concreto", "concreto premezclado (630,1,2)", "630,1,2", ""),
    ("concreto", "concreto preparado en obra (630,1,3,1)", "630,1,3,1", ""),
    ("prefabricado", "elemento prefabricado de concreto (633,1,1)", "633,1,1", "por m"),
    ("gavion", "gavión / colchogavión estilo 1", "681,1", ""),
    ("gavion", "gavión / colchogavión estilo 2", "681,2", ""),
]

# (elemento, ítem, código de insumo)
INSUMOS = [
    ("acero", "acero corrugado grado 60 (suministro)", "B0020003"),
    ("acero", "varilla corrugada No. 8", "B0015367"),
    ("acero", "malla electrosoldada ASTM A1064", "B0033281"),
    ("acero", "platina galvanizada A653", "B0033287"),
    ("anclaje", "torón de tensionamiento", "B0015150"),
    ("anclaje", "cabezal de tensionamiento (12 torones)", "B0033264"),
    ("anclaje", "varilla 5/8 como anclaje al suelo", "B0015361"),
    ("concreto", "concreto 14 MPa", "B0123660"),
    ("concreto", "concreto 21 MPa", "B0123650"),
    ("concreto", "concreto 28 MPa", "B0123620"),
    ("concreto", "concreto 35 MPa", "B0123630"),
    ("cemento", "cemento uso general (kg)", "B0103569"),
    ("formaleta", "formaleta de madera para concreto (m2)", "B021000"),
    ("formaleta", "formaleta para muros (m2)", "B021005"),
    ("pilote", "pilote prefabricado 0,40 m (m)", "B0014735"),
    ("tablestaca", "tablestaca metálica riel grado 36 (u)", "B0015080"),
    ("soldadura", "soldadura 6013 (kg)", "B0015000"),
    ("soldadura", "soldadura 7018 (kg)", "B0015010"),
    ("pintura", "pintura anticorrosiva (gl)", "B0014760"),
    ("geosintetico", "geomalla biaxial 20 kN/m (m2)", "B0014112"),
    ("geosintetico", "geotextil tejido (m2)", "B025011"),
]


def _estadisticas(serie: pd.Series, ref: float | None) -> dict:
    s = serie.dropna()
    q1, med, q3 = (float(s.quantile(q)) for q in (0.25, 0.5, 0.75))
    return {"n_provincias": int(s.size), "ref_0802": None if ref is None else float(ref), "mediana_nacional": med, "q1": q1, "q3": q3,
            "min": float(s.min()), "max": float(s.max()), "rango_intercuartil_rel": (q3 - q1) / med if med else None}


def construir() -> pd.DataFrame:
    act = pd.read_csv(CACHE / "invias_actividad_costos.csv")
    ins = pd.read_csv(CACHE / "invias_insumos_precios.csv")
    meta_a = pd.read_csv(CACHE / "invias_actividades.csv").set_index("numeral")
    meta_i = pd.read_csv(CACHE / "invias_insumos.csv").set_index("codigo")
    act["provincia_codigo"] = act["provincia_codigo"].astype(str).str.zfill(4)
    ins["provincia_codigo"] = ins["provincia_codigo"].astype(str).str.zfill(4)
    filas = []
    for elem, item, num, nota in ACTIVIDADES:
        d = act[act["numeral"] == num].set_index("provincia_codigo")
        if d.empty:
            continue
        ref = d["costo_directo_total"].get(PROV_REF)
        filas.append({"elemento": elem, "item": item, "fuente": "INVIAS APU 2026-1", "codigo": num, "tipo": "actividad", "unidad": meta_a.loc[num, "unidad"],
                      **_estadisticas(d["costo_directo_total"], ref), "nota": nota})
    for elem, item, cod in INSUMOS:
        d = ins[ins["insumo_codigo"] == cod].set_index("provincia_codigo")
        if d.empty:
            continue
        ref = d["precio"].get(PROV_REF)
        filas.append({"elemento": elem, "item": item, "fuente": "INVIAS insumos 2026-1", "codigo": cod, "tipo": "insumo", "unidad": meta_i.loc[cod, "unidad"],
                      **_estadisticas(d["precio"], ref), "nota": ""})
    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = construir()
    SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA / "catalogo_precios_2026-1.csv", index=False, encoding="utf-8")
    (SALIDA / "catalogo_precios_2026-1.json").write_text(json.dumps(df.to_dict("records"), indent=2, ensure_ascii=False), encoding="utf-8")
    pd.set_option("display.width", 220, "display.max_colwidth", 55)
    print(df[["elemento", "item", "unidad", "ref_0802", "mediana_nacional", "rango_intercuartil_rel", "n_provincias"]].round(3).to_string())
