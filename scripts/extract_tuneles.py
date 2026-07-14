"""
Extrae el Manual para el Diseño, Construcción, Operación y Mantenimiento de
Túneles de Carretera para Colombia (Edición 2021, INVIAS/MinTransporte,
adoptado por la Resolución 20213040058015 del 2 de diciembre de 2021) y lo
estructura en el mismo formato chunk_id/seccion_origen/titulo/embedding_ready
que usa ingest_normativa.py.

Fuente real: PDF nativo de texto (no escaneado — read_file_content extrajo
437K caracteres reales directamente, sin necesitar OCR), 153 páginas reales,
9 capítulos, subsecciones numeradas "N.N" / "N.N.N" (ej. "1.4.1 Ley
Colombiana para Infraestructura vial"). Confirmado real por metadata interna
del documento: fecha "Bogotá D.C., diciembre 2 de 2021" coincide exacto con
la Resolución 58015/2021 que lo adopta, y nombra funcionarios reales del
Gobierno (Iván Duque Márquez, Ángela María Orozco Gómez).

Uso: python scripts/extract_tuneles.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "scripts" / "_tuneles_raw_drive_dump" / "tuneles_raw.txt"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "tuneles"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Numero de subseccion "N.N" o "N.N.N", tolerante a envoltura en negrita
# markdown (**1.4 Titulo**) y a que el titulo pueda seguir en la misma linea.
SECCION_RE = re.compile(
    r'\*{0,2}(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)\s+([A-ZÁÉÍÓÚÑ][^\n*]{3,120}?)\*{0,2}\s*\n',
)


def clean_raw(text: str) -> str:
    # Ruido de la conversion PDF->texto: marcadores de salto de pagina y
    # tablas de una sola celda vacia que Google inserta entre paginas.
    text = re.sub(r'\|\s*\|\s*\n\|\s*:-:\s*\|\s*\n\[\*\*Page \d+\*\*\]\(\)\s*\n', ' ', text)
    text = re.sub(r'-{4,}\n', ' ', text)
    text = re.sub(r'\[(.+?)\]\(#\d+\)', r'\1', text)  # enlaces internos al TOC
    return text


def split_secciones(text: str) -> list[dict]:
    matches = list(SECCION_RE.finditer(text))
    chunks = []
    counters: dict[str, int] = {}
    for i, m in enumerate(matches):
        num = m.group(1)
        titulo = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        body = re.sub(r'[ \t]+', ' ', body)
        body = re.sub(r'\n{2,}', ' ', body)
        # Igual que en NSR-10/RAS 2000: una subseccion sin cuerpo real (solo
        # aparece en el indice enlazado, ej. "[DISEÑO](#160)") no aporta nada
        # citable -- se descarta.
        if len(body) < 60:
            continue
        # El indice del manual (tabla de contenido) repite estos mismos
        # numeros de seccion seguidos de lineas de puntos "....." y numero
        # de pagina ("3-44") -- no es contenido real, es la lista del indice.
        if body.count('....') >= 2 or len(re.findall(r'\d+-\d{1,3}\b', body)) >= 3:
            continue
        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"TUNELES-{num.replace('.', '_')}{suffix}"
        embedding_ready = f"{num} {titulo}. {body}"
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()
        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": f"{num} {titulo}",
            "titulo": titulo[:200],
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        '"norma": "Manual de Túneles de Carretera para Colombia (Edición 2021)", "titulo_completo": "Manual para el Diseño, Construcción, Operación y Mantenimiento de Túneles de Carretera para Colombia",',
        '"fuente": "INVIAS / Ministerio de Transporte, Edición 2021, adoptado por Resolución 20213040058015 del 02/12/2021",',
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

    out_path = OUT_DIR / "tuneles.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  tuneles.txt: {len(chunks)} chunks -> {out_path}")


def main():
    raw = RAW_PATH.read_text(encoding="utf-8")
    text = clean_raw(raw)
    chunks = split_secciones(text)
    if not chunks:
        print("  ADVERTENCIA: 0 chunks extraídos, revisar patrón")
    write_chunk_file(chunks)
    print(f"\nTotal chunks Manual de Túneles: {len(chunks)}")


if __name__ == "__main__":
    main()
