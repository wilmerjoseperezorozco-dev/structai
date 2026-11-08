# Resultados Etapa B: sesgo de CHIRPS frente a pluviómetros automáticos del IDEAM y corrección por cuantiles (2026-11-08)

Protocolo, fijado y publicado antes de descargar ningún registro: [`PROTOCOLO_SESGO_CHIRPS.md`](PROTOCOLO_SESGO_CHIRPS.md) (con la Enmienda 1, también anterior a cualquier cálculo de sesgo). Código: `sesgo_chirps_analisis.py`. Salidas: `sesgo_chirps_resultados.json`, `pluviometros_seleccion.json`. Datos: IDEAM, conjunto `s54a-sgyg` (pluviómetros automáticos, acumulados de 10 minutos) y catálogo `hp9r-jxuu`; CHIRPS v3.0 diario.

**Esta es una muestra piloto**, no una calibración nacional (ver Límites).

## Muestra
- 42 estaciones aceptadas (Caribe 12, Andina 12, Pacífica 12, Orinoquía 6) con al menos 300 días válidos en 2022-2024 (criterio rebajado de 700 en la Enmienda 1 porque casi todos los sensores automáticos son recientes).
- **35** estaciones tienen al menos 300 días con dato en ambas fuentes y entran al cálculo del sesgo (Andina 11, Caribe 10, Pacífica 12, **Orinoquía 2**).
- **27** entran a la validación de la corrección (dejando una estación fuera exige al menos 3 vecinas de la misma región): Orinoquía **no se puede validar** (2 estaciones).
- Alineación horaria: la correlación de Spearman diaria mediana es 0,502 con las marcas tal como están y 0,520 con +5 h; se usó +5 h por el criterio del protocolo. La diferencia es pequeña.

## Sesgo antes de corregir (pixel que contiene la estación)
| Región (n) | Spearman | Razón total CHIRPS/pluviómetro [IC95 %] | Razón p50 | Razón p90 | Razón p99 [IC95 %] | Días ≥ 1 mm: pluviómetro / CHIRPS |
|---|---:|---:|---:|---:|---:|---:|
| Andina (11) | 0,53 | 1,44 [1,16; 1,92] | 0,94 | 0,75 | 0,90 [0,67; 1,14] | 0,42 / 0,66 |
| Caribe (10) | 0,45 | 1,35 [0,73; 5,60] | 1,64 | 1,03 | 0,77 [0,58; 4,50] | 0,25 / 0,40 |
| Orinoquía (2) | 0,63 | 1,26 (n = 2) | 0,94 | 1,09 | 1,07 (n = 2) | 0,54 / 0,64 |
| Pacífica (12) | 0,48 | 1,11 [1,09; 1,39] | 0,82 | 0,76 | 0,93 [0,78; 1,04] | 0,37 / 0,53 |
| **Todas (35)** | **0,50** | **1,33 [1,16; 1,45]** | 0,94 | 0,80 | **0,90 [0,78; 1,05]** | **0,38 / 0,55** |

Con la media de 3 × 3 pixeles el cuadro es parecido (todas: razón total 1,28 [1,15; 1,43]; p99 0,85 [0,77; 0,94]).

**Lectura del patrón.** En total, CHIRPS acumula **más** lluvia que el pluviómetro (+33 %, IC95 % que excluye 1), pero **en los días lluviosos sus cuantiles altos son iguales o algo menores** (p90: 0,80; p99: 0,90 con IC95 % que incluye 1). Ambas cosas son compatibles porque CHIRPS registra lluvia ≥ 1 mm en **muchos más días** (55 % frente a 38 %): un exceso de días con lluvia ligera suma volumen sin subir los extremos. Es un patrón coherente con ese mecanismo, pero **no lo verifiqué** (por ejemplo, no separé los días en que el pluviómetro marca cero). El Caribe tiene una dispersión enorme entre estaciones (razón total de 0,73 a 5,60).

