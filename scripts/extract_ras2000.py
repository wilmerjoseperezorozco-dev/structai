"""
Extrae el texto oficial de RAS 2000 (Títulos A-H) desde los archivos raw
descargados de Google Drive y los estructura en el mismo formato chunk_id/
seccion_origen/titulo/embedding_ready que ya usa ingest_normativa.py para
NSR-10 — así se ingesta con exactamente el mismo pipeline probado, sin
inventar contenido: cada chunk es texto oficial real, solo re-segmentado
por artículo (Título A, la resolución legal) o por código de sección
técnica (Títulos B-H, los anexos técnicos, formato "X.N.N").

Los archivos fuente (RAW_DIR) son scripts Python completos de un chatbot
RAG/CAG (LangChain/Ollama) descargados de Drive, cada uno con el texto
oficial de su título embebido en un bloque `TEXTO_COMPLETO = """..."""` —
no se versionan en este repo (son material de trabajo intermedio, no el
producto final); el resultado de este script (packages/construdata/
normativa_raw/ras2000/titulo_*.txt) sí se versiona, igual que nsr10/ntc.

Para volver a correr esto: descargar de nuevo los 8 Google Docs de la
carpeta de Drive (ver memoria del proyecto para los file IDs) a
RAW_DIR/titulo_{a..h}_raw.txt, luego `python scripts/extract_ras2000.py`.

Uso: python scripts/extract_ras2000.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "scripts" / "_ras2000_raw_drive_dump"  # material intermedio, no versionado (ver .gitignore)
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "ras2000"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TITULOS = {
    "a": "Condiciones Generales (Resolución 1096 de 2000)",
    "b": "Sistemas de Acueducto",
    "c": "Sistemas de Potabilización",
    "d": "Sistemas de Recolección y Evacuación de Aguas Residuales y Pluviales",
    "e": "Tratamiento de Aguas Residuales",
    "f": "Sistemas de Aseo Urbano",
    "g": "Aspectos Complementarios",
    "h": "Compendio Normativo",
}


def extract_texto_completo(raw: str) -> str:
    m = re.search(r'TEXTO_COMPLETO\s*=\s*"""(.*?)"""', raw, re.DOTALL)
    if not m:
        raise ValueError("No se encontró TEXTO_COMPLETO")
    texto = m.group(1)
    # Marcadores de nota al pie del documento fuente (ej. "[reference:12]") —
    # ruido para el embedding/búsqueda semántica, no aportan significado.
    texto = re.sub(r'\[reference:\d+\]', '', texto)
    return texto


def split_articulos(texto: str) -> list[dict]:
    """Título A: la resolución legal, estructurada por ARTÍCULO N.

    Sin re.IGNORECASE a propósito: los encabezados reales van en mayúscula
    ("ARTÍCULO 4º.—"); el texto corrido cita otros artículos en minúscula
    ("...ver artículo 14...") como referencia cruzada dentro de una frase,
    no como inicio de un artículo nuevo — con IGNORECASE esas referencias
    se detectaban como artículos falsos y partían el chunk a la mitad.
    """
    pattern = re.compile(
        r'(ART[ÍI]CULO\s+\d+[º°]?\.?—?)\s*(.*?)'
        r'(?=ART[ÍI]CULO\s+\d+[º°]?\.?—?|\Z)',
        re.DOTALL,
    )
    chunks = []
    for m in pattern.finditer(texto):
        header = m.group(1).strip()
        body = (header + " " + m.group(2)).strip()
        body = re.sub(r'\s+', ' ', body)
        if len(body) < 20:
            continue
        num_m = re.search(r'\d+', header)
        titulo_corto = body.split(".—")[1][:80].strip() if ".—" in body else body[:80]
        chunks.append({
            "chunk_id": f"RAS-A-ART{num_m.group(0) if num_m else '0'}",
            "seccion_origen": header,
            "titulo": titulo_corto,
            "embedding_ready": body,
        })
    return chunks


def split_secciones(texto: str, letra: str) -> list[dict]:
    """Títulos B-H: anexos técnicos, estructurados por código 'X.N.N' (con o sin punto tras la letra)."""
    letra_upper = letra.upper()
    pattern = re.compile(
        rf'(?:^|\n)\s*{letra_upper}\.?(\d+\.\d+(?:\.\d+)?)\s+([^\n]*)\n'
        rf'(.*?)(?=(?:\n\s*{letra_upper}\.?\d+\.\d+(?:\.\d+)?\s)|\Z)',
        re.DOTALL,
    )
    chunks = []
    for m in pattern.finditer(texto):
        codigo = f"{letra_upper}.{m.group(1)}"
        titulo_linea = m.group(2).strip()
        cuerpo = m.group(3).strip()
        texto_completo = re.sub(r'\s+', ' ', f"{titulo_linea} {cuerpo}").strip()
        # Umbral real, no arbitrario: un chunk de solo-título sin cuerpo
        # (ej. Título B trae varias secciones que en la fuente de Drive son
        # solo un renglón de índice, sin desarrollo técnico) no aporta nada
        # citable al RAG — mejor no tenerlo que tenerlo vacío y que el
        # sistema "cite" una sección sin contenido real detrás.
        if len(texto_completo) < 60:
            continue
        chunks.append({
            "chunk_id": f"RAS-{codigo.replace('.', '_')}",
            "seccion_origen": codigo,
            "titulo": titulo_linea[:200] if titulo_linea else codigo,
            "embedding_ready": texto_completo,
        })
    return chunks


def write_chunk_file(letra: str, titulo_completo: str, chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        f'"norma": "RAS 2000", "titulo": "{letra.upper()}", "titulo_completo": "{titulo_completo}",',
        '"fuente": "Resolución 1096 de 2000 (RAS), Ministerio de Desarrollo Económico / OAS",',
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

    out_path = OUT_DIR / f"titulo_{letra}.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  titulo_{letra}.txt: {len(chunks)} chunks -> {out_path}")


def main():
    total = 0
    for letra, titulo_completo in TITULOS.items():
        raw_path = RAW_DIR / f"titulo_{letra}_raw.txt"
        raw = raw_path.read_text(encoding="utf-8")
        texto = extract_texto_completo(raw)

        if letra == "a":
            chunks = split_articulos(texto)
        else:
            chunks = split_secciones(texto, letra)

        if not chunks:
            print(f"  ADVERTENCIA: titulo_{letra} -> 0 chunks extraídos, revisar patrón")
        write_chunk_file(letra, titulo_completo, chunks)
        total += len(chunks)

    print(f"\nTotal chunks RAS 2000 (A-H): {total}")


if __name__ == "__main__":
    main()
