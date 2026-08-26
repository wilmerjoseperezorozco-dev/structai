"""
Carga el Título C real de NSR-10 (Concreto Estructural) a nsr10_chunks,
reemplazando los 15 chunks curados/parafraseados que existían antes por
texto verbatim real, numeral por numeral (mismo estándar que Título G).

Sub-trochea cada artículo al límite real de 128 tokens del modelo de
embeddings (paraphrase-multilingual-MiniLM-L12-v2 trunca en silencio más
allá de eso — ver [[project_construdata_limite_tokens_embeddings]] en la
memoria del proyecto) usando la misma función `_dividir_en_subchunks` ya
probada en la ingesta de Ecuador/Perú (párrafo -> oración -> fragmento por
coma, en ese orden, nunca corta a la mitad de una palabra).

Los 15 chunks viejos (todos con norma_id NULL, confirmado antes de tocar
nada) se borran explícitamente por ese filtro -- nunca se toca ningún otro
título ni ningún chunk con norma_id ya asignado.

Uso: python scripts/ingesta/nsr10/ingest_nsr10_titulo_c.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

NSR10_DIR = Path(__file__).resolve().parent
ROOT = NSR10_DIR.parents[2]
CHUNKS_PATH = ROOT / "packages" / "construdata" / "normativa_raw" / "nsr10" / "titulo_c_chunks.jsonl"

from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CODIGO = "NSR10-TITULO-C"
MAX_TOKENS_POR_SUBCHUNK = 110  # mismo límite soft ya usado en Ecuador/Perú


def _partir_por_palabra(frag: str, tokenizer, max_tokens: int) -> list[str]:
    """Si un fragmento (ya partido por oración/coma) todavía excede
    max_tokens, lo re-parte por palabra completa. Devuelve [frag] sin
    tocar si ya cabe -- caso normal, esto casi nunca se activa."""
    if len(tokenizer.encode(frag)) <= max_tokens:
        return [frag]
    palabras = frag.split(" ")
    partes: list[str] = []
    actual = ""
    for palabra in palabras:
        candidato = f"{actual} {palabra}".strip() if actual else palabra
        if len(tokenizer.encode(candidato)) <= max_tokens:
            actual = candidato
        else:
            if actual:
                partes.append(actual)
            actual = palabra
    if actual:
        partes.append(actual)
    return partes


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Idéntica a la ya probada en scripts/ingesta/ecuador_nec_se_ds/*.py --
    párrafo completo si cabe, si no por oración, si no por fragmento
    separado por coma. Nunca corta a la mitad de una palabra."""
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual} {parrafo}" if actual else parrafo
        if n_tok(candidato) <= max_tokens:
            actual = candidato
            continue
        if actual:
            subchunks.append(actual)
            actual = ""
        if n_tok(parrafo) <= max_tokens:
            actual = parrafo
            continue
        oraciones = re.split(r"(?<=[.;])\s+", parrafo)
        buffer = ""
        for oracion in oraciones:
            fragmentos = (
                re.split(r"(?<=,)\s+", oracion)
                if n_tok(oracion) > max_tokens
                else [oracion]
            )
            # Último recurso, no presente en la versión original de
            # Ecuador/Perú: encontrado en Título C que algunos fragmentos
            # SIGUEN sobrando 128 tokens ni por coma (ej. listas de
            # excepciones largas en una sola oración, sin comas internas,
            # C.9.2.1) -- se re-parten por palabra completa antes de seguir,
            # nunca se deja pasar un fragmento que violaría el límite.
            fragmentos_finales = []
            for frag in fragmentos:
                fragmentos_finales.extend(_partir_por_palabra(frag, tokenizer, max_tokens))
            for frag in fragmentos_finales:
                cand = f"{buffer} {frag}".strip() if buffer else frag
                if n_tok(cand) <= max_tokens:
                    buffer = cand
                else:
                    if buffer:
                        subchunks.append(buffer)
                    buffer = frag
        if buffer:
            actual = buffer
    if actual:
        subchunks.append(actual)
    return subchunks


def main(dry_run: bool = False):
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    sb = create_client(supabase_url, supabase_key)

    row = sb.table("normas_registro").select("id").eq("codigo", CODIGO).execute()
    if not row.data:
        raise RuntimeError(f"{CODIGO} no existe en normas_registro — registrarlo primero")
    norma_id = row.data[0]["id"]

    chunks = [json.loads(line) for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"Artículos extraídos (antes de sub-trochear): {len(chunks)}")

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    all_rows = []
    for c in chunks:
        # c["texto"] ya trae "NSR-10 Título C C.N — <título>. <contenido>"
        # completo (armado en extract_nsr10_titulo_c.py) -- no hace falta
        # anteponer titulo de nuevo, ya está adentro.
        subchunks = _dividir_en_subchunks(c["texto"], tokenizer)
        if not subchunks:
            continue
        for i, sub in enumerate(subchunks):
            suffix = f"-sub{i+1}" if len(subchunks) > 1 else ""
            all_rows.append({
                "id": f"{c['id']}{suffix}",
                "capitulo": c["capitulo"],
                "seccion": c["seccion"],
                "titulo": c["titulo"][:500],
                "texto": sub,
                "norma_id": norma_id,
            })

    print(f"Subchunks reales (después de trochear a {MAX_TOKENS_POR_SUBCHUNK} tokens): {len(all_rows)}")

    # Verificación real antes de insertar -- no confiar en que el trocheo
    # funcionó solo porque no lanzó excepción.
    excede = [r["id"] for r in all_rows if len(tokenizer.encode(r["texto"])) > 128]
    if excede:
        print(f"ABORTADO: {len(excede)} subchunks todavía exceden 128 tokens: {excede[:5]}")
        return

    if dry_run:
        print("[dry-run] No se modifica Supabase. Muestra de 3 filas:")
        for r in all_rows[:3]:
            print(f"  {r['id']} | {r['seccion']} | {r['texto'][:100]}")
        return

    print("Generando embeddings...")
    textos = [r["texto"] for r in all_rows]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    for row_, vec in zip(all_rows, vectores):
        row_["embedding"] = vec.tolist()

    # Los 15 chunks viejos (fichas curadas/parafraseadas) tienen norma_id
    # NULL -- confirmado antes de escribir este script. Este filtro NUNCA
    # toca chunks con norma_id ya asignado (ninguno de los otros títulos
    # lo tiene, así que en la práctica hoy esto solo afecta a Título C).
    print("Borrando los 15 chunks viejos de Título C (norma_id NULL, verificado antes)...")
    borrado = sb.table("nsr10_chunks").delete() \
        .like("capitulo", "%Título C%") \
        .is_("norma_id", "null") \
        .execute()
    print(f"  borrados: {len(borrado.data)}")

    print("Subiendo a nsr10_chunks...")
    for i in range(0, len(all_rows), 50):
        batch = all_rows[i:i + 50]
        sb.table("nsr10_chunks").upsert(batch, on_conflict="id").execute()
        print(f"  {min(i + 50, len(all_rows))}/{len(all_rows)}")
    print(f"OK: {len(all_rows)} chunks de Título C cargados en nsr10_chunks")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
