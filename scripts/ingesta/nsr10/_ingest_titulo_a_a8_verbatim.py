"""
Ingesta verbatim de Título A, Capítulo A.8 (Efectos sísmicos sobre
elementos estructurales que no hacen parte del sistema de resistencia
sísmica) -- NSR-10. Fase 1 del plan de cierre del Título A (2026-09-22),
auditoría real de numerales confirmó A.8 en 0% de cobertura (18 numerales
reales, ninguno con chunk).

Fuente: NSR-10-124-128.pdf, páginas PDF 3-5 (A-83 a A-85), leídas
visualmente con Read pages= sobre el PDF nativo. Continuidad exacta desde
el fin de A.7 (página 2 del mismo PDF, ver
_ingest_titulo_a_a7_verbatim.py).

Uso: python _ingest_titulo_a_a8_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"

CHUNKS = [
    {
        "id": "NSR10-A-A_8_0_nomenclatura",
        "seccion": "A.8.0 — Nomenclatura del Capítulo A.8",
        "titulo": "Título A, A.8.0: glosario de símbolos del capítulo de elementos no estructurales (aceleración As/ai/ax, fuerza Fp, altura equivalente heq, coeficiente R0).",
        "texto": (
            "CAPÍTULO A.8 — EFECTOS SÍSMICOS SOBRE ELEMENTOS ESTRUCTURALES QUE NO "
            "HACEN PARTE DEL SISTEMA DE RESISTENCIA SÍSMICA\n\n"
            "A.8.0 — NOMENCLATURA\n\n"
            "As = aceleración máxima en la superficie del suelo estimada como la "
            "aceleración espectral correspondiente a un período de vibración igual "
            "a cero, Véase A.8.2.1.1.\n"
            "ai = aceleración en el nivel i, Véase A.8.2.1.1.\n"
            "ax = aceleración horizontal, expresada como un porcentaje de la "
            "aceleración de la gravedad, sobre el elemento estructural que no hace "
            "parte del sistema de resistencia sísmica, localizado en el piso x\n"
            "Fp = fuerza horizontal sobre un elemento estructural que no hace "
            "parte del sistema de resistencia sísmica, aplicada en su centro de "
            "masa.\n"
            "g = aceleración debida a la gravedad (g = 9.8 m/s²).\n"
            "hi = altura en metros, medida desde la base, del nivel i, véase "
            "A.8.2.1.1.\n"
            "hn = altura en metros, medida desde la base, del piso más alto de la "
            "edificación, véase A.8.2.1.1.\n"
            "heq = altura equivalente del sistema de un grado de libertad que "
            "simula la edificación, véase A.8.2.1.1.\n"
            "Mp = masa de un elemento estructural que no hace parte del sistema de "
            "resistencia sísmica.\n"
            "R0 = coeficiente de capacidad de disipación de energía básico "
            "definido para cada sistema estructural y cada grado de capacidad de "
            "disipación de energía del material estructural. Véase el Capítulo "
            "A.3.\n"
            "Sa = valor del espectro de aceleraciones de diseño para un período de "
            "vibración dado. Máxima aceleración horizontal de diseño, expresada "
            "como una fracción de la aceleración de la gravedad, para un sistema "
            "de un grado de libertad con un período de vibración T. Está definido "
            "en A.2.6."
        ),
    },
    {
        "id": "NSR10-A-A_8_1_general",
        "seccion": "A.8.1 — General",
        "titulo": "Título A, A.8.1: alcance del capítulo (escaleras, tanques, cubiertas, columnetas, apoyos de equipos, etc.) — A.8.1.1 alcance (a-g), A.8.1.2 responsabilidad del diseñador estructural, A.8.1.3 criterio de diseño (a-b, deformaciones impuestas).",
        "texto": (
            "A.8.1 — GENERAL\n\n"
            "A.8.1.1 — ALCANCE — El presente Capítulo cubre las previsiones "
            "sísmicas que deben tenerse en el diseño de los elementos "
            "estructurales que no hacen parte del sistema de resistencia sísmica, "
            "tal como se define en el Capítulo A.3, y de sus anclajes a él. Dentro "
            "de estos elementos se incluyen, pero no están limitados a:\n\n"
            "(a) Escaleras, rampas, etc.,\n"
            "(b) Tanques, piscinas, etc.,\n"
            "(c) Elementos de cubiertas, tales como cerchas, correas, etc.,\n"
            "(d) Elementos secundarios de los sistemas de entrepiso, tales como "
            "viguetas, etc.,\n"
            "(e) Columnas, columnetas, machones, y otros elementos que dan soporte "
            "a cubiertas y otras partes menores de la edificación,\n"
            "(f) Apoyos de equipos tales como ascensores, escaleras mecánicas, "
            "etc., y\n"
            "(g) En general todos aquellos elementos estructurales que se incluyen "
            "dentro de los planos estructurales y que no hacen parte del sistema "
            "de resistencia sísmica.\n\n"
            "A.8.1.2 — RESPONSABILIDAD DEL DISEÑO — El diseño, ante las "
            "solicitaciones establecidas por el presente Reglamento en el Título A "
            "o en el Título B, de todo elemento estructural que figure dentro de "
            "los planos estructurales, es responsabilidad del diseñador "
            "estructural. Dentro de estos elementos se incluyen los elementos "
            "mencionados en A.8.1.1.\n\n"
            "A.8.1.3 — CRITERIO DE DISEÑO — El diseño ante efectos sísmicos de los "
            "elementos estructurales que no hacen parte del sistema de resistencia "
            "sísmica, constituido por los elementos estructurales en sí, y de los "
            "anclajes, uniones o amarres de estos elementos al sistema de "
            "resistencia sísmica, debe realizarse para la situación que controle:\n\n"
            "(a) El efecto de las fuerzas sobre el elemento en sí,\n"
            "(b) La capacidad de resistir las deformaciones, que al elemento le "
            "impone el sistema de resistencia sísmica al responder a los "
            "movimientos sísmicos de diseño, y la influencia que pueda tener el "
            "elemento en la respuesta sísmica de la estructura, como puede ser el "
            "caso de las escaleras y rampas, las cuales pueden actuar como "
            "arriostramientos (o diagonales) de un piso con otro."
        ),
    },
    {
        "id": "NSR10-A-A_8_2_1_aceleracion_horizontal",
        "seccion": "A.8.2.1 — Aceleración horizontal sobre el elemento",
        "titulo": "Título A, A.8.2.1: A.8.2.1.1 método de la fuerza horizontal equivalente (ecuación A.8.2-1, heq≈0.75hn) y A.8.2.1.2 método del análisis dinámico para obtener la aceleración ai/ax sobre un elemento no estructural.",
        "texto": (
            "A.8.2 — FUERZAS HORIZONTALES DE DISEÑO\n\n"
            "A.8.2.1 — ACELERACIÓN HORIZONTAL SOBRE EL ELEMENTO — El elemento se "
            "ve sometido, ante la ocurrencia de los movimientos sísmicos de "
            "diseño, a las mismas aceleraciones horizontales que se ve sometido el "
            "sistema de resistencia sísmica en la misma altura sobre la base de la "
            "edificación en que se encuentre el elemento.\n\n"
            "Las fuerzas inerciales a que se ve sometido el elemento o cualquier "
            "porción de él, corresponden a la masa del elemento multiplicada por "
            "la aceleración que le imponen los movimientos causados por el sismo. "
            "Esta aceleración se determina por medio de uno de los procedimientos "
            "siguientes:\n\n"
            "A.8.2.1.1 — Método de la fuerza horizontal equivalente — Cuando se "
            "utilice el método de la fuerza horizontal equivalente, tal como lo "
            "prescribe el Capítulo A.4, la aceleración horizontal, ai, expresada "
            "como una fracción de la aceleración de la gravedad, sobre el "
            "elemento estructural que no hace parte del sistema de resistencia "
            "sísmica, localizado en el piso i, se obtiene por medio de la "
            "siguiente ecuación:\n\n"
            "ai = As + (Sa − As)·hi/heq   para hi ≤ heq\n"
            "ai = Sa · hi/heq   para hi ≥ heq   (A.8.2-1)\n\n"
            "heq puede estimarse simplificadamente como 0.75·hn\n\n"
            "Alternativamente a la ecuación A.8.2-1 para calcular las fuerzas que "
            "deben resistir los diafragmas de piso o de cubierta, pueden usarse "
            "estimaciones más precisas de las aceleraciones absolutas máximas a "
            "que estarían sometidos estos diafragmas, resultado por ejemplo, de "
            "análisis dinámicos.\n\n"
            "A.8.2.1.2 — Método del análisis dinámico — Cuando se utilice el "
            "método del análisis dinámico, la aceleración horizontal, ax, "
            "expresada como un porcentaje de la aceleración de la gravedad, sobre "
            "el elemento estructural que no hace parte del sistema de resistencia "
            "sísmica, localizado en el piso x, es igual a la aceleración a que se "
            "ve sometido el piso después de realizar el ajuste de resultados "
            "prescrito en A.5.4.5. El valor de la aceleración obtenida por medio "
            "del método del análisis dinámico no puede ser menor que el que se "
            "obtiene por medio de la ecuación A.8.2-1."
        ),
    },
    {
        "id": "NSR10-A-A_8_2_2_fuerzas_horizontales_sobre_elemento",
        "seccion": "A.8.2.2 — Fuerzas horizontales sobre el elemento",
        "titulo": "Título A, A.8.2.2: fuerza horizontal reducida de diseño Fp sobre un elemento no estructural (ecuación A.8.2-2, Fp=ax·g·Mp/R0), A.8.2.2.1 (elementos con características dinámicas propias) y A.8.2.2.2 (elementos con apoyos que se desplazan relativamente).",
        "texto": (
            "A.8.2.2 — FUERZAS HORIZONTALES SOBRE EL ELEMENTO — La fuerza sísmica "
            "horizontal reducida de diseño, que puede actuar en cualquier "
            "dirección, sobre el elemento estructural que no hace parte del "
            "sistema de resistencia sísmica en su centro de masa, se obtiene por "
            "medio de la siguiente ecuación:\n\n"
            "Fp = (ax·g/R0)·Mp   (A.8.2-2)\n\n"
            "donde R0 es el coeficiente de capacidad de disipación de energía "
            "correspondiente a los requisitos de diseño del elemento estructural, "
            "como se indica en A.8.4. La anterior ecuación puede aplicarse a "
            "elementos que tienen un solo apoyo, o cuando no hay desplazamientos "
            "relativos entre sus apoyos.\n\n"
            "A.8.2.2.1 — Cuando el elemento estructural que no hace parte del "
            "sistema de resistencia sísmica, tiene características dinámicas que "
            "amplifiquen su respuesta ante la aceleración ax, estas "
            "características deben tenerse en cuenta en la evaluación de las "
            "fuerzas horizontales que lo puedan afectar. Esto ocurre especialmente "
            "en apéndices de la edificación.\n\n"
            "A.8.2.2.2 — Cuando el elemento estructural que no hace parte del "
            "sistema de resistencia sísmica, tiene apoyos que pueden desplazarse "
            "relativamente durante el sismo, como es el caso de elementos que "
            "están conectados a dos pisos diferentes de la edificación, deben "
            "tenerse en cuenta en el diseño, además de las fuerzas calculadas por "
            "medio de la ecuación A.8.2-2, las fuerzas que inducen desplazamientos "
            "relativos entre sus apoyos."
        ),
    },
    {
        "id": "NSR10-A-A_8_2_3_a_A_8_4_1_cierre",
        "seccion": "A.8.2.3 a A.8.4.1",
        "titulo": "Título A, A.8.2.3 (fuerzas sobre las uniones al sistema de resistencia sísmica, remite a A.3.6.4), A.8.3 deformaciones de diseño (límites del Capítulo A.6) y A.8.4 requisitos de diseño por material.",
        "texto": (
            "A.8.2.3 — FUERZAS SOBRE LAS UNIONES AL SISTEMA DE RESISTENCIA "
            "SÍSMICA — Además de los requisitos de A.3.6.4, las uniones, empalmes "
            "y amarres, de los elementos estructurales que no hacen parte del "
            "sistema de resistencia sísmica, deben ser capaces de resistir la "
            "totalidad de las fuerzas sísmicas reducidas de diseño sobre el "
            "elemento tal como las define A.8.2.2.\n\n"
            "A.8.3 — DEFORMACIONES DE DISEÑO\n\n"
            "A.8.3.1 — Los elementos estructurales que no hacen parte del sistema "
            "de resistencia sísmica deben ser capaces de resistir, sin deterioro, "
            "las deformaciones que les impone la respuesta sísmica de la "
            "estructura. Como mínimo deben ser capaces de resistir las "
            "deformaciones que se obtienen de las derivas máximas de diseño "
            "determinadas como se indica en el Capítulo A.6.\n\n"
            "A.8.4 — REQUISITOS DE DISEÑO\n\n"
            "A.8.4.1 — Los requisitos que deben seguirse en el diseño de los "
            "elementos estructurales que no hacen parte del sistema de "
            "resistencia sísmica para cada uno de los materiales cubiertos por el "
            "Reglamento, deben ser los que se indiquen en cada uno de los Títulos "
            "correspondientes dentro del Reglamento, y en su defecto, los del "
            "nivel de capacidad de disipación de energía menor de los dados para "
            "cada material."
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
    print(f"Codificando {len(textos)} chunks-padre de A.8...")
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

    print(f"Subiendo {len(rows)} chunks-padre de A.8 a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_a_a8_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
