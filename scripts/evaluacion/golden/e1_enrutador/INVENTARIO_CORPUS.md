# Inventario de normas y datos de StructAI (issue #170)

Generado por `inventario_corpus.py` (solo lectura, conteos exactos). La pertenencia a dominios sale de `FUENTES_DOMINIO`; todo lo de `nsr10_chunks` y `ntc_chunks` es además de `normativa_general`.

## Totales del corpus RAG

| Tabla | Chunks |
|---|---|
| `nsr10_chunks` | 10909 |
| `ntc_chunks` | 294 |
| `motor_chunks` | 4060 |
| `peru_e030_chunks` | 204 |
| `ecuador_nec_se_ds_chunks` | 395 |

## Chunks disponibles por dominio (un chunk compartido cuenta en cada dominio)

| Dominio | Chunks |
|---|---|
| `normativa_general` | 11203 |
| `vias` | 2816 |
| `geopot` | 2157 |
| `gerencia` | 818 |
| `vulnerabilidad_vivienda` | 426 |
| `ecuador_nec_se_ds` | 395 |
| `aquai` | 333 |
| `peru_e030` | 204 |

## Matriz norma → dominios

| Tabla | Norma / unidad | Chunks | Dominio primario | Otros dominios | Parcial |
|---|---|---|---|---|---|
| ecuador_nec_se_ds_chunks | ecuador_nec_se_ds_chunks | 395 | `ecuador_nec_se_ds` |  |  |
| motor_chunks | [vias] Normas de Ensayo — Sección 200 (Agregados Pétreos) | 1145 | `geopot` | vias (1145) |  |
| motor_chunks | [vias] CCP-14 — Norma Colombiana de Diseño de Puentes (INVIAS / AASHTO LRFD) | 1096 | `vias` |  |  |
| motor_chunks | [aquai] Resolución 0330 de 2017 | 287 | `aquai` |  |  |
| motor_chunks | [gerencia] Ley 80 de 1993 | 223 | `gerencia` |  |  |
| motor_chunks | [gerencia] Manual de Interventoría y Supervisión de Obra Pública — Capítulo 2 (Resolución  | 174 | `gerencia` |  |  |
| motor_chunks | [gerencia] Ley 1474 de 2011 | 163 | `gerencia` |  |  |
| motor_chunks | [gerencia] Manual de Interventoría de Obra Pública 2022 (INVIAS, MEPI-MN1 v1) | 154 | `gerencia` |  |  |
| motor_chunks | [vias] Manual de Túneles de Carretera para Colombia (Edición 2021, INVIAS) | 143 | `vias` |  |  |
| motor_chunks | [vias] CCP-14 — Norma Colombiana de Diseño de Puentes (INVIAS / AASHTO LRFD) [⚠ extracción | 124 | `vias` |  |  |
| motor_chunks | [geopot] Guía POT — Ministerio de Vivienda, Ciudad y Territorio (2024) | 89 | `geopot` |  |  |
| motor_chunks | [gerencia] Ley 1150 de 2007 | 71 | `gerencia` |  |  |
| motor_chunks | [vias] Manual de Pavimentos INVIAS — bajos_volumenes | 69 | `vias` |  |  |
| motor_chunks | [vias] Normas de Ensayo — Sección 300 (Cemento) | 63 | `geopot` | vias (63) |  |
| motor_chunks | [vias] Manual de Pavimentos INVIAS — concreto | 57 | `vias` |  |  |
| motor_chunks | [vias] Manual de Pavimentos INVIAS — asfaltico | 42 | `vias` |  |  |
| motor_chunks | [vias] INV E-826-22 | 38 | `vias` |  |  |
| motor_chunks | [vias] INV E-632-22 | 14 | `vias` |  |  |
| motor_chunks | [aquai] Resolución CRA 956 de 2021 | 14 | `aquai` |  |  |
| motor_chunks | [aquai] NTC 1500 (ficha técnica — no es el texto normativo completo) | 13 | `aquai` |  |  |
| motor_chunks | [gerencia] ISO 9001:2015 (ficha técnica — no es el texto normativo completo, protegido por | 11 | `gerencia` |  |  |
| motor_chunks | [vias] INV E-631-22 | 10 | `vias` |  |  |
| motor_chunks | [geopot] Fuentes de información secundaria para el ordenamiento territorial — MVCT (sept.  | 5 | `geopot` |  |  |
| motor_chunks | [aquai] Resolución CRA 955 de 2021 | 5 | `aquai` |  |  |
| motor_chunks | [gerencia] NTC-ISO 31000:2018 (ficha técnica — no es el texto normativo completo, protegid | 4 | `gerencia` |  |  |
| motor_chunks | [gerencia] ISO 19011:2011 (ficha técnica — no es el texto normativo completo, protegido po | 4 | `gerencia` |  |  |
| motor_chunks | [gerencia] PMI/PMBOK — Earned Value Management (EVM) | 3 | `gerencia` |  |  |
| motor_chunks | [gerencia] ISO/IEC 27001:2022 (ficha técnica — no es el texto normativo completo, protegid | 3 | `gerencia` |  |  |
| motor_chunks | [gerencia] ISO 14001:2015 (ficha técnica — no es el texto normativo completo, protegido po | 3 | `gerencia` |  |  |
| motor_chunks | [geopot] ASTM D2487 — Sistema Unificado de Clasificación de Suelos (USCS) | 1 | `geopot` |  |  |
| motor_chunks | [geopot] ASTM D2487 (USCS) · AASHTO M145 | 1 | `geopot` |  |  |
| motor_chunks | [geopot] INV E-125 (Límite Líquido) / INV E-126 (Límite Plástico) | 1 | `geopot` |  |  |
| motor_chunks | [geopot] INV E-141 (Proctor Estándar) / INV E-142 (Proctor Modificado) | 1 | `geopot` |  |  |
| motor_chunks | [geopot] INV E-148 — California Bearing Ratio (CBR) | 1 | `geopot` |  |  |
| motor_chunks | [geopot] INV E-123 (granulometría suelos) / NTC 77 (agregados) | 1 | `geopot` |  |  |
| motor_chunks | [geopot] NTC 673 (compresión de cilindros) / NTC 396 (asentamiento — cono de Abrams) | 1 | `geopot` |  |  |
| motor_chunks | [geopot] NSR-10 (Título C) / ACI 318 — Conformidad de resistencia del concreto | 1 | `geopot` |  |  |
| motor_chunks | [geopot] NTC 174 (requisitos generales) / NTC 237 (densidad y absorción) / NTC 218 (desgas | 1 | `geopot` |  |  |
| motor_chunks | [geopot] NTC 174 (requisitos) / NTC 237 (densidad SSS por picnómetro, ASTM C128) / NTC 77  | 1 | `geopot` |  |  |
| motor_chunks | [geopot] ACI 211.1 — Diseño básico de proporciones de concreto (aplicación simplificada) | 1 | `geopot` |  |  |
| motor_chunks | [geopot] NSR-10 (Título A) — Movimientos sísmicos de diseño, zonificación por municipio/de | 1 | `geopot` |  |  |
| motor_chunks | [vias] Manual de Diseño Geométrico de Carreteras INVIAS 2008 — Capítulo 3, Tabla 3.2 | 1 | `vias` |  |  |
| motor_chunks | [vias] Manual INVIAS 2008 Cap. 3 (Tablas 3.4-3.5), Cap. 4 (Tabla 4.1), Cap. 5 — con bombeo | 1 | `vias` |  |  |
| motor_chunks | [vias] Método mecánico-empírico, ábacos AASHTO 93 adaptados (Manual INVIAS) | 1 | `vias` |  |  |
| motor_chunks | [vias] Método mecánico-empírico AASHTO 93 adaptado — estructura flexible | 1 | `vias` |  |  |
| motor_chunks | [vias] Método mecánico-empírico AASHTO 93 adaptado — estructura rígida | 1 | `vias` |  |  |
| motor_chunks | [vias] Manual de Mantenimiento de Carreteras INVIAS (2016), adoptado por Resolución 04046  | 1 | `vias` |  |  |
| motor_chunks | [vias] Manual de Mantenimiento de Carreteras INVIAS (2016), Resolución 04046 de 2018 | 1 | `vias` |  |  |
| motor_chunks | [vias] Guía de estandarización INVIAS 2023 / IDU / IGAC · NTC 6271 | 1 | `vias` |  |  |
| motor_chunks | [vias] NTC 2017 (tercera actualización, 2018) — INVIAS Art. 510 | 1 | `vias` |  |  |
| motor_chunks | [vias] NTC 4342 — Geotextiles en pavimentos asfálticos, equivalente INVIAS D6140 | 1 | `vias` |  |  |
| motor_chunks | [vias] NTC 121 (especificación de desempeño, 2021) / NTC 1362 (cemento blanco, incluida en | 1 | `vias` |  |  |
| motor_chunks | [vias] NTC 1299 (IDT ASTM C494/C494M-05a) / NTC 3502 (equivalente ASTM C260) | 1 | `vias` |  |  |
| motor_chunks | [vias] NTC 3459 (ed. 2001) | 1 | `vias` |  |  |
| motor_chunks | [gerencia] Extensión predictiva sobre EVM (PMI/PMBOK) — modelo de riesgo | 1 | `gerencia` |  |  |
| motor_chunks | [vias] NTC 3493 (equivalente ASTM C618) / NTC 4018 (primera actualización 2017, equivalent | 1 | `vias` |  |  |
| motor_chunks | [vias] NTC 4024 (muestreo y ensayo, 2001) / NTC 4924 (equivalente ASTM C331, 2001) | 1 | `vias` |  |  |
| motor_chunks | [gerencia] PMI/PMBOK — Earned Value Management (EVM), extensión de portafolio | 1 | `gerencia` |  |  |
| motor_chunks | [gerencia] Estadística aplicada a series de tiempo de KPIs de proyecto (sin dependencias e | 1 | `gerencia` |  |  |
| motor_chunks | [gerencia] Extensión predictiva sobre EVM (PMI/PMBOK) — proyección de cronograma | 1 | `gerencia` |  |  |
| motor_chunks | [gerencia] Extensión predictiva sobre EVM (PMI/PMBOK) — forecasting y análisis de correlac | 1 | `gerencia` |  |  |
| motor_chunks | [aquai] Ley 142/1994 Art. 85 + Res. CRA 884/2019 Art. 4, aplicado en Res. UAE-CRA 350/2022 | 1 | `aquai` |  |  |
| nsr10_chunks | NSR-10 Título F | 2728 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título C | 2559 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título A | 1587 | `normativa_general` | vulnerabilidad_vivienda (145), geopot (235) | sí |
| nsr10_chunks | NSR-10 Título G | 1193 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título D | 719 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título H | 552 | `geopot` | normativa_general (552) |  |
| nsr10_chunks | NSR-10 Título K | 433 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título B | 315 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título J | 288 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título E | 177 | `vulnerabilidad_vivienda` | normativa_general (177) |  |
| nsr10_chunks | RES0312 | 76 | `normativa_general` |  |  |
| nsr10_chunks | NSR-10 Título I | 62 | `normativa_general` |  |  |
| nsr10_chunks | AIS2004 | 55 | `vulnerabilidad_vivienda` | normativa_general (55) |  |
| nsr10_chunks | NSR10 | 50 | `normativa_general` |  |  |
| nsr10_chunks | RES4272 | 47 | `normativa_general` |  |  |
| nsr10_chunks | BUILDCHANGE | 27 | `vulnerabilidad_vivienda` | normativa_general (27) |  |
| nsr10_chunks | AIS410 | 22 | `vulnerabilidad_vivienda` | normativa_general (22) |  |
| nsr10_chunks | NSR-10 Alcance | 11 | `normativa_general` |  |  |
| nsr10_chunks | RES5018 | 8 | `normativa_general` |  |  |
| ntc_chunks | Decreto 1072 de 2015 | 59 | `normativa_general` |  |  |
| ntc_chunks | ACI 318-05 (ficha técnica curada -- Cap. 11 y 21, no es el texto completo verbatim) | 17 | `normativa_general` |  |  |
| ntc_chunks | NTC 2289 | 14 | `normativa_general` |  |  |
| ntc_chunks | NTC 1500 | 13 | `aquai` | normativa_general (13) |  |
| ntc_chunks | NTC 121 | 13 | `geopot` | normativa_general (13) |  |
| ntc_chunks | NTC 30 | 13 | `normativa_general` |  |  |
| ntc_chunks | NTC 4026 | 13 | `normativa_general` |  |  |
| ntc_chunks | NTC 396 | 12 | `geopot` | normativa_general (12) |  |
| ntc_chunks | NTC 4076 | 12 | `normativa_general` |  |  |
| ntc_chunks | NTC 454 | 12 | `geopot` | normativa_general (12) |  |
| ntc_chunks | NTC 1032 | 11 | `normativa_general` |  |  |
| ntc_chunks | NTC 174 | 11 | `geopot` | normativa_general (11) |  |
| ntc_chunks | NTC 3459 | 10 | `normativa_general` |  |  |
| ntc_chunks | NTC 4595 | 10 | `normativa_general` |  |  |
| ntc_chunks | NTC 504 | 10 | `normativa_general` |  |  |
| ntc_chunks | NTC 1028 | 9 | `normativa_general` |  |  |
| ntc_chunks | NTC 4027 | 9 | `normativa_general` |  |  |
| ntc_chunks | Ley 1562 de 2012 | 8 | `normativa_general` |  |  |
| ntc_chunks | NTC 1328 | 8 | `normativa_general` |  |  |
| ntc_chunks | NTC 673 | 8 | `geopot` | normativa_general (8) |  |
| ntc_chunks | SGSST | 7 | `normativa_general` |  |  |
| ntc_chunks | AISC 360-2010 (ficha técnica curada -- Cap. A y arranque de B, no es el texto completo ver | 6 | `normativa_general` |  |  |
| ntc_chunks | NTC 2516 | 3 | `normativa_general` |  |  |
| ntc_chunks | NSR-10 Título C — Concreto Estructural | 2 | `normativa_general` |  |  |
| ntc_chunks | NSR-10 — Elementos No Estructurales (resumen técnico, no verbatim — probablemente Título A | 2 | `normativa_general` |  |  |
| ntc_chunks | APU — Conceptos Generales | 1 | `normativa_general` |  |  |
| ntc_chunks | NSR-10 Título D — Mampostería Estructural | 1 | `normativa_general` |  |  |
| peru_e030_chunks | peru_e030_chunks | 204 | `peru_e030` |  |  |

## Datos estructurados (ramas propias del código)

| Tabla | Filas | Dominio que la usa | Dónde se lee |
|---|---|---|---|
| `apu_precios_referencia` | 4566 | apu_precios | buscar_precios_apu |
| `apu_insumos_referencia` | 10281 | apu_precios | buscar_precios_apu |
| `apu_items_nacional` | 1754 | apu_precios | precios nacionales MiPymes |
| `apu_precios_nacional_detalle` | 114616 | apu_precios | precios nacionales MiPymes |
| `invias_actividades` | 526 | apu_precios+vias | buscar_precios_invias_vias |
| `invias_insumos_precios` | 92820 | apu_precios+vias | buscar_precios_invias_vias |
| `invias_provincias` | 140 | apu_precios+vias | buscar_precios_invias_vias |
| `sgc_amenaza_sismica_municipios` | 1121 | geopot+aquai+vivienda+NG | sgc_amenaza_sismica |
| `nsr10_apendice_a4_municipios` | 1117 | geopot | Apéndice A-4 municipal |
| `microzonificacion_sismica_local` | 36 | geopot | microzonificacion_local |
| `igac_suelos_ufh` | 169088 | geopot | igac_client |
| `ideam_estaciones_caudal` | 3099 | aquai | ideam_client |
| `ideam_caudal_historico` | 352022 | aquai | ideam_client |
| `ideam_caudal_estadisticas_mes` | 11310 | aquai | ideam_client |
| `sisben_vulnerabilidad_vivienda_municipio` | 1099 | vulnerabilidad_vivienda | _bloque_vulnerabilidad_vivienda |
| `ungrd_emergencias` | 41893 | geopot+NG | informe de sitio |
| `peru_e030_zonificacion_distrital` | 1884 | peru_e030 | pais_zonificacion |
| `ecuador_nec_se_ds_zonificacion_poblacion` | 512 | ecuador_nec_se_ds | pais_zonificacion |
| `normas_registro` | 69 | todos (vigencia) | metadata de búsqueda |
| `normas_modificaciones` | 28 | todos (vigencia) | vigilancia normativa |
| `normas_referencias_cruzadas` | 1354 | todos | referencias cruzadas |
| `noticias_relevantes` | 9786 | NG (actualidad) | _bloque_contexto_noticias |
