"""
Ingesta verbatim de Título A, Capítulo A.6 (Requisitos de la deriva)
-- NSR-10. Fase 4 del plan de cierre del Título A (2026-09-22),
auditoría real de numerales confirmó A.6 en 6/35 (faltan 29) -- límites
de deriva y separación sísmica entre edificaciones, citado por casi
todos los capítulos de análisis estructural (A.3, A.4, A.5, A.10).

Fuente: NSR-10-116-123.pdf, páginas PDF 1-7 (A-73 a A-79), leídas
visualmente con Read pages= sobre el PDF nativo -- nunca extracción
mecánica (pypdf), por el bug de corrupción de codificación ya
documentado en otros títulos. La Figura A.6.5-1 (diagrama de medición
de la separación sísmica) no se transcribe como imagen -- es un
gráfico; su contenido normativo (coeficientes por altura de piso) sí
está íntegro en la Tabla A.6.5-1, que se transcribe completa.

Uso: python _ingest_titulo_a_a6_verbatim.py
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
        "id": "NSR10-A-A_6_0_nomenclatura",
        "seccion": "A.6.0 — Nomenclatura del Capítulo A.6",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "CAPÍTULO A.6 — REQUISITOS DE LA DERIVA\n\n"
            "A.6.0 — NOMENCLATURA\n\n"
            "hi = altura en metros, medida desde la base, del nivel i.\n"
            "hn = altura en metros, medida desde la base, del piso más "
            "alto del edificio.\n"
            "hp^i = altura del piso i, medida desde la superficie del "
            "diafragma del piso i hasta la superficie del diafragma del "
            "piso inmediatamente inferior, i-1.\n"
            "j = índice de una de las direcciones ortogonales principales "
            "en planta, puede ser x o y.\n"
            "Pi = suma de la carga vertical total, incluyendo muerta y "
            "viva, que existe en el piso i, y todos los pisos localizados "
            "por encima. Para el cálculo de los efectos P-Delta, no hay "
            "necesidad que los coeficientes de carga sean mayores que la "
            "unidad.\n"
            "Qi = índice de estabilidad, del piso i, utilizado en la "
            "evaluación de los efectos P-Delta. Véase A.6.2.3.\n"
            "rj = proyección, sobre la dirección perpendicular en planta a "
            "la dirección bajo estudio, j, de la distancia entre el centro "
            "de masa del piso y el punto de interés.\n"
            "T = período fundamental del edificio como se determina en "
            "A.4.2.\n"
            "Ta = período de vibración fundamental aproximado. Véase "
            "A.4.2.\n"
            "Vi = fuerza cortante del piso i, en la dirección bajo "
            "estudio, sin dividir por R. Se determina por medio de las "
            "ecuaciones del numeral A.4.3. Corresponde a la suma de las "
            "fuerzas horizontales sísmicas que se aplican al nivel i, y "
            "todos los niveles localizados por encima de él.\n"
            "Δcm,j^i = deriva del piso i, en la dirección bajo estudio, j, "
            "medida en el centro de masa del piso, como la diferencia "
            "entre el desplazamiento horizontal del piso i menos el del "
            "piso i-1 en la misma dirección j.\n"
            "Δj^i = deriva del piso i en la dirección principal en planta "
            "j.\n"
            "Δmax^i = deriva máxima para cualquier punto del piso i.\n"
            "δcm,j^i = desplazamiento horizontal, del centro de masa del "
            "piso i, en la dirección j.\n"
            "δpd,j^i = desplazamiento horizontal adicional, del centro de "
            "masa del piso i, causado por efectos P-Delta, en la dirección "
            "j.\n"
            "δt,j^i = desplazamiento horizontal adicional causado por "
            "efectos de torsión de cualquier punto del diafragma del piso "
            "i en la dirección j.\n"
            "δtot,j^i = desplazamiento total horizontal, de cualquier "
            "punto del diafragma del piso i en la dirección j.\n"
            "θi = rotación alrededor de un eje vertical que pasa por el "
            "centro de masa del piso i, causada por los efectos "
            "torsionales, en radianes."
        ),
    },
    {
        "id": "NSR10-A-A_6_1_general",
        "seccion": "A.6.1 — General (alcance, definición y necesidad de controlar la deriva)",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "A.6.1 — GENERAL\n\n"
            "A.6.1.1 — ALCANCE — En el presente Capítulo se dan los "
            "procedimientos para calcular la deriva así como sus límites "
            "permisibles.\n\n"
            "A.6.1.2 — DEFINICIÓN DE DERIVA — Se entiende por deriva el "
            "desplazamiento horizontal relativo entre dos puntos "
            "colocados en la misma línea vertical, en dos pisos o niveles "
            "consecutivos de la edificación.\n\n"
            "A.6.1.3 — NECESIDAD DE CONTROLAR LA DERIVA — La deriva está "
            "asociada con los siguientes efectos durante un temblor:\n\n"
            "(a) Deformación inelástica de los elementos estructurales y "
            "no estructurales.\n"
            "(b) Estabilidad global de la estructura.\n"
            "(c) Daño a los elementos estructurales que no hacen parte del "
            "sistema de resistencia sísmica y a los elementos no "
            "estructurales, tales como muros divisorios, particiones, "
            "enchapes, acabados, instalaciones eléctricas, mecánicas, "
            "etc.\n"
            "(d) Alarma y pánico entre las personas que ocupen la "
            "edificación.\n\n"
            "Por las razones anteriores es fundamental llevar a cabo "
            "durante el diseño un estricto cumplimiento de los requisitos "
            "de deriva dados en el presente Capítulo, con el fin de "
            "garantizar el cumplimiento del propósito del Reglamento y un "
            "adecuado comportamiento de la estructura y su contenido."
        ),
    },
    {
        "id": "NSR10-A-A_6_2_1_a_2_2_desplazamientos_centro_masa_torsion",
        "seccion": "A.6.2.1 y A.6.2.2 — Desplazamientos en el centro de masa y causados por torsión",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "A.6.2 — CÁLCULO DEL DESPLAZAMIENTO HORIZONTAL\n\n"
            "A.6.2.1 — DESPLAZAMIENTOS HORIZONTALES EN EL CENTRO DE MASA "
            "DEL PISO, δcm,j — Corresponden a los desplazamientos "
            "horizontales, en las dos direcciones principales en planta, "
            "que tiene el centro de masa del piso. En caso de cálculo de "
            "desplazamientos haciendo uso del método de análisis dinámico "
            "deberá tomarse en cuenta lo indicado en A.5.4.4 para la "
            "combinación de los modos.\n\n"
            "A.6.2.1.1 — Cuando se utilice el método de la fuerza "
            "horizontal equivalente, las fuerzas horizontales que se "
            "empleen para determinar los desplazamientos horizontales y "
            "torsionales en el centro de masa pueden calcularse "
            "utilizando el período, T, que se obtiene por medio de la "
            "ecuación A.4.2-1, aplicando el límite de CuTa indicado allí, "
            "o alternativamente el período T obtenido por alguna de las "
            "ecuaciones A.4.2-3 o A.4.2-5.\n\n"
            "A.6.2.1.2 — En las edificaciones pertenecientes a los grupos "
            "de uso II, III y IV, para la determinación de las fuerzas "
            "horizontales que se empleen para calcular los "
            "desplazamientos horizontales en el centro de masa, se "
            "permite que el coeficiente de importancia I, tenga un valor "
            "igual a la unidad (I = 1.0), y las fuerzas de diseño a "
            "emplear para obtener la resistencia de la estructura deben "
            "utilizar el valor del coeficiente de importancia I "
            "correspondiente al grupo de uso de la edificación, tal como "
            "se define en A.2.5.2.\n\n"
            "A.6.2.2 — DESPLAZAMIENTOS HORIZONTALES CAUSADOS POR EFECTOS "
            "TORSIONALES, δt,j — Corresponden a los desplazamientos "
            "horizontales adicionales, en las dos direcciones principales "
            "ortogonales en planta, causados por la rotación de toda la "
            "estructura con respecto a un eje vertical y debida a los "
            "efectos torsionales definidos en A.3.6.7. Este efecto solo "
            "debe evaluarse cuando los diafragmas son rígidos. Cuando los "
            "diafragmas son rígidos el incremento en desplazamiento "
            "horizontal causado por los efectos torsionales en cualquiera "
            "de las dos direcciones principales en planta, se obtiene "
            "de:\n\n"
            "δt,j = rj·θi       (A.6.2-1)\n\n"
            "donde δt,j es el incremento en desplazamiento horizontal "
            "causado por los efectos torsionales en un punto dentro del "
            "nivel i, en una de las direcciones principales en planta, rj "
            "es la proyección sobre la dirección perpendicular en planta a "
            "la dirección bajo estudio, j, de la distancia entre el "
            "centro de masa del piso y el punto de interés, y θi es la "
            "rotación alrededor de un eje vertical que pasa por el centro "
            "de masa del nivel i, causada por los efectos torsionales."
        ),
    },
    {
        "id": "NSR10-A-A_6_2_3_a_2_4_p_delta_desplazamientos_totales",
        "seccion": "A.6.2.3 y A.6.2.4 — Efectos P-Delta y desplazamientos horizontales totales",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "A.6.2.3 — DESPLAZAMIENTOS HORIZONTALES CAUSADOS POR EFECTOS "
            "P-DELTA, δpd,j — Corresponden a los efectos adicionales, en "
            "las dos direcciones principales en planta, causados por los "
            "efectos de segundo orden (efectos P-Delta) de la estructura. "
            "Estos efectos deben tenerse en cuenta cuando el índice de "
            "estabilidad, Qi, es mayor de 0.10. El índice de estabilidad, "
            "para el piso i y en la dirección bajo estudio, se calcula "
            "por medio de la siguiente ecuación:\n\n"
            "Qi = Pi·Δcm / (Vi·hpi)       (A.6.2-2)\n\n"
            "El índice de estabilidad de cualquier piso, Qi, no debe "
            "exceder el valor de 0.30. Cuando el valor de Qi es mayor que "
            "0.30, la estructura es potencialmente inestable y debe "
            "rigidizarse, a menos que se cumplan, en estructuras de "
            "concreto reforzado, la totalidad de los requisitos "
            "enumerados en C.10.11.6.2(b).\n\n"
            "La deflexión adicional causada por el efecto P-Delta en la "
            "dirección bajo estudio y para el piso i, se calcula por "
            "medio de la siguiente ecuación:\n\n"
            "δpd = δcm·(Qi / (1-Qi))       (A.6.2-3)\n\n"
            "A.6.2.3.1 — Alternativamente, los efectos P-Delta pueden "
            "evaluarse siguiendo los requisitos de C.10.11 en estructuras "
            "de concreto reforzado.\n\n"
            "A.6.2.3.2 — Cuando el índice de estabilidad es mayor de "
            "0.10, los efectos P-Delta en las fuerzas internas de la "
            "estructura causadas por las cargas laterales deben "
            "aumentarse, multiplicándolas en cada piso por el factor "
            "1/(1-Qi).\n\n"
            "A.6.2.4 — DESPLAZAMIENTOS HORIZONTALES TOTALES — Los "
            "desplazamientos horizontales, en las dos direcciones "
            "principales ortogonales en planta, que tienen todos los "
            "grados de libertad de la estructura al verse afectada por "
            "los movimientos sísmicos de diseño definidos en A.2.2, se "
            "determinan por medio del análisis estructural realizado "
            "utilizando el método de análisis definido en A.3.4 y con las "
            "rigideces indicadas en A.3.4.3. Los desplazamientos totales "
            "horizontales, δt0t,j, en cualquiera de las direcciones "
            "principales en planta, j, y para cualquier grado de libertad "
            "de la estructura, se obtienen de la siguiente suma de "
            "valores absolutos:\n\n"
            "δt0t,j = |δcm,j| + |δt,j| + |δpd,j|       (A.6.2-4)\n\n"
            "donde δcm,j corresponde al desplazamiento horizontal del "
            "centro de masa en la dirección bajo estudio, j; δt,j el "
            "desplazamiento adicional causado por los efectos "
            "torsionales en la dirección bajo estudio cuando el "
            "diafragma sea rígido, j, y δpd,j al desplazamiento adicional "
            "causado por el efecto P-Delta en la dirección bajo estudio, "
            "j. Cuando se utilicen los procedimientos de interacción "
            "suelo-estructura, o cuando A.3.4.2 así lo requiera porque se "
            "realizó el análisis de la estructura suponiéndola empotrada "
            "en su base, los desplazamientos adicionales obtenidos de "
            "acuerdo con el procedimiento del Capítulo A.7."
        ),
    },
    {
        "id": "NSR10-A-A_6_3_evaluacion_deriva_maxima",
        "seccion": "A.6.3 — Evaluación de la deriva máxima",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "A.6.3 — EVALUACIÓN DE LA DERIVA MÁXIMA\n\n"
            "A.6.3.1 — DERIVA MÁXIMA — La deriva máxima para cualquier "
            "piso debe obtenerse así:\n\n"
            "A.6.3.1.1 — En edificaciones regulares e irregulares que no "
            "tengan irregularidades en planta de los tipos 1aP ó 1bP "
            "(véase la tabla A.3-6), o edificaciones con diafragma "
            "flexible, la deriva máxima para el piso i, Δmax^i, "
            "corresponde a la mayor deriva de las dos direcciones "
            "principales en planta, j, calculada como el valor absoluto "
            "de la diferencia algebraica de los desplazamientos "
            "horizontales del centro de masa del diafragma del piso i, "
            "δcm,j, en la dirección principal en planta bajo estudio con "
            "respecto a los del diafragma del piso inmediatamente "
            "inferior (i-1), incluyendo los efectos P-Delta.\n\n"
            "A.6.3.1.2 — En edificaciones que tengan irregularidades en "
            "planta de los tipos 1aP ó 1bP (véase la tabla A.3-6) la "
            "deriva máxima en cualquier punto del piso i, se puede "
            "obtener como la diferencia entre los desplazamientos "
            "horizontales totales máximos, de acuerdo con A.6.2.4, del "
            "punto en el piso i y los desplazamientos horizontales "
            "totales máximos de un punto localizado en el mismo eje "
            "vertical en el piso inmediatamente inferior (i-1), por medio "
            "de la siguiente ecuación:\n\n"
            "Δmax^i = raíz[ Σ(j=1,2) (δtot,j^i - δtot,j^(i-1))² ]      "
            "(A.6.3-1)\n\n"
            "Alternativamente se pueden usar procedimientos para estimar "
            "respuestas máximas de cantidades vectoriales. El cumplimiento "
            "del cálculo de la deriva para cualquier punto del piso se "
            "puede realizar verificándola solamente en todos los ejes "
            "verticales de columna y en los puntos localizados en los "
            "bordes de los muros estructurales. La máxima deriva del piso "
            "i, Δmax^i, corresponde a la máxima deriva que se obtenga de "
            "todos los puntos así estudiados dentro del mismo piso i.\n\n"
            "A.6.3.1.3 — En los pisos superiores de edificaciones que "
            "cumplen las condiciones (a) a (e) presentadas a continuación, "
            "se permite calcular la deriva máxima del piso de la forma "
            "alternativa que se obtiene con la expresión A.6.3-2 indicada "
            "en esta sección.\n\n"
            "(a) La edificación tiene diez o más pisos de altura sobre su "
            "base.\n"
            "(b) El procedimiento alternativo solo es aplicable en los "
            "pisos superiores localizados por encima de dos tercios de la "
            "altura de la edificación medida desde la base.\n"
            "(c) El sistema estructural de resistencia sísmica es "
            "diferente a pórtico resistente a momento.\n"
            "(d) La edificación se clasifica como regular tanto en planta "
            "como en altura de acuerdo con los requisitos del Capítulo "
            "A.3.\n"
            "(e) El índice de estabilidad, Qi, es menor de 0.10 en todos "
            "los pisos donde sería aplicable este procedimiento "
            "alternativo.\n\n"
            "La máxima deriva del piso i, Δmax^i, en el procedimiento "
            "alternativo corresponde a la máxima deriva de las dos "
            "direcciones principales en planta, j, calculada por medio de "
            "la siguiente ecuación:\n\n"
            "Δj^i = δcm,j^(i-1) - 0.5·[(δcm,j^(i-1)-δcm,j^(i-2))·"
            "(hp^i+hp^(i-1))/hp^(i-1) + δcm,j^(i-2)] - 0.5·δcm,j^(i-1)  "
            "(A.6.3-2)"
        ),
    },
    {
        "id": "NSR10-A-A_6_4_limites_deriva",
        "seccion": "A.6.4 — Límites de la deriva (Tabla A.6.4-1)",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "A.6.4 — LÍMITES DE LA DERIVA\n\n"
            "A.6.4.1 — La deriva máxima para cualquier piso determinada "
            "de acuerdo con el procedimiento de A.6.3.1, no puede exceder "
            "los límites establecidos en la tabla A.6.4-1, en la cual la "
            "deriva máxima se expresa como un porcentaje de la altura de "
            "piso hpi:\n\n"
            "Tabla A.6.4-1 — Derivas máximas como porcentaje de hpi:\n"
            "- Estructuras de concreto reforzado, metálicas, de madera, y "
            "de mampostería que cumplen los requisitos de A.6.4.2.2: "
            "1.0% (Δmax^i ≤ 0.010 hpi).\n"
            "- Estructuras de mampostería que cumplen los requisitos de "
            "A.6.4.2.3: 0.5% (Δmax^i ≤ 0.005 hpi).\n\n"
            "A.6.4.1.1 — Cuando se utilicen secciones fisuradas, tanto en "
            "concreto reforzado, como en mampostería y en el caso de "
            "estructuras mixtas con acero, las derivas pueden "
            "multiplicarse por 0.7 antes de hacer la comparación con los "
            "límites dados en la tabla A.6.4-1.\n\n"
            "A.6.4.1.2 — Cuando se haya efectuado un análisis inelástico "
            "verificando el desempeño de la totalidad de los elementos "
            "estructurales en un rango de desempeño no mayor a "
            "\"Protección de la Vida\" (LS según los requerimientos del "
            "ASCE 31 y ASCE 41), las derivas pueden multiplicarse por 0.7 "
            "antes de hacer la comparación con los límites dados en la "
            "tabla A.6.4-1.\n\n"
            "A.6.4.1.3 — Se permite emplear el límite de deriva máxima "
            "permisible de 0.010 hpi en edificaciones construidas con "
            "mampostería estructural cuando éstas estén compuestas por "
            "muros cuyo modo prevalente de falla sea la flexión ante "
            "fuerzas paralelas al plano del muro, diseñados esencialmente "
            "como elementos verticales esbeltos que actúan como voladizos "
            "apoyados en su base o cimentación, y que se construyen de "
            "tal manera que la transferencia de momento entre muros a "
            "través de los elementos horizontales de acople en los "
            "diafragmas de entrepiso, ya sean losas, vigas de enlace, "
            "antepechos o dinteles, sea despreciable.\n\n"
            "A.6.4.1.4 — Cuando se trate de muros de mampostería "
            "estructural poco esbeltos o cuyo modo prevaleciente de falla "
            "sea causado por esfuerzos cortantes, debe emplearse el "
            "límite de deriva máxima permisible de 0.005 hpi.\n\n"
            "A.6.4.1.5 — No hay límites de deriva en edificaciones de un "
            "piso, siempre que los muros y las particiones interiores y "
            "exteriores así como los cielorrasos se diseñen para acomodar "
            "las derivas del piso."
        ),
    },
    {
        "id": "NSR10-A-A_6_5_1_a_5_2_1_separacion_misma_construccion_alcance",
        "seccion": "A.6.5.1 y A.6.5.2.1 — Separación dentro de la misma construcción y alcance con edificaciones vecinas",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "A.6.5 — SEPARACIÓN ENTRE ESTRUCTURAS ADYACENTES POR "
            "CONSIDERACIONES SÍSMICAS\n\n"
            "A.6.5.1 — DENTRO DE LA MISMA CONSTRUCCIÓN — Todas las partes "
            "de la estructura deben diseñarse y construirse para que "
            "actúen como una unidad integral para efectos de resistir las "
            "fuerzas sísmicas, a menos que se separen una distancia "
            "suficiente para evitar la colisión nociva entre las partes. "
            "Para determinar la distancia mínima de separación debe "
            "sumarse el valor absoluto de los desplazamientos horizontales "
            "totales obtenidos en A.6.2.1 para cada una de las porciones "
            "de la edificación en la dirección perpendicular a la junta "
            "que las separe, a menos que se tomen medidas para que no se "
            "presente daño a la estructura al utilizar una distancia "
            "menor.\n\n"
            "A.6.5.2 — ENTRE EDIFICACIONES VECINAS QUE NO HAGAN PARTE DE "
            "LA MISMA CONSTRUCCIÓN — La separación entre edificaciones "
            "vecinas, para evitar efectos nocivos ante la ocurrencia de "
            "un sismo, debe cumplir los siguientes requisitos:\n\n"
            "A.6.5.2.1 — Alcance — La presente reglamentación es "
            "aplicable en los siguientes casos:\n\n"
            "(a) En municipios localizados en Zonas de Amenaza Sísmica "
            "Baja según lo dispone el presente Reglamento en su Capítulo "
            "A.2 no se requieren consideraciones de separación sísmica "
            "entre edificaciones vecinas.\n"
            "(b) Solo aplica para la obtención de licencias de "
            "construcción de edificaciones nuevas que se soliciten por "
            "primera vez con posterioridad a la adopción del presente "
            "Reglamento.\n"
            "(c) No aplica para el caso de edificaciones que sean objeto "
            "del trámite de Reconocimiento.\n"
            "(d) Para el caso de rehabilitaciones sísmicas de "
            "edificaciones existentes aplican los requisitos especiales "
            "que se indican en A.10.7.\n"
            "(e) Los requisitos de esta sección del Reglamento pueden ser "
            "modificados por la administración municipal o distrital, "
            "siempre y cuando los requisitos de la separación sísmica que "
            "resulten de la aplicación de la reglamentación municipal o "
            "distrital no sean menores que los dados aquí."
        ),
    },
    {
        "id": "NSR10-A-A_6_5_2_2_a_5_2_3_definiciones_requisitos_separacion",
        "seccion": "A.6.5.2.2 y A.6.5.2.3 — Definiciones y requisitos de separación sísmica respecto al paramento del lote",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "A.6.5.2.2 — Definiciones — En el Capítulo A.13 deben "
            "consultarse las siguientes definiciones: altura del piso, "
            "altura de la edificación en la colindancia, cerramiento, "
            "coincidencia de las losas de entrepiso en la colindancia, "
            "nivel (medido desde la base) de un piso en la colindancia, "
            "número de pisos aéreos de la edificación, número de pisos "
            "aéreos en la colindancia, y separación sísmica en la "
            "colindancia. Además debe tenerse en cuenta cuando el terreno "
            "es inclinado en la colindancia, o haya diferentes alturas de "
            "piso en la colindancia, o exista un número diferente de "
            "pisos aéreos en la colindancia, que debe utilizarse la altura "
            "de piso, o el número de pisos aéreos que conduzca a la mayor "
            "separación sísmica.\n\n"
            "A.6.5.2.3 — Requisitos de separación sísmica con respecto al "
            "paramento del lote para edificaciones nuevas — Deben "
            "cumplirse los siguientes requisitos para efectos de "
            "determinar la separación sísmica con respecto al paramento "
            "del lote en edificaciones nuevas cubiertas por el alcance "
            "dado en A.6.5.2.1:\n\n"
            "(a) Cuando el paramento del lote sea colindante con vía "
            "pública o zona verde pública no requiere separación sísmica "
            "con respecto al paramento en ese costado o costados. Ello no "
            "exime cumplir los requisitos urbanísticos de las normas "
            "municipales para la edificación en lo referente a "
            "retrocesos.\n"
            "(b) Cuando en la colindancia haya un cerramiento, y la "
            "edificación nueva esté separada de este cerramiento en una "
            "distancia que supera la señalada para el piso crítico en la "
            "Tabla A.6.5-1 no se requiere separación sísmica del "
            "cerramiento de la edificación nueva con respecto al paramento "
            "del lote.\n"
            "(c) Las edificaciones con uno o dos pisos aéreos en la "
            "colindancia no requieren separación sísmica (véase también la "
            "Tabla A.6.5-1).\n"
            "(d) Las edificaciones de más de dos pisos aéreos en la "
            "colindancia deben separarse del paramento en la colindancia "
            "así (véase también la Tabla A.6.5-1 y Figura A.6.5-1):\n\n"
            "(i) Edificaciones hasta de tres pisos aéreos en la "
            "colindancia — No se requiere separación sísmica de la "
            "edificación nueva con respecto al paramento cuando no haya "
            "edificación vecina existente, o cuando las losas de la "
            "edificación nueva coincidan en la colindancia (véanse las "
            "definiciones) con las de la edificación existente en la "
            "misma colindancia. Si las losas de entrepiso de la "
            "edificación nueva no coinciden con las de la edificación "
            "existente se requiere una separación sísmica de la "
            "edificación nueva con respecto al paramento igual al 1% (uno "
            "por ciento) de la altura de la edificación nueva en la "
            "colindancia.\n\n"
            "(ii) Edificaciones de más de tres pisos aéreos en la "
            "colindancia — Cuando las losas de la edificación nueva "
            "coinciden en la colindancia (véanse las definiciones) con "
            "las de la edificación vecina existente en la misma "
            "colindancia la edificación nueva debe retirarse del "
            "paramento en la colindancia una distancia de separación "
            "sísmica igual al 2% (dos por ciento) de la altura de la "
            "edificación nueva en la colindancia. Cuando las losas de "
            "entrepiso de la edificación nueva no coinciden con las de la "
            "edificación existente en la colindancia, esta separación "
            "sísmica debe ser del 3% (tres por ciento) de la altura de la "
            "edificación nueva en la colindancia. Si no existe edificación "
            "vecina en la colindancia (cubre además el caso de que sea "
            "solo un cerramiento), esta separación sísmica debe ser del 1% "
            "(uno por ciento) de la altura de la edificación nueva en la "
            "colindancia."
        ),
    },
    {
        "id": "NSR10-A-A_6_5_2_3_tabla_y_cierre",
        "seccion": "A.6.5.2.3 (cont.) — Tabla A.6.5-1 y disposiciones finales de separación sísmica",
        "titulo": "NSR-10 Título A — Capítulo A.6 — Requisitos de la deriva",
        "texto": (
            "Tabla A.6.5-1 — Separación sísmica mínima en la cubierta "
            "entre edificaciones colindantes que no hagan parte de la "
            "misma construcción (por altura de la edificación nueva y "
            "tipo de colindancia):\n\n"
            "1 y 2 pisos: no requiere separación en ningún caso (coincidan "
            "o no las losas de entrepiso, exista o no edificación "
            "vecina).\n\n"
            "3 pisos: si coinciden las losas de entrepiso con edificación "
            "vecina existente que no ha dejado la separación sísmica "
            "requerida, no requiere separación; si no coinciden las "
            "losas, 0.01 veces la altura de la edificación nueva (1% de "
            "hn); si no existe edificación vecina o la que existe ya dejó "
            "la separación requerida, no requiere separación.\n\n"
            "Más de 3 pisos: si coinciden las losas de entrepiso con "
            "edificación vecina existente que no ha dejado la separación "
            "requerida, 0.02 veces la altura de la edificación nueva (2% "
            "de hn); si no coinciden las losas, 0.03 veces la altura (3% "
            "de hn); si no existe edificación vecina o la que existe ya "
            "dejó la separación requerida, 0.01 veces la altura (1% de "
            "hn).\n\n"
            "Notas de la Tabla A.6.5-1: (1) Para obtener la separación "
            "sísmica en pisos diferentes a la cubierta se aplicará el "
            "coeficiente indicado en la Tabla multiplicado por la altura "
            "sobre el terreno del piso en particular. (2) Cuando el "
            "terreno en la colindancia sea inclinado en el sentido del "
            "paramento, o haya diferentes alturas de piso o diferentes "
            "números de pisos aéreos en la colindancia, se tomará en la "
            "edificación nueva la altura de piso, o el número de pisos "
            "aéreos que conduzca a la mayor separación sísmica.\n\n"
            "Figura A.6.5-1 — Medición de la separación sísmica (vista en "
            "elevación): la separación sísmica para cualquier piso es "
            "como mínimo la distancia que se obtiene al multiplicar el "
            "coeficiente indicado en la Tabla A.6.5-1 por la altura hi "
            "correspondiente a ese piso, medida desde el nivel del "
            "terreno hasta la superficie del diafragma del piso aéreo en "
            "estudio.\n\n"
            "(e) Cuando se requiera separación sísmica, la separación en "
            "cualquier piso en particular corresponde a la distancia "
            "horizontal en dirección perpendicular al plano vertical "
            "levantado sobre el lindero entre los dos lotes de terreno, "
            "medida desde la losa de entrepiso de la edificación hasta "
            "este plano, calculada utilizando la altura sobre el nivel "
            "del terreno del piso en particular multiplicada por el "
            "coeficiente que indique la Tabla A.6.5-1 para ese caso. "
            "Véase también la Figura A.6.5-1.\n\n"
            "(f) Deben tomarse precauciones para que no se depositen "
            "materiales extraños dentro de la separación sísmica entre "
            "edificaciones. Así mismo debe colocarse un protección de "
            "humedad apropiada para que el agua lluvia no entre dentro de "
            "la abertura de la separación sísmica.\n\n"
            "(g) Para el caso de edificaciones objeto de reforzamiento y "
            "rehabilitación sísmica el ingeniero diseñador de la "
            "rehabilitación debe dejar constancia de que estudió el "
            "potencial efecto nocivo de la interacción con las "
            "edificaciones vecinas colindantes y que tomó las medidas "
            "apropiadas según su mejor criterio dentro de lo requerido en "
            "A.10.1.7.\n\n"
            "(h) El paramento del lote y la separación sísmica requerida "
            "deben quedar claramente indicados en los planos "
            "arquitectónicos que se presentan a la autoridad competente o "
            "curaduría para la obtención de la licencia de construcción."
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
