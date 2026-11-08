# Protocolo: catálogo de sismos del SGC frente al Apéndice A-4 de la NSR-10 (fijado el 2026-11-08, antes de descargar los eventos)

**Pregunta.** ¿La sismicidad instrumental registrada por el SGC se distribuye entre los municipios como lo implica el Aa del Apéndice A-4?

**Datos.** SGC `catalogo_sismos/catalogo_de_sismos_2`, capa `CATS.f25_capa_sols_pref` (solución preferida por evento; 16.290 eventos, magnitud 3,5 a 8,45, fechas hasta 2020-12-30, **incluye eventos históricos y de países vecinos**). Polígonos municipales del IGAC ya en `scripts/satelite/_cache/poligonos_nac_*.geojson`. A-4 extraído (Aa, zona por código DANE). La capa permite consultar por rangos de OBJECTID (no admite paginación).

**Selección fija:**
- Periodo **1993-2020** (la Red Sismológica Nacional opera desde 1993; antes la completitud es menor y heterogénea).
- Eventos con epicentro **dentro** de un polígono municipal continental. Los eventos costa afuera y los de países vecinos no cuentan (límite declarado).
- **Magnitud mínima primaria: M ≥ 4,0.** Sensibilidad: M ≥ 3,5 y M ≥ 4,5. Se reporta la magnitud de completitud estimada (máxima curvatura de la distribución del periodo), sin cambiar el umbral primario.
- Todas las profundidades; sensibilidad con solo ≤ 70 km.

**Medida.** Tasa = eventos por 1.000 km² por año en el municipio.

**Confirmatorios** (IC95 % por bootstrap de bloques por departamento, 2.000 réplicas):
- **C1:** ρ de Spearman(Aa, tasa) > 0 con IC que excluye 0.
- **C2:** la tasa mediana crece de zona Baja a Intermedia y a Alta (monótona), con la razón Alta/Baja y su IC.

**Descriptivo (sin criterio de decisión):**
- Municipios de zona **Baja** con tasa en el decil más alto de todo el país (sismicidad alta con Aa bajo), y municipios de zona **Alta** sin ningún evento M ≥ 4,0.
- Tasa por región natural.

**Qué NO se concluye:** que el Aa esté bien o mal. El Aa es un valor de diseño probabilista a 475 años que integra fuentes lejanas, atenuación y sismos grandes y raros que un catálogo de 28 años no contiene; la sismicidad instrumental reciente no es la base del Aa ni su sustituto. Un desacuerdo se lee como señal a revisar, no como error.

**Limitaciones de antemano:** 28 años no capturan el ciclo de los sismos grandes; la tasa de eventos pequeños depende de la densidad de la red (más estaciones, más eventos detectados, p. ej. en el Eje Cafetero y Bogotá frente a Amazonía y Orinoquía), lo que sesga a favor de zonas ya instrumentadas; los municipios grandes diluyen la tasa por área; los enjambres y réplicas inflan conteos locales (no se declusteriza); un municipio costero puede tener sismicidad relevante costa afuera que no cuenta.
