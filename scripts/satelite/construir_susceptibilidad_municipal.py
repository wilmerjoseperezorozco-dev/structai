"""Construye packages/construdata/data/susceptibilidad_municipal.json para el plugin de susceptibilidad del chat.

Para cada municipio: (a) el mapa OFICIAL del SGC de amenaza por movimientos en masa (porcentaje de área por clase) y (b) un índice RELATIVO de StructAI:
promedio de la probabilidad predicha, fuera de muestra (validación cruzada que deja grupos de departamentos fuera), sobre los puntos de fondo del municipio, expresado
como percentil entre municipios. Los puntos de fondo son aleatorios sobre tierra (razón 5:1 con las presencias SIMMA), así que el índice ordena municipios entre sí;
NO es una probabilidad absoluta. Se valida contra el mapa del SGC (correlación de rangos) y por región (AUC). Uso: python construir_susceptibilidad_municipal.py"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "scripts" / "datos"))
import p1_susceptibilidad as S  # noqa: E402  (cargar, oof, TODAS)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SALIDA = RAIZ / "packages" / "construdata" / "data" / "susceptibilidad_municipal.json"
MIN_FONDO = 20
REGIONES = {"08": "Caribe", "13": "Caribe", "20": "Caribe", "23": "Caribe", "44": "Caribe", "47": "Caribe", "70": "Caribe",
            "05": "Andina", "11": "Andina", "15": "Andina", "17": "Andina", "25": "Andina", "41": "Andina", "54": "Andina", "63": "Andina", "66": "Andina", "68": "Andina", "73": "Andina",
            "19": "Pacifica", "27": "Pacifica", "52": "Pacifica", "76": "Pacifica", "50": "Orinoquia", "81": "Orinoquia", "85": "Orinoquia", "99": "Orinoquia",
            "18": "Amazonia", "86": "Amazonia", "91": "Amazonia", "94": "Amazonia", "95": "Amazonia", "97": "Amazonia"}
norm = lambda s: unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower().strip()


def main() -> None:
    d = S.cargar(); d["mun"] = d["mun"].astype(int).astype(str).str.zfill(5)
    p = np.mean([S.oof(d, S.TODAS, r) for r in range(2)], axis=0)        # 2 réplicas de partición, promedio
    d["p"] = p; d["reg"] = d.mun.str[:2].map(REGIONES)
    print(f"Muestras {len(d)}; AUC espacial global del modelo de índice: {roc_auc_score(d.presencia, d.p):.3f}")
    auc_reg = {r: float(roc_auc_score(g.presencia, g.p)) for r, g in d.groupby("reg") if g.presencia.nunique() == 2 and len(g) > 200}
    print("AUC por región (fuera de muestra):", {k: round(v, 3) for k, v in auc_reg.items()})
    fondo = d[d.presencia == 0].groupby("mun").agg(n_fondo=("p", "size"), p_medio=("p", "mean"))
    ev = d[d.presencia == 1].groupby("mun").size().rename("n_eventos")
    t = fondo.join(ev).fillna({"n_eventos": 0})
    elegibles = t[t.n_fondo >= MIN_FONDO].copy(); elegibles["indice_pct"] = elegibles.p_medio.rank(pct=True) * 100
    t["indice_pct"] = elegibles.indice_pct
    sgc = {x["CODIGO_DAN"].zfill(5): x for x in json.loads((AQUI / "sgc_amenaza_mm_municipios.json").read_text(encoding="utf-8"))}
    print("Categorías SGC (media de % por clase):")
    df = pd.DataFrame(sgc).T
    for c in ("SUM_BAJA", "SUM_MEDIA", "SUM_ALTA", "SUM_MUY_AL"):
        df[c] = df[c].astype(float)
    print(df.groupby("CATEGORIA")[["SUM_BAJA", "SUM_MEDIA", "SUM_ALTA", "SUM_MUY_AL"]].mean().round(1).to_string())
    df["alta_pct"] = df.SUM_ALTA + df.SUM_MUY_AL
    comun = elegibles.join(df[["alta_pct"]], how="inner")
    rho_g = spearmanr(comun.indice_pct, comun.alta_pct)[0]
    print(f"\nValidación contra el mapa oficial del SGC (% de área en amenaza alta o muy alta): ρ de Spearman = {rho_g:+.2f} sobre {len(comun)} municipios")
    rho_reg = {}
    for r in sorted(set(REGIONES.values())):
        g = comun[comun.index.str[:2].map(REGIONES) == r]
        if len(g) >= 15:
            rho_reg[r] = {"rho": float(spearmanr(g.indice_pct, g.alta_pct)[0]), "n": int(len(g))}
    print("ρ por región:", {k: (round(v['rho'], 2), v['n']) for k, v in rho_reg.items()})
    mun = {}
    for cod, x in sgc.items():
        fila = t.loc[cod] if cod in t.index else None
        mun[cod] = {"municipio": x["MUNICIPIO"], "departamento": x["DEPARTAMEN"], "categoria_sgc": x["CATEGORIA"],
                    "sgc_pct": {"baja": round(float(x["SUM_BAJA"]), 1), "media": round(float(x["SUM_MEDIA"]), 1), "alta": round(float(x["SUM_ALTA"]), 1), "muy_alta": round(float(x["SUM_MUY_AL"]), 1)},
                    "n_fondo": int(fila.n_fondo) if fila is not None else 0, "n_eventos": int(fila.n_eventos) if fila is not None else 0,
                    "indice_pct": round(float(fila.indice_pct), 0) if fila is not None and not np.isnan(fila.indice_pct) else None}
    SALIDA.write_text(json.dumps({"fuente": "SGC (mapa de amenaza por movimientos en masa) y modelo de StructAI (gradient boosting, validación espacial; scripts/datos/p1_susceptibilidad.py)",
                                  "min_fondo": MIN_FONDO, "auc_region": auc_reg, "rho_sgc_global": float(rho_g), "rho_sgc_region": rho_reg, "municipios": mun}, ensure_ascii=False), encoding="utf-8")
    print(f"\n{SALIDA} ({SALIDA.stat().st_size / 1e3:.0f} KB); municipios con índice: {sum(v['indice_pct'] is not None for v in mun.values())} de {len(mun)}")


if __name__ == "__main__":
    main()
