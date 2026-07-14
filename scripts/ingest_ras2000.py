"""
Carga el corpus RAS 2000 (Títulos A-H, texto oficial real extraído de
Drive) a Supabase (motor_chunks, motor='aquai'), generando embeddings
locales. Reemplaza los 13 chunks de AquAI redactados a mano en
ingest_motor_chunks.py con 303 chunks reales extraídos artículo por
artículo (Título A, la resolución legal) o sección por sección (Títulos
B-H, los anexos técnicos, formato "X.N.N") — mismo nivel de trazabilidad
que ya tiene el corpus de NSR-10/NTC/SGSST.

Reutiliza el extractor por regex de ingest_normativa.py (extract_chunks):
los archivos fuente de packages/construdata/normativa_raw/ras2000/ traen
la misma estructura chunk_id/seccion_origen/titulo/embedding_ready que
NSR-10 — generada por scripts/extract_ras2000.py a partir del texto
oficial descargado de Drive (Resolución 1096 de 2000 / OAS), no inventada.

Uso: python scripts/ingest_ras2000.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "ras2000"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_normativa import _clean, extract_chunks  # reutiliza el extractor ya probado

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

TITULOS = {
    "a": "Título A — Condiciones Generales (Resolución 1096 de 2000)",
    "b": "Título B — Sistemas de Acueducto",
    "c": "Título C — Sistemas de Potabilización",
    "d": "Título D — Sistemas de Recolección y Evacuación de Aguas Residuales y Pluviales",
    "e": "Título E — Tratamiento de Aguas Residuales",
    "f": "Título F — Sistemas de Aseo Urbano",
    "g": "Título G — Aspectos Complementarios",
    "h": "Título H — Compendio Normativo",
}


def parse_titulo_file(path: Path, norma_label: str) -> list[dict]:
    cleaned = _clean(path.read_text(encoding="utf-8"))
    rows = []
    for chunk in extract_chunks(cleaned):
        rows.append({
            "seccion": chunk["seccion_origen"] or chunk["chunk_id"],
            "titulo": chunk["titulo"][:500] or chunk["chunk_id"],
            "norma_ref": f"RAS 2000 {norma_label}",
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
    for letra, norma_label in TITULOS.items():
        path = RAW_DIR / f"titulo_{letra}.txt"
        if not path.exists():
            print(f"  ADVERTENCIA: {path.name} no existe, se omite")
            continue
        rows = parse_titulo_file(path, norma_label)
        print(f"  {path.name}: {len(rows)} chunks ({norma_label})")
        all_rows.extend(rows)

    print(f"\nTotal RAS 2000: {len(all_rows)} chunks")
    if not all_rows:
        print("Nada que cargar.")
        return

    print("\nGenerando embeddings...")
    textos = [f"{r['titulo']}. {r['contenido']}" for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
    for row, vec in zip(all_rows, vectores):
        row["embedding"] = vec.tolist()
        row["motor"] = "aquai"

    print("\nBorrando chunks previos de AquAI en motor_chunks (reemplaza los 13 redactados a mano)...")
    borrado = sb.table("motor_chunks").delete().eq("motor", "aquai").execute()
    print(f"  limpiados {len(borrado.data)} chunks previos")

    print("Subiendo a motor_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("motor_chunks").insert(batch).execute()
    print(f"OK: {len(all_rows)} chunks RAS 2000 cargados en motor_chunks (motor='aquai')")


if __name__ == "__main__":
    main()
