"""
NSR-10 Titulo K -- cierra los huecos puntuales dentro de K.3 (Requisitos
para zonas comunes) encontrados en el repaso de backend (issue #8) y
confirmados al revisar Titulos E/J/K completos (issue #5): K.3.7, K.3.8.1
y K.3.8.4 faltaban entre K.3.4-K.3.6 y K.3.8.2-K.3.8.3/K.3.8.5-K.3.8.7,
que ya estaban cargados.

Fuente: NSR-10-1571-1625.pdf (Drive, id 1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z
-- mismo archivo usado para K.4 el 2026-08-20), paginas internas K-18 a
K-21.

Uso: python _ingest_titulo_k_gaps_k37_k381_k384.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título K — Requisitos Complementarios"

CHUNKS = [
    {
        "id": "NSR10-K-K_3_7_proteccion_evacuacion",
        "seccion": "K.3.7 (Protección de los medios de evacuación)",
        "titulo": (
            "Proteccion de medios de evacuacion: corredores de acceso a "
            "salida con carga de ocupacion >30 personas deben separarse "
            "con muros/particiones de materiales NO combustibles; salidas "
            "protegidas contra fuego y humo en todo su recorrido, "
            "aberturas con marcos/puertas de combustion lenta o "
            "incombustibles."
        ),
        "texto": (
            "NSR-10 Título K, Capítulo K.3 — Requisitos para zonas "
            "comunes. K.3.7 — Protección de los medios de evacuación.\n\n"
            "K.3.7.1 CORREDORES — los corredores utilizados como acceso a "
            "una salida con carga de ocupación SUPERIOR A 30 personas "
            "deben separarse de las demás partes de la edificación por "
            "muros, particiones u otros elementos hechos con materiales "
            "NO COMBUSTIBLES.\n\n"
            "K.3.7.2 SALIDAS — cuando una salida requiere protección de "
            "las demás partes de la edificación, el elemento de "
            "separación debe cumplir:\n"
            "  K.3.7.2.1 — las salidas deben proporcionar protección "
            "contra el fuego y el humo a lo largo de TODO su recorrido, "
            "mediante separaciones levantadas con materiales no "
            "combustibles.\n"
            "  K.3.7.2.2 — todas las aberturas de las salidas deben "
            "protegerse con marcos y puertas de materiales de combustión "
            "lenta o incombustibles."
        ),
    },
    {
        "id": "NSR10-K-K_3_8_1_general_medios_salida",
        "seccion": "K.3.8.1 (General — medios de salida)",
        "titulo": (
            "Requisitos generales de medios de salida (K.3.8, marco "
            "general antes de puertas/escaleras): ubicacion visible sin "
            "obstrucciones permanentes, desembocar a calle/espacio "
            "abierto/area de refugio con dimensiones que aseguren la "
            "evacuacion."
        ),
        "texto": (
            "NSR-10 Título K, Capítulo K.3 — K.3.8 Medios de Salida. "
            "K.3.8.1 — General (requisitos que aplican a TODOS los "
            "medios de salida, previos al detalle de puertas K.3.8.2, "
            "escaleras interiores K.3.8.3 y escaleras exteriores "
            "K.3.8.4):\n\n"
            "K.3.8.1.1 — todas las salidas deben localizarse de tal "
            "manera que sean CLARAMENTE VISIBLES; su ubicación debe "
            "indicarse claramente y su acceso debe mantenerse SIN "
            "OBSTRUCCIONES y libre de obstáculos durante todo el "
            "tiempo.\n\n"
            "K.3.8.1.2 — toda salida debe desembocar DIRECTAMENTE a la "
            "calle, a un espacio abierto, o a un área de refugio no "
            "obstruible por fuego, humo u otra causa, y tener "
            "dimensiones tales que aseguren la evacuación de los "
            "ocupantes."
        ),
    },
    {
        "id": "NSR10-K-K_3_8_4_escaleras_exteriores",
        "seccion": "K.3.8.4 (Escaleras exteriores)",
        "titulo": (
            "Escaleras exteriores como medio de salida: deben cumplir los "
            "mismos requisitos que las interiores (K.3.8.3) mas "
            "proteccion especifica contra el fuego -- en edificaciones de "
            "3 o mas pisos deben estar solidamente integradas al "
            "edificio."
        ),
        "texto": (
            "NSR-10 Título K, Capítulo K.3 — K.3.8.4 Escaleras "
            "exteriores. Cualquier escalera exterior instalada "
            "permanentemente en una edificación puede servir como salida "
            "cuando cumpla los requisitos ya exigidos para escaleras "
            "interiores (K.3.8.3: ancho mínimo, huella/contrahuella según "
            "NTC 4145/4140, descansos, pasamanos, altura libre mínima "
            "2 m, materiales antideslizantes, prohibición de madera) MÁS "
            "los prescritos aquí:\n\n"
            "K.3.8.4.1 — Protección contra el fuego: las escaleras "
            "exteriores utilizadas en edificaciones de TRES O MÁS PISOS "
            "deben estar SÓLIDAMENTE INTEGRADAS al edificio, y su "
            "capacidad portante se determina según los factores y carga "
            "de ocupación que el uso determine."
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
    textos = [c["texto"] for c in CHUNKS]
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

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks K.3.7/K.3.8.1/K.3.8.4 cargados con embedding.")


if __name__ == "__main__":
    main()
