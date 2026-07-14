"""
Carga el Manual de Interventoría de Obra Pública 2022 (INVIAS) a
motor_chunks (motor='gerencia'), generando embeddings locales. Complemento
procedimental/técnico de las 3 leyes de contratación pública ya cargadas
(Ley 80/1150/1474) — ver scripts/ingest_leyes_gerencia.py.

Uso: python scripts/ingest_interventoria.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "packages" / "construdata" / "normativa_raw" / "gerencia_leyes" / "manual_interventoria_2022.txt"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_normativa import _clean, extract_chunks

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CODIGO = "MAN-INTERVENTORIA-2022"
NORMA_LABEL = "Manual de Interventoría de Obra Pública 2022 (INVIAS, MEPI-MN1 v1)"


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

    cleaned = _clean(RAW_PATH.read_text(encoding="utf-8"))
    chunks = extract_chunks(cleaned)
    print(f"  manual_interventoria_2022.txt: {len(chunks)} chunks")

    all_rows = []
    for c in chunks:
        all_rows.append({
            "seccion": c["seccion_origen"] or c["chunk_id"],
            "titulo": c["titulo"][:500] or c["chunk_id"],
            "norma_ref": NORMA_LABEL,
            "contenido": c["embedding_ready"],
            "norma_id": norma_id,
            "motor": "gerencia",
        })

    print(f"\nTotal chunks Manual de Interventoría: {len(all_rows)}")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for row_, vec in zip(all_rows, vectores):
        row_["embedding"] = vec.tolist()

    print("Borrando chunks previos del Manual de Interventoría (idempotente, por norma_id)...")
    borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a motor_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
        print(f"  {min(i + 50, len(all_rows))}/{len(all_rows)}")
    print(f"OK: {len(all_rows)} chunks del Manual de Interventoría cargados en motor_chunks (motor='gerencia')")


if __name__ == "__main__":
    main()
