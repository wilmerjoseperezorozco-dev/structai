"""
══════════════════════════════════════════════════════════════
SEED NTC + SEGURIDAD INDUSTRIAL → Supabase pgvector
Base de conocimiento para RAG multi-norma (ingeniería civil CO)
══════════════════════════════════════════════════════════════
Uso:
  pip install openai supabase python-dotenv --break-system-packages
  export OPENAI_API_KEY=sk-...
  export SUPABASE_URL=https://xxx.supabase.co
  export SUPABASE_SERVICE_KEY=eyJ...
  python seed_ntc_knowledge.py

Tabla objetivo: public.ntc_chunks (id bigserial, norma, seccion, titulo,
contenido, embedding vector(1536)) — consultada por search_knowledge() junto
con nsr10_chunks. knowledge_nodes/knowledge_chunks/knowledge_edges (el diseño
original de este script) NUNCA existieron en el proyecto Supabase real; ese
esquema quedó abandonado en migration_ntc.sql. seed_nodes()/seed_edges() se
dejan como referencia pero no se ejecutan — no hay tabla de grafo de
dependencias en el esquema vigente.
"""

import os, uuid, json, time
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

load_dotenv()

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

# ─── CHUNKS EXTRAÍDOS DE GOOGLE DRIVE ─────────────────────────────────────────
# Fuente: 20 Google Docs en carpeta Drive NTC Barranquilla 2026
# Estructura: {id, norma, capitulo, titulo, contenido, aplica_a, tags}

