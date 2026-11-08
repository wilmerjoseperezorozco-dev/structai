"""
Ingesta verbatim del Apéndice A-1 del Título A de NSR-10 (Recomendaciones
sísmicas para algunas estructuras que se salen del alcance del Reglamento),
páginas A-139 y A-140. Fase 4 del plan de cierre del Título A (2026-11-08).

Fuente: NSR-10-183-190.pdf, páginas PDF 1 y 2, leídas visualmente con Read
pages= sobre el PDF nativo. Los subíndices se transcriben en línea (R0).

Uso: se sube vía _resplit_titulo_a_apendice_a1_por_limite_tokens.py
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"
PREFIJO = "NSR10-A-APA1"
CAB = "NSR-10 — Apéndice A-1 — Recomendaciones sísmicas para algunas estructuras que se salen del alcance del Reglamento\n\n"

CHUNKS = [
    {
        "id": f"{PREFIJO}_A_1_0_nomenclatura",
        "seccion": "A-1.0 — Nomenclatura",
        "titulo": "Apéndice A-1, A-1.0: nomenclatura (g, I, M, R0, R, T, W) para estructuras especiales como tanques, silos y chimeneas.",
        "texto": CAB + (
            "APÉNDICE A-1 — RECOMENDACIONES SÍSMICAS PARA ALGUNAS ESTRUCTURAS QUE SE SALEN DEL ALCANCE DEL REGLAMENTO\n\n"
            "A-1.0 — NOMENCLATURA\n\n"
            "g = aceleración debida a la gravedad (g = 9.8 m/s²).\n"
            "I = coeficiente de importancia dado en A.2.5.2.\n"
            "M = masa total de la edificación; M debe ser igual a la masa total de la estructura más su contenido. En estructuras tales como tanques, silos y otras estructuras de almacenamiento debe incluir la masa correspondiente al contenido operacional normal de la estructura.\n"
            "R0 = coeficiente de capacidad de disipación de energía básico definido para cada sistema estructural y cada grado de capacidad de disipación de energía del material estructural. Véase el Capítulo A.3.\n"
            "R = coeficiente de capacidad de disipación de energía para ser empleado en el diseño, corresponde al coeficiente de disipación de energía básico, R0, multiplicado por los coeficientes de reducción de capacidad de disipación de energía por irregularidades en altura, en planta, y por ausencia de redundancia en el sistema estructural de resistencia sísmica (R = φa φp φr R0). Véase el Capítulo A.3.\n"
            "T = período fundamental de la estructura.\n"
            "W = peso total de la edificación; W = Mg."
        ),
    },
    {
        "id": f"{PREFIJO}_A_1_1_general_periodo",
        "seccion": "A-1.1 y A-1.2 — General y período fundamental",
        "titulo": "Apéndice A-1, A-1.1 y A-1.2: propósito (norma AIS-180 de 2010), alcance fuera de la Ley 400, requisitos aplicables y período fundamental (ecuación A.4.2-1).",
        "texto": CAB + (
            "A-1.1 — GENERAL\n\n"
            "A-1.1.1 — PROPÓSITO — En el presente Apéndice se dan recomendaciones que permiten determinar las fuerzas sísmicas de diseño de algunas estructuras especiales no cubiertas por el alcance de las Normas Sismo Resistentes Colombianas y su Reglamento. Complementariamente, se puede consultar el documento \"Norma AIS-180 — Requisitos de diseño sismo resistente para algunas estructuras diferentes a edificaciones\", 2010, de la Asociación Colombiana de Ingeniería Sísmica – AIS, el que corresponde a la traducción y adaptación del Capítulo 14 del documento NEHRP 2003 y el cual analiza en detalle el comportamiento de tanques, recipientes y silos principalmente. El presente Apéndice y el documento de AIS señalado, contienen recomendaciones de diseño que no tienen carácter obligatorio, y se incluyen únicamente por razones ilustrativas.\n\n"
            "A-1.1.2 — ALCANCE — Los requisitos del presente Apéndice pueden emplearse en el diseño sismo resistente de construcciones que se salen del alcance de la Ley 400 de 1997 y sus reglamentos. Se dan los parámetros de diseño sismo resistente de una forma compatible con lo que se requiere para edificaciones en el presente Reglamento.\n\n"
            "A-1.1.3 — REQUISITOS APLICABLES — En general se recomienda seguir los requisitos del Reglamento con las excepciones anotadas en el presente Capítulo. Debe tenerse especial cuidado con las fuerzas de viento sobre estas estructuras especiales, pues en muchos casos son mayores que las fuerzas sísmicas.\n\n"
            "A-1.2 — PERIODO FUNDAMENTAL DE LA ESTRUCTURA\n\n"
            "A-1.2.1 — El valor del período fundamental de la estructura, T, debe obtenerse a partir de las propiedades de su sistema de resistencia sísmica, en la dirección bajo consideración, de acuerdo con los principios de la dinámica estructural, utilizando un modelo matemático linealmente elástico de la estructura. Este requisito puede suplirse por medio del uso de la ecuación A.4.2-1."
        ),
    },
    {
        "id": f"{PREFIJO}_A_1_3_fuerzas_sismicas",
        "seccion": "A-1.3 — Cálculo de las fuerzas sísmicas de diseño (A-1.3.1 a A-1.3.4)",
        "titulo": "Apéndice A-1, A-1.3: movimientos sísmicos de diseño, masa total con contenido operacional, coeficiente de importancia I = 1 salvo grupos II, III o IV y líneas vitales, distribución en altura.",
        "texto": CAB + (
            "A-1.3 — CALCULO DE LAS FUERZAS SÍSMICAS DE DISEÑO\n\n"
            "A-1.3.1 — MOVIMIENTOS SÍSMICOS DE DISEÑO — Debe utilizarse la definición de los movimientos sísmicos de diseño dada en el Capítulo A.2 del Reglamento.\n\n"
            "A-1.3.2 — MASA TOTAL, M — La masa total, M, debe incluir la masa correspondiente a todas las cargas muertas y las masas correspondientes al contenido operacional normal de la estructura, especialmente en tanques, silos y otras estructuras de almacenamiento.\n\n"
            "A-1.3.3 — COEFICIENTE DE IMPORTANCIA, I — Debe tomarse un coeficiente de importancia, I, igual a la unidad, a menos que la estructura sea parte o pueda afectar edificaciones de los grupos de usos II, III o IV. En el caso de estructuras que sean parte de sistemas de líneas vitales, la definición del coeficiente de importancia a emplear se debe basar en consideraciones que incluyan el nivel de redundancia del sistema y el potencial de que una eventual falla de la estructura pueda afectar la operación o estabilidad de edificaciones indispensables.\n\n"
            "A-1.3.4 — DISTRIBUCIÓN EN LA ALTURA DE LAS FUERZAS SÍSMICAS — La distribución en la altura de las fuerzas sísmicas horizontales puede realizarse por cualquiera de los procedimientos presentados en los Capítulos A.4 o A.5 del Reglamento."
        ),
    },
    {
        "id": f"{PREFIJO}_A_1_3_5_intro",
        "seccion": "A-1.3.5 — Coeficiente básico de disipación de energía R0",
        "titulo": "Apéndice A-1, A-1.3.5: se recomienda usar los valores de R0 de la Tabla A-1.3-1; A-1.4.1 deriva de estructuras especiales a criterio del diseñador.",
        "texto": CAB + (
            "A-1.3.5 — COEFICIENTE BÁSICO DE DISIPACIÓN DE ENERGÍA, R0 — Se recomienda utilizar los valores del coeficiente de capacidad de disipación de energía, R0, dados en la tabla A-1.3-1 del presente Apéndice.\n\n"
            "A-1.4 — REQUISITOS DE DERIVA\n\n"
            "A-1.4.1 — Los requisitos para la deriva presentados en el Capítulo A.6, no son aplicables directamente a estructuras especiales diferentes de las cubiertas por el Reglamento en su alcance. Los límites de la deriva deben ser establecidos por el diseñador tomando en cuenta el peligro que representa para la vida la falla de elementos estructurales y no estructurales, como consecuencia de los desplazamientos que sufre la estructura al verse afectada por los movimientos sísmicos de diseño"
        ),
    },
]

# Tabla A-1.3-1: una fila por chunk, para que la fila nunca se separe de su valor
# al re-trocear (un chunk único de tabla se partía y dejaba filas sin valor).
_FILAS_R0 = [
    ("tanques", "Tanques, contenedores de líquidos y gases a presión, apoyados sobre columnas arriostradas, con diagonales, o no", "2.0"),
    ("silos_concreto", "Silos y chimeneas de concreto reforzado vaciado en sitio, cuyas paredes son continuas hasta la fundación", "3.5"),
    ("torre_faldones", "Estructuras en forma de torre cuya masa está distribuida en la altura, tales como chimeneas, silos y tanques, cuyos apoyos consisten en faldones.", "3.0"),
    ("torres_celosia", "Torres en celosía, autoportantes o con templetes, chimeneas y torres con templetes.", "3.0"),
    ("pendulo_invertido", "Estructuras de tipo péndulo invertido", "2.0"),
    ("tolvas", "Tolvas sobre columnas, con o sin contravientos.", "3.0"),
    ("torres_enfriamiento", "Torres de enfriamiento", "3.5"),
    ("anaqueles", "Torres o anaqueles de almacenamiento", "3.0"),
    ("avisos", "Avisos y vallas publicitarias", "3.5"),
    ("monumentos", "Monumentos y estructuras de parques de diversión", "2.0"),
    ("otras", "Otras estructuras autoportantes, no incluidas anteriormente", "3.0"),
]
for _k, _tipo, _r0 in _FILAS_R0:
    CHUNKS.append({
        "id": f"{PREFIJO}_A_1_3_1_tabla_R0_{_k}",
        "seccion": f"Tabla A-1.3-1 — R0 para {_tipo[:60]}",
        "titulo": f"Apéndice A-1, Tabla A-1.3-1: valor de R0 = {_r0} para {_tipo}",
        "texto": "NSR-10 — Apéndice A-1 — Tabla A-1.3-1\n\n" + (
            "Tabla A-1.3-1 — Coeficiente de capacidad de disipación de energía, R0, para algunas estructuras especiales (Apéndice A-1, A-1.3.5)\n\n"
            f"Tipo de estructura: {_tipo}\n"
            f"Valor de R0: {_r0}"
        ),
    })
