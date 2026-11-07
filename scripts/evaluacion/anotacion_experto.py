"""M7 del protocolo de métricas sin LLM: preparación de la anotación humana y cálculo del acuerdo entre expertos.

  python scripts/evaluacion/anotacion_experto.py generar            -> anotacion_experto_muestra.csv (60 preguntas estratificadas, semilla fija)
  python scripts/evaluacion/anotacion_experto.py kappa a.csv b.csv  -> κ de Cohen entre dos anotadores (y acuerdo simple) por columna
  python scripts/evaluacion/anotacion_experto.py fleiss a.csv b.csv c.csv ...  -> κ de Fleiss (≥ 3 anotadores)

Columnas a llenar por cada anotador (valores permitidos): rel_ctx1, rel_ctx2, rel_ctx3 (0 = irrelevante, 1 = parcial, 2 = contiene la respuesta),
correccion_respuesta (0 = incorrecta, 1 = parcial, 2 = correcta), cita_correcta (0/1). Las columnas de contexto y respuesta se muestran truncadas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
EVAL = Path(__file__).resolve().parent
COLUMNAS = ["rel_ctx1", "rel_ctx2", "rel_ctx3", "correccion_respuesta", "cita_correcta"]
N_POR_TIPO = {"hecho": 24, "COLOQ": 10, "SINT": 10, "ADV": 8, "COMP": 8}


def generar() -> None:
    filas = [json.loads(l) for l in open(EVAL / "baseline_2026-09-09_278preguntas_muestras.jsonl", encoding="utf-8")]
    df = pd.DataFrame(filas)
    pref = df["id"].str.split("-").str[0].str.rstrip("0123456789")
    df["tipo"] = np.where(pref.isin(N_POR_TIPO), pref, "hecho")
    partes = [g.sample(n=min(N_POR_TIPO[t], len(g)), random_state=20261107) for t, g in df.groupby("tipo")]
    m = pd.concat(partes).sample(frac=1, random_state=1).reset_index(drop=True)
    out = pd.DataFrame({"id": m["id"], "tipo": m["tipo"], "pregunta": m["user_input"], "respuesta": m["response"].str[:900],
                        "contexto1": m["retrieved_contexts"].map(lambda c: c[0][:500] if len(c) > 0 else ""),
                        "contexto2": m["retrieved_contexts"].map(lambda c: c[1][:500] if len(c) > 1 else ""),
                        "contexto3": m["retrieved_contexts"].map(lambda c: c[2][:500] if len(c) > 2 else ""),
                        "referencia": m["reference"].str[:600]})
    for c in COLUMNAS + ["comentario"]:
        out[c] = ""
    out.to_csv(EVAL / "anotacion_experto_muestra.csv", index=False, encoding="utf-8-sig")
    print(f"Generado anotacion_experto_muestra.csv con {len(out)} preguntas: {out.tipo.value_counts().to_dict()}")


def kappa_cohen(a: pd.Series, b: pd.Series) -> tuple[float, float]:
    ok = a.notna() & b.notna()
    a, b = a[ok].astype(int), b[ok].astype(int)
    if len(a) == 0:
        return (np.nan, np.nan)
    cats = sorted(set(a) | set(b))
    po = float((a.values == b.values).mean())
    pe = sum((a == c).mean() * (b == c).mean() for c in cats)
    return ((po - pe) / (1 - pe) if pe < 1 else 1.0, po)


def kappa_fleiss(tabla: np.ndarray) -> float:
    n = tabla.sum(axis=1)[0]
    p_j = tabla.sum(axis=0) / tabla.sum()
    p_i = (np.square(tabla).sum(axis=1) - n) / (n * (n - 1))
    pbar, pe = p_i.mean(), np.square(p_j).sum()
    return (pbar - pe) / (1 - pe) if pe < 1 else 1.0


def interpretar(k: float) -> str:
    return "sin acuerdo" if k < 0 else "leve" if k < 0.21 else "aceptable" if k < 0.41 else "moderado" if k < 0.61 else "sustancial" if k < 0.81 else "casi perfecto"


def main() -> None:
    modo = sys.argv[1] if len(sys.argv) > 1 else "generar"
    if modo == "generar":
        return generar()
    ds = [pd.read_csv(p) for p in sys.argv[2:]]
    if modo == "kappa" and len(ds) == 2:
        for c in COLUMNAS:
            k, po = kappa_cohen(ds[0][c], ds[1][c])
            print(f"{c:<22} κ de Cohen = {k:+.2f} ({interpretar(k)}); acuerdo simple {po:.0%}")
    elif modo == "fleiss" and len(ds) >= 3:
        for c in COLUMNAS:
            m = pd.concat([d[c] for d in ds], axis=1).dropna().astype(int).to_numpy()
            cats = sorted(set(m.flatten()))
            tabla = np.array([[int((fila == k).sum()) for k in cats] for fila in m])
            k = kappa_fleiss(tabla)
            print(f"{c:<22} κ de Fleiss = {k:+.2f} ({interpretar(k)}); n={len(m)}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
