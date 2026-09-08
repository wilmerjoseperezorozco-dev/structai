"""
Dataset de evaluación RAGAS — NSR-10 y normas asociadas.

Reutiliza los mismos hechos ya verificados a mano en
apps/api/tests/test_rag_nsr10_regresion.py (no se inventan preguntas
nuevas para esto) — cada uno ya tiene un hecho numérico real confirmado
contra el PDF oficial (o, para NTC/SGSST, contra el texto verbatim ya
cargado en ntc_chunks). Aquí se les agrega un `ground_truth` corto (una
oración con el hecho real, no una respuesta completa "oficial") para que
RAGAS pueda calcular context_precision/context_recall además de
faithfulness/answer_relevancy (que no necesitan ground_truth).

El ground_truth es deliberadamente mínimo -- una frase que contiene el
hecho verificado, no una redacción completa "ideal" de la norma (eso
sería inventar contenido que no se verificó línea por línea). Esto basta
para que RAGAS mida si el contexto recuperado contiene esa frase/idea,
sin arriesgar que el ground_truth mismo esté mal redactado.

Ampliación 2026-08-27 (de 12 a 52 preguntas, a pedido del usuario): las
12 originales cubrían solo Títulos A/B/C. Las nuevas 40 extienden la
misma disciplina a los títulos que ya están verbatim completos (D, E, G)
y a los chunks de precisión ya existentes en A/F/J/K, más NTC 121/174/1500
y el Decreto 1072 (SGSST) -- nada inventado, todo extraído con SQL directo
contra nsr10_chunks/ntc_chunks y verificado contra el texto real antes de
escribir el ground_truth. Ver [[project_structai_ragas_baseline]] y
[[project_structai_nsr10_inventario_titulos]] en memoria.

Ampliación posterior no documentada aquí (detectada 2026-09-07 al recontar
el archivo: el docstring seguía diciendo "52 preguntas" pero
CASOS_BASELINE ya tenía 103 -- quedó desactualizado tras agregarse, en
sesiones siguientes, la cobertura extensa de Título F.4 (acero formado en
frío) y F.5 (aluminio), que sí siguió el mismo criterio de extracción
verbatim + verificación, solo que sin actualizar este comentario).

Ampliación 2026-09-07 (de 103 a 143 preguntas, a pedido del usuario, tras
analizar la variedad real del dataset): las 103 anteriores son casi en su
totalidad preguntas de un solo hecho numérico ("¿cuál es el valor de X
según el Título Y?"), sin ninguna que combine dos títulos, ninguna
adversarial (sin respuesta real en el corpus), ninguna compuesta
precio+norma, y ninguna con fraseo coloquial de campo. Las 40 nuevas
preguntas (id con prefijo "X-...", "ADV-...", "COMP-...", "COLOQ-...")
se agregan al final de CASOS_BASELINE, agrupadas en 4 bloques nuevos con
su propio comentario de sección -- no se creó una lista aparte a
propósito, para que ragas_52preguntas.py siga corriendo sobre un solo
dataset sin tener que tocar ese script.

Ampliación 2026-09-07 (misma sesión, de 143 a 145): +2 preguntas reales
de Título H (ids "H-asentamiento-..."/"H-fsicp-..."), primera ingesta
tras la auditoría numeral-por-numeral que confirmó que Título H solo
cubría H.1-H.3.2 (~18% del título) -- ver memoria privada del usuario,
project_structai_nsr10_inventario_titulos.md.
"""

