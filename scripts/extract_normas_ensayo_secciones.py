"""
Extrae las normas de ensayo INV-E reales de los archivos grandes "SECCIÓN
NNN.pdf" del paquete "Normas de Ensayo de Materiales para Carreteras"
(INVIAS, edición 2012) — cada archivo de Sección contiene MÚLTIPLES normas
INV-E individuales concatenadas (ej. Sección 200 = Agregados Pétreos, trae
las normas E-201 a E-245 seguidas una tras otra).

Extracción de dos niveles:
  1. Se detectan los límites reales entre normas individuales buscando el
     patrón "INV E – NNN – YY" (numeral + año de la versión) — cada norma
     nueva referencia su PROPIO número la primera vez que aparece. Como las
     normas se presentan en orden numérico ascendente dentro del archivo,
     se usa una heurística de secuencia monótona creciente para descartar
     referencias cruzadas hacia atrás dentro del cuerpo de otra norma (ej.
     "...ver la norma INV E-141..." mencionada dentro de la norma E-232).
  2. Dentro de cada norma individual, se segmenta por numeral de cláusula
     real ("1 OBJETO", "5.2 PROCEDIMIENTO"...) — mismo patrón ya validado
     en extract_normas_ensayo.py para los 3 pilotos INV E-631/632/826.

Fuente: PDFs descargados vía Drive y extraídos LOCALMENTE con PyMuPDF —
la herramienta read_file_content de Drive revuelve el orden de lectura en
estos documentos (columna lateral con "NORMAS Y ESPECIFICACIONES 2012
INVIAS" mezclada con el cuerpo), mientras PyMuPDF con get_text() por
defecto preserva el orden real de lectura. Verificado manualmente antes de
confiar en el patrón (ver scratchpad de la sesión 2026-07-14).

Uso: python scripts/extract_normas_ensayo_secciones.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_normas_ensayo_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "vias"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SECCIONES = {
    "seccion_200": {
        "raw_file": "seccion_200.txt",
        "titulo_completo": "Sección 200 — Agregados Pétreos (Normas de Ensayo de Materiales para Carreteras, INVIAS 2012)",
    },
    "seccion_300": {
        "raw_file": "seccion_300.txt",
        "titulo_completo": "Sección 300 — Cemento (Normas de Ensayo de Materiales para Carreteras, INVIAS 2012)",
    },
}

NORMA_BOUNDARY_RE = re.compile(r'INV\.?\s*E\s*[–—-]\s*(\d{3})\s*[–—-]\s*(\d{2})')
CLAUSE_RE = re.compile(
    r'(?<=\n)(\d{1,2}(?:\.\d{1,2}){0,3})\s+([A-ZÁÉÍÓÚÑ][^\n]{2,100})(?=\n)'
)


def find_norma_boundaries(text: str) -> list[tuple[int, str]]:
    """Devuelve [(posición_inicio, numero_norma), ...] en orden, quedándose
    solo con la primera aparición real de cada número siguiendo la
    secuencia ascendente (filtra referencias cruzadas hacia atrás)."""
    boundaries = []
    last_num = 0
    for m in NORMA_BOUNDARY_RE.finditer(text):
        num = int(m.group(1))
        if num > last_num:
            boundaries.append((m.start(), m.group(1)))
            last_num = num
    return boundaries


def split_clauses(body: str, norma_num: str) -> list[dict]:
    matches = list(CLAUSE_RE.finditer(body))
    chunks = []
    counters: dict[str, int] = {}
    for i, m in enumerate(matches):
        num, titulo = m.group(1), m.group(2).strip().rstrip('.')
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[content_start:content_end].strip()
        content = re.sub(r'\n{2,}', ' ', content)
        content = re.sub(r'[ \t]+', ' ', content)

        if len(content) < 30:
            continue

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"INVE{norma_num}-{num.replace('.', '_')}{suffix}"

        embedding_ready = f"INV E-{norma_num} {num} {titulo}. {content}"
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": f"INV E-{norma_num} — {num} {titulo}",
            "titulo": titulo[:250],
            "embedding_ready": embedding_ready,
        })
    return chunks


def split_normas(text: str, codigo_seccion: str) -> list[dict]:
    boundaries = find_norma_boundaries(text)
    all_chunks = []
    for i, (start, norma_num) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        body = text[start:end]
        chunks = split_clauses(body, norma_num)
        if not chunks:
            # cuerpo con muy poca estructura reconocible: no se fabrica nada,
            # se omite esa norma individual y sigue con la siguiente
            continue
        all_chunks.extend(chunks)
    return all_chunks


def write_chunk_file(codigo: str, titulo_completo: str, chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        f'"norma": "{titulo_completo}", "titulo_completo": "{titulo_completo}",',
        '"fuente": "INVIAS — Normas de Ensayo de Materiales para Carreteras, edición 2012 (reemplaza Resolución 3290 de 2007)",',
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
    for codigo, meta in SECCIONES.items():
        raw_path = RAW_DIR / meta["raw_file"]
        if not raw_path.exists():
            print(f"  ADVERTENCIA: {raw_path} no existe, se omite {codigo}")
            continue
        text = raw_path.read_text(encoding="utf-8")
        boundaries = find_norma_boundaries(text)
        print(f"  {codigo}: {len(boundaries)} normas individuales detectadas ({', '.join(n for _, n in boundaries[:5])}...)")
        chunks = split_normas(text, codigo)
        write_chunk_file(codigo, meta["titulo_completo"], chunks)
        total += len(chunks)
    print(f"\nTotal chunks Secciones de Normas de Ensayo: {total}")


if __name__ == "__main__":
    main()
