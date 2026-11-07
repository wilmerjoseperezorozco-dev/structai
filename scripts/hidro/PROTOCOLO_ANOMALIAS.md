# Anomalías de caudal del IDEAM (issue #44): protocolo fijado ANTES de correr — 2026-11-07

**Pregunta:** ¿un detector estacional robusto, y uno que además descuenta la persistencia del mes anterior, separan mejor un caudal mensual anómalo de uno normal que la regla actual de producción?

**Regla actual de producción** (`rag_multi_norma.py::_comparar_caudal_historico`): se marca un caudal mensual cuando supera el percentil 90 histórico de ese mismo mes en la estación. Por construcción marca ≈ 10 % de los meses normales.

## Datos y partición
`ideam_caudal_historico` (caudal medio mensual por estación, 352.022 filas). Estaciones con ≥ 20 años de registro y ≥ 85 % de los meses del tramo presentes. **Entrenamiento:** meses hasta 2009 (climatología y coeficiente de persistencia). **Prueba:** meses desde 2010 (estaciones con ≥ 24 meses de prueba).

## Detectores (puntajes; mayor = más anómalo)
- **B0 (producción):** caudal / percentil 90 del mes (entrenamiento).
- **M1 (robusto estacional):** z = (ln q − mediana_mes) / (1,4826·MAD_mes), con mediana y MAD del logaritmo por mes calendario en el entrenamiento.
- **M2 (residuo con persistencia, versión barata de lo que pide #44 con LSTM):** r_t = z_t − φ·z_{t−1}, con φ = autocorrelación de lag 1 de z en el entrenamiento.

## Evaluación por inyección (no hay anomalías reales etiquetadas)
Para cada mes de prueba se multiplica el caudal por un factor f ∈ {1,5; 2; 3} (mes anterior sin tocar) y se calcula el **AUC** entre los puntajes de los meses inyectados y los de los meses sin tocar de la misma estación (libre de umbral). Se reporta además el punto de operación de B0 tal cual (tasa de meses normales marcados y sensibilidad).
- **Confirmatorios** (diferencia de AUC por estación, IC95 % por bootstrap de estaciones; Holm sobre dos pruebas, α = 0,05): **C1** AUC(M1) − AUC(B0) > 0 en f = 2. **C2** AUC(M2) − AUC(M1) > 0 en f = 2.
- **Descriptivo:** f = 1,5 y f = 3; por estación, cuántas mejoran.

## Limitaciones declaradas
La inyección crea un pico de un solo mes; una creciente real es persistente y espacialmente correlacionada. El AUC no mide cuán útil es el detector para decidir. Los registros mensuales promedian días de crecida y pueden ocultar picos. Estados de aprobación `Preliminar` pueden cambiar. Esto sigue siendo una **señal estadística de investigación, nunca una alerta oficial** (competencia de IDEAM y UNGRD).
