"""
Script para cargar los PDFs NSR-10 (Títulos A-K) a Supabase pgvector.
Uso: python scripts/load_nsr10.py

Requiere:
  - SUPABASE_URL y SUPABASE_SERVICE_KEY en .env
  - OPENAI_API_KEY para embeddings
  - pypdf, openai, supabase-py instalados

Los PDFs están en: packages/knowledge/nsr10/
Formato esperado: RAG+CAG Capitulo X.pdf
"""

import os
import json
import pathlib
import re
import time

ROOT = pathlib.Path(__file__).parent.parent

NSR10_DIR = ROOT / "packages" / "knowledge" / "nsr10"

TITULOS = {
    "A": "Requisitos Generales de Diseño y Construcción Sismo Resistente",
    "B": "Cargas",
    "C": "Concreto Estructural",
    "D": "Mampostería Estructural",
    "E": "Casas de 1 y 2 Pisos",
    "F": "Estructuras Metálicas",
    "G": "Estructuras de Madera y Guadua",
    "H": "Estudios Geotécnicos",
    "I": "Supervisión Técnica",
    "J": "Requisitos de Protección contra Incendio",
    "K": "Requisitos Complementarios",
}

CHUNK_SIZE   = 800   # tokens aproximados por chunk
CHUNK_OVERLAP = 100  # overlap entre chunks


def extract_pdf_text(pdf_path: pathlib.Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages:
            t = page.extract_text() or ""
            text += t + "\n"
        return text
    except ImportError:
        print("  [!] pypdf no instalado. Instala con: pip install pypdf")
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 50]


def get_embeddings(texts: list[str], api_key: str) -> list[list[float]]:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    embeddings = []
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,
        )
        embeddings.extend([e.embedding for e in response.data])
        time.sleep(0.2)
    return embeddings


def detect_seccion(chunk: str, titulo: str) -> str:
    match = re.search(r'(?:NSR-10|Artículo|Art\.|Sección)\s+([A-K][\.\d]+)', chunk)
    if match:
        return match.group(1)
    return f"{titulo}.x"


def load_nsr10(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    openai_key   = os.environ.get("OPENAI_API_KEY", "")

    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    sb = create_client(supabase_url, supabase_key)

    pdfs = sorted(NSR10_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron PDFs en {NSR10_DIR}")
        return

    print(f"Encontrados {len(pdfs)} PDFs NSR-10\n")

    total_chunks = 0

    for pdf in pdfs:
        # Detectar letra del título del nombre de archivo
        m = re.search(r'Capitulo?\s+([A-K])', pdf.name, re.IGNORECASE)
        if not m:
            print(f"  [skip] No se pudo detectar título en: {pdf.name}")
            continue

        titulo = m.group(1).upper()
        norma  = f"NSR-10 Título {titulo}"
        nombre = TITULOS.get(titulo, f"Título {titulo}")

        print(f"  Procesando {norma} — {nombre}")

        text = extract_pdf_text(pdf)
        if not text:
            print(f"    [!] Sin texto extraído")
            continue

        chunks = chunk_text(text)
        print(f"    {len(chunks)} chunks generados")

        if dry_run:
            print(f"    [dry-run] Saltando carga a Supabase")
            total_chunks += len(chunks)
            continue

        embeddings = get_embeddings(chunks, openai_key)

        # Columnas reales de public.nsr10_chunks: id (PK, sin default), capitulo,
        # seccion, titulo, texto, embedding — NO norma/contenido/chunk_idx, que
        # es lo que este script escribía antes (fallaba en el primer upsert).
        rows = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            seccion = detect_seccion(chunk, titulo)
            rows.append({
                "id":        f"NSR10-{titulo}-{i:04d}",
                "capitulo":  titulo,
                "titulo":    nombre,
                "seccion":   seccion,
                "texto":     chunk,
                "embedding": emb,
            })

        sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
        print(f"    OK: {len(rows)} chunks cargados a Supabase")
        total_chunks += len(rows)
        time.sleep(0.5)

    print(f"\nTotal chunks cargados: {total_chunks}")
    print("NSR-10 lista para RAG.")


if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv
    load_nsr10(dry_run=dry)
