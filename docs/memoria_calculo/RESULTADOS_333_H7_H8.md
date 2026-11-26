# Resultados #333 (H8 y H7): qué explica que las zapatas no quepan

- **Prerregistro:** [`PRERREGISTRO_333_H7_H8.md`](PRERREGISTRO_333_H7_H8.md), publicado en #333 antes de correr.
- **Corrida:** 25 trabajos, 0 errores, 53 s. q_adm = 200 kPa.
- **Reproducción:** igual que en #324-C, 5/11 edificios tienen alguna zapata que no cabe (414, 1106, 1278, 1701 y 1762). Coincide en W36D y en sin_viento.

## Veredictos

| Id | Resultado | Predicción de Wilmer | Contrapredicción de Claude | Veredicto |
|---|---|---|---|---|
| **H8** | La regla (N ≥ 11 o P_serv,máx > 3.500 kN) la cumplen **3 de los 5** que no caben. 414 (N = 10, P = 2.455 kN) y 1106 (N = 10, P = 3.366 kN) no la cumplen. La recíproca también falla: 554, 898, 1290 y 1413 cumplen la regla y **caben**. El 898 tiene la mayor P (5.532 kN) y cabe | 5/5 | implicación sí, recíproca no | Wilmer: **refutada**. Claude: **refutada a medias** (acerté la recíproca, no la implicación) |
| **H7** | El diseño solo-columna se encontró en **1 de 3** (1290). En 1290 el momento exterior con viga es **−19 %** (160 frente a 198 kN·m), pero ninguno de los dos diseños tiene traslape. En 1729 y 1762 no hubo diseño solo-columna en la rejilla prerregistrada | momento menor y sin traslape en ≥ 2/3 | no se cumple | **inconclusa**: no hay traslape que evitar (n = 1) |

## Lo que salió y nadie predijo (post hoc, exploratorio)

1. **Lo que decide si la zapata cabe es la forma de la cuadrícula, no N ni P.**

   | Relación de luces L_larga / L_corta | Edificios | ¿Alguna zapata no cabe? |
   |---|---|---|
   | ≥ 1,38 | 414 (1,38), 1701 (1,50), 1278 (1,67), 1106 (1,78), 1762 (1,88) | **5/5** sí |
   | ≤ 1,18 | 554, 898, 910, 1290, 1413, 1729 | **0/6** |

   - **Separa 11/11.** El mejor umbral de P separa solo 7/11, y P > 3.500 kN separa menos.
   - **Mecanismo:** la zapata **cuadrada** necesita área ∝ P ∝ área tributaria Lx·Ly, pero el espacio lo limita la luz **corta**. Con bahías alargadas, la zapata cuadrada choca en la dirección corta y le sobra espacio en la larga.
   - Es una regla post hoc sobre 11 edificios. **Se prueba con datos distintos antes de usarla.**
2. **Consecuencia para H5:** antes de pasar a losa o pilotes, la transición más barata en suelo medio probablemente sea una **zapata rectangular** orientada con la luz larga, o una **combinada**. El motor hoy solo diseña zapatas cuadradas. H5 debe incluir esa opción, o sobrestimará el salto de costo.
3. **El optimizador de #324 no siempre halla el óptimo de su propia rejilla.** Se hizo una sensibilidad post hoc con PASOS_EXTRA = 20 en lugar de 4:
   - **1729:** existe un diseño solo-columna (700/550/600) **0,7 % más barato** que el de viga peraltada que eligió #324 (500,7 frente a 504,4 M COP). La viga no era necesaria: la heurística la eligió porque se detiene 4 tamaños por encima de la columna mínima por deriva. El sobrecosto de 1729 en #324 baja de +12,7 % a ~+11,9 %. Ninguna conclusión de #324 cambia, pero R2 y H3 de #324-C usaron ese diseño.
   - **1762:** ni con 20 pasos hay diseño solo-columna con h = 600. Ahí peraltar la viga sí es necesario.
   - **Momentos en la base:** con la viga, el momento exterior es menor en los dos edificios comparables. En 1290 es −19 %; en 1729 es −27 % (171 frente a 236 kN·m), un dato de la sensibilidad. La primera mitad de H7 (la viga alivia el momento en la base) tiene apoyo. La segunda (que eso evite traslapes) no se puede ver aquí, porque ninguno de los dos tiene traslape.

## Consecuencias

- **Issue de seguimiento propuesto:** que el optimizador no se detenga en PASOS_EXTRA cuando todos los pasos fallan por diseño de elementos, o que reporte la búsqueda incompleta. Hoy la palabra "óptimo" de #324 debe leerse como "óptimo de la heurística".
- **#333, H5:** agregar zapata rectangular y combinada como transiciones antes de la losa.
- **H6:** sin cambios.

## Limitaciones

- n = 11 en H8, y n = 1 (o 2 con la sensibilidad) en H7.
- Un solo q_adm (200 kPa) y un solo escenario de viento (W36D).
- Zapata aislada cuadrada; separación mínima de 0,30 m como hipótesis de medición.
- La regla de la relación de luces es post hoc.
- **No diseña cimentaciones reales:** el estudio de suelos y la firma del ingeniero son insustituibles.
