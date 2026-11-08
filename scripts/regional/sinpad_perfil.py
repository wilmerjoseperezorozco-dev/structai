"""Perfil de calidad del conjunto SINPAD (INDECI, Perú) para la fase F1 del issue #110.

Uso:  python -I sinpad_perfil.py <BD_2003-2025_EMERGENCIAS.csv> <BD_2026_Semestre_I.csv>
Solo lectura: no escribe nada. Los CSV no se versionan (viven fuera del repo).
Fuente: datosabiertos.gob.pe, «Emergencias y daños a nivel nacional por departamento»
(INDECI, ODC-BY). Los dos archivos tienen nombres de columna distintos y la fecha de 2025
viene en MM/DD/AA (ver el informe).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

MM_PELIGROS = ("DESLIZAMIENTO", "HUAYCO", "DERRUMBE DE CERRO", "ALUD", "EROSION")
DANOS = (
    "FALLECIDOS", "VIVIENDAS DESTRUIDAS", "PUENTE DESTRUIDO", "PUENTE AFECTADO",
    "CARRETERA DESTRUIDA KM", "CARRETERA AFECTADA KM", "CAMINO RURAL DESTRUIDO KM",
)


def leer(ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta, encoding="latin-1", sep=";", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    return df.rename(columns={df.columns[0]: "COD", df.columns[1]: "FECHA", df.columns[2]: "ANO"})


def formato_fecha(serie: pd.Series) -> dict[str, int]:
    largo = serie.str.fullmatch(r"\d\d/\d\d/\d{4}")
    corto = serie.str.fullmatch(r"\d\d/\d\d/\d\d")
    return {"DD/MM/AAAA": int(largo.sum()), "MM/DD/AA": int(corto.sum()),
            "otro": int((~largo & ~corto).sum())}


def main(ruta_a: str, ruta_b: str) -> None:
    a = leer(Path(ruta_a))
    b = pd.read_csv(ruta_b, encoding="latin-1", sep=";", dtype=str)
    print(f"filas 2003-2025: {len(a)}  | columnas: {a.shape[1]}")
    print(f"filas 2026-S1:   {len(b)}  | columnas: {b.shape[1]}")
    print("esquemas distintos entre archivos:", [c.strip() for c in b.columns] != list(a.columns))
    print("filas por año:", a.ANO.value_counts().sort_index().to_dict())
    print("formato de fecha:", formato_fecha(a.FECHA))
    c25 = a[a.ANO == "2025"].FECHA.str.extract(r"(\d\d)/(\d\d)/\d\d").astype(int)
    print("2025: primer campo >12:", int((c25[0] > 12).sum()), "| segundo campo >12:", int((c25[1] > 12).sum()))
    print("códigos de emergencia repetidos:", int(a.COD.duplicated().sum()))
    print("distritos con evento por año:", a.groupby("ANO")["COD. DISTRITO"].nunique().to_dict())
    v = a[a.ANO.isin([str(y) for y in range(2019, 2025)])]
    print(f"2019-2024: {len(v)} filas, {v['COD. DISTRITO'].nunique()} distritos")
    print("peligros:", v.PELIGRO.value_counts().head(12).to_dict())
    mm = v[v.PELIGRO.isin(MM_PELIGROS)]
    print(f"movimientos en masa (peligros {MM_PELIGROS}): {len(mm)} filas, {mm['COD. DISTRITO'].nunique()} distritos")
    for c in DANOS:
        x = pd.to_numeric(v[c].astype(str).str.replace(",", "."), errors="coerce")
        print(f"{c:28s} no nulo {x.notna().mean():.2f}  >0 {(x > 0).mean():.3f}  máx {x.max()}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
