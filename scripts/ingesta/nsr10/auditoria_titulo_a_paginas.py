"""Cobertura de TEXTO del Titulo A por pagina: fraccion de fragmentos de 6 palabras de cada pagina del PDF fuente
que aparece en el texto de los chunks A.* de la base. Mide completitud verbatim sin depender de la columna `seccion`.
Solo lectura. Salida: auditoria_titulo_a_paginas.json
"""
from __future__ import annotations
import json, os, re, sys, unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
import pypdf
from supabase import create_client

RAW = RAIZ / "scripts" / "ingesta" / "nsr10" / "raw"
PDFS = ["43-54", "56-81", "81-94", "95-105", "106-115", "116-123", "124-128", "130-138", "140-154", "156-158", "160-166", "168-181", "183-190", "191-218"]
K = 6

def norm(s: str) -> list[str]:
    s = unicodedata.normalize("NFKD", s).lower()
    return re.findall(r"[a-z0-9]+", "".join(c for c in s if not unicodedata.combining(c)))

def sh(pal: list[str]) -> list[str]:
    return [" ".join(pal[i:i + K]) for i in range(0, max(len(pal) - K + 1, 0))]

def main():
    load_dotenv(RAIZ / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    filas, ini = [], 0
    while True:
        lote = sb.table("nsr10_chunks").select("id,texto").ilike("id", "NSR10-A%").range(ini, ini + 999).execute().data
        filas += lote
        if len(lote) < 1000:
            break
        ini += 1000
    base = set()
    for f in filas:
        base.update(sh(norm(f["texto"] or "")))
    print(f"chunks Titulo A (id NSR10-A*): {len(filas)}; fragmentos distintos: {len(base)}")
    out, tot, hit = [], 0, 0
    for n in PDFS:
        rd = pypdf.PdfReader(str(RAW / f"NSR-10-{n}.pdf"))
        for i, p in enumerate(rd.pages):
            fr = sh(norm(p.extract_text() or ""))
            if len(fr) < 30:
                continue
            ok = sum(1 for x in fr if x in base)
            tot += len(fr); hit += ok
            enc = re.findall(r"\b(A\.\d+(?:\.\d+)*)\b", p.extract_text() or "")[:2]
            out.append({"pdf": n, "pagina_pdf": i + 1, "fragmentos": len(fr), "cobertura": round(ok / len(fr), 3), "numerales_en_pagina": enc})
    print(f"cobertura global de texto: {100 * hit / tot:.1f} % ({hit}/{tot} fragmentos de 6 palabras), {len(out)} paginas")
    bajas = sorted([o for o in out if o["cobertura"] < 0.6], key=lambda o: o["cobertura"])
    print(f"paginas con cobertura < 60 %: {len(bajas)}")
    for o in bajas[:60]:
        print(f"  {o['pdf']:<8} p{o['pagina_pdf']:>3}  {100 * o['cobertura']:>3.0f} %  ({o['fragmentos']} fr.)  {o['numerales_en_pagina']}")
    (Path(__file__).parent / "auditoria_titulo_a_paginas.json").write_text(json.dumps({"global": hit / tot, "paginas": out}, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
