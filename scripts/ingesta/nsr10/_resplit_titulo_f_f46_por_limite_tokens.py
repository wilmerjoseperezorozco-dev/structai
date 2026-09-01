"""
Re-trocea los chunks de F.4.6 (ya transcritos verbatim en
_ingest_titulo_f_f46_verbatim.py) en piezas mas chicas -- mismo patron
que F.4.2/F.4.3/F.4.4/F.4.5, MAS un segundo paso nuevo.

Hallazgo real 2026-09-01 (F.4.6): el splitter compartido de F.4.2
(`split_texto`, TARGET_CHARS=450 ~ 100 tokens estimados a 4.5
chars/token) asume prosa normal -- para contenido denso en numeros,
tablas y simbolos griegos (phi, beta, gamma, Sigma) la relacion real
es mucho mas baja que 4.5 chars/token. Verificado con el tokenizer
REAL del modelo (no la estimacion): de 30 piezas que el splitter de
caracteres daba por buenas (todas <=128 tokens ESTIMADOS), 10
resultaron tener entre 133 y 205 tokens REALES -- se habrian truncado
en silencio al cargar el embedding (confirmado con
`model.max_seq_length=128` y el propio warning de HuggingFace
"Token indices sequence length is longer than the specified maximum
sequence length"). La estimacion de caracteres NO es un proxy
confiable para este tipo de contenido.

Fix: segundo paso que mide tokens REALES con el tokenizer del modelo
sobre cada pieza que ya paso el split por caracteres, y sub-particiona
por oraciones/clausulas (separador ". " o "; " o ", ") cualquier pieza
que siga sobre 128 tokens reales, repitiendo hasta que todas queden
por debajo. Se verifica de nuevo con el tokenizer real al final --
nunca se confia en la estimacion de caracteres como palabra final.

No relee el PDF: reusa el texto verbatim ya transcrito.

Uso: python _resplit_titulo_f_f46_por_limite_tokens.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _ingest_titulo_f_f46_verbatim import CHUNKS as PARENT_CHUNKS, CAPITULO
from _resplit_titulo_f_f42_por_limite_tokens import split_texto, TARGET_CHARS

LIMITE_TOKENS_REAL = 128


def _sub_particionar_por_tokens_reales(texto: str, tokenizer) -> list[str]:
    """Sub-particiona una pieza que sigue sobre el limite REAL de tokens
    (no estimado), por clausulas (". ", "; ", ", " en ese orden de
    preferencia) hasta que cada pieza mida <=128 tokens reales."""
    n_tokens = len(tokenizer.encode(texto, add_special_tokens=True))
    if n_tokens <= LIMITE_TOKENS_REAL:
        return [texto]

    for separador in [". ", "; ", ", "]:
        if separador in texto:
            partes = texto.split(separador)
            # reconstituir con el separador salvo en la ultima parte
            partes = [p + separador if i < len(partes) - 1 else p for i, p in enumerate(partes)]
            break
    else:
        # no hay donde partir limpio -- particion dura por palabras
        palabras = texto.split(" ")
        mitad = len(palabras) // 2
        partes = [" ".join(palabras[:mitad]), " ".join(palabras[mitad:])]

    if len(partes) == 1:
        # el separador elegido no partio nada real (una sola clausula
        # larga) -- forzar particion dura por palabras
        palabras = texto.split(" ")
        mitad = len(palabras) // 2
        partes = [" ".join(palabras[:mitad]), " ".join(palabras[mitad:])]

    # agrupar clausulas consecutivas en piezas <=128 tokens reales
    piezas: list[str] = []
    actual = ""
    for parte in partes:
        candidato = (actual + parte) if actual else parte
        if len(tokenizer.encode(candidato, add_special_tokens=True)) <= LIMITE_TOKENS_REAL:
            actual = candidato
        else:
            if actual:
                piezas.append(actual.strip())
            actual = parte
    if actual:
        piezas.append(actual.strip())

    # recursion por si alguna pieza resultante SIGUE sobre el limite
    resultado: list[str] = []
    for p in piezas:
        resultado.extend(_sub_particionar_por_tokens_reales(p, tokenizer))
    return resultado


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local (necesario ya desde el paso de troceo, para medir tokens reales)...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    child_chunks = []
    for parent in PARENT_CHUNKS:
        piezas_por_chars = split_texto(parent["texto"])
        piezas_finales: list[str] = []
        for pieza in piezas_por_chars:
            piezas_finales.extend(_sub_particionar_por_tokens_reales(pieza, tokenizer))
        for i, pieza in enumerate(piezas_finales, start=1):
            child_chunks.append({
                "id": f"{parent['id']}_p{i}",
                "seccion": parent["seccion"],
                "titulo": parent["titulo"],
                "texto": pieza,
            })

    print(f"Chunks padre: {len(PARENT_CHUNKS)} -> piezas chicas: {len(child_chunks)}")

    # Verificacion final con el tokenizer REAL -- nunca confiar en la
    # estimacion de caracteres como palabra final.
    over_limit = []
    for c in child_chunks:
        n = len(tokenizer.encode(c["texto"], add_special_tokens=True))
        if n > LIMITE_TOKENS_REAL:
            over_limit.append((c["id"], n))
    print(f"Piezas todavia sobre {LIMITE_TOKENS_REAL} tokens REALES tras sub-particion: {len(over_limit)}")
    for cid, n in over_limit:
        print(f"  ! {cid}: {n} tokens reales")
    if over_limit:
        raise SystemExit("Hay piezas que siguen sobre el limite real -- no subir a produccion sin resolver.")

    textos = [c["texto"] for c in child_chunks]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(child_chunks, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo piezas chicas a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    parent_ids = [p["id"] for p in PARENT_CHUNKS]
    print(f"\nBorrando los {len(parent_ids)} chunks-padre sobredimensionados...")
    sb.table("nsr10_chunks").delete().in_("id", parent_ids).execute()

    print(f"\nOK: {len(rows)} chunks chicos de F.4.6 cargados, {len(parent_ids)} chunks-padre borrados.")


if __name__ == "__main__":
    main()
