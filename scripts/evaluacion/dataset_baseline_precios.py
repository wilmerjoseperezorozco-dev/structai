"""
Dataset de evaluación RAGAS — precios/APU (rag_multi_norma.ask_precios()).

Mismo criterio que dataset_baseline_nsr10.py: cada `ground_truth` es una
frase corta con un hecho REAL, extraído con SQL directo contra Supabase
(nunca inventado) antes de escribirse aquí -- no una redacción "ideal"
completa de lo que debería responder el sistema.

Cubre las 4 ramas reales del RPC buscar_precios_apu() (actividad/insumo/
proveedor regional/proveedor nacional), más 2 categorías nuevas pensadas
para medir cosas que hoy no mide ningún test de precios:

- ADVERSARIAL (materiales/actividades que no existen en la base): la
  búsqueda híbrida (texto completo + trigram, umbral 0.2) NO devuelve
  cero resultados para estas preguntas -- devuelve coincidencias parciales
  de texto sobre palabras comunes (ej. "concreto de kriptonita" trae
  "Motobomba de concreto", por la palabra "concreto"). Verificado en vivo
  contra producción antes de escribir el ground_truth: el LLM sí reconoce
  que ninguno de esos resultados es el material preguntado y responde que
  no tiene el precio, en vez de inventar uno o presentar el resultado
  suelto como si fuera la respuesta -- el ground_truth de estas 5
  preguntas refleja ESE comportamiento correcto observado, no una
  suposición de "debería fallar".
- COLOQUIAL/SINÓNIMOS: reusa directamente SINONIMOS_CONSTRUCCION (agregado
  2026-09-03, commit 6bef90f) -- pregunta con el término regional que el
  usuario típicamente escribiría, ground_truth con el precio real
  guardado bajo el término técnico/distinto que la expansión de
  sinónimos debe encontrar. Cada par (ej. "cabilla" -> "varilla") se
  verificó con SQL directo (conteo de filas por cada término) antes de
  escribirse -- no todos los grupos de SINONIMOS_CONSTRUCCION tienen
  ambos términos presentes en la base hoy, solo se usan aquí los que sí.

Pendiente (Paso 3 del plan de Fase 4, no antes): 5 preguntas de desglose
jerárquico actividad→insumo, una vez implementado
obtener_desglose_actividad() -- agregar aquí después de esa migración,
no antes, para poder medir su impacto real comparando el RAGAS "antes"
(este dataset) contra el "después".
"""

