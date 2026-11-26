# Resultados #324: redimensionar por viento

- **Prerregistro:** [`PRERREGISTRO_324_REDIMENSIONAR_VIENTO.md`](PRERREGISTRO_324_REDIMENSIONAR_VIENTO.md), publicado en #324 antes de correr.
- **Corrida:** 50 optimizaciones (25 edificios × 2 brazos), 0 errores, 23 min.
- **Costo:** directo, vigas + columnas.

## Veredictos: todas las predicciones se cumplen

| Id | Resultado | Predicción | Veredicto |
|---|---|---|---|
| R0 | `sin_viento` reproduce las secciones del corpus: 25/25 | 25/25 | **se cumple** |
| **R1** | Grupo falla: **11/11** encuentran diseño que cumple con W36D | 11/11 | **se cumple** |
| **R2** | Grupo falla: sobrecosto con mediana de **+8,6 %**, rango [+1,5; +18,0 %] | mediana entre +2 y +15 % | **se cumple** |
| R3 | Grupo cambia: el óptimo con viento no es más caro que la sección fija con más refuerzo en 14/14; sobrecosto con mediana de +0,7 % (máx. +3,5 %) | ≥ 12/14; mediana < 3 % | **se cumple** |
| R4 | Grupo falla: sube la columna inferior en 8/11 | ≥ 8/11 | **se cumple**, justo en el límite |

## Secciones propuestas en el grupo falla

Formato: columna inferior / superior / h de viga, en mm.

| id | Sin viento | Con W36D | Sobrecosto |
|---|---|---|---|
| 898 | 750/600/750 | 800/650/**850** | +18,0 % |
| 1729 | 600/450/600 | 600/450/**650** | +12,7 % |
| 1106 | 600/450/700 | **650/500**/700 | +10,3 % |
| 910 | 450/450/500 | **500**/350/**550** | +9,8 % |
| 1413 | 550/400/600 | **600/450**/600 | +9,5 % |
| 1762 | 600/450/600 | 550/400/**650** | +8,6 % |
| 414 | 450/450/550 | **550**/400/550 | +8,1 % |
| 554 | 450/450/600 | **550**/400/550 | +6,3 % |
| 1278 | 650/500/750 | **700/550**/750 | +2,6 % |
| 1290 | 600/450/550 | 600/450/**600** | +2,3 % |
| 1701 | 500/500/600 | **600**/450/600 | +1,5 % |

## Lectura

1. **Basta con secciones de pórtico algo mayores.** Ninguno de los 11 necesitó otro sistema estructural. Muros y sistemas combinados (#119) no son indispensables en esta población. Puede que sean más baratos, pero eso no se midió.
2. **El patrón típico** es una columna inferior 50–100 mm más grande con una columna superior más esbelta (Δ = 150). El viento concentra la demanda en los pisos bajos, igual que el sismo, pero con más flexión biaxial.
3. **En 3 casos la solución fue la viga, no la columna** (1290, 1729, 1762). Una viga más peralta rigidiza el pórtico y le baja momento a la columna. El optimizador encontró esa salida; mi predicción R4 no la anticipaba.
4. **El costo del viento en edificios altos de zona baja con 36 m/s y exposición D:**
   - en los que cambian solo de refuerzo, <1 % en la mediana;
   - en los que necesitaban sección nueva, ~9 % en la mediana y hasta 18 %.

## Limitaciones

- La rejilla es el óptimo de esta heurística, no el diseño de un ingeniero.
- La deriva por viento no se limita, porque la NSR-10 no fija un límite.
- Costo directo de estructura, sin cimentación. Una columna mayor también cambia la cimentación.
- Un solo escenario de viento (W36D). La sensibilidad a β (#323) afecta también estas secciones.
- **Un optimizador nunca aprueba un diseño: propone, y el ingeniero firma.**
