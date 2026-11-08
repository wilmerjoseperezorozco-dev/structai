# Auditoría de evaluación: qué se mide en StructAI y qué no

Fecha: 2026-11-08. Issue de seguimiento: #109. Alcance: solo lectura. Se midió la cobertura de pruebas de los motores, se revisó la composición de las baterías de evaluación del RAG y se contó la información faltante en las métricas. No se modificó ningún componente.

## 1. Resumen

Se mide poco de lo que existe, y lo que se mide es estrecho. Los hallazgos principales:

1. **El RAG se evalúa casi solo sobre NSR-10.** De 278 preguntas, 48 son del Título H, 46 del F y 21 del A. No hay preguntas de vías, hidráulica, geotecnia, puentes, costos de obra ni hidrología. Hay además 55 preguntas de precios (APU) en una batería aparte.
2. **Las métricas con LLM tienen muchos valores faltantes y no al azar.** Faithfulness falta en 32,4 % de las filas y context_precision en 51,4 %. Solo 131 filas tienen las cuatro métricas. El análisis retroactivo (issue #95, A0) ya mostró que la ausencia depende del tipo de pregunta.
3. **El juez es un LLM sin calibrar y los datasets los escribió el mismo equipo que construye el sistema.** No hay concordancia medida con un experto humano a escala.
4. **Los motores de cálculo tienen pruebas, pero la cobertura es desigual** y `motor-topovia` no tiene ninguna.
5. **Cinco normas del registro tienen vigencia «desconocido».**
6. **Varios resultados de investigación (F1, etc.) no tienen validación externa.**

## 2. Motores de cálculo

Archivos de prueba por motor (conteo de archivos `test_*`; la cobertura de líneas se midió con `pytest --cov`):

| Motor | Archivos de prueba | Observación |
|---|---|---|
| motor-apu | 4 | Cubierto además por pruebas de API de precios y sinónimos |
| motor-deformacion | 4 | Mejor documentado con ejemplos y referencias |
| motor-aquai | 2 | Cobertura de líneas 74 %, la más baja de los motores con pruebas. El verificador de la Res. 0330 tiene 83 pruebas en el paquete |
| motor-estructural | 1 | Una sola batería para un dominio amplio |
| motor-vias | 1 | Issue #106: pavimento rígido sin verificación |
| motor-acero-frio | 1 | MVP |
| motor-geopot | 1 | |
| motor-gerencia | 1 | Sin referencias externas en las pruebas |
| motor-vulnerabilidad-vivienda | 1 | |
| motor-topovia | **0** | Sin pruebas |

Límite de esta tabla: contar archivos no mide calidad. Una prueba que reproduce el mismo código no valida el método. Solo se pudo constatar, por búsqueda de texto, que algunas pruebas citan artículos, tablas o ejemplos de libro; eso es un indicio y no una verificación.

La regla del proyecto exige 80 % de cobertura. Los motores medidos no se compararon uno por uno con esa cifra en este informe, salvo aquai (74 %, por debajo). Falta la tabla completa con porcentaje por motor.

## 3. Evaluación del RAG

### 3.1 Composición de las 278 preguntas

| Tipo | n | Faithfulness faltante | Faithfulness media (válidos) |
|---|---|---|---|
| hecho | 166 | 18,7 % | 0,80 |
| COLOQ (lenguaje coloquial) | 34 | 52,9 % | 0,68 |
| SINT (síntesis) | 30 | 40,0 % | 0,68 |
| ADV (adversarias) | 28 | 75,0 % | 0,54 (n válido = 7, poco confiable) |
| COMP (comparaciones) | 20 | 40,0 % | 0,53 |

Por título de la NSR-10: H 48 (39,6 % faltante), F 46 (2,2 %), A 21 (42,9 %), K 10, C 8, B 7, D 7 y el resto con 4 o menos preguntas. Hay títulos con 1 a 3 preguntas, que no permiten concluir nada por título.

### 3.2 Qué no se evalúa

- Dominios sin ninguna pregunta: vías y pavimentos, hidráulica e hidrología, geotecnia y cimentaciones, puentes, movimiento de tierras, maquinaria, programación de obra, mantenimiento.
- Normas del RAG fuera de la NSR-10 (RAS, NTC, Decreto 1072, normas de otros países) tienen 1 a 2 preguntas cada una.
- La respuesta correcta de las preguntas ADV es abstenerse. La métrica context_precision es 100 % faltante en ellas porque no hay contexto relevante que puntuar. Esto es esperable, pero significa que la capacidad de abstención solo se mide con otro criterio.
- Las preguntas compuestas precio + norma (issue #97) fallan en alrededor de 50 % de la parte de precio.
- Latencia, costo por consulta y precisión en producción (issue #84) no están medidos.

### 3.3 Valores faltantes

El análisis retroactivo (`scripts/evaluacion/analisis_estadistico_retroactivo_resultados.json`) muestra que la ausencia de faithfulness no es aleatoria: varía de 0 % en varios títulos a 75 % en las preguntas adversarias. En el diagnóstico de COMP, 10 de 20 respuestas tienen relevancia 0 y 9 contienen lenguaje de abstención («no tengo»). Una media calculada solo con filas válidas sobrestima la calidad en los tipos con más ausencias.

Qué no se hizo: separar, fila por fila, cuántos de los 90 valores faltantes de faithfulness son fallos del evaluador (tiempo de espera, formato inválido) y cuántos son ausencias legítimas (el sistema se abstuvo). Esa separación es el primer trabajo propuesto.

## 4. Validez de la medición

- **Juez sin calibrar.** El mismo tipo de modelo evalúa y genera. No hay un conjunto de pares con anotación experta suficiente para medir concordancia. Existen archivos de anotación (`anotacion_experto*.py/.csv`), pero no se ha reportado una concordancia sobre la batería completa.
- **Datasets propios.** Las preguntas y referencias fueron redactadas dentro del proyecto. Pueden favorecer lo que el sistema ya sabe responder.
- **Métricas sin LLM.** El protocolo `PROTOCOLO_METRICAS_SIN_LLM.md` y `metricas_sin_llm.py` existen como alternativa; falta usarlos de forma sistemática junto con las métricas del juez.
- **Estadística.** Existe el paquete `eval-stats` (intervalos bootstrap, pruebas pareadas con corrección de Holm). Las baterías anteriores a su existencia se re-analizaron de forma retroactiva, pero las comparaciones entre versiones siguen sin un protocolo fijo previo a cada cambio.

## 5. Normas y vigencia

Registro (`normas_registro`, 64 filas): 49 vigentes, 9 derogadas totalmente, 1 derogada parcialmente, **5 con vigencia desconocida**: RES-20213040041135-2021, RES-001049-2013, RES-000803-2009, RES-108-2015 y RES-2743-2026. Cada una debe verificarse en fuente oficial antes de que el RAG las sirva como vigentes.

Incidente conocido: el texto indexado de la Res. 0330/2017 era una transcripción anterior a las Res. 799 y 908 de 2021 (255 artículos frente a 265 del consolidado, y SUDS 25 % frente a 30 %). La re-ingesta está preparada y verificada en simulación, pero **no aplicada** en producción; requiere respaldo, carga en etapa, verificación de recuperación y aprobación.

## 6. Resultados de investigación sin validación externa

- F1 (filo de agua): clasificación con umbrales legales verificados (Ley 1715/2014 modificada por Ley 2294/2023), pero sin inventario público tabular de proyectos para contrastar. Es un cribado, no una estimación de potencial instalable.
- Perfiles longitudinales con DEM de 90 m: la pendiente depende de la resolución; falta repetir con 30 m.
- Caudales mensuales: el protocolo original suponía curva de duración diaria y debió enmendarse.
- Coeficientes IDF de `motor-aquai`: marcados como no verificados.

## 7. Plan propuesto (en orden de valor)

1. Separar los faltantes de faithfulness en fallo del evaluador y abstención legítima; reportar medias con y sin imputación.
2. Construir un benchmark v2 con cobertura por dominio (mínimo 20 preguntas por dominio con motor propio), redactado y revisado por una persona distinta de quien implementa, y con anotación experta de una muestra para calibrar el juez.
3. Escribir pruebas para `motor-topovia` y llevar cada motor a 80 % de cobertura con casos tomados de ejemplos publicados (libros, normas) y no del propio código.
4. Verificar la vigencia de las 5 normas desconocidas.
5. Decidir sobre la re-ingesta de la Res. 0330.
6. Fijar un protocolo de comparación pareada previo a cada cambio de recuperación o de modelo.
7. Medir latencia y costo por consulta en producción (issue #84).

Este plan se coordina con el issue #95 (plan maestro de evaluación) y no lo duplica.
