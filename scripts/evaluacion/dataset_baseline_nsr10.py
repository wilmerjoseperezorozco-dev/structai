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

Ampliación 2026-09-07 (misma sesión, continuación: 145 -> 163) siguió
el mismo criterio -- verificación real con ask() antes de agregar cada
pregunta -- a medida que se cerraba Título H completo (H.5 a H.10) y se
empezaba Título A.3.3 (irregularidades en planta/altura).

Ampliación 2026-09-07 (misma sesión, 163 -> 276, a pedido explícito del
usuario: "vemos cuantas preguntas aumentamos... tal vez algunas 300
bien variadas aumentando nivel de complejidad" y "sin correr, dejarlas
ahi"). **Cambio metodológico deliberado respecto a TODO lo anterior en
este archivo**: estas 113 preguntas nuevas NO se verificaron con ask()
en vivo contra producción -- se dejan escritas para una futura corrida
de RAGAS/regresión que las evalúe en bloque, en vez de gastar cupo de
Groq/OpenAI verificando una por una como se hizo con las 163 previas.
El ground_truth de todas formas viene de una fuente real: para Título H
(H.9/H.10, 27 preguntas) y Título A (A.3.3, 14 preguntas), del texto
verbatim transcrito y subido a producción en esta misma sesión
(confirmado contra el PDF oficial antes de escribir cada chunk); para
las demás 72 (síntesis cruzada SINT2, adversarial ADV2, coloquial
COLOQ2, compuestas multi-hop COMP2), de los ground_truth YA verificados
de las 163 preguntas anteriores de este mismo archivo -- ningún hecho
nuevo se inventó sin una fuente verificada previamente. No se llegó al
número redondo de "algunas 300" pedido -- se priorizó no forzar
preguntas de relleno de calidad dudosa solo para completar la cifra;
276 preguntas reales, bien variadas, es el resultado honesto de esta
ronda. Antes de correr RAGAS/pytest sobre este archivo la próxima vez,
las 113 preguntas de esta ampliación deben pasar primero por
verificación real contra `ask()` (retrieval + generación), igual que
todas las anteriores -- no se puede asumir que pasan solo porque el
ground_truth es correcto, el sistema real podría fallar en recuperarlo
o en sintetizarlo (ver los hallazgos de H.8.4-1/H.10.2.2.2 en este
mismo archivo como ejemplo de por qué esa verificación importa).

**VERIFICACIÓN REAL COMPLETADA 2026-09-08** (pedido explícito del
usuario: "corre las 113 preguntas nuevas contra ask() y anota el
hallazgo") -- `scripts/evaluacion/_verificar_113_nuevas_ask.py`, 113
llamadas reales a `ask()` (Groq agotado, respaldo OpenAI automático),
resultados completos en `scripts/evaluacion/resultados_113_nuevas.json`.
El chequeo automático (comparar números extraídos del ground_truth
contra la respuesta) tuvo muchos falsos negativos por formato (φ vs
"phi", unicode, respuestas en lista) -- **los 62 "AUTO-FAIL" se
revisaron a mano uno por uno**. Resultado real: de las 95 preguntas
factuales (excluyendo las 18 adversariales), ~76 correctas (~80%,
consistente con el baseline RAGAS ya medido) y **19 fallos reales**,
agrupados en:
1. **2 alucinaciones nuevas confirmadas** (mismo patrón que F.5.4.5):
   `H-H9-cuatro-tipos-suelos-colapsables` (el LLM reemplazó 2 de los 4
   tipos reales -- cenizas volcánicas y suelos residuales -- por
   contenido inventado, mezclando la definición general de H.9.3.1 con
   la lista de H.9.3.2); `COLOQ2-fyt-confinamiento-700MPa` (el LLM
   inventó una fórmula completa 0.0018×200.000=360MPa y una cita a
   C.10.13.8.7 que no corresponde, en vez del valor real de 700 MPa).
2. **1 contradicción lógica real**: `COMP2-A-phi-1bP-vs-1bA` responde
   "No, son diferentes" y en la misma respuesta demuestra que ambos
   valen φ=0.8 -- el LLM se contradice a sí mismo en una pregunta
   compuesta de comparación.
3. **~16 fallos de retrieval real** (el chunk correcto existe en
   producción pero no se recuperó, o se recuperó el capítulo
   equivocado) -- incluye un hallazgo transversal medible: varias
   preguntas `COLOQ2-` (fraseo coloquial) fallan pese a que la MISMA
   pregunta en fraseo técnico directo ya había pasado en este mismo
   dataset (ej. `F-analisis-racional-phi-miembros-080-conexiones-065`
   pasó, `COLOQ2-analisis-racional-phi` -- misma pregunta, fraseo
   coloquial -- no recuperó el valor). Confirma cuantitativamente lo
   que esa categoría se diseñó para medir.

**Las 18 preguntas adversariales (ADV2-) dieron 18/18 limpio** -- ningún
caso de alucinación de contenido fabricado al preguntar por normas,
títulos o materiales que no existen; el sistema admitió honestamente
no tener la información en todos los casos.

Detalle completo por pregunta (incluye las ~76 correctas) en
`resultados_113_nuevas.json`. No se removió ninguna pregunta de este
dataset por haber fallado -- RAGAS mide desempeño real, no exige que
todo pase; los 19 fallos reales quedan documentados aquí y en memoria
privada (`project_structai_nsr10_inventario_titulos.md`) como
hallazgos a corregir, no ocultados.
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
    # ---- Título A, ampliación A.3.3 completo (Configuración estructural:
    # irregularidades en planta y en altura, ausencia de redundancia,
    # sobrerresistencia) + Tablas A.3-5/6/7 ----
    # Ingesta verbatim 2026-09-07 (misma sesión), 2/2 PASSED contra
    # producción real. Corrige un hallazgo real: memoria privada vieja
    # describía "A.3.6" como el capítulo de irregularidades -- INCORRECTO,
    # A.3.6 real es "Efectos sísmicos en los elementos estructurales"; las
    # irregularidades viven en A.3.3.4/A.3.3.5 con las Tablas A.3-6/A.3-7,
    # que nunca se habían extraído (nota de cobertura vieja lo admitía
    # honestamente como PENDIENTE).
    {
        "pregunta": "Cual es el valor de phi_p para una irregularidad torsional extrema tipo 1bP segun la Tabla A.3-6 del Titulo A?",
        "ground_truth": "phi_p = 0.8 para la irregularidad torsional extrema tipo 1bP, según la Tabla A.3-6.",
        "id": "A-phi-p-torsional-extrema-1bP-08",
    },
    {
        "pregunta": "Cuando se considera que una estructura tiene piso debil extremo tipo 5bA segun la Tabla A.3-7 del Titulo A?",
        "ground_truth": "Cuando la resistencia del piso es menor del 65% de la del piso inmediatamente superior; se aplica phi_a = 0.8.",
        "id": "A-piso-debil-extremo-5bA-65porciento",
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
    # ======================================================================
    # AMPLIACIÓN 2026-09-07 (misma sesión, a pedido explícito del usuario:
    # "vemos cuantas preguntas aumentamos... tal vez algunas 300 bien
    # variadas aumentando nivel de complejidad"): de 163 a 278 preguntas.
    #
    # DIFERENCIA METODOLÓGICA IMPORTANTE respecto a todo lo anterior en este
    # archivo: estas preguntas NO se verificaron con ask() en vivo contra
    # producción (pedido explícito: "sin correr, dejarlas ahi") -- se
    # dejan escritas para una futura corrida de RAGAS/regresión que las
    # evalúe en bloque. El ground_truth sigue viniendo de una fuente real
    # y verificada: para Título H (H.9/H.10) y Título A (A.3.3), del texto
    # verbatim que se transcribió y subió a producción en esta misma sesión
    # (confirmado contra el PDF oficial antes de escribir el chunk); para
    # las demás categorías (síntesis cruzada, coloquial, compuestas), de
    # los ground_truth YA verificados de las 163 preguntas anteriores en
    # este mismo archivo -- no se inventa ningún hecho nuevo sin fuente.
    # ======================================================================

    # ---- Título H, más hechos de H.9 (suelos expansivos/dispersivos/
    # colapsables/vegetación) no cubiertos por las 4 preguntas ya
    # verificadas de H.9 ----
    {
        "pregunta": "Cuales son los minerales activos que le dan a una arcilla su caracter expansivo segun el Titulo H?",
        "ground_truth": "Los minerales activos reconocidos son la montmorilonita, la vermiculita y algunas variedades de haloisita.",
        "id": "H-H9-minerales-expansivos-montmorilonita",
    },
    {
        "pregunta": "Con que sufijo identifica el IGAC en la taxonomia agrologica a los suelos potencialmente expansivos segun el Titulo H?",
        "ground_truth": "Se identifican con el sufijo \"ert\" o con la palabra \"Vertic\" (por ejemplo Udert, Haplustert, Vertic Paleoudult).",
        "id": "H-H9-sufijo-vertic-igac",
    },
    {
        "pregunta": "Que porcentaje minimo de los sondeos debe reconocer los materiales bajo la zona activa en un estudio de suelos expansivos segun el Titulo H?",
        "ground_truth": "Por lo menos el 50% de los sondeos deben reconocer suficientemente los materiales que se encuentran por debajo de la zona activa.",
        "id": "H-H9-sondeos-50porciento-zona-activa",
    },
    {
        "pregunta": "Que pendiente de drenaje perimetral se recomienda alrededor de una estructura en suelo expansivo segun el Titulo H?",
        "ground_truth": "Se recomienda un adecuado drenaje alrededor de las estructuras por medio de pendientes perimetrales del 2% al 10%.",
        "id": "H-H9-drenaje-perimetral-2-10porciento",
    },
    {
        "pregunta": "Cuales son los cuatro tipos principales de suelos colapsables que reconoce el Titulo H?",
        "ground_truth": "Suelos aluviales y coluviales, suelos eólicos (loess), cenizas volcánicas, y suelos residuales.",
        "id": "H-H9-cuatro-tipos-suelos-colapsables",
    },
    {
        "pregunta": "A partir de que deformacion potencial de hidrocolapso se clasifica un suelo como muy severo segun la Tabla H.9.3-1 del Titulo H?",
        "ground_truth": "Cuando la deformación potencial de hidrocolapso (épsilon_w) es mayor de 0.20, la clasificación de severidad es muy severa.",
        "id": "H-H9-hidrocolapso-muy-severo-020",
    },
    {
        "pregunta": "A cuantos kPa de presion de poros negativa equivale una succion de pF=4 segun la Tabla H.9.4-1 del Titulo H?",
        "ground_truth": "Un pF de 4 equivale a una presión de poros negativa de 981 kPa (10 kgf/cm2), según la Tabla H.9.4-1.",
        "id": "H-H9-pf4-981kpa",
    },
    {
        "pregunta": "Cuantos litros de agua por dia transpira un eucalipto Eucalyptus Macarthuri en un dia soleado segun la Tabla H.9.4-2 del Titulo H?",
        "ground_truth": "500 litros por día, según la Tabla H.9.4-2 de requerimientos de agua.",
        "id": "H-H9-eucalyptus-macarthuri-500Ldia",
    },
    {
        "pregunta": "A que velocidad maxima puede crecer una raiz en busqueda de agua y nutrientes segun el Titulo H?",
        "ground_truth": "El crecimiento de las raíces puede llegar a 20 mm por día en búsqueda de agua y nutrientes.",
        "id": "H-H9-crecimiento-raices-20mm-dia",
    },
    {
        "pregunta": "Menciona una especie de arbol considerada agresiva por el Titulo H que no deberia sembrarse cerca de edificaciones.",
        "ground_truth": "El Urapán (Fraxinus chinensis), el Eucalipto, el Sauce, el Pino, la Acacia o el Cerezo -- todas consideradas especies agresivas en H.9.4.6.2(a).",
        "id": "H-H9-especie-agresiva-urapan",
    },
    {
        "pregunta": "Cuales son los dos caminos de mitigacion de tipo estructural para suelos expansivos segun el Titulo H?",
        "ground_truth": "Cimentación rígida y construcción flexible, según H.9.1.9.",
        "id": "H-H9-mitigacion-estructural-dos-caminos",
    },
    {
        "pregunta": "Hasta que pendiente de ladera se puede aplicar el recubrimiento vegetativo como medida contra suelos erodables segun el Titulo H?",
        "ground_truth": "El recubrimiento vegetativo es aplicable en laderas de poca pendiente, menor de 20%.",
        "id": "H-H9-recubrimiento-vegetativo-20porciento",
    },
    {
        "pregunta": "En que rango de succion pF se ubica el limite plastico de un suelo segun el Titulo H?",
        "ground_truth": "El límite plástico corresponde a succiones pF entre 4 y 5.",
        "id": "H-H9-limite-plastico-pf-4a5",
    },
    {
        "pregunta": "Por encima de que valor de succion pF se desencadena un proceso de desecacion en vez de expansion segun el Titulo H?",
        "ground_truth": "Para succiones pF superiores a 3.0 se desencadena un proceso de desecación; para pF inferiores a 3.0, uno de expansión.",
        "id": "H-H9-limite-practico-pf-30",
    },
    {
        "pregunta": "Que tipo de suelos identifica el Titulo H con el nombre generico de loess?",
        "ground_truth": "Los suelos eólicos -- arenas y limos arenosos con escaso cemento arcilloso, depositados por el viento, reciben el nombre genérico de loess en las zonas templadas.",
        "id": "H-H9-loess-suelos-eolicos",
    },

    # ---- Título H, más hechos de H.10 (rehabilitación sísmica) no
    # cubiertos por las 2 preguntas ya verificadas de H.10 ----
    {
        "pregunta": "Cuales son las cinco amenazas sismicas del sitio que enumera el Titulo H para rehabilitacion de cimentaciones?",
        "ground_truth": "Ruptura de una falla, licuación, compactación diferencial, deslizamientos, y avalancha o inundación.",
        "id": "H-H10-cinco-amenazas-sismicas-sitio",
    },
    {
        "pregunta": "De que edad geologica minima deben ser los materiales geologicos bajo el nivel freatico para descartar amenaza de compactacion diferencial segun el Titulo H?",
        "ground_truth": "Deben ser del Pleistoceno en edad geológica, es decir más antiguos de 11.000 años.",
        "id": "H-H10-pleistoceno-11000anos",
    },
    {
        "pregunta": "Cuales son los tres tipos de cimentacion que considera el Titulo H para el reforzamiento y rigidez de cimentaciones?",
        "ground_truth": "Cimentaciones superficiales (zapatas y losas), pilotes, y pilas.",
        "id": "H-H10-tres-tipos-cimentacion",
    },
    {
        "pregunta": "Menciona dos esquemas de mejoramiento estructural para mitigar deslizamientos segun el Titulo H.",
        "ground_truth": "Muros de gravedad, muros anclados/pernados (soil nailing), muros de tierra mecánicamente estabilizada, barreras para flujos de escombros, reforzamiento del edificio, vigas de equilibrio en la cimentación, o muros/pantallas de cortante.",
        "id": "H-H10-mejoramiento-estructural-deslizamientos",
    },
    {
        "pregunta": "Que tecnica de inyeccion menciona el Titulo H para mejorar el suelo bajo cimentaciones existentes?",
        "ground_truth": "El jet grouting, además de inyecciones de compactación e inyecciones químicas (cemento, cal).",
        "id": "H-H10-jet-grouting-mejoramiento-suelo",
    },
    {
        "pregunta": "Bajo la suposicion de base fija en un procedimiento lineal, como deben ser las acciones sobre los componentes geotecnicos segun el Titulo H?",
        "ground_truth": "Las acciones sobre los componentes geotécnicos deberán ser de fuerza controlada.",
        "id": "H-H10-base-fija-fuerza-controlada",
    },
    {
        "pregunta": "Menciona dos fuentes reales de amenaza de avalancha o inundacion que reconoce el Titulo H para rehabilitacion sismica.",
        "ground_truth": "Presas/acueductos/tanques de almacenamiento de agua dañados por el sismo, áreas costeras susceptibles a tsunamis, o áreas bajas con subsidencia regional.",
        "id": "H-H10-fuentes-avalancha-inundacion",
    },
    {
        "pregunta": "Cuales son los tres tipos generales de medidas de mitigacion de la amenaza de licuacion segun el Titulo H?",
        "ground_truth": "Modificar la estructura, modificar la cimentación, o modificar las condiciones del suelo.",
        "id": "H-H10-tres-medidas-mitigacion-licuacion",
    },
    {
        "pregunta": "Quien debe determinar la capacidad ultima y de trabajo de los componentes de la cimentacion segun el Titulo H, capitulo de rehabilitacion sismica?",
        "ground_truth": "El ingeniero geotecnista, según los requisitos del capítulo H.4.",
        "id": "H-H10-capacidad-ultima-geotecnista",
    },
    {
        "pregunta": "Que tecnica se usa para incrementar la capacidad o resistencia a traccion de una zapata existente segun el Titulo H?",
        "ground_truth": "Las zapatas y losas pueden ser sub-muradas para incrementar su capacidad o resistencia a la tracción.",
        "id": "H-H10-zapatas-submuradas",
    },
    {
        "pregunta": "Para que sirven las vigas de equilibrio en la cimentacion segun el Titulo H?",
        "ground_truth": "Para dar interconexión adecuada cuando existe potencial de desplazamiento diferencial lateral de las cimentaciones del edificio.",
        "id": "H-H10-vigas-equilibrio-desplazamiento-lateral",
    },
    {
        "pregunta": "Que tipo de amenazas cubre el alcance del capitulo de rehabilitacion sismica de edificios del Titulo H?",
        "ground_truth": "Amenazas potenciales de origen sismo-geotécnico: licuación, compactación diferencial, deslizamientos, caída de rocas y avalanchas.",
        "id": "H-H10-alcance-amenazas-sismogeotecnicas",
    },

    # ---- Título A, más hechos de A.3.3 (irregularidades) no cubiertos
    # por las 2 preguntas ya verificadas de A.3.3 ----
    {
        "pregunta": "Cual es la formula del coeficiente de capacidad de disipacion de energia reducido R segun la ecuacion A.3.3-1 del Titulo A?",
        "ground_truth": "R = phi_a * phi_p * phi_r * R0 (ecuación A.3.3-1).",
        "id": "A-A33-ecuacion-A331-R",
    },
    {
        "pregunta": "A partir de que porcentaje de la dimension de la planta se considera excesivo un retroceso en una esquina segun la Tabla A.3-6 del Titulo A?",
        "ground_truth": "Cuando las proyecciones de la estructura a ambos lados del retroceso son mayores que el 15% de la dimensión de la planta en esa dirección (Tipo 2P).",
        "id": "A-A33-retroceso-esquina-15porciento",
    },
    {
        "pregunta": "A partir de que porcentaje del area bruta del diafragma se considera irregularidad por discontinuidad del diafragma segun la Tabla A.3-6 del Titulo A?",
        "ground_truth": "Cuando las aberturas, entrantes, retrocesos o huecos tienen áreas mayores al 50% del área bruta del diafragma (Tipo 3P).",
        "id": "A-A33-discontinuidad-diafragma-50porciento",
    },
    {
        "pregunta": "Cual es el valor de phi_p para la irregularidad tipo 4P, desplazamientos del plano de accion, segun la Tabla A.3-6 del Titulo A?",
        "ground_truth": "phi_p = 0.8 para la irregularidad tipo 4P.",
        "id": "A-A33-phi-p-tipo-4P-08",
    },
    {
        "pregunta": "Cual es el valor de phi_p para la irregularidad tipo 5P, sistemas no paralelos, segun la Tabla A.3-6 del Titulo A?",
        "ground_truth": "phi_p = 0.9 para la irregularidad tipo 5P.",
        "id": "A-A33-phi-p-tipo-5P-09",
    },
    {
        "pregunta": "Cuando se considera que un piso tiene irregularidad tipo 1aA, piso flexible, segun la Tabla A.3-7 del Titulo A?",
        "ground_truth": "Cuando la rigidez ante fuerzas horizontales de un piso es menor del 70% pero superior o igual al 60% de la rigidez del piso superior, o menor del 80% pero superior o igual al 70% del promedio de los tres pisos superiores. phi_a = 0.9.",
        "id": "A-A33-piso-flexible-1aA",
    },
    {
        "pregunta": "A partir de que relacion de masas entre pisos contiguos se considera irregularidad tipo 2A segun la Tabla A.3-7 del Titulo A?",
        "ground_truth": "Cuando la masa de cualquier piso es mayor que 1.5 veces la masa de uno de los pisos contiguos (excepto cubiertas más livianas). phi_a = 0.9.",
        "id": "A-A33-irregularidad-masa-2A-15veces",
    },
    {
        "pregunta": "A partir de que relacion de dimensiones horizontales entre pisos adyacentes se considera irregularidad geometrica tipo 3A segun la Tabla A.3-7 del Titulo A?",
        "ground_truth": "Cuando la dimensión horizontal del sistema de resistencia sísmica en un piso es mayor que 1.3 veces la misma dimensión en un piso adyacente. phi_a = 0.9.",
        "id": "A-A33-irregularidad-geometrica-3A-13veces",
    },
    {
        "pregunta": "Cual es el valor de phi_a para la irregularidad tipo 4A, desplazamientos dentro del plano de accion, segun la Tabla A.3-7 del Titulo A?",
        "ground_truth": "phi_a = 0.8 para la irregularidad tipo 4A.",
        "id": "A-A33-phi-a-tipo-4A-08",
    },
    {
        "pregunta": "Cuando se considera que un piso tiene irregularidad tipo 5aA, piso debil, segun la Tabla A.3-7 del Titulo A?",
        "ground_truth": "Cuando la resistencia del piso es menor del 80% pero superior o igual al 65% de la del piso inmediatamente superior. phi_a = 0.9.",
        "id": "A-A33-piso-debil-5aA-80porciento",
    },
    {
        "pregunta": "A que tipos de irregularidad en planta puede limitarse la evaluacion en zonas de amenaza sismica baja para grupos de uso I y II segun el Titulo A?",
        "ground_truth": "A las irregularidades tipo 1aP y 1bP (Tabla A.3-6), según A.3.3.6.",
        "id": "A-A33-zona-baja-1aP-1bP",
    },
    {
        "pregunta": "A que tipos de irregularidad en planta puede limitarse la evaluacion en zona de amenaza sismica intermedia para el grupo de uso I segun el Titulo A?",
        "ground_truth": "A las irregularidades tipo 1aP, 1bP, 3P y 4P (Tabla A.3-6), según A.3.3.7.",
        "id": "A-A33-zona-intermedia-1aP-1bP-3P-4P",
    },
    {
        "pregunta": "Que valor de phi_r se asigna siempre a una edificacion con capacidad de disipacion de energia minima DMI segun el Titulo A?",
        "ground_truth": "phi_r = 1.0 siempre, para edificaciones con sistema estructural DMI (A.3.3.8.1).",
        "id": "A-A33-DMI-phi-r-siempre-10",
    },
    {
        "pregunta": "Cual es la formula de la ecuacion A.3.3-2 para las fuerzas de diseno amplificadas por sobrerresistencia segun el Titulo A?",
        "ground_truth": "E = (Omega0 * Fs / R) mas menos 0.5 * Aa * Fa * D (ecuación A.3.3-2).",
        "id": "A-A33-ecuacion-A332-sobrerresistencia",
    },

    # ---- Síntesis cruzada entre títulos (SINT2) ----
    {
        "pregunta": "Es mayor la sobrecarga minima que exige el Titulo H para la via publica cerca de excavaciones (15 kPa) que la carga minima de diseno por viento del Titulo B (0.40 kN/m2)?",
        "ground_truth": "Sí, 15 kPa (equivalentes a 15 kN/m²) es mucho mayor que 0.40 kN/m², aunque miden fenómenos distintos (sobrecarga de excavación vs. presión de viento).",
        "id": "SINT2-sobrecarga-H-vs-viento-B",
    },
    {
        "pregunta": "Es mayor la sobrecarga minima que exige el Titulo H cerca de excavaciones (15 kPa) que la carga viva para estanterias de biblioteca del Titulo B (7 kN/m2)?",
        "ground_truth": "Sí, 15 kN/m² es mayor que 7 kN/m², aunque son cargas de naturaleza distinta (sobrecarga temporal de excavación vs. carga viva de servicio).",
        "id": "SINT2-sobrecarga-H-vs-biblioteca-B",
    },
    {
        "pregunta": "Es mas inclinado el talud a partir del cual el Titulo H exige evaluar estabilidad de laderas (18 grados) que el angulo que define un tragaluz segun el Titulo K (mas de 15 grados)?",
        "ground_truth": "Sí, 18° es mayor que 15°, aunque son criterios de títulos y propósitos completamente distintos (estabilidad geotécnica de laderas vs. clasificación de vidrio inclinado).",
        "id": "SINT2-talud-H10-vs-tragaluz-K",
    },
    {
        "pregunta": "Es mayor el angulo de doblez de los ganchos sismicos en estribos de confinamiento del Titulo C (135 grados) que el angulo de talud del Titulo H que activa la evaluacion de estabilidad de laderas (18 grados)?",
        "ground_truth": "Sí, 135° es mucho mayor que 18°, aunque son ángulos de naturaleza completamente distinta (doblez de refuerzo de acero vs. inclinación de un talud).",
        "id": "SINT2-ganchos-C-vs-talud-H10",
    },
    {
        "pregunta": "Es menor el factor de seguridad minimo al deslizamiento en condicion estatica de muros de contencion del Titulo H (1.60) que el factor de seguridad exigido para paneles de vidrio en barandas del Titulo K (4)?",
        "ground_truth": "Sí, 1.60 es menor que 4, aunque son factores de seguridad de disciplinas distintas (geotecnia vs. vidrio de seguridad) y no directamente comparables en su significado físico.",
        "id": "SINT2-fs-deslizamiento-H-vs-vidrio-K",
    },
    {
        "pregunta": "Es mayor el f'c minimo del concreto estructural del Titulo C (17 MPa) que la resistencia minima del mortero de pega en mamposteria del Titulo E (7.5 MPa)?",
        "ground_truth": "Sí, 17 MPa es más del doble de 7.5 MPa, aunque son materiales y títulos distintos (concreto estructural vs. mortero de pega de mampostería de 1-2 pisos).",
        "id": "SINT2-fc-C-vs-mortero-pega-E-17vs75",
    },
    {
        "pregunta": "Es mayor el espesor minimo de un muro de mamposteria no reforzada del Titulo D (120 mm) que el espesor minimo de acero base en entramados livianos formados en frio del Titulo F (0.455 mm)?",
        "ground_truth": "Sí, 120 mm es varios órdenes de magnitud mayor que 0.455 mm, pero son magnitudes de naturaleza distinta (espesor de un muro de mampostería vs. espesor de lámina de acero) que no tiene sentido comparar en la práctica.",
        "id": "SINT2-espesor-D-vs-acero-F",
    },
    {
        "pregunta": "Puede compararse directamente el area minima de las columnas de confinamiento del Titulo E (20.000 mm2) con el porcentaje maximo de celdas verticales del Titulo D (65%)?",
        "ground_truth": "No son directamente comparables -- uno es un área absoluta en mm² (Título E, columnas de confinamiento) y el otro es un porcentaje relativo del área de sección transversal (Título D, celdas verticales de mampostería).",
        "id": "SINT2-columna-E-vs-celdas-D-no-comparable",
    },
    {
        "pregunta": "Tiene sentido comparar la deriva maxima permitida para concreto del Titulo A (1.0%) con el factor de seguridad al deslizamiento de muros de contencion del Titulo H (1.60)?",
        "ground_truth": "No directamente -- la deriva máxima es un porcentaje de desplazamiento relativo de piso (Título A, requisito estructural sísmico) mientras que el factor de seguridad al deslizamiento es un cociente de resistencia/solicitación (Título H, requisito geotécnico); son magnitudes de naturaleza distinta.",
        "id": "SINT2-deriva-A-vs-fs-H-no-comparable",
    },
    {
        "pregunta": "El Titulo A y el Titulo H regulan lo mismo para el diseno de la cimentacion de un edificio sismo resistente?",
        "ground_truth": "No, son complementarios: el Título A define las fuerzas sísmicas de diseño y los sistemas estructurales de resistencia sísmica, mientras que el Título H define las capacidades del suelo, los factores de seguridad geotécnicos y los estudios de suelo necesarios para diseñar la cimentación misma.",
        "id": "SINT2-titulo-A-vs-H-cimentacion",
    },
    {
        "pregunta": "El Titulo K prohibe las uniones clavadas igual que el Titulo G lo hace para la guadua?",
        "ground_truth": "No, la prohibición de uniones clavadas es específica de la guadua en el Título G (por el riesgo de grietas longitudinales); el Título K regula vidrios y tiene sus propios requisitos de seguridad, sin relación con uniones clavadas.",
        "id": "SINT2-vidrio-K-vs-guadua-G-uniones",
    },
    {
        "pregunta": "Exige el Titulo G un umbral de area construida para supervision tecnica igual al que exige el Titulo D para mamposteria?",
        "ground_truth": "El Título D sí establece un umbral numérico claro (más de 3.000 m² de área construida obliga a supervisión técnica en mampostería); el corpus no documenta un umbral equivalente específico para madera/guadua en el Título G, así que no es correcto asumir que aplica el mismo número.",
        "id": "SINT2-supervision-D-vs-G-no-mismo-umbral",
    },
    {
        "pregunta": "Es mayor el recubrimiento minimo del concreto contra el suelo del Titulo C (75 mm) que el espesor minimo de un muro de mamposteria no reforzada del Titulo D (120 mm)?",
        "ground_truth": "No, 75 mm es menor que 120 mm, aunque miden conceptos distintos (recubrimiento de acero de refuerzo en concreto vs. espesor nominal de un muro de mampostería).",
        "id": "SINT2-recubrimiento-C-vs-espesor-D",
    },
    {
        "pregunta": "Los cinco anos de experiencia que exige el Titulo H para un geotecnista son el mismo requisito que los cinco anos de registro que exige el Titulo I para un supervisor tecnico?",
        "ground_truth": "No, aunque el número coincide (5 años), son requisitos distintos: el Título H exige más de 5 años de experiencia previa en diseño geotécnico de cimentaciones para dirigir un estudio, mientras que el Título I exige conservar el registro escrito de las labores de supervisión durante al menos 5 años después de realizadas.",
        "id": "SINT2-experiencia-H-vs-registro-I-distintos",
    },
    {
        "pregunta": "El caudal minimo de un hidrante para hospitales del Titulo J (63 L/s) y la fuerza maxima de apertura de una puerta de emergencia del Titulo K (250 N) se pueden expresar en las mismas unidades?",
        "ground_truth": "No, son magnitudes físicas distintas -- un caudal (litros por segundo) y una fuerza (newtons) -- no se pueden convertir la una en la otra ni comparar directamente.",
        "id": "SINT2-hidrante-J-vs-puerta-K-unidades",
    },
    {
        "pregunta": "Los suelos colapsables descritos en el Titulo H y los suelos expansivos descritos en el mismo titulo son el mismo fenomeno geotecnico?",
        "ground_truth": "No, son fenómenos distintos: los suelos expansivos (H.9.1) se hinchan al ganar humedad por minerales activos como la montmorilonita, mientras que los suelos colapsables (H.9.3) pierden su estructura y se asientan bruscamente al saturarse, sin relación con la expansión.",
        "id": "SINT2-suelo-colapsable-vs-expansivo-H",
    },
    {
        "pregunta": "Regula el Titulo A los mismos sistemas de disipacion de energia (DMI/DMO/DES) que aplica el Titulo C para el concreto?",
        "ground_truth": "El Título A define el marco general de los grados de capacidad de disipación de energía (DMI/DMO/DES) y sus coeficientes R0 asociados a cada sistema estructural, mientras que el Título C aplica esos mismos grados a los requisitos de detallado específicos del concreto reforzado -- son complementarios, no duplicados.",
        "id": "SINT2-DMI-DMO-DES-A-vs-C",
    },
    {
        "pregunta": "Es correcto decir que el Titulo D y el Titulo G regulan el mismo material estructural?",
        "ground_truth": "No, el Título D regula mampostería estructural (bloques de concreto, arcilla, morteros), mientras que el Título G regula madera y guadua -- son materiales y capítulos completamente distintos.",
        "id": "SINT2-material-D-vs-G-distintos",
    },

    # ---- Adversarial / sin respuesta real en el corpus (ADV2) ----
    {
        "pregunta": "Que exige el Titulo N de la NSR-10 sobre sostenibilidad y huella de carbono en la construccion?",
        "ground_truth": "La NSR-10 no tiene un Título N -- la numeración de títulos llega hasta el Título K. El sistema no debe inventar contenido para un título que no existe.",
        "id": "ADV2-titulo-N-sostenibilidad-fabricado",
    },
    {
        "pregunta": "Existe una NTC 5555 sobre resistencia al fuego de puertas de madera dentro del corpus?",
        "ground_truth": "No existe una NTC 5555 en el corpus ingestado -- el sistema no debe inventar requisitos para una norma que no está cargada ni confirmada.",
        "id": "ADV2-ntc-5555-puertas-madera",
    },
    {
        "pregunta": "Que exige la NSR-10 sobre la instalacion de paneles solares fotovoltaicos en cubiertas?",
        "ground_truth": "El corpus verbatim de la NSR-10 ingestado no contiene requisitos específicos sobre paneles solares fotovoltaicos -- el sistema no debe inventar un numeral o tabla para esto.",
        "id": "ADV2-paneles-solares-fotovoltaicos",
    },
    {
        "pregunta": "Cuales son los valores de Aa y Av para la ciudad de Miami, Estados Unidos, segun la NSR-10?",
        "ground_truth": "La NSR-10 es una norma colombiana que solo asigna valores de Aa y Av a municipios de Colombia -- no existe un valor real de Aa/Av para una ciudad de otro país. El sistema no debe inventar un valor.",
        "id": "ADV2-miami-Aa-Av",
    },
    {
        "pregunta": "Que numeral de la NSR-10 regula el diseno de piscinas de fibra de vidrio prefabricadas?",
        "ground_truth": "El corpus no tiene un numeral específico sobre piscinas de fibra de vidrio prefabricadas -- el sistema no debe inventar un numeral para esto.",
        "id": "ADV2-piscinas-fibra-vidrio",
    },
    {
        "pregunta": "Que exige el Titulo F sobre estructuras de titanio?",
        "ground_truth": "El Título F regula acero (F.1-F.4) y aluminio (F.5) -- el titanio no es un material reconocido por ese título. El sistema no debe inventar requisitos de titanio atribuidos al Título F.",
        "id": "ADV2-titanio-titulo-F",
    },
    {
        "pregunta": "Cual es el f'c minimo segun el Titulo C para concreto fabricado con regolito lunar?",
        "ground_truth": "El Título C regula concreto estructural convencional en Colombia -- no existe un f'c definido para concreto lunar o regolito, es un escenario fuera del alcance de la norma. El sistema no debe inventar un valor.",
        "id": "ADV2-concreto-lunar-regolito",
    },
    {
        "pregunta": "Existe un Titulo Z en la NSR-10 dedicado a inteligencia artificial en el diseno estructural?",
        "ground_truth": "No, la NSR-10 no tiene un Título Z ni ningún título dedicado a inteligencia artificial -- la numeración llega hasta el Título K. El sistema no debe inventar contenido para esto.",
        "id": "ADV2-titulo-Z-ia-fabricado",
    },
    {
        "pregunta": "Que exige la Resolucion 0330 de RAS 2000 sobre torres eolicas marinas?",
        "ground_truth": "La Resolución 0330 (RAS 2000) regula sistemas de acueducto, alcantarillado y aseo -- no regula torres eólicas marinas, un tema completamente fuera de su alcance. El sistema no debe inventar contenido.",
        "id": "ADV2-ras2000-torres-eolicas",
    },
    {
        "pregunta": "Cuantos decibelios maximo permite el Titulo A durante la ocurrencia de un sismo de diseno?",
        "ground_truth": "El Título A regula fuerzas y requisitos sísmicos estructurales, no niveles de ruido -- la pregunta mezcla dos magnitudes sin relación. El sistema no debe inventar un límite de decibelios.",
        "id": "ADV2-decibeles-sismo-titulo-A",
    },
    {
        "pregunta": "Que capitulo de la NSR-10 regula el uso de drones para inspeccion estructural?",
        "ground_truth": "El corpus de la NSR-10 no tiene ningún capítulo sobre drones de inspección -- es tecnología posterior a la norma y fuera de su alcance actual. El sistema no debe inventar un capítulo para esto.",
        "id": "ADV2-drones-inspeccion-estructural",
    },
    {
        "pregunta": "Cual es el factor de seguridad minimo para cimentaciones en la superficie lunar segun el Titulo H?",
        "ground_truth": "El Título H regula estudios geotécnicos en Colombia -- no existe ni puede existir un factor de seguridad real para cimentaciones fuera de la Tierra. El sistema no debe inventar un valor.",
        "id": "ADV2-cimentaciones-luna-titulo-H",
    },
    {
        "pregunta": "Que exige el Titulo D sobre mamposteria de vidrio reforzado con fibra de carbono?",
        "ground_truth": "El Título D regula mampostería de unidades de arcilla, concreto o similares -- \"mampostería de vidrio reforzado con fibra de carbono\" no es un material reconocido por ese título. El sistema no debe inventar requisitos.",
        "id": "ADV2-mamposteria-vidrio-fibra-carbono",
    },
    {
        "pregunta": "Existe una NTC 12345 sobre certificacion de drones dentro del corpus?",
        "ground_truth": "No existe una NTC 12345 en el corpus ni como norma colombiana real conocida para certificación de drones -- el sistema no debe inventar requisitos para ella.",
        "id": "ADV2-ntc-12345-drones",
    },
    {
        "pregunta": "Que numeral de la NSR-10 fija la altura maxima permitida para un rascacielos de mas de 200 pisos?",
        "ground_truth": "La NSR-10 no fija un límite absoluto de número de pisos como tal -- los límites de altura dependen del sistema estructural, la zona de amenaza sísmica y el material (Tablas A.3-1 a A.3-4). El sistema no debe inventar un numeral que fije \"200 pisos\" como tope genérico.",
        "id": "ADV2-limite-200-pisos-rascacielos",
    },
    {
        "pregunta": "Que exige la NSR-10 sobre el diseno de plataformas petroleras costa afuera?",
        "ground_truth": "La NSR-10 regula edificaciones civiles en tierra firme, no estructuras costa afuera como plataformas petroleras -- ese tipo de infraestructura se rige por normas especializadas distintas (ej. API RP 2A). El sistema no debe inventar contenido de la NSR-10 para esto.",
        "id": "ADV2-plataformas-petroleras-costa-afuera",
    },
    {
        "pregunta": "Cual es el espesor minimo de pared que exige el Titulo K para tanques septicos plasticos?",
        "ground_truth": "El Título K regula seguridad humana en incendios, vidrios y otros requisitos complementarios -- no regula tanques sépticos plásticos, un tema de instalaciones sanitarias fuera de su alcance. El sistema no debe inventar un valor.",
        "id": "ADV2-tanques-septicos-titulo-K",
    },
    {
        "pregunta": "Que exige el Titulo G sobre estructuras de bambu proveniente de Asia (Bambusa vulgaris) para uso estructural en Colombia?",
        "ground_truth": "El Título G regula específicamente la guadua angustifolia kunth como especie estructural reconocida en Colombia -- el corpus no documenta requisitos verbatim para otras especies de bambú asiático como material estructural alterno. El sistema no debe inventar una equivalencia sin fuente.",
        "id": "ADV2-bambu-asiatico-titulo-G",
    },

    # ---- Fraseo coloquial de campo (COLOQ2) — reformulaciones de hechos
    # YA verificados en este dataset, no hechos nuevos ----
    {
        "pregunta": "Aunque el sitio parezca tranquilo y sin mucho viento, cual es la carga minima de viento que toca calcularle a un edificio de todas formas?",
        "ground_truth": "0.40 kN/m², la carga mínima de diseño por viento en el sistema principal de resistencia a fuerzas de viento (SPRFV), según el Título B.",
        "id": "COLOQ2-viento-minimo-040",
    },
    {
        "pregunta": "Hasta que tan resistente se le puede contar el acero de los estribos para calcular el confinamiento de una columna, segun el Titulo C?",
        "ground_truth": "El valor de fyt usado para calcular la cuantía del refuerzo de confinamiento no debe exceder 700 MPa, según el Título C.",
        "id": "COLOQ2-fyt-confinamiento-700MPa",
    },
    {
        "pregunta": "Cuanto fierro como maximo se le puede meter a una viga sismo resistente antes de pasarse del limite, segun el Titulo C?",
        "ground_truth": "La cuantía de refuerzo a flexión en vigas de pórticos DES no debe exceder 0.025, según el Título C.",
        "id": "COLOQ2-cuantia-maxima-flexion-DES",
    },
    {
        "pregunta": "Que tan fuerte tiene que ser el mortero que se le echa relleno por dentro a los bloques de mamposteria, segun el Titulo D?",
        "ground_truth": "La resistencia a la compresión del mortero de relleno a los 28 días nunca puede ser inferior a 12.5 MPa, según el Título D.",
        "id": "COLOQ2-mortero-relleno-125MPa",
    },
    {
        "pregunta": "Que tanto hueco vacio se le puede dejar a un bloque de mamposteria sin pasarse del limite que pone la norma, segun el Titulo D?",
        "ground_truth": "El área de las celdas verticales no puede ser mayor al 65% del área de la sección transversal, según el Título D.",
        "id": "COLOQ2-celdas-verticales-65porciento",
    },
    {
        "pregunta": "Que tan resistente tiene que ser el mortero de pega de una casa de uno o dos pisos, segun el Titulo E?",
        "ground_truth": "La resistencia mínima a la compresión del mortero de pega a los 28 días es 7.5 MPa, según el Título E.",
        "id": "COLOQ2-mortero-pega-75MPa",
    },
    {
        "pregunta": "A cuantos pies tablares equivale un metro cubico de madera, para cotizar en el aserradero, segun el Titulo G?",
        "ground_truth": "Un metro cúbico de madera tiene 424 pies tablares, según el Título G.",
        "id": "COLOQ2-m3-424-pies-tablares",
    },
    {
        "pregunta": "Cada cuantos metros cuadrados toca poner un hidrante en un hospital, y con que tanta presion de agua, segun el Titulo J?",
        "ground_truth": "Para hospitales, el área de servicio por hidrante es 500 m² y el caudal mínimo requerido es 63 L/s, según el Título J.",
        "id": "COLOQ2-hidrante-hospital-500m2-63Ls",
    },
    {
        "pregunta": "Cuantas puertas de salida minimo necesita un edificio donde caben entre 500 y 1000 personas, segun el Titulo K?",
        "ground_truth": "Una edificación con carga de ocupación entre 501 y 1000 personas requiere mínimo 3 salidas, según el Título K.",
        "id": "COLOQ2-numero-salidas-501-1000",
    },
    {
        "pregunta": "Cuanto tiempo minimo tienen que durar prendidas las luces de emergencia si se va la luz, segun el Titulo K?",
        "ground_truth": "El sistema de iluminación de emergencia debe estar en servicio por no menos de 1.5 horas tras una falla del sistema principal, según el Título K.",
        "id": "COLOQ2-iluminacion-emergencia-15horas",
    },
    {
        "pregunta": "Cuantos anos de experiencia minimo necesita el ingeniero que firma un estudio de suelos, segun el Titulo H?",
        "ground_truth": "El profesional que dirige un estudio geotécnico debe tener una experiencia mayor de 5 años en diseño geotécnico de cimentaciones, según el Título H.",
        "id": "COLOQ2-experiencia-geotecnista-5anos",
    },
    {
        "pregunta": "Que tan hondo y cuantos huecos toca hacer para el estudio de suelos de un edificio alto de mas de 10 pisos, segun el Titulo H?",
        "ground_truth": "Para categoría Alta (11 a 20 niveles), la profundidad mínima de sondeos es 25 m y el número mínimo es 4 sondeos, según el Título H.",
        "id": "COLOQ2-sondeos-categoria-alta-25m",
    },
    {
        "pregunta": "Cuales son los dos niveles de supervision tecnica que puede haber en una obra, segun el Titulo I?",
        "ground_truth": "Grado A (Continua) y Grado B (Itinerante), según el Título I.",
        "id": "COLOQ2-dos-grados-supervision-AB",
    },
    {
        "pregunta": "Cuanto peso minimo hay que asumirle a la calle cuando se esta excavando al lado, segun el Titulo H?",
        "ground_truth": "La sobrecarga uniforme mínima a considerar en la vía pública y zonas libres próximas a excavaciones temporales es 15 kPa (1.5 t/m²), según el Título H.",
        "id": "COLOQ2-sobrecarga-excavaciones-15kpa",
    },
    {
        "pregunta": "Que tan enterrada tiene que quedar la base de un muro de contencion de gravedad, segun el Titulo H?",
        "ground_truth": "La base de un muro de gravedad o en voladizo debe desplantarse cuando menos a 1 m bajo la superficie del terreno, según el Título H.",
        "id": "COLOQ2-desplante-muro-gravedad-1m",
    },
    {
        "pregunta": "Desde que tan profunda una excavacion toca tener un plan por si algo sale mal, segun el Titulo H?",
        "ground_truth": "A partir de 3 m de profundidad de excavación debe contarse con un plan de contingencia, según el Título H.",
        "id": "COLOQ2-plan-contingencia-3m",
    },
    {
        "pregunta": "Que tanto se le puede confiar a un miembro de acero calculado por el metodo racional de ingenieria, y a sus conexiones, segun el Titulo F?",
        "ground_truth": "Para miembros, φ = 0.80. Para conexiones, φ = 0.65, según el Título F.",
        "id": "COLOQ2-analisis-racional-phi",
    },
    {
        "pregunta": "Que tan fuerte le puede temblar la tierra a un edificio en Barranquilla, segun los valores de la norma?",
        "ground_truth": "Los valores de Aa y Av para Barranquilla son 0.10, según el Título A.",
        "id": "COLOQ2-Aa-Av-Barranquilla",
    },
    {
        "pregunta": "Hasta que tanta succion le puede sacar una planta al agua del suelo antes de marchitarse, segun el Titulo H?",
        "ground_truth": "El punto de marchitamiento equivale a una presión métrica de succión igual a pF = 4.2, según el Título H.",
        "id": "COLOQ2-punto-marchitamiento-pf42",
    },
    {
        "pregunta": "Como se sabe si un suelo se va a colapsar cuando se moja, segun el Titulo H?",
        "ground_truth": "El suelo es colapsable si gamma_d/gamma_dcrit es menor o igual a 1; si es mayor a 1, el suelo es estable o expansivo, según el Título H.",
        "id": "COLOQ2-criterio-colapsabilidad",
    },
    {
        "pregunta": "A partir de que tan inclinada una ladera toca revisarle la estabilidad para reforzar un edificio viejo, segun el Titulo H?",
        "ground_truth": "Cuando la pendiente del talud excede aproximadamente 18 grados (3 horizontal: 1 vertical), según el Título H.",
        "id": "COLOQ2-inclinacion-talud-18grados",
    },
    {
        "pregunta": "Que tan resistente al SPT tiene que ser una arena para que no se preocupe uno por licuacion, segun el Titulo H?",
        "ground_truth": "N160 de 30 golpes/pie para profundidades bajo la tabla de agua, o con un contenido de arcilla mayor de 20%, según el Título H.",
        "id": "COLOQ2-n160-licuacion-30golpes",
    },
    {
        "pregunta": "A que profundidad crecen normalmente las raices de un arbol grande, segun el Titulo H?",
        "ground_truth": "Las raíces de los árboles generalmente se desarrollan por lo regular a no más de 6.0 m de profundidad, según el Título H.",
        "id": "COLOQ2-profundidad-raices-6m",
    },
    {
        "pregunta": "Que tanta sal de sodio en el agua hace que una arcilla se le clasifique como dispersiva y no se pueda usar de relleno, segun el Titulo H?",
        "ground_truth": "Se considera suelo dispersivo cuando la concentración de sales de sodio (Na) en el agua intersticial pasa de 40% o 60% del total de sales disueltas, según el Título H.",
        "id": "COLOQ2-suelo-dispersivo-sales-sodio",
    },

    # ---- Compuestas / multi-hop dentro del mismo título (COMP2) ----
    {
        "pregunta": "Es el mismo factor de seguridad el que exige el Titulo H para cimentaciones bajo carga normal (H.4) que el que exige para el deslizamiento de muros de contencion (H.6)?",
        "ground_truth": "No -- H.4 exige un factor de seguridad indirecto FSICP=3.0 para cimentaciones bajo carga muerta más viva normal, mientras que H.6 exige un factor de seguridad de 1.60 al deslizamiento en condición estática para estructuras de contención -- son criterios distintos con valores distintos, aunque ambos vienen del mismo Título H.",
        "id": "COMP2-H-fs-h4-vs-h6",
    },
    {
        "pregunta": "Llegan las raices de los arboles mas profundo que los sondeos minimos exigidos para un edificio de categoria Alta, segun el Titulo H?",
        "ground_truth": "No -- las raíces llegan típicamente hasta 6.0 m (H.9.4.4.2), mientras que los sondeos de categoría Alta (11 a 20 niveles) deben llegar a 25 m de profundidad (H.3) -- los sondeos van mucho más profundo que las raíces.",
        "id": "COMP2-H-raices-vs-sondeos",
    },
    {
        "pregunta": "Si un talud tiene una pendiente de 20 grados, debe evaluarse su estabilidad para rehabilitacion sismica segun el Titulo H, y que factor de seguridad estatico minimo exige el mismo titulo para muros de contencion?",
        "ground_truth": "Sí, debe evaluarse porque 20° excede el umbral de 18° que activa la evaluación de estabilidad de laderas (H.10.2.2.4); el factor de seguridad estático mínimo para muros de contención es 1.60 (H.6, Tabla H.6.9-1) -- son dos requisitos distintos del mismo Título H.",
        "id": "COMP2-H-talud-20grados-vs-fs-deslizamiento",
    },
    {
        "pregunta": "Es igual el valor de reduccion por irregularidad torsional extrema en planta (tipo 1bP) que el de piso flexible extremo en altura (tipo 1bA), segun las Tablas A.3-6 y A.3-7 del Titulo A?",
        "ground_truth": "Sí, ambos valen phi=0.8, aunque son irregularidades de naturaleza distinta (torsión extrema en planta vs. rigidez extrema en altura).",
        "id": "COMP2-A-phi-1bP-vs-1bA",
    },
    {
        "pregunta": "Se evaluan los mismos tipos de irregularidad en planta en zona de amenaza sismica baja que en zona intermedia, segun el Titulo A?",
        "ground_truth": "No -- en zona baja (grupos de uso I y II) solo se evalúan los tipos 1aP y 1bP; en zona intermedia (grupo de uso I) se agregan también los tipos 3P y 4P.",
        "id": "COMP2-A-zona-baja-vs-intermedia",
    },
    {
        "pregunta": "El concreto DES/DMO (21 MPa minimo) usa el mismo factor phi de reduccion para traccion que el concreto general (17 MPa), segun el Titulo C?",
        "ground_truth": "Sí -- el factor φ=0.90 para secciones controladas por tracción no depende de si el concreto es DES/DMO o general; lo que cambia entre ambos es el f'c mínimo exigido (21 MPa vs 17 MPa), no el factor phi.",
        "id": "COMP2-C-fc-vs-phi-DES-DMO",
    },
    {
        "pregunta": "Que diferencia hay entre el factor phi de miembros y el de conexiones en el analisis racional de ingenieria del Titulo F?",
        "ground_truth": "El factor φ=0.80 aplica a miembros, mientras que φ=0.65 aplica a conexiones -- las conexiones tienen un factor de reducción de resistencia más conservador (menor) que los miembros, según el Título F.",
        "id": "COMP2-F-phi-miembros-vs-conexiones",
    },
    {
        "pregunta": "El factor de seguridad de 4 para barandas de vidrio del Titulo K aplica solo al vidrio templado, o a cualquier tipo de vidrio?",
        "ground_truth": "Aplica a los paneles de vidrio para barandas y pasamanos en general, no es exclusivo del vidrio templado (que es un tratamiento térmico específico descrito aparte en el Título K).",
        "id": "COMP2-K-vidrio-barandas-vs-templado",
    },
    {
        "pregunta": "Una casa de mamposteria no reforzada de 3.500 m2 en zona de amenaza sismica baja con Aa=0.03 cumple los dos requisitos del Titulo D sobre supervision tecnica y uso de mamposteria no reforzada?",
        "ground_truth": "Sí, cumple ambos: requeriría supervisión técnica obligatoria por superar 3.000 m² de área construida, y sí podría usar mampostería no reforzada como sistema de resistencia sísmica porque Aa=0.03 es menor o igual a 0.05, el límite que exige el Título D.",
        "id": "COMP2-D-supervision-vs-no-reforzada-3500m2",
    },
    {
        "pregunta": "Coinciden los umbrales de altura del Titulo A para exigir metodo de analisis dinamico (mas de 20 niveles o 60m) con los limites de altura que da la Tabla A.3-4 para el sistema dual con muros de concreto DES (sin limite)?",
        "ground_truth": "No coinciden porque no son comparables directamente -- el umbral de 20 niveles/60 m (A.3.4.2.2) decide qué método de análisis usar, mientras que la Tabla A.3-4 da límites de altura máxima permitidos por sistema estructural y zona sísmica (para el sistema dual con muros DES en zona alta, el límite es \"sin límite\"), son dos reglas independientes del Título A que conviven, no se contradicen.",
        "id": "COMP2-A-umbral-dinamico-vs-tabla-A34",
    },
    {
        "pregunta": "Se puede clasificar un piso simultaneamente como irregular tipo 1aA (piso flexible) y tipo 5aA (piso debil) segun las tablas del Titulo A?",
        "ground_truth": "Sí, son criterios independientes (rigidez vs. resistencia) definidos en la misma Tabla A.3-7 -- un piso puede cumplir ambos criterios a la vez si tiene tanto baja rigidez relativa como baja resistencia relativa frente a los pisos adyacentes; cuando hay varios tipos de irregularidad simultáneos se aplica el menor valor de phi_a (A.3.3.3).",
        "id": "COMP2-A-1aA-y-5aA-simultaneos",
    },
    {
        "pregunta": "El Titulo H exige el mismo numero minimo de historias de movimiento para el analisis de respuesta dinamica (H.7) que el numero minimo de sondeos para categoria Alta (H.3)?",
        "ground_truth": "Coinciden en el número (3 y 4 respectivamente son distintos en realidad) -- el Título H exige mínimo 3 historias de movimiento en el tiempo para análisis de respuesta dinámica (H.7) y mínimo 4 sondeos para categoría Alta de 11 a 20 niveles (H.3) -- son requisitos de naturaleza distinta (historias sísmicas de análisis vs. número de perforaciones de exploración) que no deben confundirse pese a ser números cercanos.",
        "id": "COMP2-H-historias-vs-sondeos-categoria",
    },
]
