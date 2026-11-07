# Relaciones no lineales con rezago: opciones, física y estado de medición

Documento de investigación, 2026-11-08. Pregunta: dados dos variables de entrada x1 y x2, ¿cómo capturar una relación **no lineal** y **con rezago** que produce y1, y cuáles opciones hay? Se separa lo verificado, lo medido en StructAI y lo que no se puede medir con los datos actuales.

## 1. La idea en sencillo
Tres ingredientes distintos, que conviene no mezclar:
- **Forma (no linealidad):** el efecto no es proporcional; puede saturarse o activarse a partir de un umbral.
- **Rezago:** el efecto llega meses después y puede cambiar de signo según el retraso.
- **Interacción:** el efecto de x1 depende del valor de x2.

Un modelo de segundo orden (regresión estática) ignora los tres; uno de tercer orden los modela. La pregunta honesta es si modelarlos **mejora la predicción fuera de muestra**, no solo el ajuste.

## 2. Física que justifica esperar no linealidad (verificada en la literatura)
- **Umbral de temperatura del mar para la convección.** La convección profunda tropical arranca por encima de un umbral de temperatura del mar de unos 27,5 °C o 26,1 °C según cómo se defina (Yun et al., 2021); los dos valores no son intercambiables ([Yun et al., 2021](https://www.uwi.edu/climatehub/sites/default/files/2024-02/ENSO%E2%80%93rainfallVariability_Yunetal._2021.pdf)).
- **Humedad y extremos.** La capacidad del aire de contener humedad crece ≈ 7 % por °C (Clausius-Clapeyron); los extremos pueden superar esa línea base o quedarse por debajo según escala y región ([Roca et al., 2022](https://www.lmd.ens.fr/muller/Pubs/2022RocaEtAl.pdf); [Rios-Berrios et al., 2025](https://texmex.mit.edu/ftp/pub/emanuel/PAPERS/Rios-Berrios_etal_2025.pdf)). No hay un valor único acordado por grado.
- **Interacción entre océanos.** La lluvia del Caribe responde más cuando las señales de ENSO y del Atlántico norte tropical (TNA) se refuerzan (Giannini, Cane y Kushnir), y un Atlántico norte tropical más cálido debilita el chorro de bajo nivel del Caribe y aumenta la lluvia en Colombia ([Arias et al.](https://link.springer.com/article/10.1007/s00704-024-04934-6)). Es una interacción, pero la literatura no establece si es no lineal.
- **Estacionalidad.** El efecto de El Niño sobre el chorro del Caribe cambia de signo entre la primera y la segunda mitad del año.
- **Asimetría.** Un estudio en Colombia con análisis de recurrencia halló sincronización fuerte con las anomalías negativas de la temperatura del Pacífico oriental (La Niña) y débil con las positivas.

## 3. Catálogo de opciones

| Método | Qué hace | Estado en StructAI | Observación |
|---|---|---|---|
| Rezagos distribuidos lineales (cresta) | Un coeficiente por rezago | **Medido** (M1) | Línea base |
| Lineal con modulación estacional | Coeficientes que varían con el mes | **Medido** (M1s) | Capta el cambio de signo estacional |
| Aditivo con splines por rezago | Curva no lineal por variable | **Medido** (M2) | Sin interacción |
| Interacción y cuadráticos explícitos (ONI × TNA) | Producto y cuadrados de las medias | **Medido** (M4) | La interacción de Giannini et al. |
| Gradient boosting con rezagos | Interacciones libres | **Medido** (M3) | Propenso a sobreajuste con ~500 datos |
| **DLNM** (modelos de rezago distribuido no lineal) | Superficie exposición-rezago-respuesta con una base cruzada ([Gasparrini, 2010](https://researchonline.lshtm.ac.uk/id/eprint/2975)) | No medido | Implementado en R (`dlnm`), no instalado; nuestro M2 es una aproximación aditiva |
| GAM con interacción tensorial | Superficie suave conjunta de x1 y x2 | No medido | Viable con los datos actuales |
| Autorregresión con exógenas (ARX/NARX) | Añade la propia historia de y | No medido | Viable; en lluvia mensual aporta poco |
| Modelos de umbral y de regímenes (TAR, Markov) | Cambio de comportamiento por encima de un umbral | No medido | Necesita temperatura del mar local absoluta (no solo anomalías) |
| Cartografía cruzada convergente (CCM), entropía de transferencia, PCMCI | Detectan acoplamiento causal no lineal ([CCM](https://arxiv.org/pdf/1407.5696)) | No medido | Literatura mixta sobre cuál es más fiable ([ESD, 2018](https://esd.copernicus.org/articles/9/1063/2018/esd-9-1063-2018.pdf)); sirve para detectar, no para predecir |
| Coherencia por ondeletas | Relación por escala de tiempo | No medido | Viable |
| Regresión cuantílica | Cambia la cola, no la media | No medido | Útil para extremos |
| Procesos gaussianos | Incertidumbre calibrada | No medido | Viable, costoso |
| Redes recurrentes, TCN, transformadores | Dinámicas complejas | No medido | **Sin datos suficientes** (528 meses de lluvia, ≈ 250 de temperatura) |
| Koopman, DMD, SINDy | Descubren ecuaciones dinámicas | No medido | Muy sensibles al ruido |
| Modelos físicos acoplados | Simulan la atmósfera y el océano | Fuera de alcance | Es lo que usan los servicios oficiales |

## 4. «Microvariaciones de temperatura»
Lo que se puede afirmar depende del ruido: una tendencia pequeña solo se detecta si supera el **efecto mínimo detectable**, que se calcula del ruido observado. Datos disponibles verificados: el IDEAM publica temperatura máxima, mínima y ambiente (28, 28 y 94 millones de registros), de modo que hay material para estudiarlo por estación; el experimento de este documento reporta la tendencia del Caribe con su intervalo y su efecto mínimo detectable.

## 5. Qué se puede «optimizar» con datos oceanográficos hoy
Con honestidad sobre los datos: el nivel del mar del IDEAM tiene **dos estaciones** (una en el Caribe, 2012-2020), así que no alcanza para tendencias ni para diseño costero. Lo que sí aporta valor ahora:
1. **Usar el índice del Atlántico (TNA) como predictor** del clima del Caribe (ver el experimento).
2. **Valor informativo:** decidir qué estaciones y qué capas conservar (línea de `RESULTADOS_VALOR_INFORMATIVO.md`).
3. Para obras costeras haría falta un servicio de altimetría satelital y datos de oleaje, **no verificados** como abiertos.

## 6. Resultado del experimento (2026-11-08)
Detalle en [`scripts/clima/RESULTADOS_REZAGOS_NO_LINEALES.md`](../../scripts/clima/RESULTADOS_REZAGOS_NO_LINEALES.md). Con ONI y TNA como x1 y x2 y la lluvia y la temperatura del Caribe como y1: un modelo **lineal con modulación estacional** da una habilidad modesta para la lluvia (+0,12 a 1 mes, concentrada en junio-agosto, negativa en marzo-mayo) que **no es significativa tras corregir por comparaciones múltiples** (p = 0,08); **ningún modelo no lineal** (aditivo, boosting, interacción ONI×TNA) lo supera, y con la temperatura no hay habilidad. La tendencia de la temperatura máxima (+0,26 °C/década) queda por debajo del efecto mínimo detectable (0,42). Conclusión: con estos datos y esta resolución, la no linealidad no mejora la predicción; las opciones sin medir de la sección 3 requieren más datos o temperaturas absolutas del mar.
