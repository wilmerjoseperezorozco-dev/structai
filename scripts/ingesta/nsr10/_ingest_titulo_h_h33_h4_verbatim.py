"""
NSR-10 Titulo H (Estudios Geotecnicos) -- cierre de H.3 (H.3.3, Ensayos
de laboratorio) + H.4 COMPLETO (Cimentaciones). Primera pieza real de
ingesta tras la auditoria numeral-por-numeral de 2026-09-07 que
confirmo que Titulo H solo cubria H.1-H.3.2 (~18% del titulo, 33 de 181
encabezados reales) -- ver memoria privada del usuario,
project_structai_nsr10_inventario_titulos.md, seccion "Titulo H:
auditoria numeral por numeral confirma hueco real GRANDE".

H.3.3.1 (Seleccion de muestras), H.3.3.2 (Tipo y numero de ensayos),
H.3.3.3 (Propiedades basicas, con H.3.3.3.1 suelos y H.3.3.3.2 rocas),
H.3.3.4 (Caracterizacion geomecanica detallada), H.3.3.5 (Ejecucion de
ensayos de campo) -- cierra el Capitulo H.3 completo.

H.4.0 (Nomenclatura), H.4.1 (Generalidades), H.4.2 (Cimentaciones
superficiales -- zapatas y losas: H.4.2.1 estados limite de falla,
H.4.2.2 estados limite de servicio, H.4.2.3 capacidad admisible),
H.4.3 (Cimentaciones compensadas: H.4.3.1-3), H.4.4 (Cimentaciones con
pilotes: H.4.4.1-3), H.4.5 (Cimentaciones en roca: H.4.5.1-2), H.4.6
(Profundidad de cimentacion), H.4.7 (Factores de seguridad indirectos,
con Tabla H.4.7-1 y ecuaciones H.4.7-1 a -4, Tabla H.4.7-2), H.4.8
(Asentamientos: H.4.8.1-5), H.4.9 (Efectos de los asentamientos:
H.4.9.1-4, Tabla H.4.9-1), H.4.10 (Diseno estructural de la
cimentacion) -- cierra el Capitulo H.4 completo.

Fuente: NSR-10-1451-1500.pdf (Drive id 1DSJnOYqJixF0Nm1ewOH1VBDFpKas4x-y,
ya descargado en scripts/ingesta/nsr10/raw/ por el agente de auditoria),
paginas PDF 1-10 (H-11 a H-20), leidas visualmente con Read pages= sobre
el PDF nativo (nunca texto plano, para no corromper subindices/formulas).
Continuidad exacta verificada con la ultima pagina de
NSR-10-1401-1450.pdf (H-10, fin de H.3.2.5) -- H.3.2.6 (Numero minimo de
sondeos, ya cubierto por chunks existentes segun la auditoria) empalma
sin salto con H.3.3 al inicio de este PDF.

CHUNKS escritos en piezas por numeral/subnumeral, re-trocheadas
programaticamente al final con VERIFICACION REAL de tokens (no solo
estimacion por caracteres) via
_resplit_titulo_h_h33_h4_por_limite_tokens.py -- mismo metodo ya
establecido para F.4.6/F.4.7 (el unico confiable, ver memoria privada
project_construdata_limite_tokens_embeddings).

Uso: python _ingest_titulo_h_h33_h4_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título H — Estudios Geotécnicos"

CHUNKS = [
    # ---- Cierre de H.3 (Caracterización geotécnica del subsuelo) ----
    {
        "id": "NSR10-H-H_3_3_1_seleccion_muestras",
        "seccion": "H.3.3 / H.3.3.1 (Ensayos de laboratorio — selección de muestras)",
        "titulo": "Las muestras de campo deben ser seleccionadas por el ingeniero geotecnista, representativas y conservadas adecuadamente.",
        "texto": (
            "H.3.3 — ENSAYOS DE LABORATORIO. H.3.3.1 — SELECCIÓN DE "
            "MUESTRAS — Las muestras obtenidas de la exploración de "
            "campo deberán ser objeto de los manejos y cuidados que "
            "garanticen su representatividad y conservación. Las "
            "muestras para la ejecución de ensayos de laboratorio "
            "deberán ser seleccionadas por el ingeniero geotecnista y "
            "deberán corresponder a los diferentes materiales afectados "
            "por el proyecto."
        ),
    },
    {
        "id": "NSR10-H-H_3_3_2_tipo_numero_ensayos",
        "seccion": "H.3.3.2 (Ensayos de laboratorio — tipo y número de ensayos)",
        "titulo": "El ingeniero geotecnista define tipo/número de ensayos según el proyecto; deben cubrir clasificación, peso unitario, permeabilidad, compresibilidad y resistencia.",
        "texto": (
            "H.3.3.2 — TIPO Y NÚMERO DE ENSAYOS — El tipo y número de "
            "ensayos depende de las características propias de los "
            "suelos o materiales rocosos por investigar, del alcance del "
            "proyecto y del criterio del ingeniero geotecnista. El "
            "ingeniero geotecnista ordenará los ensayos de laboratorio "
            "que permitan conocer con claridad la clasificación, peso "
            "unitario y permeabilidad de las muestras escogidas. "
            "Igualmente los ensayos de laboratorio que ordene el "
            "ingeniero geotecnista deben permitir establecer con "
            "claridad las propiedades geomecánicas de compresibilidad y "
            "expansión de las muestras escogidas, así como las de "
            "esfuerzo-deformación y resistencia al corte ante cargas "
            "monotónicas. Los análisis de respuesta de sitio deben "
            "realizarse con resultados de ensayos de laboratorio que "
            "establezcan con claridad las propiedades esfuerzo "
            "deformación ante cargas cíclicas de los materiales de las "
            "muestras escogidas."
        ),
    },
    {
        "id": "NSR10-H-H_3_3_3_propiedades_basicas",
        "seccion": "H.3.3.3 / H.3.3.3.1 / H.3.3.3.2 (Propiedades básicas — suelos y rocas)",
        "titulo": "Propiedades básicas mínimas de suelos (peso unitario, humedad, clasificación, resistencia) y de rocas (peso unitario, compresión simple, alterabilidad).",
        "texto": (
            "H.3.3.3 — PROPIEDADES BÁSICAS — Las propiedades básicas "
            "para la caracterización de suelos y rocas son como mínimo "
            "las siguientes: H.3.3.3.1 — Propiedades básicas de los "
            "suelos — Las propiedades básicas mínimas de los suelos a "
            "determinar con los ensayos de laboratorio son: peso "
            "unitario, humedad y clasificación completa para cada uno de "
            "los estratos o unidades estratigráficas y sus distintos "
            "niveles de meteorización. Igualmente debe determinarse como "
            "mínimo las propiedades de resistencia en cada uno de los "
            "materiales típicos encontrados en el sitio mediante "
            "compresión simple o corte directo en suelos cohesivos, y "
            "corte directo o SPT en suelos granulares. H.3.3.3.2 — "
            "Propiedades básicas de las rocas — Las propiedades básicas "
            "mínimas de las rocas a determinar con los ensayos de "
            "laboratorio son: peso unitario, compresión simple (o carga "
            "puntual) y eventualmente la alterabilidad de este material "
            "mediante ensayos tipo desleimiento-durabilidad o similares."
        ),
    },
    {
        "id": "NSR10-H-H_3_3_4_caracterizacion_geomecanica",
        "seccion": "H.3.3.4 (Caracterización geomecánica detallada)",
        "titulo": "Propiedades mecánicas/hidráulicas detalladas (resistencia al corte, esfuerzo-deformación, compresibilidad, expansión, permeabilidad); G y ξ vía ensayos dinámicos.",
        "texto": (
            "H.3.3.4 — CARACTERIZACIÓN GEOMECÁNICA DETALLADA — Las "
            "propiedades mecánicas e hidráulicas del subsuelo tales "
            "como: resistencia al cortante, propiedades "
            "esfuerzo-deformación, compresibilidad, expansión, "
            "permeabilidad y otras que resulten pertinentes de acuerdo "
            "con la naturaleza geológica del área, se determinarán en "
            "cada caso mediante procedimientos aceptados de campo o "
            "laboratorio, debiendo el informe respectivo justificar su "
            "número y representatividad de manera precisa y coherente "
            "con el modelo geológico y geotécnico del sitio. Cuando por "
            "el análisis de las condiciones ambientales y físicas del "
            "sitio así se establezca, los procedimientos de ensayo deben "
            "precisarse y seleccionarse de tal modo que permitan "
            "determinar la influencia de la saturación, condiciones de "
            "drenaje y confinamiento, cargas cíclicas y en general "
            "factores que se consideren significativos sobre el "
            "comportamiento mecánico de los materiales investigados. "
            "Las propiedades dinámicas del suelo, y en particular el "
            "módulo de rigidez al cortante, G, y el porcentaje de "
            "amortiguamiento con respecto al crítico, ξ, a diferentes "
            "niveles de deformación, se determinarán en el laboratorio "
            "mediante ensayos de columna resonante, ensayo triaxial "
            "cíclico, corte simple cíclico u otro similar y técnicamente "
            "reconocido. Los resultados de estos ensayos se "
            "interpretarán siguiendo métodos y criterios reconocidos, de "
            "acuerdo con el principio de operación de cada uno de los "
            "aparatos. En todos los casos, se deberá tener presente que "
            "los valores de G y ξ obtenidos están asociados a los "
            "niveles de deformación impuestos en cada aparato y pueden "
            "diferir de los prevalecientes en el campo."
        ),
    },
    {
        "id": "NSR10-H-H_3_3_5_ensayos_campo",
        "seccion": "H.3.3.5 (Ejecución de ensayos de campo)",
        "titulo": "Pruebas de campo con equipos y metodologías reconocidas, respaldadas por correlaciones confiables e intervalos de confiabilidad establecidos.",
        "texto": (
            "H.3.3.5 — EJECUCIÓN DE ENSAYOS DE CAMPO — El ingeniero "
            "responsable del estudio podrá llevar a cabo pruebas de "
            "campo para la determinación de propiedades geomecánicas, en "
            "cuyo caso deberá realizarlos con equipos y metodologías de "
            "reconocida aceptación técnica, patronados y calibrados "
            "siempre y cuando, sus resultados e interpretaciones se "
            "respalden mediante correlaciones confiables y aceptadas con "
            "los ensayos convencionales, sustentadas en experiencias "
            "publicadas y se establezcan sus intervalos más probables de "
            "confiabilidad."
        ),
    },
    # ---- H.4 — Cimentaciones ----
    {
        "id": "NSR10-H-H_4_0_nomenclatura",
        "seccion": "H.4.0 (Nomenclatura del Capítulo H.4 — Cimentaciones)",
        "titulo": "F_SICP (factores de seguridad indirectos mínimos), τ_L (resistencia al cortante suelo/cimentación), σ_c, P_A, ψ.",
        "texto": (
            "CAPÍTULO H.4 — CIMENTACIONES. H.4.0 — NOMENCLATURA — "
            "F_SICP = factores de seguridad indirectos mínimos. "
            "τ_L = resistencia al cortante en la interfaz suelo / "
            "elemento de cimentación ≤ τ_f. σ_c = resistencia a "
            "compresión simple del material rocoso o del material del "
            "pilote, la que sea menor. P_A = presión atmosférica. "
            "ψ = factor empírico que puede tomarse como 0.5 para rocas "
            "arcillosas, 1.0 para rocas calcáreas o concreto y 2.0 para "
            "rocas arenosas."
        ),
    },
    {
        "id": "NSR10-H-H_4_1_generalidades",
        "seccion": "H.4.1 (Generalidades)",
        "titulo": "Toda edificación debe soportarse en materiales adecuados en resistencia/rigidez, nunca sobre capa vegetal/rellenos sueltos/materiales degradables; diseño empotrado en la base.",
        "texto": (
            "H.4.1 — GENERALIDADES — Toda edificación debe soportarse "
            "sobre el terreno en forma adecuada para sus fines de "
            "diseño, construcción y funcionamiento. En ningún caso puede "
            "apoyarse sobre la capa vegetal, rellenos sueltos, "
            "materiales degradables o inestables, susceptibles de "
            "erosión, socavación, licuación o arrastre por aguas "
            "subterráneas. La cimentación se debe colocar sobre "
            "materiales que presenten propiedades mecánicas adecuadas en "
            "términos de resistencia y rigidez, o sobre rellenos "
            "artificiales, que no incluyan materiales degradables, "
            "debidamente compactados. En el diseño de toda cimentación "
            "se deben considerar tanto los estados límite de falla, del "
            "suelo de soporte y de los elementos estructurales de la "
            "cimentación, como los estados límites de servicio. Los "
            "edificios se deben diseñar empotrados en su base para que "
            "los esfuerzos se transmitan en forma adecuada a la "
            "cimentación En los cálculos se tendrá en cuenta la "
            "interacción entre los diferentes elementos de la "
            "cimentación de la estructura y de las edificaciones "
            "vecinas, como analizar si hay superposición de bulbos de "
            "carga, los efectos de las excentricidades de los centros de "
            "gravedad y cargas que en conjunto se ocasionan. Los "
            "parámetros de diseño deben justificarse plenamente, con "
            "base en resultados provenientes de ensayos de campo y "
            "laboratorio."
        ),
    },
    {
        "id": "NSR10-H-H_4_2_1_2_zapatas_losas_falla_servicio",
        "seccion": "H.4.2 / H.4.2.1 / H.4.2.2 (Cimentaciones superficiales — estados límite de falla y de servicio)",
        "titulo": "Falla: métodos analíticos/empíricos, falla por cortante general/local/punzonamiento; servicio: asentamientos inmediatos/consolidación/sismo.",
        "texto": (
            "H.4.2 — CIMENTACIONES SUPERFICIALES - ZAPATAS Y LOSAS. "
            "H.4.2.1 — ESTADOS LÍMITES DE FALLA — El esfuerzo límite "
            "básico de falla de cimentaciones superficiales se calculará "
            "por métodos analíticos o empíricos, debidamente apoyados en "
            "experiencias documentadas, recurriendo a los métodos de la "
            "teoría de plasticidad y/o análisis de equilibrio límite que "
            "consideren los diversos mecanismos de falla compatibles con "
            "el perfil estratigráfico. Además de la falla por cortante "
            "general, se estudiarán las posibles fallas por cortante "
            "local, es decir aquellas que puedan afectar solamente una "
            "parte del suelo que soporta el cimiento, así como la falla "
            "por punzonamiento en suelos blandos. En el cálculo se "
            "deberá considerar lo siguiente: (a) Posición del nivel "
            "freático más desfavorable durante la vida útil de la "
            "edificación, (b) Excentricidades que haya entre el punto de "
            "aplicación de las cargas y resultantes y el centroide "
            "geométrico de la cimentación, (c) Influencia de estratos de "
            "suelos blandos bajo los cimientos, (d) Influencia de "
            "taludes próximos a los cimientos, (e) Suelos susceptibles a "
            "la pérdida parcial o total de su resistencia, por "
            "generación de presión de poros o deformaciones volumétricas "
            "importantes, bajo solicitaciones sísmicas (Véase el "
            "Capítulo H.7), (f) Existencia de galerías, cavernas, "
            "grietas u otras oquedades. H.4.2.2 — ESTADOS LÍMITES DE "
            "SERVICIO — La seguridad para los estados límite de servicio "
            "resulta del cálculo de asentamientos inmediatos, por "
            "consolidación, los asentamientos secundarios y los "
            "asentamientos por sismo. La evaluación de los asentamientos "
            "debe realizarse mediante modelos de aceptación generalizada "
            "empleando parámetros de deformación obtenidos a partir de "
            "ensayos de laboratorio o correlaciones de campo "
            "suficientemente apoyadas en la experiencia. Pueden "
            "utilizarse relaciones entre el módulo de elasticidad y el "
            "valor de la penetración estándar y la penetración con cono, "
            "con el soporte experimental adecuado."
        ),
    },
    {
        "id": "NSR10-H-H_4_2_asentamientos_calculo_admisible",
        "seccion": "H.4.2 (Cimentaciones superficiales — cálculo de asentamientos y H.4.2.3 capacidad admisible)",
        "titulo": "Asentamientos inmediatos por elasticidad, consolidación por migración de agua, diferenciales en varios sitios; capacidad admisible = menor entre falla reducida por FS y máximos admitidos.",
        "texto": (
            "Los asentamientos inmediatos bajo cargas estáticas se "
            "calcularán utilizando la teoría de la elasticidad. En "
            "suelos granulares se tomará en cuenta el incremento de la "
            "rigidez del suelo con la presión de confinamiento. La "
            "magnitud de las deformaciones permanentes que pueden "
            "presentarse bajo cargas sísmicas se podrá estimar con "
            "procedimientos de equilibrio límite para condiciones "
            "dinámicas. Los asentamientos por consolidación se producen "
            "por la migración gradual del agua hacia afuera de los "
            "suelos saturados, como respuesta a una sobre carga externa. "
            "Su cálculo se realizará con los parámetros determinados de "
            "las pruebas de consolidación unidimensional o triaxial "
            "realizadas con muestras inalteradas representativas del "
            "material existente bajo los cimientos. Los incrementos de "
            "presión a las diferentes profundidades, inducidos por la "
            "presión que los cimientos transmiten al suelo, se "
            "calcularán con la teoría de la elasticidad. La presión de "
            "contacto en los cimientos se estimará considerando "
            "hipótesis extremas de repartición de carga, o a partir de "
            "un análisis de interacción estática suelo-estructura. Para "
            "evaluar los asentamientos diferenciales de la cimentación y "
            "los inducidos en construcciones vecinas, los asentamientos "
            "se calcularán en un número de sitios ubicados dentro y "
            "fuera del área cargada. Para determinar los asentamientos "
            "por sismo hay que considerar las cargas verticales de los "
            "apoyos y las cargas resultantes de los momentos, "
            "especialmente en muros pantalla. El ingeniero estructural "
            "le suministrará al ingeniero geotecnista la información "
            "relativa al sismo para que se evalúe los asentamientos por "
            "este tipo de cargas (instantáneas) y los integre con los de "
            "rebotes, consolidaciones, etc. H.4.2.3 — CAPACIDAD "
            "ADMISIBLE — La capacidad admisible de diseño para la "
            "cimentación deberá ser el menor valor entre el esfuerzo "
            "límite de falla (Véase H.4.2.1), reducido por el factor de "
            "seguridad, y el que produzca asentamientos iguales a los "
            "máximos permitidos (Véase H.4.8). Esta capacidad debe ser "
            "claramente establecida en los informes geotécnicos."
        ),
    },
    {
        "id": "NSR10-H-H_4_3_cimentaciones_compensadas",
        "seccion": "H.4.3 / H.4.3.1 / H.4.3.2 / H.4.3.3 (Cimentaciones compensadas — falla, servicio, capacidad admisible)",
        "titulo": "Verificar flotación con celdas bajo nivel freático llenas de agua; asentamientos inmediatos/transitorios/por sismo/por carga neta; capacidad admisible según H.4.2.3.",
        "texto": (
            "H.4.3 — CIMENTACIONES COMPENSADAS. H.4.3.1 — ESTADOS "
            "LÍMITES DE FALLA — La estabilidad de las cimentaciones "
            "compensadas se verificará como se indica en H.6.2.1. Se "
            "comprobará además que no pueda ocurrir flotación de la "
            "cimentación durante ni después de la construcción, para lo "
            "cual se deberá considerar una posición conservadora del "
            "nivel freático. Las celdas de la losa de cimentación que "
            "estén por debajo del nivel freático deberán considerarse "
            "como llenas de agua, y el peso de esta deberá adicionarse "
            "al de la subestructura, a menos que se tomen precauciones "
            "para que esto no suceda. Se prestará especial atención a la "
            "evaluación de la carga de falla por cortante local, o "
            "cortante general del suelo, bajo la combinación de carga "
            "que considere el sismo. H.4.3.2 — ESTADOS LÍMITES DE "
            "SERVICIO — Para estas cimentaciones se deberá calcular: (a) "
            "Los asentamientos inmediatos debidos a la carga total "
            "transmitida al suelo por la cimentación, incluyendo los "
            "debidos a la recarga del suelo descargado al realizar la "
            "excavación (Véase el Capítulo H.6), (b) Los asentamientos "
            "transitorios y permanentes del suelo de cimentación bajo la "
            "hipótesis de cargas estáticas permanentes combinadas con "
            "carga sísmica cíclica, (c) Los asentamientos debidos al "
            "incremento o reducción neta de carga en el contacto "
            "cimentación-suelo, (d) Los asentamientos inmediatos, de "
            "consolidación y los debidos a sismo se calcularán como se "
            "indica en H.4.2.2. La técnica empleada en la realización de "
            "la excavación (Véase H.8.3) será, en gran medida, la "
            "responsable de que se obtengan resultados de asentamientos "
            "acordes a los valores calculados. H.4.3.3 — CAPACIDAD "
            "ADMISIBLE — La capacidad admisible se determinará como se "
            "indica en H.4.2.3."
        ),
    },
    {
        "id": "NSR10-H-H_4_4_1_cimentaciones_pilotes_falla",
        "seccion": "H.4.4 / H.4.4.1 (Cimentaciones con pilotes — estados límite de falla)",
        "titulo": "Falla del sistema suelo-zapatas/suelo-pilotes o combinada; carga de falla = menor entre pilotes individuales, bloque de terreno, y grupos con eficiencia.",
        "texto": (
            "H.4.4 — CIMENTACIONES CON PILOTES — La capacidad de un "
            "pilote individual debe evaluarse considerando "
            "separadamente la fricción lateral y la resistencia por la "
            "punta con las teorías convencionales de la mecánica de "
            "suelos. H.4.4.1 — ESTADOS LÍMITES DE FALLA — Se deberá "
            "verificar que la cimentación diseñada resulte suficiente "
            "para asegurar la estabilidad de la edificación en alguna de "
            "las siguientes condiciones: (a) Falla del sistema "
            "suelo-zapatas, o suelo-losa de cimentación, despreciando la "
            "capacidad de los pilotes, como se indica en H.4.2.1, (b) "
            "Falla del sistema suelo-pilotes, despreciando la capacidad "
            "del sistema suelo-zapatas o suelo-losa, para lo cual debe "
            "considerarse que la carga de falla del sistema es la menor "
            "de los siguientes valores: 1) suma de las capacidades de "
            "carga de los pilotes individuales; 2) capacidad de carga de "
            "un bloque de terreno cuya geometría sea igual a la "
            "envolvente del conjunto de pilotes; 3) suma de las "
            "capacidades de carga de los diversos grupos de pilotes en "
            "que pueda subdividirse la cimentación, teniendo en cuenta "
            "la posible reducción por la eficiencia de grupos de "
            "pilotes. La capacidad de carga bajo cargas excéntricas se "
            "evaluará calculando la distribución de cargas en cada "
            "pilote mediante la teoría de la elasticidad, o a partir de "
            "un análisis de interacción suelo-estructura. No se tendrá "
            "en cuenta la capacidad de carga de los pilotes sometidos a "
            "tracción, a menos que se hayan diseñado y construido con "
            "ese fin. Además de la capacidad a cargas de gravedad se "
            "comprobará la capacidad del suelo para soportar los "
            "esfuerzos inducidos por los pilotes o pilas sometidos a "
            "fuerzas horizontales, así como la capacidad de estos "
            "elementos para transmitir dichas solicitaciones "
            "horizontales. Para solicitaciones sísmicas se deberá tener "
            "en cuenta que sobre los pilotes actúa, además de la carga "
            "sísmica horizontal del edificio, la carga sísmica sobre el "
            "suelo que está en contacto con el pilote. Se podrán "
            "presentar casos en que los pilotes o pilas proyectados "
            "trabajen por punta y fricción, en estos casos se deben "
            "hacer los respectivos análisis para compatibilizar las "
            "deformaciones de los dos estados límites con factores de "
            "seguridad diferenciales."
        ),
    },
    {
        "id": "NSR10-H-H_4_4_2_3_pilotes_servicio_friccion",
        "seccion": "H.4.4.2 / H.4.4.3 (Cimentaciones con pilotes — estados límite de servicio y pilotes de fricción para control de asentamientos)",
        "titulo": "Asentamientos por penetración/deformación bajo carga y fricción negativa; pilotes de fricción como complemento no toman cargas sísmicas.",
        "texto": (
            "H.4.4.2 — ESTADOS LÍMITES DE SERVICIO — Los asentamientos "
            "de cimentaciones con pilotes de fricción bajo cargas de "
            "gravedad se estimarán considerando la penetración de los "
            "mismos y las deformaciones del suelo que lo soporta, así "
            "como la fricción negativa. En el cálculo de los movimientos "
            "anteriores se tendrá en cuenta las excentricidades de "
            "carga. Para pilotes por punta o pilas los asentamientos se "
            "calcularán teniendo en cuenta la deformación propia bajo la "
            "acción de las cargas, incluyendo si es el caso fricción "
            "negativa, y la de los materiales bajo el nivel de apoyo de "
            "las puntas. Deberá comprobarse que no resulten excesivos el "
            "desplazamiento lateral ni el giro transitorio de la "
            "cimentación bajo la fuerza cortante y el momento de "
            "volcamiento sísmico. Las deformaciones permanentes bajo la "
            "condición de carga que incluya el efecto del sismo se "
            "podrán estimar con métodos de equilibrio límite para "
            "condiciones dinámicas. H.4.4.3 — USO DE PILOTES DE "
            "FRICCIÓN PARA CONTROL DE ASENTAMIENTOS — Cuando se "
            "utilicen pilotes de fricción como complemento de un sistema "
            "de cimentación parcialmente compensada para reducir "
            "asentamientos en suelos cohesivos blandos, transfiriendo "
            "parte de la carga a los estratos más profundos, los pilotes "
            "generalmente no tienen la capacidad para soportar por sí "
            "solos el peso de la edificación ya que se diseñan para "
            "trabajar al límite de falla en condiciones estáticas. Para "
            "determinar la capacidad admisible, deberá entonces tenerse "
            "en cuenta que estos pilotes no pueden tomar las cargas "
            "sísmicas de la edificación. Adicionalmente deberá "
            "considerarse la posibilidad que las zapatas o losa de "
            "cimentación puedan perder el sustento del suelo de apoyo. "
            "En todos los casos se verificará que la cimentación no "
            "exceda los estados límites de falla y servicio. En ese "
            "caso, el espacio que se deje entre la punta de los pilotes "
            "de fricción y toda capa dura subyacente deberá ser "
            "suficiente para que en ninguna condición puedan los pilotes "
            "llegar a apoyarse en esta capa como consecuencia de la "
            "consolidación del estrato en que se colocaron. A criterio "
            "del ingeniero geotecnista se puede considerar la "
            "posibilidad de utilizar los pilotes de control de "
            "asentamientos para mejoramiento de la capacidad portante "
            "del conjunto."
        ),
    },
    {
        "id": "NSR10-H-H_4_5_cimentaciones_roca",
        "seccion": "H.4.5 / H.4.5.1 / H.4.5.2 (Cimentaciones en roca — falla y servicio)",
        "titulo": "Macizo rocoso evaluado como medio continuo equivalente y/o discontinuo; estado límite = el menor de ambos análisis; servicio según continuidad del macizo.",
        "texto": (
            "H.4.5 — CIMENTACIONES EN ROCA — Para cimentaciones en "
            "macizos rocosos se seguirán los mismos lineamientos "
            "anteriores, teniendo en cuenta que la resistencia y rigidez "
            "de los macizos rocosos son siempre menores que los de las "
            "muestras de roca (material rocoso) y adoptando los "
            "siguientes: H.4.5.1 — ESTADOS LÍMITES DE FALLA — el macizo "
            "rocoso debe evaluarse por medio de dos modelos "
            "complementarios: (a) Considerar el macizo rocoso como un "
            "medio continuo equivalente, con envolvente de resistencia "
            "(esfuerzo cortante vs esfuerzo normal efectivo) curva o con "
            "parámetros lineales equivalentes para el intervalo de "
            "esfuerzos que se esté considerando. (b) Considerar el "
            "macizo rocoso como un medio discontinuo, para lo cual se "
            "deberán analizar los mecanismos de falla cinemáticamente "
            "posibles por las discontinuidades. (c) El estado límite "
            "será el menor que resulte de los dos análisis anteriores. "
            "(d) En los casos extremos de macizos rocosos muy "
            "fracturados o casi sin discontinuidades no sería necesario "
            "evaluar el mecanismo de falla con las características "
            "esfuerzo-deformación de las discontinuidades y mecanismos "
            "cinemáticamente posibles. H.4.5.2 — ESTADOS LÍMITES DE "
            "SERVICIO — (a) Si el macizo rocoso se considera continuo, "
            "debe evaluarse como un medio elástico, con módulos de "
            "deformación apropiados al estado de esfuerzos previsto, "
            "estimados bien sea de relaciones empíricas con los sistemas "
            "de clasificación, ensayos geofísicos o con ensayos de "
            "placa. (b) Si el macizo rocoso se considera discontinuo, se "
            "debe hacer el análisis del mecanismo de falla con las "
            "características esfuerzo-deformación de las discontinuidades y "
            "mecanismos cinemáticamente posibles apropiados."
        ),
    },
    {
        "id": "NSR10-H-H_4_6_profundidad_cimentacion",
        "seccion": "H.4.6 (Profundidad de cimentación)",
        "titulo": "Profundidad mínima debe evitar erosión/socavación por tubificación, cambios de humedad en suelos arcillosos, y efectos de raíces de árboles.",
        "texto": (
            "H.4.6 — PROFUNDIDAD DE CIMENTACIÓN — La profundidad mínima "
            "de cimentación para los cálculos de capacidad debe "
            "contemplar los siguientes aspectos, además de los "
            "incluidos en H.4.1 - Generalidades. (a) La profundidad tal "
            "que se elimine toda posibilidad de erosión o meteorización "
            "acelerada del suelo, arrastre del mismo por tubificación "
            "causada por flujo de las aguas superficiales o subterráneas "
            "de cualquier origen. (b) En los suelos arcillosos, la "
            "profundidad de las cimentaciones debe llevarse hasta un "
            "nivel tal que no haya influencia de los cambios de humedad "
            "inducidos por agentes externos (Véase el capítulo H-9). (c) "
            "Es preciso diseñar las cimentaciones superficiales en forma "
            "tal que se eviten los efectos de las raíces principales de "
            "los árboles próximos a la edificación o alternativamente se "
            "deben dar recomendaciones en cuanto a arborización (Véase "
            "el capítulo H-9)."
        ),
    },
    {
        "id": "NSR10-H-H_4_7_1_factores_seguridad_indirectos_tabla1",
        "seccion": "H.4.7 / H.4.7.1 (Factores de seguridad indirectos — Tabla H.4.7-1)",
        "titulo": "Tabla H.4.7-1: FSICP mínimo 3.0 (carga muerta+viva normal), 2.5 (máxima), 1.5 (con sismo pseudo-estático).",
        "texto": (
            "H.4.7 — FACTORES DE SEGURIDAD INDIRECTOS — Para "
            "cimentaciones se aconsejan los siguientes factores de "
            "seguridad indirectos mínimos: H.4.7.1 — CAPACIDAD PORTANTE "
            "DE CIMIENTOS SUPERFICIALES Y CAPACIDAD PORTANTE DE PUNTA DE "
            "CIMENTACIONES PROFUNDAS — Para estos casos se aconsejan los "
            "siguientes valores: Tabla H.4.7-1 — Factores de Seguridad "
            "Indirectos F_SICP Mínimos (Condición — F_SICP Mínimo "
            "Diseño): Carga Muerta + Carga Viva Normal — 3.0. Carga "
            "Muerta + Carga Viva Máxima — 2.5. Carga Muerta + Carga Viva "
            "Normal + Sismo de Diseño Seudo estático — 1.5. En todo caso "
            "se deberá demostrar que los valores de F_SB directos "
            "equivalentes no son inferiores a los de la Tabla H.2.4-1."
        ),
    },
    {
        "id": "NSR10-H-H_4_7_2_friccion_pilotes_ecuaciones",
        "seccion": "H.4.7.2 (Capacidad portante por fricción de cimentaciones profundas — ecuaciones H.4.7-1 a -4)",
        "titulo": "FSL=τL/τA; τL=(2/3)τF por defecto, o τL=ατF (α según fórmula con Su/PA) para H.2-6, o τL=ψ(σc/2PA)^0.5 para pilotes/caissons en roca.",
        "texto": (
            "H.4.7.2 — CAPACIDAD PORTANTE POR FRICCIÓN DE CIMENTACIONES "
            "PROFUNDAS — (a) En este caso el Factor de Seguridad está "
            "definido por: F_SL = τ_L / τ_A (H.4.7-1), en la cual τ_L = "
            "resistencia al cortante en la interfaz suelo / elemento de "
            "cimentación ≤ τ_f. (b) A menos que se demuestre con ensayos "
            "para la obra en estudio, se tomará, para la ecuación "
            "H.4.7-1: τ_L = 2/3·τ_F (H.4.7-2). (c) En el caso de la "
            "ecuación H.2-6 (τ_F = S_U), se deberá usar τ_L = α·τ_F = "
            "α·S_u (H.4.7-3), en la cual α = 0.2 + 0.8·exp[0.35 − "
            "(2S_u/P_A)] ≤ 1.0 (o una expresión con tendencia similar). "
            "Y se podrán usar los valores de F_SL iguales a los de F_SB "
            "de la tabla H.2.4-1. (d) En el caso de pilotes o caissons "
            "en roca, se debe tomar τ_L con una formulación apropiada, "
            "tal como τ_L = ψ·[σ_c/2P_A]^−0.5 (H.4-7-4), en la cual σ_c "
            "= resistencia a compresión simple del material rocoso o del "
            "material del pilote, la que sea menor. P_A = presión "
            "atmosférica. ψ = factor empírico que puede tomarse como 0.5 "
            "para rocas arcillosas, 1.0 para rocas calcáreas o concreto "
            "y 2.0 para rocas arenosas. Y se podrán usar valores de "
            "F_SL iguales a los de F_SB de la tabla H.2.4-1."
        ),
    },
    {
        "id": "NSR10-H-H_4_7_3_pruebas_carga_tabla2",
        "seccion": "H.4.7.3 (Capacidad portante por pruebas de carga y factores de seguridad — Tabla H.4.7-2)",
        "titulo": "Tabla H.4.7-2: número mínimo de ensayos de carga por categoría (Baja≥1, Media≥2, Alta≥3, Especial≥5), permite reducir FSICP hasta 80% del valor mínimo.",
        "texto": (
            "H.4.7.3 — CAPACIDAD PORTANTE POR PRUEBAS DE CARGA Y "
            "FACTORES DE SEGURIDAD — La capacidad portante última de "
            "cimentaciones profundas se podrá calcular alternativamente, "
            "a partir de pruebas de carga ejecutadas y en número "
            "suficiente de pilas o pilotes de acuerdo con lo señalado en "
            "la tabla H.4.7-2. En este caso los factores de seguridad "
            "mínimos podrán reducirse sin que lleguen a ser inferiores "
            "al 80% de los indicados en la tabla 4.7.1. Tabla H.4.7-2 — "
            "Número Mínimo de Ensayos de Carga en Pilotes o Pilas para "
            "Reducir F_SICP (Categoría — No de Pruebas): Baja — ≥1. "
            "Media — ≥2. Alta — ≥3. Especial — ≥5."
        ),
    },
    {
        "id": "NSR10-H-H_4_8_1_2_asentamientos_inmediatos_consolidacion",
        "seccion": "H.4.8 / H.4.8.1 / H.4.8.2 (Asentamientos — inmediatos y por consolidación)",
        "titulo": "Servicio evaluado por asentamientos inmediatos/consolidación/secundarios/sismo; consolidación = migración de agua por sobrecarga externa (primaria).",
        "texto": (
            "H.4.8 — ASENTAMIENTOS — La seguridad para el estado límite "
            "de servicio resulta del cálculo de asentamientos "
            "inmediatos, por consolidación, los asentamientos "
            "secundarios y los asentamientos por sismo. La evaluación de "
            "los asentamientos debe realizarse mediante modelos de "
            "aceptación generalizada empleando parámetros de deformación "
            "obtenidos a partir de ensayos de laboratorio o "
            "correlaciones de campo suficientemente apoyadas en la "
            "experiencia. En cada caso debe verificarse la ocurrencia y "
            "la pertinencia de los casos de asentamiento descritos en "
            "este numeral. H.4.8.1 — ASENTAMIENTOS INMEDIATOS — Los "
            "asentamientos inmediatos dependen de las propiedades de los "
            "suelos a bajas deformaciones, en cuyo caso puede aceptarse "
            "su comportamiento elástico, y de la rigidez y extensión del "
            "cimiento mismo. El procedimiento se establece enseguida "
            "para suelos cohesivos y para suelos granulares en forma "
            "separada. H.4.8.2 — ASENTAMIENTOS POR CONSOLIDACIÓN — Los "
            "asentamientos por consolidación se producen por la "
            "migración del agua hacia afuera de los suelos saturados, "
            "como respuesta a una sobre carga externa. Se define también "
            "como consolidación primaria."
        ),
    },
    {
        "id": "NSR10-H-H_4_8_3_4_5_asentamientos_secundarios_totales_roca",
        "seccion": "H.4.8.3 / H.4.8.4 / H.4.8.5 (Asentamientos secundarios, totales, y en macizos rocosos)",
        "titulo": "Secundarios = deformación a esfuerzo efectivo constante (materia orgánica); totales = suma de todos; en roca continua sin inmediatos/consolidación, solo secundarios si hay materia orgánica.",
        "texto": (
            "H.4.8.3 — ASENTAMIENTOS SECUNDARIOS — La consolidación "
            "secundaria puede definirse como la deformación en el "
            "tiempo que ocurre esencialmente a un esfuerzo efectivo "
            "constante. No obstante, las deformaciones propias de la "
            "consolidación primaria pueden coincidir en el tiempo con "
            "las de la consolidación secundaria. Debe, en consecuencia, "
            "adelantarse el programa de laboratorio que permita "
            "comprobar la posible ocurrencia del fenómeno. Se estima que "
            "materiales con alto contenido orgánico presentan este "
            "fenómeno. H.4.8.4 — ASENTAMIENTOS TOTALES — Son la suma de "
            "asentamientos inmediatos, por consolidación y secundarios, "
            "cuando estos últimos son importantes. H.4.8.5 — "
            "ASENTAMIENTOS EN MACIZOS ROCOSOS — En este caso para el "
            "cálculo de asentamientos se deberá tomar el macizo rocoso "
            "como un medio elástico, isotrópico o anisotrópico según sea "
            "el caso, si se considera como un medio continuo o con las "
            "deformaciones por las discontinuidades, en el caso de "
            "considerar el macizo rocoso como un medio discontinuo. No "
            "se considerarán asentamientos inmediatos ni por "
            "consolidación, pero, a juicio del Ingeniero responsable, se "
            "deberían estimar asentamientos secundarios los cuales se "
            "pueden presentar en macizos rocosos de rocas arcillosas, "
            "calcáreas o con alto contenido orgánico."
        ),
    },
    {
        "id": "NSR10-H-H_4_9_1_2_efectos_asentamientos_totales",
        "seccion": "H.4.9 / H.4.9.1 / H.4.9.2 (Efectos de los asentamientos — clasificación y límites de asentamientos totales)",
        "titulo": "Máximo/diferencial/giro; límites totales a 20 años: 30cm aisladas, 15cm entre medianeros, sin afectar funcionalidad de conducciones/accesos.",
        "texto": (
            "H.4.9 — EFECTOS DE LOS ASENTAMIENTOS. H.4.9.1 — "
            "CLASIFICACIÓN — Se deben calcular los distintos tipos de "
            "asentamientos que se especifican a continuación: (a) "
            "Asentamiento máximo — Definido como el asentamiento total "
            "de mayor valor entre todos los producidos en la "
            "cimentación. (b) Asentamiento diferencial — Definido como "
            "la diferencia entre los valores de asentamiento "
            "correspondientes a dos partes diferentes de la estructura. "
            "(c) Giro — Definida como la rotación de la edificación, "
            "sobre el plano horizontal, producida por asentamientos "
            "diferenciales de la misma. H.4.9.2 — LÍMITES DE "
            "ASENTAMIENTOS TOTALES — Los asentamientos totales "
            "calculados a 20 años se deben limitar a los siguientes "
            "valores: (a) Para construcciones aisladas 30 cm, siempre y "
            "cuando no se afecten la funcionalidad de conducciones de "
            "servicios y accesos a la construcción. (b) Para "
            "construcciones entre medianeros 15 cm, siempre y cuando no "
            "se afecten las construcciones e instalaciones vecinas."
        ),
    },
    {
        "id": "NSR10-H-H_4_9_3_tabla1_limites_diferenciales",
        "seccion": "H.4.9.3 (Límites de asentamientos diferenciales — Tabla H.4.9-1)",
        "titulo": "Δmax/ℓ: 1/1000 muros con acabados susceptibles, 1/500 muros de carga concreto/mampostería, 1/300 pórticos concreto sin acabados, 1/160 estructura metálica.",
        "texto": (
            "H.4.9.3 — LÍMITES DE ASENTAMIENTOS DIFERENCIALES — Los "
            "asentamientos diferenciales calculados se deben limitar a "
            "los valores fijados en la tabla H.4.9-1, expresados en "
            "función de ℓ, distancia entre apoyos o columnas, de acuerdo "
            "con el tipo de construcción. Tabla H.4.9-1 — Valores "
            "máximos de asentamientos diferenciales calculados, "
            "expresados en función de la distancia entre apoyos o "
            "columnas, ℓ (Tipo de construcción — Δmax): (a) Edificaciones "
            "con muros y acabados susceptibles de dañarse con "
            "asentamientos menores — ℓ/1000. (b) Edificaciones con muros "
            "de carga en concreto o en mampostería — ℓ/500. (c) "
            "Edificaciones con pórticos en concreto, sin acabados "
            "susceptibles de dañarse con asentamientos menores — ℓ/300. "
            "(d) Edificaciones en estructura metálica, sin acabados "
            "susceptibles de dañarse con asentamientos menores — ℓ/160."
        ),
    },
    {
        "id": "NSR10-H-H_4_9_4_limites_giro",
        "seccion": "H.4.9.4 (Límites de giro)",
        "titulo": "Giros calculados limitados a valores que no produzcan efectos estéticos/funcionales ni disminuyan el valor comercial; máximo ℓ/250.",
        "texto": (
            "H.4.9.4 — LÍMITES DE GIRO — Los giros calculados deben "
            "limitarse a valores que no produzcan efectos estéticos o "
            "funcionales que impidan o perjudiquen el funcionamiento "
            "normal de la edificación, amenacen su seguridad, o "
            "disminuyan el valor comercial de la misma. En ningún caso "
            "localmente pueden sobrepasar de ℓ/250."
        ),
    },
    {
        "id": "NSR10-H-H_4_10_diseno_estructural_cimentacion",
        "seccion": "H.4.10 (Diseño estructural de la cimentación)",
        "titulo": "Excentricidades entre cargas resultantes y centroide geométrico; losas: presiones de contacto en equilibrio; pilotes diseñados para transporte/izado/hinca.",
        "texto": (
            "H.4.10 — DISEÑO ESTRUCTURAL DE LA CIMENTACIÓN — Para el "
            "diseño estructural de toda cimentación deben calcularse las "
            "excentricidades que haya entre el punto de aplicación de "
            "las cargas y resultantes y el centroide geométrico de la "
            "cimentación. Dichas excentricidades tienen que tenerse en "
            "cuenta en el cálculo de la capacidad ante falla, capacidad "
            "admisible y asentamientos totales, diferenciales y giros. "
            "Las losas de cimentación deben diseñarse de tal manera que "
            "las resultantes de las cargas estáticas aplicadas coincidan "
            "con el centroide geométrico de la losa. Para obtener la "
            "precisión necesaria en el cálculo de los centros de "
            "gravedad y de empujes de la losa, debe considerarse todo el "
            "conjunto de cargas reales que actúan sobre la losa, "
            "incluyendo en ellos las de los muros interiores y "
            "exteriores, acabados, excavaciones adyacentes a la losa, "
            "sobrecarga neta causada por los edificios vecinos y la "
            "posibilidad de variación de los niveles de aguas "
            "subterráneas. Las presiones de contacto calculadas deben "
            "ser tales que las deformaciones diferenciales del suelo "
            "calculadas con ellas coincidan aproximadamente con la del "
            "sistema subestructura superestructura. En su cálculo se "
            "acepta suponer que el medio es elástico, y se pueden usar "
            "las soluciones analíticas existentes o métodos numéricos. "
            "Se acepta cualquier distribución de presiones de contacto "
            "que satisfaga las siguientes condiciones: (a) Que exista "
            "equilibrio local y general entre las presiones de contacto "
            "y las fuerzas internas en la subestructura, y las fuerzas y "
            "momentos transmitidos a ésta por la superestructura, (b) "
            "Que los asentamientos diferenciales inmediatos más los de "
            "consolidación calculados con las presiones de contacto sean "
            "de magnitud admisible (H.4.9), (c) Que las deformaciones "
            "diferenciales instantáneas más las de largo plazo, del "
            "sistema subestructura-superestructura, sean de magnitud "
            "admisible (H.4.9). La distribución de presiones de contacto "
            "podrá determinarse para las diferentes combinaciones de "
            "carga a corto y largo plazos, con base en simplificaciones "
            "e hipótesis conservadoras, o mediante análisis de "
            "interacción suelo-estructura. Los pilotes y sus conexiones "
            "se diseñarán para poder soportar los esfuerzos resultantes "
            "de las cargas verticales y horizontales consideradas en el "
            "diseño de la cimentación, y las que se presenten durante el "
            "transporte, izado e hinca. Los pilotes deberán ser capaces "
            "de soportar estructuralmente la carga que corresponde a su "
            "estado límite de falla. Los pilotes de concreto, de acero y "
            "de madera, deberán cumplir con los requisitos estipulados "
            "en el Título C, F y G relativos al diseño y construcción de "
            "estructuras en estos tipos de materiales. Los pilotes "
            "metálicos deberán protegerse contra corrosión al menos en "
            "el tramo comprendido entre la cabeza y la profundidad a la "
            "que se estime el máximo descenso del nivel freático. "
            "Siempre se deben analizar las interacciones que se "
            "presentan con las excavaciones vecinas, limitando la "
            "capacidad portante total o utilizando pilotes de "
            "mejoramiento del suelo."
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

    print(f"\nOK: {len(rows)} chunks verbatim de H.3.3+H.4 cargados. H.3 y H.4 quedan COMPLETOS.")


if __name__ == "__main__":
    main()
