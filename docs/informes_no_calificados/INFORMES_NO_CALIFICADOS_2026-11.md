# Informes de resultados que no calificaron como motor (7 al 9 de noviembre de 2026)

Cada entrada recoge, para una prueba que no calificó como motor, la pregunta, el criterio fijado antes de calcular, el resultado, **las limitaciones que impidieron calificar** y lo que haría falta para repetirla con posibilidades reales. Un resultado negativo no es un fallo del trabajo: fija hasta dónde llegan estos datos. Los criterios **no deben modificarse** después de ver los datos; una repetición se registra como protocolo nuevo.

Contexto y criterio de motor: [`../CLASIFICACION_HIPOTESIS_Y_MOTORES_2026-11.md`](../CLASIFICACION_HIPOTESIS_Y_MOTORES_2026-11.md) · [`../REGLAS_MOTORES_DE_CALCULO.md`](../REGLAS_MOTORES_DE_CALCULO.md). Las rutas de protocolo, resultados y datos están bajo `scripts/` en cada caso.

---

## A. Hidrología de caudales máximos (`scripts/hidro/`)

### A1. Pendiente del cauce principal en la regionalización (E1)
- **Pregunta.** ¿Añadir o sustituir la pendiente del cauce mejora la estimación regional de caudal máximo a T = 10 años?
- **Criterio.** Reducción de la mediana de |error ln| con IC 97,5 % (Bonferroni) que excluya 0.
- **Resultado.** No se cumple. Factor de error típico: M2 1,75; M2c (sustituye) 1,82; M2b (añade) 1,76.
- **Limitaciones.** DEM agregado a ~90 m: en la mediana de las cuencas, el 44 % de los tramos de la ruta cae en el piso de pendiente del protocolo, y la pendiente de Taylor-Schwarz sale sistemáticamente baja. Muestra de 256 cuencas con área mínima de 5 km²; no cubre el dominio de la Res. 0330 (menos de 80 ha). Un contraste secundario (cuencas > 30 %) excluye 0 con efecto de ~1 %, dentro de 24 contrastes sin corregir: no se presenta como hallazgo.
- **Para repetirla.** DEM de 30 m (Copernicus original), cuencas pequeñas, protocolo nuevo preregistrado. Sigue sin medirse la lluvia de diseño por duración.
- **Archivos.** `PROTOCOLO_PENDIENTE_CAUCE.md`, `RESULTADOS_PENDIENTE_CAUCE.md`, `pendiente_cauce_resultados.json`.

### A2. Régimen térmico como predictor del caudal de diseño (H3)
- **Pregunta.** ¿Un índice de régimen térmico mejora la regionalización de caudales?
- **Resultado.** El criterio primario no se cumple. No se probaron otras formas del índice, como fijaba el protocolo para evitar buscar hasta que algo salga.
- **Limitaciones.** La temperatura anual no refleja el régimen estacional ni la humedad del suelo; la fórmula de Holdridge no usa radiación ni viento; las temperaturas se concentran en zonas pobladas; la altitud media de la cuenca no es la del sitio de medida; el caudal observado es el máximo horario.
- **Para repetirla.** La humedad antecedente del suelo por evento requiere series diarias o de satélite (ESA CCI cubre bien el Caribe y queda vacía en Andes y Pacífico, ver `scripts/satelite/RESULTADOS_ESA_CCI_COBERTURA.md`). Queda abierta.
- **Archivos.** `RESULTADOS_REGIMEN_TERMICO.md`, `regimen_termico_resultados.json`.

### A3. No estacionariedad espacial y transferibilidad
- **Pregunta.** ¿Un modelo por región natural supera al modelo nacional, y se transfiere entre regiones?
- **Resultado.** C1 no se cumple (diferencia 0,000; IC [−0,067; 0,000]). Hallazgo de contenido: un modelo entrenado sin el Caribe lo subestima por un factor de 3 (mediana Q̂/Q = 0,33; error típico de 1,89 a 3,00). La pendiente cambia de signo entre el Caribe (−0,74) y la Pacífica (+0,93).
- **Limitaciones.** Solo variación espacial; Orinoquía (11 estaciones) no se puede modelar; en 18 de 35 estaciones pacíficas quedan menos de 30 de entrenamiento tras la zona de exclusión; la prueba F de interacción no es válida como prueba formal (autocorrelación espacial); con 35 a 152 estaciones por región la potencia es limitada.
- **Para repetirla.** Más estaciones por región (especialmente Orinoquía y Amazonía), un método de prueba que contemple la autocorrelación espacial, y estacionariedad temporal verificada. **Consecuencia práctica:** no exportar la ecuación nacional a otra región o país sin calibrar con estaciones locales.
- **Archivos.** `PROTOCOLO_NO_ESTACIONARIEDAD.md`, `RESULTADOS_NO_ESTACIONARIEDAD.md`.

