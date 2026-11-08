# Protocolo H1: lluvia media anual de CHIRPS frente a las normales climatológicas del IDEAM 1991-2020 (preregistrado 2026-11-08, antes de comparar ningún valor de CHIRPS con ninguna normal)

**Pregunta.** La regionalización de caudales (Etapa A) usa como predictor la lluvia media anual 1991-2020 de CHIRPS v3. El IDEAM publica las normales climatológicas 1991-2020 de cientos de estaciones. ¿Cuánto difiere CHIRPS de las normales, en qué regiones y alturas, y una corrección estimada en unas estaciones reduce el error en estaciones no usadas para estimarla? ¿Cambia eso la estimación del caudal de diseño de la Etapa A?

**Es una comparación de un satélite con la red de superficie, no una calibración nacional.** Dos advertencias de entrada: (1) CHIRPS incorpora datos de estaciones, y parte de las del IDEAM puede estar entre ellas, de modo que el acuerdo puede **sobrestimar** la exactitud independiente de CHIRPS; no hay forma de separarlo con estos datos. (2) Se compara el promedio de un pixel de ~5 km con un punto.

## 1. Datos
- **Normales:** conjunto `nsz2-kzcq` de datos.gov.co (IDEAM, licencia CC BY-SA 4.0), parámetro precipitación, periodo 1991-2020: 1.599 estaciones con coordenadas, altitud, 12 medias mensuales y media anual. Se descargó y se revisó únicamente su estructura y la distribución de la columna `ao`; no se ha cruzado con CHIRPS.
- **CHIRPS:** la lluvia media anual 1991-2020 ya calculada en la Etapa A (`_cache/lluvia_media_anual_1991_2020.npz`) y, para el ciclo estacional, el mes a mes de CHIRPS mensual del mismo periodo. Valor en el pixel que contiene la estación (principal) y media 3 × 3 (sensibilidad).
- **Campo `ao`:** toma valores de 1 a 11, no está documentado en lo que revisé. Por su rango (las directrices de la OMM permiten hasta 10 años faltantes de 30) podría ser el número de años faltantes, pero **no está verificado**. No se usa para filtrar en el análisis primario; se reporta como sensibilidad (estaciones con `ao` ≤ 5).

## 2. Estaciones del análisis
Las de los 21 departamentos del proyecto, agrupadas en las regiones de la Etapa A (Caribe, Andina, Pacífica, Orinoquía; los mismos grupos de departamentos de `pluviometros_descarga.py`). Se excluyen estaciones sin coordenadas o con la media anual fuera de [100; 15.000] mm. Las estaciones de otros departamentos (Chocó, Amazonas, etc.) se describen aparte, sin corrección ni conclusión.

## 3. Medidas del acuerdo (antes de corregir)
Por estación: e = ln(P_CHIRPS / P_normal). Resumen: mediana de e (sesgo), mediana de |e| (error típico), cuantiles de e, por región y por banda de altitud de la estación (< 500; 500-1.500; 1.500-2.500; ≥ 2.500 m) y por clase de lluvia (< 1.000; 1.000-2.000; 2.000-3.500; ≥ 3.500 mm). IC95 % por bootstrap de **bloques espaciales de 1°** (no de estaciones sueltas, porque estaciones cercanas se parecen). Ciclo estacional: correlación de Spearman de las 12 medias mensuales por estación y acuerdo del mes más lluvioso.

## 4. Corrección (tres variantes, fijadas ahora)
- **C0:** sin corrección.
- **C1:** multiplicar por la mediana regional de P_normal / P_CHIRPS de las estaciones de entrenamiento.
- **C2:** ln(P_normal) = a + b · ln(P_CHIRPS) + c · altitud(km) + efecto de región, ajustada por mínimos cuadrados con las estaciones de entrenamiento.

**Validación:** dejando un bloque de 1° fuera, con zona de exclusión de 50 km alrededor de las estaciones evaluadas; los parámetros se estiman con las demás estaciones. En las estaciones excluidas se compara |ln(P_corregida / P_normal)| con el de C0.

## 5. Criterios
- **Primario:** C1 reduce la mediana de |e| respecto de C0 en la validación; IC95 % de la diferencia por bloques que excluya 0. Si no, se informa que la corrección regional simple no mejora.
- **Secundarios (todos reportados):** C2 frente a C0 y frente a C1; por región y banda de altitud; con el pixel 3 × 3; solo estaciones con `ao` ≤ 5; ciclo estacional.
- **Efecto sobre la Etapa A.** El predictor de lluvia de cada cuenca de la Etapa A (media de CHIRPS en la cuenca) se sustituye por su versión corregida con el modelo ajustado **sin** las estaciones del mismo bloque de 1° que la cuenca; se repite la validación ciega de M2 a T = 10 y se compara el factor de error típico con el de la Etapa A (1,75). Es un escenario condicional, no una nueva calibración.

## 6. Límites declarados de antemano
Normales de estaciones concentradas en zonas pobladas y a ciertas alturas; escala punto-pixel; posible no independencia de CHIRPS; las normales miden la lluvia media, no la de tormenta de diseño; el significado de `ao` sin verificar; no hay validación en zonas sin estaciones (montaña alta, selva). **No sustituye una calibración hidrológica con ingeniero responsable.**
