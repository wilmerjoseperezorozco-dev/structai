# Protocolo: caudales de diseño en sitios sin aforo por regionalización, con validación ciega en cuencas con estación (preregistrado 2026-11-08, antes de delinear ninguna cuenca ni ajustar ningún modelo)

**Pregunta.** ¿Se puede estimar el caudal máximo de diseño de un sitio sin estación a partir de datos que existen en cualquier lugar del país (área de la cuenca, pendiente, lluvia), y con qué error? El error se mide **a ciegas**: se aplica el método a la cuenca de una estación real del IDEAM sin usar sus caudales (ni los de sus vecinas cercanas), y se compara con el caudal que esa estación midió.

**Alcance de esta etapa y lo que queda para otra.** Esta es la **Etapa A** (regionalización y validación). La **Etapa B** (corrección de sesgo de CHIRPS con pluviómetros del IDEAM por cuantiles) queda fuera de esta corrida por una restricción de datos que se declara abajo y se preregistra aparte antes de ejecutarla. La humedad antecedente del suelo se trata también por separado: la regionalización usa máximos anuales sin evento asociado y no puede probarla.

## 1. Datos
- **Variable objetivo.** Caudales de retorno Q_T para T = 2, 5, 10, 25 y 50 años ajustados con GEV a los máximos anuales del IDEAM (`Q_MX_A`), ya calculados en `frecuencia_crecientes_ideam.json` (protocolo §21). T = 100 queda fuera por ser extrapolación. **Inclusión de estaciones:** al menos 30 años de registro, último año ≥ 2000, y no más del 10 % de años con valor repetido (`rep ≤ 0,10`), como en §21. Es un máximo horario, no el pico instantáneo: el caudal observado **subestima** el pico de diseño en cuencas pequeñas, y esto se declara como límite del objetivo y no del método.
- **Predictores de cuenca**, calculados con el modelo digital de terreno Copernicus de ~90 m de cada departamento (los 21 departamentos ya descargados para el proyecto, que cubren el Caribe, la región Andina, el Valle, Cauca, Nariño y Meta): **A** (área de la cuenca, km²), **S** (pendiente media de la cuenca, %), **P** (lluvia media anual 1991-2020 promediada sobre la cuenca, mm, con CHIRPS v3 mensual). Sensibilidad: **H** (elevación media).
- **Delineación.** La estación se ajusta («snap») a la celda de mayor acumulación dentro de 1,5 km; se exige que esa celda drene ≥ 5 km². La cuenca es el conjunto de celdas que drena a ella (D8). Se **excluye** toda cuenca cuya máscara toque el borde del modelo de terreno (el área quedaría truncada) y toda cuenca con A < 5 km².
- **Catálogo de estaciones:** `ideam_estaciones_caudal` (coordenadas, corriente, categoría limnimétrica o limnigráfica).

## 2. Validación ciega (el núcleo del protocolo)
Para predecir la estación *i*, se entrenan los modelos **sin** la estación *i* ni ninguna estación a menos de **50 km** de ella ni ninguna de la misma corriente (por nombre en el catálogo). Los caudales de *i* no intervienen en ningún parámetro. Esto es una validación cruzada espacial con zona de exclusión. Sensibilidad: sin zona de exclusión (0 km), que mide cuánto engaña la proximidad espacial.

## 3. Modelos comparados (todos en logaritmos, ajustados por mínimos cuadrados dentro de cada pliegue)
- **B0 (fórmula única):** caudal específico constante, Q̂ = q\*·A, con q\* la mediana de Q_T/A en el entrenamiento.
- **B1 (solo área):** ln Q = a + b·ln A.
- **M1 (área y lluvia):** ln Q = a + b·ln A + c·ln P.
- **M2 (área, lluvia y pendiente; nuestro método):** ln Q = a + b·ln A + c·ln P + d·ln S.
- **M3 (M2 con efectos de región natural):** M2 más una constante por región natural (Caribe, Andina, Pacífica, Orinoquía).
- **M4 (cuenca gemela):** la estación de entrenamiento más cercana en el espacio estandarizado (ln A, ln S, ln P) fuera de la zona de exclusión; Q̂ = Q_gemela · (A/A_gemela)^b, con b de B1.

## 4. Métrica y criterios
- **Error:** ε = ln(Q̂ / Q_obs). Se reporta, por T y por región natural: mediana de |ε| (factor de error típico = exp), sesgo (mediana de ε), raíz del error cuadrático medio, y fracción de estaciones dentro de un factor 2 (|ε| < ln 2).
- **Margen de error cuantificable:** cuantiles 5 %, 25 %, 50 %, 75 % y 95 % de ε en la validación ciega, que definen un intervalo de predicción multiplicativo.
- **Prueba confirmatoria (única):** a **T = 10**, la mediana de |ε| de **M2 es menor que la de B1**; IC95 % de la diferencia por remuestreo pareado de bloques espaciales (celdas de 1° × 1°) que excluya 0. Si no, se informa que la pendiente y la lluvia no mejoran sobre el área sola.
- **Secundarias (exploratorias, todas reportadas):** M2 frente a M1 (aporte de la pendiente); M3 y M4 frente a M2; cada T; cada región.
- **Ecuaciones propias:** se reportan los coeficientes del ajuste con todas las estaciones por T y por región, con IC95 % por bloques, el dominio de validez (rangos de A, S y P) y la advertencia de no extrapolar fuera de él.

