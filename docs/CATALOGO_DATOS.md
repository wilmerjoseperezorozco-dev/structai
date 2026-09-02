# Catálogo de datos — corpus RAG

Complementa `infra/supabase/SCHEMA.md` (tablas, RLS, funciones RPC —
leerlo primero para el panorama completo del schema). Este documento
cubre lo que `SCHEMA.md` no cubre: el significado columna por columna
de las 4 tablas del corpus RAG normativo, y la convención de `id` con
la que se nombra cada chunk — hoy repartida entre `CLAUDE.md`,
comentarios de scripts individuales y la memoria privada de sesiones de
Claude Code. Existe porque esa dispersión ya causó confusión real (ver
"Inconsistencias reales conocidas" abajo, encontradas auditando el
schema en vivo el 2026-09-01, no asumidas).

## Las 4 tablas del corpus RAG normativo

| Tabla | Filas (2026-09-01) | Tipo de `id` | Columna del texto | Columna de agrupación |
|---|---:|---|---|---|
| `nsr10_chunks` | 7.243 | `text` (slug descriptivo) | `texto` | `capitulo` |
| `ntc_chunks` | 294 | `bigint` (autoincremental) | `contenido` | `norma` |
| `motor_chunks` | 4.060 | `bigint` (autoincremental) | `contenido` | `motor` |
| `normas_registro` | 63 | `uuid` | — (es metadatos, no contenido) | `codigo` |

**Por qué la columna de texto se llama distinto según la tabla**
(`texto` en `nsr10_chunks`, `contenido` en las otras dos): decisión de
diseño de sesiones distintas, nunca unificada. No es un bug — el código
de cada motor/RAG ya sabe qué columna leer de qué tabla (`rag_multi_norma.py`)
— pero es la clase de detalle que solo vivía en la cabeza de quien
escribió cada `_ingest_*.py`, ahora está aquí.

### `nsr10_chunks` — columnas reales (confirmado por introspección directa, no por los scripts)

| Columna | Tipo | Nullable | Significado |
|---|---|---|---|
| `id` | `text` | NO | Slug descriptivo único, ver convención abajo |
| `capitulo` | `text` | NO | Nombre del Título/Capítulo NSR-10 en texto libre — **confirmado inconsistente**: 33 variantes de texto distintas existen hoy para referirse a los mismos títulos (ej. "Título C — Concreto Estructural" vs "Título C - Concreto Estructural", guion largo vs guion corto). No usar esta columna para agrupar/filtrar por título de forma confiable — usar el prefijo del `id` en su lugar (ver `_titulo_de_id()` en `scripts/mantenimiento/auditar_tokens_reales_corpus_completo.py`, ya escrita y probada para esto). |
| `seccion` | `text` | SÍ | Numeral/sección específica dentro del capítulo (ej. `"F.4.7.5.3.1"`), en texto libre — más específico que `capitulo`, menos normalizado |
| `titulo` | `text` | NO | Título corto/resumen de qué trata el chunk (para mostrar en UI o depurar) — **no confundir con "Título" de la norma** (A-K); pese al nombre, esta columna es más parecida a un subtítulo descriptivo |
| `texto` | `text` | NO | El contenido verbatim real. Lo que se le muestra al LLM y al usuario cuando el chunk se recupera |
| `embedding` | `vector(384)` | SÍ | Embedding de `paraphrase-multilingual-MiniLM-L12-v2` sobre `texto` — **debe medir ≤128 tokens reales del tokenizer del modelo**, no una estimación por caracteres (ver hallazgo real 2026-09-01 en `project_construdata_limite_tokens_embeddings`, memoria privada) |
| `created_at` | `timestamptz` | SÍ | Default `now()` |
| `norma_id` | `uuid` | SÍ | FK a `normas_registro.id`, para trazabilidad de vigencia (`estado_vigencia`/`derogada_por`) — **confirmado que solo 3.350 de 7.243 filas (46%) lo tienen poblado hoy**, no asumir que siempre está seteado |

### Convención real de `id` en `nsr10_chunks`

No hay un generador automático de ids — cada `_ingest_titulo_*.py` los
escribe a mano siguiendo (con variaciones históricas) este patrón:

```
NSR10-<Título>-<numeral_con_guiones_bajos>_<slug_descriptivo>[_p<n>][_q<n>|_r<n>]
```

- **`<Título>`**: una letra (`A`-`K`), a veces con número pegado sin
  guión para subcapítulos (`A2`, `A3`, `A4`, `A5`, `A6` — inconsistente
  con el resto, encontrado en la auditoría de hoy, no vale la pena
  normalizar retroactivamente todavía).
- **`<numeral_con_guiones_bajos>`**: el numeral real de la norma con
  puntos reemplazados por `_` (`F_4_7_5_3_1` = F.4.7.5.3.1).
- **`<slug_descriptivo>`**: texto libre corto que resume el contenido,
  útil para lectura humana en logs/SQL, no tiene reglas estrictas.
- **`_p<n>`**: sufijo de la primera generación de re-troceo por
  caracteres (`_resplit_titulo_f_f42_por_limite_tokens.py` y sus
  copias) — **método deprecado**, no usar como referencia para
  ingestas nuevas.
