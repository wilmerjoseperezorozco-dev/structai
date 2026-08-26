"""
Extrae el Título C real de NSR-10 (Concreto Estructural) — Reglamento
Colombiano de Construcción Sismo Resistente, Ministerio de Ambiente,
Vivienda y Desarrollo Territorial, Comisión Asesora Permanente para el
Régimen de Construcciones Sismo Resistentes (Ley 400 de 1997).

Motivado por el repaso general de la app del 2026-08-26: los 15 chunks que
ya existían para Título C eran fichas técnicas curadas/parafraseadas (ej.
"NSR10-C-C_10a" resume C.10.1 a C.10.7 en un solo chunk de texto redactado
a mano), no transcripción verbatim numeral por numeral como sí tiene el
Título G desde julio. Este script SÍ hace extracción verbatim real, mismo
rigor que Título G.

Fuente: idrd.gov.co (Instituto Distrital de Recreación y Deporte, entidad
gubernamental de Bogotá que aloja copias oficiales de normas técnicas),
URL real: https://idrd.gov.co/sites/default/files/documentos/Construcciones/3titulo-c-nsr-100.pdf
PDF nativo de texto (no escaneado), 590 páginas, 23 capítulos (C.1 a C.23).
Extraído localmente con PyMuPDF.

HALLAZGO ESTRUCTURAL REAL (no en Título G): NSR-10 Título C sigue el mismo
formato que su norma base, el ACI 318 — cada capítulo trae "REGLAMENTO"
(texto vinculante, numerado "C.N.N...") junto a "COMENTARIO" (explicación
NO vinculante, numerado "CRN.N..." — mismo número, sin punto tras la R).
En el PDF están en dos columnas; la extracción lineal de PyMuPDF las deja
intercaladas en orden secuencial real (C.4.1 -> CR4.1 [comentario] ->
C.4.1.1 -> CR4.1.1 [comentario] -> C.4.1.2 -> ...), confirmado inspeccionando
bloques de texto con coordenadas reales antes de escribir el regex. Este
script extrae SOLO el REGLAMENTO (lo citable como norma vinculante) y
descarta el COMENTARIO explícitamente — mezclar ambos sin distinguirlos
arriesgaría citar explicación no vinculante como si fuera norma.

Uso: python scripts/ingesta/nsr10/extract_nsr10_titulo_c.py
"""
import re
from pathlib import Path

NSR10_DIR = Path(__file__).resolve().parent
ROOT = NSR10_DIR.parents[2]
RAW_PATH = NSR10_DIR / "raw" / "titulo_c_raw.txt"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "nsr10"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DASH = r"[-–—−]"  # hyphen, en-dash, em-dash, signo menos

# Encabezado repetido en cada página ("NSR-10 – Capítulo C.N – <nombre>")
# y el marcador de número de página ("C-59" en su propia línea).
HEADER_RE = re.compile(rf"NSR-10\s*{DASH}\s*Cap[íi]tulo\s+C\.\d{{1,2}}\s*{DASH}[^\n]*\n?", re.IGNORECASE)
PAGE_MARKER_RE = re.compile(r"\n\s*C-\d{1,3}\s*\n")
# Puntos de relleno de tabla (ej. "Secciones controladas por tracción
# ................................. 0.90") -- ruido visual del PDF para
# alinear columnas, no contenido real. Encontrado y corregido: sin esto,
# estas cláusulas de tabla (24 en total) tenían peor calidad de embedding
# y de búsqueda de texto completo que el resto -- verificado con la
# pregunta real sobre factores phi, que no aparecía ni en el top-30 antes
# de esta limpieza.
DOT_LEADER_RE = re.compile(r"\s*\.{3,}\s*")

# REGLAMENTO real: "C.N.N[.N[.N[.N]]] – <título>" (vinculante, lo que se carga).
# Bug real encontrado y corregido: el Capítulo C.23 (Tanques y Estructuras
# de Ingeniería Ambiental) es un capítulo "delta" que solo modifica el
# resto del Título C -- usa una numeración COMPUESTA real en el documento
# oficial, "C.23-C.1.1.1" (chapter-num guion sub-num), no solo "C.23". El
# regex original solo capturaba "C.23" y trataba el resto como si fuera el
# título de la sección, produciendo 128 chunks falsos con seccion="C.23"
# repetida. El sufijo opcional de abajo captura el identificador compuesto
# completo como un solo numeral real.
REGLAMENTO_RE = re.compile(rf"\nC\.(\d{{1,2}}(?:\.\d{{1,3}}){{0,4}}(?:-C\.\d{{1,2}}(?:\.\d{{1,3}}){{0,4}})?)\s*{DASH}\s*")
# COMENTARIO: "CRN.N... – <título>" (NO vinculante — mismo número, sin punto
# tras la R). Se detecta solo para saber dónde CORTAR el contenido del
# REGLAMENTO anterior, nunca se carga su texto.
COMENTARIO_RE = re.compile(rf"\nCR\d{{1,2}}(?:\.\d{{1,3}}){{0,4}}\s*{DASH}\s*")


