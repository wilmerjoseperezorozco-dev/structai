"""
Carga masiva del histórico de caudal (Q_MEDIA_M, m³/s) de TODAS las
estaciones hidrológicas (Limnimétrica/Limnigráfica) del IDEAM a Supabase --
base real para el análisis estadístico de anomalía de caudal (ver
infra/supabase/migrations/20260822123425_crear_tablas_ideam_caudal_historico.sql).

Por qué esto vive aquí y no solo en ideam_client.py: el dato "de ahora"
sigue consultándose EN VIVO contra el bucket S3 (ideam_client.caudal_por_municipio),
pero el HISTÓRICO completo (necesario para calcular qué es "normal" para
cada río en cada mes) es demasiado costoso para traer en cada pregunta del
chat -- se carga una vez aquí, se recalculan las estadísticas mensuales con
una consulta SQL aparte después de correr este script (ver el comentario al
final de este archivo).

Fuente: mismo bucket S3 público sin autenticación que ideam_client.py
(datos.ideam.gov.co/s3-estacionesideam, verificado en vivo 2026-08-22).

Uso: python cargar_caudal_historico.py
"""
from __future__ import annotations

import csv
import io
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

# Reusa el mismo cliente que ya está probado en producción -- no reinventar
# la resolución de estaciones ni el parseo de CSV.
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "construdata"))
import ideam_client  # noqa: E402

_TIMEOUT = 20.0


def _catalogo_completo_limn() -> list[dict]:
    """Todas las estaciones Limnimétrica/Limnigráfica del catálogo nacional
    IDEAM, deduplicadas por código normalizado a 10 dígitos (ver el mismo
    bug documentado en ideam_client._descargar_csv_caudal). Sin filtrar por
    Activa/Suspendida a propósito: una estación suspendida igual aporta
    historia real válida para calcular el promedio de ese río en ese mes."""
    filas = ideam_client._get(
        ideam_client.DATASETS["estaciones"],
        {"$where": ideam_client._where_ilike("categoria", "Limn"), "$limit": 5000},
    )
    vistos: set[str] = set()
    unicas: list[dict] = []
    for f in filas:
        codigo = (f.get("codigo") or "").zfill(10)
        if codigo and codigo not in vistos:
            vistos.add(codigo)
            unicas.append({**f, "codigo": codigo})
    return unicas


def _parsear_float(valor) -> float | None:
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return None
    # Algunos registros de "Preliminar" tienen decimales absurdamente largos
    # (float de sensor sin redondear) -- se guarda tal cual, sin inventar
    # precisión ni redondear de más; el redondeo de presentación ya vive en
    # ideam_client.formatear_caudal().
    return v


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)

    print("Consultando catálogo nacional de estaciones Limnimétrica/Limnigráfica...")
    estaciones = _catalogo_completo_limn()
    print(f"Estaciones únicas a procesar: {len(estaciones)}")

    filas_estaciones = []
    for e in estaciones:
        filas_estaciones.append({
            "codigo": e["codigo"],
            "nombre": e.get("nombre"),
            "corriente": e.get("corriente"),
            "municipio": e.get("municipio"),
            "departamento": e.get("departamento"),
            "categoria": e.get("categoria"),
            "estado": e.get("estado"),
            "latitud": _parsear_float(e.get("latitud")),
            "longitud": _parsear_float(e.get("longitud")),
            "altitud": _parsear_float(e.get("altitud")),
        })
    print("Subiendo catálogo de estaciones (upsert)...")
    sb.table("ideam_estaciones_caudal").upsert(filas_estaciones, on_conflict="codigo").execute()
    print(f"OK: {len(filas_estaciones)} estaciones en ideam_estaciones_caudal.")

    print("\nDescargando histórico por estación (esto tarda varios minutos)...")
    total_filas_historicas = 0
    con_datos = 0
    sin_datos = 0
    errores = 0

    for i, e in enumerate(estaciones, 1):
        codigo = e["codigo"]
        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                url = f"{ideam_client.S3_BASE}/{ideam_client.S3_PREFIJO_CAUDAL}{codigo}-Q_MEDIA_M.csv"
                resp = client.get(url)
                if resp.status_code == 404:
                    sin_datos += 1
                    continue
                resp.raise_for_status()
        except httpx.HTTPError as err:
            errores += 1
            print(f"  [{i}/{len(estaciones)}] {codigo}: error de red ({err}) -- se salta")
            continue

        lector = csv.DictReader(io.StringIO(resp.text))
        filas_csv = list(lector)
        if not filas_csv:
            sin_datos += 1
            continue

        filas_hist = []
        for f in filas_csv:
            fecha = (f.get("fechaObservacion") or "")[:10]  # YYYY-MM-DD
            if not fecha:
                continue
            filas_hist.append({
                "codigo_estacion": codigo,
                "fecha": fecha,
                "caudal_m3s": _parsear_float(f.get("valorObservado")),
                "nivel_aprobacion": f.get("nivelAprobacion"),
            })

        if filas_hist:
            # Upsert por lotes de 500 -- algunas estaciones tienen 700+
            # meses de historia (60 años), no vale la pena mandarlo todo en
            # una sola llamada.
            for j in range(0, len(filas_hist), 500):
                lote = filas_hist[j:j + 500]
                sb.table("ideam_caudal_historico").upsert(
                    lote, on_conflict="codigo_estacion,fecha"
                ).execute()
            total_filas_historicas += len(filas_hist)
            con_datos += 1

        if i % 50 == 0 or i == len(estaciones):
            print(
                f"  [{i}/{len(estaciones)}] con_datos={con_datos} "
                f"sin_datos={sin_datos} errores={errores} "
                f"filas_totales={total_filas_historicas}"
            )

    print(
        f"\nOK: {con_datos} estaciones con histórico cargado "
        f"({total_filas_historicas} filas), {sin_datos} sin archivo en S3, "
        f"{errores} con error de red."
    )
    print(
        "\nSiguiente paso manual: recalcular ideam_caudal_estadisticas_mes "
        "con la consulta SQL agregada (ver comentario al final de este archivo)."
    )


# ─── Recalcular estadísticas mensuales (correr DESPUÉS de este script) ──────
# insert into ideam_caudal_estadisticas_mes
#   (codigo_estacion, mes, promedio_m3s, desviacion_m3s, p10_m3s, p90_m3s,
#    minimo_m3s, maximo_m3s, n_observaciones)
# select
#   codigo_estacion,
#   extract(month from fecha)::smallint as mes,
#   avg(caudal_m3s), stddev(caudal_m3s),
#   percentile_cont(0.1) within group (order by caudal_m3s),
#   percentile_cont(0.9) within group (order by caudal_m3s),
#   min(caudal_m3s), max(caudal_m3s), count(*)
# from ideam_caudal_historico
# where caudal_m3s is not null
# group by codigo_estacion, extract(month from fecha)
# on conflict (codigo_estacion, mes) do update set
#   promedio_m3s = excluded.promedio_m3s, desviacion_m3s = excluded.desviacion_m3s,
#   p10_m3s = excluded.p10_m3s, p90_m3s = excluded.p90_m3s,
#   minimo_m3s = excluded.minimo_m3s, maximo_m3s = excluded.maximo_m3s,
#   n_observaciones = excluded.n_observaciones;

if __name__ == "__main__":
    inicio = time.time()
    main()
    print(f"\nTiempo total: {time.time() - inicio:.0f}s")
