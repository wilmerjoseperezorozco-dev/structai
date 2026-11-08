"""Auditoria independiente del Titulo A de NSR-10: separa 'falto el chunk' de 'el audit por seccion no lo ve'.
Para cada numeral real A.* de los 14 PDFs fuente mide (1) cobertura por columna `seccion` (como el audit original)
y (2) presencia del numeral al inicio de linea dentro del TEXTO de algun chunk. Solo lectura.
Salida: auditoria_titulo_a_contenido.json (numerales sin ninguna de las dos senales, por capitulo).
"""
from __future__ import annotations
import json, os, re, sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "packages" / "rag-audit-kit"))
from dotenv import load_dotenv  # noqa: E402
from src import comparar_cobertura, dedup_preservando_orden, extraer_numerales, capitulo_de  # noqa: E402
import pypdf  # noqa: E402
from supabase import create_client  # noqa: E402

RAW = RAIZ / "scripts" / "ingesta" / "nsr10" / "raw"
PDFS = ["43-54", "56-81", "81-94", "95-105", "106-115", "116-123", "124-128", "130-138", "140-154", "156-158", "160-166", "168-181", "183-190", "191-218"]

def main():
    load_dotenv(RAIZ / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    texto = "\n".join((p.extract_text() or "") for n in PDFS for p in pypdf.PdfReader(str(RAW / f"NSR-10-{n}.pdf")).pages)
    nums = dedup_preservando_orden([n for n in extraer_numerales(texto) if n.valor.startswith("A.")])
    filas, ini = [], 0
    while True:
        lote = sb.table("nsr10_chunks").select("id,seccion,texto").ilike("seccion", "A.%").range(ini, ini + 999).execute().data
        filas += lote
        if len(lote) < 1000:
            break
        ini += 1000
    print(f"numerales reales: {len(nums)}; chunks A.* en la base: {len(filas)}")
    cub_sec = [f["seccion"] for f in filas if f.get("seccion")]
    rep = comparar_cobertura(nums, cub_sec)
    faltan_sec = {n.valor for n in nums} - set(getattr(rep, "cubiertos", []) or [])
    if not faltan_sec:  # estructura del reporte desconocida: recalcular a mano
        faltan_sec = {v for v in (getattr(rep, "faltantes", []) or [])}
    contenido = "\n".join(f.get("texto") or "" for f in filas)
    resultado, por_cap = [], defaultdict(lambda: {"total": 0, "sin_seccion": 0, "sin_ninguna": 0})
    for n in nums:
        cap = capitulo_de(n.valor)
        por_cap[cap]["total"] += 1
        sin_sec = n.valor in faltan_sec
        en_texto = re.search(r"(^|\n)\s*" + re.escape(n.valor) + r"(?![\d.]*\d)", contenido) is not None
        if sin_sec:
            por_cap[cap]["sin_seccion"] += 1
        if sin_sec and not en_texto:
            por_cap[cap]["sin_ninguna"] += 1
            resultado.append({"numeral": n.valor, "contexto": n.linea_contexto[:110]})
    tot = sum(v["total"] for v in por_cap.values()); ss = sum(v["sin_seccion"] for v in por_cap.values()); sn = sum(v["sin_ninguna"] for v in por_cap.values())
    print(f"sin cobertura por seccion: {ss}/{tot}; sin cobertura ni por seccion ni por texto: {sn}/{tot}")
    for c, v in sorted(por_cap.items()):
        print(f"  {c:<6} total {v['total']:>3}  sin seccion {v['sin_seccion']:>3}  sin ninguna senal {v['sin_ninguna']:>3}")
    (Path(__file__).parent / "auditoria_titulo_a_contenido.json").write_text(json.dumps({"por_capitulo": por_cap, "numerales_sin_ninguna_senal": resultado}, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main()