CASOS_BASELINE_PRECIOS = [
    # ---- Tipo 'actividad' (apu_precios_referencia, Barranquilla/Atlántico) ----
    {
        "pregunta": "Cuanto cuesta el cielo raso duracustic en Barranquilla?",
        "ground_truth": "El cielo raso Duracustic cuesta $33.183 COP por m² en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-cielo-raso-duracustic",
    },
    {
        "pregunta": "Cual es el precio de entrepisos placalista?",
        "ground_truth": "Los entrepisos Placalista cuestan $50.575 COP por m² en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-entrepisos-placalista",
    },
    {
        "pregunta": "Cuanto vale el relleno con gravilla de rio en Barranquilla?",
        "ground_truth": "El relleno con gravilla de río cuesta $51.557 COP por m³ en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-relleno-gravilla-rio",
    },
    {
        "pregunta": "Que precio tiene la pulida y lacada de piso de madera?",
        "ground_truth": "La pulida lacada de piso de madera cuesta $35.367 COP por m² en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-pulida-lacada-piso-madera",
    },
    {
        "pregunta": "Cuanto cuesta aplicar anticorrosivo sobre lamina llena?",
        "ground_truth": "Aplicar anticorrosivo sobre lámina llena cuesta $10.262 COP por m² en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-anticorrosivo-lamina-llena",
    },
    {
        "pregunta": "Cual es el precio del tablon liso 33x33?",
        "ground_truth": "El tablón liso 33x33 cuesta $31.616 COP por m² en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-tablon-liso-33x33",
    },
    {
        "pregunta": "Cuanto vale instalar teja transparente numero 6?",
        "ground_truth": "Instalar teja transparente No. 6 cuesta $27.477 COP por m² en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-teja-transparente-no6",
    },
    {
        "pregunta": "Que precio tiene el zocalo en marmol travertino de 7.3 cm?",
        "ground_truth": "El zócalo en mármol travertino de 7.3 cm cuesta $10.880 COP por metro lineal en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-zocalo-marmol-travertino",
    },
    {
        "pregunta": "Cuanto cuesta el pasamanos de escalera .15x.02?",
        "ground_truth": "El pasamanos de escalera .15x.02 cuesta $26.658 COP por metro lineal en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-pasamanos-escalera",
    },
    {
        "pregunta": "Cual es el precio de una valvula de bola para medidor?",
        "ground_truth": "La válvula de bola para medidor cuesta $12.418 COP por unidad en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-valvula-bola-medidor",
    },
    {
        "pregunta": "Cuanto vale la conexion de un tanque elevado en PVC?",
        "ground_truth": "La conexión de tanque elevado en PVC cuesta $339.628 COP por unidad en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-conexion-tanque-elevado-pvc",
    },
    {
        "pregunta": "Que precio tienen las camaras electricas dobles?",
        "ground_truth": "Las cámaras eléctricas dobles cuestan $410.181 COP por unidad en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-camaras-electricas-dobles",
    },
    {
        "pregunta": "Cuanto cuesta una viga tee 25x25x20x50?",
        "ground_truth": "La viga tee 25x25x20x50 cuesta $410.920 COP por m³ en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-viga-tee",
    },
    {
        "pregunta": "Cual es el precio de una tapa de sumidero de 95x45?",
        "ground_truth": "La tapa de sumidero de 95x45 cuesta $296.666 COP por unidad en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-tapa-sumidero-95x45",
    },
    {
        "pregunta": "Cuanto vale un codo de calle galvanizado de 1/2 pulgada?",
        "ground_truth": "El codo de calle galvanizado de 1/2\" cuesta $3.879 COP por unidad en Barranquilla (Catálogo Construdata).",
        "id": "precio-actividad-codo-calle-galvanizado",
    },
    # ---- Tipo 'insumo' (apu_insumos_referencia) ----
    {
        "pregunta": "Cuanto cuesta el kilo de acero corrugado figurado de 1/4 a 1 pulgada, 60000 PSI?",
        "ground_truth": "El acero corrugado figurado 1/4\"-1\" de 60.000 PSI cuesta $2.617,87 COP por kg (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-acero-corrugado-60000psi",
    },
    {
        "pregunta": "Cual es el precio del metro cubico de arena de rio en Barranquilla?",
        "ground_truth": "La arena de río cuesta $70.000 COP por m³ en Barranquilla (Catálogo Construdata).",
        "id": "precio-insumo-arena-rio",
    },
    {
        "pregunta": "Cuanto vale la arena amarilla de Puerto Colombia?",
        "ground_truth": "La arena amarilla de Puerto Colombia cuesta $15.000 COP por m³ (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-arena-amarilla-puerto-colombia",
    },
    {
        "pregunta": "Cuanto cuesta la hora de un ayudante de albañileria?",
        "ground_truth": "La hora de ayudante de albañilería (A) cuesta $2.461 COP (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-ayudante-albanileria",
    },
    {
        "pregunta": "Que precio tiene el metro cuadrado de baldosa alfa L1 de 33x33?",
        "ground_truth": "La baldosa Alfa L1 33x33 cuesta $30.160,19 COP por m² (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-baldosa-alfa-l1",
    },
    {
        "pregunta": "Cuanto vale un bloque de concreto de 20x20x40?",
        "ground_truth": "El bloque de concreto 20x20x40 cuesta $2.050,04 COP por unidad (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-bloque-concreto-20x20x40",
    },
    {
        "pregunta": "Cuanto cuesta un adaptador macho de presion PVC de 1/2 pulgada?",
        "ground_truth": "El adaptador macho presión PVC de 1/2\" cuesta $336 COP por unidad (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-adaptador-macho-pvc",
    },
    {
        "pregunta": "Cual es el precio del galon de ACPM en Barranquilla?",
        "ground_truth": "El galón de A.C.P.M. en Barranquilla cuesta $3.731,82 COP (Catálogo Construdata).",
        "id": "precio-insumo-acpm-barranquilla",
    },
    {
        "pregunta": "Cuanto vale una abrazadera colgante horizontal de 4 pulgadas?",
        "ground_truth": "La abrazadera colgante horizontal de 4\" cuesta $7.558 COP por unidad (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-abrazadera-colgante-4pulg",
    },
    {
        "pregunta": "Cuanto cuesta una bajante PVC blanco de extremo liso de 3 metros?",
        "ground_truth": "La bajante PVC blanco extremo liso de 3 m cuesta $65.057,58 COP por unidad (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-bajante-pvc-3m",
    },
    {
        "pregunta": "Cual es el precio del metro de alambre telefonico 2x22 AWG trenzado?",
        "ground_truth": "El alambre telefónico JWTPVC 2x22 AWG trenzado cuesta $615 COP por metro (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-alambre-telefonico-2x22awg",
    },
    {
        "pregunta": "Cuanto vale el metro cubico de arena de peña?",
        "ground_truth": "La arena de peña cuesta $28.940 COP por m³ (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-arena-de-pena",
    },
    {
        "pregunta": "Que precio tiene la base de arena cemento 1:20?",
        "ground_truth": "La base arena cemento 1:20 cuesta $53.400 COP por m³ (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-base-arena-cemento-1-20",
    },
    {
        "pregunta": "Cuanto cuesta un bloque de concreto de 10x20x40?",
        "ground_truth": "El bloque de concreto 10x20x40 cuesta $834,97 COP por unidad (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-bloque-concreto-10x20x40",
    },
    {
        "pregunta": "Cuanto cuesta la hora cuadrilla DD de mano de obra?",
        "ground_truth": "La hora cuadrilla DD de mano de obra cuesta $13.051,74 COP (Catálogo Construdata, Barranquilla).",
        "id": "precio-insumo-mano-obra-dd",
    },
    # ---- Tipo 'proveedor' (apu_proveedores_catalogo, regional Barranquilla) ----
    {
        "pregunta": "Cuanto cuesta un viaje de triturado de 3/4 pulgada a granel en Homecenter?",
        "ground_truth": "El triturado de 3/4\" a granel (viaje x 8 m³) cuesta $791.900 COP en Homecenter Colombia, Barranquilla.",
        "id": "precio-proveedor-triturado-homecenter",
    },
    {
        "pregunta": "Cuanto vale un candado estandar de 30mm en Ferreteria Samir?",
        "ground_truth": "El candado estándar de 30mm cuesta $43.366 COP en Ferretería Samir, Barranquilla.",
        "id": "precio-proveedor-candado-samir",
    },
    {
        "pregunta": "Cual es el precio del cemento gris Ultracem Ecocem de 50kg en Homecenter?",
        "ground_truth": "El cemento gris Ultracem Ecocem de 50kg cuesta $44.900 COP en Homecenter Colombia, Barranquilla.",
        "id": "precio-proveedor-cemento-ultracem-homecenter",
    },
    {
        "pregunta": "Cuanto cuesta el saco de cemento Argos gris de 50kg en Homecenter?",
        "ground_truth": "El saco de cemento Argos gris de 50kg cuesta $32.500 COP en Homecenter Colombia, Barranquilla.",
        "id": "precio-proveedor-cemento-argos-homecenter",
    },
    {
        "pregunta": "Que precio tiene el casco de seguridad Bunker blanco dielectrico?",
        "ground_truth": "El casco de seguridad Bunker blanco dieléctrico cuesta $31.900 COP en Homecenter Colombia, Barranquilla.",
        "id": "precio-proveedor-casco-bunker-homecenter",
    },
    # ---- Tipo 'proveedor_nacional' (IAD MIPYMES, comparación entre proveedores reales de todo el país) ----
    {
        "pregunta": "Cual es el mejor precio nacional de un codo de 90 grados en acero galvanizado de 1 1/4 pulgada?",
        "ground_truth": "El mejor precio real es $5.000 COP con Angel Rafael Rincón Mariño (Ferretería Nicholson), comparado entre 60 proveedores mipyme reales (rango $5.000–$273.200 COP).",
        "id": "precio-nacional-codo-acero-galvanizado",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de un adaptador PVC presion hembra de 2 1/2 pulgadas?",
        "ground_truth": "El mejor precio real es $6.500 COP con Luis Álvaro Gómez López (Ferremateriales El Triunfo), comparado entre 64 proveedores mipyme reales (rango $6.500–$69.502,08 COP).",
        "id": "precio-nacional-adaptador-pvc-hembra",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de una brocha de pintura de pared de 3 pulgadas con cerda china negra?",
        "ground_truth": "El mejor precio real es $7.853 COP con Martínez Muñoz Ingeniería Zomac SAS (Florencia, Caquetá), comparado entre 62 proveedores mipyme reales.",
        "id": "precio-nacional-brocha-pintura-3pulg",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de puntillas con cabeza de 2 1/2 pulgadas?",
        "ground_truth": "El mejor precio real es $3.006,33 COP con Elmer Schneider Casa Andina SAS (Pasto, Nariño), comparado entre 62 proveedores mipyme reales.",
        "id": "precio-nacional-puntillas-2-5pulg",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de vinilo blanco exterior color institucional en cuñete de 5 galones?",
        "ground_truth": "El mejor precio real es $180.811 COP con Angel Rafael Rincón Mariño (Ferretería Nicholson), comparado entre 65 proveedores mipyme reales.",
        "id": "precio-nacional-vinilo-blanco-exterior",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de pintura verde oliva en cuñete de 5 galones?",
        "ground_truth": "El mejor precio real es $238.173,10 COP con Ferconlog S.A.S., comparado entre 64 proveedores mipyme reales.",
        "id": "precio-nacional-pintura-verde-oliva",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de tubo sanitario en PVC de 3 pulgadas por 6 metros?",
        "ground_truth": "El mejor precio real es $39.281,60 COP con Grupo Empresarial LCS SAS, comparado entre 56 proveedores mipyme reales.",
        "id": "precio-nacional-tubo-sanitario-pvc-3pulg",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de un bombillo ahorrador de 65W espiral luz fria?",
        "ground_truth": "El mejor precio real es $22.500 COP con Edgar Carpio Solano (Comercial Piolín Villa del Rosario, Cúcuta, Norte de Santander), comparado entre 63 proveedores mipyme reales.",
        "id": "precio-nacional-bombillo-ahorrador-65w",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de una brocha de 4 pulgadas con cerdas naturales chinas blancas?",
        "ground_truth": "El mejor precio real es $6.312 COP con Elmer Schneider Casa Andina SAS (Pasto, Nariño), comparado entre 70 proveedores mipyme reales.",
        "id": "precio-nacional-brocha-4pulg-cerdas-naturales",
    },
    {
        "pregunta": "Cual es el mejor precio nacional de un niple en tubo de acero galvanizado a presion de 4 pulgadas por 18cm?",
        "ground_truth": "El mejor precio real es $45.934,29 COP con Valentus S.A.S. (Bucaramanga, Santander), comparado entre 56 proveedores mipyme reales.",
        "id": "precio-nacional-niple-acero-galvanizado-4pulg",
    },
    # ---- Adversarial: material/actividad que NO existe en la base ----
    # Verificado en vivo (2026-09-07) que ask_precios() NO alucina un precio
    # para ninguno de estos, pese a que la búsqueda trigram sí devuelve
    # resultados sueltos por coincidencia parcial de palabras comunes.
    {
        "pregunta": "Cuanto cuesta el concreto de kriptonita en Barranquilla?",
        "ground_truth": "No existe un precio real para 'concreto de kriptonita' en la base de datos -- el sistema no debe inventar un precio ni presentar un resultado parcialmente relacionado (ej. 'motobomba de concreto') como si fuera la respuesta.",
        "id": "precio-adversarial-concreto-kriptonita",
    },
    {
        "pregunta": "Que precio tiene la pintura invisible antifantasmas?",
        "ground_truth": "No existe un precio real para 'pintura invisible antifantasmas' en la base de datos -- el sistema no debe inventar un precio ni confundirlo con otra pintura real (ej. 'pintura anticorrosiva').",
        "id": "precio-adversarial-pintura-invisible",
    },
    {
        "pregunta": "Cuanto vale un sensor cuantico de humedad para concreto?",
        "ground_truth": "No existe un precio real para 'sensor cuántico de humedad para concreto' en la base de datos -- es un producto ficticio, el sistema no debe inventar un precio.",
        "id": "precio-adversarial-sensor-cuantico-humedad",
    },
    {
        "pregunta": "Cuanto cuesta una grapa autoadhesiva de diamante sintetico?",
        "ground_truth": "No existe un precio real para 'grapa autoadhesiva de diamante sintético' en la base de datos -- el sistema no debe inventar un precio ni confundirlo con otro insumo real (ej. 'disco diamante').",
        "id": "precio-adversarial-grapa-diamante-sintetico",
    },
    {
        "pregunta": "Cual es el precio de un ladrillo de titanio reforzado?",
        "ground_truth": "No existe un precio real para 'ladrillo de titanio reforzado' en la base de datos -- es un material ficticio, el sistema no debe inventar un precio.",
        "id": "precio-adversarial-ladrillo-titanio",
    },
    # ---- Coloquial / sinónimos regionales (SINONIMOS_CONSTRUCCION, commit 6bef90f) ----
    # Cada par se verificó con conteo SQL real antes de escribirse: el
    # término coloquial de la pregunta tiene pocas o cero filas reales, el
    # término técnico que trae la expansión de sinónimos sí tiene filas.
    {
        "pregunta": "Cuanto cuesta el friso en Barranquilla?",
        "ground_truth": "No hay filas guardadas literalmente como 'friso', pero la expansión de sinónimos debe encontrar precios reales guardados como 'revoque' (ej. 'REVOQUE LISO MUROS 1:4', 'ARENA DE REVOQUE') -- mismo concepto de obra con otro nombre.",
        "id": "precio-coloquial-friso-revoque",
    },
    {
        "pregunta": "Cuanto vale la cimbra para una placa de concreto?",
        "ground_truth": "No hay filas guardadas como 'cimbra', pero la expansión de sinónimos debe encontrar la fila real guardada como 'encofrado' (mismo concepto, término distinto).",
        "id": "precio-coloquial-cimbra-encofrado",
    },
    {
        "pregunta": "Cuanto cuesta hacer una vereda en concreto?",
        "ground_truth": "El término real predominante en la base es 'andén' (162 filas reales), no 'vereda' -- la expansión de sinónimos debe encontrar esas filas de andén al buscar 'vereda'.",
        "id": "precio-coloquial-vereda-anden",
    },
    {
        "pregunta": "Cuanto cuesta el kilo de cabilla de 5/8?",
        "ground_truth": "No hay ningún insumo guardado como 'cabilla' -- la expansión de sinónimos debe encontrar el precio real guardado como 'varilla' (ej. $6.000 COP/kg, Catálogo Construdata).",
        "id": "precio-coloquial-cabilla-varilla",
    },
    {
        "pregunta": "Cuanto cobra un capataz de obra por dia en Barranquilla?",
        "ground_truth": "No hay ningún insumo guardado como 'capataz' -- la expansión de sinónimos debe encontrar el precio real guardado como 'Maestro' ($4.377.262,50 COP, Catálogo Construdata, sin unidad especificada en el registro original).",
        "id": "precio-coloquial-capataz-maestro",
    },
]
