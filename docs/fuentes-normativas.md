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
| C — Concreto estructural | 2.410 | Verbatim completo, auditado (0% de chunks truncados) |
| D — Mampostería estructural | 711 | **Casi completo, re-auditado con método estricto 2026-09-09**: 472 numerales reales identificados (`pypdf` sobre 13 PDF fuente, `NSR-10-565-569.pdf` a `NSR-10-634-639.pdf`, 70 páginas). **Solo 9 numerales hoja sin chunk propio** (~2%, el mejor resultado de los 7 títulos re-auditados hasta ahora, mejor que G) — confirmados con spot-check leyendo el PDF real: D.1.2.2 (Memorias), D.3.7.2.7 (Refrentado y ensayo de muretes), D.4.5.3 (Mortero de pega), D.4.5.4 (Mortero de inyección), D.5.1.6.1 (Resistencia a la tracción de la mampostería), D.5.4.3.1 (relación altura/espesor efectivo máxima 25), D.6.3.5 (diámetro mínimo de barras en cavidad), D.10.5.2.1 y D.10.6.2.1 (espesores mínimos de elementos/vigas de confinamiento). El resto del título sí está en verbatim granular real. |
| E — Casas de 1 y 2 pisos | 98 | **Verbatim completo, re-auditado con método estricto 2026-09-09**: 252 numerales reales identificados (`pdftotext` sobre los 8 PDF fuente, `NSR-10-640-645.pdf` a `NSR-10-675-677.pdf`; el último archivo llegó corrupto vía MCP dos veces seguidas — mismo número exacto de caracteres base64 truncado ambas veces — y se reconstruyó su contenido a partir del `contentSnippet` de metadata de Drive, que cubre E.9 completo). Los únicos "faltantes" del diff crudo fueron 10 encabezados de capítulo (E.1–E.9) que son padres de contenido ya cubierto — falsos positivos esperados, mismo patrón de A/B/G/H/D. **Segundo título (junto con I) en salir completamente limpio del método estricto.** Único hallazgo a anotar, no confirmado como hueco: el chunk `E.8.5.1.2` cita en su texto verbatim una remisión a "columnas de guadua en E.7.26.2", un numeral que no aparece como encabezado en ninguna de las 252 secciones reales extraídas (el capítulo E.7 real termina en E.7.9 a E.7.11) — confirmado con dos motores de extracción distintos (`pdftotext` y PyMuPDF) que coinciden byte a byte en el texto, así que no es ruido de OCR de un solo motor; probablemente un error tipográfico del documento fuente original (número de referencia cruzada mal escrito), no un hueco de ingesta — queda para verificación visual del PDF si se retoma. El conteo de 37→98 chunks refleja el mismo re-troceo por límite real de tokens ya aplicado al resto del corpus, no contenido nuevo. |
| F.1–F.4 (generalidades, acero laminado/armado/tubular, provisiones sísmicas, acero formado en frío) | 988 | **Verbatim completo** (F.4 cerrado 2026-09-01) |
| F.5.1–F.5.4.6 (Aluminio — generalidades, propiedades, principios de diseño, miembros: generalidades/esfuerzos/pandeo local/ablandamiento/vigas/tensión) | 403 | Verbatim completo |
| F.5.4.7 (Miembros a compresión) | 0 | **Pendiente** — la pieza más densa de F.5 (Tabla F.5.4.7-2, 18 tipos de sección con fórmulas propias cada uno), ya mapeada parcialmente pero no transcrita, mismo `NSR-10-1083-1182.pdf` ya descargado |
| F.5.4.8–F.5.4.9, F.5.5–F.5.8 + apéndices F.5.A–F.5.F (cierra el Título F) | 0 | Pendiente — requiere descargar `NSR-10-1183-1283.pdf` (id `1xuOZukeQsLIV957z59BK2eJqpZ5qu__b`, confirmado real, no descargado todavía) |
| G — Madera y Guadua | 1.176 | **Casi completo, re-auditado con método estricto 2026-09-09**: 488 numerales reales identificados (`pypdf` sobre `NSR-10-1284-1320.pdf` + `NSR-10-1321-1400.pdf` + páginas 1-38 de `NSR-10-1401-1450.pdf`, antes de donde arranca Título H en ese mismo archivo). **~24 numerales hoja sin chunk propio** (confirmados con spot-check leyendo el PDF real: G.2.1.6, G.6.7.7, G.6.7.11 y ~21 más, mayormente cláusulas puntuales de uniones clavadas y detalles constructivos) — bajo perfil de riesgo comparado con A/B/H/J, candidato a cierre rápido cuando se retome. No es del tipo "resumen condensado" como J — el resto del título sí está en verbatim granular real (~95% de cobertura numeral por numeral). |
| H — Estudios geotécnicos | 552 (48 originales + 87 H.3.3/H.4 + 47 H.5 + 45 H.6 + 64 H.7 + 80 H.8 + 101 H.9 + 80 H.10) | **VERBATIM COMPLETO (H.1-H.10), cerrado el mismo día 2026-09-07** tras la auditoría numeral por numeral que confirmó el hueco original (181 encabezados reales identificados, partió de ~18% cubierto). Cerrados en la misma sesión: **H.3.3 (cierre de H.3), H.4 (Cimentaciones), H.5 (Excavaciones y estabilidad de taludes), H.6 (Estructuras de contención), H.7 (Evaluación geotécnica de efectos sísmicos/licuación), H.8 (Sistema constructivo), H.9 (Condiciones geotécnicas especiales: suelos expansivos/dispersivos/colapsables, efectos de la vegetación) y H.10 (Rehabilitación sísmica de edificios: amenazas sismo-geotécnicas y reforzamiento de cimentaciones)** — todos re-trocheados con verificación real de tokens, 0 sobre el límite desde el primer intento en cada pieza, sin excepción. Verificado con `ask()` real en cada pieza: 20 de 22 preguntas nuevas PASSED con cita exacta (H.9 fue 4/4 limpio); 1 falló por retrieval (límite de giro H.4.9.4, chunk corto) y 1 se descartó por diseño de pregunta defectuoso (Tabla H.6.4-1 no tiene coeficientes Kp numéricos); un caso adicional (Tabla H.4.9-1) reveló que el LLM confunde filas adyacentes de tablas densas — mismo patrón ya documentado en F.5.2/F.5.4.3/F.5.4.4. **Hallazgo real en H.8**: al verificar la ecuación de pandeo H.8.4-1 (pilotes), el LLM cita la fórmula correctamente pero responde "el Título H no especifica un valor numérico concreto para el factor de seguridad" pese a que el mismo chunk verbatim transcrito dice literalmente "F_S se tomará igual a 3.0" — un miss real de síntesis/generación, no de retrieval. **Hallazgo real en H.10**: al preguntar la profundidad de nivel freático para descartar licuación (H.10.2.2.2, valores reales: 10 m bajo el cimiento o 15 m bajo la superficie), el LLM cita el artículo correcto pero no surge los valores numéricos específicos — mismo patrón de miss de síntesis. Ninguno de los dos se agregó al dataset de regresión para no forzar un caso fallido como si pasara. Los PDF fuente ya están descargados en `scripts/ingesta/nsr10/raw/` (`NSR-10-1401-1450.pdf`, `NSR-10-1451-1500.pdf`, `NSR-10-1501-1570.pdf`). 13 chunks no-verbatim (de lo poco que existía antes) borrados el 2026-09-01 — issue [#38](https://github.com/wilmerjoseperezorozco-dev/structai/issues/38) sigue abierto (era sobre A y H; con H ya verbatim completo, queda pendiente solo por Título A) |
| I — Supervisión técnica | 62 | **Verbatim completo, confirmado con auditoría estricta 2026-09-09** — 63 numerales reales identificados (`pypdf` sobre `NSR-10-1501-1570.pdf`, páginas I-1 a I-28), 62 con chunk real y contenido verbatim verificado a mano (el numeral restante, I.1.5.1, resultó ser un falso positivo del regex de extracción, no un numeral real del documento). Único de los 7 títulos re-auditados con este método que salió limpio de entrada. |
| J — Protección contra incendios | 49 | **INCOMPLETO — hueco real grande confirmado 2026-09-09** (mismo método `pypdf` que A/B/H: 159 numerales reales identificados en `NSR-10-1501-1570.pdf`, páginas J-1 a J-32). A diferencia de A/B/H (capítulos enteros sin ningún chunk), aquí el problema es que **casi todo el título está condensado en resumen, no verbatim** — mismo patrón "resumen disfrazado de completo" ya visto en A.3.3/B.3.4, pero a escala de un título completo: ej. J.3.3.3 tiene 13 sub-numerales reales (tipos de edificación eximidos de resistencia al fuego) y solo 4 están parafraseados en 3 chunks cortos (300-350 caracteres); J.4.3.1 a J.4.3.9 (sistemas de detección/extinción — rociadores, hidrantes, alarmas — contenido técnico de uso diario) están condensados en solo 4 chunks de 150-410 caracteres cada uno. J.2.1 y J.3.1 no aparecen en ningún chunk. Candidato de re-ingesta verbatim completa, no solo relleno de huecos puntuales — issue nuevo pendiente de crear. |
| K — Otros requisitos complementarios (K.1–K.4.3) | 416 | **PARCIAL — corrige un hallazgo real anterior.** K.1, K.2, K.3, K.4.1, K.4.2 y K.4.3.1-K.4.3.9 sí están en verbatim completo, confirmado con auditoría estricta 2026-09-09 (412 numerales reales identificados en `NSR-10-1501-1570.pdf` + `NSR-10-1571-1625.pdf`). **Pero "K.4.3 completo" (afirmado en una versión anterior de esta fila, 2026-09-07) era incorrecto**: faltan **K.4.3.10 a K.4.3.16** (Vidrio estructural y de piso, Revestimiento con vidrios, Vidrios en cubierta, y 3 numerales de normas técnicas referenciadas — Colombianas, ASTM, Otras) — 7 numerales reales sin ningún chunk, visibles en las páginas 53-55 del mismo PDF `NSR-10-1571-1625.pdf` ya descargado (el último archivo de esa carpeta de Drive, así que este es el final real del capítulo, no un límite artificial de qué se descargó). |

**Título F, total real hoy**: 1.391 chunks (988 + 403) de los ~2.200-2.400
estimados para cerrarlo por completo — sigue siendo, con diferencia, el
título con más volumen de todos.

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
- **Título A — auditado 2026-09-07, hueco real confirmado también, aún
  parcialmente sin cerrar** (ver fila de arriba): 189 de 542 numerales
  (35%) sin chunk, incluyendo 6 capítulos completos (A.1/A.7/A.8/A.11/
  A.12/A.13). El capítulo de irregularidades (A.3.3, no A.3.6 como se
  creyó al principio) ya se cerró en verbatim completo el mismo día.
- **Título B — auditado 2026-09-08, hueco real confirmado también, aún
  sin cerrar** (ver fila de arriba): 7 secciones completas sin chunk
  (B.3.3 cargas muertas mínimas, B.3.5 equipos fijos, B.3.6
  consideraciones especiales, B.4.3 carga parcial, B.4.6 puente grúas,
  B.4.7 efectos dinámicos, B.4.8 empozamiento de agua y granizo).
  Menos grave en proporción que A y H originalmente, pero B.3.3
  (cargas muertas mínimas) es una tabla de referencia de uso diario en
  la práctica, no solo un detalle administrativo.
- **Título I — re-auditado 2026-09-09, único de 6 títulos re-auditados
  que salió limpio** (ver fila de arriba): 62 de 63 numerales reales con
  chunk verbatim confirmado, el numeral restante era un falso positivo
  del regex de extracción.
- **Título J — re-auditado 2026-09-09, hueco real grande confirmado**
  (ver fila de arriba): no es un caso de "capítulos enteros sin chunk"
  como A/B/H, sino que **casi todo el título está condensado en resumen
  parafraseado, no verbatim** — mismo patrón de A.3.3/B.3.4 pero a escala
  de un título completo (159 numerales reales, 49 chunks condensados).
  Candidato a re-ingesta verbatim completa.
- **Título K — re-auditado 2026-09-09, hueco real puntual confirmado,
  corrige un hallazgo anterior** (ver fila de arriba): K.1-K.4.2 y
  K.4.3.1-9 sí están completos, pero K.4.3.10-16 (7 numerales, incluidos
  3 de normas técnicas referenciadas) nunca se ingestaron pese a que la
  fila de esta misma tabla decía "K.4.3 completo" desde 2026-09-07.
- **Título G — re-auditado 2026-09-09, hueco real pequeño confirmado**
  (ver fila de arriba): ~24 de 488 numerales reales (~5%) sin chunk
  propio, todos cláusulas puntuales, no capítulos ni resúmenes
  masivos — el título con mejor cobertura de los 6 re-auditados después
  de I.
- **Título D — re-auditado 2026-09-09, hueco real muy pequeño
  confirmado** (ver fila de arriba): solo 9 de 472 numerales reales
  (~2%) sin chunk — el mejor resultado de los 7 títulos re-auditados
  hasta ahora, incluso mejor que G. Ninguno es contenido crítico
  aislado (mortero de pega/inyección ya están cubiertos por remisión a
  D.3.4/D.3.5, que sí existen).
- **Título E — re-auditado 2026-09-09, salió limpio** (ver fila de
  arriba): 252 numerales reales identificados, todos con chunk verbatim
  confirmado; los 10 "faltantes" del diff crudo eran encabezados de
  capítulo (padres de contenido ya cubierto). Único hallazgo a anotar
  sin confirmar: una remisión cruzada interna a "E.7.26.2" que no
  corresponde a ningún encabezado real extraído — posible error
  tipográfico del documento original, no tratado como hueco de ingesta.
- **Siete de nueve títulos re-auditados con el método estricto (A, B, H,
  J, K, G, D) resultaron tener algún hueco real, no auditorías
  cosméticas.** I y E salieron completamente limpios. Solo Título C
  sigue pendiente de esta auditoría estricta — dado el patrón de 7 de 9,
  la expectativa razonable es que también tenga huecos reales, no lo
  contrario.

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