### A4. Corrección de sesgo de CHIRPS por cuantiles (Etapa B)
- **Pregunta.** ¿La corrección por cuantiles mejora el percentil 99 de los días lluviosos en estaciones no usadas para estimarla?
- **Resultado.** El criterio primario no se cumple: el IC95 % incluye 0 y la corrección empeora el total. No se recomienda aplicarla.
- **Limitaciones.** 35 estaciones, 3 años, Orinoquía con 2; estaciones en zonas pobladas; comparación punto frente a píxel de 5 km; alineación horaria elegida por correlación con diferencia pequeña. Discrepancia no explicada: CHIRPS +5 % frente a las normales 1991-2020 y +33 % frente a estos pluviómetros.
- **Para repetirla.** Más estaciones y años; tratar primero la frecuencia de días lluviosos (por ejemplo un umbral por región), no los cuantiles.
- **Archivos.** `PROTOCOLO_SESGO_CHIRPS.md`, `RESULTADOS_SESGO_CHIRPS.md`.

### A5. Ecuaciones de caudal máximo de la literatura, evaluadas a ciegas
- **Pregunta.** ¿Alguna ecuación publicada mejora a M2 en las 257 estaciones?
- **Resultado.** Ninguna ecuación evaluable. No se calculó ninguna métrica.
- **Limitaciones.** De 141 trabajos únicos, 8 candidatos: el artículo del Cauca (captcha 403, no se saltó) y el modelo MG (repositorio con error 500) no se pudieron leer; una ecuación de la Amazonía peruana solo vale para 99.779–877.479 km² (la mayor cuenca propia tiene 18.624 km²); otras exigen predictores que no se calculan aquí.
- **Para repetirla.** Conseguir el texto del artículo del Cauca y del modelo MG por biblioteca universitaria y evaluarlos con el mismo protocolo sin cambiarlo. Ampliar la búsqueda exige un protocolo nuevo.
- **Archivos.** `PROTOCOLO_LITERATURA_CAUDALES.md`, `RESULTADOS_LITERATURA_CAUDALES.md`, `literatura_caudales_busqueda.json`.

---

## B. Sísmica y normativa (`scripts/ingesta/nsr10/`)

### B1. Brecha entre el Apéndice A-4 y la capa del SGC
- **Pregunta.** ¿Los 29 municipios con Aa o Av distinto entre el A-4 y el SGC son más vulnerables que el resto?
- **Resultado.** No se cumple: mediana de vivienda con material vulnerable 39,7 % (22 municipios) frente a 39,1 % (976); diferencia +0,7 puntos, IC95 % [−9,6; +9,5], p = 0,80.
- **Limitaciones.** Con 22 municipios la potencia es baja; 7 de los 29 no están en el panel (la población es un mínimo); no se verificó el año de la población; **no se sabe cuál fuente es la vigente**, así que las dos cifras de población son extremos de un intervalo; se excluyó el Sisbén (acceso no verificado, datos personales). Aa y Av se mueven en saltos de 0,05: una brecha de 20–33 % suele ser un escalón de la tabla.
- **Para repetirla.** Determinar la fuente vigente; incorporar datos de vulnerabilidad con licencia clara. Mientras tanto, 10 casos para revisión por un ingeniero (Villavicencio, Montería, Cúcuta, Caldas, La Calera, Ábrego, Santafé de Antioquia, Guachetá, Garagoa, San Luis), que alimentan #135.
- **Archivos.** `PROTOCOLO_BRECHA_NORMATIVA.md`, `RESULTADOS_BRECHA_NORMATIVA.md`, `RESULTADOS_AUDITORIA_A4_VS_SGC.md`.

### B2. ¿El mapa municipal de intensidad del SGC se reproduce desde sus puntos?
- **Resultado.** No: el mapa da un valor más alto que los puntos en 345 municipios y más bajo en 194 (sesgo medio de los puntos menos el mapa: −0,43). 218 municipios del mapa tienen valor sin ningún punto de observación, lo que sugiere interpolación (inferencia, no verificada con el SGC).
- **Limitaciones.** Escala de intensidad no documentada (código 1); un punto mal ubicado cae en el municipio equivocado; no se distingue entre interpolación, otra versión de los datos u otro criterio de agregación.
- **Implicación.** No dice que el mapa esté mal. Los análisis que comparan Aa con intensidad observada reflejan en parte un producto interpolado.
- **Archivos.** `PROTOCOLO_SISMICIDAD_HISTORICA.md`, `RESULTADOS_SISMICIDAD_HISTORICA.md`, `RESULTADOS_INTENSIDAD_VS_A4.md`.

