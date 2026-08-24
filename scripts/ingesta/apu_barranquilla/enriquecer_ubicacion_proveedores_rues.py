"""
Segunda pasada de enriquecimiento de ubicación para apu_proveedores_nacional
-- cubre los proveedores que NO matchearon contra SECOP II - Proveedores
Registrados (ver enriquecer_ubicacion_proveedores_secop.py), usando una
fuente más amplia: el registro consolidado de Cámaras de Comercio de
Colombia, "Personas Naturales, Personas Jurídicas y Entidades Sin Ánimo
de Lucro" (datos.gov.co, resource c82u-588k). SECOP II solo cubre
empresas que se registraron para contratar con el Estado -- un proveedor
mipyme real de IAD MIPYMES puede vender sin nunca haberse inscrito ahí.
Este registro es el mercantil general (toda empresa activa en Colombia
pasa por una Cámara de Comercio), mucho más amplio.

Diferencia técnica real encontrada probando esta fuente: es una tabla
enorme (registro histórico nacional completo desde los años 70) -- un
`$where ilike '%texto%'` sin índice hace time out (probado en vivo, >40s
sin respuesta). El parámetro `$q` de Socrata (búsqueda de texto indexada)
sí responde rápido -- se usa ese, NUNCA `$where ilike`, para esta fuente.

`camara_comercio` da la ciudad (sede de la Cámara donde está matriculada
la empresa, la mejor aproximación pública disponible a su ubicación real).
Se prioriza `estado_matricula = 'ACTIVA'` -- una empresa puede tener
registros históricos cancelados con el mismo nombre.

Solo se guarda cuando el nombre normalizado del candidato coincide con el
del proveedor buscado (no solo "contiene alguna palabra en común", que es
lo que $q permite de forma más laxa) -- mismo estándar de "nunca adivinar
la ciudad de un proveedor real" que la primera pasada.

Uso: python enriquecer_ubicacion_proveedores_rues.py
"""
from __future__ import annotations

import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

RUES_URL = "https://www.datos.gov.co/resource/c82u-588k.json"
_TIMEOUT = 40.0
_SUFIJOS_PUNTUADOS = re.compile(r"[.,]")


def _nombre_legal(nombre_completo: str) -> str:
    return nombre_completo.split("(")[0].strip()


def _normalizar(nombre: str) -> str:
    sin_puntuacion = _SUFIJOS_PUNTUADOS.sub("", nombre)
    return " ".join(sin_puntuacion.upper().split())


def _normalizar_municipio(texto: str) -> str:
    """Mismo criterio que sgc_amenaza_sismica._normalizar() -- sin tildes,
    solo alfanumérico -- para poder cruzar camara_comercio (RUES) contra
    municipio_normalizado (SGC) sin que una tilde faltante rompa el match."""
    nfkd = unicodedata.normalize("NFKD", texto.upper())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    solo_alfanumerico = "".join(c if c.isalnum() or c.isspace() else " " for c in sin_tildes)
    return " ".join(solo_alfanumerico.split())


def _buscar_en_rues(client: httpx.Client, nombre_legal: str, nombre_normalizado: str) -> dict | None:
    """Busca por texto completo indexado ($q, no ilike -- ver docstring del
    módulo). Filtra los candidatos a los que coinciden EXACTO tras
    normalizar puntuación (no basta con que $q los haya encontrado
    relevantes) y prioriza estado_matricula=ACTIVA. None si no hay ningún
    candidato con nombre exacto -- nunca se adivina con un candidato
    parecido pero no idéntico."""
    resp = client.get(RUES_URL, params={"$q": nombre_legal, "$limit": 20})
    resp.raise_for_status()
    candidatos = resp.json()

    exactos = [c for c in candidatos if _normalizar(c.get("razon_social") or "") == nombre_normalizado]
    if not exactos:
        return None

    activos = [c for c in exactos if c.get("estado_matricula") == "ACTIVA"]
    pool = activos or exactos

    # Si hay varias sedes/cámaras distintas para el mismo nombre exacto
    # (empresa con sucursales, o dos empresas homónimas reales), no se
    # adivina cuál -- se prefiere la fecha de renovación/matrícula más
    # reciente como mejor proxy de "la sede vigente hoy", pero se marca
    # como con posible ambigüedad para el resumen final.
    pool.sort(key=lambda c: (c.get("fecha_renovacion") or c.get("fecha_matricula") or ""), reverse=True)
    ciudades = {c.get("camara_comercio") for c in pool}
    return {"registro": pool[0], "ambiguo": len(ciudades) > 1}


