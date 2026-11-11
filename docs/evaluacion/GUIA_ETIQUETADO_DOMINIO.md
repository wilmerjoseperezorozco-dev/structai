# Guía de etiquetado de dominio (enrutador de StructAI)

Para quien etiquete preguntas con `aprendizaje_activo.py` o escriba el set held-out del issue #169.

E1e mostró que las etiquetas inconsistentes dañan el modelo tanto como las etiquetas de otra distribución. Por ejemplo, el pool de NSR-10 tenía las preguntas del Título A como `normativa_general`, mientras el test tenía Aa/Av como `geopot`. Esta guía fija una sola política.

## Dos campos

- **`etiqueta`**: el dominio que da la **mejor** respuesta hoy, el que tiene la fuente o el motor especializado (ver `FUENTES_DOMINIO` en `rag_multi_norma.py`).
- **`aceptables`**: otros dominios que también darían una respuesta correcta, separados por coma. `normativa_general` suele ser aceptable para casi todo lo que es NSR-10.

## Dominios y su alcance real

| Dominio | Etiquetar aquí cuando la pregunta trata de… |
|---|---|
| `geopot` | Amenaza sísmica de un **lugar** (Aa, Av, zona, PGA, microzonificación); geotecnia (NSR-10 Título H: capacidad portante, licuación, asentamientos, estudios de suelos); **ensayos de laboratorio** de suelos, concreto, agregados y cemento (Atterberg, Proctor, CBR, slump, cilindros, Los Ángeles, normas INV E-200/300, NTC 174/396/673); POT y estudios de amenaza municipal |
| `vulnerabilidad_vivienda` | Evaluar una **vivienda existente** de mampostería de 1-2 pisos (¿mi casa resiste?, grietas, muros sin columnas, checklist AIS, reforzamiento de vivienda) |
| `aquai` | Acueducto, alcantarillado, aguas lluvias, dotación, Res. 0330, RAS, tarifas CRA |
| `vias` | Diseño geométrico, pavimentos, mantenimiento vial, **puentes (CCP-14)**, túneles |
| `gerencia` | Valor ganado (CPI, SPI, EAC), cronograma y riesgo de proyecto, **contratación pública** (Ley 80, 1150, 1474), interventoría, ISO 9001/14001/31000 |
| `apu_precios` | Precio, costo, presupuesto o APU de un material o actividad |
| `peru_e030` / `ecuador_nec_se_ds` | Solo si se nombra el país, una ciudad de ese país o la norma |
| `normativa_general` | Diseño estructural NSR-10 (cargas, cortante basal, R0, deriva, coeficiente de importancia, concreto, acero, madera, mampostería **de diseño**), NTC de producto, SG-SST, saludos y preguntas fuera de alcance |

## Reglas de desempate

1. **Lugar + sísmica → `geopot`** (aceptable `normativa_general`). Sísmica **sin** lugar y de diseño estructural → `normativa_general` (aceptable `geopot` si es del espectro o de la zonificación).
2. **Casa existente → `vulnerabilidad_vivienda`.** Diseño de una casa nueva por el Título E → `normativa_general` (aceptable `vulnerabilidad_vivienda`).
3. **Negación: se etiqueta lo que se pregunta, nunca lo negado.** "No necesito el precio, sino la norma del recubrimiento" → `normativa_general`.
4. **Pregunta compuesta** (precio + norma, dos dominios a la vez): `etiqueta` = la parte principal, el otro dominio en `aceptables`, y escribir `compuesta` en `nota`.
5. Material de laboratorio → `geopot` aunque la norma sea INVIAS. Material en una **especificación de pavimento** → `vias`.
6. Si dudas entre dos, elige el que tenga la fuente más específica y pon el otro en `aceptables`. Si no sabes, deja la fila sin etiqueta: es mejor que una etiqueta adivinada.

## Política por norma (issue #170)

Sale del inventario `scripts/evaluacion/golden/e1_enrutador/INVENTARIO_CORPUS.md` (109 normas, 15.862 chunks), que calcula la pertenencia con las mismas reglas de la recuperación (`FUENTES_DOMINIO`). Si una pregunta se apoya sobre todo en una norma, su etiqueta es el dominio primario de esa norma, salvo que las reglas de desempate digan otra cosa.