NTC_CHUNKS = [
  # ── NTC 673 — Resistencia a compresión ──────────────────────────────────────
  {"id":"NTC673_01","capitulo":3,"norma":"NTC 673","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece el método de ensayo para determinar la resistencia a la compresión de especímenes cilíndricos de concreto, tanto para cilindros moldeados como para núcleos perforados. Es el ensayo fundamental para verificar que el concreto cumple con la resistencia especificada en el diseño (f'c).",
   "aplica_a":["control_calidad","concreto_endurecido","resistencia_compresion"],"tags":["objeto","alcance","cilindros","nucleos"]},
  {"id":"NTC673_02","capitulo":3,"norma":"NTC 673","titulo":"Correspondencia y actualización",
   "contenido":"La NTC 673 es una adopción idéntica (IDT) de la norma ASTM C39:2005. Cuenta con Tercera actualización (2010-02-17) y Cuarta actualización (2021). Se recomienda verificar la versión vigente en el catálogo de ICONTEC.",
   "aplica_a":["actualizacion_norma","correspondencia"],"tags":["ASTM_C39","tercera_actualizacion","cuarta_actualizacion","2021"]},
  {"id":"NTC673_03","capitulo":3,"norma":"NTC 673","titulo":"Descriptores de la norma",
   "contenido":"Los descriptores de la NTC 673 son: cilindro de concreto; producto de concreto; ensayo compresión; ensayo mecánico. Código ICS: 91.100.30.",
   "aplica_a":["definiciones","clasificacion"],"tags":["cilindro","compresion","mecanico","ICS_91.100.30"]},
  {"id":"NTC673_04","capitulo":3,"norma":"NTC 673","titulo":"Procedimiento - Preparación de especímenes",
   "contenido":"Se toman muestras de concreto fresco (según NTC 454) y se moldean cilindros. Los cilindros se curan en condiciones controladas (temperatura y humedad) hasta la edad de ensayo (generalmente 7, 14 o 28 días). Los extremos se refrentan para obtener superficies planas y paralelas.",
   "aplica_a":["procedimiento_ensayo","preparacion_muestras"],"tags":["muestreo","curado","refrentado","edades"]},
  {"id":"NTC673_05","capitulo":3,"norma":"NTC 673","titulo":"Procedimiento - Aplicación de carga y medición",
   "contenido":"Se aplica una carga axial de compresión a los especímenes a una velocidad controlada. Se registra la carga máxima aplicada antes de la falla del espécimen. La resistencia se calcula dividiendo la carga máxima por el área de la sección transversal del cilindro.",
   "aplica_a":["procedimiento_ensayo","ejecucion_ensayo"],"tags":["carga_axial","velocidad","falla","calculo"]},
  {"id":"NTC673_06","capitulo":3,"norma":"NTC 673","titulo":"Expresión de resultados",
   "contenido":"La resistencia a la compresión se expresa en MPa (megapascales) o kgf/cm², y se reporta con una precisión de 0.1 MPa (o 1 kgf/cm²).",
   "aplica_a":["resultados","reportes"],"tags":["MPa","kgf/cm2","precision"]},
  {"id":"NTC673_07","capitulo":3,"norma":"NTC 673","titulo":"Importancia en control de calidad",
   "contenido":"La resistencia a la compresión es la característica mecánica principal del concreto. Los resultados se utilizan para la aceptación o rechazo del concreto en obra. La frecuencia de muestreo y ensayo se define según la NSR-10 y las especificaciones del proyecto.",
   "aplica_a":["control_calidad","apus","especificaciones_obra"],"tags":["f'c","aceptacion","rechazo","NSR10"]},
  {"id":"NTC673_08","capitulo":3,"norma":"NTC 673","titulo":"Normas complementarias",
   "contenido":"Para la aplicación de la NTC 673 deben consultarse: NTC 454 (Toma de muestras de concreto fresco), NTC 550 (Elaboración y curado de especímenes), NTC 504 (Refrentado de especímenes cilíndricos) y NSR-10 C.5 (Requisitos de calidad del concreto).",
   "aplica_a":["normas_complementarias","referencias"],"tags":["NTC454","NTC550","NTC504","NSR10"]},

  # ── NTC 396 — Asentamiento concreto ─────────────────────────────────────────
  {"id":"NTC396_01","capitulo":2,"norma":"NTC 396","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece el método de ensayo para determinar el asentamiento del concreto de cemento hidráulico en la obra y en el laboratorio. El asentamiento es una medida de la consistencia del concreto, que indica el grado de fluidez de la mezcla.",
   "aplica_a":["control_calidad","concreto_fresco","ensayos_obra"],"tags":["objeto","alcance","asentamiento","consistencia"]},
  {"id":"NTC396_02","capitulo":2,"norma":"NTC 396","titulo":"Correspondencia y actualización",
   "contenido":"La NTC 396 es una adopción modificada de la ASTM C143/C143M-2020. Cuenta con Tercera Actualización (2021) y una actualización en abril de 2024 que incluye el Cono de Bedoya como alternativa aceptada.",
   "aplica_a":["actualizacion_norma","correspondencia"],"tags":["ASTM_C143","tercera_actualizacion","Cono_Bedoya","2024"]},
  {"id":"NTC396_03","capitulo":2,"norma":"NTC 396","titulo":"Equipo - Cono de Abrams",
   "contenido":"El molde para el ensayo de asentamiento es un tronco de cono metálico con dimensiones: diámetro inferior (base) 200 mm, diámetro superior 100 mm, y altura 300 mm.",
   "aplica_a":["equipo_ensayo","cono_abrams"],"tags":["molde","dimensiones","tronco_cono"]},
  {"id":"NTC396_06","capitulo":2,"norma":"NTC 396","titulo":"Procedimiento - Preparación y llenado",
   "contenido":"Se llena el molde en tres capas, cada una de aproximadamente un tercio del volumen del molde. Cada capa se compacta con 25 golpes de la varilla compactadora.",
   "aplica_a":["procedimiento_ensayo","ejecucion_ensayo"],"tags":["preparacion","llenado","capas"]},
  {"id":"NTC396_08","capitulo":2,"norma":"NTC 396","titulo":"Medición del asentamiento",
   "contenido":"Después de enrasar y retirar el molde verticalmente, se mide la diferencia entre la altura del molde y la altura del punto más alto del concreto abatido. La medición se realiza con una aproximación de 5 mm.",
   "aplica_a":["procedimiento_ensayo","medicion"],"tags":["medicion","asentamiento","aproximacion"]},
  {"id":"NTC396_10","capitulo":2,"norma":"NTC 396","titulo":"Asentamientos recomendados por elemento",
   "contenido":"Valores de asentamiento según el elemento estructural: columnas y vigas: 75-100 mm; losas y placas: 50-100 mm; concreto bombeado: 100-150 mm; zapatas y cimentaciones: 25-75 mm.",
   "aplica_a":["apus","dosificacion","especificaciones_obra"],"tags":["asentamiento","recomendaciones","elementos"]},

  # ── NTC 174 — Agregados para concreto ───────────────────────────────────────
  {"id":"NTC174_01","capitulo":1,"norma":"NTC 174","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos de gradación y calidad para los agregados finos y gruesos para uso en concreto. Es equivalente (EQV) a la ASTM C 33, con desviaciones técnicas menores.",
   "aplica_a":["agregados","concreto","seleccion_materiales"],"tags":["objeto","alcance","ASTM_C33"]},
  {"id":"NTC174_02","capitulo":1,"norma":"NTC 174","titulo":"Definición de agregado fino",
   "contenido":"El agregado fino debe estar compuesto de arena natural, arena triturada, u otro agregado reciclado. Es el material que pasa la malla 9.5 mm (No. 3/8') y es predominantemente retenido en la malla 75 μm (No. 200).",
   "aplica_a":["agregado_fino","arena","clasificacion"],"tags":["definicion","arena","tamiz"]},
  {"id":"NTC174_03","capitulo":1,"norma":"NTC 174","titulo":"Definición de agregado grueso",
   "contenido":"El agregado grueso debe estar compuesto de grava, grava triturada, roca triturada, escoria de alto horno o concreto triturado. Posee un tamaño superior al tamiz No. 4 (4.76 mm).",
   "aplica_a":["agregado_grueso","grava","clasificacion"],"tags":["definicion","grava","tamiz"]},
  {"id":"NTC174_04","capitulo":1,"norma":"NTC 174","titulo":"Módulo de finura del agregado fino",
   "contenido":"El módulo de finura del agregado fino debe ser mayor que 2.3, pero menor que 3.1. Para despachos continuos, el módulo de finura no debe variar en más de 0.20 del módulo base.",
   "aplica_a":["agregado_fino","modulo_finura","control_calidad"],"tags":["finura","granulometria","control"]},
  {"id":"NTC174_06","capitulo":1,"norma":"NTC 174","titulo":"Sustancias perjudiciales - Agregado fino",
   "contenido":"Límites de sustancias perjudiciales en agregado fino: terrones de arcilla: máximo 3.0%; material que pasa tamiz No. 200 en concreto sujeto a abrasión: máximo 3.0%; en otros concretos: máximo 5.0%; carbón o lignito: máximo 1.0%.",
   "aplica_a":["agregado_fino","sustancias_perjudiciales","control_calidad"],"tags":["arcilla","tamiz_200","carbono","limites"]},

  # ── NTC 30 — Clasificación cemento Portland ──────────────────────────────────
  {"id":"NTC30_01","capitulo":1,"norma":"NTC 30","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece la clasificación y nomenclatura de los Cementos Portland de acuerdo con sus cualidades y usos. Código ICS: 91.100.10.",
   "aplica_a":["cemento_portland","clasificacion_cemento","nomenclatura"],"tags":["objeto","alcance","clasificacion"]},
  {"id":"NTC30_02","capitulo":1,"norma":"NTC 30","titulo":"Cemento Portland Tipo 1",
   "contenido":"Es el destinado a obras de hormigón en general, al que no se le exigen propiedades especiales.",
   "aplica_a":["cemento_tipo1","seleccion_cemento","uso_general"],"tags":["tipo_1","uso_general","hormigon"]},
  {"id":"NTC30_04","capitulo":1,"norma":"NTC 30","titulo":"Cemento Portland Tipo 2",
   "contenido":"Es el destinado en general a obras de hormigón expuestas a la acción moderada de sulfatos y a obras donde se requiera moderado calor de hidratación.",
   "aplica_a":["cemento_tipo2","resistencia_sulfatos","calor_hidratacion"],"tags":["tipo_2","sulfatos","calor_hidratacion"]},
  {"id":"NTC30_05","capitulo":1,"norma":"NTC 30","titulo":"Cemento Portland Tipo 3",
   "contenido":"Es el que desarrolla altas resistencias iniciales. Aplicable en obras donde se requiere rápido desencofrado o apertura al tráfico.",
   "aplica_a":["cemento_tipo3","alta_resistencia_inicial","obras_rapidas"],"tags":["tipo_3","alta_resistencia","temprana_edad"]},
  {"id":"NTC30_07","capitulo":1,"norma":"NTC 30","titulo":"Cemento Portland Tipo 5",
   "contenido":"Es el que ofrece alta resistencia a la acción de los sulfatos. Aplicable en ambientes agresivos, suelos con alto contenido de sulfatos.",
   "aplica_a":["cemento_tipo5","alta_resistencia_sulfatos","ambientes_agresivos"],"tags":["tipo_5","sulfatos","alta_resistencia"]},

  # ── NTC 121 — Requisitos cemento Portland ────────────────────────────────────
  {"id":"NTC121_01","capitulo":1,"norma":"NTC 121","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos físicos y mecánicos que deben cumplir los siguientes tipos de cemento Portland: 1, 1M, 2, 4 y 5.",
   "aplica_a":["cemento_portland","seleccion_cemento","especificaciones_tecnicas"],"tags":["objeto","alcance","tipos"]},
  {"id":"NTC121_02","capitulo":1,"norma":"NTC 121","titulo":"Definición de Cemento Portland",
   "contenido":"Producto que se obtiene por pulverización del clinker Portland con la adición de una o más formas de sulfato de calcio. Se admiten otros productos adicionales siempre que su inclusión no afecte las propiedades del cemento resultante.",
   "aplica_a":["cemento_portland","definiciones"],"tags":["definicion","clinker","sulfato_calcio"]},
  {"id":"NTC121_05","capitulo":1,"norma":"NTC 121","titulo":"Requisitos de fraguado",
   "contenido":"El fraguado inicial debe ser ≥ 45 minutos y el fraguado final ≤ 8 horas para todos los tipos de cemento Portland.",
   "aplica_a":["fraguado","control_calidad_cemento"],"tags":["fraguado_inicial","fraguado_final","tiempo_fraguado"]},
  {"id":"NTC121_06","capitulo":1,"norma":"NTC 121","titulo":"Resistencia a la compresión - Tipo I",
   "contenido":"Resistencia mínima Tipo I: 3 días ≥ 10.0 MPa, 7 días ≥ 17.0 MPa, 28 días ≥ 28.0 MPa.",
   "aplica_a":["resistencia_compresion","cemento_tipo1"],"tags":["tipo_I","resistencia","compresion","MPa"]},
  {"id":"NTC121_08","capitulo":1,"norma":"NTC 121","titulo":"Resistencia a la compresión - Tipo III (alta resistencia inicial)",
   "contenido":"Resistencia mínima Tipo III: 1 día ≥ 12.0 MPa, 3 días ≥ 24.0 MPa, 28 días ≥ 28.0 MPa.",
   "aplica_a":["resistencia_compresion","cemento_tipo3"],"tags":["tipo_III","alta_resistencia_inicial","resistencia"]},

  # ── NTC 4026 — Bloques estructurales ────────────────────────────────────────
  {"id":"NTC4026_01","capitulo":5,"norma":"NTC 4026","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos para unidades de mampostería, perforadas o macizas de concreto, elaboradas con cemento portland, agua y agregados minerales, aptos para elaborar mampostería estructural.",
   "aplica_a":["mamposteria_estructural","bloques_estructurales","unidades_mamposteria"],"tags":["objeto","alcance","estructural","bloques"]},
  {"id":"NTC4026_05","capitulo":5,"norma":"NTC 4026","titulo":"Resistencia - Clase A",
   "contenido":"Unidades de resistencia alta (Clase A): Resistencia a la compresión promedio (3 unidades) ≥ 13 MPa y resistencia individual ≥ 11 MPa, medida sobre el área neta.",
   "aplica_a":["resistencia_compresion","clase_A","requisitos_tecnicos"],"tags":["Clase_A","13_MPa","11_MPa","area_neta"]},
  {"id":"NTC4026_06","capitulo":5,"norma":"NTC 4026","titulo":"Resistencia - Clase B",
   "contenido":"Unidades de resistencia baja (Clase B): Resistencia a la compresión promedio (3 unidades) ≥ 8 MPa y resistencia individual ≥ 7 MPa, medida sobre el área neta.",
   "aplica_a":["resistencia_compresion","clase_B","requisitos_tecnicos"],"tags":["Clase_B","8_MPa","7_MPa","area_neta"]},
  {"id":"NTC4026_09","capitulo":5,"norma":"NTC 4026","titulo":"Dimensiones estándar",
   "contenido":"Las dimensiones nominales estándar son 39 cm de largo × 19 cm de alto. Los anchos comerciales disponibles son 09, 12, 15 y 20 cm.",
   "aplica_a":["dimensiones","especificaciones_tecnicas","apus"],"tags":["39x19","anchos","09","12","15","20"]},
  {"id":"NTC4026_11","capitulo":5,"norma":"NTC 4026","titulo":"Aplicación en muros de carga",
   "contenido":"Los bloques NTC 4026 se utilizan en muros portantes que transmiten el peso de losas, cubiertas y pisos superiores hasta la cimentación. Se diseñan según NSR-10 Título D (mampostería estructural) y requieren refuerzo integrado.",
   "aplica_a":["aplicacion","apus","especificaciones_obra"],"tags":["muro_carga","NSR10","Titulo_D","dovelas","vigas"]},

  # ── NTC 4076 — Bloques no estructurales ──────────────────────────────────────
  {"id":"NTC4076_01","capitulo":5,"norma":"NTC 4076","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos para unidades de concreto para mampostería no estructural, elaboradas con cemento hidráulico, agua y agregados minerales. Están destinadas para divisiones no estructurales, interiores o exteriores.",
   "aplica_a":["mamposteria","bloques_concreto","unidades_mamposteria"],"tags":["objeto","alcance","no_estructural","bloques"]},
  {"id":"NTC4076_08","capitulo":5,"norma":"NTC 4076","titulo":"Resistencia a la compresión - Bloque no estructural",
   "contenido":"Los bloques no estructurales según NTC 4076 deben cumplir: Resistencia promedio (3 unidades) ≥ 6.0 MPa y Resistencia individual ≥ 5.0 MPa, medida sobre el área neta.",
   "aplica_a":["resistencia_compresion","requisitos_tecnicos","control_calidad"],"tags":["6.0_MPa","5.0_MPa","area_neta","no_estructural"]},
  {"id":"NTC4076_09","capitulo":5,"norma":"NTC 4076","titulo":"Comparación con bloque estructural (NTC 4026)",
   "contenido":"Bloques estructurales NTC 4026: Clase A: ≥13 MPa / ≥11 MPa. Clase B: ≥8 MPa / ≥7 MPa. No estructurales NTC 4076: ≥6.0 MPa / ≥5.0 MPa.",
   "aplica_a":["comparacion","seleccion_tipo","apus"],"tags":["NTC4026","estructural","13_MPa","8_MPa"]},

  # ── NTC 4027 — Concreto dosificado volumétricamente ─────────────────────────
  {"id":"NTC4027_05","capitulo":4,"norma":"NTC 4027","titulo":"Relación con NSR-10",
   "contenido":"La NSR-10 en su Título C.5.8.2 establece que el concreto premezclado debe cumplir con las normas NTC 3318 (ASTM C94) o NTC 4027 (ASTM C685). Ambas son aceptadas como alternativas para el suministro de concreto premezclado.",
   "aplica_a":["NSR10","normas_complementarias"],"tags":["NSR10","C.5.8.2","NTC3318","ASTM_C94","ASTM_C685"]},
  {"id":"NTC4027_07","capitulo":4,"norma":"NTC 4027","titulo":"Control de calidad - Ensayos asociados",
   "contenido":"Para verificar la calidad del concreto bajo NTC 4027 se deben realizar ensayos según: NTC 396 (Asentamiento), NTC 454 (Toma de muestras), NTC 673 (Resistencia a compresión), NTC 1028/1032 (Contenido de aire).",
   "aplica_a":["control_calidad","ensayos","apus"],"tags":["NTC396","NTC454","NTC673","NTC1028","NTC1032"]},

  # ── NTC 3459 — Agua para concreto ────────────────────────────────────────────
  {"id":"NTC3459_01","capitulo":4,"norma":"NTC 3459","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos y métodos de ensayo para determinar si el agua es apropiada para la elaboración de concreto. Aplica a agua potable, agua de fuentes naturales, agua de lluvia, agua de lavado y agua recirculada en plantas de concreto.",
   "aplica_a":["agua","concreto","control_calidad","seleccion_materiales"],"tags":["objeto","alcance","agua","fuentes"]},
  {"id":"NTC3459_04","capitulo":4,"norma":"NTC 3459","titulo":"Parámetros límite - Sulfatos y cloruros",
   "contenido":"El agua para concreto debe tener: sulfatos (SO4) máximo 1,000 mg/L, cloruros (Cl-) máximo 1,000 mg/L. La suma de sulfatos y cloruros no debe exceder 1 g/L.",
   "aplica_a":["parametros_quimicos","requisitos_tecnicos"],"tags":["sulfatos","cloruros","1000_mg/L","1_g/L"]},
  {"id":"NTC3459_05","capitulo":4,"norma":"NTC 3459","titulo":"Parámetros límite - Sólidos y pH",
   "contenido":"El agua para concreto debe tener: sólidos totales máximo 50,000 mg/L, sólidos disueltos totales (TDS) máximo 2,000 mg/L, pH mayor o igual a 5.",
   "aplica_a":["parametros_fisicos","requisitos_tecnicos"],"tags":["solidos_totales","TDS","pH","bicarbonatos"]},
  {"id":"NTC3459_08","capitulo":4,"norma":"NTC 3459","titulo":"Relación con NSR-10",
   "contenido":"La NSR-10 establece que el agua usada para mezclas de concreto debe cumplir con la NTC 3459 o la ASTM C1602. La NTC 3459 es más exigente que la ASTM C1602.",
   "aplica_a":["normas_complementarias","NSR10"],"tags":["NSR10","ASTM_C1602","exigencia"]},

  # ── NTC 1299 — Aditivos químicos para concreto ───────────────────────────────
  {"id":"NTC1299_01","capitulo":4,"norma":"NTC 1299","titulo":"Objeto y alcance",
   "contenido":"Esta norma comprende los materiales que se usan como aditivos químicos en mezclas de concreto hidráulico. Los aditivos son ingredientes que se añaden al concreto o mortero para modificar sus propiedades en estado fresco, durante el fraguado o en estado endurecido.",
   "aplica_a":["aditivos","concreto","control_calidad"],"tags":["objeto","alcance","aditivos_quimicos"]},
  {"id":"NTC1299_03","capitulo":4,"norma":"NTC 1299","titulo":"Tipo A - Plastificante (reductor de agua)",
   "contenido":"Permite disminuir la cantidad de agua necesaria para obtener una determinada consistencia del concreto. Ayuda a minimizar la exudación y disminuir la segregación. Equivalente ASTM C494 Tipo A.",
   "aplica_a":["aditivos","plastificante","dosificacion"],"tags":["Tipo_A","plastificante","reductor_agua"]},
  {"id":"NTC1299_04","capitulo":4,"norma":"NTC 1299","titulo":"Tipo B - Retardante",
   "contenido":"Demora el tiempo de fraguado del concreto. Se emplea cuando la temperatura ambiente es muy alta o cuando se requiere mayor tiempo para la colocación y acabado.",
   "aplica_a":["aditivos","retardante","climas_calidos"],"tags":["Tipo_B","retardante","fraguado","alta_temperatura"]},
  {"id":"NTC1299_05","capitulo":4,"norma":"NTC 1299","titulo":"Tipo C - Acelerante",
   "contenido":"Acelera tanto el fraguado como la ganancia de resistencia a edad temprana. Es esencial para acabados rápidos y colocación en climas fríos.",
   "aplica_a":["aditivos","acelerante","climas_frios"],"tags":["Tipo_C","acelerante","fraguado","resistencia_temprana"]},
  {"id":"NTC1299_08","capitulo":4,"norma":"NTC 1299","titulo":"Tipo F - Superplastificante",
   "contenido":"Permite la reducción del agua de mezcla en más de un 12% para obtener determinada consistencia. Es ideal para concretos de alta resistencia.",
   "aplica_a":["aditivos","superplastificante","alta_resistencia"],"tags":["Tipo_F","superplastificante","reduccion_agua",">12%"]},
  {"id":"NTC1299_11","capitulo":4,"norma":"NTC 1299","titulo":"Dosificación de aditivos",
   "contenido":"Las dosis típicas de aditivos se encuentran dentro del rango de 0.10% al 1.0% del peso del material cementante, dependiendo del efecto deseado.",
   "aplica_a":["dosificacion","apus","control_calidad"],"tags":["dosis","0.10%","1.0%","cementante"]},

  # ── NTC 1032 — Contenido de aire (método de presión) ─────────────────────────
  {"id":"NTC1032_01","capitulo":2,"norma":"NTC 1032","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece el método de ensayo para determinar el contenido de aire del concreto fresco mezclado, a partir de la observación del cambio de volumen del concreto con un cambio de presión. Equivalente ASTM C231.",
   "aplica_a":["control_calidad","concreto_fresco","contenido_aire"],"tags":["objeto","alcance","presion","cambio_volumen"]},
  {"id":"NTC1032_07","capitulo":2,"norma":"NTC 1032","titulo":"Contenido de aire recomendado",
   "contenido":"El contenido de aire en concretos con aire incorporado debe estar entre 3% y 5%. La tolerancia debe ser ± 1.5%. Para concretos con f'c < 35 MPa, se puede reducir el aire incorporado en 1%.",
   "aplica_a":["dosificacion","especificaciones_obra","apus"],"tags":["aire_incorporado","3%","5%","tolerancia"]},

  # ── NTC 1028 — Contenido de aire (método volumétrico) ────────────────────────
  {"id":"NTC1028_01","capitulo":2,"norma":"NTC 1028","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece el método volumétrico para determinar el contenido de aire del concreto fresco que contiene cualquier tipo de agregado, ya sea denso, celular o liviano. No se permite en concretos no plásticos.",
   "aplica_a":["control_calidad","concreto_fresco","contenido_aire"],"tags":["objeto","alcance","volumetrico","agregados"]},
  {"id":"NTC1028_06","capitulo":2,"norma":"NTC 1028","titulo":"Aire atrapado - Efectos negativos",
   "contenido":"El aire atrapado en diámetros mayores a 1 mm disminuye la resistencia, reduce las secciones efectivas de los elementos y causa mal aspecto.",
   "aplica_a":["control_calidad","patologias_concreto"],"tags":["aire_atrapado","1mm","resistencia","durabilidad"]},

  # ── NTC 504 — Refrentado de cilindros ────────────────────────────────────────
  {"id":"NTC504_01","capitulo":3,"norma":"NTC 504","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los aparatos, materiales y procedimientos para llevar a cabo el refrentado de cilindros de concreto. El refrentado proporciona superficies planas en los extremos de los cilindros para las pruebas de compresión. Adopción modificada ASTM C617.",
   "aplica_a":["control_calidad","concreto_endurecido","ensayos_compresion"],"tags":["objeto","alcance","refrentado","cilindros"]},
  {"id":"NTC504_03","capitulo":3,"norma":"NTC 504","titulo":"Materiales para refrentado - Yeso de alta resistencia",
   "contenido":"El yeso de alta resistencia debe proporcionar una resistencia mínima a la compresión de 34.5 MPa, validada mediante cubos de 50 mm tras 2 horas de preparación.",
   "aplica_a":["materiales_refrentado","yeso_alta_resistencia"],"tags":["yeso","34.5_MPa","cubos_50mm"]},
  {"id":"NTC504_06","capitulo":3,"norma":"NTC 504","titulo":"Requisitos de espesor del refrentado",
   "contenido":"Para cilindros con resistencia entre 3.5 y 50 MPa: espesor máximo promedio de 6 mm y máximo en cualquier parte de 8 mm. Para cilindros con resistencia mayor a 50 MPa: espesor máximo promedio de 3 mm.",
   "aplica_a":["requisitos_tecnicos","espesor_refrentado"],"tags":["espesor","6mm","8mm","3mm","MPa"]},

  # ── NTC 454 — Toma de muestras de concreto fresco ────────────────────────────
  {"id":"NTC454_01","capitulo":2,"norma":"NTC 454","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los procedimientos para obtener muestras representativas de concreto fresco. Equivalente ASTM C172. Cuenta con Segunda Actualización (1998).",
   "aplica_a":["control_calidad","concreto_fresco","muestreo"],"tags":["objeto","alcance","muestras_representativas"]},
  {"id":"NTC454_05","capitulo":2,"norma":"NTC 454","titulo":"Muestreo en mezcladoras",
   "contenido":"Para mezcladoras estacionarias y giratorias, se debe tomar una muestra compuesta después de haber descargado el primer 10% del concreto y antes del 90%.",
   "aplica_a":["procedimiento_muestreo","mezcladoras"],"tags":["muestreo","descarga","10%","90%"]},
  {"id":"NTC454_08","capitulo":2,"norma":"NTC 454","titulo":"Ensayos sobre la muestra",
   "contenido":"Los ensayos que se realizan sobre muestras según NTC 454 incluyen: asentamiento (NTC 396), temperatura (NSR-10 C.5.6.1), resistencia a la compresión (NTC 673), contenido de aire (NTC 1028/1032) y masa unitaria.",
   "aplica_a":["ensayos","control_calidad","apus"],"tags":["asentamiento","temperatura","compresion","aire"]},

  # ── NTC 2289 — Acero de refuerzo baja aleación ───────────────────────────────
  {"id":"NTC2289_01","capitulo":6,"norma":"NTC 2289","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos para las barras corrugadas y lisas de acero de baja aleación, para refuerzo de concreto. Es de uso obligatorio en territorio colombiano según la NSR-10. Corresponde a la ASTM A706.",
   "aplica_a":["acero_refuerzo","barras_corrugadas","estructuras_concreto"],"tags":["objeto","alcance","ASTM_A706","NSR10"]},
  {"id":"NTC2289_03","capitulo":6,"norma":"NTC 2289","titulo":"Propiedades mecánicas - Límite de fluencia",
   "contenido":"El límite de fluencia (fy) del acero de refuerzo bajo NTC 2289 debe estar entre 420 y 540 MPa. Corresponde al Grado 60.",
   "aplica_a":["propiedades_mecanicas","limite_fluencia","fy"],"tags":["fluencia","420_MPa","540_MPa","Grado_60"]},
  {"id":"NTC2289_04","capitulo":6,"norma":"NTC 2289","titulo":"Propiedades mecánicas - Resistencia a la tracción",
   "contenido":"La resistencia a la tracción (R) del acero de refuerzo bajo NTC 2289 debe ser mayor a 550 MPa. La relación R/fy debe ser ≥ 1.25.",
   "aplica_a":["propiedades_mecanicas","resistencia_traccion"],"tags":["traccion","550_MPa","R/fy"]},
  {"id":"NTC2289_10","capitulo":6,"norma":"NTC 2289","titulo":"Presentación y dimensiones",
   "contenido":"El acero se produce en barras rectas de 6 m, 9 m y 12 m de longitud. Diámetros disponibles: 6 mm, 1/4\", 8 mm, 9 mm, 3/8\", 12 mm, 1/2\", 15 mm, 5/8\", 3/4\", 7/8\", 1\".",
   "aplica_a":["presentacion","dimensiones","apus"],"tags":["barras","6m","9m","12m","diametros"]},
  {"id":"NTC2289_13","capitulo":6,"norma":"NTC 2289","titulo":"Relación con NSR-10 - Zonas sísmicas",
   "contenido":"La NSR-10 C.3.5.3.2 establece que solo en zona de amenaza sísmica baja se permite el uso de acero bajo NTC 248 (ASTM A615). En zonas de amenaza sísmica intermedia y alta, debe usarse acero bajo NTC 2289 (ASTM A706).",
   "aplica_a":["NSR10","zonas_sismicas","seleccion_material"],"tags":["NSR10","C.3.5.3.2","NTC248","ASTM_A615"]},

  # ── NTC 1500 — Instalaciones hidráulicas y sanitarias ────────────────────────
  {"id":"NTC1500_01","capitulo":7,"norma":"NTC 1500","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos mínimos para el diseño, construcción, instalación, modificación, reparación, reemplazo, extensión, uso y mantenimiento de los sistemas de instalaciones hidráulicas y sanitarias en edificaciones.",
   "aplica_a":["instalaciones_hidraulicas","fontaneria","saneamiento","diseno"],"tags":["objeto","alcance","sistemas","edificaciones"]},
  {"id":"NTC1500_06","capitulo":7,"norma":"NTC 1500","titulo":"Sistemas de suministro de agua",
   "contenido":"Todo aparato hidrosanitario que requiera el uso de agua debe conectarse al sistema de suministro. La norma establece los componentes básicos: tuberías, accesorios, válvulas y dispositivos de control. Versión vigente: Cuarta actualización 2020.",
   "aplica_a":["suministro_agua","redes_hidraulicas","diseno"],"tags":["suministro","agua_potable","tuberias"]},
  {"id":"NTC1500_09","capitulo":7,"norma":"NTC 1500","titulo":"Pruebas y ensayos",
   "contenido":"El sistema de tuberías debe ser probado con agua o, para sistemas no plásticos, con aire. Se deben realizar las pruebas aplicables prescritas en la NTC 1500 para determinar el cumplimiento.",
   "aplica_a":["ensayos","pruebas","control_calidad"],"tags":["pruebas","agua","aire","tuberias"]},
  {"id":"NTC1500_12","capitulo":7,"norma":"NTC 1500","titulo":"Relación con NSR-10",
   "contenido":"La NTC 1500 debe complementarse con la NSR-10 para aspectos estructurales y de seguridad. El Anexo A de la NTC 1500:2020 está dedicado a la Seguridad Estructural.",
   "aplica_a":["NSR10","seguridad_estructural","normas_complementarias"],"tags":["NSR10","seguridad_estructural","anexo_A"]},

  # ── NTC 1328 — Juntas flexibles tuberías concreto ────────────────────────────
  {"id":"NTC1328_01","capitulo":7,"norma":"NTC 1328","titulo":"Objeto y alcance",
   "contenido":"Esta norma especifica los requisitos para juntas flexibles y resistentes a filtraciones, utilizadas en la unión de tubos circulares de concreto y secciones de pozos de inspección prefabricados. El propósito es asegurar la estanqueidad de las uniones. Equivalente ASTM C443.",
   "aplica_a":["tuberias_concreto","juntas_flexibles","alcantarillado","drenaje"],"tags":["objeto","alcance","juntas","empaques_caucho"]},
  {"id":"NTC1328_03","capitulo":7,"norma":"NTC 1328","titulo":"Materiales - Empaques de caucho",
   "contenido":"Los empaques elastoméricos utilizados en las juntas deben cumplir requisitos específicos de dureza, elongación y resistencia. El compuesto debe contener no menos del 50% en volumen de caucho.",
   "aplica_a":["materiales","empaques","control_calidad"],"tags":["caucho","elastomeros","dureza","elongacion"]},

  # ── NTC 4595 — Instalaciones escolares ───────────────────────────────────────
  {"id":"NTC4595_01","capitulo":8,"norma":"NTC 4595","titulo":"Objeto y alcance",
   "contenido":"Esta norma establece los requisitos para el planeamiento y diseño físico-espacial de instalaciones y ambientes escolares, con el fin de mejorar la calidad de las instituciones educativas. Aplica a nuevas instalaciones y a la adecuación de existentes. Tercera actualización 2020.",
   "aplica_a":["diseno_escolar","infraestructura_educativa","planeamiento"],"tags":["objeto","alcance","instalaciones_escolares"]},
  {"id":"NTC4595_05","capitulo":8,"norma":"NTC 4595","titulo":"Requisitos de área - Ambiente tipo C",
   "contenido":"El Aula de Tecnología (ambiente C) requiere un espacio de 2.3 a 2.5 m² por estudiante para capacidades estándar. Talleres con equipos voluminosos requieren más de 5 m² por estudiante.",
   "aplica_a":["requisitos_tecnicos","dimensionamiento","apus"],"tags":["area","m2","estudiante","ambiente_C"]},

  # ── NTC 2516 — Dibujo técnico ────────────────────────────────────────────────
  {"id":"NTC2516_01","capitulo":8,"norma":"NTC 2516","titulo":"Dibujo técnico - Representación de vistas, secciones y cortes",
   "contenido":"Esta norma establece las reglas y convenciones para la representación gráfica de objetos y edificaciones mediante la proyección de vistas, secciones y cortes en el dibujo técnico para ingeniería civil y arquitectura.",
   "aplica_a":["dibujo_tecnico","planos","representacion_grafica"],"tags":["dibujo","planos","vistas","cortes"]},

  # ═══════════════════════════════════════════════════════════════
  # SEGURIDAD INDUSTRIAL
  # ═══════════════════════════════════════════════════════════════

  # ── Resolución 5018 de 2019 — Seguridad sector eléctrico ─────────────────────
  {"id":"RES5018_01","capitulo":1,"norma":"Resolución 5018 de 2019","titulo":"Objeto",
   "contenido":"La Resolución 5018 de 2019 tiene por objeto establecer los lineamientos en seguridad y salud en el trabajo para las actividades ejecutadas en el sector eléctrico, incluyendo trabajos en redes de alta, media y baja tensión.",
   "aplica_a":["seguridad_electrica","SST","sector_electrico"],"tags":["objeto","sector_electrico","SST","riesgo_electrico"]},
  {"id":"RES5018_02","capitulo":1,"norma":"Resolución 5018 de 2019","titulo":"Ámbito de aplicación",
   "contenido":"La resolución aplica a todas las empresas que presten o hagan uso del servicio de energía eléctrica en sus actividades de trabajo. Incluye contratistas y subcontratistas que realicen trabajos eléctricos.",
   "aplica_a":["ambito_aplicacion","contratistas","seguridad_electrica"],"tags":["aplicacion","contratistas","energia_electrica"]},
  {"id":"RES5018_03","capitulo":5,"norma":"Resolución 5018 de 2019","titulo":"Reglas de oro - Trabajo en equipos desenergizados",
   "contenido":"Para trabajos en equipos o instalaciones desenergizadas se deben aplicar las cinco reglas de oro de la seguridad eléctrica: 1) Abrir con corte visible, 2) Bloquear contra reconexión, 3) Verificar ausencia de tensión, 4) Poner a tierra y cortocircuitar, 5) Delimitar y señalizar la zona de trabajo.",
   "aplica_a":["trabajo_seguro","desenergizado","reglas_oro"],"tags":["reglas_oro","cinco_reglas","desenergizado","LOTO"]},
  {"id":"RES5018_04","capitulo":5,"norma":"Resolución 5018 de 2019","titulo":"Elementos de protección personal (EPP) sector eléctrico",
   "contenido":"Los trabajadores del sector eléctrico deben usar EPP dieléctrico: guantes de caucho dieléctrico con protector exterior, casco de seguridad dieléctrico, gafas de seguridad, ropa antiflash, calzado dieléctrico y arnés de seguridad para trabajos en altura.",
   "aplica_a":["EPP","proteccion_personal","riesgo_electrico"],"tags":["guantes_dielectrico","casco_dielectrico","ropa_antiflash","calzado"]},

  # ── Resolución 1409 de 2012 — Trabajo en alturas ─────────────────────────────
  {"id":"RES1409_01","capitulo":1,"norma":"Resolución 1409 de 2012","titulo":"Objeto y campo de aplicación",
   "contenido":"Esta resolución establece el Reglamento de Seguridad para protección contra caídas en trabajo en alturas. Aplica a todos los empleadores, empresas, contratistas, subcontratistas y trabajadores de todas las actividades económicas donde se realicen trabajos en altura mayores a 1.50 m.",
   "aplica_a":["trabajo_alturas","SST","proteccion_caidas"],"tags":["objeto","1.50m","caidas","alturas"]},
  {"id":"RES1409_02","capitulo":2,"norma":"Resolución 1409 de 2012","titulo":"Definiciones clave",
   "contenido":"Trabajo en altura: todo trabajo que se realice a 1.50 m o más sobre un nivel inferior. Línea de vida: elemento de cuerda, cable o cadena que sirve de sostén al arnés de cuerpo entero. Punto de anclaje: punto de conexión resistente para los sistemas de protección contra caídas.",
   "aplica_a":["definiciones","trabajo_alturas","sistemas_proteccion"],"tags":["1.50m","linea_vida","anclaje","definiciones"]},
  {"id":"RES1409_03","capitulo":3,"norma":"Resolución 1409 de 2012","titulo":"Medidas de prevención",
   "contenido":"El empleador debe proveer: capacitación y entrenamiento en trabajo seguro en alturas, sistemas de ingeniería (barandas, redes de seguridad), sistemas de acceso (andamios, escaleras) y sistemas de protección personal contra caídas (arnés, líneas de vida, anclajes).",
   "aplica_a":["medidas_prevencion","caidas","SST"],"tags":["capacitacion","barandas","redes","andamios","arnés"]},
  {"id":"RES1409_04","capitulo":4,"norma":"Resolución 1409 de 2012","titulo":"Arnés de cuerpo entero y conectores",
   "contenido":"El arnés de cuerpo entero es el único sistema de protección individual contra caídas aceptado. Los conectores deben soportar una carga de 22.2 kN. Los sistemas de detención de caídas deben limitar la fuerza de impacto a 6 kN.",
   "aplica_a":["EPP","arnes","conectores"],"tags":["arnes","22.2kN","6kN","conectores","carga"]},

  # ── Decreto 1072 de 2015 — SGSST ─────────────────────────────────────────────
  {"id":"DEC1072_01","capitulo":1,"norma":"Decreto 1072 de 2015","titulo":"Sistema de Gestión de Seguridad y Salud en el Trabajo (SGSST)",
   "contenido":"El Decreto 1072 de 2015 compila las normas del sector trabajo y establece el Sistema de Gestión de la Seguridad y Salud en el Trabajo (SGSST). Toda empresa con empleados debe implementarlo. Derogó el Decreto 1443 de 2014.",
   "aplica_a":["SGSST","SST","gestion_seguridad"],"tags":["SGSST","decreto","empresas","implementacion"]},
  {"id":"DEC1072_02","capitulo":2,"norma":"Decreto 1072 de 2015","titulo":"Obligaciones del empleador",
   "contenido":"El empleador debe: definir y firmar la política de SST, asignar recursos para el SGSST, garantizar la participación de los trabajadores, identificar y evaluar los peligros y riesgos, implementar los controles necesarios y garantizar la mejora continua del sistema.",
   "aplica_a":["empleador","obligaciones","SGSST"],"tags":["politica_SST","recursos","participacion","peligros","riesgos"]},
  {"id":"DEC1072_03","capitulo":2,"norma":"Decreto 1072 de 2015","titulo":"Ciclo PHVA en el SGSST",
   "contenido":"El SGSST se desarrolla sobre el ciclo PHVA (Planear, Hacer, Verificar, Actuar): Planear: diagnóstico inicial, política, objetivos. Hacer: implementación de controles y capacitación. Verificar: auditorías y medición de indicadores. Actuar: mejora continua.",
   "aplica_a":["PHVA","metodologia","mejora_continua"],"tags":["PHVA","planear","hacer","verificar","actuar"]},

  # ── Resolución 3232 de 2024 — Licencias urbanísticas ──────────────────────────
  {"id":"RES3232_01","capitulo":1,"norma":"Resolución 3232 de 2024","titulo":"Objeto - Trámite de licencias urbanísticas",
   "contenido":"La Resolución 3232 de 2024 del Ministerio de Vivienda, Ciudad y Territorio establece el procedimiento para el trámite de licencias urbanísticas y sus modalidades: nueva construcción, modificación, subdivisión, urbanización, parcelación, reconocimiento, demolición y cerramiento.",
   "aplica_a":["licencias_urbanisticas","curaduria","tramites"],"tags":["objeto","licencias","modalidades","curaduria_urbana"]},
  {"id":"RES3232_02","capitulo":2,"norma":"Resolución 3232 de 2024","titulo":"Requisitos documentales - Lista de chequeo",
   "contenido":"Para tramitar una licencia urbanística de nueva construcción se deben presentar: formulario de solicitud (Anexo 1), memoria de cálculo estructural firmada por ingeniero estructural, planos arquitectónicos y estructurales, estudio de suelos para edificaciones > 2 pisos, certificado de tradición del inmueble y vigencia de escrituras.",
   "aplica_a":["requisitos","documentos","nueva_construccion"],"tags":["Anexo_1","calculo_estructural","planos","estudio_suelos"]},
  {"id":"RES3232_03","capitulo":3,"norma":"Resolución 3232 de 2024","titulo":"Profesionales responsables",
   "contenido":"La licencia urbanística requiere la firma de: Arquitecto (proyecto arquitectónico), Ingeniero Estructural (diseño estructural y memoria de cálculo), Ingeniero de Suelos (estudio de suelos), Ingeniero de Redes (instalaciones hidrosanitarias, eléctricas y gas). Cada profesional firma solo los planos de su especialidad.",
   "aplica_a":["profesionales","responsabilidad","firmas"],"tags":["arquitecto","ingeniero_estructural","ingeniero_suelos","firmas"]},
]

