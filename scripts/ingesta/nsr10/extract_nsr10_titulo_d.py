"""
Extrae el Título D real de NSR-10 (Mampostería Estructural) — Reglamento
Colombiano de Construcción Sismo Resistente, Ministerio de Ambiente,
Vivienda y Desarrollo Territorial, Comisión Asesora Permanente para el
Régimen de Construcciones Sismo Resistentes (Ley 400 de 1997).

Mismo rigor verbatim que Título C (2026-08-26), con los 3 fixes de esa
sesión ya incorporados desde el inicio de este script (no como parches
posteriores): sin punto forzado título/contenido, con contexto del padre
en tablas enumeradas, y con limpieza de puntos de relleno de tabla del
PDF. Ver [[project_structai_nsr10_titulo_c_verbatim]] en la memoria del
proyecto para el detalle completo de cada bug.

Fuente: biblioteca de Google Drive del usuario (carpeta "NSR10" dentro de
"biblioteca 1"), NSR-10 completa dividida por rangos de página reales con
un catálogo maestro (nsr10_catalogo_maestro.json) que mapea cada archivo a
su capítulo/numeral real -- verificado a mano contra el catálogo antes de
usar (Título D = páginas Drive 565-639, 13 archivos PDF, D.1 a D.12 más
Apéndice D-1). Confirmado real leyendo el texto extraído directamente
(no solo confiando en los nombres de archivo o el catálogo): coincide
exactamente con el patrón ya visto en el Título C real (mismos
encabezados "NSR-10 – Capítulo D.N – <nombre>", mismos marcadores de
página "D-NN").

HALLAZGO ESTRUCTURAL REAL (distinto de Título C): Título D NO tiene la
separación REGLAMENTO/COMENTARIO de Título C -- verificado contando
"COMENTARIO" y marcadores "CRN" en el texto crudo, cero en ambos casos.
Estructura simple, un solo tipo de contenido vinculante, igual que
Título G. Este script es más simple que el de C por eso (sin
COMENTARIO_RE ni el recorte de fuga asociado).

Los Apéndices (Apéndice D-1, esfuerzos admisibles) usan numeración
compuesta con guion ("D-1.0", "D-1.1"...) que este script NO reconoce a
propósito, mismo criterio que Título C con sus Apéndices C-A..C-F: son
contenido complementario opcional (método alterno de diseño), no el
cuerpo regulatorio principal de los 12 capítulos. Se pueden extraer
aparte más adelante si hace falta.

Uso: python scripts/ingesta/nsr10/extract_nsr10_titulo_d.py
"""
import json
import re
from pathlib import Path

NSR10_DIR = Path(__file__).resolve().parent
ROOT = NSR10_DIR.parents[2]
RAW_PATH = NSR10_DIR / "raw" / "titulo_d_raw.txt"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "nsr10"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DASH = r"[-–—−]"  # hyphen, en-dash, em-dash, signo menos

# Encabezado repetido en cada página ("NSR-10 – Capítulo D.N – <nombre>")
# y el marcador de número de página ("D-NN" en su propia línea).
HEADER_RE = re.compile(rf"NSR-10\s*{DASH}\s*Cap[íi]tulo\s+D\.\d{{1,2}}\s*{DASH}[^\n]*\n?", re.IGNORECASE)
PAGE_MARKER_RE = re.compile(r"\n\s*D-\d{1,3}\s*\n")

# Puntos de relleno de tabla (ej. "Compresión axial................ 0.60")
# -- ruido visual del PDF para alinear columnas, no contenido real.
# Verificado real en Título D: 15 ocurrencias de 4+ puntos seguidos en el
# texto crudo antes de este fix. Mismo bug real ya encontrado y corregido
# en Título C (afectaba directamente la recuperación de la tabla D.4-1 de
# factores phi, referenciada en NSR10-D-Cap4... — se previene aquí desde
# el principio, no se espera a que un test lo detecte de nuevo).
DOT_LEADER_RE = re.compile(r"\s*\.{3,}\s*")

# REGLAMENTO: "D.N.N[.N[.N[.N]]] – <título>" (vinculante, lo único que
# existe en este título -- no hay COMENTARIO que distinguir).
REGLAMENTO_RE = re.compile(rf"\nD\.(\d{{1,2}}(?:\.\d{{1,3}}){{0,4}})\s*{DASH}\s*")


