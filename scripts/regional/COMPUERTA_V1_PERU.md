# Compuerta de datos de V1-Perú (resultado, 2026-11-08)

Cumple el §4 de `PROTOCOLO_V1_PERU.md`. **Descriptiva: no se calculó ninguna asociación.** Código: `peru_compuerta_datos.py` (commit `b70026b`, publicado antes de ejecutarlo). Insumos: SINPAD 2019-2024, polígonos COD-AB (IGN, límites de 2015), población proyectada INEI al 30-jun-2021, Copernicus GLO-90 (HAND con red de 5 km², corte < 10 m), red vial OSM de Geofabrik descargada el 2026-11-08 (trunk, primary, secondary; 42.442 tramos, 4.820 puentes que no suman a la longitud).

| Concepto | Valor |
|---|---:|
| Distritos procesados | 1.873 |
| Con al menos 5 km de vía principal | 1.484 |
| **Incluidos** (vía ≥ 5 km y datos completos) | **1.483** |
| Población incluida / excluida | 31.203.739 / 1.647.519 (95,0 % / 5,0 %) |
| Incluidos sin ningún registro SINPAD (se tratan como cero) | 13 |
| Departamentos con ≥ 10 distritos incluidos | 23 de 25 |
| E: cuartiles (25 / 50 / 75 %) e IQR | 0,060 / 0,175 / 0,387; IQR 0,327 |
| Distritos con Y1 > 0 | **96,8 %** |
| Distritos con Y2 > 0 | 71,6 % |

E por región natural (mediana y distritos): costa 0,303 (329), sierra 0,110 (936), selva alta 0,213 (114), selva baja 0,371 (91). La selva suma 205 distritos incluidos, por encima del mínimo de 15, así que es evaluable.

## Condiciones de «no concluyente» fijadas en el protocolo
| Condición | ¿Se cumple? |
|---|---|
| Menos de 300 distritos analizables | No (1.483) |
| Menos de 15 departamentos con ≥ 10 distritos | No (23) |
| Más del 90 % o menos del 10 % de distritos con Y1 > 0 | **Sí: 96,8 %** |
| IQR de E menor que 0,05 | No (0,327) |

## Consecuencia
**C-1 (Y1, viviendas dañadas por 100 mil habitantes) queda declarada «no concluyente por falta de variación en Y1» y no se interpreta**, tal como el protocolo lo fijó antes de ver los datos. Que casi todos los distritos tengan algún daño en seis años deja a Y1 sin contraste entre «con daño» y «sin daño»; la prueba de Spearman solo usaría la intensidad.

**Ambigüedad del protocolo, a resolver antes de seguir.** El texto dice que «la prueba confirmatoria» se declara no concluyente si ocurre alguna condición, pero la condición de tasa está escrita sobre Y1. Para C-2 (Y2, tasa 71,6 %) no hay una condición equivalente escrita. Hay dos lecturas: (a) la condición solo bloquea a C-1 y C-2 sigue; (b) bloquea a ambas. No se elige aquí. Cualquier enmienda se registra con fecha y antes de calcular nada.

## Límites de esta compuerta
- E depende de OpenStreetMap, voluntario; la cobertura puede variar por departamento. La exclusión por la regla de 5 km (390 distritos) puede sesgar hacia los más conectados.
- Los 18 distritos de SINPAD sin polígono (437 registros, 0,86 %) quedan fuera, como en la enmienda 1.
- La población es una proyección, no un censo.
- La región natural sale de la modalidad de los registros SINPAD del distrito; 13 distritos sin registro no tienen región.
- No se comparó el HAND de Perú contra ninguna referencia independiente. En una prueba en La Libertad, 83 de 83 distritos tuvieron valores plausibles (medianas entre 3 y 790 m); es una revisión de coherencia, no una validación.