# ─── KNOWLEDGE EDGES (relaciones entre normas) ────────────────────────────────
KNOWLEDGE_EDGES = [
  # NTC → NSR-10
  ("NTC673","NSR-10","referencia_obligatoria","NSR-10 C.5 exige ensayos NTC 673 para aceptación de concreto"),
  ("NTC396","NSR-10","referencia_obligatoria","NSR-10 C.5.6.1 establece asentamiento según NTC 396"),
  ("NTC174","NSR-10","referencia_obligatoria","NSR-10 C.3.3 exige agregados según NTC 174"),
  ("NTC121","NSR-10","referencia_obligatoria","NSR-10 C.3.2 exige cemento según NTC 121/ASTM C150"),
  ("NTC2289","NSR-10","referencia_obligatoria","NSR-10 C.3.5.3.2 exige acero NTC 2289 en zonas sísmicas intermedias y altas"),
  ("NTC4026","NSR-10","referencia_obligatoria","NSR-10 Título D exige bloques NTC 4026 para mampostería estructural"),
  ("NTC3459","NSR-10","referencia_obligatoria","NSR-10 C.3.4 exige agua para mezcla según NTC 3459"),
  ("NTC1299","NSR-10","referencia_obligatoria","NSR-10 C.3.6 exige aditivos según NTC 1299"),
  ("NTC454","NSR-10","referencia_obligatoria","NSR-10 C.5.6 exige muestras según NTC 454"),
  ("NTC1500","NSR-10","complementaria","NTC 1500 Anexo A se complementa con NSR-10 para seguridad estructural"),
  # NTC entre sí
  ("NTC673","NTC454","depende_de","NTC 673 requiere muestras tomadas según NTC 454"),
  ("NTC673","NTC504","depende_de","NTC 673 requiere refrentado según NTC 504 antes del ensayo"),
  ("NTC4026","NTC174","depende_de","NTC 4026 exige agregados que cumplan NTC 174"),
  ("NTC4026","NTC121","depende_de","NTC 4026 exige cemento que cumpla NTC 121"),
  ("NTC4076","NTC174","depende_de","NTC 4076 exige agregados que cumplan NTC 174"),
  ("NTC4076","NTC4026","complementaria","NTC 4076 no estructural vs NTC 4026 estructural"),
  ("NTC1032","NTC454","depende_de","NTC 1032 requiere muestra según NTC 454"),
  ("NTC1028","NTC454","depende_de","NTC 1028 requiere muestra según NTC 454"),
  ("NTC4027","NTC3459","depende_de","NTC 4027 exige agua según NTC 3459"),
  ("NTC4027","NTC174","depende_de","NTC 4027 exige agregados según NTC 174"),
  # Seg. Industrial entre sí
  ("RES1409","DEC1072","referencia_obligatoria","Res 1409 aplica dentro del marco del Decreto 1072 SGSST"),
  ("RES5018","DEC1072","referencia_obligatoria","Res 5018 sector eléctrico aplica dentro del marco SGSST Decreto 1072"),
  # Seg. Industrial → NSR-10
  ("RES1409","NSR-10","complementaria","Res 1409 aplica en obras de construcción que requieren NSR-10"),
  ("RES3232","NSR-10","referencia_obligatoria","Res 3232 exige memoria de cálculo estructural cumpliendo NSR-10"),
]

