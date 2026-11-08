# Inventario de datos abiertos de Colombia para ingeniería civil (2026-11-08)

**Alcance y límite.** Se consultó el catálogo público de datos.gov.co (Discovery API, solo lectura, 10 temas, 280 resultados; `scripts/inventario/catalogo_datos_gov.py` → `catalogo_datos_gov.json`). Lo verificado es que el conjunto **existe, quién lo publica, su fecha de actualización y sus columnas**. **No** se ha verificado la calidad del contenido, la cobertura ni la licencia de redistribución: eso es el paso siguiente por cada conjunto, antes de usarlo en un análisis. Los portales propios (SGC, IGAC, DANE, IDEAM GIS) no están en este catálogo y están marcados «por probar».

## 1. Lo que ya usamos
IDEAM almacén S3 (caudales), `s54a-sgyg` (lluvia 10 min), `hp9r-jxuu` (estaciones), UNGRD 2019-2024, Copernicus DEM, OSM, CHIRPS v3, ESA WorldCover, NBI/DANE, SECOP obras, ANM volúmenes, INVIAS precios, XM.

## 2. Candidatos nuevos (existen en el catálogo; contenido sin verificar)
| Id | Conjunto | Publica | Actualizado |
|---|---|---|---|
| `nsz2-kzcq` | Normales climatológicas | IDEAM | 2026-10 |
| `sbwg-7ju4`, `ccvq-rp9s`, `afdg-3zpb` | Temperatura del aire (media, máx., mín.) | IDEAM | 2026-11 |
| `bdmn-sqnh`, `vfth-yucv`, `pt9a-aamx` | Nivel instantáneo, máximo y mínimo de ríos | IDEAM | 2026-11 |
| `57sv-p2fu` | Estaciones IDEAM y de terceros | IDEAM | 2026-11 |
| `avya-p282`, `kfsz-ija2` | Lluvia, caudal y nivel; catálogo de estaciones | CVC | 2025-05 |
| `wry7-svws`, `xgsu-v9xq` | Estado de POMCA; POMCA Sogamoso | MinAmbiente / CAR | 2020-2023 |
| `ie7y-asdn`, `68qj-5xux` | Red vial; peajes | INVIAS | 2026-10 |
| `8yi9-t44c`, `qac6-9mkr` | Tráfico vehicular; recaudo | ANI | 2026-09 |
| `hq2v-5umk`, `ab8a-uwf7` | Sisbén personas y hogares (2022) | DNP | 2022-06 |
| `8dar-v8rj` | Censo 2018 por centro poblado, hogares y viviendas (Magdalena) | Gobernación | 2020 |
| `7fsy-xzzb` | Licencias de construcción Fusagasugá | Alcaldía | 2023 |
| `cb9c-h8sn`, `jbjy-vk9h` | SECOP II adiciones; contratos | ANCP | 2026-11 |
| `42ha-fhvj`, `si2v-pbq5` | RUCOM explotadores; títulos mineros | ANM | 2025-2026 |
| `nxt2-39c3` | Calidad del agua para consumo humano | INS | 2026-11 |
| `v3tn-7h59` | Encuesta a entidades sobre el terremoto | MinTIC | 2026-09 |
| `a4bc-a9tq`, `xsag-hp7j` | Eventos y emergencias (Santander, Boyacá) | Gobernaciones | 2023-2026 |

**Hueco confirmado:** el catálogo no devolvió catálogo sísmico, acelerógrafos, geotecnia ni microzonificación (solo 4 resultados, ninguno del SGC), ni un índice nacional de costos de construcción ni series de precios de insumos. Esos viven en portales propios (SGC, DANE) y hay que probarlos aparte.

## 3. Preguntas de uso: «con X datos, para sacar Y»
Cada fila es una hipótesis candidata, no un hallazgo. Se preregistra antes de analizar.

| # | Datos que se cruzan | Qué se podría sacar | Riesgo principal |
|---|---|---|---|
| 1 | Normales climatológicas + lluvia 10 min + CHIRPS | Validar la lluvia media anual de la regionalización con una fuente independiente de CHIRPS | Normales de periodos distintos |
| 2 | Nivel instantáneo/máx./mín. IDEAM + lluvia 10 min | Tiempo de respuesta (rezago) lluvia → creciente por cuenca, útil para alertas | Sensores recientes, series cortas |
| 3 | Tráfico ANI + red vial INVIAS + peajes | Carga de tráfico por tramo como insumo de diseño de pavimentos | Cobertura solo en vías concesionadas |
| 4 | SECOP adiciones + contratos de obra + UNGRD | Sobrecostos y atrasos de obra según exposición a emergencias | Los datos de contratos tienen errores de captura |
| 5 | Sisbén hogares + censo 2018 + HAND/inundación | Hogares expuestos a inundación por municipio para focalizar recursos | **Datos personales**: usar solo agregados; sin acceso a identidades |
| 6 | Licencias de construcción + zona de amenaza | Si se construye más en zonas de amenaza (fallas del ordenamiento) | Solo hay licencias de pocos municipios |
| 7 | RUCOM + títulos mineros + canteras ANM | Oferta formal de agregados por región frente a la demanda de obra | Extracción ilegal no aparece |
| 8 | Calidad del agua INS + UNGRD inundaciones | Si el agua empeora después de inundaciones (infraestructura sanitaria) | Muestreo irregular |
| 9 | Temperatura IDEAM + CHIRPS | Evapotranspiración y balance hídrico para humedad antecedente del suelo | Cobertura de estaciones |
| 10 | Encuesta MinTIC terremoto + UNGRD | Qué capacidad de respuesta tienen las entidades | Contenido y licencia por revisar |

