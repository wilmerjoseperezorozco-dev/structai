"""
Carga el corpus de la Resolución 0330 de 2017 (texto vigente, reemplaza RAS
2000 / Resolución 1096 de 2000) a Supabase (motor_chunks, motor='aquai'),
generando embeddings locales. Se suma a los 303 chunks de RAS 2000 ya
cargados (no los reemplaza) — RAS 2000 queda como referencia histórica,
correctamente marcada 'derogada_total' en normas_registro; estos 255 chunks
nuevos quedan vinculados a la fila 'vigente' de la misma tabla, así el RAG
prioriza y no advierte sobre el contenido correcto.

Uso: python scripts/ingest_res0330.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "packages" / "construdata" / "normativa_raw" / "res0330" / "res0330.txt"

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

    norma_row = sb.table("normas_registro").select("id").eq("codigo", "RES-0330-2017").execute()
    if not norma_row.data:
        raise RuntimeError("RES-0330-2017 no existe en normas_registro — correr la migración de vigencia primero")
    norma_id = norma_row.data[0]["id"]

    cleaned = _clean(RAW_PATH.read_text(encoding="utf-8"))
    chunks = extract_chunks(cleaned)
    print(f"Chunks parseados de res0330.txt: {len(chunks)}")

    rows = [{
        "seccion": c["seccion_origen"] or c["chunk_id"],
        "titulo": c["titulo"][:500] or c["chunk_id"],
        "norma_ref": "Resolución 0330 de 2017",
        "contenido": c["embedding_ready"],
        "norma_id": norma_id,
        "motor": "aquai",
    } for c in chunks]

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando chunks previos de Resolución 0330/2017 (idempotente, por norma_id)...")
    borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a motor_chunks...")
    for i in range(0, len(rows), 50):
        batch = rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
    print(f"OK: {len(rows)} chunks de Resolución 0330/2017 cargados en motor_chunks (motor='aquai', norma_id={norma_id})")


if __name__ == "__main__":
    main()
