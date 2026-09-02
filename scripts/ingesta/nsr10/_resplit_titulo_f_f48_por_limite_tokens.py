"""
Re-trocea los chunks de F.4.8 (ya transcritos verbatim en
_ingest_titulo_f_f48_verbatim.py) en piezas mas chicas -- CON
verificacion real de tokens (metodo de F.4.6/F.4.7, el unico
confiable, ver hallazgo de auditoria en F.4.3/F.4.4/F.4.5 y el resto
del corpus, memoria privada del usuario).

No relee el PDF: reusa el texto verbatim ya transcrito.

Uso: python _resplit_titulo_f_f48_por_limite_tokens.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _ingest_titulo_f_f48_verbatim import CHUNKS as PARENT_CHUNKS, CAPITULO
from _resplit_titulo_f_f42_por_limite_tokens import split_texto
from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

LIMITE_TOKENS_REAL = 128


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    child_chunks = []
    for parent in PARENT_CHUNKS:
        piezas_por_chars = split_texto(parent["texto"])
        piezas_finales: list[str] = []
        for pieza in piezas_por_chars:
            piezas_finales.extend(_sub_particionar_por_tokens_reales(pieza, tokenizer))
        for i, pieza in enumerate(piezas_finales, start=1):
            child_chunks.append({
                "id": f"{parent['id']}_p{i}",
                "seccion": parent["seccion"],
                "titulo": parent["titulo"],
                "texto": pieza,
            })

    print(f"Chunks padre: {len(PARENT_CHUNKS)} -> piezas chicas: {len(child_chunks)}")

    over_limit = []
    for c in child_chunks:
        n = len(tokenizer.encode(c["texto"], add_special_tokens=True))
        if n > LIMITE_TOKENS_REAL:
            over_limit.append((c["id"], n))
    print(f"Piezas todavia sobre {LIMITE_TOKENS_REAL} tokens REALES: {len(over_limit)}")
    for cid, n in over_limit:
        print(f"  ! {cid}: {n} tokens reales")
    if over_limit:
        raise SystemExit("Hay piezas sobre el limite real -- no subir a produccion sin resolver.")

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
    print(f"\nBorrando los {len(parent_ids)} chunks-padre sobredimensionados...")
    sb.table("nsr10_chunks").delete().in_("id", parent_ids).execute()

    print(f"\nOK: {len(rows)} chunks chicos de F.4.8 cargados, {len(parent_ids)} chunks-padre borrados.")


if __name__ == "__main__":
    main()