## 4. Orden de verificación propuesto
1. **Primero** los de mayor valor y menor riesgo: 1, 2, 9 (todo IDEAM, mismo formato que ya manejamos).
2. **Segundo** 3, 4, 7 (datos de entidades de infraestructura y contratación).
3. **Con revisión previa de privacidad:** 5 (Sisbén).
4. **Por probar fuera de datos.gov.co:** SGC (sismos, microzonificación, RNAC por solicitud), DANE (índice de costos de construcción), IGAC (cartografía y catastro), ESA CCI (humedad del suelo, con permiso para descargar).

## 5. Reglas de uso
Para cada conjunto: registrar tamaño, periodo, campos, licencia y problemas de calidad **antes** de analizarlo; no publicar datos personales; no redistribuir sin revisar la licencia; documentar los fallos conocidos como en `RESULTADOS_*`.

## 6. Servicios ArcGIS públicos del SGC y fuentes externas verificadas (2026-11-08)

**Inventario del SGC** (`srvags.sgc.gov.co/arcgis/rest/services`; script `scripts/ingesta/sgc_amenaza_sismica/inventario_servicios_arcgis.py`, salida completa en `sgc_inventario_servicios.json`): 126 servicios MapServer/FeatureServer en unas 55 carpetas, 3.020 capas, una sola con error (`Mapa_Metalogenico_Colombia_2002`). Se omitieron las carpetas marcadas como privadas o de sistema. Muchos servicios repiten las mismas capas (por ejemplo, el drenaje de 445.717 elementos aparece en varios), así que el total de ~4 millones de registros **sobreestima** lo distinto. Solo lectura, sin geometrías.

Capas que ya usamos: amenaza sísmica por municipio (`Municipios_Amenaza_NR10`) y mapa nacional de amenaza por movimientos en masa 1:100.000 (`Mapa_Nacional_Amenaza_Mov_Masa_100K`). Auditoría del A-4 contra la primera: `scripts/ingesta/nsr10/RESULTADOS_AUDITORIA_A4_VS_SGC.md`. Contraste de la segunda con eventos UNGRD: `scripts/satelite/RESULTADOS_SGC_VS_UNGRD.md`.

Capas aún sin explorar, con conteo de registros del inventario (no verificadas en contenido ni licencia):
| Capa | Registros | Posible uso |
|---|---:|---|
| `catalogo_sismos/catalogo_de_sismos_2` (CATS) | 16.290 | Catálogo sísmico para recurrencia y sismicidad local |
| `sismicidad_historica_*` (efectos, intensidades) | 6.449 efectos; 3.405 intensidades | Efectos históricos por municipio |
| `Mapa_Intensidad_Maxima_Observada_Colombia` | 1.123 municipios | Contraste con Aa/Av del A-4 |
| `Zonificacion_Sismica_Intensidad_Esperada` | 1.122 municipios | Contraste con la amenaza sísmica del reglamento |
| `SIMMA/ZonificacionAmenazaCache` | 5.501 (25K), 890 (100K) | Amenaza por movimientos en masa a mayor detalle |
| `SIMMA/ZonificacionSusceptibilidadCache` | 1.205 (100K) | Susceptibilidad a movimientos en masa |
| `Zonificacion_Amenazas_Mov_Masa` (zonificación tipo Cardique) | 23 capas, 15.261 | Zonificación local de detalle |
| `Geomorfodinamica` | 713 puntos | Dinámica geomorfológica |
| `Amenaza_Volcanica` | 40 volcanes, 47 capas | Amenaza volcánica |

**ESA CCI humedad del suelo** (v09.2, CEDA): ver `scripts/satelite/RESULTADOS_ESA_CCI_COBERTURA.md`. Sin dato en los Andes altos, el Chocó y la Amazonía; útil en el Caribe. Descarga 2019-2024 en `scripts/satelite/_cache/esa_cci_sm/` (no versionada).
