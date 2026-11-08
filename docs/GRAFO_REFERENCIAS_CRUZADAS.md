# Grafo de referencias cruzadas de la NSR-10 (fase 2 hacia KAG)

Fecha: 2026-11-08. Estado: **tabla creada y poblada; todavía no se usa en la recuperación** (no se ha medido si mejora las respuestas).

## Qué es
Tabla `normas_referencias_cruzadas` (migración `20261108160000`). Una fila = un chunk de `nsr10_chunks` que cita un numeral con una palabra clave («sección», «numeral», «capítulo», «título», «apéndice» + numeral tipo `F.4.3.3.2` o `A-3.2`). El destino es el numeral, no un chunk, porque una sección puede estar partida en varios chunks.

## Resultado de la carga (1.356 aristas)
| Resolución | Aristas | Significado |
|---|---:|---|
| exacta | 292 | existe un chunk con ese numeral |
| prefijo | 927 | solo existen subnumerales (típicamente se cita un capítulo entero) |
| sin_destino | 137 (82 numerales) | el numeral citado no está en el corpus: hueco de ingesta o numeral mal leído; **sin revisar uno a uno** |

## Límites conocidos
- Solo captura referencias con palabra clave. No captura numerales «sueltos» ni citas a tablas, figuras o ecuaciones (`Tabla F.4.8.4-1`), que aparecen en unos 940 chunks.
- El 68 % de las aristas son a nivel de capítulo (prefijo): sirven para navegar, son poco precisas para citar.
- Cubre solo `nsr10_chunks`; no NTC, Perú ni Ecuador.
- Las referencias `sin_destino` son una lista de trabajo para auditar la ingesta (p. ej. `F.4.1.2.1`, citado 13 veces, no existe como numeral propio).
- No se validó una muestra manual de aristas contra el texto; falta.

## Siguiente paso (no hecho)
Medir con el conjunto RAGAS existente si expandir los resultados con los chunks vecinos del grafo mejora fidelidad y relevancia frente a la línea base, antes de tocar `rag_multi_norma.py`.
