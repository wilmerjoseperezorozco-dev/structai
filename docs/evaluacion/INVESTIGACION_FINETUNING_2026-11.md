# ¿Fine-tuning de un modelo local para StructAI? Y otras líneas de alto valor en ingeniería de IA

Fecha: 2026-11-11. Issues #172 (modelos locales) y #169/#170 (evaluación). Documento de decisión: qué hacer, qué no, y cómo medirlo.

## 1. Respuesta corta

Sí se pueden **ajustar los pesos** de un modelo como `qwen2.5:7b` para StructAI, pero conviene entender tres cosas antes:

1. **No se reentrenan todos los pesos.** Con LoRA/QLoRA se entrenan adaptadores pequeños (del orden de 0,1–1 % de los parámetros) sobre el modelo congelado en 4 bits. Es lo que hace factible ajustar un 7B en una GPU de 15 GB.
2. **Este PC puede correr el modelo, pero no entrenarlo.** No tiene GPU. Entrenar un 7B en CPU tomaría días. Sí puede entrenar aquí modelos pequeños (embeddings, clasificador del enrutador, modelos de 0,5–1,5 B). Para el 7B, la vía práctica es una GPU prestada: Colab o Kaggle con T4 gratis, o una GPU por horas en el proyecto GCP `structai-507113`.
3. **El fine-tuning no debe usarse para meterle la norma al modelo.** La NSR-10 sigue en el RAG. Esto es lo que dice la literatura y coincide con lo que medimos.

## 2. Lo que dice la evidencia

