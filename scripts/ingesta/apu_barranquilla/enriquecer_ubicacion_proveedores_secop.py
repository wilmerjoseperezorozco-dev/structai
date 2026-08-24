"""
Enriquece los 78 proveedores del catálogo nacional IAD MIPYMES
(apu_proveedores_nacional) con departamento/municipio real, cruzando por
nombre contra el registro público oficial SECOP II - Proveedores
Registrados (datos.gov.co, resource qmzu-gj57, sin autenticación).

Por qué esto existe: el catálogo IAD MIPYMES en sí NO trae ubicación --
verificado abriendo el Excel fuente directamente (solo nombre de ítem +
precio por proveedor, una sola hoja). SECOP II sí publica departamento y
municipio reales de empresas registradas para contratar con el Estado.
Cruce por nombre, no por NIT (no lo teníamos guardado) -- normaliza
puntuación (quita puntos/comas de sufijos como "S.A.S." -> "SAS") y
extrae el nombre legal cuando el proveedor tiene un alias comercial entre
paréntesis (ej. "ANGEL RAFAEL RINCON MARIÑO (FERRETERIA NICHOLSON)" ->
busca "ANGEL RAFAEL RINCON MARIÑO").

Solo se guarda un match cuando es exacto tras normalizar (o hay UN único
candidato por contención) -- nunca se adivina la ciudad de un proveedor
real. Los que no matchean quedan con departamento/municipio NULL, visible
como "sin ubicación verificada" en vez de inventar algo.

Uso: python enriquecer_ubicacion_proveedores_secop.py
"""
from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

SECOP_URL = "https://www.datos.gov.co/resource/qmzu-gj57.json"
_TIMEOUT = 20.0

# Colombia Compra Eficiente a veces devuelve texto con codificación mal
# resuelta para vocales tildadas/ñ en municipio (ej. "MEDELLiN",
# "BOGOTa") -- se guarda tal cual llega, no se corrige a mano: es un
# problema de la fuente, no algo que debamos inventar cómo arreglar.
_SUFIJOS_PUNTUADOS = re.compile(r"[.,]")


def _nombre_legal(nombre_completo: str) -> str:
    """Quita el alias comercial entre paréntesis, si lo hay -- SECOP
    registra la razón social/nombre legal, no el nombre comercial."""
    return nombre_completo.split("(")[0].strip()


def _normalizar(nombre: str) -> str:
    """Quita puntuación de sufijos societarios ('S.A.S.' -> 'SAS',
    'LTDA.' -> 'LTDA') y espacios repetidos, para que la comparación no
    dependa de si alguien escribió el punto o no."""
    sin_puntuacion = _SUFIJOS_PUNTUADOS.sub("", nombre)
    return " ".join(sin_puntuacion.upper().split())


def _buscar_en_secop(client: httpx.Client, nombre_normalizado: str) -> dict | None:
    """Busca por contención (ILIKE) del nombre normalizado -- devuelve el
    registro SOLO si hay exactamente un candidato (evita adivinar entre
    varios homónimos). None si no hay match o hay ambigüedad real."""
    escapado = nombre_normalizado.replace("'", "''")
    resp = client.get(
        SECOP_URL,
        params={
            "$where": f"upper(nombre) like upper('%{escapado}%')",
            "$limit": 5,
        },
    )
    resp.raise_for_status()
    candidatos = resp.json()
    if len(candidatos) != 1:
        return None
    return candidatos[0]


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)

    proveedores = (
        sb.table("apu_proveedores_nacional").select("id, nombre").execute().data
    )
    print(f"Proveedores a procesar: {len(proveedores)}")

    con_match = 0
    sin_match = []
    ambiguos = []

    with httpx.Client(timeout=_TIMEOUT) as client:
        for p in proveedores:
            nombre_legal = _normalizar(_nombre_legal(p["nombre"]))
            try:
                registro = _buscar_en_secop(client, nombre_legal)
            except httpx.HTTPError as err:
                print(f"  error de red en '{p['nombre']}': {err} -- se salta")
                continue

            if registro is None:
                # Distinguir "cero candidatos" de "demasiados" solo para
                # el resumen final -- ambos casos quedan sin ubicación.
                escapado = nombre_legal.replace("'", "''")
                total = client.get(
                    SECOP_URL,
                    params={"$where": f"upper(nombre) like upper('%{escapado}%')", "$select": "count(*)"},
                ).json()
                if total and int(total[0].get("count", 0)) > 1:
                    ambiguos.append(p["nombre"])
                else:
                    sin_match.append(p["nombre"])
                continue

            departamento = registro.get("departamento")
            municipio = registro.get("municipio")
            if departamento in (None, "No Provisto", "No definido"):
                departamento = None
            if municipio in (None, "No Provisto", "No definido"):
                municipio = None

            sb.table("apu_proveedores_nacional").update({
                "nit": registro.get("nit"),
                "departamento": departamento,
                "municipio": municipio,
                "ubicacion_verificada_en": time.strftime("%Y-%m-%d"),
            }).eq("id", p["id"]).execute()
            con_match += 1

    print(f"\nOK: {con_match}/{len(proveedores)} proveedores enriquecidos con ubicación real de SECOP II.")
    if ambiguos:
        print(f"Ambiguos (varios candidatos, no se adivinó): {len(ambiguos)}")
        for n in ambiguos:
            print(f"  - {n}")
    if sin_match:
        print(f"Sin match en SECOP II (posible: vende via IAD MIPYMES sin estar en el registro de proponentes): {len(sin_match)}")
        for n in sin_match:
            print(f"  - {n}")


if __name__ == "__main__":
    inicio = time.time()
    main()
    print(f"\nTiempo total: {time.time() - inicio:.0f}s")
