# Resultados F2 (#275): subrogados entrenados con memorias sintéticas

Evaluación única sobre el reservado, ejecutada el 2026-11-19 a las 21:31 según el [prerregistro](PRERREGISTRO_F2_SUBROGADOS.md) (commit `20c2eac`, fijado antes de ver el corpus).

- **Script:** `scripts/memorias_sinteticas/entrenar_f2.py`.
- **Salida completa:** `data/memorias_sinteticas/f2/resultados_f2.json` y `guardia_detalle.csv`.

## Corpus F1

- **Tamaño:** 2.048 edificios (Sobol, semilla 275), sin errores.
  - 1.348 con solución (65,8 %);
  - 700 sin solución en la rejilla.
- **Tiempo:** 11.821 s con 8 procesos. El optimizador tarda una mediana de 41 s por edificio con solución.

| Zona | ok | sin solución |
|---|---|---|
| alta | 589 | 508 |
| intermedia | 401 | 111 |
| baja | 358 | 81 |

| Perfil | ok | sin solución |
|---|---|---|
| C | 558 | 125 |
| D | 473 | 209 |
| E | 317 | 366 |

**División:**
- reservado: 307;
- calibración conforme: 261;
- entrenamiento: 1.480.

## Criterios prerregistrados

| Salida | Criterio | Resultado | Veredicto |
|---|---|---|---|
| Factibilidad | exactitud balanceada > 0,90 | **0,920** (exactitud 0,928; 12 «factible» falsos, 10 «inviable» falsos) | CUMPLE |
| costo_cop_m2 | MAPE ≤ 10 % **y** IC95 de la mejora sobre la regresión lineal > 0 | MAPE **4,6 %** (lineal 7,8 %); IC95 de la mejora [2,4; 4,0] puntos | CUMPLE |
| Conforme 90 % en costo | cobertura entre 0,87 y 0,93 | **0,904** | CUMPLE |
| Guardia | directo + reparado ≥ 80 % | **90,4 %** (179/198), IC95 de Wilson [85,5; 93,8] % | CUMPLE |
| Diseños inseguros entregados | 0 por construcción | **0** | CUMPLE |

## Descriptivo

| Salida | MAPE LGBM | MAPE lineal | R² | Cobertura 90 % |
|---|---|---|---|---|
| acero_kg_m2 | 5,8 % | 10,0 % | 0,91 | 0,909 |
| concreto_m3_m2 | 5,6 % | 8,2 % | 0,93 | 0,874 |
| co2_kg_m2 | 5,3 % | 8,1 % | 0,94 | 0,894 |
| T_modelo_x | 4,2 % | — | 0,97 | 0,909 |
| costo (mediana por zona y N) | — | 14,7 % | — | — |

**Secciones**, error medio en pasos de rejilla de 50 mm:

| Sección | Error medio | R² | Cobertura |
|---|---|---|---|
| Columna inferior | 0,97 pasos | 0,75 | 0,91 |
| Columna superior | 0,83 pasos | 0,71 | 0,88 |
| Viga | 0,67 pasos | 0,87 | **0,84** (por debajo del nominal) |

**Guardia** (198 casos factibles del reservado):

| Origen | Casos |
|---|---|
| Directo | 112 |
| Reparado (subir la columna hasta 4 pasos) | 67 |
| Exacto (hizo falta el optimizador) | 19 |

- **Brecha de costo frente al óptimo de la F1:** mediana 2,2 %, p90 8,1 %.
- **Tiempo:** la guardia tomó 204 s en total (≈ 1 s por caso). El optimizador tarda una mediana de 41 s por caso.
- **Factibles falsos:** 12 casos sin solución fueron predichos como factibles. La F4 los rechaza y no se entrega diseño.

**Extrapolación** (MAPE del costo):

| Partición | n | MAPE |
|---|---|---|
| Entrenar con Aa ≤ 0,30 → evaluar con Aa ≥ 0,35 | 202 | 6,4 % |
| Entrenar con N ≤ 10 → evaluar con N ∈ {11, 12} | 173 | 5,5 % |

## Lectura

1. **El subrogado sirve como propuesta inicial, no como diseño.**
   - En el 90 % de los casos la guardia llega a un diseño que cumple sin correr el optimizador, unas 40 veces más rápido.
   - Ese diseño cuesta en mediana un 2,2 % más que el óptimo de la rejilla.
   - La seguridad la pone la F4, no el modelo.
2. **Costo y CO₂ por m² se predicen con ±5 %** y con intervalos conformes bien calibrados. Sirven para prefactibilidad: comparar alternativas antes de diseñar.
3. **La viga es la salida menos calibrada** (cobertura 0,84). Es esperable: la altura de viga es discreta y el optimizador tiene empates de costo entre alturas vecinas.
4. **Hallazgo del corpus, no del subrogado:** 81 de 439 edificios en zona baja quedan sin solución. Hay que revisar si viene del límite de ρmin con columnas grandes (máximo 20 #8 en el catálogo) antes de interpretarlo como algo físico.

## Limitaciones (las del prerregistro, sin cambios)

- **Optimizador heurístico:** los diseños son óptimos de una rejilla, no diseños de ingenieros.
- **Malla sin ponderar** por el inventario real.
- **Costo parcial:** solo vigas y columnas.
- **Cobertura:** solo pórticos regulares, sin muros.
- **Sin solución:** la región sin solución es de la rejilla.
- **Datos sintéticos:** los resultados valen dentro de este espacio. No son una validación contra edificios reales; eso corresponde a la F4b.
