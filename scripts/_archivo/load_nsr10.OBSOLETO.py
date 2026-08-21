"""
Script para cargar los PDFs NSR-10 (Títulos A-K) a Supabase pgvector.
Uso: python scripts/load_nsr10.py [--dry-run] [--titulos D,H,I]

Requiere:
  - SUPABASE_URL y SUPABASE_SERVICE_KEY en .env
  - sentence-transformers instalado (embeddings locales, sin costo — NO usa
    OpenAI. Corregido 2026-08-03: la versión original generaba embeddings de
    1536 dim con text-embedding-3-small, pero nsr10_chunks.embedding es
    vector(384) — el tamaño real de paraphrase-multilingual-MiniLM-L12-v2,
    el mismo modelo que usa rag_multi_norma.py para las consultas. Mezclar
    espacios de embedding distintos habría roto la similitud coseno para
    cualquier chunk cargado con este script.)
  - pypdf, supabase-py instalados

Los PDFs están en: packages/knowledge/nsr10/
Formato esperado: RAG+CAG Capitulo X.pdf

Por defecto SOLO procesa D, H, I: son los únicos títulos sin ningún trabajo
de curación real en curso (verificado contra Supabase el 2026-08-03 — A, B,
E, G, J, K ya tienen contenido sustancial; C, F tienen núcleos verbatim
insertados a mano en sesiones previas). Correr esto sobre C/E/F metería
contenido automático sin curar encima de contenido ya verificado a mano.
Pasa --titulos para procesar otro subconjunto explícitamente.
"""

import os
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

TITULOS_DEFAULT = {"D", "H", "I"}

CHUNK_SIZE   = 800   # palabras aproximadas por chunk
CHUNK_OVERLAP = 100  # overlap entre chunks

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # 384-dim, debe calzar con nsr10_chunks.embedding vector(384)


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


def get_embeddings(texts: list[str]) -> list[list[float]]:
    # HF_HUB_OFFLINE evita que sentence-transformers intente contactar HF Hub
    # para revisar actualizaciones (puede colgarse por rate-limit sin token) —
    # mismo fix ya aplicado en rag_multi_norma.py.
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()


def detect_seccion(chunk: str, titulo: str) -> str:
    match = re.search(r'(?:NSR-10|Artículo|Art\.|Sección)\s+([A-K][\.\d]+)', chunk)
    if match:
        return match.group(1)
    return f"{titulo}.x"


def load_nsr10(dry_run: bool = False, titulos_a_procesar: set[str] = None):
    from supabase import create_client

    titulos_a_procesar = titulos_a_procesar or TITULOS_DEFAULT

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    sb = create_client(supabase_url, supabase_key)

    pdfs = sorted(NSR10_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron PDFs en {NSR10_DIR}")
        return

    print(f"Encontrados {len(pdfs)} PDFs NSR-10 — procesando solo: {sorted(titulos_a_procesar)}\n")

    total_chunks = 0

    for pdf in pdfs:
        # Detectar letra del título del nombre de archivo. \s* (no \s+): el
        # PDF de Título H se llama "RAG+CAGcapituloH.pdf", sin ningún espacio
        # -- con \s+ nunca matcheaba. \b evita que la letra capturada sea el
        # inicio de otra palabra (ej. "capituloAlgo").
        m = re.search(r'Capitulo?\s*([A-K])\b', pdf.name, re.IGNORECASE)
        if not m:
            print(f"  [skip] No se pudo detectar título en: {pdf.name}")
            continue

        titulo = m.group(1).upper()
        if titulo not in titulos_a_procesar:
            print(f"  [skip] Título {titulo} no está en el subconjunto a procesar")
            continue

        nombre = TITULOS.get(titulo, f"Título {titulo}")
        # Capitulo con sufijo explícito: distingue este contenido (troceo
        # mecánico automático del PDF, sin curar) del contenido verbatim
        # insertado a mano para otros títulos -- mismo patrón ya usado para
        # marcar el contenido pendiente de reauditoría del Título F.
        capitulo_label = f"NSR-10 Título {titulo} — {nombre} (extracción automática del PDF oficial, sin curar — pendiente reauditoría)"

        print(f"  Procesando NSR-10 Título {titulo} — {nombre}")

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

        embeddings = get_embeddings(chunks)

        # Columnas reales de public.nsr10_chunks: id (PK, sin default), capitulo,
        # seccion, titulo, texto, embedding — NO norma/contenido/chunk_idx, que
        # es lo que este script escribía antes (fallaba en el primer upsert).
        # id con prefijo NSR10- (distinto del esquema {titulo}-SEC*/{titulo}-TAB*
        # usado en la curación manual) -- evita colisión de upsert.
        rows = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            seccion = detect_seccion(chunk, titulo)
            rows.append({
                "id":        f"NSR10-{titulo}-{i:04d}",
                "capitulo":  capitulo_label,
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
