"""Índices DANE ICOCED (base dic-2021 = 100) para indexar precios entre fechas.

Lee data/precios_elementos/_cache/dane/anex-ICOCED-<mes><año>.xlsx (descarga manual o con --descargar) y escribe
data/precios_elementos/indices_icoced.csv con columnas: dominio, grupo_costos, insumo, periodo (AAAA-MM), indice.
Fuente: https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-costos-de-la-construccion-de-edificaciones-icoced
Ojo: el ICCV (serie anterior) llega a dic-2021 y es otra base; este módulo solo usa el ICOCED desde ene-2022.
Uso:  python scripts/precios/indices_dane.py [--descargar anex-ICOCED-sep2026]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import openpyxl
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parents[2]
CACHE = RAIZ / "data" / "precios_elementos" / "_cache" / "dane"
SALIDA = RAIZ / "data" / "precios_elementos" / "indices_icoced.csv"
SERIES_CLAVE = RAIZ / "data" / "precios_elementos" / "icoced_series_clave.json"
INSUMOS_CLAVE = ("Acero corrugado", "Cemento", "Concreto común", "Concreto bombeable", "Formaleta y accesorios", "Elementos metálicos", "Malla",
                 "Servicios de preliminares y cimentación", "Servicios de estructura y mampostería", "Maestro", "Oficial", "Ayudante")
URL = "https://www.dane.gov.co/files/operaciones/ICOCED/{nombre}.xlsx"
MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
FILA_ANIO, FILA_MES, PRIMERA_FILA = 6, 7, 10          # 1-indexadas, hoja "Anexo 7.2"
ANCHO_BLOQUE = 4                                       # índice, mensual, año corrido, anual


def leer_anexo_7_2(ruta: Path) -> pd.DataFrame:
    ws = openpyxl.load_workbook(ruta, data_only=True, read_only=True)["Anexo 7.2"]
    filas = list(ws.iter_rows(values_only=True))
    anios, meses = filas[FILA_ANIO - 1], filas[FILA_MES - 1]
    # el año encabeza la primera columna de su bloque; los meses siguientes lo heredan
    periodos: dict[int, str] = {}
    anio = None
    for j, m in enumerate(meses):
        if anios[j] is not None and str(anios[j]).strip().isdigit():
            anio = int(str(anios[j]).strip())
        if m is not None and str(m).strip().lower() in MESES and anio is not None:
            periodos[j] = f"{anio}-{MESES[str(m).strip().lower()]:02d}"
    registros = []
    for r in filas[PRIMERA_FILA - 1:]:
        if r[0] is None or not str(r[0]).strip().isdigit():
            continue
        for j, p in periodos.items():
            v = r[j]
            if isinstance(v, (int, float)):
                registros.append((str(r[1]).strip(), str(r[2]).strip(), str(r[3]).strip(), p, float(v)))
    return pd.DataFrame(registros, columns=["dominio", "grupo_costos", "insumo", "periodo", "indice"])


def exportar_series_clave(df: pd.DataFrame) -> None:
    """JSON compacto (dominio -> insumo -> periodo -> índice) que lee `packages/motor-concreto/src/indices_icoced.py`; el CSV completo pesa 6 MB."""
    import json
    sel = df[df["insumo"].isin(INSUMOS_CLAVE)]
    out: dict = {"base": "dic-2021 = 100", "fuente": "DANE ICOCED, anexo 7.2", "series": {}}
    for (dom, ins), g in sel.groupby(["dominio", "insumo"]):
        out["series"].setdefault(dom, {})[ins] = {r.periodo: round(r.indice, 3) for r in g.itertuples()}
    SERIES_CLAVE.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def factor(df: pd.DataFrame, dominio: str, insumo: str, desde: str, hasta: str) -> float:
    """Factor multiplicativo para llevar un precio de `desde` a `hasta` (AAAA-MM) con el índice del insumo en ese dominio."""
    s = df[(df["dominio"] == dominio) & (df["insumo"] == insumo)].set_index("periodo")["indice"]
    return float(s[hasta] / s[desde])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--descargar", help="nombre del anexo, p. ej. anex-ICOCED-sep2026")
    a = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if a.descargar:
        subprocess.run(["curl", "-sL", "-o", str(CACHE / f"{a.descargar}.xlsx"), URL.format(nombre=a.descargar)], check=True)
    ultimo = sorted(CACHE.glob("anex-ICOCED-*.xlsx"), key=lambda p: p.stat().st_mtime)[-1]
    df = leer_anexo_7_2(ultimo)
    df.to_csv(SALIDA, index=False, encoding="utf-8")
    exportar_series_clave(df)
    print(ultimo.name, len(df), "filas;", df["periodo"].min(), "a", df["periodo"].max(), ";", df["dominio"].nunique(), "dominios;", df["insumo"].nunique(), "insumos")
    clave = df[df["dominio"].str.contains("Barranquilla") & df["insumo"].isin(["Acero corrugado", "Concreto premezclado", "Cemento gris", "Cemento", "Concreto"])]
    print(clave.groupby("insumo")["periodo"].agg(["min", "max", "count"]))
