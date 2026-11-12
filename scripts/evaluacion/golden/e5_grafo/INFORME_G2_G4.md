# G2 y G4: el grafo de referencias cruzadas de la NSR-10 (issue #186)

Fecha: 2026-11-11. Solo lectura en Supabase, sin LLM.
Reproducir: `python scripts/evaluacion/golden/e5_grafo/g2_g4_grafo.py` (resultados en `resultados_g2_g4.json`).

**Grafo de numerales:** de 1.354 aristas, 22 no tienen numeral de origen derivable. Quedan **973 nodos y 1.129 aristas dirigidas**. Los nodos con más PageRank: G.12, A.3, F.2, F.3, G.6, C.21, F.5, K.3, A.6, G.4.

## G2: priorización de huecos de ingesta (CORREGIDO)

> **Corrección importante (misma fecha).** La primera versión concluyó que faltaban 80 numerales, 5 de ellos usados por motores, y que había que ingerirlos. **Era un error de método:** el grafo, y luego mi re-verificación, comparaban la cita solo contra la columna `seccion` y el id del chunk. Pero un chunk suele contener varios numerales como **encabezados dentro de su texto**. Al buscar el encabezado en el texto, **72 de los 82 numerales "sin destino" ya estaban en el corpus**, incluidos los 5 de los motores (p. ej. A.2.6.1.1 es un encabezado dentro de `NSR10-A-A_2_6_1_espectro_aceleraciones_p3`). **No se ingirió nada**: hacerlo habría duplicado contenido.

**Arreglo:** `indice_numerales.py` construye un índice **numeral → chunks** a partir de los encabezados del texto (`indice_numerales_nsr10.json`: 10.674 chunks leídos, 5.141 numerales indexados). `g2_g4_grafo.py` ahora lo usa.

| Medida | Primera versión | **Con el índice** |
|---|---|---|
| Numerales "sin destino" en el grafo | 82 (137 citas) | 82 (137 citas) |
| Existen hoy en el corpus | 2 | **71** |
| **Siguen faltando** | 80 (134 citas) | **11 (28 citas)** |
| Huecos usados por motores | 5 (31 con prefijo libre) | **0** |
| Pareto 80 % | 54 de 80 | 6 de 11 |

Los 11 restantes, **todos por verificar contra el PDF** antes de ingerir:

| Numeral | Citas | Hipótesis |
|---|---|---|
| A-4 | 8 | Apéndice A-4 (Aa/Av por municipio): ya está como **tabla estructurada** (`nsr10_apendice_a4_municipios`, 1.117 filas), no como texto. Se resuelve mapeando el apéndice a la tabla, no ingiriendo |
| B.6.5.6.3 | 7 | Viento: candidato real |
| D-1 | 5 | Apéndice D-1: verificar si existe y su forma |
| B.6.3, H.6.2.5, H.7.5, F.3.10.1.4 | 1 c/u | Candidatos reales |
| F.5.19, A.1.9, C-11, H-6 | 1 c/u | **Sospecha de lectura errónea** del extractor del grafo (numerales con forma rara o que quizá no existen) |

**Lectura corregida:**
- El corpus de la NSR-10 está **mucho más completo** de lo que sugería el grafo. Los huecos reales son a lo sumo unos 7, concentrados en B.6 (viento).
- **El problema real es de direccionamiento, no de contenido:** los chunks se indexan por un solo numeral. Por eso el grafo resolvió 925 citas solo "por prefijo". El índice por encabezados permite resolverlas exactamente sin tocar la base.
- Ningún motor depende de un numeral ausente. La prueba de contrato motor → numeral de #186 puede usar el índice.

## G4: comunidades frente a la taxonomía

| Medida | Valor |
|---|---|
| Nodos / aristas (no dirigido) | 973 / 1.125 |
| Componentes conexas | 61 (la mayor: 677 nodos) |
| Comunidades (Louvain, semilla 169) | 74 |
| **Modularidad** | **0,873** (estructura de comunidades fuerte) |
| **AMI comunidades vs título NSR-10** | **0,623** (nulo p95 = 0,008; p = 0,001, 1.000 permutaciones) |
| **AMI comunidades vs dominio StructAI** | **0,075** (nulo p95 = 0,006; p = 0,001) |
| Pureza de título ponderada | 0,928 |
| Comunidades que mezclan títulos / dominios | 13 / 8 |
| Aristas puente entre dominios | geopot ↔ general: 31 · general ↔ vivienda: 23 · geopot ↔ vivienda: 5 |

Las comunidades mayores que **mezclan dominios** son todas del núcleo sísmico del Título A:

| Comunidad | n | Títulos | Dominios | Nodos centrales |
|---|---|---|---|---|
| 63 | 66 | A 44, D 14, K 3, B 2, H 2, I 1 | general 54, geopot 8, vivienda 4 | A.3, A.2, A.9 |
| 0 | 63 | A 55, D 5, B 3 | general 46, geopot 10, vivienda 7 | A.6, A.4, A.5, A.10 |
| 5 | 53 | B 46, A 4, C 2, F 1 | general 51, geopot 2 | B.6, B.2.3, A.2.2.1 |

### Discusión

1. **El grafo confirma la estructura de la norma.** Las citas siguen los títulos (AMI 0,62, muy por encima del azar). El 93 % de las citas se queda dentro de su título.
2. **Los dominios de StructAI cortan a través de las comunidades** (AMI 0,075). Es esperable: los dominios agrupan por uso (sísmica, vivienda, diseño), no por título. Lo informativo es **dónde** los cortan: en el núcleo sísmico del Título A (A.2, A.3, A.4, A.6, A.10).
3. **Explica un fallo medido del enrutador.** En el E1 (#169), las preguntas del estrato "confusor sísmico" (cortante basal, R0, coeficiente de importancia) se enrutaron bien solo entre el 20 % y el 60 % de las veces con cualquier método. El grafo muestra por qué: ese conocimiento es estructuralmente **compartido** entre geopot, vivienda y diseño general. Forzar un solo dominio es un problema mal planteado. Esto respalda:
   - las fuentes compartidas de `FUENTES_DOMINIO` (A.2 en geopot **y** en general, A.10 en vivienda **y** en general), ya implementadas en 1543fbb y e57d90d;
   - el enrutamiento multi-etiqueta propuesto (E1d);
   - la expansión por grafo de Graph RAG (#188), que seguiría justo esas aristas puente.
4. **Límites:** el grafo solo cubre la NSR-10. Las comunidades dependen de la semilla de Louvain (falta reportar estabilidad con varias semillas). El dominio de cada numeral se asignó con una regla simple por prefijo, alineada con `FUENTES_DOMINIO` pero no idéntica a la política por norma de la guía.

## Próximos pasos propuestos

- **No** ingerir los 5 numerales de los motores (ya están). Verificar contra el PDF los ~7 huecos reales restantes (sobre todo B.6) y descartar las lecturas erróneas. Plan: `scripts/ingesta/nsr10/PLAN_HUECOS_GRAFO_2026-11.md`.
- Resolver las citas del grafo con el índice por encabezados (recalcular `resolucion` exacta/prefijo) y usarlo en la prueba de contrato motor → numeral.
- G4 con 20 semillas (estabilidad, NMI entre corridas) y, cuando el grafo incluya la Res. 0330, el CCP-14 y las NTC, repetir el AMI contra los dominios.
- Usar las aristas puente del núcleo A como set de preguntas multi-salto para #188.
