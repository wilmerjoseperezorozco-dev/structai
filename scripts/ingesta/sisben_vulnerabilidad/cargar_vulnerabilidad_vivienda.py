"""
Carga masiva de la señal estadística de vulnerabilidad de vivienda por
municipio (% de viviendas con material de pared vulnerable), derivada de
la muestra anonimizada Sisbén IV (DNP, corte marzo-2022, datos.gov.co
resource np8m-kdhq) -- ver
infra/supabase/migrations/20260824120000_crear_tabla_sisben_vulnerabilidad_vivienda.sql
para el detalle completo de qué significa "vulnerable" aquí y por qué.

Por qué se agrega server-side (SoQL $group), no se traen 1.44M filas:
la tabla origen tiene 1.446.237 filas -- Socrata soporta agregación tipo
SQL (count(*) agrupado por cod_mpio), así que se piden solo los totales
ya agregados (2 consultas: total por municipio, vulnerables por
municipio) en vez de descargar y agregar 1.4M filas a mano.

Resolución de municipio/departamento: vía divipola.resolver_por_codigo()
(nuevo, agregado en esta misma sesión) -- cod_mpio de Sisbén ya es el
código DIVIPOLA oficial, no hace falta normalizar nombres.

Uso: python cargar_vulnerabilidad_vivienda.py
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
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import divipola  # noqa: E402

SISBEN_VIVIENDA_URL = "https://www.datos.gov.co/resource/np8m-kdhq.json"
_TIMEOUT = 60.0
_CORTE = "SIV_2022"

# Códigos VIV002 documentados como material de pared de mal desempeño
# sísmico -- ver comentario completo en la migración de esta tabla.
_CODIGOS_MATERIAL_VULNERABLE = ("2", "3", "4", "5", "7", "8", "9", "10")


def _agregado_por_municipio(client: httpx.Client, where: str | None = None) -> dict[str, int]:
    """Cuenta filas agrupadas por cod_mpio server-side (SoQL $group) --
    hasta 2000 municipios en un solo request, más que suficiente para los
    1.099 reales."""
    params = {"$select": "cod_mpio, count(*) as total", "$group": "cod_mpio", "$limit": 2000}
    if where:
        params["$where"] = where
    resp = client.get(SISBEN_VIVIENDA_URL, params=params)
    resp.raise_for_status()
    return {fila["cod_mpio"]: int(fila["total"]) for fila in resp.json()}


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)

    print("Agregando total de viviendas por municipio (SoQL $group)...")
    with httpx.Client(timeout=_TIMEOUT) as client:
        totales = _agregado_por_municipio(client)
        print(f"  Municipios con muestra: {len(totales)}")

        print("Agregando viviendas con material vulnerable por municipio...")
        where_vulnerable = "viv002 in (" + ",".join(f"'{c}'" for c in _CODIGOS_MATERIAL_VULNERABLE) + ")"
        vulnerables = _agregado_por_municipio(client, where=where_vulnerable)

    filas = []
    sin_resolver = []
    for cod_mpio, total in totales.items():
        n_vulnerable = vulnerables.get(cod_mpio, 0)
        registro_divipola = divipola.resolver_por_codigo(cod_mpio)
        if registro_divipola is None:
            sin_resolver.append(cod_mpio)
        filas.append({
            "codigo_municipio": cod_mpio,
            "municipio": registro_divipola["municipio"] if registro_divipola else None,
            "departamento": registro_divipola["departamento"] if registro_divipola else None,
            "n_viviendas_muestra": total,
            "n_viviendas_material_vulnerable": n_vulnerable,
            "pct_material_vulnerable": round(100.0 * n_vulnerable / total, 2) if total else 0.0,
            "corte": _CORTE,
        })

    print(f"Subiendo {len(filas)} municipios a Supabase...")
    for i in range(0, len(filas), 500):
        lote = filas[i:i + 500]
        sb.table("sisben_vulnerabilidad_vivienda_municipio").upsert(
            lote, on_conflict="codigo_municipio"
        ).execute()

    print(f"\nOK: {len(filas)} municipios cargados.")
    if sin_resolver:
        print(f"Códigos de municipio sin resolver en DIVIPOLA ({len(sin_resolver)}, quedan sin nombre pero con el dato numérico): {sin_resolver[:20]}")


if __name__ == "__main__":
    inicio = time.time()
    main()
    print(f"\nTiempo total: {time.time() - inicio:.0f}s")
