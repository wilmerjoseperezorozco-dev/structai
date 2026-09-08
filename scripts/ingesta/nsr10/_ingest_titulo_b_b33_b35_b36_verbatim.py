"""
Ingesta verbatim de Título B, secciones B.3.3 (Cargas muertas mínimas),
B.3.5 (Equipos fijos) y B.3.6 (Consideraciones especiales) -- NSR-10.
Cierra 3 de las 7 secciones sin cobertura confirmadas en la auditoría
numeral-por-numeral de Título B (2026-09-08).

Fuente: NSR-10-228-233.pdf, página PDF 2 (B-10) para B.3.3, y página
PDF 6 (B-14) para B.3.5/B.3.6, leídas visualmente con Read pages= sobre
el PDF nativo.

Nota real (no ejecutada en este script, dejada para una sesión
posterior a pedido explícito del usuario): en las mismas páginas de
este PDF (B-10 a B-13) está el texto verbatim completo de B.3.4
(Elementos no estructurales) con sus 6 tablas reales (B.3.4.1-1 a -4,
B.3.4.2-1 a -5, B.3.4.3-1) -- los chunks actuales de B.3.4 en
producción (`NSR10-B-B_3_4_r1/r2/r3`) son un resumen condensado con
solo 2-3 valores de ejemplo por tabla, no verbatim completo (mismo
patrón "resumen disfrazado de completo" ya visto en A.3.3/K.2/K.3/F.3).
Sigue siendo la referencia de mayor valor práctico pendiente de
Título B -- ver memoria privada.

Uso: python _ingest_titulo_b_b33_b35_b36_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "B"

CHUNKS = [
    {
        "id": "NSR10-B-B_3_3_cargas_muertas_minimas",
        "seccion": "B.3.3 — Cargas muertas mínimas",
        "titulo": "Título B, B.3.3: al calcular cargas muertas deben usarse masas reales de los materiales, con especial cuidado en determinar masas representativas (peso del fabricante o evaluación analítica/experimental).",
        "texto": (
            "B.3.3 — CARGAS MUERTAS MÍNIMAS\n\n"
            "Al calcular las cargas muertas deben utilizarse las masas reales de los "
            "materiales. Debe ponerse especial cuidado en determinar masas "
            "representativas en este cálculo, utilizar el peso especificado por el "
            "fabricante o en su defecto deben evaluarse analítica o "
            "experimentalmente."
        ),
    },
    {
        "id": "NSR10-B-B_3_5_equipos_fijos",
        "seccion": "B.3.5 — Equipos fijos",
        "titulo": "Título B, B.3.5: dentro de las cargas muertas debe incluirse la masa de todos los equipos fijos apoyados sobre elementos estructurales (ascensores, bombas hidráulicas, transformadores, aire acondicionado).",
        "texto": (
            "B.3.5 — EQUIPOS FIJOS\n\n"
            "Dentro de las cargas muertas deben incluirse la masa correspondiente de "
            "todos los equipos fijos que estén apoyados sobre elementos "
            "estructurales tales como ascensores, bombas hidráulicas, "
            "transformadores, equipos de aire acondicionado y ventilación y otros."
        ),
    },
    {
        "id": "NSR10-B-B_3_6_consideraciones_especiales",
        "seccion": "B.3.6 — Consideraciones especiales",
        "titulo": "Título B, B.3.6: los profesionales de construcción/supervisión técnica y el propietario deben verificar en obra que los pesos reales de materiales no superen los valores de diseño; responsabilidad de quien suscribe la licencia de construcción. Remite a A.1.3.6.5.",
        "texto": (
            "B.3.6 — CONSIDERACIONES ESPECIALES\n\n"
            "Los profesionales que participen en la construcción y la supervisión "
            "técnica, y el propietario de la edificación, deben ser conscientes de "
            "los valores de las cargas muertas utilizadas en el diseño y tomar las "
            "precauciones necesarias para verificar en la obra que los pesos de los "
            "materiales utilizados no superen los valores usados en el diseño. Es "
            "responsabilidad de quien suscribe como constructor la licencia de "
            "construcción el cumplimiento de este requisito. Véase A.1.3.6.5."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    textos = [c["texto"] for c in CHUNKS]
    print(f"Codificando {len(textos)} chunks de B.3.3/B.3.5/B.3.6...")
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for chunk, vec in zip(CHUNKS, vectores):
        rows.append({
            "id": chunk["id"],
            "capitulo": CAPITULO,
            "seccion": chunk["seccion"],
            "titulo": chunk["titulo"][:500],
            "texto": chunk["texto"],
            "embedding": vec.tolist(),
        })

    print(f"Subiendo {len(rows)} chunks a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    # Estas 3 piezas son cortas -- ya estan dentro del limite de 128 tokens
    # sin necesidad de re-troceo, pero se verifica igual como red de seguridad.
    tokenizer = model.tokenizer
    LIMITE = 128
    sobre_limite = []
    for c in CHUNKS:
        n = len(tokenizer.encode(c["texto"], add_special_tokens=True))
        if n > LIMITE:
            sobre_limite.append((c["id"], n))
    print(f"Piezas sobre {LIMITE} tokens reales: {len(sobre_limite)}")
    for cid, n in sobre_limite:
        print(f"  ! {cid}: {n} tokens reales -- requiere re-troceo, no dejar asi")

    print("OK.")


if __name__ == "__main__":
    main()
