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

## Para el set held-out

Escribir las preguntas **antes** de ver el dataset E1, con el lenguaje con que las haría un ingeniero, un maestro de obra o un estudiante. Reparto de las 60 (plantilla en `PLANTILLA_HELDOUT_K6.md`): 12 sísmica por lugar y geotecnia, 6 laboratorio, 6 vivienda, 6 agua, 6 vías, 6 gerencia, 6 precios, 9 NSR-10 de diseño o generales y 3 de Perú o Ecuador. Incluir al menos 5 negaciones y 5 preguntas compuestas.
