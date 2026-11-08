# Resultados H3: régimen térmico como predictor del caudal de diseño (2026-11-08)

Protocolo, fijado y publicado antes de ajustar: [`PROTOCOLO_REGIMEN_TERMICO.md`](PROTOCOLO_REGIMEN_TERMICO.md). Código: `regimen_termico.py`. Salidas: `regimen_termico_resultados.json`, `regimen_termico_cuencas.csv`. Datos de temperatura: normales 1991-2020 del IDEAM (`nsz2-kzcq`, CC BY-SA 4.0).

## Resultado principal: **el criterio primario NO se cumple**
Añadir la temperatura media de la cuenca (a través de la biotemperatura de Holdridge) al modelo de la Etapa A **no mejora** la predicción en cuencas no usadas para ajustar. A T = 10, M5 (con temperatura) frente a M2 (referencia): diferencia de la mediana de |error ln| **−0,028, IC95 % [−0,069; +0,022]**, que incluye 0. El factor de error típico es el mismo: 1,744 con temperatura frente a 1,746 sin ella.

## Datos
319 estaciones de temperatura media en los 21 departamentos (Andina 203, Caribe 57, Pacífica 46, Orinoquía 13; el protocolo citaba 362 en todo el país). 257 cuencas de la Etapa A en 50 bloques de 1°.

## Campo de temperatura (paso 1)
La temperatura media anual baja **5,7 °C por km de altitud** (28,8 °C a nivel del mar). Estimada dejando fuera cada estación y las que están a menos de 50 km, el error absoluto mediano es de 0,69 °C con solo la altitud (T1) y 0,64 °C añadiendo la interpolación de residuos (T2). La mejora de T2 no es clara (−0,016 °C, IC95 % [−0,123; +0,041]), por lo que se usó T1, como fijaba el protocolo.

## Validación ciega (factor de error típico)
| T (años) | M2 referencia | M5 + temperatura | M6 + altitud (control) |
|---:|---:|---:|---:|
| 2 | 1,752 | 1,771 | 1,773 |
| 5 | 1,719 | 1,766 | 1,767 |
| **10** | **1,746** | **1,744** | **1,783** |
| 25 | 1,755 | 1,771 | 1,803 |
| 50 | 1,793 | 1,838 | 1,855 |
Pruebas a T = 10: M6 frente a M2 −0,030 [−0,064; +0,028]; M5 frente a M6 −0,007 [−0,014; +0,005]. Ninguna excluye 0. A los otros periodos de retorno, el modelo con temperatura es igual o algo peor que la referencia.

## Lo que sí aparece, y por qué no hay que creerle
- **Dentro de la muestra**, el coeficiente de ln T_bio sale positivo y «significativo» (+1,21, IC95 % [+0,59; +1,92]). Pero **fuera de la muestra no mejora**: el ajuste dentro de la muestra no se traduce en mejor predicción en sitios nuevos, que es el uso real.
- **Por región (T = 10):** en la Andina y la Pacífica el modelo con temperatura mejora poco (1,80 a 1,71; 1,51 a 1,47); en el **Caribe empeora mucho** (1,89 a 2,25) y en la Orinoquía (11 cuencas) no se puede concluir. El coeficiente promedia regiones con comportamientos opuestos.
- **Es altitud disfrazada.** La correlación de ln T_bio con la altitud media es −0,99: la temperatura de una cuenca, con los datos disponibles, es casi toda altitud. Por eso el control con altitud sola (M6) se comporta igual que M5. **La temperatura no aporta información más allá de la altitud.**

## Lectura
1. La hipótesis «el régimen térmico mejora la regionalización de caudales» **no se sostiene** con estos datos. Se publica como resultado negativo.
2. No se probaron otras formas del índice, como fijaba el protocolo (evitar buscar hasta que algo salga).
3. Esto **no dice nada sobre la humedad antecedente del suelo** por evento: eso requiere series diarias o de satélite y sigue abierto.

## Límites
La temperatura anual no refleja el régimen estacional ni la humedad del suelo; la fórmula de Holdridge no usa radiación ni viento; temperaturas concentradas en zonas pobladas; la altitud media de la cuenca no es la del sitio de medida; el caudal observado es el máximo horario. **No sustituye el criterio del hidrólogo.**
