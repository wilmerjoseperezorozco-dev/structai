"""Descubrimiento de reglas del selector de tipología del muro de contención: valores SHAP nativos de LightGBM (pred_contrib, TreeSHAP) y árboles poco profundos.

Las reglas describen el comportamiento del optimizador de referencia SOBRE EL ESPACIO MUESTREADO Y BAJO LAS HIPÓTESIS DEL MOTOR (Rankine/Mononobe-Okabe, fricción tan φ con
dentellón, sombreado de la bandeja): son hallazgos del modelo, no verdades de la mecánica de suelos, y no se publican como tales sin contraste.

Uso:  python scripts/surrogate_muro/reglas.py [--dataset ...] [--modelos ...] [--salida data/surrogate_muro/reglas.md]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from entrenar import ENTRADAS, TIPOS, preparar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]


def _md(d: pd.DataFrame, indice: bool = True) -> str:
    d = d.reset_index() if indice else d
    filas = ["| " + " | ".join(map(str, d.columns)) + " |", "|" + "---|" * len(d.columns)]
    filas += ["| " + " | ".join(str(v) for v in r) + " |" for r in d.itertuples(index=False)]
    return "\n".join(filas)


def importancia_shap(carpeta: Path, df: pd.DataFrame) -> pd.DataFrame:
    """Media de |SHAP| por variable y por clase de tipología (solo casos viables)."""
    b = lgb.Booster(model_file=str(carpeta / "tipo.txt"))
    v = df[df["ganadora"] != "ninguna"]
    contrib = b.predict(v[ENTRADAS], pred_contrib=True).reshape(len(v), len(TIPOS), len(ENTRADAS) + 1)
    return pd.DataFrame(np.abs(contrib[:, :, :-1]).mean(axis=0).T, index=ENTRADAS, columns=TIPOS).sort_values(TIPOS[1], ascending=False)


def mejor_umbral(x: pd.Series, y: pd.Series) -> tuple[float, float, str]:
    """Mejor corte simple x ≤ t / x > t que separa y∈{0,1}: (umbral, exactitud, sentido)."""
    mejor = (np.nan, 0.0, "")
    for t in np.unique(np.quantile(x, np.linspace(0.05, 0.95, 91))):
        for sentido, pred in (("x ≤ t → dentellón mejor", x <= t), ("x > t → dentellón mejor", x > t)):
            acc = float((pred == y).mean())
            if acc > mejor[1]:
                mejor = (float(t), acc, sentido)
    return mejor


def reglas_dentellon(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Compara estándar vs dentellón en los casos donde ambos tienen solución: ¿cuándo gana el dentellón?"""
    p = df[(df["estandar_ok"] == 1) & (df["dentellon_ok"] == 1)].copy()
    p["gana_dentellon"] = (p["dentellon_obj"] < p["estandar_obj"]).astype(int)
    p["ahorro_dentellon"] = 1.0 - p["dentellon_obj"] / p["estandar_obj"]
    arbol = DecisionTreeClassifier(max_depth=3, min_samples_leaf=40, random_state=0).fit(p[ENTRADAS], p["gana_dentellon"])
    filas = [(v, *mejor_umbral(p[v], p["gana_dentellon"])) for v in ("H", "H_tanphi", "phi", "a_max", "q_adm", "beta")]
    umbrales = pd.DataFrame(filas, columns=["variable", "umbral", "exactitud", "sentido"]).sort_values("exactitud", ascending=False)
    txt = (f"Casos con ambas tipologías factibles: {len(p)}. El dentellón gana en {p['gana_dentellon'].mean():.1%}; ahorro mediano cuando gana "
           f"{p.loc[p['gana_dentellon'] == 1, 'ahorro_dentellon'].median():.1%}.\n\nÁrbol (profundidad 3):\n```\n{export_text(arbol, feature_names=ENTRADAS)}\n```")
    return txt, umbrales


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "surrogate_muro" / "dataset_v2.csv"))
    ap.add_argument("--modelos", default=str(RAIZ / "data" / "surrogate_muro" / "modelos_v2"))
    ap.add_argument("--salida", default=str(RAIZ / "data" / "surrogate_muro" / "reglas_v2.md"))
    a = ap.parse_args()
    df = preparar(pd.read_csv(a.dataset))
    df = df[df["error"].isna() | (df["error"] == "")]
    shap = importancia_shap(Path(a.modelos), df)
    txt, umb = reglas_dentellon(df)
    md = ["# Reglas empíricas del selector de tipología (muros en voladizo)", "", "Hallazgos del optimizador de referencia sobre el espacio muestreado; ver hipótesis en el docstring.", "",
          "## Importancia SHAP (media |SHAP| por clase)", "", _md(shap.round(4)), "", "## ¿Cuándo supera el dentellón al ensanche de la zapata?", "", txt, "",
          "### Mejor corte simple por variable", "", _md(umb.round(4), False)]
    Path(a.salida).write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