- **`_q<n>` / `_r<n>`**: sufijos del segundo paso de re-troceo con
  verificación REAL de tokens (`_sub_particionar_por_tokens_reales`,
  usado por primera vez en `_resplit_titulo_f_f46_por_limite_tokens.py`)
  — `_q` se usó en el re-trocheo específico de F.4.3/F.4.4/F.4.5,
  `_r` en el re-trocheo del resto del corpus completo (2026-09-01). No
  hay una regla semántica detrás de "q" vs "r", solo el script que lo
  generó — un mismo chunk puede terminar con más de un sufijo apilado
  (ej. `..._p1_q1`) si pasó por dos rondas de troceo en sesiones
  distintas.

**Prefijos especiales, no siguen el patrón de arriba**:
- `NSR10-ALCANCE-<Letra>`: un chunk de "alcance" resumen por título,
  de una ingesta muy temprana del proyecto.
- `NSR10-<Letra>-QA_<tema>`: chunks curados a mano ("respuesta de
  precisión"), escritos directamente para responder una pregunta
  frecuente con más densidad semántica que el texto verbatim normal —
  compiten en el ranking de retrieval con los chunks verbatim reales,
  a veces ganan cuando no deberían (ver el caso documentado en
  `project_structai_data_first_mejoras`, memoria privada, sección de
  verificación post-fix del 2026-09-01).
- `RES0312-2019-ART<n>...`, `RES4272-2021-...`, `RES5018-2019-...`:
  contenido de resoluciones SGSST, ingestadas con un patrón de id
  separado (por artículo, no por numeral NSR-10).
- `AIS2004-...`, `AIS410-23-...`, `BUILDCHANGE-2015-...`: referencias
  históricas de vulnerabilidad sísmica de vivienda (ver README,
  sección "Hacia dónde va esto").

**Heurística de lote sospechoso** (ya en `CLAUDE.md`, repetida aquí
porque es sobre todo una convención de `id`): el prefijo
`<Letra>-SEC<N>-*` marcó, en el único caso confirmado hasta hoy (A/H,
2026-09-01), un lote de contenido parafraseado presentado como si
fuera verbatim oficial — borrado, ver issue
[#38](https://github.com/wilmerjoseperezorozco-dev/structai/issues/38).
Si aparece este patrón en otro título, no confiar en el contenido sin
verificar contra el PDF fuente primero.

### `ntc_chunks` y `motor_chunks` — más simples, ids autoincrementales

Estas dos tablas no siguen la convención de `id` descriptivo de
`nsr10_chunks` — usan `bigint` autoincremental estándar de Postgres, sin
significado codificado en el número. La trazabilidad de dónde salió
cada fila vive en `seccion` (`ntc_chunks`) / `seccion` (`motor_chunks`)
y en los scripts de `scripts/ingesta/normativa_general/` y
`scripts/ingesta/motores/` respectivamente — no en el `id`.

## Inconsistencias reales conocidas (no corregidas todavía, documentadas para no repetir el hallazgo)

1. **Columna de texto con nombre distinto por tabla** (`texto` vs
   `contenido`) — ver arriba.
2. **Columna de agrupación con nombre y semántica distinta por tabla**
   (`capitulo` vs `norma` vs `motor`).
3. **`nsr10_chunks.capitulo` tiene 33 variantes de texto para los
   mismos títulos** — confirmado con SQL real
   (`select capitulo, count(*) from nsr10_chunks group by capitulo`)
   el 2026-09-01. No usar esta columna para agrupar de forma confiable.
4. **`nsr10_chunks.norma_id` solo está poblado en el 46% de las filas**
   — no asumir que la trazabilidad de vigencia vía `normas_registro`
   cubre todo el corpus.
5. **`id` es `text` descriptivo en `nsr10_chunks`, pero `bigint`
   autoincremental en `ntc_chunks`/`motor_chunks`** — ningún código de
   producción depende de que sean del mismo tipo, pero es una
   asimetría de diseño real que vale la pena tener presente antes de
   escribir un script nuevo que asuma "todos los ids son texto legible".

Ninguna de estas se corrigió en esta pasada — documentarlas es el
trabajo de "Definitions" (punto 2 del plan
`project_structai_data_first_mejoras`, memoria privada); corregirlas
de fondo (normalizar `capitulo`, unificar nombres de columna) sería un
trabajo de migración aparte, con su propio costo/riesgo, no asumido
aquí.

## How to apply

- Antes de escribir un script de ingesta nuevo para `nsr10_chunks`,
  seguir la convención de `id` de arriba — no inventar un formato
  nuevo sin razón.
- Antes de agrupar/filtrar por título de norma en SQL, usar el prefijo
  del `id` (o la lógica de `_titulo_de_id()`), no la columna
  `capitulo`.
- Al agregar una tabla nueva al corpus RAG, actualizar este documento
  Y `infra/supabase/SCHEMA.md` en el mismo commit — que la próxima
  inconsistencia de nombres de columna no vuelva a descubrirse por
  accidente meses después.
