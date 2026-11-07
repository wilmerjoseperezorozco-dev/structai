# Resultados: índice de susceptibilidad municipal y su validación contra el mapa del SGC

Ejecutado el 2026-11-08 con `construir_susceptibilidad_municipal.py` (modelo de gradient boosting con las 7 capas, validación cruzada que deja grupos de departamentos fuera, 2 réplicas; 54.723 muestras). Produce `packages/construdata/data/susceptibilidad_municipal.json`, que lee el plugin de susceptibilidad del chat.

## Qué es el índice
Para cada municipio con al menos 20 puntos de fondo (381 de 1.122), el promedio de la probabilidad predicha fuera de muestra sobre sus puntos de fondo, expresado como **percentil entre municipios**. Los puntos de fondo son aleatorios sobre tierra (razón 5:1 con las presencias SIMMA), así que el índice **ordena municipios entre sí y no es una probabilidad**.

## Validación contra el mapa oficial del SGC (% del área en amenaza alta o muy alta)

| Región | AUC fuera de muestra (presencias frente a fondo) | ρ de Spearman con el mapa del SGC | Municipios | Decisión del plugin |
|---|---:|---:|---:|---|
| Global | 0,903 | **+0,54** | 381 | — |
| Orinoquía | 0,955 | +0,81 | 47 | Muestra el índice |
| Caribe | 0,767 | +0,63 | 90 | Muestra el índice como «moderado» |
| Amazonía | 0,889 | +0,59 | 50 | Muestra el índice |
| Andina | 0,714 | **+0,10** | 124 | **Omite el índice** |
| Pacífica | 0,865 | **−0,26** | 70 | **Omite el índice** |

**Lectura.** El modelo concuerda con el mapa oficial en general, pero **no en la región Andina y de forma contraria en la Pacífica**. Un caso concreto: para Quibdó el SGC clasifica el 99 % del área en amenaza alta o muy alta y el índice lo ubicaría en el percentil 29. Por eso, en las regiones con ρ < 0,30 el plugin **no muestra el índice** y entrega solo el mapa oficial. Un AUC alto con presencias frente a fondo no basta: mide si el modelo separa lugares con y sin movimientos registrados, no si ordena bien a los municipios.

Corrección de una afirmación anterior: la idea de que «el Caribe es la región débil» venía de otro diseño (modelo completo frente a pendiente sola). En esta validación contra el mapa del SGC, el Caribe concuerda (ρ = 0,63) y las regiones débiles son la Andina y la Pacífica.

## Límites
- Los municipios sin 20 puntos de fondo (741 de 1.122, entre ellos las capitales muy urbanas y pequeñas) no tienen índice; en ellos se muestra solo el mapa del SGC.
- El inventario SIMMA no tiene fecha y la cobertura del suelo es de 2021 (riesgo de fuga).
- Las categorías del SGC en el archivo son `CD`, `D`, `M` y `SIN`; no se verificó su significado, por lo que el plugin no las muestra.
- Escala de municipio; no sustituye el estudio geotécnico del lote.
