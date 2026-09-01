"""
Auditoria real 2026-09-01: F.4.3/F.4.4/F.4.5 (NSR-10 Titulo F) se
trocearon con el splitter de F.4.2 (_resplit_titulo_f_f42_por_limite_tokens.py),
que solo ESTIMA tokens por caracteres (~4.5 chars/token) y nunca
verifica con el tokenizer real -- a diferencia de F.4.6, que ya
incorpora el segundo paso de verificacion real
(_resplit_titulo_f_f46_por_limite_tokens.py). Ver
[[project_construdata_limite_tokens_embeddings]] para el hallazgo
completo.

Este script NO re-trochea nada -- solo AUDITA: trae todos los chunks
reales de F.4.3/F.4.4/F.4.5 desde Supabase, mide cada uno con el
tokenizer real del modelo de embeddings (paraphrase-multilingual-
MiniLM-L12-v2, max_seq_length=128), y reporta cuantos y cuales
superan el limite duro -- para decidir con datos reales si hace falta
un re-trocheo, no una suposicion.

Uso: python auditar_tokens_reales_f43_f44_f45.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

LIMITE_TOKENS_REAL = 128


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local (para el tokenizer real)...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    prefijos = {
        "F.4.3": "NSR10-F-F_4_3_",
        "F.4.4": "NSR10-F-F_4_4_",
        "F.4.5": "NSR10-F-F_4_5_",
    }

    reporte_csv_path = Path(__file__).resolve().parent / "_auditoria_f43_f44_f45_resultado.csv"
    filas_csv = ["titulo,id,chars,tokens_reales,sobre_limite"]

    resumen = {}
    for titulo, prefijo in prefijos.items():
        # PostgREST usa el mismo operador "like" de SQL -- escapar los
        # guiones bajos literales del id para no matchear de mas
        # (aunque en la practica los ids de este corpus no colisionan,
        # se hace explicito por prolijidad).
        resp = sb.table("nsr10_chunks").select("id,texto").ilike("id", f"{prefijo}%").execute()
        chunks = resp.data
        sobre_limite = []
        max_tokens = 0
        for c in chunks:
            n = len(tokenizer.encode(c["texto"], add_special_tokens=True))
            max_tokens = max(max_tokens, n)
            sobre = n > LIMITE_TOKENS_REAL
            filas_csv.append(f"{titulo},{c['id']},{len(c['texto'])},{n},{sobre}")
            if sobre:
                sobre_limite.append((c["id"], len(c["texto"]), n))

        resumen[titulo] = {
            "total": len(chunks),
            "sobre_limite": len(sobre_limite),
            "max_tokens_reales": max_tokens,
            "detalle": sobre_limite,
        }

    Path(reporte_csv_path).write_text("\n".join(filas_csv), encoding="utf-8")

    print("\n" + "=" * 70)
    print("RESUMEN AUDITORIA REAL DE TOKENS (F.4.3 / F.4.4 / F.4.5)")
    print("=" * 70)
    total_sobre = 0
    for titulo, datos in resumen.items():
        total_sobre += datos["sobre_limite"]
        print(
            f"\n{titulo}: {datos['total']} chunks reales, "
            f"{datos['sobre_limite']} sobre {LIMITE_TOKENS_REAL} tokens REALES "
            f"(max real: {datos['max_tokens_reales']} tokens)"
        )
        for cid, chars, n in sorted(datos["detalle"], key=lambda x: -x[2]):
            print(f"  ! {cid}: {chars} chars -> {n} tokens reales")

    print(f"\nTOTAL piezas sobre el limite real en los 3 titulos: {total_sobre}")
    print(f"Reporte completo (293 filas) guardado en: {reporte_csv_path}")


if __name__ == "__main__":
    main()
