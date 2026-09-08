"""
NSR-10 Titulo H (Estudios Geotecnicos) -- H.8 COMPLETO (Sistema
Constructivo de Cimentaciones, Excavaciones y Muros de Contencion).
Quinta pieza real de ingesta tras la auditoria numeral-por-numeral de
2026-09-07 (ver memoria privada del usuario,
project_structai_nsr10_inventario_titulos.md).

H.8.0 (Nomenclatura), H.8.1 (Sistema geotecnico constructivo -- 3
escenarios: antes/durante/despues de la construccion), H.8.2
(Excavaciones: H.8.2.1 consideraciones generales, H.8.2.2 control del
flujo de agua, H.8.2.3 tablestacas y muros fundidos en el sitio, H.8.2.4
secuencia de excavacion, H.8.2.5 proteccion de taludes permanentes,
H.8.2.6 plan de contingencia), H.8.3 (Estructuras de contencion), H.8.4
(Procedimientos constructivos para cimentaciones: H.8.4.1 superficiales,
H.8.4.2 con pilotes o pilas con ecuacion H.8.4-1 y sub-numerales
H.8.4.2.1-3, H.8.4.3 combinadas, H.8.4.4 especiales) -- cierra el
Capitulo H.8 completo.

Fuente: NSR-10-1451-1500.pdf (Drive id 1DSJnOYqJixF0Nm1ewOH1VBDFpKas4x-y,
ya descargado en scripts/ingesta/nsr10/raw/), paginas PDF 28-34 (H-39 a
H-45, la pagina PDF 35/H-46 es "Notas" en blanco, fin del capitulo),
leidas visualmente con Read pages= sobre el PDF nativo.

CHUNKS escritos en piezas por numeral/subnumeral, re-trocheadas
programaticamente al final con VERIFICACION REAL de tokens via
_resplit_titulo_h_h8_por_limite_tokens.py -- mismo metodo ya
establecido (F.4.6/F.4.7, H.3.3+H.4, H.5, H.6, H.7).

Uso: python _ingest_titulo_h_h8_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título H — Estudios Geotécnicos"

CHUNKS = [
    {
        "id": "NSR10-H-H_8_0_nomenclatura",
        "seccion": "H.8.0 (Nomenclatura del Capítulo H.8 — Sistema constructivo)",
        "titulo": "D (diámetro del pilote), E (módulo de elasticidad), I (momento de inercia), K (coeficiente de reacción horizontal), L (longitud), N (entero para menor Pc).",
        "texto": (
            "CAPÍTULO H.8 — SISTEMA CONSTRUCTIVO DE CIMENTACIONES, "
            "EXCAVACIONES Y MUROS DE CONTENCIÓN. H.8.0 — NOMENCLATURA — "
            "D = diámetro del pilote. E = módulo de elasticidad del "
            "pilote. I = momento de inercia del pilote. K = coeficiente "
            "de reacción horizontal del suelo. L = longitud del pilote. "
            "N = número entero, determinado por tanteo, que genere el "
            "menor valor de Pc."
        ),
    },
    {
        "id": "NSR10-H-H_8_1_sistema_geotecnico_constructivo",
        "seccion": "H.8.1 (Sistema Geotécnico Constructivo — 3 escenarios: antes, durante, después)",
        "titulo": "Documento obligatorio complementario al estudio geotécnico; describe condiciones antes/durante (cambios de esfuerzo por perforación/vibración)/después de la construcción.",
        "texto": (
            "H.8.1 — SISTEMA GEOTÉCNICO CONSTRUCTIVO — El Sistema "
            "Geotécnico Constructivo definido como el sistema "
            "constructivo de cimentaciones, excavaciones y muros de "
            "contención es un documento complementario o integrado al "
            "estudio geotécnico definitivo, de obligatoria elaboración. "
            "Debe incluir el escenario más probable del proceso "
            "constructivo, considerando aspectos como secuencia de "
            "excavación, métodos de perforación, tratamientos "
            "estabilizadores previos, aplicación de pre-cargas, cambios "
            "en las trayectorias de drenaje u otros que puedan alterar "
            "o modificar en forma importante el comportamiento de los "
            "geomateriales que conforman el suelo de fundación, "
            "procedimientos constructivos de la cimentación y planes de "
            "contingencia, de acuerdo con los numerales que apliquen de "
            "este Capítulo H.8. Todo Proyecto de Construcción deberá "
            "incluir un análisis de las condiciones físicas e "
            "hidro-mecánicas de los depósitos de suelos o macizos "
            "rocosos involucrados, para cada uno de los escenarios "
            "previstos en el desarrollo de la construcción del "
            "proyecto, y específicamente deberá considerar al menos "
            "los siguientes: (a) Escenario antes de la construcción — "
            "Se describen las condiciones de los geomateriales in-situ "
            "determinadas mediante los procedimientos y prácticas "
            "convencionales y aquellas de que tratan estas normas, "
            "haciendo especial énfasis en condiciones inalteradas y con "
            "cambios menores respecto de la variación de propiedades "
            "esfuerzo–deformación con relación a las determinadas en "
            "ensayos de laboratorio. (b) Escenario durante la "
            "construcción — Se describen las condiciones que cambian o "
            "modifican las propiedades de los geomateriales como "
            "cambios en el estado de esfuerzos (descargas–recargas, "
            "humedecimiento–secado, etc.), efectos debidos a "
            "operaciones de perforación, vibraciones, ruidos, emisión y "
            "manejo de lodos y en general cualquier fuente de "
            "contaminación del subsuelo de apoyo, incluyendo "
            "variaciones en resistencia y rigidez debidas a la "
            "aplicación de las cargas de trabajo o cargas incidentales, "
            "de naturaleza estática o dinámica. (c) Escenario después "
            "de la construcción — Se describen las condiciones en las "
            "que se espera que permanezcan los geomateriales durante la "
            "vida útil de la estructura, para lo cual se debe prever la "
            "necesidad de construcción de sistemas especiales de "
            "mantenimiento de la estructura y si fuere del caso de los "
            "elementos de cimentación y el suelo que la rodea, así como "
            "la instrumentación y monitoreo de la posible variación de "
            "propiedades esfuerzo–deformación de los suelos de apoyo, "
            "debidas a modificación de las trayectorias de drenaje o "
            "inducción de presiones adicionales que aceleren o "
            "modifiquen las tasas de deformación de los materiales "
            "involucrados. Cada uno de estos escenarios deberá permitir "
            "la definición concreta de secuencias de construcción, "
            "medidas de mitigación, seguimiento y monitoreo de todos "
            "los efectos que sobre la estabilidad de las estructuras de "
            "cimentación y sobretodo de los suelos de fundación, puedan "
            "conllevar los procedimientos constructivos que se ejecuten "
            "en el proyecto."
        ),
    },
    {
        "id": "NSR10-H-H_8_2_1_excavaciones_consideraciones_generales",
        "seccion": "H.8.2 / H.8.2.1 (Excavaciones — consideraciones generales, taludes perimetrales y pilotes de fricción)",
        "titulo": "Taludes perimetrales según análisis de estabilidad; capaces de atender esfuerzos de tensión inducidos, recurrir a pilotes de fricción hincados previamente.",
        "texto": (
            "H.8.2 — EXCAVACIONES. H.8.2.1 — CONSIDERACIONES GENERALES "
            "— Cuando las separaciones con las colindancias lo "
            "permitan, las excavaciones podrán delimitarse con taludes "
            "perimetrales cuya pendiente se evaluará a partir de un "
            "análisis de estabilidad de acuerdo con el Capítulo H.6. Si "
            "existen restricciones de espacio y no son aceptables "
            "taludes verticales debido a las características del "
            "subsuelo, se recurrirá a un sistema de soporte constituido "
            "por entibados, tablestacas o muros fundidos en el lugar "
            "apuntalados o retenidos con anclajes instalados en suelos "
            "firmes. En todos los casos deberá lograrse un control "
            "adecuado del flujo de agua en el subsuelo y seguirse una "
            "secuencia de excavación que minimice los movimientos de "
            "las construcciones vecinas y servicios públicos. Para "
            "reducir la magnitud de las expansiones instantáneas será "
            "aceptable, asimismo, recurrir a pilotes de fricción "
            "hincados previamente a la excavación y capaces de atender "
            "los esfuerzos de tensión inducidos por el terreno."
        ),
    },
    {
        "id": "NSR10-H-H_8_2_2_control_flujo_agua",
        "seccion": "H.8.2.2 (Control del flujo de agua en excavaciones)",
        "titulo": "Bombeo con teoría de flujo transitorio; capacidad para gasto ≥1.5 veces el estimado; sistema de bombeo superficial y descarga libre de sedimentos.",
        "texto": (
            "H.8.2.2 — CONTROL DEL FLUJO DE AGUA — Cuando la "
            "construcción de la cimentación lo requiera, se controlará "
            "el flujo de agua en el subsuelo del predio mediante "
            "bombeo, tomando precauciones para limitar los efectos "
            "indeseables del mismo en el propio predio y en los "
            "colindantes. Se escogerá el sistema de bombeo más adecuado "
            "de acuerdo con el tipo de suelo. El gasto y el abatimiento "
            "provocado por el bombeo se calcularán mediante la teoría "
            "del flujo de agua transitorio en el suelo. El diseño del "
            "sistema de bombeo incluirá la selección del número, "
            "ubicación, diámetro y profundidad de los pozos; el tipo, "
            "diámetro y ranurado de los tubos, y del espesor y "
            "composición granulométrica del filtro. Asimismo, se "
            "especificará la capacidad mínima de las bombas y la "
            "posición del nivel dinámico en los pozos en las diversas "
            "etapas de la excavación. En el caso de materiales "
            "compresibles y excavaciones importantes, se tomará en "
            "cuenta la sobrecarga inducida en el terreno por las "
            "fuerzas de filtración y se calcularán los asentamientos "
            "correspondientes. Si los asentamientos calculados resultan "
            "excesivos, se recurrirá a procedimientos alternos que "
            "minimicen el abatimiento piezométrico. Deberá considerarse "
            "la conveniencia de reinyectar el agua bombeada en la "
            "periferia de la excavación y de usar pantallas "
            "impermeables que la aíslen, de tal manera que se modifique "
            "lo menos posible el estado de esfuerzos efectivos e "
            "iniciales del terreno; para controlar esto es muy "
            "importante la instalación de piezómetros previo al inicio "
            "de la construcción. No se debe descartar la instalación de "
            "otros instrumentos como inclinómetros, extensómetros, etc. "
            "Cualquiera que sea el tipo de instalación de bombeo que se "
            "elija, su capacidad se calculará para un gasto de "
            "extracción de por lo menos 1.5 veces superior al estimado. "
            "Además, deberá asegurarse el funcionamiento continuo de "
            "todo el sistema. En suelos de muy baja permeabilidad, "
            "abatir el nivel freático, el bombeo tendrá como objetivo: "
            "(a) Dar a las fuerzas de filtración una dirección "
            "favorable a la estabilidad de la excavación; e (b) "
            "Preservar el estado de esfuerzos del suelo; e (c) "
            "Interceptar las filtraciones provenientes de lentes "
            "permeables. En todos los casos será necesario un sistema "
            "de bombeo superficial que desaloje el agua de uno o varios "
            "cárcamos en los que se recolecten los escurrimientos de "
            "agua. El agua bombeada arrojada al sistema de drenaje "
            "público deberá estar libre de sedimentos y contaminantes."
        ),
    },
    {
        "id": "NSR10-H-H_8_2_3_4_tablestacas_secuencia",
        "seccion": "H.8.2.3 / H.8.2.4 (Tablestacas y muros fundidos en sitio; secuencia de excavación)",
        "titulo": "Tablestacas hincadas hasta estrato impermeable suficiente; empujes calculados según Capítulo H.5; excavación por etapas con secuencia simétrica.",
        "texto": (
            "H.8.2.3 — TABLESTACAS Y MUROS FUNDIDOS EN EL SITIO — "
            "Cuando se utilicen tablestacas hincadas en la periferia de "
            "la excavación o muros fundidos in situ o prefabricados, "
            "deberán prolongarse hasta una profundidad suficiente para "
            "interceptar el flujo debido a los principales estratos "
            "permeables que pueden dificultar la realización de la "
            "excavación. El cálculo de los empujes sobre los puntales "
            "que sostengan estos elementos se hará por los métodos "
            "indicados en el Capítulo H.5. El sistema de apuntalamiento "
            "podrá también ser constituido por anclajes horizontales "
            "instalados en suelos firmes o muros perpendiculares "
            "colados en el lugar o prefabricados. H.8.2.4 — SECUENCIA "
            "DE EXCAVACIÓN — El procedimiento de excavación deberá "
            "asegurar que no se rebasen los estados límite de servicio "
            "(movimientos verticales y horizontales inmediatos y "
            "diferidos por descarga en el área de excavación y en la "
            "zona circundante). De ser necesario, la excavación se "
            "realizará por etapas, según un programa que se incluirá en "
            "la memoria de diseño, señalando además las precauciones "
            "que deban tomarse para que no resulten afectadas las "
            "construcciones de los predios vecinos o los servicios "
            "públicos; estas precauciones se consignarán debidamente en "
            "los planos. Al efectuar la excavación por etapas, para "
            "limitar las expansiones del fondo a valores compatibles "
            "con el comportamiento de la propia estructura o de "
            "edificios e instalaciones colindantes, se adoptará una "
            "secuencia simétrica. Se restringirá la excavación a zanjas "
            "de pequeñas dimensiones en planta en las que se construirá "
            "y lastrará la cimentación antes de excavar otras áreas. "
            "Para reducir la magnitud de las expansiones instantáneas "
            "será aceptable, asimismo, recurrir a pilotes de fricción "
            "hincados previamente a la excavación y capaces de atender "
            "los esfuerzos de tensión inducidos por el terreno."
        ),
    },
    {
        "id": "NSR10-H-H_8_2_5_proteccion_taludes_permanentes",
        "seccion": "H.8.2.5 (Protección de taludes permanentes — anclajes, deformaciones compatibles)",
        "titulo": "Deformaciones del suelo compatibles con el sistema de protección; anclajes pasivos/activos con protección contra corrosión; verificar normas locales de excavaciones.",
        "texto": (
            "H.8.2.5 — PROTECCIÓN DE TALUDES PERMANENTES — En el diseño "
            "de los sistemas de protección de taludes naturales o "
            "cortes artificiales permanentes, se tomará en cuenta que "
            "las deformaciones del suelo protegido deben ser "
            "compatibles con las del sistema de protección empleado. "
            "Se tomará asimismo en cuenta el efecto del peso del "
            "sistema de protección sobre la estabilidad general o local "
            "del talud durante y después de la construcción. Por otra "
            "parte, los sistemas de protección deberán incluir "
            "elementos que garanticen un drenaje adecuado y eviten el "
            "desarrollo de presiones hidrostáticas que puedan "
            "comprometer la estabilidad del sistema de protección y del "
            "propio talud. En caso de usar anclajes pasivos o activos "
            "para la estabilización del talud deberá demostrarse que "
            "éstos no afectarán la estabilidad ni inducirán "
            "deformaciones significativas en las construcciones vecinas "
            "y/o en los servicios públicos. El sistema estructural de "
            "los anclajes deberá analizarse con el objetivo de asegurar "
            "su funcionamiento como elemento de anclaje. Por otra "
            "parte, se tomarán las precauciones necesarias para "
            "proteger los anclajes contra corrosión, con base en "
            "pruebas que permitan evaluar la agresividad del terreno, "
            "principalmente en cuanto a resistividad eléctrica, pH, "
            "cantidad de sulfuros, sulfatos y cloruros. Se prestará "
            "particular atención a la protección de los elementos que "
            "no se encuentran dentro del barreno y en especial en la "
            "zona del brocal (placas de apoyo, cuñas, tuercas, zona "
            "terminal del elemento tensor, etc.) Se deberá contemplar "
            "la modelación de todas las etapas del proceso constructivo "
            "con el propósito de analizar no solo la estabilidad de los "
            "taludes o cortes resultantes en su condición final, sino "
            "además que permita prever el efecto que tienen las "
            "técnicas y procedimientos de corte como voladuras "
            "controladas, mediante maquinaria pesada o manualmente, "
            "según sea el caso. Se deberá verificar la existencia de "
            "normas específicas de autoridades locales sobre la "
            "ejecución de excavaciones, uso del suelo, microzonificación "
            "sísmica o derivadas de Planes de Ordenamiento Territorial "
            "o similares."
        ),
    },
    {
        "id": "NSR10-H-H_8_2_6_plan_contingencia",
        "seccion": "H.8.2.6 (Plan de contingencia para excavaciones)",
        "titulo": "Obligatorio para excavaciones >3m o en base de laderas; define elementos vulnerables, riesgos, área de influencia, personas involucradas, rutas de evacuación.",
        "texto": (
            "H.8.2.6 — PLAN DE CONTINGENCIA PARA EXCAVACIONES — Cuando "
            "se proyecten excavaciones de más de 3 m de profundidad o "
            "en la base de laderas, se debe contar con un plan de "
            "contingencia, donde se determinen los elementos "
            "vulnerables, los riesgos potenciales, el área de "
            "influencia, las posibles personas involucradas, los "
            "mecanismos de aviso a las autoridades, las rutas de "
            "evacuación, los mecanismos de capacitación al personal, el "
            "diseño de sistemas de control de la contingencia, el "
            "listado de elementos que pueden requerirse para afrontar "
            "una contingencia y los sitios y procedimientos para "
            "adquirir dichos elementos de control."
        ),
    },
    {
        "id": "NSR10-H-H_8_3_estructuras_contencion_construccion",
        "seccion": "H.8.3 (Estructuras de contención — cuidados constructivos)",
        "titulo": "Prever sobreesfuerzos que reduzcan capacidad de soporte; secuencia completa de ejecución; drenaje preventivo diseñado para estabilidad del muro y del material contenido.",
        "texto": (
            "H.8.3 — ESTRUCTURAS DE CONTENCIÓN — Durante los procesos "
            "constructivos que involucran estructuras de contención, "
            "independientemente del tipo de estructura del cual se "
            "trate (cantiliver, de gravedad, con contrafuertes, "
            "apuntalada, etc.), se deberá prever los cuidados necesarios "
            "para no inducir sobreesfuerzos que conlleven deformaciones "
            "sobre estas y que posteriormente puedan reducir la "
            "capacidad de soporte para la cual fueron diseñadas, bajo "
            "la condición de carga final de trabajo. Se debe incluir la "
            "secuencia completa de ejecución de actividades, de manera "
            "tal que se garantice que ni los suelos de cimentación ni "
            "aquellos que servirán a relleno a la estructura de "
            "contención, sufran variaciones importantes en su rigidez y "
            "resistencia, y de manera particular en la densidad del "
            "material a colocar en el trasdós del muro, toda vez que "
            "este factor puede inducir degradación prematura de la "
            "estructura de contención. Los sistemas de drenaje "
            "preventivo deberán diseñarse e instalarse en la forma "
            "adecuada para buscar tanto la estabilidad de la estructura "
            "de contención como del material contenido y la menor "
            "variación posible de las trayectorias de drenaje "
            "naturales. Cuando se trate de estructuras de contención "
            "relacionadas con estabilidad de taludes o laderas producto "
            "de análisis en estudios de remoción en masa, se deberán "
            "tener en cuenta además de los requisitos contemplados en "
            "estas normas, aquellos prescritos por las normas que "
            "regulen ese tipo de estudios en cada zona geográfica del "
            "país."
        ),
    },
    {
        "id": "NSR10-H-H_8_4_1_cimentaciones_superficiales_construccion",
        "seccion": "H.8.4 / H.8.4.1 (Procedimientos constructivos para cimentaciones — cimentaciones superficiales)",
        "titulo": "Desplante a la profundidad del estudio geotécnico; verificar discrepancias en obra; recubrimiento del acero de refuerzo; evitar mezcla del concreto con suelo o agua freática.",
        "texto": (
            "H.8.4 — PROCEDIMIENTOS CONSTRUCTIVOS PARA CIMENTACIONES. "
            "H.8.4.1 — CIMENTACIONES SUPERFICIALES — El desplante de la "
            "cimentación se hará a la profundidad señalada en el "
            "estudio geotécnico. Sin embargo, deberá tenerse en cuenta "
            "cualquier discrepancia entre las características del "
            "suelo encontradas a esta profundidad y las consideradas en "
            "el proyecto, para que, de ser necesario, se hagan los "
            "ajustes correspondientes. Se tomarán todas las medidas "
            "necesarias para evitar que en la superficie de apoyo de la "
            "cimentación se presente alteración del suelo durante la "
            "construcción por saturación o remoldeo. Las superficies de "
            "desplante estarán libres de cuerpos extraños o sueltos. En "
            "el caso de elementos de cimentación de concreto reforzado "
            "se aplicarán procedimientos de construcción que garanticen "
            "el recubrimiento requerido para proteger el acero de "
            "refuerzo. Se tomarán las medidas necesarias para evitar "
            "que el propio suelo o cualquier líquido o gas contenido en "
            "él puedan atacar el concreto o el acero. Asimismo, durante "
            "el colado se evitará que el concreto se mezcle o contamine "
            "con partículas de suelo o con agua freática, que puedan "
            "afectar sus características de resistencia o durabilidad. "
            "Se debe incluir la secuencia en la que se deben realizar "
            "las excavaciones superficiales, disposición de sobrantes "
            "de excavación, incidencia por posibles cambios o "
            "alteraciones en las trayectorias de drenaje y variaciones "
            "del nivel freático, tiempo máximo de exposición de los "
            "geomateriales ante cambios en las condiciones ambientales, "
            "efectos por ciclos de humedecimiento–secado que puedan "
            "conllevar variaciones en las propiedades mecánicas e "
            "hidráulicas de los materiales de apoyo, efectos por ciclos "
            "de carga–descarga a los que se puedan ver sometidos los "
            "materiales del perfil, hasta la profundidad de influencia "
            "previamente determinada. En estos casos, el ingeniero "
            "geotecnista será responsable de orientar adecuadamente los "
            "procedimientos constructivos, proponiendo las fases en los "
            "cuales estos se deben adelantar e indicando con precisión "
            "la necesidad o no de instrumentar el desarrollo de dichas "
            "fases. Los trabajos relativos a excavaciones a cielo "
            "abierto, construcción de rellenos y terraplenes y "
            "procedimientos de estabilización de geomateriales in–situ, "
            "implican la realización de análisis de estabilidad "
            "estáticos y dinámicos que conduzcan a la obtención de "
            "factores de seguridad de carácter transitorio, que son "
            "precisados por estas Normas en el capítulo H-6."
        ),
    },
    {
        "id": "NSR10-H-H_8_4_2_pilotes_pilas_ecuacion_pandeo",
        "seccion": "H.8.4.2 (Cimentaciones con pilotes o pilas — verificación por pandeo, ecuación H.8.4-1)",
        "titulo": "Pc=(N²π²EI/4L²+4KDL²π²)/FS; pilotes <40cm diámetro deben revisarse por pandeo; FS=3.0; hincado en orden desde el centro hacia afuera.",
        "texto": (
            "H.8.4.2 — CIMENTACIONES CON PILOTES O PILAS — La "
            "colocación de pilotes y pilas se ajustará al proyecto "
            "correspondiente, verificando que la profundidad de "
            "desplante, el número y el espaciamiento de estos elementos "
            "correspondan a lo señalado en los planos estructurales. "
            "Los procedimientos para la instalación de pilotes y pilas "
            "deberán garantizar la integridad de estos elementos y que "
            "no se ocasionen daños a las estructuras e instalaciones "
            "vecinas por vibraciones o desplazamiento vertical y "
            "horizontal del suelo. Cada pilote, sus tramos y las juntas "
            "entre estos, en su caso, deberán diseñarse y construirse "
            "de modo que resistan las fuerzas de compresión y tensión y "
            "los momentos flexionantes que resulten del análisis. Los "
            "pilotes de diámetro menor de 40 cm deberán revisarse por "
            "pandeo verificando que la fuerza axial a la que se "
            "encontrarán sometidos, no rebasará la fuerza crítica Pc "
            "definida por: Pc = (N²π²EI/4L² + 4KDL²π²)/FS (H.8.4-1). "
            "en donde: K = coeficiente de reacción horizontal del "
            "suelo; D = diámetro del pilote; E = módulo de elasticidad "
            "del pilote; I = momento de inercia del pilote; N = número "
            "entero, determinado por tanteo, que genere el menor valor "
            "de Pc; L = longitud del pilote; y F_S se tomará igual a "
            "3.0. Los pilotes se hincarán en orden, desde la parte "
            "central del grupo hacia fuera, con el fin de uniformar la "
            "densificación en suelos granulares y de evitar acumulación "
            "excesiva de presiones de poros en suelos cohesivos."
        ),
    },
    {
        "id": "NSR10-H-H_8_4_2_1_pilas_fundidas_sitio",
        "seccion": "H.8.4.2.1 (Pilas o pilotes fundidos en el sitio — estabilización, campana, control de calidad)",
        "titulo": "Lodo bentonítico/polimérico para estabilizar la perforación; campana con ángulo ≥60° respecto a la horizontal; tolerancia de localización 10%, verticalidad 2-3%.",
        "texto": (
            "H.8.4.2.1 — Pilas o pilotes fundidos en el sitio — Para "
            "este tipo de cimentaciones profundas, el estudio "
            "geotécnico deberá definir si la perforación previa será "
            "estable en forma natural o si por el contrario se "
            "requerirá estabilizarla con lodo bentonítico o polimérico, "
            "con entibado ó encamisado. Antes de la fundida, se "
            "procederá a la inspección directa o indirecta del fondo de "
            "la perforación para verificar que las características del "
            "estrato de apoyo son satisfactorias y que todos los "
            "materiales derrumbados han sido removidos. La fundida se "
            "realizará por procedimientos que eviten la segregación del "
            "concreto y la contaminación del mismo con el lodo "
            "estabilizador de la perforación o con derrumbes de las "
            "paredes de la excavación. Se llevará un registro de la "
            "localización de los pilotes o pilas, las dimensiones "
            "relevantes de las perforaciones, las fechas de perforación "
            "y de fundida, la profundidad y los espesores de los "
            "estratos y las características del material de apoyo. "
            "Cuando la construcción de una cimentación requiera del uso "
            "de lodo bentonítico o polimérico, el constructor no deberá "
            "verterlo en el drenaje urbano, por lo que deberá destinar "
            "un área para recolectar dicho lodo después de usarlo y "
            "transportarlo a algún botadero autorizado por la autoridad "
            "ambiental. Cuando se usen pilas con ampliación de base "
            "(campana), la perforación de la misma se hará verticalmente "
            "en los primeros 20 cm para después formar con la "
            "horizontal un ángulo no menor de 60°: el peralte de la "
            "campana en el fondo será por lo menos de 20 cm o lo "
            "indicado en los planos estructurales. En general no se "
            "recomienda construir campanas bajo agua o lodos, a menos "
            "que se garantice explícitamente mediante pruebas de "
            "integridad, que el concreto colocado en esta zona en donde "
            "se desarrolla la capacidad de carga, ofrece las "
            "características de durabilidad y sanidad requeridas para "
            "un óptimo desempeño estructural durante su vida útil. "
            "Dicha condición del proceso constructivo quedará a "
            "criterio del ingeniero geotecnista. Otros aspectos a los "
            "que deberá prestarse atención son el método y equipo para "
            "la eliminación de materiales derrumbados, la duración de "
            "la fundida, así como el recubrimiento y la separación "
            "mínima del acero de refuerzo con relación al tamaño del "
            "agregado. Para desplantar la cimentación sobre el "
            "concreto sano de la pila, se deberá dejar en la parte "
            "superior una longitud extra de concreto, equivalente al "
            "90% del diámetro de la misma; este concreto, que acarrea "
            "las impurezas durante el proceso de fundido, podrá ser "
            "removido con equipo neumático hasta 20 cm arriba de la "
            "cota de desplante de la cimentación; estos últimos 20 cm "
            "se deberán quitar en forma manual procurando que la "
            "herramienta de ataque no produzca fisuras en el concreto "
            "que recibirá el resto de la cimentación. En el caso de "
            "pilas excavadas manualmente y fundidas en seco, la "
            "longitud adicional podrá ser hasta de 50% del diámetro de "
            "las mismas, evitando remover el concreto de esta parte en "
            "estado fresco con el propósito de que el curado del "
            "concreto se efectúe en dicha zona. Esta parte se demolerá "
            "siguiendo los lineamientos indicados en el punto anterior. "
            "En cualquier tipo de pila, será necesario construir una "
            "guía antes de iniciar la perforación a fin de preservar la "
            "seguridad del personal y la calidad de la pila por "
            "construir. No deberán construirse pilas excavadas "
            "manualmente (caissons) de menos de 100 cm de diámetro; "
            "para profundidades mayores de 10 m se deben proyectar "
            "diámetros mayores que permitan condiciones adecuadas de "
            "ventilación y seguridad para el personal. Las pilas o "
            "caissons deberán ser construidas con entibado o encamisado "
            "a menos que el estudio del subsuelo muestre que la "
            "perforación es estable. Respecto a la localización en "
            "planta de las pilas se aceptará una tolerancia del 10% de "
            "su diámetro. La tolerancia en la verticalidad de una pila "
            "será del 2% de su longitud hasta 25 m de profundidad y del "
            "3% para una mayor profundidad. Como medida de control de "
            "calidad y de continuidad de los pilotes fundidos in situ, "
            "se recomienda la ejecución de pruebas de integridad (PIT)."
        ),
    },
    {
        "id": "NSR10-H-H_8_4_2_2_pilotes_concreto_hincado",
        "seccion": "H.8.4.2.2 (Pilotes de concreto reforzado — traslapos, marcas, hincado)",
        "titulo": "Desviación máxima de verticalidad 3/100 (punta) o 6/100 (otros casos); posición final de cabeza ≤20cm o 1/4 del ancho del elemento estructural.",
        "texto": (
            "H.8.4.2.2 — En pilotes de concreto reforzado, se prestará "
            "especial atención a los traslapos en el acero de refuerzo "
            "longitudinal. Cada pilote deberá tener marcas que indiquen "
            "los puntos de izaje, para poder levantarlos de las mesas "
            "de fundida, transportarlos e izarlos. El estudio "
            "geotécnico deberá definir si se requiere perforación "
            "previa, con o sin extracción de suelo, para facilitar la "
            "hinca o para minimizar el desplazamiento de los suelos "
            "blandos. Se indicará en tal caso el diámetro de la "
            "perforación y su profundidad, y si es necesaria la "
            "estabilización con lodo bentonítico o polimérico. En "
            "pilotes de fricción el diámetro de la perforación previa "
            "para facilitar la hinca o para minimizar el desplazamiento "
            "de los suelos blandos no deberá ser mayor que el 75% del "
            "diámetro o lado del pilote. Si con tal diámetro máximo de "
            "la perforación no se logra hacer pasar el pilote a través "
            "de capas duras intercaladas, exclusivamente estas deberán "
            "limarse con herramientas especiales a un diámetro igual o "
            "ligeramente mayor que el del pilote. Antes de proceder al "
            "hincado, se verificará la verticalidad de los tramos de "
            "pilotes y, en su caso, la de las perforaciones previas. La "
            "desviación de la vertical del pilote no deberá ser mayor "
            "de 3/100 de su longitud para pilotes con capacidad de "
            "carga por punta ni de 6/100 en los otros casos. El equipo "
            "de hincado se especificará en términos de su energía en "
            "relación con la masa del pilote y el peso de la masa del "
            "martillo golpeador en relación con el peso del pilote, "
            "tomando muy en cuenta la experiencia local. Además, se "
            "especificarán el tipo y espesor de los materiales de "
            "amortiguamiento de la cabeza y el yelmo. El equipo de "
            "hincado podrá también definirse a partir de un análisis "
            "dinámico basado en la ecuación de onda. La posición final "
            "de la cabeza de los pilotes no deberá diferir respecto a "
            "la de proyecto en más de 20 cm ni de la cuarta parte del "
            "ancho del elemento estructural que se apoye sobre ella."
        ),
    },
    {
        "id": "NSR10-H-H_8_4_2_2_registro_pilotes_rechazados",
        "seccion": "H.8.4.2.2 (Pilotes de concreto reforzado — registro de hincado, pilotes rechazados o dañados)",
        "titulo": "Registro completo por pilote (ubicación, longitud, golpes, penetración); pilote roto/rechazado se retira y se sustituye o rellena, revisando el diseño de subestructura.",
        "texto": (
            "Al hincar cada pilote se llevará un registro de su "
            "ubicación, su longitud y dimensiones transversales, la "
            "fecha de colocación, el nivel del terreno antes de la "
            "hinca y el nivel de la cabeza inmediatamente después de la "
            "hinca. Además se incluirá el tipo de material empleado "
            "para la protección de la cabeza del pilote, el peso del "
            "martinete y su altura de caída, la energía de hincado por "
            "golpe, el número de golpes por metro de penetración a "
            "través de los estratos superiores al de apoyo y el número "
            "de golpes por cada 10 cm de penetración en el estrato de "
            "apoyo, así como el número de golpes y la penetración en la "
            "última fracción de decímetro penetrada. En el caso de "
            "pilotes hincados a través de un manto compresible hasta un "
            "estrato resistente, se verificará para cada pilote "
            "mediante nivelaciones si se ha presentado emersión por la "
            "hinca de los pilotes adyacentes y, en caso afirmativo, los "
            "pilotes afectados se volverán a hincar hasta la elevación "
            "especificada. Los métodos usados para hincar los pilotes "
            "deberán ser tales que no reduzcan la capacidad estructural "
            "de éstos. Si un pilote de punta se rompe o daña "
            "estructuralmente durante su hincado, o si por excesiva "
            "resistencia a la penetración, queda a una profundidad "
            "menor que la especificada y en ella no se pueda garantizar "
            "la capacidad de carga requerida, se extraerá la parte "
            "superior del mismo, de modo que la distancia entre el "
            "nivel de desplante de la subestructura y el nivel superior "
            "del pilote abandonado sea por lo menos de 3 m. En tal "
            "caso, se revisará el diseño de la subestructura y se "
            "instalarán pilotes sustitutos. Si es un pilote de fricción "
            "el que se rechace por daños estructurales durante su "
            "hincado, se deberá extraer totalmente y rellenar el hueco "
            "formado con otro pilote de mayor dimensión o bien con un "
            "material cuya resistencia y compresibilidad sea del mismo "
            "orden de magnitud que las del suelo que reemplaza; en este "
            "caso, también deberán revisarse el diseño de la "
            "subestructura y el comportamiento del sistema de "
            "cimentación."
        ),
    },
    {
        "id": "NSR10-H-H_8_4_2_3_pruebas_carga_pilotes",
        "seccion": "H.8.4.2.3 (Pruebas de carga en pilotes o pilas — registro de datos, análisis de irregularidad)",
        "titulo": "Registrar condiciones subsuelo, descripción del pilote/sistema/método, tabla carga-deformación, curva asentamiento-tiempo; instrumentar en cimentaciones irregulares.",
        "texto": (
            "H.8.4.2.3 — Pruebas de carga en pilotes o pilas — En caso "
            "de realizarse pruebas de carga, se llevará registro por lo "
            "menos de los datos siguientes: (a) Condiciones del "
            "subsuelo en el lugar de la prueba; (b) Descripción del "
            "pilote o pila y datos obtenidos durante la instalación; "
            "(c) Descripción del sistema de carga y del método de "
            "prueba; (d) Tabla de cargas y deformaciones durante las "
            "etapas de carga y descarga del pilote o pila; (e) "
            "Representación gráfica de la curva asentamientos–tiempo "
            "para cada incremento de carga; y (f) Observaciones e "
            "incidentes durante la instalación del pilote o pila y la "
            "prueba. Se deberán incluir los efectos esperados tanto de "
            "los métodos de perforación como de instalación de los "
            "elementos de cimentación (pilotes, pilas, caissons, etc.), "
            "con el propósito de reducir la variabilidad de los "
            "parámetros de resistencia mecánica de los materiales "
            "involucrados en función de la profundidad calculada de "
            "dichos elementos. En este caso se deberá hacer énfasis en "
            "la secuencia como se espera que los elementos de "
            "cimentación asuman las cargas, para evitar que algunos de "
            "ellos queden sobrecargados o que colapsen antes de la "
            "aplicación completa de la carga de trabajo; los "
            "procedimientos de inyección y posterior evacuación de "
            "lodos, así como su disposición final también deberán ser "
            "materia de análisis previo al desarrollo de procesos "
            "constructivos en cimentaciones profundas. En el evento en "
            "que los materiales reales presentes al momento de ejecutar "
            "la perforación o sondeo difieran considerablemente de los "
            "involucrados en los cálculos y análisis iniciales, el "
            "Ingeniero Geotecnista deberá ser advertido de esta "
            "situación considerada \"irregular\" y previamente a la "
            "autorización de continuar los trabajos de construcción de "
            "la cimentación, deberá realizar nuevos análisis de "
            "estabilidad de capacidad portante y de deformaciones según "
            "los requerimientos. Adicionalmente a las pruebas de carga "
            "o similares de que trata el literal anterior, se deberá "
            "considerar la necesidad de instrumentar o no este tipo de "
            "cimentaciones con el propósito de garantizar la integridad "
            "del sistema suelo–pilote y detectar eventuales "
            "alteraciones importantes que pueda experimentar el suelo "
            "de cimentación, debidas a los procedimientos constructivos "
            "que finalmente se adopten."
        ),
    },
    {
        "id": "NSR10-H-H_8_4_3_4_combinadas_especiales",
        "seccion": "H.8.4.3 / H.8.4.4 (Cimentaciones combinadas y especiales)",
        "titulo": "Combinadas (placa-pilote, contención-pilotes): requieren mayor análisis de interacción suelo-estructura; especiales (laderas, suelos H.9): requieren Proyecto de Construcción especial.",
        "texto": (
            "H.8.4.3 — CIMENTACIONES COMBINADAS — Este tipo de "
            "cimentación hace referencia en forma particular a los "
            "sistemas denominados placa–pilote. Debido a las "
            "incertidumbres asociadas al diseño y construcción de este "
            "tipo, se requiere mayor análisis de las implicaciones que "
            "los procesos constructivos puedan conllevar sobre la "
            "estabilidad de los suelos de cimentación. Durante la fase "
            "de construcción de los pilotes por lo general se afecta el "
            "suelo de apoyo de la losa, lo que hace necesario que se "
            "considere el cambio de parte de ese suelo por un material "
            "mejorado; estos cambios de rigidez de los geomateriales "
            "involucrados modifican los efectos de interacción "
            "suelo–estructura. Otros tipos de cimentaciones combinadas "
            "como: estructura de contención–pilotes, muros de "
            "cortante–vigas de cimentación, vigas de reacción–losa de "
            "cimentación, etc., implican cambios importantes en la "
            "rigidez de los materiales que requieren una atención "
            "especial para la definición de las secuencias "
            "constructivas, de manera que se induzca la menor cantidad "
            "de daño al suelo de fundación ó se prevea la necesidad de "
            "cambiar dicho suelo por un material más competente desde "
            "el punto de vista de su comportamiento mecánico, frente a "
            "las solicitaciones a las que va a estar expuesto, en forma "
            "particular durante la etapa de construcción de las "
            "estructuras. H.8.4.4 — CIMENTACIONES ESPECIALES — Aquí se "
            "consideran aquellas cimentaciones que se deben ejecutar en "
            "condiciones especiales del suelo de fundación, por ejemplo "
            "las que se realizan en una ladera y que requieren algún "
            "tratamiento especial como terraceo previo, estabilización "
            "o alteración importante de todo o parte del suelo de "
            "apoyo. Cuando los geomateriales están conformados por "
            "suelos excesivamente blandos o excesivamente duros, rocas "
            "con características especiales por su composición "
            "químico–mineralógica, materiales fuertemente alterados o "
            "meteorizados y los suelos contenidos en el Capítulo H-9 "
            "(suelos con características especiales), se deben "
            "considerar los cimientos que sobre ellos se apoyen como "
            "especiales, y en consecuencia deberán ser objeto de un "
            "Proyecto de Construcción igualmente especial en donde se "
            "describa con detalle tanto la secuencia de tratamiento de "
            "dichos suelos como del proceso constructivo de la "
            "cimentación propiamente dicha, considerando como etapas "
            "claves el antes, el durante y el después de la aplicación "
            "de las cargas de trabajo."
        ),
    },
]


def main():
    from sentence_transformers import SentenceTransformer
    from supabase import create_client

    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
    print(f"Chunks a insertar: {len(CHUNKS)}")
    max_len = 0
    for c in CHUNKS:
        n = len(c["texto"])
        max_len = max(max_len, n)
        print(f"  {c['id']}: {n} chars")
    print(f"\nMax chars: {max_len}")

    print("\nCargando modelo de embeddings local...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    textos = [c["texto"] for c in CHUNKS]
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

    print("\nSubiendo a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()

    print(f"\nOK: {len(rows)} chunks verbatim de H.8 cargados. H.8 queda COMPLETO.")


if __name__ == "__main__":
    main()
