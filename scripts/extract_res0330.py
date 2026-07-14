"""
Extrae el texto de la Resolución 0330 de 2017 (Ministerio de Vivienda, Ciudad
y Territorio — norma VIGENTE del sector agua potable y saneamiento básico,
deroga la Resolución 1096 de 2000 / RAS 2000) desde la transcripción en
Markdown y lo estructura en el mismo formato chunk_id/seccion_origen/titulo/
embedding_ready que ya usa ingest_normativa.py para NSR-10/RAS 2000.

Fuente y verificación (ver normas_registro.notas_vigencia para el detalle
completo): el PDF oficial escaneado (72.5 MB, Drive) supera el límite de la
herramienta de descarga y el OCR automático de "Abrir con Google Docs" no
extrajo texto real (0 caracteres, solo imágenes de página). El usuario obtuvo
una transcripción completa vía DeepSeek (otro LLM) en 3 iteraciones —
verificada aquí, no aceptada a ciegas, cruzando:
  1. La cláusula de derogación (Art. 255) coincide palabra por palabra con
     las otras 2 fuentes independientes ya confirmadas en esta sesión.
  2. Los 255 artículos son correlativos 1-255 sin huecos ni duplicados.
  3. El Art. 43 (dotación neta) es idéntico en las 3 iteraciones sucesivas
     del documento (no cambia entre versiones — no parece alucinado al azar).
  4. Contenido técnico denso con tablas de diseño numéricamente coherentes
     (rangos de ingeniería reales, no valores redondos sospechosos).
No es infalible (sigue siendo transcripción de IA, no el PDF oficial
byte-a-byte) pero pasa un umbral razonable de confianza cruzada — muy por
encima del "resumen estructurado" de 26 artículos descartado antes.

Uso: python scripts/extract_res0330.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "scripts" / "_res0330_raw_drive_dump" / "res0330_raw.md"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "res0330"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_raw(text: str) -> str:
    """Quita los 2 artefactos conversacionales de DeepSeek (inicio y el punto
    de continuación a mitad de documento) y las cercas ```markdown."""
    # Preámbulo inicial: "¡Excelente, compañero! ... ```markdown"
    text = re.sub(r'^.*?```markdown\s*', '', text, flags=re.DOTALL)
    # Continuación a mitad de documento: "¡Por supuesto, compañero! ... ---"
    text = re.sub(
        r'¡Por supuesto, compañero!.*?(?=\*{0,2}ART[ÍI]CULO\s+\d+\.)',
        '', text, flags=re.DOTALL,
    )
    text = text.replace('```', '')
    return text


def split_articulos(text: str) -> list[dict]:
    # ART[ÍI]CULO: 3 de los 255 artículos traen "ARTICULO" sin tilde (typo de
    # la transcripción). [.:] en el título: el Art. 4 termina en ":" en vez
    # de "." antes del cierre de negrita — ambos casos, sin esto, el artículo
    # completo se perdía (se fusionaba silenciosamente dentro del anterior).
    pattern = re.compile(
        r'\*{0,2}(ART[ÍI]CULO\s+(\d+)\.\s*([^\n*]+?)[.:])\*{0,2}\s*'
        r'(.*?)(?=\*{0,2}ART[ÍI]CULO\s+\d+\.|\Z)',
        re.DOTALL,
    )
    chunks = []
    for m in pattern.finditer(text):
        num = m.group(2)
        titulo_corto = m.group(3).strip()
        body = m.group(4).strip()
        body = re.sub(r'\*{1,2}', '', body)
        body = re.sub(r'[ \t]+', ' ', body)
        body = re.sub(r'\n{3,}', '\n\n', body)
        embedding_ready = f"ARTÍCULO {num}. {titulo_corto}. {body}".strip()
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready)
        chunks.append({
            "chunk_id": f"RES0330-ART{num}",
            "seccion_origen": f"ARTÍCULO {num}",
            "titulo": titulo_corto[:200],
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        '"norma": "Resolución 0330 de 2017", "titulo_completo": "Reglamento Técnico del Sector de Agua Potable y Saneamiento Básico (RAS) — vigente",',
        '"fuente": "Resolución 0330 de 2017, Ministerio de Vivienda, Ciudad y Territorio (deroga Res. 1096/2000)",',
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

    out_path = OUT_DIR / "res0330.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  res0330.txt: {len(chunks)} chunks -> {out_path}")


def main():
    raw = RAW_PATH.read_text(encoding="utf-8")
    text = clean_raw(raw)
    chunks = split_articulos(text)
    if not chunks:
        print("  ADVERTENCIA: 0 chunks extraídos, revisar patrón")
    write_chunk_file(chunks)
    print(f"\nTotal chunks Resolución 0330/2017: {len(chunks)}")


if __name__ == "__main__":
    main()
