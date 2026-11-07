# Protocolo de métricas de evaluación sin LLM (issue #95, Frente A), definido ANTES de correrlo — 2026-11-07

**Objetivo:** calcular métricas de recuperación, citas, alucinación numérica, abstención y producción **sin llamar a ningún modelo de lenguaje** (sin cuota de OpenAI ni de Groq), usando solo lo ya guardado: `baseline_2026-09-09_278preguntas_muestras.jsonl` (pregunta, respuesta, 10 contextos recuperados, respuesta de referencia), su `scorecard.csv` (RAGAS) y la tabla `consultas_history` de producción.

## Qué es y qué no es cada métrica
Son **proxies léxicos**, no juicios humanos. Un contexto «relevante» aquí es uno que **contiene los datos clave de la respuesta de referencia**, no uno que un experto haya marcado. Por eso se valida contra el juez RAGAS (M1) y se deja lista la anotación humana (M7).

## M1 — Relevancia por cobertura léxica y su validación
- **Palabras clave de la referencia:** números (con decimales), códigos normativos (patrón `[A-K]\.\d+(\.\d+)*` y «Tabla/Figura X.Y-Z») y palabras de ≥ 6 letras sin acentos que no estén en una lista fija de palabras vacías (`PALABRAS_VACIAS` en el script).
- **cobertura(contexto)** = |claves de la referencia presentes en el contexto| / |claves de la referencia|. **Contexto relevante:** cobertura ≥ 0,5.
- **Validación (criterio de uso):** ρ de Spearman entre la cobertura máxima en el top-10 y `context_recall` de RAGAS (filas donde existe) debe ser > 0,30, con IC95 % (bootstrap por clúster título/tipo) que excluya 0. **Si no se cumple, las métricas M2 no se publican como medida de recuperación.**

## M2 — Recuperación
- **recall@K** (K = 1, 3, 5, 10): fracción de preguntas con ≥ 1 contexto relevante en las primeras K posiciones. **MRR:** media de 1/rango del primer relevante (0 si no hay). **NDCG@10:** con relevancia graduada = cobertura.
- **Supuesto declarado:** el orden de `retrieved_contexts` es el orden de recuperación tras el reranking. Se excluyen las preguntas adversariales (ADV): no tienen una respuesta de contenido contra la cual medir.
- Por tipo y global, con IC95 % por clúster (2.000 réplicas).

## M3 — Corrección de citas
Se extraen de cada respuesta los códigos normativos citados (mismo patrón). **Cita con soporte** = el código aparece en algún contexto recuperado. Se reporta la tasa de citas con soporte por respuesta y agregada. Una cita sin soporte puede ser alucinación o conocimiento previo del modelo; **no se distingue** con esta métrica.

## M4 — Posible alucinación numérica
Fracción de respuestas con ≥ 1 cifra (de ≥ 2 dígitos o con decimales) que no aparece en ningún contexto recuperado (excluyendo las cifras presentes en la propia pregunta). Mismo criterio que `_detectar_posible_alucinacion_numerica` de `rag_multi_norma.py`.

## M5 — Abstención
Respuesta con abstención = contiene alguna frase de una lista fija («no tengo», «no se encuentra», «no cuento con», «no puedo confirmar», «no está en», «no hay información», «no dispongo»). **Adversariales:** tasa de abstención (esperada alta). **No adversariales:** tasa de **falsa abstención** (esperada baja); en las compuestas (COMP) es el síntoma del issue #97. IC de Wilson.

## M6 — Producción
De `consultas_history`: latencia p50/p95/p99 y su IC (bootstrap), consultas con `feedback_util` (👍/👎) y tasa de 👍 con IC de Wilson. n muy pequeño (≈ 53 consultas en total): se reporta tal cual, con la advertencia.

## M7 — Acuerdo entre expertos (preparado, no ejecutable sin personas)
Se genera `anotacion_experto_muestra.csv` con 60 preguntas estratificadas por tipo (semilla fija) y columnas para relevancia de los 3 primeros contextos (0/1/2), corrección de la respuesta (0/1/2) y corrección de la cita (0/1). `kappa_expertos.py` calcula κ de Cohen (2 anotadores) o de Fleiss (≥ 3) y compara a los anotadores contra los proxies de M1-M4.

## Limitaciones declaradas
Los proxies léxicos penalizan la paráfrasis y premian la copia literal; las referencias son de longitud y estilo variables; la validez de M2 depende de que M1 se cumpla; el dataset de 278 preguntas es el que el propio sistema ayudó a construir (riesgo de circularidad); `consultas_history` es una muestra pequeña y no representa a los evaluadores futuros.

## Aclaraciones registradas al correr (2026-11-07)
1. **IC por pregunta en los grupos de un solo tipo especial.** La primera corrida usó el tipo como clúster también dentro de cada tipo (COLOQ, COMP, SINT), lo que dejó un único clúster e intervalos de ancho cero. Era un error de implementación, no una elección guiada por resultados: en esos grupos el IC es por pregunta; en GLOBAL y `hecho` siguen los clústeres por título.
2. **Léxico de abstención ampliado, POST HOC.** Con el léxico fijado antes, las adversariales daban 57,1 % de abstención (16/28). Al revisar a mano las 12 sin coincidencia, 10 eran abstenciones con frases que la lista no incluía («el contexto no incluye / no menciona»). Se reportan **ambas** cifras: a priori y ampliada (esta última post hoc, 96,4 %, 27/28). Las tasas de falsa abstención del léxico ampliado pueden estar infladas por frases que aparecen en respuestas normales (p. ej. «no menciona» en un matiz).
3. **Validez del proxy por tipo (descriptiva):** ρ con `context_recall` de RAGAS: COLOQ +0,77, hecho +0,45, SINT +0,43, COMP +0,37; todas positivas. **NDCG@10 no se interpreta en SINT y COMP:** se normaliza contra el mejor orden posible de los mismos 10 contextos, de modo que da valores altos aunque la cobertura absoluta sea baja.
4. **Latencia por mes (descriptiva, post hoc).** Agregada al reporte tras ver la cola larga del p95/p99.
