"""
Carga el catalogo real IAD MIPYMES (Instrumento de Agregacion de Demanda,
Colombia Compra Eficiente) con granularidad de PROVEEDOR INDIVIDUAL --
78 proveedores mipyme reales de todo el pais, 1.754 materiales/items,
~110.590 precios reales (sin IVA).

Contexto: apu_precios_referencia ya tenia estos 1.754 items cargados con
region='Nacional', pero solo con la MEDIANA colapsada -- se perdio la
identidad de cada uno de los 78 proveedores. Este script recupera esa
granularidad en tablas nuevas, aditivas (no modifica apu_precios_referencia).

Fuente local (copia canonica del proyecto, gitignored):
    packages/construdata/normativa_raw/apu_nacional/
    catalogo_ferreteria_iad_mipymes_v13.xlsx
(descargado originalmente de colombiacompra.gov.co, catalogo derivado del
IAD MIPYMES de materiales de construccion y ferreteria, cobertura nacional.
Copia original del usuario en Desktop/Elementos varios/, consolidada aqui
el 2026-08-20 junto con el resto de fuentes normativas del proyecto).

Valores <= 0 se guardan pero se marcan precio_valido=false (probable "sin
oferta" o artefacto del catalogo, no un precio real de 0 pesos) -- nunca se
descartan silenciosamente, quedan visibles para auditoria.

Uso: python cargar_iad_mipymes_nacional.py
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

XLSX_PATH = (
    PROJECT_ROOT
    / "packages" / "construdata" / "normativa_raw" / "apu_nacional"
    / "catalogo_ferreteria_iad_mipymes_v13.xlsx"
)

FUENTE = (
    "Catálogo IAD MIPYMES — Instrumento de Agregación de Demanda, "
    "Colombia Compra Eficiente (precios sin IVA, cotización real por "
    "proveedor mipyme, cobertura nacional)"
)


def _parse_precio(v):
    """Convierte el valor crudo de celda (float, int, o string tipo
    '$ 1.879.869') a float. Devuelve None si esta vacio."""
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    s = s.replace("$", "").replace(" ", "")
    # formato colombiano: punto = miles, coma = decimales (poco frecuente aqui)
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def cargar_workbook():
    import openpyxl

    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb["Precios del Catálogo"]
    rows = list(ws.iter_rows(values_only=True))

    proveedores_row = rows[3]
    proveedores = [re.sub(r"\s+", " ", str(v).strip()) for v in proveedores_row if v not in (None, "")]
    assert len(proveedores) == 78, f"esperaba 78 proveedores, encontre {len(proveedores)}"

    items_raw = [r for r in rows[5:] if r[0] is not None and r[1]]
    items = []
    for r in items_raw:
        item_no = r[0]
        nombre = str(r[1]).strip()
        unidad = str(r[2]).strip() if r[2] else None
        precios = r[3 : 3 + len(proveedores)]
        items.append((item_no, nombre, unidad, precios))

    return proveedores, items


def main():
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    proveedores, items = cargar_workbook()
    print(f"Proveedores: {len(proveedores)} | Items: {len(items)}")

    # 1) Proveedores -- upsert por nombre, obtener/generar id estable
    prov_rows = [{"nombre": p, "fuente": FUENTE, "tipo_fuente": "IAD MIPYMES"} for p in proveedores]
    res = sb.table("apu_proveedores_nacional").upsert(
        prov_rows, on_conflict="nombre"
    ).execute()
    # recuperar mapping nombre -> id (el upsert no siempre devuelve todas las filas en todos los clientes)
    id_map = {}
    all_provs = sb.table("apu_proveedores_nacional").select("id,nombre").execute()
    for row in all_provs.data:
        id_map[row["nombre"]] = row["id"]
    print(f"Proveedores en BD: {len(id_map)}")

    # 2) Items -- upsert por item_no (clave estable de este catalogo)
    item_rows = [
        {"item_no": it[0], "item_nombre": it[1], "unidad": it[2], "fuente": FUENTE}
        for it in items
    ]
    sb.table("apu_items_nacional").upsert(item_rows, on_conflict="item_no").execute()
    print(f"Items en BD: {len(item_rows)}")

    # 3) Detalle de precios -- item x proveedor, en lotes
    detalle = []
    for item_no, nombre, unidad, precios in items:
        for prov_nombre, valor_crudo in zip(proveedores, precios):
            precio = _parse_precio(valor_crudo)
            if precio is None:
                continue  # sin oferta de este proveedor para este item -- no se inserta fila vacia
            prov_id = id_map.get(prov_nombre)
            if prov_id is None:
                continue
            detalle.append({
                "item_no": item_no,
                "proveedor_id": prov_id,
                "precio_sin_iva": precio,
                "precio_valido": precio > 0,
                "fuente": FUENTE,
            })

    print(f"Filas de detalle a insertar: {len(detalle)}")
    lote = 2000
    for i in range(0, len(detalle), lote):
        chunk = detalle[i : i + lote]
        sb.table("apu_precios_nacional_detalle").upsert(
            chunk, on_conflict="item_no,proveedor_id"
        ).execute()
        print(f"  ...{min(i + lote, len(detalle))}/{len(detalle)}")

    print("OK: catalogo IAD MIPYMES nacional cargado con granularidad de proveedor.")


if __name__ == "__main__":
    main()
