# Protocolo: comparación con modelos matemáticos no medidos hasta ahora

Preregistrado el 2026-11-08, antes de ejecutar. Objetivo: saber si los métodos que usamos son competitivos frente a alternativas habituales en la literatura que aún no habíamos medido, con el mismo diseño de validación y el mismo conjunto de datos. No se busca un método ganador universal sino comprobar si las diferencias superan el ruido y si un modelo más simple basta (relación con el costo de datos, ver `PROTOCOLO_VALOR_INFORMATIVO.md`).

## Comparación 1 — susceptibilidad a movimientos en masa
**Datos y validación:** las 54.723 muestras y las 7 capas del banco C, con el mismo esquema de 5 grupos de departamentos y 3 réplicas. Referencia: gradient boosting (HGB).
**Candidatos nuevos (fijos):** regresión logística (L1), regresión logística con splines por capa continua (aproximación a un modelo aditivo generalizado), bosque aleatorio (300 árboles, hoja mínima 5), árboles extremadamente aleatorios (300 árboles, hoja mínima 5) y perceptrón multicapa (64-32).
**Criterios:**
- Superioridad: ΔAUC (candidato − HGB) con IC95 % por remuestreo de departamentos; cuenta como superior si el límite inferior > 0, con Holm sobre las 5 comparaciones.
- No inferioridad del modelo simple: la regresión logística (con splines) es no inferior a HGB si el límite inferior de ΔAUC > −0,02.
- Descriptivo: AUC y puntaje de Brier por modelo; correlación de rangos (Spearman) entre las predicciones de cada par de modelos (acuerdo espacial: la literatura reporta que modelos con AUC parecido pueden discrepar mucho en el mapa).

## Comparación 2 — detectores de anomalía de caudal
**Diseño:** exactamente el de `PROTOCOLO_ANOMALIAS.md` (entrenamiento hasta 2009, prueba desde 2010, inyección de un factor ×2 en un mes, AUC por estación, 402 estaciones), con la regla de producción (B0), el z robusto (M1) y el z con persistencia (M2) como referencias.
**Candidatos nuevos (fijos):** M1b, z con escala por rango intercuartílico en lugar de MAD; M3, residuo de un AR(2) del z (generaliza M2); M4, bosque de aislamiento sobre (z, z del mes anterior) entrenado con el tramo de entrenamiento.
**Criterios:** ΔAUC de cada candidato frente a M2 (la mejor hasta ahora) con IC95 % por remuestreo de **departamentos** (31 conglomerados); superior si el límite inferior > 0, con Holm sobre las 3. Se reporta también si M2 es no inferior (margen 0,005) a M4, el método más complejo. Se informan ×1,5 y ×3 como descriptivos.

## Comparación 3 — intervalos de costo (ICOCIV)
**Diseño:** el de P4: orígenes móviles desde el mes 30, horizonte 6 meses, intervalo nominal 80 %, serie de ICOCIV-carreteras.
**Métodos:** bootstrap por bloques de 3 meses y normal iid (ya medidos) y dos nuevos: AR(1) con bootstrap de residuos y simulación histórica (distribución empírica de los cambios acumulados de 6 meses ya observados).
**Criterios:** cobertura empírica en [0,65; 0,95], ancho medio y puntaje de intervalo de Winkler (menor es mejor). Con tamaño efectivo ≈ 6 las diferencias de cobertura no son interpretables; se informan sin prueba de hipótesis y con esa advertencia.

## Qué no se concluye
Que un método sea mejor fuera de estos datos. Los resultados nulos (incluida la ausencia de diferencia entre modelos) se publican. No se ejecutan redes profundas ni modelos que requieran instalar dependencias nuevas (LightGBM, XGBoost, estadísticos de series de tiempo de terceros); quedan declarados como no medidos.
