"""
Ingesta verbatim de Título H, Capítulo H.10 (Rehabilitación sísmica de
edificios: amenazas de origen sismo-geotécnico y reforzamiento de
cimentaciones) -- NSR-10. **Cierra el Título H completo (H.1-H.10).**

Fuente: NSR-10-1451-1500.pdf, páginas PDF 48-50 (H-59 a H-61) +
NSR-10-1501-1570.pdf, páginas PDF 1-5 (H-62 a H-65), leídas visualmente
con Read pages= sobre el PDF nativo. Continuidad exacta confirmada
entre ambos archivos (H-61 termina "H.10.3 — MITIGACIÓN..." arrancando,
H-62 continúa "H.10.3.1 — MITIGACIÓN PARA RUPTURA..."). El capítulo
termina en H-65 (marca "■" de fin de título) y H-66 es una página en
blanco "Notas"; el Título I (Supervisión Técnica) arranca limpio en
I-1, página PDF 6 del segundo archivo.

Mismo patrón de 2 scripts ya establecido (H.3.3+H.4, H.5, H.6, H.7,
H.8, H.9): este script sube los chunks-padre (grandes); el script
_resplit_titulo_h_h10_por_limite_tokens.py los re-trochea con
verificación real de tokens antes de dejarlos en producción.

Uso: python _ingest_titulo_h_h10_verbatim.py
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
        "id": "NSR10-H-H_10_1_alcance",
        "seccion": "H.10.1 — Alcance del capítulo de rehabilitación sísmica",
        "titulo": "Título H, H.10.1: alcance del capítulo de rehabilitación de cimentaciones ante amenazas sismo-geotécnicas (licuación, deslizamientos, caída de rocas, avalanchas).",
        "texto": (
            "CAPÍTULO H.10 — REHABILITACIÓN SÍSMICA DE EDIFICIOS: AMENAZAS DE ORIGEN "
            "SISMO GEOTÉCNICO Y REFORZAMIENTO DE CIMENTACIONES\n\n"
            "H.10.1 — ALCANCE — En este capítulo se presentan las medidas para la "
            "rehabilitación de cimentaciones de edificios para acondicionarlas para "
            "que puedan hacer frente a las amenazas potenciales de origen "
            "sismo-geotécnico, tales como licuación, compactación diferencial, "
            "deslizamientos, caída de rocas y avalanchas, así como los requisitos "
            "geotécnicos mínimos respecto a sus cimentaciones (artículo 10.2) y "
            "pueden hacerse sólo a las cimentaciones o en conjunto con la "
            "rehabilitación sísmica de la edificación. Las técnicas para mitigar "
            "dichas amenazas se describen en el artículo H.10.3.\n\n"
            "La aceptabilidad del comportamiento de los sistemas y suelos de "
            "cimentación no se puede determinar independientemente del contexto del "
            "comportamiento de la superestructura. En el artículo H.10.4 se presentan "
            "los criterios para determinar la capacidad portante por resistencia del "
            "suelo, rigidez y parámetros de interacción suelo-estructura requeridos "
            "para hacer las evaluaciones del diseño de cimentaciones. El artículo "
            "H.10.5 contiene una guía para mejorar o reforzar cimentaciones."
        ),
    },
    {
        "id": "NSR10-H-H_10_2_1_caracterizacion_sitio",
        "seccion": "H.10.2 y H.10.2.1 — Caracterización del sitio e información del suelo de cimentación",
        "titulo": "Título H, H.10.2-H.10.2.1: caracterización geotécnica del sitio y datos del suelo de cimentación requeridos para rehabilitación sísmica (tipo de cimentación, dimensiones, cargas de diseño).",
        "texto": (
            "H.10.2 — CARACTERIZACIÓN DEL SITIO — Se requiere que la caracterización "
            "geotécnica del sitio sea consistente con el método seleccionado de "
            "rehabilitación sísmica. Consiste en recopilar la información de las "
            "condiciones del subsuelo del sitio, la configuración y cargas de la "
            "cimentación del edificio existente, y las amenazas potenciales "
            "sismo-geotécnicas del sitio.\n\n"
            "H.10.2.1 — INFORMACIÓN DEL SUELO DE CIMENTACIÓN — Se requiere información "
            "específica que describa las condiciones de cimentación del edificio que "
            "va ha ser rehabilitado. Información útil también se puede obtener del "
            "conocimiento de las cimentaciones de edificios adyacentes o cercanos. La "
            "información de la cimentación debe incluir datos del subsuelo y nivel "
            "freático, configuración del sistema de cimentación, cargas de diseño de "
            "los cimientos, y características de la relación carga-deformación.\n\n"
            "H.10.2.1.1 — Condiciones del sitio de cimentación — Las condiciones del "
            "subsuelo deben ser definidas con suficiente detalle para evaluar la "
            "capacidad última de la cimentación y determinar si el sitio es "
            "susceptible a amenazas sismo-geotécnicas.\n\n"
            "Se requiere información acerca del tipo de cimentación, dimensiones y "
            "materiales. Esta información incluye:\n"
            "(a) Tipo de cimentación: zapatas, losas, pilotes, pilas.\n"
            "(b) Dimensiones de cimientos: localización y dimensiones en planta; "
            "para pilotes, elevación de la punta, variaciones verticales (secciones "
            "de pilotes ahusados o campanas de pilas).\n"
            "(c) Materiales y construcción: para pilotes, tipo (concreto/acero/"
            "madera) y métodos de instalación (vaciados en sitio, hincados).\n\n"
            "Se debe determinar el tipo, composición, consistencia, densidad "
            "relativa, y estratos de suelos hasta una profundidad a la cual el "
            "esfuerzo transmitido por la edificación sea aproximadamente el 10% del "
            "peso total del edificio dividido por el área total de la cimentación "
            "(véase artículo H.3.2.5). Se deberá también determinar la localización "
            "del nivel freático y sus fluctuaciones estacionales bajo el edificio. "
            "Para cada tipo de suelo, se debe obtener el peso unitario gamma, la "
            "resistencia al corte (la cohesión efectiva c', el ángulo de fricción "
            "interna efectivo phi' y/o la resistencia no drenada S_u), las "
            "características de compresibilidad, el módulo de cortante G, y la "
            "relación de Poisson mu.\n\n"
            "H.10.2.1.2 — Condiciones de cimentaciones próximas — Información "
            "específica de las cimentaciones de la propia edificación, de adyacentes "
            "o cercanos puede ser útil si el subsuelo y las condiciones del agua "
            "subterránea son de baja variabilidad. Sitios adyacentes en los cuales se "
            "haya construido recientemente pueden ser una guía para la evaluación de "
            "las condiciones del sitio de la estructura a rehabilitar.\n\n"
            "H.10.2.1.3 — Cargas de diseño de los cimientos — Se requiere la "
            "información de las cargas de diseño de los cimientos, así como las "
            "cargas muertas actuales y los estimativos de cargas vivas normales y "
            "máximas.\n\n"
            "H.10.2.1.4 — Características carga-deformación bajo carga sísmica — "
            "Tradicionalmente los ingenieros geotecnistas tratan las características "
            "carga-deformación a largo plazo únicamente de las cargas muertas más "
            "las cargas vivas normales. En la mayoría de los casos, los asentamientos "
            "a largo plazo gobiernan el diseño de cimientos. Las características "
            "carga-deformación a corto plazo (sismo) no han sido usadas "
            "tradicionalmente para diseño; consecuentemente, tales relaciones "
            "generalmente no se encuentran en los informes de suelos y cimentaciones "
            "de edificios existentes. En el artículo H.10.4 se discute en detalle "
            "estas relaciones."
        ),
    },
    {
        "id": "NSR10-H-H_10_2_2_amenazas_sismicas_sitio",
        "seccion": "H.10.2.2 — Amenazas sísmicas del sitio (ruptura de falla, licuación, compactación diferencial, deslizamientos, avalancha/inundación)",
        "titulo": "Título H, H.10.2.2: identificación de amenazas sísmicas del sitio — ruptura de falla activa, licuación (criterios a-e), compactación diferencial, deslizamientos (taludes >18°), avalancha/inundación.",
        "texto": (
            "H.10.2.2 — AMENAZAS SÍSMICAS DEL SITIO — En adición a las vibraciones "
            "del terreno, las amenazas sísmicas incluyen ruptura de fallas "
            "superficiales, licuación, compactación diferencial, deslizamientos y "
            "avalanchas. El potencial de amenazas por desplazamiento del terreno en "
            "un sitio debe evaluarse. La evaluación debe incluir un estimativo de las "
            "amenazas en términos del movimiento del terreno. Si las amenazas no son "
            "aceptables, entonces deben ser mitigadas como se describe en el "
            "artículo H.10.3.\n\n"
            "H-10.2.2.1 — Ruptura de una falla — Las condiciones geológicas del sitio "
            "se deben describir con suficiente detalle para evaluar la presencia de "
            "una traza de fallas tectónicas en los suelos de cimentación del "
            "edificio. Si se conoce o se sospecha que la traza de falla está "
            "presente, se requiere información referente a la actividad, tipo de "
            "falla, sentido del desplazamiento con respecto a la geometría del "
            "edificio, estimación de valores de los desplazamientos vertical y/o "
            "horizontal con intervalos de recurrencia, y ancho de la zona de "
            "ruptura potencial.\n\n"
            "H.10.2.2.2 — Licuación — Las condiciones del subsuelo y del agua "
            "subterránea se deben describir con suficiente detalle para evaluar la "
            "presencia de materiales potencialmente licuables en los suelos de "
            "cimentación del edificio. Si se sospecha de la presencia de suelos "
            "licuables se requiere información del tipo de suelo, densidad, "
            "profundidad del nivel freático y fluctuaciones estacionales, pendiente "
            "del terreno, proximidad a la cara libre de un accidente topográfico "
            "(río, canal, lago, etc.), y evaluación de los desplazamientos o "
            "corrimientos laterales y verticales.\n\n"
            "La amenaza de licuación se debe evaluar inicialmente para establecer si "
            "el sitio es claramente libre de esta amenaza, o si por el contrario se "
            "debe realizar una investigación detallada. Generalmente se puede "
            "suponer que la amenaza de licuación no existe en los sitios en donde, "
            "con suelos similares, no ha ocurrido históricamente la licuación, y si "
            "se cumple algunos de los siguientes criterios:\n"
            "(a) Los materiales del subsuelo son roca o tienen muy baja "
            "susceptibilidad a la licuación, basado en el ambiente general de "
            "deposición y edad geológica del depósito.\n"
            "(b) El subsuelo está constituido de arcillas duras o limos arcillosos, "
            "a menos que sean altamente sensitivos basado en experiencia local.\n"
            "(c) Los suelos no cohesivos (arenas, limos, o gravas) tienen una "
            "mínima resistencia normalizada en el Ensayo de Penetración Estándar "
            "(SPT), N160, de 30 golpes/pie para profundidades bajo la tabla de "
            "agua, o con un contenido de arcilla mayor de 20%. El parámetro N160 se "
            "define como el valor de N del SPT normalizado a una sobre presión "
            "efectiva de 100 kPa (presión atmosférica =PA). Se considera arcilla al "
            "suelo cuyas partículas son de diámetro nominal ≤ 0.002 mm.\n"
            "(d) El nivel freático está por lo menos a 10 m bajo el cimiento más "
            "profundo, o 15 m bajo la superficie del terreno, incluyendo "
            "consideraciones para ascensos estacionales e históricos, y si algún "
            "talud o condición de borde libre en la vecindad no se extiende bajo la "
            "elevación del agua subterránea en el sitio.\n"
            "(e) Si aplicando los criterios mencionados existe alguna posibilidad de "
            "amenaza por licuación, entonces se requiere una evaluación detallada del "
            "potencial de licuación (véase el artículo H.7.4.5).\n\n"
            "H.10.2.2.3 — Compactación diferencial — Las condiciones del subsuelo se "
            "deben definir con suficiente detalle para que se pueda evaluar el "
            "potencial de compactación o densificación diferencial de los suelos "
            "durante una fuerte vibración del terreno. Los asentamientos "
            "diferenciales resultantes pueden ocasionar daño a las estructuras.\n\n"
            "Los tipos de suelos que son susceptibles a licuación (suelos naturales "
            "relativamente sueltos, o rellenos de suelos no compactados o "
            "pobremente compactados) también son susceptibles a compactación. La "
            "compactación puede ocurrir en los suelos por encima y bajo el nivel "
            "freático.\n\n"
            "Se puede suponer que no existe amenaza debido a compactación "
            "diferencial si las condiciones del suelo cumplen simultáneamente los "
            "siguientes criterios:\n"
            "(a) Los materiales geológicos bajo los cimientos y bajo el nivel "
            "freático no poseen una significante amenaza por licuación, basado en "
            "los criterios del artículo H.10.2.2.2.\n"
            "(b) Los materiales geológicos bajo los cimientos y encima del nivel "
            "freático son o del Pleistoceno en edad geológica (más antiguo de "
            "11,000 años), arcillas duras o limos arcillosos, o arenas no "
            "cohesivas, limos, y gravas con un mínimo N160 de 20 golpes/pie.\n"
            "(c) Si aplicando los criterios mencionados existe alguna posibilidad "
            "de amenaza por compactación diferencial, se requiere una evaluación "
            "más detallada de esta amenaza.\n\n"
            "H.10.2.2.4 — Deslizamientos — La efectividad de mitigar la amenaza por "
            "deslizamientos debe ser evaluada por el ingeniero estructural en el "
            "contexto del comportamiento global del sistema del edificio. La "
            "estabilidad de laderas se debe evaluar en los sitios cuando existe:\n"
            "(a) Taludes cuya pendiente excede de aproximadamente 18 grados (3 "
            "horizontal: 1 vertical).\n"
            "(b) Historia de inestabilidad (rotacional, traslacional, o caída de "
            "rocas).\n\n"
            "Para determinar la estabilidad del sitio véase el artículo H.6.2.\n\n"
            "El análisis de desplazamientos de la ladera deberá determinar la "
            "magnitud del movimiento potencial del terreno, el cual deberá usar el "
            "ingeniero estructural en la determinación del efecto sobre el "
            "comportamiento de la estructura. Si la estructura no se puede acomodar "
            "a los desplazamientos calculados para el terreno, deberán emplearse "
            "esquemas apropiados de mitigación como se describen en el artículo "
            "H.10.3.4.\n\n"
            "Adicionalmente a los efectos potenciales de deslizamientos sobre los "
            "suelos de cimentación, deberá considerarse los posibles efectos de "
            "caída de rocas o flujo de escombros de taludes adyacentes a la "
            "edificación.\n\n"
            "H.10.2.2.5 — Avalancha o inundación — Las condiciones del subsuelo se "
            "deben definir con suficiente detalle para que se pueda evaluar el "
            "potencial de avalancha o inundación inducida por el sismo. Las fuentes "
            "para esta amenaza incluyen:\n"
            "(a) Presas, acueductos, tanques de almacenamiento de agua y tuberías "
            "que puedan afectar el edificio por daños ocasionados por el sismo: "
            "deslizamientos, vibración fuerte o ruptura de falla activa.\n"
            "(b) Áreas o zonas costeras susceptibles a tsunamis, o áreas adyacentes "
            "a bahías o lagos que pueden estar sujetas a fenómenos de fuerte "
            "oleaje.\n"
            "(c) Áreas bajas con niveles freáticos superficiales donde la "
            "subsidencia regional podría ocasionar inundación del sitio.\n\n"
            "Se deben tomar las medidas necesarias para evitar que se produzca "
            "socavación de los suelos de cimentación del edificio por esta amenaza."
        ),
    },
    {
        "id": "NSR10-H-H_10_3_mitigacion_amenazas_sismicas",
        "seccion": "H.10.3 — Mitigación de las amenazas sísmicas del sitio (falla activa, licuación, compactación diferencial, deslizamientos, avalancha/inundación)",
        "titulo": "Título H, H.10.3: técnicas de mitigación de amenazas sismo-geotécnicas del sitio — ruptura de falla activa, licuación (modificar estructura/cimentación/suelo), compactación diferencial, deslizamientos (re-conformación, drenaje, muros), avalancha o inundación.",
        "texto": (
            "H.10.3 — MITIGACIÓN DE LAS AMENAZAS SÍSMICAS DEL SITIO — Existen "
            "metodologías para mejorar el comportamiento sísmico bajo la influencia "
            "de algunas amenazas, a costo razonable; sin embargo, algunas amenazas "
            "pueden ser tan severas que son económicamente inviables para tomar "
            "medidas de reducción del riesgo. La siguiente discusión está basada en "
            "el concepto de que las amenazas del sitio se determinan después de "
            "haber decidido la rehabilitación sísmica del edificio. Sin embargo, la "
            "decisión de rehabilitar un edificio y la selección del objetivo de la "
            "rehabilitación se pueden haber hecho con el conocimiento pleno que "
            "existen significativas amenazas del sitio y que deben ser mitigadas "
            "como parte de la rehabilitación.\n\n"
            "H.10.3.1 — MITIGACIÓN PARA RUPTURA DE FALLA ACTIVA — Grandes "
            "movimientos de la ruptura de una falla activa generalmente no pueden "
            "ser mitigados económicamente. Si las consecuencias estructurales de los "
            "desplazamientos horizontales y verticales estimados no son aceptables, "
            "la estructura, su cimentación, o ambos, podrían ser rigidizados o "
            "aumentada su resistencia para lograr un comportamiento aceptable. Las "
            "medidas son altamente dependientes de las características "
            "estructurales específicas. Vigas y losas reforzadas de cimentación son "
            "efectivas en incrementar la resistencia a desplazamientos "
            "horizontales.\n\n"
            "Las fuerzas horizontales son algunas veces limitadas por la capacidad "
            "de fricción de zapatas y losas al deslizamiento mientras que los "
            "desplazamientos verticales pueden ser similares en naturaleza a los "
            "ocasionados por asentamientos diferenciales a largo plazo.\n\n"
            "Técnicas de mitigación incluyen modificaciones de la estructura o su "
            "cimentación para distribuir los efectos de los movimientos verticales "
            "diferenciales sobre una mayor distancia horizontal, para reducir la "
            "distorsión angular.\n\n"
            "H.10.3.2 — LICUACIÓN — La efectividad de las medidas para mitigar la "
            "amenaza de licuación debe ser evaluada por el ingeniero estructural en "
            "el contexto del comportamiento global del sistema del edificio. Si se "
            "ha determinado que la licuación es de probable ocurrencia, y las "
            "consecuencias en términos de desplazamientos horizontales y verticales "
            "no son aceptables, entonces tres tipos generales de medidas de "
            "mitigación deberán considerarse, individuales o en combinación:\n"
            "(a) Modificar la estructura — a la estructura se le puede mejorar su "
            "resistencia contra las deformaciones del terreno que se predice "
            "ocasionará la licuación. Esta solución es viable para pequeñas "
            "deformaciones del terreno.\n"
            "(b) Modificar la cimentación — el sistema de cimentación se puede "
            "modificar para reducir o eliminar el potencial de grandes "
            "desplazamientos de los cimientos; por ejemplo, sub-murando los "
            "cimientos superficiales existentes hasta un estrato no licuable más "
            "profundo. Alternativamente (o mediante el uso de cimientos "
            "profundos), un sistema de cimientos superficiales se puede hacer más "
            "rígido (por ejemplo, con un sistema de vigas entre zapatas "
            "individuales) con el fin de reducir los movimientos diferenciales del "
            "terreno transmitidos a la estructura.\n"
            "(c) Modificar las condiciones del suelo — un número de medidas para "
            "mejorar el terreno se pueden considerar para reducir o eliminar el "
            "potencial de licuación y sus efectos (véase el artículo H.7.4.6 para "
            "mitigar el potencial de licuación en proyectos de edificaciones "
            "nuevas). Algunas de estas medidas no son aplicables bajo un edificio "
            "existente por los efectos del procedimiento sobre el edificio. Si la "
            "licuación ocasiona corrimientos laterales en el sitio del edificio, "
            "entonces mitigar la amenaza de licuación es más difícil, ya que los "
            "movimientos bajo el edificio pueden depender del comportamiento de la "
            "masa de suelo a distancias más allá del edificio, así como "
            "inmediatamente debajo de él. Entonces las medidas para prevenir "
            "corrimientos laterales pueden, en algunos casos, requerir la "
            "estabilización de grandes volúmenes de suelo y/o la construcción de "
            "estructuras de contención que puedan reducir el potencial para, o la "
            "cantidad de, movimientos laterales.\n\n"
            "H.10.3.3 — MITIGACIÓN PARA COMPACTACIÓN DIFERENCIAL — La efectividad "
            "de las medidas para mitigar la amenaza de compactación diferencial "
            "debe ser evaluada por el ingeniero estructural en el contexto del "
            "comportamiento global del sistema del edificio.\n\n"
            "Para los casos en los cuales se predice asentamientos diferenciales "
            "significantes de la cimentación del edificio, las opciones de "
            "mitigación son similares a las descritas para mitigar la amenaza de "
            "licuación: mejorar la resistencia de la estructura para los "
            "movimientos del terreno, aumentar la resistencia del sistema de "
            "cimentación, y mejorar las condiciones del suelo.\n\n"
            "H.10.3.4 — DESLIZAMIENTOS — La efectividad de mitigar la amenaza por "
            "deslizamientos debe ser evaluada por el ingeniero estructural en el "
            "contexto del comportamiento global del sistema del edificio. Un "
            "número de esquemas son disponibles para reducir el potencial impacto "
            "de deslizamientos inducidos por sismo, incluyendo:\n"
            "(a) Re-conformación topográfica\n"
            "(b) Drenaje\n"
            "(c) Defensas\n"
            "(d) Mejoramiento estructural\n"
            "   - Muros de gravedad\n"
            "   - Muros anclados/pernados (\"soil nailing\")\n"
            "   - Muros de tierra mecánicamente estabilizada\n"
            "   - Barreras para flujos de escombros o caída de rocas\n"
            "   - Reforzamiento del edificio para resistir la deformación\n"
            "   - Vigas de equilibrio en la cimentación\n"
            "   - Muros o pantallas de cortante\n"
            "(e) Modificación del suelo/reemplazo\n"
            "   - Inyecciones\n"
            "   - Densificación\n\n"
            "La efectividad de algunos de estos esquemas se debe considerar con "
            "base en la cantidad del movimiento del terreno que el edificio puede "
            "tolerar.\n\n"
            "H.10.3.5 — AVALANCHA O INUNDACIÓN — La efectividad de mitigar la "
            "amenaza por avalancha o inundación debe ser evaluada por el ingeniero "
            "estructural en el contexto del comportamiento global del sistema del "
            "edificio. El daño potencial causado por avalancha o inundación "
            "inducida por sismo puede ser mitigado por los siguientes esquemas:\n"
            "(a) Mejoramiento o rehabilitación de la obra cercana, (presas, "
            "tuberías o instalaciones de acueductos independientes del edificio "
            "rehabilitado).\n"
            "(b) Obras de desvío del flujo que se estima inundará el edificio.\n"
            "(c) Pavimentos alrededor del edificio para minimizar la erosión en "
            "los cimientos.\n"
            "(d) Construcción de muro o rompeolas para protección de tsunami."
        ),
    },
    {
        "id": "NSR10-H-H_10_4_reforzamiento_rigidez_cimentacion",
        "seccion": "H.10.4 — Reforzamiento y rigidez de la cimentación (capacidades últimas, carga-deformación, criterio de aceptabilidad)",
        "titulo": "Título H, H.10.4: reforzamiento y rigidez de la cimentación — capacidades últimas de carga (H.4), características carga-deformación, criterio de aceptabilidad lineal (base fija/flexible) y no lineal.",
        "texto": (
            "H.10.4 — REFORZAMIENTO Y RIGIDEZ DE LA CIMENTACIÓN — En este artículo "
            "se supone que los suelos no son susceptibles a pérdida significativa de "
            "resistencia debido a la carga sísmica. Con esta suposición, los "
            "siguientes párrafos proporcionan una perspectiva de los requisitos y "
            "procedimientos para evaluar la habilidad de las cimentaciones para "
            "resistir las cargas impuestas por el sismo sin deformaciones "
            "excesivas. Si los suelos son susceptibles a pérdida significativa de "
            "resistencia, debido a los efectos directos de las vibraciones "
            "sísmicas, entonces se debe, o considerar medidas de mejoramiento de la "
            "condición del suelo de cimentación o realizar análisis que demuestren "
            "que la pérdida de resistencia del suelo no ocasiona deformaciones "
            "estructurales excesivas.\n\n"
            "Las consideraciones del comportamiento de la cimentación son solo una "
            "parte de la rehabilitación sísmica de los edificios. La selección del "
            "objetivo deseado de rehabilitación probablemente deberá definirse sin "
            "relación a los detalles específicos del edificio, incluyendo la "
            "cimentación. El ingeniero estructural escogerá el tipo de "
            "procedimiento de análisis apropiado (estático lineal o dinámico, o "
            "estático no lineal o dinámico).\n\n"
            "H.10.4.1 — CAPACIDADES ÚLTIMAS Y CAPACIDADES DE CARGA — La capacidad "
            "última y de trabajo de los componentes de la cimentación la debe "
            "determinar el ingeniero geotecnista según los requisitos del capítulo "
            "H.4.\n\n"
            "H.10.4.2 — CARACTERÍSTICAS CARGA-DEFORMACIÓN PARA CIMENTACIONES — Las "
            "características carga-deformación se requieren cuando se consideran "
            "los efectos de la cimentación en procedimientos estáticos lineales o "
            "dinámicos, estático no lineal (pushover), o dinámico no lineal "
            "(historia en el tiempo).\n\n"
            "Los parámetros del comportamiento carga-deformación, caracterizados "
            "tanto por rigidez como capacidad, pueden tener un efecto significativo "
            "tanto en la respuesta estructural como en la distribución de la carga "
            "en los elementos de la estructura.\n\n"
            "Los sistemas de cimentación para edificios en algunos casos pueden ser "
            "complejos, pero por simplicidad se consideran tres tipos: "
            "cimentaciones superficiales (zapatas y losas), pilotes y pilas.\n\n"
            "Mientras se reconoce que el comportamiento carga-deformación de las "
            "cimentaciones es no lineal, a causa de las dificultades para "
            "determinar las propiedades del suelo y las cargas estáticas en "
            "cimentaciones, además de la probable variabilidad de los suelos que "
            "soportan las cimentaciones, se recomienda que el ingeniero geotecnista "
            "en conjunto con el estructural escojan una representación equivalente "
            "elasto-plástica del comportamiento carga-deformación de los "
            "cimientos.\n\n"
            "H.10.4.3 — CRITERIO DE ACEPTABILIDAD DE LA CIMENTACIÓN — Este artículo "
            "contiene el criterio de aceptabilidad para los componentes "
            "geotécnicos de las cimentaciones del edificio. Los componentes "
            "estructurales deben cumplir los requisitos del artículo H.4.10. Los "
            "componentes geotécnicos incluyen las partes del suelo de cimientos "
            "superficiales (zapatas y losas), y pilotes y pilas de fricción y de "
            "soporte en la punta. Estos criterios aplican a todas las acciones de "
            "cargas verticales, momentos y fuerzas laterales aplicadas al suelo.\n\n"
            "H.10.4.3.1 — Procedimiento lineal — La aceptabilidad de componentes "
            "geotécnicos sujetos a procedimientos lineales depende las suposiciones "
            "básicas del modelo utilizado en el análisis:\n"
            "(a) Suposición de base fija — Si se supone que la base de la "
            "estructura es completamente rígida (base fija), las acciones sobre "
            "los componentes geotécnicos deberán ser de fuerza controlada. Esta "
            "suposición no se recomienda para edificaciones sensitivas a rotación "
            "de la base u otro tipo de movimiento de la cimentación.\n"
            "(b) Suposición de base flexible — Si la base de la estructura se "
            "modela mediante componentes geotécnicos lineales, no es necesario "
            "cumplir con el estado límite de servicio ya que los desplazamientos "
            "resultantes se pueden acomodar a los criterios de aceptabilidad para "
            "el resto de la estructura.\n\n"
            "H.10.4.3.2 — Procedimiento no lineal — La aceptabilidad de componentes "
            "geotécnicos sujetos a procedimientos lineales depende de las "
            "suposiciones básicas del modelo utilizado en el análisis:\n"
            "(a) Suposición de base fija — Si se supone que la base de la "
            "estructura es completamente rígida, entonces las reacciones en la "
            "base de la estructura, para todos los componentes geotécnicos, no "
            "deben exceder el estado límite de falla. La suposición de base fija no "
            "se recomienda para edificaciones sensitivas a rotación de la base u "
            "otro tipo de movimiento de la cimentación.\n"
            "(b) Suposición de base flexible — Si la base de la estructura se "
            "modela utilizando componentes geotécnicos flexibles, no lineales, "
            "entonces la componente resultante de los desplazamientos no requiere "
            "ser limitada para el estado límite de servicio, ya que los "
            "desplazamientos resultantes se pueden acomodar a los criterios de "
            "aceptabilidad del resto de la estructura, los cuales se basarán en la "
            "necesidad del servicio continuo y seguridad de la edificación."
        ),
    },
    {
        "id": "NSR10-H-H_10_5_rehabilitacion_suelo_cimientos",
        "seccion": "H.10.5 — Rehabilitación del suelo y cimientos (mejoramiento del suelo, zapatas y losas)",
        "titulo": "Título H, H.10.5: rehabilitación del suelo y cimientos — mejoramiento del suelo (inyecciones, jet grouting, densificación) y refuerzo de zapatas y losas superficiales (sub-muradas, vigas de equilibrio, anclajes). Fin del Título H.",
        "texto": (
            "H.10.5 — REHABILITACIÓN DEL SUELO Y CIMIENTOS — Este artículo contiene "
            "guías para modificar las cimentaciones y mejorar el comportamiento "
            "sísmico anticipado. Específicamente, el alcance de este artículo "
            "incluye métodos sugeridos para modificar la cimentación y las "
            "características de los elementos de cimentación desde una perspectiva "
            "geotécnica. Estos deben ser utilizados en combinación con los "
            "requisitos de los materiales estructurales de los otros capítulos.\n\n"
            "H.10.5.1 — MEJORAMIENTO DEL SUELO — Las opciones de mejoramiento del "
            "suelo con el fin de incrementar la capacidad admisible de las "
            "cimentaciones son limitadas (véase el artículo H.10.3.2). Remoción del "
            "suelo, reemplazo, y densificación por vibración generalmente no son "
            "viables porque ocasionan asentamientos de los cimientos o son muy "
            "costosas de implementar sin causar estos asentamientos.\n\n"
            "Inyecciones pueden ser consideradas para incrementar la capacidad "
            "portante. Inyecciones de compactación pueden lograr densificación y "
            "resistencia de una variedad de tipos de suelos, y/o transmitir las "
            "cargas de los cimientos a estratos más duros y profundos. La técnica "
            "requiere de un cuidadoso control para evitar el levantamiento de los "
            "elementos de cimentación o losas de pisos adyacentes durante el "
            "proceso de inyección. Inyecciones químicas (cemento, cal, etc.) pueden "
            "conseguir el reforzamiento de suelos arenosos, pero en suelos de grano "
            "fino o arenas limosas pueden ser poco efectivas. \"Jet grouting\" "
            "también se podría considerar. Estas mismas técnicas también se pueden "
            "utilizar para incrementar la resistencia friccional de la base de los "
            "cimientos a carga lateral.\n\n"
            "Opciones que pueden ser consideradas para incrementar la resistencia "
            "pasiva de los suelos adyacentes a las cimentaciones incluyen remoción "
            "y reemplazo de los suelos con suelos más resistentes, o con suelos "
            "estabilizados con inyecciones químicas, o \"jet grouting\", o suelos "
            "densificados por impacto o compactación vibratoria (si las capas a "
            "compactar no son demasiado gruesas y los efectos de vibración sobre "
            "la estructura son tolerables).\n\n"
            "H.10.5.2 — CIMIENTOS SUPERFICIALES (ZAPATAS Y LOSAS) — Nuevas zapatas "
            "y losas se le pueden adicionar a la estructura para soportar nuevos "
            "elementos estructurales como muros de cortante o pórticos. En estos "
            "casos, las capacidades y rigideces deben ser determinadas de acuerdo "
            "a los procedimientos del artículo H.10.4.\n\n"
            "Zapatas existentes pueden ser agrandadas para incrementar su capacidad "
            "o resistencia a la tracción. Generalmente, las capacidades y rigidez "
            "pueden ser determinadas de acuerdo con el artículo H.10.4. Sin "
            "embargo, puede ser necesaria la consideración de presiones de "
            "contacto existentes sobre la resistencia y rigidez de la zapata "
            "modificada, obtenida mediante un análisis de interacción suelo "
            "estructura, a menos que se consiga modificar la distribución de las "
            "presiones de contacto por algún método viable.\n\n"
            "Las zapatas y losas pueden ser sub-muradas para incrementar su "
            "capacidad o resistencia a tracción. Esta técnica mejora la capacidad "
            "portante bajando el horizonte de contacto de la zapata. La capacidad "
            "a tracción se mejora incrementando la masa de suelo resistente por "
            "encima de la zapata. Generalmente, capacidades y rigideces se pueden "
            "determinar de acuerdo a los procedimientos del artículo H.10.4. "
            "Pueden ser requeridos consideraciones de los efectos de gateo y "
            "transferencia de carga.\n\n"
            "Cuando existe potencial para el desplazamiento diferencial lateral de "
            "las cimentaciones del edificio, se debe suministrar interconexión "
            "adecuada con vigas de equilibrio, o una losa de cimentación bien "
            "reforzada puede proporcionar buena mitigación de estos efectos. Un "
            "sistema de anclajes también proporciona soporte al desplazamiento "
            "diferencial lateral cuando el análisis rotacional lo exige, y debe "
            "considerarse la recomendación del ingeniero geotecnista."
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
    print(f"Codificando {len(textos)} chunks-padre de H.10...")
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

    print(f"Subiendo {len(rows)} chunks-padre de H.10 a nsr10_chunks (upsert por id)...")
    sb.table("nsr10_chunks").upsert(rows, on_conflict="id").execute()
    print("OK. Ahora correr _resplit_titulo_h_h10_por_limite_tokens.py para re-trocear.")


if __name__ == "__main__":
    main()
