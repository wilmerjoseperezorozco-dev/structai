# Resultados: ¿se reproduce el mapa municipal de intensidad máxima observada del SGC desde sus puntos? (2026-11-08)

Protocolo fijado antes de descargar los puntos (commit `2662ef2`): [`PROTOCOLO_SISMICIDAD_HISTORICA.md`](PROTOCOLO_SISMICIDAD_HISTORICA.md). Código: `auditoria_sismicidad_historica.py`. Salida: `auditoria_sismicidad_historica.json`.

## Datos
Puntos de intensidad histórica del SGC: 1.430 en la capa de intensidad máxima y 3.405 en la de todas las observaciones (una sola escala, código 1, no documentado). Mapa municipal: 1.095 municipios con categoría `M`. Asignación de puntos a municipios con los polígonos del IGAC.

## Resultado
| Medida | Resultado | Criterio fijado |
|---|---:|---|
| Municipios del mapa con al menos un punto | 877 de 1.095 | |
| Coincidencia exacta (valor redondeado) | 39 % | |
| Diferencia ≤ 1 | **79 %** | ≥ 90 % |
| ρ de Spearman | **0,65** | ≥ 0,9 |
| Municipios del mapa sin ningún punto | **218** | |

**El criterio no se cumple:** el mapa municipal no se reproduce como el máximo de los puntos. El mapa da un valor más alto que los puntos en 345 municipios y más bajo en 194 (sesgo medio de los puntos menos el mapa: −0,43). Usar la unión de las dos capas de puntos da exactamente el mismo resultado, así que la capa de máximos ya contiene los valores de la otra.

## Qué implica y qué no
- **Implica** que el mapa municipal del SGC no es una agregación directa de estos puntos: 218 municipios del mapa tienen valor sin ningún punto de observación, lo que sugiere interpolación o extrapolación. Es una inferencia, no la verifiqué con el SGC.
- **No implica** que el mapa esté mal. Un mapa interpolado puede ser razonable aunque no coincida con el máximo puntual.
- **Consecuencia para el resultado anterior** (`RESULTADOS_INTENSIDAD_VS_A4.md`): la concordancia entre Aa e intensidad observada refleja en parte un producto interpolado. Los resultados de ese análisis siguen valiendo, con esa salvedad.

## Límites
La escala de intensidad no está documentada; un punto mal ubicado cae en el municipio equivocado; no distingo si las discrepancias vienen de interpolación, de otra versión de los datos o de otro criterio de agregación.
