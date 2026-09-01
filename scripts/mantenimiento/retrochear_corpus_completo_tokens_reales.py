"""
Corrige el hallazgo real de auditar_tokens_reales_corpus_completo.py
(2026-09-01, punto 3 del plan Data First -- ver memoria privada del
usuario, project_structai_data_first_mejoras): 493 de 4.129 chunks
(11.9%) de nsr10_chunks median mas de 128 tokens REALES -- se estaban
truncando en silencio para la busqueda semantica, con severidad muy
dispareja por titulo (K/B/J/A/referencias historicas al 100%
afectados, F-resto 74.8%, E 94.4%, G 50.5%; C/D/H/SGSST en 0%, no se
tocan).

Este script NO re-lee ningun PDF ni re-transcribe nada -- el texto
verbatim ya cargado es correcto, solo estaba mal trocheado en algun
momento anterior a la disciplina de verificacion real establecida
hoy (F.4.6/F.4.7/F.4.3-5 retrochear). Mide CADA chunk de nsr10_chunks
con el tokenizer real; para el que mide <=128 tokens, no lo toca (no
gasta un re-embed innecesario); para el que mide mas, lo sub-particiona
por clausulas (reusa _sub_particionar_por_tokens_reales de
_resplit_titulo_f_f46_por_limite_tokens.py) hasta confirmar <=128
tokens reales, sube las piezas nuevas con sufijo "_r<n>", y borra el
chunk viejo sobredimensionado.

Excluye a proposito los prefijos de F.4.3 a F.4.7 (ya auditados y
re-trocheados hoy, confirmados en 0).

Uso: python retrochear_corpus_completo_tokens_reales.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "ingesta" / "nsr10"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales
from auditar_tokens_reales_corpus_completo import _titulo_de_id, PREFIJOS_YA_AUDITADOS

LIMITE_TOKENS_REAL = 128
BATCH_UPSERT = 200  # subir en lotes para no mandar un solo request gigante


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
            .select("id,capitulo,seccion,titulo,texto")
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
    print(f"Excluidos (ya auditados hoy, F.4.3-F.4.7): {len(all_rows) - len(rows)}")
    print(f"A revisar: {len(rows)}")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    print("\nMidiendo tokens reales de cada chunk...")
    a_reemplazar = []
    for i, r in enumerate(rows, 1):
        n = len(tokenizer.encode(r["texto"], add_special_tokens=True))
        if n > LIMITE_TOKENS_REAL:
            a_reemplazar.append(r)
        if i % 1000 == 0:
            print(f"  ... {i}/{len(rows)}")

    print(f"\n{len(a_reemplazar)} chunks sobre el límite real -- re-trocheando...")

    nuevas_filas = []
    ids_viejos = []
    por_titulo_reemplazados = {}
    for parent in a_reemplazar:
        ids_viejos.append(parent["id"])
        titulo = _titulo_de_id(parent["id"])
        por_titulo_reemplazados[titulo] = por_titulo_reemplazados.get(titulo, 0) + 1
        piezas = _sub_particionar_por_tokens_reales(parent["texto"], tokenizer)
        for i, pieza in enumerate(piezas, start=1):
            nuevas_filas.append({
                "id": f"{parent['id']}_r{i}",
                "capitulo": parent["capitulo"],
                "seccion": parent["seccion"],
                "titulo": (parent["titulo"] or "")[:500],
                "texto": pieza,
            })

    print("Verificando (segunda vez, real) que ninguna pieza nueva siga sobre el límite...")
    sobre_limite_tras_split = [
        r["id"] for r in nuevas_filas
        if len(tokenizer.encode(r["texto"], add_special_tokens=True)) > LIMITE_TOKENS_REAL
    ]
    if sobre_limite_tras_split:
        raise SystemExit(f"Piezas todavia sobre el limite tras sub-particion: {sobre_limite_tras_split}")
    print(f"OK: {len(a_reemplazar)} chunks viejos -> {len(nuevas_filas)} piezas nuevas, 0 sobre el límite real")

    print("\nGenerando embeddings (puede tardar)...")
    textos = [r["texto"] for r in nuevas_filas]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for r, vec in zip(nuevas_filas, vectores):
        r["embedding"] = vec.tolist()

    print(f"\nSubiendo {len(nuevas_filas)} piezas nuevas en lotes de {BATCH_UPSERT}...")
    for i in range(0, len(nuevas_filas), BATCH_UPSERT):
        lote = nuevas_filas[i:i + BATCH_UPSERT]
        sb.table("nsr10_chunks").upsert(lote, on_conflict="id").execute()
        print(f"  subido lote {i // BATCH_UPSERT + 1} ({len(lote)} filas)")

    print(f"\nBorrando {len(ids_viejos)} chunks viejos sobredimensionados en lotes de {BATCH_UPSERT}...")
    for i in range(0, len(ids_viejos), BATCH_UPSERT):
        lote = ids_viejos[i:i + BATCH_UPSERT]
        sb.table("nsr10_chunks").delete().in_("id", lote).execute()
        print(f"  borrado lote {i // BATCH_UPSERT + 1} ({len(lote)} ids)")

    print("\n" + "=" * 70)
    print("RESUMEN POR TÍTULO (chunks viejos reemplazados)")
    print("=" * 70)
    for titulo, n in sorted(por_titulo_reemplazados.items(), key=lambda x: -x[1]):
        print(f"  {titulo}: {n}")

    print(f"\nOK: {len(ids_viejos)} chunks sobredimensionados reemplazados por {len(nuevas_filas)} piezas reales.")


if __name__ == "__main__":
    main()
