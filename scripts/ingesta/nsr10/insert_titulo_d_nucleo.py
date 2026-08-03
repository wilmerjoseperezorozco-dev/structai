"""
Inserta el núcleo verbatim real de NSR-10 Título D (Mampostería Estructural)
en nsr10_chunks — D.1, D.2 y D.3 completos, texto oficial extraído
directamente de los PDF fuente en Google Drive (carpeta METADATOS, ver
nsr10_catalogo_maestro.json), NO del "PDF" RAG+CAG sintético que hay en
packages/knowledge/nsr10/ (ese resultó ser un export JSON/LaTeX roto de un
sistema RAG/CAG anterior, no la norma oficial — descartado el 2026-08-03).

Mismo patrón usado para Título C y F (núcleo verbatim, no exhaustivo):
D.1 (alcance/generalidades), D.2 (clasificación/usos/normas/nomenclatura/
definiciones), D.3 (calidad de materiales — cemento, acero, mortero de
pega/relleno con sus tablas D.3.4-1/D.3.5-1, unidades con tabla D.3.6-1,
determinación de f'm con fórmulas D.3.7-1/2/3, evaluación y aceptación).
D.4 en adelante (requisitos de diseño detallados) quedan para una siguiente
ronda.

Uso: python scripts/ingesta/nsr10/insert_titulo_d_nucleo.py [--dry-run]
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
from dotenv import load_dotenv
load_dotenv(ROOT / "apps" / "api" / ".env")

CAPITULO_LABEL = "NSR-10 Título D — Mampostería Estructural"

CHUNKS = [
    {
        "id": "NSR10-D-D_1",
        "seccion": "D.1",
        "titulo": "Capítulo D.1 — Requisitos generales (alcance, planos y memorias, supervisión técnica, requisitos generales para las estructuras)",
        "texto": """CAPÍTULO D.1 REQUISITOS GENERALES

D.1.1 — ALCANCE

D.1.1.1 — ALCANCE — El Título D de este Reglamento establece los requisitos mínimos de diseño y construcción para las estructuras de mampostería y sus elementos. Estas estructuras tienen un nivel de seguridad comparable a las estructuras de otros materiales, cuando se diseñan y construyen de acuerdo con los requisitos del presente Reglamento.

D.1.1.2 — ESTRUCTURAS ESPECIALES — Para estructuras especiales tales como arcos, bóvedas, tanques, silos y chimeneas, los requisitos del Título D de este Reglamento pueden utilizarse cuando sean aplicables, a juicio del ingeniero diseñador.

D.1.1.3 — PROPÓSITO — Los requisitos establecidos en este Título están dirigidos a lograr un comportamiento apropiado de las construcciones en mampostería estructural y su integridad estructural bajo las condiciones de carga vertical permanente o transitoria, bajo condiciones de fuerza lateral, de viento o de sismo y bajo estados ocasionales de fuerzas anormales.

D.1.1.4 — COMPLEMENTO — El Título D se complementa con los otros Títulos de este Reglamento. En el eventual caso de conflicto entre uno o varios de los requisitos, debe adoptarse como válido el más severo de ellos.

D.1.1.5 — REQUISITOS MÍNIMOS — Los procedimientos y las especificaciones establecidas constituyen los requisitos mínimos que deben cumplir el diseño y la construcción de estructuras de mampostería, con el objetivo de la protección a la vida y en lo posible los bienes materiales de los usuarios de la edificación.

D.1.1.6 — PROCEDIMIENTO DE DISEÑO — Las estructuras de mampostería deben diseñarse por el método del estado límite de resistencia utilizando las combinaciones de carga descritas en B.2.4, y los requisitos del Título D que se presentan para este método. No obstante, se permite el diseño de estructuras de mampostería por el método de esfuerzos de trabajo admisibles utilizando las combinaciones de carga descritas en B.2.3, y para el efecto deben emplearse los requisitos alternos presentados en el Apéndice D-1 — Diseño de estructuras de mampostería por el método de los esfuerzos de trabajo admisibles. Todo el diseño de la estructura debe realizarse por uno de los dos métodos.

D.1.2 — PLANOS Y MEMORIAS