## 5. Incertidumbre y sensibilidad
1. **Propagación de errores de los predictores** (Monte Carlo, 2.000 réplicas): A con error lognormal de 15 %, S de 20 % y P de 15 %. Son supuestos declarados, no errores medidos; sirven para ver cuánto del error total podrían explicar.
2. **Elasticidades** del caudal frente a cada predictor (coeficientes estandarizados).
3. **Sensibilidad metodológica:** radio de ajuste de la estación (0,75 y 3 km); registro ≥ 40 años; excluir estaciones con forma ξ fuera de [−0,5; 0,5]; objetivo Log-Pearson III en lugar de GEV; excluir cuencas de más de 2.000 km²; excluir estaciones limnimétricas (lectura visual) y quedarse con las limnigráficas; zona de exclusión de 0 y de 100 km.

## 6. Etapa B (preregistrada en esquema; se ejecuta después y con su propio protocolo)
**Restricción de datos verificada.** El almacén abierto del IDEAM (`datos.ideam.gov.co/s3-estacionesideam`) **no contiene precipitación** (solo caudal y nivel). La lluvia de las estaciones está en `datos.gov.co` (conjunto `Precipitación`, `s54a-sgyg`, desde 2017, registros subhorarios de sensores). Las consultas de agregación sobre ese conjunto no terminan en el tiempo disponible, y solo funciona la descarga fila por fila de una estación y un periodo (unos 7 s por estación-año). La corrección de sesgo por cuantiles se haría con una **muestra piloto** de pluviómetros con traslape con CHIRPS (2019-2024) y control de calidad por día, que se fijará antes de calcular ningún sesgo. Con registros tan cortos, solo es válida para lluvia diaria, no para tener un factor definitivo sobre las extremas.

## 7. Límites declarados de antemano
Máximo horario ≠ pico instantáneo. Estacionariedad supuesta. DEM de 90 m: la delineación en llanuras y en cuencas pequeñas es incierta, y ya se sabe que no ve diques ni canales. El área de cuenca de la estación no se verifica con un valor oficial (no hay uno en el catálogo): el ajuste a la red de drenaje puede equivocarse de cauce. La regionalización no incluye cuencas con regulación (embalses), trasvases ni cauces con minería. La lluvia media anual describe el clima, no la tormenta de diseño. **No sustituye el estudio hidrológico de un proyecto con ingeniero responsable.**

## Enmienda 1 (2026-11-08, antes de ajustar ningún modelo; no se ha usado ningún caudal para decidirla)
**Hallazgo técnico al probar la delineación.** (a) La función de cuenca de la librería devolvía una sola celda con su modo de ajuste por defecto en 105 de 223 estaciones: error de código, corregido usando el índice de la celda en lugar de coordenadas. (b) La regla «mayor acumulación dentro de 1,5 km» tiende a saltar a un río mayor cercano: en una estación de prueba la celda de la estación drenaba 178 km² y la regla eligió una celda de 750 km² a 1,5 km.
**Cambio.** Se calculan tres variantes de ajuste a la red: radio 1.500 m (la preregistrada), 500 m y 0 m (la celda de la estación). Para cada una se registra la diferencia entre la elevación del terreno en la celda elegida y la altitud de la estación en el catálogo del IDEAM. **Se elige para todo el análisis la variante con menor mediana de |diferencia de elevación|**, criterio que no usa caudales. Las otras dos se usan como sensibilidad. Si la mediana es parecida (diferencia menor de 5 m), se mantiene la preregistrada (1.500 m).
**Otras correcciones.** Los polígonos departamentales se validan antes de unirlos (seis departamentos fallaron por geometrías inválidas). El criterio de exclusión de cuencas que tocan el borde del modelo de terreno no cambia.
**Corrección del criterio de borde (misma enmienda, antes de ajustar ningún modelo).** Se verificó que la última fila de los modelos de terreno es NODATA, por lo que las cuencas que llegan al borde se detienen una celda antes y el chequeo «toca el borde» no las detectaba: una cuenca de unos 27.000 km² abarcaba las columnas 1 a 2.820 de 2.822. El criterio pasa a «la máscara llega a menos de 3 celdas del borde del modelo de terreno». Se vuelve a delinear todo.