def embed(text: str) -> list[float]:
    """Genera embedding con OpenAI text-embedding-3-small (1536d)."""
    resp = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

def norma_codigo(norma_str: str) -> str:
    """Extrae código limpio p.e. 'NTC 673' → 'NTC673'."""
    return norma_str.replace(" ", "").replace("ó","o").replace("ú","u").replace("é","e")

def seed_nodes():
    """Inserta un knowledge_node por cada norma única."""
    print("\n📌 Seeding knowledge_nodes...")
    normas_meta = {
        "NTC 673":  {"titulo":"Método de ensayo resistencia a compresión de cilindros de concreto","tipo":"NTC","fuente":"ICONTEC / ASTM C39"},
        "NTC 396":  {"titulo":"Método de ensayo para asentamiento del concreto","tipo":"NTC","fuente":"ICONTEC / ASTM C143"},
        "NTC 174":  {"titulo":"Requisitos para los agregados usados en concreto","tipo":"NTC","fuente":"ICONTEC / ASTM C33"},
        "NTC 30":   {"titulo":"Clasificación y nomenclatura del cemento Portland","tipo":"NTC","fuente":"ICONTEC"},
        "NTC 121":  {"titulo":"Especificaciones para cemento Portland","tipo":"NTC","fuente":"ICONTEC / ASTM C1157"},
        "NTC 4026": {"titulo":"Especificaciones para bloques de concreto — mampostería estructural","tipo":"NTC","fuente":"ICONTEC / ASTM C90"},
        "NTC 4076": {"titulo":"Especificaciones para bloques de concreto — mampostería no estructural","tipo":"NTC","fuente":"ICONTEC"},
        "NTC 4027": {"titulo":"Concreto dosificado volumétricamente y mezclado de forma continua","tipo":"NTC","fuente":"ICONTEC / ASTM C685"},
        "NTC 3459": {"titulo":"Agua para la elaboración de concreto","tipo":"NTC","fuente":"ICONTEC"},
        "NTC 1299": {"titulo":"Aditivos químicos para uso en concreto","tipo":"NTC","fuente":"ICONTEC / ASTM C494"},
        "NTC 1032": {"titulo":"Determinación del contenido de aire del concreto fresco — método de presión","tipo":"NTC","fuente":"ICONTEC / ASTM C231"},
        "NTC 1028": {"titulo":"Determinación del contenido de aire del concreto fresco — método volumétrico","tipo":"NTC","fuente":"ICONTEC"},
        "NTC 504":  {"titulo":"Refrentado de especímenes cilíndricos de concreto","tipo":"NTC","fuente":"ICONTEC / ASTM C617"},
        "NTC 454":  {"titulo":"Toma de muestras de concreto fresco","tipo":"NTC","fuente":"ICONTEC / ASTM C172"},
        "NTC 2289": {"titulo":"Barras corrugadas de acero de baja aleación para refuerzo de concreto","tipo":"NTC","fuente":"ICONTEC / ASTM A706"},
        "NTC 1500": {"titulo":"Código Colombiano de Instalaciones Hidráulicas y Sanitarias","tipo":"NTC","fuente":"ICONTEC"},
        "NTC 1328": {"titulo":"Juntas flexibles para tubos circulares de concreto — empaques de caucho","tipo":"NTC","fuente":"ICONTEC / ASTM C443"},
        "NTC 4595": {"titulo":"Planeamiento y diseño de instalaciones escolares","tipo":"NTC","fuente":"ICONTEC"},
        "NTC 2516": {"titulo":"Dibujo técnico — representación de vistas, secciones y cortes","tipo":"NTC","fuente":"ICONTEC"},
        "Resolución 5018 de 2019": {"titulo":"Estándares mínimos de SST para el sector eléctrico","tipo":"Resolución","fuente":"Ministerio del Trabajo"},
        "Resolución 1409 de 2012": {"titulo":"Reglamento de seguridad para protección contra caídas en trabajo en alturas","tipo":"Resolución","fuente":"Ministerio del Trabajo"},
        "Decreto 1072 de 2015":    {"titulo":"Decreto único reglamentario del sector trabajo — SGSST","tipo":"Decreto","fuente":"Presidencia de la República"},
        "Resolución 3232 de 2024": {"titulo":"Procedimiento para el trámite de licencias urbanísticas","tipo":"Resolución","fuente":"Ministerio de Vivienda, Ciudad y Territorio"},
    }
    for norma, meta in normas_meta.items():
        node = {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"node.{norma}")),
            "tipo": meta["tipo"],
            "codigo": norma,
            "titulo": meta["titulo"],
            "version": "2024",
            "fuente": meta["fuente"],
            "descripcion": meta["titulo"]
        }
        sb.table("knowledge_nodes").upsert(node, on_conflict="codigo").execute()
        print(f"  ✅ {norma}")

