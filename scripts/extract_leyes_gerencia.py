"""
Extrae las 3 leyes colombianas de contratación pública que dan base legal
real a motor-gerencia (gerencia de proyectos de construcción en Colombia,
más allá del PMBOK/EVM genérico que ya tenía el motor):
  - Ley 80 de 1993 — Estatuto General de Contratación de la Administración Pública
  - Ley 1150 de 2007 — Eficiencia y transparencia en la Ley 80
  - Ley 1474 de 2011 — Estatuto Anticorrupción (incluye interventoría/supervisión)

Fuente real: Gestor Normativo (Departamento Administrativo de la Función
Pública) — Ley 80 y 1150 vía Google Docs (texto real extraído), Ley 1474
vía PDF nativo de texto (extraído localmente con PyMuPDF, 52 páginas).

Estructura por "ARTÍCULO N" real, igual que RAS 2000 — SIN re.IGNORECASE
a propósito: los encabezados reales siempre empiezan con "A" mayúscula
("Artículo 5º.-" o "ARTÍCULO 5."), mientras las referencias cruzadas
dentro del texto van en minúscula ("...ver artículo 24..."); con
IGNORECASE esas referencias se detectarían como artículos falsos y
partirían el chunk a la mitad (mismo bug ya encontrado y corregido en
RAS 2000 Título A).

Uso: python scripts/extract_leyes_gerencia.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_gerencia_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "gerencia_leyes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LEYES = {
    "ley80_1993": {
        "raw_file": "ley80_1993.txt",
        "titulo_completo": "Ley 80 de 1993 — Estatuto General de Contratación de la Administración Pública",
    },
    "ley1150_2007": {
        "raw_file": "ley1150_2007.txt",
        "titulo_completo": "Ley 1150 de 2007 — Eficiencia y transparencia en la Ley 80 de 1993",
    },
    "ley1474_2011": {
        "raw_file": "ley1474_2011.txt",
        "titulo_completo": "Ley 1474 de 2011 — Estatuto Anticorrupción",
    },
}

# "A" mayuscula obligatoria (excluye referencias cruzadas en minuscula);
# tolera "Artículo 5º.-", "ARTÍCULO 5o.", "ARTÍCULO 5." (3 formatos reales
# distintos entre las 3 leyes) y el envoltorio "**" de markdown.
ARTICULO_RE = re.compile(
    r'\*{0,2}A(?:rt[íi]culo|RT[ÍI]CULO)\s+(\d+)[ºo°]?\.?-?\*{0,2}\s*',
)


def clean_raw(text: str) -> str:
    text = re.sub(
        r'\|\s*\|\s*\n\|\s*:-:\s*\|\s*\n\[\*\*Page \d+\*\*\]\(\)\s*\n',
        ' ', text,
    )
    text = re.sub(r'\*{1,3}', '', text)
    return text


def split_articulos(text: str, codigo: str) -> list[dict]:
    matches = list(ARTICULO_RE.finditer(text))
    chunks = []
    counters: dict[str, int] = {}
    for i, m in enumerate(matches):
        num = m.group(1)
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        body = re.sub(r'[ \t]+', ' ', body)
        body = re.sub(r'\n{2,}', ' ', body)

        if len(body) < 30:
            continue

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"{codigo.upper()}-ART{num}{suffix}"

        titulo_corto = body.split(".")[0][:100].strip()
        embedding_ready = f"Artículo {num}. {body}"
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": f"Artículo {num}",
            "titulo": titulo_corto,
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(codigo: str, titulo_completo: str, chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        f'"norma": "{titulo_completo}", "titulo_completo": "{titulo_completo}",',
        '"fuente": "Gestor Normativo — Departamento Administrativo de la Función Pública (Función Pública)",',
        '"fecha_extraccion": "2026-07-14"',
        '},',
        '"chunks": [',
    ]
    for c in chunks:
        contenido = c["embedding_ready"].replace('"', "'")
        titulo = c["titulo"].replace('"', "'")
        lines.append('{')
        lines.append(f'"chunk_id": "{c["chunk_id"]}",')
        lines.append(f'"seccion_origen": "{c["seccion_origen"]}",')
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
    for codigo, meta in LEYES.items():
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
    print(f"\nTotal chunks leyes de gerencia: {total}")


if __name__ == "__main__":
    main()