### B3. Catálogo de sismos del SGC frente al Aa del A-4
- **Resultado.** C1 se cumple débilmente; C2 no se cumple de forma trivial porque la definición era mala: el 67 % de los municipios no tiene ningún evento M ≥ 4,0 en 28 años y la mediana es 0 en todas las zonas.
- **Para repetirla.** Redefinir la variable de respuesta (por ejemplo, magnitud acumulada o intensidad máxima) en un protocolo nuevo. En las capas de intensidad, el PGA del SGC no es comparable con el Aa.
- **Archivos.** `PROTOCOLO_CATALOGO_SISMOS_VS_A4.md`, `RESULTADOS_CATALOGO_SISMOS_VS_A4.md`.

### B4. Docling frente a pypdf en las páginas A.2.3–A.2.6
- **Resultado.** La regla se cumple por 3,4 puntos de recall numérico (dos fichas de 59); la ventaja es mínima, útil en tablas, no decodifica ecuaciones. Es una herramienta, no un motor.
- **Limitación.** Los recalls por grupo de páginas no son interpretables (se compararon contra toda la referencia).
- **Archivos.** `PROTOCOLO_DOCLING_A2.md`, `RESULTADOS_DOCLING_A2.md`.

---

## C. Territorio, vías y reporte de eventos (`scripts/satelite/`, `scripts/regional/`)

### C1. Índice geomorfométrico de exposición para vías terciarias (V1 y V2)
- **Resultado.** Ninguno de los dos criterios se cumple: el índice no ordena los municipios por eventos de la UNGRD mejor que el azar y no supera a la pendiente sola. Ninguna sensibilidad cambia la conclusión.
- **Limitaciones.** DEM de 90 m (no ve taludes de corte ni terraplenes); TWI con pendiente mínima 0,001 (decisión de implementación no fijada en el protocolo); la clase de vía de OpenStreetMap no es la categoría oficial de vía terciaria; cobertura de OSM desigual; **sin validación contra el fenómeno que importa** (inundación o falla efectiva de un tramo). La lista de tramos prioritarios no debe usarse para decidir inversiones.
- **Para repetirla.** Validar tramo por tramo contra inundación observada con radar (Sentinel-1), que no depende de reportes municipales; falta preregistrarlo.
- **Archivos.** `PROTOCOLO_INDICE_VIAL_GEOMORFOMETRICO.md`, `RESULTADOS_INDICE_VIAL.md`.

### C2. V1: exposición de la vía principal a terreno bajo y reportes de daño
- **Resultado.** V1 no se confirma fuera del Caribe (C-1). La asociación vista en el Caribe no es una ley general. En V1-Perú tampoco se generaliza como patrón único; la heterogeneidad por región natural es el hallazgo (efecto positivo en la costa, negativo en la sierra).
- **Limitaciones.** El resultado primario suma todos los eventos de la UNGRD (la versión solo-inundación da +0,10 [+0,01; +0,18] pero no alcanza el umbral preregistrado de 0,15); la UNGRD mide también capacidad de reportar; HAND de 90 m no ve diques ni terraplenes; OSM voluntario; «terreno bajo» significa cosas distintas en una llanura y en una montaña (fracción mediana HAND < 10 m: 0,49 en el Caribe, 0,06 en la Andina). En Perú, C-1 no fue concluyente por la tasa de Y1. No se debe usar la exposición vial como indicador de focalización.
- **Archivos.** `scripts/satelite/PROTOCOLO_V1_CONFIRMACION.md`, `RESULTADOS_V1.md`; `scripts/regional/PROTOCOLO_V1_PERU.md`, `RESULTADOS_V1_PERU.md`. Exploratorias pendientes de V1-Perú: #125.

### C3. Sesgo de reporte de la UNGRD
- **Resultado.** El sesgo de reporte, medido así, no explica el efecto del Caribe (S3).
- **Limitaciones.** Descarte débil: la mediana del indicador P_A es 0,00 en el Caribe y en la Pacífica, casi no varía y tiene poca capacidad de detectar un sesgo; no hay medida directa de capacidad institucional; los indicadores usan el mismo periodo que el resultado; los eventos se cuentan por municipio de reporte, no por sitio.
- **Para repetirla.** Explicaciones físicas o territoriales propias del Caribe (ciénagas, planicies, red vial sobre llanuras de inundación) y una medida directa de capacidad institucional.
- **Archivos.** `PROTOCOLO_SESGO_REPORTE.md`, `RESULTADOS_SESGO_REPORTE.md`.

