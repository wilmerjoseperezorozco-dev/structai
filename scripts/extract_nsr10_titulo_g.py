"""
Extrae el Título G real de NSR-10 (Estructuras de Madera y Estructuras de
Guadua) — Reglamento Colombiano de Construcción Sismo Resistente, Ministerio
de Ambiente, Vivienda y Desarrollo Territorial, Comisión Asesora Permanente
para el Régimen de Construcciones Sismo Resistentes (Ley 400 de 1997).

Gap real detectado en la auditoría de esta sesión: lo que `nsr10_chunks`
tenía cargado como "Título F — Estructuras de Madera" es en realidad
contenido de madera/guadua (subject-matter de Título G), pero los chunks
existentes A-J son resúmenes técnicos redactados a mano ("Basado en NDS
2005 adaptado...") sin numeración real de artículos, no texto oficial
extraído verbatim. Este script SÍ hace extracción verbatim real, con el
mismo rigor que RAS 2000 / leyes de Gerencia / manuales INVIAS de esta
sesión — y usa la letra oficial correcta ("G"), sin tocar ni reetiquetar
los Títulos A-J ya existentes (esa reauditoría queda para otra sesión,
documentada aparte).

Fuente: idrd.gov.co (Instituto Distrital de Recreación y Deporte, entidad
gubernamental de Bogotá que aloja copias oficiales de normas técnicas),
PDF nativo de texto (no escaneado, no encriptado para extracción), 168
páginas, extraído localmente con PyMuPDF. Documento del propio Ministerio
de Ambiente, Vivienda y Desarrollo Territorial / Comisión Asesora
Permanente — mismo emisor real que el resto de títulos NSR-10.

Uso: python scripts/extract_nsr10_titulo_g.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "scripts" / "_nsr10_titulo_g_raw_drive_dump" / "titulo_g_raw.txt"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "nsr10"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADER_FOOTER_RE = re.compile(
    r'NSR-10\s*[—–-]\s*T[íi]tulo G\s*[—–-]\s*Estructuras de madera y estructuras de guadua\s*\n*',
    re.IGNORECASE,
)
PAGE_MARKER_RE = re.compile(r'\n\s*G-\d{1,3}\s*\n')

# Encabezados reales de nivel capítulo ("CAPÍTULO G.N") y de artículo/numeral
# ("G.N.N[.N[.N]] – TÍTULO"), con "–"/"-" como separador real observado en
# el documento (no ".", a diferencia de las leyes de Gerencia).
CAPITULO_RE = re.compile(r'CAP[ÍI]TULO\s+(G\.\d{1,2})\s*\n+([^\n]{3,100})')
NUMERAL_RE = re.compile(
    r'(?<=\n)(G\.\d{1,2}(?:\.\d{1,2}){1,4})\s*[—–-]\s*([A-ZÁÉÍÓÚÑ0-9][^\n]{1,120})'
)


def clean_raw(text: str) -> str:
    text = HEADER_FOOTER_RE.sub("", text)
    text = PAGE_MARKER_RE.sub("\n", text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def find_body_start(text: str) -> int:
    m = re.search(r'CAP[ÍI]TULO\s+G\.1\s*\n+REQUISITOS GENERALES', text)
    if not m:
        raise RuntimeError("No se encontró el inicio real del cuerpo ('CAPÍTULO G.1 REQUISITOS GENERALES')")
    return m.start()


def split_articulos(body: str) -> list[dict]:
    matches = list(NUMERAL_RE.finditer(body))
    chunks = []
    counters: dict[str, int] = {}
    for i, m in enumerate(matches):
        num, titulo = m.group(1), m.group(2).strip().rstrip('.')

        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[content_start:content_end].strip()
        content = re.sub(r'\n{2,}', '\n', content)

        if len(content) < 30:
            continue

        embedding_ready = f"NSR-10 Título G {num} – {titulo}. {content}"
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"NSR10-G-{num.replace('.', '_')}{suffix}"

        chunks.append({
            "id": chunk_id,
            "capitulo": "NSR-10 Título G — Estructuras de Madera y Estructuras de Guadua",
            "seccion": num,
            "titulo": titulo[:250],
            "texto": embedding_ready,
        })
    return chunks


def main():
    raw = RAW_PATH.read_text(encoding="utf-8")
    text = clean_raw(raw)
    body = text[find_body_start(text):]

    chunks = split_articulos(body)

    out_path = OUT_DIR / "titulo_g_chunks.jsonl"
    import json
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"Título G: {len(chunks)} chunks -> {out_path}")


if __name__ == "__main__":
    main()
