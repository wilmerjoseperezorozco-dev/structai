"""
NSR-10 Título F, Capítulo F.5 (Estructuras de aluminio) — Etapa 2 de la ingesta (auditoría 2026-11-08).
Completa los numerales que la auditoría por páginas no encontró en `nsr10_chunks`: F.5.7.7 a F.5.7.8 (fatiga) y F.5.8 (ensayos).
Extrae del PDF fuente (raw/, gitignored), de encabezado a encabezado, y re-trocea por el límite real de tokens.

Uso:  python _ingest_titulo_f5_aluminio_fatiga_ensayos.py --dry-run | (sin flag: upsert)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _ingest_titulo_c_etapa1_truncados as base  # noqa: E402  (reutiliza extraer/HEADING/PIE)

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"
PDF = "NSR-10-1183-1283.pdf"
NUMERALES = [
    "F.5.7.8", "F.5.7.8.1", "F.5.7.8.2", "F.5.7.8.3", "F.5.7.8.4", "F.5.7.8.5",
    "F.5.8", "F.5.8.1", "F.5.8.2", "F.5.8.3", "F.5.8.3.1", "F.5.8.3.2", "F.5.8.3.3", "F.5.8.3.4",
    "F.5.8.4", "F.5.8.4.1", "F.5.8.4.2", "F.5.8.4.3", "F.5.8.4.4", "F.5.8.4.5", "F.5.8.5",
]


def construir() -> list[dict]:
    chunks = []
    for numeral in NUMERALES:
        try:
            texto = base.extraer(numeral, PDF, titulo_f=True)
        except SystemExit as exc:
            print(f"AVISO: {exc}")
            continue
        if len(texto) < 60:  # encabezado sin cuerpo propio (los hijos llevan el texto)
            continue
        chunks.append({"id": f"NSR10-F-F_{numeral[2:].replace('.', '_')}", "capitulo": CAPITULO, "seccion": numeral,
                       "titulo": texto[:60], "texto": f"NSR-10 Título F {texto}"})
    return chunks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    chunks = construir()
    for c in chunks:
        print(f"--- {c['id']} ({len(c['texto'])} car.)\n{c['texto'][:300]}\n")
    print(f"{len(chunks)} chunks")
    if args.dry_run:
        return
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    from supabase import create_client
    from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

    load_dotenv(base.PROJECT_ROOT / "apps" / "api" / ".env")
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    filas = []
    for c in chunks:
        for k, p in enumerate(_sub_particionar_por_tokens_reales(c["texto"], modelo.tokenizer)):
            filas.append({**c, "id": c["id"] if k == 0 else f"{c['id']}_r{k}", "texto": p, "embedding": modelo.encode(p).tolist()})
    sb.table("nsr10_chunks").upsert(filas, on_conflict="id").execute()
    print(f"{len(filas)} filas upserted")


if __name__ == "__main__":
    main()
