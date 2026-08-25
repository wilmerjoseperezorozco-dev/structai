# Schema de Supabase — StructAI

Proyecto Supabase: `zuiwdtwkahkrrnnatniy` ("StructAI"). Este documento se
generó por introspección directa contra la base de datos real (no a mano)
el **2026-08-20**, como parte de cerrar el drift entre el repo y la base de
datos de producción (ver `migrations/README.md` para el historial completo
de cómo se llegó a este estado). Las migraciones reales, con SQL exacto,
viven en `migrations/*.sql` — este archivo es un resumen legible, no la
fuente de la verdad (la fuente de la verdad es la base de datos y las
migraciones versionadas).

**Nota de mantenimiento**: los conteos de filas de abajo son un snapshot del
2026-08-20 — van a quedar desactualizados con el tiempo, por diseño (no se
actualizan a mano en cada sesión). Para el estado real y en vivo, usar el
endpoint público `GET /data-status` de `apps/api` en vez de este documento.

## Tablas principales

### Corpus RAG (normativa, público de solo lectura)

| Tabla | Filas (2026-08-20) | RLS | Propósito |
|---|---:|---|---|
| `nsr10_chunks` | 1.010 | SELECT público + ALL service_role | Chunks verbatim/resumen de NSR-10 (Títulos A-K), con `embedding vector(384)` |
| `ntc_chunks` | 294 | SELECT público + ALL service_role | Normas técnicas colombianas (NTC) + SGSST (Decreto 1072, Ley 1562, Res. 0312) |
| `motor_chunks` | 4.060 | SELECT público | Corpus propio por motor (AquAI/RAS 2000, GeoPot, Vías/INVIAS, Gerencia) |
| `normas_registro` | 63 | SELECT público + ALL service_role | Metadatos de vigencia/fuente por norma — no contenido, trazabilidad |

### Base de precios (público de solo lectura)

| Tabla | Filas | Propósito |
|---|---:|---|
| `apu_precios_referencia` | 4.566 | Actividades con precio de referencia (Construdata, contratos reales, INVIAS, IAD MIPYMES) |
| `apu_insumos_referencia` | 10.281 | Insumos (material/mano de obra/equipo) desglosados por actividad |
| `apu_proveedores_catalogo` | 24 | SKU con precio verificado, proveedores locales del Atlántico (Homecenter, Ferretería Samir) |
| `apu_proveedores_nacional` | 78 | Proveedores mipyme reales a nivel nacional (IAD MIPYMES, Colombia Compra Eficiente) |
| `apu_items_nacional` | 1.754 | Catálogo de materiales del IAD MIPYMES (item_no como PK estable) |
| `apu_precios_nacional_detalle` | 114.616 | Precio individual por proveedor nacional × item — permite comparar, no solo mediana |

### Datos de usuario (RLS por `auth.uid()`, CRUD completo)

| Tabla | Propósito |
|---|---|
| `profiles` | Perfil + plan (free/pro/enterprise) + contador de consultas del mes |
| `apu_calculations` | Historial de cálculos APU guardados por el usuario |
| `consultas_history` | Historial de chat (RAG) por usuario |
| `consultas` | (legado/en desuso — 0 filas) |
| `plan_analyses` | Análisis de planos subidos (motor de detección) |
| `compliance_checks` | Verificaciones de cumplimiento normativo |
| `agent_results` | Resultados de agentes/automatizaciones |
| `aquai_proyectos`, `geopot_proyectos`, `vias_proyectos`, `gerencia_proyectos` | Proyectos guardados por motor, uno por dominio |

### Otros

| Tabla | Filas | Propósito |
|---|---:|---|
| `noticias_relevantes` | 988 | Titular+resumen+link de noticias (sismos/normativa) vía Google News RSS — nunca el artículo completo |

## Índices de búsqueda

Búsqueda semántica (`nsr10_chunks`, `ntc_chunks`) usa **exact KNN** contra
`embedding vector(384)` (operador `<=>`, sin índice `ivfflat`) — el índice
aproximado que existía se eliminó el 2026-08-20 por recall bajo (ver
migración `drop_ivfflat_indexes_low_recall`); con el volumen actual de estas
tablas, un `seq scan` exacto es del orden de milisegundos y garantiza
recall 100%.

