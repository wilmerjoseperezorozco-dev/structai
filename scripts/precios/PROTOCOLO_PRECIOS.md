# Programa de análisis de precios y costos de obra: factibilidad verificada y protocolo (2026-11-07)

**Objetivo del programa (pedido del usuario):** evitar sobrecostos en licitaciones y proteger el margen de obra frente a la volatilidad de materiales (acero, cemento, agregados, asfalto): variables exógenas (TRM, combustibles, inflación, ENSO, peajes y distancias), ingeniería de características (rezagos, medias móviles, diferenciales entre regiones vecinas), proyección de costos con Monte Carlo, optimización de compras y almacenamiento, detección de precios atípicos, costos paramétricos, auditoría automática de APU, recomendador de actividades y datos sintéticos.

## 1. Lo que se verificó (hechos, no supuestos)

**Nuestra base de precios NO tiene dimensión temporal.** Todas las tablas son fotografías de un momento:
| Tabla | Filas | Contenido | Fecha |
|---|---|---|---|
| `invias_insumos_precios` | 92.820 | 663 insumos × 140 provincias | periodo único `2026-1` |
| `invias_actividad_costos` | 73.640 | 526 actividades × 140 provincias | `2026-1` |
| `invias_actividad_insumos` | 619.920 | líneas de APU (composición) | `2026-1` |
| `apu_precios_nacional_detalle` | 114.616 | 1.754 ítems × ~65 cotizaciones (78 proveedores) | carga 2026-08-20 |
| `apu_insumos_referencia` / `apu_precios_referencia` | 10.281 / 4.521 | referencias de APU | captura 2026-08-08 (casi todas) |

**Consecuencia:** con nuestra propia base **no se pueden estimar rezagos, medias móviles, volatilidad ni pronósticos de precios**; tampoco validarlos fuera de muestra. La dimensión temporal tiene que venir de series externas.

**Series externas verificadas:**
| Variable | Fuente | Estado |
|---|---|---|
| TRM | datos.gov.co `32sa-8pi3` | **8.383 datos diarios, 1991-12-02 a hoy**; descargada a `_cache/trm_historica.json` |
| Índice de costos de obras civiles (ICOCIV) | DANE (anexos mensuales .xlsx, ~19 MB cada uno) | **existe desde enero de 2021** (índice total mensual en el Anexo 1; variaciones por grupo, subgrupo e insumo básico en los Anexos 5, 9 y 11); cada anexo trae solo el mes publicado, así que hay que bajar ~70 archivos (~1,3 GB) para armar la serie por insumo |
| ICCP (antecesor) | DANE | **terminó en enero de 2022** (base dic-2020 = 100 en los últimos boletines; bases anteriores distintas, hay que empalmar) |
| Inflación (IPC) y producción/despachos de cemento | DANE | ya descargados (`scripts/macro`) |
| ENSO (ONI) | NOAA | ya descargado |
| Combustibles | datos.gov.co `x6id-4v3g` (13.574 filas, 2015) y `gjy9-tpph` (1.368 filas, 2022) | **escasos y desactualizados**: no sirven como serie mensual de ACPM/gasolina; falta una fuente (precios regulados de MinEnergía/SICOM) |
| Peajes | no se encontró un conjunto abierto en datos.gov.co | pendiente |
| Distancias logísticas | calculables entre capitales departamentales y puertos | solo aproximación en línea recta |

**Una fuente que NO se usa:** `wz5s-v2ak` (matrículas mercantiles de una cámara de comercio) trae nombres, identificaciones, correos y teléfonos de personas: **no se toca por privacidad**.

**Calidad de la base INVIAS:** los 73.640 APU (actividad × provincia) son **aritméticamente consistentes** (suma de líneas = costo directo en 100 % de los casos, componentes suman el total); 240 filas con total nulo o cero. La auditoría de coherencia aritmética no encuentra errores; los errores posibles están en los **precios unitarios y rendimientos**, no en las sumas.

**Los precios INVIAS son de referencia administrada, no cotizaciones de mercado** (ver `informe_geografia_precios.md`): casi no varían por región (índices 0,92 a 1,00) y no se asocian con la distancia a puertos ni a Bogotá (ρ ≈ 0). Una proyección de costos de mercado no se puede apoyar solo en ellos.

**Los 114.616 precios de `apu_precios_nacional_detalle`** muestran dispersión muy alta entre proveedores (CV mediano 0,96 por ítem; 4.043 marcados no válidos y 1.583 sospechosos): es el insumo natural para detectar precios atípicos, pero antes hay que entender qué mide cada ítem (presentaciones y unidades distintas inflan el CV).

