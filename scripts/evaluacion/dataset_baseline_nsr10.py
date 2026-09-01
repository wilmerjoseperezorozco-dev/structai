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
]