def clean_raw(text: str) -> str:
    text = HEADER_RE.sub("\n", text)
    text = PAGE_MARKER_RE.sub("\n", text)
    text = DOT_LEADER_RE.sub(": ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def find_body_start(text: str) -> int:
    matches = list(re.finditer(rf"CAP[ÍI]TULO\s+D\.1\s*\n?\s*REQUISITOS GENERALES", text))
    if not matches:
        raise RuntimeError("No se encontró el inicio real del cuerpo ('CAPÍTULO D.1 REQUISITOS GENERALES')")
    # A diferencia de Título C, esta fuente (Google Drive, ya recortada
    # por rango de página real) no repite el encabezado en una portada o
    # índice previo -- un solo match real, verificado contando antes de
    # asumir "última ocurrencia" como en el script de C.
    return matches[0].start()


APENDICE_RE = re.compile(r"\nAP[ÉE]NDICE\s+D-1\b")


def cap_before_apendices(body: str) -> str:
    """Igual que en Título C: el Apéndice D-1 usa numeración compuesta con
    guion ("D-1.0", "D-1.1"...) que REGLAMENTO_RE no reconoce -- sin este
    corte, el último marcador real de D.12 se tragaría todo el apéndice
    como su propio contenido."""
    m = APENDICE_RE.search(body)
    return body[:m.start()] if m else body


def split_articulos(body: str) -> list[dict]:
    reg_matches = [(m.start(), m.end(), m.group(1)) for m in REGLAMENTO_RE.finditer(body)]

    # Primera pasada: título/contenido crudos de cada marcador, sin
    # filtrar todavía -- se necesita el texto del padre disponible para
    # la segunda pasada aunque el propio padre no termine siendo un chunk.
    raw: list[dict] = []
    for i, (start, end, num) in enumerate(reg_matches):
        rest = body[end:]
        newline_idx = rest.find("\n")
        titulo = rest[:newline_idx].strip() if newline_idx != -1 else rest[:120].strip()
        content_start = end + (newline_idx if newline_idx != -1 else 0)

        content_end = reg_matches[i + 1][0] if i + 1 < len(reg_matches) else len(body)
        content = body[content_start:content_end].strip()
        content = re.sub(r"\n{2,}", "\n", content)

        raw.append({"num": num, "titulo": titulo, "content": content})

    raw_by_num = {r["num"]: r for r in raw}

    chunks = []
    counters: dict[str, int] = {}
    for r in raw:
        num, titulo, content = r["num"], r["titulo"], r["content"]

        if len(content) < 20:
            continue

        # Un "D.N" pelado (sin sub-numeral) nunca es un encabezado real en
        # este documento -- mismo criterio verificado en Título C (todo
        # capítulo real abre con su D.N.1). Filtra referencias cruzadas
        # sueltas dentro de texto corrido (ej. "según D.3").
        if "." not in num:
            continue

        # Sin punto forzado entre título y contenido (bug real de Título C,
        # afectaba 27.6% de esos chunks): la "primera línea" tras el
        # marcador casi nunca es un título real, es solo dónde cae el
        # salto de línea de una oración que sigue corriendo en el
        # contenido. Unir con espacio simple no inventa una oración donde
        # no la hay.
        cuerpo = f"{titulo} {content}"

        # Contexto del padre en tablas enumeradas (mismo bug real de
        # Título C: numerales hijos de una tabla enumerada no repiten las
        # palabras clave de su cláusula padre). Se antepone SOLO cuando el
        # padre termina en ":" (enumeración real confirmada
        # estructuralmente) y es corto (≤300 caracteres).
        parent_num = num.rsplit(".", 1)[0] if "." in num else None
        parent = raw_by_num.get(parent_num) if parent_num else None
        if parent and parent["content"].rstrip().endswith(":") and len(parent["content"]) <= 300:
            cuerpo = f"{parent['titulo']} {parent['content']} {cuerpo}"

        embedding_ready = f"NSR-10 Título D D.{num} — {cuerpo}"
        embedding_ready = re.sub(r"\s+", " ", embedding_ready).strip()

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"NSR10-D-D_{num.replace('.', '_')}{suffix}"

        chunks.append({
            "id": chunk_id,
            "capitulo": "NSR-10 Título D — Mampostería Estructural",
            "seccion": f"D.{num}",
            "titulo": titulo[:250],
            "texto": embedding_ready,
        })
    return chunks


def main():
    raw = RAW_PATH.read_text(encoding="utf-8")
    text = clean_raw(raw)
    body = text[find_body_start(text):]
    body = cap_before_apendices(body)

    chunks = split_articulos(body)

    out_path = OUT_DIR / "titulo_d_chunks.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    with open("resumen_extraccion_d.txt", "w", encoding="utf-8") as f:
        f.write(f"Título D: {len(chunks)} chunks -> {out_path}\n")
        f.write("Primeros 5 chunks:\n")
        for c in chunks[:5]:
            f.write(f"  {c['id']} | {c['seccion']} | {c['titulo'][:80]}\n")
        f.write("Últimos 5 chunks:\n")
        for c in chunks[-5:]:
            f.write(f"  {c['id']} | {c['seccion']} | {c['titulo'][:80]}\n")

    print(f"Título D: {len(chunks)} chunks -> {out_path}")


if __name__ == "__main__":
    main()
