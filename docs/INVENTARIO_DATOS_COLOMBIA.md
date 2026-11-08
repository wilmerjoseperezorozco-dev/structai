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
