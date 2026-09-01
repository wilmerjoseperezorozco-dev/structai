"""
Corrige el hallazgo real de auditar_tokens_reales_f43_f44_f45.py
(2026-09-01): 151 de 293 chunks (51.5%) de F.4.3/F.4.4/F.4.5 median
mas de 128 tokens REALES pese a haber "pasado" el splitter por
caracteres de F.4.2 -- se estaban truncando en silencio al vectorizar,
exactamente el mismo bug que motivo el fix de F.4.6. Ver
[[project_construdata_limite_tokens_embeddings]].

Este script NO re-lee el PDF ni re-transcribe nada -- el texto
verbatim ya cargado es correcto, solo estaba mal trocheado. Toma cada
chunk existente de los 3 titulos, mide con el tokenizer real, y SOLO
para los que superan el limite: sub-particiona por clausulas
(reusando _sub_particionar_por_tokens_reales de
_resplit_titulo_f_f46_por_limite_tokens.py) hasta confirmar <=128
tokens reales, sube las piezas nuevas, y borra el chunk viejo
sobredimensionado. Los chunks que ya estaban bien (142 de 293) se
dejan intactos -- no se les toca el id ni se re-sube su embedding.

Uso: python retrochear_f43_f44_f45_tokens_reales.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "ingesta" / "nsr10"))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

LIMITE_TOKENS_REAL = 128
PREFIJOS = {
    "F.4.3": "NSR10-F-F_4_3_",
    "F.4.4": "NSR10-F-F_4_4_",
    "F.4.5": "NSR10-F-F_4_5_",
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    total_reemplazados = 0
    total_piezas_nuevas = 0

    for titulo, prefijo in PREFIJOS.items():
        print(f"\n{'='*70}\n{titulo}\n{'='*70}")
        resp = sb.table("nsr10_chunks").select("id,capitulo,seccion,titulo,texto").ilike("id", f"{prefijo}%").execute()
        chunks = resp.data

        a_reemplazar = []
        for c in chunks:
            n = len(tokenizer.encode(c["texto"], add_special_tokens=True))
            if n > LIMITE_TOKENS_REAL:
                a_reemplazar.append(c)

        print(f"{len(chunks)} chunks totales, {len(a_reemplazar)} sobre el límite real -- re-trocheando...")

        if not a_reemplazar:
            continue

        nuevas_filas = []
        ids_viejos = []
        for parent in a_reemplazar:
            ids_viejos.append(parent["id"])
            piezas = _sub_particionar_por_tokens_reales(parent["texto"], tokenizer)
            for i, pieza in enumerate(piezas, start=1):
                nuevas_filas.append({
                    "id": f"{parent['id']}_q{i}",
                    "capitulo": parent["capitulo"],
                    "seccion": parent["seccion"],
                    "titulo": parent["titulo"],
                    "texto": pieza,
                })

        # Verificacion real antes de subir nada.
        sobre_limite_tras_split = [
            r["id"] for r in nuevas_filas
            if len(tokenizer.encode(r["texto"], add_special_tokens=True)) > LIMITE_TOKENS_REAL
        ]
        if sobre_limite_tras_split:
            raise SystemExit(f"Piezas todavia sobre el limite tras sub-particion: {sobre_limite_tras_split}")

        print(f"  {len(a_reemplazar)} chunks viejos -> {len(nuevas_filas)} piezas nuevas, 0 sobre el limite real")

        print("  Generando embeddings...")
        textos = [r["texto"] for r in nuevas_filas]
        vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)
        for r, vec in zip(nuevas_filas, vectores):
            r["embedding"] = vec.tolist()
            r["titulo"] = r["titulo"][:500] if r["titulo"] else r["titulo"]

        print("  Subiendo piezas nuevas...")
        sb.table("nsr10_chunks").upsert(nuevas_filas, on_conflict="id").execute()

        print(f"  Borrando {len(ids_viejos)} chunks viejos sobredimensionados...")
        sb.table("nsr10_chunks").delete().in_("id", ids_viejos).execute()

        total_reemplazados += len(ids_viejos)
        total_piezas_nuevas += len(nuevas_filas)

    print(f"\n{'='*70}")
    print(f"OK: {total_reemplazados} chunks sobredimensionados reemplazados por {total_piezas_nuevas} piezas reales verificadas con el tokenizer.")


if __name__ == "__main__":
    main()
