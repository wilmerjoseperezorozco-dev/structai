"""
Extrae las cartillas de precios de referencia de EPC (Empresas Públicas de Cundinamarca), 2021–2026, a formato largo.

Fuente: anterior.epc.com.co/apu/ (2021–2025) y epc.com.co/precios-referencia-epc-2026/ (2026). Documentos públicos
descargados el 2026-11-12 a scripts/ingesta/epc/raw/ (gitignored). Solo se leen: son datos de terceros.

Estructura de cada cartilla: una tabla por página con DESCRIPCIÓN, UNIDAD y una columna de precio por MUNICIPIO de la
provincia (hasta 2025 además una columna CÓDIGO jerárquico 1 / 1.1 / 1.1.1). Filas sin unidad ni precio son
encabezados (capítulo o subcapítulo). El texto de cada celda se lee por su rectángulo (get_textbox) porque la
extracción directa de tablas pega las palabras.

Salida (una fila por actividad × municipio × año):
  scripts/ingesta/epc/salida/epc_precios_largo.csv
  columnas: anio, provincia, municipio, codigo, capitulo, subcapitulo, actividad, unidad, precio, archivo, pagina
y un control de calidad en docs/presupuesto/EPC_EXTRACCION.md.

Uso: python scripts/ingesta/epc/extraer_cartillas_epc.py
"""
from __future__ import annotations

import collections
import csv
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
RAW = AQUI / "raw"
SALIDA = AQUI / "salida" / "epc_precios_largo.csv"
INFORME = RAIZ / "docs" / "presupuesto" / "EPC_EXTRACCION.md"
RX_PRECIO_ES = re.compile(r"^\d{1,3}(\.\d{3})*(,\d{1,2})?$")
RX_PRECIO_EN = re.compile(r"^\d{1,3}(,\d{3})*(\.\d{1,2})?$")
RX_CODIGO = re.compile(r"^\d+(\.\d+)*\.?$")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", s).strip()