D.1.2.1 — PLANOS ESTRUCTURALES — Además de los requisitos establecidos en A.1.5.2, debe especificarse y detallarse en los planos: (a) Características de las unidades de mampostería, indicando la norma NTC bajo la cual deben fabricarse (según D.3.6). (b) Valor de la resistencia nominal a la compresión de la mampostería (f'm), respecto al área neta promedio de la sección. (c) Definición del mortero de pega como tipo H, M, S o N (D.3.4), fijando su resistencia mínima a la compresión. (d) Ubicación de las celdas y cavidades a inyectar con mortero de relleno. (e) Definición del tipo de mortero de relleno (D.3.5), con su resistencia mínima a la compresión. (f) Tamaño y localización de todos los elementos especificados. (g) Tamaño especificado, resistencia, tipo y localización del acero de refuerzo, anclajes mecánicos y conectores. (h) Ubicación, tamaño y características de las juntas de control y de construcción. (i) Ubicación y tamaño de las celdas de inspección.

D.1.2.2 — MEMORIAS — Se debe cumplir lo estipulado en A.1.5.3.

D.1.3 — SUPERVISIÓN TÉCNICA

D.1.3.1 — OBLIGATORIEDAD DE LA SUPERVISIÓN TÉCNICA — Toda edificación de más de 3000 m² de área construida debe someterse a Supervisión Técnica, como lo indica la Ley 400 de 1997. El Supervisor técnico debe cumplir lo dispuesto en el Título I. Dada la susceptibilidad de la mampostería estructural a los defectos de la calidad de la mano de obra y de los materiales, es recomendable, en edificaciones de menos de 3000 m², que toda obra con este sistema se construya bajo estricta supervisión técnica de un profesional idóneo (Ingeniero Civil o Arquitecto matriculado) o un representante competente bajo su responsabilidad.

D.1.3.2 — ALCANCE DE LA SUPERVISIÓN — El supervisor técnico debe verificar la concordancia entre la obra ejecutada y los planos y especificaciones de construcción, según I.2.4.

D.1.3.3 — REGISTRO DE LAS LABORES DE SUPERVISIÓN — El Supervisor técnico debe llevar un registro escrito de su labor, controlando y registrando la calidad de las unidades de mampostería, de los morteros de pega y de relleno, la disposición de armaduras, anclajes y conectores, y supervisando las operaciones de inyección de mortero.

D.1.4 — REQUISITOS GENERALES PARA LAS ESTRUCTURAS EN MAMPOSTERÍA ESTRUCTURAL

D.1.4.1 — RESISTENCIA ANTE CARGAS HORIZONTALES EN DOS DIRECCIONES ORTOGONALES EN PLANTA — Los muros estructurales tienen gran rigidez para fuerzas en su plano y baja rigidez/resistencia perpendicular a su plano. Toda estructura conformada por muros estructurales debe tener componentes en las dos direcciones ortogonales principales de la edificación.

D.1.4.1.1 — Diferencia en rigidez entre las dos direcciones principales en planta — En edificaciones de mampostería estructural con tres niveles o más, la rigidez aportada por el conjunto de elementos estructurales en una dirección no puede ser inferior al 20% de la rigidez en la dirección ortogonal. En edificaciones de uno y dos niveles esta relación puede reducirse al 10%.

D.1.4.2 — MODELO MATEMÁTICO PARA REALIZAR EL ANÁLISIS — Se puede utilizar el modelo de muros en voladizo empotrados en la base y arriostrados lateralmente por los diafragmas de piso, o cualquier modelo estructural alternativo compatible con el funcionamiento real de la construcción, siempre que se garantice la mejor precisión de la respuesta por evidencia experimental o teórica.

D.1.4.3 — DIAFRAGMAS HORIZONTALES DE PISO — El sistema de piso usado como diafragma debe diseñarse teniendo en cuenta lo dispuesto en A.3.6.8.

D.1.4.4 — INCONVENIENCIA DE LA COMBINACIÓN DE SISTEMAS ESTRUCTURALES — No se considera conveniente la combinación en altura de sistemas estructurales de diferentes capacidades de disipación de energía, dado que la estructura puede trabajar en el rango inelástico bajo sismos severos.

D.1.4.5 — REQUISITOS PARA LA COMBINACIÓN DE SISTEMAS ESTRUCTURALES DE MAMPOSTERÍA — En caso de combinación en planta o en altura de sistemas estructurales diferentes, deben cumplirse los requisitos de A.3.2.4 y A.3.2.5.

D.1.4.6 — LÍMITES DE DERIVA PARA SISTEMAS DE MAMPOSTERÍA ESTRUCTURAL — Los límites de deriva para construcciones en mampostería estructural están indicados en la tabla A.6.4-1.

D.1.4.7 — REQUISITOS PARA LOS MATERIALES — Todos los materiales utilizados en la construcción de estructuras de mampostería deben cumplir las normas y especificaciones del capítulo D.3.

D.1.4.8 — CONDICIONES AMBIENTALES — Cuando las condiciones ambientales estén por fuera de las normales o puedan afectar negativamente las características especificadas de los materiales, deben tomarse precauciones adicionales que garanticen el funcionamiento correcto de la construcción.

D.1.4.9 — MANO DE OBRA EN LAS ESTRUCTURAS DE MAMPOSTERÍA — Debe darse especial importancia a la utilización de mano de obra calificada, con controles iniciales y previos que permitan determinar la calificación exigida al personal involucrado.""",
    },
    {
        "id": "NSR10-D-D_2_clasificacion_usos_normas",
        "seccion": "D.2.1 a D.2.3",
        "titulo": "Capítulo D.2 — Clasificación de la mampostería estructural, usos permitidos y normas NTC/ASTM citadas",
        "texto": """CAPÍTULO D.2 CLASIFICACIÓN, USOS, NORMAS, NOMENCLATURA Y DEFINICIONES

D.2.1 — CLASIFICACIÓN DE LA MAMPOSTERÍA ESTRUCTURAL. Estas normas reconocen los siguientes tipos de mampostería:

D.2.1.1 — MAMPOSTERÍA DE CAVIDAD REFORZADA — Construcción con dos paredes de piezas de mampostería de caras paralelas, reforzadas o no, separadas por un espacio continuo de concreto reforzado, con funcionamiento compuesto (capítulo D.6). Se clasifica como sistema con capacidad especial de disipación de energía en el rango inelástico (DES).

D.2.1.2 — MAMPOSTERÍA REFORZADA — Construcción con piezas de mampostería de perforación vertical, unidas por mortero, reforzada internamente con barras y alambres de acero (capítulo D.7). Se clasifica como DES cuando todas sus celdas se inyectan con mortero de relleno o se cumplen los refuerzos mínimos adicionales de D.7.2.1.1, y como DMO (capacidad moderada) cuando solo se inyectan las celdas verticales que llevan refuerzo.

D.2.1.3 — MAMPOSTERÍA PARCIALMENTE REFORZADA — Piezas de perforación vertical unidas por mortero, reforzada internamente (capítulo D.8). Se clasifica como DMO.

D.2.1.4 — MAMPOSTERÍA NO REFORZADA — Piezas unidas por mortero que no cumple las cuantías mínimas de refuerzo de la parcialmente reforzada (capítulo D.9). Se clasifica como DMI (capacidad mínima).

D.2.1.5 — MAMPOSTERÍA DE MUROS CONFINADOS — Piezas unidas por mortero, reforzada principalmente con elementos de concreto reforzado construidos alrededor del muro, confinándolo (capítulo D.10). Se clasifica como DMO.

D.2.1.6 — MAMPOSTERÍA DE MUROS DIAFRAGMA — Muros dentro de una estructura de pórticos que restringen su desplazamiento libre bajo cargas laterales (capítulo D.11). No se permite para edificaciones nuevas; su empleo solo se permite dentro del alcance del Capítulo A.10 (adición, modificación o remodelación de edificaciones existentes, o evaluación de vulnerabilidad sísmica).

D.2.1.7 — MAMPOSTERÍA REFORZADA EXTERNAMENTE — El refuerzo se coloca dentro de una capa de revoque (pañete), fijado al muro mediante conectores y/o clavos (capítulo D.12). Se clasifica como DMI.

D.2.2 — USOS DE LA MAMPOSTERÍA ESTRUCTURAL

D.2.2.1 — USOS PERMITIDOS — Se permite el uso de la mampostería estructural como sistema estructural, cumpliendo las salvedades del presente Título y las limitaciones del capítulo A.3 según la zona de amenaza sísmica, grupo de uso de la edificación y tipo de sistema estructural.

D.2.2.2 — COMBINACIÓN DE SISTEMAS ESTRUCTURALES — La combinación de sistemas que incluyen mampostería estructural debe cumplir los requisitos del capítulo A.3.

D.2.2.3 — ELEMENTOS DE CONCRETO REFORZADO DENTRO DE LA MAMPOSTERÍA ESTRUCTURAL — Se permite el empleo de elementos de concreto reforzado embebidos dentro de la mampostería o en combinación con ella (dinteles, vigas, elementos colectores de diafragmas, machones, etc.). Su diseño debe seguir los requisitos del Título C para el mismo grado de capacidad de disipación de energía asignado al tipo de mampostería en que están colocados. El coeficiente básico de disipación de energía R0 debe ser el mismo asignado al sistema de mampostería estructural en el capítulo A.3.

D.2.3 — NORMAS Y ESPECIFICACIONES CITADAS EN EL TÍTULO D. Las siguientes normas NTC (ICONTEC) y ASTM hacen parte integral del Título D (ver A.1.6 sobre su obligatoriedad). Entre las más relevantes: NTC 121/321 (cemento portland), NTC 4050/ASTM C91 (cemento para mampostería), NTC 4046/ASTM C5 (cal viva), NTC 4019/ASTM C207 (cal hidratada), NTC 161/248/2289 (barras de refuerzo, ASTM A615/A706), NTC 3329/ASTM C270 (mortero de pega), NTC 3356/ASTM C1142 (mortero premezclado de larga duración), NTC 4048/ASTM C476 (mortero de relleno/grout), NTC 2240/ASTM C144 (agregados para mortero de pega), NTC 4020/ASTM C404 (agregados para mortero de relleno), NTC 3495/ASTM E447 (resistencia a compresión de prismas de mampostería), NTC 3546/ASTM C780 (evaluación en laboratorio y obra de morteros), NTC 4026/ASTM C90 (bloques de concreto estructurales), NTC 4026/ASTM C55 (unidades macizas de concreto), NTC 4076/ASTM C129 (unidades de concreto no estructurales), NTC 4205/ASTM C34-C56-C62 (unidades de arcilla cocida), NTC 922/ASTM C73 (unidades sílico-calcáreas), NTC 4383 (términos y definiciones sobre mampostería de concreto).""",
    },
    {
        "id": "NSR10-D-D_2_nomenclatura_definiciones",
        "seccion": "D.2.4 a D.2.5",
        "titulo": "Capítulo D.2 — Nomenclatura (f'm, f'cp, f'cr, Vm, etc.) y definiciones de términos de mampostería",
        "texto": """D.2.4 — NOMENCLATURA (selección de las variables de mayor uso). Aa = coeficiente de aceleración pico efectiva (Título A). Ae = área efectiva de la sección de mampostería, mm² (D.5.4.1). Amv = área efectiva para determinar esfuerzos cortantes, mm² (D.5.4.5). Ast = área total de acero de refuerzo en la sección de muro, mm². Av = área de refuerzo horizontal que resiste cortante espaciado a separación s, mm². b = ancho efectivo de la sección, mm (D.5.4.4). c = profundidad del eje neutro en la zona de compresión, mm. d = distancia de la cara de compresión al centroide del refuerzo en tracción, mm. Em = módulo de elasticidad de la mampostería, MPa. Es = módulo de elasticidad del acero de refuerzo, MPa. f'c = resistencia especificada a la compresión del concreto de los elementos de confinamiento, MPa. f'cp = resistencia especificada a la compresión del mortero de pega, MPa. f'cr = resistencia especificada a la compresión del mortero de relleno, MPa. f'cu = resistencia especificada a la compresión de la unidad de mampostería sobre área neta, MPa. f'm = resistencia especificada a la compresión de la mampostería, MPa. fr = módulo de ruptura de la mampostería, MPa. fy = resistencia a la fluencia del acero de refuerzo, MPa. Gm = módulo de cortante de la mampostería, MPa. kp = factor de corrección por absorción de la unidad en mampostería no inyectada: 1.4 para unidades de concreto, 0.8 para unidades de arcilla o sílico-calcáreas. kr = factor de corrección por absorción de la unidad en mampostería inyectada: 0.90 para unidades de concreto, 0.75 para unidades de arcilla o sílico-calcáreas. Mn = resistencia nominal a flexión. Mu = momento mayorado solicitado de diseño del muro. Pn = resistencia nominal a carga axial, N. Pu = fuerza axial de diseño solicitada sobre el muro, N. R = coeficiente de capacidad de disipación de energía. R0 = coeficiente básico de capacidad de disipación de energía. Rm = parámetro definido por la ecuación D.3.7-1. r = relación entre el área neta y el área bruta de las unidades de mampostería. Vn = fuerza cortante resistente nominal del muro, N. Vm = resistencia nominal para fuerza cortante contribuida por la mampostería, N. Vu = fuerza cortante mayorada solicitada de diseño del muro, N. Vs = resistencia nominal para fuerza cortante contribuida por el refuerzo de cortante, N. εmu = máxima deformación unitaria permisible de compresión en la mampostería (εmu = 0.003). φ = coeficiente de reducción de resistencia. ρ = cuantía de refuerzo a tracción por flexión.

D.2.5 — DEFINICIONES (términos de mayor uso en el Título D; consultar además A.13, capítulo C.2 y NTC 4383). Absorción — Cantidad de agua que penetra en los poros de la unidad en relación al peso seco. Acción compuesta — Transferencia de esfuerzos entre componentes de un elemento que actúan en conjunto como uno solo. Área neta de la sección — Área de la unidad de mampostería incluyendo morteros de relleno y excluyendo cavidades. Bloque de perforación vertical — Bloque de concreto o arcilla cocida con perforaciones verticales que forman celdas donde se coloca el refuerzo; en celdas con refuerzo vertical debe colocarse mortero de relleno. Cemento de mampostería — Cemento hidráulico para mortero de pega, con mayor plasticidad y retención de agua que el cemento Portland solo. Cuantía — Relación entre el área transversal del refuerzo y el área bruta de la sección considerada. Dimensiones nominales — Dimensiones modulares de la unidad incluyendo espesores de pega/acabados; no exceden en más de 10 mm las dimensiones reales. Junta de control — Separación continua que reduce la transferencia de esfuerzos, para permitir desplazamientos controlados. Mortero de pega — Mezcla plástica de cementantes, agregado fino y agua, usada para unir unidades de mampostería. Mortero de relleno — Mezcla fluida de cementantes, agregados y agua, para colocarse sin segregación en celdas o cavidades. Mortero de recubrimiento o revoque (pañete) — Mezcla plástica para dar acabado liso (enlucir) los muros. Murete o prisma — Ensamble de piezas de mampostería con mortero de pega, inyectado o no, usado como espécimen de ensayo para determinar propiedades de la mampostería. Muro estructural — Elemento de longitud considerable respecto a su espesor, que atiende cargas en su plano además de su peso propio. Muro no estructural — Elemento que separa espacios y solo atiende cargas de su peso propio. Resistencia a la compresión de la mampostería (f'm) — Mínima resistencia nominal de la mampostería a compresión, medida sobre el área transversal neta, sobre la cual se basa su diseño. Unidad de mampostería — Elemento de colocación manual, de características pétreas y estabilidad dimensional, que unida con mortero configura el muro de mampostería.""",
    },
    {
        "id": "NSR10-D-D_3_cemento_acero_mortero_pega",
        "seccion": "D.3.1 a D.3.4",
        "titulo": "Capítulo D.3 — Cemento y cal, acero de refuerzo, mortero de pega (Tabla D.3.4-1: tipos H/M/S/N)",
        "texto": """CAPÍTULO D.3 CALIDAD DE LOS MATERIALES EN LA MAMPOSTERÍA ESTRUCTURAL

D.3.1 — ASPECTOS GENERALES. D.3.1.1 — REQUISITOS PARA LOS MATERIALES — Los materiales utilizados en las construcciones de mampostería estructural deben cumplir los requisitos de calidad del presente Capítulo, comprobado mediante ensayos sobre muestras representativas. D.3.1.2 — ENSAYOS DE CONTROL DE CALIDAD — Deben seguirse las normas técnicas colombianas NTC respectivas; a falta de ellas, las normas ASTM mencionadas en el Reglamento (ver D.2.3).

D.3.2 — CEMENTO Y CAL. D.3.2.1 — El cemento debe corresponder en tipo y clase a aquel sobre el cual se basan las dosificaciones del concreto y los morteros: Cemento portland NTC 121 y NTC 321 (se permite ASTM C150/C595); Cemento para mampostería NTC 4050 (ASTM C91); Cal viva NTC 4046 (ASTM C5); Cal hidratada NTC 4019 (ASTM C270).

D.3.3 — ACERO DE REFUERZO. D.3.3.1 — El acero de refuerzo debe cumplir los mismos requisitos de C.3.5 y ajustarse a las normas de producción y uso allí mencionadas. Al momento de la colocación debe estar limpio, sin corrosión y figurado según planos.

D.3.4 — MORTERO DE PEGA. D.3.4.1 — REQUISITOS GENERALES — Los morteros de pega deben cumplir la norma NTC 3329 (ASTM C270) y lo especificado en la Tabla D.3.4-1. El mortero premezclado debe cumplir NTC 3356 (ASTM C1142). Deben tener buena plasticidad, consistencia y retención de agua mínima para la hidratación del cemento, garantizando adherencia con las unidades.

Tabla D.3.4-1 Clasificación de los morteros de pega por propiedad o por proporción:
— Tipo H: resistencia mínima a la compresión f'cp = 22.5 MPa; flujo 115-125%; retención mínima de agua 75%; proporción cementante 1 parte cemento portland : 0.25 cal hidratada (no aplica cemento de mampostería); arena/material cementante entre 2.00 y 2.5.
— Tipo M: f'cp = 17.5 MPa; flujo 115-125%; retención 75%; alternativa cemento portland:cal hidratada 1:0.25 (arena 2.25-3.0), o cemento portland:cemento para mampostería 1:1 (arena 2.25-2.5).
— Tipo S: f'cp = 12.5 MPa; flujo 110-120%; retención 75%; cemento portland:cal hidratada 1:(0.25 a 0.50) (arena 2.50-3.5), o cemento portland:cemento para mampostería 1:0.5 (arena 2.50-3.0).
— Tipo N: f'cp = 7.5 MPa; flujo 105-115%; retención 75%; cemento portland:cal hidratada 1:(0.50 a 1.25) (arena 3.00-4.5), o cemento portland:cemento para mampostería 1:1 (arena 3.00-4.0). El mortero tipo N solo se permite en sistemas con capacidad mínima de disipación de energía (DMI).
Notas de la tabla: resistencia medida a 28 días en cubos de 50 mm de lado (NTC 3546/ASTM C780 para control en obra); no se incluye la cal como cementante en el cálculo arena/cementante; el tipo de cemento para mampostería (M, S o N) debe ser el mismo que el tipo de mortero de pega; no se permiten dosificaciones que combinen simultáneamente cal hidratada y cemento de mampostería.

D.3.4.2 — DOSIFICACIÓN DEL MORTERO DE PEGA — Debe basarse en ensayos previos de laboratorio o experiencia de campo en obras similares. La resistencia se mide a 28 días en cubos de 50 mm de lado o cilindros de 75×150 mm. D.3.4.2.1 — Probetas cilíndricas — Sus resultados deben correlacionarse respecto a los de cubos de 50 mm, según NTC 3546 (ASTM C780). D.3.4.3 — USO DE LA CAL — Debe ser cal hidratada, verificando que no sea perjudicial a las propiedades especificadas. D.3.4.4 — AGREGADOS — Deben cumplir NTC 2240 (ASTM C144), libres de contaminantes. D.3.4.5 — AGUA — Debe estar limpia y libre de sustancias dañinas (cumplir C.3.4). D.3.4.6 — COLORANTES Y ADITIVOS — Requieren aprobación previa del supervisor técnico y evidencia de que no deterioran propiedades ni causan corrosión del refuerzo. D.3.4.7 — PREPARACIÓN EN OBRA — Con mezcladoras mecánicas apropiadas; tiempo de mezclado suficiente para uniformidad sin segregación; preparación manual solo para obras menores. D.3.4.7.1 — Morteros mezclados en seco en obra no pueden usarse después de 2 horas y media de mezclados (excepto los de larga vida). D.3.4.7.2 — Morteros premezclados de larga vida — Usarse según instrucciones y tiempo del fabricante, verificando que no presenten deterioro al momento de usarse.""",
    },
    {
        "id": "NSR10-D-D_3_mortero_relleno_unidades",
        "seccion": "D.3.5 a D.3.6",
        "titulo": "Capítulo D.3 — Mortero de relleno (Tabla D.3.5-1) y unidades de mampostería (Tabla D.3.6-1: espesores mínimos)",
        "texto": """D.3.5 — MORTERO DE RELLENO. D.3.5.1 — REQUISITOS GENERALES — Debe cumplir NTC 4048 (ASTM C476); buena consistencia y fluidez suficiente para penetrar en las celdas de inyección sin segregación. D.3.5.2 — DOSIFICACIÓN — Basada en ensayos previos de laboratorio o experiencia de campo, según la Tabla D.3.5-1. La resistencia f'cr se mide a 28 días sobre probetas tomadas en las celdas de las unidades huecas o en prismas, con papel permeable, según NTC 4043 (ASTM C1019); también puede medirse en cilindros de 75×150 mm (NTC 3546/ASTM C780 para mortero de relleno fino; C.5.6.3.1 y C.5.6.3.2 para mortero de relleno grueso).

Tabla D.3.5-1 Clasificación y dosificación por volumen de los morteros de relleno:
— Mortero Fino: relación cemento portland 1 : agregado fino (arena) mínimo 2.25 - máximo 3.5; no aplica agregado grueso.
— Mortero Grueso: relación cemento portland 1 : agregado fino mínimo 2.25 - máximo 3.0; agregado grueso (tamaño menor de 10 mm) mínimo 1.0 - máximo 2.0.

D.3.5.3 — VALOR MÁXIMO DE LA RESISTENCIA A LA COMPRESIÓN — La resistencia del mortero de relleno a 28 días, f'cr, debe tener un valor máximo de 1.5 veces f'm y un valor mínimo de 1.25 veces f'm, pero en ningún caso puede ser inferior a 12.5 MPa. D.3.5.4 — USO DE LA CAL — Debe cumplir NTC 4019 (ASTM C207), dosificación máxima 10% del volumen de cemento. D.3.5.5 — AGREGADOS — Deben cumplir NTC 4020 (ASTM C404), libres de contaminantes. D.3.5.6 — AGUA Y ADITIVOS — Deben cumplir D.3.4.5 y D.3.4.6, en concordancia con C.3.4 y C.3.6. D.3.5.7 — MEZCLADO Y TRANSPORTE — Con mezcladoras mecánicas apropiadas, garantizando la conservación de consistencia y plasticidad durante el transporte hasta el sitio de inyección.

D.3.6 — UNIDADES DE MAMPOSTERÍA. D.3.6.1 — TIPOS — Pueden ser de concreto, cerámica (arcilla cocida), sílico-calcáreas o piedra; de perforación vertical, horizontal o sólidas (cavidades menores al 25% del volumen de la pieza) según la posición normal en el muro. D.3.6.2 — NORMAS DE PRODUCCIÓN Y CALIDAD: Unidades de concreto: bloque de perforación vertical portante NTC 4026 (ASTM C90); unidades macizas (tolete) portantes NTC 4026 (ASTM C55); unidades no estructurales NTC 4076 (ASTM C129). Unidades de arcilla: bloque de perforación vertical estructural NTC 4205-1 (ASTM C34); macizas (tolete) estructurales NTC 4205-1 (ASTM C62, C652); no estructurales NTC 4205-2 (ASTM C56, C212, C216); perforación horizontal estructural NTC 4205-1 (ASTM C56, C212); para fachadas NTC 4205-3. Unidades sílico-calcáreas: NTC 922 (ASTM C73). D.3.6.3 — UNIDADES ESPECIALES — Deben cumplir las especificaciones de las unidades típicas del mismo material. D.3.6.4 — UNIDADES DE PERFORACIÓN VERTICAL — Se pueden usar en todos los tipos de mampostería estructural de D.2.1. D.3.6.4.1 — El área de celdas verticales no puede ser mayor al 65% del área de la sección transversal; celdas para refuerzo no menores de 50 mm ni de 3000 mm² de área.

Tabla D.3.6-1 Espesores mínimos de paredes en unidades (bloques) de perforación vertical (mm):
— Espesor externo nominal 80 mm(1): espesor mínimo de paredes exteriores sin perforaciones secundarias 20 mm, con perforaciones secundarias 30 mm; tabiques transversales 20 mm.
— 100 mm: exteriores 20 mm (30 con perforaciones), tabiques 20 mm.
— 120 mm: exteriores 22 mm (32 con perforaciones), tabiques 20 mm.
— 150 mm: exteriores 25 mm (35), tabiques 25 mm.
— 200 mm: exteriores 30 mm (40), tabiques 25 mm.
— 250 mm: exteriores 35 mm (45), tabiques 30 mm.
— 300 mm: exteriores 40 mm (50), tabiques 30 mm.
Nota (1): la unidad de 80 mm de espesor externo nominal solo se permite en muros no estructurales y en paredes laterales de mampostería de cavidad.

D.3.6.4.2 — Perforaciones secundarias en arcilla cocida no pueden tener dimensión transversal mayor de 20 mm ni estar a menos de 10 mm del borde de la pared perforada. D.3.6.5 — UNIDADES DE PERFORACIÓN HORIZONTAL — Solo en mampostería de muros confinados, de cavidad reforzada y reforzada externamente (o combinadas con perforación vertical en edificaciones de uno y dos pisos grupo de uso I, no reforzada o parcialmente reforzada). D.3.6.6 — UNIDADES MACIZAS — Mismo alcance de uso que D.3.6.5, y también combinadas con perforación vertical para mampostería parcialmente reforzada.""",
    },
    {
        "id": "NSR10-D-D_3_fm_evaluacion",
        "seccion": "D.3.7 a D.3.8",
        "titulo": "Capítulo D.3 — Determinación de f'm (registros históricos, muretes, calidad de materiales; fórmulas D.3.7-1/2/3) y evaluación/aceptación de la mampostería",
        "texto": """D.3.7 — DETERMINACIÓN DE LA RESISTENCIA DE LA MAMPOSTERÍA A LA COMPRESIÓN f'm. D.3.7.1 — El valor especificado de f'm se determina por uno de: (a) registros históricos (D.3.7.3); (b) determinación experimental sobre muretes de prueba (D.3.7.4); (c) ensayos sobre materiales individuales (D.3.7.5). D.3.7.1.1 — Los valores de f'm basados en calidad de materiales solo se usan en diseño previo a la construcción, no para control de calidad.

D.3.7.2 — ELABORACIÓN Y ENSAYO DE LOS MURETES — Según NTC 3495 (ASTM E447). D.3.7.2.1 — Deben elaborarse con los mismos materiales y condiciones de la estructura (humedad, mano de obra). D.3.7.2.2 — El valor de f'm de una muestra es el promedio de 3 muretes de igual procedencia, sin exceder el 125% del menor valor obtenido. D.3.7.2.3 — Se obtiene dividiendo la carga última por el área neta del murete. D.3.7.2.4 — Los muretes deben tener mínimo 300 mm de altura, relación altura-ancho entre 1.5 y 5; para bloque de perforación vertical, al menos el largo de una pieza completa; otros tipos al menos 100 mm de largo.

D.3.7.2.5 — Corrección por esbeltez — El valor de f'm debe corregirse multiplicándolo por el factor de la Tabla D.3.7-1: relación altura/espesor del murete 1.5 → factor 0.86; 2.0 → 1.0; 2.5 → 1.04; 3.0 → 1.07; 4.0 → 1.15; 5.0 → 1.22.

D.3.7.2.6 — Curado — 7 días al aire a 21°C ±5°, humedad relativa >90%, luego humedad 30-50% hasta ensayo a los 28 días. D.3.7.2.7 — Refrentado y ensayo bajo NTC 3495 (ASTM E447).

D.3.7.3 — DETERMINACIÓN ESTADÍSTICA DE f'm (registros históricos, coeficiente de variación ≤30%): D.3.7.3.1 — Más de 30 ensayos históricos: f'm = 75% del promedio del registro. D.3.7.3.2 — Entre 10 y 30 ensayos: f'm = 70% del promedio. D.3.7.3.3 — Menos de 10 ensayos (con 3 o más muretes por prueba): no pueden usarse registros históricos.

D.3.7.4 — DETERMINACIÓN EXPERIMENTAL DE f'm (ensayos previos a la obra): D.3.7.4.1 — 30 o más muretes: f'm = 85% del promedio. D.3.7.4.2 — Entre 10 y 30 muretes: f'm = 80% del promedio. D.3.7.4.3 — Entre 3 y 10 muretes: f'm = 75% del promedio.

D.3.7.5 — VALOR DE f'm BASADO EN LA CALIDAD DE LOS MATERIALES — En ausencia de correlación apropiada, se determina mediante: Rm = [75/(2h+3hcu)]·f'cu + [75/(50kp+3hcu)]·f'cp ≤ 0.8·f'cu (ecuación D.3.7-1); f'm = 0.75·Rm (ecuación D.3.7-2). Los valores deben indicarse en planos estructurales y controlarse en obra según D.3.8, sin eximir la comprobación de f'm por muretes (D.3.8.1.4).

D.3.7.6 — VALOR DE f'm CUANDO LAS CELDAS SE INYECTAN CON MORTERO DE RELLENO — Para mampostería de cavidad reforzada o de perforación vertical inyectada: f'm = 0.75·[r·Rm + 0.9·kr·(1-r)·f'cr] ≤ 0.94·Rm (ecuación D.3.7-3).

D.3.8 — EVALUACIÓN Y ACEPTACIÓN DE LA MAMPOSTERÍA. D.3.8.1 — FRECUENCIA DE MUESTREO Y ENSAYOS (mínimos): D.3.8.1.1 — Mortero de pega: 1 ensayo de resistencia (promedio 3 probetas) por cada 200 m² de muro o por día de pega; verificar semanalmente plasticidad y retención de agua. D.3.8.1.2 — Mortero de relleno: 1 ensayo por cada 10 m³ de mortero inyectado o por día de inyección. D.3.8.1.3 — Unidades de mampostería: ensayos de absorción inicial, absorción total, estabilidad dimensional y resistencia a compresión de al menos 5 unidades por lote de hasta 5000 unidades, y no menos de 1 unidad por cada 200 m² de muro construido. D.3.8.1.4 — Muretes: f'm debe verificarse con al menos 3 muretes por cada 500 m² de muro o fracción, con los materiales y procedimientos de obra; para unidades de perforación vertical debe medirse el efecto del mortero de relleno con ensayos adicionales de muretes inyectados, en cantidad no inferior al 50% del total de especímenes. D.3.8.1.5 — Acero de refuerzo: según C.3.5.10.

D.3.8.2 — CRITERIOS DE ACEPTACIÓN Y RECHAZO. D.3.8.2.1 — Resistencia mínima: la mampostería es satisfactoria si el promedio de resistencias (morteros de pega, relleno, unidades y muretes) es ≥ la resistencia especificada, y ningún valor individual es inferior al 80% de la especificada. D.3.8.2.2 — Medidas correctivas: si no se cumple, deben tomarse medidas de inmediato para aumentar el promedio de evaluaciones subsiguientes. D.3.8.2.3 — Resultados bajos: si algún resultado individual es inferior al 80%, deben asegurar que la capacidad de carga no se haya comprometido; en caso de confirmarse baja resistencia con impacto significativo, se puede apelar al ensayo de extracción de 3 porciones cortadas por lote afectado (resistencia promedio ≥80% de la especificada). D.3.8.2.4 — Pruebas de carga: si persiste la duda sobre seguridad estructural, el supervisor técnico puede ordenar pruebas de carga como las del Capítulo C.20.""",
    },
]


