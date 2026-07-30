"""
Carga el Capítulo 6 del Decreto 1072 de 2015 (Sistema de Gestión de la
Seguridad y Salud en el Trabajo — SG-SST, Libro 2 Parte 2 Título 4
Capítulo 6, artículos 2.2.4.6.1 a 2.2.4.6.42) a ntc_chunks, generando
embeddings locales (mismo modelo que el resto del proyecto:
paraphrase-multilingual-MiniLM-L12-v2, 384-dim).

Fuente: texto oficial completo del "EVA - Gestor Normativo" (Departamento
Administrativo de la Función Pública), versión integrada con
modificaciones, actualizada a marzo de 2026 — no un resumen, texto legal
verbatim (acto de gobierno colombiano de dominio público, sin restricción
de copyright, mismo criterio que RAS 2000/NSR-10 Título G/manuales
INVIAS). Extraído con PyMuPDF y limpiado de encabezados/pies de página
que se colaban en 15 de los 42 artículos en los saltos de página del PDF
(patrón "Departamento Administrativo de la Función Pública / Decreto 1072
de 2015 Sector Trabajo / <num> / EVA - Gestor Normativo" repetido en cada
página — verificado antes y después de la limpieza que ningún artículo
quedó cortado ni con residuo de ese patrón).

Gap real cerrado: SGSST no tenía ninguna fila en normas_registro ni
ntc_chunks antes de este script — confirmado por conteo real, no
supuesto. "Decreto 1072 de 2015" ya estaba registrado en el
KEYWORD_MAP de rag_multi_norma.py (routing general, no motor
específico) desde antes — este script solo carga el contenido real que
faltaba.

Uso: python scripts/ingest_decreto_1072_sgsst.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = ROOT / "packages" / "construdata" / "normativa_raw" / "sgsst" / "decreto_1072_cap6_chunks.jsonl"

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CODIGO = "DECRETO-1072-2015-CAP6-SGSST"
NOMBRE_COMPLETO = (
    "Decreto 1072 de 2015 — Decreto Único Reglamentario del Sector Trabajo, "
    "Libro 2 Parte 2 Título 4 Capítulo 6: Sistema de Gestión de la Seguridad "
    "y Salud en el Trabajo (SG-SST)"
)


def registrar_norma(sb) -> str:
    """Idempotente: si ya existe el código, reutiliza el id; si no, lo crea."""
    existente = sb.table("normas_registro").select("id").eq("codigo", CODIGO).execute()
    if existente.data:
        return existente.data[0]["id"]

    nuevo = sb.table("normas_registro").insert({
        "codigo": CODIGO,
        "nombre_completo": NOMBRE_COMPLETO,
        "entidad_emisora": "Presidencia de la República / Departamento Administrativo de la Función Pública",
        "tipo": "decreto",
        "estado_vigencia": "vigente",
        "notas_vigencia": (
            "Texto oficial completo (verbatim, no ficha técnica) de los 42 artículos del "
            "Capítulo 6, extraído de la versión integrada del Gestor Normativo (Función "
            "Pública), actualizada a 12 de marzo de 2026. Fuente: acto de gobierno de dominio "
            "público, sin restricción de copyright (a diferencia de ISO/NTC comerciales, que "
            "sí se cargan como ficha técnica). El decreto completo (335 páginas, todo el "
            "sector Trabajo) no se cargó completo — solo el capítulo SGSST, que es el alcance "
            "relevante para StructAI/motor-gerencia (trazabilidad de obra) y para el trabajo "
            "de grado del usuario."
        ),
    }).execute()
    return nuevo.data[0]["id"]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_id = registrar_norma(sb)
    print(f"normas_registro OK — {CODIGO} → {norma_id}")

    chunks = [json.loads(line) for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Total artículos Capítulo 6 SGSST: {len(chunks)}")

    all_rows = []
    for c in chunks:
        all_rows.append({
            "norma": "Decreto 1072 de 2015",
            "seccion": c["seccion"],
            "titulo": c["titulo"],
            "contenido": c["contenido"],
            "norma_id": norma_id,
        })

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for row, vec in zip(all_rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando chunks previos del Decreto 1072 Cap. 6 (idempotente, por norma_id)...")
    borrado = sb.table("ntc_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a ntc_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("ntc_chunks").insert(batch).execute()
        print(f"  {min(i + 50, len(all_rows))}/{len(all_rows)}")
    print(f"OK: {len(all_rows)} artículos del Decreto 1072 Cap. 6 (SGSST) cargados en ntc_chunks")


if __name__ == "__main__":
    main()
