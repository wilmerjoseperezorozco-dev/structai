"""
Extrae el Manual de Interventoría de Obra Pública 2022 (INVIAS, código
MEPI-MN1, versión 1, VIGENTE según el catálogo oficial de invias.gov.co/4154
que reemplazó al Manual de Interventoría 2016 DEROGADO). Complemento
procedimental/técnico de la Ley 1474/2011 (que ya cubre interventoría desde
el lado legal) — este manual da el detalle operativo real: facultades y
obligaciones específicas de la interventoría (46 numerales, Sección 8.4),
generales (Sección 8.3), y ambientales/sociales/prediales/sostenibilidad
(Sección 8.5), más el listado completo de normatividad aplicable (Sección 7,
46 leyes/decretos/resoluciones reales).

Fuente: Google Drive, id 1DFLXCHU8khCdO01QlCDwFlv-T8dnoUN3, PDF nativo de
texto (no escaneado), firmado digitalmente por Juan Esteban Gil Chavarría
(Director General INVIAS) y Juan Esteban Romero Toro (Director de Ejecución
y Operación) — funcionarios reales verificables.

Estructura mixta real del documento, manejada explícitamente:
  - Secciones principales 1-9, numeral simple sin punto final, título en
    MAYÚSCULA SOSTENIDA ("8 LA INTERVENTORÍA").
  - Subsecciones reales con numeral compuesto (N.N o N.N.N), pueden venir en
    mayúscula ("4.1 PRINCIPIOS...") o en Título normal ("4.2.1 Principios
    Institucionales") — el punto en común que las identifica es el numeral
    con punto interno, no el uso de mayúsculas.
  - Listas planas numeradas 1..46 DENTRO de una sección (7=normatividad,
    8.3/8.4/8.5=facultades) — mismo numeral simple que las secciones
    principales, pero en Título/oración normal (nunca MAYÚSCULA SOSTENIDA).
    Se distinguen de las secciones principales 1-9 por esa diferencia de
    capitalización — heurística verificada contra el documento real antes
    de confiar en ella (ver scratchpad de la sesión).

Uso: python scripts/extract_interventoria.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "scripts" / "_interventoria_raw_drive_dump" / "manual_interventoria_2022.txt"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "gerencia_leyes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADER_FOOTER_RE = re.compile(
    r'INSTITUTO NACIONAL DE V[ÍI]AS PROCESO MISIONAL EJECUCI[ÓO]N DE PROYECTOS '
    r'DE INFRAESTRUCTURA DE TRANSPORTE MANUAL DE INTERVENTOR[ÍI]A OBRA P[ÚU]BLICA'
    r'\s*\n+\s*C[ÓO]DIGO MEPI-MN1\s*\n+\s*VERSI[ÓO]N 1\s*\n+\s*P[ÁA]GINA \d+ DE 70\s*\n*',
)

HEADER_RE = re.compile(
    r'(?<=\n\n)(\d{1,2}(?:\.\d{1,2}){0,2})\.?\s+([A-ZÁÉÍÓÚÑ][^\n]{2,110})(?=\n\n)'
)


def clean_raw(text: str) -> str:
    text = text.replace("\\.", ".")
    text = HEADER_FOOTER_RE.sub("\n\n", text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def is_allcaps_title(title: str) -> bool:
    letters = re.sub(r'[^A-ZÁÉÍÓÚÑa-záéíóúñ]', '', title)
    return letters.isupper() and len(letters) >= 3


def split_sections(body: str) -> list[dict]:
    matches = list(HEADER_RE.finditer(body))
    chunks = []
    current_top = None
    current_sub = None
    for i, m in enumerate(matches):
        num, title = m.group(1), m.group(2).strip()
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[content_start:content_end].strip()
        content = re.sub(r'\n{2,}', '\n', content)

        is_dotted = "." in num
        if is_dotted:
            current_sub = f"{num} {title}"
            seccion_origen = f"{current_top} > {current_sub}" if current_top else current_sub
            label = current_sub
            chunk_id = f"INTERVENTORIA-{num.replace('.', '_')}"
        elif is_allcaps_title(title):
            current_top = f"{num} {title}"
            current_sub = None
            seccion_origen = current_top
            label = current_top
            chunk_id = f"INTERVENTORIA-SEC{num}"
        else:
            parent = current_sub or current_top or "?"
            seccion_origen = f"{parent} > {num}. {title}"
            label = f"{parent} — {num}. {title}"
            parent_num = (current_sub or current_top or "0").split(" ")[0].replace(".", "_")
            chunk_id = f"INTERVENTORIA-{parent_num}-IT{num}"

        if len(content) < 30 and not is_dotted and is_allcaps_title(title):
            # sección principal con solo un título de paso (contenido real vive en sus subsecciones)
            continue

        embedding_ready = f"{label}. {content}".strip()
        embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()
        if len(embedding_ready) < 40:
            continue

        chunks.append({
            "chunk_id": chunk_id,
            "seccion_origen": seccion_origen,
            "titulo": (title if len(title) <= 100 else title[:100]),
            "embedding_ready": embedding_ready,
        })
    return chunks


def write_chunk_file(chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        '"norma": "Manual de Interventoría de Obra Pública 2022 (INVIAS, MEPI-MN1 v1)",',
        '"titulo_completo": "Manual de Interventoría de Obra Pública — Instituto Nacional de Vías (INVIAS), código MEPI-MN1, versión 1",',
        '"fuente": "INVIAS — firmado digitalmente por Juan Esteban Gil Chavarría (Director General) y Juan Esteban Romero Toro (Director de Ejecución y Operación)",',
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

    out_path = OUT_DIR / "manual_interventoria_2022.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  manual_interventoria_2022.txt: {len(chunks)} chunks -> {out_path}")


def extract_vigencia_chunk(text: str) -> dict | None:
    m = re.search(
        r'VIGENCIA Y PROCEDIMIENTO DE MODIFICACI[ÓO]N\s*\n\n(.+?)\n\n1\.?\s+INTRODUCCI[ÓO]N',
        text, re.DOTALL,
    )
    if not m:
        return None
    content = re.sub(r'\s+', ' ', m.group(1)).strip()
    return {
        "chunk_id": "INTERVENTORIA-VIGENCIA",
        "seccion_origen": "Vigencia y procedimiento de modificación",
        "titulo": "Vigencia y procedimiento de modificación",
        "embedding_ready": f"Vigencia y procedimiento de modificación. {content}",
    }


def main():
    raw = RAW_PATH.read_text(encoding="utf-8")
    text = clean_raw(raw)

    vigencia_chunk = extract_vigencia_chunk(text)

    # cuerpo real empieza en "1 INTRODUCCIÓN" (después del índice y la lista
    # maestra de instructivos/formatos, que son solo códigos de formularios,
    # no contenido narrativo del manual)
    body_start_match = re.search(r'\n\n1\.?\s+INTRODUCCI[ÓO]N\s*\n\n', text)
    if not body_start_match:
        raise RuntimeError("No se encontró el inicio real del cuerpo ('1 INTRODUCCIÓN')")
    body = text[body_start_match.start():]

    chunks = split_sections(body)
    if vigencia_chunk:
        chunks = [vigencia_chunk] + chunks
    write_chunk_file(chunks)
    print(f"\nTotal chunks Manual de Interventoría: {len(chunks)}")


if __name__ == "__main__":
    main()
