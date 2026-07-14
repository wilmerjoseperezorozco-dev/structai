"""
Carga el corpus POT (Plan de Ordenamiento Territorial) a motor_chunks
(motor='geopot'), generando embeddings locales. Vincula GeoPot con la fase
de "muestras de laboratorio -> estabilidad/riesgo de suelo -> POT" pedida
por el usuario.

Fuentes reales (Google Drive, carpeta compartida por el usuario 2026-07-14,
Ministerio de Vivienda, Ciudad y Territorio):
  1-2. Los 2 documentos "Recomendaciones técnicas para la contratación..."
       (revisión general / modificación excepcional del POT) -> 73 chunks
       reales extraídos por scripts/extract_pot.py, formato compatible con
       extract_chunks() de ingest_normativa.py.
  3.   "Fuentes de información secundaria para el ordenamiento territorial"
       (Ministerio de Vivienda, Subdirección de Asistencia Técnica, sept.
       2023) — directorio real de fuentes/URLs oficiales (IGAC, SGC, IDEAM,
       IAVH, DNP, DANE, catastros municipales incl. Barranquilla). El PDF
       trae una tabla cuyo orden de celdas se desordena al extraer texto
       plano (limitación de la conversión PDF->texto, no del contenido) —
       se reorganizó por TEMA a partir del texto real ya verificado, sin
       inventar URLs ni entidades que no aparezcan en el documento fuente.

Los 2 anexos en Excel (especificaciones de productos, rev. general / modif.
excepcional) NO se ingestaron: son una matriz de celdas aplanada por la
conversión a texto plano sin separadores de fila confiables — intentar
parsearla automáticamente arriesgaba mezclar columnas de filas distintas
(fabricar relaciones producto/contenido que no son las reales). Quedan
registradas como fuente conocida en normas_registro.notas_vigencia,
pendientes de una extracción manual/hoja por hoja si se necesitan.

Uso: python scripts/ingest_pot.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
POT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "pot"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_normativa import _clean, extract_chunks

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


# Fuentes de información secundaria para el ordenamiento territorial (Anexo 1,
# Ministerio de Vivienda, sept. 2023) — reorganizado por TEMA a partir del
# texto real extraído, URLs y entidades verbatim del documento fuente.
FUENTES_SECUNDARIAS = [
    {
        "seccion": "Fuentes secundarias — Cartografía base y determinantes",
        "titulo": "IGAC — Cartografía base, catastro y determinantes",
        "contenido": (
            "Instituto Geográfico Agustín Codazzi (IGAC): Colombia en Mapas "
            "(https://www.colombiaenmapas.gov.co) — visor unificado de "
            "información cartográfica del país, búsqueda por municipio. "
            "Geoportal IGAC (https://geoportal.igac.gov.co/contenido/datos-abiertos-igac): "
            "cartografía base 1:500.000, 1:100.000 y 1:25.000 (general y por planchas), "
            "bases de datos catastrales geográficas y alfanuméricas por departamento "
            "(construcción, nomenclatura domiciliaria/vial, manzana, predio, urbano/rural). "
            "Especificaciones técnicas de cartografía básica (2016, Capítulo II Modelo de "
            "Datos): https://www.igac.gov.co/es/contenido/areas-estrategicas/especifica. "
            "SIAM (Sistema de Información Ambiental Marina, https://siam.invemar.org.co/informacion-geografica): "
            "cartografía continental y batimetría de mares colombianos."
        ),
    },
    {
        "seccion": "Fuentes secundarias — Riesgos (SGC)",
        "titulo": "Servicio Geológico Colombiano — movimientos en masa, sismicidad, geoamenazas",
        "contenido": (
            "Servicio Geológico Colombiano (SGC), condicionantes del ordenamiento territorial "
            "por riesgo: SIMMA — Sistema de información de movimientos en masa de Colombia "
            "(https://simma.sgc.gov.co/#/). Sismicidad histórica de Colombia "
            "(http://sish.sgc.gov.co/visor/). Catálogo de historia sísmica por municipio "
            "(Consulta Experta Seiscomp, bdrsnc.sgc.gov.co). Geoportal SGC "
            "(https://www2.sgc.gov.co/sgc/mapas/Paginas/geoportal.aspx): geociencias básicas, "
            "recursos minerales, geoamenazas (mapas de amenaza por departamento). Es la fuente "
            "oficial de referencia para los Estudios Básicos de Amenaza por movimientos en "
            "masa exigidos en el POT (Decreto 1077 de 2015)."
        ),
    },
    {
        "seccion": "Fuentes secundarias — Medio ambiente e IDEAM",
        "titulo": "SIAC, IAVH e IDEAM — datos ambientales, hídricos y climáticos",
        "contenido": (
            "Sistema de Información Ambiental de Colombia — SIAC (https://siac-datosabiertos-mads.hub.arcgis.com/, "
            "www.siac.gov.co): capas nacionales de agua, suelo, biodiversidad, cambio climático "
            "y licencias ambientales. Instituto Alexander von Humboldt — IAVH (datos.humboldt.org.co): "
            "investigación institucional y biodiversidad por municipio/departamento, áreas "
            "protegidas SINAP, parques nacionales/regionales. IDEAM (www.ideam.gov.co, "
            "visor.ideam.gov.co/geovisor): agrometeorología, amenaza ambiental, calidad del agua, "
            "clima (análisis climático, potencial energético, precipitación, temperatura y sus "
            "variaciones), demanda hídrica, escenarios de cambio climático, estado de degradación "
            "de suelos, estado de coberturas de la tierra y ecosistemas, huella e indicadores "
            "hídricos, oferta de agua superficial y subterránea, riesgo ambiental, vulnerabilidad "
            "al cambio climático y susceptibilidad ambiental. Fuente directa para cruzar patrones "
            "de lluvia/clima con estudios de amenaza del POT."
        ),
    },
    {
        "seccion": "Fuentes secundarias — Minería, energía e infraestructura",
        "titulo": "UPME, ANI, INVIAS, ANT, UPRA",
        "contenido": (
            "Unidad de Planeación Minero Energética — UPME: solicitudes y títulos mineros "
            "vigentes (annamineria.anm.gov.co), radiación/brillo solar, proyectos de "
            "transmisión, cobertura eléctrica (sig.simec.gov.co). Agencia Nacional de "
            "Infraestructura — ANI (sig.ani.gov.co): mapas de carreteras, proyectos 2G/3G/4G, "
            "aeropuertos, puertos, ferrocarriles. INVIAS (hermes2.invias.gov.co, "
            "inviasopendata-invias.opendata.arcgis.com): sistema de información vial. "
            "Agencia Nacional de Tierras — ANT y Unidad de Planificación Rural Agropecuaria — "
            "UPRA (sipra.upra.gov.co): resguardos indígenas, zonas de reserva campesina, "
            "consejos comunitarios, capas del sector agropecuario."
        ),
    },
    {
        "seccion": "Fuentes secundarias — Estadísticas nacionales y catastros municipales",
        "titulo": "DNP, DANE y catastros por municipio (incluye Barranquilla)",
        "contenido": (
            "DNP: TerriData (https://terridata.dnp.gov.co) — portal de estadísticas e "
            "indicadores por municipio; Portal Territorial (KIT OT y KIT PDD, "
            "portalterritorial.dnp.gov.co); Mapa de inversiones en regalías "
            "(maparegalias.sgr.gov.co); Proyectos Tipo (proyectostipo.dnp.gov.co). "
            "DANE: censo poblacional, estadísticas por tema, geoportal estadístico "
            "(geoportal.dane.gov.co). Corporaciones Autónomas Regionales: Planes de "
            "Ordenación y Manejo de Cuenca Hidrográfica (POMCA) y planes de manejo hídrico "
            "(instrumentos que requieren concertación con el POT). Catastros municipales "
            "propios con geoportal: Antioquia (catastroantioquia.co), Cali, "
            "**Barranquilla** (barranquilla.maps.arcgis.com/apps/webappviewer, "
            "id=0c8676d453f64fc39f60952816db523a), Bogotá (IDECA, ideca.gov.co), "
            "Medellín (geomedellin), Manizales (expediente municipal)."
        ),
    },
]


def cargar_docx_chunks(sb, norma_id: str) -> list[dict]:
    rows = []
    for f in ["rev_general", "modif_excep"]:
        path = POT_DIR / f"{f}.txt"
        if not path.exists():
            print(f"  ADVERTENCIA: {path.name} no existe, se omite")
            continue
        cleaned = _clean(path.read_text(encoding="utf-8"))
        chunks = extract_chunks(cleaned)
        print(f"  {f}.txt: {len(chunks)} chunks")
        for c in chunks:
            rows.append({
                "seccion": c["seccion_origen"] or c["chunk_id"],
                "titulo": c["titulo"][:500] or c["chunk_id"],
                "norma_ref": "Guía POT — Ministerio de Vivienda, Ciudad y Territorio (2024)",
                "contenido": c["embedding_ready"],
                "norma_id": norma_id,
                "motor": "geopot",
            })
    return rows


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "POT-MVCT-2024").execute()
    if not norma_row.data:
        raise RuntimeError("POT-MVCT-2024 no existe en normas_registro — correr la migración de vigencia primero")
    norma_id = norma_row.data[0]["id"]

    fuentes_row = sb.table("normas_registro").select("id").eq("codigo", "POT-FUENTES-SEC-2023").execute()
    if not fuentes_row.data:
        raise RuntimeError("POT-FUENTES-SEC-2023 no existe en normas_registro — correr la migración de vigencia primero")
    fuentes_id = fuentes_row.data[0]["id"]

    print("Extrayendo chunks de las 2 guías POT (docx)...")
    rows = cargar_docx_chunks(sb, norma_id)

    print("Agregando fuentes de información secundaria (Anexo 1)...")
    for f in FUENTES_SECUNDARIAS:
        rows.append({
            "seccion": f["seccion"],
            "titulo": f["titulo"],
            "norma_ref": "Fuentes de información secundaria para el ordenamiento territorial — MVCT (sept. 2023)",
            "contenido": f["contenido"],
            "norma_id": fuentes_id,
            "motor": "geopot",
        })

    print(f"\nTotal chunks POT: {len(rows)}")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando chunks POT previos (idempotente, por norma_id)...")
    for nid in (norma_id, fuentes_id):
        borrado = sb.table("motor_chunks").delete().eq("norma_id", nid).execute()
        print(f"  limpiados {len(borrado.data)} chunks previos (norma_id={nid})")

    print("Subiendo a motor_chunks...")
    for i in range(0, len(rows), 50):
        batch = rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
    print(f"OK: {len(rows)} chunks POT cargados en motor_chunks (motor='geopot')")


if __name__ == "__main__":
    main()
