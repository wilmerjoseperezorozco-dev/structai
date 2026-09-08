"""
Ingesta verbatim de Título H, Capítulo H.9 (Condiciones geotécnicas
especiales: suelos expansivos, dispersivos/erodables, colapsables,
efectos de la vegetación) -- NSR-10.

Fuente: NSR-10-1451-1500.pdf, páginas PDF 36-47 (H-47 a H-58), leídas
visualmente con Read pages= sobre el PDF nativo (nunca texto plano, ver
CLAUDE.md). Continuidad exacta desde el fin de H.8 (H-46, página en
blanco "Notas") confirmada.

Mismo patrón de 2 scripts ya establecido (H.3.3+H.4, H.5, H.6, H.7,
H.8): este script sube los chunks-padre (grandes); el script
_resplit_titulo_h_h9_por_limite_tokens.py los re-trochea con
verificación real de tokens antes de dejarlos en producción.

Uso: python _ingest_titulo_h_h9_verbatim.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "apps" / "api" / ".env")

CAPITULO = "H"

CHUNKS = [
    {
        "id": "NSR10-H-H_9_0_nomenclatura",
        "seccion": "H.9.0 — Nomenclatura del Capítulo H.9",
        "titulo": "Título H, H.9.0: glosario de símbolos usados en el capítulo de condiciones geotécnicas especiales (suelos expansivos, colapsables, vegetación).",
        "texto": (
            "CAPÍTULO H.9 — CONDICIONES GEOTÉCNICAS ESPECIALES\n\n"
            "H.9.0 — NOMENCLATURA\n\n"
            "B = coeficiente de proporcionalidad\n"
            "c_w = coeficiente de hidroconsolidación\n"
            "G_s = gravedad específica del suelo\n"
            "h = altura negativa de agua en el suelo; altura de succión\n"
            "H_i = espesor de la capa i del suelo potencialmente colapsable\n"
            "IP = Índice de plasticidad\n"
            "LL = límite líquido en porcentaje\n"
            "p = presión total en el suelo\n"
            "P_ex = presión de expansión probable en el campo (kgf/cm2)\n"
            "pF = succión, expresada como el logaritmo de la altura negativa de presión de poros\n"
            "S = grado de saturación\n"
            "s = succión, en términos de presión\n"
            "S_o = grado de saturación inicial\n"
            "u = presión de poros\n"
            "w_eq = humedad de equilibrio\n"
            "w_l = límite líquido en fracción decimal\n"
            "W_N = Humedad natural\n"
            "z = profundidad\n"
            "alfa = saturación relativa, o grado de humedecimiento\n"
            "omega_eq = humedad de equilibrio en porcentaje\n"
            "gamma_w = peso unitario del agua (g/cm3)\n"
            "gamma_d = peso unitario seco (g/cm3)\n"
            "gamma_dcrit = peso unitario crítico como identificación de la colapsibilidad\n"
            "epsilon_w = potencial de hidrocolapso\n"
            "d(epsilon_w) = derivada del potencial de hidrocolapso\n"
            "delta_w = asentamiento por hidroconsolidación\n"
            "sigma_t = umbral de esfuerzo de colapso\n"
            "sigma_v = esfuerzo vertical total\n"
            "alfa = fracción de la presión total que actúa como presión de poros\n"
            "epsilon_w = deformación potencial de hidrocolapso\n"
            "sigma = esfuerzo normal al cual tiene lugar la hidroconsolidación\n"
            "omega_N = humedad natural en fracción decimal\n"
            "gamma_w = peso unitario del agua, en las unidades pertinentes"
        ),
    },
    {
        "id": "NSR10-H-H_9_1_1_a_H_9_1_2_1",
        "seccion": "H.9.1.1 a H.9.1.2.1 — Suelos expansivos: generalidades y zona activa",
        "titulo": "Título H, H.9.1: generalidades de suelos expansivos (montmorilonita, vermiculita, haloisita) y profundidad de la zona activa (Figura H.9.1-2).",
        "texto": (
            "H.9.1 — SUELOS EXPANSIVOS\n\n"
            "H.9.1.1 — GENERALIDADES — Como característica especial, todas las arcillas "
            "tienen, de una forma u otra, la propiedad de contraerse cuando pierden "
            "humedad y de expandirse cuando la ganan de nuevo según las condiciones "
            "ambientales. Como minerales activos se reconocen la montmorilonita, la "
            "vermiculita y algunas variedades de haloisita; la particularidad de éstos "
            "radica en que tienen la propiedad de \"absorber\" moléculas de agua dentro "
            "de su propia estructura molecular.\n\n"
            "Los daños que presentan las edificaciones cimentadas superficialmente en "
            "estos suelos se manifiestan progresivamente mediante fisuramientos, "
            "agrietamientos y giros de conjunto de los muros y elementos estructurales, "
            "a causa de movimientos desiguales de sus cimientos, especialmente en los "
            "años de prolongados períodos de verano e invierno, como los causados por "
            "los fenómenos del Niño y de la Niña. En los artículos H-9.1.6 a H-9.1.8 se "
            "presentan algunas medidas para mitigar este fenómeno.\n\n"
            "H.9.1.2 — PROFUNDIDAD DE LA ZONA ACTIVA — Se identifica la zona activa, en "
            "relación con los suelos expansivos, como la máxima profundidad a la que se "
            "observan fluctuaciones estacionales de humedad. La zona activa y su "
            "extensión se presentan esquemáticamente en la figura H.9.1-2 (perfil de "
            "profundidad vs. humedad natural W_N en verano/invierno, con la profundidad "
            "de variación estacional y la máxima profundidad de desecación, hasta el "
            "nivel freático).\n\n"
            "H.9.1.2.1 — Caso con el nivel freático — La expansividad cesa bajo la "
            "posición del nivel freático pero puede verse afectada por las oscilaciones "
            "de éste, de acuerdo con los factores climáticos."
        ),
    },
    {
        "id": "NSR10-H-H_9_1_3_identificacion_tabla",
        "seccion": "H.9.1.3 — Identificación de los suelos expansivos + Tabla H.9.1-1",
        "titulo": "Título H, H.9.1.3: identificación de suelos expansivos (IGAC, paleocauces) y Tabla H.9.1-1 de clasificación por expansión/límite líquido/IP.",
        "texto": (
            "H.9.1.3 — IDENTIFICACIÓN DE LOS SUELOS EXPANSIVOS — Se debe observar el "
            "comportamiento de edificaciones vecinas, en cuanto a señales de "
            "asentamientos diferenciales, pérdida de verticalidad, fisuras, etc., como "
            "resultado de procesos de expansión y contracción volumétrica del subsuelo. "
            "Si el reconocimiento se realiza en verano, se debe verificar la existencia "
            "de grietas en la superficie del terreno, tanto en la dirección vertical "
            "como horizontal.\n\n"
            "En los mapas e informes de suelos del Instituto Geográfico Agustín Codazzi "
            "(IGAC) es posible identificar áreas donde existan suelos potencialmente "
            "expansivos, los cuales se denominan \"vertisoles\" o suelos con "
            "\"característica vértica\". En la taxonomía agrológica se identifican con "
            "el sufijo \"ert\" o con la palabra \"Vertic\" (por ejemplo: Udert, Haplustert, "
            "Vertic Paleoudult, etc).\n\n"
            "Los mapas geológicos y geomorfológicos del área, y especialmente las "
            "fotografías aéreas estereoscópicas, son útiles para la identificación de "
            "paleocauces que se encuentran cubiertos por eventos naturales o antrópicos "
            "en los procesos urbanísticos. Estos paleocauces pueden ocasionar "
            "importantes incrementos en el contenido de agua del subsuelo durante las "
            "temporadas de lluvias, y por lo tanto altas expansiones y posteriores "
            "contracciones diferenciales en el terreno durante el verano. Se debe "
            "verificar y precisar su localización, profundidad, dimensiones y "
            "materiales, mediante técnicas de exploración directas o indirectas.\n\n"
            "Se debe evaluar el régimen de las aguas subterráneas, el nivel freático y "
            "las probables fluctuaciones durante la vida útil del proyecto, dado que "
            "estas condiciones son muy importantes para definir la profundidad de la "
            "zona activa. Lentes o bolsas de materiales granulares pueden pertenecer a "
            "paleocauces y propiciar condiciones favorables para producir variaciones "
            "estacionales de la humedad en el subsuelo, incrementado considerablemente "
            "el espesor de la zona activa.\n\n"
            "Se debe realizar la exploración de campo de acuerdo a los requisitos "
            "establecidos en el Capítulo H.3 de estas Normas. Por lo menos el 50% de "
            "los sondeos deben reconocer suficientemente los materiales que se "
            "encuentran por debajo de la zona activa.\n\n"
            "En la tabla H.9.1-1 se reproducen los criterios de laboratorio más "
            "aceptados para el reconocimiento de los suelos expansivos basados en "
            "altos valores del límite líquido, del índice de plasticidad, contenido de "
            "partículas coloidales y bajos valores del límite de contracción. Estos "
            "criterios deben verificarse en el laboratorio mediante ensayos de las "
            "propiedades índices correspondientes y de expansión en el consolidómetro.\n\n"
            "Tabla H.9.1-1 — Clasificación de suelos expansivos:\n"
            "Potencial de expansión | Expansión (%) medida en consolidómetro bajo "
            "presión vertical de 0.07 kgf/cm2 | Límite líquido LL (%) | Límite de "
            "contracción (%) | Índice de plasticidad IP (%) | Porcentaje de partículas "
            "menores de una micra (μ) | Expansión libre EL en (%), medida en probeta\n"
            "Muy alto | > 30 | > 63 | < 10 | > 32 | > 37 | > 100\n"
            "Alto | 20-30 | 50-63 | 6-12 | 23-45 | 18-37 | > 100\n"
            "Medio | 10-20 | 39-50 | 8-18 | 12-34 | 12-27 | 50-100\n"
            "Bajo | < 10 | < 39 | > 13 | < 20 | < 17 | < 50"
        ),
    },
    {
        "id": "NSR10-H-H_9_1_4_H_9_1_5",
        "seccion": "H.9.1.4 y H.9.1.5 — Humedad de equilibrio y modelos geotécnicos",
        "titulo": "Título H, H.9.1.4-H.9.1.5: humedad de equilibrio, alteración del equilibrio suelo-vegetación-clima, y modelos geotécnicos para suelos no saturados.",
        "texto": (
            "H.9.1.4 — HUMEDAD DE EQUILIBRIO — Se ha definido la humedad de equilibrio "
            "como aquella que corresponde a la avidez natural del suelo por el agua; "
            "si la humedad natural es inferior, el suelo buscará satisfacerla, proceso "
            "en el cual tiene lugar la expansión.\n\n"
            "En terrenos de intensa dinámica fluvial, los climas estacionales producen "
            "fluctuaciones del nivel freático que ocasionan cambios de humedad/succión "
            "desiguales en el subsuelo, y por lo tanto cambios volumétricos desiguales "
            "en el subsuelo. En las zonas donde hay evidencias que existen paleocauces "
            "en el subsuelo, la cabeza piezométrica en ellos se incrementa durante la "
            "temporada lluviosa, ocasionando expansiones desiguales del terreno.\n\n"
            "Cuando se interviene el terreno, se altera el equilibrio que la naturaleza "
            "establece entre el suelo, la vegetación y el clima. Al retirar la capa "
            "vegetal, la cual debido a su baja permeabilidad protege al subsuelo de la "
            "evaporación excesiva y de la infiltración de las aguas lluvias, se deja al "
            "subsuelo en condiciones más críticas para el control de los cambios de "
            "humedad, pues la evaporación se aumenta en el verano y la infiltración de "
            "las aguas lluvias se incrementa en el invierno. Si esta se reemplaza por "
            "materiales granulares de alta permeabilidad, la condición también es "
            "crítica.\n\n"
            "Al edificar, o simplemente cubrir el terreno, se interrumpe el equilibrio "
            "pues se altera el gradiente térmico existente en el subsuelo y se producen "
            "fenómenos de migración de agua y acción capilar. Esto ocasiona un aumento "
            "desigual de la humedad en la zona activa, el cual es considerablemente "
            "mayor en el centro del área cubierta, y por lo tanto se produce una "
            "expansión desigual del terreno. Si las fugas de las redes del acueducto y "
            "alcantarillado se acumulan en el relleno de materiales muy permeables, "
            "también se incrementan las expansiones diferenciales de la zona activa.\n\n"
            "La vegetación y especialmente las raíces de los árboles ornamentales que "
            "se siembran al urbanizar los terrenos, al extraer el agua que necesitan "
            "para su supervivencia también afectan el equilibrio dinámico del "
            "subsuelo. En los meses del año en que la evapotranspiración excede a la "
            "precipitación se reduce desigualmente la humedad de la zona activa. Se "
            "presenta mayor reducción de humedad en las áreas descubiertas y con mayor "
            "vegetación, mayor succión y por lo tanto se produce una mayor contracción "
            "del terreno en estas áreas. La substitución selectiva de los árboles "
            "restablece el equilibrio dinámico del subsuelo y detiene el proceso de "
            "desecación y asentamiento (véase el artículo H.9.4).\n\n"
            "H-9.1.5 — MODELOS GEOTÉCNICOS — Para desarrollar los modelos geotécnicos "
            "de la mecánica de suelos no saturados, relacionados con los cambios "
            "volumétricos, flujo de agua y resistencia al esfuerzo cortante, se ha "
            "propuesto el uso de las curvas de laboratorio que relacionan "
            "humedad-succión (curva característica suelo-agua), permeabilidad-succión "
            "y resistencia al esfuerzo cortante-succión. Estas relaciones se pueden "
            "determinar en el laboratorio mediante mediciones directas. Las "
            "investigaciones actuales están encaminadas a encontrar métodos indirectos "
            "que permitan obtener la curva característica suelo-agua a partir de las "
            "propiedades básicas del suelo, como la relación de vacíos, saturación, "
            "gravedad específica, límite líquido, granulometría y densidad seca.\n\n"
            "Las formas de aproximarse al fenómeno de los suelos expansivos citadas en "
            "este Reglamento no son excluyentes, ni pretenden reemplazar otros métodos "
            "presentes o futuros; su uso a plena conciencia es respetado y alentado y "
            "está cubierto dentro de la responsabilidad propia del ejercicio de la "
            "ingeniería geotécnica."
        ),
    },
    {
        "id": "NSR10-H-H_9_1_6_medidas_preventivas",
        "seccion": "H.9.1.6 — Medidas preventivas para suelos expansivos",
        "titulo": "Título H, H.9.1.6: medidas preventivas (a-f) contra suelos expansivos: membranas impermeables, barreras de humedad, drenaje, sub-drenajes, alcantarillados, paisajismo.",
        "texto": (
            "H.9.1.6 — MEDIDAS PREVENTIVAS — Con el fin de alterar lo menos posible el "
            "equilibrio dinámico del subsuelo y reducir los potenciales cambios de "
            "humedad/succión, y por tanto las expansiones/contracciones del subsuelo "
            "las siguientes acciones preventivas son útiles:\n\n"
            "(a) Cubrir el terreno sobre el cual se proyectan las edificaciones con "
            "membranas impermeables que impidan la filtración de agua hacia el suelo "
            "expansivo.\n"
            "(b) Barreras de humedad — Colocadas perimetralmente a la estructura pueden "
            "coadyuvar al equilibrio; debe evitarse sin embargo, que se establezcan "
            "canales de humedecimiento como fenómenos termo-osmóticos que hagan inútil "
            "la precaución.\n"
            "(c) Drenaje de las aguas de escorrentía — Debe proveerse un adecuado "
            "drenaje alrededor de las estructuras por medio de pendientados "
            "perimetrales (2-10%), cunetas revestidas, áreas pavimentadas y "
            "canalizaciones de las aguas lluvias.\n"
            "(d) Sub-drenajes — para interceptar los flujos de aguas subterráneas, así "
            "como para disipar las presiones artesianas de los paleocauces "
            "existentes.\n"
            "(e) Alcantarillados y rellenos — Los alcantarillados en suelos "
            "expansivos, deben ser estancos; así mismo los rellenos deben hacerse con "
            "materiales inertes de baja permeabilidad y compactados según la "
            "especificación compatible.\n"
            "(f) Paisajismo e irrigación — Separar convenientemente las actividades de "
            "paisajismo, relacionadas con irrigación de plantas y jardines, de las "
            "estructuras adyacentes."
        ),
    },
    {
        "id": "NSR10-H-H_9_1_7_H_9_1_8",
        "seccion": "H.9.1.7 y H.9.1.8 — Alteración y elusión de suelos expansivos",
        "titulo": "Título H, H.9.1.7-H.9.1.8: alteración del suelo expansivo (reemplazo, tratamiento con cal, pre humedecimiento) y elusión (profundizar cimientos, pilotes pre excavados, placas aéreas).",
        "texto": (
            "H.9.1.7 — ALTERACIÓN DEL SUELO EXPANSIVO — Puede lograrse por cualquiera "
            "de los siguientes métodos:\n"
            "(a) Reemplazo — Consiste en la excavación y el reemplazo de la capa "
            "expansiva, cuando su espesor y profundidad no lo hacen prohibitivamente "
            "costoso.\n"
            "(b) Tratamiento con cal — La mezcla superficial de cal con el suelo "
            "potencialmente expansivo o su inyección a presión es benéfica, según el "
            "estado del suelo (agrietado o no) y el método de aplicación (inyección a "
            "presión o mezcla mecánica). Se debe disponer del equipo adecuado para "
            "pulverizar el suelo en el sitio del tratamiento, o para realizar "
            "inyecciones a presión.\n"
            "(c) Pre humedecimiento — El pre humedecimiento supone la expansión previa "
            "a la colocación de la estructura y el mantenimiento de esa humedad bajo "
            "una placa o un recubrimiento impermeable. Se debe tener presente que "
            "generalmente se requiere mucho tiempo para lograr que el agua penetre en "
            "la zona activa. Adicionalmente, la pérdida de capacidad de soporte "
            "dificulta las operaciones de construcción.\n\n"
            "H.9.1.8 — ELUSIÓN DE LOS SUELOS EXPANSIVOS — Se puede intentar por los "
            "siguientes procedimientos:\n"
            "(a) Profundizar los cimientos — Hasta pasar, al menos parcialmente, la "
            "profundidad de la zona crítica donde la expansión es más severa.\n"
            "(b) Pilotes pre excavados — A la profundidad necesaria para desarrollar "
            "la carga; puede completarse con el aislamiento del fuste del pilote en la "
            "zona activa. También puede considerarse el uso de micropilotes para "
            "reducir la fricción del fuste en la zona activa.\n"
            "(c) Placas aéreas — Para evitar el contacto de los pisos con el suelo "
            "potencialmente expansivo y mantener el gradiente térmico existente en el "
            "subsuelo."
        ),
    },
    {
        "id": "NSR10-H-H_9_1_9_mitigacion_estructural",
        "seccion": "H.9.1.9 — Mitigación de tipo estructural para suelos expansivos",
        "titulo": "Título H, H.9.1.9: mitigación estructural de suelos expansivos mediante cimentación rígida o construcción flexible.",
        "texto": (
            "H.9.1.9 — MITIGACIÓN DE TIPO ESTRUCTURAL — Este tipo de solución se logra "
            "por los siguientes caminos mutuamente excluyentes:\n\n"
            "(a) Cimentación rígida — Rigidización de los elementos de la cimentación "
            "de manera que la estructura se mueva como un todo. Está acompañada a "
            "menudo de concentración de la carga en ciertos puntos y liberación en "
            "otros, para permitir el alivio de las presiones de expansión bajo losas "
            "huecas, tipo artesonado. Los métodos convencionales de diseño de estas "
            "losas consideran las condiciones del clima, los parámetros del suelo "
            "(expansión, distancia de variación de la humedad, y rigidez), las "
            "condiciones de carga de la estructura, y las dimensiones y rigidez de la "
            "losa. También se han desarrollado modelos numéricos de interacción "
            "suelo-estructura. La estructura debe diseñarse en consecuencia.\n"
            "(b) Construcción flexible — Que permita el movimiento sin daño de "
            "ciertos elementos de la estructura. Los elementos no estructurales deben "
            "estar concebidos para acomodarse a estos ajustes."
        ),
    },
    {
        "id": "NSR10-H-H_9_2_suelos_dispersivos_erodables",
        "seccion": "H.9.2 — Suelos dispersivos o erodables (completo)",
        "titulo": "Título H, H.9.2 completo: suelos dispersivos y erodables, tipos, comportamiento, medidas preventivas y precaución.",
        "texto": (
            "H.9.2 — SUELOS DISPERSIVOS O ERODABLES\n\n"
            "H.9.2.1 — GENERALIDADES — Se identifican como suelos erodables, las "
            "arenas muy finas o los limos no cohesivos que exhiben una manifiesta "
            "vulnerabilidad ante la presencia de agua.\n\n"
            "H.9.2.2 — TIPOS DE SUELOS ERODABLES — Se distinguen dos tipos de suelos "
            "muy sensibles a la presencia de agua; éstos son:\n"
            "(a) Suelos dispersivos — Arcillas cuya concentración de sales de sodio "
            "(Na) en el agua intersticial pasa de 40% o 60% del total de sales "
            "disueltas.\n"
            "(b) Suelos erodables — Arenas finas, polvo de roca, limos no cohesivos y "
            "depósitos eólicos, propios de ambientes aluviales tranquilos y "
            "constantes que resultan en una granulometría relativamente homogénea.\n\n"
            "H.9.2.3 — CARACTERÍSTICAS DE SU COMPORTAMIENTO — Los suelos dispersivos "
            "entran de manera espontánea en solución en presencia de agua, primero "
            "como una nube de materia en suspensión, y luego como una extensión "
            "generalizada del fenómeno. Los suelos erodables, en cambio, no se "
            "disuelven pero sí son afectados por corrientes de agua de menor caudal, "
            "inclusive a bajos niveles del gradiente hidráulico, formando "
            "carcavamientos, tubificación y erosión retrogresiva o remontante.\n\n"
            "H.9.2.4 — MEDIDAS PREVENTIVAS — Las principales medidas preventivas cuyo "
            "análisis debe llevarse a cabo son:\n"
            "(a) Remoción del suelo erosionable — Cuando la operación es "
            "económicamente factible, y cuando se ha identificado con antelación la "
            "extensión y profundidad de la zona vulnerable.\n"
            "(b) Restricción severa del humedecimiento — Por medio de una combinación "
            "de drenajes, sub-drenajes, pavimentos impermeables y reglamentación del "
            "uso de agua.\n"
            "(c) Recubrimiento impermeable — Terraplén debidamente gradado, colocado "
            "sobre una capa doble de geotextil impermeable, debajo, y geotextil no "
            "tejido encima.\n"
            "(d) Recubrimiento vegetativo — Aplicable en las laderas de poca "
            "pendiente (< 20%), consiste en sembrar especies vegetales sobre "
            "geomalla, diseñada para el efecto, con restricciones laterales en "
            "maderas o cañas colocadas paralelamente a la curva de nivel, para evitar "
            "el transporte longitudinal del material a lo largo del plano de la "
            "pendiente.\n\n"
            "H.9.2.5 — PRECAUCIÓN — No deben utilizarse por ningún motivo materiales "
            "identificados como dispersivos o erodables, como materia prima para "
            "rellenos o terraplenes. Tampoco se deben utilizar materiales "
            "sospechosos de serlo, hasta tanto no se compruebe su naturaleza por "
            "medio de ensayos apropiados."
        ),
    },
    {
        "id": "NSR10-H-H_9_3_1_H_9_3_2",
        "seccion": "H.9.3.1 y H.9.3.2 — Suelos colapsables: generalidades y tipos",
        "titulo": "Título H, H.9.3.1-H.9.3.2: generalidades y 4 tipos de suelos colapsables (aluviales/coluviales, eólicos, cenizas volcánicas, residuales).",
        "texto": (
            "H.9.3 — SUELOS COLAPSABLES\n\n"
            "H.9.3.1 — GENERALIDADES — Se identifican como suelos colapsables aquellos "
            "depósitos formados por arenas y limos, en algunos casos cementados por "
            "arcillas y sales (carbonato de calcio), que si bien resisten cargas "
            "considerables en su estado seco, sufren pérdidas de su conformación "
            "estructural, acompañadas de severas reducciones en el volumen exterior "
            "cuando se aumenta o se satura.\n\n"
            "H.9.3.2 — TIPOS DE SUELOS COLAPSABLES — Se distinguen cuatro tipos "
            "principales de suelos colapsables, a saber:\n"
            "(a) Suelos aluviales y coluviales — Depositados en ambientes "
            "semi-desérticos por flujos más o menos torrenciales, tienen con "
            "frecuencia una estructura inestable (suelos metastables).\n"
            "(b) Suelos eólicos — Depositados por el viento, son arenas y limos "
            "arenosos con escaso cemento arcilloso en una estructura suelta o "
            "inestable. Reciben el nombre genérico de \"loess\" en las zonas "
            "templadas.\n"
            "(c) Cenizas volcánicas — Provenientes de cenizas arrojadas al aire por "
            "eventos recientes de actividad volcánica explosiva, conforman planicies "
            "de suelos limosos y limo-arcillosos con manifiesto carácter metastable.\n"
            "(d) Suelos residuales — Derivados de la descomposición in-situ de "
            "minerales de ciertas rocas, son luego lixiviados por el agua y pierden "
            "su cemento y su sustento por lo cual también terminan con una "
            "estructura inestable."
        ),
    },
    {
        "id": "NSR10-H-H_9_3_3_identificacion_colapsabilidad",
        "seccion": "H.9.3.3 — Identificación de colapsabilidad (ecuación H.9.3-1)",
        "titulo": "Título H, H.9.3.3: identificación de colapsabilidad mediante gamma_dcrit, ecuación H.9.3-1, y criterio de evaluación H.9.3.3.1.",
        "texto": (
            "H.9.3.3 — IDENTIFICACIÓN DE COLAPSABILIDAD — Se identifica la "
            "colapsabilidad de estos depósitos, cuando el volumen de vacíos el "
            "depósito es inestable. La evaluación se puede hacer mediante la "
            "siguiente formulación:\n\n"
            "gamma_dcrit = gamma_w / [(1/G_s) + w_l]   (H.9.3-1)\n\n"
            "H.9.3.3.1 — Criterio de evaluación — De esta manera, puede decirse que "
            "si:\n"
            "gamma_d / gamma_dcrit > 1, el suelo es estable o expansivo, y si\n"
            "gamma_d / gamma_dcrit <= 1, el suelo es colapsable"
        ),
    },
    {
        "id": "NSR10-H-H_9_3_4_clasificacion_grado_colapsibilidad",
        "seccion": "H.9.3.4 — Clasificación de grado de colapsibilidad (ecuaciones H.9.3-2/-3, Tabla H.9.3-1)",
        "titulo": "Título H, H.9.3.4: clasificación de grado de colapsibilidad mediante epsilon_w (deformación potencial de hidrocolapso), ecuaciones H.9.3-2/-3, y Tabla H.9.3-1 de severidad.",
        "texto": (
            "H.9.3.4 — CLASIFICACIÓN DE GRADO DE COLAPSIBILIDAD — Se define la "
            "deformación del hidrocolapso potencial como dependiente del coeficiente "
            "de hidroconsolidación y de la relación de esfuerzos entre el presente y "
            "el umbral de colapso, así:\n\n"
            "epsilon_w = c_w (log(sigma) - log(sigma_t)) = c_w log(sigma/sigma_t)   (H.9.3-2)\n\n"
            "donde:\n"
            "c_w = d(epsilon_w) / d(log sigma)   (H.9.3-3)\n\n"
            "De acuerdo con la anterior definición de términos, la clasificación se "
            "presenta en la tabla H.9.3-1.\n\n"
            "Tabla H.9.3-1 — Clasificación de colapsibilidad:\n"
            "Deformación potencial de hidrocolapso epsilon_w | Clasificación de "
            "severidad\n"
            "0 - 0.01 | sin problema\n"
            "0.01 - 0.05 | moderada\n"
            "0.05 - 0.10 | problema potencial\n"
            "0.10 - 0.20 | severa\n"
            "> 0.20 | muy severa"
        ),
    },
    {
        "id": "NSR10-H-H_9_3_5_asentamientos_colapso",
        "seccion": "H.9.3.5 — Cálculo de asentamientos por colapso (ecuación H.9.3-4)",
        "titulo": "Título H, H.9.3.5: cálculo de asentamientos por colapso mediante la ecuación H.9.3-4 (delta_w).",
        "texto": (
            "H.9.3.5 — CÁLCULO DE ASENTAMIENTOS POR COLAPSO — El cálculo de "
            "asentamientos por colapso de los suelos puede hacerse por medio de la "
            "siguiente formulación (Es posible utilizar otras expresiones de "
            "reconocida validez en la literatura):\n\n"
            "delta_w = suma[alfa * c_w * H_i * log(sigma_v / sigma_t)]   (H.9.3-4)\n\n"
            "donde alfa = (S - S_o) / (1 - S_o) equivale a una saturación relativa o a "
            "un coeficiente de humedecimiento.\n\n"
            "H.9.3.5.1 — Nótese que éste es un análisis por esfuerzos totales. "
            "Además, este asentamiento difiere del elástico o del de consolidación "
            "definidos en otros apartes de este Reglamento."
        ),
    },
    {
        "id": "NSR10-H-H_9_3_6_medidas_preventivas_colapso",
        "seccion": "H.9.3.6 — Medidas preventivas para suelos colapsables",
        "titulo": "Título H, H.9.3.6: medidas preventivas (a-i) contra suelos colapsables: remoción, restricción de humedecimiento, transferencia de cargas, inyección química, pre humedecimiento, compactación, vibroflotación, voladuras controladas, diseño tolerante.",
        "texto": (
            "H.9.3.6 — MEDIDAS PREVENTIVAS — Las principales medidas preventivas se "
            "enuncian enseguida:\n"
            "(a) Remoción del suelo colapsable — Cuando su profundidad y espesor lo "
            "hacen factible.\n"
            "(b) Restricción o minimización del humedecimiento — Por medio de "
            "drenaje, pavimentos impermeables y reglamentación del uso del agua.\n"
            "(c) Transferencia de las cargas a suelos inertes — Mediante "
            "cimentaciones profundas o semiprofundas, cuando la profundidad de estos "
            "suelos inertes es razonable. Debe tenerse en cuenta sobre los pilotes la "
            "posible fricción negativa originada en el fenómeno del colapso.\n"
            "(d) Estabilización por inyección de agentes químicos — Puede aplicarse "
            "localmente o en reparación de estructuras dañadas. Su costo lo hace "
            "prohibitivo en grandes extensiones.\n"
            "(e) Pre humedecimiento — Se recomienda el procedimiento en combinación "
            "con algún tipo de sobrecarga de manera que se logre el colapso "
            "anticipado del material defectuoso; es importante verificar el destino "
            "del agua agregada, porque es factible que a causa de la estratificación "
            "natural, su flujo se efectúe más horizontalmente que en forma vertical y "
            "no se logre el efecto esperado.\n"
            "(f) Compactación — Puede lograrse con cilindros o compactadores "
            "vibratorias convencionales, en combinación con humedecimiento moderado. "
            "También debe considerarse la factibilidad de instalar pilotes de "
            "desplazamiento por hincado, o pilotes de grava, hasta la profundidad "
            "requerida para pasar la capa potencialmente problemática. En algunos "
            "casos, a prudente distancia de estructuras existentes, debe "
            "considerarse la aplicación de la técnica de la compactación dinámica "
            "profunda, consistente en dejar caer un peso considerable, desde una "
            "cierta altura, repetitivamente sobre una serie de puntos distribuidos "
            "en un patrón predeterminado.\n"
            "(g) Vibroflotación — Esta técnica, consiste en la introducción dentro "
            "del suelo, mediante chorros de agua, de un cabezote vibratorio; ha "
            "demostrado su utilidad. Las perforaciones hechas con la herramienta "
            "citada, son luego rellenadas con gravas.\n"
            "(h) Voladuras controladas a profundidad — Esta técnica, aún en estado "
            "experimental consiste en detonar cargas explosivas a profundidad, con "
            "un cierto patrón de localización y en presencia de agua.\n"
            "(i) Diseño estructural tolerante — En los casos donde se demuestra que "
            "el asentamiento resultante del colapso no es inadmisible, debe "
            "diseñarse la estructura para resistir dicho movimiento sin distorsión "
            "ni daño aparente."
        ),
    },
    {
        "id": "NSR10-H-H_9_4_1_a_H_9_4_2_1",
        "seccion": "H.9.4.1 a H.9.4.2.1 — Efectos de la vegetación: definición del problema y de succión",
        "titulo": "Título H, H.9.4.1-H.9.4.2: definición del problema de la vegetación sobre el suelo, definición de succión (ecuaciones H.9.4-1/-2) y Tabla H.9.4-1 de equivalencias.",
        "texto": (
            "H.9.4 — EFECTOS DE LA VEGETACIÓN\n\n"
            "H.9.4.1 — DEFINICIÓN DEL PROBLEMA — Las raíces propias de la vegetación "
            "tienen la capacidad de extraer agua del suelo para garantizar su "
            "supervivencia. En consecuencia, la humedad natural del mismo suelo se "
            "altera en relación con el estado que tendría si no existieran tales "
            "raíces. Así, la alteración de la humedad causa, a su vez, cambios en el "
            "volumen del suelo en relación inversa con su permeabilidad, por lo cual "
            "son afectados mayormente los suelos de carácter arcilloso, y las "
            "cimentaciones situadas en la vecindad, o apoyadas sobre los suelos "
            "afectados, pueden sufrir movimientos verticales y, eventualmente, "
            "también horizontales. La sección H.9.4 se relaciona con los movimientos "
            "del suelo originados en la acción de la vegetación.\n\n"
            "H.9.4.2 — DEFINICIÓN DE SUCCIÓN — La presión del agua dentro del suelo "
            "puede expresarse como:\n\n"
            "u = alfa*p - s   (H.9.4-1)\n\n"
            "donde la fracción de presión total (alfa*p) es siempre positiva, y la "
            "succión (s) es siempre negativa. La succión puede expresarse en "
            "términos de la escala logarítmica pF como función de la altura negativa "
            "del agua en cm, así:\n\n"
            "pF = log10(h / gamma_w)   (H.9.4-2)\n\n"
            "H.9.4.2.1 — Equivalencias de la succión — La succión es una expresión de "
            "la presión de poros negativa. La equivalencia entre succión, altura de "
            "agua y presión se presenta en la Tabla H.9.4-1.\n\n"
            "Tabla H.9.4-1 — Equivalencias de la succión:\n"
            "pF | Altura de agua (cm) | Presión de poros negativa (kPa) | Presión de "
            "poros negativa (kgf/cm2)\n"
            "0 | 1 | - | -\n"
            "1 | 10 | 0.981 | 0.01\n"
            "2 | 10^2 | 9.81 | 0.1\n"
            "3 | 10^3 | 98.1 | 1\n"
            "4 | 10^4 | 981 | 10\n"
            "5 | 10^5 | 9810 | 100\n"
            "6 | 10^6 | 98100 | 1000\n"
            "7 | 10^7 | 981000 | 10000"
        ),
    },
    {
        "id": "NSR10-H-H_9_4_3_equilibrio_dinamico",
        "seccion": "H.9.4.3 — Equilibrio dinámico suelo-vegetación-clima",
        "titulo": "Título H, H.9.4.3: equilibrio dinámico entre suelo, vegetación y clima (Figura H.9.4-1, succión vs. profundidad).",
        "texto": (
            "H-9.4.3 — EQUILIBRIO DINÁMICO — Sin la intervención del hombre, la "
            "naturaleza establece un equilibrio dinámico entre el tipo de suelo, la "
            "vegetación y el clima. Cuando este equilibrio se altera se inducen "
            "cambios en el suelo que pueden acarrear asentamientos, expansiones o "
            "levantamientos, colapsos y otros cambios que es preciso controlar. "
            "(Véase la Figura H.9.4-1, que muestra la succión de equilibrio en "
            "función de la profundidad, con la profundidad de variación estacional "
            "hasta el nivel freático)."
        ),
    },
    {
        "id": "NSR10-H-H_9_4_4_caracteristicas_vegetacion",
        "seccion": "H.9.4.4 — Características de la vegetación (H.9.4.4.1 a H.9.4.4.5)",
        "titulo": "Título H, H.9.4.4: características de la vegetación — sistema radicular, profundidad de raíces (hasta 6 m), extensión, requerimientos de agua (Tabla H.9.4-2), punto de marchitamiento.",
        "texto": (
            "H.9.4.4 — CARACTERÍSTICAS DE LA VEGETACIÓN\n\n"
            "H.9.4.4.1 — Sistema radicular — El árbol, dependiendo de su especie "
            "particular, extiende una red de raíces primarias y secundarias hasta de "
            "cuarto orden, compuestas por raíces leñosas y no leñosas. El sistema de "
            "raíces es el encargado de tomar el agua del suelo, junto con los "
            "nutrientes, agua que se transpira a través de los estomas colocados "
            "principalmente en el anverso de las hojas.\n\n"
            "H.9.4.4.2 — Profundidad de las raíces — La profundidad de las raíces "
            "depende de la especie de que se trate, del tamaño del árbol y de la "
            "profundidad del nivel freático. Para crecer las raíces necesitan aire, "
            "por lo cual su existencia está limitada por la posición del nivel "
            "freático; generalmente se observa que las raíces se desarrollan en el "
            "espacio medio entre la superficie y el nivel del agua y por lo regular "
            "a no más de 6.0 m. En casos de presencia de agua, las raíces abundan en "
            "superficie; en caso de escasez, ganan profundidad para recoger el agua "
            "disponible en los estratos más bajos. El crecimiento de las raíces puede "
            "llegar a 20 mm por día en búsqueda de agua y nutrientes.\n\n"
            "H.9.4.4.3 — Extensión del sistema radicular — El sistema de raíces se "
            "extiende lateralmente para reproducir la sombra del follaje, y a "
            "profundidad dependiendo de la especie y de las demás condiciones dadas. "
            "Según un criterio, las raíces se extienden hasta una y media veces la "
            "altura del árbol; según otro criterio, hasta una y media veces el radio "
            "de su follaje.\n\n"
            "H.9.4.4.4 — Requerimientos de agua — El requerimiento de agua depende "
            "del tamaño del árbol y de las variables del clima (temperatura, "
            "insolación y viento). Para un árbol adulto este requerimiento ha sido "
            "tasado en cientos de litros de agua por día. En la Tabla H.9.4-2 se "
            "presentan algunos valores típicos.\n\n"
            "Tabla H.9.4-2 — Requerimientos de agua:\n"
            "Especie | Transpiración día soleado\n"
            "Eucalyptus Macarthuri | 500 l/día\n"
            "Acacia Mollissima | 250 l/día\n"
            "Pasto (Themeda) | 1 l/día/m2\n\n"
            "H.9.4.4.5 — Punto de marchitamiento — La cavitación del agua con "
            "oxígeno disuelto ocurre aproximadamente a una atmósfera de tensión. "
            "Esto, no obstante, el sistema de succión de las plantas está asegurado "
            "contra la cavitación, y las presiones de succión son más elevadas. En "
            "efecto, se define el punto de marchitamiento como la máxima succión "
            "aplicada por una planta para extraer el agua del suelo. Este punto "
            "equivale a una presión métrica de succión igual a pF = 4.2, que es "
            "superior a 10^3 kPa."
        ),
    },
    {
        "id": "NSR10-H-H_9_4_5_relacion_con_suelos",
        "seccion": "H.9.4.5 — Relación de la vegetación con los suelos (ecuación H.9.4-3, Figura H.9.4-3)",
        "titulo": "Título H, H.9.4.5: relación con los suelos — humedad de equilibrio, ecuación H.9.4-3 (B=0.5 para pF=2, B=0.4 para pF=3), límites de consistencia, movimiento de suelos.",
        "texto": (
            "H.9.4.5 — RELACIÓN CON LOS SUELOS\n\n"
            "H.9.4.5.1 — Humedad de equilibrio — Se define, en este contexto, como "
            "la humedad de equilibrio aquella que adopta el suelo como respuesta a "
            "una succión determinada.\n\n"
            "H.9.4.5.2 — Tipo de suelos — La humedad de equilibrio depende del tipo "
            "de suelo expresado en términos del límite líquido. Se calcula así:\n\n"
            "w_eq = B * LL   (H.9.4-3)\n\n"
            "Para diferentes succiones, B adopta diferentes valores, en concordancia "
            "con lo expresado en la ecuación H.9.4-1 (véase la figura H.9.4-3), así:\n"
            "Para pF = 2, entonces B = 0.5\n"
            "y para pF = 3, entonces B = 0.4\n\n"
            "H.9.4.5.3 — Límites de consistencia — La succión se relaciona con los "
            "límites de consistencia de un suelo determinado y varía según el tipo "
            "de tal suelo. En general, el límite plástico corresponde a succiones pF "
            "entre 4 y 5; y el límite de contracción a succiones pF entre 5 y 6. "
            "Nótese que la succión correspondiente al límite de marchitamiento es "
            "menor que la del límite de contracción de la mayoría de los suelos "
            "(Véase la figura H.9.4-3).\n\n"
            "H.9.4.5.4 — Movimiento de los suelos — Como consecuencia del equilibrio "
            "dinámico entre la vegetación, los suelos y el clima, se desatan "
            "fenómenos de contracción y expansión que es preciso calcular según los "
            "procedimientos dados en este Reglamento.\n\n"
            "H.9.4.5.4.1 — Límites Prácticos — Se ha establecido que para succiones "
            "pF superiores a 3.0 se desencadena un proceso de desecación; por el "
            "contrario para succiones pF inferiores a 3.0 se desencadena uno de "
            "expansión en suelos con el potencial correlativo."
        ),
    },
    {
        "id": "NSR10-H-H_9_4_6_relacion_con_edificaciones",
        "seccion": "H.9.4.6 — Relación de la vegetación con las edificaciones (acción y medidas preventivas)",
        "titulo": "Título H, H.9.4.6: relación con edificaciones — asentamientos/levantamientos por vegetación, control de especies agresivas (urapán, eucalipto, sauce, pino, acacia, cerezo), poda, corte de raíces.",
        "texto": (
            "H.9.4.6 — RELACIÓN CON LAS EDIFICACIONES — Deben considerarse los "
            "siguientes aspectos:\n\n"
            "H.9.4.6.1 — Acción de la vegetación —\n"
            "(a) Asentamientos — Producidos por los árboles individualmente o en "
            "conjunto, cuando son sembrados en las cercanías de edificaciones y el "
            "suministro de agua es deficiente ya sea por el clima o por reducción "
            "excesiva del área descubierta expuesta a la lluvia.\n"
            "(b) Levantamientos — Producidos cuando un sistema de suelo-vegetación, "
            "previamente equilibrado, es súbitamente desprovisto de su cobertura "
            "vegetal; al cesar la succión, aumenta la humedad hasta aproximarse a su "
            "nuevo punto de equilibrio con la consiguiente expansión.\n"
            "(c) Especies agresivas — Especies particularmente agresivas buscan el "
            "agua bajo la cubierta propicia de la edificación y en algunos casos "
            "invaden con sus raíces las tuberías de los alcantarillados.\n"
            "(d) Cambios estacionales — Los cambios estacionales del clima, y aún "
            "alteraciones más substanciales como el Fenómeno del Niño, producen un "
            "desequilibrio puntual del sistema.\n\n"
            "H.9.4.6.2 — Medidas preventivas — Las medidas preventivas tienen que "
            "ver con la siembra de plantas ornamentales en nuevos proyectos y con el "
            "tratamiento de las especies ya sembradas. Estas son:\n"
            "(a) Control de especies agresivas — Se consideran especies agresivas, "
            "aquellas originarias del extranjero, de zonas con climas "
            "particularmente severos. Se enuncian para estos efectos: Urapán "
            "(Fraxinus chinensis); Eucalipto (Eucalyptus mobulus, viminalis y "
            "camaldulensis); Sauce (Salix humboltiana); Pino (Pinus patula, "
            "radiata, taedo); Acacia (Acacia melanoxylon); Cerezo (Pronus "
            "serotina).\n"
            "(b) Substitución selectiva de árboles dañinos — Ciertos árboles "
            "manifiestamente dañinos por su acción deletérea sobre edificaciones, "
            "pavimentos, juegos deportivos, zonas de esparcimiento deben ser "
            "substituidos.\n"
            "(c) Poda continuada — La poda continuada, bajo dirección de manos "
            "expertas, contribuye a mantener el follaje en un tamaño adecuado a su "
            "función y al espacio disponible.\n"
            "(d) Corte moderado de raíces — Se recomienda esta práctica en relación "
            "con las raíces invasoras que penetran bajo los pavimentos, en los muros "
            "o en las tuberías del alcantarillado.\n"
            "(e) Suministro ponderado de agua — El suministro de agua, sobre todo en "
            "la estación seca, es una medida sana cuando se cuenta con el líquido y "
            "se trata de especies que se quiere conservar.\n"
            "(f) Selección de especies — En ausencia de disposiciones distritales o "
            "municipales, respecto a las especies adecuadas al clima y al tipo de "
            "suelos de la localidad, se deben evitar aquellas especies sobre las que "
            "se tenga evidencia acerca de su comportamiento nocivo."
        ),
    },
    {
        "id": "NSR10-H-H_9_4_7_vegetacion_laderas",
        "seccion": "H.9.4.7 — Relación de la vegetación con las laderas",
        "titulo": "Título H, H.9.4.7: efectos benéficos de la vegetación en laderas — reducción de erosión, refuerzo del suelo por raíces, reducción de presiones de poros.",
        "texto": (
            "H.9.4.7 — RELACIÓN DE LA VEGETACIÓN CON LAS LADERAS — Mientras las "
            "especies mencionadas en H.9.4.6.2a) pueden ser nocivas para las "
            "edificaciones, en las laderas el efecto es contrario y pueden ser muy "
            "benéficas, pues:\n"
            "(a) Con la interceptación de la lluvia con el follaje reducen la "
            "energía de las gotas y regulan la escorrentía reduciendo la erosión en "
            "la ladera.\n"
            "(b) El sistema radicular provee refuerzo al suelo, minimizando la "
            "posibilidad de deslizamientos someros.\n"
            "(c) La extracción del agua subterránea reduce las presiones de poros "
            "incrementando la estabilidad de la ladera."
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
    print(f"Codificando {len(textos)} chunks-padre de H.9...")
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

    print(f"Subiendo {len(rows)} chunks-padre de H.9 a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_h_h9_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
