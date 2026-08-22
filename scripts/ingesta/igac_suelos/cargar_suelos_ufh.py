"""
Carga masiva (una sola vez, o cuando el IGAC/UPRA publique una versión
nueva del dataset) del catálogo nacional de Unidades Físicas Homogéneas
(UFH) de suelo a Supabase -- igac_suelos_ufh (ver
infra/supabase/migrations/20260822170000_crear_tabla_igac_suelos_ufh.sql).

Por qué esto existe además de packages/construdata/igac_client.py: ese
módulo consulta datos.gov.co (Socrata) EN VIVO en cada pregunta del chat.
El dato en sí es esencialmente estático (taxonomía de suelo no cambia con
el tiempo, a diferencia del caudal del IDEAM) -- cargarlo una vez a
Supabase evita depender de una llamada HTTP externa por pregunta y deja
la app resiliente ante rate-limits o caídas de datos.gov.co.

Fuente: misma plataforma pública Socrata sin autenticación que
ideam_client.py (datos.gov.co, resource fy2r-gwsd, 169.088 filas
verificadas en vivo 2026-08-22). Geometría (the_geom) NO se trae -- nunca
se usa para el contexto de texto del RAG.

Uso: python cargar_suelos_ufh.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

BASE_URL = "https://www.datos.gov.co/resource"
DATASET_UFH = "fy2r-gwsd"
_TIMEOUT = 30.0
_PAGINA = 50000  # límite práctico de Socrata por página

# Todos los campos de atributo del dataset origen, EXCEPTO the_geom
# (geometría de polígono -- nunca se usa para el contexto de texto y solo
# infla la tabla). "consecutiv" es el índice único de fila que usamos
# como id primario.
_CAMPOS = (
    "consecutiv,municipio,departamen,cod_dane_m,taxonomia,textura,"
    "pendiente,drenaje,inund,profundi,pedrego,salinidad,ph,alt_msnm,"
    "clase_ufh,area_ha"
)


def _parsear_float(valor) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _parsear_int(valor) -> int | None:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)

    print("Descargando catálogo nacional de suelos UFH (IGAC/UPRA, datos.gov.co)...")
    total_filas = 0
    sin_id = 0
    offset = 0

    with httpx.Client(timeout=_TIMEOUT) as client:
        while True:
            resp = client.get(
                f"{BASE_URL}/{DATASET_UFH}.json",
                params={
                    "$select": _CAMPOS,
                    "$order": "consecutiv",
                    "$limit": _PAGINA,
                    "$offset": offset,
                },
            )
            resp.raise_for_status()
            pagina = resp.json()
            if not pagina:
                break

            filas = []
            for r in pagina:
                id_fila = _parsear_int(r.get("consecutiv"))
                if id_fila is None:
                    sin_id += 1
                    continue
                filas.append({
                    "id": id_fila,
                    "municipio": r.get("municipio"),
                    "departamento": r.get("departamen"),
                    "cod_dane_municipio": r.get("cod_dane_m"),
                    "taxonomia": r.get("taxonomia"),
                    "textura": r.get("textura"),
                    "pendiente": r.get("pendiente"),
                    "drenaje": r.get("drenaje"),
                    "inund": r.get("inund"),
                    "profundi": r.get("profundi"),
                    "pedrego": r.get("pedrego"),
                    "salinidad": r.get("salinidad"),
                    "ph": r.get("ph"),
                    "alt_msnm": r.get("alt_msnm"),
                    "clase_ufh": r.get("clase_ufh"),
                    "area_ha": _parsear_float(r.get("area_ha")),
                })

            for i in range(0, len(filas), 1000):
                lote = filas[i:i + 1000]
                sb.table("igac_suelos_ufh").upsert(lote, on_conflict="id").execute()

            total_filas += len(filas)
            offset += _PAGINA
            print(f"  offset={offset} filas_acumuladas={total_filas}")

            if len(pagina) < _PAGINA:
                break

    print(f"\nOK: {total_filas} filas cargadas en igac_suelos_ufh ({sin_id} sin 'consecutiv', saltadas).")


if __name__ == "__main__":
    inicio = time.time()
    main()
    print(f"Tiempo total: {time.time() - inicio:.0f}s")
