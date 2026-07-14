"""
Extrae la Norma Colombiana de Diseño de Puentes CCP-14 (basada en AASHTO LRFD
Bridge Design Specifications, adoptada oficialmente por INVIAS) desde sus 15
secciones oficiales (PDFs nativos de texto descargados directo del sitio de
INVIAS) y las estructura en el mismo formato chunk_id/seccion_origen/titulo/
embedding_ready que usa ingest_normativa.py.

Estructura real del CCP-14 (igual a AASHTO LRFD): cada "Artículo" numerado
N.N / N.N.N es la disposición vinculante; cada bloque "CN.N" es el
Comentario asociado -- el propio Artículo 1.1 del CCP-14 aclara que "esos
documentos y este comentario no están concebidos como parte de estas
especificaciones" (no vinculante, solo contexto). Se extraen ambos pero
etiquetados por separado (seccion_origen antepone "[Comentario]" cuando
corresponde) para que el RAG nunca presente un comentario como si fuera
la disposición normativa obligatoria.

Uso: python scripts/extract_ccp14.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_ccp14_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "ccp14"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SECCIONES = {
    "01": "Introducción",
    "02": "Características Generales de Diseño y Ubicación",
    "03": "Cargas y Factores de Carga",
    "04": "Análisis y Evaluación Estructural",
    "05": "Estructuras de Concreto",
    "06": "Estructuras de Acero",
    "07": "Estructuras de Aluminio",
    "08": "Estructuras de Madera",
    "09": "Tableros y Sistemas de Tableros",
    "10": "Cimentaciones",
    "11": "Muros, Estribos y Pilas",
    "12": "Estructuras Enterradas y Revestimientos para Túneles",
    "13": "Barandas",
    "14": "Juntas y Apoyos",
    "15": "Diseño de Barreras de Sonido",
}

# Encabezado de articulo: "15.1 — ALCANCE" o "**5.1 — ALCANCE**" (algunas
# secciones, ej. Concreto, envuelven el encabezado completo en negrita
# markdown -- \*{0,2} tolera el "**" antes del numero, que de otro modo
# rompe el ^ de inicio de linea). Hasta 4 niveles reales vistos (5.4.2.3.1).
ARTICULO_RE = re.compile(r'^\*{0,2}(\d{1,2}(?:\.\d{1,2}){1,4})\s*[—–-]\s*(.+?)\*{0,2}$', re.MULTILINE)
# Encabezado de comentario: "C15.4.2" o "**C1.3.1** — texto", puede venir solo en su linea
COMENTARIO_RE = re.compile(r'^\*{0,2}(C\d{1,2}(?:\.\d{1,2}){0,4})\*{0,2}\s*(?:[—–-]\s*(.+?))?\*{0,2}$', re.MULTILINE)


def clean_raw(text: str, seccion_num: str) -> str:
    # Ruido de la conversion PDF->texto: el pie de pagina "SECCIÓN N N-P" se
    # repite intercalado en el cuerpo del texto.
    text = re.sub(rf'SECCI[ÓO]N\s+{int(seccion_num)}\s+\d{{1,2}}-\d{{1,3}}', ' ', text)
    text = re.sub(r'\*{1,3}', '', text)  # negrita/cursiva markdown, no aporta al contenido
    return text


def split_secciones(text: str, seccion_num: str, seccion_nombre: str) -> list[dict]:
    headers = []
    for m in ARTICULO_RE.finditer(text):
        headers.append((m.start(), m.end(), m.group(1), m.group(2).strip(), False))
    for m in COMENTARIO_RE.finditer(text):
        titulo = (m.group(2) or "").strip()
        headers.append((m.start(), m.end(), m.group(1), titulo, True))
    headers.sort(key=lambda h: h[0])

    chunks = []
    counters: dict[str, int] = {}
    for i, (start, end, num, titulo, es_comentario) in enumerate(headers):
        body_start = end
        body_end = headers[i + 1][0] if i + 1 < len(headers) else len(text)
        body = text[body_start:body_end].strip()
        body = re.sub(r'[ \t]+', ' ', body)
        body = re.sub(r'\n{2,}', ' ', body)

        if len(body) < 60:
            continue
        # Filtro de indice/tabla de contenido: mismo criterio que Tuneles.
        if body.count('....') >= 2 or len(re.findall(r'\d{1,2}-\d{1,3}\b', body)) >= 3:
            continue

        key = f"S{seccion_num}-{num}{'C' if es_comentario else ''}"
        counters[key] = counters.get(key, 0) + 1
        suffix = f"-{counters[key]}" if counters[key] > 1 else ""
        chunk_id = f"CCP14-{key.replace('.', '_')}{suffix}"

        label = f"[Comentario] {num}" if es_comentario else num
        titulo_final = titulo if titulo else (f"Comentario a {num[1:]}" if es_comentario else num)
        seccion_origen = f"Sección {seccion_num} ({seccion_nombre}) — {label}" + (f" {titulo}" if titulo else "")
        embedding_ready = f"CCP-14 Sección {seccion_num} {seccion_nombre}. {label} {titulo}. {body}".strip()
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready)

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": seccion_origen,
            "titulo": titulo_final[:200],
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(all_chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        '"norma": "CCP-14 — Norma Colombiana de Diseño de Puentes", "titulo_completo": "Norma Colombiana de Diseño de Puentes CCP-14 (basada en AASHTO LRFD Bridge Design Specifications)",',
        '"fuente": "INVIAS, adoptada oficialmente para el diseño de puentes en Colombia",',
        '"fecha_extraccion": "2026-07-14"',
        '},',
        '"chunks": [',
    ]
    for c in all_chunks:
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

    out_path = OUT_DIR / "ccp14.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ccp14.txt: {len(all_chunks)} chunks -> {out_path}")


def main():
    all_chunks = []
    for num, nombre in SECCIONES.items():
        raw_path = RAW_DIR / f"seccion_{num}.txt"
        if not raw_path.exists():
            print(f"  ADVERTENCIA: {raw_path.name} no existe, se omite")
            continue
        raw = raw_path.read_text(encoding="utf-8")
        text = clean_raw(raw, num)
        chunks = split_secciones(text, num, nombre)
        print(f"  Sección {num} ({nombre}): {len(chunks)} chunks")
        all_chunks.extend(chunks)

    if not all_chunks:
        print("  ADVERTENCIA: 0 chunks extraídos, revisar patrón")
    write_chunk_file(all_chunks)
    print(f"\nTotal chunks CCP-14: {len(all_chunks)}")


if __name__ == "__main__":
    main()
