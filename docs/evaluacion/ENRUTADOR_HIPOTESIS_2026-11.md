# ¿Sirve el enrutador contrastivo para StructAI? Hipótesis, evidencia y literatura

Fecha: 2026-11-10. Issue #169. Complementa `scripts/evaluacion/golden/e1_enrutador/INFORME_E1.md`.

## Hipótesis

Los dominios de StructAI son "continentales": comparten vocabulario y conceptos (sismo aparece en geopot, vivienda, normativa general, Perú y Ecuador; muros en vías y en vivienda; concreto en geopot, vías y precios). Un enrutador que representa cada dominio con **un solo centroide de embeddings** y decide por coseno, **sin regla de rechazo**, no puede separarlos de forma confiable.

## Evidencia propia (sin LLM, reproducible)

| Medición | Valor | Lectura |
|---|---|---|
| Coseno entre centroides de dominio | mediana 0,506; máx. 0,782 (geopot–vías), 0,749 (Perú–Ecuador), 0,690 (aquai–geopot) | Los dominios ocupan regiones vecinas del espacio |
| Margen top-1 vs top-2 cuando el contrastivo acierta | mediana 0,075 | Incluso los aciertos son por poco |
| Margen cuando falla | mediana 0,033 | Los errores son casi empates |
| Contrastivo solo, aceptable (96 preguntas) | 57,3 % | Por debajo de keyword solo |
| Caso Sincelejo | ventaja de 0,085 sobre `normativa_general` | Un umbral absoluto no lo atrapa (0,557 > τ); un margen sí |

La hipótesis se sostiene **para el método actual**: centroide único + coseno + sin rechazo.

## E1b: ¿cambiar de representación o de método? (test n = 58)

| Variante | Estricto | Aceptable [IC95] | p Holm vs producción |
|---|---|---|---|
| V1 producción (keyword → centroides) | 55,2 % | 70,7 % [58–81] | — |
| V3 producción + margen δ = 0,18 | 56,9 % | 86,2 % [75–93] | 0,059 |
| C1 TF-IDF (palabras + caracteres) + SVM, con rechazo | 77,6 % | 79,3 % [67–88] | 0,80 |
| C2 TF-IDF + regresión logística | 75,9 % | 77,6 % [65–86] | 0,80 |
| **C3 MiniLM (el mismo de producción) + regresión logística, con rechazo** | **82,8 %** | 84,5 % [73–92] | 0,23 |

Entrenamiento: 124 preguntas (los ejemplos de referencia del contrastivo + dev del E1). El umbral de rechazo se ajustó por validación cruzada sobre el entrenamiento.

Lectura:
- **No se replica** el resultado de Bansal y Agarwal (2026), donde lo léxico superó a MiniLM. Su tarea enruta por *tipo* de consulta (factual, razonamiento, resumen), en inglés y con 7.727 consultas. La nuestra enruta por *dominio*, en español, con 124 ejemplos.
- La misma representación MiniLM pasa de 57 % (centroides) a 83 % estricto (clasificador discriminativo con rechazo). **El problema era el método de decisión, no los embeddings.**
- V3 gana en "aceptable" principalmente refugiándose en `normativa_general`. Es seguro, pero acierta el dominio exacto mucho menos que C3.
- Ninguna diferencia es significativa tras Holm. Con 58 casos esto es una señal, no una conclusión.

## Literatura que respalda o guía la elección

1. **Bansal y Agarwal (2026)**, *Lightweight Query Routing for Adaptive RAG: A Baseline Study on RAGRouter-Bench*, arXiv:2604.03455. Clasificadores clásicos baratos enrutan bien (TF-IDF + SVM, 93,2 % de exactitud). Dicen explícitamente que el enrutamiento que solo mira la consulta tiene un techo, y que lo que falta es enrutamiento **consciente del corpus**.
2. **Xu, Kang y Lü (2026)**, *A Multi-cluster Boundary Learning Method for Out-of-Scope Intent Detection via MiniLM Embedding*, arXiv:2607.07974. Con el mismo tipo de embedding (MiniLM), un solo prototipo por clase no basta: proponen varios clústeres por intención y aprender fronteras para detectar lo que queda fuera de alcance. Es directamente nuestro caso (dominios con subtemas: geopot = laboratorio + sísmica + POT).
3. **Chow (1970)**, *On optimum recognition error and reject tradeoff*, IEEE Trans. Information Theory. Base de la clasificación con opción de rechazo: abstenerse (aquí, caer a `normativa_general`) cuando la confianza es baja reduce el error. Justifica formalmente V3/C3 con rechazo.
4. **Ethayarajh (2019)**, *How Contextual are Contextualized Word Representations?*, EMNLP. Anisotropía: las representaciones ocupan un cono estrecho y cualquier par de textos tiene coseno alto. Explica por qué los scores del contrastivo viven en una franja angosta (0,25–0,60) y los márgenes son mínimos.
5. **Loghmani (2026)**, *Semantic Entanglement in Vector-Based Retrieval*, arXiv:2604.17677. Define un índice de entrelazamiento entre subdominios en el espacio vectorial y muestra que limita la precisión alcanzable; en un corpus de salud con unos 25 subdominios, reestructurar el contenido antes de vectorizar sube la precisión top-K de ~32 % a ~82 %. Es el análogo, del lado de la recuperación, de nuestro problema de enrutamiento.

## Qué sería lo idóneo para StructAI (a probar, no a integrar todavía)

Por orden de costo y de respaldo:
1. **Rechazo por margen** sobre `normativa_general` (V3). Es el cambio mínimo; arregla el caso de origen y cuenta con el respaldo de Chow (1970).
2. **Clasificador discriminativo sobre MiniLM con rechazo** (C3), en vez de centroides. Mismo modelo y mismo costo de inferencia. Necesita más ejemplos etiquetados por dominio (hoy 5 a 17 por dominio).
3. **Enrutamiento consciente del corpus (E1c).** Buscar primero en todo el corpus (la búsqueda híbrida ya lo hace) y decidir el dominio según de dónde vienen los mejores chunks, usando `FUENTES_DOMINIO`. Responde a la limitación que declaran Bansal y Agarwal, y cambia la pregunta de "¿de qué habla?" a "¿dónde está la respuesta?".
4. **Jerárquico:** primero país (Colombia / Perú / Ecuador) y si es pregunta de cálculo o de norma; después el motor. Ataca los pares más pegados (Perú–Ecuador, geopot–vías).

El enrutador por LLM queda fuera por ahora: agrega una llamada por consulta y hoy el respaldo de OpenAI no tiene crédito.

## Siguiente paso

- E1c (enrutamiento consciente del corpus), sin LLM, sobre el mismo test.
- Ampliar las etiquetas: ~60 preguntas held-out de otra persona, más preguntas reales de `consultas_history` cuando haya tráfico.
- Integrar solo la variante que gane con IC que no cruce 0 y sin regresión en `test_rag_motores_regresion.py`.