| Trabajo | Hallazgo | Implicación para StructAI |
|---|---|---|
| Ovadia et al. (2024), *Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs*, EMNLP | El RAG supera consistentemente al fine-tuning para inyectar conocimiento, tanto el ya visto en entrenamiento como el nuevo | Las normas se quedan en el RAG; no se "entrenan" |
| Gekhman et al. (2024), *Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?*, EMNLP | Entrenar con hechos que el modelo no sabía aumenta linealmente su tendencia a alucinar; el fine-tuning sirve sobre todo para enseñar a *usar* lo que ya sabe. Lo mitigan la parada temprana y el filtrado de ejemplos desconocidos | Riesgo directo: un modelo ajustado con valores de la NSR-10 podría inventar valores con más confianza |
| Zhang et al. (2024), *RAFT: Adapting Language Model to Domain Specific RAG* (arXiv:2403.10131) | Entrenar con la pregunta + el documento correcto + **documentos distractores** + una respuesta razonada que cita el documento mejora el RAG de dominio | **Esta es la receta adecuada**: enseñar a usar el contexto, citar el numeral e ignorar lo irrelevante, no memorizar la norma |
| Medición propia, #172 | Sin contexto, los 4 modelos locales confunden "asentamiento del concreto" (slump) con hundimiento | Confirma que su conocimiento de ingeniería colombiana es débil y que el RAG es indispensable |
| Medición propia, E1e (#169) | 38 ejemplos de la distribución real valen más que 333 de otra | Un dataset de fine-tuning sesgado empeora el modelo, aunque sea grande |

## 3. Lo que ya existe en el repo

`scripts/evaluacion/qlora_export/` (2026-09-29) tiene **185 ejemplos de entrenamiento y 31 de held-out** en formato de chat (system/user/assistant). El `system` es el prompt real de producción, el `user` lleva el contexto recuperado tal como lo arma `ask()`, y el `assistant` es la respuesta de Groq (`gpt-oss-120b`) filtrada por RAGAS (faithfulness y context recall). Es material de **destilación**: enseñar al modelo chico a responder como el grande, con el mismo contexto.

Dos problemas a resolver antes de usarlo:
- **Está sesgado hacia NSR-10:** de los 216 ejemplos, unos 170 son de NSR-10, NTC u otras normas generales y unos 46 de precios (conteo por palabras clave en la pregunta). Es el mismo tipo de sesgo que el E1e mostró dañino. Faltan los motores: agua, vías, gerencia, vivienda y laboratorio.
- **No tiene distractores explícitos** al estilo RAFT, ni ejemplos de abstención en suficiente cantidad.

## 4. Plan propuesto (E4: fine-tuning con medición antes/después)

1. **Línea base local:** el piloto en curso de #172 (qwen2.5:7b sin ajuste, 38 casos), y luego la batería completa (138).
2. **Dataset RAFT de StructAI:** a partir de `qlora_export`, más preguntas de todos los dominios (#170):
   - el contexto se arma con la recuperación real; en ~20 % de los ejemplos se quita el chunk correcto y la respuesta esperada es abstenerse;
   - la respuesta debe citar el numeral o la tabla;
   - solo se incluyen hechos verificables en el contexto (filtro de Gekhman: nada que el modelo deba "saber" de memoria);
   - partición por pregunta, y el held-out nunca se toca.
3. **Entrenamiento QLoRA** en Colab T4 con Unsloth, sobre `Qwen2.5-7B-Instruct` (y `Qwen2.5-3B` como alternativa más rápida en este CPU): 1–2 épocas, parada temprana con el held-out. Exportar a GGUF Q4_K_M y crear `structai-qwen7b` en Ollama con un Modelfile.
4. **Medición con el mismo harness** (`scripts/evaluacion/golden/e3_modelos_locales/correr_bateria.py`): batería de 138 casos + held-out de `qlora_export`. McNemar pareado frente al modelo base. Métricas: hechos correctos, abstención correcta, alucinación numérica, latencia.
5. **Criterio preregistrado:** el modelo ajustado se adopta solo si mejora los hechos correctos con IC que no cruce 0 **y no aumenta** la alucinación numérica (la advertencia de Gekhman).

Costo estimado: $0 con Colab o Kaggle gratis; el límite es el tiempo de sesión de GPU. Riesgo principal: que el modelo mejore el estilo y empeore la fidelidad. Por eso la alucinación numérica es criterio de rechazo.

## 5. Otras líneas de alto valor en ingeniería de IA para StructAI

Ordenadas por valor esperado y por lo que se puede hacer **en este PC sin GPU**:

| # | Línea | Por qué importa en StructAI | ¿Se puede aquí? |
|---|---|---|---|
| 1 | **Fine-tuning del modelo de embeddings** (MiniLM 384-dim) con pares pregunta → chunk correcto (pérdida contrastiva con negativos del mismo lote) | Mejora a la vez la **recuperación** y el **enrutador**: C3/K6 usa los mismos embeddings. Ataca el entrelazamiento geopot–vías medido en el E1c (coseno 0,78) | Sí, en CPU: el modelo es chico. Se evalúa con un índice local (recall@k, E2) antes de reindexar producción |
| 2 | **Cascada de modelos con el umbral de confianza** | El τ del E1e también sirve para decidir **quién responde**: preguntas fáciles y seguras → modelo local o barato; difíciles → Groq. Baja costo y dependencia de cuota | Sí, cuando #172 diga qué modelo local es confiable |
| 3 | **Salidas estructuradas + verificación determinista** | Para la auditoría de documentos (T2 de #169): el LLM extrae valores a un esquema JSON y Python compara contra la lista de control. Es la hipótesis principal del benchmark | Sí: Ollama soporta `format` con JSON Schema |
| 4 | **Juez LLM calibrado con anotación experta** | La auditoría #109 mostró un juez sin calibrar y métricas con hasta 51 % de faltantes. Un juez local evaluado contra anotaciones humanas (`anotacion_experto.py`) evalúa sin gastar cuota | Sí, lento pero gratis |
| 5 | **Observabilidad por consulta** | Trazas de enrutamiento, chunks usados, latencia, costo y alucinación por consulta real. Es el pool del aprendizaje activo | Sí, por ejemplo Langfuse self-hosted en el homelab |
| 6 | **Optimización automática de prompts** contra las baterías (estilo DSPy) | Las baterías de 138 casos son una función objetivo lista | Sí con un modelo local; es caro en tiempo |
| 7 | **Reranker cross-encoder ajustado al dominio** | Producción ya usa un reranker; ajustarlo con los mismos pares de la línea 1 | Sí en CPU para uno pequeño |
| 8 | **Serving local eficiente** (prompt caching del system prompt, `keep_alive`, `num_ctx` justo, cuantización) | La lectura del prompt es el cuello de botella medido (30 tok/s en el 7B) | Sí |

**Sobre usar el modelo local como respaldo de producción:** con ~3 minutos por respuesta en CPU, no sirve para el chat en vivo (Cloud Run además no tiene GPU). Sí sirve para el CI, la evaluación y los procesos nocturnos. Para el respaldo de producción, lo práctico sigue siendo recargar OpenAI u otro proveedor barato. Se decide con los datos de #172.

## Referencias

- Ovadia, O., Brief, M., Mishaeli, M. y Elisha, O. (2024). Fine-Tuning or Retrieval? Comparing Knowledge Injection in LLMs. *EMNLP 2024*, 237–250. arXiv:2312.05934.
- Gekhman, Z. et al. (2024). Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations? *EMNLP 2024*. arXiv:2405.05904.
- Zhang, T. et al. (2024). RAFT: Adapting Language Model to Domain Specific RAG. arXiv:2403.10131.
- Dettmers, T. et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. *NeurIPS 2023*. arXiv:2305.14314.
- Hu, E. et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. *ICLR 2022*. arXiv:2106.09685.
