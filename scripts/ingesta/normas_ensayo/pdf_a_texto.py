"""
Convierte los PDF del manual INVIAS 2012 (Normas de Ensayo de Materiales para Carreteras) a texto plano
con PyMuPDF, en el orden real de lectura, para extract_normas_ensayo_secciones.py.

Los PDF son archivos descargados (datos no confiables): deben estar en una carpeta propia y este script
se corre con `python -I`, pasando la carpeta como argumento. No ejecuta nada del PDF; solo extrae texto.

Uso: python -I scripts/ingesta/normas_ensayo/pdf_a_texto.py C:/Users/wilme/dev/descargas/inv_e_2012

Archivos esperados (nombres del paquete original; se aceptan con o sin tilde dañada):
  SECCIÓN 100.pdf, SECCIÓN 400.pdf, SECCIÓN 600.pdf,
  SECCIONES 700 Y 800 (primera parte).pdf, SECCIONES 700 Y 800 (segunda parte)mod_2013-NOV-15.pdf
"""
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "scripts" / "_normas_ensayo_raw_drive_dump"

# (patrón sobre el nombre del PDF, archivo de salida)
MAPA = [
    (r"SECCI.?N 100\b", "seccion_100.txt"),
    (r"SECCI.?N 200\b", "seccion_200.txt"),
    (r"SECCI.?N 300\b", "seccion_300.txt"),
    (r"SECCI.?N 400\b", "seccion_400.txt"),
    (r"SECCI.?N 600\b", "seccion_600.txt"),
    (r"700 Y 800 \(primera", "seccion_700_800_a.txt"),
    (r"700 Y 800 \(segunda", "seccion_700_800_b.txt"),
]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    origen = Path(sys.argv[1])
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(origen.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"no hay PDF en {origen}")
    for pdf in pdfs:
        destino = next((d for patron, d in MAPA if re.search(patron, pdf.name, re.I)), None)
        if destino is None:
            print(f"  omitido (no es una sección esperada): {pdf.name}")
            continue
        with pymupdf.open(pdf) as doc:
            if "2012" not in "".join(doc[i].get_text() for i in range(min(3, len(doc)))):
                raise SystemExit(f"{pdf.name}: no dice 'NORMAS Y ESPECIFICACIONES 2012' en las primeras páginas; "
                                 "¿es la edición 2007 (superada)? No se procesa.")
            texto = "\n".join(p.get_text() for p in doc)
            paginas = len(doc)
        (RAW_DIR / destino).write_text(texto, encoding="utf-8")
        print(f"  {pdf.name} -> {destino}: {paginas} páginas, {len(texto):,} caracteres")


if __name__ == "__main__":
    main()
