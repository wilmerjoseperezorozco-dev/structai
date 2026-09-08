"""
Ingesta verbatim de Título A, Capítulo A.3.3 (Configuración Estructural
de la Edificación -- irregularidades en planta y en altura, ausencia de
redundancia, coeficiente de sobrerresistencia) + Tablas A.3-5, A.3-6 y
A.3-7 -- NSR-10.

**Corrige un hallazgo real**: la memoria privada del proyecto describía
"A.3.6" como el capítulo de irregularidades -- eso era INCORRECTO
(A.3.6 real es "Efectos sísmicos en los elementos estructurales", sin
relación con irregularidades). El contenido real de irregularidades
en planta/altura está en A.3.3.4/A.3.3.5, con las Tablas A.3-6/A.3-7
que las definen numéricamente -- confirmado leyendo el PDF real, no
la memoria vieja (que coincide con el patrón ya documentado de
`capitulo_a.txt`, un JSON local con nombres de capítulo fabricados).

**Reemplaza chunks viejos condensados/parafraseados**: NSR10-A3-A_3_3_r1
a r5 tenían el mismo patrón de "resumen disfrazado de completo" ya
encontrado en K.2/K.3/F.3 (paráfrasis con notación abreviada, no texto
oficial verbatim). También resuelve la nota de cobertura
`NSR10-A3-A_3_nota_de_cobertura-05` que documentaba honestamente que
las Tablas A.3-5/6/7 nunca se habían logrado extraer -- ahora sí.

Fuente: NSR-10-81-94.pdf, páginas PDF 5-7 (A-42 a A-44, A.3.3.1 a
A.3.3.9) + NSR-10-95-105.pdf, páginas PDF 7-9 (A-58 a A-60, Tablas
A.3-5/6/7), leídas visualmente con Read pages= sobre el PDF nativo.

Uso: python _ingest_titulo_a_a33_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "A"

# IDs viejos (paráfrasis/pendientes) a borrar antes de subir los nuevos verbatim
IDS_A_BORRAR = [
    "NSR10-A3-A_3_3_r1",
    "NSR10-A3-A_3_3_r2",
    "NSR10-A3-A_3_3_r3",
    "NSR10-A3-A_3_3_r4",
    "NSR10-A3-A_3_3_r5",
    "NSR10-A3-A_3_nota_de_cobertura-05",
]

CHUNKS = [
    {
        "id": "NSR10-A-A_3_3_1_A_3_3_2",
        "seccion": "A.3.3.1 y A.3.3.2 — Configuración estructural: general y definición",
        "titulo": "Título A, A.3.3.1-A.3.3.2: clasificación de la edificación como regular/irregular en planta y altura, y definición de configuración estructural.",
        "texto": (
            "A.3.3 — CONFIGURACIÓN ESTRUCTURAL DE LA EDIFICACIÓN\n\n"
            "A.3.3.1 — GENERAL — Para efectos de diseño sísmico la edificación debe "
            "clasificarse como regular o como irregular en planta y en altura o como "
            "redundante o con ausencia de redundancia de acuerdo con los requisitos "
            "de esta sección.\n\n"
            "A.3.3.2 — DEFINICIÓN DE LA CONFIGURACIÓN ESTRUCTURAL — Se entiende por "
            "configuración estructural de la edificación, no solamente la forma "
            "exterior de ella y su tamaño, sino la naturaleza, las dimensiones y la "
            "localización de los elementos estructurales, y no estructurales, que "
            "afecten el comportamiento de la edificación ante las solicitaciones "
            "sísmicas."
        ),
    },
    {
        "id": "NSR10-A-A_3_3_3_reduccion_valor_R",
        "seccion": "A.3.3.3 — Reducción del valor de R para estructuras irregulares y con ausencia de redundancia (ecuación A.3.3-1)",
        "titulo": "Título A, A.3.3.3: fórmula R = φa·φp·φr·R0 (ecuación A.3.3-1) — reducción del coeficiente de capacidad de disipación de energía por irregularidad en planta/altura y ausencia de redundancia.",
        "texto": (
            "A.3.3.3 — REDUCCIÓN DEL VALOR DE R PARA ESTRUCTURAS IRREGULARES Y CON "
            "AUSENCIA DE REDUNDANCIA — Cuando una estructura se clasifique como "
            "irregular, el valor del coeficiente de capacidad de disipación de "
            "energía R que se utilice en el diseño sísmico de la edificación, debe "
            "reducirse multiplicándolo por φp, debido a irregularidades en planta, "
            "por φa debido a irregularidades en altura, y por φr debido a ausencia "
            "de redundancia, como indica la ecuación A.3.3-1:\n\n"
            "R = φa · φp · φr · R0   (A.3.3-1)\n\n"
            "Cuando una edificación tiene varios tipos de irregularidad en planta "
            "simultáneamente, se aplicará el menor valor de φp. Análogamente, "
            "cuando una edificación tiene varios tipos de irregularidad en altura "
            "simultáneamente, se aplicará el menor valor de φa."
        ),
    },
    {
        "id": "NSR10-A-A_3_3_4_A_3_3_5_A_3_3_5_1",
        "seccion": "A.3.3.4, A.3.3.5 y A.3.3.5.1 — Configuración en planta, en altura, y excepciones a las irregularidades en altura",
        "titulo": "Título A, A.3.3.4-A.3.3.5.1: definición de irregularidad en planta (Tabla A.3-6) e irregularidad en altura (Tabla A.3-7), y excepción cuando la deriva de cada piso es menor a 1.3 veces la del piso superior.",
        "texto": (
            "A.3.3.4 — CONFIGURACIÓN EN PLANTA — La edificación se considera "
            "irregular cuando ocurra, véase la figura A.3-1, uno, o varios, de los "
            "casos descritos en la tabla A.3-6, donde se definen los valores de φp.\n\n"
            "A.3.3.5 — CONFIGURACIÓN EN LA ALTURA — Una edificación se clasifica "
            "como irregular en altura, véase la figura A.3-2, cuando ocurre uno, o "
            "varios, de los casos descritos en la tabla A.3-7, donde se definen los "
            "valores de φa.\n\n"
            "A.3.3.5.1 — Excepciones a las irregularidades en altura — Cuando para "
            "todos los pisos, la deriva de cualquier piso es menor de 1.3 veces la "
            "deriva del piso siguiente hacia arriba, puede considerarse que no "
            "existen irregularidades en altura de los tipos 1aA, 1bA, 2A, ó 3A, tal "
            "como se definen en la tabla A.3-7, y en este caso se aplica φa = 1. No "
            "hay necesidad de considerar en esta evaluación las derivas de los dos "
            "pisos superiores de la edificación ni la de los sótanos que tengan "
            "muros de contención integrados a la estructura en toda su periferia. "
            "Las derivas utilizadas en la evaluación pueden calcularse sin incluir "
            "los efectos torsionales. Así mismo, no se considera irregular la "
            "estructura flexible apoyada sobre una estructura con mayor rigidez que "
            "cumpla los requisitos correspondientes de la tabla A.3-5."
        ),
    },
    {
        "id": "NSR10-A-A_3_3_6_A_3_3_7",
        "seccion": "A.3.3.6 y A.3.3.7 — Evaluación simplificada de irregularidad en zonas de amenaza sísmica baja e intermedia",
        "titulo": "Título A, A.3.3.6-A.3.3.7: en zonas de amenaza sísmica baja (grupos I y II) la evaluación puede limitarse a irregularidades tipo 1aP/1bP en planta y 5aA/5bA en altura; en amenaza intermedia (grupo I) se agregan 3P/4P y 4A.",
        "texto": (
            "A.3.3.6 — EDIFICACIONES EN ZONAS DE AMENAZA SÍSMICA BAJA DE LOS GRUPOS "
            "DE USO I Y II — Para las edificaciones pertenecientes a los grupos de "
            "uso I y II, localizadas en zonas de amenaza sísmica baja, la "
            "evaluación para determinar si la edificación es irregular o no, puede "
            "limitarse a irregularidades en planta del tipo 1aP, 1bP (tabla A.3-6) "
            "y en altura del tipo 5aA y 5bA (tabla A.3-7).\n\n"
            "A.3.3.7 — EDIFICACIONES EN ZONAS DE AMENAZA SÍSMICA INTERMEDIA DEL "
            "GRUPO DE USO I — Para las edificaciones pertenecientes al grupo de uso "
            "I, localizadas en zonas de amenaza sísmica intermedia, la evaluación "
            "para determinar si la edificación es irregular o no, puede limitarse "
            "a irregularidades en planta de los tipos 1aP, 1bP, 3P y 4P (tabla "
            "A.3-6) y en altura de los tipos 4A, 5aA y 5bA (tabla A.3-7)."
        ),
    },
    {
        "id": "NSR10-A-A_3_3_8_ausencia_redundancia",
        "seccion": "A.3.3.8 — Ausencia de redundancia en el sistema estructural de resistencia sísmica (φr, DMI/DMO/DES)",
        "titulo": "Título A, A.3.3.8: factor de reducción por ausencia de redundancia φr — φr=1.0 para sistemas DMI; para DMO/DES se evalúan 4 condiciones (a-d) en pisos que resistan >35% del cortante basal, si no se cumplen φr=0.75.",
        "texto": (
            "A.3.3.8 — AUSENCIA DE REDUNDANCIA EN EL SISTEMA ESTRUCTURAL DE "
            "RESISTENCIA SÍSMICA — Debe asignarse un factor de reducción de "
            "resistencia por ausencia de redundancia en el sistema estructural de "
            "resistencia sísmica, φr, en las dos direcciones principales en planta "
            "de la siguiente manera:\n\n"
            "A.3.3.8.1 — En edificaciones con un sistema estructural con capacidad "
            "de disipación de energía mínima (DMI) — Para edificaciones cuyo "
            "sistema estructural de resistencia sísmica es de un material que "
            "cumple los requisitos de capacidad de disipación de energía mínima "
            "(DMI) el valor del factor de reducción de resistencia por ausencia de "
            "redundancia en el sistema estructural de resistencia sísmica, φr, se "
            "le asigna un valor de la unidad (φr = 1.0).\n\n"
            "A.3.3.8.2 — En edificaciones con un sistema estructural con capacidad "
            "de disipación de energía moderada (DMO) y especial (DES) — Para "
            "edificaciones cuyo sistema estructural es de un material que cumple "
            "los requisitos de capacidad de disipación de energía moderada (DMO) o "
            "especial (DES) el valor del factor de reducción por ausencia de "
            "redundancia en el sistema estructural de resistencia sísmica, φr, se "
            "le puede asignar un valor de la unidad (φr = 1.0) cuando en todos los "
            "pisos que resistan más del 35 por ciento del corte basal en la "
            "dirección bajo estudio el sistema estructural de resistencia sísmica "
            "cumpla las siguientes condiciones de redundancia:\n\n"
            "(a) En sistemas compuestos por pórticos con arriostramientos "
            "concéntricos — La falla de cualquiera de las diagonales o sus "
            "conexiones al pórtico no resulta en una reducción de más del 33 por "
            "ciento de la resistencia ante fuerzas horizontales del piso ni "
            "produce una irregularidad torsional en planta extrema (Tipo 1bP).\n"
            "(b) En sistemas compuestos por pórticos con arriostramientos "
            "excéntricos — La pérdida de resistencia a momento (si se trata de "
            "vínculos a momento), o a cortante (para el caso de vínculos a "
            "corte), de los dos extremos de un vínculo no resulta en una reducción "
            "de más del 33 por ciento de la resistencia ante fuerzas horizontales "
            "del piso ni produce una irregularidad torsional en planta extrema "
            "(Tipo 1bP).\n"
            "(c) En sistemas de pórtico resistente a momentos — La pérdida de la "
            "resistencia a momento en la conexión viga-columna de los dos "
            "extremos de una viga no resulta en una reducción de más del 33 por "
            "ciento de la resistencia ante fuerzas horizontales del piso ni "
            "produce una irregularidad torsional en planta extrema (Tipo 1bP).\n"
            "(d) En sistemas con muros estructurales de concreto estructural — La "
            "falla de un muro estructural o de una porción de él que tengan una "
            "relación de la altura del piso a su longitud horizontal mayor de la "
            "unidad, o de los elementos colectores que lo conectan al diafragma, "
            "no resulta en una reducción de más del 33 por ciento de la "
            "resistencia ante fuerzas horizontales del piso ni produce una "
            "irregularidad torsional en planta extrema (Tipo 1bP).\n"
            "(e) Para otros sistemas — No hay requisitos especiales.\n\n"
            "En los sistemas estructurales que no cumplan las condiciones "
            "enunciadas en (a) a (d) el factor de reducción de resistencia por "
            "ausencia de redundancia en el sistema estructural de resistencia "
            "sísmica, φr, se le debe asignar un valor de φr = 0.75. Aunque no se "
            "cumplan las condiciones enunciadas en (a) a (d) el factor de "
            "reducción de resistencia por ausencia de redundancia en el sistema "
            "estructural de resistencia sísmica, φr, se le debe asignar un valor "
            "igual a la unidad (φr = 1.0) si todos los pisos que resistan más del "
            "35 por ciento del corte basal en la dirección bajo estudio el sistema "
            "estructural de resistencia sísmica sean regulares en planta y tengan "
            "al menos dos vanos compuestos por elementos localizados en la "
            "periferia a ambos lados de la planta en las dos direcciones "
            "principales. Cuando se trate de muros estructurales para efectos de "
            "contar el número de vanos equivalentes se calcula como la longitud "
            "horizontal del muro dividida por la altura del piso."
        ),
    },
    {
        "id": "NSR10-A-A_3_3_9_sobrerresistencia",
        "seccion": "A.3.3.9 — Uso del coeficiente de sobrerresistencia Ω0 (ecuación A.3.3-2)",
        "titulo": "Título A, A.3.3.9: fórmula de fuerzas de diseño amplificadas por sobrerresistencia E=(Ω0·Fs/R)±0.5·Aa·Fa·D (ecuación A.3.3-2) para elementos frágiles de conexión.",
        "texto": (
            "A.3.3.9 — USO DEL COEFICIENTE DE SOBRERRESISTENCIA Ω0 — Cuando los "
            "requisitos para el material estructural y el grado de capacidad de "
            "disipación de energía requieren que los elementos frágiles o las "
            "conexiones entre elementos se diseñen para fuerzas sísmicas, E, "
            "amplificadas por el coeficiente de sobrerresistencia, Ω0, éste debe "
            "emplearse de la siguiente manera para obtener las fuerzas de diseño "
            "que incluyen los efectos sísmicos:\n\n"
            "E = (Ω0 · Fs / R) ± 0.5 · Aa · Fa · D   (A.3.3-2)\n\n"
            "Donde Fs corresponde a las fuerzas sísmicas obtenidas del análisis, R "
            "es el coeficiente de capacidad de disipación de energía correspondiente "
            "al sistema estructural de resistencia sísmica R = φa·φp·φr·R0, y D "
            "corresponde a la carga muerta que actúa sobre el elemento tal como se "
            "define en el Título B del Reglamento y el signo de la parte derecha "
            "de la ecuación es el que conduce al mayor valor de E, dependiendo del "
            "signo de Fs."
        ),
    },
    {
        "id": "NSR10-A-Tabla_A3-5_mezcla_sistemas_altura",
        "seccion": "Tabla A.3-5 — Mezcla de sistemas estructurales en la altura",
        "titulo": "Título A, Tabla A.3-5: requisitos para estructura flexible apoyada sobre una con mayor rigidez (no se considera irregular si cumple 3 condiciones a-c) y para estructura rígida apoyada sobre una con menor rigidez (no aceptable).",
        "texto": (
            "Tabla A.3-5 — Mezcla de sistemas estructurales en la altura:\n\n"
            "CASO 1: Estructura flexible apoyada sobre una estructura con mayor "
            "rigidez.\n"
            "Descripción de la combinación: Puede utilizarse los requisitos dados "
            "aquí si la estructura cumple las siguientes condiciones: (a) Ambas "
            "partes de la estructura, consideradas separadamente, puedan ser "
            "clasificadas como regulares de acuerdo con los requisitos de A.3.3, "
            "(b) El promedio de las rigideces de piso de la parte baja sea por lo "
            "menos 10 veces el promedio de las rigideces de piso de la parte alta "
            "y (c) El período de la estructura, considerada como un todo, no sea "
            "mayor de 1.1 veces el período de la parte superior, al ser "
            "considerada como una estructura independiente empotrada en la base. "
            "Si no se cumplen las condiciones anteriores la estructura se "
            "considera irregular y deben seguirse los requisitos de A.3.3.\n"
            "Requisitos: Se permite que esta combinación no se considere irregular "
            "(φp = φa = 1.0), y el sistema puede diseñarse sísmicamente utilizando "
            "el método de la fuerza horizontal equivalente, tal como lo prescribe "
            "el Capítulo A.4, de la siguiente manera: (1) La parte superior "
            "flexible puede ser analizada y diseñada como una estructura "
            "separada, apoyada para efecto de las fuerzas horizontales por la "
            "parte más rígida inferior, usando el valor apropiado de R0 para su "
            "sistema estructural. (2) La parte rígida inferior debe ser analizada "
            "y diseñada como una estructura separada, usando el valor apropiado "
            "de R0 para su sistema estructural, y las reacciones de la parte "
            "superior, obtenidas de su análisis, deben ser amplificadas por la "
            "relación entre el valor de R0 para la parte superior y el valor de "
            "R0 de la parte inferior.\n\n"
            "CASO 2: Estructura rígida apoyada sobre una estructura con menor "
            "rigidez.\n"
            "Descripción de la combinación: Corresponde a edificaciones en las "
            "cuales se suspende antes de llegar a la base de la estructura, "
            "parcial o totalmente, un sistema estructural más rígido que el que "
            "llega a la base de la estructura. Este tipo de combinación de "
            "sistemas estructurales en la altura presenta inconvenientes en su "
            "comportamiento sísmico. No es aceptable como una solución "
            "estructural para el presente Reglamento.\n"
            "Requisitos: (1) No es aceptable como solución estructural para el "
            "presente Reglamento."
        ),
    },
    {
        "id": "NSR10-A-Tabla_A3-6_irregularidades_planta",
        "seccion": "Tabla A.3-6 — Irregularidades en planta (5 tipos, coeficiente φp)",
        "titulo": "Título A, Tabla A.3-6: los 5 tipos de irregularidad en planta — 1aP torsional (φp=0.9), 1bP torsional extrema (φp=0.8), 2P retrocesos en esquinas (φp=0.9), 3P discontinuidades en diafragma (φp=0.9), 4P desplazamientos del plano de acción (φp=0.8), 5P sistemas no paralelos (φp=0.9).",
        "texto": (
            "Tabla A.3-6 — Irregularidades en planta:\n\n"
            "Tipo 1aP — Irregularidad torsional — La irregularidad torsional "
            "existe cuando en una edificación con diafragma rígido, la máxima "
            "deriva de piso de un extremo de la estructura, calculada incluyendo "
            "la torsión accidental y medida perpendicularmente a un eje "
            "determinado, es más de 1.2 y menor o igual a 1.4 veces la deriva "
            "promedio de los dos extremos de la estructura, con respecto al mismo "
            "eje de referencia. φp = 0.9. Referencias: A.3.3.6, A.3.4.2, A.3.6.3.1, "
            "A.3.6.7.1, A.3.6.8.4, A.5.2.1.\n\n"
            "Tipo 1bP — Irregularidad torsional extrema — La irregularidad "
            "torsional extrema existe cuando en una edificación con diafragma "
            "rígido, la máxima deriva de piso de un extremo de la estructura, "
            "calculada incluyendo la torsión accidental y medida "
            "perpendicularmente a un eje determinado, es más de 1.4 veces la "
            "deriva promedio de los dos extremos de la estructura, con respecto "
            "al mismo eje de referencia. φp = 0.8. Referencias: A.3.3.6, A.3.4.2, "
            "A.3.6.3.1, A.3.6.7.1, A.3.6.8.4, A.5.2.1.\n\n"
            "Tipo 2P — Retrocesos excesivos en las esquinas — La configuración de "
            "una estructura se considera irregular cuando ésta tiene retrocesos "
            "excesivos en sus esquinas. Un retroceso en una esquina se considera "
            "excesivo cuando las proyecciones de la estructura, a ambos lados del "
            "retroceso, son mayores que el 15 por ciento de la dimensión de la "
            "planta de la estructura en la dirección del retroceso. φp = 0.9. "
            "Referencias: A.3.4.2, A.3.6.8.4, A.3.6.8.5, A.5.2.1.\n\n"
            "Tipo 3P — Discontinuidades en el diafragma — Cuando el diafragma "
            "tiene discontinuidades apreciables o variaciones en su rigidez, "
            "incluyendo las causadas por aberturas, entrantes, retrocesos o "
            "huecos con áreas mayores al 50 por ciento del área bruta del "
            "diafragma o existen cambios en la rigidez efectiva del diafragma de "
            "más del 50 por ciento, entre niveles consecutivos, la estructura se "
            "considera irregular. φp = 0.9. Referencias: A.3.3.7, A.3.4.2, "
            "A.3.6.8.4, A.5.2.1.\n\n"
            "Tipo 4P — Desplazamientos del plano de acción de elementos "
            "verticales — La estructura se considera irregular cuando existen "
            "discontinuidades en las trayectorias de las fuerzas inducidas por "
            "los efectos sísmicos, tales como cuando se traslada el plano que "
            "contiene a un grupo de elementos verticales del sistema de "
            "resistencia sísmica, en una dirección perpendicular a él, generando "
            "un nuevo plano. Los altillos o mansardas de un solo piso se eximen "
            "de este requisito en la consideración de irregularidad. φp = 0.8. "
            "Referencias: A.3.3.7, A.3.4.2, A.3.6.12, A.5.2.1.\n\n"
            "Tipo 5P — Sistemas no paralelos — Cuando las direcciones de acción "
            "horizontal de los elementos verticales del sistema de resistencia "
            "sísmica no son paralelas o simétricas con respecto a los ejes "
            "ortogonales horizontales principales del sistema de resistencia "
            "sísmica, la estructura se considera irregular. φp = 0.9. "
            "Referencias: A.3.4.2, A.3.6.3.1, A.5.2.1.\n\n"
            "Notas: (1) En zonas de amenaza sísmica intermedia para edificaciones "
            "pertenecientes al grupo de uso I, la evaluación de irregularidad se "
            "puede limitar a las irregularidades de los tipos 1aP, 1bP, 3P y 4P "
            "(Véase A.3.3.7). (2) En zonas de amenaza sísmica baja para "
            "edificaciones pertenecientes a los grupos de uso I y II, la "
            "evaluación de irregularidad se puede limitar a las irregularidades "
            "tipo 1aP e 1bP (Véase A.3.3.6)."
        ),
    },
    {
        "id": "NSR10-A-Tabla_A3-7_irregularidades_altura",
        "seccion": "Tabla A.3-7 — Irregularidades en altura (6 tipos, coeficiente φa)",
        "titulo": "Título A, Tabla A.3-7: los 6 tipos de irregularidad en altura — 1aA piso flexible (φa=0.9), 1bA piso flexible extremo (φa=0.8), 2A distribución de masas (φa=0.9), 3A geométrica (φa=0.9), 4A desplazamientos en el plano de acción (φa=0.8), 5aA piso débil (φa=0.9), 5bA piso débil extremo (φa=0.8).",
        "texto": (
            "Tabla A.3-7 — Irregularidades en altura:\n\n"
            "Tipo 1aA — Piso flexible (Irregularidad en rigidez) — Cuando la "
            "rigidez ante fuerzas horizontales de un piso es menor del 70 por "
            "ciento pero superior o igual al 60 por ciento de la rigidez del piso "
            "superior o menor del 80 por ciento pero superior o igual al 70 por "
            "ciento del promedio de la rigidez de los tres pisos superiores, la "
            "estructura se considera irregular. φa = 0.9. Referencias: A.3.3.5.1, "
            "A.3.4.2.\n\n"
            "Tipo 1bA — Piso flexible (Irregularidad extrema en rigidez) — Cuando "
            "la rigidez ante fuerzas horizontales de un piso es menor del 60 por "
            "ciento de la rigidez del piso superior o menor del 70 por ciento del "
            "promedio de la rigidez de los tres pisos superiores, la estructura "
            "se considera irregular. φa = 0.8. Referencias: A.3.3.5.1, A.3.4.2.\n\n"
            "Tipo 2A — Irregularidad en la distribución de las masas — Cuando la "
            "masa, mi, de cualquier piso es mayor que 1.5 veces la masa de uno de "
            "los pisos contiguos, la estructura se considera irregular. Se "
            "exceptúa el caso de cubiertas que sean más livianas que el piso de "
            "abajo. φa = 0.9. Referencias: A.3.3.5.1, A.3.4.2.\n\n"
            "Tipo 3A — Irregularidad geométrica — Cuando la dimensión horizontal "
            "del sistema de resistencia sísmica en cualquier piso es mayor que "
            "1.3 veces la misma dimensión en un piso adyacente, la estructura se "
            "considera irregular. Se exceptúa el caso de los altillos de un solo "
            "piso. φa = 0.9. Referencias: A.3.4.2.\n\n"
            "Tipo 4A — Desplazamientos dentro del plano de acción — La estructura "
            "se considera irregular cuando existen desplazamientos en el "
            "alineamiento de elementos verticales del sistema de resistencia "
            "sísmica, dentro del mismo plano que los contiene, y estos "
            "desplazamientos son mayores que la dimensión horizontal del "
            "elemento. Cuando los elementos desplazados solo sostienen la "
            "cubierta sin otras cargas adicionales de tanques o equipos, se "
            "eximen de esta consideración de irregularidad. φa = 0.8. "
            "Referencias: A.3.3.7, A.3.4.2, A.3.6.12.\n\n"
            "Tipo 5aA — Piso débil — Discontinuidad en la resistencia — Cuando la "
            "resistencia del piso es menor del 80 por ciento de la del piso "
            "inmediatamente superior o igual al 65 por ciento, entendiendo la "
            "resistencia del piso como la suma de las resistencias de todos los "
            "elementos que comparten el cortante del piso para la dirección "
            "considerada, la estructura se considera irregular. φa = 0.9. "
            "Referencias: A.3.2.4.1, A.3.3.6, A.3.3.7, A.3.4.2.\n\n"
            "Tipo 5bA — Piso débil — Discontinuidad extrema en la resistencia — "
            "Cuando la resistencia del piso es menor del 65 por ciento de la del "
            "piso inmediatamente superior, entendiendo la resistencia del piso "
            "como la suma de las resistencias de todos los elementos que "
            "comparten el cortante del piso para la dirección considerada, la "
            "estructura se considera irregular. φa = 0.8. Referencias: A.3.2.4.1, "
            "A.3.3.6, A.3.3.7, A.3.4.2.\n\n"
            "Notas: (1) Cuando la deriva de cualquier piso es menor de 1.3 veces "
            "la deriva del piso siguiente hacia arriba, puede considerarse que no "
            "existen irregularidades de los tipos 1aA, 1bA, 2A, ó 3A (Véase "
            "A.3.3.5.1). (2) En zonas de amenaza sísmica intermedia para "
            "edificaciones pertenecientes al grupo de uso I, la evaluación de "
            "irregularidad se puede limitar a las irregularidades de los tipos "
            "4A, 5aA y 5bA (Véase A.3.3.7). (3) En zonas de amenaza sísmica baja "
            "para edificaciones pertenecientes a los grupos de usos I y II, la "
            "evaluación de irregularidad se puede limitar a la irregularidad "
            "tipo 5aA y 5bA (Véase A.3.3.6)."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

    print(f"Borrando {len(IDS_A_BORRAR)} chunks viejos (paráfrasis/pendientes)...")
    sb.table("nsr10_chunks").delete().in_("id", IDS_A_BORRAR).execute()

    print("Cargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    textos = [c["texto"] for c in CHUNKS]
    print(f"Codificando {len(textos)} chunks-padre de A.3.3...")
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

    print(f"Subiendo {len(rows)} chunks-padre de A.3.3 a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_a_a33_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
