"""
Extrae las 2 guías del Ministerio de Vivienda, Ciudad y Territorio (2024)
para la contratación de revisiones de POT — "Recomendaciones técnicas a los
municipios y distritos para la elaboración de los contenidos técnicos en los
procesos de contratación de los POT" (revisión general / modificación
excepcional) — y las estructura por jerarquía de encabezados (# / ## / ###,
tal como los preserva la conversión de .docx a texto) en el mismo formato
chunk_id/seccion_origen/titulo/embedding_ready que usa ingest_normativa.py.

A diferencia de RAS 2000/NSR-10 (normas legales con artículos numerados),
estos son documentos de guía técnica/administrativa del Ministerio de
Vivienda — se segmentan por su propia estructura de encabezados en vez de
por "artículo".

Fuente real (Google Drive, carpeta compartida por el usuario 2026-07-14):
- revision-general-pot_mayo-2024.docx
- modif-excep-rev-excep-corto-y-mediano-plazo-mayo-2024.docx

Uso: python scripts/extract_pot.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_pot_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "pot"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DOCS = {
    "rev_general": {
        "raw_file": "pot_revision_general.txt",
        "titulo_completo": "Recomendaciones técnicas para la contratación — Revisión General del POT",
    },
    "modif_excep": {
        "raw_file": "pot_modif_excepcional.txt",
        "titulo_completo": "Recomendaciones técnicas para la contratación — Modificación/Revisión Excepcional del POT (corto y mediano plazo)",
    },
}

HEADER_RE = re.compile(r'^(#{1,3})\s+(.+?)\s*$', re.MULTILINE)


def split_secciones(text: str, doc_code: str) -> list[dict]:
    headers = [(len(m.group(1)), m.group(2).strip(), m.start(), m.end()) for m in HEADER_RE.finditer(text)]
    chunks = []
    # Pila de contexto jerarquico: path[level] = titulo de esa cabecera
    path: dict[int, str] = {}
    counters: dict[str, int] = {}

    for i, (level, titulo, start, end) in enumerate(headers):
        # Actualiza el path jerarquico; limpia niveles mas profundos al entrar a uno nuevo
        path[level] = titulo
        for deeper in [l for l in path if l > level]:
            del path[deeper]

        body_start = end
        body_end = headers[i + 1][2] if i + 1 < len(headers) else len(text)
        body = text[body_start:body_end].strip()
        body = re.sub(r'[ \t]+', ' ', body)
        body = re.sub(r'\n{3,}', '\n\n', body)

        # Filtro real: una cabecera cuyo unico contenido antes de la siguiente
        # cabecera es vacio/trivial (ej. un H2 que solo agrupa H3s) no aporta
        # nada citable por si sola -- se omite, igual que en RAS 2000 Titulo B.
        if len(body) < 40:
            continue

        breadcrumb = " > ".join(path[l] for l in sorted(path) if l <= level)
        key = f"{doc_code}-{level}"
        counters[key] = counters.get(key, 0) + 1
        chunk_id = f"POT-{doc_code.upper()}-{level}-{counters[key]}"

        embedding_ready = f"{breadcrumb}. {body}".strip()
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready)

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": breadcrumb,
            "titulo": titulo[:200],
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(doc_code: str, titulo_completo: str, chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        f'"norma": "Guía POT — Ministerio de Vivienda, Ciudad y Territorio (2024)", "titulo_completo": "{titulo_completo}",',
        '"fuente": "Ministerio de Vivienda, Ciudad y Territorio, 2024 — Recomendaciones técnicas para la contratación de procesos de revisión del POT",',
        '"fecha_extraccion": "2026-07-14"',
        '},',
        '"chunks": [',
    ]
    for c in chunks:
        contenido = c["embedding_ready"].replace('"', "'")
        titulo = c["titulo"].replace('"', "'")
        seccion = c["seccion_origen"].replace('"', "'")
        lines.append('{')
        lines.append(f'"chunk_id": "{c["chunk_id"]}",')
        lines.append(f'"seccion_origen": "{seccion}",')
        lines.append(f'"titulo": "{titulo}",')
        lines.append(f'"embedding_ready": "{contenido}"')
        lines.append('},')
    lines.append(']')
    lines.append('}')

    out_path = OUT_DIR / f"{doc_code}.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {doc_code}.txt: {len(chunks)} chunks -> {out_path}")


def main():
    total = 0
    for doc_code, meta in DOCS.items():
        raw_path = RAW_DIR / meta["raw_file"]
        if not raw_path.exists():
            print(f"  ADVERTENCIA: {raw_path} no existe, se omite {doc_code}")
            continue
        text = raw_path.read_text(encoding="utf-8")
        chunks = split_secciones(text, doc_code)
        if not chunks:
            print(f"  ADVERTENCIA: {doc_code} -> 0 chunks extraídos, revisar patrón")
        write_chunk_file(doc_code, meta["titulo_completo"], chunks)
        total += len(chunks)
    print(f"\nTotal chunks guías POT: {total}")


if __name__ == "__main__":
    main()
