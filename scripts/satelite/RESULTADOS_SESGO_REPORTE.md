# Resultados: sesgo de reporte de la UNGRD y su efecto sobre V1 (2026-11-08)

Protocolo fijado antes de calcular: [`PROTOCOLO_SESGO_REPORTE.md`](PROTOCOLO_SESGO_REPORTE.md). Código: `sesgo_reporte_ungrd.py`. Salida: `sesgo_reporte_resultados.json`. Panel: 1.000 municipios de 21 departamentos (el de `RESULTADOS_V1.md`) y los 41.893 eventos de la tabla de la UNGRD (2019-2024).

## Veredicto de la prueba principal (S3): **el sesgo de reporte, medido así, no explica el efecto del Caribe**
En el Caribe (n = 159), el efecto de la exposición vial sobre las viviendas dañadas es una razón de tasas de **1,20 por cada +0,10 de exposición** (IC95 % [1,11; 1,30]). Al agregar el indicador principal de capacidad de reporte (P_A: incendios y colapsos estructurales por 100 mil habitantes) pasa a **1,19 [1,12; 1,27]**. La atenuación es de 6 %; el criterio preregistrado para decir que el sesgo explica el efecto era 50 % o más. Con los indicadores de sensibilidad el resultado es el mismo: con P_B (todos los eventos no hidrometeorológicos) el RR sube a 1,22 (atenuación −6 %), y con P_C (fracción de eventos sin efecto cuantificado, n = 154) sube a 1,20 (−7 %). En la muestra conjunta el efecto es ≈ 1,0 con o sin los indicadores, así que no hay nada que atenuar.

## S1: ¿qué predice la capacidad de reporte? (efectos fijos de departamento, errores agrupados, n = 1.000)
- **NBI 2018:** +0,0102 por punto de NBI (IC95 % [+0,005; +0,016], p < 0,001). Los municipios con más necesidades básicas insatisfechas reportan **más** incendios y colapsos estructurales por habitante, no menos. Es lo contrario de lo que se esperaría si P_A midiera solo la capacidad institucional: P_A mezcla capacidad de reporte con riesgo real (la vivienda más precaria se incendia y colapsa más).
- **Población (log):** +0,115 (p = 0,016): los municipios grandes reportan más por habitante.
- **% cabecera:** +0,38 (IC [−0,14; +0,90]); **área:** +0,12 (p = 0,051): sin efecto claro.

## S2: ¿se asocia la capacidad de reporte con la red vial?
| Muestra | Variable vial | ρ parcial | IC95 % por departamentos |
|---|---|---:|---|
| Caribe | exposición vial | −0,02 | [−0,16; +0,14] |
| Caribe | km de vía principal por 100 km² | −0,11 | [−0,24; −0,01] |
| Conjunta | exposición vial | −0,23 | [−0,34; −0,12] |
| Conjunta | km de vía por 100 km² | +0,11 | [+0,02; +0,17] |

En el Caribe, la capacidad de reporte no se asocia con la exposición vial (la vía no actúa como confusor por este camino). En la muestra conjunta, los municipios con vías más expuestas reportan **menos** eventos estructurales, lo que apunta a municipios más rurales y de llanura, no a un mayor reporte.

## S4: reporte por región y año (fracción de municipios con al menos un evento / eventos por 100 mil habitantes)
| Región | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| Andina | 76 % / 11,8 | 85 % / 11,5 | 83 % / 11,8 | 83 % / 39,8 | 86 % / 16,1 | 95 % / 27,8 |
| Caribe | 74 % / 5,0 | 86 % / 5,1 | 71 % / 3,9 | 75 % / 10,7 | 74 % / 7,8 | 93 % / 17,4 |
| Orinoquia | 100 % / 39,6 | 93 % / 21,1 | 93 % / 25,7 | 97 % / 73,1 | 79 % / 16,3 | 97 % / 23,3 |
| Pacífica | 82 % / 7,2 | 61 % / 3,7 | 89 % / 6,6 | 86 % / 28,2 | 86 % / 7,8 | 95 % / 19,2 |

- Los picos de 2022 y 2024 aparecen en **todas** las regiones, lo que sugiere un fenómeno nacional (La Niña en 2022, El Niño con incendios en 2024) o un cambio nacional en la práctica de registro; con esta tabla no se pueden separar.
- En 2024 entre el 93 % y el 97 % de los municipios reportan al menos un evento en todas las regiones, frente a 61 % a 86 % en 2019-2021: coherente con un registro más completo en los años recientes.
- El Caribe reporta menos eventos por habitante que las demás regiones en todos los años (por ejemplo 5,0 frente a 11,8 en la Andina en 2019), lo que es compatible con menor reporte, menor riesgo o ambos.

## Lectura
1. **El efecto del Caribe no se explica por el reporte, según los indicadores usados.** Sigue siendo una asociación regional sin explicación comprobada.
2. **Este resultado es débil como descarte.** La mediana de P_A es 0,00 en el Caribe y en la Pacífica: la mayoría de municipios no reporta ningún incendio ni colapso estructural, por lo que el indicador casi no varía allí y tiene poca capacidad de detectar un sesgo. P_A también responde a riesgo real (S1, NBI). Un efecto que no desciende **no prueba** que el reporte sea insesgado.
3. Lo que queda por probar son explicaciones **físicas o territoriales propias del Caribe**: que la red vial (diques, terraplenes y carreteras sobre llanuras de inundación) esté asociada con condiciones del territorio que el HAND de 90 m y los controles no capturan, por ejemplo la dinámica de ciénagas y planicies, la ganadería extensiva y los asentamientos sobre diques.

## Límites
No hay medida directa de capacidad institucional (personal, presupuesto del consejo municipal de gestión del riesgo). Los indicadores usan el mismo periodo que el resultado. Los eventos se cuentan por municipio de reporte, no por sitio. Dos cargas distintas de la tabla (2019-2022 y 2023-2024) pueden diferir en la práctica de registro.
