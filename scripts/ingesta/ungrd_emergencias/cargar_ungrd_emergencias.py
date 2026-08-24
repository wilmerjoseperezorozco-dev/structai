"""
Carga masiva del histórico real de emergencias reportadas a la UNGRD
(2019-2024, datos.gov.co) -- ver issue #21 del repo structai y
infra/supabase/migrations/20260824130000_crear_tabla_ungrd_emergencias.sql
para el detalle completo de la investigación.

Dos datasets con esquema DISTINTO para el detalle de ayuda logística
(materiales, kits, subsidios) pero 20 campos de impacto en COMÚN --
se normaliza solo a esos campos comunes, no se intenta reconciliar el
detalle de ayuda entre ambos (sería inventar equivalencias que la fuente
no garantiza).

Idempotente por fuente: borra e inserta de nuevo cada fuente completa en
vez de intentar deduplicar por clave compuesta -- no hay un id estable
compartido entre los dos datasets, y son solo ~42.000 filas totales,
recargar completo es barato y siempre correcto.

Uso: python cargar_ungrd_emergencias.py
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

BASE_URL = "https://www.datos.gov.co/resource"
_TIMEOUT = 60.0
_PAGINA = 5000

# Fuentes: (etiqueta, resource_id, nombre del campo de código DIVIPOLA en
# ESE dataset -- difiere entre los dos, ver investigación en el issue #21)
_FUENTES = (
    ("UNGRD 2019-2022", "wwkg-r6te", "divipola"),
    ("UNGRD 2023-2024", "rgre-6ak4", "codificaci_n_segun_divipola"),
)

# Los 20 campos de impacto reales que SÍ son consistentes entre ambos
# datasets (verificado comparando columnas antes de escribir este loader).
_CAMPOS_COMUNES = (
    "fecha,departamento,municipio,evento,fallecidos,heridos,desaparecidos,"
    "personas,familias,viviendas_destruidas,viviendas_averiadas,"
    "vias_averiadas,puentes_vehiculares,puentes_peatonales,acueducto,"
    "alcantarillado,centros_de_salud,centros_educativos,"
    "centros_comunitarios,hectareas,otros_afectacion"
)


def _parsear_int(valor) -> int | None:
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return None


def _parsear_float(valor) -> float | None:
    try:
        return float(valor)
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

    total_general = 0
    with httpx.Client(timeout=_TIMEOUT) as client:
        for etiqueta, resource_id, campo_divipola in _FUENTES:
            print(f"\n=== {etiqueta} ({resource_id}) ===")
            print("Borrando carga previa de esta fuente (recarga completa, idempotente)...")
            sb.table("ungrd_emergencias").delete().eq("fuente", etiqueta).execute()

            offset = 0
            total_fuente = 0
            while True:
                resp = client.get(
                    f"{BASE_URL}/{resource_id}.json",
                    params={
                        "$select": f"{_CAMPOS_COMUNES},{campo_divipola} as divipola_codigo",
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
                    codigo_municipio = None
                    codigo_crudo = r.get("divipola_codigo")
                    if codigo_crudo and str(codigo_crudo).strip() not in ("0", ""):
                        registro_divipola = divipola.resolver_por_codigo(codigo_crudo)
                        if registro_divipola:
                            codigo_municipio = registro_divipola["codigo_municipio"]

                    fecha = (r.get("fecha") or "")[:10] or None
                    filas.append({
                        "fecha": fecha,
                        "departamento": r.get("departamento"),
                        "municipio": r.get("municipio"),
                        "codigo_municipio": codigo_municipio,
                        "evento": r.get("evento"),
                        "fallecidos": _parsear_int(r.get("fallecidos")),
                        "heridos": _parsear_int(r.get("heridos")),
                        "desaparecidos": _parsear_int(r.get("desaparecidos")),
                        "personas": _parsear_int(r.get("personas")),
                        "familias": _parsear_int(r.get("familias")),
                        "viviendas_destruidas": _parsear_int(r.get("viviendas_destruidas")),
                        "viviendas_averiadas": _parsear_int(r.get("viviendas_averiadas")),
                        "vias_averiadas": _parsear_int(r.get("vias_averiadas")),
                        "puentes_vehiculares": _parsear_int(r.get("puentes_vehiculares")),
                        "puentes_peatonales": _parsear_int(r.get("puentes_peatonales")),
                        "acueducto": _parsear_int(r.get("acueducto")),
                        "alcantarillado": _parsear_int(r.get("alcantarillado")),
                        "centros_de_salud": _parsear_int(r.get("centros_de_salud")),
                        "centros_educativos": _parsear_int(r.get("centros_educativos")),
                        "centros_comunitarios": _parsear_int(r.get("centros_comunitarios")),
                        "hectareas": _parsear_float(r.get("hectareas")),
                        "otros_afectacion": r.get("otros_afectacion"),
                        "fuente": etiqueta,
                    })

                for i in range(0, len(filas), 1000):
                    sb.table("ungrd_emergencias").insert(filas[i:i + 1000]).execute()

                total_fuente += len(filas)
                offset += _PAGINA
                print(f"  offset={offset} filas_acumuladas={total_fuente}")
                if len(pagina) < _PAGINA:
                    break

            print(f"OK {etiqueta}: {total_fuente} eventos cargados.")
            total_general += total_fuente

    print(f"\nOK TOTAL: {total_general} eventos de emergencia cargados en ungrd_emergencias.")


if __name__ == "__main__":
    inicio = time.time()
    main()
    print(f"\nTiempo total: {time.time() - inicio:.0f}s")
