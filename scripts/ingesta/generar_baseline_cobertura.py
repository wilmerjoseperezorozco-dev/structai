"""
Genera un archivo baseline de cobertura para un título/norma, usando
rag-audit-kit. Se corre A MANO (no en CI, necesita el PDF fuente que es
gitignored) cada vez que se cierra o avanza sustancialmente la ingesta
verbatim de un título -- el archivo resultante SÍ se versiona en git (solo
tiene numerales/estructura, no el texto normativo con derechos de autor) y
es lo que scripts/ingesta/verificar_cobertura_baseline.py usa en CI para
detectar regresiones sin necesitar el PDF ahí.

Uso:
    python scripts/ingesta/generar_baseline_cobertura.py \\
        --pdf scripts/ingesta/nsr10/raw/NSR-10-1501-1570.pdf \\
        --prefijo "I." \\
        --tabla nsr10_chunks --columna seccion \\
        --titulo "NSR-10 Título I — Supervisión técnica" \\
        --out scripts/ingesta/nsr10/cobertura_baseline/I.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "packages" / "rag-audit-kit"))

from dotenv import load_dotenv  # noqa: E402

from src import comparar_cobertura, dedup_preservando_orden, extraer_numerales  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, help="PDF fuente (no se commitea, solo se lee)")
    ap.add_argument("--prefijo", required=True, help='Prefijo de numeral a aislar, ej. "I."')
    ap.add_argument("--tabla", default="nsr10_chunks")
    ap.add_argument("--columna", default="seccion")
    ap.add_argument("--titulo", required=True, help="Nombre legible del título/norma")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
    from supabase import create_client

    import pypdf

    lector = pypdf.PdfReader(args.pdf)
    texto = "\n".join(p.extract_text() or "" for p in lector.pages)
    numerales = dedup_preservando_orden(
        [n for n in extraer_numerales(texto) if n.valor.startswith(args.prefijo)]
    )

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    res = sb.table(args.tabla).select(args.columna).ilike(args.columna, f"{args.prefijo}%").execute()
    cubiertos = [r[args.columna] for r in res.data if r.get(args.columna)]

    reporte = comparar_cobertura(numerales, cubiertos)

    salida = {
        "titulo": args.titulo,
        "prefijo_seccion": args.prefijo,
        "tabla": args.tabla,
        "columna_seccion": args.columna,
        "generado_utc": datetime.now(timezone.utc).isoformat(),
        "fuente_pdf": os.path.basename(args.pdf),
        "pct_cobertura_al_generar": reporte.pct_cobertura,
        "total_numerales": reporte.total_fuente,
        # Solo las etiquetas de numeral (ej. "A.3.3.4") -- estructura, no el
        # texto normativo con derechos de autor. Mismo criterio que
        # docs/fuentes-normativas.md, que ya lista numerales específicos en
        # prosa sin que eso implique reproducir la norma completa.
        "numerales": [n.valor for n in numerales],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Baseline escrito en {out_path}")
    print(f"{reporte.total_cubiertos}/{reporte.total_fuente} numerales cubiertos ({reporte.pct_cobertura}%)")
    if reporte.faltantes:
        print(f"Faltantes (candidatos, verificar antes de asumir hueco real): {[n.valor for n in reporte.faltantes]}")


if __name__ == "__main__":
    main()
