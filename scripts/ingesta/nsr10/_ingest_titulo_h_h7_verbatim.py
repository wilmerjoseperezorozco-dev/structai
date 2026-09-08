"""
NSR-10 Titulo H (Estudios Geotecnicos) -- H.7 COMPLETO (Evaluacion
Geotecnica de Efectos Sismicos). Cuarta pieza real de ingesta tras la
auditoria numeral-por-numeral de 2026-09-07 (ver memoria privada del
usuario, project_structai_nsr10_inventario_titulos.md).

H.7.0 (Nomenclatura), H.7.1 (Aspectos basicos: H.7.1.1 efecto de la
litologia y tipos de suelos, H.7.1.2 efecto del tipo de solicitacion,
H.7.1.3 efecto de topografia y tipo de ondas), H.7.2 (Analisis de
respuesta dinamica), H.7.3 (Analisis de estabilidad), H.7.4 (La
licuacion y los fenomenos relacionados: H.7.4.1 licuacion de flujo,
H.7.4.2 movilidad ciclica, H.7.4.3 volcanes de arena, H.7.4.4
susceptibilidad a la licuacion, H.7.4.5 metodos de evaluacion del
potencial de licuacion, H.7.4.6 metodos de mejoramiento de depositos
susceptibles) -- cierra el Capitulo H.7 completo.

Hallazgo real de paginacion (no de contenido): la fuente salta
directamente de la pagina interna H-37 a H-39 -- no existe H-38 como
pagina separada, la seccion "Notas:" en blanco al final de H.7 es parte
de la propia H-37, no una pagina H-38 faltante. H.7 esta 100% completo
pese a esa aparente discontinuidad de numeracion.

Fuente: NSR-10-1451-1500.pdf (Drive id 1DSJnOYqJixF0Nm1ewOH1VBDFpKas4x-y,
ya descargado en scripts/ingesta/nsr10/raw/), paginas PDF 23-27 (H-33 a
H-37), leidas visualmente con Read pages= sobre el PDF nativo.

CHUNKS escritos en piezas por numeral/subnumeral, re-trocheadas
programaticamente al final con VERIFICACION REAL de tokens via
_resplit_titulo_h_h7_por_limite_tokens.py -- mismo metodo ya
establecido (F.4.6/F.4.7, H.3.3+H.4, H.5, H.6).

Uso: python _ingest_titulo_h_h7_verbatim.py
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
        "id": "NSR10-H-H_7_0_nomenclatura",
        "seccion": "H.7.0 (Nomenclatura del Capítulo H.7 — Evaluación geotécnica de efectos sísmicos)",
        "titulo": "G (variación de la rigidez), βs (amortiguamiento), Amax (aceleraciones máximas del terreno).",
        "texto": (
            "CAPÍTULO H.7 — EVALUACIÓN GEOTÉCNICA DE EFECTOS SÍSMICOS. "
            "H.7.0 — NOMENLATURA — G = variación de la rigidez. "
            "β_s = amortiguamiento. A_max = aceleraciones máximas del "
            "terreno."
        ),
    },
    {
        "id": "NSR10-H-H_7_1_aspectos_basicos_intro",
        "seccion": "H.7.1 (Aspectos básicos — introducción)",
        "titulo": "Evaluación geotécnica considera efectos inerciales y cinemáticos; 4 temas: litología, tipo de solicitación sísmica, condiciones topográficas, interacción sismo-suelo-estructura.",
        "texto": (
            "H.7.1 — ASPECTOS BÁSICOS — Para realizar la evaluación "
            "geotécnica de efectos sísmicos que deben ser considerados "
            "en el diseño de estructuras se parte de los aspectos "
            "básicos que están relacionados con la modificación del "
            "movimiento del terreno (efectos inerciales) y los "
            "cinemáticos. Adicionalmente, los aspectos básicos "
            "contribuyen a cuantificar de una manera acertada las "
            "incertidumbres relacionadas con la respuesta dinámica del "
            "terreno, las condiciones de estabilidad de los materiales, "
            "y los efectos del potencial de licuación o movilidad "
            "cíclica en los suelos granulares y en suelos de grano fino "
            "de baja plasticidad. En este Capítulo, los aspectos "
            "básicos se separan en cuatro temas: la incidencia de la "
            "litología del terreno, el tipo de solicitación sísmica, "
            "las condiciones topográficas y al efecto de la interacción "
            "sismo-suelo-estructura."
        ),
    },
    {
        "id": "NSR10-H-H_7_1_1_efecto_litologia_a_b",
        "seccion": "H.7.1.1 (Efecto de la litología y tipos de suelos — caracterización del perfil, rigidez y amortiguamiento)",
        "titulo": "Vs con la profundidad hasta roca/suelos duros (Vs>500m/s); determinar variación de G y βs con el nivel de deformación mediante ensayos dinámicos de laboratorio.",
        "texto": (
            "H.7.1.1 — EFECTO DE LA LITOLOGÍA Y TIPOS DE SUELOS — (a) "
            "La caracterización básica del perfil litológico se "
            "establece en términos de los valores de velocidad de onda "
            "de corte (V_s) con la profundidad y su variación "
            "horizontal, hasta el nivel de roca (rechazo en el ensayo "
            "SPT), o suelos duros (V_s > 500 m/s) mediante ensayos "
            "geofísicos en el terreno. Adicionalmente, de manera "
            "complementaria para efectos de caracterización de la "
            "variación espacial, o para evaluar los rangos de valores "
            "de las propiedades relevantes, se pueden utilizar "
            "correlaciones debidamente soportadas con otros parámetros "
            "geotécnicos. Estas correlaciones no pueden reemplazar las "
            "mediciones directas en el terreno. (b) Para los diferentes "
            "materiales presentes en el perfil se debe determinar la "
            "variación de la rigidez (G) y del amortiguamiento (β_s) "
            "con el nivel de deformaciones y de esfuerzos (degradación "
            "de propiedades dinámicas). La determinación de la "
            "variación de la rigidez dinámica se puede hacer mediante "
            "ensayos dinámicos de laboratorio siempre y cuando se "
            "cuente con muestras representativas de alta calidad. En "
            "este caso los ensayos deben cubrir el rango de interés de "
            "deformaciones y esfuerzos, en función del número de ciclos "
            "de carga, para el problema que se esté estudiando, y se "
            "deben normalizar adecuadamente para poder relacionarlos "
            "con los valores de rigidez en el terreno, preferiblemente "
            "mediante la determinación en el laboratorio, sobre las "
            "mismas muestras, de la velocidad de onda de corte a bajas "
            "deformaciones. Se debe justificar adecuadamente la "
            "normalización que se haga de la variación de la rigidez "
            "dinámica con la deformación."
        ),
    },
    {
        "id": "NSR10-H-H_7_1_1_efecto_litologia_c_d",
        "seccion": "H.7.1.1 (Efecto de la litología — correlaciones internacionales, verificación de resistencia dinámica y licuación)",
        "titulo": "Estimar variación de rigidez/amortiguamiento con correlaciones internacionales comparadas con ensayos dinámicos; considerar licuación, degradación de resistencia y asentamientos por densificación.",
        "texto": (
            "(c) La variación de la rigidez y el amortiguamiento con la "
            "deformación también se debe estimar con base en "
            "referencias debidamente sustentadas de correlaciones o "
            "modelos reportados en la literatura técnica internacional. "
            "Estos resultados se deben comparar con los obtenidos de "
            "los ensayos dinámicos de laboratorio. (d) Se debe dar "
            "consideración explícita a la verificación de la "
            "resistencia dinámica de cada material, incluyendo cuando "
            "sea aplicable, la evaluación del potencial de licuación de "
            "los suelos granulares y suelos de grano fino de baja "
            "plasticidad, y la degradación progresiva de la resistencia "
            "dinámica de los suelos finos con el número de ciclos de "
            "carga equivalente. También deben calcularse los "
            "asentamientos producidos por el sismo (deformación "
            "volumétrica por densificación), empleando criterios o "
            "metodologías actualizadas y reconocidas internacionalmente."
        ),
    },
    {
        "id": "NSR10-H-H_7_1_2_efecto_tipo_solicitacion",
        "seccion": "H.7.1.2 (Efecto del tipo de solicitación — historias de movimiento, componente vertical)",
        "titulo": "Usar mínimo 3 historias de movimiento representativas y compatibles con el Estudio Nacional de Amenaza Sísmica; componente vertical 50-100% de la horizontal para fuentes cercanas (<25km).",
        "texto": (
            "H.7.1.2 — EFECTO DEL TIPO DE SOLICITACIÓN — Para la "
            "evaluación de la respuesta del terreno ante la propagación "
            "del sismo se debe tener presente que cada fuente sismogénica "
            "que produce sismos de diferente magnitud y distancia con "
            "respecto al lo cual genera escenarios de respuesta "
            "dinámica del subsuelo significativamente diferentes, aún "
            "si los niveles de aceleración máxima del terreno son "
            "similares para las diferentes fuentes. Por lo tanto para "
            "evaluación geotécnica de efectos sísmicos los análisis de "
            "respuesta dinámica deben utilizar por lo menos tres "
            "historias de movimiento en función del tiempo "
            "representativas de cada una de las diferentes fuentes "
            "sismogénicas que sean relevantes para el sitio de estudio "
            "y que sean compatibles con los niveles de amenaza sísmica "
            "para el sitio de acuerdo con el Estudio Nacional de "
            "Amenaza Sísmica vigente o estudios posteriores aplicables. "
            "Para el caso de fuentes sismogénicas cercanas (menores de "
            "25 Km de distancia epicentral) con potencial de generación "
            "de eventos superficiales (profundidad focal menor de 20 "
            "Km), debe considerarse el aporte de la componente vertical "
            "de la señal sísmica en el análisis de respuesta del "
            "terreno. Generalmente, la aceleración vertical puede "
            "variar entre el 50% y el 100% del valor de la aceleración "
            "horizontal, según sea cada caso particular. En caso de "
            "existir información instrumentada con las redes de "
            "acelerómetros locales o regionales, es posible definir "
            "para el proyecto ubicado en la localidad estudiada, una "
            "relación más ajustada entre los valores de las dos "
            "componentes de aceleración. Las historias de movimiento "
            "que se utilicen deben ser representativas de las "
            "condiciones en roca, preferiblemente registros reales sin "
            "modificar debidamente sustentados. En caso de que se "
            "utilicen historias sintéticas de movimiento o historias "
            "reales modificadas estas deben ser debidamente sustentadas "
            "para garantizar su representatividad y que sean razonables "
            "desde el punto de vista sismológico. En todos los casos se "
            "debe asegurar que los espectros de aceleración, velocidad "
            "y desplazamientos de las señales que se utilicen sean "
            "compatibles y representativos de las condiciones de "
            "estudio y que estas historias no incluyan efectos previos "
            "de respuesta local o topográfica o cualquier otro tipo de "
            "anomalía que pueda posteriormente verse reflejada en "
            "resultados de respuesta no representativos."
        ),
    },
    {
        "id": "NSR10-H-H_7_1_3_a_b_topografia_ondas",
        "seccion": "H.7.1.3 (Efecto de topografía y tipo de ondas — ondas de corte SH, combinación de ondas superficiales)",
        "titulo": "Ondas SH: modelos 1D/2D/3D según relevancia topográfica; efectos topográficos relevantes si pendiente/profundidad de roca varía >10% en el área de influencia.",
        "texto": (
            "H.7.1.3 — EFECTO DE TOPOGRAFÍA Y DEL TIPO DE ONDAS EN LA "
            "RESPUESTA — (a) Componente de ondas de corte que se "
            "propaga verticalmente (SH) — Este es el tipo de ondas son "
            "las predominantes en los casos donde la superficie del "
            "terreno y la estratigrafía de todo el perfil geotécnico es "
            "horizontal o con pendientes menores de 10%, o donde los "
            "efectos topográficos no son relevantes. Para la evaluación "
            "de la respuesta sísmica se pueden emplear modelos "
            "numéricos unidimensionales (1D), bidimensionales (2D) o "
            "tridimensionales (3D) de propagación de ondas. (b) "
            "Combinación de ondas superficiales y de corte, y efecto de "
            "las longitudes de onda de la excitación en relación con la "
            "respuesta y la estratigrafía — Estos efectos solo se "
            "pueden estudiar mediante modelos de respuesta dinámica "
            "bidimensional (2D) o tridimensional (3D) y son relevantes "
            "cuando las condiciones estratigráficas de suelos y "
            "topografía no son uniforme ni plana, se debe considerar el "
            "efecto topográfico tanto de la variación de la superficie "
            "del terreno, como de la profundidad del contacto con la "
            "roca subyacente, para determinar zonas del terreno donde "
            "se genere amplificación o atenuación local de las ondas "
            "sísmicas. Estos efectos son relevantes si la pendiente del "
            "terreno o del contacto con la roca subyacente son mayores "
            "a 10% en el área de influencia del proyecto. Para tener en "
            "cuenta estos efectos se deben realizar análisis de "
            "respuesta dinámica con modelos numéricos 2D o 3D según sea "
            "la situación particular."
        ),
    },
    {
        "id": "NSR10-H-H_7_1_3_c_d_e_instrumentacion_resonancia",
        "seccion": "H.7.1.3 (Efecto de topografía — instrumentación sísmica, resonancia triple, umbral 0.4g)",
        "titulo": "Validar modelos con instrumentación sísmica local; posible resonancia roca-suelo/suelo-suelo/suelo-estructura; análisis detallado obligatorio para grupos III/IV con roca <0.4g.",
        "texto": (
            "(c) Empleo de la instrumentación sísmica para validar los "
            "modelos numéricos de respuesta dinámica 1D, 2D o 3D. En "
            "las zonas donde se cuente con redes locales o regionales "
            "de acelerómetros, los registros existentes que resulten "
            "representativos de la respuesta del sitio objeto de "
            "estudio, deberán utilizarse para hacer análisis de "
            "sensibilidad del comportamiento dinámico de los materiales "
            "del subsuelo o para establecer análisis comparativos con "
            "los modelos teóricos de la respuesta sísmica asociada a "
            "efectos topográficos. (d) En el rango elástico se puede "
            "registrar un fenómeno de triple resonancia. En primer "
            "término, efecto roca-suelo debido a similitudes entre los "
            "periodos predominantes de vibración de los movimientos "
            "incidentes de los sismos y los movimientos de los "
            "depósitos de suelos. En segundo término, efecto "
            "suelo-suelo ocasionado por el confinamiento de las ondas "
            "en una artesa, causado a su vez por la diferencia entre la "
            "impedancia del suelo contenido y la roca de base; el "
            "resultado inmediato es una mayor duración del sismo "
            "sentido en el depósito de suelos, en relación con el "
            "movimiento originario en roca. En tercer término, un "
            "efecto suelo-estructura cuando coinciden sus períodos "
            "predominantes de vibración y el período fundamental de la "
            "estructura. Cabe anotar que como el comportamiento de la "
            "estructura y el suelo es usualmente no-lineal para el "
            "sismo de diseño, este fenómeno puede no ser relevante para "
            "este sismo. Si bien en el caso de los sismos el "
            "comportamiento no lineal del suelo y de la estructura "
            "cambia los periodos, en el caso de resonancia por "
            "vibraciones ambientales se pueden presentar relativamente "
            "fácil y llegar a sobrepasar los límites que puede tolerar "
            "un residente y causar eventual fatiga de la estructura por "
            "su constante repetición. (e) La evaluación de la "
            "amplificación resulta importante para aceleraciones "
            "originarias en roca inferiores a un valor límite que es "
            "del orden de 0.4g. Para aceleraciones superiores a la "
            "antedicha se presenta el fenómeno contrario, ó sea una "
            "amplificación. El análisis detallado del fenómeno debe "
            "hacerse obligatoriamente para las edificaciones "
            "clasificadas como grupos de uso III, IV (Artículo A.2.9.3.6 "
            "del Reglamento) para las demás categorías es opcional. Los "
            "métodos para efectuar este análisis deben estar "
            "adecuadamente sustentados dentro de la dinámica de suelos "
            "y la ingeniería sísmica. Se permite el uso de modelos "
            "unidimensionales, y cuando la información sobre los "
            "depósitos de suelos lo permita, se pueden emplear modelos "
            "más sofisticados. Su uso debe reemplazarse progresivamente "
            "los métodos aproximados; se recomienda cuando la "
            "información disponible lo justifique y sea compatible con "
            "la complejidad del proyecto. Al respecto deben consultarse "
            "los requisitos del Capítulo A2 del Reglamento."
        ),
    },
    {
        "id": "NSR10-H-H_7_2_analisis_respuesta_dinamica",
        "seccion": "H.7.2 (Análisis de respuesta dinámica — 6 componentes obligatorios)",
        "titulo": "Señales de entrada, extensión del dominio hasta la roca, discretización del medio, compatibilidad geotécnico-numérico, historias de esfuerzos/aceleración, historias de desplazamientos.",
        "texto": (
            "H.7.2 — ANÁLISIS DE RESPUESTA DINÁMICA — El tipo de "
            "análisis de respuesta dinámica se debe seleccionar de "
            "acuerdo con los criterios antes indicados, teniendo en "
            "cuenta la litología y las condiciones topográficas y puede "
            "ser en una, dos o tres dimensiones. Los modelos que se "
            "utilicen deben ser internacionalmente aceptados, y para su "
            "uso se deben establecer de manera clara y explícita los "
            "siguientes componentes del análisis: (a) Señales de "
            "entrada — Debe tenerse en cuenta los tipos de fuentes y "
            "eventos representativos de la amenaza sísmica, incluyendo "
            "acelerogramas y espectros de aceleración, velocidad y "
            "desplazamientos. (b) Extensión del dominio para el modelo "
            "de análisis — Debe llegar hasta el nivel de la roca y para "
            "los modelos de dos y tres dimensiones se debe extender las "
            "fronteras laterales lo suficiente para representar "
            "adecuadamente el problema (efectos de variación lateral de "
            "la litología y generación y propagación de ondas "
            "superficiales). (c) Discretización del medio continuo — "
            "En modelos numéricos la discretización de la malla "
            "(elementos finitos, diferencias finitas, etc.) debe ser "
            "tal que no produzca efectos numéricos de filtrado de "
            "componentes del movimiento. La discretización que se "
            "utilice se debe sustentar objetivamente. (d) Relación "
            "entre el modelo geotécnico para análisis de respuesta y "
            "los parámetros de caracterización geotécnica dinámica del "
            "subsuelo — Debe existir compatibilidad entre el modelo "
            "geotécnico, la caracterización geotécnica dinámica "
            "realizada y los niveles de esfuerzos y deformaciones del "
            "problema estudiado. Estos se deben sustentar adecuadamente. "
            "(e) Se debe presentar resultados de historias de "
            "aceleración historias de esfuerzos cortantes generados o "
            "espectros de respuesta tanto de aceleración como de "
            "velocidad y desplazamientos — Deben escogerse los puntos "
            "que sean relevantes para el problema considerado (nivel de "
            "cimentación, campo libre, centro de gravedad de masas que "
            "empujan sobre estructuras de contención o talud, perfil de "
            "aceleración con la profundidad para evaluación de "
            "potencial de licuación o zonas de falla, etc.), según sea "
            "aplicable. (f) Se deben presentar historias de "
            "desplazamientos totales y relativos en puntos relevantes "
            "del problema — Por ejemplo desplazamientos relativos a lo "
            "largo de cimentaciones profundas, o entre diferentes "
            "puntos a lo largo de estructuras de cimentación contención "
            "o talud, etc. según sea aplicable, con el fin de "
            "establecer los aspectos cinemáticos relevantes de la "
            "respuesta."
        ),
    },
    {
        "id": "NSR10-H-H_7_3_analisis_estabilidad",
        "seccion": "H.7.3 (Análisis de estabilidad — 8 aspectos a considerar)",
        "titulo": "Empujes dinámicos, deformaciones transientes/permanentes/diferenciales, cimentaciones ante volteo/arrancamiento, licuación, densificación, coeficiente pseudo-estático, estabilidad dinámica de taludes.",
        "texto": (
            "H.7.3 — ANÁLISIS DE ESTABILIDAD — A partir de la "
            "caracterización y los análisis de respuesta dinámica o "
            "utilizando métodos internacionalmente aceptados, según sea "
            "la condición particular del sitio, se deben considerar los "
            "siguientes aspectos relacionados con la estabilidad del "
            "terreno o de las estructuras en contacto con el suelo: (a) "
            "Empujes dinámicos del terreno para estructuras de "
            "contención y pilotes de punta. (b) Deformaciones "
            "transientes y permanentes impuestas por el movimiento "
            "sísmico a estructuras enterradas. (c) Deformaciones "
            "diferenciales generadas por el sismo (transientes y "
            "permanentes) en estructuras de gran extensión o en casos "
            "en que las condiciones del terreno puedan cambiar "
            "sustancialmente en el área del proyecto. (d) Estabilidad "
            "de cimentaciones por efectos de volteo, arrancamiento, "
            "desplazamiento lateral capacidad portante o efectos "
            "hidrodinámicos. Para estos análisis se deben considerar "
            "las cargas de servicio (sin mayorar) de las solicitaciones "
            "dinámicas de las estructuras sin considerar reducción por "
            "efectos de ductilidad de las mismas. (e) Potencial de "
            "licuación o desplazamiento (corrimiento) lateral por "
            "movilidad cíclica (f) Deformaciones o asentamientos "
            "permanentes generados por densificación del terreno. (g) "
            "Definición del coeficiente pseudo-estático de fuerza "
            "horizontal y vertical en taludes naturales o excavaciones, "
            "teniendo en cuenta la incidencia de los efectos "
            "topográficos en el análisis de estabilidad durante sismo. "
            "(h) Estabilidad dinámica o seudo-estática de taludes "
            "naturales o de excavación de influencia directa para el "
            "proyecto, a partir de modelos de respuesta que involucren "
            "relaciones esfuerzo-deformación-tiempo o con métodos "
            "empíricos."
        ),
    },
    {
        "id": "NSR10-H-H_7_4_licuacion_intro",
        "seccion": "H.7.4 (La licuación y los fenómenos relacionados — introducción)",
        "titulo": "Licuación: tendencia a densificarse bajo carga cíclica en suelos granulares saturados con drenaje lento, crecimiento de presión de poros y pérdida de esfuerzo efectivo.",
        "texto": (
            "H.7.4 — LA LICUACIÓN Y LOS FENÓMENOS RELACIONADOS — Los "
            "suelos granulares tienen una tendencia natural a "
            "densificarse bajo carga, ya sea ésta monotónica o cíclica. "
            "Cuando el suelo está saturado y el drenaje es lento o "
            "totalmente inexistente, esta tendencia a la densificación "
            "causa el crecimiento de la presión de poros, en exceso de "
            "su estado estático, y el decrecimiento correlativo del "
            "esfuerzo efectivo hasta que sobreviene la flotación de las "
            "partículas, lo que ha recibido el nombre genérico de "
            "licuación."
        ),
    },
    {
        "id": "NSR10-H-H_7_4_1_2_3_licuacion_flujo_movilidad_volcanes",
        "seccion": "H.7.4.1 / H.7.4.2 / H.7.4.3 (Licuación de flujo, movilidad cíclica, volcanes de arena)",
        "titulo": "Flujo: esfuerzo estático>resistencia del suelo licuado, colapso; movilidad cíclica: esfuerzo estático<resistencia, falla escalonada; volcanes de arena: erupciones por disipación de presión de poros.",
        "texto": (
            "H.7.4.1 — LICUACIÓN DE FLUJO — Se define como un estado de "
            "movimiento catastrófico donde el esfuerzo cortante "
            "estático es superior a la resistencia correlativa del "
            "suelo en su condición licuada. Cuando sobreviene el "
            "movimiento sísmico, este actúa como disparador y en "
            "adelante las grandes deformaciones generadas son el "
            "producto del estado de esfuerzos estáticos. H.7.4.2 — "
            "MOVILIDAD CÍCLICA — En contraste con el anterior, el "
            "fenómeno denominado movilidad cíclica tiene lugar cuando "
            "el estado de esfuerzos estáticos es inferior a la "
            "resistencia del suelo licuado; durante el movimiento "
            "sísmico el estado de esfuerzos aumenta en forma escalonada "
            "hasta que se alcanza la resistencia del suelo y sobreviene "
            "la falla. Los términos licuación horizontal, corrimiento "
            "lateral y oscilación del terreno son casos especiales de "
            "movilidad cíclica observados en la práctica. H.7.4.3 — "
            "VOLCANES DE ARENA — Es un fenómeno que frecuentemente "
            "acompaña la ocurrencia de la licuación; durante el "
            "movimiento sísmico, o inmediatamente después, el exceso de "
            "presión de poros es disipado, normalmente hacia arriba "
            "como la dirección más fácil y en puntos localizados, o a "
            "lo largo de grietas, se producen erupciones de arena en "
            "estado líquido que conforman pequeños volcanes."
        ),
    },
    {
        "id": "NSR10-H-H_7_4_4_susceptibilidad_licuacion",
        "seccion": "H.7.4.4 (Susceptibilidad a la licuación — 9 características de suelos)",
        "titulo": "Holoceno más susceptible que Pleistoceno; saturación necesaria; depósitos fluviales/coluviales/eólicos; arenas finas/limosas muy susceptibles; partículas redondeadas y micáceas más susceptibles.",
        "texto": (
            "H.7.4.4 — SUSCEPTIBILIDAD A LA LICUACIÓN — Teniendo en "
            "cuenta que no todos los suelos son licuables es preciso "
            "conformar una lista de características del suelo mismo y "
            "de su circunstancia, que conducen a que sean susceptibles "
            "a la licuación: (a) La edad geológica es determinante: "
            "suelos del Holoceno son más susceptibles que los del "
            "Pleistoceno y la licuación de depósitos de edades "
            "anteriores no es común. (b) El depósito de suelo debe "
            "estar saturado, o cerca de la saturación, para que ocurra "
            "la licuación. (c) Depósitos fluviales, coluviales, "
            "granulares, eólicos, cuando saturados, son susceptibles de "
            "licuación. (d) Asimismo pueden clasificarse como licuables "
            "los depósitos de abanicos aluviales, planicies aluviales, "
            "playas, terrazas y estuarios. (e) Son muy susceptibles a "
            "la licuación las arenas finas y arenas limosas, "
            "relativamente uniformes, con densidad suelta y media. "
            "Generalmente se producen grandes deformaciones del terreno "
            "y de las estructuras apoyadas, y pueden formar volcanes de "
            "arena en superficie con los correspondientes cambios "
            "volumétricos severos. (f) Los depósitos bien gradados con "
            "tamaños hasta gravas, gravas arenosas y gravas "
            "areno-limosas, son menos susceptibles a licuación, pero de "
            "todas formas deben verificarse. Estos materiales también "
            "pueden generar cambios volumétricos del terreno. (g) Los "
            "limos, limos arcillosos y arcillas limosas, de baja "
            "plasticidad y con la humedad natural cercana al límite "
            "líquido, también son susceptibles de presentar licuación o "
            "falla cíclica. Generalmente se produce la degradación "
            "progresiva de la resistencia dinámica de los suelos finos "
            "con el número de ciclos de carga equivalente, llevándolos "
            "a la falla o generando grandes asentamientos del terreno y "
            "de las estructuras apoyadas en él. (h) Suelos con "
            "partículas redondeadas, son más susceptibles que suelos "
            "con partículas angulares. Suelos con partículas micáceas, "
            "propios de suelos volcánicos, son más susceptibles. (i) "
            "Cuando el depósito está en condición seca o con bajo grado "
            "de saturación, se genera un proceso de densificación con "
            "las consecuentes deformaciones permanentes del terreno y "
            "estructuras apoyadas en él."
        ),
    },
    {
        "id": "NSR10-H-H_7_4_5_metodos_evaluacion_potencial",
        "seccion": "H.7.4.5 (Métodos de evaluación del potencial de licuación — estudio geotécnico y parámetros)",
        "titulo": "Evaluar con técnicas de laboratorio/campo determinísticas/probabilísticas; el Estudio Geotécnico debe describir consecuencias (asentamiento diferencial, corrimiento lateral, presión sobre estructuras) y medidas de mitigación.",
        "texto": (
            "H.7.4.5 — MÉTODOS DE EVALUACIÓN DEL POTENCIAL DE LICUACIÓN "
            "— Para la evaluación del potencial de licuación y de las "
            "deformaciones permanentes, se deben emplear técnicas de "
            "laboratorio y/o ensayos de campo, que correspondan a "
            "metodologías determinísticas o probabilísticas "
            "actualizadas reconocidas internacionalmente. El Estudio "
            "Geotécnico deberá describir la susceptibilidad y "
            "consecuencias potenciales de licuación y pérdida de "
            "resistencia del suelo (incluyendo estimativos de "
            "asentamiento diferencial, corrimiento lateral, cargas "
            "laterales sobre las cimentaciones, reducción de la "
            "capacidad de soporte de las cimentaciones, incremento en "
            "la presión lateral sobre estructuras de retención y "
            "flotación de estructuras enterradas), y deberá discutir "
            "las medidas para la mitigación (numeral H.7.5). Las "
            "medidas de mitigación deberán ser tenidas en consideración "
            "en el diseño de la estructura y pueden incluir, pero no "
            "son limitadas a, estabilización o densificación del "
            "terreno, selección de tipos de cimentaciones a "
            "profundidades apropiadas, selección de sistemas "
            "estructurales que se acomoden a los desplazamientos y "
            "fuerzas anticipadas, o alguna combinación de estas "
            "medidas. También deben evaluarse las implicaciones de las "
            "medidas de mitigación para garantizar el funcionamiento "
            "del proyecto y su entorno luego del sismo. En general, "
            "debe buscarse que las estructuras no queden ubicadas sobre "
            "suelos susceptibles a la licuación. El potencial de "
            "licuación del suelo, la pérdida de resistencia y las "
            "deformaciones permanentes, deberían ser evaluadas para las "
            "aceleraciones máximas del terreno (A_max), las magnitudes "
            "(M_w) esperadas de los posibles escenarios de eventos "
            "sísmicos, número de ciclos de carga, la resistencia a la "
            "penetración del suelo (ensayos SPT, cono estático, "
            "piezocono, becker, V_s, etc), y demás características "
            "consistentes con los movimientos sísmicos del terreno y el "
            "método empleado. Se permite determinar la A_max basado en "
            "un estudio de microzonificación sísmica de la ciudad o en "
            "un estudio específico de respuesta de sitio que tenga en "
            "cuenta efectos de amplificación (numerales A.1.9 y H.7.2). "
            "En suelos finos, por su comportamiento particular, podrá "
            "verificarse mediante relaciones que incluyan IP, Wn/LL, y "
            "demás parámetros sugeridos por las metodologías modernas "
            "sobre el tema."
        ),
    },
    {
        "id": "NSR10-H-H_7_4_6_metodos_mejoramiento",
        "seccion": "H.7.4.6 (Métodos de mejoramiento de depósitos susceptibles a la licuación — 14 técnicas)",
        "titulo": "Drenajes, vibro-densificación/compactación/reemplazo, pilotes de compactación/radicales, compactación dinámica, inyecciones, estribos de sobrecarga, jet grouting, vitrificación in-situ, explosiones.",
        "texto": (
            "H.7.4.6 — MÉTODOS DE MEJORAMIENTO DE LOS DEPÓSITOS DE "
            "SUELOS SUCEPTIBLES A LA LICUACIÓN — En correspondencia con "
            "los factores que aumentan la vulnerabilidad del suelo ante "
            "los esfuerzos cíclicos se indican algunos métodos para "
            "densificar el terreno y/o mejorar su resistencia. Estos "
            "son: (a) Drenajes — Drenajes y sub drenajes de grava, "
            "gravilla, drenajes tipo \"Mecha\" (Wick) y pozos para "
            "mantener baja la presión del agua y disipar eventuales "
            "excesos. (b) Vibro-densificación — Es una densificación "
            "por vibración que opera por medio de una licuación "
            "moderada que produce densificación del depósito. (c) "
            "Vibro-compactación — Vibración bajo agua que produce la "
            "densificación de material; las aberturas son rellenadas "
            "luego con material compactado. (d) Vibro-reemplazo — "
            "Huecos perforados a golpes, son luego rellenados con grava "
            "arena y piedra, con o sin agentes cementantes. (e) Pilotes "
            "de compactación — Procede mediante el hincado con "
            "vibración de pilotes de desplazamiento. (f) Compactación "
            "dinámica — Mediante una repetida aplicación del impacto de "
            "un gran peso dejado caer desde cierta altura con una guía "
            "preparada para el efecto. (g) Inyecciones de compactación "
            "— Inyecciones de una mezcla gruesa y viscosa de material "
            "que produce el desplazamiento y la compactación del "
            "depósito. (h) Estribos de sobrecarga — Que consiste en "
            "aumentar la resistencia a la licuación aumentando, con "
            "sobrecarga, la presión afectiva de confinamiento. (i) "
            "Pilotes Radicales — A veces llamados banderillas, con "
            "diámetro reducido, perforados e inyectados, pueden reducir "
            "el potencial de licuación. (j) Inyección de elementos "
            "químicos — Inyección a presión de elementos químicos "
            "cementantes del depósito arenoso grueso. (k) Jet grouting "
            "— Que excava, mezcla y rellena materiales adicionales, "
            "incluso cementantes mediante chorros de agua a alta "
            "presión. (l) Pilotes y pantallas pre excavadas — La "
            "colocación de pilotes y pantallas -a presión o sin ella- "
            "rellenos en cemento, cal, o asfalto reducen el potencial "
            "de licuación. (m) Vitrificación in-situ — Consiste en la "
            "fundición del suelo mediante chorros de fuego que "
            "transforman el material en roca. (n) Explosiones y "
            "voladuras — Con un patrón determinado y a una profundidad "
            "relacionada con la magnitud del problema, pueden inducir "
            "licuación limitada y producir la densificación del "
            "material en profundidad."
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

    print(f"\nOK: {len(rows)} chunks verbatim de H.7 cargados. H.7 queda COMPLETO.")


if __name__ == "__main__":
    main()
