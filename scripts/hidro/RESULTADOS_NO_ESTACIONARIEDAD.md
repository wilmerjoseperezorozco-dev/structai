# Resultados: no estacionariedad espacial y transferibilidad del modelo de caudales máximos (2026-11-08)

Protocolo fijado y publicado antes de ajustar ningún modelo regional (commit `9b83b70`): [`PROTOCOLO_NO_ESTACIONARIEDAD.md`](PROTOCOLO_NO_ESTACIONARIEDAD.md). Código: `no_estacionariedad.py`. Salida: `no_estacionariedad_resultados.json`. Mismas 257 estaciones y misma validación ciega (zona de exclusión de 50 km) de la Etapa A. Un primer intento falló por un error mío (el resumen esperaba una columna que no creé); se corrigió y se repitió sin cambiar ningún criterio.

## C1 (confirmatorio): **no se cumple**
A T = 10, el modelo por región natural (M5a) **no** tiene un error menor que el modelo nacional (M2): diferencia de la mediana de |ε| = 0,000, IC95 % [−0,067; 0,000] por bloques espaciales. El IC no excluye 0 (su límite superior es exactamente 0), así que por regla el resultado es **«no se confirma»**. Factor de error típico: M2 **1,75**, M5a **1,79**. Lo mismo a T = 2, 5, 25 y 50 y en todas las sensibilidades (sin zona de exclusión, con 100 km, objetivo Log-Pearson III, cuencas ≤ 2.000 km²).

Por región (T = 10, factor típico M2 → M5a): **Caribe 1,89 → 2,40 (peor)**, Andina 1,80 → 1,75 (apenas mejor), Pacífica 1,51 → 1,51 (idéntico: en 18 de 35 estaciones quedan menos de 30 estaciones de entrenamiento en la región tras la zona de exclusión y la regla del protocolo manda usar el modelo nacional). Orinoquía (11) siempre usa el nacional.

## Secundarios (exploratorios)
| Comparación a T = 10 | Factor típico | Diferencia frente a M2 [IC95 %] |
|---|---:|---|
| M2 nacional | 1,75 | |
| M5a regiones naturales | 1,79 | 0,000 [−0,067; 0,000] |
| M5b dominios por agrupamiento, k = 3 | 1,79 | 0,000 [−0,060; 0,000] |
| M5b dominios por agrupamiento, k = 4 | 1,71 | −0,003 [−0,064; 0,000] |
| R bosque aleatorio nacional | 1,78 | −0,034 [−0,125; +0,014] |

Ninguna alternativa mejora de forma detectable al modelo nacional. M5b con k = 4 tiene el mejor factor puntual (1,71) pero su IC incluye 0 y no estaba designado como criterio.

## Los coeficientes sí difieren, pero eso no mejora la predicción
Ajuste por región a T = 10 (IC95 % por bloques):
| Región (n) | Exponente del área | Exponente de la lluvia | Exponente de la pendiente |
|---|---|---|---|
| Nacional (257) | 0,50 [0,40; 0,62] | 1,27 [0,66; 1,67] | −0,73 [−0,87; −0,40] |
| Andina (152) | 0,60 [0,43; 0,77] | 1,23 [0,38; 1,66] | −0,15 [−0,83; 0,48] |
| Caribe (59) | 0,38 [0,17; 0,59] | 1,46 [−0,01; 2,02] | **−0,74 [−0,89; −0,51]** |
| Pacífica (35) | 0,69 [0,31; 0,83] | 0,84 [0,15; 1,20] | **+0,93 [0,33; 2,10]** |

El caso claro es la pendiente: **negativa en el Caribe y positiva en la Pacífica, con intervalos que no se solapan**. La prueba F de interacción da F = 5,7 (p ≈ 1×10⁻⁶), pero **no es válida como prueba formal** (estaciones autocorrelacionadas en el espacio, como declaré). Es compatible con no estacionariedad en los coeficientes. Aun así, con 35 a 152 estaciones por región el costo en varianza de estimar tres coeficientes por región cancela la ganancia: la heterogeneidad existe pero no se traduce en mejor predicción a ciegas. Eso es distinto de «el modelo nacional es adecuado en todas partes».

## C2: el modelo nacional no «falla» en ninguna región según la regla fijada
| Región | Factor de sesgo [IC95 %] | Factor típico |
|---|---|---:|
| Andina (152) | 0,93 [0,78; 1,27] | 1,80 |
| Caribe (59) | 0,74 [0,47; 1,12] | 1,89 |
| Pacífica (35) | 1,16 [0,63; 1,53] | 1,51 |
| Orinoquía (11) | 1,43 [1,04; 4,54] | 1,80 |

La regla exigía IC95 % que excluya 1 **y** sesgo fuera de [0,67; 1,5]. Orinoquía excluye 1 pero su sesgo puntual (1,43) queda dentro del rango, y con 11 estaciones no se concluye. El Caribe tiende a subestimar (0,74) pero el IC incluye 1.

## T1: transferibilidad entre regiones (dejar una región entera fuera)
| Región excluida del entrenamiento | n | Factor típico | Sesgo |
|---|---:|---:|---:|
| **Caribe** | 59 | **3,00** (frente a 1,89 en la validación normal) | **0,33** |
| Andina | 152 | 1,80 | 0,91 |
| Pacífica | 35 | 1,58 | 1,16 |
| Orinoquía (no se concluye) | 11 | 1,68 | 1,68 |

**Este es el hallazgo con más contenido.** Un modelo entrenado sin el Caribe **subestima ese territorio por un factor de 3** (mediana de Q̂/Q = 0,33) y su error típico sube de 1,89 a 3,00. La Andina y la Pacífica, en cambio, se transfieren sin penalización apreciable. Es coherente con la señal de coeficientes distintos, y es lo más cercano a «un modelo calibrado en otra parte falla»: **falla al trasladarlo al Caribe**, no en general. No investigué la causa (podría ser el relieve bajo, la regulación de cauces en llanuras o la lluvia).

## Conclusión
1. **«Un modelo único nacional falla» no se demuestra.** Con estos datos, el modelo nacional con datos de todo el país rinde igual que los regionales y no tiene sesgo regional significativo.
2. **Sí hay evidencia de no estacionariedad de los coeficientes** (la pendiente cambia de signo entre el Caribe y la Pacífica) y **de falta de transferibilidad hacia el Caribe**: usar un modelo calibrado en otras regiones allí subestima los caudales de crecientes por un factor de 3.
3. Para StructAI: la ecuación nacional se puede usar con el margen de error ya declarado, **pero no debe exportarse a otro país o región sin calibrar con estaciones locales**, y la validación local en el Caribe es el punto crítico.

## Límites
Solo variación **espacial**; la estacionariedad temporal se supone. Orinoquía no se puede modelar. Las regiones se asignan por departamento. Con 35 a 152 estaciones la potencia es limitada: un resultado nulo no prueba que no haya regionalización útil con más datos o mejores predictores. El caudal observado es el máximo horario. El agrupamiento k-means y el bosque aleatorio usaron hiperparámetros fijos, sin optimizar. No sustituye el estudio hidrológico de un proyecto.