def limpiar(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\n", " ")).strip()


def precio(s: str | None) -> float | None:
    t = limpiar(s).replace("$", "").replace(" ", "")
    if not t or t in ("-", "N/A", "NA"):
        return None
    if RX_PRECIO_ES.match(t) and ("," in t[-3:] or "." in t):
        if "," in t:
            return float(t.replace(".", "").replace(",", "."))
        if RX_PRECIO_EN.match(t) and re.search(r"\.\d{1,2}$", t):    # 1.50 ambiguo: tratar como decimal inglés
            return float(t)
        return float(t.replace(".", ""))
    if RX_PRECIO_EN.match(t):
        return float(t.replace(",", ""))
    try:
        return float(t)
    except ValueError:
        return None


def textos_fila(palabras, fila) -> list[str]:
    """Texto de cada celda a partir de las palabras de la página (leídas UNA vez por página): una palabra pertenece
    a la celda que contiene su centro. Mucho más rápido que get_textbox por celda (la primera versión tardaba horas)."""
    out = []
    for c in fila.cells:
        if not c:
            out.append("")
            continue
        x0, y0, x1, y1 = c
        dentro = [w for w in palabras if x0 <= (w[0] + w[2]) / 2 <= x1 and y0 <= (w[1] + w[3]) / 2 <= y1]
        dentro.sort(key=lambda w: (round(w[1], 0), w[0]))
        out.append(limpiar(" ".join(w[4] for w in dentro)))
    return out


def meta_archivo(nombre: str) -> tuple[str, int]:
    m = re.match(r"(?i)cartilla[- ](.+?)[- ](20\d{2})\.pdf$", nombre)
    return m.group(1).replace("-", " ").upper(), int(m.group(2))


def extraer(pdf: Path) -> tuple[list[dict], dict]:
    provincia, anio = meta_archivo(pdf.name)
    filas_out, info = [], collections.Counter()
    municipios, i_desc, i_uni, i_cod = None, None, None, None
    capitulo = subcapitulo = None
    pendiente_cap = None       # encabezado visto; si le sigue otro encabezado, era capítulo
    doc = pymupdf.open(pdf)
    for np_, page in enumerate(doc, 1):
        palabras = page.get_text("words")
        for tab in page.find_tables().tables:
            for fila in tab.rows:
                t = textos_fila(palabras, fila)
                tn = [norm(x) for x in t]
                if any(x.startswith("DESCRIPCI") for x in tn) and "UNIDAD" in tn:
                    i_desc = next(i for i, x in enumerate(tn) if x.startswith("DESCRIPCI"))
                    i_uni = tn.index("UNIDAD")
                    i_cod = next((i for i, x in enumerate(tn) if x.startswith("CODIGO")), None)
                    municipios = [(i, t[i]) for i in range(i_uni + 1, len(t)) if t[i]]
                    info["encabezados"] += 1
                    continue
                if municipios is None or i_desc is None or i_desc >= len(t):
                    continue
                desc = t[i_desc]
                uni = t[i_uni] if i_uni < len(t) else ""
                cod = t[i_cod] if i_cod is not None and i_cod < len(t) else ""
                precios = {m: precio(t[i]) for i, m in municipios if i < len(t)}
                hay_precio = any(v is not None for v in precios.values())
                if not desc:
                    continue
                if not uni and not hay_precio:
                    # Encabezado. Con código: el nivel lo da el número de puntos. Sin código: heurística.
                    if cod and RX_CODIGO.match(cod):
                        nivel = cod.rstrip(".").count(".")
                        if nivel == 0:
                            capitulo, subcapitulo = desc, None
                        else:
                            subcapitulo = desc
                    else:
                        if pendiente_cap is not None:
                            capitulo = pendiente_cap
                        pendiente_cap = desc
                        subcapitulo = desc
                    info["encabezados_capitulo"] += 1
                    continue
                if pendiente_cap is not None and not cod:
                    pendiente_cap = None      # el último encabezado antes de un ítem es subcapítulo
                if not hay_precio:
                    info["items_sin_precio"] += 1
                for m, v in precios.items():
                    if v is None:
                        continue
                    filas_out.append({"anio": anio, "provincia": provincia, "municipio": m, "codigo": cod,
                                      "capitulo": capitulo, "subcapitulo": subcapitulo, "actividad": desc,
                                      "unidad": uni, "precio": v, "archivo": pdf.name, "pagina": np_})
                info["items"] += 1
    info["municipios"] = len(municipios or [])
    return filas_out, info


def main() -> None:
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    partes = SALIDA.parent / "partes"
    partes.mkdir(exist_ok=True)
    todas, resumen = [], []
    campos = ["anio", "provincia", "municipio", "codigo", "capitulo", "subcapitulo", "actividad", "unidad", "precio",
              "archivo", "pagina"]
    for pdf in sorted(RAW.glob("CARTILLA-*.pdf")):
        parte = partes / (pdf.stem + ".csv")
        if parte.exists():                       # retomar: la cartilla ya se extrajo
            with parte.open(encoding="utf-8") as fh:
                filas = list(csv.DictReader(fh))
            info = collections.Counter(items=len({(f["actividad"], f["unidad"], f["pagina"]) for f in filas}),
                                       municipios=len({f["municipio"] for f in filas}))
        else:
            filas, info = extraer(pdf)
            with parte.open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=campos)
                w.writeheader()
                w.writerows(filas)
        todas += filas
        resumen.append((pdf.name, info))
        print(f"{pdf.name:40s} ítems={info['items']:4d} municipios={info['municipios']:2d} filas={len(filas)}", flush=True)
    with SALIDA.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(todas[0]))
        w.writeheader()
        w.writerows(todas)

    por_anio = collections.Counter(f["anio"] for f in todas)
    munis = {(f["provincia"], f["municipio"]) for f in todas}
    acts = {(norm(f["actividad"]), norm(f["unidad"])) for f in todas}
    sin_cap = sum(1 for f in todas if not f["capitulo"])
    l = ["# Extracción de las cartillas de precios de EPC (2021–2026)", "",
         "Generado por `scripts/ingesta/epc/extraer_cartillas_epc.py`. Fuente pública: Empresas Públicas de "
         "Cundinamarca (EPC), listas de precios de referencia por provincia, adoptadas por Decisión Empresarial anual. "
         "PDF en `scripts/ingesta/epc/raw/` (gitignored); salida en `scripts/ingesta/epc/salida/`.", "",
         f"- Cartillas: **{len(resumen)}** (15 provincias × 6 años). Filas (actividad × municipio × año): **{len(todas):,}**.",
         f"- Municipios: **{len(munis)}**. Actividades distintas (descripción + unidad): **{len(acts):,}**.",
         f"- Filas por año: " + ", ".join(f"{a}: {n:,}" for a, n in sorted(por_anio.items())),
         f"- Filas sin capítulo asignado: {sin_cap:,}.", "",
         "| Cartilla | Ítems | Municipios | Filas | Ítems sin precio |", "|---|---|---|---|---|"]
    for nombre, info in resumen:
        l.append(f"| {nombre} | {info['items']} | {info['municipios']} | "
                 f"{sum(1 for f in todas if f['archivo'] == nombre):,} | {info['items_sin_precio']} |")
    INFORME.write_text("\n".join(l) + "\n", encoding="utf-8")
    print("\n".join(l[:9]))


if __name__ == "__main__":
    sys.exit(main())
