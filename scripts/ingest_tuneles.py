"""
Carga el Manual de Túneles de Carretera para Colombia (Edición 2021) a
motor_chunks (motor='vias'), generando embeddings locales. Módulo nuevo
para motor-vias -- Túneles nunca se había portado (el "documento masivo"
original solo cubría diseño geométrico/pavimentos/mantenimiento/topografía/
NTC materiales).

Uso: python scripts/ingest_tuneles.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "packages" / "construdata" / "normativa_raw" / "tuneles" / "tuneles.txt"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_normativa import _clean, extract_chunks

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "MAN-TUNELES-2021").execute()
    if not norma_row.data:
        raise RuntimeError("MAN-TUNELES-2021 no existe en normas_registro — correr la migración de vigencia primero")
    norma_id = norma_row.data[0]["id"]

    cleaned = _clean(RAW_PATH.read_text(encoding="utf-8"))
    chunks = extract_chunks(cleaned)
    print(f"Chunks parseados de tuneles.txt: {len(chunks)}")

    rows = [{
        "seccion": c["seccion_origen"] or c["chunk_id"],
        "titulo": c["titulo"][:500] or c["chunk_id"],
        "norma_ref": "Manual de Túneles de Carretera para Colombia (Edición 2021, INVIAS)",
        "contenido": c["embedding_ready"],
        "norma_id": norma_id,
        "motor": "vias",
    } for c in chunks]

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando chunks previos de Túneles (idempotente, por norma_id)...")
    borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a motor_chunks...")
    for i in range(0, len(rows), 50):
        batch = rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
    print(f"OK: {len(rows)} chunks de Túneles cargados en motor_chunks (motor='vias')")


if __name__ == "__main__":
    main()
