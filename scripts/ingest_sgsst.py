"""
Carga el corpus SGSST (Seguridad y Salud en el Trabajo) desde
packages/construdata/normativa_raw/sgsst/ a Supabase (ntc_chunks — mismo
lugar donde ya viven NSR-10/NTC, para que el RAG general los recupere juntos
en una sola consulta), generando embeddings locales.

Reutiliza el extractor por regex de ingest_normativa.py (extract_chunks):
los archivos fuente de esta carpeta traen la misma estructura chunk_id/
seccion_origen/titulo/embedding_ready que los de NSR-10, extraída
directamente de Google Drive (carpeta SGSST) con el formato "RAG+CAG" que
ya se usó para el resto del corpus normativo — no se inventa contenido, se
reutiliza el mismo pipeline de extracción ya probado.

Uso: python scripts/ingest_sgsst.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "sgsst"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_normativa import _clean, extract_chunks  # reutiliza el extractor ya probado

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

# norma -> archivo fuente (un archivo = una norma completa, igual que NSR-10)
SGSST_FILES = {
    "decreto_1072_2015.txt": "Decreto 1072 de 2015",
    "resolucion_0312_2019.txt": "Resolución 0312 de 2019",
    "ley_1562_2012.txt": "Ley 1562 de 2012",
}


def parse_sgsst_file(path: Path, norma: str) -> list[dict]:
    cleaned = _clean(path.read_text(encoding="utf-8"))
    rows = []
    for chunk in extract_chunks(cleaned):
        rows.append({
            "norma": norma,
            "seccion": chunk["seccion_origen"],
            "titulo": chunk["titulo"][:500],
            "contenido": chunk["embedding_ready"],
        })
    return rows


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    all_rows: list[dict] = []
    for filename, norma in SGSST_FILES.items():
        path = RAW_DIR / filename
        rows = parse_sgsst_file(path, norma)
        print(f"  {filename}: {len(rows)} chunks ({norma})")
        all_rows.extend(rows)

    print(f"\nTotal SGSST: {len(all_rows)} chunks")
    if not all_rows:
        print("Nada que cargar.")
        return

    print("\nGenerando embeddings...")
    textos = [r["contenido"] for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(all_rows, vectores):
        row["embedding"] = vec.tolist()

    print("Borrando contenido SGSST previo de ntc_chunks (idempotencia)...")
    normas_nuevas = list({r["norma"] for r in all_rows})
    for norma in normas_nuevas:
        sb.table("ntc_chunks").delete().eq("norma", norma).execute()

    print("Subiendo a ntc_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("ntc_chunks").insert(batch).execute()
    print(f"OK: {len(all_rows)} chunks SGSST cargados")


if __name__ == "__main__":
    main()
