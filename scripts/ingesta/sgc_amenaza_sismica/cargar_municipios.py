"""
Carga masiva (una sola vez, o cuando el SGC actualice valores) del catálogo
nacional de amenaza sísmica NSR-10 por municipio a Supabase --
sgc_amenaza_sismica_municipios (ver
infra/supabase/migrations/20260822160000_crear_tabla_sgc_amenaza_sismica_municipios.sql).

Por qué esto existe además de packages/construdata/sgc_amenaza_sismica.py:
ese módulo cachea en memoria del PROCESO (se pierde en cada arranque en frío)
y depende de un endpoint no documentado, HTTP, no oficial
(srvags.sgc.gov.co) en el camino crítico de cada respuesta -- si ese
servicio cambia o cae, la app pierde el dato hasta que vuelva. Este script
persiste el mismo dato una vez a Supabase para que sgc_amenaza_sismica.py
pueda leerlo de ahí primero y solo dependa del endpoint en vivo como
respaldo si la tabla llegara a estar vacía.

Reusa la misma consulta paginada ya probada en producción -- no reinventar
el manejo de exceededTransferLimit ni el parseo de atributos.

Uso: python cargar_municipios.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import sgc_amenaza_sismica  # noqa: E402


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)

    print("Consultando catálogo nacional de amenaza sísmica NSR-10 (srvags.sgc.gov.co)...")
    # OJO: _cargar_desde_servicio_vivo(), NO _cargar_cache() -- _cargar_cache()
    # ahora lee Supabase PRIMERO (ver sgc_amenaza_sismica.py), así que llamarla
    # aquí solo devolvería lo que ya está en la tabla (vacío la primera vez,
    # potencialmente obsoleto en recargas). Este script existe justo para
    # refrescar esa tabla desde la fuente real.
    cache = sgc_amenaza_sismica._cargar_desde_servicio_vivo()
    if not cache:
        print("ERROR: el servicio del SGC no respondió (o respuesta vacía) -- nada que cargar.")
        sys.exit(1)
    total_municipios = sum(len(v) for v in cache.values())
    print(f"Nombres únicos: {len(cache)} -- municipios totales (incl. nombres repetidos entre departamentos): {total_municipios}")

    filas_por_clave: dict[tuple[str, str], dict] = {}
    for normalizado, registros in cache.items():
        for r in registros:
            depto_normalizado = sgc_amenaza_sismica._normalizar(r.get("departamento") or "")
            clave = (normalizado, depto_normalizado)
            if clave in filas_por_clave:
                # Duplicado real dentro de la propia fuente del SGC (ej.
                # 'Inzá, Cauca' aparece dos veces con valores idénticos --
                # encontrado 2026-08-22). Se descarta la repetición, no es
                # un municipio distinto.
                continue
            filas_por_clave[clave] = {
                "municipio_normalizado": normalizado,
                "departamento_normalizado": depto_normalizado,
                "municipio": r["municipio"],
                "departamento": r.get("departamento"),
                "aa": r.get("aa"),
                "av": r.get("av"),
                "ae": r.get("ae"),
                "ad": r.get("ad"),
                "zona": r.get("zona"),
                "longitud": r.get("longitud"),
                "latitud": r.get("latitud"),
            }
    filas = list(filas_por_clave.values())

    print("Subiendo a Supabase (upsert por lotes de 500)...")
    for i in range(0, len(filas), 500):
        lote = filas[i:i + 500]
        sb.table("sgc_amenaza_sismica_municipios").upsert(
            lote, on_conflict="municipio_normalizado,departamento_normalizado"
        ).execute()
    print(f"OK: {len(filas)} municipios cargados en sgc_amenaza_sismica_municipios.")


if __name__ == "__main__":
    inicio = time.time()
    main()
    print(f"Tiempo total: {time.time() - inicio:.0f}s")