## 2. Qué se puede y qué no (honesto)
| Componente | ¿Viable ahora? | Condición |
|---|---|---|
| Detección de precios atípicos | **Sí** | sobre las cotizaciones por ítem; se compara con las marcas existentes (`precio_sospechoso`) y con una revisión manual de una muestra |
| Auditoría automática de APU | **Parcial** | la aritmética ya cumple; se pueden auditar rendimientos y proporciones de insumos frente a actividades similares |
| Recomendador de actividades | **Sí, a nivel de APU** | similitud de composición (insumos compartidos) y predicción de un insumo omitido; **no** hay presupuestos de proyectos reales, así que no hay recomendación por co-ocurrencia en obras |
| Proyección de costos con Monte Carlo | **Sí, por escenarios** | la volatilidad y la transmisión (TRM, combustible, inflación) se estiman de series externas (ICOCIV 2021→, TRM, IPC) y se aplican a la composición de cada APU; **no se valida contra precios propios** porque no hay historia propia |
| Rezagos, medias móviles, diferenciales entre regiones vecinas | **Solo sobre las series externas** | los diferenciales regionales sí se pueden construir con la foto de 140 provincias, pero INVIAS casi no los tiene |
| Optimización de compras y almacenamiento | **Sí, como modelo** | inventario con precio estocástico (escenarios del Monte Carlo); es un método, no una recomendación validada |
| Costos paramétricos (p. ej. costo por km) | **No con lo que hay** | faltan proyectos con cantidades; SECOP trae valor y plazo, no cantidades |
| Datos sintéticos | **Sí, con límites** | solo para entrenar y probar detectores y recomendadores; evaluación TSTR (entrenar en sintético, probar en real); **nunca** se escriben en las tablas de precios ni se usan para cotizar |

## 3. Orden de ejecución propuesto (cada paso con su regla fijada antes de correr)
1. **P1 — precios atípicos** sobre `apu_precios_nacional_detalle`.
2. **P2 — recomendador de APU** y auditoría de rendimientos sobre `invias_actividad_insumos` (validación dejando un insumo fuera).
3. **P3 — serie de costos externa:** descargar los ~70 anexos ICOCIV (con ritmo moderado), armar el índice por grupo e insumo, empalmar con el ICCP si se obtiene, y estimar la transmisión TRM / combustible / IPC / ENSO con rezagos y validación fuera de muestra.
4. **P4 — Monte Carlo de costo en riesgo** de un presupuesto de ejemplo (APU × cantidades) con escenarios de P3.
5. **P5 — optimización de compras** bajo esos escenarios (caso didáctico, rotulado como método).
6. **P6 — datos sintéticos** con TSTR, solo para P1 y P2.

## 4. Riesgos a tener presentes
Sin historia propia no hay validación temporal de nada que toque precios de la base; la transmisión estimada con ICOCIV (≈ 70 meses) es corta y cubre un periodo atípico (2021-2022); los precios de referencia no son de mercado; un modelo de «proyección de costos» no sustituye el análisis de un presupuestador ni una cotización; los datos sintéticos pueden reproducir sesgos de los reales y nunca deben presentarse como precios.

---
# P1 y P2 — reglas fijadas ANTES de correr (2026-11-07)

## P1 — Precios atípicos en `apu_precios_nacional_detalle` (catálogo IAD MIPYMES de Colombia Compra Eficiente)
**Qué son los datos (verificado):** cotizaciones sin IVA de 78 proveedores mipyme a 1.754 ítems estandarizados (1.472 en «und»); casi todos los proveedores cotizan casi todos los ítems (mediana 1.754). Un valor extremo suele ser un error de digitación del proveedor, no un precio de mercado. **No se publican nombres de proveedores** (hay personas naturales): solo identificadores anónimos y conteos.
- **Excluidas del análisis:** las 4.043 cotizaciones ya marcadas no válidas (nulas o ≤ 0). Ítems con < 20 cotizaciones válidas.
- **Detector A (primario):** z robusto del logaritmo del precio dentro de cada ítem, z = (ln p − mediana)/(1,4826·MAD); atípica si |z| > 3,5. Si MAD = 0, se usa el rango intercuartílico.
- **Detector B (secundario):** cercas extremas del logaritmo: fuera de [Q1 − 3·RIC, Q3 + 3·RIC].
- **Error de unidad o de decimal (descriptivo):** una cotización atípica cuya razón con la mediana del ítem es cercana a una potencia de diez (|log10(razón) − k| < 0,05 con k ∈ {±1, ±2, ±3}).
- **Efecto proveedor:** descomposición ln p = efecto ítem + efecto proveedor + residuo (mínimos cuadrados alternados); se reporta qué parte de la varianza explica el proveedor y cuántos proveedores muestran un sesgo sistemático (mediana de z con |mediana| > 1).
- **Evaluación (no hay verdad de referencia):** (i) fracción marcada por A y por B; (ii) concordancia con la marca existente `precio_sospechoso` (precisión, sensibilidad, κ de Cohen); (iii) fracción de las marcadas cercana a potencias de diez; (iv) revisión descriptiva de una muestra aleatoria de 30 cotizaciones marcadas por A y no por la marca existente (ítem, unidad, precio, mediana), **sin presentarla como validación**.
- **Límite:** un precio atípico en este catálogo no es necesariamente erróneo (presentaciones, marcas, ubicación); y la marca existente tampoco es una verdad de referencia.