| Norma o grupo (chunks) | Dominio primario | Aceptables | Límite / ejemplo |
|---|---|---|---|
| NSR-10 Título A (1.587) | `normativa_general` | `geopot` (A.2, zonificación), `vulnerabilidad_vivienda` (A.10, rehabilitación) | "Aa de Pasto" → geopot; "método de la fuerza horizontal equivalente" → NG |
| NSR-10 Título H (552) | `geopot` | `normativa_general` | capacidad portante, licuación, estudio geotécnico |
| NSR-10 Título E (177) + AIS 2004, AIS 410-23, Build Change (104) | `vulnerabilidad_vivienda` si es una casa existente | `normativa_general` | diseño de una casa nueva por el Título E → NG |
| NSR-10 B, C, D, F, G, I, J, K y Alcance (8.300) | `normativa_general` | — | concreto, acero, madera, mampostería de diseño, incendio, accesibilidad |
| Res. 0312, Res. 4272, Res. 5018, Decreto 1072, Ley 1562, SG-SST | `normativa_general` | — | seguridad y salud en obra |
| Res. 0330, CRA 955/956, Ley 142 Art. 85, NTC 1500 (333) | `aquai` | — | NTC 1500 es fontanería: aquai aunque esté en `ntc_chunks` |
| Normas de Ensayo INVIAS Secc. 200 y 300 (1.208) | `vias` si es especificación de obra vial | `geopot` si es un ensayo de laboratorio | "desgaste Los Ángeles del agregado" → geopot; "agregado para base granular" → vias |
| NTC 121, 174, 396, 454, 673 y fichas INV E-123/125/126/141/148, ASTM D2487, ACI 211 | `geopot` | `normativa_general` | slump, cilindros, granulometría, Proctor, CBR, USCS |
| Otras NTC de producto (2289, 30, 4026, 4076, 1032, 3459, 504, 1028, 4027, 1328, 2516, 4595) y fichas ACI 318 / AISC 360 | `normativa_general` | `geopot` si la pregunta es de ensayo | NTC 2289 (barras corrugadas) es requisito de producto, no de laboratorio |
| CCP-14 (1.220), Manual de Túneles (143), Manuales de Pavimentos, Diseño Geométrico y Mantenimiento INVIAS, INV E-631/632/826, NTC 2017/4342 | `vias` | — | puentes, túneles, pavimentos |
| Guía POT y fuentes secundarias MVCT (94) | `geopot` | `normativa_general` | POT, estudios básicos de amenaza |
| Ley 80, Ley 1150, Ley 1474, manuales de interventoría (785) | `gerencia` | — | contratación pública e interventoría |
| PMI/EVM, ISO 9001/14001/19011/27001/31000 (33) | `gerencia` | — | valor ganado, sistemas de gestión |
| E.030 Perú (204) / NEC-SE-DS Ecuador (395) | `peru_e030` / `ecuador_nec_se_ds` | — | solo si se nombra el país, una ciudad o la norma |
| Datos estructurados: precios APU e INVIAS | `apu_precios` | `vias` si es precio INVIAS de vía | — |
| Datos estructurados: SGC, Apéndice A-4 municipal, microzonificación, suelos IGAC | `geopot` | `normativa_general` | dato de un lugar concreto |
| Datos estructurados: caudales IDEAM | `aquai` | `geopot` si es amenaza por inundación | — |
| Datos estructurados: Sisbén (material de vivienda) | `vulnerabilidad_vivienda` | — | — |

Cuando se cargue una norma nueva hay que agregarla a esta tabla y a `FUENTES_DOMINIO`. `test_integridad_dominios.py` falla si un motor de `motor_chunks` no tiene dominio declarado.

## Para el set held-out

Escribir las preguntas **antes** de ver el dataset E1, con el lenguaje con que las haría un ingeniero, un maestro de obra o un estudiante. Reparto de las 60 (plantilla en `PLANTILLA_HELDOUT_K6.md`): 12 sísmica por lugar y geotecnia, 6 laboratorio, 6 vivienda, 6 agua, 6 vías, 6 gerencia, 6 precios, 9 NSR-10 de diseño o generales y 3 de Perú o Ecuador. Incluir al menos 5 negaciones y 5 preguntas compuestas.
