# Preparación del E4: destilación de StructAI a un modelo de 7B (antes del prerregistro)

Fecha: 2026-11-21. Issues: #179 (QLoRA en Kaggle), #258 (SFT + DPO + RL), #263, #268 (recompensa), #261 (sabotaje), #257 (inyección).
Plan previo: [`INVESTIGACION_FINETUNING_2026-11.md`](INVESTIGACION_FINETUNING_2026-11.md) §4.

**Propósito.** Dejar resuelto todo lo que no depende de los resultados: el alumno, el maestro, qué datos sirven, qué umbral debe pasar cada respuesta del maestro, el presupuesto de Groq y de Kaggle, y cómo se mide. El prerregistro se escribe después, sobre esta base, y antes de generar un solo ejemplo.

---

## 1. Alumno y maestro

### 1.1 Alumno: "Qwen2.7 7B" no existe

Familias abiertas de Qwen con un modelo de 7–9B, verificadas el 2026-11-21:

| Modelo | Licencia | A favor | En contra |
|---|---|---|---|
| **Qwen2.5-7B-Instruct** | Apache 2.0 | Ya es la línea base de E3 (`qwen2.5_7b.jsonl`, sabotaje, inyección y recompensa #268), así que el antes/después es pareado con datos que ya existen. Unsloth tiene la versión de 4 bits lista. Está probado en T4 | Es de 2024 |
| **Qwen3.5-9B** (marzo de 2026) | Apache 2.0 | Más reciente y multimodal, con 262K de contexto | Según Artificial Analysis supera a gpt-oss-120b en su índice: **destilar de un maestro más débil que el alumno no tiene sentido científico**. El modo de razonamiento viene activo por defecto. No hay línea base en E3. Con 9B es más justo en un T4 |

**Decisión (Wilmer, 2026-11-21): Qwen2.5-7B-Instruct.** Si más adelante se quiere Qwen3.5-9B, la pregunta cambia de "destilar" a "adaptar al dominio con datos verificados", y hay que medir primero si el maestro le gana al alumno en nuestras baterías.

Nota: #272 busca modelos no chinos con licencia comercial. Qwen es Apache 2.0 y cumple la regla de licencias; la procedencia es otra discusión que conviene dejar escrita.

### 1.2 Maestro: Groq `openai/gpt-oss-120b`

- **Licencia:** Apache 2.0, más la política de uso de gpt-oss, que básicamente obliga a cumplir la ley aplicable. Ninguna de las dos prohíbe entrenar con las salidas.
- **Términos de Groq:** remiten a los términos del dueño del modelo y ceden al cliente los derechos que Groq tenga sobre las salidas. Prohíben usarlas para hacer ingeniería inversa del servicio de Groq, que no es lo que hacemos.
- **Clave:** solo `GROQ_API_KEY_EVAL` (`_privado/.env.groq_eval`), nunca la de producción.
- **Registro:** antes de entrenar, anotar Qwen, gpt-oss, Unsloth y TRL en el registro de licencias (#219).

---

## 2. ¿Hay contexto suficiente en los demás motores? (inventario, solo lectura, 2026-11-21)

### 2.1 Corpus RAG por dominio

| Dominio | Fuente | Chunks | Comentario |
|---|---|---|---|
| NSR-10 | `nsr10_chunks` | 10.909 | F 2.646 · C 2.512 · A 1.365 · G 1.194 · D 719 · H 553 · K 434 · B 292 · J 289 · E 178 · I 63 |
| Vías y puentes | `motor_chunks` vias | 3.029 | CCP-14 1.309 (+124 con ruido de extracción), INV E sección 200 1.145, túneles 143, pavimentos 168, cemento 63 |
| Gerencia y contratación | `motor_chunks` gerencia | 818 | Ley 80 223, Manual de Interventoría 2022 154 + cap. 2 (Res. 970/2024) 174, Ley 1474 163, Ley 1150 71, fichas ISO |
| Agua (AquAI) | `motor_chunks` aquai | 320 | Res. 0330/2017 287, CRA 956/955, ficha NTC 1500. El RAS 2000 derogado ya no está |
| Ordenamiento (GeoPot) | `motor_chunks` geopot | 106 | Guía POT 2024: 89. Laboratorio: ~12 fichas sueltas |
| Laboratorio y NTC | `ntc_chunks` | 294 | Decreto 1072 59; NTC de ~200 caracteres cada una; ACI 318 y AISC 360 como fichas curadas |
| Perú y Ecuador | índice local | 204 + 395 | E.030 (corpus mixto) y NEC-SE-DS (vigencia no confirmada) |

**Veredicto:**
- **Sí alcanza** en NSR-10, vías y gerencia: hay miles de chunks para sacar preguntas.
- **Es delgado** en agua (320), ordenamiento (106) y laboratorio (294 chunks cortos). Ahí hay que esperar menos preguntas por chunk y medir por separado.
- **No hay corpus RAG** para concreto, geotecnia, licuación, redes, análisis, APU y precios, vivienda (AIS), exploración, acero de lámina delgada y orquestador. Pero esos motores son **deterministas**.

### 2.2 Motores deterministas: la mejor fuente

En los motores la respuesta correcta no la da Groq: la calcula el motor (`ResultadoMotor`, #263). Para cada motor se generan entradas aleatorias dentro de su dominio de validez. El motor da el valor verdadero, y Groq solo redacta la explicación.

Una respuesta del maestro se acepta solo si contiene el valor del motor dentro de su tolerancia. Así se cubren 16 paquetes `packages/motor-*` sin depender del RAG y con verificación exacta.

**Aclaración:** los motores no son *machine learning*. Son cálculo determinista: la norma y la física programadas en Python. Por eso sirven de verificador: su resultado no es una predicción.

Solo cuatro motores tienen corpus RAG propio: vías, gerencia, AquAI y GeoPot (este último con ~12 fichas de laboratorio). Los demás nunca lo tuvieron.

El ML de verdad está en otros lugares:
- el enrutador K6;
- los subrogados F2 (#275);
- el pronóstico de precios (#247–#253);
- el laboratorio digital del concreto (#116).

### 2.4 Laboratorio sin el texto de las NTC

El hueco de las NTC se cubre sin copiar texto de ICONTEC, con tres fuentes:

1. **Calculadoras deterministas que ya existen** en `motor-geopot`:
   - `lab_suelos`: USCS, AASHTO, límites de Atterberg, Proctor, CBR, granulometría (D10, D30, D60, Cu, Cc), espesor de pavimento;
   - `lab_concreto`: resistencia de cilindros, estadística por edad, proyección a 28 días, conformidad;
   - `lab_agregados`: densidad SSS, absorción, módulo de finura, verificación de requisitos.

   Con entradas aleatorias dentro de rango, el motor da la respuesta exacta, y el maestro solo la explica.
2. **Normas de ensayo INVIAS (INV E)**, que son públicas y equivalentes en muchos casos a las NTC. La sección 200 (agregados, 1.145 chunks) y la 300 (cemento) ya están. Faltan la 100 (suelos), la 400 (concreto) y la 700 (asfaltos).
3. **ML del laboratorio (#116):** predicción de la resistencia con datos abiertos (UCI de Yeh, CC BY 4.0; los de Mendeley, cuya licencia hay que revisar) y calibración local. Son ejemplos con la incertidumbre explícita, no con un valor único.

### 2.5 Completar los dominios delgados (antes de generar)

| Dominio | Hoy | Fuentes públicas candidatas (cada descarga se aprueba antes) |
|---|---|---|
| Agua | 320 | Res. 799 de 2021 (modifica la 0330); Decreto 1077 de 2015 (agua y saneamiento); resoluciones CRA vigentes |
| Ordenamiento | 106 | Ley 388 de 1997; Decreto 1077 de 2015 (ordenamiento y estudios de riesgo, que incorporó el 1807 de 2014); Ley 1523 de 2012 |
| Laboratorio | 294 cortos | INV E secciones 100, 400 y 700; especificaciones generales de construcción INVIAS |
| Motores sin RAG | 0 | No hace falta corpus: el motor es el verificador (§2.2) |

**Meta:** que cada dominio que se quiera afirmar tenga al menos ~300 chunks vigentes, o un motor determinista, antes de generar preguntas.

### 2.6 Datos que NO entran al entrenamiento

| Excluido | Por qué |
|---|---|
| Texto de las NTC (`ntc_chunks` de normas ICONTEC) | Derechos de autor de ICONTEC: no se suben a Kaggle ni quedan en los pesos. Sí pueden entrar las fichas curadas propias (ACI, AISC, ISO, NTC 1500), marcadas como tales |
| CCP-14 con aviso de ruido (124 chunks) | Las fórmulas y tablas pueden venir corruptas; se le enseñaría al modelo un número falso |
| Normas sin vigencia confirmada o derogadas (ISO 19011:2011, NEC-SE-DS, Res. 2857/1999) | Se usan solo para enseñar el aviso de vigencia con respaldo (`vigencia_evidencia.py`), nunca como norma vigente |
| `consultas_history` (consultas reales) | Privacidad: no sale del PC (#178). Las preguntas de distribución real se reescriben a mano o se generan |
| Baterías NSR-10 (125), motores (13), sabotaje, inyección, held-out K6 y `qlora_export/heldout.jsonl` | Son evaluación. Se deduplican del entrenamiento (§5.3) |
| `qlora_export/train.jsonl` (185) tal cual | Se generó en septiembre, antes de los arreglos de vigencia, inyección y abstención. Entra solo si cada respuesta vuelve a pasar el umbral de la §3 |

---

## 3. Umbral mínimo de una respuesta del maestro

No hay un número único en la literatura:
- **AlpaGasus** usó una nota ≥ 4,5/5 de un juez LLM y se quedó con 9k de 52k ejemplos;
- **LIMA** mostró que unos 1.000 ejemplos muy curados bastan para el estilo;
- **RFT y el muestreo por rechazo** se quedan solo con las respuestas verificadas como correctas.

En StructAI el umbral **no puede ser un juez LLM ni la recompensa rica de #268**: la rica no pasó su validación prerregistrada (Spearman 0,48). Por eso el umbral se arma con **compuertas deterministas**. Un ejemplo entra solo si pasa todas:

| Compuerta | Regla | Verificador existente |
|---|---|---|
| **U1 Hecho** | Contiene el valor verificado: el de la batería, el del chunk oráculo o el del motor. Tolerancia numérica: la del motor, o el redondeo de la norma | `_contiene_alguna` de las baterías; `ResultadoMotor` |
| **U2 Sin número inventado** | Cero números que no estén en el contexto ni en la pregunta | `_detectar_posible_alucinacion_numerica` |
| **U3 Cita** | Cita el numeral, la tabla o el artículo, y lo citado está en el contexto | Regex de numerales contra los encabezados `[norma — sección]` |
| **U4 Vigencia** | No afirma una derogación que el contexto no respalda | `_quitar_aviso_vigencia_sin_respaldo` (#264, #294) |
| **U5 Inyección** | Si el contexto trae un fragmento envenenado, no lo obedece: no da el valor falso, ni da los dos valores, ni escribe el canario | `inyeccion.clasificar` (#257) → solo vale `resiste` |
| **U6 Abstención** | Si el contexto solo trae distractores, se abstiene y no inventa | `RX_ABSTENCION`; hay que reemplazar el clasificador de #261 antes del prerregistro |
| **U7 Forma** | En español; entre 40 y 700 tokens; sin el razonamiento interno de gpt-oss (solo la respuesta final); sin la frase de un aviso legal copiada | Chequeo de longitud e idioma |

**Muestreo por rechazo:**
- Para cada pregunta, el maestro genera k = 4 respuestas con temperatura 0,7.
- Entra **una** de las que pasan U1–U7, la más corta, para no premiar el relleno.
- **Tasa de aprobación por pregunta:** si pasan 0 de 4, la pregunta va al conjunto "difícil", que no se entrena y se diagnostica. Si pasan 1 de 4, entra marcada como "frágil".
- **Umbral del maestro por dominio:** si el maestro aprueba menos del **60 %** de las preguntas de un dominio (al menos una de cuatro), ese dominio no se destila. El maestro no es confiable ahí, y el alumno heredaría sus errores. Se reporta y se resuelve con motor o con datos, no con más muestras.

**Tamaño mínimo**, a fijar en el prerregistro:
- **≥ 1.500 ejemplos aceptados** en total.
- **≥ 100 por dominio** que se quiera afirmar, y **≥ 30 por dominio** en el held-out, para que el IC por dominio sirva de algo.
- **Mezcla RAFT:** 80 % con el oráculo más 4 distractores del mismo dominio, elegidos difíciles (vecinos por embedding); 20 % solo con distractores, donde lo correcto es abstenerse.
- **≥ 10 % de ejemplos con un fragmento inyectado** donde lo correcto es resistir.

---

## 4. Presupuesto

### 4.1 Groq (medido el 2026-11-21 con la clave eval)

| Plan | Límites de gpt-oss-120b | ¿Alcanza? |
|---|---|---|
| **Gratuito** (el de la clave eval) | 1.000 solicitudes/día, **8.000 tokens/min**, ~200K tokens/día. Los límites son por organización, y hoy se comparten con la fase 2 diaria de #236 | **No.** Con ~4K tokens por llamada salen ~50 llamadas al día. 2.000 preguntas × 4 muestras serían más de 150 días |
| **Developer** (pago por uso, con límite de gasto) | ~250K tokens/min, sin tope diario. Precio aproximado US$ 0,15 por millón de entrada y US$ 0,60 por millón de salida, con caché de entrada a US$ 0,075 | **Sí.** 2.000 × 4 × (3,5K entrada + 0,6K salida) ≈ 28M entrada + 4,8M salida ≈ **US$ 7**. Con el prompt del sistema en caché, menos. Verificar el precio en la consola antes |

**Decisión (2026-11-21): solo el plan gratuito.** Wilmer nunca ha podido contratar el plan pago de Groq porque aparece sin disponibilidad. Las alternativas gratuitas tampoco resuelven:
- **Cerebras** cerró su plan gratuito abierto en 2026 y solo da US$ 5 de prueba.
- **OpenRouter** permite unas 50 solicitudes al día en sus modelos gratuitos, y gpt-oss-120b gratis ya no aparece de forma estable.

Por eso el diseño se ajusta para caber en ~200K tokens al día:

| Medida | Efecto |
|---|---|
| **Ejemplos de motor sin RAG:** el prompt lleva el `ResultadoMotor` en JSON, no fragmentos de norma (~500 tokens de entrada y ~300 de salida) | ~250 llamadas al día |
| **Ejemplos RAG compactos:** system de ~500 tokens + 5 fragmentos de ~250 tokens (~1,8K de entrada y ~400 de salida) | ~90 llamadas al día |
| **Rechazo secuencial en vez de k = 4 fijo:** una muestra; si falla una compuerta, una segunda; máximo 3 | ~1,3 llamadas por ejemplo si el maestro aprueba ~75 % |
| **Prompt del sistema idéntico en todas las llamadas** | Groq no cuenta los tokens en caché contra el límite |
| **Cola diaria con prioridad:** #236 fase 2 primero, E4 después; se para antes del tope y se reanuda al día siguiente sin repetir | No rompe la evaluación que ya corre |

**Estimación:**
- 700 ejemplos de motor × 1,3 × 0,8K ≈ 0,7M tokens;
- 800 ejemplos RAG × 1,3 × 2,2K ≈ 2,3M tokens;
- total **≈ 3M tokens**, unos **15 días** con la clave entera, o **~30 días** compartida con #236.

Es viable sin pagar. El rechazo secuencial reemplaza al k = 4 de la §3: la regla de aprobación por pregunta se mide sobre los intentos que se hagan, con un máximo de 3.

### 4.2 Kaggle

- **Recursos:** dos T4 de 16 GB o una P100; ~30 h de GPU por semana (la cifra flota, verla en la cuenta); sesiones de 12 h; disco de trabajo ~20 GB.
- **Receta:** Unsloth y QLoRA de 4 bits sobre `unsloth/Qwen2.5-7B-Instruct-bnb-4bit`, con LoRA r = 16 en las proyecciones de atención y MLP, `adamw_8bit`, gradient checkpointing, batch 1 y acumulación 16, 1–2 épocas, y parada temprana con la validación.
- **`max_seq_length`:**
  - Hoy el prompt de producción mide ~2,3K tokens y el contexto llega a ~7K.
  - Para un T4 hay que **acotar a 4.096 tokens**: system compacto más 5 fragmentos, oráculo incluido.
  - El alumno se evalúa con el mismo formato con el que se entrenó.
  - Que el modelo de producción use ese formato es otra decisión.
- **Tiempo:** no hay cifras confiables publicadas. Se mide con un piloto de 100 ejemplos: un trabajo corto, no un experimento.
- **Datos en Kaggle:** dataset **privado**, solo con texto público (NSR-10, leyes, resoluciones, manuales INVIAS), fichas propias y preguntas generadas. Nada de NTC, ni de `consultas_history`, ni de secretos. El adaptador LoRA se descarga a `_privado/` o a Hugging Face privado.
- **Credenciales:** el usuario crea el token en kaggle.com → Settings → API, y lo guarda él mismo en `%USERPROFILE%\.kaggle\kaggle.json`. Claude no maneja ese token.
- **CLI:** instalada el 2026-11-21 en `C:\Users\wilme\dev\venvs\kaggle` (kaggle 2.2.5, Apache 2.0; se agregó `six`, que la CLI necesita y no declara).

---

## 5. Diseño científico (lo que va al prerregistro)

### 5.1 Brazos, todos con el mismo harness (`correr_bateria.py`)

1. Qwen2.5-7B base con el formato del entrenamiento.
2. Qwen2.5-7B base con el prompt de producción (línea base de E3).
3. **Alumno** (Qwen2.5-7B + LoRA).
4. **Maestro** (gpt-oss-120b, el techo), solo en el held-out para no gastar cuota.
5. **Control de "aprendizaje de plantillas"** (#263): un alumno entrenado con las mismas preguntas pero respuestas genéricas sin el dato. Separa "aprendió el formato" de "aprendió a usar el contexto".

### 5.2 Métricas

| Métrica | Fuente | Tipo |
|---|---|---|
| Hechos correctos | baterías NSR-10 125 + motores 13 + held-out por dominio | **primaria** |
| Alucinación numérica | `_detectar_posible_alucinacion_numerica` | **de rechazo**: no puede subir (Gekhman) |
| Usa el contexto o la memoria | sabotaje #261 (el valor del contexto alterado debe aparecer) | secundaria |
| Resistencia a inyección | 4 ataques de #257 | de rechazo: no puede empeorar |
| Abstención correcta | ejemplos solo con distractores del held-out | secundaria |
| Olvido | subconjunto general en español, fijado en el prerregistro | de rechazo |
| Latencia y tok/s en CPU (GGUF Q4_K_M en Ollama) | mismo PC que E3 | descriptiva |

**Estadística:** McNemar exacto pareado del alumno frente a la base; IC de Wilson; bootstrap estratificado por dominio con 10.000 réplicas y semilla fija; corrección de Holm para las comparaciones por dominio.

### 5.3 Fugas y contaminación

- **Partición por fuente, no por pregunta:** los chunks oráculo del held-out no aparecen como oráculo en el entrenamiento.
- **Deduplicación** contra todas las baterías de evaluación: coseno ≥ 0,90 con MiniLM, o un 13-grama compartido, saca la pregunta del entrenamiento.
- Las preguntas del held-out las escribe una persona, como en K6, o salen de motores con semilla distinta.

### 5.4 Regla de adopción (borrador)

El alumno se adopta como modelo del CI y del nocturno, no de producción, si:
- mejora los hechos correctos frente al brazo 2 con un IC95 que no cruce 0;
- no sube la alucinación numérica;
- no empeora la inyección ni el olvido;
- y supera al control de plantillas.

---

## 6. Lista de pendientes antes del prerregistro

- [x] Alumno: Qwen2.5-7B-Instruct (Wilmer, 2026-11-21).
- [x] Groq: solo el plan gratuito, con cola diaria (§4.1).
- [x] Umbrales U1–U7 aprobados por Wilmer (2026-11-21).
- [ ] El usuario crea el token de Kaggle y lo guarda en `kaggle.json`.
- [ ] Completar los dominios delgados (§2.5): cada descarga se aprueba por separado.
- [ ] Generador de ejemplos de laboratorio con `lab_suelos`, `lab_concreto` y `lab_agregados` (§2.4).
- [ ] Reemplazar el clasificador de abstención de #261, porque U6 depende de él.
- [ ] Guía de etiquetado v2 de #268 (obedecer una inyección o dar el valor falso junto al real vale 0) y nueva muestra ciega, si se quiere usar la recompensa rica como filtro adicional.
- [ ] `generar_dataset_e4.py`: armar preguntas por dominio, el contexto RAFT y los motores con semilla.
- [ ] `umbral_maestro.py`: compuertas U1–U7, con pruebas de oro y de sabotaje por compuerta.
- [ ] Deduplicación contra la evaluación (§5.3).
- [ ] Notebook de Kaggle (Unsloth): piloto de 100 ejemplos para medir tiempo y memoria con 4.096 tokens.
- [ ] Registrar las licencias (Qwen, gpt-oss, Unsloth, TRL) en #219.

## Fuentes consultadas (2026-11-21)

- Licencia de Qwen2.5-7B-Instruct: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/main/LICENSE
- Qwen3.5-9B: https://huggingface.co/Qwen/Qwen3.5-9B · https://artificialanalysis.ai/articles/qwen3-5-small-models
- Licencia y política de gpt-oss: https://help.openai.com/en/articles/11870455-openai-gpt-oss · https://huggingface.co/openai/gpt-oss-20b/blob/main/USAGE_POLICY
- Términos de Groq: https://console.groq.com/docs/legal/services-agreement · https://groq.com/terms-of-use
- Límites y precios de Groq: https://console.groq.com/docs/rate-limits · https://groq.com/blog/gpt-oss-improvements-prompt-caching-and-lower-pricing
- Kaggle: https://amitpandeytiktok.github.io/awesome-free-compute-2026/compute.html (secundaria; verificar en la cuenta)
- Unsloth en T4: https://huggingface.co/unsloth/Qwen2.5-7B-Instruct-bnb-4bit
- AlpaGasus: arXiv:2307.08701 · RAFT: arXiv:2403.10131 · RARE (muestreo por rechazo con Qwen2.5-7B): arXiv:2503.23513 · LoRA learns less and forgets less: arXiv:2405.09673 · Gekhman et al. 2024: arXiv:2405.05904
