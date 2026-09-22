"""
Ingesta verbatim de Título A, Capítulo A.1 (Introducción -- alcance de
las disposiciones) -- NSR-10. Fase 3 del plan de cierre del Título A
(2026-09-22), auditoría real de numerales confirmó A.1 con 68
faltantes de un capítulo corto (11 páginas, A-1 a A-11) -- introductorio
pero citado por casi todos los demás capítulos (A.1.2.3 Alcance,
A.1.3 procedimiento de diseño con la Tabla A.1.3-1, A.1.6 obligatoriedad
de normas NTC).

Fuente: NSR-10-43-54.pdf, páginas 2-12 (A-1 a A-11). Leídas visualmente
con Read pages= sobre el PDF nativo -- nunca extracción mecánica
(pypdf), por el bug de corrupción de codificación ya documentado en
otros títulos.

Uso: python _ingest_titulo_a_a1_verbatim.py
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
        "id": "NSR10-A-A_1_1_normas_sismo_resistentes",
        "seccion": "A.1.1 — Normas sismo resistentes colombianas",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.1 — NORMAS SISMO RESISTENTES COLOMBIANAS\n\n"
            "A.1.1.1 — El diseño, construcción y supervisión técnica de "
            "edificaciones en el territorio de la República de Colombia debe "
            "someterse a los criterios y requisitos mínimos que se establecen "
            "en las Normas Sismo Resistentes Colombianas, las cuales "
            "comprenden:\n\n"
            "(a) La Ley 400 de 1997,\n"
            "(b) La Ley 1229 de 2008,\n"
            "(c) El presente Reglamento Colombiano de Construcciones Sismo "
            "Resistentes, NSR-10, y\n"
            "(d) Las resoluciones expedidas por la \"Comisión Asesora "
            "Permanente del Régimen de Construcciones Sismo Resistentes\" del "
            "Gobierno Nacional, adscrita al Ministerio de Ambiente, Vivienda y "
            "Desarrollo Territorial, y creada por el Artículo 39 de la Ley 400 "
            "de 1997."
        ),
    },
    {
        "id": "NSR10-A-A_1_2_1_a_2_2_temario_y_objeto",
        "seccion": "A.1.2.1 y A.1.2.2 — Temario y Objeto del Reglamento",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.2 — ORGANIZACIÓN DEL PRESENTE REGLAMENTO\n\n"
            "A.1.2.1 — TEMARIO — El presente Reglamento Colombiano de "
            "Construcciones Sismo Resistentes, NSR-10, está dividido "
            "temáticamente en los siguientes Títulos, de acuerdo con lo "
            "prescrito en el Artículo 47 de la Ley 400 de 1997, así:\n\n"
            "TÍTULO A — Requisitos generales de diseño y construcción sismo "
            "resistente\n"
            "TÍTULO B — Cargas\n"
            "TÍTULO C — Concreto estructural\n"
            "TÍTULO D — Mampostería estructural\n"
            "TÍTULO E — Casas de uno y dos pisos\n"
            "TÍTULO F — Estructuras metálicas\n"
            "TÍTULO G — Estructuras de madera y Estructuras de guadua\n"
            "TÍTULO H — Estudios geotécnicos\n"
            "TÍTULO I — Supervisión técnica\n"
            "TÍTULO J — Requisitos de protección contra el fuego en "
            "edificaciones\n"
            "TÍTULO K — Otros requisitos complementarios\n\n"
            "A.1.2.2 — OBJETO — El presente Reglamento de Construcciones "
            "Sismo Resistentes, NSR-10, tiene por objeto:\n\n"
            "A.1.2.2.1 — Reducir a un mínimo el riesgo de la pérdida de "
            "vidas humanas, y defender en lo posible el patrimonio del "
            "Estado y de los ciudadanos.\n\n"
            "A.1.2.2.2 — Una edificación diseñada siguiendo los requisitos "
            "de este Reglamento, debe ser capaz de resistir, además de las "
            "fuerzas que le impone su uso, temblores de poca intensidad sin "
            "daño, temblores moderados sin daño estructural, pero "
            "posiblemente con algún daño a los elementos no estructurales y "
            "un temblor fuerte con daños a elementos estructurales y no "
            "estructurales pero sin colapso.\n\n"
            "A.1.2.2.3 — Además de la defensa de la vida, con el "
            "cumplimiento de los niveles prescritos por el presente "
            "Reglamento para los movimientos sísmicos de diseño, los "
            "cuales corresponden a requisitos mínimos establecidos para el "
            "diseño de elementos estructurales y elementos no "
            "estructurales, se permite proteger en alguna medida el "
            "patrimonio.\n\n"
            "A.1.2.2.4 — Los movimientos sísmicos de diseño prescritos en "
            "el presente Reglamento corresponden a los que afectarían las "
            "edificaciones de presentarse un sismo fuerte. Ante la "
            "ocurrencia, en el territorio nacional, de un sismo fuerte que "
            "induzca movimientos de características similares a los "
            "movimientos sísmicos de diseño prescritos en el presente "
            "Reglamento deben esperarse, en las edificaciones construidas "
            "cumpliendo con el Reglamento, daños estructurales y no "
            "estructurales reparables, aunque en algunos casos pueda que "
            "no sea económicamente factible su reparación.\n\n"
            "A.1.2.2.5 — Para las edificaciones indispensables y de "
            "atención a la comunidad como las define el Capítulo A.2 del "
            "presente Reglamento, se espera que el daño producido por "
            "movimientos sísmicos de características similares a los "
            "movimientos sísmicos de diseño prescritos en él sea reparable "
            "y no sea tan severo que inhiba la operación y ocupación "
            "inmediata y continuada de la edificación."
        ),
    },
    {
        "id": "NSR10-A-A_1_2_3_alcance",
        "seccion": "A.1.2.3 — Alcance del Reglamento",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.2.3 — ALCANCE — El presente Reglamento de Construcciones "
            "Sismo Resistentes, NSR-10, contiene:\n\n"
            "A.1.2.3.1 — Los requisitos mínimos para el diseño y "
            "construcción de edificaciones nuevas, con el fin de que sean "
            "capaces de resistir las fuerzas que les impone la naturaleza "
            "o su uso y para incrementar su resistencia a los efectos "
            "producidos por los movimientos sísmicos. Además establece, en "
            "el Título E, requisitos simplificados de diseño y "
            "construcción para casas de uno y dos pisos que pertenezcan al "
            "grupo de uso I tal como lo define A.2.5.1.4.\n\n"
            "A.1.2.3.2 — Para edificaciones construidas antes de la "
            "vigencia del presente Reglamento, el Capítulo A.10 establece "
            "los requisitos a emplear en la evaluación, adición, "
            "modificación y remodelación del sistema estructural; el "
            "análisis de vulnerabilidad, el diseño de las intervenciones "
            "de reforzamiento y rehabilitación sísmica, y la reparación de "
            "edificaciones con posterioridad a la ocurrencia de un sismo.\n\n"
            "A.1.2.3.3 — En el Capítulo A.12 se establecen requisitos "
            "especiales para el diseño y construcción sismo resistente de "
            "edificaciones indispensables pertenecientes al grupo de uso "
            "IV tal como lo define A.2.5.1.1 y las incluidas en los "
            "literales (a), (b), (c) y (d) del grupo de uso III, tal como "
            "lo define A.2.5.1.2, esenciales para la recuperación de la "
            "comunidad con posterioridad a la ocurrencia de una "
            "emergencia, incluyendo un sismo. En relación con las "
            "edificaciones incluidas en los literales (e) y (f) del grupo "
            "de uso III, como lo define A.2.5.1.2, queda a decisión del "
            "propietario en el primer caso o de la autoridad competente en "
            "el segundo definir si se requiere adelantar el diseño de "
            "ellas según los requisitos especiales del Capítulo A.12."
        ),
    },
    {
        "id": "NSR10-A-A_1_2_4_excepciones",
        "seccion": "A.1.2.4 — Excepciones al alcance del Reglamento",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.2.4 — EXCEPCIONES — El presente Reglamento de "
            "Construcciones Sismo Resistentes, NSR-10, es aplicable a "
            "edificaciones (construcciones cuyo uso primordial es la "
            "habitación u ocupación por seres humanos) y no se aplica a:\n\n"
            "A.1.2.4.1 — El diseño y construcción de estructuras "
            "especiales tales como puentes, torres de transmisión, torres "
            "y equipos industriales, muelles, estructuras hidráulicas y "
            "todas aquellas construcciones diferentes de edificaciones.\n\n"
            "A.1.2.4.2 — Estructuras cuyo comportamiento dinámico y "
            "respuesta ante los movimientos sísmicos de diseño difiera del "
            "de edificaciones convencionales. Cuando el uso de estas "
            "estructuras es la habitación u ocupación por seres humanos, "
            "su diseño y construcción debe someterse a lo prescrito en el "
            "Capítulo II, Artículos 8° a 14° de la Ley 400 de 1997.\n\n"
            "A.1.2.4.3 — Estructuras que no estén cubiertas dentro de las "
            "limitaciones de cada uno de los materiales estructurales "
            "prescritos dentro de este Reglamento. Cuando el uso de estas "
            "estructuras es la habitación u ocupación por seres humanos, "
            "su diseño y construcción debe someterse a lo prescrito en el "
            "Capítulo II, Artículos 8° a 14° de la Ley 400 de 1997.\n\n"
            "A.1.2.4.4 — Para el diseño sismo resistente de algunas "
            "estructuras que se salen del alcance del Reglamento, puede "
            "consultarse el Apéndice A-1, el cual no tiene carácter "
            "obligatorio."
        ),
    },
    {
        "id": "NSR10-A-A_1_2_5_definiciones",
        "seccion": "A.1.2.5 — Definiciones",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.2.5 — DEFINICIONES — En el Capítulo A.13 del presente "
            "Reglamento de Construcciones Sismo Resistentes se dan las "
            "definiciones de los términos empleados en el presente Título "
            "A del Reglamento."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_1_a_3_general_estudios_diseno",
        "seccion": "A.1.3.1 a A.1.3.3 — General, estudios geotécnicos y diseño arquitectónico",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.3 — PROCEDIMIENTO DE DISEÑO Y CONSTRUCCIÓN DE "
            "EDIFICACIONES, DE ACUERDO CON EL REGLAMENTO\n\n"
            "A.1.3.1 — GENERAL — El diseño y construcción de una "
            "edificación sometida a este Reglamento debe llevarse a cabo "
            "como se indica a continuación. Las diferentes etapas de los "
            "estudios, construcción y supervisión técnica, se amplían en "
            "las secciones pertinentes del Reglamento.\n\n"
            "A.1.3.2 — ESTUDIOS GEOTÉCNICOS — Debe realizarse una "
            "exploración del subsuelo en el lugar en que se va a construir "
            "la edificación, complementada con una consideración de sus "
            "alrededores para detectar, de ser el caso, movimientos de "
            "suelo. El alcance de la exploración y el programa de ensayos "
            "de laboratorio se establecen en el Título H — Estudios "
            "Geotécnicos. El ingeniero geotecnista debe elaborar un "
            "informe en el cual relacione la exploración y los resultados "
            "obtenidos en el laboratorio, se den las recomendaciones que "
            "debe seguir el ingeniero estructural en el diseño de la "
            "cimentación y obras de contención, la definición de los "
            "efectos sísmicos locales, los procedimientos constructivos "
            "que debe emplear el constructor, y los aspectos especiales a "
            "ser tenidos en cuenta por el supervisor técnico. En el "
            "reporte se deben indicar los asentamientos esperados, su "
            "variabilidad en el tiempo y las medidas que deben tomarse "
            "para no afectar adversamente las construcciones vecinas. El "
            "reporte debe ir firmado, o rotulado, por un ingeniero civil "
            "facultado para este fin de acuerdo con la Ley 400 de 1997.\n\n"
            "A.1.3.3 — DISEÑO ARQUITECTÓNICO — El proyecto arquitectónico "
            "de la edificación debe cumplir la reglamentación urbana "
            "vigente, los requisitos especificados en el Título J y en el "
            "Título K y además debe indicar, para efectos de este "
            "Reglamento, los usos de cada una de las partes de la "
            "edificación y su clasificación dentro de los grupos de uso "
            "definidos en el Capítulo A.2, el tipo de cada uno de los "
            "elementos no estructurales y el grado de desempeño mínimo que "
            "deben tener de acuerdo con los requisitos del Capítulo A.9. "
            "El proyecto arquitectónico debe ir firmado por un arquitecto "
            "con matrícula profesional vigente. Cuando los planos "
            "arquitectónicos incluyan los diseños sísmicos de los "
            "elementos no estructurales, éstos deben ir firmados, o "
            "rotulados, por un profesional facultado para este fin de "
            "acuerdo con la Ley 400 de 1997. Véase A.1.3.6."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_4_diseno_estructural_intro",
        "seccion": "A.1.3.4 — Diseño estructural (introducción)",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.3.4 — DISEÑO ESTRUCTURAL — El diseño estructural debe ser "
            "realizado por un ingeniero civil facultado para este fin, de "
            "acuerdo con la Ley 400 de 1997. La estructura de la "
            "edificación debe diseñarse para que tenga resistencia y "
            "rigidez adecuada ante las cargas mínimas de diseño prescritas "
            "por el Reglamento y debe, además, verificarse que dispone de "
            "rigidez adecuada para limitar la deformabilidad ante las "
            "cargas de servicio, de tal manera que no se vea afectado el "
            "funcionamiento de la edificación. A continuación en la tabla "
            "A.1.3-1 se especifican las etapas que deben llevarse a cabo, "
            "dentro del alcance de este Reglamento, en el diseño "
            "estructural de edificaciones nuevas y existentes, diferentes "
            "a las cubiertas en A.1.3.11. En la tabla A.1.3-1 se ha "
            "seguido el orden del procedimiento de diseño de edificaciones "
            "nuevas, el cual no necesariamente coincide con el de "
            "edificaciones existentes, pues este último se debe ajustar a "
            "la secuencia prescrita en el Capítulo A.10 y lo indicado en "
            "la tabla A.1.3-1 tiene simplemente carácter informativo para "
            "las edificaciones existentes."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_4_tabla_pasos_1_a_4",
        "seccion": "Tabla A.1.3-1 — Procedimiento de diseño estructural (Pasos 1 a 4)",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "Tabla A.1.3-1 — Procedimiento de diseño estructural para "
            "edificaciones nuevas y existentes (columnas: Diseño de "
            "edificaciones nuevas | Intervención de edificaciones "
            "existentes):\n\n"
            "Paso 1 — Predimensionamiento y coordinación con los otros "
            "profesionales. Nuevas: definición del sistema estructural, "
            "dimensiones tentativas para evaluar preliminarmente las "
            "diferentes solicitaciones tales como la masa de la "
            "estructura, las cargas muertas, las cargas vivas, los "
            "efectos sísmicos, y las fuerzas de viento. Estas dimensiones "
            "preliminares se coordinan con los otros profesionales que "
            "participan en el diseño. Existentes: además de la "
            "coordinación con otros profesionales respecto al proyecto, "
            "debe establecerse si la intervención está comprendida dentro "
            "del alcance dado en A.10.1.3. Si está cubierto, se deben "
            "realizar las etapas 1 y 2 de A.10.1.4 y con esa información "
            "se debe realizar la etapa 3 de ese numeral.\n\n"
            "Paso 2 — Evaluación de las solicitaciones definitivas. "
            "Nuevas: con las dimensiones de los elementos de la "
            "estructura definidos como resultado del paso 1, se evalúan "
            "todas las solicitaciones que pueden afectar la edificación "
            "de acuerdo con los requisitos del Título B del Reglamento. "
            "Estas incluyen: el efecto gravitacional de la masa de los "
            "elementos estructurales, o peso propio, las cargas de "
            "acabados y elementos no estructurales, las cargas muertas, "
            "las fuerzas de viento, las deformaciones impuestas por "
            "efectos reológicos de los materiales estructurales y "
            "asentamientos del suelo que da apoyo a la fundación. Así "
            "mismo se debe determinar la masa de la edificación y su "
            "contenido cuando así lo exige el Reglamento, la cual será "
            "empleada en la determinación de los efectos sísmicos, de "
            "acuerdo con los pasos siguientes. Existentes: se debe "
            "realizar la etapa 4 de A.10.1.4 donde, entre otros aspectos, "
            "se debe determinar una información real análoga a la exigida "
            "para edificaciones nuevas, pero con base en la edificación "
            "existente de acuerdo con lo indicado en A.10.4.2.6.\n\n"
            "Paso 3 — Obtención del nivel de amenaza sísmica y los "
            "valores de Aa y Av. Nuevas: este paso consiste en localizar "
            "el lugar donde se construirá la edificación dentro de los "
            "mapas de zonificación sísmica dados en el Capítulo A.2 del "
            "Reglamento y en determinar el nivel de amenaza sísmica del "
            "lugar, de acuerdo con los valores de los parámetros Aa y Av "
            "obtenidos en los mapas de zonificación sísmica del Capítulo "
            "A.2. El nivel de amenaza sísmica se clasificará como alta, "
            "intermedia o baja. En el Apéndice A-4 se presenta una "
            "enumeración de los municipios colombianos, con su definición "
            "de la zona de amenaza sísmica, y los valores de los "
            "parámetros Aa y Av, entre otros. Existentes: dentro del "
            "alcance de la etapa 4 de A.10.4.1, para las edificaciones "
            "existentes los movimientos sísmicos de diseño se determinan "
            "de igual forma que para edificaciones nuevas, con la "
            "excepción de las edificaciones a las cuales el Reglamento "
            "les permite acogerse al uso de movimientos sísmicos para el "
            "nivel de seguridad limitada para rehabilitación sísmica. "
            "Para el uso de movimientos sísmicos para el nivel de "
            "seguridad limitada debe consultarse A.10.9.2.5, el cual solo "
            "aplica a edificaciones declaradas como patrimonio histórico y "
            "bajo las condiciones impuestas allí. En este caso se permite "
            "el uso de Ae, en vez de los valores de Aa y Av tal como se "
            "indica en A.10.3.\n\n"
            "Paso 4 — Movimientos sísmicos de diseño. Nuevas: deben "
            "definirse unos movimientos sísmicos de diseño en el lugar de "
            "la edificación, de acuerdo con los requisitos del Capítulo "
            "A.2 del Reglamento y, en el caso de Edificaciones cubiertas "
            "por A.1.2.3.3, con los requisitos del Capítulo A.12 del "
            "Reglamento, tomando en cuenta: (a) la amenaza sísmica para el "
            "lugar determinada en el paso 3, expresada a través de los "
            "parámetros Aa, Av, o Ad, según sea el caso, los cuales "
            "representan la aceleración horizontal pico efectiva y la "
            "velocidad horizontal pico efectiva expresada en términos de "
            "aceleración del sismo de diseño, (b) las características de "
            "la estratificación del suelo subyacente en el lugar a través "
            "de unos coeficientes de sitio Fa y Fv, y (c) la importancia "
            "de la edificación para la recuperación de la comunidad con "
            "posterioridad a la ocurrencia de un sismo a través de un "
            "coeficiente de importancia I. Las características de los "
            "movimientos sísmicos de diseño se expresan por medio de un "
            "espectro elástico de diseño. El Reglamento contempla "
            "descripciones alternativas del sismo de diseño, ya sea a "
            "través de familias de acelerogramas, o bien por medio de "
            "expresiones derivadas de estudios de microzonificación "
            "sísmica, las cuales deben determinarse siguiendo los "
            "requisitos dados en el Capítulo A.2. Existentes: se deben "
            "seguir el mismo procedimiento que para edificaciones nuevas. "
            "Para el caso de edificaciones declaradas como patrimonio "
            "histórico y bajo las condiciones que lo permite A.10.9.2.5 se "
            "pueden utilizar los movimientos sísmicos para el nivel de "
            "seguridad limitada definido en A.10.3."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_4_tabla_pasos_5_a_9",
        "seccion": "Tabla A.1.3-1 — Procedimiento de diseño estructural (Pasos 5 a 9)",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "Tabla A.1.3-1 — Procedimiento de diseño estructural "
            "(continuación, Pasos 5 a 9):\n\n"
            "Paso 5 — Características de la estructuración y del material "
            "estructural empleado. Nuevas: el sistema estructural de "
            "resistencia sísmica de la edificación debe clasificarse "
            "dentro de uno de los sistemas estructurales prescritos en el "
            "Capítulo A.3: sistema de muros de carga, sistema combinado, "
            "sistema de pórtico, o sistema dual. El Reglamento define "
            "limitaciones en el empleo de los sistemas estructurales de "
            "resistencia sísmica en función de la zona de amenaza sísmica "
            "donde se encuentre localizada la edificación, del tipo de "
            "material estructural empleado (concreto estructural, "
            "estructura metálica, mampostería estructural, o madera), de "
            "la forma misma como se disponga el material en los elementos "
            "estructurales según la posibilidad de responder "
            "adecuadamente ante movimientos sísmicos como los esperados "
            "por medio de su capacidad de disipación de energía, la cual "
            "puede ser especial (DES), moderada (DMO) o mínima (DMI), de "
            "la altura de la edificación, y de su grado de irregularidad. "
            "Existentes: dentro del alcance de la etapa 4 de A.10.4.1, "
            "para las edificaciones existentes se determinan, de acuerdo "
            "con las características del sistema estructural empleado "
            "originalmente en su construcción, una correspondencia con "
            "los sistemas estructurales que se permiten para edificaciones "
            "nuevas de acuerdo con lo prescrito en A.10.4.2.\n\n"
            "Paso 6 — Grado de irregularidad de la estructura y "
            "procedimiento de análisis. Nuevas: definición del "
            "procedimiento de análisis sísmico de la estructura de "
            "acuerdo con la regularidad o irregularidad de la "
            "configuración de la edificación, tanto en planta como en "
            "alzado, su grado de redundancia o de ausencia de ella en el "
            "sistema estructural de resistencia sísmica, su altura, las "
            "características del suelo en el lugar, y el nivel de amenaza "
            "sísmica, siguiendo los preceptos dados en el Capítulo A.3 de "
            "este Reglamento. Existentes: se aplican los mismos "
            "principios que para edificaciones nuevas.\n\n"
            "Paso 7 — Determinación de las fuerzas sísmicas. Nuevas: "
            "obtención de las fuerzas sísmicas, Fs, que deben aplicarse a "
            "la estructura para lo cual deben usarse los movimientos "
            "sísmicos de diseño definidos en el paso 4. Existentes: "
            "dentro del alcance de la etapa 4 de A.10.4.1, para las "
            "edificaciones existentes se determinan unas solicitaciones "
            "equivalentes a las de edificaciones nuevas, pero ajustadas a "
            "las propiedades de la estructura existente. Véase A.10.4.2.\n\n"
            "Paso 8 — Análisis sísmico de la estructura. Nuevas: el "
            "análisis sísmico de la estructura se lleva a cabo aplicando "
            "los movimientos sísmicos de diseño prescritos, a un modelo "
            "matemático apropiado de la estructura, tal como se define en "
            "el Capítulo A.3. Este análisis se realiza para los "
            "movimientos sísmicos de diseño sin ser divididos por el "
            "coeficiente de capacidad de disipación de energía, R, y debe "
            "hacerse por el método que se haya definido en el paso 6. "
            "Deben determinarse los desplazamientos máximos que imponen "
            "los movimientos sísmicos de diseño a la estructura y las "
            "fuerzas internas que se derivan de ellos. Existentes: se debe "
            "cumplir lo indicado en la etapa 5 de A.10.1.4.\n\n"
            "Paso 9 — Desplazamientos horizontales. Nuevas: evaluación de "
            "los desplazamientos horizontales, incluyendo los efectos "
            "torsionales de toda la estructura, y las derivas "
            "(desplazamiento relativo entre niveles contiguos), "
            "utilizando los procedimientos dados en el Capítulo A.6 y con "
            "base en los desplazamientos obtenidos en el paso 8. "
            "Existentes: se debe cumplir lo indicado en la etapa 9 de "
            "A.10.1.4."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_4_tabla_pasos_10_a_12",
        "seccion": "Tabla A.1.3-1 — Procedimiento de diseño estructural (Pasos 10 a 12)",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "Tabla A.1.3-1 — Procedimiento de diseño estructural "
            "(continuación, Pasos 10 a 12):\n\n"
            "Paso 10 — Verificación de derivas. Nuevas: comprobación de "
            "que las derivas de diseño obtenidas no excedan los límites "
            "dados en el Capítulo A.6. Si la estructura excede los "
            "límites de deriva, calculada incluyendo los efectos "
            "torsionales de toda la estructura, es obligatorio rigidizarla, "
            "llevando a cabo nuevamente los pasos 8, 9 y 10, hasta cuando "
            "cumpla la comprobación de derivas. Existentes: se debe "
            "cumplir lo indicado en la etapa 10 de A.10.1.4.\n\n"
            "Paso 11 — Combinación de las diferentes solicitaciones. "
            "Nuevas: las diferentes solicitaciones que deben ser tenidas "
            "en cuenta, se combinan para obtener las fuerzas internas de "
            "diseño de la estructura, de acuerdo con los requisitos del "
            "Capítulo B.2 del Reglamento, por el método de diseño propio "
            "de cada material estructural. En cada una de las "
            "combinaciones de carga requeridas, las solicitaciones se "
            "multiplican por el coeficiente de carga prescrito para esa "
            "combinación en el Capítulo B.2 del Reglamento. En los "
            "efectos causados por el sismo de diseño se tiene en cuenta la "
            "capacidad de disipación de energía del sistema estructural, "
            "lo cual se logra empleando unos efectos sísmicos reducidos de "
            "diseño, E, obtenidos dividiendo las fuerzas sísmicas Fs, "
            "determinadas en el paso 7, por el coeficiente de capacidad de "
            "disipación de energía R (E = Fs/R). El coeficiente de "
            "capacidad de disipación de energía, R, es función de: (a) el "
            "sistema de resistencia sísmica de acuerdo con la "
            "clasificación dada en el Capítulo A.3, (b) del grado de "
            "irregularidad de la edificación, (c) del grado de "
            "redundancia o de ausencia de ella en el sistema estructural "
            "de resistencia sísmica, y (d) de los requisitos de diseño y "
            "detallado de cada material, para el grado de capacidad de "
            "disipación de energía correspondiente (DMI, DMO, o DES), tal "
            "como se especifica en el Capítulo A.3. Existentes: se debe "
            "cumplir lo indicado en las etapas 6 a 8 de A.10.1.4.\n\n"
            "Paso 12 — Diseño de los elementos estructurales. Nuevas: se "
            "lleva a cabo de acuerdo con los requisitos propios del "
            "sistema de resistencia sísmica y del material estructural "
            "utilizado. Los elementos estructurales deben diseñarse y "
            "detallarse de acuerdo con los requisitos propios del grado "
            "de capacidad de disipación de energía mínimo (DMI) moderado "
            "(DMO), o especial (DES) prescrito en el Capítulo A.3, según "
            "les corresponda, lo cual le permitirá a la estructura "
            "responder, ante la ocurrencia de un sismo, en el rango "
            "inelástico de respuesta y cumplir con los objetivos de las "
            "normas sismo resistentes. El diseño de los elementos "
            "estructurales debe realizarse para los valores más "
            "desfavorables obtenidos de las combinaciones obtenidas en el "
            "paso 11, tal como prescribe el Título B de este Reglamento. "
            "Existentes: se debe cumplir lo indicado en las etapas 8, 11 y "
            "12 de A.10.1.4 donde se indica como interpretar la "
            "resistencia efectiva de la edificación a la luz de las "
            "solicitaciones equivalentes y como se define la resistencia "
            "a proveer para reducir la vulnerabilidad de la edificación, "
            "cuando es vulnerable, para diseñar la intervención de la "
            "edificación."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_5_diseno_cimentacion",
        "seccion": "A.1.3.5 — Diseño de la cimentación",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.3.5 — DISEÑO DE LA CIMENTACIÓN — Los efectos de las "
            "diferentes solicitaciones, incluyendo los efectos de los "
            "movimientos sísmicos de diseño sobre los elementos de la "
            "cimentación y el suelo de soporte se obtienen así:\n\n"
            "(a) Para efectos del diseño estructural de los elementos que "
            "componen la cimentación, se emplean los resultados de las "
            "combinaciones realizadas en el paso 11 de A.1.3.4, empleando "
            "las cargas apropiadas y las fuerzas sísmicas reducidas de "
            "diseño, E, a partir de las reacciones de la estructura sobre "
            "estos elementos, tomando en cuenta la capacidad de la "
            "estructura. En el diseño de los elementos de cimentación "
            "deben seguirse los requisitos propios del material "
            "estructural y del Título H de este Reglamento.\n\n"
            "(b) Para efectos de obtener los esfuerzos sobre el suelo de "
            "cimentación, a partir de las reacciones de la estructura y "
            "su cimentación sobre el suelo, se emplean las combinaciones "
            "de carga para el método de esfuerzos de trabajo de la "
            "sección B.2.3, empleando las cargas apropiadas y las fuerzas "
            "sísmicas reducidas de diseño, E. Los efectos de la "
            "estructura y del sismo sobre el suelo así obtenidos están "
            "definidos al nivel de esfuerzos de trabajo y deben evaluarse "
            "de acuerdo con los requisitos del Título H de este "
            "Reglamento."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_6_diseno_sismico_no_estructurales",
        "seccion": "A.1.3.6 — Diseño sísmico de los elementos no estructurales",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.3.6 — DISEÑO SÍSMICO DE LOS ELEMENTOS NO ESTRUCTURALES "
            "— El diseño sísmico de los elementos no estructurales debe "
            "realizarse de acuerdo con los siguientes requisitos:\n\n"
            "A.1.3.6.1 — Se debe cumplir el grado de desempeño superior, "
            "bueno o bajo que define el Capítulo A.9 según el grupo de "
            "uso al cual pertenezca la edificación.\n\n"
            "A.1.3.6.2 — El diseño de los elementos no estructurales debe "
            "ser llevado a cabo por profesionales facultados para este "
            "fin de acuerdo con los artículos 26 y 29 de la Ley 400 de "
            "1997 y siguiendo los requisitos del Capítulo A.9, "
            "considerando para el efecto los parámetros de diseño sísmico "
            "aportados por el diseñador estructural.\n\n"
            "A.1.3.6.3 — Dentro de la clasificación de elementos no "
            "estructurales se incluyen sistemas como las estanterías, "
            "cuyo tratamiento deberá ser como el de los sistemas "
            "estructurales, los cuales pueden hacer parte de la "
            "estructura de la edificación, o ser un sistema estructural "
            "independiente de la estructura de la edificación donde se "
            "alojan. El diseño de este tipo de sistemas debe ser llevado "
            "a cabo por ingenieros estructurales, siguiendo requisitos de "
            "diseño sismo resistente acordes con las condiciones de carga "
            "específicas de cada aplicación, de acuerdo con el Capítulo "
            "A.9.\n\n"
            "A.1.3.6.4 — Se permite el uso de elementos diseñados e "
            "instalados por su fabricante, o cuya instalación se hace "
            "siguiendo sus instrucciones, cumpliendo lo indicado en "
            "A.1.5.1.2.\n\n"
            "A.1.3.6.5 — El constructor quien suscribe la licencia de "
            "construcción debe:\n\n"
            "(a) Recopilar los diseños de los diferentes elementos no "
            "estructurales y las características y documentación de "
            "aquellos que se acojan a lo permitido en A.1.5.1.2, para "
            "presentarlos en una sola memoria ante la Curaduría u oficina "
            "o dependencia encargada de estudiar, tramitar, y expedir las "
            "licencias de construcción.\n\n"
            "(b) Los diferentes diseños de los elementos no estructurales "
            "deben ser firmados por el Constructor que suscribe la "
            "licencia, indicando así que se hace responsable que los "
            "elementos no estructurales se construyan de acuerdo con lo "
            "diseñado, cumpliendo con el grado de desempeño especificado."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_7_a_9_revision_construccion_supervision",
        "seccion": "A.1.3.7 a A.1.3.9 — Revisión de los diseños, construcción y supervisión técnica",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.3.7 — REVISIÓN DE LOS DISEÑOS — Los planos, memorias y "
            "estudios realizados deben ser revisados para efectos de la "
            "obtención de la licencia de construcción tal como lo indica "
            "la Ley 400 de 1997, la Ley 388 de 1997 y sus respectivos "
            "reglamentos. Esta revisión debe ser realizada en la "
            "curaduría o en las oficinas o dependencias encargadas de "
            "estudiar, tramitar, y expedir las licencias de construcción, "
            "o bien por un profesional independiente, a costo de quien "
            "solicita la licencia. Los revisores de los diseños deben "
            "tener las cualidades establecidas en la Ley 400 de 1997.\n\n"
            "A.1.3.8 — CONSTRUCCIÓN — La construcción de la estructura, y "
            "de los elementos no estructurales, de la edificación se "
            "realiza de acuerdo con los requisitos propios del material, "
            "para el grado de capacidad de disipación de energía para el "
            "cual fue diseñada, y bajo una supervisión técnica, cuando así "
            "lo exija la Ley 400 de 1997, realizada de acuerdo con los "
            "requisitos del Título I. En la construcción deben cumplirse "
            "los requisitos dados por el Reglamento para cada material "
            "estructural y seguirse los procedimientos y especificaciones "
            "dados por los diseñadores. La dirección de la construcción "
            "debe ser realizada por un ingeniero civil, o arquitecto, o "
            "un ingeniero mecánico para el caso de estructuras metálicas o "
            "prefabricadas, facultados para este fin, de acuerdo con la "
            "Ley 400 de 1997, o un constructor en arquitectura o "
            "ingeniería facultado para este fin por la Ley 1229 de "
            "2008.\n\n"
            "A.1.3.9 — SUPERVISIÓN TÉCNICA — De acuerdo con el Título V "
            "de la Ley 400 de 1997, la construcción de estructuras de "
            "edificaciones, o unidades constructivas, que tengan más de "
            "3000 m² de área construida, independientemente de su uso, "
            "debe someterse a una supervisión técnica realizada de "
            "acuerdo con lo establecido en esta sección y en el Título I "
            "de este Reglamento."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_9_1_a_9_6_supervision_subsecciones",
        "seccion": "A.1.3.9.1 a A.1.3.9.6 — Casos y alcance de la supervisión técnica",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.3.9.1 — Edificaciones indispensables y de atención a la "
            "comunidad — De acuerdo con el Artículo 20 de la Ley 400 de "
            "1997, las edificaciones de los grupos de uso III y IV, "
            "independientemente del área que tengan, deben someterse a "
            "una Supervisión Técnica.\n\n"
            "A.1.3.9.2 — Edificaciones diseñadas y construidas de acuerdo "
            "con el Título E del Reglamento — De acuerdo con el Parágrafo "
            "1° del Artículo 18 de la Ley 400 de 1997, se excluyen de la "
            "obligatoriedad de la supervisión técnica, las estructuras "
            "que se diseñen y construyan siguiendo las recomendaciones "
            "del Título E, siempre y cuando se trate de menos de 15 "
            "unidades de vivienda.\n\n"
            "A.1.3.9.3 — Supervisión técnica exigida por los diseñadores "
            "— De acuerdo con el Parágrafo 2° del Artículo 18 de la Ley "
            "400 de 1997, el diseñador estructural, o el ingeniero "
            "geotecnista, de acuerdo con su criterio, pueden requerir "
            "supervisión técnica en edificaciones de cualquier área; cuya "
            "complejidad, procedimientos constructivos especiales o "
            "materiales empleados, la hagan necesaria, consignado este "
            "requisito en los planos estructurales o en el estudio "
            "geotécnico respectivo.\n\n"
            "A.1.3.9.4 — Idoneidad del supervisor técnico — El supervisor "
            "técnico debe ser un profesional, ingeniero civil o "
            "arquitecto, que cumpla las cualidades exigidas por el "
            "Capítulo V del Título VI de la Ley 400 de 1997 o un "
            "constructor en arquitectura e ingeniería según los artículos "
            "3° y 4° de la Ley 1229 de 2008. El profesional, bajo su "
            "responsabilidad, puede delegar en personal no profesional "
            "algunas de las labores de la supervisión. La supervisión "
            "técnica corresponde a una parte de la interventoría y puede "
            "ser llevada a cabo por un profesional diferente al "
            "interventor.\n\n"
            "A.1.3.9.5 — Alcance de la supervisión técnica — El alcance "
            "de las labores que debe realizar el supervisor técnico están "
            "establecidas en el Título I de este Reglamento.\n\n"
            "A.1.3.9.6 — Edificaciones donde no se requiere supervisión "
            "técnica — En aquellas edificaciones donde no se requiera la "
            "supervisión técnica, este hecho no exime al constructor de "
            "realizar los controles de calidad de los materiales que el "
            "Reglamento requiere para los diferentes materiales "
            "estructurales, ni de llevar registros y controles de las "
            "condiciones de cimentación y geotécnicas del proyecto."
        ),
    },
    {
        "id": "NSR10-A-A_1_3_10_a_13_edificaciones_indispensables_casas_ambiental",
        "seccion": "A.1.3.10 a A.1.3.13 — Edificaciones indispensables, casas de uno/dos pisos, aspectos fundamentales y construcción ambiental",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.3.10 — EDIFICACIONES INDISPENSABLES — Las edificaciones "
            "indispensables, pertenecientes al grupo de uso IV, tal como "
            "las define A.2.5.1.1, y las incluidas en los literales (a), "
            "(b), (c) y (d) del grupo de uso III, tal como las define "
            "A.2.5.1.2, deben diseñarse y construirse cumpliendo los "
            "requisitos presentados en el procedimiento de diseño "
            "definido en A.1.3.2 a A.1.3.8 y además los requisitos "
            "adicionales dados en el Capítulo A.12, dentro de los cuales "
            "se amplía el Paso 10 de A.1.3.4, exigiendo una verificación "
            "de la edificación para los movimientos sísmicos "
            "correspondientes al umbral de daño de la edificación. En "
            "relación con las edificaciones incluidas en los literales "
            "(e) y (f) del grupo de uso III, como lo define A.2.5.1.2, "
            "queda a decisión del propietario en el primer caso o de la "
            "autoridad competente en el segundo definir si se requiere "
            "adelantar el diseño de ellas según los requisitos especiales "
            "del Capítulo A.12.\n\n"
            "A.1.3.11 — CASAS DE UNO Y DOS PISOS — Las edificaciones de "
            "uno y dos pisos deben diseñarse de acuerdo con los "
            "Capítulos A.1 a A.12 de este Reglamento. Las casas de uno y "
            "dos pisos del grupo de uso I, tal como lo define A.2.5.1.4, "
            "que no formen parte de programas de quince o más unidades de "
            "vivienda ni tengan más de 3000 m² de área en conjunto, "
            "pueden diseñarse alternativamente de acuerdo con los "
            "requisitos del Título E de este Reglamento.\n\n"
            "A.1.3.12 — ASPECTOS FUNDAMENTALES DE DISEÑO — En toda "
            "edificación del grupo de uso I, como las define A.2.5.1, que "
            "tenga más de 3000 m² de área en conjunto, que forme parte de "
            "un programa de quince o más unidades de vivienda, y en todas "
            "las edificaciones de los grupos de usos II, III y IV, como "
            "las define A.2.5.1, y cuando con base en las características "
            "de la edificación o el lugar alguno de los diseñadores lo "
            "estime conveniente, deben considerarse los siguientes "
            "aspectos especiales en su diseño, construcción y supervisión "
            "técnica:\n\n"
            "(a) Influencia del tipo de suelo en la amplificación de los "
            "movimientos sísmicos y la respuesta sísmica de las "
            "edificaciones que igualmente pueden verse afectadas por la "
            "similitud entre los períodos de la estructura y alguno de "
            "los períodos del depósito,\n"
            "(b) Potencial de licuación del suelo en el lugar,\n"
            "(c) Posibilidad de falla de taludes o remoción en masa "
            "debida al sismo,\n"
            "(d) Comportamiento en grupo del conjunto ante solicitaciones "
            "sísmicas, eólicas y térmicas de acuerdo con las juntas que "
            "tenga el proyecto,\n"
            "(e) Especificaciones complementarias acerca de la calidad de "
            "los materiales a utilizar y del alcance de los ensayos de "
            "comprobación técnica de la calidad real de estos "
            "materiales, y\n"
            "(f) Verificación de la concepción estructural de la "
            "edificación desde el punto de vista de cargas verticales y "
            "fuerzas horizontales.\n"
            "(g) Obligatoriedad de una supervisión técnica, "
            "profesionalmente calificada, de la construcción, según lo "
            "requerido en A.1.3.9.\n\n"
            "A.1.3.13 — CONSTRUCCIÓN RESPONSABLE AMBIENTALMENTE — Las "
            "construcciones que se adelanten en el territorio nacional "
            "deben cumplir con la legislación y reglamentación nacional, "
            "departamental y municipal o distrital respecto al uso "
            "responsable ambientalmente de materiales y procedimientos "
            "constructivos. Se deben utilizar adecuadamente los recursos "
            "naturales y tener en cuenta el medio ambiente sin producir "
            "deterioro en él y sin vulnerar la renovación o disponibilidad "
            "futura de estos materiales. Esta responsabilidad ambiental "
            "debe desarrollarse desde la etapa de diseño y aplicarse y "
            "verificarse en la etapa de construcción, por todos los "
            "profesionales y demás personas que intervengan en dichas "
            "etapas."
        ),
    },
    {
        "id": "NSR10-A-A_1_4_consideraciones_especiales",
        "seccion": "A.1.4 — Consideraciones especiales",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.4 — CONSIDERACIONES ESPECIALES\n\n"
            "A.1.4.1 — POR TAMAÑO Y GRUPO DE USO — En toda edificación "
            "del grupo de uso I, como la define A.2.5.1, que tenga más "
            "de 3000 m² de área en conjunto, o que forme parte de un "
            "programa de quince o más unidades de vivienda, y en todas "
            "las edificaciones de los grupos de usos II, III y IV, como "
            "las define A.2.5.1, debe tenerse en cuenta la obligatoriedad "
            "de la supervisión técnica, profesionalmente calificada, de "
            "la construcción, según lo requerido en A.1.3.9.\n\n"
            "A.1.4.2 — SISTEMAS PREFABRICADOS — De acuerdo con lo "
            "establecido en el Artículo 12 de la Ley 400 de 1997, se "
            "permite el uso de sistemas de resistencia sísmica que estén "
            "compuestos, parcial o totalmente, por elementos "
            "prefabricados, que no estén cubiertos por este Reglamento, "
            "siempre y cuando cumpla uno de los dos procedimientos "
            "siguientes:\n\n"
            "(a) Se utilicen los criterios de diseño sísmico presentados "
            "en A.3.1.7, o\n"
            "(b) Se obtenga una autorización previa de la Comisión "
            "Asesora Permanente para el Régimen de Construcciones Sismo "
            "Resistentes, de acuerdo con los requisitos y "
            "responsabilidades establecidas en el Artículo 14 de la Ley "
            "400 de 1997."
        ),
    },
    {
        "id": "NSR10-A-A_1_5_1_disenador_responsable",
        "seccion": "A.1.5.1 — Diseñador responsable",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.5 — DISEÑOS, PLANOS, MEMORIAS Y ESTUDIOS\n\n"
            "A.1.5.1 — DISEÑADOR RESPONSABLE — La responsabilidad de los "
            "diseños de los diferentes elementos que componen la "
            "edificación recae en los profesionales bajo cuya dirección "
            "se elaboran los diferentes diseños particulares. Se "
            "presume, que cuando un elemento figure en un plano o "
            "memoria de diseño, es porque se han tomado todas las "
            "medidas necesarias para cumplir el propósito del Reglamento "
            "y por lo tanto el profesional que firma o rotula el plano es "
            "el responsable del diseño correspondiente.\n\n"
            "A.1.5.1.1 — Deben consultarse en el Título II de la Ley 400 "
            "de 1997, así como en el Capítulo A.13 de este Reglamento, "
            "las definiciones de constructor, diseñador arquitectónico, "
            "diseñador estructural, ingeniero geotecnista, propietario y "
            "supervisor técnico, para efectos de la asignación de las "
            "responsabilidades correspondientes.\n\n"
            "A.1.5.1.2 — En aquellos casos en los cuales en los diseños "
            "se especifican elementos cuyo suministro e instalación se "
            "realiza por parte de su fabricante o siguiendo sus "
            "instrucciones, el diseñador puede limitarse a especificar en "
            "sus planos, memorias o especificaciones, las características "
            "que deben cumplir los elementos, y la responsabilidad de que "
            "se cumplan estas características recae en el constructor que "
            "suscribe la licencia de construcción y este cumplimiento "
            "debe ser verificado por el supervisor técnico, cuando la "
            "edificación deba contar con su participación según el "
            "A.1.3.9."
        ),
    },
    {
        "id": "NSR10-A-A_1_5_2_planos",
        "seccion": "A.1.5.2 — Planos (arquitectónicos, estructurales, no estructurales)",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.5.2 — PLANOS — Los planos arquitectónicos, estructurales "
            "y de elementos no estructurales, que se presenten para la "
            "obtención de la licencia de construcción deben ser iguales a "
            "los utilizados en la construcción de la obra, y por lo menos "
            "una copia debe permanecer en archivo de la Curaduría, "
            "departamento administrativo o dependencia distrital o "
            "municipal encargada de expedir las licencias de "
            "construcción. La Curaduría Urbana o la dependencia municipal "
            "o distrital encargada de expedir las licencias de "
            "construcción, podrá solicitar una copia en medio magnético "
            "del proyecto estructural (planos y memorias), en los "
            "formatos digitales que ésta defina. En los proyectos que "
            "requieran supervisión técnica, de acuerdo con el presente "
            "Reglamento, se deberá cumplir adicionalmente con lo "
            "especificado en el Título I en relación con los planos "
            "finales de obra (planos record).\n\n"
            "A.1.5.2.1 — Planos estructurales — Los planos estructurales "
            "deben ir firmados o rotulados con un sello seco por un "
            "ingeniero civil facultado para ese fin y quien obra como "
            "diseñador estructural responsable. Los planos estructurales "
            "deben contener como mínimo: (a) especificaciones de los "
            "materiales de construcción que se van a utilizar en la "
            "estructura, tales como resistencia del concreto, resistencia "
            "del acero, calidad de las unidades de mampostería, tipo de "
            "mortero, calidad de la madera estructural, y toda "
            "información adicional que sea relevante para la "
            "construcción y supervisión técnica de la estructura. Cuando "
            "la calidad de material cambie dentro de la misma "
            "edificación, debe anotarse claramente cuál material debe "
            "usarse en cada porción de la estructura, (b) tamaño y "
            "localización de todos los elementos estructurales así como "
            "sus dimensiones y refuerzo, (c) precauciones que se deben "
            "tener en cuenta, tales como contraflechas, para "
            "contrarrestar cambios volumétricos de los materiales "
            "estructurales tales como: cambios por variaciones en la "
            "humedad ambiente, retracción de fraguado, flujo plástico o "
            "variaciones de temperatura, (d) localización y magnitud de "
            "todas las fuerzas de preesfuerzo, cuando se utilice concreto "
            "preesforzado, (e) tipo y localización de las conexiones "
            "entre elementos estructurales y los empalmes entre los "
            "elementos de refuerzo, así como detalles de conexiones y "
            "sistema de limpieza y protección anticorrosiva en el caso de "
            "estructuras de acero, (f) el grado de capacidad de "
            "disipación de energía bajo el cual se diseñó el material "
            "estructural del sistema de resistencia sísmica, (g) las "
            "cargas vivas y de acabados supuestas en los cálculos, y (h) "
            "el grupo de uso al cual pertenece la edificación.\n\n"
            "A.1.5.2.2 — Planos arquitectónicos y de elementos no "
            "estructurales arquitectónicos — Los planos arquitectónicos "
            "deben ir firmados o rotulados con un sello seco por un "
            "arquitecto facultado para ese fin y quien obra como "
            "diseñador arquitectónico responsable. Para efectos del "
            "presente Reglamento deben contener el grado de desempeño "
            "sísmico de los elementos no estructurales arquitectónicos, "
            "tal como los define el Capítulo A.9, y además todos los "
            "detalles y especificaciones, compatibles con este grado de "
            "desempeño, necesarios para garantizar que la construcción "
            "pueda ejecutarse y supervisarse apropiadamente. El diseñador "
            "de los elementos no estructurales, cuando el diseño sísmico "
            "de los elementos no estructurales se realice por un "
            "profesional diferente del arquitecto, debe firmar o rotular "
            "los planos arquitectónicos generales, además de los de los "
            "diseños particulares. Véase A.1.3.6.\n\n"
            "A.1.5.2.3 — Planos hidráulicos y sanitarios, eléctricos, "
            "mecánicos y de instalaciones especiales — Los planos de "
            "instalaciones hidráulicas y sanitarias, eléctricas, "
            "mecánicas, y de instalaciones especiales, deben ir firmados "
            "o rotulados con un sello seco por profesionales facultados "
            "para ese fin. Para efectos del presente Reglamento deben "
            "contener el grado de desempeño de los elementos no "
            "estructurales diferentes de arquitectónicos, tal como lo "
            "define el Capítulo A.9, y además todos los detalles y "
            "especificaciones, compatibles con este grado de desempeño, "
            "necesarios para garantizar que la construcción pueda "
            "ejecutarse y supervisarse apropiadamente."
        ),
    },
    {
        "id": "NSR10-A-A_1_5_3_memorias",
        "seccion": "A.1.5.3 — Memorias de diseño",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.5.3 — MEMORIAS — Los planos deben ir acompañados por "
            "memorias de diseño y cálculo en las cuales se describan los "
            "procedimientos por medio de los cuales se realizaron los "
            "diseños.\n\n"
            "A.1.5.3.1 — Memorias estructurales — Los planos "
            "estructurales que se presenten para obtener la licencia de "
            "construcción deben ir acompañados de la memoria "
            "justificativa de cálculos, firmada por el Ingeniero que "
            "realizó el diseño estructural. En esta memoria debe "
            "incluirse una descripción del sistema estructural usado, y "
            "además deben anotarse claramente las cargas verticales, el "
            "grado de capacidad de disipación de energía del sistema de "
            "resistencia sísmica, el cálculo de la fuerza sísmica, el "
            "tipo de análisis estructural utilizado y la verificación de "
            "que las derivas máximas no fueron excedidas. Cuando se use "
            "un equipo de procesamiento automático de información, "
            "además de lo anterior, debe entregarse una descripción de "
            "los principios bajo los cuales se realiza el modelo digital "
            "y su análisis estructural y los datos de entrada al "
            "procesador automático debidamente identificados. Los datos "
            "de salida pueden utilizarse para ilustrar los resultados y "
            "pueden incluirse en su totalidad en un anexo a las memorias "
            "de cálculo, pero no pueden constituirse en sí mismos como "
            "memorias de cálculo, requiriéndose de una memoria "
            "explicativa de su utilización en el diseño.\n\n"
            "A.1.5.3.2 — Memorias de otros diseños — Las justificaciones "
            "para el grado de desempeño de los elementos no estructurales "
            "deben consignarse en una memoria. Esta memoria debe ser "
            "elaborada por el profesional responsable de los diseños, ya "
            "sea el arquitecto o el diseñador de los elementos no "
            "estructurales, y los diseñadores hidráulicos, eléctricos, "
            "mecánicos o de instalaciones especiales. Véase A.1.3.6. "
            "Igualmente debe contarse con una memoria de las "
            "especificaciones sobre materiales, elementos estructurales, "
            "medios de ingreso y egreso y sistemas de detección y "
            "extinción de incendios relacionadas con la seguridad a la "
            "vida, de acuerdo con los Títulos J y K de este Reglamento."
        ),
    },
    {
        "id": "NSR10-A-A_1_5_4_estudio_geotecnico",
        "seccion": "A.1.5.4 — Estudio geotécnico",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.5.4 — ESTUDIO GEOTÉCNICO — Para efectos de obtener una "
            "licencia de construcción debe presentarse un estudio "
            "geotécnico realizado de acuerdo con los requisitos del "
            "Título H del presente Reglamento. El estudio geotécnico "
            "debe ir firmado por un ingeniero civil facultado para ese "
            "fin, y debe hacer referencia a:\n\n"
            "(a) Lo exigido en A.1.3.2,\n"
            "(b) A la definición de los efectos locales exigida en A.2.4, "
            "incluyendo el caso en el que se realice un estudio sísmico "
            "particular de sitio según lo indicado en A.2.10,\n"
            "(c) A la obtención de los parámetros del suelo para efectos "
            "de la evaluación de la interacción suelo-estructura tal como "
            "la define el Capítulo A.3, y\n"
            "(d) A las demás que exija el Título H."
        ),
    },
    {
        "id": "NSR10-A-A_1_6_obligatoriedad_normas_tecnicas",
        "seccion": "A.1.6 — Obligatoriedad de las normas técnicas citadas en el Reglamento",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.6 — OBLIGATORIEDAD DE LAS NORMAS TÉCNICAS CITADAS EN EL "
            "REGLAMENTO\n\n"
            "A.1.6.1 — NORMAS NTC — Las Normas Técnicas Colombianas NTC, "
            "citadas en el presente Reglamento, hacen parte de él. Las "
            "normas NTC son promulgadas por el Instituto Colombiano de "
            "Normas Técnicas y Certificación ICONTEC, único organismo "
            "nacional de normalización reconocido por el gobierno de "
            "Colombia.\n\n"
            "A.1.6.2 — OTRAS NORMAS — En aquellos casos en los cuales no "
            "exista una norma NTC se acepta la utilización de normas de "
            "la Sociedad Americana de Ensayo y Materiales (American "
            "Society for Testing and Materials — ASTM) o de otras "
            "instituciones, las cuales también hacen parte del Reglamento "
            "cuando no exista la correspondiente norma NTC.\n\n"
            "A.1.6.3 — REFERENCIAS — Al lado de las normas NTC se ha "
            "colocado entre paréntesis una norma de la ASTM o de otra "
            "institución. Esto se hace únicamente como referencia y la "
            "norma obligatoria siempre será la norma NTC. Esta norma de "
            "referencia corresponde a una norma ASTM, o de otra "
            "institución, que es compatible con los requisitos "
            "correspondientes del Reglamento, y no necesariamente "
            "corresponde a la norma antecedente de la norma NTC con las "
            "que se encuentren consignadas en el texto de la misma "
            "norma."
        ),
    },
    {
        "id": "NSR10-A-A_1_7_sistema_unidades",
        "seccion": "A.1.7 — Sistema de unidades",
        "titulo": "NSR-10 Título A — Capítulo A.1 — Introducción",
        "texto": (
            "A.1.7 — SISTEMA DE UNIDADES\n\n"
            "A.1.7.1 — SISTEMA MÉTRICO SI — De acuerdo con lo exigido "
            "por el Decreto 1731 de 18 de Septiembre de 1967, el "
            "presente Reglamento Colombiano de Construcciones Sismo "
            "Resistentes, NSR-10, se ha expedido utilizando el Sistema "
            "Internacional de Medidas (SI), el cual es de uso "
            "obligatorio en el territorio nacional. Debe consultarse la "
            "norma NTC 1000 (ISO 1000), expedida por el ICONTEC, para "
            "efectos de la correcta aplicación del Sistema Internacional "
            "de Medidas SI.\n\n"
            "A.1.7.2 — REFERENCIAS AL SISTEMA MÉTRICO mks — La unidades "
            "que se utilizan en las ecuaciones del Reglamento son las "
            "unidades del sistema SI. Al final de algunos Títulos hay un "
            "apéndice en el cual se relacionan las ecuaciones "
            "correspondientes en los sistemas de unidades SI y mks. En "
            "general todas las ecuaciones en las cuales se utiliza la "
            "raíz cuadrada de un esfuerzo, que por definición sigue "
            "teniendo unidades de esfuerzo, como es el caso de raíz de "
            "f'c en concreto reforzado, raíz de f'm en mampostería "
            "reforzada, ó raíz de Fy en estructuras metálicas, producen "
            "resultados inconsistentes si se emplean en esfuerzos "
            "expresados en el sistema mks (kgf/cm²), y solo pueden "
            "emplearse con esfuerzos expresados en el Sistema "
            "Internacional de Medidas (SI)."
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