def clean_raw(text: str) -> str:
    text = HEADER_RE.sub("\n", text)
    text = PAGE_MARKER_RE.sub("\n", text)
    text = DOT_LEADER_RE.sub(": ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def find_body_start(text: str) -> int:
    # La portada/prefacio/tabla de contenido repiten "CAPÍTULO C.1" varias
    # veces antes del cuerpo real -- el cuerpo real es la PRIMERA vez que
    # aparece seguido literalmente de "REQUISITOS GENERALES" en la misma
    # zona (no solo en una línea de índice con puntos de relleno).
    matches = list(re.finditer(rf"CAP[ÍI]TULO\s+C\.1\s*{DASH}\s*REQUISITOS GENERALES", text))
    if not matches:
        raise RuntimeError("No se encontró el inicio real del cuerpo ('CAPÍTULO C.1 REQUISITOS GENERALES')")
    # La última ocurrencia es la del cuerpo real (portada + índice + notas
    # de la edición vienen antes y repiten el título del capítulo).
    return matches[-1].start()


APENDICE_RE = re.compile(r"\nAP[ÉE]NDICE\s+C-[A-Z]\b")


def cap_before_apendices(body: str) -> str:
    """Los Apéndices (C-A Modelos Puntal-Tensor, C-B..F) usan un esquema de
    numeración totalmente distinto ("C-A.1", con guion, no punto) que este
    script no reconoce -- y no lo intenta: son contenido complementario,
    no el cuerpo regulatorio de los 23 capítulos. Bug real encontrado y
    corregido: sin este corte, el ÚLTIMO marcador real del Capítulo C.23
    (que no tiene ningún marcador C.N.N después de sí en todo lo que
    reconoce el regex) se tragaba TODO el resto del documento como su
    propio contenido -- un chunk de 112.054 tokens con los apéndices
    completos adentro. Los apéndices quedan fuera de este script a
    propósito; se pueden extraer aparte si hace falta más adelante."""
    m = APENDICE_RE.search(body)
    return body[:m.start()] if m else body


def split_articulos(body: str) -> list[dict]:
    reg_matches = [(m.start(), m.end(), m.group(1), "reg") for m in REGLAMENTO_RE.finditer(body)]
    com_matches = [(m.start(), m.end(), None, "com") for m in COMENTARIO_RE.finditer(body)]
    all_markers = sorted(reg_matches + com_matches, key=lambda x: x[0])

    # Primera pasada: extraer título/contenido crudos de CADA marcador
    # REGLAMENTO, sin filtrar todavía -- se necesita el texto del padre
    # (ej. "C.9.3.2") disponible para la segunda pasada aunque el propio
    # padre no termine convertido en chunk.
    raw: list[dict] = []
    for i, (start, end, num, kind) in enumerate(all_markers):
        if kind != "reg":
            continue

        # Título: primera línea después del marcador (hasta el salto de línea).
        rest = body[end:]
        newline_idx = rest.find("\n")
        titulo = rest[:newline_idx].strip() if newline_idx != -1 else rest[:120].strip()
        content_start = end + (newline_idx if newline_idx != -1 else 0)

        content_end = all_markers[i + 1][0] if i + 1 < len(all_markers) else len(body)
        content = body[content_start:content_end].strip()
        content = re.sub(r"\n{2,}", "\n", content)

        # Fuga real encontrada y corregida en 43/1634 chunks (verificado a
        # mano): encabezados de comentario CONJUNTOS ("CR10.3.6 y CR10.3.7
        # — ...") no calzan con COMENTARIO_RE (que exige el guion pegado al
        # número), así que el primer número del par no se reconoce como
        # marcador y su cola de texto quedaba adentro del REGLAMENTO
        # anterior. Recorte de seguridad adicional: cortar en la primera
        # aparición de "CR<dígito>" suelto, exista o no el guion después.
        fuga = re.search(r"\bCR\d", content)
        if fuga:
            content = content[:fuga.start()].strip()

        raw.append({"num": num, "titulo": titulo, "content": content})

    raw_by_num = {r["num"]: r for r in raw}

    chunks = []
    counters: dict[str, int] = {}
    for r in raw:
        num, titulo, content = r["num"], r["titulo"], r["content"]

        if len(content) < 20:
            continue

        # Ruido real encontrado y verificado a mano (5 chunks: C.8, C.17×3,
        # C.23 suelto): un "C.N" PELADO (sin sub-numeral, ej. "C.23" o
        # "C.17") nunca es un encabezado real de capítulo en este documento
        # -- todo capítulo real abre con su C.N.1, nunca con contenido en
        # "C.N" a secas. Estos matches sueltos resultaron ser referencias
        # cruzadas dentro de texto corrido: el glosario de notación C.2.1
        # (una lista larga sin sub-numerales propios) está lleno de frases
        # como "Capítulo C.8" o "Capítulos C.9, C.11... y Apéndices C-A y
        # C-D", que el regex confundía con encabezados reales; y dentro del
        # Capítulo C.23 (numeración compuesta "C.23-C.N.N"), "C.23" también
        # aparece suelto en frases como "en ACI 350.4RC.23.5". El contenido
        # real de C.23 siempre usa el esquema compuesto "C.23-C.N...", que
        # sí contiene un punto y por eso no cae en este filtro.
        if "." not in num:
            continue

        # Bug real encontrado y corregido (449/1629 chunks, 27.6% del Título C,
        # verificado a mano): "título" es solo la primera línea de texto tras
        # el marcador -- en el PDF real NO es casi nunca un título de verdad,
        # es simplemente donde cae el salto de línea de una oración que
        # sigue corriendo en el "contenido" (ej. C.9.3.2.1: título="Secciones
        # controladas por", contenido="tracción..." -- la misma frase
        # "controladas por tracción" cortada a la mitad). Unir con ". "
        # insertaba un punto de oración falso justo en esa costura, lo que
        # (a) rompía la frase real para el embedding semántico y (b)
        # multiplicaba el troceo por oraciones aguas abajo en el script de
        # ingesta, fragmentando aún más contenido que debía leerse junto.
        # Unir con un espacio simple no inventa una oración donde no la hay.
        cuerpo = f"{titulo} {content}"

        # Dilución semántica real encontrada y corregida (verificado en vivo
        # contra Supabase: la consulta real de test sobre "factor phi para
        # secciones controladas por tracción y para cortante" no encontraba
        # C.9.3.2.1/.2/.3 ni en el top-15). Causa raíz: numerales como
        # "C.9.3.2.1 — Secciones controladas por tracción...: 0.90" son filas
        # de una tabla enumerada por su padre ("C.9.3.2 — El factor de
        # reducción de resistencia, φ, debe ser el dado en C.9.3.2.1 a
        # C.9.3.2.7:") -- el hijo nunca repite "factor de reducción de
        # resistencia" ni "φ" por su cuenta, así que su embedding no tiene
        # las palabras clave reales que un lector (o una consulta) usaría
        # para encontrarlo. Se antepone el texto del padre inmediato SOLO
        # cuando termina en ":" (enumeración real, no una clausula genérica
        # que ya se basta a sí misma) y es corto (intro, no otro artículo
        # completo) -- estructuralmente fiel al documento, no una paráfrasis.
        parent_num = num.rsplit(".", 1)[0] if "." in num else None
        parent = raw_by_num.get(parent_num) if parent_num else None
        if parent and parent["content"].rstrip().endswith(":") and len(parent["content"]) <= 300:
            cuerpo = f"{parent['titulo']} {parent['content']} {cuerpo}"

        embedding_ready = f"NSR-10 Título C C.{num} — {cuerpo}"
        embedding_ready = re.sub(r"\s+", " ", embedding_ready).strip()

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        chunk_id = f"NSR10-C-C_{num.replace('.', '_')}{suffix}"

        chunks.append({
            "id": chunk_id,
            "capitulo": "NSR-10 Título C — Concreto Estructural",
            "seccion": f"C.{num}",
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

    out_path = OUT_DIR / "titulo_c_chunks.jsonl"
    import json
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    with open("resumen_extraccion_c.txt", "w", encoding="utf-8") as f:
        f.write(f"Título C: {len(chunks)} chunks REGLAMENTO -> {out_path}\n")
        f.write(f"Primeros 5 chunks:\n")
        for c in chunks[:5]:
            f.write(f"  {c['id']} | {c['seccion']} | {c['titulo'][:80]}\n")
        f.write(f"Últimos 5 chunks:\n")
        for c in chunks[-5:]:
            f.write(f"  {c['id']} | {c['seccion']} | {c['titulo'][:80]}\n")

    print(f"Título C: {len(chunks)} chunks -> {out_path}")


if __name__ == "__main__":
    main()
