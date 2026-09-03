"""
Ingesta verbatim de NSR-10 Titulo F.5.4.5 (Estructuras de Aluminio --
Diseno Estatico de Miembros: VIGAS).

Fuente: NSR-10-1083-1182.pdf (paginas internas F-476 a F-488), ya
descargado localmente en scripts/ingesta/nsr10/raw/ (gitignored).
Texto transcrito verbatim leyendo el PDF nativo pagina por pagina
(nunca el texto plano exportado, corrompe subindices/formulas).

Sistema de unidades: kgf/kgf.mm^2 (no SI) -- ver F.5.1.1.

Uso: python _ingest_titulo_f_f545_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_5_4_5_1_generalidades",
        "seccion": "F.5.4.5.1 — Generalidades",
        "titulo": "F.5.4.5 Vigas",
        "texto": (
            "F.5.4.5 — VIGAS\n\n"
            "F.5.4.5.1 — Generalidades — Las siguientes revisiones se deben "
            "realizar a todas las vigas (incluyendo vigas ensambladas).\n\n"
            "(a) Revisión a momento — En cualquier sección transversal, el "
            "momento M bajo carga mayorada no debe exceder la resistencia "
            "de diseño a momento MRS de la sección, calculada de acuerdo "
            "con F.5.4.5.2 (o alternamente de acuerdo con el apéndice "
            "F.5.D). MRS se debe reducir apropiadamente, cuando sea "
            "necesario, para tener en cuenta un cortante coincidente "
            "(véase F.5.4.5.4).\n\n"
            "(b) Revisión a cortante — En cualquier sección transversal, "
            "la fuerza cortante V bajo carga mayorada no debe exceder la "
            "resistencia de diseño a fuerza cortante VRS (véase "
            "F.5.4.5.3).\n\n"
            "En algunos casos, es necesario hacer también una o ambas de "
            "las siguientes revisiones:\n\n"
            "(1) Revisión de aplastamiento del alma (véase F.5.4.5.5)\n"
            "(2) Revisión de pandeo torsional lateral (véase F.5.4.5.6)\n\n"
            "Las vigas ensambladas, que tienen almas rigidizadas más "
            "esbeltas, deben diseñarse preferiblemente usando F.5.5.4. Se "
            "permite diseñarlas como vigas pero es probable que se pierda "
            "en economía.\n\n"
            "Para el diseño de vigas sometidas a flexión biaxial "
            "combinada con carga axial, se debe usar F.5.4.8. Las vigas "
            "sujetas a flexión biaxial respecto a ambos ejes principales "
            "se deben revisar también de acuerdo con F.5.4.8."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_2_a_b_clasificacion_calculo_basico",
        "seccion": "F.5.4.5.2(a)(b) — Clasificación de la sección, cálculo básico de MRS",
        "titulo": "6 casos de MRS: no soldada/soldada × totalmente compacta/semi-compacta/esbelta, eq F.5.4.5-1 a -6",
        "texto": (
            "F.5.4.5.2 — Resistencia a momento uniaxial de la sección\n\n"
            "(a) Clasificación de la sección para resistencia a momento — "
            "Primero es necesario clasificar la sección como totalmente "
            "compacta, semi-compacta o esbelta basándose en el elemento "
            "componente menos favorable, de acuerdo con F.5.4.3.3.\n\n"
            "En el caso de un elemento saliente reforzado que forme parte "
            "o sea toda la aleta a compresión, la presencia de refuerzo "
            "en forma de una pestaña dirigida hacia afuera debe ignorarse "
            "para la clasificación de la sección.\n\n"
            "(b) Cálculo básico — La resistencia de diseño a momento MRS "
            "de una sección dada, en ausencia de cortante, debe "
            "encontrarse, por lo general, como se indica a continuación:\n\n"
            "No soldada, totalmente compacta: MRS = po Zn φ (F.5.4.5-1)\n"
            "No soldada, semi-compacta: MRS = po Sn φ (F.5.4.5-2)\n"
            "Soldada, totalmente compacta: MRS = po Zne φ (F.5.4.5-3)\n"
            "Soldada, semi-compacta: MRS = po Sne φ (F.5.4.5-4)\n"
            "No soldada, esbelta: MRS = po Se φ o, MRS = po Sn φ lo que "
            "sea menor (F.5.4.5-5)\n"
            "Soldada, esbelta: MRS = po Se φ o, MRS = po Sne φ lo que sea "
            "menor (F.5.4.5-6)\n\n"
            "Donde:\n"
            "Sn y Zn = módulos elástico y plástico, respectivamente, de "
            "la sección neta\n"
            "Sne y Zne = módulos elástico y plástico, respectivamente, de "
            "la sección neta efectiva\n"
            "Se = módulo plástico de la sección efectiva\n"
            "po = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2)\n"
            "φ = coeficiente de reducción de capacidad (véase la tabla "
            "F.5.3.3-1)\n\n"
            "Se permite en secciones semi-compactas y esbeltas, si es "
            "favorable, tomar la resistencia a momento basada en un "
            "patrón de esfuerzos elasto-plástico tal como se indica en "
            "el apéndice F.5.D. Si esto se hace, la nota 5 del literal "
            "(c) de este mismo numeral no es válida."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_2_c_seccion_supuesta_espesor",
        "seccion": "F.5.4.5.2(c) — Sección supuesta: sección neta, neta efectiva, efectiva",
        "titulo": "Espesor reducido: elemento esbelto (kL t), no-esbelto ablandado (kz t), esbelto+ablandado (menor de ambos)",
        "texto": (
            "(c) Sección supuesta — La terminología usada en el literal "
            "(b) de este mismo numeral implica lo siguiente:\n\n"
            "• La sección neta incluye solamente la reducción por los "
            "agujeros\n"
            "• La sección neta efectiva incluye el espesor reducido "
            "tomado en la vecindad de las soldaduras para tener en "
            "cuenta el ablandamiento en la zona afectada por el calor "
            "conjuntamente con la reducción por los agujeros.\n"
            "• La sección efectiva incluye el espesor reducido para "
            "tomar en cuenta el ablandamiento en la zona afectada por el "
            "calor y el pandeo local pero no se hace reducción por los "
            "agujeros.\n\n"
            "El espesor reducido se debe tomar, por lo general, de "
            "acuerdo con lo siguiente para los diferentes elementos en "
            "una sección.\n\n"
            "(1) Elemento esbelto libre de efectos de zona afectada por "
            "el calor — Se toma un espesor kL t para todo el elemento, "
            "kL se encuentra siguiendo F.5.4.3.4.\n\n"
            "(2) Elementos no-esbeltos sujetos a efectos de zona "
            "afectada por el calor — Se toma un espesor kz t para las "
            "partes ablandadas del elemento. kz y la extensión del "
            "ablandamiento están dados en F.5.4.4.2 y F.5.4.4.3.\n\n"
            "(3) Elemento esbelto con efectos de zona afectada por el "
            "calor — Se toma el espesor reducido como el menor de kz t y "
            "kL t para la parte ablandada y kL t para el resto del "
            "elemento."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_2_c_notas1_5_kzy",
        "seccion": "F.5.4.5.2(c) — Notas 1-5, coeficiente kzy",
        "titulo": "Nota 3: eq F.5.4.5-7. Nota 5: eq F.5.4.5-8, kzy",
        "texto": (
            "Nota 1 — Cuando se localiza un agujero en la región de "
            "espesor reducido, la reducción para ese agujero debe "
            "basarse en el espesor reducido.\n\n"
            "Nota 2 — En el caso de elementos reforzados, kL se debe "
            "aplicar al área del refuerzo así como al espesor básico de "
            "la lámina.\n\n"
            "Nota 3 — Cuando se considera un elemento de aleta esbelto "
            "que se localiza más cerca del eje neutro que la fibra "
            "extrema a tensión del material, se permite tomar un valor "
            "más favorable de kL. Esto se hace usando un valor "
            "modificado de ε en la figura F.5.4.3-5 (en lugar del valor "
            "normal, véase el literal (a) de F.5.4.3.4) de acuerdo con:\n\n"
            "ε = (25 y1 / po y2)^(1/2)  (F.5.4.5-7)\n\n"
            "donde y1 y y2 son las distancias desde el eje neutro "
            "elástico de la sección bruta hasta las fibras extremas y "
            "hasta el elemento considerado, respectivamente. Esta "
            "relación se aplica sólo si el elemento es substancialmente "
            "paralelo al eje de flexión.\n\n"
            "Nota 4 — Para un elemento reforzado que forma parte de la "
            "aleta a compresión de una sección esbelta en la cual el "
            "refuerzo tiene la forma de una pestaña dirigida hacia "
            "afuera, la presencia de la pestaña debe ignorarse para "
            "determinar la resistencia a momento.\n\n"
            "Nota 5 — Para un elemento soldado en una sección "
            "semi-compacta o esbelta, se puede suponer un espesor más "
            "favorable de acuerdo con lo siguiente:\n\n"
            "• Se ignora el ablandamiento en la zona afectada por el "
            "calor para cualquier material que esté a menos de kz y1 "
            "del eje neutro elástico de la sección bruta, donde y1 es la "
            "distancia de allí a las fibras más lejanas de la sección.\n"
            "• Para el material de la zona afectada por el calor, a una "
            "distancia y > kz y1 del eje neutro, kz se puede reemplazar "
            "por un valor kzy determinado de acuerdo con:\n\n"
            "kzy = kz + 1 - y/y1  (F.5.4.5-8)"
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_2_d_e_hibridas_semicompactas",
        "seccion": "F.5.4.5.2(d)(e) — Secciones híbridas, secciones semi-compactas",
        "titulo": "Interpolación MRS eq F.5.4.5-9",
        "texto": (
            "(d) Secciones híbridas — La capacidad a momento de una "
            "sección híbrida que contiene materiales de diferente "
            "resistencia, se debe encontrar, con seguridad, en el menor "
            "valor de po dentro de la sección. Como alternativa puede "
            "usarse el siguiente procedimiento que es más ventajoso.\n\n"
            "• Cada elemento se clasifica de acuerdo con su valor "
            "particular de po\n"
            "• Para una sección totalmente compacta, MRS se encuentra "
            "usando la teoría de flexión plástica convencional teniendo "
            "en cuenta el valor de po en cada elemento y usando "
            "nuevamente la sección neta efectiva en el caso de miembros "
            "soldados\n"
            "• Para otras secciones, MRS se encuentra con la expresión "
            "F.5.20, F.5.22 o F.5.23 del literal (b) de F.5.4.5.2, la "
            "que sea apropiada, tomando como base los valores de po y Z "
            "del punto de la sección que da los menores valores de "
            "MRS.\n\n"
            "(e) Secciones semi-compactas — Para este tipo de secciones "
            "se permite, si se desea, tomar una valor mejorado de MRS "
            "que se obtiene por interpolación de acuerdo con lo "
            "siguiente:\n\n"
            "MRS = Ms + [(β0 - β)/(β0 - β1)] (Mf - Ms)  (F.5.4.5-9)\n\n"
            "Donde:\n"
            "Mf y Ms = valores de MRS totalmente compacto y "
            "semi-compacto encontrados de acuerdo con el literal (b) de "
            "F.5.4.5.2\n"
            "β = valor de β para el elemento más crítico de la sección\n"
            "β1 y β0 = valores límite de β totalmente y semi-compacto "
            "para ese mismo elemento (véase la tabla F.5.4.3-1)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_3_a_clasificacion_cortante",
        "seccion": "F.5.4.5.3(a) — Clasificación de la sección para cortante",
        "titulo": "d/t≤49ε compacta, d/t>49ε esbelta; almas con/sin platinas, barra sólida, tubería redonda",
        "texto": (
            "F.5.4.5.3 — Resistencia a fuerza cortante\n\n"
            "(a) Clasificación de la sección — Primero es necesario "
            "clasificar la sección como compacta o esbelta en términos "
            "de su resistencia a fuerza cortante: una sección compacta "
            "no se afecta por pandeo mientras que una sección esbelta se "
            "debe revisar a pandeo. Las secciones se clasifican como "
            "sigue:\n\n"
            "(1) Secciones que contienen almas a cortante orientadas en "
            "el plano de carga, sin platinas de enchape:\n"
            "d/t ≤ 49ε → compacta\n"
            "d/t > 49ε → esbelta\n\n"
            "Donde:\n"
            "d = altura libre del alma entre aletas (medida sobre la "
            "pendiente en el caso de almas inclinadas)\n"
            "t = espesor del alma\n"
            "ε = (25/po)^(1/2) = (15/pv)^(1/2)\n"
            "po y pv = esfuerzos límite (en kgf/mm²) (véanse las tablas "
            "F.5.4.2-1 y F.5.4.2-2)\n\n"
            "(2) Secciones que contienen almas a cortante orientadas en "
            "el plano de carga, con platinas de enchape — Véase el "
            "literal (e).\n"
            "(3) Barra sólida — compacta\n"
            "(4) Tubería redonda — la misma clasificación que para "
            "compresión axial (véanse el literal (d) de F.5.4.3.2 y el "
            "literal (c) de F.5.4.3.3.)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_3_b_secciones_compactas_av",
        "seccion": "F.5.4.5.3(b) — Secciones compactas, área efectiva de cortante Av",
        "titulo": "VRS=φpvAv eq F.5.4.5-10; Av=0.8NDt (F.5.4.5-11), con ablandamiento (F.5.4.5-12), barra sólida (F.5.4.5-13), tubo (F.5.4.5-14)",
        "texto": (
            "(b) Secciones compactas — La resistencia de diseño a fuerza "
            "cortante VRS de una sección, en ausencia de momento, se "
            "puede calcular mediante la siguiente ecuación:\n\n"
            "VRS = φ pv Av  (F.5.4.5-10)\n\n"
            "Donde:\n"
            "pv = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2)\n"
            "Av = área efectiva de cortante\n"
            "φ = coeficiente de reducción de capacidad (véase la tabla "
            "F.5.3.3-1)\n\n"
            "El área de la sección efectiva será:\n\n"
            "(1) Para secciones que contienen almas a cortante sin "
            "platinas de enchape que están libres de ablandamiento en "
            "la zona afectada por el calor, Av se determina usando:\n\n"
            "Av = 0.8NDt  (F.5.4.5-11)\n\n"
            "Donde:\n"
            "D = altura total del alma medida desde la superficie "
            "exterior de las aletas\n"
            "t = espesor del alma\n"
            "N = número de almas\n\n"
            "La presencia de pequeños agujeros se puede ignorar siempre "
            "y cuando ellos no ocupen, en total, más del 20% de la "
            "altura libre del alma entre aletas.\n\n"
            "(2) Para secciones como las de (1) pero con almas afectadas "
            "por ablandamiento en la zona afectada por el calor, Av se "
            "determina con la siguiente ecuación:\n\n"
            "Av = N(0.8Dt - (1-kz)dz t)  (F.5.4.5-12)\n\n"
            "Donde:\n"
            "dz = altura total de material de la zona afectada por el "
            "calor dentro de la altura libre entre aletas del alma "
            "(véase F.5.4.4.3)\n"
            "kz = coeficiente de ablandamiento (véase F.5.4.4.2)\n\n"
            "Para un alma soldada en toda su altura o continuamente "
            "soldada longitudinalmente en cualquier punto de su altura, "
            "VRS se debe tomar como kz veces el valor no soldado.\n\n"
            "(3) Para una barra sólida: Av = 0.8A ó 0.8Ae  (F.5.4.5-13)\n"
            "(4) Para un tubo redondo compacto: Av = 0.6A ó 0.6Ae  "
            "(F.5.4.5-14)\n\n"
            "Donde:\n"
            "A = área de la sección (en ausencia de ablandamiento en la "
            "zona afectada por el calor)\n"
            "Ae = área efectiva de la sección (cuando hay ablandamiento "
            "en la zona afectada por el calor) encontrada tomando un "
            "espesor efectivo de kz veces el espesor real para el "
            "material de la zona afectada por el calor.\n\n"
            "En el caso de secciones que contienen almas a cortante, se "
            "pueden usar los métodos para el cálculo de VRS de vigas "
            "ensambladas (véanse los literales (a) y (d) de F.5.5.4.2)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_3_c_secciones_esbeltas",
        "seccion": "F.5.4.5.3(c) — Secciones esbeltas: fluencia y pandeo",
        "titulo": "VRS = φ(34000Nt³/d) ≤ φpvAv (F.5.4.5-15)",
        "texto": (
            "(c) Secciones esbeltas — La resistencia de diseño a fuerza "
            "cortante VRS, en ausencia de momento, para secciones que "
            "contienen almas esbeltas a cortante sin platinas de enchape "
            "y orientadas en el plano de carga, se debe tomar como la "
            "menor de los dos valores obtenidos en las siguientes "
            "revisiones:\n\n"
            "(1) Revisión a fluencia — La resistencia se calcula como "
            "para una sección compacta usando el literal (b) de "
            "F.5.4.5.3.\n\n"
            "(2) Revisión por pandeo — El valor de VRS en kgf se obtiene "
            "con la siguiente expresión:\n\n"
            "VRS = φ (34 000 N t³ / d) ≤ φ pv Av  (F.5.4.5-15)\n\n"
            "Donde:\n"
            "d = altura libre del alma entre aletas"
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_3_d_e_almas_inclinadas_platinas",
        "seccion": "F.5.4.5.3(d)(e) — Almas a cortante inclinadas, uso de platinas de enchape",
        "titulo": "Factor cos θ para almas inclinadas; v1/vtf para platinas",
        "texto": (
            "(d) Almas a cortante inclinadas — Las expresiones que "
            "cubren secciones compactas en el literal (b) de F.5.4.5.3 "
            "siguen siendo válidas para almas inclinadas siempre que D "
            "sea medido perpendicularmente al eje neutro. Para revisar "
            "secciones inclinadas esbeltas (véase el literal (c) de "
            "F.5.4.5.3), la expresión F.5.4.5-15 debe factorarse por cos "
            "θ, donde θ es el ángulo entre el alma y el plano de "
            "aplicación de la carga.\n\n"
            "(e) Uso de platinas de enchape — La resistencia a fuerza "
            "cortante de secciones que contienen almas a cortante con "
            "platinas de enchape puede generalmente calcularse, con "
            "seguridad, usando el tratamiento dado en F.5.5.4.2 pero con "
            "los coeficientes v tomados como sigue:\n\n"
            "v1 = coeficiente de pandeo crítico al corte en el rango "
            "elástico determinado según el literal (b) de F.5.5.4.2\n"
            "vtf = coeficiente de campo tensionado, igual a cero\n\n"
            "Este tratamiento es válido sólo si las platinas de enchape "
            "cumplen con F.5.5.4.4."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_4_combinacion_momento_cortante",
        "seccion": "F.5.4.5.4 — Combinación de momento y fuerza cortante",
        "titulo": "MRSO eq F.5.4.5-16/-17: cortante bajo/elevado",
        "texto": (
            "F.5.4.5.4 — Combinación de momento y fuerza cortante\n\n"
            "(a) Momento con cortante bajo — En cualquier sección, se "
            "puede suponer que la resistencia de diseño a momento MRS no "
            "se afecta por una fuerza cortante coincidente V (bajo carga "
            "mayorada) menor que la mitad de la resistencia de diseño a "
            "fuerza cortante VRS encontrada en el literal (c) de "
            "F.5.4.5.3.\n\n"
            "(b) Momento con cortante elevado — Si V excede 0.5VRS, se "
            "debe calcular un valor reducido de la resistencia de diseño "
            "a momento MRSO:\n\n"
            "(1) Para secciones con almas a cortante conectadas a aletas "
            "en ambos extremos longitudinales:\n\n"
            "MRSO = MRS (1 + (1-α)(0.6 - 1.2V/VRS))  (F.5.4.5-16)\n\n"
            "(2) Para otras secciones:\n\n"
            "MRSO = MRS (1.6 - 1.2V/VRS)  (F.5.4.5-17)\n\n"
            "Donde:\n"
            "MRS = resistencia de diseño a momento de la sección, en "
            "ausencia de cortante (véase F.5.4.5.2)\n"
            "α = relación entre los esfuerzos cortantes mínimo y máximo "
            "en el alma suponiendo distribución elástica de esfuerzos\n\n"
            "Para secciones clasificadas como esbeltas para flexión o "
            "afectadas por ablandamiento en la zona afectada por el "
            "calor, α debe basarse en la sección supuesta usada en la "
            "demostración de MRS (véase el literal (c) de F.5.4.5.2)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_5_a_aplastamiento_alma_no_rigidizada",
        "seccion": "F.5.4.5.5(a) — Aplastamiento del alma, alma no rigidizada",
        "titulo": "pw1≤φpa o kzpa/φ (F.5.4.5-18); pw2≤φps (F.5.4.5-19)",
        "texto": (
            "F.5.4.5.5 — Aplastamiento del alma — Este numeral trata del "
            "diseño de almas sometidas a fuerzas localizadas causadas "
            "por cargas concentradas o reacciones aplicadas a una viga.\n\n"
            "(a) Alma no rigidizada — Cuando el alma, por sí sola, debe "
            "soportar la fuerza localizada, sin el suministro de un "
            "rigidizador de apoyo, como por ejemplo bajo una carga "
            "rodante, las dos condiciones siguientes deben cumplirse:\n\n"
            "pw1 ≤ φpa o, kz pa / φ  (F.5.4.5-18)\n"
            "pw2 ≤ φps  (F.5.4.5-19)\n\n"
            "Donde:\n"
            "pw1, pw2 = esfuerzos en el borde extremo y en el punto "
            "medio, respectivamente, suponiendo un ángulo de dispersión "
            "de 45° a cada lado de una fuerza localizada\n"
            "pa = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2)\n"
            "ps = esfuerzo de pandeo para el alma tratada como una "
            "columna delgada entre aletas\n"
            "kz = coeficiente de ablandamiento para el material de la "
            "zona afectada por el calor (véase F.5.4.4.2)\n"
            "φ = coeficiente de reducción de capacidad (véase la tabla "
            "F.5.3.3-1)\n\n"
            "En la ecuación F.5.4.5-18, la segunda expresión debe "
            "usarse cuando el alma está soldada a la aleta y hay "
            "ablandamiento en la zona afectada por el calor. De otro "
            "modo, la primera expresión es válida.\n\n"
            "El valor de ps debe determinarse de acuerdo con el literal "
            "(a) de F.5.4.7.3, seleccionando la curva en la figura "
            "F.5.4.5-3(a) que intercepta el eje de esfuerzos en un valor "
            "po (véanse las tablas F.5.4.2-1 y F.5.4.2-2). El parámetro "
            "de esbeltez λ que se debe usar para seleccionar la curva "
            "debe tener en cuenta el posible movimiento lateral relativo "
            "de las aletas cuando el alma se pandea y nunca debe ser "
            "menor que 3.5d/t."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_5_b_c_platina_enchape_rigidizada",
        "seccion": "F.5.4.5.5(b)(c) — Alma con platina de enchape, alma rigidizada",
        "titulo": "F.5.4.5.5",
        "texto": (
            "(b) Alma con platina de enchape — Cuando se suministra una "
            "platina de enchape, se debe satisfacer la ecuación "
            "F.5.4.5-18 tanto en el extremo superior de la platina de "
            "enchape como en el extremo superior del alma delgada.\n\n"
            "(c) Alma rigidizada — Un rigidizador de apoyo apropiado "
            "debe ser de sección compacta. Puede ser conservadoramente "
            "diseñado suponiendo que resiste la fuerza de aplastamiento "
            "completa, sin ayuda del alma. El rigidizador se revisa como "
            "un miembro a compresión (véase F.5.4.7) para pandeo como "
            "columna fuera del plano y aplastamiento local considerando "
            "efectos de flexión, si es necesario (véase F.5.4.8). "
            "Alternativamente, se puede diseñar un rigidizador más "
            "económico utilizando la cláusula de rigidizador de viga "
            "ensamblada (véase F.5.5.4.4)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_6_intro_a_condicion_basica",
        "seccion": "F.5.4.5.6 — Pandeo torsional lateral, condición básica",
        "titulo": "Casos donde se puede ignorar; M≤MRx eq F.5.4.5-20",
        "texto": (
            "F.5.4.5.6 — Pandeo torsional lateral — Una viga, que no sea "
            "una de las excepciones dadas aquí, se debe revisar contra "
            "posible falla por pandeo torsional lateral de acuerdo con "
            "los literales (a) a (f) de este mismo numeral.\n\n"
            "La posibilidad de falla prematura por pandeo torsional "
            "lateral se puede ignorar en cualquiera de los siguientes "
            "casos:\n\n"
            "• Flexión respecto al eje menor\n"
            "• Viga soportada contra movimiento lateral en toda su "
            "longitud\n"
            "• Soporte lateral de la aleta a compresión suministrado a "
            "espaciamiento no mayor que 40εry\n\n"
            "Donde:\n"
            "ry = eje de giro menor de la sección\n"
            "ε = (25/po)^(1/2)\n"
            "po = esfuerzo límite (en kgf/mm²) del material de la aleta "
            "a compresión (véanse las tablas F.5.4.2-1 y F.5.4.2-2)\n\n"
            "(a) Condición básica — La viga debe revisarse por posible "
            "pandeo torsional lateral en cada tramo no soportado entre "
            "puntos de apoyo lateral. En cada uno de ellos se debe "
            "satisfacer la siguiente condición:\n\n"
            "M ≤ MRx  (F.5.4.5-20)\n\n"
            "Donde:\n"
            "M = momento bajo carga mayorada en la longitud considerada\n"
            "MRx = momento factorado de resistencia a pandeo torsional "
            "lateral, es igual a ps S/φ\n"
            "S = módulo plástico de la sección bruta sin reducción por "
            "ablandamiento en la zona afectada por el calor, pandeo "
            "local o agujeros\n"
            "φ = coeficiente de reducción de capacidad (véase la tabla "
            "F.5.3.3-1)\n"
            "ps = esfuerzo de pandeo (véase el literal (c) de F.5.4.5.6)"
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_6_b_margen_variacion_momento",
        "seccion": "F.5.4.5.6(b) — Margen para variación de momento",
        "titulo": "M̄=0.6M1+0.4M2 (F.5.4.5-21); M̄=0.4M1 (F.5.4.5-22); Figura F.5.4.5-1",
        "texto": (
            "(b) Margen para variación de momento — El valor de M en el "
            "literal (a) puede ser, seguramente, tomado como el valor "
            "máximo en el tramo considerado. Como alternativa, se "
            "permite tomar M como el momento uniforme equivalente M̄. "
            "Para el caso de gradiente simple de momento en la longitud "
            "considerada (variación lineal) M̄ se puede tomar como se "
            "indica enseguida:\n\n"
            "para 1.0 > M2/M1 ≥ -0.5: M̄ = 0.6M1 + 0.4M2  (F.5.4.5-21)\n"
            "para M2/M1 < -0.5: M̄ = 0.4M1  (F.5.4.5-22)\n\n"
            "donde M1 y M2 son, respectivamente, los momentos máximo y "
            "mínimo (véase la figura F.5.4.5-1). Para otros casos de "
            "variación de momento consulte el apéndice F.5.G.\n\n"
            "Figura F.5.4.5-1 — Pandeo torsional lateral, momento "
            "uniforme equivalente M̄: viga apoyada con momentos M1 y M2 "
            "aplicados en cada extremo, diagrama de momentos con "
            "variación lineal entre M1 (máximo) y M2 (mínimo, puede ser "
            "negativo), y el valor uniforme equivalente M̄ marcado entre "
            "ambos."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_6_figuras_2_3_pandeo_columna",
        "seccion": "Figuras F.5.4.5-2 y F.5.4.5-3(a)(b)(c) — Esfuerzo de pandeo",
        "titulo": "Gráficas ps (kgf/mm²) vs λ para vigas y miembros a compresión",
        "texto": (
            "Figura F.5.4.5-2 — Pandeo torsional lateral de vigas, "
            "esfuerzo de pandeo ps: gráfica de ps (kgf/mm², eje vertical "
            "0-30+) contra λ (eje horizontal 0-130+), familia de curvas "
            "descendentes desde valores altos de ps en λ bajo hacia "
            "valores bajos en λ alto, convergiendo hacia una curva "
            "límite común en λ grande. NOTA: para encontrar ps con "
            "λ>130 véase la figura F.5.I-1, apéndice I.\n\n"
            "Figura F.5.4.5-3(a) — Esfuerzo de pandeo como columna para "
            "miembros a compresión ps: misma forma de gráfica (ps vs "
            "λ), familia de curvas equivalente para el caso de "
            "compresión axial en vez de flexión. NOTA: para encontrar ps "
            "con λ>130 véase la figura F.5.I-1, apéndice I.\n\n"
            "Figura F.5.4.5-3(b) — Esfuerzo de pandeo como columna para "
            "miembros a compresión ps: continuación de la familia de "
            "curvas de (a), mismo formato y nota sobre λ>130.\n\n"
            "Figura F.5.4.5-3(c) — Esfuerzo de pandeo como columna para "
            "miembros a compresión ps: tercera y última página de la "
            "familia de curvas, mismo formato y nota sobre λ>130. Estas "
            "tres figuras (a)(b)(c) forman un solo conjunto de curvas "
            "por tipo/condición de sección, seleccionadas según el "
            "literal (a) de F.5.4.7.3 para el cálculo de ps en "
            "aplastamiento del alma (F.5.4.5.5) y compresión axial "
            "(F.5.4.7)."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_6_c_esfuerzo_pandeo_p1",
        "seccion": "F.5.4.5.6(c) — Esfuerzo de pandeo, valor de p1",
        "titulo": "p1=po no soldadas totalmente compactas (F.5.4.5-23); p1=MRS/φS otras (F.5.4.5-24)",
        "texto": (
            "(c) Esfuerzo de pandeo — El esfuerzo de pandeo torsional "
            "lateral ps se lee en la figura F.5.4.5-2 usando la curva "
            "que intercepta el eje de esfuerzos en un esfuerzo p1 "
            "encontrado de acuerdo con lo siguiente:\n\n"
            "(1) Para secciones no soldadas totalmente compactas:\n\n"
            "p1 = po  (F.5.4.5-23)\n\n"
            "(2) Para otras secciones incluyendo secciones híbridas:\n\n"
            "p1 = MRS / (φS)  (F.5.4.5-24)\n\n"
            "Donde:\n"
            "po = esfuerzo límite (véanse las tablas F.5.4.2-1 y "
            "F.5.4.2-2)\n"
            "MRS = resistencia a momento de diseño de la sección\n"
            "S = módulo plástico de la sección bruta\n"
            "φ = coeficiente de reducción de capacidad (véase la tabla "
            "F.5.3.3-1)\n\n"
            "Por lo general, MRS debe determinarse de acuerdo con "
            "F.5.4.5.2 teniendo en cuenta pandeo local y ablandamiento "
            "en la zona afectada por el calor pero sin reducción por "
            "agujeros.\n\n"
            "Para vigas de gran esbeltez (λ>130) es necesario consultar "
            "la curva adimensional apropiada en el apéndice F.5.I para "
            "encontrar ps."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_6_d_parametro_esbeltez",
        "seccion": "F.5.4.5.6(d) — Parámetro de esbeltez λ",
        "titulo": "Valor conservador (F.5.4.5-25), expresión general (F.5.4.5-26), miembros I/canal (F.5.4.5-27)",
        "texto": (
            "(d) Parámetro de esbeltez — El parámetro de esbeltez de "
            "pandeo torsional lateral, λ, necesario para la figura "
            "F.7.4.9, se puede obtener usando cualquiera de las "
            "siguientes expresiones F.5.4.5-25 a F.5.4.5-27.\n\n"
            "Valor conservador: λ = λy = l/ry  (F.5.4.5-25)\n\n"
            "Donde:\n"
            "l = longitud efectiva para pandeo torsional lateral\n"
            "ry = radio de giro del eje menor para la sección bruta\n\n"
            "Para los siguientes casos, se debe usar el apéndice F.5.G "
            "para calcular la longitud efectiva de la viga (l):\n\n"
            "(1) vigas en voladizo\n"
            "(2) vigas sujetas a cargas desestabilizadoras, esto es, "
            "carga entre puntos de soporte lateral que efectivamente "
            "actúa en un punto de la sección sobre el lado a compresión "
            "del eje neutro\n"
            "(3) vigas sujetas a cargas normales cuando la aleta a "
            "compresión no está lateralmente restringida, ambas aletas "
            "pueden rotar en el plano y la restricción torsional es "
            "suministrada únicamente por el soporte de la aleta de "
            "fondo en los apoyos.\n\n"
            "Para todos los otros tipos de soporte, l, puede tomarse "
            "seguramente como la distancia entre puntos de soporte "
            "lateral. Alternativamente, se puede encontrar un valor más "
            "favorable para ciertas condiciones de restricción usando "
            "F.5.G.1.\n\n"
            "Expresión general: λ = π(ES/Mcr)^(1/2)  (F.5.4.5-26)\n\n"
            "Donde:\n"
            "E = módulo de elasticidad\n"
            "S = módulo plástico de la sección bruta\n"
            "Mcr = momento uniforme elástico crítico (véase F.5.G.2)\n\n"
            "Miembros con sección en I o en canal cubiertos en la tabla "
            "F.5.4.5-1 — El parámetro λ puede tomarse como se indica "
            "enseguida pero no debe exceder el valor dado por la "
            "ecuación F.5.4.5-25:\n\n"
            "λ = Xλy / [1 + Y(λy/(D/t2))²]^(1/4)  (F.5.4.5-27)\n\n"
            "Donde:\n"
            "D = altura total de la sección\n"
            "t2 = espesor de la aleta\n"
            "X y Y = coeficientes tomados de la tabla F.5.4.5-1 (pueden "
            "ser tomados conservadoramente como X=1.0, Y=0.05)\n\n"
            "Cuando el refuerzo de la aleta de una viga en I o un "
            "miembro en canal no es de la forma precisa mostrada en la "
            "tabla F.5.4.5-1 (pestañas simples), se permite inclusive "
            "obtener λ usando la expresión F.5.4.5-27. Si esto se hace, "
            "X y Y deben tomarse como para una pestaña simple "
            "equivalente que tiene la misma altura interna C, en tanto "
            "que λy se calcula para la sección con el refuerzo real."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_6_e_f_restricciones_soldaduras",
        "seccion": "F.5.4.5.6(e)(f) — Restricciones laterales efectivas, vigas con soldaduras localizadas",
        "titulo": "Fuerza de restricción 3%; ablandamiento en extremos ignorable si < ancho de sección",
        "texto": (
            "(e) Restricciones laterales efectivas — Los sistemas de "
            "arriostramiento para proveer restricción lateral se deben "
            "diseñar suponiendo que la fuerza lateral total ejercida por "
            "una aleta a compresión, bajo carga mayorada, distribuida "
            "entre los puntos de restricción en cualquier vano, es el 3% "
            "de la compresión en esa aleta.\n\n"
            "Cuando una serie de dos o más vigas paralelas requieren "
            "restricción lateral, no es adecuado simplemente amarrar las "
            "aletas a compresión juntas de modo que resulten mutuamente "
            "dependientes. La restricción es adecuada únicamente si se "
            "anclan los amarres a un soporte robusto independiente o si "
            "se provee un sistema de arriostramiento triangulado. Si el "
            "número de vigas paralelas es mayor de 3, es suficiente "
            "diseñar el sistema de restricción para resistir la suma de "
            "las tres mayores fuerzas compresivas únicamente.\n\n"
            "(f) Vigas que contienen soldaduras localizadas — El valor "
            "de MRS en el literal (c) de F.5.4.5.6 para una viga sujeta "
            "a ablandamiento en la zona afectada por el calor, debe "
            "generalmente referirse a la sección más desfavorable en el "
            "vano considerado aunque tal ablandamiento ocurra únicamente "
            "localmente a lo largo de la longitud.\n\n"
            "Sin embargo, cuando el ablandamiento en la zona afectada "
            "por el calor ocurre en los extremos únicamente, su "
            "presencia se puede ignorar para considerar el pandeo "
            "torsional lateral siempre y cuando tal ablandamiento no "
            "exceda una distancia a lo largo del miembro, en cada "
            "extremo del vano, mayor que el ancho de la sección."
        ),
    },
    {
        "id": "NSR10-F-F_5_4_5_tabla1_coeficientes_x_y",
        "seccion": "Tabla F.5.4.5-1 — Pandeo torsional lateral de vigas, coeficientes X y Y",
        "titulo": "3 secciones (I con pestaña interna, T doble simétrica, Z/canal), fórmulas X/Y en función de D/B, t2/t1, C/B",
        "texto": (
            "Tabla F.5.4.5-1 — Pandeo torsional lateral de vigas, "
            "coeficientes X y Y (válida para vigas en I o canal con "
            "pestañas de refuerzo simples):\n\n"
            "Sección 1 — Perfil en I con pestaña interna (dimensiones B "
            "ancho aleta, D altura, t1 espesor alma, t2 espesor aleta, "
            "sin dimensión C):\n"
            "X = 0.90 - 0.03(D/B) + 0.04(t2/t1)\n"
            "Y = 0.05 + 0.010{(D/B)[(t2/t1) - 1]}^(1/2)\n\n"
            "Sección 2 — Perfil doble T con pestañas internas simétricas "
            "arriba y abajo (dimensiones B, D, C = altura de la pestaña, "
            "t1=t2):\n"
            "X = 0.94 - (D/B)(0.03 - 0.07(C/B)) - 0.3(C/B)\n"
            "Y = 0.05 - 0.06(C/B)\n\n"
            "Sección 3 — Perfil en Z / canal con pestaña interna simple "
            "(dimensiones B, D, t1, t2):\n"
            "X = 0.95 - 0.03(D/B) + 0.06(t2/t1)\n"
            "Y = 0.07 + 0.014{(D/B)[(t2/t1) - 1]}^(1/2)\n\n"
            "Sección 4 — Perfil en canal con pestaña interna simple y "
            "dimensión C, simétrico (dimensiones B, D, C, t1=t2):\n"
            "X = 1.01 - (D/B)(0.03 - 0.06(C/B)) - 0.3(C/B)\n"
            "Y = 0.07 - 0.10(C/B)\n\n"
            "Nota: Las expresiones para X y Y son válidas para "
            "1.5 ≤ D/B ≤ 4.5, 1 ≤ t2/t1 ≤ 2, 0 ≤ C/B ≤ 0.5."
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

    print(f"\nOK: {len(rows)} chunks de F.5.4.5 cargados.")
    max_len = max(len(c["texto"]) for c in CHUNKS)
    print(f"Chunk más largo: {max_len} caracteres.")


if __name__ == "__main__":
    main()
