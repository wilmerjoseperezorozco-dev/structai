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
