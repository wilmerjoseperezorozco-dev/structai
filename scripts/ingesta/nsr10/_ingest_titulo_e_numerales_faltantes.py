"""
NSR-10 Título E (Casas de uno y dos pisos) — Etapa 2 de la ingesta (auditoría 2026-11-08).
Carga los numerales de E.1–E.8 que `docs/AUDITORIA_NSR10_PAGINAS_2026-11.json` marca como «nunca_mencionado» (69).
Extracción de encabezado a encabezado desde el PDF fuente (raw/, gitignored), re-troceo por tokens reales.

Uso:  python _ingest_titulo_e_numerales_faltantes.py --dry-run | (sin flag: upsert)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _ingest_titulo_c_etapa1_truncados as base  # noqa: E402

CAPITULO = "NSR-10 Título E — Casas de Uno y Dos Pisos"
AUDITORIA = base.PROJECT_ROOT / "docs" / "AUDITORIA_NSR10_PAGINAS_2026-11.json"
MAPA = HERE / "numerales_pdf.json"  # numeral -> PDF (generado por auditoria_paginas.py --cache)


def numerales_faltantes() -> list[str]:
    d = json.loads(AUDITORIA.read_text(encoding="utf-8"))["nunca_mencionado"]
    return sorted((n for t, v in d.items() if t.startswith("E.") for n in v),
                  key=lambda x: [int(p) if p.isdigit() else 0 for p in x[2:].split(".")])


def construir(mapa: dict[str, str]) -> list[dict]:
    chunks = []
    for numeral in numerales_faltantes():
        pdf = mapa.get(numeral)
        if not pdf:
            print(f"AVISO: {numeral} sin PDF en el mapa")
            continue
        texto = base.extraer(numeral, pdf, titulo_f=True)  # regex estricto de encabezado (guion con espacios)
        if len(texto) < 40:
            print(f"AVISO: {numeral} sin cuerpo propio ({len(texto)} car.)")
            continue
        chunks.append({"id": f"NSR10-E-E_{numeral[2:].replace('.', '_')}", "capitulo": CAPITULO, "seccion": numeral,
                       "titulo": texto[:60], "texto": f"NSR-10 Título E {texto}"})
    return chunks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--mapa", default=str(MAPA))
    args = ap.parse_args()
    mapa = json.loads(Path(args.mapa).read_text(encoding="utf-8"))
    chunks = construir(mapa)
    for c in chunks:
        print(f"--- {c['id']} ({len(c['texto'])} car.)\n{c['texto'][:200]}\n")
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
