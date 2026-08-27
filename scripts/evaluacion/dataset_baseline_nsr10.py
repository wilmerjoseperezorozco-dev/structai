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
]
