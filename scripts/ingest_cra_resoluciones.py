"""
Carga las Resoluciones CRA reales a motor_chunks (motor='aquai'), generando
embeddings locales.

Uso: python scripts/ingest_cra_resoluciones.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CRA_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "cra"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_normativa import _clean, extract_chunks

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

RESOLUCIONES = {
    "res_cra_955_2021": ("RES-CRA-955-2021", "Resolución CRA 955 de 2021"),
    "res_cra_956_2021": ("RES-CRA-956-2021", "Resolución CRA 956 de 2021"),
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_ids = {}
    for doc_code, (codigo, _) in RESOLUCIONES.items():
        row = sb.table("normas_registro").select("id").eq("codigo", codigo).execute()
        if not row.data:
            raise RuntimeError(f"{codigo} no existe en normas_registro — registrarlo primero")
        norma_ids[doc_code] = row.data[0]["id"]

    all_rows = []
    for doc_code, (codigo, norma_label) in RESOLUCIONES.items():
        path = CRA_DIR / f"{doc_code}.txt"
        if not path.exists():
            print(f"  ADVERTENCIA: {path.name} no existe, se omite")
            continue
        cleaned = _clean(path.read_text(encoding="utf-8"))
        chunks = extract_chunks(cleaned)
        print(f"  {doc_code}.txt: {len(chunks)} chunks")
        for c in chunks:
            all_rows.append({
                "seccion": c["seccion_origen"] or c["chunk_id"],
                "titulo": c["titulo"][:500] or c["chunk_id"],
                "norma_ref": norma_label,
                "contenido": c["embedding_ready"],
                "norma_id": norma_ids[doc_code],
                "motor": "aquai",
            })

    print(f"\nTotal chunks Resoluciones CRA: {len(all_rows)}")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for row_, vec in zip(all_rows, vectores):
        row_["embedding"] = vec.tolist()

    print("Borrando chunks previos (idempotente, por norma_id)...")
    for doc_code, norma_id in norma_ids.items():
        borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
        print(f"  limpiados {len(borrado.data)} chunks previos ({doc_code})")

    print("Subiendo a motor_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
        print(f"  {min(i + 50, len(all_rows))}/{len(all_rows)}")
    print(f"OK: {len(all_rows)} chunks de Resoluciones CRA cargados en motor_chunks (motor='aquai')")


if __name__ == "__main__":
    main()
