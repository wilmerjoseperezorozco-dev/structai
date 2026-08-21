"""
Agrega el chunk verbatim de NSR-10 A.3.8 (Estructuras aisladas sismicamente en
su base) y A.3.9 (Uso de elementos disipadores de energia) — gap real
detectado 2026-08-20 (cero chunks existentes pese a que la norma si cubre el
tema, aunque de forma muy breve).

Fuente: NSR-10-81-94.pdf (Drive, id 1Z2rzll9ER-td_OGXzTUUPv1R68kAoNSL),
paginas internas A-49 a A-51.

Uso: python _ingest_a38_a39.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CHUNK = {
    "id": "NSR10-A-A_3_8_a_A_3_9",
    "capitulo": "NSR-10 Título A — Requisitos generales de diseño y construcción sismo resistente",
    "seccion": "A.3.8 a A.3.9",
    "titulo": (
        "Estructuras aisladas sismicamente en su base y uso de disipadores de energia: la "
        "NSR-10 PERMITE ambos sistemas pero no desarrolla metodologia de diseno propia — "
        "remite integramente a FEMA 450/NEHRP 2003 o ASCE/SEI 7-05 (ambos documentos "
        "estadounidenses de mediados de los 2000, hoy superados por ediciones mas recientes "
        "como ASCE 7-16/7-22 Cap. 17), exige cumplir Articulos 10 y 11 de la Ley 400 de 1997, "
        "y obliga supervision tecnica permanente (Titulo I)."
    ),
    "texto": (
        "NSR-10 Título A, Capítulo A.3 — Requisitos generales de diseño sismo resistente. "
        "A.3.8 — Estructuras aisladas sísmicamente en su base.\n\n"
        "A.3.8.1 — Se permite el empleo de estructuras aisladas sísmicamente en su base, "
        "siempre y cuando se cumplan en su totalidad los requisitos al respecto de uno de "
        "los dos documentos siguientes: (a) \"NEHRP Recommended Provisions for Seismic "
        "Regulations for New Buildings — Provisions and Commentary\", 2003 Edition, Federal "
        "Emergency Management Agency, FEMA 450, Building Seismic Safety Council, National "
        "Institute of Buildings Sciences, Washington, D.C., USA, 2004; (b) \"Minimum Design "
        "Loads for Building and Other Structures\", ASCE/SEI 7-05, Structural Engineering "
        "Institute of the American Society of Civil Engineers, Reston, Virginia, USA, 2006.\n\n"
        "A.3.8.2 — En el diseño y construcción de estructuras aisladas sísmicamente en su "
        "base, se deben cumplir los requisitos de los Artículos 10 y 11 de la Ley 400 de "
        "1997, asumiendo el diseñador estructural y el constructor las responsabilidades que "
        "allí se indican.\n\n"
        "A.3.8.3 — La construcción de una edificación que utilice sistemas de aislamiento "
        "sísmico en su base debe someterse a una supervisión técnica permanente, como la "
        "describe el Título I.\n\n"
        "A.3.9 — Uso de elementos disipadores de energía.\n\n"
        "A.3.9.1 — Se permite el empleo de elementos disipadores de energía, siempre y "
        "cuando se cumplan en su totalidad los requisitos al respecto de uno de los dos "
        "documentos siguientes: (a) \"NEHRP Recommended Provisions for Seismic Regulations "
        "for New Buildings — Provisions and Commentary\", 2003 Edition, FEMA 450, Building "
        "Seismic Safety Council, National Institute of Buildings Sciences, Washington, D.C., "
        "USA, 2004; (b) \"Minimum Design Loads for Building and Other Structures\", ASCE/SEI "
        "7-05, Structural Engineering Institute of the American Society of Civil Engineers, "
        "Reston, Virginia, USA, 2006.\n\n"
        "A.3.9.2 — En el diseño y construcción de estructuras que tengan elementos "
        "disipadores de energía, se deben cumplir los requisitos de los Artículos 10 y 11 de "
        "la Ley 400 de 1997, asumiendo el diseñador estructural y el constructor las "
        "responsabilidades que allí se indican.\n\n"
        "A.3.9.3 — La construcción de una edificación que utilice elementos disipadores de "
        "energía debe someterse a una supervisión técnica permanente, como la describe el "
        "Título I.\n\n"
        "NOTA IMPORTANTE PARA EL USUARIO: estos 6 artículos son TODO lo que la NSR-10 dice "
        "sobre aislamiento sísmico y disipadores — no contiene ninguna ecuación, criterio de "
        "diseño, ni procedimiento de análisis propio para estos sistemas. La norma colombiana "
        "delega el 100% de la metodología técnica a dos referencias estadounidenses de "
        "mediados de la década de 2000 (FEMA 450 de 2004, ASCE/SEI 7-05 de 2006), hoy "
        "superadas por ediciones más recientes (ASCE 7-16 y 7-22 Capítulo 17 son el estándar "
        "actual de diseño sismo-aislado en EE.UU.). Un ingeniero que quiera diseñar con "
        "aislamiento de base o disipadores en Colombia debe recurrir directamente a esas "
        "normas internacionales — la NSR-10 solo autoriza el uso y fija responsabilidades "
        "legales y de supervisión."
    ),
}


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    vec = model.encode([CHUNK["texto"]], normalize_embeddings=True)[0]

    row = dict(CHUNK)
    row["embedding"] = vec.tolist()
    row["titulo"] = row["titulo"][:500]

    sb.table("nsr10_chunks").upsert(row, on_conflict="id").execute()
    print(f"OK: {CHUNK['id']} cargado con embedding ({len(CHUNK['texto'])} chars).")


if __name__ == "__main__":
    main()