# El modelo de embeddings (paraphrase-multilingual-MiniLM-L12-v2) trunca
# duro a 128 tokens -- verificado empiricamente el 2026-08-03 (warning
# explicito de sentence-transformers + prueba de similitud coseno). En
# texto tecnico en espanol la relacion real es ~3.5-3.8 caracteres/token,
# asi que el limite seguro de caracteres por chunk es ~400-450, NO el
# tamano de "capitulo completo" (4000-7000 chars) que se escribio arriba
# para mantener legible el codigo fuente de este script. Este limite
# aplica solo a la busqueda semantica -- el texto guardado en Supabase
# puede ser mas largo, pero si el chunk es mas largo que esto la busqueda
# vectorial solo "ve" el principio y el resto queda invisible para RAG.
# El proxy de caracteres (~420) no es exacto para texto denso en simbolos,
# numeros y listas tecnicas (ej. la lista de normas NTC/ASTM o la tabla de
# nomenclatura f'm/f'cp/etc.) -- esos fragmentos tokenizan mas denso que
# prosa normal. Se mide el conteo real de tokens del propio tokenizer del
# modelo, no una aproximacion por caracteres -- verificado el 2026-08-03
# tras encontrar 7/92 subchunks que excedian 128 pese a tener <420 chars.
MAX_TOKENS_POR_SUBCHUNK = 110  # margen bajo 128 para [CLS]/[SEP] y variacion