Búsqueda de precios (`apu_precios_referencia`, `apu_insumos_referencia`,
`apu_proveedores_catalogo`, `apu_items_nacional`) usa **texto completo en
español + trigram** (`gin (to_tsvector('spanish', ...))` + `gin (... 
gin_trgm_ops)`), no embeddings — más preciso para nombres de materiales
exactos que similitud semántica.

## Funciones / RPC principales

| Función | Uso |
|---|---|
| `match_nsr10_chunks(query_embedding, match_count, filter_caps, min_similarity)` | Búsqueda semántica sobre `nsr10_chunks` |
| `search_knowledge(...)` (2 overloads) | Búsqueda híbrida RRF sobre `nsr10_chunks`+`ntc_chunks`+`motor_chunks` — el overload con `p_motor` (el que llama `search()` en `rag_multi_norma.py`) usa lexemas con OR (`unnest(to_tsvector(...))` + `string_agg`, fix `20260809114440_fix_search_knowledge_or_tsquery.sql`), no `plainto_tsquery` AND-estricto |
| `match_peru_e030_chunks(...)` / `search_knowledge_peru_e030(...)` | Ídem para `peru_e030_chunks` — la segunda es la híbrida (RRF, OR lematizado vía `plainto_tsquery` reescrito a `\|`). Wireada al chat real desde 2026-08-25 — `rag_multi_norma.search_peru_e030()` la llama (motor `peru_e030`, ver `MOTOR_KEYWORD_MAP`/`ask_delegado()`) |
| `match_ecuador_nec_se_ds_chunks(...)` / `search_knowledge_ecuador_nec_se_ds(...)` | Ídem para `ecuador_nec_se_ds_chunks`. Wireada al chat real desde 2026-08-25 — `rag_multi_norma.search_ecuador_nec_se_ds()` (motor `ecuador_nec_se_ds`) |
| `search_nsr10_fulltext(query_text, match_count, filter_caps)` | Búsqueda de texto completo (respaldo/complemento de la semántica) |
| `buscar_precios_apu(p_query, p_limit)` | Búsqueda de precios (4 fuentes: actividades, insumos, proveedores locales, proveedores nacionales) |
| `save_apu_calculation(...)`, `save_consulta(...)`, `save_plan_analysis(...)` | Persistencia de historial por usuario |
| `handle_new_user()` | Trigger: crea fila en `profiles` al registrarse un usuario nuevo |
| `set_updated_at()` | Trigger genérico de `updated_at` |

## Row Level Security

RLS está **habilitado en todas las tablas de `public`**, sin excepción
(confirmado por introspección, no supuesto). Dos patrones:

1. **Corpus público de solo lectura** (`nsr10_chunks`, `ntc_chunks`,
   `motor_chunks`, `normas_registro`, `apu_*`, `noticias_relevantes`):
   política `SELECT` abierta a cualquiera (incluso sin autenticar), y
   `ALL` reservado a `service_role` para escritura (scripts de ingesta).
2. **Datos por usuario** (`profiles`, `apu_calculations`,
   `consultas_history`, `plan_analyses`, `compliance_checks`,
   `agent_results`, `*_proyectos`): CRUD completo (`SELECT`/`INSERT`/
   `UPDATE`/`DELETE`) filtrado por `auth.uid() = user_id` (o equivalente).

## Cómo mantener esto actualizado

- Cualquier cambio de schema nuevo debe aplicarse vía el MCP de Supabase
  (`apply_migration`) **y además** guardarse como archivo en
  `migrations/` con el mismo patrón `<version>_<nombre>.sql` — así el repo
  deja de acumular drift con la base de datos real.
- Este `SCHEMA.md` es un snapshot, no se regenera automáticamente — se
  actualiza a mano cuando el schema cambie de forma significativa (tabla
  nueva, RLS distinto), no en cada migración menor.
