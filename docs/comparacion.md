# StructAI frente a un asistente de IA genérico

## Por qué esta comparación, y no otra

No comparo StructAI contra un producto comercial específico de la competencia — no tengo acceso verificado a sus bases de datos internas, y afirmar algo sobre una herramienta ajena sin poder probarlo no es un estándar que me interese aplicar aquí. La comparación que sí puedo sostener con evidencia, y la que en la práctica decide si un ingeniero usa StructAI o no, es esta: **¿qué pasa si en vez de StructAI le preguntas lo mismo directamente a un asistente de IA de propósito general** (ChatGPT, Claude, Gemini, sin ninguna base de datos normativa ni de precios conectada)?

Cada fila de la tabla es verificable por cualquiera, hoy mismo:

- Las cifras de cobertura, en vivo, sin necesidad de confiar en este documento: [`GET /data-status`](https://structai-api-235651108862.us-east1.run.app/data-status).
- El comportamiento ante una pregunta sin contenido cargado, probando el chat en [structai.online](https://www.structai.online).
- El código de las reglas de citación y de bloqueo de alucinación, público, en [`packages/construdata/rag_multi_norma.py`](../packages/construdata/rag_multi_norma.py).

## Tabla comparativa

| Criterio | StructAI | Asistente de IA genérico |
|---|---|---|
| Cita la norma exacta (sección/artículo, no solo el nombre del reglamento) | Sí — cada respuesta de `/ask` incluye norma, sección y `norma_ref` verificable | No de forma confiable — puede citar un artículo que no existe o mezclar versiones de la norma sin advertirlo |
| Si no tiene contenido cargado para un tema, lo dice explícitamente | Sí — el dominio se detecta y el sistema responde que no hay contenido cargado en vez de inventar una respuesta | No — tiende a generar una respuesta plausible aunque no tenga la información real, sin señal de que está adivinando |
| Precio de materiales con proveedor identificable | Sí — 78 proveedores mipyme reales a nivel nacional (catálogo IAD MIPYMES, Colombia Compra Eficiente) más 2 proveedores locales del Atlántico con SKU verificado en ficha de producto | No — no tiene acceso a ninguna base de precios real; cualquier cifra que dé es una estimación sin fuente verificable |
| Costo de la búsqueda semántica (embeddings) | Cero — modelo local (`sentence-transformers`, 384 dimensiones), sin llamadas a un proveedor externo por consulta | No aplica — no hace búsqueda sobre un corpus propio |
| Cobertura normativa verificable por título/capítulo | Sí — NSR-10 con núcleo verbatim real en varios títulos (extraído directo de los PDF oficiales, no una paráfrasis genérica), 18 normas NTC, SGSST completo, RAS 2000 (11/11 módulos) | Depende del material que haya visto en su entrenamiento, sin forma de auditar qué tan actualizado o completo está |
| Auditable — se puede verificar de dónde salió cada dato | Sí — cada chunk normativo y cada precio tiene una fuente registrada (`normas_registro`, `apu_precios_referencia.fuente`), y el pipeline de carga está versionado en el repositorio (`scripts/ingesta/`) | No — no hay forma de rastrear el origen de una afirmación específica |

## Lo que esta comparación no dice

Un asistente de IA genérico sigue siendo más flexible para preguntas abiertas, de redacción, o fuera del dominio normativo/de precios colombiano — StructAI no compite ahí, ni lo intenta. La comparación es específica: **para una pregunta que un ingeniero civil colombiano necesita responder con una cita verificable**, StructAI está construido para eso desde la base de datos hacia arriba; un asistente genérico, no.

## Estado honesto de la cobertura (verificado, no proyectado)

StructAI es un piloto en producción, no una cobertura nacional completa todavía. Concretamente, hoy:

- La base de precios con proveedor local verificado (SKU + ficha de producto) cubre el Atlántico; la base de precios nacional (IAD MIPYMES) da referencia de todo el país pero sin desglose por ciudad de cada proveedor.
- NSR-10 tiene profundidad verbatim real en varios títulos; otros conservan una síntesis técnica de referencia, no transcripción palabra por palabra todavía.
- El roadmap de qué falta y qué está en curso es público: [issues abiertos del repositorio](https://github.com/wilmerjoseperezorozco-dev/structai/issues), no una promesa sin fecha.

Prefiero que este documento quede corto en algunas filas antes que inflar una comparación que no pueda sostener si alguien la verifica — es la misma exigencia que le pido a cada respuesta que da el sistema.
