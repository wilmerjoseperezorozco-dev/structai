"""
Ingesta verbatim de Título A, Capítulo A.4 (Método de la fuerza horizontal
equivalente) -- NSR-10. Fase 1 del plan de cierre del Título A (2026-09-22),
auditoría real de numerales confirmó A.4 en 0% de cobertura (11 numerales
reales, ninguno con chunk).

Fuente: NSR-10-106-115.pdf, páginas PDF 1-4 (A-63 a A-66), leídas
visualmente con Read pages= sobre el PDF nativo (nunca texto plano --
extracción mecánica con pypdf da caracteres de reemplazo en tildes en
estas páginas, mismo problema ya documentado para otros PDFs de NSR-10).
A.5 (Método del análisis dinámico) empieza en la página 5 del mismo PDF,
fuera de alcance de este capítulo.

Uso: python _ingest_titulo_a_a4_verbatim.py
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
        "id": "NSR10-A-A_4_0_nomenclatura",
        "seccion": "A.4.0 — Nomenclatura del Capítulo A.4",
        "titulo": "Título A, A.4.0: glosario de símbolos del método de la fuerza horizontal equivalente (área en la base, coeficientes Ct/Cu/Cvx, período fundamental T, masa M, cortante Vs).",
        "texto": (
            "CAPÍTULO A.4 — MÉTODO DE LA FUERZA HORIZONTAL EQUIVALENTE\n\n"
            "A.4.0 — NOMENCLATURA\n\n"
            "AB = área de la edificación en su base, en m².\n"
            "Awi = área mínima de cortante de la sección de un muro estructural i, "
            "medida en un plano horizontal, en el primer nivel de la estructura y en "
            "la dirección en estudio, en m². Véase A.4.2.\n"
            "Av = coeficiente de aceleración que representa la velocidad horizontal "
            "pico efectiva, para diseño, dado en A.2.2.\n"
            "Ct = coeficiente utilizado para calcular el período de la estructura, "
            "definido en A.4.2.2.\n"
            "Cu = coeficiente utilizado para calcular el período máximo permisible la "
            "estructura, definido en A.4.2.1.\n"
            "Cvx = coeficiente definido en A.4.3.\n"
            "ℓwi = longitud medida horizontalmente, en metros, de un muro estructural i "
            "en el primer nivel de la estructura y en la dirección en estudio. "
            "Véase A.4.2.\n"
            "Fi, Fx = fuerzas sísmicas horizontales en los niveles i o x respectivamente. "
            "Véase A.4.3.\n"
            "Fv = coeficiente de amplificación que afecta la aceleración en la zona de "
            "períodos intermedios, debida a los efectos de sitio, adimensional.\n"
            "fi = fuerza sísmica horizontal en el nivel i para ser utilizada en la "
            "ecuación A.4.2-1.\n"
            "g = aceleración debida a la gravedad (9.8 m/s²).\n"
            "hi, hx = altura en metros, medida desde la base, del nivel i o x. "
            "Véase A.4.3.2.\n"
            "hn = altura en metros, medida desde la base, del piso más alto del "
            "edificio. Véase A.4.2.2.\n"
            "hp = altura del piso medida desde la superficie del diafragma del piso "
            "hasta la superficie del diafragma del piso inmediatamente inferior.\n"
            "hwi = altura del muro i medida desde la base, en m.\n"
            "I = coeficiente de importancia dado en A.2.5.2.\n"
            "k = exponente relacionado con el período fundamental, T, de la "
            "edificación dado en A.4.3.2.\n"
            "M = masa total de la edificación — M debe ser igual a la masa total de "
            "la estructura más la masa de aquellos elementos tales como muros "
            "divisorios y particiones, equipos permanentes, tanques y sus "
            "contenidos, etc. En depósitos o bodegas debe incluirse además un 25 "
            "por ciento de la masa correspondiente a los elementos que causan la "
            "carga viva del piso. Capítulos A.4 y A.5 (en kg).\n"
            "mi, mx = parte de M que está colocada en el nivel i o x respectivamente.\n"
            "N = número de pisos de la edificación.\n"
            "nw = número de muros de la edificación efectivos para resistir las "
            "fuerzas sísmicas horizontales en la dirección bajo estudio.\n"
            "Sa = valor del espectro de aceleraciones de diseño para un período de "
            "vibración dado. Máxima aceleración horizontal de diseño, expresada "
            "como una fracción de la aceleración de la gravedad, para un sistema "
            "de un grado de libertad con un período de vibración T. Está definido "
            "en A.2.6.\n"
            "T = período fundamental del edificio como se determina en A.4.2.\n"
            "Ta = período de vibración fundamental aproximado. Véase A.4.2.\n"
            "Vs = cortante sísmico en la base, para las fuerzas sísmicas. Véase A.4.3.\n"
            "α = exponente para ser utilizado en el cálculo del período aproximado "
            "Ta. Véase A.4.2.2.\n"
            "δi = desplazamiento horizontal del nivel i con respecto a la base de la "
            "estructura, debido a las fuerzas horizontales fi, para ser utilizado "
            "en la ecuación A.4.2-1."
        ),
    },
    {
        "id": "NSR10-A-A_4_1_general",
        "seccion": "A.4.1 — General",
        "titulo": "Título A, A.4.1: alcance del Capítulo A.4 (método de la fuerza horizontal equivalente), remite al Capítulo A.3 para saber cuándo aplica.",
        "texto": (
            "A.4.1 — GENERAL\n\n"
            "A.4.1.1 — Los requisitos de este Capítulo controlan la obtención de las "
            "fuerzas sísmicas horizontales de la edificación y el análisis sísmico de "
            "la misma, de acuerdo con los requisitos dados en el Capítulo A.3 para la "
            "utilización del método de la fuerza horizontal equivalente."
        ),
    },
    {
        "id": "NSR10-A-A_4_2_periodo_fundamental",
        "seccion": "A.4.2 — Período fundamental de la edificación",
        "titulo": "Título A, A.4.2: cálculo del período fundamental T (ecuación A.4.2-1, modelo dinámico), límite CuTa (ecuación A.4.2-2), período aproximado Ta (ecuación A.4.2-3, Tabla A.4.2-1 de Ct y α, ecuación A.4.2-4 de Cw, ecuación A.4.2-5 simplificada), y regla de reanálisis si difiere más del 10%.",
        "texto": (
            "A.4.2 — PERÍODO FUNDAMENTAL DE LA EDIFICACIÓN\n\n"
            "A.4.2.1 — El valor del período fundamental de la edificación, T, debe "
            "obtenerse a partir de las propiedades de su sistema de resistencia "
            "sísmica, en la dirección bajo consideración, de acuerdo con los "
            "principios de la dinámica estructural, utilizando un modelo matemático "
            "linealmente elástico de la estructura. Este requisito puede suplirse por "
            "medio del uso de la siguiente ecuación:\n\n"
            "T = 2π · √[ Σ(i=1 a n) (mi·δi²) / Σ(i=1 a n) (fi·δi) ]   (A.4.2-1)\n\n"
            "Los valores de fi representan unas fuerzas horizontales distribuidas "
            "aproximadamente de acuerdo con las ecuaciones A.4.3-2 y A.4.3-3, o "
            "utilizando cualquier otra distribución racional que se aproxime a la "
            "del modo fundamental de la estructura en la dirección en estudio. Las "
            "deflexiones horizontales, δi, deben calcularse utilizando las fuerzas "
            "horizontales fi.\n\n"
            "El valor de T no puede exceder Cu·Ta, donde Cu se calcula por medio de "
            "la ecuación A.4.2-2 y Ta se calcula de acuerdo con A.4.2-3.\n\n"
            "Cu = 1.75 − 1.2·Av·Fv   (A.4.2-2)\n\n"
            "pero Cu no debe ser menor de 1.2.\n\n"
            "A.4.2.2 — Alternativamente el valor de T puede ser igual al período "
            "fundamental aproximado, Ta, que se obtenga por medio de la ecuación "
            "A.4.2-3.\n\n"
            "Ta = Ct·h^α   (A.4.2-3)\n\n"
            "donde Ct y α tienen los valores dados en la tabla A.4.2-1.\n\n"
            "Tabla A.4.2-1 — Valor de los parámetros Ct y α para el cálculo del "
            "período aproximado Ta\n\n"
            "Sistema estructural de resistencia sísmica | Ct | α\n"
            "Pórticos resistentes a momentos de concreto reforzado que resisten la "
            "totalidad de las fuerzas sísmicas y que no están limitados o adheridos "
            "a componentes más rígidos, estructurales o no estructurales, que "
            "limiten los desplazamientos horizontales al verse sometidos a las "
            "fuerzas sísmicas | 0.047 | 0.9\n"
            "Pórticos resistentes a momentos de acero estructural que resisten la "
            "totalidad de las fuerzas sísmicas y que no están limitados o adheridos "
            "a componentes más rígidos, estructurales o no estructurales, que "
            "limiten los desplazamientos horizontales al verse sometidos a las "
            "fuerzas sísmicas | 0.072 | 0.8\n"
            "Pórticos arriostrados de acero estructural con diagonales excéntricas "
            "restringidas a pandeo | 0.073 | 0.75\n"
            "Todos los otros sistemas estructurales basados en muros de rigidez "
            "similar o mayor a la de muros de concreto o mampostería | 0.049 | 0.75\n"
            "Alternativamente, para estructuras que tengan muros estructurales de "
            "concreto reforzado o mampostería estructural, pueden emplearse los "
            "siguientes parámetros Ct y α, donde Cw se calcula utilizando la "
            "ecuación A.4.2-4 | 0.0062/√Cw | 1.00\n\n"
            "Cw = (100/AB) · Σ(i=1 a nw) [ (hn/hwi)² · Awi / (1 + 0.83·(hwi/ℓwi)²) ]   "
            "(A.4.2-4)\n\n"
            "Alternativamente, para edificaciones de 12 pisos o menos con alturas de "
            "piso, hp, no mayores de 3 m cuyo sistema estructural de resistencia "
            "sísmica está compuesto por pórticos resistentes a momentos de concreto "
            "reforzado o acero estructural, el período de vibración aproximado, Ta, "
            "en s, puede determinarse por medio de la ecuación A.4.2-5.\n\n"
            "Ta = 0.1·N   (A.4.2-5)\n\n"
            "A.4.2.3 — El valor de T obtenido al utilizar las ecuaciones A.4.2-1, "
            "A.4.2-3 o A.4.2-5 es un estimativo inicial razonable del período "
            "estructural para predecir las fuerzas a aplicar sobre la estructura con "
            "el fin de dimensionar su sistema de resistencia sísmica. Sin embargo, "
            "una vez dimensionada la estructura, debe calcularse el valor ajustado "
            "de T mediante la aplicación de análisis modal o de la ecuación "
            "A.4.2-1 para compararlo con el estimado inicial; si el periodo de la "
            "estructura diseñada difiriera en más del 10% con el periodo estimado "
            "inicialmente, debe repetirse el proceso de análisis, utilizando el "
            "último periodo calculado como nuevo estimado, hasta que se converja en "
            "un resultado dentro de la tolerancia del 10% señalada."
        ),
    },
    {
        "id": "NSR10-A-A_4_3_fuerzas_sismicas_horizontales",
        "seccion": "A.4.3 — Fuerzas sísmicas horizontales equivalentes",
        "titulo": "Título A, A.4.3: cortante sísmico en la base Vs (ecuación A.4.3-1), distribución de la fuerza sísmica horizontal Fx por nivel (ecuaciones A.4.3-2/A.4.3-3, exponente k según T).",
        "texto": (
            "A.4.3 — FUERZAS SÍSMICAS HORIZONTALES EQUIVALENTES\n\n"
            "A.4.3.1 — El cortante sísmico en la base, Vs, equivalente a la totalidad "
            "de los efectos inerciales horizontales producidos por los movimientos "
            "sísmicos de diseño, en la dirección en estudio, se obtiene por medio de "
            "la siguiente ecuación:\n\n"
            "Vs = Sa · g · M   (A.4.3-1)\n\n"
            "El valor de Sa en la ecuación anterior corresponde al valor de la "
            "aceleración, como fracción de la de la gravedad, leída en el espectro "
            "definido en A.2.6 para el período T de la edificación.\n\n"
            "A.4.3.2 — La fuerza sísmica horizontal, Fx, en cualquier nivel x, para "
            "la dirección en estudio, debe determinarse usando la siguiente "
            "ecuación:\n\n"
            "Fx = Cvx · Vs   (A.4.3-2)\n\n"
            "y\n\n"
            "Cvx = (mx · hx^k) / [ Σ(i=1 a n) (mi · hi^k) ]   (A.4.3-3)\n\n"
            "donde k es un exponente relacionado con el período fundamental, T, de "
            "la edificación de la siguiente manera:\n\n"
            "(a) Para T menor o igual a 0.5 segundos, k = 1.0,\n"
            "(b) Para T entre 0.5 y 2.5 segundos, k = 0.75 + 0.5T, y\n"
            "(c) Para T mayor que 2.5 segundos, k = 2.0."
        ),
    },
    {
        "id": "NSR10-A-A_4_4_analisis_de_la_estructura",
        "seccion": "A.4.4 — Análisis de la estructura",
        "titulo": "Título A, A.4.4: requisitos del análisis con modelo matemático linealmente elástico (condiciones de apoyo, diafragma, momentos de vuelco, torsión, dirección de aplicación) y resultados mínimos exigidos (desplazamientos, cortante de piso, fuerzas en cimentación, fuerzas internas por elemento).",
        "texto": (
            "A.4.4 — ANÁLISIS DE LA ESTRUCTURA\n\n"
            "A.4.4.1 — El efecto de las fuerzas sísmicas, obtenidas de acuerdo con "
            "los requisitos de A.4.3, correspondientes a cada nivel, debe evaluarse "
            "por medio de un análisis realizado utilizando un modelo matemático "
            "linealmente elástico de la estructura, que represente adecuadamente "
            "las características del sistema estructural. El análisis, realizado de "
            "acuerdo con los principios de la mecánica estructural, debe tenerse en "
            "cuenta, como mínimo:\n\n"
            "(a) Las condiciones de apoyo de la estructura, especialmente cuando se "
            "combinen elementos verticales de resistencia sísmica con diferencias "
            "apreciables en su rigidez,\n"
            "(b) El efecto de diafragma, rígido o flexible, de los entrepisos de la "
            "edificación, en la distribución del cortante sísmico del piso a los "
            "elementos verticales del sistema estructural de resistencia sísmica,\n"
            "(c) Las variaciones en las fuerzas axiales de los elementos verticales "
            "del sistema de resistencia sísmica causadas por los momentos de vuelco "
            "que inducen las fuerzas sísmicas,\n"
            "(d) Los efectos torsionales prescritos en A.3.6.7,\n"
            "(e) Los efectos de la dirección de aplicación de la fuerza sísmica "
            "prescritos en A.3.6.3,\n"
            "(f) En estructuras de concreto reforzado y mampostería estructural, a "
            "juicio del ingeniero diseñador, consideraciones acerca del grado de "
            "fisuración de los elementos, compatibles con las fuerzas sísmicas y el "
            "grado de capacidad de disipación de energía prescrito para el material "
            "estructural, y\n"
            "(g) Deben consultarse lo requisitos de A.3.4.3.\n\n"
            "A.4.4.2 — Como resultados del análisis se deben obtener, como mínimo:\n\n"
            "(a) Los desplazamientos horizontales de la estructura, incluyendo los "
            "efectos torsionales, que se emplean para evaluar si las derivas de la "
            "estructura cumplen los requisitos dados en el Capítulo A.6,\n"
            "(b) La distribución del cortante de piso, incluyendo los efectos "
            "torsionales, a todos los elementos verticales del sistema de "
            "resistencia sísmica,\n"
            "(c) Los efectos de las fuerzas sísmicas en la cimentación de la "
            "edificación, y\n"
            "(d) Las fuerzas internas (momentos flectores, fuerzas cortantes, "
            "fuerzas axiales y momentos de torsión) correspondientes a cada "
            "elemento que haga parte del sistema de resistencia sísmica."
        ),
    },
    {
        "id": "NSR10-A-A_4_5_sistema_internacional_medidas",
        "seccion": "A.4.5 — Uso del Sistema Internacional de Medidas (SI) en el cálculo de las fuerzas sísmicas de acuerdo con este Capítulo",
        "titulo": "Título A, A.4.5: nota explicativa sobre unidades SI (kg, N, kN, Mg) al aplicar la ecuación A.4.3-1 y equivalencia con el antiguo sistema mks (kgf, ton).",
        "texto": (
            "A.4.5 — USO DEL SISTEMA INTERNACIONAL DE MEDIDAS (SI) EN EL CÁLCULO DE "
            "LAS FUERZAS SÍSMICAS DE ACUERDO CON ESTE CAPÍTULO\n\n"
            "En el Sistema Internacional de Medidas (SI) el kg (kilogramo) es una "
            "unidad de masa, por lo tanto la masa de la estructura se debe expresar "
            "en kg. Aplicando la 2ª Ley de Newton que dice que la fuerza inercial es "
            "igual a la masa del cuerpo multiplicada por su aceleración; si la masa "
            "está sometida a una aceleración en m/s², se obtiene una fuerza cuyas "
            "unidades son (kg·m/s²). Por definición, en el sistema SI la unidad de "
            "fuerza es un newton (N) y corresponde a la fuerza inercial de una masa "
            "de 1 kg sometida a una aceleración de 1 m/s² (1 N = 1 kg · 1 m/s²). "
            "Entonces, si la masa se expresa en kg y las aceleraciones en m/s², se "
            "obtiene fuerzas inerciales en newtons.\n\n"
            "La ecuación A.4.3-1 es una aplicación de la 2ª Ley de Newton y se "
            "emplea para determinar las fuerzas inerciales horizontales que "
            "producen los movimientos del terreno causados por el sismo de diseño. "
            "El valor de la aceleración horizontal máxima que tiene el terreno "
            "donde se apoya la estructura, se lee del espectro de aceleraciones, "
            "Sa, definido en el Capítulo A.2 para el período fundamental de "
            "vibración de la estructura T. El espectro Sa es adimensional, y "
            "corresponde a la aceleración horizontal que impone el sismo en la base "
            "de la estructura, expresada como una fracción de la aceleración de la "
            "gravedad, por lo tanto para obtener la aceleración en m/s², debe "
            "multiplicarse por la aceleración de la gravedad, g (g = 9.8 m/s²). Al "
            "utilizar la ecuación A.4.3-1, si la masa total de la edificación, M, "
            "se expresa en kg, entonces la totalidad de las fuerzas inerciales "
            "horizontales que actúan sobre la estructura cuando ésta se ve sometida "
            "al sismo de diseño, Vs, se obtiene en newtons así:\n\n"
            "Vs = Sa·g·M (m/s²)·(kg) = Sa·g·M (kg·m/s²) = Sa·g·M (N)\n\n"
            "Pero en el diseño práctico de edificaciones, tanto el kg como el N, son "
            "unidades muy pequeñas; por esta razón es conveniente expresar la masa "
            "en Mg (Megagramos, 1 Mg = 1 000 kg = 10⁶ g). En este caso la "
            "aplicación de la ecuación A.4.3-1 conduce a una fuerza, Vs, en kN "
            "(kilonewtons):\n\n"
            "Vs = Sa·g·M (m/s²)·(Mg) = Sa·g·M (Mg·m/s²) = Sa·g·M (1000·kg·m/s²) = "
            "Sa·g·M (1000·N) = Sa·g·M (kN)\n\n"
            "A modo de referencia, en el antiguo sistema mks (m-kgf-s, "
            "metro-kilogramo fuerza-segundo) 1 kgf = 9.8 N ≅ 10 N, y análogamente "
            "1 000 kgf = 1 ton = 9 806.65 N ≅ 10 000 N = 10 kN. Entonces un kN es "
            "aproximadamente un décimo de tonelada."
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
    print(f"Codificando {len(textos)} chunks-padre de A.4...")
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

    print(f"Subiendo {len(rows)} chunks-padre de A.4 a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_a_a4_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
