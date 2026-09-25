# Fuentes normativas — NSR-10

Mapa real de qué archivo de Google Drive corresponde a qué Título/Capítulo
de la NSR-10, y estado real de ingesta verbatim por título. Existe porque
hasta el 2026-09-01 esta información solo vivía en la memoria privada de
sesiones de Claude Code — si esa memoria se perdiera, reconstruir "qué PDF
es cuál título" habría requerido releer 90+ archivos de Drive uno por uno.
Este documento cierra ese hueco de lineage/ownership: vive en el repo,
versionado en git, no depende de ninguna sesión de IA en particular.

## Carpeta de Drive

- **Carpeta padre** (todos los 87 archivos PDF de NSR-10): `1cjG4OHjxLpla0s5dlpnWS_PAhTd6Dqmh`
  — https://drive.google.com/drive/folders/1cjG4OHjxLpla0s5dlpnWS_PAhTd6Dqmh
- Cobertura real: páginas Drive 1 a 1625, con un hueco real documentado abajo.
- El catálogo detallado por archivo (capítulos, tablas mencionadas, notas de
  corrección histórica, huecos de numeración no verificados uno a uno) vive
  local en `scripts/ingesta/nsr10/raw/_catalogo_maestro_limpio.txt` —
  **gitignored a propósito** (es un catálogo intermedio/documento fuente,
  misma convención que los PDF crudos, ver `scripts/README.md`). Este
  documento es el resumen navegable y versionado; el catálogo local sigue
  siendo la fuente de mayor detalle si hace falta.

## Hueco real conocido en la fuente

**Página Drive 560 no existe como archivo.** Verificado por lectura de
contenido (no solo numeración): el Apéndice C-F "Equivalencia SI/mks/inglés"
se corta a mitad de una ecuación en la página interna C-257 (fin de
`NSR-10-551-559.pdf`), y el siguiente archivo (`NSR-10-561-563.pdf`) retoma
directamente en C-259. No existe ningún archivo en la carpeta de Drive que
cubra esa página — pérdida real de una fracción del Apéndice C-F. Documentado
por decisión del usuario (2026-08-01): no bloquea el resto del catálogo, pero
sigue pendiente de completar si aparece la fuente.

## Estado real de ingesta verbatim por título (actualizado 2026-09-07, `count(*)` real contra `nsr10_chunks`)

Los conteos de esta tabla crecieron bastante frente a versiones anteriores
de este documento — no por contenido nuevo en A/B/H/K, sino por la
auditoría de tokens reales del 2026-09-01 (ver nota más abajo), que
re-trocheó todo el corpus a piezas más pequeñas respetando el límite real
de 128 tokens del modelo de embeddings. Un título con más chunks hoy no
significa más norma cubierta, solo troceo más fino.

