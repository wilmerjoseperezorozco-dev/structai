# Estado del arte, brecha y qué resuelve cada línea

Documento vivo, verificado el 2026-11-08. Para cada línea de trabajo: qué problema es, qué dice la literatura que encontré, qué hicimos, qué brecha cerramos y qué no. La búsqueda bibliográfica fue de lectura rápida (títulos y resúmenes), no una revisión sistemática: cuando digo «no encontré», significa eso y no que no exista. Las líneas marcadas «sin verificar» todavía no tienen búsqueda.

**Lectura honesta de conjunto.** Casi ningún método de este proyecto es nuevo. Lo que aporta es otra cosa: aplicarlos con datos abiertos de Colombia, con el análisis **preregistrado antes de ejecutar**, con intervalos que respetan que las estaciones vecinas no son independientes, y publicando también los resultados negativos. Esa es la brecha que se puede defender.

---

## 1. ¿Dónde es más probable que se deslice una ladera? (susceptibilidad a movimientos en masa)

**En sencillo:** con relieve, geología, cobertura y lluvia, estimar qué zonas se parecen más a las que ya se deslizaron.

**Literatura.** Los conjuntos de árboles (bosque aleatorio, boosting) suelen rendir muy bien frente a otros algoritmos ([revisión en Remote Sensing, 2022](https://doi.org/https://doi.org/10.3390/rs14133029)). Una validación cruzada al azar da una exactitud sesgada y por eso se recomienda la validación espacial ([Remote Sensing, 2025](https://doaj.org/article/bc4bfcef8be04bc6981e192574e91ef2)). Dos modelos con AUC parecido pueden dar mapas muy distintos ([Frontiers in Earth Science, 2025](https://public-pages-files-2025.frontiersin.org/journals/earth-science/articles/10.3389/feart.2025.1702688/pdf)).

**Lo que hicimos.** Pesos de evidencia, regresión logística y gradient boosting con validación que deja departamentos fuera; análisis preregistrado; resultados por región. AUC de 0,775 (pesos de evidencia) a 0,830 (boosting con cobertura del suelo) en la validación de H6.

**Brecha que cerramos.** Una evaluación espacial y reproducible para Colombia que muestra **dónde falla**: en el Caribe el modelo completo no supera a la pendiente sola. También cuantifica cuánto de los datos hace falta (ver sección 7).

**Lo que no cerramos.** No hay validación con inventarios con fecha (el nuestro no la tiene) y la cobertura del suelo es de 2021, con riesgo de fuga. No hemos medido redes profundas sobre rásteres ni LightGBM/XGBoost (no están instalados).

*Comparación con modelos no medidos antes* ([`RESULTADOS_COMPARATIVO.md`](../scripts/datos/RESULTADOS_COMPARATIVO.md)): ningún modelo (logística, bosques, árboles extremadamente aleatorios, red neuronal) supera al boosting tras corregir por comparaciones múltiples, y una **logística con splines**, simple y explicable, es no inferior. Hacer más complejo el modelo no es lo que mejora el mapa.

---

## 2. ¿Cuánta agua trae una creciente que ocurre una vez cada 50 o 100 años? (frecuencia de crecientes)

**En sencillo:** estimar el caudal extremo que hay que esperar para diseñar obras.

**Literatura.** Los modelos «no estacionarios» ponen índices del clima (ENSO, PDO, NAO, temperatura) dentro de los parámetros de la distribución y suelen preferirse; usar uno estacionario puede subestimar los cuantiles recientes y dar diseños inseguros ([PMC, 2019](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6542809/); [Scientific Reports, 2019](https://link.springer.com/article/10.1038/s41598-019-44603-7)). Los momentos L reducen la incertidumbre con pocos datos en el análisis regional ([NIH Roorkee](https://nihroorkee.gov.in/studies_2014-2025/60-Development%20of%20regional%20relationships_sanjay%20kumar.pdf)).

**Lo que hicimos.** Ajuste estacionario por estación (GEV, LP3), con momentos L como punto de partida; verificación de calibración; modelo con ENSO como covariable y validación hacia adelante; curva de crecimiento regional con intervalos por departamento.

**Brecha que cerramos.** Una comprobación **a escala nacional** de que el ajuste estacionario **no está calibrado** (la excedencia observada del Q10 fue 0,135 y el 44 % de estaciones tiene tendencia), y de que el efecto de ENSO existe dentro de la muestra (29 % de estaciones) pero **no mejora la predicción** ni por estación (41 %) ni agrupado por región (52 %). Es un resultado negativo preregistrado.

**Lo que no cerramos.** No hay curvas para cuencas pequeñas, que son las relevantes para alcantarillas, ni modelos bayesianos jerárquicos, ni picos sobre umbral (los datos son máximos anuales).

---

## 3. ¿Este caudal mensual es raro? (detección de anomalías de caudal)

**En sencillo:** marcar los meses que se salen de lo normal para esa estación y esa época del año.

**Literatura.** El banco de pruebas más cercano compara z-score, rango intercuartílico, residuo de STL, bosque de aislamiento y LOF con reglas hidrológicas ([HydroGEM](https://arxiv.org/pdf/2512.14106)). También hay autoencoders LSTM aplicados a caudales ([Nair y Adarsh](https://doi.org/10.21467/proceedings.156.16)). No encontré una comparación del z estacional robusto frente a estas alternativas.

**Lo que hicimos.** Regla de producción (percentil 90 del mes), z robusto estacional (M1), z con persistencia del mes anterior (M2), y ahora tres alternativas (IQR, AR(2) y bosque de aislamiento), evaluados por inyección de un factor ×2 con intervalos por departamento.

**Brecha que cerramos.** Mostramos que la regla de producción marca el **15,5 %** de los meses normales (no el 10 % previsto), que **añadir la persistencia es lo que mejora** (AUC 0,854 → 0,901) y que el z estacional por sí solo no supera la regla actual. También medimos que las estaciones **no son independientes** (correlación mediana de 0,46 a menos de 50 km), lo que hace falsos muchos intervalos que las tratan como réplicas.

**Lo que no cerramos.** No probamos autoencoders LSTM ni foundation models (requieren dependencias y GPU). Un caveat sobre el bosque de aislamiento: marca valores raros en **ambas** colas, mientras la inyección solo sube el caudal, de modo que su desventaja no es un veredicto general sobre ese método.

---

## 4. ¿Cuánto puede subir el costo de una obra? (costos de obra y su incertidumbre)

**En sencillo:** estimar el riesgo de que los costos suban en los próximos meses, y si el dólar o el petróleo se trasladan al costo.

**Literatura.** Se usan ARIMA, redes neuronales e híbridos para pronosticar índices de costos; los modelos de corrección de error vectorial con precios al productor o petróleo superan a los univariantes ([Shahandashti y Ashuri](https://structurae.net/fr/litterature/article-de-revue/forecasting-construction-cost-indices-methods-trends-and-influential-factors), [AlTalhoni et al., 2024](https://katalog.lib.cas.cz/KNAV/EdsRecord/edsdoj,edsdoj.748fca37b205452b9658281a2d058e8e)). No encontré trabajos sobre cobertura de intervalos por bootstrap ni sobre traslado del tipo de cambio a costos de materiales.

**Lo que hicimos.** Proyecciones locales de TRM y petróleo sobre el ICOCIV (69 meses), Monte Carlo por bloques con validación fuera de muestra y cuatro métodos de intervalo comparados.

**Brecha que cerramos.** Un orden de magnitud con validación: el riesgo de costo de una obra vial es de unos 6-8 % a 6-12 meses según el índice de canasta. Y el límite: **con 69 meses no se puede decir ni que el dólar se traslada ni que no**; la prueba no tiene potencia. Los cuatro métodos de intervalo cubren igual y la normal simple es la más estrecha.

**Lo que no cerramos.** No hay modelos de corrección de error vectorial (requieren series largas y cointegración), ni la exposición de un contrato concreto con cláusula de ajuste.

---

## 5. Precios atípicos y recomendador de insumos para APU

**En sencillo:** avisar cuando un precio se aleja demasiado de lo habitual y sugerir insumos que faltan en un análisis de precios unitarios.

**Literatura:** *sin verificar*. Pendiente buscar detección de atípicos en precios de construcción y sistemas de recomendación para presupuestos.

**Lo que hicimos y su límite.** Tamizaje robusto con umbral conforme, sensibilidad ante un error ×10 de 0,64 (el criterio era 0,90) y acierto@10 del recomendador de 0,84 frente a 0,78 de un control. No es un detector confiable de errores de unidad.

---

## 6. Respuestas con la norma exacta (RAG normativo)

**En sencillo:** responder citando el capítulo y el numeral de la norma, y decir «no sé» cuando no está cargada.

**Literatura.** En el Código Nacional de Construcción de Canadá, un recuperador léxico (BM25 con Elasticsearch) fue el mejor de los probados ([arXiv 2505.04666](https://arxiv.org/abs/2505.04666?context=cs)). En texto legal, BM25 se mantiene competitivo y los modelos densos con reordenador aportan fundamento semántico ([DOG-RAG](https://ceur-ws.org/Vol-4301/Poster9.pdf)); la fusión híbrida y el reordenamiento son la vía habitual ([CanLegalRAGBench](https://arxiv.org/pdf/2605.30497)). No encontré un estudio de reordenamiento específico sobre códigos de construcción.

**Lo que hicimos.** Recuperación híbrida con fusión de rangos y reordenador, extracción verbatim auditada numeral por numeral, evaluación con RAGAS (n = 278) y métricas que no dependen de un LLM.

**Brecha que cerramos.** Un corpus **en español, con trazabilidad por numeral y auditoría de cobertura** de la normativa colombiana, y métricas abiertas que dicen lo que falla (por ejemplo, 15,4 % de proxy de alucinación numérica y 28 % de fallos del juez en una corrida).

**Lo que no cerramos.** No hemos medido, sobre nuestro corpus, BM25 solo frente a denso solo frente a híbrido (la literatura sugiere que BM25 podría ser fuerte); eso corresponde a P1c.

---

## 7. ¿Hace falta guardar y procesar todo? (valor informativo y costo de los datos)

**En sencillo:** averiguar cuánto se puede recortar de los datos sin cambiar las conclusiones.

**Literatura.** Ya existe selección con refuerzo de qué imágenes de alta resolución adquirir ([Ayush, Uzkent et al.](https://liner.com/review/efficient-poverty-mapping-from-high-resolution-remote-sensing-images); [Uzkent et al., WACV 2020](https://openaccess.thecvf.com/content_WACV_2020/papers/Uzkent_Efficient_Object_Detection_in_Large_Images_Using_Deep_Reinforcement_Learning_WACV_2020_paper.pdf)) y selección de subconjuntos representativos en teledetección: con el 10 % de los datos se conserva más del 92 % de la exactitud ([ICML 2025](https://icml.cc/virtual/2025/48809)). En comparaciones generales el muestreo aleatorio sigue siendo una línea base fuerte.

**Lo que hicimos.** Medimos el costo real de lo que almacenamos (P0) y la frontera costo-utilidad con tres estrategias simples en tres bancos (P1).

**Brecha que cerramos (provisional).** Un criterio de **no inferioridad sobre las conclusiones científicas**, no solo sobre la exactitud, con la dependencia respecto del tipo de pregunta: un efecto promedio se conserva con el 5 % de las estaciones, y una cuantía de precisión del 5 % exige el 50 %.

**Lo que no cerramos.** No se ha evaluado el refuerzo (P2 y P3 no se ejecutaron) y la puerta que lo justificaría, tal como estaba escrita, no era informativa (ver la enmienda).
