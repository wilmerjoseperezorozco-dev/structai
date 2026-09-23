"""
Ingesta verbatim de Título B, Capítulo B.5 (Empuje de tierra y presión
hidrostática) -- NSR-10. Fase 1 del plan de cierre del Título B
(2026-09-23), auditoría real de numerales confirmó B.5 en 1/8 (faltan
7) -- capítulo completo cabe en 1 sola página (B-19).

Fuente: NSR-10-238.pdf, página PDF 1 (B-19, capítulo completo, PDF
completo). Leída visualmente con Read pages= sobre el PDF nativo --
nunca extracción mecánica (pypdf).

Uso: python _ingest_titulo_b_b5_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "B"

CHUNKS = [
    {
        "id": "NSR10-B-B_5_completo_empuje_tierra_presion_hidrostatica",
        "seccion": "B.5.1 a B.5.4 — Empuje de tierra y presión hidrostática completo (muros de sótano, subpresión, suelos expansivos, zonas inundables)",
        "titulo": "NSR-10 Título B — Capítulo B.5 — Empuje de tierra y presión hidrostática",
        "texto": (
            "CAPÍTULO B.5 — EMPUJE DE TIERRA Y PRESIÓN HIDROSTÁTICA\n\n"
            "B.5.1 — EMPUJE EN MUROS DE CONTENCIÓN DE SÓTANOS\n\n"
            "B.5.1.1 — En el diseño de los muros de contención de los "
            "sótanos y otras estructuras aproximadamente verticales "
            "localizadas bajo tierra, debe tenerse en cuenta el empuje "
            "lateral del suelo adyacente. Igualmente deben tenerse en "
            "cuenta las posibles cargas tanto vivas como muertas que "
            "puedan darse en la parte superior del suelo adyacente. "
            "Cuando parte o toda la estructura de sótano está por "
            "debajo del nivel freático, el empuje debe calcularse para "
            "el peso del suelo sumergido y la totalidad de la presión "
            "hidrostática. Deben consultarse los requisitos del Título "
            "H del Reglamento.\n\n"
            "B.5.1.2 — El coeficiente de empuje de tierra deberá "
            "elegirse en función de las condiciones de deformabilidad "
            "de la estructura de contención, pudiéndose asignar el "
            "coeficiente de empuje activo cuando las estructuras tengan "
            "libertad de giro y de traslación; en caso contrario, el "
            "coeficiente será el de reposo o uno mayor, hasta el valor "
            "del pasivo, a juicio del ingeniero geotecnista y de "
            "acuerdo con las condiciones geométricas de la estructura y "
            "de los taludes adyacentes, cumpliendo los requisitos "
            "adicionales del Título H del Reglamento.\n\n"
            "B.5.2 — PRESIÓN ASCENDENTE, SUBPRESIÓN, EN LOSAS DE PISO DE "
            "SÓTANOS — En el diseño de la losa de piso de sótano y "
            "otras estructuras aproximadamente horizontales localizadas "
            "bajo tierra debe tenerse en cuenta la totalidad de la "
            "presión hidrostática ascendente aplicada sobre el área. La "
            "cabeza de presión hidrostática debe medirse desde el nivel "
            "freático. La misma consideración debe hacerse en el diseño "
            "de tanques y piscinas. Véase el capítulo C.23.\n\n"
            "B.5.3 — SUELOS EXPANSIVOS — Cuando existan suelos "
            "expansivos bajo la cimentación de la edificación, o bajo "
            "losas apoyadas sobre el terreno, la cimentación, las losas "
            "y los otros elementos de la edificación, deben diseñarse "
            "para que sean capaces de tolerar los movimientos que se "
            "presenten, y resistir las presiones ascendentes causadas "
            "por la expansión del suelo, o bien los suelos expansivos "
            "deben retirarse o estabilizarse debajo y en los "
            "alrededores de la edificación, de acuerdo con las "
            "indicaciones del ingeniero geotecnista. Debe consultarse "
            "el Título H del Reglamento.\n\n"
            "B.5.4 — ZONAS INUNDABLES — En aquellas zonas designadas "
            "por la autoridad competente como inundables, el sistema "
            "estructural de la edificación debe diseñarse y "
            "construirse para que sea capaz de resistir los efectos de "
            "flotación y de desplazamiento lateral causados por los "
            "efectos hidrostáticos, hidrodinámicos y de impacto de "
            "objetos flotantes."
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
    print(f"Codificando {len(textos)} chunks...")
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

    print(f"\nSubiendo {len(rows)} chunks a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK.")


if __name__ == "__main__":
    main()