| Título | Chunks reales | Estado |
|---|---|---|
| A — Requisitos generales | 240 (verificado con SQL; incluye ~182 previos + 54 piezas reales de A.3.3 tras re-troceo — **corrección real**: una versión anterior de esta fila decía "191 (182+9)", confundiendo el conteo de 9 chunks-padre de A.3.3 con las 54 piezas finales que quedaron en producción tras el re-troceo) bajo prefijos `NSR10-A-`/`A2-`/`A3-`/`A4-`/`A5-`/`A6-` (convención de id inconsistente — ver `docs/CATALOGO_DATOS.md`) | **INCOMPLETO — hueco real confirmado 2026-09-07** (`pypdf` sobre los 14 PDF fuente + comparación contra `nsr10_chunks`, 542 numerales reales identificados). **189 de 542 numerales (35%) sin ningún chunk al momento de auditar.** 6 capítulos completos sin cobertura: A.1 (Introducción, 67 numerales), A.7 (Interacción suelo-estructura, 16), A.8 (Efectos sísmicos sobre elementos no estructurales, 17), A.11 (Instrumentación sísmica, 12), A.12 (Edificaciones indispensables grupos II/III, 34), A.13 (Definiciones, 2). **Corrección real 2026-09-07 (misma sesión)**: la memoria privada y una versión anterior de esta fila decían que el hueco parcial más importante era "A.3.6 (Irregularidades en planta/altura)" — eso era **INCORRECTO**, confirmado leyendo el PDF real: A.3.6 es en realidad "Efectos sísmicos en los elementos estructurales", sin relación con irregularidades (mismo patrón que el `capitulo_a.txt` fabricado ya documentado más abajo). Las irregularidades reales viven en **A.3.3.4/A.3.3.5**, con las Tablas A.3-6 (5 tipos en planta) y A.3-7 (6 tipos en altura) que las definen numéricamente — **cerrado verbatim completo el mismo día que se encontró el error**, reemplazando 6 chunks viejos parafraseados por 9 chunks verbatim (54 piezas tras re-troceo), incluyendo las 2 tablas que una nota de cobertura anterior admitía honestamente como "PENDIENTE, no se lograron extraer". Verificado con `ask()` real: 2/2 PASSED (φp=0.8 para irregularidad torsional extrema 1bP, criterio de piso débil extremo 5bA). Algunos rangos existentes de A.2 están marcados "resumen" (prosa condensada, no verbatim estricto) — bandera a revisar. Los 14 PDF fuente ya están descargados en `scripts/ingesta/nsr10/raw/`. issue [#38](https://github.com/wilmerjoseperezorozco-dev/structai/issues/38) sigue abierto para el resto del hueco (A.1/A.7/A.8/A.11/A.12/A.13) |
| B — Cargas | 172 (169 + 3 B.3.3/B.3.5/B.3.6) | **PARCIAL, hueco real confirmado 2026-09-08 y en cierre progresivo** (mismo método `pypdf` + comparación contra `nsr10_chunks` que confirmó A y H: 186 numerales reales identificados en los 6 capítulos B.1-B.6). Partió de **7 secciones completas sin ningún chunk**; cerradas el mismo día: **B.3.3 (Cargas muertas mínimas), B.3.5 (Equipos fijos), B.3.6 (Consideraciones especiales)** — verificado con `ask()` real, 2/2 PASSED. **Quedan pendientes 4**: B.4.3 (Carga parcial), B.4.6 (Puente grúas), B.4.7 (Efectos dinámicos), B.4.8 (Cargas de empozamiento de agua y de granizo — **hallazgo curioso: la NSR-10 sí regula cargas de granizo, contrario a lo que se hubiera asumido antes de auditar**; no confundir con el caso adversarial `ADV2-decreto1077-granizo-cubiertas` del dataset de evaluación, que sigue siendo válido porque pregunta específicamente por el Decreto 1077, una norma distinta, no por la NSR-10). **Hallazgo adicional real, no en el alcance original de la auditoría**: los chunks existentes de B.3.4 (`NSR10-B-B_3_4_r1/r2/r3`) son un resumen condensado con solo 2-3 valores de ejemplo por tabla, no verbatim completo — mismo patrón "resumen disfrazado de completo" ya visto en A.3.3/K.2/K.3/F.3; el texto verbatim completo (6 tablas reales, B.3.4.1-1 a B.3.4.3-1) ya se leyó y está disponible en `_ingest_titulo_b_b33_b35_b36_verbatim.py` (docstring) para una futura ingesta, es la referencia de mayor valor práctico pendiente de Título B. El resto de B.1-B.6 (incluido todo B.6, Viento, extensamente cubierto hasta B.6.6.4.1) sí tiene chunks reales. Los 6 PDF fuente ya están descargados en `scripts/ingesta/nsr10/raw/` (`NSR-10-219-221.pdf` a `NSR-10-240-301.pdf`). |
| C — Concreto estructural | 2.442 | **Verbatim completo** — de los ~41 candidatos del diff crudo de la auditoría estricta 2026-09-09 (1.814 numerales reales en 29 PDF fuente), 26 eran huecos reales y se ingestaron verbatim el mismo día: C.3.6.1, C.6.3.6.1, C.7.10.4.6, C.7.12.3.2, C.8.10.1, C.9.3.2.3, C.11.3.2, C.11.7.6, C.12.14.3.2, C.13.5.3.3, C.13.7.2.1, C.13.9.1.2, C.13.9.5.2, C.13.9.8, C.14.8.2.3, C.15.5.3, C.18.3.2.2, **C.18.5 y C.18.5.1 (Esfuerzos admisibles en el acero de preesforzado, el hallazgo más valioso: capítulo completo con contenido real sin ningún chunk)**, C.18.18.2.2, C.21.4.4.4, C.21.7.2.1, C.21.11.1, C.21.12.3.4, C.21.13.3.1, C.22.7.3. Los otros 15 candidatos se descartaron tras verificación adicional, no eran huecos reales: C.9.2.5-7 (el capítulo real salta de C.9.2.4 a C.9.3, no existen), C.8.5.4/C.8.5.5/C.8.5.12 (citados desde el Apéndice C-G con una numeración que no corresponde al C.8.5 real, de solo 3 numerales — el contenido de Ec/Es ya está cubierto bajo C.8.5.1/C.8.5.2), y 9 más (C.11.6.6.2, C.11.7.4.3, C.11.12.3, C.12.3.2.5, C.13.2.6, C.21.2.1.6, C.21.2.6, C.21.7.6.2, C.21.7.6.3) que solo aparecían como remisión cruzada sin encabezado propio localizable. El Apéndice C-C (`C.23-*`) no se auditó numeral por numeral en esta pasada. Script: `_ingest_titulo_c_26_numerales_faltantes.py`. |
| D — Mampostería estructural | 719 | **Verbatim completo** — los 9 numerales hoja reales confirmados en la auditoría estricta 2026-09-09 (D.1.2.2, D.3.7.2.7, D.4.5.3, D.4.5.4, D.5.1.6.1, D.5.4.3.1, D.6.3.5, D.10.5.2.1, D.10.6.2.1) se ingestaron verbatim el mismo día. Script: `_ingest_titulo_d_9_numerales_faltantes.py`. |
| E — Casas de 1 y 2 pisos | 98 | **Verbatim completo, re-auditado con método estricto 2026-09-09**: 252 numerales reales identificados (`pdftotext` sobre los 8 PDF fuente, `NSR-10-640-645.pdf` a `NSR-10-675-677.pdf`; el último archivo llegó corrupto vía MCP dos veces seguidas — mismo número exacto de caracteres base64 truncado ambas veces — y se reconstruyó su contenido a partir del `contentSnippet` de metadata de Drive, que cubre E.9 completo). Los únicos "faltantes" del diff crudo fueron 10 encabezados de capítulo (E.1–E.9) que son padres de contenido ya cubierto — falsos positivos esperados, mismo patrón de A/B/G/H/D. **Segundo título (junto con I) en salir completamente limpio del método estricto.** Único hallazgo a anotar, no confirmado como hueco: el chunk `E.8.5.1.2` cita en su texto verbatim una remisión a "columnas de guadua en E.7.26.2", un numeral que no aparece como encabezado en ninguna de las 252 secciones reales extraídas (el capítulo E.7 real termina en E.7.9 a E.7.11) — confirmado con dos motores de extracción distintos (`pdftotext` y PyMuPDF) que coinciden byte a byte en el texto, así que no es ruido de OCR de un solo motor; probablemente un error tipográfico del documento fuente original (número de referencia cruzada mal escrito), no un hueco de ingesta — queda para verificación visual del PDF si se retoma. El conteo de 37→98 chunks refleja el mismo re-troceo por límite real de tokens ya aplicado al resto del corpus, no contenido nuevo. |
| F.1–F.4 (generalidades, acero laminado/armado/tubular, provisiones sísmicas, acero formado en frío) | 988 | **Verbatim completo** (F.4 cerrado 2026-09-01) |
| F.5.1–F.5.4.6 (Aluminio — generalidades, propiedades, principios de diseño, miembros: generalidades/esfuerzos/pandeo local/ablandamiento/vigas/tensión) | 403 | Verbatim completo |
| F.5.4.7 (Miembros a compresión) + F.5.4.8.1 (Generalidades flexión+axial) | 69 | **Verbatim completo, cerrado 2026-09-24 (Fase 1 del plan de cierre de Título F)** — la pieza más densa de F.5 (Tabla F.5.4.7-2, 18 casos de sección con fórmulas propias λ0/s/X/Y cada uno). Nota de fidelidad honesta: los 18 dibujos de sección transversal de la tabla y las 3 figuras de interpolación gráfica (F.5.4.7-1, F.5.4.7-2a/b) NO se transcriben — son diagramas visuales sin ecuación cerrada, mismo criterio ya aplicado a las figuras Cp/GCp de viento (issue #56) y a los mapas de amenaza sísmica de Título A; solo se documentan las fórmulas (el contenido técnico real). Verificado con `ask()` real (3 verificaciones de miembro a compresión; 2.5% de fuerza axial para presillas F.5.4.7.9(f)). Offset de páginas confirmado por lectura visual: página_F = página_real − 681. Script: `_ingest_titulo_f_f547_f548_1_verbatim.py`. |
| F.5.4.8.2 (cierre) a F.5.4.9 (cierra todo F.5.4) | 15 | **Verbatim completo, cerrado 2026-09-24 (Fase 2)** — `NSR-10-1183-1283.pdf` descargado desde Google Drive (id `1xuOZukeQsLIV957z59BK2eJqpZ5qu__b`), confirmada continuidad exacta de texto con el corte del PDF anterior (misma frase, sin salto). Cubre F.5.4.8.2 (cola), F.5.4.8.3 (revisión de sección, ec. F.5.4.8-1), F.5.4.8.4 (revisión por pandeo general, 4 casos A/B/C/D, ec. F.5.4.8-2 a F.5.4.8-6) y F.5.4.9 (deformación, estado límite de servicio). **Hallazgo real**: el documento fuente tiene un error tipográfico propio en F.5.4.8.4(b), cita "F.7.4.5.6" cuando la referencia correcta y consistente con el resto del numeral es F.5.4.5.6 — documentado explícitamente en el chunk, no corregido silenciosamente. Verificado con `ask()` real (deflexión elástica se calcula bajo carga nominal, no mayorada). Script: `_ingest_titulo_f_f548_f549_verbatim.py`. |
| F.5.5.1–F.5.5.2 (Generalidades + Láminas No Rigidizadas completo) | 30 | **Verbatim completo, cerrado 2026-09-24 (Fase 3)** — esfuerzo directo (F.5.5.2.1), momento en el plano (F.5.5.2.2), gradiente de esfuerzo longitudinal (F.5.5.2.3), cortante (F.5.5.2.4) y acciones combinadas (F.5.5.2.5). Verificado con `ask()` real (20% del área para ignorar agujeros pequeños en cortante). Script: `_ingest_titulo_f_f551_f552_verbatim.py`. |
| F.5.5.3 completo (Láminas Multi-Rigidizadas) | 23 | **Verbatim completo, cerrado 2026-09-24 (Fase 4)** — compresión uniforme (F.5.5.3.1), momento en el plano (F.5.5.3.2), gradiente de esfuerzos longitudinal (F.5.5.3.3) y cortante (F.5.5.3.4, con la Figura F.5.5.3-1 documentada como no transcribible por ser lectura gráfica). Verificación con `ask()` real dio un falso negativo (0.3L de espaciamiento máximo de rigidizadores) — confirmado por SQL directo que el dato SÍ está verbatim en la pieza `_r2` del chunk, es una limitación de retrieval por embeddings ante contenido técnico denso, no un hueco de datos (mismo patrón ya visto con la tabla J.3.4-1 de Título J). Script: `_ingest_titulo_f_f553_verbatim.py`. |
| F.5.5.4.1–F.5.5.4.5 (Vigas Ensambladas: momento, cortante, rigidizadores, almas corrugadas) | 66 | **Verbatim completo, cerrado 2026-09-24 (Fase 5)** — resistencia a momento (F.5.5.4.1), resistencia a cortante con acción de campo tensionado (F.5.5.4.2), vigas rigidizadas longitudinal y transversalmente (F.5.5.4.3), rigidizadores de alma tipos A/B/C y platinas de enchape (F.5.5.4.4) y uso de almas corrugadas (F.5.5.4.5). Las Figuras F.5.5.4-1/2/3 (coeficientes v2/v3/m1) documentadas como no transcribibles (curvas gráficas). Verificado con `ask()` real: 1/2 preguntas perfecta (2 funciones del poste extremo); la otra reveló un miss real de síntesis del LLM (mencionó solo Tipo A/B de rigidizador, omitió el Tipo C longitudinal que sí está verbatim en el chunk) — mismo patrón de miss ya documentado en H.8/H.10, no se agregó a regresión. Script: `_ingest_titulo_f_f554_1_a_5_verbatim.py`. |
| F.5.5.4.6 (cierra F.5.5 completo) + F.5.6.1–F.5.6.4.3 (Diseño Estático de Uniones: generalidades, remaches/pernos) | 35 | **Verbatim completo, cerrado 2026-09-24 (Fase 6)** — cierra F.5.5.4.6 (interacción momento-cortante, figuras no transcribibles) y abre F.5.6 (uniones): generalidades (F.5.6.1), consideraciones de diseño (F.5.6.2.1-3), consideraciones geométricas (F.5.6.3.1-3.9, espaciamientos/distancia al borde/avellanado/intersecciones) y resistencia de sujetadores individuales (F.5.6.4.1-4.3, con la Tabla F.5.6.4-1 de esfuerzos límite por aleación). Verificado con `ask()` real (2.5d espaciamiento mínimo; remaches de aluminio no recomendados a tensión) — una respuesta mencionó tangencialmente una norma "CCP-14" ajena al corpus (posible alucinación del LLM sobre el dato correcto ya dado, no un problema de datos/retrieval). Script: `_ingest_titulo_f_f5546_f561_a_f5643_verbatim.py`. |
| F.5.6.4.4–F.5.6.6 (Aplastamiento, pernos de alta resistencia a fricción, uniones con pasadores) | 25 | **Verbatim completo, cerrado 2026-09-24 (Fase 7)** — aplastamiento (F.5.6.4.4, ec. F.5.6.4-3/4/5), cortante+tensión combinados (F.5.6.4.5, ec. F.5.6.4-6), F.5.6.5 completo (pernos de alta resistencia a fricción: estados límite, capacidad por fricción, preesfuerzo, coeficiente de deslizamiento μs=0.33) y F.5.6.6 completo (uniones con pasadores: pasadores sólidos, miembros conectados por pasadores). Verificado con `ask()` real (μs=0.33 con chorro de arena G38). Script: `_ingest_titulo_f_f5644_a_f566_verbatim.py`. |
| F.5.6.7–F.5.6.8 (Uniones soldadas: tipos, geometría, resistencia de diseño) | 37 | **Verbatim completo, cerrado 2026-09-24 (Fase 8)** — F.5.6.7 completo (criterios de selección de unión, efecto en resistencia estática/fatiga, corrosión, preparación de bordes, distorsión, información al fabricante, soldaduras a tope y de filete) y F.5.6.8 completo (grupos de soldaduras, esfuerzo límite del metal de aporte Tabla F.5.6.8-1, esfuerzo límite en zona afectada por el calor Tabla F.5.6.8-2). Verificación con `ask()` dio otro falso negativo (pw de 6061/6082) — confirmado por SQL directo que el dato SÍ está verbatim en la pieza `_r4`, mismo patrón de limitación de retrieval por embeddings ante tablas densas ya documentado en Fase 4 y en Título J. Script: `_ingest_titulo_f_f567_f568_verbatim.py`. |
| F.5.6.9–F.5.8 + apéndices F.5.A–F.5.F (cierra el Título F) | 0 | **Pendiente — Fase 9**, mismo `NSR-10-1183-1283.pdf` ya descargado, continúa desde la página interna F-531 (F.5.6.9 — Resistencia de Diseño de Soldaduras). |
| G — Madera y Guadua | 1.193 | **Verbatim completo** — de los 27 candidatos del diff crudo de la auditoría estricta 2026-09-09 (489 numerales reales), 18 eran huecos reales y se ingestaron verbatim el mismo día: G.2.1.6, G.6.2.3, G.6.2.5, G.6.7.7, G.6.7.11, G.6.9.2, G.6.14.1.3, G.6.15.3, G.6.15.4, G.12.3.2.6, G.12.3.2.7, G.12.6.2.1, G.12.6.2.5, G.12.6.7, G.12.7.5, G.12.8.6.3, G.12.8.10.2, y **G.12.3.2.2** (hallazgo real de typo del documento fuente: el PDF imprime este numeral como "G.12.4.2.2" por error, corregido por su posición real entre G.12.3.2.1 y G.12.3.2.3). Los otros 9 candidatos se descartaron por ser referencias de tabla/ecuación embebidas en celdas de coeficientes (mismo patrón que en Título C) o citas cruzadas sin encabezado propio localizable: G.2.2.4, G.2.2.5, G.2.3, G.3.3.4.4, G.4.3.10, G.4.6.2.8, G.5.1.1, G.12.16, G.32. Script: `_ingest_titulo_g_24_numerales_faltantes.py`. |
| H — Estudios geotécnicos | 552 (48 originales + 87 H.3.3/H.4 + 47 H.5 + 45 H.6 + 64 H.7 + 80 H.8 + 101 H.9 + 80 H.10) | **VERBATIM COMPLETO (H.1-H.10), cerrado el mismo día 2026-09-07** tras la auditoría numeral por numeral que confirmó el hueco original (181 encabezados reales identificados, partió de ~18% cubierto). Cerrados en la misma sesión: **H.3.3 (cierre de H.3), H.4 (Cimentaciones), H.5 (Excavaciones y estabilidad de taludes), H.6 (Estructuras de contención), H.7 (Evaluación geotécnica de efectos sísmicos/licuación), H.8 (Sistema constructivo), H.9 (Condiciones geotécnicas especiales: suelos expansivos/dispersivos/colapsables, efectos de la vegetación) y H.10 (Rehabilitación sísmica de edificios: amenazas sismo-geotécnicas y reforzamiento de cimentaciones)** — todos re-trocheados con verificación real de tokens, 0 sobre el límite desde el primer intento en cada pieza, sin excepción. Verificado con `ask()` real en cada pieza: 20 de 22 preguntas nuevas PASSED con cita exacta (H.9 fue 4/4 limpio); 1 falló por retrieval (límite de giro H.4.9.4, chunk corto) y 1 se descartó por diseño de pregunta defectuoso (Tabla H.6.4-1 no tiene coeficientes Kp numéricos); un caso adicional (Tabla H.4.9-1) reveló que el LLM confunde filas adyacentes de tablas densas — mismo patrón ya documentado en F.5.2/F.5.4.3/F.5.4.4. **Hallazgo real en H.8**: al verificar la ecuación de pandeo H.8.4-1 (pilotes), el LLM cita la fórmula correctamente pero responde "el Título H no especifica un valor numérico concreto para el factor de seguridad" pese a que el mismo chunk verbatim transcrito dice literalmente "F_S se tomará igual a 3.0" — un miss real de síntesis/generación, no de retrieval. **Hallazgo real en H.10**: al preguntar la profundidad de nivel freático para descartar licuación (H.10.2.2.2, valores reales: 10 m bajo el cimiento o 15 m bajo la superficie), el LLM cita el artículo correcto pero no surge los valores numéricos específicos — mismo patrón de miss de síntesis. Ninguno de los dos se agregó al dataset de regresión para no forzar un caso fallido como si pasara. Los PDF fuente ya están descargados en `scripts/ingesta/nsr10/raw/` (`NSR-10-1401-1450.pdf`, `NSR-10-1451-1500.pdf`, `NSR-10-1501-1570.pdf`). 13 chunks no-verbatim (de lo poco que existía antes) borrados el 2026-09-01 — issue [#38](https://github.com/wilmerjoseperezorozco-dev/structai/issues/38) sigue abierto (era sobre A y H; con H ya verbatim completo, queda pendiente solo por Título A) |
| I — Supervisión técnica | 62 | **Verbatim completo, confirmado con auditoría estricta 2026-09-09** — 63 numerales reales identificados (`pypdf` sobre `NSR-10-1501-1570.pdf`, páginas I-1 a I-28), 62 con chunk real y contenido verbatim verificado a mano (el numeral restante, I.1.5.1, resultó ser un falso positivo del regex de extracción, no un numeral real del documento). Único de los 7 títulos re-auditados con este método que salió limpio de entrada. |
| J — Protección contra incendios | 49 | **INCOMPLETO — hueco real grande confirmado 2026-09-09** (mismo método `pypdf` que A/B/H: 159 numerales reales identificados en `NSR-10-1501-1570.pdf`, páginas J-1 a J-32). A diferencia de A/B/H (capítulos enteros sin ningún chunk), aquí el problema es que **casi todo el título está condensado en resumen, no verbatim** — mismo patrón "resumen disfrazado de completo" ya visto en A.3.3/B.3.4, pero a escala de un título completo: ej. J.3.3.3 tiene 13 sub-numerales reales (tipos de edificación eximidos de resistencia al fuego) y solo 4 están parafraseados en 3 chunks cortos (300-350 caracteres); J.4.3.1 a J.4.3.9 (sistemas de detección/extinción — rociadores, hidrantes, alarmas — contenido técnico de uso diario) están condensados en solo 4 chunks de 150-410 caracteres cada uno. J.2.1 y J.3.1 no aparecen en ningún chunk. Candidato de re-ingesta verbatim completa, no solo relleno de huecos puntuales — issue nuevo pendiente de crear. |
| K — Otros requisitos complementarios (K.1–K.4.3) | 433 | **Verbatim completo (K.1–K.4.3.16), cerrado el mismo día que se encontró el hueco.** La re-auditoría estricta 2026-09-09 confirmó que "K.4.3 completo" (afirmado en una versión anterior de esta fila, 2026-09-07) era incorrecto: faltaban K.4.3.10 a K.4.3.16 (Vidrio estructural y de piso, Revestimiento con vidrios, Vidrios en cubierta, y 3 numerales de normas técnicas referenciadas — Colombianas, ASTM, Otras), 7 numerales reales de las páginas 53-55 del mismo `NSR-10-1571-1625.pdf` ya descargado (el final real del capítulo). Ingestados verbatim el mismo día. Script: `_ingest_titulo_k_k4310_a_k4316_verbatim.py`. |

**Título F, total real hoy**: 1.691 chunks (988 + 403 + 69 + 15 + 30 +
23 + 66 + 35 + 25 + 37) de los ~2.200-2.400 estimados para cerrarlo por
completo — sigue siendo, con diferencia, el título con más volumen de
todos. Con esto **F.5.4, F.5.5, y F.5.6.1-F.5.6.8 (todo el diseño
estático de uniones excepto la resistencia de soldaduras propiamente
dicha) quedan verbatim completos**; queda pendiente F.5.6.9
(resistencia de diseño de soldaduras) en adelante hasta F.5.8 más los
apéndices F.5.A-F.5.F.

**Sobre la auditoría numeral por numeral (mismo método que confirmó
K.3.11–K.3.18, 0% cubiertos, 2026-08-27 — extraer con `pypdf`/regex los
numerales que existen REALMENTE en el PDF fuente y compararlos contra los
ids de chunk en la base, no solo mirar si "el chunk que existe se ve
completo")**:

- **Título H — auditado 2026-09-07, hueco real confirmado y CERRADO el
  mismo día** (ver fila de arriba): partió de 148 de 181 encabezados
  reales sin chunk (el título cubría apenas H.1–H.3.2). No era un caso
  de "probablemente está bien, falta el papeleo" — de hecho la mayoría
  técnica del título (cimentaciones, taludes, muros de contención,
  licuación, suelos problemáticos, rehabilitación sísmica) nunca se
  había ingestado. Los 181 encabezados quedaron cerrados en verbatim
  completo (H.1-H.10) antes de terminar la sesión.
- **Título A — re-auditado con `rag-audit-kit` 2026-09-22, hueco real
  mucho más grande de lo estimado el 2026-09-07** (el audit anterior
  medía a nivel de capítulo, "¿existe algo de A.10?"; este audit mide
  numeral por numeral contra la columna `seccion` real): **555 numerales
  reales** extraídos de los 14 PDFs (páginas 43-218), solo **58/555
  (10.5%)** cubiertos antes de esta sesión. Hallazgo clave: A.9 y A.10
  ya tenían chunks reales, pero con `seccion` en formato de rango
  condensado (ej. `"A.10.1 a A.10.9"`, 14 chunks cortos) — contenido
  parafraseado, no verbatim numeral por numeral, mismo patrón ya
  documentado en A.3.3/B.3.4/Título J.
  **Fase 1 del plan de cierre por fases cerrada el mismo día**: A.4
  (Método de la fuerza horizontal equivalente), A.7 (Interacción
  suelo-estructura), A.8 (Efectos sísmicos sobre elementos no
  estructurales), A.11 (Instrumentación sísmica) y A.13 (Definiciones y
  nomenclatura — resultó ser un glosario de 14 páginas/~150 términos,
  no los "3 numerales" que sugería el audit automático, porque el
  regex de numerales no detecta entradas de glosario sin numeración).
  Los 5 capítulos verificados con `ask()` real citando valores y
  fórmulas exactos (Vs=Sa·g·M, Fp=(ax·g/R0)·Mp, umbral de 20.000 m²
  para instrumentación en zona alta, período de retorno de 475 años,
  etc.). Cobertura del título tras la Fase 1: 85/555 (15.3%).
  Scripts: `_ingest_titulo_a_a{4,7,8,11,13}_verbatim.py` +
  `_resplit_titulo_a_a{4,7,8,11,13}_por_limite_tokens.py`.
  **Fase 2 cerrada el mismo día**: A.2 (Zonas de amenaza sísmica y
  movimientos sísmicos de diseño) — el capítulo de mayor valor real del
  título (Aa/Av, espectro de diseño A.2.6 citado por prácticamente
  todos los demás capítulos), resultó ser 27 páginas (A-13 a A-38), muy
  por encima de lo que sugerían sus "77 faltantes". Incluye Tabla
  A.2.3-2 completa (32 ciudades capitales con Aa/Av/zona), las 6
  clasificaciones de perfil de suelo (Tabla A.2.4-1), el espectro de
  diseño completo (aceleraciones/velocidades/desplazamientos, A.2.6.1 a
  A.2.6.3), los 4 grupos de uso y coeficiente de importancia (A.2.5), y
  el alcance completo de microzonificación sísmica (A.2.9) y estudios
  particulares de sitio (A.2.10). El Apéndice A-4 (Aa/Av de TODOS los
  municipios) se dejó fuera a propósito — no tiene numerales "A.2.x" (no
  es parte del cuerpo del capítulo) y esa misma información ya la sirve
  en vivo el SGC (`sgc_amenaza_sismica.py`). Verificado con `ask()` real
  (Sa=1.2·Av·Fv·I/T, Aa=Av=0.10 para Barranquilla, los 6 tipos de perfil
  A-F, Grupo IV/I=1.50 para hospitales). Scripts:
  `_ingest_titulo_a_a2_verbatim.py` +
  `_resplit_titulo_a_a2_por_limite_tokens.py`. Cobertura tras la Fase 2:
  116/555 (20.9%).
  **Fase 3 cerrada el mismo día**: A.1 (Introducción — alcance de las
  disposiciones), capítulo corto (11 páginas, A-1 a A-11) pero
  introductorio, citado por casi todos los demás capítulos: A.1.2.3
  (alcance del Reglamento), la Tabla A.1.3-1 completa (los 12 pasos del
  procedimiento de diseño estructural, edificaciones nuevas vs.
  existentes), A.1.3.9 (umbral de 3000 m² para supervisión técnica
  obligatoria y exención de 15 viviendas bajo Título E), A.1.5 (planos y
  memorias: qué debe firmar cada profesional), A.1.6 (obligatoriedad de
  normas NTC) y A.1.7 (Sistema Internacional SI, NTC 1000). 22
  chunks-padre → 127 chunks reales. Verificado con `ask()` real (umbral
  3000 m² de supervisión técnica, exención de 15 viviendas del Título E,
  Sistema SI + NTC 1000, firma del ingeniero civil en planos
  estructurales). Scripts: `_ingest_titulo_a_a1_verbatim.py` +
  `_resplit_titulo_a_a1_por_limite_tokens.py`. Cobertura tras la Fase 3:
  151/555 (27.2%).
  **Fase 4 cerrada el mismo día**: A.5 (Método del análisis dinámico) +
  A.6 (Requisitos de la deriva), ambos citados por A.3/A.4/A.10. A.5
  cubre el análisis dinámico espectral y cronológico completo (número
  mínimo de modos = 90% de masa participante, combinación modal,
  ajuste del cortante dinámico al 80%/90% del método estático). A.6
  cubre los límites de deriva (Tabla A.6.4-1: 1.0% concreto/acero/
  madera, 0.5% mampostería sin requisitos especiales), efectos P-Delta
  (índice de estabilidad Qi, límite 0.30), y la separación sísmica
  completa entre edificaciones vecinas (Tabla A.6.5-1: 1%/2%/3% de la
  altura según pisos y coincidencia de losas). 8 + 9 chunks-padre → 68
  + 70 chunks reales. Verificado con `ask()` real (90% masa
  participante, derivas 1.0%/0.5%, Qi>0.30 obliga a rigidizar, 3% de
  separación sísmica cuando no coinciden losas). Scripts:
  `_ingest_titulo_a_a{5,6}_verbatim.py` +
  `_resplit_titulo_a_a{5,6}_por_limite_tokens.py`. Cobertura tras la
  Fase 4: 166/555 (29.9%).
  **Fase 5 cerrada el mismo día**: A.3 (Requisitos generales de diseño
  sismo resistente) — el capítulo más citado de todo el título (todos
  los demás remiten a "el sistema del Capítulo A.3", "el coeficiente
  R", "las irregularidades de la tabla A.3-6/A.3-7"), 24 páginas (A-39
  a A-62). **Hallazgo real al inspeccionar lo ya cargado antes de
  escribir el script**: buena parte de A.3.1, A.3.2, A.3.4 y A.3.8-A.3.9
  (25 chunks) NO era verbatim — era texto condensado/parafraseado de
  una ingesta anterior, mismo patrón ya documentado en A.9/A.10/Título
  J (ej. `A_3_2_r1` decía "Se reconocen CUATRO sistemas
  estructurales..." en vez del texto real). Esos 25 chunks se borraron
  y se reemplazaron por transcripción verbatim real; A.3.3.1-3.3.9 y
  las 4 tablas de coeficientes R0/Ω0 por sistema estructural (Tablas
  A.3-1 a A.3-4) ya eran verbatim correctas de una sesión anterior y no
  se retocaron. Se agregó lo que faltaba entero: A.3.0 nomenclatura,
  A.3.1 completo (incluye el R0=1.5 de sistemas prefabricados), A.3.2
  completo (los 4 sistemas con sus requisitos), A.3.4 completo (los 4
  métodos de análisis y cuándo usar cada uno), A.3.5, A.3.6 completo
  (torsión, diafragmas, muros, péndulo invertido, aceleraciones
  verticales — el bloque más grande del capítulo), A.3.7, A.3.8-A.3.9
  completos, y las Tablas A.3-5 (mezcla de sistemas en altura), A.3-6
  (las 5 irregularidades en planta con sus φp) y A.3-7 (las 6
  irregularidades en altura con sus φa) — antes inexistentes. 19
  chunks-padre → 171 chunks reales. Verificado con `ask()` real (4
  sistemas estructurales, 25% cortante mínimo del pórtico en sistema
  dual, cuándo usar fuerza horizontal equivalente en irregulares,
  φp=0.8 para irregularidad torsional extrema 1bP, R0=1.5 prefabricados
  sin evidencia experimental); un quinto caso (fuerza de amarre de
  vigas de cimentación) confirmó dato correcto en la base pero con miss
  de retrieval — mismo patrón de variación conocido, no error de datos.
  Scripts: `_ingest_titulo_a_a3_verbatim.py` +
  `_resplit_titulo_a_a3_por_limite_tokens.py`. Cobertura tras la Fase
  5, re-auditada completa: 194/555 (35.0%).
  **Fase 6 cerrada el mismo día**: A.9 (Elementos no estructurales) +
  A.10 (Evaluación e intervención de edificaciones construidas antes
  de la vigencia del Reglamento) — el bloque más grande del título (9
  + 15 páginas, A-87 a A-111). **Hallazgo real**: los 21 chunks de A.9
  y los 17 de A.10 ya cargados NO eran verbatim — texto condensado de
  una ingesta anterior, mismo patrón que A.3 (Fase 5). Se borraron y se
  reemplazaron por transcripción real completa. A.9 cubre: grados de
  desempeño (Tabla A.9.2-1), la ecuación de fuerza sísmica de diseño
  Fp completa (A.9.4-1/2), los 4 tipos de anclaje según Rp (especiales/
  dúctiles/no dúctiles/húmedos), elementos de fachada y "columnas
  cautivas", y las 2 tablas completas de coeficientes ap/Rp (A.9.5-1
  acabados, A.9.6-1 instalaciones). A.10 cubre: el procedimiento de
  evaluación completo (las 12 etapas de A.10.1.4), los movimientos
  sísmicos con seguridad limitada (coeficiente Ae, Tablas A.10.3-1/2
  con las 32 ciudades capitales), los índices de sobreesfuerzo y
  flexibilidad, los 3 tipos de modificación (ampliación adosada, en
  altura, actualización), rehabilitación sísmica según edad de la
  edificación (NSR-98/Decreto 1400/patrimonio histórico), y reparación
  de edificaciones dañadas por sismos. 12+19 chunks-padre → 107+145
  chunks reales. Verificado con `ask()` real (grado Superior para
  Grupo IV, activación del interruptor automático a 0.5·Aa, Ae=0.05
  para Barranquilla, R'=1.0 para mampostería no reforzada sin
  información, límite de 10% para modificaciones menores); un caso
  (Rp=0.5 para anclaje húmedo) confirmó dato correcto en la base con
  miss de retrieval, mismo patrón ya documentado. **Hallazgo
  operativo real durante la re-auditoría**: el propio script de
  auditoría de cobertura sufrió el bug de paginación de Supabase ya
  documentado en otros scripts del proyecto (`.select().execute()` sin
  `.range()` trunca en 1000 filas) — `nsr10_chunks` ya supera 1200
  filas con prefijo "A.", así que la primera corrida post-Fase-6 dio
  un falso 32.1% (mostrando A.9/A.10 en 0%); corregido paginando la
  consulta, cobertura real confirmada. Scripts:
  `_ingest_titulo_a_a{9,10}_verbatim.py` +
  `_resplit_titulo_a_a{9,10}_por_limite_tokens.py`. Cobertura tras la
  Fase 6, re-auditada completa y paginada: 245/555 (44.1%).
  **Fase 7 cerrada el mismo día — plan de 7 fases COMPLETO**: A.12
  (Requisitos especiales para edificaciones indispensables de los
  grupos de uso III y IV), capítulo corto (7 páginas, A-117 a A-123)
  que estaba en 0% de cobertura pese a ser el requisito diferencial de
  hospitales/estaciones de bomberos/etc. Cubre completo: el
  procedimiento de verificación del umbral de daño (los 4 pasos A-D de
  A.12.1.4), el coeficiente Ad con las Tablas A.12.2-1/A.12.2-2 (32
  ciudades capitales), el espectro sísmico completo del umbral de daño
  (ecuaciones A.12.3-1 a A.12.3-6), la metodología de análisis
  (A.12.4), los límites de deriva del umbral de daño (Tabla A.12.5-1:
  0.40%/0.20%), y la exención de verificación de esfuerzos (A.12.6). 7
  chunks-padre → 61 chunks reales. Verificado con `ask()` real (deriva
  0.40% concreto reforzado, A.12.6.1 no requiere verificar esfuerzos,
  80% de probabilidad de excedencia en 50 años); dos casos (alcance
  A.12.1.2, Ad=0.03 Barranquilla) confirmaron dato correcto en la base
  con miss de retrieval, mismo patrón ya documentado repetidamente en
  esta sesión. Scripts: `_ingest_titulo_a_a12_verbatim.py` +
  `_resplit_titulo_a_a12_por_limite_tokens.py`. Cobertura final del
  Título A, re-auditada completa y paginada: **253/555 (45.6%)**, de
  10.5% al inicio del día — subida de 35 puntos porcentuales en una
  sola sesión, con 3 casos reales de chunks condensados/no-verbatim
  detectados y corregidos en el camino (A.3, A.9, A.10). El 54.4%
  residual reportado por el audit automático es mayoría "falso
  faltante" por el límite conocido de rag-audit-kit con `seccion` en
  formato de rango (ver README del paquete) — cada capítulo cerrado se
  verificó honestamente con `ask()` real, no solo con el número del
  audit.
- **Título B — re-auditado con `rag-audit-kit` 2026-09-23, hueco real
  mucho más grande de lo que decía la nota de 2026-09-08** (esa nota
  hablaba de "7 secciones sin chunk"; el re-audit numeral por numeral
  contra los 6 PDFs fuente encontró **186 numerales reales, solo 50/186
  (26.9%) cubiertos** antes de esta sesión): B.1 (Requisitos
  generales) 1/16, B.2 (Combinaciones de carga) 5/20, B.3 (Cargas
  muertas) 7/10 — el mejor, solo falta B.3.4 (condensado, ya
  identificado en 2026-09-08), B.4 (Cargas vivas) 6/25, B.5 (Empuje de
  tierra/presión hidrostática) 1/8, y **B.6 (Fuerzas de viento) 30/107
  — el capítulo dominante**, 62 páginas (mucho más grande de lo
  estimado), de las cuales solo ~36 son prosa normativa real (B.6.1 a
  B.6.5, Métodos 1 y 2); las ~24 páginas finales de B.6.6 (Método 3)
  son casi enteramente figuras de coeficientes de presión (Cp/GCp por
  forma de cubierta/ángulo/zona), mismo patrón que los mapas de
  amenaza sísmica de Título A dejados fuera del alcance verbatim —
  pendiente de decisión explícita en la fase que llegue a B.6.6.
  **Plan de cierre por fases** (por tamaño/valor):
  - **Fase 1 (cerrada 2026-09-23)**: B.1 (Requisitos generales,
    completo, 2 páginas) + B.5 (Empuje de tierra y presión
    hidrostática, completo, cabe en 1 página). 2+1 chunks-padre → 12+9
    chunks reales. Verificado con `ask()` real (empuje bajo nivel
    freático, coeficiente activo con libertad de giro/traslación,
    integridad estructural ante daño local, zonas inundables).
    Cobertura tras Fase 1: 56/186 (30.1%).
  - **Fase 2 (cerrada 2026-09-23)**: B.2 (Combinaciones de carga,
    completo, 5 páginas B-3 a B-7) — se multiplica en todo el resto de
    títulos. Cubre el glosario bilingüe completo de definiciones
    (B.2.1.1), la nomenclatura completa (B.2.2), las 10 combinaciones
    de esfuerzos de trabajo (B.2.3, ecuaciones B.2.3-1 a B.2.3-10) y
    las 7 combinaciones mayoradas por el método de la resistencia
    (B.2.4, ecuaciones B.2.4-1 a B.2.4-7) con sus 7 notas de aplicación
    (factor de reducción a 0.5 para L, 1.3W sin factor de
    direccionalidad, advertencia explícita de no mezclar factores de
    carga NSR-10 con φ de NSR-98). 7 chunks-padre → 48 chunks reales.
    Verificado con `ask()` real (1.4(D+F), reducción a 0.5 de L y sus
    excepciones, 1.3W sin direccionalidad, advertencia NSR-98).
    Scripts: `_ingest_titulo_b_b2_verbatim.py` +
    `_resplit_titulo_b_b2_por_limite_tokens.py`. Cobertura tras la
    Fase 2: 69/186 (37.1%).
  - **Fase 3 (cerrada 2026-09-23)**: B.3.4 (Elementos no
    estructurales, dentro de Cargas muertas — 3 chunks condensados
    reemplazados por 6 tablas reales completas, B.3.4.1-1 a
    B.3.4.3-1) + B.4 completo (Cargas vivas — 9 chunks condensados de
    B.4.1-4.2/4.4-4.5 reemplazados, y B.4.3/B.4.6/B.4.7/B.4.8
    completamente ausentes agregados: carga parcial, puente grúas,
    efectos dinámicos, empozamiento de agua y de granizo). 7+11
    chunks-padre → 50+41 chunks reales. Verificado por SQL directo
    contra la base (0.25 kN/m² pañete en yeso/concreto para cielo
    raso, 20% de fuerza horizontal para puente grúas con cabina de
    operación) — la verificación end-to-end con `ask()` no pudo
    completarse por una inestabilidad real e intermitente de
    conectividad de Supabase durante esta sesión (confirmada con
    curl/MCP, no causada por la ingesta). **Hallazgo importante que
    reescribe el resto del plan**: al inspeccionar el corpus se
    encontró que B.6 (Fuerzas de viento) YA tenía prácticamente todo
    su texto normativo (B.6.1-B.6.4 completos, B.6.5 Método 2
    completo con sus 26 ecuaciones, B.6.6 Método 3 completo) cargado
    verbatim desde una sesión previa (2026-09-08, ver commits
    `cbc4d6d`/`8a3f4ac`) — solo bajo `seccion` en formato de rango que
    el audit automático no reconocía como cobertura completa. Scripts:
    `_ingest_titulo_b_b34_verbatim.py` + `_ingest_titulo_b_b4_verbatim.py`
    + sus resplits. Cobertura tras la Fase 3: 78/186 (41.9%).
  - **Fase 4 (re-alcance)**: dado el hallazgo de Fase 3, ya no hacen
    falta 3 fases separadas para B.6 — el trabajo pendiente real es
    (a) cerrar B.1 (13 faltantes, Requisitos generales — curiosamente
    aún con hueco real pese a ser corto) y B.5 (3 faltantes
    residuales), y (b) una revisión de calidad puntual de 2 pasajes de
    B.6.5 ya marcados con "NOTA DE FIDELIDAD" en el propio chunk
    (posible reordenamiento OCR en fórmulas de B.6.5.12.4.2 y
    B.6.5-19) más la decisión, aún pendiente, sobre las ~19 figuras de
    coeficientes de presión (Cp/GCp) de B.6.5/B.6.6 dejadas fuera de
    alcance verbatim.
  - **Fase 4 (cerrada 2026-09-23)**: verificación de B.1/B.5 y cierre
    de la revisión de calidad de B.6.5. Los "13 faltantes" de B.1 y
    "3 faltantes" de B.5 resultaron ser **falsos negativos** del
    audit automático — se confirmó por consulta SQL directa que todo
    el contenido de ambos capítulos (transcrito completo en la Fase 1)
    ya está presente verbatim; el residual es el mismo límite conocido
    de `rag-audit-kit` con `seccion` en formato de rango. En el
    camino se encontraron y borraron 6 chunks condensados duplicados
    (`NSR10-B-B_1_r1-3`, `NSR10-B-B_5_r1-3`) que habían quedado sin
    limpiar de antes de la Fase 1, redundantes con el verbatim real ya
    cargado. Los 2 pasajes de B.6.5 marcados "NOTA DE FIDELIDAD" se
    verificaron contra la página B-35 del PDF: el texto de B.6.5.12.4.2
    resultó correcto (no corrupto), y la ecuación B.6.5-19
    (excentricidad para estructuras flexibles) que antes solo se
    describía sin la fórmula real, se completó con la fórmula
    verificada (3 chunks nuevos, reemplazando el chunk incompleto y su
    nota de fidelidad ahora resuelta). **Decisión del usuario sobre las
    ~19 figuras Cp/GCp**: quedan documentadas como
    [issue #56](https://github.com/wilmerjoseperezorozco-dev/structai/issues/56)
    para decidir su alcance en una sesión futura, en vez de resolverlas
    ahora. Cobertura tras la Fase 4 (sin cambio numérico esperado —
    fase de limpieza/verificación, no de contenido nuevo): 78/186
    (41.9%).
  - **Hallazgo operativo real de esta sesión**: durante la Fase 3-4 se
    encontró que el cliente Python (httpx) con HTTP/2 fallaba de forma
    consistente y reproducible en peticiones POST/DELETE contra
    Supabase (`RemoteProtocolError: ConnectionTerminated`), mientras
    curl y HTTP/1.1 funcionaban sin problema — confirmado que NO era
    un incidente de plataforma (producción y REST API respondían bien
    por curl) sino algo específico a la negociación HTTP/2 desde esta
    sesión/red. Solución aplicada: forzar `httpx.Client(http2=False)`
    al crear el cliente de Supabase — ver
    `_fix_titulo_b_b65_ecuacion_19.py` para el patrón reusable si
    reaparece en scripts futuros.
- **Título I — re-auditado 2026-09-09, único de 6 títulos re-auditados
  que salió limpio** (ver fila de arriba): 62 de 63 numerales reales con
  chunk verbatim confirmado, el numeral restante era un falso positivo
  del regex de extracción.
- **Título J — re-auditado 2026-09-09, hueco real grande confirmado; re-ingesta
  verbatim EN CURSO desde 2026-09-12** (ver fila de arriba): no es un caso de
  "capítulos enteros sin chunk" como A/B/H, sino que casi todo el título
  estaba condensado en resumen parafraseado, no verbatim, y además con las
  tildes eliminadas por completo (confirmado leyendo un chunk real antes de
  re-ingestar) — mismo patrón de A.3.3/B.3.4 pero a escala de un título
  completo (155-159 numerales reales, 49 chunks condensados originales).
  **Bloqueo técnico real encontrado al re-ingestar**: el PDF fuente
  (`NSR-10-1501-1570.pdf`) tiene el texto con codificación de fuente rota —
  `pdftotext` y `fitz` devuelven el carácter de reemplazo `�` en vez de
  tildes reales (mismo tipo de problema ya visto en un PDF de Título E) —
  confirmado probando ambas herramientas antes de decidir usar lectura
  visual (`Read` con render de imagen) numeral por numeral, página por
  página, en vez de extracción mecánica. **Progreso real**: **J.1 y J.2
  completos**, más J.3.1 a J.3.3.3.13 (definiciones del capítulo, tablas
  de categorización de riesgo J.3.3-1/J.3.3-2/J.3.3-3, exenciones de
  cuantificación) — 149 chunks en producción (antes 49), verificados con
  retrieval real contra `search_knowledge()`. **Corrección propia en el
  camino**: un primer intento de transcribir las tablas matriciales
  J.3.3-1/J.3.3-2 quedó aproximado con una nota de "disponible en el PDF
  dada su complejidad" — se detectó antes de ingestar y se corrigió
  releyendo la página con cuidado celda por celda, marcando explícitamente
  las celdas en blanco de la tabla real (no inventadas) y dejando una nota
  de verificación honesta para cualquier uso de diseño real. **Offset de
  páginas corregido 2026-09-24** (el docstring original del script de
  J.3 parte 1 decía "páginas reales 44-47" para J-11 a J-14, offset
  equivocado — confirmado por lectura visual directa que el offset real
  es página_J = página_real − 29, ej. página real 46 = pie de página
  "J-17"). **J.3.4 y J.3.5 completos (2026-09-24)**: las dos tablas
  alfabéticas grandes de potencial combustible (J.3.4-1 por área ~100
  filas, J.3.4-2 por masa ~100 filas), la tabla de resistencia
  normalizada J.3.4-3, J.3.4.3.1-3.8, y todo J.3.5 (elementos de
  concreto/mampostería/acero estructural, tablas J.3.5-1 a J.3.5-10,
  ecuaciones J.3.5-1/2/3) — reemplazando 12 chunks condensados
  confirmados por lectura directa de su `texto` antes de borrar (patrón
  "resumen disfrazado de completo" de siempre: minúsculas sin tildes,
  `seccion` genérico o en rango). Cobertura de J.3 tras esto: 53/54
  (el 1 restante es el mismo falso negativo conocido de rag-audit-kit
  con `seccion` en formato no numeral, ej. "J.3.5-6"). **Bug real
  encontrado y corregido en el propio script de ingesta**: un chunk
  nuevo reusó el mismo id base que un chunk condensado viejo
  (`NSR10-J-J_3_5_3`); como el script hacía upsert y LUEGO borraba
  `IDS_OBSOLETOS`, el borrado eliminó también las piezas nuevas recién
  insertadas con el mismo id — solo sobrevivió la pieza `_r4` (la vieja
  solo tenía `_r1..r3`). Fix: invertir el orden (borrar obsoletos
  primero, upsert después), documentado en el propio script para no
  repetirlo. Verificado con `ask()` real tras el fix (mampostería de
  arcilla maciza a 2h → 100mm, correcto contra la tabla). **Limitación
  de retrieval observada, no de datos**: una pregunta puntual por un
  solo material dentro de la tabla J.3.4-1 (~100 filas alfabéticas) no
  siempre recupera el chunk correcto pese a que el dato está verbatim
  confirmado por SQL directo — limitación conocida de embeddings contra
  contenido tabular denso, no exclusiva de este título. **Título J
  CERRADO 2026-09-24**: Capítulo J.4 completo (44/44 numerales —
  J.4.1 Alcance, J.4.2 detección/alarma con la tabla J.4.2-1 por
  grupo/subgrupo de ocupación, J.4.3 extinción con la tabla J.4.3-1 de
  normas NFPA y las 9 subsecciones por grupo de ocupación A/C/F/I/L/M/
  P/R-2/R-3, cada una con rociadores automáticos/tomas fijas para
  bomberos/extintores portátiles), reemplazando los últimos 6 chunks
  condensados. Cobertura final del título: **158/159 (99.4%)** — J.1
  5/5, J.2 56/56, J.3 53/54 (el 1 restante es el mismo falso negativo
  conocido de rag-audit-kit), J.4 44/44. Verificado con `ask()` real
  (NFPA 13 para rociadores en almacenamiento grupo A, 5 kg de polvo
  químico seco por cada 10 vehículos en estacionamientos).
- **Título K — re-auditado y CERRADO el mismo día 2026-09-09, corrige
  un hallazgo anterior** (ver fila de arriba): K.1-K.4.2 y K.4.3.1-9 ya
  estaban completos, pero K.4.3.10-16 (7 numerales, incluidos 3 de
  normas técnicas referenciadas) nunca se habían ingestado pese a que
  la fila de esta misma tabla decía "K.4.3 completo" desde 2026-09-07 —
  ya cerrado en verbatim.
- **Título G — re-auditado y CERRADO el mismo día 2026-09-09** (ver
  fila de arriba): 18 de 27 candidatos eran huecos reales (~4% del
  título), todos cláusulas puntuales — ya ingestados verbatim,
  incluyendo la corrección de un typo real del documento fuente
  (G.12.4.2.2 impreso, G.12.3.2.2 real).
- **Título D — re-auditado y CERRADO el mismo día 2026-09-09** (ver
  fila de arriba): los 9 numerales reales (~2% del título, el mejor
  resultado proporcional de todos) ya están en verbatim — ninguno era
  contenido crítico aislado (mortero de pega/inyección remitían a
  D.3.4/D.3.5, ya completos).
- **Título E — re-auditado 2026-09-09, salió limpio** (ver fila de
  arriba): 252 numerales reales identificados, todos con chunk verbatim
  confirmado; los 10 "faltantes" del diff crudo eran encabezados de
  capítulo (padres de contenido ya cubierto). Único hallazgo a anotar
  sin confirmar: una remisión cruzada interna a "E.7.26.2" que no
  corresponde a ningún encabezado real extraído — posible error
  tipográfico del documento original, no tratado como hueco de ingesta.
- **Título C — re-auditado y CERRADO el mismo día 2026-09-09** (ver
  fila de arriba): el título más grande del corpus, 1.814 numerales
  reales identificados en los 29 PDF fuente. De los ~41 candidatos del
  diff crudo, 26 eran huecos reales (~1,4% del título) y ya están en
  verbatim — el hallazgo más valioso, el capítulo **C.18.5 (Esfuerzos
  admisibles en el acero de preesforzado)**, tenía contenido real
  completo sin ningún chunk en producción. Se descartaron 15 falsos
  positivos del diff crudo (números de ecuación mal parseados, citas a
  la norma externa AASHTO, texto de tabla pegado al numeral, remisiones
  sin encabezado propio localizable) — mismo rigor de spot-check ya
  aplicado a G/D/E. El Apéndice C-C (`C.23-*`) no se auditó numeral por
  numeral en esta pasada, queda fuera de alcance.
- **Ocho de diez títulos re-auditados con el método estricto (A, B, C,
  D, G, H, J, K) tuvieron algún hueco real, no auditorías cosméticas —
  solo I y E salieron completamente limpios. De esos ocho, seis ya
  están cerrados en verbatim completo (H, K, G, D, C, y el A.3.3 de A):
  solo quedan A (6 capítulos), B (4 secciones) y J (candidato a
  re-ingesta completa) con hueco real pendiente de cerrar.** Con esto
  se completa el barrido de los 11 títulos de la NSR-10 con este
  método — ningún título queda sin auditoría estricta al menos una
  vez.

**Hallazgo colateral de la auditoría de A, sin relación con huecos de
contenido**: `scripts/ingesta/nsr10/raw/capitulo_a.txt` (JSON local,
gitignored) describe una estructura de capítulos de Título A que **no
coincide con la real** (dice que A.4 es "Filosofía del diseño
sismorresistente", A.7 "Métodos de análisis sísmico", etc. — nombres
fabricados, con `"fecha_extraccion": "2024-01-15"` como placeholder, no
una extracción real del PDF). No se identificó que ningún script de
ingesta real lo use, pero queda como alerta si aparece referenciado en
el futuro — mismo espíritu que la nota de integridad ya existente sobre
el pipeline automático descartado.

**Nota real sobre calidad, ya corregida (2026-09-01)**: se encontró que
151 de 293 chunks (51.5%) de F.4.3/F.4.4/F.4.5 se truncaban en silencio al
buscar, por un bug real del splitter de troceo. Generalizado el chequeo a
**todo** `nsr10_chunks` (4.129 chunks medidos entonces): 493 (11.9%)
superaban el límite real de 128 tokens, con severidad muy dispareja —
Títulos K, B, J y A rotos al 100% de sus chunks; C, D, H y las 3
resoluciones SGSST en 0%. **Corregido el mismo día para todo el corpus**
(no solo F.4.3-F.4.5): verificado con una segunda auditoría independiente,
0% de chunks sobre el límite en la totalidad de `nsr10_chunks`. Esto
explica por qué los conteos de A/B/K de esta tabla son mucho más altos que
en versiones anteriores del documento — no es contenido nuevo, es el mismo
texto verbatim ya cargado, re-trocheado en piezas más pequeñas y
correctas. Script de auditoría reusable:
`scripts/mantenimiento/auditar_tokens_reales_corpus_completo.py`.

## Otros dominios (no cubiertos por este documento todavía)

RAS 2000 (motor AquAI), NTC/SGSST, ACI-318, interventoría, y las normas de
otros países del programa de replicabilidad (Perú E.030, Ecuador NEC-SE-DS)
tienen su propia procedencia documentada dentro de los docstrings de sus
scripts de ingesta respectivos (`scripts/ingesta/<dominio>/`), no
consolidada aquí. Candidato real para una futura extensión de este
documento si se vuelve a sentir el mismo dolor de "¿de dónde salió esto?".

## Tabla completa: los 87 archivos PDF de NSR-10 en Drive

Generada programáticamente desde `_catalogo_maestro_limpio.txt`
(2026-09-01) para minimizar error de transcripción manual sobre 87 filas.

| Archivo Drive | Drive file ID | Páginas Drive | Título(s) NSR-10 que cubre |
|---|---|---|---|
| `NSR-10-1-42.pdf` | `1FE_Q1ZkpTHi02qzTeFfYvZ8SiSG0c0nl` | 1-42 | Frente/preliminares del documento — no corresponde a un Título específico; resume y referencia TODOS los Títulos (A a K) |
| `NSR-10-43-54.pdf` | `18hLA1kxfXSYM6_BBEhZAGrQoIyLWoEKi` | 43-54 | Título A — Requisitos generales de diseño y construcción sismo resistente |
| `NSR-10-56-81.pdf` | `1oXm1kdtcMT2IE7ncFXmjKhybR3GEuh-g` | 56-81 | Título A |
| `NSR-10-81-94.pdf` | `1Z2rzll9ER-td_OGXzTUUPv1R68kAoNSL` | 81-94 | Título A |
| `NSR-10-95-105.pdf` | `1-KdJrOrUi_CTanS9XwJ7F1yDUGR83iuZ` | 95-105 | Título A |
| `NSR-10-106-115.pdf` | `1K7g_gGXO8hinr4_gIZxX31A-3tOxRx8A` | 106-115 | Título A |
| `NSR-10-116-123.pdf` | `10GAjgw1bkvL_o2joqtlofClkvDfLtNK-` | 116-123 | Título A |
| `NSR-10-124-128.pdf` | `1Uz5bf-lKMi5w4-2srJGTC_6jiuIxOiij` | 124-128 | Título A |
| `NSR-10-130-138.pdf` | `1-aUdCX_gFVIuooVNKrxu3xYB0WUlwo4p` | 130-138 | Título A |
| `NSR-10-140-154.pdf` | `1-QYd8J2UT0e9J0NQqp--2R4zVkoLhE9G` | 140-154 | Título A |
| `NSR-10-156-158.pdf` | `1iWkVUjD0g6FhAqFQu_uk2TdMbUwQ051O` | 156-158 | Título A |
| `NSR-10-160-166.pdf` | `1ADbcvU5sdKszsu1YBX_PQh7wa1EeW82y` | 160-166 | Título A |
| `NSR-10-168-181.pdf` | `1_rIFrq446kA5KvtuhkBAz3EChmnTZPju` | 168-181 | Título A |
| `NSR-10-183-190.pdf` | `17GTmdRIAURzlFrZlmhfK7ZA-APQ7JGvp` | 183-190 | Título A |
| `NSR-10-191-218.pdf` | `15ITURkjmFtqW2Ti-NEGaV63083QIby7t` | 191-218 | Título A |
| `NSR-10-219-221.pdf` | `1QfZAq-Iq7niauW_cj-CHqi31jG_r1zvV` | 219-221 | Título B — Cargas |
| `NSR-10-222-226.pdf` | `1fs3wrb8XUW1RQl15wgwlORir7aQOiFub` | 222-226 | Título B |
| `NSR-10-228-233.pdf` | `1JW5YAIgkKWDxx0zaEzKY9Q5ViW7L1uWv` | 228-233 | Título B |
| `NSR-10-234-237.pdf` | `10HxWiRfuK_hGoSEeLpKOThRJR4nQBFgL` | 234-237 | Título B |
| `NSR-10-238.pdf` | `1ZPWTQjhxPI-aX7WeDFoe3vhPEWxYG_0G` | 238 | Título B |
| `NSR-10-240-301.pdf` | `1ZLlTm7J__ucSvEt99qizpl3AocB12naL` | 240-301 | Título B |
| `NSR-10-302-306.pdf` | `1GG9xFIcyG40bRxL8BoiSGvFURSUDK5qA` | 302-306 | Título C — Concreto estructural |
| `NSR-10-307-326.pdf` | `15RTPZ-YuHm8Si_8bvqVbQa6mvp4d3PC7` | 307-326 | Título C |
| `NSR-10-327-335.pdf` | `1wLo8D1HHvJGZ-bwUjDX4padkPhHWwKlU` | 327-335 | Título C |
| `NSR-10-337-340.pdf` | `1TgJElqq6wHfw_z7iZ-9CiEDocumuTmYn` | 337-340 | Título C |
| `NSR-10-341-347.pdf` | `14FNc8gDURxzl0Tx5rIqiUG9-CkUNUlAV` | 341-347 | Título C |
| `NSR-10-349-351.pdf` | `1SM6LyDkFQwDCLS3oIphbIOFTwRTx1-5j` | 349-351 | Título C |
| `NSR-10-353-362.pdf` | `1Jv-QdqVSTXBTc6YryrOUr0oi7WL8cXKr` | 353-362 | Título C |
| `NSR-10-363-367.pdf` | `16naJnmO-oc43chhaMiwH8xN6nmK9p_ir` | 363-367 | Título C |
| `NSR-10-369-375.pdf` | `1oeZnIpg80Q43K7hgcbFrV8L8vQ9ZAe8w` | 369-375 | Título C |
| `NSR-10-377-387.pdf` | `1pWyvESW5zxlrSDmkf_Mq5mqLt-HaylGd` | 377-387 | Título C |
| `NSR-10-389-407.pdf` | `1GjwE7e-6PrdG-1oB_6a5pOACgcGPfP-B` | 389-407 | Título C |
| `NSR-10-409-419.pdf` | `1o1f3UOenS1jMjTFJCbxcoDSyaYlm0bVU` | 409-419 | Título C |
| `NSR-10-421-434.pdf` | `1rnyD279L75BRYj37RKmUonfFLZpbq6q_` | 421-434 | Título C |
| `NSR-10-435-438.pdf` | `11rUWagmqgIg0qUMQxm1psrakoWpq9AF3` | 435-438 | Título C |
| `NSR-10-439-442.pdf` | `1smeqckxouKNR1JgDrjlJslBD1M21-teE` | 439-442 | Título C |
| `NSR-10-443-448.pdf` | `1vOMV5i2zKWXLWKNEN6ydod-mBkvm28fY` | 443-448 | Título C |
| `NSR-10-449-452.pdf` | `1NhX0OSYA5f1bWRuw10mRk1urA50BZNTv` | 449-452 | Título C |
| `NSR-10-453-467.pdf` | `1xKquECuk3uMOqibbBHzaTR7fAmWhJ5rA` | 453-467 | Título C |
| `NSR-10-469-471.pdf` | `1WKY1RHabP5UtGN9DbOPDxdMrrQ4730DT` | 469-471 | Título C |
| `NSR-10-473-475.pdf` | `1uFLdvk6of90E4OUsFqVxYGFlV9Lx7TlT` | 473-475 | Título C |
| `NSR-10-477-501.pdf` | `1omqD-cbxdtW-EICMmIa6mcUp4XEGRqVu` | 477-501 | Título C |
| `NSR-10-503-508.pdf` | `1RIVSynbH1B9eqZfNDJib0j3N9RTMkpx0` | 503-508 | Título C |
| `NSR-10-509-524.pdf` | `1Ysawa0UrNH-iPB8F8R9jrigx_a8tSSH7` | 509-524 | Título C |
| `NSR-10-525-528.pdf` | `1HlPRfbeSYkMc4080ayr2KF3DgooD0DTm` | 525-528 | Título C |
| `NSR-10-529-531.pdf` | `1cr7WV4rl-huaujmoOc-25nyQ_q67k0Xk` | 529-531 | Título C |
| `NSR-10-533-535.pdf` | `1bS0Ky3YAjvS_ONBvu_ekkEgR2hjKyZAQ` | 533-535 | Título C |
| `NSR-10-537-550.pdf` | `1Ve_VbHxBMoOL9itWKtq5rgDylGJy6EA8` | 537-550 | Título C |
| `NSR-10-551-559.pdf` | `1oww3CM4OOoWROkEnAThYfWWmNC2Fzpft` | 551-559 | Título C (fin — ver hueco de la página 560 arriba) |
| `NSR-10-561-563.pdf` | `1eBPBon0MfXqWVoFoeSdQgxeMkSQ-BoKB` | 561-563 | Título C (Apéndice C-G en adelante) |
| `NSR-10-565-569.pdf` | `1LayIE7iRuAqEXNLMbEyz1EH8LCpM5BOn` | 565-569 | Título D — Mampostería estructural |
| `NSR-10-570-577.pdf` | `1f9qokn6yW9B3dIUIKeqAQ5KmTDRDOwL1` | 570-577 | Título D |
| `NSR-10-578-585.pdf` | `17GXpDJk_Pdc7_KTRR8xFssFZFGLRV97u` | 578-585 | Título D |
| `NSR-10-586-594.pdf` | `1D6qb6zw3DDNa9y6Z6d83iBCnFJQJyV6B` | 586-594 | Título D |
| `NSR-10-596-607.pdf` | `1yCB-S_xJv_5USUPcz5PPlGx68L7Ks-Rx` | 596-607 | Título D |
| `NSR-10-608-610.pdf` | `1QRiGCTDJcTdq6tpbE3GR02asFlzcNJ_m` | 608-610 | Título D |
| `NSR-10-612-613.pdf` | `1wJ2L1-tIdhDR-H3V0vQQK0oOO-zpi-zb` | 612-613 | Título D |
| `NSR-10-614-615.pdf` | `1p2bI1oS4LTLy_65mIsUr_EZ_aAvGRmQr` | 614-615 | Título D |
| `NSR-10-616.pdf` | `1VoXYeio7wnewSUPa4mASs-3mpWx1DZ9V` | 616 | Título D |
| `NSR-10-618-626.pdf` | `15EN9smBI-6Rdqvg_reL4TpguXl21RuHA` | 618-626 | Título D |
| `NSR-10-628-629.pdf` | `1ljmWcNf1DPpZ-AFNCPpu9uaIGTheMYtG` | 628-629 | Título D |
| `NSR-10-630-632.pdf` | `1BDBrYKhSyAHp_-hn8JTRuLYmxI5jM2_e` | 630-632 | Título D |
| `NSR-10-634-639.pdf` | `1jynQiUueUL2e4_zBXwrBdCHMh8JHlYQM` | 634-639 | Título D (fin) |
| `NSR-10-640-645.pdf` | `19Q4eHuWYfnqP2sOl2yA_sFlkpCHkdmJv` | 640-645 | Título E — Casas de 1 y 2 pisos |
| `NSR-10-647-650.pdf` | `1wXLPONpRf0jE5zrcLCdIdPd9eh6H1CvJ` | 647-650 | Título E |
| `NSR-10-651-656.pdf` | `15TEbUtDIBiBJOYWPV6gnhBv6wnz4wFfU` | 651-656 | Título E |
| `NSR-10-657-659.pdf` | `1esCTjzirgAYJo0Od6TkGmevawU30tBO2` | 657-659 | Título E |
| `NSR-10-661-662.pdf` | `1L0UTAwzdv7yORk-Qsy4U-UCTVXscxJ7r` | 661-662 | Título E |
| `NSR-10-663-668.pdf` | `1MmwioL9qcmrvwq_HCpivlVN1OVMqVPxe` | 663-668 | Título E |
| `NSR-10-669-673.pdf` | `1hOnhHtDKKVSBfJT2lcCP9qkrd2A4wVzQ` | 669-673 | Título E |
| `NSR-10-675-677.pdf` | `1Wi6mUKjduN2_TZlmIYCqqORAnL1O4qE7` | 675-677 | Título E (fin) |
| `NSR-10-681-712.pdf` | `1bqvzOLETovw6ePw9wSD0g5kFntS4nnuK` | 681-712 | Título F — Estructuras metálicas |
| `NSR-10-712-742.pdf` | `14t3dnpSmcqmLHvC-Qn5NOsQYmHlV99SB` | 712-742 | Título F |
| `NSR-10-743-770.pdf` | `15RBFpErGNE3cYaDsVGIYyVbwCu0NbdCF` | 743-770 | Título F |
| `NSR-10-771-800.pdf` | `1SdwrVt8VdwB-UgB74Rdk4aAvkDPPNdhj` | 771-800 | Título F |
| `NSR-10-801-840.pdf` | `1qqTLAZvH7iG4_qVQToeY_fgKwblxlffk` | 801-840 | Título F |
| `NSR-10-841-900.pdf` | `116BU3sPl1kJfQxYct7AaS2wf9-kMPzgF` | 841-900 | Título F |
| `NSR-10-901-980.pdf` | `14q4ylyJYB9H1IdLrdZ0X0crekxxbajmm` | 901-980 | Título F — F.3 (F-220 a F-299) |
| `NSR-10-982-1082.pdf` | `1Mr7auE8pwQ3IiQaZmLgVY5-Xdu7psmze` | 982-1082 | Título F — F.4.1 a F.4.7 (F-301 a F-401) ✅ verbatim completo |
| `NSR-10-1083-1182.pdf` | `1XeyIKw992yoJAD1kgjmYJ5qEA70R85Gi` | 1083-1182 | Título F — F.4.7 (cont.) + F.4.8 (F-402 en adelante) — descargado localmente, F.4.8 pendiente de ingestar |
| `NSR-10-1183-1283.pdf` | `1xuOZukeQsLIV957z59BK2eJqpZ5qu__b` | 1183-1283 | Título F — F.5 Aluminio + apéndices, cierra el Título F — pendiente, no descargado todavía |
| `NSR-10-1284-1320.pdf` | `13jdgOa7_r2qZfxaIOT-_0UY1FvAX0q1B` | 1284-1320 | Título G — Madera y Guadua |
| `NSR-10-1321-1400.pdf` | `1M5uohqWc7oyyoVudbJcMPZN-AiYm0CAa` | 1321-1400 | Título G |
| `NSR-10-1401-1450.pdf` | `1-EB1qUFpZCvgDtp0wOrB-cwAbvlL0O3-` | 1401-1450 | Título G (fin) + Título H — Estudios geotécnicos (inicio) |
| `NSR-10-1451-1500.pdf` | `1DSJnOYqJixF0Nm1ewOH1VBDFpKas4x-y` | 1451-1500 | Título H |
| `NSR-10-1501-1570.pdf` | `1AXhovLAquw_qFr0I4B7IiTGmuiIl24JP` | 1501-1570 | Título H (fin) + Título I — Supervisión técnica + Título J — Incendios + Título K — Complementarios (inicio, K.2 K-3 a K-8) |
| `NSR-10-1571-1625.pdf` | `1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z` | 1571-1625 | Título K (K.2 K-9 a K-12, K.3 completo, K.4.1, K.4.2, K.4.3 parcial hasta K.4.3.16 — **último archivo de la carpeta, K.4.3 bloqueado a partir de aquí**) |

## How to apply

Antes de arrancar una nueva pieza de ingesta verbatim de NSR-10, buscar el
título en la tabla de arriba para saber qué archivo de Drive descargar (o
confirmar que ya está en `scripts/ingesta/nsr10/raw/`, gitignored, antes de
volver a descargarlo). Actualizar la sección "Estado real de ingesta" de
este documento en el mismo commit que cierre un título — que no vuelva a
vivir solo en memoria privada.

## CI de cobertura (idea 6 del roadmap, 2026-09-16)

`packages/rag-audit-kit` (idea 1) extrajo a código reusable el método de
auditoría de numerales ya usado a mano título por título. El job
`test-cobertura-ingesta` de `ci.yml` usa ese paquete en cada PR para
verificar que la cobertura de cualquier título con un baseline guardado no
haya **retrocedido** — no exige que el corpus ya esté completo (no lo
está, ver tabla de arriba), solo que no pierda silenciosamente cobertura
que ya tenía (una migración mal escrita, un borrado accidental, un bug en
un script de ingesta).

Cuando se cierra o avanza sustancialmente un título, generar/actualizar su
baseline en el mismo commit:

```bash
python scripts/ingesta/generar_baseline_cobertura.py \
  --pdf scripts/ingesta/nsr10/raw/<archivo>.pdf \
  --prefijo "X." \
  --titulo "NSR-10 Título X — <nombre>" \
  --out scripts/ingesta/nsr10/cobertura_baseline/X.json
```

Hoy solo existe el baseline de Título I (generado al validar
rag-audit-kit) — el resto se agrega progresivamente, no retroactivamente
de una sola vez. El archivo baseline solo guarda etiquetas de numeral
("I.3.3.2"), nunca el texto normativo — no hay problema de derechos de
autor en commitearlo.
