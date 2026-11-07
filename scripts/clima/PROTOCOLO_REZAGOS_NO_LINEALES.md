# Protocolo: relación no lineal con rezago entre el Pacífico, el Atlántico y el clima del Caribe colombiano

Preregistrado el 2026-11-08, antes de ejecutar. Pregunta del proyecto: dados dos predictores (x1, x2) con rezago, ¿existe una relación **no lineal** con la variable de respuesta y1 que un modelo no lineal capture mejor que uno lineal, **fuera de muestra**? Es el tercer orden (dinámica con rezago e interacción) frente al segundo (regresión estática).

## Variables
- **x1:** Índice Oceánico de El Niño (ONI, NOAA CPC), mensual. **x2:** índice TNA de temperatura del Atlántico norte tropical (anomalía 5,5°N-23,5°N, 15°W-57,5°W; NOAA PSL), mensual desde 1948.
- **y1 (lluvia):** anomalía estandarizada de la precipitación media mensual de los 195 municipios del Caribe (códigos DANE 08, 13, 20, 23, 44, 47, 70), CHIRPS v3 (1981-2024, 528 meses). Estandarización por mes calendario con la media y la desviación del tramo de entrenamiento de cada partición (sin información del tramo de prueba).
- **y2 (temperatura):** anomalía media mensual de la temperatura máxima horaria del aire de las estaciones IDEAM del Caribe (2006-2026), cada estación respecto de su propia climatología de entrenamiento; solo meses con ≥ 5 estaciones. Misma regla de estandarización. Su muestra es menor (≈ 190 meses), por lo que la potencia es menor y se declara.

## Diseño
- **Horizontes:** h = 1 y h = 3 meses. Predictores: los rezagos h a h+8 de x1 y de x2 (18 variables), y el seno y coseno del mes calendario del objetivo.
- **Modelos (fijos, sin ajuste de hiperparámetros por el resultado):**
  - **M0:** climatología (anomalía = 0).
  - **M1:** regresión lineal con penalización de cresta (α = 10, variables estandarizadas).
  - **M1s:** M1 con la respuesta modulada por la estación (cada predictor × [1, seno, coseno]).
  - **M2:** aditivo no lineal, splines cúbicos (4 nudos) por variable con rezago + cresta (α = 10).
  - **M3:** gradient boosting (profundidad 3, 150 iteraciones, tasa 0,05, hoja mínima 20) con interacciones libres.
  - **M4:** M1 más la media de ONI en los rezagos, la media de TNA, su producto y sus cuadrados (no linealidad e interacción explícitas).
- **Validación:** validación cruzada por bloques contiguos (6), eliminando 12 meses a cada lado del bloque de prueba del entrenamiento. Habilidad = 1 − MSE(modelo)/MSE(M0) sobre las predicciones fuera de muestra reunidas. IC95 % por bootstrap de bloques móviles de 12 meses sobre las diferencias pareadas de error cuadrático.

## Pruebas
- **Confirmatoria 1 (habilidad):** M1s mejor que M0 (diferencia de MSE < 0), para cada y × h. Holm sobre las 4 combinaciones.
- **Confirmatoria 2 (no linealidad):** M2, M3 y M4 frente a M1s, dentro de cada y × h; Holm sobre las 3. Se concluye que hay relación no lineal útil solo si algún modelo no lineal supera a M1s con p ajustado < 0,05 **y** su habilidad frente a M0 es positiva.
- **Descriptivas:** habilidad por estación del año; respuesta al ONI por rezago (de M1); tendencia de la temperatura (Theil-Sen, IC por bootstrap de bloques) y efecto mínimo detectable con el ruido observado.

## Qué no se concluye
Causalidad. Los índices del Pacífico y el Atlántico están correlacionados entre sí y con la estacionalidad; la no estacionariedad (cambio climático, cambios de estaciones) puede dar o quitar habilidad. Un resultado nulo se publica igual. Resultados previos del proyecto (H4 y H13) sugieren que ENSO se relaciona dentro de la muestra pero no mejora el pronóstico; este protocolo pone a prueba si añadir el Atlántico, los rezagos y la no linealidad cambia eso.