## P2 — Recomendador de APU y auditoría de rendimientos (`invias_actividad_insumos`, 2026-1)
**Datos:** composición de las 526 actividades (insumos, cantidad o rendimiento, valor de la línea) para **una provincia de referencia** (la que tenga las 526 actividades; la composición es la misma entre provincias y varían los precios).
- **P2a — Recomendar el insumo que falta:** para cada actividad con ≥ 4 insumos se oculta un insumo al azar (semilla fija, 5 repeticiones) y se pide el ranking de insumos a partir de los restantes. Modelos: (1) **popularidad** (insumos más frecuentes), (2) **co-ocurrencia** (PMI entre insumos), (3) **vecinos** (similitud coseno TF-IDF entre actividades y votación de los k = 10 más parecidos). Métricas: **acierto@5, acierto@10 y MRR**, con IC95 % por bootstrap de bloques por capítulo del numeral. **Criterio:** el modelo de vecinos supera a la popularidad en acierto@10 con IC de la diferencia que excluye 0.
- **P2b — Auditoría de proporciones por inyección de errores:** detector = z robusto de la participación de cada línea en el costo frente a la participación del mismo insumo en las 10 actividades más parecidas. Evaluación **por inyección** (no hay errores reales etiquetados): se corrompe una línea de actividades elegidas al azar (cantidad ×10, ×0,1 o eliminación de la línea de mayor participación) y se mide la **sensibilidad con una tasa de falsos positivos fija de 5 %** sobre las líneas sin tocar. **Criterio:** sensibilidad ≥ 0,5 para ×10 y ×0,1 con IC que excluya 0,2.
- **Límites:** las actividades de INVIAS son de obra vial y cubren solo una parte de la construcción; la composición es de referencia; la inyección de errores mide cuánto detecta el método errores *sintéticos*, no los reales; no hay presupuestos de proyectos, así que no se evalúa recomendación por co-ocurrencia en obras.

---

# P3 y P4 — transmisión y Monte Carlo del costo: reglas fijadas ANTES de correr (2026-11-07)

**Datos.** ICOCIV (DANE, anexo de septiembre de 2026, base diciembre 2020 = 100): índice total (Anexo 1) y por grupo de obra (Anexo 16), mensual de 2021-01 a 2026-09 (69 meses); grupos «Carreteras, calles y vías» (530201) y «Tuberías…» (530203). Series externas mensuales: TRM (media del mes), IPC (índice), WTI en USD (FRED, aproximación del petróleo; no es el precio del asfalto) y ONI. Todas se transforman en variación logarítmica mensual (el ONI queda en nivel).

**Límite de complejidad (por tener 69 puntos).** Un regresor externo a la vez, a lo sumo 6 rezagos, errores HAC (Newey-West, 6 rezagos). No se ajustan modelos con varios regresores ni más de 2 parámetros por serie.

**P3 — transmisión.**
1. *Descriptivo.* Media, desviación y autocorrelación (rezagos 1-6) de las variaciones mensuales; comparación del subperiodo 2021-2022 con 2023-2026.
2. *Confirmatorio (familia de 2, Holm).* Proyecciones locales: respuesta acumulada de ln ICOCIV-carreteras entre t−1 y t+h a una variación logarítmica de (a) TRM y (b) WTI en t, controlando por la variación rezagada del propio índice, h = 0…6. Se prueba h = 6; signo esperado positivo. Se reporta además la potencia: el efecto mínimo detectable al 80 %.
3. *Exploratorio (sin ajuste, rotulado).* IPC y ONI; y la interacción «subperiodo 2021-2022 × choque de TRM» (¿la transmisión depende del régimen inflacionario?).

**P4 — Monte Carlo del costo.** Generador: bootstrap por bloques de 3 meses de las variaciones mensuales de ICOCIV-carreteras (conserva autocorrelación), en dos variantes: muestra completa y solo 2023-2026. Salida: multiplicador de costo a 6 y 12 meses (P5, P50, P95), y el «costo en riesgo» (P95 − mediana) como porcentaje del presupuesto.
- *Validación fuera de muestra* con origen móvil (orígenes desde el mes 30): cobertura empírica del intervalo nominal 80 % a 6 meses. Criterio: cobertura en [0,65; 0,95]; fuera de ese rango, «intervalos no calibrados». Se informa el tamaño efectivo de muestra (las ventanas se solapan) y no se afirma más allá.
- *Referencia:* el generador se compara con el supuesto ingenuo de crecimiento constante.
- *Cota (no estimación):* si el cemento asfáltico (≈ un tercio del costo por m² del ítem 4) se moviera uno a uno con WTI × TRM, se reporta el multiplicador resultante como cota superior.

**No se concluye:** un pronóstico de precios, ni una elasticidad estructural. Con 69 meses y un periodo atípico, cualquier transmisión se presenta como asociación de corto plazo.
