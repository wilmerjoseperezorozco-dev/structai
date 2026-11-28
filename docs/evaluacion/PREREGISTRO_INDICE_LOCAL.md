# Preregistro: efecto del índice RAG local en la calidad de las respuestas (2026-11-16)

Este documento se fijó **antes** de generar una sola respuesta de la fase 2. Cualquier cambio posterior al análisis
debe quedar como enmienda fechada al final, sin borrar lo de arriba.

## Pregunta

Desde la revisión `structai-api-00015-hot`, producción busca con el índice local (búsqueda exacta). Antes usaba las
RPC de Supabase, donde HNSW con `ef_search = 40` recorta la parte semántica. ¿El cambio sube, baja o no cambia la
proporción de respuestas que contienen el hecho verificado?

## Población y filtro

- Preguntas: todas las de `apps/api/tests/test_rag_nsr10_regresion.py` (`ask`) y `test_rag_motores_regresion.py`
  (`ask_delegado`).
- **Filtro 1** (`scripts/evaluacion/indice_local/filtro_contexto.py`): arma el prompt de generación en los dos modos.
  - La descomposición en sub-preguntas es la misma en los dos, hecha una sola vez con Groq y guardada en caché.
  - Si el prompt es idéntico byte a byte, la respuesta no puede depender del índice: la pregunta cuenta como **sin
    efecto** y no se genera.
- **Fase 2** (`fase2_generacion.py`): las preguntas con prompt distinto, en orden aleatorio con semilla `20261116`.

## Tratamiento y medición

- Una generación por modo y pregunta. Mismo modelo que producción (`openai/gpt-oss-120b` en Groq), temperatura 0,1,
  `reasoning_effort = low`. El orden de los dos modos también es aleatorio por pregunta.
- **Variable primaria:** aprueba = la respuesta contiene alguna de las variantes del caso, con el mismo
  `_contiene_alguna` de las baterías. En motores además se exige el dominio esperado.
- Se usa solo `GROQ_API_KEY_EVAL`, nunca la clave de producción. Supabase solo se lee y la caché de respuestas está
  apagada.

## Análisis fijado de antemano

- **Prueba principal:** McNemar exacto (binomial bilateral) sobre los pares discordantes local ✓ / RPC ✗ frente a
  local ✗ / RPC ✓, con α = 0,05.
- **Tamaño del efecto:** diferencia de proporciones apareada con IC95 por bootstrap de pares (10.000 réplicas,
  semilla 20261116).
- **Se informa además:**
  - el total de la batería: las preguntas sin efecto cuentan con la misma aprobación en ambos modos, aunque no se
    generaron;
  - resultados por batería (nsr10 / motores);
  - aprobación absoluta de cada modo con IC de Wilson.

### Reglas de decisión

- Si el IC95 está entero por encima de 0, **el índice local mejora** la calidad.
- Si cruza 0, **no se detecta diferencia** con este n. Se informa el n y el efecto mínimo detectable; no se afirma
  equivalencia.
- Si está entero por debajo de 0, **regresión**. Se revierte con `RAG_INDICE_LOCAL=false`, sin redesplegar, y se
  investiga.

## Limitaciones declaradas

- Una sola muestra por modo: la variación propia del LLM entra como ruido. Los pares la reducen pero no la eliminan.
- La calificación es por subcadena: no mide si el resto de la respuesta es correcto ni si cita bien la fuente.
- La cuota diaria de la clave (unos 200.000 tokens, ~6.000 por respuesta) da para ~15 pares por día. Si la clave vence
  antes de cubrir toda la población, se analiza la muestra aleatoria cubierta y se declara su tamaño.
- Las baterías las escribió el equipo, así que no son una muestra del uso real.

## Desviación declarada (2026-11-18)

El 18-11 la corrida se detuvo con HTTP 413: Groq rechazó un prompt por tamaño (≈ 11.800 tokens estimados, más que el límite de 8.000 tokens/min de la clave de evaluación). Como el orden es fijo, la corrida se habría detenido todos los días en la misma pregunta. Desde esta fecha, una generación rechazada con 413 se registra como **no aprobada** (`"error": "413"`) y se sigue con la siguiente. En el análisis se reportan aparte cuántas generaciones fueron 413 y en qué modo, y se da el resultado con y sin ellas. La decisión se tomó sin ver la respuesta de esa pregunta (no existe: Groq no la generó).

## Resultado (2026-11-27)

La fase 2 cubrió **toda** la población: 126 preguntas con prompt distinto × 2 modos = 252 generaciones, completas el 2026-11-22. Las 12 preguntas con prompt idéntico cuentan como sin efecto. El análisis es el fijado arriba, sin cambios, y está en `scripts/evaluacion/indice_local/analizar_fase2.py`; las tablas, en `resultados/RESULTADOS_FASE2.md`.

- **Prueba principal**, batería total, con 413 = no aprobada:
  - local 115/126 (91,3 %) frente a RPC 114/126 (90,5 %);
  - discordantes: 3 a favor de local y 2 a favor de RPC; McNemar exacto p = 1,00;
  - diferencia local − RPC = **+0,7 pts, IC95 [−2,2, +3,6]**.
- **Decisión según la regla:** el IC cruza 0, así que **no se detecta diferencia con este n**. El efecto mínimo detectable con 80 % de potencia es de unos ±4,5 pts. No se afirma equivalencia.
- **No hay regresión**, así que no aplica revertir con `RAG_INDICE_LOCAL=false`.
- **Sin los 11 pares con 413** (5 en local y 6 en RPC): 113/119 en los dos modos, discordantes 1/1, diferencia +0,0 pts, IC95 [−2,3, +2,3]. Misma conclusión.
- **Motores:** solo 6 preguntas generadas, todas aprobadas en ambos modos. Con ese n no se concluye nada por batería.
