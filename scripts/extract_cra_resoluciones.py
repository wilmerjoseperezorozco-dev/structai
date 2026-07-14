"""
Extrae las Resoluciones CRA (Comisión de Regulación de Agua Potable y
Saneamiento Básico) reales para AquAI — dominio tarifario/regulatorio de
acueducto, alcantarillado y aseo, complemento a RAS 2000/Resolución 0330.

Fuente: Google Drive, PDFs oficiales de la CRA (Ministerio de Vivienda,
Ciudad y Territorio), texto nativo.

Uso: python scripts/extract_cra_resoluciones.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_cra_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "cra"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RESOLUCIONES = {
    "res_cra_955_2021": {
        "raw_file": "res_cra_955_2021.txt",
        "titulo_completo": "Resolución CRA 955 de 2021 — Modifica medidas transitorias de suspensión/corte de acueducto y costos de lavado y desinfección de áreas públicas (COVID-19)",
    },
    "res_cra_956_2021": {
        "raw_file": "res_cra_956_2021.txt",
        "titulo_completo": "Resolución CRA 956 de 2021 — Acuerdos de barrido y limpieza de vías y áreas públicas y resolución de conflictos por remuneración entre prestadores de aseo",
    },
}

# Artículos con numeral simple ("Artículo N.") o con numeral compuesto real
# de la Resolución CRA 943 ("ARTÍCULO 5.8.2.N.N.").
ARTICULO_RE = re.compile(
    r'(?:^|\n)(?:Art[íi]culo|ART[ÍI]CULO)\s+(\d{1,2}(?:\.\d{1,2}){0,4})\.?\s*',
)


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
        chunk_id = f"{codigo.upper()}-ART{num.replace('.', '_')}{suffix}"

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
        '"fuente": "Comisión de Regulación de Agua Potable y Saneamiento Básico (CRA)",',
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
    for codigo, meta in RESOLUCIONES.items():
        raw_path = RAW_DIR / meta["raw_file"]
        if not raw_path.exists():
            print(f"  ADVERTENCIA: {raw_path} no existe, se omite {codigo}")
            continue
        text = raw_path.read_text(encoding="utf-8")
        chunks = split_articulos(text, codigo)
        if not chunks:
            print(f"  ADVERTENCIA: {codigo} -> 0 chunks extraídos, revisar patrón")
        write_chunk_file(codigo, meta["titulo_completo"], chunks)
        total += len(chunks)
    print(f"\nTotal chunks Resoluciones CRA: {total}")


if __name__ == "__main__":
    main()
