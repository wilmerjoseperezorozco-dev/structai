"""
Carga las 3 leyes colombianas de contratación pública (Ley 80/1993, Ley
1150/2007, Ley 1474/2011) a motor_chunks (motor='gerencia'), generando
embeddings locales. Le da a motor-gerencia base legal colombiana real,
más allá del PMBOK/EVM genérico que ya tenía.

Uso: python scripts/ingest_leyes_gerencia.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
LEYES_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "gerencia_leyes"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_normativa import _clean, extract_chunks

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

LEYES = {
    "ley80_1993": ("LEY-80-1993", "Ley 80 de 1993"),
    "ley1150_2007": ("LEY-1150-2007", "Ley 1150 de 2007"),
    "ley1474_2011": ("LEY-1474-2011", "Ley 1474 de 2011"),
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    norma_ids = {}
    for doc_code, (codigo, _) in LEYES.items():
        row = sb.table("normas_registro").select("id").eq("codigo", codigo).execute()
        if not row.data:
            raise RuntimeError(f"{codigo} no existe en normas_registro — correr la migración de vigencia primero")
        norma_ids[doc_code] = row.data[0]["id"]

    all_rows = []
    for doc_code, (codigo, norma_label) in LEYES.items():
        path = LEYES_DIR / f"{doc_code}.txt"
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
                "motor": "gerencia",
            })

    print(f"\nTotal chunks leyes de gerencia: {len(all_rows)}")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    print("Generando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for row, vec in zip(all_rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando chunks previos de leyes de gerencia (idempotente, por norma_id)...")
    for doc_code, norma_id in norma_ids.items():
        borrado = sb.table("motor_chunks").delete().eq("norma_id", norma_id).execute()
        print(f"  limpiados {len(borrado.data)} chunks previos ({doc_code})")

    print("Subiendo a motor_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
        print(f"  {min(i + 50, len(all_rows))}/{len(all_rows)}")
    print(f"OK: {len(all_rows)} chunks de leyes de gerencia cargados en motor_chunks (motor='gerencia')")


if __name__ == "__main__":
    main()
