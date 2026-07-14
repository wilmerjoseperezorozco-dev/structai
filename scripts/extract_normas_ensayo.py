"""
Extrae las 3 normas de ensayo INV-E reales adoptadas por la Resolución
2451 de 2022 (INVIAS) para nuevas tecnologías: INV E-631-22 (relaciones
humedad-peso unitario seco de mezclas de suelo con estabilizantes
químicos no tradicionales), INV E-632-22 (resistencia a la compresión
inconfinada de las mismas mezclas), INV E-826-22 (deflectómetro de
impacto liviano LWD). Primeras 3 normas reales de la carpeta "Normas de
ensayo de materiales para carreteras.zip" (99MB, sin desempaquetar
todavía) — sirven de piloto del patrón antes de procesar el resto.

Fuente: Google Drive, mismos ids ya usados en la sesión, PDFs nativos de
texto, INVIAS.

Uso: python scripts/extract_normas_ensayo.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_normas_ensayo_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "vias"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NORMAS = {
    "inv_e_631_22": {
        "raw_file": "inv_e_631_22.txt",
        "titulo_completo": "INV E-631-22 — Relaciones humedad-peso unitario seco de mezclas de suelo con estabilizantes químicos no tradicionales",
    },
    "inv_e_632_22": {
        "raw_file": "inv_e_632_22.txt",
        "titulo_completo": "INV E-632-22 — Resistencia a la compresión inconfinada de muestras de suelo estabilizadas con productos químicos no tradicionales",
    },
    "inv_e_826_22": {
        "raw_file": "inv_e_826_22.txt",
        "titulo_completo": "INV E-826-22 — Método para medir deflexiones mediante un deflectómetro de impacto liviano (LWD) en suelos",
    },
}

HEADER_RE = re.compile(
    r'(?<=\n)(\d{1,2}(?:\.\d{1,2}){0,3})\s+([A-ZÁÉÍÓÚÑ][^\n]{2,100})(?=\n)'
)


def clean_raw(text: str) -> str:
    text = re.sub(r'\*{1,3}', '', text)
    text = re.sub(
        r'\|\s*\|\s*\n\|\s*:-:\s*\|\s*\n\[Page \d+\]\(\)\s*\n', ' ', text,
    )
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def split_articulos(text: str, codigo: str) -> list[dict]:
    matches = list(HEADER_RE.finditer(text))
    chunks = []
    counters: dict[str, int] = {}
    for i, m in enumerate(matches):
        num, titulo = m.group(1), m.group(2).strip().rstrip('.')
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[content_start:content_end].strip()
        content = re.sub(r'\n{2,}', '\n', content)

        if len(content) < 30:
            continue

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"{codigo.upper()}-{num.replace('.', '_')}{suffix}"

        embedding_ready = f"{codigo.upper().replace('_', ' ')} {num} {titulo}. {content}"
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": f"{num} {titulo}",
            "titulo": titulo[:250],
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(codigo: str, titulo_completo: str, chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        f'"norma": "{titulo_completo}", "titulo_completo": "{titulo_completo}",',
        '"fuente": "INVIAS — Normas de Ensayo de Materiales para Carreteras, adoptadas por Resolución 2451 de 2022",',
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

    out_path = OUT_DIR / f"{codigo}.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {codigo}.txt: {len(chunks)} chunks -> {out_path}")


def main():
    total = 0
    for codigo, meta in NORMAS.items():
        raw_path = RAW_DIR / meta["raw_file"]
        if not raw_path.exists():
            print(f"  ADVERTENCIA: {raw_path} no existe, se omite {codigo}")
            continue
        raw = raw_path.read_text(encoding="utf-8")
        text = clean_raw(raw)
        chunks = split_articulos(text, codigo)
        if not chunks:
            print(f"  ADVERTENCIA: {codigo} -> 0 chunks extraídos, revisar patrón")
        write_chunk_file(codigo, meta["titulo_completo"], chunks)
        total += len(chunks)
    print(f"\nTotal chunks normas de ensayo: {total}")


if __name__ == "__main__":
    main()