### C4. Mapa de amenaza del SGC frente a eventos de la UNGRD
- **Resultado.** Los criterios K1–K4 se cumplen (AUC ≈ 0,75; robusto sin 2022 y sin los 11 municipios de más de 500 mil habitantes), pero la pendiente sola ordena igual. No aporta un motor propio.
- **Archivos.** `RESULTADOS_SGC_VS_UNGRD.md`, `RESULTADOS_SIMMA_DETALLE.md` (SIMMA a 1:25.000 cubre pocos municipios).

### C5. Barrido exploratorio del Caribe
- **Alcance.** Genera hipótesis; no confirma nada. 120 pares con 7 departamentos y 195 municipios admiten por construcción alrededor de 10 % de falsos descubrimientos entre los candidatos. La mayoría de los candidatos con |ρ| alto son definicionales (terreno bajo e inundación). V2 (terreno bajo y vivienda vulnerable, ρ = −0,35) y V3 quedan como hipótesis sin preregistrar.
- **Archivos.** `PROTOCOLO_BARRIDO_CARIBE.md`, `RESULTADOS_BARRIDO_CARIBE.md`.

---

## D. Umbrales y formulas de movimientos en masa (`scripts/satelite/RESULTADOS_UMBRALES_Y_FORMULAS.md`)

| Prueba | Resultado | Por qué no califica |
|---|---|---|
| T2 y T3: curva de lluvia acumulada–duración (E–D) | TSS +0,090 con 90 % de falsas alarmas; la regla simple de un solo D* es mejor (TSS +0,253) | La curva compleja no aporta sobre la regla simple. **La regla simple sí se plantea como motor (ver issue)**. |
| M1: área de movimientos con log-normal o inversa gamma | Log-normal rechazada al 5 % (KS p = 0,040) | Muestra de 184 polígonos no probabilística; sin volumen ni fecha: no sirve para dimensionar contención. |
| H2: umbral con pendiente y ONI | ΔTSS −0,031: significativamente peor que la curva global | La corrida por región se interrumpió y quedó pendiente de registrar. |
| H4b: GEV con ONI, predictiva | La candidata gana en 43,1 % de estaciones | Significativo, pero en contra (peor que el azar). |
| H5: forma ξ fija regional | No mejora | — |
| Caribe | No se ajusta: 63 eventos de calibración (< 100) | Datos insuficientes. |

Nota de herramienta: `consolidar_corrida.py` marcaba H2 y H4b como «significativo» porque los p-valores son bilaterales; ahora distingue el sentido.

---

## E. Precios (`scripts/precios/`)

### E1. Agregados y producción de canteras (B1)
- **Resultado.** Nulo. La prima de precio de agregados de una provincia no se explica por la oferta declarada, la distancia a los 25 mayores municipios productores, a Bogotá ni al puerto; todos los IC incluyen 0.
- **Limitaciones.** Solo 32 departamentos independientes (un efecto |ρ| < 0,4 no se distinguiría de cero); el volumen de la ANM es el declarado para regalías y gran parte sale de extracción informal o de río sin título; los precios de INVIAS son de referencia y pueden suavizar la geografía real; la ubicación se aproximó con la capital departamental.
- **Para repetirla.** Cotizaciones de mercado con ubicación, o volúmenes verificados de canteras. Con los datos actuales no vale la pena refinar el modelo.
- **Archivos.** `PROTOCOLO_AGREGADOS_CANTERAS.md`, `RESULTADOS_AGREGADOS_CANTERAS.md`.

### E2. Transmisión TRM y WTI al índice ICOCIV (P3)
- **Resultado.** TRM → carreteras acumulado a 6 meses +0,194 (p Holm 0,111, no significativo); WTI no significativo. Efecto mínimo detectable 0,283 (TRM) y 0,128 (WTI).
- **Limitaciones.** 69 meses con un solo ciclo no identifican transmisiones de corto plazo; el IPC y el índice se mueven juntos por el ciclo inflacionario común. El Monte Carlo del costo (P4: costo en riesgo de 5,9 % a 6 meses y 7,5 % a 12 meses) cubre el 80 % nominal, pero la referencia ingenua cubre igual de bien. Alimenta #102 y #113.
- **Archivos.** `PROTOCOLO_PRECIOS.md`, `RESULTADOS_P3_P4.md`.

---

## Qué hacer con este material
- No citar ninguno de estos resultados negativos como prueba de ausencia de efecto: son ausencia de evidencia con estos datos.
- Cada «para repetirla» se convierte en un issue solo cuando los datos o el método nuevos existen; los cuatro con ruta clara ya están abiertos.
- Si un criterio no se cumplió, no se enmienda: se escribe un protocolo nuevo, se fija antes de calcular y se enlaza a este informe.
