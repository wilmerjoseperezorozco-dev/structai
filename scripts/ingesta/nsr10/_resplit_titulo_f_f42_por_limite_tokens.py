"""
Re-trocea los 6 chunks de F.4.2 (ya transcritos verbatim en
_ingest_titulo_f_f42_verbatim.py) en piezas mas chicas -- hallazgo real
2026-09-01: el modelo de embeddings (paraphrase-multilingual-MiniLM-
L12-v2) trunca a 128 tokens (confirmado con `model.max_seq_length`).
Los 6 chunks originales median 614-1386 tokens estimados -- el modelo
solo "veia" el arranque de cada uno, el resto quedaba invisible para
el retrieval semantico (confirmado con una prueba de retrieval real
que no traia el chunk correcto ni en el top-40 para una pregunta cuya
respuesta esta verbatim en el texto). Mismo bug ya documentado como
deuda tecnica pendiente en la memoria del proyecto desde 2026-08-03
(chunk de 38.301 chars en Titulo G) -- esta vez se corrige en el
momento en vez de dejarlo pendiente otra vez.

No relee el PDF: reusa el texto verbatim ya transcrito, solo lo
particiona en piezas de ~450 caracteres (~100 tokens, con margen)
respetando saltos de parrafo/oracion para no partir formulas a la
mitad cuando es evitable. Borra los 6 chunks-padre sobredimensionados
y los reemplaza por las piezas chicas.

Uso: python _resplit_titulo_f_f42_por_limite_tokens.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _ingest_titulo_f_f42_verbatim import CHUNKS as PARENT_CHUNKS, CAPITULO

TARGET_CHARS = 450  # ~100 tokens en espanol tecnico, deja margen bajo el limite real de 128


def split_texto(texto: str, target: int = TARGET_CHARS) -> list[str]:
    """Parte por parrafos (\\n\\n) primero; si un parrafo sigue largo, por
    oraciones (". "); si una oracion sola sigue larga (formula extensa),
    se deja entera -- preferible un chunk un poco mas largo que cortar
    una ecuacion a la mitad."""
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    piezas: list[str] = []
    actual = ""
    for p in parrafos:
        if len(p) <= target:
            candidato = (actual + "\n\n" + p).strip() if actual else p
            if len(candidato) <= target * 1.3:
                actual = candidato
                continue
            else:
                if actual:
                    piezas.append(actual)
                actual = p
                continue
        # parrafo largo: particionar por oraciones
        if actual:
            piezas.append(actual)
            actual = ""
        oraciones = re.split(r"(?<=[.:])\s+(?=[A-ZÁÉÍÓÚÑ0-9])", p)
        buf = ""
        for o in oraciones:
            cand = (buf + " " + o).strip() if buf else o
            if len(cand) <= target * 1.3:
                buf = cand
            else:
                if buf:
                    piezas.append(buf)
                buf = o
        if buf:
            piezas.append(buf)
    if actual:
        piezas.append(actual)
    return piezas


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    child_chunks = []
    for parent in PARENT_CHUNKS:
        piezas = split_texto(parent["texto"])
        for i, pieza in enumerate(piezas, start=1):
            child_chunks.append({
                "id": f"{parent['id']}_p{i}",
                "seccion": parent["seccion"],
                "titulo": parent["titulo"],
                "texto": pieza,
            })

    print(f"Chunks padre: {len(PARENT_CHUNKS)} -> piezas chicas: {len(child_chunks)}")
    for c in child_chunks:
        print(f"  {c['id']}: {len(c['texto'])} chars (~{round(len(c['texto'])/4.5)} tokens est.)")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in child_chunks]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(child_chunks, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo piezas chicas a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    parent_ids = [p["id"] for p in PARENT_CHUNKS]
    print(f"\nBorrando los {len(parent_ids)} chunks-padre sobredimensionados (superados por las piezas chicas)...")
    sb.table("nsr10_chunks").delete().in_("id", parent_ids).execute()

    print(f"\nOK: {len(rows)} chunks chicos de F.4.2 cargados, {len(parent_ids)} chunks-padre borrados.")


if __name__ == "__main__":
    main()
