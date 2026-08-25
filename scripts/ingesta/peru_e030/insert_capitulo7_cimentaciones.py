"""
Inserta el núcleo verbatim real del Capítulo VII (Cimentaciones, Artículos
44-47) de la norma E.030 de Perú en peru_e030_chunks. Séptimo bloque del
corpus, después de los Capítulos I-VI (ver los otros insert_capituloN_*.py
-- mismo texto oficial del MVCS, misma base legal de citación verbatim,
Art. 9(b) del Decreto Legislativo N° 822).

Cubre: generalidades de cimentación (presiones por esfuerzos admisibles
con factor 0,8), capacidad portante (obligación de considerar licuación
del suelo en el EMS), momento de volteo (factor de seguridad ≥1,2), y
cimentaciones sobre suelos flexibles o de baja capacidad portante
(elementos/vigas de conexión obligatorios en suelos S3/S4 y zonas 3/4,
armadura mínima de pilotes en tracción).

Es el capítulo más corto de la norma junto con el V, pero cubre una
decisión de diseño con consecuencias reales: cuándo un ingeniero está
obligado a poner vigas de conexión entre zapatas.

Uso: python scripts/ingesta/peru_e030/insert_capitulo7_cimentaciones.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "E.030 Capítulo VII — Cimentaciones"

CHUNKS = [
    {
        "id": "E030-CAP7-ART44_45-GENERALIDADES_CAPACIDAD_PORTANTE",
        "seccion": "Artículos 44 y 45",
        "titulo": "Generalidades de Cimentación (factor 0,8 por esfuerzos admisibles) y Capacidad Portante (licuación del suelo)",
        "texto": """Artículo 44.- Generalidades

44.1. Las suposiciones que se hagan para los apoyos de la estructura son concordantes con las características propias del suelo de cimentación.

44.2. La determinación de las presiones actuantes en el suelo para la verificación por esfuerzos admisibles, se hace con las fuerzas obtenidas del análisis sísmico multiplicadas por 0,8.

Artículo 45.- Capacidad Portante

En todo Estudio de Mecánica de Suelos (EMS) se consideran los efectos de los sismos para la determinación de la capacidad portante del suelo de cimentación. En los sitios en que pueda producirse licuación del suelo, se efectúa una investigación geotécnica que evalúe esta posibilidad y determine la solución más adecuada.""",
    },
    {
        "id": "E030-CAP7-ART46_47-MOMENTO_VOLTEO_SUELOS_FLEXIBLES",
        "seccion": "Artículos 46 y 47",
        "titulo": "Momento de Volteo (factor de seguridad ≥1,2) y Cimentaciones Sobre Suelos Flexibles o de Baja Capacidad Portante (vigas de conexión)",
        "texto": """Artículo 46.- Momento de Volteo

Toda estructura y su cimentación son diseñadas para resistir el momento de volteo que produce un sismo, según los artículos 28 o 29. El factor de seguridad calculado con las fuerzas que se obtienen en aplicación de esta Norma es mayor o igual que 1,2.

Artículo 47.- Cimentaciones Sobre Suelos Flexibles o de Baja Capacidad Portante

47.1. Para zapatas aisladas con o sin pilotes en suelos tipo S3 y S4 y para las Zonas 3 y 4, se provee elementos de conexión, los que soportan en tracción o compresión, una fuerza horizontal mínima equivalente al 10% de la carga vertical que soporta la zapata.

47.2. Para suelos de capacidad portante menor que 0,15 MPa, se provee vigas de conexión en ambas direcciones.

47.3. Para el caso de pilotes y cajones de cimentación, se debe proveer vigas de conexión tomando en cuenta los giros y deformaciones por efecto de la fuerza horizontal diseñando pilotes y zapatas para estas solicitaciones. Los pilotes tienen una armadura en tracción equivalente por lo menos al 15% de la carga vertical que soportan.""",
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
