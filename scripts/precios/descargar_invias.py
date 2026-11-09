"""Descarga a CSV local (cache, no versionado) las tablas INVIAS APU regionalizados 2026-1 de Supabase, con paginación explícita (el límite por defecto es 1.000 filas).
Uso: python scripts/precios/descargar_invias.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / "apps" / "api" / ".env")
CACHE = RAIZ / "data" / "precios_elementos" / "_cache"
PAGINA = 1000
TABLAS = {"invias_actividad_costos": "numeral,provincia_codigo,periodo,costo_equipo,costo_materiales,costo_transporte,costo_mano_obra,costo_directo_total",
          "invias_actividades": "numeral,descripcion,unidad", "invias_provincias": "codigo,codigo_departamento,departamento,provincia,region_natural",
          "invias_insumos": "codigo,descripcion,unidad,tipo_insumo,categoria", "invias_insumos_precios": "insumo_codigo,provincia_codigo,periodo,precio"}


def descargar(cliente, tabla: str, columnas: str) -> pd.DataFrame:
    filas, desde = [], 0
    while True:
        lote = cliente.table(tabla).select(columnas).order(columnas.split(",")[0]).range(desde, desde + PAGINA - 1).execute().data
        filas += lote
        if len(lote) < PAGINA:
            return pd.DataFrame(filas)
        desde += PAGINA


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    CACHE.mkdir(parents=True, exist_ok=True)
    cliente = create_client(os.environ["SUPABASE_URL"], os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_KEY"])
    for tabla, cols in TABLAS.items():
        df = descargar(cliente, tabla, cols)
        df.to_csv(CACHE / f"{tabla}.csv", index=False)
        print(tabla, len(df), flush=True)