CASOS_BASELINE = [
    {
        "pregunta": "El Titulo B trata directamente las fuerzas sismicas de diseño?",
        "ground_truth": "No, el Título B trata cargas y no fuerzas sísmicas; las fuerzas sísmicas de diseño están en el Título A.",
        "id": "B-viento-no-es-sismo",
    },
    {
        "pregunta": "Segun la tabla de carga viva de la NSR-10, cual es la carga viva para estanterias en una biblioteca?",
        "ground_truth": "La carga viva para estanterías en una biblioteca es 7.0 kN/m².",
        "id": "B-biblioteca-estanterias-7kNm2",
    },
    {
        "pregunta": "Cual es la carga minima de diseño por viento en el SPRFV segun la NSR-10?",
        "ground_truth": "La carga mínima de diseño por viento en el sistema principal de resistencia a fuerzas de viento (SPRFV) es 0.40 kN/m².",
        "id": "B-viento-minimo-040",
    },
    {
        "pregunta": "Cuales son los 4 sistemas estructurales de resistencia sismica que reconoce la NSR-10?",
        "ground_truth": "Los 4 sistemas estructurales de resistencia sísmica son: muros de carga, combinado, pórtico y sistema dual.",
        "id": "A-4-sistemas-estructurales",
    },
    {
        "pregunta": "En el analisis dinamico, el cortante dinamico total en la base no puede ser menor a que porcentaje del cortante de la fuerza horizontal equivalente, para estructuras regulares e irregulares?",
        "ground_truth": "El cortante dinámico total en la base no puede ser menor al 80% para estructuras regulares y 90% para estructuras irregulares.",
        "id": "A-ajuste-dinamico-80-90",
    },
    {
        "pregunta": "Cuales son los valores de Aa y Av para Barranquilla segun la NSR-10?",
        "ground_truth": "Los valores de Aa y Av para Barranquilla son 0.10.",
        "id": "A-Aa-Av-Barranquilla",
    },
    {
        "pregunta": "Cual es la deriva maxima permitida como porcentaje de la altura de piso para una estructura de concreto reforzado?",
        "ground_truth": "La deriva máxima permitida para una estructura de concreto reforzado es 1.0% de la altura de piso.",
        "id": "A-deriva-maxima-1-porciento",
    },
    {
        "pregunta": "Cual es la resistencia minima a la compresion f'c que exige la NSR-10 para el concreto estructural?",
        "ground_truth": "La resistencia mínima a la compresión f'c que exige la NSR-10 para el concreto estructural es 17 MPa.",
        "id": "C-fc-minimo-general-17MPa",
    },
    {
        "pregunta": "Cual es la resistencia minima a la compresion del concreto para estructuras con capacidad de disipacion de energia especial DES o moderada DMO?",
        "ground_truth": "La resistencia mínima a la compresión del concreto para estructuras DES o DMO es 21 MPa.",
        "id": "C-fc-minimo-DMO-DES-21MPa",
    },
    {
        "pregunta": "Cual es el recubrimiento minimo cuando el concreto esta colocado contra el suelo y expuesto permanentemente a el?",
        "ground_truth": "El recubrimiento mínimo cuando el concreto está colocado contra el suelo y expuesto permanentemente a él es 75 mm.",
        "id": "C-recubrimiento-contacto-suelo-75mm",
    },
    {
        "pregunta": "Cuales son los factores de reduccion de resistencia phi para secciones controladas por traccion y para cortante?",
        "ground_truth": "El factor de reducción de resistencia phi para secciones controladas por tracción es 0.90.",
        "id": "C-factor-phi-traccion-090",
    },
    {
        "pregunta": "Cual es el angulo de doblez de los ganchos sismicos en estribos de confinamiento para estructuras DMO y DES?",
        "ground_truth": "El ángulo de doblez de los ganchos sísmicos en estribos de confinamiento para estructuras DMO y DES es 135 grados.",
        "id": "C-ganchos-sismicos-135grados",
    },
    # ---- Título C, ampliación ----
    {
        "pregunta": "Cual es la cuantia maxima de refuerzo a flexion permitida en vigas de porticos resistentes a momento con capacidad especial DES segun el Titulo C?",
        "ground_truth": "La cuantía de refuerzo a flexión en vigas de pórticos DES no debe exceder 0.025.",
        "id": "C-cuantia-maxima-flexion-DES-0025",
    },
    {
        "pregunta": "Cual es el valor maximo de fyt que se puede usar para calcular la cuantia del refuerzo de confinamiento segun el Titulo C?",
        "ground_truth": "El valor de fyt usado para calcular la cuantía del refuerzo de confinamiento no debe exceder 700 MPa.",
        "id": "C-fyt-maximo-confinamiento-700MPa",
    },
    {
        "pregunta": "Cual es el espaciamiento maximo del refuerzo en diafragmas estructurales de concreto, excepto losas post-tensadas, segun el Titulo C?",
        "ground_truth": "El espaciamiento del refuerzo en diafragmas estructurales, excepto losas post-tensadas, no debe exceder 450 mm.",
        "id": "C-diafragmas-espaciamiento-max-450mm",
    },
    # ---- Título D (Mampostería Estructural) ----
    {
        "pregunta": "A partir de que area construida es obligatoria la supervision tecnica en una estructura de mamposteria segun el Titulo D?",
        "ground_truth": "Toda edificación de mampostería con más de 3000 m² de área construida debe someterse a supervisión técnica.",
        "id": "D-supervision-tecnica-3000m2",
    },
    {
        "pregunta": "Cual es el valor minimo absoluto de resistencia a la compresion del mortero de relleno a los 28 dias segun el Titulo D, sin importar la resistencia de la mamposteria?",
        "ground_truth": "La resistencia a la compresión del mortero de relleno a los 28 días nunca puede ser inferior a 12.5 MPa.",
        "id": "D-mortero-relleno-minimo-125MPa",
    },
    {
        "pregunta": "Que porcentaje maximo del area de la seccion transversal pueden ocupar las celdas verticales en una unidad de mamposteria de perforacion vertical segun el Titulo D?",
        "ground_truth": "El área de las celdas verticales no puede ser mayor al 65% del área de la sección transversal.",
        "id": "D-celdas-verticales-max-65porciento",
    },
    {
        "pregunta": "Cual es el diametro minimo de refuerzo permitido en celdas de mamposteria inyectadas con mortero segun el Titulo D?",
        "ground_truth": "El diámetro mínimo de refuerzo en celdas inyectadas es N°3 (3/8'') o 10M (10 mm).",
        "id": "D-diametro-minimo-refuerzo-celdas-10mm",
    },
    {
        "pregunta": "Cual es el espesor minimo nominal de un muro de mamposteria NO reforzada segun el Titulo D?",
        "ground_truth": "El espesor mínimo nominal de un muro de mampostería no reforzada es 120 mm.",
        "id": "D-espesor-minimo-no-reforzada-120mm",
    },
    {
        "pregunta": "En que condicion de amenaza sismica se permite usar mamposteria no reforzada como sistema de resistencia sismica segun el Titulo D?",
        "ground_truth": "La mampostería no reforzada solo puede usarse como sistema de resistencia sísmica en zonas de amenaza sísmica baja donde Aa sea menor o igual a 0.05.",
        "id": "D-no-reforzada-zona-baja-Aa-005",
    },
    {
        "pregunta": "En que dimension de probetas se mide la resistencia a la compresion de los morteros de pega tipo H M S o N segun el Titulo D?",
        "ground_truth": "La resistencia a la compresión de los morteros de pega se mide en cubos de 50 mm de lado, o en cilindros de 75 mm de diámetro por 150 mm de altura.",
        "id": "D-morteros-probetas-cubos-50mm",
    },
    # ---- Título E (Casas de Uno y Dos Pisos) ----
    {
        "pregunta": "Cual es la resistencia minima a compresion a los 28 dias del mortero de pega en mamposteria confinada segun el Titulo E?",
        "ground_truth": "La resistencia mínima a la compresión del mortero de pega a los 28 días es 7.5 MPa.",
        "id": "E-mortero-pega-75MPa",
    },
    {
        "pregunta": "Cual es el espesor minimo nominal de un muro estructural en zona sismica alta para una casa de dos pisos, primer nivel, segun el Titulo E?",
        "ground_truth": "El espesor mínimo nominal en zona sísmica alta, casa de dos pisos, primer nivel, es 110 mm.",
        "id": "E-espesor-muro-zona-alta-2pisos-110mm",
    },
    {
        "pregunta": "Cual es el area transversal minima de las columnas de confinamiento en mamposteria confinada segun el Titulo E?",
        "ground_truth": "El área transversal mínima de las columnas de confinamiento es 20 000 mm² (200 cm²).",
        "id": "E-columnas-confinamiento-area-20000mm2",
    },
    # ---- Título G (Madera y Guadua) ----
    {
        "pregunta": "Cuantos pies tablares tiene un metro cubico de madera segun el Titulo G?",
        "ground_truth": "Un metro cúbico de madera tiene 424 pies tablares.",
        "id": "G-m3-424-pies-tablares",
    },
    {
        "pregunta": "Cual es el contenido de humedad maximo permitido para madera estructural en general, y para madera laminada, segun el Titulo G?",
        "ground_truth": "La madera estructural debe tener un contenido de humedad máximo del 19%, o del 12% si es madera laminada.",
        "id": "G-humedad-madera-estructural-19-12porciento",
    },
    {
        "pregunta": "Se permiten las uniones clavadas en elementos de guadua segun el Titulo G?",
        "ground_truth": "No, las uniones clavadas no se permiten en guadua porque los clavos inducen grietas longitudinales.",
        "id": "G-guadua-uniones-clavadas-prohibidas",
    },
    {
        "pregunta": "Para que contenido de humedad maximo son representativas las cargas admisibles de conexiones de guadua de la tabla G.12.11-2 segun el Titulo G?",
        "ground_truth": "Las cargas admisibles de la tabla G.12.11-2 son representativas de guaduas con contenido de humedad inferior al 19%.",
        "id": "G-guadua-humedad-cargas-admisibles-19porciento",
    },
    # ---- Título A, ampliación ----
    {
        "pregunta": "Cual es la deriva maxima permitida para mamposteria con falla predominante por cortante segun el Titulo A?",
        "ground_truth": "La deriva máxima permitida para mampostería con falla predominante por cortante es 0.5% de la altura de piso.",
        "id": "A-deriva-mamposteria-cortante-05porciento",
    },
    # ---- Título F, ampliación ----
    {
        "pregunta": "Cual es la ecuacion basica de diseño DCCR para estructuras de acero segun el Titulo F?",
        "ground_truth": "La ecuación básica del método DCCR es Ru menor o igual a phi por Rn, donde Ru es la resistencia requerida, Rn la resistencia nominal y phi el coeficiente de reducción de resistencia.",
        "id": "F-DCCR-formula-Ru-phiRn",
    },
    {
        "pregunta": "Cuales son los limites de luz entre columnas y peralte total de la cercha en un Portico con Cercha Ductil (PCD) segun el Titulo F?",
        "ground_truth": "En un Pórtico con Cercha Dúctil (PCD), la luz entre columnas no debe exceder 20 m y el peralte total de la cercha no debe exceder 1.8 m.",
        "id": "F-PCD-limites-luz20m-peralte18m",
    },
    # ---- Título J (Protección contra Incendios) ----
    {
        "pregunta": "Cual es el area de servicio y el caudal minimo requerido por hidrante para un hospital segun el Titulo J?",
        "ground_truth": "Para hospitales, el área de servicio por hidrante es 500 m² y el caudal mínimo requerido es 63 L/s.",
        "id": "J-hidrante-hospital-500m2-63Ls",
    },
    {
        "pregunta": "Cual es la resistencia al fuego minima en horas de un muro cortafuego en una edificacion de categoria de riesgo I segun el Titulo J?",
        "ground_truth": "Un muro cortafuego en categoría de riesgo I requiere una resistencia al fuego mínima de 3 horas.",
        "id": "J-muro-cortafuego-categoria1-3horas",
    },
    # ---- Título K (Otros Requisitos Complementarios) ----
    {
        "pregunta": "Cual es la fuerza maxima requerida para abrir completamente una puerta de salida segun el Titulo K?",
        "ground_truth": "La fuerza requerida para abrir completamente una puerta de salida debe ser inferior a 250 N.",
        "id": "K-fuerza-apertura-puerta-250N",
    },
    {
        "pregunta": "Por cuanto tiempo minimo debe permanecer en servicio el sistema de iluminacion de emergencia tras una falla del sistema principal segun el Titulo K?",
        "ground_truth": "El sistema de iluminación de emergencia debe estar en servicio por no menos de 1.5 horas tras una falla del sistema principal.",
        "id": "K-iluminacion-emergencia-15horas",
    },
    {
        "pregunta": "Cuantas salidas minimas se requieren para una edificacion con carga de ocupacion entre 501 y 1000 personas segun el Titulo K?",
        "ground_truth": "Una edificación con carga de ocupación entre 501 y 1000 personas requiere mínimo 3 salidas.",
        "id": "K-numero-salidas-501-1000-3salidas",
    },
    # ---- Título H (Estudios Geotécnicos) ----
    {
        "pregunta": "Cuantos años minimos de experiencia en diseño geotecnico de cimentaciones debe tener el profesional que dirige un estudio geotecnico segun el Titulo H?",
        "ground_truth": "El profesional que dirige un estudio geotécnico debe tener una experiencia mayor de 5 años en diseño geotécnico de cimentaciones.",
        "id": "H-experiencia-geotecnista-5anos",
    },
    {
        "pregunta": "Cual es la profundidad minima y el numero minimo de sondeos para una unidad de construccion de categoria Alta (11 a 20 niveles) segun el Titulo H?",
        "ground_truth": "Para categoría Alta (11 a 20 niveles), la profundidad mínima de sondeos es 25 m y el número mínimo es 4 sondeos.",
        "id": "H-sondeos-categoria-alta-25m-4sondeos",
    },
    {
        "pregunta": "Entre cuantos niveles y que rango de cargas de servicio define el Titulo H la categoria Media de una unidad de construccion?",
        "ground_truth": "La categoría Media se define entre 4 y 10 niveles, con cargas de servicio entre 801 y 4000 kN.",
        "id": "H-categoria-media-4a10niveles",
    },
    # ---- Título I (Supervisión Técnica) ----
    {
        "pregunta": "Cual es la excepcion a la obligatoriedad de supervision tecnica para casas de uno y dos pisos del Titulo E, segun el Titulo I?",
        "ground_truth": "Se excluyen de la supervisión técnica obligatoria las estructuras del Título E cuando sean menos de 15 unidades de vivienda.",
        "id": "I-excepcion-titulo-E-15viviendas",
    },
    {
        "pregunta": "Durante cuantos años minimo debe conservar el supervisor tecnico el registro escrito de sus labores segun el Titulo I?",
        "ground_truth": "El supervisor técnico debe conservar el registro escrito de sus labores durante al menos 5 años.",
        "id": "I-registro-supervisor-5anos",
    },
    {
        "pregunta": "Cuales son los dos grados de supervision tecnica que reconoce el Titulo I?",
        "ground_truth": "Los dos grados de supervisión técnica son Grado A (Continua) y Grado B (Itinerante).",
        "id": "I-dos-grados-supervision-AB",
    },
    # ---- Título B, ampliación ----
    {
        "pregunta": "Cual es el porcentaje de incremento de carga viva por impacto para los soportes de elevadores o ascensores segun el Titulo B?",
        "ground_truth": "El incremento de carga viva por impacto para soportes de elevadores o ascensores es del 100%.",
        "id": "B-impacto-ascensores-100porciento",
    },
    {
        "pregunta": "Cual es el valor del factor de efecto rafaga G para estructuras rigidas segun el Titulo B?",
        "ground_truth": "El factor de efecto ráfaga G para estructuras rígidas se toma como 0.85.",
        "id": "B-factor-rafaga-G085",
    },
    # ---- NTC (ICONTEC) y SGSST (Decreto 1072 de 2015) ----
    {
        "pregunta": "Se pueden instalar las instalaciones hidraulicas y sanitarias en la caja del ascensor o el cuarto de maquinas segun la NTC 1500?",
        "ground_truth": "No, las instalaciones hidráulicas y sanitarias no deben instalarse en la caja del ascensor ni en el cuarto de máquinas.",
        "id": "NTC1500-instalaciones-prohibidas-ascensor",
    },
    {
        "pregunta": "Entre que valores debe estar el modulo de finura del agregado fino para concreto segun la NTC 174?",
        "ground_truth": "El módulo de finura del agregado fino debe ser mayor que 2.3 pero menor que 3.1.",
        "id": "NTC174-modulo-finura-23-31",
    },
    {
        "pregunta": "Cual es el tiempo minimo de fraguado inicial del cemento Portland segun la NTC 121?",
        "ground_truth": "El fraguado inicial del cemento Portland debe ser mayor o igual a 45 minutos.",
        "id": "NTC121-fraguado-inicial-45min",
    },
    {
        "pregunta": "Cual es la multa maxima en SMMLV por no reportar un accidente de trabajo grave o mortal segun el Decreto 1072 de 2015?",
        "ground_truth": "No reportar un accidente de trabajo grave o mortal tiene una multa máxima de 1000 SMMLV.",
        "id": "Decreto1072-multa-no-reportar-AT-1000SMMLV",
    },
    {
        "pregunta": "En cuantos meses debe completar la Fase 3 de implementacion del SG-SST una empresa grande de mas de 200 trabajadores segun el Decreto 1072 de 2015?",
        "ground_truth": "Una empresa grande (más de 200 trabajadores) debe completar la Fase 3 del SG-SST en 6 meses.",
        "id": "Decreto1072-fase3-empresa-grande-6meses",
    },
    {
        "pregunta": "Cual es el porcentaje maximo de terrones de arcilla y particulas deleznables permitido en el agregado fino para concreto segun la NTC 174?",
        "ground_truth": "El límite máximo de terrones de arcilla y partículas deleznables en el agregado fino es 3.0%.",
        "id": "NTC174-terrones-arcilla-max-3porciento",
    },
    {
        "pregunta": "Cual es la expansion maxima en autoclave permitida para el cemento Portland segun la NTC 121?",
        "ground_truth": "La expansión en autoclave no debe exceder el 0.80% para el cemento Portland.",
        "id": "NTC121-expansion-autoclave-08porciento",
    },
    # ---- Título K, ampliación (K.4.1 — glosario de vidrios) ----
    {
        "pregunta": "Que le pasa al vidrio templado (fully tempered) cuando se rompe, segun el Titulo K?",
        "ground_truth": "El vidrio templado, al romperse en cualquier punto, se fragmenta entero en pequeños pedazos con bordes relativamente romos.",
        "id": "K-vidrio-templado-fragmenta-pequeños-pedazos",
    },
    {
        "pregunta": "A partir de que angulo respecto a la vertical se considera un vidrio como tragaluz o claraboya segun el Titulo K?",
        "ground_truth": "Se considera tragaluz o claraboya el vidrio plano instalado en un ángulo mayor a 15° de la vertical en el exterior de un edificio.",
        "id": "K-tragaluz-angulo-15grados",
    },
    {
        "pregunta": "Cual es la diferencia entre vidrio templado y vidrio termoendurecido segun el Titulo K?",
        "ground_truth": "El vidrio templado se trata térmicamente hasta lograr una compresión alta en la superficie o el borde; el termoendurecido logra solo una compresión moderada.",
        "id": "K-templado-vs-termoendurecido-compresion",
    },
    # ---- Título K, ampliación (K.4.2 — requisitos de diseño de vidrios) ----
    {
        "pregunta": "Cual es el factor de seguridad exigido para el diseño de barandas y pasamanos de vidrio segun el Titulo K?",
        "ground_truth": "Los paneles para barandas y pasamanos de vidrio se deben diseñar con un factor de seguridad igual a cuatro (4).",
        "id": "K-barandas-vidrio-factor-seguridad-4",
    },
    {
        "pregunta": "Se permite usar vidrios de 2 mm de espesor segun el Titulo K?",
        "ground_truth": "No, se prohíbe el uso de vidrios de 2 mm debido a su excesiva flexibilidad.",
        "id": "K-vidrio-2mm-prohibido",
    },
    {
        "pregunta": "Cual es el limite recomendado de probabilidad de rotura aceptable por esfuerzos termicos en vidrio segun el Titulo K?",
        "ground_truth": "Es recomendable que la probabilidad de rotura aceptable por esfuerzos térmicos no sea superior al 0.8%.",
        "id": "K-esfuerzos-termicos-probabilidad-rotura-08porciento",
    },
    {
        "pregunta": "A partir de que inclinacion respecto a la vertical se considera un sistema vidriado como inclinado (no vertical) segun el Titulo K?",
        "ground_truth": "Un sistema vidriado se considera inclinado cuando tiene una inclinación de más de 15° con respecto a la vertical.",
        "id": "K-vidrio-inclinado-mas-de-15grados",
    },
    {
        "pregunta": "Cuales son los factores de resistencia phi minimos para miembros y para conexiones en un analisis racional de ingenieria de acero formado en frio segun el Titulo F?",
        "ground_truth": "Para miembros, φ = 0.80. Para conexiones, φ = 0.65.",
        "id": "F-analisis-racional-phi-miembros-080-conexiones-065",
    },
    {
        "pregunta": "Cual es el espesor minimo entregado permitido para acero formado en frio respecto al espesor de diseño segun el Titulo F?",
        "ground_truth": "El espesor mínimo de acero sin revestimiento, del producto formado en frío tal como se entrega a la obra, no debe ser en ningún punto menor que el 95% del espesor usado en su diseño.",
        "id": "F-espesor-minimo-entregado-95porciento",
    },
    {
        "pregunta": "Hasta que espesor de lamina, rollo, tira o barra aplica la especificacion de estructuras de acero con perfiles formados en frio del Titulo F?",
        "ground_truth": "Aplica a miembros estructurales de acero de bajo carbono o de baja aleación, cuya sección ha sido formada en frío, a partir de láminas, rollos, tiras, platinas o barras de espesor menor o igual a 25.4 mm (1 pulgada).",
        "id": "F-f41-alcance-espesor-maximo-254mm",
    },
    {
        "pregunta": "Cual es la maxima relacion ancho plano-espesor w/t para un elemento a compresion rigidizado con ambos bordes longitudinales conectados a otros elementos rigidizados segun el Titulo F?",
        "ground_truth": "Para un elemento a compresión rigidizado con ambos bordes longitudinales conectados a otros elementos rigidizados, w/t ≤ 500.",
        "id": "F-f42-max-wt-elemento-rigidizado-ambos-bordes-500",
    },
    {
        "pregunta": "Cual es la relacion maxima altura-espesor h/t para almas no reforzadas de miembros en flexion de acero formado en frio segun el Titulo F?",
        "ground_truth": "Para almas no reforzadas, (h/t)máx = 200.",
        "id": "F-f42-max-ht-almas-no-reforzadas-200",
    },
    {
        "pregunta": "Que coeficiente de pandeo de placa k se usa para elementos NO rigidizados bajo compresion uniforme segun el Titulo F?",
        "ground_truth": "El ancho efectivo se determina igual que para elementos rigidizados, excepto que el coeficiente de pandeo de placa k se toma como 0.43.",
        "id": "F-f42-k-elemento-no-rigidizado-043",
    },
    {
        "pregunta": "Cual es el coeficiente kv de pandeo al corte para almas no reforzadas de acero formado en frio segun el Titulo F?",
        "ground_truth": "Para almas no reforzadas, kv = 5.34.",
        "id": "F-f43-kv-almas-no-reforzadas-534",
    },
    {
        "pregunta": "Cual es el factor de resistencia phi para fluencia en la seccion bruta de un miembro en tension de acero formado en frio segun el Titulo F?",
        "ground_truth": "Para fluencia en la sección bruta, Tn = Ag·Fy, con φt = 0.90.",
        "id": "F-f43-phi-tension-fluencia-seccion-bruta-090",
    },
    {
        "pregunta": "Cual es el factor de resistencia phi para rotura en la seccion neta de un miembro en tension de acero formado en frio segun el Titulo F?",
        "ground_truth": "Para rotura en la sección neta lejos de la conexión, Tn = An·Fu, con φt = 0.75.",
        "id": "F-f43-phi-tension-rotura-seccion-neta-075",
    },
    {
        "pregunta": "Cual es el rango de espesor minimo especificado del acero base permitido para entramados livianos repetitivos de acero formado en frio segun el Titulo F?",
        "ground_truth": "El espesor mínimo especificado del acero base debe estar entre 0.455 mm y 2.997 mm.",
        "id": "F-f44-espesor-entramados-livianos-0455-2997",
    },
    {
        "pregunta": "Cual es la resistencia nominal requerida de la riostra para restringir la traslacion lateral de un miembro sencillo en compresion axialmente cargado segun el Titulo F?",
        "ground_truth": "Pbr,1 = 0.01·Pn, es decir, el 1% de la resistencia nominal bajo compresión axial del miembro.",
        "id": "F-f44-pbr1-riostra-compresion-001pn",
    },
    {
        "pregunta": "Cual es el diametro efectivo minimo de fusion permitido para una soldadura de tapon en conexiones de acero formado en frio segun el Titulo F?",
        "ground_truth": "Las soldaduras de tapón deben especificarse con un diámetro efectivo de área de fusión mínimo que no puede ser menor a 9.5 mm.",
        "id": "F-f45-tapon-diametro-efectivo-minimo-95mm",
    },
    {
        "pregunta": "Cual es la distancia minima entre centros de perforaciones para pernos en conexiones de acero formado en frio segun el Titulo F?",
        "ground_truth": "La distancia mínima entre centros de perforaciones no debe ser menor a 3 veces el diámetro nominal del perno, d.",
        "id": "F-f45-pernos-distancia-minima-3d",
    },
    {
        "pregunta": "Como se calcula la resistencia nominal al desgarramiento del tornillo Pnot en conexiones atornilladas de acero formado en frio segun el Titulo F?",
        "ground_truth": "Pnot = 0.85·tc·d·Fu2, donde tc es el menor valor entre la profundidad de penetración y el espesor t2, d es el diámetro nominal del tornillo y Fu2 es la resistencia última del miembro que no está en contacto con la cabeza del tornillo o la arandela.",
        "id": "F-f45-cierre-pnot-desgarramiento-tornillo-085",
    },
    {
        "pregunta": "Que ecuaciones se usan para la rotura por bloque de cortante en conexiones de lamina delgada de acero segun el Titulo F?",
        "ground_truth": "Rn se determina como el menor valor entre Rn = 0.6·Fy·Agv + Fu·Ant (F.4.5.5-3) y Rn = 0.6·Fu·Anv + Fu·Ant (F.4.5.5-4), aplicable cuando el espesor de la parte conectada más delgada es menor a 4.76 mm (φ=0.65 para conexiones pernadas, φ=0.60 para soldadas).",
        "id": "F-f45-cierre-bloque-cortante-476mm",
    },
    {
        "pregunta": "Que requisitos aplican para las conexiones de acero formado en frio con componentes estructurales de otros materiales segun el Titulo F?",
        "ground_truth": "Deben proveerse mecanismos de transferencia de cargas de apoyo (F.4.5.6.1), considerar el cortante de arrancamiento y desgarramiento del sujetador por tensión con resistencia de anclaje determinada por normas del producto o ensayo (F.4.5.6.2), y proveerse mecanismos de transferencia de fuerzas cortantes sin exceder los valores permitidos por el Reglamento (F.4.5.6.3).",
        "id": "F-f45-cierre-conexiones-otros-materiales",
    },
    {
        "pregunta": "Que norma tecnica colombiana rige los procedimientos de la prueba a tension para determinar propiedades mecanicas de secciones completas de acero formado en frio segun el Titulo F?",
        "ground_truth": "La norma NTC 3353 (equivalente a ASTM A370-05), según la sección F.4.6.3.1.",
        "id": "F-f46-ntc3353-prueba-tension-seccion-completa",
    },
    {
        "pregunta": "Cuantos especimenes a tension minimo se deben tomar de cada rollo madre para establecer los valores representativos de acero virgen segun el Titulo F?",
        "ground_truth": "Al menos cuatro especímenes a tensión de cada rollo madre, tomados longitudinalmente a una distancia del borde externo del rollo igual a la cuarta parte del ancho (F.4.6.3.3).",
        "id": "F-f46-acero-virgen-cuatro-especimenes",
    },
    {
        "pregunta": "Cuantos especimenes identicos minimo se requieren en un ensayo de comportamiento estructural DCCR y cual es la desviacion maxima permitida respecto al promedio segun el Titulo F?",
        "ground_truth": "No menos de tres especímenes idénticos, siempre que la desviación entre el resultado de cualquier ensayo individual y el promedio no exceda ±15% (F.4.6.1.1(a)).",
        "id": "F-f46-dccr-tres-especimenes-15pct",
    },
    {
        "pregunta": "Cuantos milimetros de recubrimiento minimo de concreto se requieren sobre la cresta del tablero de acero de un sistema compuesto segun el Titulo F?",
        "ground_truth": "50 mm sobre la cresta del tablero metálico; cuando se requiere refuerzo adicional para momento negativo, el recubrimiento mínimo sobre esas barras es de 20 mm (F.4.7.5.3.1).",
        "id": "F-f47-recubrimiento-minimo-50mm",
    },
    {
        "pregunta": "Cual es el espesor minimo de acero base aceptado para fabricacion del tablero metalico de trabajo en seccion compuesta segun el Titulo F?",
        "ground_truth": "Un espesor de acero base de 0.71 mm (tipo o calibre 22), según la sección F.4.7.2 y la Tabla F.4.7.2-2.",
        "id": "F-f47-espesor-minimo-071mm-calibre22",
    },
    {
        "pregunta": "El apuntalamiento temporal de un tablero metalico debe permanecer instalado hasta que el concreto alcance que porcentaje de su resistencia y por cuantos dias minimo segun el Titulo F?",
        "ground_truth": "Hasta que el concreto alcance el 75% de su resistencia especificada a compresión y durante un mínimo de 7 días (F.4.7.6.1).",
        "id": "F-f47-apuntalamiento-75pct-7dias",
    },
    {
        "pregunta": "Cual es el rango de espesor minimo del acero permitido para entramados de acero formado en frio segun el Titulo F?",
        "ground_truth": "Entre 0.46 mm y 3.00 mm, según la sección F.4.8.1.",
        "id": "F-f48-espesor-046-300mm",
    },
    {
        "pregunta": "Cual es el espaciamiento minimo centro a centro requerido entre perforaciones de un miembro de entramado de acero formado en frio segun el Titulo F?",
        "ground_truth": "No menor a 600 mm, salvo que el fabricante especifique otras condiciones distintas (F.4.8.3.5).",
        "id": "F-f48-perforaciones-espaciamiento-600mm",
    },
    {
        "pregunta": "Cual es la carga nominal axial maxima por paral cuando se usa tablero de yeso de 12.7mm con tornillo No 6 segun el Titulo F?",
        "ground_truth": "25.8 kN, según la Tabla F.4.8.4-1.",
        "id": "F-f48-carga-axial-tablero-yeso-258kn",
    },
    {
        "pregunta": "En el capitulo F.5 de estructuras de aluminio del Titulo F, en que sistema de unidades estan expresadas las fuerzas y los esfuerzos?",
        "ground_truth": "En kgf (fuerzas) y kgf/mm² (esfuerzos) — no en el sistema internacional SI —, según la sección F.5.1.1.",
        "id": "F-f51-sistema-unidades-kgf",
    },
    {
        "pregunta": "Que tipos de estructuras cubren los requisitos de diseno del capitulo de estructuras de aluminio de la NSR-10?",
        "ground_truth": "Estructuras aporticadas, en celosía y de lámina rigidizada, con elementos extruídos o laminados, para aplicaciones como puentes, edificios, torres, vehículos de carretera y sobre rieles, naves marinas, grúas y estructuras sobre cubierta ubicadas mar adentro (F.5.1.1).",
        "id": "F-f51-alcance-tipos-estructuras",
    },
    {
        "pregunta": "Cual es el esfuerzo minimo de prueba del 0.2 por ciento en kgf por milimetro cuadrado para la aleacion de aluminio 6082 en condicion T6 extrusiones hasta 20mm segun el Titulo F?",
        "ground_truth": "25.5 kgf/mm², según la Tabla F.5.2.2-1.",
        "id": "F-f52-6082-t6-esfuerzo-255kgf",
    },
    {
        "pregunta": "Que nivel de proteccion contra la corrosion requiere el aluminio de durabilidad A sumergido en agua salada segun el Titulo F?",
        "ground_truth": "Requiere protección (P), según la Tabla F.5.2.4-1 — a diferencia de agua dulce, donde no se requiere protección para durabilidad A.",
        "id": "F-f52-durabilidad-a-agua-salada-proteccion",
    },
    {
        "pregunta": "Cual es la deflexion limite recomendada para voladizos que soportan pisos en estructuras de aluminio segun el Titulo F?",
        "ground_truth": "L/180, según la Tabla F.5.3.4-1.",
        "id": "F-f53-deflexion-voladizo-L180",
    },
    {
        "pregunta": "Cual es el coeficiente de reduccion de capacidad phi para uniones soldadas en estructuras de aluminio segun el Titulo F?",
        "ground_truth": "0.80, según la Tabla F.5.3.3-1 (debe usarse 0.70 en procedimientos que no cumplan las especificaciones de aprobación de soldadura TIG/MIG como la BS4870 Parte 2).",
        "id": "F-f53-phi-union-soldada",
    },
    {
        "pregunta": "En el diseno de estructuras de aluminio del Titulo F, cuando se revisa fatiga se deben considerar colapso total y crecimiento estable de grietas, cual es la tolerancia de dano?",
        "ground_truth": "El crecimiento estable de grietas se determina monitoreando la tasa de crecimiento de las grietas de fatiga en inspecciones regulares, acordando con el cliente los métodos de inspección, longitudes límite y tasas admisibles de crecimiento (F.5.3.6.3).",
        "id": "F-f53-fatiga-crecimiento-grietas",
    },
    {
        "pregunta": "Cual es el esfuerzo limite po para aluminio 6061-T6 en extrusion segun la NSR-10 Titulo F.5.4?",
        "ground_truth": "24 kgf/mm², para espesores hasta 150 mm, según la Tabla F.5.4.2-1.",
        "id": "F-f541-2-esfuerzo-limite-po-6061-t6",
    },
    {
        "pregunta": "En estructuras de aluminio del Titulo F.5 de la NSR-10, que significa que en una seccion clasificada como totalmente compacta el pandeo local puede ignorarse?",
        "ground_truth": "Significa que la sección puede desarrollar su resistencia plástica total (momento igual a po veces el módulo elástico, o mayor) sin que el pandeo local premature de los elementos de pared delgada reduzca su capacidad (F.5.4.3.3).",
        "id": "F-f543-totalmente-compacta-pandeo-local",
    },
    {
        "pregunta": "Cual es el valor limite de beta0 para elementos salientes de aluminio no soldados segun la tabla de valores limite de beta de la NSR-10 Titulo F.5?",
        "ground_truth": "β0 = 7ε, según la Tabla F.5.4.3-1 (elementos internos no soldados: β0 = 22ε).",
        "id": "F-f543-beta0-elementos-salientes-no-soldados",
    },
    {
        "pregunta": "Segun la Tabla F.5.4.4-1 de coeficiente de ablandamiento kz de la NSR-10 Titulo F.5, cual es el valor de kz para la aleacion 6061 tratada en caliente T6 en extrusion o tuberia extruida?",
        "ground_truth": "kz = 0.50, tanto para extrusión (E) como para tubería extruída (DT), según la Tabla F.5.4.4-1.",
        "id": "F-f544-kz-6061-t6",
    },
    {
        "pregunta": "Cual es el tiempo de recuperacion en dias para aleaciones de aluminio de la serie 7000 despues de soldar antes de aplicar el coeficiente kz segun el Titulo F.5?",
        "ground_truth": "30 días, siempre que el material se mantenga a una temperatura no menor de 15°C (F.5.4.4.2(c); la serie 6*** requiere solo 3 días).",
        "id": "F-f544-tiempo-recuperacion-serie-7000",
    },
    {
        "pregunta": "En estructuras de aluminio del Titulo F.5, cual es el valor de eta cuando una union tiene un solo camino de calor valido y el espesor tc es menor o igual a 25mm?",
        "ground_truth": "η = 1.50 (para tc > 25mm, η = 1.33), según F.5.4.4.3(e)(2).",
        "id": "F-f544-eta-un-camino-calor-tc25",
    },
    {
        "pregunta": "Cual es el espaciamiento maximo de soporte lateral para poder ignorar el pandeo torsional lateral en vigas de aluminio del Titulo F.5?",
        "ground_truth": "40εry (ε=(25/po)^0.5, ry = radio de giro del eje menor), según F.5.4.5.6.",
        "id": "F-f545-espaciamiento-40epsilon-ry",
    },
    {
        "pregunta": "Segun el Titulo F.5 de aluminio, cual es el porcentaje de la fuerza de compresion en la aleta que deben resistir las restricciones laterales de una viga?",
        "ground_truth": "3% de la compresión en la aleta, según F.5.4.5.6(e).",
        "id": "F-f545-restricciones-laterales-3-porciento",
    },
    {
        "pregunta": "En el Titulo F.5 de aluminio, que numeral se recomienda usar preferiblemente para disenar vigas ensambladas que tienen almas rigidizadas mas esbeltas?",
        "ground_truth": "F.5.5.4 (según F.5.4.5.1); la cláusula específica de rigidizador de viga ensamblada es F.5.5.4.4.",
        "id": "F-f545-vigas-ensambladas-f5541",
    },
    {
        "pregunta": "Segun el Titulo F.5 de aluminio, cual es la reduccion de area que se resta para un componente unico conectado por un lado a una cartela en un tirante conectado excentricamente?",
        "ground_truth": "0.6Ao (donde Ao es el área efectiva del lado o lados salientes del elemento conectado, ignorando cualquier filete), según F.5.4.6.2(1). Para un componente doble simétricamente conectado a cada lado de una cartela es 0.2Ao.",
        "id": "F-f546-tirante-excentrico-06ao",
    },
    {
        "pregunta": "En estructuras de aluminio del Titulo F.5, cuales son los tres tipos de miembros a tension considerados como conectados excentricamente segun F.5.4.6.2?",
        "ground_truth": "Ángulos conectados únicamente por una aleta, canales conectados por el alma, y secciones T conectadas por la aleta.",
        "id": "F-f546-tres-tipos-conexion-excentrica",
    },
    {
        "pregunta": "Segun el Titulo F.5 de aluminio, la resistencia a tension de diseno PRS de un miembro se toma como el menor de cuales dos valores?",
        "ground_truth": "El menor entre fluencia general a lo largo del miembro y falla local en una sección crítica, según F.5.4.6.1.",
        "id": "F-f546-prs-menor-fluencia-falla-local",
    },
    # ==== AMPLIACIÓN 2026-09-07: preguntas complejas (ver docstring) ====
    # ---- Síntesis cruzada entre títulos (ambos hechos ya verificados por
    # separado arriba -- la pregunta nueva obliga a combinarlos) ----
    {
        "pregunta": "Barranquilla tiene Aa=0.10 segun la NSR-10. Podria usarse mamposteria no reforzada como sistema de resistencia sismica en Barranquilla segun el Titulo D?",
        "ground_truth": "No, porque el Título D solo permite mampostería no reforzada como sistema de resistencia sísmica en zonas con Aa menor o igual a 0.05, y Barranquilla tiene Aa = 0.10.",
        "id": "SINT-barranquilla-Aa010-vs-mamposteria-no-reforzada-D",
    },
    {
        "pregunta": "Es mayor la resistencia minima que exige el Titulo C para el concreto estructural que la que exige el Titulo D para el mortero de relleno de mamposteria?",
        "ground_truth": "Sí: el Título C exige mínimo 17 MPa para el concreto estructural, mayor que los 12.5 MPa mínimos que exige el Título D para el mortero de relleno.",
        "id": "SINT-fc-concreto-C-vs-mortero-relleno-D",
    },
    {
        "pregunta": "Es mucho mayor la resistencia minima del concreto para estructuras DES o DMO del Titulo C que la del mortero de pega en casas de uno y dos pisos del Titulo E?",
        "ground_truth": "Sí: el Título C exige mínimo 21 MPa para concreto DES/DMO, casi el triple de los 7.5 MPa mínimos que exige el Título E para el mortero de pega en casas de uno y dos pisos.",
        "id": "SINT-fc-DES-DMO-C-vs-mortero-pega-E",
    },
    {
        "pregunta": "Es igual el factor de reduccion de resistencia phi para secciones controladas por traccion en concreto del Titulo C que el factor phi para miembros en un analisis racional de acero formado en frio del Titulo F?",
        "ground_truth": "No: el Título C usa φ=0.90 para secciones controladas por tracción en concreto, mientras que el Título F usa φ=0.80 para miembros en un análisis racional de acero formado en frío.",
        "id": "SINT-phi-traccion-C-vs-phi-miembros-F",
    },
    {
        "pregunta": "Es mas exigente el Titulo D con la resistencia del mortero de relleno que el Titulo E con la resistencia del mortero de pega en mamposteria confinada?",
        "ground_truth": "Sí: el Título D exige mínimo 12.5 MPa para el mortero de relleno, más que los 7.5 MPa mínimos que exige el Título E para el mortero de pega en mampostería confinada.",
        "id": "SINT-mortero-relleno-D-vs-mortero-pega-E",
    },
    {
        "pregunta": "Es el mismo numero de anos el que exige el Titulo H de experiencia minima a un geotecnista que el numero de anos que el Titulo I exige conservar el registro de un supervisor tecnico?",
        "ground_truth": "Sí, coincide el número (5 años) pero se refieren a cosas distintas: el Título H exige más de 5 años de experiencia en diseño geotécnico, y el Título I exige conservar el registro del supervisor durante al menos 5 años.",
        "id": "SINT-5anos-geotecnista-H-vs-registro-supervisor-I",
    },
    {
        "pregunta": "El caudal minimo de un hidrante para un hospital lo regula el mismo titulo de la NSR-10 que la fuerza maxima para abrir una puerta de salida?",
        "ground_truth": "No: el caudal mínimo de hidrantes (63 L/s para hospitales) lo regula el Título J, mientras que la fuerza máxima de apertura de puertas de salida (menor a 250 N) la regula el Título K.",
        "id": "SINT-hidrante-J-vs-fuerza-puerta-K",
    },
    {
        "pregunta": "Se definen los 4 sistemas estructurales de resistencia sismica en el mismo titulo de la NSR-10 que trata la carga de viento?",
        "ground_truth": "No: los 4 sistemas estructurales de resistencia sísmica (muros de carga, combinado, pórtico, dual) se definen en el Título A, mientras que la carga de viento se trata en el Título B.",
        "id": "SINT-sistemas-sismicos-A-vs-viento-B",
    },
    {
        "pregunta": "Regulan el mismo material estructural el Titulo D y el Titulo G de la NSR-10?",
        "ground_truth": "No: el Título D regula mampostería estructural, mientras que el Título G regula madera y guadua — son materiales y títulos distintos.",
        "id": "SINT-material-D-vs-G",
    },
    {
        "pregunta": "Aplican las mismas reglas de conexion el Titulo F para acero que el Titulo G para guadua?",
        "ground_truth": "No: son títulos de materiales distintos con reglas propias de conexión — por ejemplo, el Título G prohíbe las uniones clavadas en guadua, una restricción que no aplica al acero del Título F.",
        "id": "SINT-conexiones-F-vs-G",
    },
    {
        "pregunta": "El recubrimiento minimo del concreto contra el suelo lo regula el mismo titulo de la NSR-10 que los requisitos de vidrio en barandas?",
        "ground_truth": "No: el recubrimiento mínimo del concreto contra el suelo (75 mm) lo regula el Título C, mientras que los requisitos de vidrio en barandas (factor de seguridad 4) los regula el Título K.",
        "id": "SINT-recubrimiento-C-vs-vidrio-barandas-K",
    },
    {
        "pregunta": "Es mas alta la resistencia minima del concreto estructural del Titulo C que el limite de fraguado inicial del cemento Portland de la NTC 121?",
        "ground_truth": "No son comparables directamente (17 MPa es una resistencia a la compresión, 45 minutos es un tiempo de fraguado) — el Título C regula la resistencia del concreto y la NTC 121 regula el tiempo mínimo de fraguado inicial del cemento, son propiedades distintas del mismo material.",
        "id": "SINT-fc-concreto-C-vs-fraguado-NTC121",
    },
    # ---- Preguntas compuestas precio+norma (primera cobertura real de
    # _ask_delegado_compuesto() -- combinan un hecho normativo ya verificado
    # arriba con un precio real de scripts/evaluacion/dataset_baseline_precios.py) ----
    {
        "pregunta": "Cual es la resistencia minima a la compresion f'c que exige la NSR-10 para el concreto estructural, y cuanto cuesta el kilo de acero corrugado figurado de 1/4 a 1 pulgada en Barranquilla?",
        "ground_truth": "El f'c mínimo es 17 MPa (Título C); el acero corrugado figurado 1/4\"-1\" de 60.000 PSI cuesta $2.617,87 COP por kg en Barranquilla.",
        "id": "COMP-fc-minimo-y-acero-corrugado",
    },
    {
        "pregunta": "Cuantos pies tablares tiene un metro cubico de madera segun el Titulo G, y cuanto cuesta el metro cubico de arena de rio en Barranquilla?",
        "ground_truth": "Un metro cúbico de madera tiene 424 pies tablares (Título G); la arena de río cuesta $70.000 COP por m³ en Barranquilla.",
        "id": "COMP-pies-tablares-y-arena-rio",
    },
    {
        "pregunta": "Cual es el recubrimiento minimo del concreto cuando esta en contacto permanente con el suelo, y cuanto cuesta un bloque de concreto de 20x20x40 en Barranquilla?",
        "ground_truth": "El recubrimiento mínimo es 75 mm (Título C); el bloque de concreto 20x20x40 cuesta $2.050,04 COP por unidad en Barranquilla.",
        "id": "COMP-recubrimiento-y-bloque-concreto",
    },
    {
        "pregunta": "Cual es la deriva maxima permitida para una estructura de concreto reforzado, y cuanto cuesta el saco de cemento Argos gris de 50kg en Homecenter?",
        "ground_truth": "La deriva máxima es 1.0% de la altura de piso (Título A); el saco de cemento Argos gris de 50kg cuesta $32.500 COP en Homecenter Colombia.",
        "id": "COMP-deriva-maxima-y-cemento-argos",
    },
    {
        "pregunta": "Cual es el angulo de doblez de los ganchos sismicos en estribos de confinamiento, y cuanto vale la hora de un ayudante de albañileria en Barranquilla?",
        "ground_truth": "El ángulo es 135 grados (Título C, estructuras DMO/DES); la hora de ayudante de albañilería cuesta $2.461 COP en Barranquilla.",
        "id": "COMP-ganchos-sismicos-y-ayudante",
    },
    {
        "pregunta": "Cual es la resistencia minima del mortero de relleno en mamposteria segun el Titulo D, y cuanto cuesta el metro cuadrado de baldosa Alfa L1 de 33x33?",
        "ground_truth": "El mortero de relleno nunca puede ser inferior a 12.5 MPa (Título D); la baldosa Alfa L1 33x33 cuesta $30.160,19 COP por m².",
        "id": "COMP-mortero-relleno-y-baldosa",
    },
    {
        "pregunta": "A partir de que area construida es obligatoria la supervision tecnica en mamposteria segun el Titulo D, y cual es el mejor precio nacional de un codo de acero galvanizado de 1 1/4 pulgada?",
        "ground_truth": "Es obligatoria por encima de 3.000 m² de área construida (Título D); el mejor precio nacional del codo de 90° en acero galvanizado de 1 1/4\" es $5.000 COP con Ferretería Nicholson, comparado entre 60 proveedores mipyme reales.",
        "id": "COMP-supervision-mamposteria-y-codo-galvanizado",
    },
    {
        "pregunta": "Cual es la fuerza maxima requerida para abrir completamente una puerta de salida segun el Titulo K, y cuanto cuesta un candado estandar de 30mm en Ferreteria Samir?",
        "ground_truth": "La fuerza máxima es menor a 250 N (Título K); el candado estándar de 30mm cuesta $43.366 COP en Ferretería Samir, Barranquilla.",
        "id": "COMP-fuerza-puerta-y-candado",
    },
    # ---- Fraseo coloquial de campo (reformulaciones informales de hechos ya
    # verificados arriba -- mide si REGISTRO cambia el resultado, no solo la
    # redacción) ----
    {
        "pregunta": "Los ganchos de los flejes en una columna sismica se doblan a 90 grados o mas cerrados?",
        "ground_truth": "Se doblan a 135 grados según el Título C (para estructuras DMO y DES) — más cerrado que un ángulo recto de 90 grados.",
        "id": "COLOQ-ganchos-flejes-columna",
    },
    {
        "pregunta": "Si el concreto va pegado a la tierra todo el tiempo, cuanto de recubrimiento le tengo que dejar a la varilla?",
        "ground_truth": "75 mm, según el Título C, cuando el concreto está en contacto permanente con el suelo.",
        "id": "COLOQ-recubrimiento-varilla-tierra",
    },
    {
        "pregunta": "De que resistencia minima tiene que ser el concreto de una estructura, la mas floja que se permite?",
        "ground_truth": "17 MPa, la resistencia mínima a la compresión que exige el Título C para el concreto estructural.",
        "id": "COLOQ-resistencia-concreto-floja",
    },
    {
        "pregunta": "Cuanto se puede ladear un piso de un edificio de concreto sin que sea un problema, segun la norma?",
        "ground_truth": "1.0% de la altura del piso, la deriva máxima permitida para estructuras de concreto reforzado según el Título A.",
        "id": "COLOQ-ladeo-piso-concreto",
    },
    {
        "pregunta": "Que tan humeda puede estar la madera que se usa para la estructura del techo?",
        "ground_truth": "Máximo 19% de humedad para madera estructural en general, o 12% si es madera laminada, según el Título G.",
        "id": "COLOQ-humedad-madera-techo",
    },
    {
        "pregunta": "Se le puede meter clavo a la guadua para unir dos piezas?",
        "ground_truth": "No, las uniones clavadas están prohibidas en guadua porque los clavos inducen grietas longitudinales, según el Título G.",
        "id": "COLOQ-clavo-guadua",
    },
    {
        "pregunta": "Que tan dura puede estar una puerta de emergencia para que la gente la pueda abrir sin problema?",
        "ground_truth": "La fuerza requerida para abrirla completamente debe ser menor a 250 N, según el Título K.",
        "id": "COLOQ-dureza-puerta-emergencia",
    },
    {
        "pregunta": "Desde que tamano de obra en mamposteria toca contratar un supervisor tecnico si o si?",
        "ground_truth": "A partir de 3.000 m² de área construida, según el Título D.",
        "id": "COLOQ-tamano-obra-supervisor",
    },
    {
        "pregunta": "Que tan gruesa tiene que ser minimo una columna de confinamiento en un muro de mamposteria confinada?",
        "ground_truth": "El área transversal mínima es 20.000 mm² (200 cm²), según el Título E.",
        "id": "COLOQ-columna-confinamiento-gruesa",
    },
    {
        "pregunta": "Cuales son las formas en que se puede armar la estructura de un edificio para que aguante un temblor, segun la norma?",
        "ground_truth": "Los 4 sistemas estructurales de resistencia sísmica que reconoce la NSR-10 son: muros de carga, combinado, pórtico y sistema dual (Título A).",
        "id": "COLOQ-formas-estructura-temblor",
    },
    # ---- Título H, ampliación H.3.3 (cierre) + H.4 completo (Cimentaciones) ----
    # Ingesta verbatim 2026-09-07, primera pieza tras la auditoría numeral por
    # numeral que confirmó que Título H solo cubría H.1-H.3.2 (~18%). Mismas
    # 2 preguntas verificadas PASSED de test_rag_nsr10_regresion.py -- otras
    # 2 probadas no pasaron (retrieval y una confusión de fila de tabla en
    # generación, ver memoria privada) y se dejaron fuera a propósito.
    {
        "pregunta": "Cual es el asentamiento maximo permitido a 20 anos para construcciones aisladas segun el Titulo H de la NSR-10?",
        "ground_truth": "El asentamiento total calculado a 20 años para construcciones aisladas se limita a 30 cm, siempre que no se afecte la funcionalidad de conducciones de servicios ni el acceso a la construcción.",
        "id": "H-asentamiento-maximo-aisladas-30cm",
    },
    {
        "pregunta": "Cuales son los factores de seguridad indirectos minimos para cimentaciones bajo carga muerta mas carga viva normal segun el Titulo H?",
        "ground_truth": "El factor de seguridad indirecto mínimo F_SICP para cimentaciones bajo carga muerta más carga viva normal es 3.0.",
        "id": "H-fsicp-carga-muerta-viva-normal-30",
    },
    # ---- Título H, ampliación H.5 completo (Excavaciones y estabilidad de taludes) ----
    {
        "pregunta": "Cual es la sobrecarga uniforme minima a considerar en la via publica y zonas proximas a excavaciones temporales segun el Titulo H?",
        "ground_truth": "La sobrecarga uniforme mínima a considerar en la vía pública y zonas libres próximas a excavaciones temporales es 15 kPa (1.5 t/m²).",
        "id": "H-sobrecarga-minima-excavaciones-15kpa",
    },
    {
        "pregunta": "En cuanto tiempo puede reducirse la cohesion de los materiales arcillosos en taludes de excavacion segun el Titulo H?",
        "ground_truth": "La cohesión de los materiales arcillosos tiende a disminuir con el tiempo, en una proporción que puede alcanzar 30% en un plazo de un mes.",
        "id": "H-cohesion-arcillas-30porciento-1mes",
    },
    {
        "pregunta": "Cual es el valor minimo de KST sobre amax para macizos rocosos con RQD mayor a 50 por ciento segun el Titulo H?",
        "ground_truth": "Para macizos rocosos con RQD > 50%, el valor mínimo de KST/amax es 1.00, sin necesidad de análisis de amplificación.",
        "id": "H-kst-amax-macizos-rocosos-100",
    },
    # ---- Título H, ampliación H.6 completo (Estructuras de contención) ----
    {
        "pregunta": "A que profundidad minima bajo la superficie del terreno debe desplantarse la base de un muro de gravedad segun el Titulo H?",
        "ground_truth": "La base de un muro de gravedad o en voladizo debe desplantarse cuando menos a 1 m bajo la superficie del terreno enfrente del muro.",
        "id": "H-desplante-muro-gravedad-1m",
    },
    {
        "pregunta": "Cual es el factor de seguridad minimo al deslizamiento en condicion estatica para estructuras de contencion segun el Titulo H?",
        "ground_truth": "El factor de seguridad mínimo al deslizamiento en condición estática es 1.60, según la Tabla H.6.9-1.",
        "id": "H-fs-deslizamiento-estatico-160",
    },
    # ---- Título H, ampliación H.7 completo (Evaluación geotécnica de efectos sísmicos) ----
    {
        "pregunta": "A partir de que distancia epicentral se debe considerar el aporte de la componente vertical de la senal sismica segun el Titulo H?",
        "ground_truth": "Para fuentes sismogénicas cercanas (menores de 25 km de distancia epicentral) con potencial de eventos superficiales, debe considerarse el aporte de la componente vertical de la señal sísmica.",
        "id": "H-componente-vertical-25km",
    },
    {
        "pregunta": "Cual es el valor limite de aceleracion en roca para el cual resulta importante evaluar la amplificacion segun el Titulo H?",
        "ground_truth": "La evaluación de la amplificación resulta importante para aceleraciones originarias en roca inferiores a un valor límite del orden de 0.4g.",
        "id": "H-amplificacion-limite-04g",
    },
    {
        "pregunta": "Cuantas historias de movimiento minimo se deben utilizar en los analisis de respuesta dinamica segun el Titulo H?",
        "ground_truth": "Los análisis de respuesta dinámica deben utilizar por lo menos tres historias de movimiento en función del tiempo, representativas de las diferentes fuentes sismogénicas relevantes.",
        "id": "H-historias-movimiento-minimo-tres",
    },
    # ---- Título H, ampliación H.8 completo (Sistema constructivo de
    # cimentaciones, excavaciones y muros de contención) ----
    # Ingesta verbatim 2026-09-07 (misma sesión). 2/3 preguntas probadas
    # PASSED contra producción real; la 3ra (factor de seguridad al pandeo
    # de pilotes, FS=3.0) es un hallazgo real de generación -- el LLM citó
    # correctamente la ecuación H.8.4-1 pero dijo que el Título H "no
    # especifica un valor numérico concreto" pese a que "F_S se tomará
    # igual a 3.0" está en el mismo chunk verbatim -- se deja fuera del
    # dataset a propósito (no forzada como PASSED), ver memoria privada /
    # docs/fuentes-normativas.md para el detalle.
    {
        "pregunta": "A partir de que profundidad de excavacion se debe contar con un plan de contingencia segun el Titulo H?",
        "ground_truth": "A partir de 3 m de profundidad de excavación debe contarse con un plan de contingencia.",
        "id": "H-plan-contingencia-3m",
    },
    {
        "pregunta": "Cual es la desviacion maxima de verticalidad permitida para un pilote hincado con capacidad de carga por punta segun el Titulo H?",
        "ground_truth": "La desviación máxima de verticalidad permitida no deberá ser mayor de 3/100 de su longitud.",
        "id": "H-desviacion-verticalidad-pilote-3-100",
    },
    # ---- Título H, ampliación H.9 completo (Condiciones geotécnicas
    # especiales: suelos expansivos, dispersivos/erodables, colapsables,
    # efectos de la vegetación) ----
    # Ingesta verbatim 2026-09-07 (misma sesión), 4/4 PASSED contra
    # producción real -- capítulo más grande de Título H (29 encabezados
    # reales), sin hallazgos fallidos esta vez.
    {
        "pregunta": "Cual es la profundidad maxima tipica hasta la que se desarrollan las raices de un arbol segun el Titulo H?",
        "ground_truth": "Las raíces de los árboles generalmente se desarrollan por lo regular a no más de 6.0 m de profundidad, según el Título H.",
        "id": "H-profundidad-raices-6m",
    },
    {
        "pregunta": "A que valor de pF equivale el punto de marchitamiento de las plantas segun el Titulo H?",
        "ground_truth": "El punto de marchitamiento equivale a una presión métrica de succión igual a pF = 4.2, superior a 10^3 kPa.",
        "id": "H-punto-marchitamiento-pf-42",
    },
    {
        "pregunta": "Cual es el criterio para que un suelo se considere colapsable segun la relacion gamma_d sobre gamma_dcrit del Titulo H?",
        "ground_truth": "El suelo es colapsable si gamma_d/gamma_dcrit es menor o igual a 1; si es mayor a 1, el suelo es estable o expansivo.",
        "id": "H-criterio-colapsabilidad-gamma-dcrit",
    },
    {
        "pregunta": "A partir de que porcentaje de sales de sodio en el agua intersticial se considera una arcilla como suelo dispersivo segun el Titulo H?",
        "ground_truth": "Se considera suelo dispersivo cuando la concentración de sales de sodio (Na) en el agua intersticial pasa de 40% o 60% del total de sales disueltas.",
        "id": "H-suelo-dispersivo-sales-sodio-40-60",
    },
    # ---- Título H, ampliación H.10 completo (Rehabilitación sísmica de
    # edificios: amenazas de origen sismo-geotécnico y reforzamiento de
    # cimentaciones) — CIERRA TÍTULO H COMPLETO (H.1-H.10) ----
    # Ingesta verbatim 2026-09-07 (misma sesión), 2/3 PASSED contra
    # producción real. La 3ra (profundidad del nivel freático para
    # descartar licuación, H.10.2.2.2) es un hallazgo real de
    # generación: el LLM cita el artículo correcto pero no surge los
    # valores específicos (10 m bajo el cimiento más profundo, o 15 m
    # bajo la superficie) presentes en el mismo chunk verbatim -- no
    # se agregó al dataset.
    {
        "pregunta": "A partir de que inclinacion de talud se debe evaluar la estabilidad de laderas para rehabilitacion sismica segun el Titulo H?",
        "ground_truth": "Cuando la pendiente del talud excede aproximadamente 18 grados (3 horizontal: 1 vertical), según el Título H.",
        "id": "H-inclinacion-talud-rehabilitacion-18grados",
    },
    {
        "pregunta": "Cual es el N160 minimo para suelos no cohesivos bajo la tabla de agua para descartar amenaza de licuacion segun el Titulo H?",
        "ground_truth": "N160 de 30 golpes/pie para profundidades bajo la tabla de agua, o con un contenido de arcilla mayor de 20%.",
        "id": "H-n160-minimo-licuacion-30golpes",
    },
    # ---- Adversarial / sin respuesta real en el corpus ----
    # 4 de estas 10 se probaron EN VIVO contra ask() antes de escribir el
    # ground_truth (batch de 2026-09-07). Hallazgo real e importante: la
    # pregunta sobre "Título L" hizo que el sistema AFIRME que existe un
    # "NSR-10, Título L (Diseño y Construcción de Estructuras Metálicas)"
    # -- fabricado; verificado con SQL directo (0 filas con Título L en
    # nsr10_chunks) que la NSR-10 real solo llega hasta el Título K, y que
    # "Estructuras Metálicas" es en realidad el Título F. Es una
    # alucinación real, no una suposición -- queda documentada tal cual
    # para medirla con RAGAS, no corregida de antemano. Las otras 3
    # verificadas en vivo (NTC 99999, decibeles de ruido) el sistema SÍ
    # respondió honestamente que no tiene esa información -- casos
    # positivos reales, no solo teóricos. Ojo: al verificar esto se
    # encontró además que K.4.3 (vidrios de seguridad) SÍ está cargado
    # verbatim y se citó con precisión -- la memoria privada del proyecto
    # que lo daba por "bloqueado, sin fuente" estaba desactualizada
    # (corregida por separado, no se usa K.4.3 aquí como adversarial).
    # Las otras 6 son construidas por diseño (título/norma/tema que no
    # existe o está fuera del alcance de la NSR-10), razonablemente
    # seguras de no tener contenido real, pero NO probadas una por una en
    # vivo por límite de tiempo -- si alguna resulta tener contenido real
    # al correr RAGAS, hay que revisar y corregir el ground_truth, no
    # ignorar el resultado.
    {
        "pregunta": "Que dice el Titulo L de la NSR-10 sobre estructuras metalicas prefabricadas?",
        "ground_truth": "La NSR-10 no tiene un Título L -- la numeración de títulos llega hasta el Título K. Estructuras metálicas está regulado en el Título F, no en un supuesto Título L. El sistema no debe afirmar que existe un Título L ni inventar su contenido.",
        "id": "ADV-titulo-L-fabricado",
    },
    {
        "pregunta": "Que exige el Titulo M de la NSR-10 sobre estructuras de bambu laminado?",
        "ground_truth": "La NSR-10 no tiene un Título M -- la numeración de títulos llega hasta el Título K. El sistema no debe inventar contenido para un título que no existe.",
        "id": "ADV-titulo-M-bambu-laminado",
    },
    {
        "pregunta": "Que exige la NTC 99999 sobre acabados de pintura?",
        "ground_truth": "No existe una NTC 99999 en el corpus ni como norma colombiana real conocida -- el sistema no debe inventar requisitos para ella.",
        "id": "ADV-ntc-99999-acabados-pintura",
    },
    {
        "pregunta": "Cual es el limite de decibeles de ruido permitido en obra segun la NSR-10?",
        "ground_truth": "La NSR-10 no regula límites de ruido en obra -- ese tema lo regulan normas ambientales y de salud ocupacional (ej. resoluciones del Ministerio de Trabajo), no la NSR-10. El sistema debe aclarar que no es un tema de la NSR-10, no inventar un valor en decibeles.",
        "id": "ADV-decibeles-ruido-obra",
    },
    {
        "pregunta": "Cuales son los valores de Aa y Av para una ciudad en Marte segun la NSR-10?",
        "ground_truth": "La NSR-10 es una norma colombiana que solo asigna valores de Aa y Av a municipios de Colombia -- no existe ni puede existir un valor real para una ubicación fuera de Colombia (o fuera del planeta). El sistema no debe inventar un valor.",
        "id": "ADV-marte-Aa-Av",
    },
    {
        "pregunta": "Que exige la NTC 88888 sobre iluminacion LED en fachadas?",
        "ground_truth": "No existe una NTC 88888 en el corpus ni como norma colombiana real conocida -- el sistema no debe inventar requisitos para ella.",
        "id": "ADV-ntc-88888-iluminacion-led",
    },
    {
        "pregunta": "Cual es el factor de reduccion de resistencia phi para estructuras de diamante estructural segun el Titulo C?",
        "ground_truth": "\"Diamante estructural\" no es un material reconocido por la NSR-10 (que regula concreto, acero, mampostería, madera/guadua y aluminio) -- el sistema no debe inventar un factor phi para un material que no existe en la norma.",
        "id": "ADV-material-diamante-estructural",
    },
    {
        "pregunta": "Que capitulo de la NSR-10 regula el diseno de puentes colgantes peatonales de mas de 500 metros de luz?",
        "ground_truth": "La NSR-10 regula edificaciones, no puentes -- el diseño de puentes en Colombia lo regula el CCP-14 (INVIAS/AASHTO LRFD), una norma distinta. El sistema no debe inventar un capítulo de la NSR-10 para esto.",
        "id": "ADV-puentes-colgantes-fuera-alcance",
    },
    {
        "pregunta": "Que exige el Decreto 1077 de 2015 sobre el peso maximo de granizo permitido en cubiertas?",
        "ground_truth": "El Decreto 1077 de 2015 es una norma real de Colombia (licencias urbanísticas y ordenamiento territorial, Ley 388/1997), pero no regula cargas de granizo en cubiertas -- eso sería, si acaso, una carga técnica de la NSR-10 Título B. El sistema no debe inventar una exigencia de granizo atribuida al Decreto 1077.",
        "id": "ADV-decreto1077-granizo-cubiertas",
    },
    {
        "pregunta": "Que dice la NSR-10 sobre el diseno estructural de reactores nucleares?",
        "ground_truth": "La NSR-10 es una norma de edificaciones civiles convencionales en Colombia y no regula reactores nucleares -- ese es un tema completamente fuera de su alcance. El sistema no debe inventar contenido para esto.",
        "id": "ADV-reactor-nuclear-fuera-alcance",
    },
]
