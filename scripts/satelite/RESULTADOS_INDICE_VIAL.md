# Resultados: índice geomorfométrico de exposición para vías terciarias, solo con DEM (2026-11-08)

Protocolo fijado y publicado antes de calcular ningún índice (commit `24e6f65`): [`PROTOCOLO_INDICE_VIAL_GEOMORFOMETRICO.md`](PROTOCOLO_INDICE_VIAL_GEOMORFOMETRICO.md). Código: `indice_vial_extraer.py` (terreno y OpenStreetMap), `indice_vial_analisis.py` (índices y validación). Salida: `indice_vial_resultados.json`. OpenStreetMap consultado el 2026-11-08 (marcas de tiempo de la base entre 15:30 y 16:01 UTC).

## Datos
| Ámbito | Departamentos | Tramos | Longitud | Tipos (track / unclassified / tertiary) |
|---|---|---:|---:|---|
| Caribe | 7 | 42.181 | 56.808 km | 21.628 / 15.026 / 5.527 |
| Andes (contraste) | Antioquia, Cundinamarca, Santander | 76.362 | 78.088 km | 32.820 / 33.127 / 10.415 |

Validación con municipios que tienen al menos 5 km de vía en la muestra (criterio heredado de C1; no figuraba en el protocolo): **192 municipios en el Caribe** (179 con al menos un evento de la UNGRD) y **326 en los Andes** (313 con evento).

## Resultado confirmatorio: **ninguno de los dos criterios se cumple**
| Criterio | Caribe | Andes |
|---|---|---|
| **V1** ρ parcial del índice de 3 variables (I3) con eventos por 100 km², controlando población y reporte | **−0,16** [−0,43; +0,03] | −0,17 [−0,28; +0,10] |
| **V2** ΔAUC = AUC(I3) − AUC(solo pendiente crítica, I1) | **−0,095** [−0,386; +0,091] | +0,060 [−0,065; +0,158] |
| AUC de I3 | 0,56 [0,34; 0,68] | 0,50 [0,49; 0,82] |
| AUC de la pendiente crítica sola (I1) | 0,65 [0,49; 0,81] | 0,44 [0,37; 0,89] |
| AUC de la pendiente p90 municipal del DEM (referencia) | 0,62 | 0,44 |

**Lectura.** El índice de tres variables **no ordena los municipios por eventos de la UNGRD mejor que el azar de forma detectable, y no supera a la pendiente sola** (V2 no se cumple en ninguno de los dos ámbitos). En el Caribe el ρ parcial es incluso negativo, aunque su IC95 % incluye 0. El resultado es compatible con «no hay relación» y con «relación débil en cualquier sentido»: los intervalos son muy anchos.

## Por qué este resultado es poco informativo (y no debe leerse como «el índice es malo»)
1. **La variable de resultado casi no tiene variación.** El 93 % de los municipios del Caribe (179 de 192) y el 96 % de los andinos (313 de 326) tienen al menos un evento. Con apenas 13 municipios sin evento en el Caribe, el AUC tiene un poder muy bajo, y el IC95 % de V2 llega a casi ±0,4.
2. **Muy pocos bloques.** Siete departamentos en el Caribe y **solo tres en los Andes**: el remuestreo por bloques de departamento con tres bloques no es una cuantificación fiable de la incertidumbre. Los resultados andinos son indicativos como máximo.
3. **La pendiente crítica casi no existe en el Caribe.** El 96 % de los tramos del Caribe tienen una fracción de puntos con pendiente ≥ 15° igual a cero (65 % en los Andes). En el Caribe el índice descansa casi por completo en TWI y distancia a drenaje.
4. **La validación es indirecta y municipal**: eventos de 2019-2024 reportados por municipio, no daños a vías ni ubicaciones.
5. **Sensibilidades** (umbrales de pendiente 10° y 25°, distancia a drenaje 50 y 200 m, pendiente p90 en lugar de la fracción crítica, I2 con dos variables): ninguna cambia la conclusión. La variante I2 del Caribe da ρ parcial −0,25 [−0,47; −0,06], el único caso con IC95 % que excluye 0 y, además, en dirección contraria a la esperada: no estaba entre los criterios confirmatorios y no debe interpretarse sin más.

## Redundancia entre variables (Spearman por tramo)
| Par | Caribe | Andes |
|---|---:|---:|
| Pendiente crítica frente a TWI | −0,12 | −0,29 |
| Pendiente crítica frente a distancia a drenaje | 0,09 | 0,00 |
| TWI frente a distancia a drenaje | 0,40 | 0,38 |

TWI y distancia a drenaje comparten una parte de la información (ρ ≈ 0,4) pero no son redundantes; la pendiente crítica es casi independiente de las otras dos.

## Conclusión
1. **No se logró demostrar que un índice de pendiente crítica + TWI + distancia a drenaje, derivado solo del DEM de 90 m, aporte algo sobre la pendiente sola**, ni siquiera que ordene municipios por eventos reportados mejor que el azar. Tampoco se demostró lo contrario.
2. **No existe validación contra el fenómeno que importa** (inundación o falla efectiva de un tramo). La lista de los 20 tramos y 20 municipios con mayor índice está en `indice_vial_resultados.json`, pero no debe usarse para decidir inversiones: es una ordenación de condiciones del terreno sin validar.
3. **Siguiente paso con más sentido:** validar el índice tramo por tramo contra **inundación observada con radar (Sentinel-1)**, que no depende de reportes municipales ni de un resultado casi constante. Ver la propuesta en la conversación; falta preregistrarla.

## Límites
DEM de 90 m (no ve taludes de corte ni terraplenes). TWI con pendiente mínima de 0,001 (decisión de implementación no fijada en el protocolo). La clase de vía de OpenStreetMap no es la categoría oficial de vía terciaria. Cobertura de OSM voluntaria y desigual entre departamentos. Cada tramo se asigna al municipio de su punto medio. Eventos UNGRD: reportes, con sesgo de reporte, 2022 atípico.
