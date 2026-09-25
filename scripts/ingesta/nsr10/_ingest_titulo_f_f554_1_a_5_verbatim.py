"""
Ingesta verbatim de NSR-10 Título F.5.5.4.1 a F.5.5.4.5 (Vigas
Ensambladas -- Estructuras de Aluminio): resistencia a momento (.4.1),
resistencia a cortante (.4.2, con acción de campo tensionado), vigas
rigidizadas longitudinal y transversalmente (.4.3), rigidizadores de
alma y platinas de enchape (.4.4) y uso de almas corrugadas o
frecuentemente rigidizadas (.4.5). Fase 5 del plan de cierre de Título F.

Fuente: NSR-10-1183-1283.pdf (páginas internas F-512 a F-519), ya
descargado desde Google Drive en la Fase 2, en
scripts/ingesta/nsr10/raw/ (gitignored). Mismo offset confirmado:
página_F = página_real - 681.

Nota de fidelidad honesta: las Figuras F.5.5.4-1, F.5.5.4-2 y F.5.5.4-3
(coeficientes de pandeo por cortante v2, v3, m1) son curvas de
interpolación gráfica (familias de curvas paramétricas por a/d) sin
ecuación cerrada -- no se transcriben valores numéricos leídos de la
curva, mismo criterio ya aplicado repetidamente en Título F.

Uso: python _ingest_titulo_f_f554_1_a_5_verbatim.py
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
        "id": "NSR10-F-F_5_5_4_intro", "seccion": "F.5.5.4",
        "titulo": "F.5.5.4 — Vigas Ensambladas: definición, alcance de .4.1-.4.6, apéndice F.5-D como alternativa, condiciones de aplicabilidad",
        "texto": (
            "F.5.5.4 — VIGAS ENSAMBLADAS — Una viga ensamblada es una viga fabricada consistente de láminas "
            "actuando como aleta a tensión, aleta a compresión y alma. El alma típicamente tiene proporciones "
            "esbeltas y está reforzada transversalmente con rigidizadores de apoyo e intermedios (véase la figura "
            "F.5.5.1-3). Puede tener también rigidizadores longitudinales. Una característica básica es que los "
            "rigidizadores del alma son diseñados para dar extremos soportados a los paneles del alma "
            "permaneciendo esencialmente rectos cuando ocurre el pandeo. "
            "Las resistencias a momento y cortante de las vigas ensambladas con almas transversalmente "
            "rigidizadas son cubiertas por F.5.5.4.1 y F.5.5.4.2. En F.5.5.4.3 se dan las modificaciones "
            "necesarias para cuando se adicionan rigidizadores longitudinales. Se permite seguir el apéndice F.5-D "
            "en lugar de F.5.5.4.1, si se desea, para determinar la resistencia a momento, esto puede conducir a "
            "economía en el diseño. "
            "Los métodos dados en F.5.5.4.1, F.5.5.4.2 y F.5.5.4.3 son válidos siempre que ocurra lo siguiente: los "
            "rigidizadores cumplen con F.5.5.4.4; el espaciamiento a de los rigidizadores transversales no es "
            "menor que la mitad de la altura libre del alma medida entre las aletas (para almas corrugadas o "
            "cercanamente rigidizadas, véase F.5.5.4.5). "
            "Puede ser benéfico suministrar una platina de enchape, a una o ambas aletas. Esta debe cumplir con el "
            "literal (g) de F.5.5.4.4 para ser efectiva. "
            "La interacción entre momento y cortante es tratada en F.5.5.4.6. "
            "Si el aplastamiento del alma o el pandeo torsional lateral se consideran factores influyentes, el "
            "diseñador debe consultar F.5.4.5.5 o F.5.4.5.6. Para vigas sujetas a carga axial y flexión, es "
            "pertinente F.5.4.8. "
            "El tratamiento de vigas ensambladas dado en F.5.5.4.1 a F.5.5.4.6 es generalmente también aplicable a "
            "vigas con sección en cajón siempre que las almas sean de forma similar."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_1_a_b", "seccion": "F.5.5.4.1",
        "titulo": "F.5.5.4.1 — Resistencia a momento de vigas rigidizadas transversalmente: revisión por fluencia (a) y por pandeo (b)",
        "texto": (
            "F.5.5.4.1 — Resistencia a momento de vigas ensambladas rigidizadas transversalmente — Para determinar "
            "la resistencia de diseño a momento se debe hacer una revisión por fluencia y una revisión por pandeo. "
            "Para vigas híbridas, con materiales diferentes en aletas y alma, se debe consultar también el literal "
            "(d) de F.5.4.5.2. "
            "(a) Revisión por fluencia — El momento generado en cualquier sección transversal bajo carga mayorada "
            "no debe exceder la resistencia de diseño a momento MRS que se usaría si la sección fuera tratada como "
            "semi-compacta. El valor de MRS se obtiene usando el literal (b) de F.5.4.5.2 (ecuación F.5.4.5-2 o "
            "F.5.4.5-4), según sea adecuado, teniendo en cuenta los agujeros y los efectos de la zona afectada por "
            "el calor pero ignorando el pandeo local. Si la viga no está lateralmente soportada, debe revisarse de "
            "acuerdo con F.5.4.5.6. "
            "(b) Revisión por pandeo — El siguiente tratamiento se aplica a vigas ensambladas con rigidizadores "
            "transversales pero sin rigidizadores longitudinales. "
            "Para cada tramo de viga entre rigidizadores transversales, el momento generado bajo carga mayorada, a "
            "una distancia igual a 0.4a del extremo más esforzado, no debe exceder la resistencia de diseño a "
            "momento MRS de ese tramo basada en la falla última por pandeo. El valor de MRS se obtiene de acuerdo "
            "con el literal (b) de F.5.4.5.2 (ecuación F.5.4.5-5), teniendo en cuenta el pandeo local y el "
            "ablandamiento en la zona afectada por el calor pero ignorando los agujeros. Sin embargo, para el "
            "propósito de esta revisión es permitido ignorar los efectos de la zona afectada por el calor, "
            "causados por la soldadura de los rigidizadores transversales. "
            "Para considerar el pandeo del alma se debe encontrar el coeficiente de espesor efectivo kL de acuerdo "
            "con F.5.4.3.4, tomando β como en el literal (a) de F.5.4.3.2. No obstante, si el extremo a compresión "
            "del alma está más cerca del eje neutro que el extremo a tensión, se permite, en su lugar, proceder "
            "como en el literal (c) de F.5.5.4.1, lo que tiende a ser más favorable. "
            "Se puede suponer que cualquier platina de enchape, si es suministrada, brinda soporte efectivo en el "
            "extremo a la lámina esbelta del alma a la cual está unida siempre y cuando cumpla con el literal (g) "
            "de F.5.5.4.4. Por lo tanto, para encontrar kL para la lámina del alma en la figura F.5.4.3-5 (b), β "
            "puede basarse en un valor d medido hasta la punta de la o las platinas de enchape."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_1_c", "seccion": "F.5.5.4.1(c)",
        "titulo": "F.5.5.4.1(c) — Tratamiento alternativo del pandeo del alma: Zona 1 (kL función de y1) y Zona 2 (kL=1.0)",
        "texto": (
            "(c) Tratamiento alternativo del pandeo del alma — Si el eje neutro está localizado de modo que está "
            "más cerca del extremo del alma a compresión que del extremo a tensión, se permite tratar el alma como "
            "compuesta por dos zonas con diferentes valores de kL obtenidos como se indica a continuación: "
            "Zona 1, se extiende una distancia y1 a cada lado del eje neutro: kL se lee en la figura F.5.4.3-5 (b) "
            "tomando β = 0.7 y1/t donde y1 es la distancia desde el eje neutro de la sección bruta hasta el "
            "extremo a compresión. "
            "Zona 2, ocupa el resto del alma: kL = 1.0."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_2_a_b", "seccion": "F.5.5.4.2",
        "titulo": "F.5.5.4.2 — Resistencia a cortante de vigas rigidizadas transversalmente: revisión por fluencia (a, ec. F.5.5.4-1/2) y por pandeo (b, ec. F.5.5.4-3/4)",
        "texto": (
            "F.5.5.4.2 — Resistencia a cortante de vigas ensambladas rigidizadas transversalmente — Se deben hacer "
            "dos revisiones: por fluencia y por pandeo. En almas con soldaduras continuas longitudinales es "
            "también necesario hacer una revisión por zona afectada por el calor (véase el literal (d) de este "
            "numeral). La presencia de pequeños agujeros en la lámina del alma puede ignorarse para cada revisión "
            "siempre que éstos no ocupen más del 20% del área de la sección. "
            "(a) Revisión por fluencia — La fuerza cortante V generada bajo carga mayorada en cualquier sección "
            "transversal, no debe exceder el valor de VRS encontrado como se indica enseguida: "
            "sin platina de enchape: VRS = φ Pvw Awe  (F.5.5.4-1). con platina o platinas de enchape: "
            "VRS = φ(Pvw Awe + Pvt Ate)  (F.5.5.4-2). "
            "Donde: Pvw, Pvt = esfuerzos límites para los materiales del alma y la platina saliente respectivamente "
            "(equivalente a Pv en las tablas F.5.4.2-1 y F.5.4.2-2). Awe = área de la sección efectiva del alma "
            "entre las aletas, o hasta los extremos de la platina de enchape. Ate = área de la sección efectiva de "
            "la platina de enchape, o área total de dos de ellas. φ = coeficiente de reducción de capacidad (véase "
            "la tabla F.5.3.3-1). "
            "Las áreas efectivas se obtienen tomando un espesor reducido igual a kz veces el espesor real en "
            "cualquier región afectada por el calor (véanse F.5.4.4.2 y F.5.4.4.3). "
            "(b) Revisión por pandeo — En cualquier vano entre rigidizadores transversales, la fuerza cortante V "
            "generada bajo carga mayorada no debe exceder el valor límite VRS para ese vano, basado en la falla "
            "última por pandeo. El valor de VRS debe encontrarse usando la expresión apropiada de las siguientes, "
            "en las que se saca ventaja del comportamiento posterior al pandeo: "
            "sin platina de enchape: VRS = φ(v1 + vtf) Pvw d t  (F.5.5.4-3). con platina o platinas de enchape: "
            "VRS = φ[(v1 + vtf) Pvw d t + Pvt Ate]  (F.5.5.4-4). "
            "Donde: d = altura del alma medida entre aletas, o hasta los extremos de la platina de enchape. "
            "t = espesor no reducido de la lámina del alma. v1 = coeficiente de pandeo inicial por cortante, leído "
            "en la figura F.5.5.3-1 tomando ε=(15/Pv)^(1/2). vtf = coeficiente de campo tensionado (véase el "
            "literal (c) siguiente). Las otras cantidades son las definidas en el literal (c) de este numeral."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_2_c", "seccion": "F.5.5.4.2(c)",
        "titulo": "F.5.5.4.2(c) — Acción de campo tensionado: paneles Tipo 1 (con vtf, ec. F.5.5.4-5/6) vs. Tipo 2 (vtf=0)",
        "texto": (
            "(c) Acción de campo tensionado — Se identifican dos tipos de paneles de alma: "
            "Tipo 1: paneles capaces de mantener un campo tensionado, es decir: un panel interno, un panel en un "
            "tramo final con un poste extremo que cumple con el literal (e) de F.5.5.4.4. "
            "Tipo 2: un panel en un tramo final que carece de un poste extremo adecuado. En los paneles tipo 2, la "
            "acción de campo tensionado es despreciable y por lo tanto vtf debe ser tomado como cero en el literal "
            "(b) de F.5.5.4.2. "
            "Los paneles tipo 1 son generalmente capaces de desarrollar resistencia a cortante adicional después "
            "de la aparición inicial de pandeo, debido a la acción de campo tensionado. En este caso vtf debe "
            "tomarse de acuerdo con lo siguiente: "
            "(i) Panel no soldado: vtf = v2 + m·v3  (F.5.5.4-5). "
            "(ii) Panel con soldaduras en los extremos: vtf = kz(v2 + m·v3)  (F.5.5.4-6). "
            "Donde: v2 = coeficiente de pandeo por cortante determinado en la figura F.5.5.4-1. v3 = coeficiente de "
            "pandeo por cortante determinado en la figura F.5.5.4-2. kz = coeficiente de ablandamiento de la zona "
            "afectada por el calor (véase F.5.4.4.2). m1, m2 = coeficientes de pandeo por cortante, donde m1 se "
            "determina en la figura F.5.5.4-3 y m2 = (4 pof Sf / (pow d² t))^(1/2). Donde: pof y pow = esfuerzos "
            "límite po para el material de las aletas y el alma (véase la tabla F.5.4.2-1). Sf = módulo plástico "
            "de la sección de aleta efectiva respecto a su propio eje de igual área, en el plano del alma (se toma "
            "el menor valor si las aletas son diferentes). El valor de m se toma como el menor de m1 y m2. "
            "Para determinar Sf, la sección considerada debe incluir la lámina de la aleta conjuntamente con la "
            "platina de enchape si está presente, con la reducción de espesor apropiada para tener en cuenta el "
            "pandeo local y el ablandamiento en la zona afectada por el calor (véase el literal (c) de F.5.4.5.2) "
            "pero sin reducción por agujeros. Si la viga tiene dos o más almas, el módulo plástico de la aleta "
            "completa debe ser apropiadamente compartido para obtener Sf para cada alma."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_2_figuras", "seccion": "F.5.5.4-1_a_F.5.5.4-3",
        "titulo": "Figuras F.5.5.4-1 (v2), F.5.5.4-2 (v3) y F.5.5.4-3 (m1): coeficientes de pandeo por cortante con campo tensionado, curvas gráficas NO transcritas",
        "texto": (
            "Figura F.5.5.4-1 — Coeficiente básico de pandeo al corte considerando campo tensionado, v2: curva de "
            "interpolación gráfica (eje vertical v2 de 0 a 0.5, eje horizontal d/te de 0 a más de 280, familia de "
            "curvas paramétricas por relación a/d de 0.50 a ≥2.5). Nota del original: esta figura no debe usarse "
            "para paneles con rigidizadores longitudinales. "
            "Figura F.5.5.4-2 — Coeficiente de pandeo al corte considerando campo tensionado y contribución de la "
            "aleta, v3: misma estructura de ejes (v3 de 0 a 2.0, d/te de 0 a más de 280, familia por a/d). Misma "
            "nota: no debe usarse para paneles con rigidizadores longitudinales. "
            "Figura F.5.5.4-3 — Coeficiente de pandeo por cortante m1: misma estructura (m1 de 0 a 0.8, d/te de 0 "
            "a más de 280, familia por a/d). Misma nota: no debe usarse para paneles con rigidizadores "
            "longitudinales. "
            "Las tres son lecturas gráficas de interpolación sin ecuación cerrada — no se transcriben valores "
            "numéricos de las curvas, deben leerse directamente del PDF original (páginas F-514 y F-515)."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_2_d", "seccion": "F.5.5.4.2(d)",
        "titulo": "F.5.5.4.2(d) — Revisión por zona afectada por el calor en almas con soldaduras longitudinales: ecuación F.5.5.4-7",
        "texto": (
            "(d) Revisión por zona afectada por el calor — En almas con soldaduras longitudinales, la fuerza "
            "cortante V, generada bajo carga mayorada, no debe sobrepasar la resistencia de diseño a fuerza "
            "cortante de cualquiera de tales soldaduras. VRS está dado por: "
            "VRS = φ kz pvw I t / (Ae ȳ)  (F.5.5.4-7). "
            "Donde: I = segundo momento del área de la sección bruta. Ae ȳ = primer momento del área bruta "
            "excluida por fuera de la soldadura. Ae = área de la sección. ȳ = distancia del centroide del eje "
            "neutro hasta esta área. kz, pvw, φ = de acuerdo con su definición en los literales (a) y (c) de "
            "F.5.5.4.2."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_3", "seccion": "F.5.5.4.3",
        "titulo": "F.5.5.4.3 — Vigas rigidizadas longitudinal y transversalmente: resistencia a momento (a) y a cortante (b)",
        "texto": (
            "F.5.5.4.3 — Vigas rigidizadas longitudinal y transversalmente. "
            "(a) Resistencia a momento — El procedimiento para determinar la resistencia a momento es básicamente "
            "el mismo que para vigas con rigidizadores transversales únicamente e involucra una revisión por "
            "fluencia y una revisión por pandeo. La revisión por fluencia se realiza de acuerdo con el literal (a) "
            "de F.5.5.4.1. "
            "Para hacer la revisión por pandeo (véase el literal (b) de F.5.5.4.1) se supone que cada rigidizador "
            "longitudinal brinda una línea de apoyo al alma subdividiéndola en sub-paneles separados desde el "
            "punto de vista de pandeo local. Para determinar la sección efectiva de la viga se pueden usar valores "
            "mejorados de kL para los sub-paneles que se obtienen tomando el ancho y el patrón de esfuerzo correcto "
            "para cada sub-panel para determinar su valor de β. "
            "(b) Resistencia a cortante — Las revisiones por fluencia (véase el literal (a) de F.5.5.4.2) y por "
            "zona afectada por el calor (véase el literal (d) de F.5.5.4.2) no se afectan por la presencia de "
            "rigidizadores longitudinales. "
            "La revisión por pandeo se debe llevar a cabo, generalmente, de acuerdo con el literal (b) de "
            "F.5.5.4.2, pero v1 y vtf se determinan como se indica a continuación: "
            "el valor de v1 se determina en la figura F.5.5.3-1 tomando d igual a la altura del mayor sub-panel "
            "(en lugar de la altura total del alma); el valor de vtf se calcula usando la ecuación apropiada "
            "F.5.5.4-5 o F.5.5.4-6 en el literal (c) de F.5.5.4.2, con los factores v2, v3 y m obtenidos así: "
            "los valores v2, v3 y m1 se calculan usando las fórmulas del apéndice F.5-I que se relacionan con las "
            "figuras F.5.5.4-1 a F.5.5.4-3, respectivamente, tomando d como la altura total tal como se define en "
            "el literal (b) de F.5.5.4.2 y v1 como el valor encontrado de acuerdo con lo anterior. Las figuras "
            "F.5.5.4-1 a F.5.5.4-3 no deben usarse para paneles de alma con rigidizadores longitudinales. "
            "El valor de m2 se calcula como en el literal (c) de F.5.5.4.2 tomando un d tal como se define en el "
            "literal (b) del mismo numeral."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_4_a_b", "seccion": "F.5.5.4.4",
        "titulo": "F.5.5.4.4 — Rigidizadores de alma y platinas de enchape: Tipos A/B/C, compacidad (a) y sección efectiva de rigidizador (b, ec. F.5.5.4-8)",
        "texto": (
            "F.5.5.4.4 — Rigidizadores de alma y platinas de enchape — Se consideran los siguientes tipos de "
            "rigidizador de alma (véase la figura F.5.5.1-3). Pueden estar colocados a uno o ambos lados. "
            "Tipo A, rigidizador intermedio — rigidizador transversal diferente de los cubiertos por el tipo B. "
            "Tipo B, rigidizador de apoyo — rigidizador transversal localizado en el punto de aplicación una carga "
            "concentrada o reacción. Tipo C, rigidizador longitudinal — rigidizador atravesado longitudinalmente "
            "entre rigidizadores transversales. "
            "Para que las resistencias proyectadas se logren, es generalmente necesario que los rigidizadores de "
            "alma cumplan con lo siguiente: tipos A, B, C — compacidad (véase el literal (a) de F.5.5.4.4); tipos "
            "A, B, C — rigidez (véase el literal (c) de F.5.5.4.4); tipos A, B únicamente — estabilidad (véase el "
            "literal (d) de F.5.5.4.4). "
            "Un rigidizador transversal debe extenderse sin interrupciones de aleta a aleta aún cuando se coloquen "
            "platinas de enchape. Cuando se coloca un rigidizador de apoyo se debe cuidar que la aleta transfiera "
            "la fuerza aplicada al rigidizador. No es esencial que el rigidizador esté conectado a las aletas. "
            "Mientras sea posible, los rigidizadores longitudinales deben ser continuos desde un vano de la viga "
            "hasta el siguiente. Cuando ésto no sea posible, las longitudes separadas deben colindar con el "
            "rigidizador transversal que las divide. "
            "(a) Compacidad — Todos los rigidizadores deben ser de sección compacta en términos de resistencia a "
            "compresión axial (véase el literal (c) de F.5.4.3.3). "
            "(b) Sección efectiva de rigidizador — La sección efectiva de rigidizador se usa en la revisión de los "
            "requisitos de rigidez y estabilidad. Consiste del rigidizador, o par de rigidizadores si están a "
            "ambos lados, real en conjunto con un ancho efectivo de lámina de alma, be (véase la figura F.5.5.4-4). "
            "Este ancho efectivo se extiende una distancia b1 a cada lado del punto o puntos de fijación del "
            "rigidizador como se muestra, y está dado generalmente por: "
            "(1) Para un rigidizador transversal: b1 = el menor de 0.13a y 15εt. Para un rigidizador transversal "
            "localizado en el extremo de una viga, el valor de b1 en el lado exterior (únicamente) debe tomarse "
            "como se indica a continuación en lugar del valor anterior: b1 = el menor de a0 y 7εt, donde a0 es la "
            "distancia desde el rigidizador hasta el borde libre de la lámina del alma. "
            "(2) Para un rigidizador longitudinal: b1 = el menor de 0.13dav y 15εt. Donde: ε = (15/pv)^(1/2). "
            "pv = esfuerzo límite del material del alma (véanse las tablas F.5.4.2-1 y F.5.4.2-2). dav = altura "
            "promedio de los dos sub-paneles situados a cada lado del rigidizador longitudinal. (F.5.5.4-8: ε = "
            "(15/pv)^(1/2))."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_4_c", "seccion": "F.5.5.4.4(c)",
        "titulo": "F.5.5.4.4(c) — Rigidez: rigidizador transversal (ec. F.5.5.4-9) y longitudinal (ec. F.5.5.4-10), condición sobre a/d o dav/a",
        "texto": (
            "(c) Rigidez — Para las proporciones de panel dadas, el segundo momento del área Is de la sección "
            "completa de rigidizador efectivo (véase el literal (b) de F.5.5.4.4) respecto al eje centroidal "
            "paralelo al alma, debe satisfacer lo siguiente: "
            "(1) Para un rigidizador transversal, si a/d ≤ 2.5: Is ≥ d t³ (2d/a − 0.7)  (F.5.5.4-9). "
            "(2) Para un rigidizador longitudinal, si dav/a ≤ 2.5: Is ≥ a t³ (2a/dav − 0.7)  (F.5.5.4-10). "
            "La condición de rigidez puede obviarse cuando las proporciones del panel están por fuera del rango "
            "indicado."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_4_d", "seccion": "F.5.5.4.4(d)",
        "titulo": "F.5.5.4.4(d) — Estabilidad de rigidizadores transversales: carga P para rigidizador intermedio (ec. F.5.5.4-11) y de apoyo (ec. F.5.5.4-12), longitud efectiva de columna (ec. F.5.5.4-13/14)",
        "texto": (
            "(d) Estabilidad (Rigidizadores transversales únicamente) — La sección efectiva de rigidizador (véase "
            "el literal (b) de F.5.5.4.4) se considera como un miembro a compresión que soporta una carga P, bajo "
            "carga mayorada, dada por: "
            "(1) Para un rigidizador intermedio: P = V/3  (F.5.5.4-11). "
            "(2) Para un rigidizador de apoyo: P = p1 + V/3  (F.5.5.4-12). "
            "Donde: V = valor promedio de la fuerza cortante generada en los paneles del alma a cada lado del "
            "rigidizador considerado. P1 = carga concentrada o reacción que actúa en el rigidizador. "
            "El valor de P no debe exceder la resistencia axial de diseño del miembro a compresión, determinada de "
            "acuerdo con F.5.4.7 tomando en cuenta el pandeo como columna (fuera del plano del alma) y el "
            "aplastamiento local pero ignorando el pandeo torsional. Para considerar el pandeo como columna, se "
            "debe tomar una longitud efectiva de miembro a compresión l de acuerdo con: "
            "para a/d ≥ 1.5: l = d  (F.5.5.4-13). "
            "para a/d < 1.5: l = d / [1.6 - (0.4a/d)]^(1/2)  (F.5.5.4-14). "
            "Cuando la dimensión a del panel es diferente en los lados opuestos de un rigidizador, se debe tomar un "
            "valor promedio para ella en las expresiones F.5.5.4-13 y F.5.5.4-14. Para cualquier rigidizador "
            "extremo, l = d. "
            "Es importante tener en cuenta los efectos de flexión que se introducen si hay excentricidad entre la "
            "línea de acción de P y el eje centroidal de la sección efectiva. Esto puede ser hecho usando las "
            "fórmulas de interacción dadas en F.5.4.8.3 y F.5.4.8.4 (c), donde My es el momento debido a la acción "
            "y Mx=0. Tal excentricidad ocurre especialmente cuando se usan rigidizadores a un solo lado."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_4_e", "seccion": "F.5.5.4.4(e)",
        "titulo": "F.5.5.4.4(e) — Postes extremos requeridos para resistir el campo tensionado: 2 funciones, 2 formas constructivas, ecuaciones F.5.5.4-15/16",
        "texto": (
            "(e) Postes extremos requeridos para resistir el campo tensionado — Cuando se determina la resistencia "
            "a fuerza cortante de un tramo extremo de una viga ensamblada, sólo se permite tomar ventaja de la "
            "acción de campo tensionado si se suministra un poste adecuado en el extremo exterior del panel del "
            "alma. Este debe diseñarse para cumplir con las siguientes dos funciones, la interacción entre los dos "
            "efectos puede ignorarse: actuar como un rigidizador de apoyo resistiendo la reacción en el apoyo de "
            "la viga; actuar como una viga corta uniendo las aletas de la viga y resistiendo el campo tensionado "
            "en el plano del alma. "
            "Un poste de extremo puede tener cualquiera de las siguientes formas y, en cada caso, debe estar "
            "seguramente conectado a ambas aletas de la viga. Puede contar de dos rigidizadores transversales de "
            "doble lado que forman las aletas de una viga corta, conjuntamente con una tira de lámina del alma "
            "entre ellos. Uno de los rigidizadores transversales debe estar localizado apropiadamente para que "
            "cumpla el papel de soporte. Puede ser en la forma de material insertado conectado al extremo de la "
            "lámina del alma. "
            "Para llevar a cabo la segunda función, el poste de extremo tiene que resistir una fuerza cortante Vep "
            "conjuntamente con un momento Mep actuando en el plano de la lámina del alma (bajo carga mayorada), "
            "dados por las siguientes expresiones: "
            "Vep = 0.6 pv d t [1 - v1(q/(Pv - v1)) / v2]^(1/2)  (F.5.5.4-15). Mep = 0.1 d Vep  (F.5.5.4-16). "
            "Donde: q = esfuerzo cortante promedio generado en el panel extremo del alma bajo carga mayorada, "
            "basado en el espesor reducido. pv = esfuerzo límite del material del alma (véanse las tablas "
            "F.5.4.2-1 y F.5.4.2-2). v1 y v2 = coeficientes relacionados con los paneles extremos, encontrados en "
            "las figuras F.5.5.3-1 y F.5.5.4-1 ó en F.5.5.4.3 (si es longitudinalmente rigidizada). "
            "Para calcular q se permite suponer que parte de la fuerza cortante sobre la viga es soportada por las "
            "platinas de enchape, si las hay."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_4_f", "seccion": "F.5.5.4.4(f)",
        "titulo": "F.5.5.4.4(f) — Postes extremos requeridos para resistir torsión: ecuación F.5.5.4-17",
        "texto": (
            "(f) Postes extremos requeridos para resistir torsión — Si un poste de extremo es el único medio de "
            "suministro de resistencia contra el retorcimiento en el extremo de una viga, se debe cumplir lo "
            "siguiente: Iep ≥ d³ tf R / (250 W)  (F.5.5.4-17). "
            "Donde: Iep = segundo momento del área de la sección del poste extremo respecto a la línea central del "
            "alma. d = altura del alma medida entre aletas o hasta los extremos de la platina de enchape. "
            "tf = espesor de la aleta (tomado como el valor máximo cuando el espesor varía a lo largo de la viga "
            "considerado). R = reacción en el extremo de la viga considerado, bajo carga mayorada. W = carga total "
            "mayorada sobre la luz adyacente."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_4_g", "seccion": "F.5.5.4.4(g)",
        "titulo": "F.5.5.4.4(g) — Platinas de enchape: definición, compacidad, construcción en dos o tres capas",
        "texto": (
            "(g) Platinas de enchape — Una platina de enchape consiste de material que se extiende hacia adentro "
            "desde una aleta para formar una parte engrosada hacia el alma. Para ser efectiva, sus dimensiones "
            "deben ser tales que sea compacta en compresión axial (véase F.5.4.3.3). "
            "Cuando una platina de enchape está construida en dos o tres capas, consistiendo de la lámina del alma "
            "conectada a un elemento, o elementos, integral con la aleta, el espesor t requerido para revisar su "
            "compacidad puede tomarse como el espesor total. Sin embargo, si la construcción es remachada o "
            "pernada, es también necesario revisar que cualquier saliente más allá de la última línea de remaches "
            "o pernos sea, por sí sola, compacta."
        ),
    },
    {
        "id": "NSR10-F-F_5_5_4_5", "seccion": "F.5.5.4.5",
        "titulo": "F.5.5.4.5 — Uso de almas corrugadas o frecuentemente rigidizadas: refuerzo subcrítico, resistencia a momento (a) y a cortante (b)",
        "texto": (
            "F.5.5.4.5 — Uso de almas corrugadas o frecuentemente rigidizadas — Las vigas que tienen refuerzo "
            "transversal del alma en forma de corrugaciones o de rigidizadores poco espaciados, con una separación "
            "de menos de 0.3 veces la altura entre aletas, se describen en los literales (a) y (b) siguientes. "
            "Este refuerzo transversal se trata como subcrítico de modo que puede deformarse con el alma en el "
            "modo de pandeo general y, por lo tanto, no necesariamente satisface los literales (c) y (d) de "
            "F.5.5.4.4. "
            "(a) Resistencia a momento — Cuando el alma consiste de una lámina plana con rigidizadores fijados, la "
            "resistencia a momento debe encontrarse según F.5.5.4.1. Pero con un alma corrugada debe suponerse que "
            "la contribución del alma es cero y la resistencia a momento es suministrada únicamente por las "
            "aletas. "
            "(b) Resistencia a fuerza cortante — La resistencia de diseño a fuerza cortante VRS debe determinarse "
            "como se indica en F.5.5.3.4 para láminas multi-rigidizadas a cortante."
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
