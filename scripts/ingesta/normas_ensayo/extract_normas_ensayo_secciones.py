"""
Extrae las normas de ensayo INV-E reales de los archivos grandes "SECCIÓN
NNN.pdf" del paquete "Normas de Ensayo de Materiales para Carreteras"
(INVIAS, edición 2012) — cada archivo de Sección contiene MÚLTIPLES normas
INV-E individuales concatenadas (ej. Sección 200 = Agregados Pétreos, trae
las normas E-201 a E-245 seguidas una tras otra).

Extracción de dos niveles:
  1. Se detectan los límites reales entre normas individuales buscando el
     patrón "INV E – NNN – YY" (numeral + año de la versión) — cada norma
     nueva referencia su PROPIO número la primera vez que aparece. Como las
     normas se presentan en orden numérico ascendente dentro del archivo,
     se usa una heurística de secuencia monótona creciente para descartar
     referencias cruzadas hacia atrás dentro del cuerpo de otra norma (ej.
     "...ver la norma INV E-141..." mencionada dentro de la norma E-232).
  2. Dentro de cada norma individual, se segmenta por numeral de cláusula
     real ("1 OBJETO", "5.2 PROCEDIMIENTO"...) — mismo patrón ya validado
     en extract_normas_ensayo.py para los 3 pilotos INV E-631/632/826.

Fuente: PDFs descargados vía Drive y extraídos LOCALMENTE con PyMuPDF —
la herramienta read_file_content de Drive revuelve el orden de lectura en
estos documentos (columna lateral con "NORMAS Y ESPECIFICACIONES 2012
INVIAS" mezclada con el cuerpo), mientras PyMuPDF con get_text() por
defecto preserva el orden real de lectura. Verificado manualmente antes de
confiar en el patrón (ver scratchpad de la sesión 2026-07-14).

Uso: python -I scripts/ingesta/normas_ensayo/extract_normas_ensayo_secciones.py  (antes: pdf_a_texto.py)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "scripts" / "_normas_ensayo_raw_drive_dump"
OUT_DIR = ROOT / "packages" / "construdata" / "normativa_raw" / "vias"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SECCIONES = {
    "seccion_200": {
        "raw_file": "seccion_200.txt",
        "rango": (200, 299),
        "titulo_completo": "Sección 200 — Agregados Pétreos (Normas de Ensayo de Materiales para Carreteras, INVIAS 2012)",
    },
    "seccion_300": {
        "raw_file": "seccion_300.txt",
        "rango": (300, 399),
        "titulo_completo": "Sección 300 — Cemento (Normas de Ensayo de Materiales para Carreteras, INVIAS 2012)",
    },
    # #295: secciones que faltaban (títulos según la Introducción, I.2.1, del mismo manual 2012)
    "seccion_100": {
        "raw_file": "seccion_100.txt",
        "rango": (100, 199),
        "titulo_completo": "Sección 100 — Suelos (Normas de Ensayo de Materiales para Carreteras, INVIAS 2012)",
    },
    "seccion_400": {
        "raw_file": "seccion_400.txt",
        "rango": (400, 499),
        "titulo_completo": "Sección 400 — Concreto hidráulico (Normas de Ensayo de Materiales para Carreteras, INVIAS 2012)",
    },
    "seccion_600": {
        "raw_file": "seccion_600.txt",
        "rango": (600, 699),
        "titulo_completo": "Sección 600 — Estabilización de suelos (Normas de Ensayo de Materiales para Carreteras, INVIAS 2012)",
    },
    # el manual reparte 700 y 800 en dos PDF; cada uno se procesa aparte para que la secuencia ascendente no se rompa
    "seccion_700_800_a": {
        "raw_file": "seccion_700_800_a.txt",
        "rango": (700, 899),
        "titulo_completo": "Secciones 700 y 800 — Materiales y mezclas asfálticas y prospección de pavimentos, primera parte (INVIAS 2012)",
    },
    "seccion_700_800_b": {
        "raw_file": "seccion_700_800_b.txt",
        "rango": (700, 899),
        "titulo_completo": "Secciones 700 y 800 — Materiales y mezclas asfálticas y prospección de pavimentos, segunda parte (INVIAS 2012, mod. 2013-11-15)",
    },
}

# Normas con versión posterior ya registrada (Res. 2451 de 2022: INV-E-631-22, INV-E-632-22, INV-E-826-22).
# Si aparecen en la edición 2012 no se extraen: la versión vigente es la de 2022 y ya está en motor_chunks.
NORMAS_CON_VERSION_POSTERIOR = {"631", "632", "826"}

NORMA_BOUNDARY_RE = re.compile(r'INV\.?\s*E\s*[–—-]\s*(\d{3})\s*[–—-]\s*(\d{2})')
CLAUSE_RE = re.compile(
    r'(?<=\n)(\d{1,2}(?:\.\d{1,2}){0,3})\s+([A-ZÁÉÍÓÚÑ][^\n]{2,100})(?=\n)'
)


# Líneas de encabezado/pie de página del manual 2012: no son contenido de la norma.
_RUIDO_PAGINA = re.compile(
    r'^[ \t]*(?:NORMAS Y ESPECIFICACIONES 2012 INVIAS|Instituto Nacional de V[ií]as|'
    r'Normas de Ensayo de Materiales para Carreteras|Secci[oó]n \d00\s*[–—-][^\n]*|'
    r'Secciones 700 y 800\s*[–—-][^\n]*|I\.N\.V\. E\s*-\s*\d{3}|E\s*-\s*\d{3}|E \d{3}\s*-\s*\d+)[ \t]*$',
    re.I | re.M)
MAX_PALABRAS = 150  # ~200 tokens del modelo de embeddings; cada parte repite el encabezado de la cláusula


def limpiar_paginas(text: str) -> str:
    """Quita los encabezados y pies que se repiten en cada página (antes contaminaban los chunks)."""
    return _RUIDO_PAGINA.sub("", text)


def _partir(texto: str) -> list[str]:
    palabras = texto.split()
    return [" ".join(palabras[i:i + MAX_PALABRAS]) for i in range(0, len(palabras), MAX_PALABRAS)] or [""]


def find_norma_boundaries(text: str, rango: tuple[int, int] = (0, 999)) -> list[tuple[int, str]]:
    """Devuelve [(posición_inicio, numero_norma), ...] en orden, quedándose
    solo con la primera aparición real de cada número siguiendo la
    secuencia ascendente (filtra referencias cruzadas hacia atrás).
    Solo acepta números dentro del rango de la sección: una referencia hacia
    adelante a otra sección (p. ej. «INV E-823» en la Introducción que abre el
    PDF de la Sección 100, o «INV E-805» dentro de la 600) rompería la secuencia."""
    boundaries = []
    last_num = 0
    for m in NORMA_BOUNDARY_RE.finditer(text):
        num = int(m.group(1))
        if rango[0] <= num <= rango[1] and num > last_num:
            boundaries.append((m.start(), m.group(1)))
            last_num = num
    return boundaries


def split_clauses(body: str, norma_num: str) -> list[dict]:
    matches = list(CLAUSE_RE.finditer(body))
    chunks = []
    counters: dict[str, int] = {}
    for i, m in enumerate(matches):
        num, titulo = m.group(1), m.group(2).strip().rstrip('.')
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[content_start:content_end].strip()
        content = re.sub(r'-\n(?=[a-záéíóúñ])', '', content)  # palabra partida por guion al final de línea
        content = re.sub(r'\s+', ' ', content).strip()          # un salto de línea del PDF es un espacio

        if len(content) < 30:
            continue

        # Un numeral como «1.4 Este método ... Para» no es un título: es la primera línea del párrafo.
        # Solo los encabezados en mayúsculas («5 PROCEDIMIENTO») se separan con punto.
        es_encabezado = titulo.upper() == titulo
        rotulo = titulo if es_encabezado else titulo[:80]

        counters[num] = counters.get(num, 0) + 1
        suffix = f"-{counters[num]}" if counters[num] > 1 else ""
        cuerpo = content if es_encabezado else f"{m.group(2).strip()} {content}"
        partes = _partir(cuerpo)
        for k, parte in enumerate(partes, 1):
            etiqueta = f" (parte {k}/{len(partes)})" if len(partes) > 1 else ""
            chunk_id = f"INVE{norma_num}-{num.replace('.', '_')}{suffix}" + (f"-p{k}" if len(partes) > 1 else "")
            if es_encabezado:
                embedding_ready = f"INV E-{norma_num} {num} {titulo}{etiqueta}. {parte}"
            else:
                embedding_ready = f"INV E-{norma_num} {num}{etiqueta} {parte}"
            embedding_ready = re.sub(r'\s+', ' ', embedding_ready).strip()
            chunks.append({
                "chunk_id": chunk_id,
                "seccion_origen": f"INV E-{norma_num} — {num} {rotulo}{etiqueta}",
                "titulo": rotulo[:250],
                "embedding_ready": embedding_ready,
            })
    return chunks


def split_normas(text: str, codigo_seccion: str, rango: tuple[int, int] = (0, 999)) -> list[dict]:
    boundaries = find_norma_boundaries(text, rango)
    all_chunks = []
    for i, (start, norma_num) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        if norma_num in NORMAS_CON_VERSION_POSTERIOR:
            print(f"    INV E-{norma_num}: omitida (versión 2022 vigente ya registrada)")
            continue
        body = text[start:end]
        chunks = split_clauses(body, norma_num)
        if not chunks:
            # cuerpo con muy poca estructura reconocible: no se fabrica nada,
            # se omite esa norma individual y sigue con la siguiente
            continue
        all_chunks.extend(chunks)
    return all_chunks


def write_chunk_file(codigo: str, titulo_completo: str, chunks: list[dict]) -> None:
    lines = [
        '{',
        '"metadata": {',
        f'"norma": "{titulo_completo}", "titulo_completo": "{titulo_completo}",',
        '"fuente": "INVIAS — Normas de Ensayo de Materiales para Carreteras, edición 2012, adoptada por la Resolución 1375 de 2014 (reemplaza la Resolución 3290 de 2007)",',
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

    out_path = OUT_DIR / f"{codigo}.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {codigo}.txt: {len(chunks)} chunks -> {out_path}")


def main():
    total = 0
    for codigo, meta in SECCIONES.items():
        raw_path = RAW_DIR / meta["raw_file"]
        if not raw_path.exists():
            print(f"  ADVERTENCIA: {raw_path} no existe, se omite {codigo}")
            continue
        text = limpiar_paginas(raw_path.read_text(encoding="utf-8"))
        boundaries = find_norma_boundaries(text, meta["rango"])
        print(f"  {codigo}: {len(boundaries)} normas individuales detectadas ({', '.join(n for _, n in boundaries[:5])}...{boundaries[-1][1] if boundaries else ''})")
        chunks = split_normas(text, codigo, meta["rango"])
        write_chunk_file(codigo, meta["titulo_completo"], chunks)
        total += len(chunks)
    print(f"\nTotal chunks Secciones de Normas de Ensayo: {total}")


if __name__ == "__main__":
    main()
