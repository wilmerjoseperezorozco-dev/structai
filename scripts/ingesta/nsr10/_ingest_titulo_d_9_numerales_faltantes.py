"""
NSR-10 Titulo D, 9 numerales hoja reales confirmados sin chunk propio en
la re-auditoria estricta 2026-09-09 (ver docs/fuentes-normativas.md, fila
de Titulo D) -- el mejor resultado de todos los titulos re-auditados
salvo I (~2% del titulo).

Los 9 son remisiones cortas o definiciones puntuales de una sola frase
cada una -- ninguno es contenido critico aislado (D.4.5.3/D.4.5.4 remiten
a D.3.4/D.3.5, que ya estan completos verbatim).

Fuentes (13 PDF ya descargados en la sesion de auditoria, Drive carpeta
de Titulo D), pagina real de cada uno confirmada leyendo visualmente:
- D.1.2.2: NSR-10-565-569.pdf, pagina D-2
- D.3.7.2.7: NSR-10-578-585.pdf, pagina D-18
- D.4.5.3 y D.4.5.4: NSR-10-586-594.pdf, pagina D-25
- D.5.1.6.1 y D.5.4.3.1: NSR-10-596-607.pdf, paginas D-33 y PDF pag.6
- D.6.3.5: NSR-10-608-610.pdf, pagina D-44
- D.10.5.2.1 y D.10.6.2.1: NSR-10-618-626.pdf, paginas D-55/D-56

Uso: python _ingest_titulo_d_9_numerales_faltantes.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _resplit_titulo_f_f46_por_limite_tokens import _sub_particionar_por_tokens_reales

CAPITULO = "NSR-10 Título D — Mampostería Estructural"

CHUNKS = [
    {
        "id": "NSR10-D-D_1_2_2_memorias",
        "seccion": "D.1.2.2 (Memorias)",
        "titulo": "Remisión de las memorias de cálculo de mampostería estructural al Capítulo A.1.5.3.",
        "texto": (
            "NSR-10 Título D, Capítulo D.1 — D.1.2.2 — MEMORIAS — Se debe cumplir "
            "lo estipulado al respecto en A.1.5.3."
        ),
    },
    {
        "id": "NSR10-D-D_3_7_2_7_refrentado_ensayo",
        "seccion": "D.3.7.2.7 (Refrentado y Ensayo de Muretes)",
        "titulo": "Norma técnica aplicable (NTC 3495 / ASTM E447) para el refrentado y ensayo de muretes de mampostería.",
        "texto": (
            "NSR-10 Título D, Capítulo D.3 — D.3.7.2.7 — Refrentado y ensayo — Los "
            "muretes deben refrentarse y ensayarse bajo la norma NTC 3495 (ASTM "
            "E447)."
        ),
    },
    {
        "id": "NSR10-D-D_4_5_3_a_4_morteros",
        "seccion": "D.4.5.3 a D.4.5.4 (Mortero de Pega y Mortero de Inyección)",
        "titulo": "Remisión de los requisitos de mortero de pega y mortero de inyección a los capítulos D.3.4 y D.3.5.",
        "texto": (
            "NSR-10 Título D, Capítulo D.4 — D.4.5.3 — MORTERO DE PEGA — Debe "
            "cumplir con los requisitos de D.3.4. D.4.5.4 — MORTERO DE INYECCIÓN "
            "— Debe cumplir con los requisitos en D.3.5."
        ),
    },
    {
        "id": "NSR10-D-D_5_1_6_1_resistencia_traccion",
        "seccion": "D.5.1.6.1 (Resistencia a la Tracción de la Mampostería)",
        "titulo": "Suposición de diseño: la mampostería no resiste esfuerzos de tracción, base del método del estado límite de resistencia.",
        "texto": (
            "NSR-10 Título D, Capítulo D.5 — D.5.1.6 — SUPOSICIONES DE DISEÑO — El "
            "diseño de mampostería estructural por el método del estado límite de "
            "resistencia se basa en las siguientes suposiciones: D.5.1.6.1 — "
            "Resistencia a la tracción de la mampostería — La mampostería no "
            "resiste esfuerzos de tracción."
        ),
    },
    {
        "id": "NSR10-D-D_5_4_3_1_relacion_altura_espesor",
        "seccion": "D.5.4.3.1 (Relación Altura Efectivo/Espesor Efectivo Máxima)",
        "titulo": "Límite de esbeltez: la relación entre altura efectiva y espesor efectivo no puede superar 25 en muros estructurales.",
        "texto": (
            "NSR-10 Título D, Capítulo D.5 — D.5.4.3.1 — La relación entre altura "
            "efectiva y espesor efectivo no puede ser superior a 25 en muros "
            "estructurales."
        ),
    },
    {
        "id": "NSR10-D-D_6_3_5_diametro_minimo_cavidad",
        "seccion": "D.6.3.5 (Diámetro Mínimo de Barras en la Cavidad)",
        "titulo": "Límite de diámetro de las barras de refuerzo en muros de cavidad reforzada, en función del espesor de la cavidad.",
        "texto": (
            "NSR-10 Título D, Capítulo D.6 — D.6.3.5 — DIÁMETRO MÍNIMO — El "
            "diámetro de las barras de la cavidad no puede ser mayor que la "
            "cuarta parte de su espesor."
        ),
    },
    {
        "id": "NSR10-D-D_10_5_2_1_a_10_6_2_1_espesores_confinamiento",
        "seccion": "D.10.5.2.1 y D.10.6.2.1 (Espesores Mínimos de Columnas y Vigas de Confinamiento)",
        "titulo": "Espesor mínimo de las columnas y vigas de confinamiento en mampostería confinada: debe ser el mismo del muro confinado.",
        "texto": (
            "NSR-10 Título D, Capítulo D.10 — D.10.5.2 — DIMENSIONES MÍNIMAS — Las "
            "dimensiones mínimas para los elementos de confinamiento debe ser las "
            "siguientes: D.10.5.2.1 — Espesor mínimo — El espesor mínimo de los "
            "elementos de confinamiento debe ser el mismo del muro confinado. "
            "D.10.6.2 — DIMENSIONES MÍNIMAS — Las dimensiones mínimas para las "
            "vigas de confinamiento debe ser las siguientes: D.10.6.2.1 — Espesor "
            "mínimo — El espesor mínimo de las vigas de confinamiento debe ser el "
            "mismo del muro confinado."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    for c in CHUNKS:
        print(f"  {c['id']} ({c['seccion']}): {len(c['texto'])} chars")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    print("\nSub-particionando por tokens REALES (limite 128, medido con el tokenizer)...")
    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            n_tok = len(tokenizer.encode(pieza, add_special_tokens=True))
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })
            print(f"  {chunk['id'] + sufijo:60s} {n_tok:3d} tokens")
    print(f"\n{len(CHUNKS)} piezas originales -> {len(piezas_finales)} piezas reales tras troceo.")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = []
    for pieza, vec in zip(piezas_finales, vectores):
        rows.append({
            "id": pieza["id"],
            "capitulo": CAPITULO,
            "seccion": pieza["seccion"],
            "titulo": pieza["titulo"][:500],
            "texto": pieza["texto"],
            "embedding": vec.tolist(),
        })

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de los 9 numerales de Título D cargados. Título D completo.")


if __name__ == "__main__":
    main()
