# Protocolo H3: régimen térmico (temperatura de las normales del IDEAM) como predictor del caudal de diseño (preregistrado 2026-11-08, antes de construir el campo de temperatura de las cuencas y de ajustar ningún modelo con él)

**Pregunta.** La regionalización de caudales (Etapa A) usa área, lluvia media anual y pendiente. ¿La temperatura media de la cuenca, que fija la evapotranspiración potencial y por tanto cuánta lluvia se convierte en escorrentía, mejora el pronóstico del caudal máximo en sitios no usados para ajustar el modelo?

**Qué es y qué no es.** Es una versión **climatológica** (régimen medio anual) de la idea de «humedad antecedente del suelo». **No** mide la humedad del suelo antes de cada evento, que requeriría series diarias o de satélite (por ejemplo ESA CCI) y datos por evento; eso queda como hipótesis aparte.

**Advertencia de diseño.** Con los datos disponibles, la temperatura de una cuenca se obtiene en gran parte de su altitud media. Por eso se incluye un modelo de control solo con altitud: si la temperatura no mejora por encima de la altitud sola, el resultado es «la temperatura no agrega información más allá de la altitud».

## 1. Datos
- **Temperatura media anual 1991-2020 de las normales** (`nsz2-kzcq`, IDEAM, CC BY-SA 4.0), parámetro `TEMPERATURA MEDIA`, 362 estaciones con coordenadas y altitud. Se cuentan promedio de los 12 meses disponibles; el significado de la columna `ao` no está verificado y no se usa para filtrar.
- **Cuencas:** las de la Etapa A (`cuencas_estaciones.csv`, variante elegida, altitud media `elev_media_m` y lluvia media de CHIRPS `lluvia_media_mm`). Caudales máximos y periodos de retorno: los mismos de la Etapa A.

## 2. Campo de temperatura (paso 1, validado primero)
- **T1:** T = a + b · altitud (km), mínimos cuadrados con las estaciones de las normales dentro de los 21 departamentos del proyecto.
- **T2:** T1 más interpolación de los residuos con ponderación inversa a la distancia al cuadrado de las 3 estaciones más cercanas (máximo 100 km; sin estaciones, residuo 0).
Validación dejando fuera cada estación y las que están a menos de 50 km; se reporta el error medio absoluto en °C y su IC95 % por bloques de 1°. T2 se usa para las cuencas si su error en la validación es menor que el de T1 con IC95 % que excluya 0; si no, se usa T1.
La temperatura de la cuenca es el campo evaluado en su altitud media y en el punto de la estación de caudal.

## 3. Índice de régimen
Biotemperatura de Holdridge T_bio = mín(máx(T, 0), 30) °C. Evapotranspiración potencial PET = 58,93 · T_bio (mm/año) y relación PET/P con P = lluvia media de CHIRPS de la cuenca. Como PET/P = 58,93 · T_bio / P, incluir ln(PET/P) junto a ln P equivale a incluir **ln T_bio**: eso es lo que entra en el modelo.

## 4. Modelos (misma validación ciega de la Etapa A: zona de exclusión de 50 km y misma corriente, T = 10)
- **M2:** ln Q = a + b ln A + c ln P + d ln S (referencia de la Etapa A).
- **M5:** M2 + e · ln T_bio.
- **M6 (control):** M2 + e · altitud media (km).
Solo T = 10 es confirmatorio; los demás periodos de retorno se reportan.

## 5. Criterios
- **Primario:** M5 reduce la mediana de |error ln| respecto de M2; IC95 % de la diferencia por bloques espaciales de 1° que excluya 0.
- **Secundarios (todos reportados):** M6 frente a M2; M5 frente a M6 (si la temperatura agrega algo más allá de la altitud); por región natural; T = 2, 5, 25, 50; sensibilidad con T1 en lugar de T2; signo y magnitud del coeficiente con su IC95 %.
Si el criterio primario no se cumple, se informa que la temperatura no mejora la regionalización; no se prueban otras formas del índice.

## 6. Límites declarados de antemano
La temperatura media anual no representa el régimen estacional ni la humedad del suelo antes de un evento; la fórmula de Holdridge es una aproximación que no usa radiación ni viento; solo hay 362 estaciones de temperatura, concentradas en zonas pobladas; la altitud media de la cuenca no es la del punto de medida; la temperatura y la pendiente son proxies de la altitud y de la región, y los signos de los coeficientes no se interpretan causalmente (como ocurrió con la pendiente en la Etapa A). **No sustituye el criterio del hidrólogo.**