def seed_chunks():
    """Embebe e inserta todos los chunks en public.ntc_chunks (esquema real).

    ntc_chunks.id es bigserial autogenerado — no hay columna de código externo
    para hacer upsert idempotente, así que se borran las filas existentes de
    cada norma antes de insertar su lote (re-ejecutar el script no duplica).
    """
    print(f"\n📦 Seeding {len(NTC_CHUNKS)} chunks en ntc_chunks...")
    normas_ya_limpiadas: set[str] = set()
    for i, chunk in enumerate(NTC_CHUNKS):
        if chunk["norma"] not in normas_ya_limpiadas:
            sb.table("ntc_chunks").delete().eq("norma", chunk["norma"]).execute()
            normas_ya_limpiadas.add(chunk["norma"])

        texto = f"{chunk['norma']} — {chunk['titulo']}: {chunk['contenido']}"
        embedding = embed(texto)
        row = {
            "norma":     chunk["norma"],
            "seccion":   chunk["id"],
            "titulo":    chunk["titulo"],
            "contenido": chunk["contenido"],
            "embedding": embedding,
        }
        sb.table("ntc_chunks").insert(row).execute()
        print(f"  [{i+1}/{len(NTC_CHUNKS)}] {chunk['id']}")
        # Respetar rate limit OpenAI (500 RPM = ~12 req/s max)
        if (i + 1) % 20 == 0:
            time.sleep(1)

