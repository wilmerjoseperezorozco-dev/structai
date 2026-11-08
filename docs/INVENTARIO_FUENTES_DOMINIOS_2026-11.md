# Inventario de fuentes normativas por dominio (issue #110)

Fecha: 2026-11-08. **Estado: borrador de inventario. Ninguna fuente está verificada en la fuente primaria ni descargada.** Salió de una búsqueda web por dominio (resultados secundarios: compiladores jurídicos, repositorios, proyectos de norma). Cada fila debe confirmarse en el Diario Oficial, el Gestor Normativo o el sitio de la entidad antes de ingestar (regla del proyecto). No se ingestó nada ni se cambió la base de datos.

Criterio de puntuación (1–5, máx. 20), como en `scripts/hidro/NORMAS_CANDIDATAS_INGESTA.md`: **A** relevancia para el dominio, **B** probabilidad de consulta por el usuario, **C** facilidad de obtener texto verificable, **D** riesgo de que el RAG sirva una versión desactualizada si no se ingesta.

## 1. Fuentes candidatas

| Dominio | Fuente (por verificar) | Qué se encontró | A | B | C | D | Total |
|---|---|---|---|---|---|---|---|
| Vías, excavación y terraplenes | Especificaciones Generales de Construcción de Carreteras (INVÍAS): Res. 4561/2022 (sustituye a la 1524/2022), con la Res. 2451/2022, la Res. 6044/2024 y artículos adoptados en 2025 (defensas metálicas y de concreto, arts. 730 y 731) | Cadena de modificaciones activa. **No se localizó el artículo de excavación, explanación ni voladura de roca** | 5 | 5 | 4 | 5 | 19 |
| Puentes | Res. 0108/2015 (MinTransporte) que adopta la CCP-14 | Ya está en el registro como `RES-108-2015` con vigencia «desconocido». La búsqueda la muestra como norma aplicada hoy; hay un **proyecto** de 2026 (no vigente) que modifica la sección 13, «Barandas» | 5 | 4 | 4 | 3 | 16 |
| Taludes | Manual de Estabilidad de Taludes (INVÍAS) | La agenda regulatoria 2024 lo lista como elaboración y adopción pendiente. **No hay evidencia de que esté adoptado.** Una nota de prensa sin fecha dice que solo da recomendaciones técnicas | 5 | 5 | 1 | 5 | 16 |
| Minería subterránea | Decreto 1886/2015 (Reglamento de Seguridad en Labores Mineras Subterráneas), modificado por el Decreto 944/2022; Res. ANM 368/2016 (autorrescatadores). Deroga el Decreto 1335/1987 | Texto disponible en varios compiladores. Hay un decreto de 2025 (875) citado en una presentación **sin verificar su contenido** | 4 | 3 | 5 | 4 | 16 |
| Minería a cielo abierto | Un decreto de 2022 sobre higiene y seguridad minera a cielo abierto (citado como Decreto 539/2022) | **Número y contenido sin verificar** | 4 | 3 | 3 | 4 | 14 |
| Explosivos | Decreto-Ley 2535/1993 (armas, municiones y explosivos) y reglamentos (1809/1994, 334/2002, compilación en Decreto 1070/2015 del sector Defensa); control del DCCAE (Ministerio de Defensa) e INDUMIL | Marco general confirmado en varios compiladores. **Vigencia actual y requisitos para obras civiles sin verificar** | 4 | 2 | 5 | 4 | 15 |
| Ferroviaria | Res. 20243040046045/2024 (compatibilidad de material rodante y asignación de surcos), modificada por la Res. 20253040024075/2025; Ley 76/1920 como base histórica | **No existe un reglamento técnico ferroviario unificado**; hay normas dispersas y proyectos de resolución y de ley que no están en vigor. El texto «Res. 924/2025 de surcos» **no se confirmó**: puede ser una referencia errónea | 3 | 2 | 4 | 4 | 13 |

## 2. Lecturas y límites

1. **Prioridad:** las Especificaciones Generales de Carreteras son la fuente de mayor puntaje y la que más probablemente se consulte. Antes de ingestarlas hay que ubicar el texto oficial vigente de cada artículo modificado; hoy no se sabe qué artículos cambió cada resolución.
2. **Puentes:** el registro dice «desconocido» para la que parece ser la norma de puentes en uso. Resolver ese estado en fuente primaria es barato y mejora el corpus que ya existe.
3. **Taludes:** no hay norma adoptada que ingestar. Ingestar un manual no adoptado como si fuera norma sería el error de vigencia que el proyecto ya cometió antes. Se registra como seguimiento y no como ingesta.
4. **Ferroviaria:** el corpus tendría que declarar que no hay reglamento unificado. Eso es información útil por sí misma y debe quedar dicho de forma explícita en las respuestas.
5. **Explosivos:** el alcance es normativo y de riesgo (quién autoriza, qué se exige). El repositorio no recibirá procedimientos operativos de manejo.
6. **Límite metodológico:** una sola búsqueda por tema no agota las normas. No se buscaron aún la Ley 1682/2013 (infraestructura de transporte), el Código de Minas (Ley 685/2001), normativa de licenciamiento ambiental de obras viales ni los criterios de vibración de voladuras.

## 3. Siguiente paso propuesto

Verificación en fuente primaria, sin descargas de archivos nuevos hasta que se autoricen (se indicaría nombre, fuente y tamaño):
1. Res. 0108/2015 y su estado actual → actualizar `RES-108-2015` en el registro.
2. Cadena de las Especificaciones Generales (4561/2022, 6044/2024, 2025) y ubicación de los artículos de excavación.
3. Decreto 1886/2015 con el 944/2022 consolidado.
4. Confirmar o descartar Decreto 539/2022, Decreto 875/2025 y la «Res. 924/2025».
