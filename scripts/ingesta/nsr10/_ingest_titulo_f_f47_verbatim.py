"""
NSR-10 Titulo F, Capitulo F.4 (Estructuras de Acero con Perfiles de
Lamina Formada en Frio) -- F.4.7 (TABLEROS METALICOS PARA TRABAJO EN
SECCION COMPUESTA) COMPLETO. Octava pieza de F.4/F.5.

F.4.7.1 (Alcance), F.4.7.2 (Materiales -- Tabla F.4.7.2-1 tolerancias,
Tabla F.4.7.2-2 espesores, acabados), F.4.7.3 (Diseno del tablero
como formaleta -- Figura F.4.7.3-1 diagramas de carga/momento/
deflexion/reaccion para luz simple/dos luces/tres luces continuas,
DEA, DCCR, deflexiones, longitud minima de apoyo), F.4.7.4
(Almacenamiento en sitio e instalacion -- bordes a tope, anclaje,
soldadura, sujetadores mecanicos), F.4.7.5 (Diseno del tablero y
concreto como unidad compuesta -- ensayos, concreto, deflexiones,
refuerzo por retraccion, flexion DEA/DCCR con ecuaciones F.4.7.5-1 a
-4, conectores de cortante F.4.7.5-5, cortante F.4.7.5-6/-7 con
Figura F.4.7.5-1, cortante+momento combinados DEA/DCCR F.4.7.5-8 a
-10), F.4.7.6 (Procedimiento constructivo -- apuntalamiento, limpieza,
vaciado), F.4.7.7 (Consideraciones adicionales -- estacionamientos,
voladizos, vigas en seccion compuesta, cargas concentradas con
ecuaciones F.4.7.7-1 a -7 y Figura F.4.7.7-1, tuberia).

Con esto F.4.7 queda COMPLETO. F.4.8 (Especificaciones para
construccion de entramados de acero formado en frio, sistemas de
construccion en seco y entramados de cerchas) arranca justo despues,
en F-411 -- no es parte de este chunk, queda para otra sesion.

CHUNKS escritos en piezas chicas, re-trocheadas programaticamente al
final con VERIFICACION REAL de tokens (no solo estimacion por
caracteres) via _resplit_titulo_f_f47_por_limite_tokens.py -- mismo
metodo que F.4.6, el unico confiable segun el hallazgo de auditoria
de F.4.3/F.4.4/F.4.5 (ver memoria privada del usuario,
project_construdata_limite_tokens_embeddings).

Fuente: NSR-10-982-1082.pdf (Drive id 1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze),
pagina F-401 (ultima pagina de ese PDF); y NSR-10-1083-1182.pdf (Drive
id 1XeyIKw992yoJAD1kgjmYJ5qEA70R85Gi), paginas F-402 a F-410 (paginas
PDF 1-9). Confirmada continuidad exacta entre ambos PDFs (F-401 ->
F-402 sin salto), leidas visualmente pagina por pagina.

Uso: python _ingest_titulo_f_f47_verbatim.py
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "NSR-10 Título F — Estructuras Metálicas"

CHUNKS = [
    {
        "id": "NSR10-F-F_4_7_intro_alcance",
        "seccion": "F.4.7 / F.4.7.1 (Tableros metálicos para trabajo en sección compuesta — intro y alcance)",
        "titulo": "Aplica a losas/diafragmas con tablero metálico y vaciado de concreto; tablero actúa como formaleta permanente y refuerzo positivo a flexión.",
        "texto": (
            "F.4.7 — TABLEROS METÁLICOS PARA TRABAJO EN SECCIÓN "
            "COMPUESTA — Las disposiciones de esta parte del Reglamento "
            "se aplican a losas o diafragmas diseñados y construidos "
            "con un tablero metálico sobre el cual se hace un vaciado "
            "en concreto. Todo lo estipulado en esta sección está de "
            "acuerdo con los numerales F.4.1 a F.4.5 de esta norma, "
            "excepto donde se indique lo contrario. Los planos deben "
            "especificar claramente la solución técnica del sistema y "
            "mostrar los detalles de instalación así, como los "
            "accesorios a utilizar. F.4.7.1 — ALCANCE — Esta parte del "
            "Reglamento se refiere a tableros de acero para entrepisos "
            "de comportamiento compuesto. El tablero es formado en "
            "frío y actúa como una formaleta permanente y como el "
            "refuerzo positivo a flexión para el concreto estructural. "
            "Cuando se sujeta adecuadamente, el tablero en acero "
            "también actúa como una plataforma de trabajo para las "
            "diferentes actividades de la construcción. Después que el "
            "concreto ha curado genera un vínculo con el tablero en "
            "acero debido a la geometría del panel metálico, medios "
            "mecánicos, adherencia superficial o por una combinación "
            "de todos estos medios."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_2_materiales_tolerancias",
        "seccion": "F.4.7.2 / F.4.7.2.1 (Materiales — fluencia mínima, espesor, Tabla F.4.7.2-1 tolerancias)",
        "titulo": "Fy mínimo 230 MPa, espesor mínimo tipo 22 (0.71mm); Tabla F.4.7.2-1: tolerancias de longitud, espesor, ancho, flecha, escuadra.",
        "texto": (
            "F.4.7.2 — MATERIALES — El tablero de acero para entrepisos "
            "de comportamiento compuesto debe ser fabricado siguiendo "
            "los lineamientos estipulados en las secciones F.4.1 a "
            "F.4.5 de esta norma, a menos que se indique algo diferente "
            "en esta sección. El acero utilizado para su formación debe "
            "tener un esfuerzo mínimo de fluencia de 230 MPa (33 ksi). "
            "El espesor mínimo de la lámina, aceptado para fabricación "
            "del tablero metálico de trabajo en sección compuesta, "
            "corresponde a un espesor de acero base de 0.71 mm (tipo o "
            "calibre 22), de acuerdo con la sección F.4.7.2.1 y la "
            "tabla F.4.7.2-2. F.4.7.2.1 — Tolerancias — Las tolerancias "
            "aplicables en la fabricación del tablero se encuentran "
            "consignadas en la tabla F.4.7.2-1: Tabla F.4.7.2-1 — "
            "Tolerancias de fabricación del tablero. Longitud del "
            "panel: ±12 mm. Espesor: no debe ser menor al 95% del "
            "espesor de diseño. Ancho útil del panel: +20 mm, −10 mm. "
            "Flecha y curvatura: 6 mm en 3.00 m de longitud. Extremo "
            "del panel fuera de escuadra: 10 mm por metro de ancho del "
            "panel. Si la literatura publicada del producto no muestra "
            "el espesor del material sin recubrimiento en milímetros (o "
            "décimas de pulgada), pero sí presenta en una lista los "
            "números del tipo o calibre, el espesor del acero antes del "
            "recubrimiento en pintura o metal (espesor base de acuerdo "
            "con la sección F.4.1.2.4) deberá estar en concordancia con "
            "lo estipulado en la tabla F.4.7.2-2."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_2_2_tabla2_espesores_acabados",
        "seccion": "Tabla F.4.7.2-2 (Espesores de diseño y mínimos) + F.4.7.2.2 (Acabados)",
        "titulo": "Tabla espesores tipo 22 a 16 (0.75-1.52mm diseño / 0.71-1.44mm mínimo); acabado mínimo galvanizado G60 (Z180), NTC 4011.",
        "texto": (
            "Tabla F.4.7.2-2 — Espesores de diseño y mínimos aceptables "
            "del material antes del recubrimiento (Tipo/calibre — "
            "espesor de diseño mm/pulg — espesor mínimo mm/pulg). "
            "22: 0.75/0.0295 — 0.71/0.0280. 21: 0.84/0.0329 — "
            "0.79/0.0311. 20: 0.91/0.0358 — 0.86/0.0340. 19: "
            "1.06/0.0418 — 1.01/0.0398. 18: 1.20/0.0474 — 1.14/0.0449. "
            "17: 1.37/0.0538 — 1.30/0.0512. 16: 1.52/0.0598 — "
            "1.44/0.0567. F.4.7.2.2 — Acabados — El acabado sobre el "
            "tablero de acero para entrepiso de comportamiento "
            "compuesto debe ser especificado por el diseñador y debe "
            "ser adecuado para el medio ambiente en que se encuentre "
            "la estructura. Debido a que el tablero es el refuerzo a "
            "flexión para la losa, este debe ser diseñado para "
            "trabajar durante toda la vida útil de la estructura. El "
            "acabado mínimo debe ser un recubrimiento galvanizado en "
            "zinc G60 (Z180), de acuerdo con la norma NTC 4011 (ASTM "
            "A653/A653M)."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_3_figura1_diagramas_carga",
        "seccion": "F.4.7.3 / Figura F.4.7.3-1 (Diseño del tablero como formaleta — diagramas de carga, momento, deflexión y reacciones)",
        "titulo": "Fórmulas de momento/deflexión/reacción para luz simple, dos y tres luces continuas, con carga puntual P y cargas distribuidas W1/W2.",
        "texto": (
            "F.4.7.3 — DISEÑO DEL TABLERO COMO FORMALETA — Las "
            "propiedades de la sección del tablero de acero se deben "
            "calcular de acuerdo a lo dispuesto en las secciones F.4.2 "
            "a F.4.5 de este Reglamento. Figura F.4.7.3-1 — Diagramas "
            "de carga, momentos, deflexiones y reacciones durante la "
            "construcción con un tablero metálico para entrepiso. "
            "Diagramas de carga y momento flector: Luz simple, carga P: "
            "+M = 0.25PL + 0.125W1tL². Luz simple, cargas W1+W2: "
            "+M = 0.125(W1+W2)L². Dos luces continuas, carga P: "
            "+M = 0.203PL + 0.096W1L². Dos luces continuas, cargas "
            "W1+W2: +M = 0.096(W1+W2)L², −M = 0.125(W1+W2)L². Tres "
            "luces continuas, carga P: +M = 0.20PL + 0.094W1L². Tres "
            "luces continuas, cargas W1+W2: +M = 0.094(W1+W2)L², "
            "−M = 0.117(W1+W2)L². Diagramas de carga y deflexiones: "
            "luz simple Δ = 0.0130·W1·L⁴/EI, dos luces continuas "
            "Δ = 0.0054·W1·L⁴/EI, tres luces continuas "
            "Δ = 0.0069·W1·L⁴/EI. Diagramas de cargas y reacciones en "
            "los apoyos: luz simple Pext = 0.5(W1+W2)L; dos luces "
            "continuas Pext = 0.375(W1+W2)L, Pint = 1.25(W1+W2)L; tres "
            "luces continuas Pext = 0.4(W1+W2)L, Pint = 1.1(W1+W2)L. "
            "Notas: P = 2.2 kN carga concentrada. I = Momento de "
            "Inercia (mm⁴/m). W1 = Peso de la losa de concreto + peso "
            "del tablero metálico. W2 = Carga de construcción 1 kPa. "
            "E = 203,000 MPa Módulo de elasticidad del acero. L = Luz "
            "libre (mm). W1t = 1.5 x Peso de losa de concreto ≤ Peso "
            "losa de concreto + 1.5 kPa + Peso del tablero metálico."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_3_1_2_dea_dccr",
        "seccion": "F.4.7.3.1 / F.4.7.3.2 (Diseño por Esfuerzos Admisibles y DCCR para el tablero como formaleta)",
        "titulo": "DEA: esfuerzo por flexión ≤0.6Fy (máx 250MPa) + cargas vivas mínimas 1.0kPa/2.2kN; DCCR: mismas cargas, factores del Título B.",
        "texto": (
            "F.4.7.3.1 — Diseño por Esfuerzos Admisibles (DEA) — Debe "
            "considerarse la interacción del cortante y la flexión en "
            "los cálculos. El esfuerzo debido a la flexión no excederá "
            "0.6 veces el esfuerzo de fluencia de diseño, Fy, bajo un "
            "máximo de 250 MPa, bajo las cargas combinadas del concreto "
            "fresco, el panel metálico y las siguientes cargas vivas "
            "mínimas de construcción: 1.0 kPa de carga uniformemente "
            "distribuida o una carga concentrada de 2.2 kN en un ancho "
            "de 1.0 m. El tablero metálico debe ser seleccionado para "
            "soportar una carga mínima distribuida de 2.4 kPa. Para "
            "luces simples la carga del concreto fresco debe ser como "
            "mínimo la mayor de su peso propio incrementado en un 50% "
            "ó 1.5 kPa. F.4.7.3.2 — Diseño con Coeficientes de Carga y "
            "Resistencia (DCCR) — Las factores de carga a emplear para "
            "las condiciones de construcción mostradas en la figura "
            "F.4.7.3-1 deben estar de acuerdo con el Título B de este "
            "Reglamento. Se debe verificar la interacción entre el "
            "cortante y la flexión. La resistencia requerida se debe "
            "calcular teniendo en cuenta las cargas combinadas del "
            "concreto fresco, el panel metálico y las siguientes cargas "
            "vivas mínimas de construcción: 1.0 kPa de carga "
            "uniformemente distribuida o una carga concentrada de "
            "2.2 kN en un ancho de 1.0 m. El tablero metálico debe ser "
            "seleccionado para soportar una carga mínima distribuida de "
            "2.4 kPa. Para luces simples la carga del concreto fresco "
            "debe ser como mínimo la menor de su peso propio "
            "incrementado en un 50% ó 1.5 kPa. Los factores de "
            "resistencia para flexión, cortante y apoyo interior se "
            "deben determinar de acuerdo con lo requerido por las "
            "secciones F.4.3 a F.4.5 de esta especificación."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_3_3_4_deflexiones_apoyo",
        "seccion": "F.4.7.3.3 / F.4.7.3.4 (Deflexiones y longitud mínima de apoyo del tablero como formaleta)",
        "titulo": "Deflexiones limitadas a L/180 o 20mm; apoyo mínimo recomendado 40mm, arrugamiento del alma +33% por cargas temporales.",
        "texto": (
            "F.4.7.3.3 — Deflexiones — Las deflexiones teóricas "
            "calculadas para el tablero de acero trabajando como "
            "formaleta deben basarse en el peso del concreto fresco, "
            "determinado a partir del espesor de diseño de la losa, y "
            "el peso propio del panel metálico uniformemente cargado "
            "en todas las luces (véase figura F.4.7.3-1 columna 2). "
            "Las deflexiones deben limitarse a la menor entre L/180 ó "
            "20 mm, medidas con respecto a los miembros de apoyo. Para "
            "el cálculo de las deflexiones no se toman en cuenta las "
            "cargas de construcción debido a su naturaleza temporal. "
            "F.4.7.3.4 — Longitud mínima de apoyo — Las longitudes "
            "mínimas de apoyo se deben determinar de acuerdo con las "
            "disposiciones de la sección F.4.3.3.4 de esta norma. Para "
            "el cálculo de estas longitudes se debe utilizar la carga "
            "del concreto fresco, el peso propio del panel metálico, y "
            "una carga de construcción de 1.0 kPa (véase la figura "
            "F.4.7.3-1 columna 3). Se recomienda un apoyo mínimo de "
            "40 mm para prevenir el deslizamiento de la lámina con "
            "respecto a su apoyo, sin embargo, este debe ser calculado "
            "siguiendo las disposiciones del párrafo anterior. El "
            "tablero de acero debe ser sujetado de manera adecuada "
            "para evitar su deslizamiento. La capacidad de arrugamiento "
            "del alma del tablero, en apoyos interiores, puede ser "
            "incrementada un 33% debido a cargas temporales de "
            "construcción."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_4_1_2_almacenamiento_instalacion",
        "seccion": "F.4.7.4 / F.4.7.4.1 / F.4.7.4.2 (Almacenamiento en sitio e instalación)",
        "titulo": "Paquete elevado y ventilado; unidades alineadas longitudinalmente sin escalonamientos sobre los apoyos.",
        "texto": (
            "F.4.7.4 — ALMACENAMIENTO EN SITIO E INSTALACIÓN — "
            "F.4.7.4.1 — Almacenamiento en sitio — El paquete de "
            "tableros en acero debe estar separado del terreno con un "
            "extremo elevado para proveer el suficiente drenaje y "
            "protegido contra la intemperie con una cubierta "
            "impermeable, lo suficientemente ventilado para evitar la "
            "condensación. F.4.7.4.2 — Instalación del tablero — Cada "
            "unidad de tablero debe ser colocada sobre la estructura de "
            "soporte de acuerdo con los planos de diseño. Debe "
            "ajustarse a su posición final, con sus traslapos "
            "longitudinales bien alineados y los extremos apoyados "
            "sobre los miembros estructurales sin escalonamientos sobre "
            "los apoyos. Todos los paneles metálicos deben estar "
            "alineados longitudinalmente en los diferentes vanos."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_4_3_bordes_extremos",
        "seccion": "F.4.7.4.3 (Bordes extremos a tope)",
        "titulo": "Láminas a tope sobre los apoyos, tolerancia máxima de longitud 12mm; traslapo desaconsejado por resaltos de cortante.",
        "texto": (
            "F.4.7.4.3 — Bordes extremos a tope — Las láminas del panel "
            "deben estar a tope sobre los apoyos. Debe tenerse en "
            "cuenta la máxima tolerancia en la longitud de 12 mm "
            "(remitirse a la sección F.4.7.2.1). El traslapo sobre los "
            "apoyos de las láminas no es conveniente debido a los "
            "resaltos de cortante (repujado en el alma) o que el "
            "perfil de la sección transversal puede evitar el ajuste "
            "lámina a lámina. El espacio entre láminas traslapadas "
            "puede hacer más difícil la operación de sujeción mediante "
            "soldadura. Los espacios entre bordes extremos de láminas "
            "son aceptables, pudiendo requerirse la colocación de "
            "cintas especiales para el sello de la junta."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_4_4_anclaje",
        "seccion": "F.4.7.4.4 (Anclaje — generalidades)",
        "titulo": "Anclaje inmediato tras alineación; separaciones >1.5m requieren sujetadores longitudinales adicionales.",
        "texto": (
            "F.4.7.4.4 — Anclaje — Las láminas del tablero para "
            "entrepiso deben estar ancladas a los miembros de soporte "
            "(incluyendo estructuras de acero y/o muros de carga en el "
            "perímetro longitudinal y no sólo transversal), ya sea por "
            "soldadura o por sujetadores mecánicos. Esta sujeción debe "
            "hacerse inmediatamente después de la alineación. El "
            "anclaje mínimo para la instalación de la lámina se "
            "especifica en la sección F.4.7.4.4.1. No debe caminarse o "
            "estacionarse sobre el tablero de acero hasta que se hayan "
            "realizado estos anclajes mínimos. Las unidades del tablero "
            "metálico con separaciones entre apoyos mayores a 1.5 m "
            "deberán tener sujetadores longitudinales en los traslapos "
            "lámina a lámina y lámina a borde perimetral (el perímetro "
            "con el miembro estructural de acero o concreto), en la "
            "mitad de la luz o a intervalos de 1.0 m, la menor de las "
            "dos. Estos sujetadores longitudinales se colocaran a "
            "partir del centro de la luz hacia los apoyos. Bajo "
            "ninguna circunstancia deben dejarse láminas no sujetadas, "
            "garantizándose siempre el anclaje de los tableros. El "
            "objetivo del sujetador en el traslapo longitudinal es "
            "prevenir deflexiones diferenciales entre láminas o "
            "tableros durante el vaciado del concreto y por lo tanto "
            "evitar la separación de la junta longitudinal. No se "
            "deben admitir los huecos causados por soldadura durante "
            "las operaciones de sujeción de lámina. Debe seleccionarse "
            "un sistema adecuado de anclaje."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_4_4_1_2_soldadura_sujetadores",
        "seccion": "F.4.7.4.4.1 / F.4.7.4.4.2 (Soldadura y sujetadores mecánicos para el anclaje)",
        "titulo": "Soldadura mínimo 15mm diámetro cada 300mm promedio (máx 460mm); sujetadores mecánicos requieren ensayos documentados.",
        "texto": (
            "F.4.7.4.4.1 — Soldadura — Los procedimientos de soldadura "
            "estarán estrictamente de acuerdo con las especificaciones "
            "de la sección F.4.5 de este Reglamento, o en su defecto a "
            "lo dispuesto en el numeral F.2. Se requiere un punto de "
            "soldadura mínimo de 15 mm de diámetro, o equivalente, en "
            "las crestas laterales del tablero metálico sobre el "
            "apoyo, más un número adicional de puntos de soldadura "
            "intermedios hasta obtener un espaciamiento promedio de "
            "300 mm. El máximo espaciamiento entre puntos adyacentes de "
            "sujeción no excederá los 460 mm. Cuando se utilicen "
            "soldaduras de filete deben ser de al menos 25 mm de "
            "longitud. El metal de aporte penetrará todas las capas de "
            "material del tablero en el final del traslapo longitudinal "
            "sobre el apoyo y tendrá una buena fusión a los miembros "
            "estructurales de soporte. Se deben utilizar arandelas para "
            "soldar sobre todas las unidades de tablero con espesor "
            "base de 0.71 mm (calibre 22). Las arandelas tendrán un "
            "espesor mínimo de 1.50 mm (calibre 16), y un diámetro "
            "nominal de perforación de 10 mm. F.4.7.4.4.2 — Sujetadores "
            "mecánicos — Los sujetadores mecánicos (tornillos, "
            "sujetadores anclados neumáticamente o accionados con "
            "pólvora) pueden utilizarse como medios de anclaje, siempre "
            "y cuando el tipo y espaciamiento del sujetador satisfaga "
            "el criterio de diseño. Para la aprobación de su uso, el "
            "fabricante deberá presentar los ensayos documentados, "
            "formulas de diseño y tablas."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_1_generalidades",
        "seccion": "F.4.7.5 / F.4.7.5.1 (Diseño del tablero y concreto como unidad compuesta — generalidades)",
        "titulo": "Sistema compuesto diseñado como losa de concreto reforzado; malla electro-soldada sola no garantiza refuerzo negativo continuo.",
        "texto": (
            "F.4.7.5 — DISEÑO DEL TABLERO Y CONCRETO COMO UNA UNIDAD "
            "COMPUESTA — F.4.7.5.1 — Generalidades — El sistema de "
            "entrepiso compuesto se debe diseñar como una losa de "
            "concreto reforzado con el tablero de acero actuando como "
            "el refuerzo positivo. Las losas deben diseñarse como "
            "sistemas de luces simples o continuas bajo cargas "
            "uniformes. La altura o espesor de la losa corresponde a la "
            "distancia medida desde la parte inferior del tablero "
            "metálico hasta el plano superior del concreto. Las "
            "consideraciones especiales para cargas concentradas "
            "(sección F.4.7.7.4) y comportamiento como diafragma "
            "requieren un análisis adicional. La capacidad de carga "
            "horizontal debe analizarse con procedimientos racionales "
            "aceptados. Su comportamiento como diafragma debe ser "
            "aprobado por el ingeniero diseñador. Si el diseñador "
            "requiere un sistema de losa continuo sobre los apoyos, "
            "debe garantizarse la presencia de refuerzo negativo "
            "utilizando las ecuaciones convencionales del concreto "
            "reforzado, de acuerdo con lo estipulado en el Título C de "
            "esta norma. La malla electro-soldada, en caso de "
            "seleccionarse como el refuerzo por temperatura, no "
            "garantiza por sí sólo la suficiente área de acero para "
            "lograr el comportamiento como losa continua (ver sección "
            "F.4.7.5.5). El tablero metálico no puede considerarse como "
            "refuerzo en compresión para el caso de voladizos. Debe "
            "tenerse especial cuidado con cargas provenientes de "
            "cielos falsos en voladizos del sistema de entrepiso "
            "compuesto. Los procedimientos de diseño de este numeral no "
            "se pueden aplicar a sistemas de losa de entrepiso sin "
            "conectores de cortante unidos al sistema de apoyo, sin la "
            "presencia de barreras para el fraguado del concreto u "
            "otras restricciones. Las losas deben estar unidas a su "
            "sistema de apoyo, así sea con los anclajes mínimos por "
            "construcción del numeral F.4.7.4.4. En caso de que no se "
            "consideren conectores de cortante para el diseño, la "
            "capacidad de carga por unidad de área debe determinarse "
            "mediante ensayos de adherencia concreto-lámina o por el "
            "método de esfuerzos admisibles (DEA) (sección "
            "F.4.7.5.6.1). La presencia de conectores de cortante en "
            "una cuantía adecuada garantiza el alcance de la "
            "resistencia de diseño a flexión en la sección transversal "
            "de la losa. Debe utilizarse el apropiado factor de "
            "resistencia, φ, para la determinación de la resistencia "
            "de diseño."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_2_3_ensayos_concreto",
        "seccion": "F.4.7.5.2 / F.4.7.5.2.1 / F.4.7.5.3 / F.4.7.5.3.1 (Ensayos, determinación de la carga, concreto, recubrimiento mínimo)",
        "titulo": "f'c mínimo 21MPa, sin aditivos clorhídricos; recubrimiento mínimo 50mm sobre la cresta (20mm sobre barras de refuerzo negativo).",
        "texto": (
            "F.4.7.5.2 — Ensayos — El fabricante podrá utilizar los "
            "criterios de diseño aplicables para determinar la "
            "resistencia del sistema de losa (ver sección F.4.7.5.6) o, "
            "alternativamente, el fabricante deberá realizar, bajo "
            "supervisión profesional, un número suficiente de ensayos "
            "con el sistema losa-tablero para garantizar su "
            "comportamiento compuesto. F.4.7.5.2.1 — Determinación de "
            "la carga — La capacidad de carga sobreimpuesta disponible "
            "se determinará con los procedimientos estándar de diseño "
            "del concreto reforzado, mediante el uso de factores de "
            "resistencia de diseño o factores de seguridad, según sea "
            "aplicable, y factores de reducción basados en la "
            "presencia, ausencia, o espaciamiento de los conectores de "
            "cortante sobre las vigas perpendiculares al tablero, tal "
            "como se muestra en la sección F.4.7.5.6. F.4.7.5.3 — "
            "Concreto — El concreto estará de acuerdo con lo "
            "estipulado en el Título C de este Reglamento. La "
            "resistencia mínima a compresión, f'c, será de 21 MPa o lo "
            "que se requiera para resistencia al fuego o durabilidad. "
            "No se deben utilizar aditivos que contengan sales "
            "clorhídricas. F.4.7.5.3.1 — Recubrimiento mínimo — El "
            "recubrimiento mínimo de concreto sobre la cresta del "
            "tablero metálico debe ser de 50 mm. Cuando se requiera "
            "refuerzo adicional para momento negativo, el recubrimiento "
            "mínimo de concreto sobre estas barras será de 20 mm."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_4_5_deflexiones_refuerzo",
        "seccion": "F.4.7.5.4 / F.4.7.5.5 (Deflexiones del sistema compuesto y refuerzo por retracción y temperatura)",
        "titulo": "Deflexiones ≤L/360; refuerzo por retracción mínimo 0.00075 del área de concreto (o fibras de acero/sintéticas alternativas).",
        "texto": (
            "F.4.7.5.4 — Deflexiones — Las deflexiones del sistema de "
            "losa compuesto no excederán L/360 bajo la carga "
            "sobreimpuesta. Para el sistema compuesto estas deflexiones "
            "pueden calcularse utilizando el promedio de la inercia "
            "agrietada y no agrietada, cuando se use el procedimiento "
            "de la sección transformada. F.4.7.5.5 — Refuerzo por "
            "retracción y temperatura — El refuerzo por retracción y "
            "temperatura deberá consistir de una malla electro-soldada "
            "o barras de refuerzo, con un área mínima de 0.00075 veces "
            "el área del concreto sobre el tablero metálico, pero no "
            "debe ser menor que una malla con un área de 59.3 mm² de "
            "acero por metro de ancho de losa. Alternativamente, "
            "pueden utilizarse fibras de acero en lugar de la malla de "
            "refuerzo para efectos de retracción y temperatura de "
            "acuerdo a las especificaciones NTC 5214 (ASTM A820), en "
            "una cuantía mínima de 14.8 kg/m³, o fibras macro "
            "sintéticas, hechas a partir de poliolefino virgen, con un "
            "diámetro equivalente entre 0.4 mm y 1.25 mm con una "
            "relación de aspecto mínima (longitud/diámetro equivalente) "
            "de 50, en una cuantía mínima de 2.4 kg/m³."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_6_1_flexion_dea",
        "seccion": "F.4.7.5.6 / F.4.7.5.6.1 (Flexión — Método de Diseño por Esfuerzos Admisibles, ecuación F.4.7.5-1)",
        "titulo": "Madm = C·Fy·Sc; C=0.60 sin conectores de cortante, C=0.75 con conectores.",
        "texto": (
            "F.4.7.5.6 — Flexión. F.4.7.5.6.1 — Método de Diseño por "
            "Esfuerzos Admisibles (DEA) — La resistencia admisible a "
            "flexión se debe determinar con la siguiente ecuación: "
            "Madm = C·Fy·Sc (F.4.7.5-1). Donde: Madm = resistencia "
            "admisible a flexión. Fy = esfuerzo de fluencia de diseño "
            "determinado en la sección F.4.1.6.1. Sc = módulo elástico "
            "mínimo de la sección transversal transformada agrietada. "
            "C = factor de seguridad. Si no se considera la presencia "
            "de conectores de cortante en el diseño C = 0.60. Si estos "
            "se consideran, C puede tomarse igual a 0.75. No existe una "
            "correlación entre las capacidades de carga halladas por "
            "los dos diferentes métodos de diseño, DCCR o DEA."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_6_2_flexion_dccr",
        "seccion": "F.4.7.5.6.2 (Flexión — Método DCCR, ecuaciones F.4.7.5-2 a -4)",
        "titulo": "φMn=φAsFy(d−a/2) con conectores suficientes; φMn=φScFy sin conectores; φ=0.85; limitación real de ensayos en calibre 16.",
        "texto": (
            "F.4.7.5.6.2 — Método de Diseño con Coeficientes de Carga y "
            "Resistencia (DCCR) — La resistencia de diseño a flexión se "
            "debe calcular a partir de los procedimientos estándar de "
            "diseño de concreto reforzado del Título C de este "
            "Reglamento y las combinaciones de carga de acuerdo con lo "
            "establecido en el Título B de este Reglamento. La "
            "resistencia de diseño a flexión, cuando se dispone de "
            "conectores en la cuantía suficiente para alcanzar la "
            "capacidad máxima de la sección transversal, como se "
            "especifica en F.4.7.5.6.3, se debe determinar a partir de "
            "la ecuación F.4.7.5-2: φMn = φAsFy(d − a/2) (F.4.7.5-2). "
            "Donde: φMn = resistencia de diseño a flexión ancho "
            "unitario. φ = factor de resistencia, φ = 0.85. Fy = "
            "esfuerzo de fluencia de diseño determinado en la sección "
            "F.4.1.6.1. d = distancia desde la parte superior de la "
            "losa de concreto hasta el centroide del tablero metálico. "
            "As = área transversal del tablero metálico. "
            "a = AsFy/(0.85f'c·b) (F.4.7.5-3). Donde: f'c = resistencia "
            "a compresión del concreto, mínimo 21 MPa. b = ancho "
            "unitario de la zona a compresión de concreto (usualmente, "
            "1.0 m = 1000 mm). Adicionalmente, la resistencia de "
            "diseño a flexión cuando no se dispone o no se toman en "
            "cuenta los conectores de cortante, se determina mediante: "
            "φMn = φScFy (F.4.7.5-4). Donde: φ = 0.85. Fy = esfuerzo "
            "de fluencia de diseño determinado en la sección F.4.1.6.1. "
            "Sc = módulo elástico mínimo de la sección transversal "
            "transformada agrietada. Debido a la escasez de ensayos "
            "sobre tableros metálicos calibre 16 (1.50 mm) y a que la "
            "profundidad de los resaltos de cortante (repujado en el "
            "alma) requerida para desarrollar la capacidad a momento en "
            "la sección transversal, sin incluir los conectores de "
            "cortante, podría no ser suficiente en este espesor de "
            "lámina, los valores máximos de resistencia a flexión deben "
            "ser los obtenidos para el sistema con un tablero en "
            "calibre 18 (1.20 mm). El fabricante sólo podrá publicar "
            "tablas de carga y capacidades máximas limitadas a las "
            "máximas obtenidas para un sistema de entrepiso con un "
            "tablero de 1.2 mm (calibre 18) de espesor. Las propiedades "
            "para el diseño de la sección transversal del tablero "
            "metálico, deben ser suministradas por el fabricante del "
            "producto. Se puede realizar una interpolación lineal "
            "entre las ecuaciones F.4.7.5-2 y F.4.7.5-4 para obtener la "
            "resistencia a flexión de una losa con conectores de "
            "cortante en un número no suficiente para alcanzar la "
            "resistencia nominal máxima a flexión de la sección "
            "transversal."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_6_3_conectores_cortante",
        "seccion": "F.4.7.5.6.3 (Conectores de cortante — ecuación F.4.7.5-5)",
        "titulo": "Ns=Fy(As−Awebs/2−Abf)/(142.58(f'cEc)^0.5), número de pernos de 19mm requerido por metro de ancho.",
        "texto": (
            "F.4.7.5.6.3 — Conectores de cortante — El número requerido "
            "de pernos conectores de cortante de diámetro de 19 mm por "
            "metro de ancho para anclar la losa de manera que pueda "
            "alcanzarse la resistencia nominal a flexión en la sección "
            "transversal, será estimado por la siguiente ecuación: "
            "Ns = Fy·(As − Awebs/2 − Abf)/(142.58·(f'c·Ec)^0.5) "
            "(F.4.7.5-5). Donde: Ns = número de pernos conectores de "
            "19 mm requerido por metro de ancho. As = área de acero en "
            "mm² por metro de ancho. Awebs = área de las almas en mm² "
            "por metro de ancho. Abf = área de acero de la aleta "
            "inferior en mm² por metro de ancho. Fy = esfuerzo de "
            "fluencia de diseño en MPa determinado en la sección "
            "F.4.1.6.1. Ec = módulo de elasticidad del concreto en MPa "
            "de acuerdo con el Título C de este Reglamento. El valor "
            "de As se calcula con base en el ancho plano del material. "
            "Las propiedades de la sección transversal, para la "
            "determinación del número requerido de conectores, deben "
            "ser suministradas por el fabricante del producto, o en su "
            "defecto, este presentará esquemas o planos de la sección "
            "para el cálculo de las áreas en la obtención de Ns."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_7_cortante_figura1",
        "seccion": "F.4.7.5.7 (Cortante — ecuaciones F.4.7.5-6 y -7, Figura F.4.7.5-1)",
        "titulo": "φVn=φVtab+φVc; φVc=φ(√f'c/6)Ac; Figura F.4.7.5-1 muestra las áreas de concreto disponibles para cortante (a)(b)(c).",
        "texto": (
            "F.4.7.5.7 — Cortante — El área de concreto disponible "
            "para cortante se obtiene a partir de la figura F.4.7.5-1. "
            "Debido a que el refuerzo negativo puede o no utilizarse, "
            "queda a discreción del diseñador revisar si el área de "
            "concreto sobre cualquier barra de acero debe ser deducida "
            "del área de concreto disponible para resistir fuerzas "
            "cortantes. La resistencia de diseño a cortante, φVn, es "
            "la resistencia a cortante vertical total del sistema de "
            "entrepiso compuesto, multiplicada por un factor de "
            "resistencia. Esta resistencia será la suma de las "
            "capacidades a cortante del tablero metálico y del "
            "concreto, calculada mediante la ecuación F.4.7.5-6: "
            "φVn = φVtab + φVc (F.4.7.5-6). Donde: φ = factor de "
            "resistencia, φ = 0.85. φVn = resistencia de diseño a "
            "cortante del sistema de entrepiso compuesto. φVtab = "
            "resistencia de diseño a cortante del tablero metálico de "
            "acuerdo con lo especificado en F.4.3.3.2.1. φVc = "
            "resistencia de diseño a cortante suministrada por el "
            "concreto, que puede calcularse como: φVc = φ·(√f'c/6)·Ac "
            "(F.4.7.5-7). Donde: f'c = resistencia a compresión del "
            "concreto en MPa, mínimo 21 MPa. Ac = área de concreto "
            "disponible para cortante en mm² obtenida de la figura "
            "F.4.7.5-1. Figura F.4.7.5-1 — Áreas disponibles para "
            "cortante: (a) las zonas sombreadas representan el área "
            "disponible para cortante entre valles espaciados una "
            "distancia S; (b) si las áreas de corte se traslapan se "
            "ajusta el área; (c) se ajusta el área calculando la forma "
            "en la cual la dimensión en la parte superior no exceda la "
            "separación S indicada en (a)."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_5_8_cortante_momento_combinados",
        "seccion": "F.4.7.5.8 (Cortante y momento flector combinados — DEA y DCCR, ecuaciones F.4.7.5-8 a -10)",
        "titulo": "DEA: √((ΩbM/Mn)²+(ΩvV/Vn)²)≤1.0, Ωv=1.60, Ωb=1.67; DCCR: √((M̄/φbMn)²+(V̄/φvVn)²)≤1.0, φv=φb=0.95.",
        "texto": (
            "F.4.7.5.8 — Cortante y momento flector combinados. "
            "F.4.7.5.8.1 — Método de Diseño por Esfuerzos Admisibles "
            "(DEA) — La ecuación de interacción para cortante y "
            "momento flector es la siguiente: "
            "√((ΩbM/Mn)² + (ΩvV/Vn)²) ≤ 1.0 (F.4.7.5-8). Ωv = 1.60. "
            "Ωb = 1.67. Donde: V = resistencia requerida a cortante. "
            "M = resistencia requerida a flexión. Vn = resistencia "
            "nominal a cortante de acuerdo con la sección F.4.7.5.7. "
            "Mn = resistencia a flexión para DEA = Fy·Sc (F.4.7.5-9). "
            "Fy y Sc se definen en la sección F.4.7.5.6.1. La ecuación "
            "F.4.7.5-8 se debe utilizar para la interacción del tablero "
            "metálico actuando como formaleta (etapa de construcción) "
            "y también cuando está trabajando con el concreto como "
            "sistema compuesto. F.4.7.5.8.2 — Método de Diseño con "
            "Coeficientes de Carga y Resistencia (DCCR) — La ecuación "
            "de interacción entre cortante y momento flector es: "
            "√((M̄/φbMn)² + (V̄/φvVn)²) ≤ 1.0 (F.4.7.5-10). φv = 0.95. "
            "φb = 0.95. Donde: V̄ = resistencia requerida a cortante, "
            "V̄ = Vu. M̄ = resistencia requerida a flexión, M̄ = Mu. "
            "Vn = resistencia nominal a cortante de acuerdo con la "
            "sección F.4.7.5.7. Mn = resistencia nominal a flexión de "
            "acuerdo con la sección F.4.7.5.6.2."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_6_procedimiento_constructivo",
        "seccion": "F.4.7.6 (Procedimiento constructivo — apuntalamiento, limpieza, vaciado)",
        "titulo": "Apuntalamiento hasta 75% resistencia y mín. 7 días; tablero libre de tierra/residuos antes del vaciado; vaciado uniforme sin impactos.",
        "texto": (
            "F.4.7.6 — PROCEDIMIENTO CONSTRUCTIVO — F.4.7.6.1 — "
            "Apuntalamiento temporal — En caso de requerirse "
            "apuntalamiento temporal para la condición mínima de carga "
            "sobreimpuesta al tablero de 2.4 kPa, este debe estar "
            "asegurado en el sitio antes de empezar la instalación de "
            "los tableros. El apuntalamiento debe diseñarse e "
            "instalarse de acuerdo con los procedimientos de "
            "apuntalamiento para concreto reforzado estipulados en el "
            "Título C de este Reglamento. El apuntalamiento debe "
            "permanecer en su sitio hasta que el concreto alcance el "
            "75% de su resistencia especificada a compresión y durante "
            "un mínimo de 7 días. F.4.7.6.2 — Limpieza — Antes del "
            "vaciado del concreto el tablero de acero debe estar libre "
            "de tierra, escombros, agua estancada, residuos por "
            "operaciones de taladrado o algún otro material extraño. "
            "F.4.7.6.3 — Vaciado del concreto — Debe tenerse especial "
            "cuidado durante el vaciado del concreto de manera que el "
            "tablero no esté sujeto a ningún impacto que exceda su "
            "capacidad de diseño. El concreto debe colocarse desde un "
            "bajo nivel con respecto al panel metálico, para evitar "
            "impactos. El vaciado debe realizarse de manera uniforme "
            "sobre la estructura de soporte y desde allí extenderse "
            "hacia el centro de la luz del tablero. Si se utilizan "
            "equipos menores de acarreo de material deben colocarse "
            "tablones para el tránsito de estos. Los equipos solo "
            "pueden operar sobre esta plataforma. Los tablones serán de "
            "una rigidez adecuada para transferir las cargas al tablero "
            "metálico sin causar daño. Deben evitarse todos los daños "
            "por una inadecuada colocación del concreto."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_7_1_2_3_estacionamientos_voladizos_vigas",
        "seccion": "F.4.7.7 / F.4.7.7.1 / F.4.7.7.2 / F.4.7.7.3 (Consideraciones adicionales — estacionamientos, voladizos, vigas en sección compuesta)",
        "titulo": "Estacionamientos: refuerzo negativo + protección salina; voladizos: solo formaleta, esfuerzo máx 138MPa, deflexión L/120.",
        "texto": (
            "F.4.7.7 — CONSIDERACIONES ADICIONALES — F.4.7.7.1 — "
            "Estacionamientos — El uso del sistema de entrepiso "
            "compuesto es apropiado para edificios de estacionamientos. "
            "La experiencia práctica ha mostrado un comportamiento "
            "excelente. Para su uso en edificios de parqueaderos deben "
            "tenerse en cuenta las siguientes consideraciones: (1) Las "
            "losas deben diseñarse como sistemas de luces continuas "
            "con refuerzo para momento sobre los apoyos. (2) En caso de "
            "ser necesario, se debe suministrar refuerzo adicional para "
            "detener el agrietamiento causado por grandes diferencias "
            "de temperatura y para garantizar una mejor distribución de "
            "las cargas. (3) En zonas con alta presencia salina (agua "
            "marina) deben tomarse medidas de protección. Se recomienda "
            "un galvanizado mínimo G90 (Z275), de acuerdo con la norma "
            "NTC 4011 (ASTM A653/A653M) y recubrir la parte inferior "
            "del tablero con una pintura adecuada. Las medidas de "
            "protección deben mantenerse durante toda la vida útil de "
            "la estructura. F.4.7.7.2 — Voladizos — En el caso de "
            "voladizos, el tablero solo debe trabajar como formaleta "
            "permanente, y debe suministrarse el refuerzo negativo que "
            "se requiera para soportar la condición de carga. No se "
            "debe considerar al tablero como refuerzo en compresión. "
            "El esfuerzo máximo admisible en la sección transversal "
            "del tablero metálico, actuando como formaleta en "
            "voladizo, debe ser 138 MPa (20 000 lb/pulg²) calculado "
            "bajo las cargas combinadas del peso propio del concreto "
            "fresco, el peso propio del tablero metálico y 1.0 kPa o "
            "el peso propio del concreto fresco, el peso propio del "
            "tablero metálico y una carga puntual, aplicada en el "
            "extremo del voladizo, de 2200 N por metro de ancho, la "
            "más crítica de ambas combinaciones. La deflexión máxima "
            "en el borde libre es L/120, donde L es la longitud del "
            "voladizo, bajo las cargas del peso propio del concreto y "
            "el peso propio del tablero. Se supone un ancho de apoyo "
            "de 89 mm para la revisión por arrugamiento del alma con "
            "una carga combinada del peso propio del concreto, el peso "
            "propio del tablero metálico y 1.0 kPa. Si el ancho del "
            "apoyo es menor a 89 mm debe consultarse con el fabricante "
            "del tablero metálico. F.4.7.7.3 — Vigas y viguetas en "
            "sección compuesta — Las secciones del sistema de entrepiso "
            "compuesto son apropiadas para su uso con vigas en sección "
            "compuesta."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_7_4_cargas_concentradas_ecuaciones",
        "seccion": "F.4.7.7.4 (Cargas concentradas — ecuaciones F.4.7.7-1 a -7, Figura F.4.7.7-1)",
        "titulo": "Ancho de distribución efectiva bm/be para flexión y cortante; refuerzo de distribución mín. 0.00075·A'c; momento eje débil M=Pbe/15w.",
        "texto": (
            "F.4.7.7.4 — Cargas concentradas — La figura F.4.7.7-1 "
            "muestra los anchos efectivos de distribución de una carga "
            "concentrada. Este análisis debe hacerse cuando se apliquen "
            "al sistema cargas sobreimpuestas mayores de 20 kPa. El "
            "área obtenida para el acero de distribución mediante este "
            "procedimiento no debe ser inferior a 0.00075·A'c, donde "
            "A'c es el área de concreto (por ancho unitario) sobre las "
            "crestas del tablero metálico, la cual es diferente al "
            "área de concreto Ac disponible para cortante. Las "
            "fórmulas para los anchos de distribución efectiva son las "
            "siguientes: bm = b2 + 2tc + 2tt (F.4.7.7-1). Flexión en "
            "una luz simple: be = bm + 2(1 − x/L)x (F.4.7.7-2). Donde "
            "x es distancia de localización de la carga con respecto "
            "al apoyo. Flexión en luces continuas: "
            "be = bm + (4/3)(1 − x/L)x (F.4.7.7-3). Cortante: "
            "be = bm + (1 − x/L)x (F.4.7.7-4). Pero en ningún caso: "
            "be > 2.71(tc/h), en metros (F.4.7.7-5a). Momento "
            "alrededor del eje débil: M = P·be/(15w) (F.4.7.7-6). "
            "Donde: w = L/2 + b3, pero no debe superar el valor de L "
            "(F.4.7.7-7). Figura F.4.7.7-1 — Distribución de cargas "
            "concentradas: (a) muestra bm=b2+2tc+2tt, con tt=espesor "
            "de acabado (capa de rodamiento, si no existe tt=0) y "
            "acero de distribución sobre el ancho bm; (b) muestra la "
            "carga P aplicada sobre un ancho b2×b3, distribuida en un "
            "ancho efectivo bc dentro de un ancho de losa w."
        ),
    },
    {
        "id": "NSR10-F-F_4_7_7_5_tuberia",
        "seccion": "F.4.7.7.5 (Tubería embebida en el sistema de losa)",
        "titulo": "Conductos ≤25.4mm o ≤1/3 del recubrimiento, sin atravesar valles, espaciados mínimo 460mm, recubrimiento mínimo 19mm.",
        "texto": (
            "F.4.7.7.5 — Tubería — Pueden colocarse conductos en el "
            "sistema de losa cuando el tamaño del tubo sea de 25.4 mm "
            "o menor en diámetro, o menor a 1/3 del recubrimiento del "
            "concreto, sin atravesar valles del tablero, y esté "
            "espaciado 460 mm como mínimo, con un recubrimiento mínimo "
            "de 19 mm, excepto que las especificaciones de diseño "
            "limiten a una condición más exigente."
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

    print(f"\nOK: {len(rows)} chunks verbatim de F.4.7 cargados. F.4.7 queda COMPLETO.")


if __name__ == "__main__":
    main()
