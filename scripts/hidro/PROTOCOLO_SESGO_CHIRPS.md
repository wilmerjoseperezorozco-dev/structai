# Protocolo Etapa B: sesgo de CHIRPS frente a pluviómetros automáticos del IDEAM y corrección por cuantiles (preregistrado 2026-11-08, antes de descargar ningún registro de pluviómetro ni calcular ningún sesgo)

**Pregunta.** CHIRPS (satélite, 5 km) y los pluviómetros automáticos del IDEAM miden la misma lluvia diaria. ¿Cuánto difieren, de qué manera (frecuencia de días lluviosos, lluvias medias, lluvias extremas), y una corrección por cuantiles estimada en unas estaciones reduce el error en estaciones que no se usaron para estimarla? ¿Cambia eso la estimación del caudal de diseño de la Etapa A?

**Esta es una muestra piloto, no una calibración nacional.** Tres años de traslape, una muestra de estaciones automáticas y un satélite con resolución de 5 km. La corrección que resulte solo es válida para el periodo y las regiones muestreadas.

## 1. Datos
- **Pluviómetros:** conjunto `Precipitación` (`s54a-sgyg`, `datos.gov.co`, IDEAM): acumulados de 10 minutos de sensores automáticos con telemetría. Verificado antes de fijar este protocolo, sin cruzarlo con CHIRPS: 144 registros por día en estaciones normales; algunos días tienen varios cientos de registros por duplicación de sensores; los valores no son negativos y el 79 % es cero.
- **CHIRPS:** v3.0 diaria, producto final «sat» (el mismo de los demás análisis del proyecto), pixel que contiene la estación (principal) y media de 3 × 3 pixeles (sensibilidad).
- **Periodo:** 2022-01-01 a 2024-12-31 (incluye La Niña 2022, la transición de 2023 y El Niño de 2024).
- **Catálogo:** estaciones del catálogo nacional del IDEAM (`hp9r-jxuu`) con estado Activa, tecnología «Automática con Telemetría», categoría pluviométrica, pluviográfica o climatológica, en los 21 departamentos del proyecto, agrupadas en las regiones naturales de la Etapa A (Caribe, Andina, Pacífica, Orinoquía).

## 2. Selección de la muestra (fijada ahora; no depende de CHIRPS)
Dentro de cada región se ordenan las estaciones candidatas al azar (semilla 20261108) y se recorren en ese orden: se descarga cada una y se la **acepta** si tiene al menos **700 días válidos** de los 1.096. Se detiene cuando hay 12 aceptadas por región (48 en total) o se recorren 40 candidatas por región. El criterio de aceptación solo usa los datos del pluviómetro.

## 3. Total diario del pluviómetro y control de calidad (fijado ahora)
- Se usa **un solo sensor por estación** (el de más registros) y se elimina la duplicación por marca de tiempo.
- Un día es **válido** si el sensor tiene al menos 130 de los 144 registros esperados (≥ 90 %), ningún valor negativo y total diario ≤ 600 mm. El total del día es la suma de los acumulados de 10 minutos.
- **Alineación horaria.** CHIRPS suma el día en horario UTC; el momento de las marcas del IDEAM (hora local o UTC) no está documentado en lo que revisé. Se prueban las dos alineaciones (marcas tal como están y marcas + 5 horas) y se elige la que da mayor mediana de correlación de Spearman diaria entre pluviómetro y CHIRPS en toda la muestra. Esa elección usa la correlación, no el tamaño del sesgo.

## 4. Medidas del sesgo (antes de corregir)
Por estación, solo sobre días válidos: (a) correlación de Spearman diaria; (b) razón del total acumulado CHIRPS / pluviómetro; (c) frecuencia de días con lluvia ≥ 1 mm en cada fuente; (d) razón de cuantiles de los días con lluvia ≥ 1 mm (percentiles 50, 75, 90, 95 y 99); (e) razón del máximo diario del periodo. Resumen por región con IC95 % por bootstrap de estaciones.

## 5. Corrección por cuantiles
**Método.** Para cada región, el factor de corrección en el cuantil *q* es la mediana, entre las estaciones de entrenamiento de esa región, de (cuantil *q* del pluviómetro) / (cuantil *q* de CHIRPS) de los días con lluvia ≥ 1 mm, en los percentiles 50, 75, 90, 95 y 99; entre percentiles se interpola linealmente y por encima del 99 se mantiene el factor del 99.
**Validación (sin usar la estación evaluada):** dejando una estación fuera; los parámetros se estiman con las demás estaciones de la misma región. Se mide, en la estación excluida, el error de los cuantiles de CHIRPS antes y después de corregir.

## 6. Criterios
- **Primario:** en la validación dejando una estación fuera, la mediana de |ln(razón CHIRPS / pluviómetro)| del **percentil 99** de los días lluviosos **disminuye** con la corrección; IC95 % de la diferencia por bootstrap de estaciones que excluya 0. Si no, se informa que la corrección no mejora las lluvias fuertes.
- **Secundarios (todos reportados):** lo mismo en los percentiles 50, 75, 90 y 95; en el total acumulado; en la frecuencia de días lluviosos (la corrección por cuantiles no la modifica; se reporta como límite); por región; con el pixel de 3 × 3.
- **Efecto sobre la Etapa A.** La Etapa A usa la **lluvia media anual** 1991-2020 de CHIRPS como predictor. Con la razón regional del total acumulado de la sección 4, se construye un escenario de predictor corregido (la lluvia media anual de cada cuenca se multiplica por la razón regional inversa) y se repite la validación ciega de la Etapa A para T = 10, comparando el factor de error típico de M2 con y sin corrección. Es un escenario condicional: supone que el sesgo de 2022-2024 es el de 1991-2020.

## 7. Límites declarados de antemano
Tres años y 48 estaciones: no hay forma de estimar un factor definitivo para eventos de más de pocos años de retorno. Las estaciones automáticas se concentran en zonas pobladas y a ciertas alturas. La comparación mezcla una medida puntual con el promedio de un pixel de 5 km, que es una diferencia de escala, no solo de sesgo. El IDEAM puede tener faltas de calidad en el sensor que el control no detecta (sensor obstruido, lluvia subregistrada). La corrección de cuantiles no repara la frecuencia de días lluviosos. **No sustituye una calibración con datos de serie larga ni el criterio del hidrólogo.**

## Enmienda 1 (2026-11-08, antes de extraer CHIRPS y de calcular ningún sesgo)
**Hallazgo.** Al descargar la primera tanda (128 estaciones recorridas, 40 por región), 79 no tienen ningún registro en 2022-2024 y solo 6 tienen 700 o más días válidos: casi todos los sensores automáticos del conjunto son recientes. Con el criterio de 700 días se aceptarían 7 de 48 estaciones, insuficiente.
**Cambio.** El mínimo de días válidos baja de 700 a **300** y el máximo de candidatas recorridas por región sube de 40 a **120**. El criterio sigue usando solo el pluviómetro. Como las estaciones recientes cubren solo parte del periodo, **todas las comparaciones se hacen únicamente en días con dato válido en ambas fuentes**, y se reporta el número de días y las estaciones por año; las estaciones con menos de dos temporadas lluviosas no permiten comparar el total anual y se señalan.