def _dividir_en_subchunks(texto: str, tokenizer, max_tokens: int = MAX_TOKENS_POR_SUBCHUNK) -> list[str]:
    """Divide por parrafo (separados por \\n\\n, cada uno ya es un articulo
    NSR-10 completo en el texto verbatim de arriba), empacando parrafos
    consecutivos hasta el limite de tokens reales. Un parrafo que por si
    solo excede el limite (ej. el bloque de la Tabla D.3.4-1) se divide
    por oracion."""
    def n_tok(s: str) -> int:
        return len(tokenizer.encode(s))

    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    subchunks: list[str] = []
    actual = ""
    for parrafo in parrafos:
        candidato = f"{actual}\n\n{parrafo}" if actual else parrafo
        if n_tok(candidato) <= max_tokens:
            actual = candidato
            continue
        if actual:
            subchunks.append(actual)
            actual = ""
        if n_tok(parrafo) <= max_tokens:
            actual = parrafo
            continue
        # Parrafo individual demasiado largo (ej. tabla): dividir por oracion.
        oraciones = re.split(r"(?<=[.;])\s+", parrafo)
        buffer = ""
        for oracion in oraciones:
            # Una sola "oracion" (sin punto/punto y coma intermedio, ej. una
            # enumeracion larga separada solo por comas) puede seguir
            # excediendo el limite por si sola -- dividir por coma como
            # ultimo recurso.
            fragmentos = (
                re.split(r"(?<=,)\s+", oracion)
                if n_tok(oracion) > max_tokens
                else [oracion]
            )
            for frag in fragmentos:
                cand = f"{buffer} {frag}".strip() if buffer else frag
                if n_tok(cand) <= max_tokens:
                    buffer = cand
                else:
                    if buffer:
                        subchunks.append(buffer)
                    buffer = frag
        if buffer:
            actual = buffer
    if actual:
        subchunks.append(actual)
    return subchunks


