"""
Carga el corpus normativo (NSR-10 + NTC) desde packages/construdata/normativa_raw/
a Supabase (nsr10_chunks / ntc_chunks), generando embeddings locales.

Los archivos fuente no son JSON válido de forma confiable: pasaron por un
formateador que escapó con backslash caracteres markdown (_ [ ] * ~ ` & ...),
y el campo `contenido_latex` de cada chunk tiene LaTeX con su propio escapado
anidado (LaTeX → JSON → markdown) que rompe cualquier parser JSON estricto o
relajado. Como el único campo que de verdad usamos es `embedding_ready`
(prosa limpia, ya pensada para este uso, sin LaTeX), extraemos los chunks
por regex directamente en vez de exigir que el documento entero sea JSON
válido — es inmune al desorden de contenido_latex.

Uso: python scripts/ingest_normativa.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "packages" / "construdata" / "normativa_raw"

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

# JSON solo reconoce \" \\ \/ \b \f \n \r \t \uXXXX como escapes válidos. Cualquier
# `\X` con X fuera de ese set es un escape de markdown mal puesto (el formateador
# fuente escapó _ [ ] * ~ ` & # + - . ! ( ) para que no se leyeran como markdown).
_INVALID_ESCAPE = re.compile(r'\\(?!["\\/bfnrtu])')


def _clean(text: str) -> str:
    return _INVALID_ESCAPE.sub("", text)


def _field(name: str) -> re.Pattern:
    return re.compile(rf'"{name}"\s*:\s*"((?:[^"\\]|\\.)*)"')


_CHUNK_ID = _field("chunk_id")
_SECCION = _field("seccion_origen")
_TITULO = _field("titulo")
_EMBEDDING_READY = _field("embedding_ready")
_TITULO_COMPLETO = _field("titulo_completo")
_NORMA = _field("norma")


def _unescape_value(v: str) -> str:
    return v.replace('\\"', '"').replace("\\\\", "\\")


def extract_chunks(cleaned: str) -> list[dict]:
    """Extrae registros chunk_id/seccion_origen/titulo/embedding_ready por regex,
    tolerando que el resto del documento no sea JSON válido."""
    id_matches = list(_CHUNK_ID.finditer(cleaned))
    chunks = []
    for i, m in enumerate(id_matches):
        start = m.start()
        end = id_matches[i + 1].start() if i + 1 < len(id_matches) else len(cleaned)
        block = cleaned[start:end]
        embed_m = _EMBEDDING_READY.search(block)
        if not embed_m:
            continue
        seccion_m = _SECCION.search(block)
        titulo_m = _TITULO.search(block)
        chunks.append({
            "chunk_id": _unescape_value(m.group(1)),
            "seccion_origen": _unescape_value(seccion_m.group(1)) if seccion_m else "",
            "titulo": _unescape_value(titulo_m.group(1)) if titulo_m else "",
            "embedding_ready": _unescape_value(embed_m.group(1)),
        })
    return chunks


NSR10_TITULOS = {
    "capitulo_a": "A", "capitulo_b": "B", "capitulo_c": "C", "capitulo_d": "D",
    "capitulo_e": "E", "capitulo_f": "F", "capitulo_h": "H", "capitulo_i": "I",
    "capitulo_j": "J", "capitulo_k": "K",
}


def parse_nsr10_file(path: Path) -> list[dict]:
    cleaned = _clean(path.read_text(encoding="utf-8"))
    letra = NSR10_TITULOS.get(path.stem, path.stem.upper())
    titulo_m = _TITULO_COMPLETO.search(cleaned)
    titulo_completo = _unescape_value(titulo_m.group(1)) if titulo_m else ""
    norma_label = f"NSR-10 Título {letra} — {titulo_completo}".rstrip(" —")

    rows = []
    for chunk in extract_chunks(cleaned):
        rows.append({
            "id": chunk["chunk_id"] or f"{path.stem}-{len(rows)}",
            "capitulo": norma_label,
            "seccion": chunk["seccion_origen"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["embedding_ready"],
        })
    return rows


# Los .txt de NTC son un array plano de objetos {id, capitulo, norma, titulo,
# contenido, ...} — formato distinto y más simple que el de NSR-10 (sin LaTeX).
_NTC_ID = _field("id")
_NTC_CAPITULO = re.compile(r'"capitulo"\s*:\s*"?(\d+)"?')
_NTC_CONTENIDO = _field("contenido")


def parse_ntc_file(path: Path) -> list[dict]:
    cleaned = _clean(path.read_text(encoding="utf-8"))
    id_matches = list(_NTC_ID.finditer(cleaned))

    rows = []
    for i, m in enumerate(id_matches):
        start = m.start()
        end = id_matches[i + 1].start() if i + 1 < len(id_matches) else len(cleaned)
        block = cleaned[start:end]
        contenido_m = _NTC_CONTENIDO.search(block)
        if not contenido_m:
            continue
        norma_m = _NORMA.search(block)
        titulo_m = _TITULO.search(block)
        norma = _unescape_value(norma_m.group(1)) if norma_m else path.stem.replace("ntc_", "NTC ")
        rows.append({
            "norma": norma,
            "seccion": _unescape_value(m.group(1)),  # el "id" (ej. NTC121_05) hace de sección
            "titulo": _unescape_value(titulo_m.group(1))[:500] if titulo_m else "",
            "contenido": _unescape_value(contenido_m.group(1)),
        })
    return rows


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    print("Cargando modelo de embeddings local (paraphrase-multilingual-MiniLM-L12-v2)...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    nsr10_rows: list[dict] = []
    for path in sorted((RAW_DIR / "nsr10").glob("*.txt")):
        if path.stem not in NSR10_TITULOS:
            continue
        rows = parse_nsr10_file(path)
        print(f"  {path.name}: {len(rows)} chunks")
        nsr10_rows.extend(rows)

    ntc_rows: list[dict] = []
    for path in sorted((RAW_DIR / "ntc").glob("*.txt")):
        rows = parse_ntc_file(path)
        print(f"  {path.name}: {len(rows)} chunks")
        ntc_rows.extend(rows)

    print(f"\nTotal NSR-10: {len(nsr10_rows)} chunks | Total NTC: {len(ntc_rows)} chunks")

    if nsr10_rows:
        print("\nGenerando embeddings NSR-10...")
        textos = [r["texto"] for r in nsr10_rows]
        vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
        for row, vec in zip(nsr10_rows, vectores):
            row["embedding"] = vec.tolist()
        print("Subiendo a nsr10_chunks...")
        for i in range(0, len(nsr10_rows), 50):
            batch = nsr10_rows[i:i + 50]
            sb.table("nsr10_chunks").upsert(batch, on_conflict="id").execute()
        print(f"OK: {len(nsr10_rows)} chunks NSR-10 cargados")

    if ntc_rows:
        print("\nGenerando embeddings NTC...")
        textos = [r["contenido"] for r in ntc_rows]
        vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
        for row, vec in zip(ntc_rows, vectores):
            row["embedding"] = vec.tolist()
        print("Borrando contenido previo de ntc_chunks (idempotencia, sin llave natural)...")
        normas_nuevas = list({r["norma"] for r in ntc_rows})
        for norma in normas_nuevas:
            sb.table("ntc_chunks").delete().eq("norma", norma).execute()
        print("Subiendo a ntc_chunks...")
        for i in range(0, len(ntc_rows), 50):
            batch = ntc_rows[i:i + 50]
            sb.table("ntc_chunks").insert(batch).execute()
        print(f"OK: {len(ntc_rows)} chunks NTC cargados")


if __name__ == "__main__":
    main()
