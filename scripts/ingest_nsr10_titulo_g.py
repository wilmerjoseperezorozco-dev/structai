"""
Carga el Título G real de NSR-10 (Estructuras de Madera y Estructuras de
Guadua) a nsr10_chunks, generando embeddings locales (mismo modelo que el
resto del proyecto: paraphrase-multilingual-MiniLM-L12-v2, 384-dim).

Gap real cerrado: Título G nunca había sido cargado. Vinculado a
normas_registro (NSR10-TITULO-G) via norma_id — a diferencia de los demás
Títulos A-J ya existentes, que siguen con norma_id NULL (esa reauditoría
queda para otra sesión, ver notas_vigencia de NSR10-TITULO-G).

Uso: python scripts/ingest_nsr10_titulo_g.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = ROOT / "packages" / "construdata" / "normativa_raw" / "nsr10" / "titulo_g_chunks.jsonl"

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CODIGO = "NSR10-TITULO-G"


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    row = sb.table("normas_registro").select("id").eq("codigo", CODIGO).execute()
    if not row.data:
        raise RuntimeError(f"{CODIGO} no existe en normas_registro — registrarlo primero")
    norma_id = row.data[0]["id"]

    chunks = [json.loads(line) for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Total chunks Título G: {len(chunks)}")

    all_rows = []
    for c in chunks:
        all_rows.append({
            "id": c["id"],
            "capitulo": c["capitulo"],
            "seccion": c["seccion"],
            "titulo": c["titulo"][:500],
            "texto": c["texto"],
            "norma_id": norma_id,
        })

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['texto']}" for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for row_, vec in zip(all_rows, vectores):
        row_["embedding"] = vec.tolist()

    print("Borrando chunks previos del Título G (idempotente, por norma_id)...")
    borrado = sb.table("nsr10_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a nsr10_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("nsr10_chunks").upsert(batch, on_conflict="id").execute()
        print(f"  {min(i + 50, len(all_rows))}/{len(all_rows)}")
    print(f"OK: {len(all_rows)} chunks del Título G cargados en nsr10_chunks")


if __name__ == "__main__":
    main()