def insertar(dry_run: bool = False):
    from supabase import create_client

    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        print("ERROR: Configura SUPABASE_URL y SUPABASE_SERVICE_KEY en .env")
        return

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    filas_planas = []
    for chunk in CHUNKS:
        subchunks = _dividir_en_subchunks(chunk["texto"], model.tokenizer)
        for i, sub in enumerate(subchunks, start=1):
            filas_planas.append({
                "id": f"{chunk['id']}-{i:02d}" if len(subchunks) > 1 else chunk["id"],
                "titulo": chunk["titulo"],
                "seccion": chunk["seccion"],
                "texto": sub,
            })

    textos = [f["texto"] for f in filas_planas]
    embeddings = model.encode(textos, normalize_embeddings=True, batch_size=16).tolist()

    excedidos = 0
    rows = []
    for f, emb in zip(filas_planas, embeddings):
        n_tokens = len(model.tokenizer.encode(f["texto"]))
        if n_tokens > 128:
            excedidos += 1
        rows.append({
            "id": f["id"],
            "capitulo": CAPITULO_LABEL,
            "titulo": f["titulo"],
            "seccion": f["seccion"],
            "texto": f["texto"],
            "embedding": emb,
        })

    print(f"{len(CHUNKS)} bloques originales -> {len(rows)} subchunks reales (limite 128 tokens):")
    for r in rows:
        print(f"  {r['id']} — {r['seccion']} — {len(r['texto'])} chars")
    print(f"\nSubchunks que exceden 128 tokens (se truncarian en la busqueda): {excedidos}/{len(rows)}")

    if dry_run:
        print("[dry-run] No se inserta en Supabase.")
        return

    if excedidos > 0:
        print("ABORTADO: hay subchunks que exceden el limite de tokens. Revisar antes de insertar.")
        return

    sb = create_client(supabase_url, supabase_key)
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print(f"OK: {len(rows)} chunks insertados/actualizados en nsr10_chunks.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    insertar(dry_run=dry)
