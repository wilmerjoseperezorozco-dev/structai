"""
Extrae el Capítulo 2 (Supervisión de Contratos y Convenios) que la
Resolución 970 de 2024 adicionó al Manual de Interventoría de Obra
Pública INVIAS — renombrándolo "Manual de Interventoría y Supervisión
de Obra Pública". Gap real: este capítulo NO estaba en los 126 chunks
ya cargados del manual base (PDF de 70 páginas, sin este capítulo).

Fuente: Google Drive, id 1pGtj4cWzXr8WcHT8qpy_ju5dmiXWDywr, código
MEPI-FR-1 versión 1, 24 páginas, texto nativo.

Uso: python scripts/extract_interventoria_cap2.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "scripts" / "_interventoria_raw_drive_dump" / "capitulo2_supervision.txt"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "gerencia_leyes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_BLOCK_RE = re.compile(
    r'\|\s*\|\s*\n\|\s*:-:\s*\|\s*\n\[\*\*Page \d+\*\*\]\(\)\s*\n'
)
HEADER_FOOTER_RE = re.compile(
    r'PROCESO:\s*EJECUCI[ÓO]N Y OPERACI[ÓO]N DE PROYECTOS DE\s*\n+'
    r'INFRAESTRUCTURA DE TRANSPORTE\s*\n+'
    r'MANUAL DE INTERVENTOR[ÍI]A Y SUPERVISI[ÓO]N DE OBRA P[ÚU]BLICA\s*\n+'
    r'C[ÓO]DIGO\s*\n+MEPI-FR-1\s*\n+VERSI[ÓO]N\s*\n+1\s*\n+P[ÁA]GINA\s*\n+\d+\s*\n+de 24\s*\n*',
)
HEADER_RE = re.compile(
    r'(?<=\n)(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s+([A-ZÁÉÍÓÚÑ][^\n]{2,150})(?=\n)'
)


def clean_raw(text: str) -> str:
    text = PAGE_BLOCK_RE.sub(" ", text)
    text = HEADER_FOOTER_RE.sub("\n\n", text)
    text = re.sub(r'\*{1,3}', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def split_sections(text: str) -> list[dict]:
    matches = [m for m in HEADER_RE.finditer(text) if m.group(2).strip().upper() != "PÁGINA"]
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
        chunk_id = f"INTERVENTORIA-CAP2-{num.replace('.', '_')}{suffix}"

        embedding_ready = f"Manual de Interventoría y Supervisión de Obra Pública — Capítulo 2 (Supervisión de Contratos y Convenios) {num} — {titulo}. {content}"
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": f"Capítulo 2 (Supervisión) {num} — {titulo}",
            "titulo": titulo[:250],
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        '"norma": "Manual de Interventoría y Supervisión de Obra Pública — Capítulo 2: Supervisión de Contratos y Convenios",',
        '"titulo_completo": "Capítulo 2 (Supervisión de Contratos y Convenios), adicionado al Manual de Interventoría de Obra Pública INVIAS por la Resolución 970 de 2024",',
        '"fuente": "INVIAS, código MEPI-FR-1 versión 1",',
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

    out_path = OUT_DIR / "interventoria_cap2_supervision.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  interventoria_cap2_supervision.txt: {len(chunks)} chunks -> {out_path}")


def main():
    raw = RAW_PATH.read_text(encoding="utf-8")
    text = clean_raw(raw)
    chunks = split_sections(text)
    write_chunk_file(chunks)
    print(f"\nTotal chunks Capítulo 2 Supervisión: {len(chunks)}")


if __name__ == "__main__":
    main()
