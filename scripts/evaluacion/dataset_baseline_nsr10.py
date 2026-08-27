"""
Dataset de evaluación RAGAS — línea base NSR-10 (Títulos A/B/C).

Reutiliza las mismas 12 preguntas ya verificadas a mano en
apps/api/tests/test_rag_nsr10_regresion.py (no se inventan preguntas
nuevas para esto) — cada una ya tiene un hecho numérico real confirmado
contra el PDF oficial. Aquí se les agrega un `ground_truth` corto (una
oración con el hecho real, no una respuesta completa "oficial") para que
RAGAS pueda calcular context_precision/context_recall además de
faithfulness/answer_relevancy (que no necesitan ground_truth).

El ground_truth es deliberadamente mínimo -- una frase que contiene el
hecho verificado, no una redacción completa "ideal" de la norma (eso
sería inventar contenido que no se verificó línea por línea). Esto basta
para que RAGAS mida si el contexto recuperado contiene esa frase/idea,
sin arriesgar que el ground_truth mismo esté mal redactado.
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
]
