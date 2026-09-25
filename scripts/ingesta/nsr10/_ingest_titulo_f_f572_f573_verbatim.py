"""
Ingesta verbatim de NSR-10 Título F.5.7.2 completo (Criterios de Diseño
por Fatiga: criterio de falla fr^m N ≤ K2) y F.5.7.3 completo
(Procedimiento de Estimación de la Fatiga: 6 pasos, regla de Miner) --
Estructuras de Aluminio. Fase 11 del plan de cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-539 a F-543), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta -- IMPORTANTE: las tablas de clasificación de
fatiga F.5.7.2-1 (Tipo 1, detalles no soldados), F.5.7.3-1 (Tipo 2,
detalles soldados sobre la superficie) y F.5.7.3-2 (Tipo 3, detalles
soldados en conexiones extremas) son tablas de celdas combinadas
multinivel (localización del agrietamiento / requisitos dimensionales /
requisitos de fabricación / requisitos de inspección / área de
esfuerzos / parámetro especial, cruzados contra 7-11 sub-tipos cada
una) que describen criterios geométricos y de fabricación detallados
para cada sub-tipo de detalle. Transcribir esa estructura completa en
prosa arriesgaría perder fidelidad o introducir errores de
correspondencia celda-a-celda. Se transcriben verbatim las dos filas
finales de cada tabla (Tipo número y Clase máxima permitida), que son
el dato numérico realmente usado en el cálculo de fatiga (ecuación
F.5.7.2-1), y se documenta la estructura y el propósito de las filas
descriptivas sin inventar su contenido exacto -- quien necesite el
criterio geométrico completo de un sub-tipo debe consultar el PDF
original (páginas F-539, F-542, F-543). Mismo criterio de honestidad ya
aplicado a figuras/curvas gráficas en el resto de Título F.

Las Figuras F.5.7.2-1a (procedimiento de evaluación con la regla de
Miner) y F.5.7.2-1b (clasificación tipo 1, detalles no soldados) son
diagramas explicativos -- se documenta su contenido conceptual, no la
geometría del dibujo.

Uso: python _ingest_titulo_f_f572_f573_verbatim.py
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

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_5_7_2_1", "seccion": "F.5.7.2.1",
        "titulo": "F.5.7.2 — Criterios de Diseño por Fatiga. F.5.7.2.1 — Criterio de falla: fr^m·N≤K2 (ecuación F.5.7.2-1), K2 y m dependen de la clase de detalle",
        "texto": (
            "F.5.7.2 — CRITERIOS DE DISEÑO POR FATIGA — Se recomienda que, en lo posible, las estructuras de "
            "aluminio sean diseñadas sobre la base de brindar una vida segura. El método de evaluación dado en "
            "este numeral está diseñado para asegurar que la probabilidad de falla por fatiga durante la vida de "
            "la estructura sea comparable con la de otros modos de falla para estado límite último. "
            "Puede haber circunstancias en las que la severidad de la carga, el grado de redundancia y la "
            "facilidad de inspección y reparación sean tales que un acercamiento de seguridad en la falla o "
            "tolerancia de daño pueda justificarse en términos económicos. En este caso, los márgenes de "
            "seguridad pueden reducirse respecto a los requeridos para un diseño de vida segura. En F.5.3 se da "
            "una guía sobre esto. "
            "F.5.7.2.1 — Criterio de falla por fatiga — La base del diseño por fatiga usada aquí es que la vida "
            "requerida será alcanzada siempre que: fr^m N ≤ K2  (F.5.7.2-1). "
            "Donde: N = número de ciclos de un rango de esfuerzo fr necesarios para la falla. K2 = constante que "
            "depende de la clase de detalle y busca asegurar una alta probabilidad de supervivencia (véase "
            "F.5.7.8.1). fr = rango de esfuerzo principal del detalle, es constante para todos los ciclos. "
            "m = pendiente inversa de las curvas fr-N, es constante para la mayoría de las clases de detalle. "
            "En la mayoría de los propósitos estructurales prácticos, los detalles no experimentan historias de "
            "esfuerzo de amplitud constante. El tratamiento para carga general se da en F.5.7.3. "
            "El método para derivar el rango, o rangos, de esfuerzo apropiado fr se da en F.5.7.4 y F.5.7.6. En "
            "F.5.7.7 se dan las clasificaciones para los tipos de detalle más comúnmente usados. Los valores de "
            "K2 y m están dados en F.5.7.8. "
            "Si los datos de resistencia a la fatiga usados son los dados en F.5.7.8 y la carga cumple con "
            "F.5.7.4, entonces el valor del coeficiente general de carga γf debe ser tomado como uno."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_2_tabla1", "seccion": "F.5.7.2-1",
        "titulo": "Tabla F.5.7.2-1 — Clasificación de fatiga Tipo 1 (detalles NO soldados): 7 sub-tipos 1.1-1.7, clases máximas permitidas 60/60/50/35/29/29/17",
        "texto": (
            "Tabla F.5.7.2-1 — Clasificación tipo 1: detalles no soldados, en secciones laminadas o extruídas. "
            "Describe, para 7 sub-tipos, la localización de la iniciación potencial del agrietamiento (saliendo de "
            "cualquier soldadura, de cualquier conexión o parte estructural, en superficies maquinadas/pulidas, en "
            "agujeros taladrados o sacados, en conexiones traslapadas o empalmadas con pernos de fricción/remaches/"
            "pernos por aplastamiento), junto con requisitos dimensionales (ej. radio de apertura o esquina "
            "entrante ≥ t, diámetro de agujero ≤ 3t), requisitos de fabricación (acabado superficial, apriete de "
            "pernos) y requisitos de inspección (ensayo de colorante penetrante). El área de esfuerzos de diseño "
            "es el área neta de la sección transversal, con el coeficiente de concentración de esfuerzos aplicado "
            "en aperturas o esquinas entrantes cuando corresponda (véase la nota de fidelidad del script sobre la "
            "estructura completa de la tabla). "
            "Tipo número: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7. "
            "Clase máxima permitida (el valor real usado en la ecuación F.5.7.2-1, vía K2/m de F.5.7.8): "
            "1.1 → 60. 1.2 → 60. 1.3 → 50. 1.4 → 35. 1.5 → 29 (pernos que trabajan por fricción). "
            "1.6 → 29 (remaches). 1.7 → 17 (pernos que trabajan por aplastamiento)."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_2_figuras", "seccion": "F.5.7.2-1a_y_1b",
        "titulo": "Figuras F.5.7.2-1a (procedimiento de evaluación, regla de Miner) y F.5.7.2-1b (clasificación tipo 1, detalles no soldados): diagramas explicativos",
        "texto": (
            "Figura F.5.7.2-1a — Procedimiento de evaluación de la fatiga: diagrama de 6 paneles (a-f) mostrando "
            "el flujo conceptual completo: (a) secuencia de carga típica repetida n veces durante la vida de "
            "diseño (cargas PA y PB en el tiempo); (b) historia de esfuerzos resultante en el detalle X-X; "
            "(c) conteo de ciclos por el método de embalse (rainflow), identificando rangos fr1 a fr4; "
            "(d) espectro de esfuerzos ordenado descendente con ciclos n1 a n4; (e) ciclos para la falla N1 a N4 "
            "leídos de la línea fr-N del detalle X-X; (f) sumatoria de daño según la regla de Palmgren-Miner: "
            "Σ(n/N) = n1/N1 + n2/N2 + n3/N3 + n4/N4. Diagrama conceptual, no se transcribe la geometría gráfica, "
            "solo la secuencia lógica ya descrita en F.5.7.3. "
            "Figura F.5.7.2-1b — Clasificación tipo 1: detalles no soldados — ilustración isométrica de un "
            "elemento estructural señalando visualmente los sitios típicos de iniciación de grietas (localización "
            "típica de grieta, borde de corte, sujetador, dirección de la fluctuación del esfuerzo) sobre bordes "
            "cortados, agujeros y conexiones apernadas. Diagrama conceptual, no se transcribe la geometría "
            "gráfica."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_3", "seccion": "F.5.7.3",
        "titulo": "F.5.7.3 — Procedimiento de estimación de la fatiga: 6 pasos (a-f), vida estimada = vida de diseño mayorada / Σn/N (ecuación F.5.7.3-1)",
        "texto": (
            "F.5.7.3 — PROCEDIMIENTO DE ESTIMACION DE LA FATIGA — Un miembro estructural puede contener varios "
            "sitios potenciales de iniciación de grietas por fatiga. Las regiones de la estructura que tienen las "
            "más altas fluctuaciones de esfuerzos y/o las más severas concentraciones de esfuerzos deben "
            "normalmente ser revisadas primero. El procedimiento básico es el siguiente (véase la figura "
            "F.5.7.2-1a): "
            "(a) Se obtiene un estimativo del límite superior de la secuencia de carga de servicio para la vida "
            "de diseño de la estructura (véase F.5.7.4 y apéndice F.5.B). "
            "(b) Se estima la historia de esfuerzo resultante para el detalle (véase F.5.7.5). "
            "(c) Se reduce la historia de esfuerzo a un número equivalente de ciclos (n) de diferentes rangos de "
            "esfuerzo fr usando una técnica de conteo de ciclos (véase F.5.7.6.1). "
            "(d) Se ordenan los ciclos en orden descendente de amplitud, fr1, fr2, para formar un espectro de "
            "esfuerzo (véase F.5.7.6.2). "
            "(e) Se clasifica el detalle de acuerdo con las tablas F.5.7.2-1 a F.5.7.3-2 y F.5.7.7. Para la "
            "clasificación apropiada y el rango de esfuerzo de diseño (fr1, etc.), encontrar la resistencia a la "
            "fatiga permisible (N1, etc.) usando F.5.7.8.1. Cuando se haya decidido usar un valor de γmf "
            "diferente de la unidad, ésto debe ser tomado en cuenta para fijar los valores de los rangos de "
            "esfuerzo de diseño (véase F.5.3.6.2). "
            "(f) Sumar el daño total para todos los ciclos usando el gran total de Miner: "
            "vida estimada = (vida de diseño mayorada) / Σ(n/N)  (F.5.7.3-1). "
            "Si la Σ(n/N) excede la unidad entonces se deben reducir los rangos de esfuerzo en ese punto o se "
            "debe cambiar el detalle por uno de clase más alta (véase F.5.7.7)."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_3_tabla1", "seccion": "F.5.7.3-1",
        "titulo": "Tabla F.5.7.3-1 — Clasificación de fatiga Tipo 2 (detalles soldados sobre la superficie del miembro): 11 sub-tipos 2.1-2.11, clases máximas 50/42/35/29/24/20/17/20/24/29/17",
        "texto": (
            "Tabla F.5.7.3-1 — Clasificación tipo 2: detalles soldados sobre la superficie del miembro, en "
            "secciones laminadas o extruídas y miembros ensamblados. Describe, para 11 sub-tipos, la localización "
            "de la iniciación potencial del agrietamiento (en un accesorio largo o corto soldado, saliendo del "
            "extremo de la soldadura, en un bache intermedio de una soldadura longitudinal, en el extremo de la "
            "soldadura, en el agujero de una copa, en el borde de un miembro), requisitos dimensionales "
            "(soldadura a tope de penetración total vs. soldadura de filete, con criterios de longitud/ancho del "
            "accesorio y de intermitencia m/h), requisitos de fabricación (pulir socavaduras, cepillar el "
            "sobrellenado) y requisitos de inspección (colorante penetrante, radiografía). El área de esfuerzos "
            "de diseño es la sección transversal mínima del miembro en el punto de localización potencial del "
            "agrietamiento (véase la nota de fidelidad del script sobre la estructura completa de la tabla). "
            "Tipo número: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11. "
            "Clase máxima permitida: 2.1 → 50. 2.2 → 42. 2.3 → 35. 2.4 → 29. 2.5 → 24. 2.6 → 20. 2.7 → 17. "
            "2.8 → 20. 2.9 → 24. 2.10 → 29. 2.11 → 17."
        ),
    },
    {
        "id": "NSR10-F-F_5_7_3_tabla2", "seccion": "F.5.7.3-2",
        "titulo": "Tabla F.5.7.3-2 — Clasificación de fatiga Tipo 3 (detalles soldados en conexiones extremas de un miembro): 11 sub-tipos 3.1-3.11, clases máximas 42/35/29/24/17/24/20/24/20/24/14",
        "texto": (
            "Tabla F.5.7.3-2 — Clasificación tipo 3: detalles soldados en las conexiones extremas de un miembro, "
            "en planchas y extrusiones planas, y formas laminadas/formadas/extruídas. Describe, para 11 sub-tipos, "
            "la localización de la iniciación potencial del agrietamiento (en una unión soldada transversal, dos "
            "láminas o miembros unidos extremo a extremo con o sin tercer miembro en la unión, en la garganta de "
            "la soldadura, en cualquier unión parcialmente fundida), requisitos dimensionales (igual ancho/espesor "
            "o cambio con pendiente ≤1 en 4, soldadura a tope de penetración total/parcial o de filete), "
            "requisitos de fabricación (soldado en ambos lados o un solo lado, desalineamiento máximo ≤0.5t3, no "
            "puntear en los 10 mm a partir del borde) y requisitos de inspección (colorantes, radiografías, "
            "ultrasonido). El área de esfuerzos de diseño es la sección transversal mínima o el área de garganta "
            "efectiva, según el sub-tipo (véase la nota de fidelidad del script sobre la estructura completa de la "
            "tabla). "
            "Tipo número: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11. "
            "Clase máxima permitida: 3.1 → 42. 3.2 → 35. 3.3 → 29. 3.4 → 24. 3.5 → 17. 3.6 → 24. 3.7 → 20. "
            "3.8 → 24. 3.9 → 20. 3.10 → 24. 3.11 → 14."
        ),
    },
]


def main():
    import httpx
    from sentence_transformers import SentenceTransformer
    from supabase import ClientOptions, create_client

    http_client = httpx.Client(http2=False, timeout=120)
    sb = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
        options=ClientOptions(httpx_client=http_client),
    )
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


if __name__ == "__main__":
    main()
