"""
Ingesta verbatim de Título B, Capítulo B.1 (Requisitos generales) --
NSR-10. Fase 1 del plan de cierre del Título B (2026-09-23),
auditoría real de numerales confirmó B.1 en 1/16 (faltan 15) --
capítulo corto (2 páginas) pero fundacional, citado por B.2 y todos
los demás capítulos de cargas.

Fuente: NSR-10-219-221.pdf, páginas PDF 2-3 (B-1 a B-2, capítulo
completo). Leídas visualmente con Read pages= sobre el PDF nativo --
nunca extracción mecánica (pypdf).

Uso: python _ingest_titulo_b_b1_verbatim.py
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
        "id": "NSR10-B-B_1_1_a_1_2_alcance_requisitos_basicos",
        "seccion": "B.1.1 y B.1.2 — Alcance y requisitos básicos (resistencia, funcionamiento, deformaciones impuestas, análisis)",
        "titulo": "NSR-10 Título B — Capítulo B.1 — Requisitos generales",
        "texto": (
            "TÍTULO B — CARGAS\n\n"
            "CAPÍTULO B.1 — REQUISITOS GENERALES\n\n"
            "B.1.1 — ALCANCE — El presente Título de este Reglamento da "
            "los requisitos mínimos que deben cumplir las edificaciones "
            "con respecto a cargas que deben emplearse en su diseño, "
            "diferentes a las fuerzas o efectos que impone el sismo. "
            "Para que una estructura sismo resistente cumpla "
            "adecuadamente su objetivo, debe ser capaz de resistir "
            "además de los efectos sísmicos, los efectos de las cargas "
            "prescritas en el presente Título. El diseño de los "
            "elementos que componen la estructura de la edificación "
            "debe hacerse para la combinación de carga crítica.\n\n"
            "B.1.2 — REQUISITOS BÁSICOS\n\n"
            "B.1.2.1 — La estructura y todas sus partes deben cumplir, "
            "además de las prescripciones dadas en el Título A por "
            "razones sísmicas, los siguientes requisitos:\n\n"
            "B.1.2.1.1 — Resistencia — La estructura de la edificación "
            "y todas sus partes deben diseñarse y construirse para que "
            "los materiales utilizados en la construcción de los "
            "elementos y sus conexiones puedan soportar con seguridad "
            "todas las cargas contempladas en el presente Título B de "
            "la NSR-10 sin exceder las resistencias de diseño cuando se "
            "mayoran las cargas por medio de coeficientes de carga, o "
            "los esfuerzos admisibles cuando se utilicen las cargas sin "
            "mayorar.\n\n"
            "B.1.2.1.2 — Funcionamiento — Los sistemas estructurales y "
            "sus componentes deben diseñarse para que tengan una "
            "rigidez adecuada que limite: (a) las deflexiones verticales "
            "de los elementos, (b) la deriva ante cargas de sismo y "
            "viento, (c) las vibraciones y (d) cualquier otra "
            "deformación que afecte adversamente el funcionamiento de "
            "la estructura o edificación.\n\n"
            "B.1.2.1.3 — Fuerzas causadas por deformaciones impuestas — "
            "Deben tenerse en cuenta en el diseño las fuerzas causadas "
            "por deformaciones impuestas a la estructura por: (a) los "
            "asentamientos diferenciales contemplados en el título H, "
            "(b) por restricción a los cambios dimensionales debidos a "
            "variaciones de temperatura, expansiones por humedad, "
            "retracción de fraguado, flujo plástico y efectos "
            "similares.\n\n"
            "B.1.2.1.4 — Análisis — Los efectos de las cargas en los "
            "diferentes elementos de la estructura y sus conexiones "
            "deben determinarse utilizando métodos aceptados de "
            "análisis estructural, teniendo en cuenta los principios de "
            "equilibrio, estabilidad general, compatibilidad de "
            "deformaciones y las propiedades de los materiales tanto a "
            "corto como a largo plazo. En aquellos elementos que "
            "tiendan a acumular deformaciones residuales bajo cargas de "
            "servicio sostenidas (flujo plástico) debe tenerse en "
            "cuenta en el análisis sus efectos durante la vida útil de "
            "la estructura."
        ),
    },
    {
        "id": "NSR10-B-B_1_3_a_1_4_integridad_estructural_trayectorias",
        "seccion": "B.1.3 y B.1.4 — Unidad e integridad estructural general y trayectorias de cargas",
        "titulo": "NSR-10 Título B — Capítulo B.1 — Requisitos generales",
        "texto": (
            "B.1.3 — UNIDAD E INTEGRIDAD ESTRUCTURAL GENERAL\n\n"
            "B.1.3.1 — Además de los requisitos de amarre entre partes "
            "de la estructura y entre los elementos estructurales que "
            "se dan por razones sísmicas en el Título A de este "
            "Reglamento, deben tenerse en cuenta los requisitos "
            "adicionales que se dan a continuación. En el caso de "
            "estructuras de concreto reforzado deben consultarse "
            "también los requisitos de C.7.13.\n\n"
            "B.1.3.2 — Por razones accidentales o debido a que la "
            "estructura se utiliza para fines diferentes a los previstos "
            "en el diseño, ésta puede sufrir daño local o la falta de "
            "capacidad resistente en un elemento o en una porción menor "
            "de la edificación. Debido a esto los elementos y miembros "
            "estructurales deben estar unidos con el fin de obtener una "
            "integridad estructural general que les permita "
            "experimentar daño local sin que la estructura en general "
            "pierda su estabilidad ni extienda el daño local a otros "
            "elementos, ni se presente colapso progresivo.\n\n"
            "B.1.3.3 — El método más común para obtener integridad "
            "estructural consiste en disponer los elementos "
            "estructurales de tal manera que provean estabilidad "
            "general a la estructura, dándoles continuidad y "
            "garantizando que tengan suficiente ductilidad, capacidad "
            "de absorción y capacidad de disipación de energía para que "
            "pueda redistribuir cargas desde una zona dañada a las "
            "regiones adyacentes sin colapso.\n\n"
            "B.1.4 — TRAYECTORIAS DE CARGAS\n\n"
            "B.1.4.1 — El sistema estructural debe diseñarse de tal "
            "manera que exista una trayectoria continua para todas las "
            "cargas y solicitaciones consideradas en el diseño.\n\n"
            "B.1.4.2 — La trayectoria de carga que se disponga debe "
            "diseñarse de tal manera que sea capaz de resistir "
            "adecuadamente las fuerzas desde su punto de aplicación a "
            "la estructura, o lugar donde se originen en la estructura, "
            "a través de los elementos estructurales hasta la "
            "cimentación u otros elementos de apoyo.\n\n"
            "B.1.4.3 — En estructuras sometidas a fuerzas horizontales "
            "de viento, sismo, empuje de tierras y otras, los elementos "
            "estructurales que sean parte de la trayectoria de cargas "
            "deben ser capaces de resistir las fuerzas que se aplican "
            "en la superficie de otros elementos estructurales ya sea "
            "como cargas distribuidas o efectos inerciales causados por "
            "la masa de estos elementos y debe incluir diafragmas "
            "cuando sean requeridos para transmitir las fuerzas "
            "horizontales a los elementos verticales del sistema de "
            "resistencia ante fuerzas laterales."
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
