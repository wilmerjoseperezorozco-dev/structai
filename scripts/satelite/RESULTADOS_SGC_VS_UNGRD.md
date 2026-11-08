# Resultados: ¿el mapa de amenaza por movimientos en masa del SGC ordena los municipios como los eventos de la UNGRD? (2026-11-08)

Protocolo fijado y publicado antes de calcular (commit `6556d1f`): `PROTOCOLO_ANALISIS.md`, §26. Código: `contraste_sgc_vs_ungrd.py`. Salida: `contraste_sgc_vs_ungrd.json`.

## Muestra
995 municipios del panel con índice del SGC (% del área en amenaza alta + muy alta) y pendiente del DEM; 663 (67 %) reportan al menos un evento de «MOVIMIENTO EN MASA» en 2019-2024. Cubre 21 departamentos, no todo el país. Todos los intervalos son IC95 % por bootstrap de bloques por departamento.

## Criterios preregistrados
| Criterio | Resultado | ¿Se cumple? |
|---|---|---|
| **K1** AUC del índice SGC para «hubo al menos un evento» (IC excluye 0,5) | **0,76** [0,68; 0,85] | Sí |
| **K2** ρ de Spearman con eventos por 100 km² (IC excluye 0) | **+0,44** [+0,29; +0,61] | Sí |
| **K3** ρ parcial controlando población y capacidad de reporte | **+0,39** [+0,28; +0,53] | Sí |
| **K4** ρ parcial controlando además la pendiente p90 | **+0,18** [+0,08; +0,29] | Sí |
| Umbral «predice bien»: AUC ≥ 0,65 y K2 y K3 cumplidos | AUC 0,76 | Cumplido |

El umbral de 0,65 lo fijé yo de antemano y es arbitrario.

## Por cuartil del índice del SGC
| Cuartil (índice medio) | % municipios con evento | Eventos por 100 km² (mediana) |
|---|---:|---:|
| 1.º (2 %) | 31 % | 0,0 |
| 2.º (29 %) | 69 % | 1,0 |
| 3.º (60 %) | 79 % | 1,6 |
| 4.º (89 %) | 87 % | 2,4 |

La relación es monótona: a mayor amenaza en el mapa, más municipios con eventos y más eventos por área.

## Lo que matiza el resultado
1. **La pendiente sola ordena igual de bien.** El AUC de la pendiente p90 del DEM sola es 0,78, frente a 0,76 del índice del SGC, y su ρ es +0,47 frente a +0,44. No probé si la diferencia es distinguible; no hay evidencia de que el mapa supere a la pendiente en este análisis. K4 sí indica que el mapa conserva una asociación con los eventos después de descontar la pendiente (+0,18), pero es mucho menor que la bruta (+0,44).
2. **Por región es desigual.** AUC en la Pacífica 0,73, en la Andina **0,65**, en el Caribe **0,59** (solo 46 de 192 municipios con evento). Orinoquía (29 municipios) no se reporta. Estos AUC por región son estimaciones puntuales sin intervalo.
3. **Una tasa base alta limita la lectura del AUC.** Con el 67 % de los municipios con evento, una variable con poca información ya obtiene un AUC > 0,5.
4. **Es consistente con la advertencia anterior** (`RESULTADOS_SUSCEPTIBILIDAD_MUNICIPAL.md`): en la Andina y la Pacífica el modelo propio concordaba mal con el mapa del SGC. Aquí el mapa del SGC concuerda moderadamente con los eventos en esas mismas regiones; no se contradicen, porque son comparaciones distintas.

## Robustez
Quitando 2022 (año con 3-4 veces los eventos normales): AUC 0,75, K2 +0,44, K3 +0,39, K4 +0,20. Quitando los municipios con más de 500 mil habitantes (11): AUC 0,76, K2 +0,44, K3 +0,39, K4 +0,18. Las conclusiones no cambian.

## Límites
- La UNGRD mide **reportes**, no eventos. K3 descuenta un indicador de capacidad de reporte (incendios y colapsos estructurales por habitante) y la población, pero ese indicador es imperfecto, como mostró el análisis de sesgo de reporte.
- Es un análisis **municipal**: un municipio con una pequeña fracción del área en amenaza alta puede tener todos sus eventos allí. No valida el mapa punto a punto.
- El mapa del SGC probablemente usa la pendiente como insumo, así que su asociación con eventos en parte repite la de la pendiente.
- 6 años de eventos, uno atípico; 21 departamentos; sin corrección por autocorrelación espacial salvo el bootstrap por departamento.

## Conclusión
El mapa del SGC **sí ordena** los municipios en el sentido esperado, y lo hace más que el azar incluso después de descontar el sesgo de reporte. **No hay evidencia de que ordene mejor que la pendiente sola**, y en el Caribe y la Andina la capacidad es modesta. Para StructAI significa que mostrar el índice del SGC como referencia es defendible, pero no como sustituto de un estudio local.
