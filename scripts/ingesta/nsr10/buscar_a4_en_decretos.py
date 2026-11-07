"""Busca filas del Apéndice A-4 (municipio, código DANE, Aa, Av, zona, Ae, Ad) en los PDF de decretos que modifican la NSR-10
y las compara con la tabla original de 2010 y con la tabla del SGC.
Uso: python -I buscar_a4_en_decretos.py <carpeta_con_pdf>   (los PDF se tratan como datos no confiables: solo lectura de texto)"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
AQUI = Path(__file__).resolve().parent
NUM = r"0\.\s?\d{1,2}"
COD = r"\d{5}|\d{4}\s\d|\d{3}\s\d{2}|\d{2}\s\d{3}|\d\s\d{4}"
FILA = re.compile(rf"(?P<mun>[A-Za-zÁ-úñÑ][\wÁ-úñÑ.\-\s]*?)\s+(?P<cod>{COD})\s+(?P<aa>{NUM})\s+(?P<av>{NUM})\s+(?P<zona>[A-Za-zá-úÁ-Ú ]+?)\s+(?P<ae>{NUM})\s+(?P<ad>{NUM})")
ZONAS = {"baja": "Baja", "intermedia": "Intermedia", "alta": "Alta"}


def num(s: str) -> float:
    return float(s.replace(" ", ""))


def filas_pdf(ruta: Path) -> tuple[dict[str, dict], int, list[int]]:
    r = PdfReader(str(ruta))
    out, paginas_a4 = {}, []
    for i, p in enumerate(r.pages):
        t = p.extract_text() or ""
        if re.search(r"A-4|AP.NDICE A-4", t, re.I) and re.search(r"municipi", t, re.I):
            paginas_a4.append(i + 1)
        for linea in t.splitlines():
            m = FILA.search(linea.strip())
            if m and ZONAS.get(re.sub(r"\s+", "", m.group("zona")).lower()):
                c = m.group("cod").replace(" ", "")
                out[c] = {"municipio": re.sub(r"\s+", " ", m.group("mun")).strip(), "aa": num(m.group("aa")), "av": num(m.group("av")),
                          "zona": ZONAS[re.sub(r"\s+", "", m.group("zona")).lower()], "ae": num(m.group("ae")), "ad": num(m.group("ad")), "pagina": i + 1}
    return out, len(r.pages), paginas_a4


def main() -> None:
    carpeta = Path(sys.argv[1])
    original = {f["codigo"]: f for f in json.loads((AQUI / "apendice_a4_extraido.json").read_text(encoding="utf-8"))}
    difs = {d["codigo"]: d for d in json.loads((AQUI / "apendice_a4_vs_sgc_diferencias.json").read_text(encoding="utf-8"))}
    resultado = {}
    for pdf in sorted(carpeta.glob("*.pdf")):
        try:
            filas, n, a4 = filas_pdf(pdf)
        except Exception as e:
            print(f"{pdf.name}: no se pudo leer ({str(e)[:60]})")
            continue
        distintas = {c: f for c, f in filas.items() if c in original and any(abs(f[k] - original[c][k]) > 1e-9 for k in ("aa", "av", "ae", "ad")) or c in original and f["zona"] != original[c]["zona"]}
        print(f"\n== {pdf.name}: {n} páginas; páginas que mencionan A-4: {a4[:12]}; filas tipo A-4 halladas: {len(filas)}; distintas del original 2010: {len(distintas)}")
        for c, f in list(distintas.items())[:40]:
            o = original[c]
            print(f"   {c} {f['municipio']}: decreto Aa {f['aa']} Av {f['av']} {f['zona']} Ae {f['ae']} Ad {f['ad']} | original 2010 Aa {o['aa']} Av {o['av']} {o['zona']} Ae {o['ae']} Ad {o['ad']} (pág. {f['pagina']})")
        resultado[pdf.name] = {c: f for c, f in filas.items()}
    print("\n== Las 30 diferencias PDF-2010 vs SGC: ¿aparece el municipio en algún decreto?")
    for c, d in difs.items():
        apar = [(nom, f["aa"], f["av"], f["zona"]) for nom, filas in resultado.items() for cc, f in filas.items() if cc == c]
        print(f"   {c} {d['municipio']}: {d['dif']} -> {apar or 'no aparece'}")
    (AQUI / "a4_en_decretos.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