## Corrección por cuantiles (validación dejando una estación fuera, factores de la misma región)
27 estaciones. Diferencia de la mediana de |ln(razón)| (después − antes), IC95 % por bootstrap de estaciones:

| Cuantil | Antes | Después | Diferencia [IC95 %] |
|---|---:|---:|---:|
| p50 | 0,23 | 0,20 | −0,061 [−0,068; +0,066] |
| p75 | 0,32 | 0,22 | −0,143 [−0,176; +0,043] |
| p90 | 0,32 | 0,21 | −0,005 [−0,224; +0,028] |
| p95 | 0,33 | 0,16 | −0,028 [−0,172; +0,064] |
| **p99 (primario)** | 0,29 | 0,26 | **−0,015 [−0,114; +0,142]** |
| Total acumulado | 0,33 | **0,52** | **+0,166 [+0,127; +0,181]** |

**Criterio primario: NO se cumple.** La corrección no mejora de forma detectable el percentil 99 de los días lluviosos en estaciones no usadas para estimarla (el IC95 % incluye 0). Tampoco mejora ningún otro cuantil con claridad. Y **empeora el total acumulado** (el error pasa de 0,33 a 0,52, IC95 % que excluye 0): los factores de las regiones Andina y Pacífica son mayores que 1 en los cuantiles altos, y como CHIRPS ya acumula de más por exceso de días lluviosos, subir los días lluviosos agrava el total. Es el límite que el protocolo declaró de antemano (la corrección por cuantiles no repara la frecuencia de días lluviosos), y aquí se vuelve el problema dominante.

## Efecto sobre la regionalización (Etapa A, T = 10) — escenario condicional
Escalando la lluvia media anual de cada cuenca por la razón regional inversa:
| Modelo | Sin corrección | Con corrección |
|---|---:|---:|
| M2 (referencia) | 1,746 | 1,766 |
| M1 | 1,886 | 1,924 |
| M3 | 1,872 | 1,872 |
| B1 | 1,883 | 1,883 |

**La corrección no mejora la regionalización** (M2 pasa de 1,75 a 1,77). Consistente con H1 y con el análisis de incertidumbre previo: el factor de error de ~1,75 no viene del sesgo de la lluvia media.

## Una discrepancia que no puedo explicar
Contra las normales climatológicas 1991-2020 (H1), CHIRPS está **+5 %** en la lluvia media anual en 1.445 estaciones; contra estos pluviómetros automáticos 2022-2024 está **+33 %** en el total. Las muestras, los periodos y los instrumentos son distintos (estaciones automáticas recientes, altitudes y entornos distintos, posible subregistro del sensor, 2022-2024 húmedo-seco), y **este análisis no permite separar esas causas**. No se debe leer ninguna de las dos cifras como «el sesgo de CHIRPS en Colombia».

## Conclusiones
1. CHIRPS reproduce con correlación moderada (Spearman ≈ 0,5, esperable al comparar un pixel de 5 km con un punto) la lluvia diaria de estos pluviómetros, acumula más total y registra más días lluviosos, sin subestimar de forma detectable el percentil 99.
2. **No hay evidencia de que la corrección por cuantiles mejore las lluvias fuertes**, y empeora el total. No se recomienda aplicarla.
3. La Etapa A **no cambia**: no se corrige el predictor.
4. Si se quisiera corregir CHIRPS en serio, el siguiente paso sería tratar primero la **frecuencia de días lluviosos** (por ejemplo un umbral por región), no los cuantiles.

## Límites
Muestra piloto: 35 estaciones evaluadas, 3 años, Orinoquía con 2; estaciones concentradas en zonas pobladas y en ciertas alturas; punto frente a pixel de 5 km (diferencia de escala, no solo de sesgo); alineación horaria elegida por correlación con diferencia pequeña (0,502 frente a 0,520); posible falla de sensor no detectada por el control; el efecto sobre la Etapa A supone que el sesgo de 2022-2024 es el de 1991-2020. Los IC95 % reflejan solo la variación entre estaciones. **No sustituye una calibración con series largas ni el criterio del hidrólogo.**
