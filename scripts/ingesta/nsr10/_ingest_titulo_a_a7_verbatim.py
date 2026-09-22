"""
Ingesta verbatim de Título A, Capítulo A.7 (Interacción suelo-estructura)
-- NSR-10. Fase 1 del plan de cierre del Título A (2026-09-22), auditoría
real de numerales confirmó A.7 en 0% de cobertura (17 numerales reales,
ninguno con chunk).

Fuente: NSR-10-124-128.pdf, páginas PDF 1-2 (A-81 a A-82), leídas
visualmente con Read pages= sobre el PDF nativo. A.8 (Efectos sísmicos
sobre elementos estructurales que no hacen parte del sistema de
resistencia sísmica) empieza en la página 3 del mismo PDF, cubierto en
_ingest_titulo_a_a8_verbatim.py.

Uso: python _ingest_titulo_a_a7_verbatim.py
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
        "id": "NSR10-A-A_7_1_1_definicion",
        "seccion": "A.7.1.1 — Definición",
        "titulo": "Título A, A.7.1.1: por qué incluir la interacción suelo-estructura en el análisis sísmico (rigidez de la cimentación y características dinámicas del suelo pueden variar la respuesta real frente a la estimada).",
        "texto": (
            "CAPÍTULO A.7 — INTERACCIÓN SUELO-ESTRUCTURA\n\n"
            "A.7.1 — GENERAL\n\n"
            "A.7.1.1 — DEFINICIÓN — La respuesta sísmica de la estructura está "
            "íntimamente ligada a la forma como los movimientos sísmicos del "
            "terreno afectan la estructura a través de su cimentación. Las "
            "características dinámicas del suelo subyacente, la rigidez y "
            "disposición de la cimentación y el tipo de sistema estructural de la "
            "edificación interactúan entre sí para caracterizar los efectos "
            "sísmicos sobre ella. El hecho de que no se tome en cuenta la rigidez "
            "de la cimentación y las características dinámicas del suelo "
            "subyacente en el análisis sísmico de la edificación puede conducir a "
            "variaciones apreciables entre la respuesta sísmica estimada y la "
            "respuesta real de la estructura. Por las razones anotadas es "
            "conveniente incluir los efectos de la interacción suelo-estructura en "
            "el análisis sísmico de la edificación."
        ),
    },
    {
        "id": "NSR10-A-A_7_1_2_efectos_asociados",
        "seccion": "A.7.1.2 — Efectos asociados con la interacción suelo-estructura",
        "titulo": "Título A, A.7.1.2: 6 aspectos (a-f) en que la interacción suelo-estructura cambia la respuesta real (suelos blandos, período, amortiguamiento, desplazamientos, distribución de cortantes) y A.7.1.2.1 (no confundir con efectos de sitio del Capítulo A.2).",
        "texto": (
            "A.7.1.2 — EFECTOS ASOCIADOS CON LA INTERACCIÓN SUELO-ESTRUCTURA — "
            "Dependiendo de las características de la estructura, de su cimentación "
            "y del suelo subyacente, la respuesta de la estructura ante "
            "solicitaciones estáticas verticales y dinámicas (sismo) puede variar "
            "con respecto al estimativo que se realiza sin tener en cuenta la "
            "interacción suelo-estructura, en los siguientes aspectos:\n\n"
            "(a) La presencia de suelos blandos y compresibles en las distribución "
            "de esfuerzos y deformaciones bajo losas de fundación, tanto ante "
            "solicitaciones de cargas verticales como de fuerzas horizontales,\n"
            "(b) Aumento en el periodo del sistema suelo-estructura que considera la "
            "flexibilidad del suelo, respecto a la evaluación de los períodos de "
            "vibración de la edificación considerando un modelo de base empotrada,\n"
            "(c) Generalmente aumento del amortiguamiento viscoso equivalente del "
            "sistema estructura-cimentación-suelo respecto al considerado para solo "
            "la estructura, al involucrar la disipación adicional de energía "
            "producto de los amortiguamientos material y geométrico del suelo,\n"
            "(d) Aumento de los desplazamientos laterales de la estructura ante "
            "solicitaciones sísmicas, debidos en parte significativa a la rotación "
            "de la base por efecto de cabeceo, con cambios en las derivas "
            "(desplazamientos horizontales relativos) en función de la altura a la "
            "que se encuentren los niveles en consideración,\n"
            "(e) Variación en la distribución de las fuerzas cortantes horizontales "
            "producidas por los movimientos sísmicos, entre los diferentes "
            "elementos del sistema de resistencia sísmica, especialmente cuando se "
            "combinan elementos con rigideces y sistemas de apoyo en la cimentación "
            "diferentes, como puede ser el caso de combinación de pórticos y muros "
            "estructurales,\n"
            "(f) y otros.\n\n"
            "A.7.1.2.1 — Los efectos de interacción suelo-estructura no deben "
            "confundirse con los efectos de sitio, causados por la amplificación de "
            "la onda sísmica al viajar desde la roca hasta la superficie, los "
            "cuales se describen en el Capítulo A.2."
        ),
    },
    {
        "id": "NSR10-A-A_7_1_3_procedimiento_recomendado",
        "seccion": "A.7.1.3 — Procedimiento recomendado",
        "titulo": "Título A, A.7.1.3: el capítulo define criterios generales, responsabilidad compartida ingeniero estructural + geotecnista, remite a A.3.4.2 y al Apéndice A-2 si hay información suficiente.",
        "texto": (
            "A.7.1.3 — PROCEDIMIENTO RECOMENDADO — El presente Capítulo define los "
            "criterios generales que deben ser tenidos en cuenta, tanto por el "
            "ingeniero estructural como por el ingeniero geotecnista, cuando se "
            "deban utilizar procedimientos de interacción suelo-estructura, de "
            "acuerdo con los requisitos de A.3.4.2. Si a juicio del ingeniero "
            "estructural y el ingeniero geotecnista se dispone de la información "
            "necesaria, obtenida con el mayor rigor posible, acerca de los "
            "parámetros geotécnicos y estructurales involucrados, se pueden "
            "utilizar los requisitos presentados en el Apéndice A-2 del presente "
            "Título del Reglamento."
        ),
    },
    {
        "id": "NSR10-A-A_7_2_informacion_geotecnica",
        "seccion": "A.7.2 — Información geotécnica",
        "titulo": "Título A, A.7.2: alcance mínimo del estudio geotécnico para interacción suelo-estructura — A.7.2.1 exploración, A.7.2.2 laboratorio, A.7.2.3 interpretación, A.7.2.4 revisión y evaluación de resultados.",
        "texto": (
            "A.7.2 — INFORMACIÓN GEOTÉCNICA\n\n"
            "A continuación se describe el alcance mínimo de la exploración, "
            "interpretación y recomendaciones que debe contener el estudio "
            "geotécnico, en un todo de acuerdo con lo señalado en el Título H del "
            "presente Reglamento:\n\n"
            "A.7.2.1 — EXPLORACIÓN — Los procedimientos de exploración deben ser "
            "consistentes con el tipo de propiedades que deban estudiarse, ya sea "
            "por procedimientos de campo o de laboratorio. Debe tenerse especial "
            "cuidado respecto a los niveles de deformación a que se expresen las "
            "propiedades del suelo, los cuales deben ser compatibles con los "
            "niveles de deformación que le imponen los movimientos sísmicos.\n\n"
            "A.7.2.2 — LABORATORIO — Los procedimientos de laboratorio deben "
            "cuantificar, directa o indirectamente, las características del "
            "material bajo condiciones dinámicas y a los niveles de deformación "
            "esperados durante los movimientos sísmicos.\n\n"
            "A.7.2.3 — INTERPRETACIÓN — La información de campo y de laboratorio "
            "debe combinarse en un conjunto de recomendaciones que describan y "
            "sustenten las características que debe emplear el ingeniero "
            "estructural en los modelos matemáticos del fenómeno. Las "
            "recomendaciones deben fijar limitaciones y rangos de aplicabilidad, "
            "fáciles de identificar, con el fin de evitar el peligro que entraña la "
            "utilización de los parámetros recomendados, fuera del contexto bajo el "
            "cual se expresaron.\n\n"
            "A.7.2.4 — REVISIÓN Y EVALUACIÓN DE LOS RESULTADOS — El ingeniero "
            "geotecnista debe revisar y avalar los resultados obtenidos por el "
            "ingeniero estructural, en lo concerniente a las recomendaciones para "
            "interacción suelo-estructura del estudio geotécnico y a la validez de "
            "los resultados de interacción suelo-estructura obtenidos con base en "
            "sus propias recomendaciones."
        ),
    },
    {
        "id": "NSR10-A-A_7_3_analisis_y_diseno_estructural",
        "seccion": "A.7.3 — Análisis y diseño estructural",
        "titulo": "Título A, A.7.3: aspectos que debe cubrir el ingeniero estructural — A.7.3.1 tipo de modelo, A.7.3.2 fuerzas de diseño, A.7.3.3 derivas (límites del Capítulo A.6), A.7.3.4 cortante sísmico en la base (piso mínimo CuTa del Capítulo A.4), A.7.3.5 valores máximos y mínimos.",
        "texto": (
            "A.7.3 — ANÁLISIS Y DISEÑO ESTRUCTURAL\n\n"
            "A continuación se describen el alcance mínimo de los aspectos que debe "
            "tener en cuenta el ingeniero estructural para describir los efectos de "
            "interacción suelo-estructura:\n\n"
            "A.7.3.1 — TIPO DE MODELO — Los modelos matemáticos pueden ser "
            "estáticos o dinámicos y deben describir las características de "
            "rigidez de la estructura, la cimentación y el suelo, a niveles "
            "compatibles con las deformaciones esperadas. En los modelos "
            "estructurales utilizados en el análisis de la estructura deben "
            "introducirse condiciones de apoyo elástico de los muros, columnas y "
            "elementos del sistema de resistencia sísmica al nivel de la "
            "cimentación, consistentes con las rigideces supuestas para obtener la "
            "respuesta de la estructura teniendo en cuenta los efectos de "
            "interacción suelo-estructura.\n\n"
            "A.7.3.2 — FUERZAS DE DISEÑO DE LOS ELEMENTOS ESTRUCTURALES — El "
            "modelo matemático empleado debe utilizarse en la evaluación de las "
            "características propias de la respuesta de la estructura ante las "
            "diferentes solicitaciones. La distribución de las fuerzas internas de "
            "la estructura que se utilice en el diseño de la misma debe ser la que "
            "se obtiene a través del análisis que incluye los efectos de "
            "interacción suelo-estructura.\n\n"
            "A.7.3.3 — DERIVAS — Las derivas obtenidas al utilizar los "
            "procedimientos de interacción suelo-estructura deben cumplir con los "
            "límites establecidos en el Capítulo A.6. Como se indicó en A.7.1.2 "
            "(d) hay casos en que deben esperarse derivas mayores que las que se "
            "obtendrían al suponer la estructura empotrada en su base.\n\n"
            "A.7.3.4 — CORTANTE SÍSMICO EN LA BASE — En aquellos casos en los "
            "cuales se presente un aumento en el cortante sísmico en la base, el "
            "diseño debe realizarse para el cortante obtenido utilizando la "
            "interacción suelo-estructura. Cuando debido a un aumento en el "
            "periodo estructural equivalente y/o en el amortiguamiento efectivo se "
            "presente una disminución del cortante sísmico de diseño en la base, "
            "el valor del cortante sísmico de diseño en la base no puede ser menor "
            "que el que se obtendría utilizando el método de la fuerza horizontal "
            "equivalente del Capítulo A.4, empleando un período de vibración igual "
            "a CuTa según A.4.2.1 y los espectros del Capítulo A.2.\n\n"
            "A.7.3.5 — VALORES MÁXIMOS Y MÍNIMOS DE LOS EFECTOS DE INTERACCIÓN "
            "SUELO-ESTRUCTURA — Debido a la incertidumbre que presenta la "
            "determinación de los parámetros del suelo utilizados en el análisis "
            "de interacción suelo-estructura, deben considerarse los valores "
            "máximos y mínimos esperados de tales parámetros y utilizarse aquellos "
            "que produzcan los efectos más desfavorables, tanto en la "
            "determinación de los cortantes sísmicos, como para el cálculo de las "
            "derivas de piso y las fuerzas de diseño de los elementos de la "
            "estructura y la cimentación."
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
    print(f"Codificando {len(textos)} chunks-padre de A.7...")
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

    print(f"Subiendo {len(rows)} chunks-padre de A.7 a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_a_a7_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
