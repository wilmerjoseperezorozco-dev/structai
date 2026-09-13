"""
Título J — re-ingesta verbatim, Capítulo J.1 (Generalidades), primer lote
de la re-ingesta completa decidida el 2026-09-12 (ver memoria del autor,
project_structai_nsr10_inventario_titulos y project_structai_plataforma_
investigativa_ia): los 49 chunks existentes de Título J están CONDENSADOS
en resumen parafraseado (no verbatim) Y además tienen las tildes
eliminadas por completo — confirmado leyendo NSR10-J-J_1_1_r1 real antes
de escribir este script.

Fuente: NSR-10-1501-1570.pdf, páginas 30-32 (Capítulo J.1 completo,
J.1.1.1 a J.1.1.3 + Tabla J.1.1-1). Extraído VISUALMENTE (Read con
render de imagen), no con pdftotext/fitz — ambos devuelven el carácter
de reemplazo "�" en vez de tildes reales en este PDF específico (mismo
tipo de corrupción de fuente ya visto en un PDF de Título E), confirmado
probando los dos antes de decidir usar lectura visual.

Reemplaza (no complementa) los 4 chunks obsoletos NSR10-J-J_1_1_r1..r4.
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

CAPITULO = "NSR-10 Título J — Requisitos de Protección Contra Incendios en Edificaciones"

# Chunks obsoletos (resumen condensado + sin tildes) que este lote reemplaza
IDS_OBSOLETOS = [
    "NSR10-J-J_1_1_r1", "NSR10-J-J_1_1_r2", "NSR10-J-J_1_1_r3", "NSR10-J-J_1_1_r4",
]

CHUNKS = [
    {
        "id": "NSR10-J-J_1_1_1",
        "seccion": "J.1.1.1",
        "titulo": "J.1.1.1 — Propósito y alcance del Título J: 5 premisas (reducir riesgo, evitar propagación, facilitar evacuación y extinción, minimizar colapso)",
        "texto": (
            "J.1.1.1 — Toda edificación deberá cumplir con los requisitos mínimos de protección contra incendios "
            "establecidos en el presente Capítulo, correspondientes al uso de la edificación y su grupo de ocupación, "
            "de acuerdo con la clasificación dada en J.1.1.2. En consecuencia, el propósito del Título J es el de "
            "establecer dichos requisitos con base en las siguientes premisas: "
            "(a) Reducir en todo lo posible el riesgo de incendios en edificaciones. "
            "(b) Evitar la propagación del fuego tanto dentro de las edificaciones como hacia estructuras aledañas. "
            "(c) Facilitar las tareas de evacuación de los ocupantes de las edificaciones en caso de incendio. "
            "(d) Facilitar el proceso de extinción de incendios en las edificaciones. "
            "(e) Minimizar el riesgo de colapso de la estructura durante las labores de evacuación y extinción."
        ),
    },
    {
        "id": "NSR10-J-J_1_1_2",
        "seccion": "J.1.1.2",
        "titulo": "J.1.1.2 — Clasificación de edificaciones por Grupos de Ocupación (remite a K.2.1.2), Tabla J.1.1-1 completa",
        "texto": (
            "J.1.1.2 — Para efectos de la aplicación de los requisitos que se establecen en este Título se hace "
            "necesaria la clasificación de las edificaciones por Grupos de Ocupación. Según esto se utiliza la "
            "clasificación que se presenta en el numeral K.2.1.2 de este Reglamento, cuya tabla se repite aquí para "
            "efectos ilustrativos. Para las explicaciones y detalles referentes a la clasificación de edificaciones "
            "referirse al Capítulo K.2. "
            "Tabla J.1.1-1 — Grupos y subgrupos de ocupación (Grupo/Subgrupo — Clasificación — Sección del Reglamento): "
            "A — Almacenamiento — K.2.2 (A-1 Riesgo moderado; A-2 Riesgo bajo). "
            "C — Comercial — K.2.3 (C-1 Servicios; C-2 Bienes). "
            "E — Especiales — K.2.4. "
            "F — Fabril e industrial — K.2.5 (F-1 Riesgo moderado; F-2 Riesgo bajo). "
            "I — Institucional — K.2.6 (I-1 Reclusión; I-2 Salud o incapacidad; I-3 Educación; I-4 Seguridad pública; "
            "I-5 Servicio público). "
            "L — Lugares de reunión — K.2.7 (L-1 Deportivos; L-2 Culturales y teatros; L-3 Sociales y recreativos; "
            "L-4 Religiosos; L-5 De transporte). "
            "M — Mixto y otros — K.2.8. "
            "P — Alta peligrosidad — K.2.9. "
            "R — Residencial — K.2.10 (R-1 Unifamiliar y bifamiliar; R-2 Multifamiliar; R-3 Hoteles). "
            "T — Temporal — K.2.11."
        ),
    },
    {
        "id": "NSR10-J-J_1_1_3",
        "seccion": "J.1.1.3",
        "titulo": "J.1.1.3 — Responsabilidad del cumplimiento de Títulos J y K recae en el profesional constructor del proyecto",
        "texto": (
            "J.1.1.3 — La responsabilidad del cumplimiento del Título J - Requisitos de protección contra el fuego "
            "en edificaciones y el Título K – Otros requisitos complementarios, recae en el profesional que figura "
            "como constructor del proyecto para la solicitud de la licencia de construcción."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    tokenizer = model.tokenizer

    piezas_finales = []
    for chunk in CHUNKS:
        piezas = _sub_particionar_por_tokens_reales(chunk["texto"], tokenizer)
        for i, pieza in enumerate(piezas):
            sufijo = "" if len(piezas) == 1 else f"_r{i + 1}"
            piezas_finales.append({
                "id": chunk["id"] + sufijo,
                "seccion": chunk["seccion"],
                "titulo": chunk["titulo"],
                "texto": pieza,
            })

    print(f"{len(CHUNKS)} numerales -> {len(piezas_finales)} piezas tras trocear por límite real de tokens")

    textos = [p["texto"] for p in piezas_finales]
    vectores = model.encode(textos, normalize_embeddings=True, show_progress_bar=True)

    rows = [
        {
            "id": p["id"], "capitulo": CAPITULO, "seccion": p["seccion"],
            "titulo": p["titulo"][:500], "texto": p["texto"], "embedding": v.tolist(),
        }
        for p, v in zip(piezas_finales, vectores)
    ]
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"Upsert OK: {len(rows)} filas nuevas.")

    if IDS_OBSOLETOS:
        sb.table("nsr10_chunks").delete().in_("id", IDS_OBSOLETOS).execute()
        print(f"Borrados {len(IDS_OBSOLETOS)} chunks obsoletos (resumen sin tildes): {IDS_OBSOLETOS}")


if __name__ == "__main__":
    main()
