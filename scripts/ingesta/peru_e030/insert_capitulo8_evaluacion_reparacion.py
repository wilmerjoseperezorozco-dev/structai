"""
Inserta el núcleo verbatim real del Capítulo VIII (Evaluación, Reparación
y Reforzamiento de Estructuras, Artículos 48-49) de la norma E.030 de Perú
en peru_e030_chunks. Octavo bloque del corpus, después de los Capítulos
I-VII (ver los otros insert_capituloN_*.py -- mismo texto oficial del
MVCS, misma base legal de citación verbatim, Art. 9(b) del Decreto
Legislativo N° 822).

Cubre: quién evalúa una estructura después de un sismo (ingeniero civil,
que determina buen estado / reforzamiento / reparación / demolición) y los
requisitos del proyecto de reparación o reforzamiento, incluyendo la
remisión al RNE y al documento FEMA P-420 para reforzamiento sísmico
progresivo.

Es el capítulo más corto de toda la norma (solo 2 artículos), pero
relevante para el caso de uso post-sismo -- exactamente el tipo de
escenario donde StructAI ya tiene experiencia con el módulo de
señales de riesgo de Colombia (SGC/Sisbén/UNGRD).

Uso: python scripts/ingesta/peru_e030/insert_capitulo8_evaluacion_reparacion.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo VIII — Evaluación, Reparación y Reforzamiento de Estructuras"

CHUNKS = [
    {
        "id": "E030-CAP8-INTRO_ART48-EVALUACION",
        "seccion": "Introducción y Artículo 48",
        "titulo": "Evaluación de Estructuras Después de un Sismo (a cargo de ingeniero civil: buen estado, reforzamiento, reparación o demolición)",
        "texto": """CAPÍTULO VIII — EVALUACIÓN, REPARACIÓN Y REFORZAMIENTO DE ESTRUCTURAS

Las estructuras dañadas por sismos son evaluadas, reparadas y/o reforzadas de tal manera que se corrijan los posibles defectos estructurales que provocaron los daños y recuperen la capacidad de resistir un nuevo evento sísmico, acorde con la filosofía del Diseño Sismorresistente señalada en el artículo 3.

Artículo 48.- Evaluación de Estructuras Después de un Sismo

Ocurrido el evento sísmico, la estructura es evaluada por un ingeniero civil, quien determina si la edificación se encuentra en buen estado o requiere de reforzamiento, reparación o demolición. El estudio necesariamente considera las características geotécnicas del sitio.""",
    },
    {
        "id": "E030-CAP8-ART49-REPARACION_REFORZAMIENTO",
        "seccion": "Artículo 49",
        "titulo": "Reparación y Reforzamiento (lineamientos RNE, criterios alternativos con justificación técnica, reforzamiento sísmico progresivo FEMA P-420)",
        "texto": """Artículo 49.- Reparación y Reforzamiento

49.1. La reparación o reforzamiento dota a la estructura de una combinación adecuada de rigidez, resistencia y ductilidad que garantice su buen comportamiento en eventos futuros.

49.2. El proyecto de reparación o reforzamiento incluye los detalles, procedimientos y sistemas constructivos a seguirse.

49.3. Para la reparación y el reforzamiento sísmico de edificaciones se siguen los lineamientos del Reglamento Nacional de Edificaciones (RNE). Se pueden emplear otros criterios y procedimientos diferentes a los indicados en el RNE, con la debida justificación técnica y con aprobación del propietario y de la autoridad competente.

49.4. Las edificaciones se pueden intervenir empleando los criterios de reforzamiento sísmico progresivo y en la medida que sea aplicable, usando los criterios establecidos en el documento "Engineering Guideline for Incremental Seismic Rehabilitation", FEMA P-420, Risk Management Series, USA, 2009.""",
    },
]


# Mismo límite verificado empíricamente en scripts/ingesta/nsr10/ el
# 2026-08-03: el tokenizer real (no una aproximación por caracteres) es lo
# único confiable.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variación


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite se divide por oracion, y si aun asi excede, por
    coma."""
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual}\n\n{parrafo}" if actual else parrafo
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
            for frag in fragmentos:
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


def insertar(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    filas_planas = []
    for chunk in CHUNKS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "titulo": chunk["titulo"],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    rows = []
    for f, emb in zip(filas_planas, embeddings):
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
        rows.append({
            "id": f["id"],
            "capitulo": CAPITULO_LABEL,
            "titulo": f["titulo"],
            "seccion": f["seccion"],
            "texto": f["texto"],
            "embedding": emb,
        })

    print(f"{len(CHUNKS)} bloques originales -> {len(rows)} subchunks reales (limite 128 tokens):")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens (se truncarian en la busqueda): {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("peru_e030_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en peru_e030_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
