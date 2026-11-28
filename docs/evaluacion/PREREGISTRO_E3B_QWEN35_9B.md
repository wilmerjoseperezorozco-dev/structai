# Preregistro E3b, primer candidato: qwen3.5:9b frente a qwen2.5:7b (#302), 2026-11-27

Este documento se fija **antes** de generar una sola respuesta con qwen3.5:9b. Cualquier cambio posterior queda como
enmienda fechada al final, sin borrar lo de arriba.

## Pregunta

¿qwen3.5:9b responde mejor que qwen2.5:7b (línea base de E3 #172, modelo del CI nocturno y alumno actual de E4) en las
baterías de StructAI, con la misma recuperación, los mismos prompts y el mismo código?

## Modelos

| | Etiqueta en Ollama (WSL) | Cuantización | Licencia (página de Ollama, 2026-11-27) |
|---|---|---|---|
| Candidato | `qwen3.5:9b` | Q4_K_M | Apache 2.0 |
| Línea base | `qwen2.5:7b` | Q4_K_M | Apache 2.0 |

## Procedimiento

- **Batería:** las 142 pruebas `pytest -m llm` de `apps/api/tests`: 125 de NSR-10, 13 de motores y 4 más.
  - Calificación determinista: la misma `_contiene_alguna` de cada prueba, sin juez LLM.
  - En motores se exige además el dominio correcto.
- **Mismo código para los dos:** el mismo commit de master en el worktree `structai-nocturno`.
  - La línea base es la corrida del CI nocturno (`scripts/nocturno/ci_nocturno.sh`).
  - El candidato es la misma corrida con `STRUCTAI_LLM_LOCAL=qwen3.5:9b`.
  - Las dos van con el mismo índice RAG del despliegue, temperatura 0,1, `num_ctx` 16384 y `num_predict` 700.
  - Caché de respuestas apagada.
- **Razonamiento:** `STRUCTAI_OLLAMA_THINK=false` para qwen3.5:9b. Así su razonamiento no se come los 700 tokens de
  respuesta, y la latencia en CPU es comparable con la de qwen2.5:7b, que no razona.
  - Una corrida con razonamiento encendido sería otro brazo, con su propio preregistro.
- **Reintentos:** las pruebas llevan `flaky(reruns=1)`. El resultado de cada caso es el final tras ≤ 1 reintento, igual
  para los dos modelos.
- **Si la línea base de la noche no termina:** se repite la noche siguiente sobre el mismo commit. No se compara contra
  una corrida de otro commit.

## Análisis fijado de antemano

- **Prueba principal:** McNemar exacto (binomial bilateral) sobre los pares discordantes por prueba
  (qwen3.5 ✓ / qwen2.5 ✗ frente a qwen3.5 ✗ / qwen2.5 ✓), con α = 0,05.
- **Tamaño del efecto:** diferencia apareada de proporciones (qwen3.5 − qwen2.5) con IC95 por bootstrap de pares
  (10.000 réplicas, semilla 20261127).
- **Se informa además:**
  - aprobación absoluta de cada modelo con IC de Wilson;
  - resultados por batería (nsr10 / motores / resto);
  - duración total y por caso (p50/p95);
  - casos con error de infraestructura (Ollama caído, timeout), que se reportan aparte y no cuentan como fallo del
    modelo.

### Reglas de decisión

- IC95 entero por encima de 0: **qwen3.5:9b mejora** sobre qwen2.5:7b. Pasa a candidato a modelo del CI nocturno y a
  alumno de E4, decisión aparte con su PR.
- IC95 que cruza 0: **no se detecta diferencia** con este n. Se informa el efecto mínimo detectable y no se afirma
  equivalencia.
- IC95 entero por debajo de 0: **qwen3.5:9b es peor** en esta configuración.

### Comparación descriptiva con el maestro (no decide nada)

- Las respuestas de `openai/gpt-oss-120b` (Groq) en modo índice local de la fase 2 (`PREREGISTRO_INDICE_LOCAL.md`)
  cubren 126 de estas preguntas, con el mismo criterio de calificación.
- Se reporta la aprobación de qwen3.5:9b sobre esas 126 frente a la del maestro, **solo como referencia**, por tres
  diferencias:
  - otro commit (2026-11-16);
  - una sola generación, sin reintento;
  - otro proveedor.
- No se gasta cuota de Groq. La regla 1 de #302 (replantear E4 si un candidato iguala al maestro) necesita una
  comparación simétrica, con preregistro propio.

## Limitaciones declaradas

- Una sola muestra por modelo y caso (más el reintento): la variación propia del LLM entra como ruido.
- La calificación por subcadena no mide si el resto de la respuesta es correcto ni si cita bien.
- Las baterías las escribió el equipo, así que no son una muestra del uso real.
- El proyector de visión de qwen3.5 no se usa: las preguntas son solo texto.