def seed_edges():
    """Inserta knowledge_edges entre normas."""
    print(f"\n🔗 Seeding {len(KNOWLEDGE_EDGES)} edges...")
    # Obtener IDs de nodos por código
    result = sb.table("knowledge_nodes").select("id,codigo").execute()
    node_ids = {row["codigo"]: row["id"] for row in result.data}

    for src_code, tgt_code, rel_type, desc in KNOWLEDGE_EDGES:
        # Buscar coincidencias parciales (e.g. "NTC673" → "NTC 673")
        src_id = next((v for k, v in node_ids.items() if src_code.replace(" ","") in k.replace(" ","")), None)
        tgt_id = next((v for k, v in node_ids.items() if tgt_code.replace(" ","") in k.replace(" ","")), None)

        if not src_id or not tgt_id:
            # NSR-10 puede no estar en knowledge_nodes si fue seeded antes
            if tgt_code == "NSR-10":
                # Buscar o crear nodo NSR-10
                r = sb.table("knowledge_nodes").select("id").eq("codigo","NSR-10").execute()
                if r.data:
                    tgt_id = r.data[0]["id"]
                else:
                    tgt_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "node.NSR-10"))
                    sb.table("knowledge_nodes").upsert({
                        "id": tgt_id, "tipo": "Reglamento", "codigo": "NSR-10",
                        "titulo": "Norma Sismo Resistente de Colombia",
                        "version": "2010", "fuente": "Ministerio de Vivienda"
                    }, on_conflict="codigo").execute()
            else:
                print(f"  ⚠️  Nodo no encontrado: {src_code} → {tgt_code}")
                continue

        edge = {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"edge.{src_code}.{tgt_code}.{rel_type}")),
            "source_id": src_id,
            "target_id": tgt_id,
            "tipo_relacion": rel_type,
            "descripcion": desc
        }
        sb.table("knowledge_edges").upsert(edge, on_conflict="id").execute()
        print(f"  ✅ {src_code} --[{rel_type}]--> {tgt_code}")

if __name__ == "__main__":
    print("══════════════════════════════════════════════════════════")
    print("  SEED NTC + SEGURIDAD INDUSTRIAL → ntc_chunks (Supabase pgvector)")
    print(f"  Total chunks: {len(NTC_CHUNKS)}")
    print("══════════════════════════════════════════════════════════")

    # seed_nodes()/seed_edges() no se ejecutan: knowledge_nodes/knowledge_edges
    # no existen en el esquema real de este proyecto. Se conservan como
    # referencia por si en el futuro se agrega un grafo de dependencias sobre
    # una tabla nueva compatible.
    seed_chunks()

    print("\n🎉 Seed completado exitosamente!")
    print(f"   ntc_chunks: {len(NTC_CHUNKS)} chunks embebidos, {len(set(c['norma'] for c in NTC_CHUNKS))} normas")
