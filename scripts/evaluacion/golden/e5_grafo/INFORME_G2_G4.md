# G2 y G4: el grafo de referencias cruzadas de la NSR-10 (issue #186)

Fecha: 2026-11-11. Solo lectura en Supabase, sin LLM.
Reproducir: `python scripts/evaluacion/golden/e5_grafo/g2_g4_grafo.py` (resultados en `resultados_g2_g4.json`).

**Grafo de numerales:** de 1.354 aristas, 22 no tienen numeral de origen derivable. Quedan **973 nodos y 1.129 aristas dirigidas**. Los nodos con más PageRank: G.12, A.3, F.2, F.3, G.6, C.21, F.5, K.3, A.6, G.4.

## G2: priorización de huecos de ingesta

| Medida | Valor |
|---|---|
| Numerales citados que no están en el grafo (`sin_destino`) | 82 (137 citas) |
| Re-verificados contra el corpus actual: ya existen hoy | 2 |
| **Siguen faltando** | **80 numerales, 134 citas** |
| Concentración | **F.4 (acero formado en frío): 27** · **B.6 (viento): 22** · A-3.2: 4 · K.3: 4 · A.2: 3 · F.3: 3 · K.4: 3 |
| Pareto | Cubrir el 80 % de las citas exige 54 de 80 numerales: **no hay atajo**, las citas están repartidas |
| **Huecos que usan los motores** | **5** (tabla abajo) |

| Numeral faltante | Citas | Motor | Numeral en el código del motor | Tipo |
|---|---|---|---|---|
| **A.2.6.1.1** | 1 | motor-geopot | A.2.6.1.1 (también A.2.6) | **exacta** |
| | | motor-estructural | A.2.6 | prefijo |
| **F.4.2.3.1** | 1 | motor-acero-frio | F.4.2.3.1 | **exacta** |
| F.4.2.2.2 | 2 | motor-acero-frio | F.4.2.2 | prefijo |
| A.4.3.1 | 2 | motor-geopot | A.4.3 | prefijo |
| A.6.4.1 | 1 | motor-geopot | A.6.4 | prefijo |

**Corrección durante el análisis:** la primera versión relacionaba un hueco con un motor por cualquier prefijo. Un "F.4" genérico en el código de `motor-acero-frio` se relacionaba así con todos los F.4.x y daba **31** huecos usados por motores. Con la regla estricta (coincidencia exacta, o prefijo solo si el numeral corto tiene al menos tres niveles) son **5**. `motor-aquai` se excluye porque sus numerales son del RAS / Res. 0330, no de la NSR-10.

**Lectura:**
- **Dos motores implementan numerales cuyo texto verbatim no está en StructAI:** `motor-geopot` (A.2.6.1.1, espectro de diseño) y `motor-acero-frio` (F.4.2.3.1). El cálculo puede estar bien, pero el usuario no puede verificarlo contra el texto de la norma dentro de StructAI. Rompe la regla del proyecto de "honestidad de fuente siempre verificable".
- **Prioridad de ingesta:**
  1. los 5 numerales que usan los motores;
  2. el capítulo **F.4** (27; el motor de acero formado en frío depende de él);
  3. **B.6**, viento (22).
  
  Antes de ingerir, verificar contra `docs/fuentes-normativas.md` y la vigencia (regla de CLAUDE.md).

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

- Ingerir los 5 numerales que usan los motores (con prioridad sobre el resto) y después F.4 y B.6. Agregar la prueba de contrato de #186: un motor no puede citar un numeral NSR-10 ausente del corpus.
- G4 con 20 semillas (estabilidad, NMI entre corridas) y, cuando el grafo incluya la Res. 0330, el CCP-14 y las NTC, repetir el AMI contra los dominios.
- Usar las aristas puente del núcleo A como set de preguntas multi-salto para #188.