def main():
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_KEY"]
    )
    from supabase import create_client
    sb = create_client(supabase_url, supabase_key)

    # Solo los que la primera pasada (SECOP II) dejó sin departamento --
    # no se re-toca a los 29 ya enriquecidos.
    proveedores = (
        sb.table("apu_proveedores_nacional")
        .select("id, nombre")
        .is_("departamento", "null")
        .execute()
        .data
    )
    print(f"Proveedores pendientes (sin match en SECOP II): {len(proveedores)}")

    # RUES solo da el nombre de la Cámara de Comercio (~= ciudad), no el
    # departamento. Se resuelve el departamento real cruzando contra
    # sgc_amenaza_sismica_municipios (1.121 municipios reales, cargados
    # 2026-08-24, ver project_structai_guardian_incidentes) en vez de dejar
    # el departamento vacío -- reusa un dato ya verificado en esta misma
    # sesión en lugar de duplicar la lógica de resolución de municipio.
    #
    # OJO paginación: la tabla tiene 1.121 filas, por encima del límite
    # por defecto de PostgREST (1.000) -- un .select() sin .range() trunca
    # en silencio (bug real encontrado y corregido en esta misma sesión:
    # "Bogotá" y "Barranquilla" quedaron sin departamento resuelto porque
    # BARRANQUILLA cayó fuera de las primeras 1.000 filas devueltas).
    municipios_reales = []
    offset = 0
    while True:
        pagina = (
            sb.table("sgc_amenaza_sismica_municipios")
            .select("municipio_normalizado, departamento")
            .range(offset, offset + 999)
            .execute()
            .data
        )
        municipios_reales.extend(pagina)
        if len(pagina) < 1000:
            break
        offset += 1000
    depto_por_municipio = {m["municipio_normalizado"]: m["departamento"] for m in municipios_reales}
    # Bogotá D.C. es un caso especial real: RUES/SECOP dan "BOGOTA" (o
    # variantes) como ciudad, pero el DIVIPOLA oficial (y por lo tanto la
    # clave normalizada en sgc_amenaza_sismica_municipios) es
    # "Bogotá, D.C." -> "BOGOTA D C". Sin este alias, el municipio más
    # grande del país queda sistemáticamente sin departamento resuelto.
    if "BOGOTA D C" in depto_por_municipio:
        depto_por_municipio["BOGOTA"] = depto_por_municipio["BOGOTA D C"]

    con_match = 0
    ambiguos = 0
    sin_match = []

    with httpx.Client(timeout=_TIMEOUT) as client:
        for p in proveedores:
            nombre_legal = _nombre_legal(p["nombre"])
            nombre_normalizado = _normalizar(nombre_legal)
            try:
                resultado = _buscar_en_rues(client, nombre_legal, nombre_normalizado)
            except httpx.HTTPError as err:
                print(f"  error de red en '{p['nombre']}': {err} -- se salta")
                continue

            if resultado is None:
                sin_match.append(p["nombre"])
                continue

            registro = resultado["registro"]
            ciudad = registro.get("camara_comercio")
            if resultado["ambiguo"]:
                ambiguos += 1
                print(f"  ambiguo (varias sedes/homónimos ACTIVOS): {p['nombre']} -> se usa la más reciente: {ciudad}")

            departamento = depto_por_municipio.get(_normalizar_municipio(ciudad)) if ciudad else None
            municipio_final = ciudad.title() if ciudad else None
            # Bogotá D.C. es simultáneamente ciudad y departamento -- guardar
            # ambos campos produce un "Bogota, Bogotá, D. C." redundante en
            # el texto que ve el usuario. El departamento ya identifica el
            # lugar sin ambigüedad, así que se deja municipio vacío en ese
            # caso (mismo criterio aplicado al backfill manual de esta sesión).
            if municipio_final and _normalizar_municipio(municipio_final) == "BOGOTA":
                municipio_final = None

            sb.table("apu_proveedores_nacional").update({
                "nit": registro.get("nit") or registro.get("numero_identificacion"),
                "departamento": departamento,
                "municipio": municipio_final,
                "ubicacion_verificada_en": time.strftime("%Y-%m-%d"),
            }).eq("id", p["id"]).execute()
            con_match += 1

    print(f"\nOK: {con_match}/{len(proveedores)} proveedores adicionales enriquecidos con ciudad real de RUES (Cámaras de Comercio).")
    print(f"De esos, {ambiguos} tenían más de una sede activa -- se usó la más reciente.")
    if sin_match:
        print(f"Siguen sin match ni en SECOP II ni en RUES: {len(sin_match)}")
        for n in sin_match:
            print(f"  - {n}")


if __name__ == "__main__":
    inicio = time.time()
    main()
    print(f"\nTiempo total: {time.time() - inicio:.0f}s")
