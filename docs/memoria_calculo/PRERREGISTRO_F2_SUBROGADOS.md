# Prerregistro F2 (#275): subrogados entrenados con memorias sintéticas

Fijado el 2026-11-19, mientras corre la F1 (`scripts/memorias_sinteticas/generar.py --m 11`) y **antes** de ver el corpus.
Lo único visto: el piloto de 16 casos (ids 0–15 del mismo Sobol), con 12 soluciones y 4 sin solución. Esos ids quedan dentro del corpus y van **fuera** del conjunto reservado.

## Datos

- **Corpus:** `data/memorias_sinteticas/corpus.csv`, una fila por edificio del Sobol (semilla 275).
- **Entradas (12):** N, vanos_x, vanos_y, Lx, Ly, hp, Aa, Av, perfil, uso (L y grupo), D, f'c. La capacidad se deriva de la zona.
- **Salidas:**
  - **Factibilidad:** `estado` = ok o sin_solucion. Los `error` se reportan y se excluyen.
  - **Diseño óptimo:** c_inferior, c_superior, h_viga.
  - **Cantidades y costo por m²:** acero_kg_m2, concreto_m3_m2, costo_cop_m2, co2_kg_m2.
  - **Respuesta:** T_modelo_x.
- **División:**
  - 15 % reservado al azar (semilla 275, excluidos los ids 0–15);
  - del 85 % restante, 15 % para calibración conforme;
  - el resto para entrenar.

## Modelos

- **Método:** LightGBM, con los mismos hiperparámetros del subrogado de muros (`scripts/surrogate_muro/entrenar.py`), sin búsqueda de hiperparámetros sobre el reservado.
- **Variables:** las regresiones se entrenan en log para costo, acero, concreto y CO₂.
- **Intervalos:** conformes por partición al 90 %.
- **Comparaciones base, fijadas de antemano:**
  - regresión lineal en log con las mismas variables más log(N) y Aa·N;
  - mediana por (zona, N) para los costos.

## Criterios (sobre el reservado, una sola evaluación)

| Salida | Métrica | Criterio de éxito |
|---|---|---|
| Factibilidad | exactitud balanceada; tasa de "factible" falso | exactitud balanceada > 0,90 |
| costo_cop_m2 | MAPE; IC95 bootstrap de MAPE_base − MAPE_LGBM | MAPE ≤ 10 % **y** IC de la mejora sobre la regresión lineal > 0 |
| acero_kg_m2, concreto_m3_m2, co2_kg_m2 | MAPE | descriptivo; se reporta junto con las comparaciones base |
| Intervalos conformes 90 % | cobertura empírica | entre 0,87 y 0,93 en costo_cop_m2 |
| Secciones (c, h) | error absoluto en pasos de rejilla de 50 mm | descriptivo |

## Guardia: el subrogado nunca aprueba un diseño

- **Propuesta:** las secciones predichas se redondean a la rejilla y pasan por el diseño completo F4.
- **Clasificación de cada caso del reservado:**
  - «directo»: cumple con lo propuesto;
  - «reparado»: cumple tras subir la columna hasta 4 pasos;
  - «exacto»: hace falta el optimizador.
- **Se reporta:**
  - la proporción de cada clase;
  - la brecha de costo frente al óptimo de la F1;
  - la cantidad de diseños inseguros entregados, que tiene que ser **0 por construcción**.
- **Criterio:** «directo» + «reparado» ≥ 80 %, con IC95 de Wilson reportado.

## Extrapolación (descriptivo, sin criterio)

- **Amenaza:** entrenar con Aa ≤ 0,30 y evaluar con Aa ≥ 0,35.
- **Altura:** entrenar con N ≤ 10 y evaluar con N ∈ {11, 12}.

## Limitaciones declaradas

- **Optimizador heurístico.** Los "diseños" son óptimos de una rejilla de secciones, no diseños de ingenieros.
- **Malla sin ponderar.** No refleja el inventario real.
- **Costo parcial.** Es costo directo de vigas y columnas, con precios de la línea base 2026-11. No incluye losas, cimentación ni mano de obra indirecta.
- **Cobertura geométrica.** Plantas rectangulares regulares, solo pórticos, sin muros.
- **La región sin solución es de la rejilla, no de la física.** Con vigas de más de 850 mm o con muros podría haber solución.
