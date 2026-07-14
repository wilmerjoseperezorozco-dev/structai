"""
Extrae los 2 manuales oficiales de diseño de pavimentos de INVIAS/ICPC —
"Manual de diseño de pavimentos de concreto para vías con bajos, medios y
altos volúmenes de tránsito" (ICPC + Ministerio de Transporte + INVIAS) y
"Manual de Diseño de Pavimentos Asfálticos en Vías con Medios y Altos
Volúmenes de Tránsito" (INVIAS + Ministerio de Transporte) — y los
estructura en el mismo formato chunk_id/seccion_origen/titulo/
embedding_ready que usa ingest_normativa.py.

Confirmados reales: nombran funcionarios reales (Jorge Alberto Álvarez
Pabón, director ICPC; Mauricio Cárdenas Santamaría, Ministro de Transporte
real de la época). Ambos usan numeración de sección real N.N/N.N.N.

Estos 2 manuales oficiales reemplazan el "AASHTO-93 adaptado" genérico que
hoy usa motor-vias para pavimentos (packages/motor-vias/src/pavimentos.py)
-- ver normas_registro para el detalle de por qué esto es un gap de
precisión real, no solo de trazabilidad.

Uso: python scripts/extract_pavimentos.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_pavimentos_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "pavimentos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DOCS = {
    "concreto": {
        "raw_file": "concreto.txt",
        "titulo_completo": "Manual de diseño de pavimentos de concreto para vías con bajos, medios y altos volúmenes de tránsito (ICPC / Ministerio de Transporte / INVIAS)",
    },
    "asfaltico": {
        "raw_file": "asfaltico.txt",
        "titulo_completo": "Manual de Diseño de Pavimentos Asfálticos en Vías con Medios y Altos Volúmenes de Tránsito (INVIAS / Ministerio de Transporte)",
    },
    "bajos_volumenes": {
        "raw_file": "bajos_volumenes.txt",
        "titulo_completo": "Manual de Diseño de Pavimentos Asfálticos para Vías con Bajos Volúmenes de Tránsito (INVIAS / Ministerio de Transporte, abril 2007, adoptado por Resolución 003482/2007)",
    },
}

HEADER_RE = re.compile(r'^(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)\s+([A-ZÁÉÍÓÚÑ][^\n]{2,90})$', re.MULTILINE)
CONECTORES = re.compile(r'\b(de|la|el|en|que|para|con|los|las|una|del)\b', re.IGNORECASE)


# Marcadores literales que solo aparecen en la tabla de contenido desordenada
# por la conversion PDF->texto (columnas de numero/titulo/pagina fusionadas
# en el orden equivocado) -- nunca en prosa real del manual.
TOC_MARKERS_RE = re.compile(r'\bCONTENIDO\b|\bCAPITULO\s+\d+\b|\bPag\.\s*$|^Pag\.', re.MULTILINE)


def es_prosa_real(body: str) -> bool:
    """Distingue prosa real de un indice/tabla de contenido desordenado por
    la conversion PDF->texto (titulos y numeros de pagina entremezclados
    sin frases conectadas) -- la prosa real tiene alta densidad de
    palabras conectoras; un indice desordenado, casi ninguna, y ademas
    trae marcadores literales de indice (CONTENIDO, CAPITULO N, Pag.)."""
    if len(body) < 60:
        return False
    if TOC_MARKERS_RE.search(body):
        return False
    # Racimo de 3+ numeros de subseccion "sueltos" (sin texto real alrededor,
    # solo separados por saltos de linea) es la firma de un indice fusionado.
    if len(re.findall(r'(?:^|\n)\d{1,2}\.\d{1,2}(?:\.\d{1,2})?(?:\n|$)', body)) >= 3:
        return False
    conectores = len(CONECTORES.findall(body))
    return conectores >= max(3, len(body) // 80)


def split_secciones(text: str, doc_code: str) -> list[dict]:
    headers = list(HEADER_RE.finditer(text))
    chunks = []
    counters: dict[str, int] = {}
    for i, m in enumerate(headers):
        num, titulo = m.group(1), m.group(2).strip()
        body_start = m.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[body_start:body_end].strip()
        body = re.sub(r'[ \t]+', ' ', body)
        body = re.sub(r'\n{2,}', ' ', body)

        if not es_prosa_real(body):
            continue

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"PAV-{doc_code.upper()}-{num.replace('.', '_')}{suffix}"
        embedding_ready = f"{num} {titulo}. {body}"
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": f"{num} {titulo}",
            "titulo": titulo[:200],
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(doc_code: str, titulo_completo: str, chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        f'"norma": "Manual de Pavimentos INVIAS — {doc_code}", "titulo_completo": "{titulo_completo}",',
        '"fuente": "INVIAS / Ministerio de Transporte (concreto: coedición ICPC)",',
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
    print(f"\nTotal chunks manuales de pavimentos: {total}")


if __name__ == "__main__":
    main()
