"""
Auditoria real 2026-09-01 (punto 3 del plan Data First, ver memoria
privada del usuario, project_structai_data_first_mejoras): generaliza
auditar_tokens_reales_f43_f44_f45.py a TODO nsr10_chunks, para saber
con evidencia real que tan grande es el problema de truncamiento
silencioso fuera de F.4.3/F.4.4/F.4.5 (que ya se auditaron y
corrigieron).

Excluye a proposito los prefijos de F.4.3 a F.4.7 (ya auditados y
re-trocheados hoy con verificacion real de tokens -- serian 0 sobre
el limite, no vale la pena volver a medirlos).

Este script NO re-trochea nada -- solo AUDITA y reporta, agrupado por
titulo real (derivado del id), para decidir con datos donde vale la
pena invertir el esfuerzo de re-trocheo despues.

Uso: python auditar_tokens_reales_corpus_completo.py
"""
from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

LIMITE_TOKENS_REAL = 128

# Prefijos ya auditados y re-trocheados hoy con verificacion real de
# tokens (F.4.3, F.4.4, F.4.5 parcial+cierre, F.4.6, F.4.7) -- excluir
# para no perder tiempo re-midiendo algo que ya se confirmo en 0.
PREFIJOS_YA_AUDITADOS = (
    "NSR10-F-F_4_3_",
    "NSR10-F-F_4_4_",
    "NSR10-F-F_4_5_",
    "NSR10-F-F_4_6_",
    "NSR10-F-F_4_7_",
)


def _titulo_de_id(id_: str) -> str:
    """Deriva un titulo legible a partir del id real del chunk -- no
    confia en la columna `capitulo` (verificado inconsistente: 33
    variantes de texto distintas para los mismos titulos)."""
    m = re.match(r"^NSR10-([A-Z])([0-9])?-", id_)
    if m:
        letra, num = m.group(1), m.group(2)
        return f"Título {letra}" + (f".{num}" if num else "")
    if id_.startswith("RES0312-2019"):
        return "SGSST — Res. 0312/2019"
    if id_.startswith("RES4272-2021"):
        return "SGSST — Res. 4272/2021"
    if id_.startswith("RES5018-2019"):
        return "SGSST — Res. 5018/2019"
    if id_.startswith("NSR10-ALCANCE-"):
        return "NSR-10 — chunks de alcance (varios títulos)"
    if id_.startswith("AIS2004") or id_.startswith("AIS410") or id_.startswith("BUILDCHANGE"):
        return "Referencias históricas (AIS/BuildChange)"
    return f"Sin clasificar: {id_[:25]}"


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Trayendo todos los chunks de nsr10_chunks (paginado)...")
    all_rows = []
    page_size = 1000
    offset = 0
    while True:
        resp = (
            sb.table("nsr10_chunks")
            .select("id,texto")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = resp.data
        all_rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    print(f"Total real en nsr10_chunks: {len(all_rows)}")

    rows = [r for r in all_rows if not r["id"].startswith(PREFIJOS_YA_AUDITADOS)]
    excluidos = len(all_rows) - len(rows)
    print(f"Excluidos (ya auditados hoy, F.4.3-F.4.7): {excluidos}")
    print(f"A auditar: {len(rows)}")

    print("\nCargando modelo de embeddings local (tokenizer real)...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    por_titulo = defaultdict(lambda: {"total": 0, "sobre_limite": 0, "max_tokens": 0, "peores": []})

    print("\nMidiendo tokens reales de cada chunk (puede tardar unos minutos)...")
    for i, r in enumerate(rows, 1):
        titulo = _titulo_de_id(r["id"])
        n = len(tokenizer.encode(r["texto"], add_special_tokens=True))
        bucket = por_titulo[titulo]
        bucket["total"] += 1
        bucket["max_tokens"] = max(bucket["max_tokens"], n)
        if n > LIMITE_TOKENS_REAL:
            bucket["sobre_limite"] += 1
            bucket["peores"].append((r["id"], n))
        if i % 500 == 0:
            print(f"  ... {i}/{len(rows)}")

    print("\n" + "=" * 78)
    print("RESUMEN AUDITORIA REAL DE TOKENS — CORPUS COMPLETO nsr10_chunks")
    print("(excluye F.4.3-F.4.7, ya auditados y confirmados en 0 hoy)")
    print("=" * 78)

    total_chunks = 0
    total_sobre = 0
    filas_reporte = ["titulo,total,sobre_limite,pct_afectado,max_tokens_real"]
    for titulo in sorted(por_titulo.keys(), key=lambda t: -por_titulo[t]["sobre_limite"]):
        d = por_titulo[titulo]
        pct = round(100 * d["sobre_limite"] / d["total"], 1) if d["total"] else 0.0
        total_chunks += d["total"]
        total_sobre += d["sobre_limite"]
        marca = "  <<<< " if pct >= 30 else ("  <<< " if pct >= 10 else "")
        print(
            f"{titulo}: {d['total']} chunks, {d['sobre_limite']} sobre el límite "
            f"({pct}%), max real {d['max_tokens']} tokens{marca}"
        )
        filas_reporte.append(f"{titulo},{d['total']},{d['sobre_limite']},{pct},{d['max_tokens']}")

    print("-" * 78)
    pct_total = round(100 * total_sobre / total_chunks, 1) if total_chunks else 0.0
    print(f"TOTAL: {total_chunks} chunks auditados, {total_sobre} sobre el límite real ({pct_total}%)")

    reporte_path = Path(__file__).resolve().parent / "_auditoria_corpus_completo_resultado.csv"
    reporte_path.write_text("\n".join(filas_reporte), encoding="utf-8")
    print(f"\nReporte por título guardado en: {reporte_path}")
    print("(no incluye el detalle de cada chunk individual -- ese detalle vive")
    print(" en la salida de consola de esta corrida, no se persiste)")


if __name__ == "__main__":
    main()
