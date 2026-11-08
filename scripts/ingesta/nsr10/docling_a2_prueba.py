"""Prueba de Docling frente a pypdf sobre A.2.3-A.2.6 de la NSR-10. Protocolo: PROTOCOLO_DOCLING_A2.md
Uso: python docling_a2_prueba.py <carpeta_docling_aislada> <carpeta_cache_hf>"""
from __future__ import annotations

import ast
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, sys.argv[1])
os.environ["HF_HOME"] = sys.argv[2]

import pypdf  # noqa: E402
import psutil  # noqa: E402

PDF = AQUI / "raw" / "NSR-10-56-81.pdf"
PAG_INI, PAG_FIN = 3, 17
GRUPOS = {"tablas_3_4": (3, 4), "tablas_10_12": (10, 12), "tabla_14": (14, 14), "espectro_15_17": (15, 17)}
SECCIONES = ("A.2.3", "A.2.4", "A.2.5", "A.2.6")
RE_NUM = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?(?![\w])")
RE_NUMERAL = re.compile(r"A\.\d+(?:\.\d+)*(?:-\d+)?")


def sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn").strip()


def fichas_num(t: str) -> set[str]:
    out = set()
    for m in RE_NUM.findall(t):
        n = m.replace(",", ".")
        if "." in n or len(n) >= 3:
            out.add(n)
    return out


def fichas_numeral(t: str) -> set[str]:
    return {m.rstrip(".") for m in RE_NUMERAL.findall(t)}


def referencia() -> tuple[str, dict]:
    arbol = ast.parse((AQUI / "_ingest_titulo_a_a2_verbatim.py").read_text(encoding="utf-8"))
    textos, filas = [], {}
    for n in ast.walk(arbol):
        if not isinstance(n, ast.Dict):
            continue
        r = {k.value: (v.value if isinstance(v, ast.Constant) else None) for k, v in zip(n.keys, n.values) if isinstance(k, ast.Constant)}
        sec = str(r.get("seccion") or "")
        if sec.startswith(SECCIONES) and r.get("texto"):
            textos.append(r["texto"])
            if sec.startswith("A.2.3"):
                for ln in r["texto"].splitlines():
                    p = [c.strip() for c in ln.split("|")]
                    if len(p) == 4 and re.fullmatch(r"0\.\d\d", p[1]) and re.fullmatch(r"0\.\d\d", p[2]):
                        filas[sin_acentos(p[0])] = (p[1], p[2])
    return "\n".join(textos), filas


def recalls(ref: str, out: str) -> dict:
    rn, on = fichas_num(ref), fichas_num(out)
    rl, ol = fichas_numeral(ref), fichas_numeral(out)
    return {"fichas_numericas_ref": len(rn), "recall_numerico": len(rn & on) / len(rn), "faltan_num": sorted(rn - on)[:40],
            "fichas_numeral_ref": len(rl), "recall_numeral": len(rl & ol) / len(rl), "faltan_numeral": sorted(rl - ol)[:40]}


def main() -> None:
    ref, filas_ref = referencia()
    lector = pypdf.PdfReader(str(PDF))
    pag_pypdf = {i: (lector.pages[i - 1].extract_text() or "") for i in range(PAG_INI, PAG_FIN + 1)}
    from docling.document_converter import DocumentConverter  # noqa: E402

    proc = psutil.Process()
    t0 = time.time()
    conv = DocumentConverter()
    t_carga = time.time() - t0
    t1 = time.time()
    res = conv.convert(str(PDF), page_range=(PAG_INI, PAG_FIN))
    t_conv = time.time() - t1
    doc = res.document
    md_total = doc.export_to_markdown()
    R = {"referencia_chars": len(ref), "filas_tabla_A_2_3_2_ref": len(filas_ref), "tiempo_carga_s": round(t_carga, 1),
         "tiempo_conversion_s": round(t_conv, 1), "rss_mb": round(proc.memory_info().rss / 1e6)}
    R["total"] = {"pypdf": recalls(ref, "\n".join(pag_pypdf.values())), "docling": recalls(ref, md_total)}
    # por grupo de paginas (Docling por pagina)
    R["por_grupo"] = {}
    for g, (a, b) in GRUPOS.items():
        txt_py = "\n".join(pag_pypdf[i] for i in range(a, b + 1))
        txt_do = doc.export_to_markdown(page_no=None) if False else "\n".join(doc.export_to_markdown(page_no=i) for i in range(a, b + 1))
        R["por_grupo"][g] = {"pypdf": {k: v for k, v in recalls(ref, txt_py).items() if k.startswith("recall")},
                             "docling": {k: v for k, v in recalls(ref, txt_do).items() if k.startswith("recall")}}
    # tabla A.2.3-2 en Docling
    ok = tot = 0
    for tb in doc.tables:
        try:
            df = tb.export_to_dataframe(doc)
        except Exception:
            continue
        for fila in df.astype(str).values.tolist():
            nombre = sin_acentos(fila[0]) if fila else ""
            nums = [c.strip() for c in fila[1:3]]
            if nombre in filas_ref:
                tot += 1
                ok += int(tuple(nums) == filas_ref[nombre])
    R["tabla_A_2_3_2"] = {"filas_docling_con_nombre_de_referencia": tot, "filas_iguales_a_la_referencia": ok, "filas_referencia": len(filas_ref)}
    R["n_tablas_docling"] = len(doc.tables)
    (AQUI / "docling_a2_resultados.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    (Path(sys.argv[2]) / "docling_a2.md").write_text(md_total, encoding="utf-8")
    print(json.dumps({k: v for k, v in R.items() if k != "total"}, ensure_ascii=False, indent=1))
    for m in ("pypdf", "docling"):
        t = R["total"][m]
        print(m, "recall numerico", round(t["recall_numerico"], 3), "de", t["fichas_numericas_ref"], "| numeral", round(t["recall_numeral"], 3), "de", t["fichas_numeral_ref"])


if __name__ == "__main__":
    main()
