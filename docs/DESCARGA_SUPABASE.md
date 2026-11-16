# Descarga de Supabase para seguir en el plan gratuito (2026-11-16)

El plan gratuito de Supabase tiene un tope de 500 MB. El 2026-11-16 la base estaba en **489 MB**; después de los cambios
de abajo quedó en **312 MB**. Cada número se midió en producción con consultas de solo lectura, antes y después de cada cambio.

| Cambio | Antes | Después | Cómo se verificó |
|---|---|---|---|
| 3 índices btree duplicados (IDEAM, INVIAS costos, INVIAS precios) | 489 MB | 466 MB | Mismas columnas y orden que su restricción UNIQUE; reversible (`20261116120000`) |
| `invias_actividad_insumos` vaciada | 466 MB | **312 MB** | Respaldo con conteo, md5 de los ids en orden y sumas exactas idénticos a la base; `TRUNCATE` con candado (`20261116130000`) |

## Respaldo de `invias_actividad_insumos`

- Archivo `invias_actividad_insumos_2026-11-16.jsonl.gz` (42,5 MB; 619.920 filas, `numeric` como texto exacto).
  sha256 `ee88ba88…4a38`.
- Copias: `C:/Users/wilme/dev/respaldos/supabase/` y `OneDrive/Respaldos-StructAI/supabase/`.
- Se escribe con `scripts/respaldo/respaldar_tabla.py` y se lee con `scripts/respaldo/leer_respaldo.py`, que verifica el
  sha256 antes de leer.
- `scripts/precios/p2_recomendador_apu.py` ahora lee del respaldo.
- `scripts/ingesta/invias_apu/cargar_invias_apu.py` escribe las líneas a JSONL.gz. Solo vuelve a Supabase con
  `INVIAS_INSUMOS_A_SUPABASE=true`.
- Nada en producción la leía: el chat usa `packages/motor-apu/data/composicion_invias_2026_1.json`.

## Lecturas repetidas que salieron de Supabase

- **Estadísticas de caudal IDEAM en RAM.** `ideam_caudal_estadisticas_mes` tiene una fila por estación y mes (11.310 filas,
  ~1 MB). Se carga entera una vez por instancia y se renueva cada 24 h, así que cada comparación de caudal deja de ser un
  viaje a Supabase. Se verificó que el resumen coincide exactamente con el recálculo desde el crudo: promedio, n, p90,
  mínimo y máximo, 0 diferencias.
- **Caché de respuestas RAG en dos niveles.** El nivel 1 es la memoria del proceso (`apps/api/cache.py`) y el nivel 2,
  Supabase. Un acierto de nivel 1 hace 0 viajes y uno de nivel 2 hace 1 lectura; antes eran 2, por el UPDATE del contador.

## Por qué pesaba `rag_cache_respuestas`

- 190 de sus 222 filas estaban vencidas y nunca se borraban.
- Cada fila pesaba ~9,8 KB porque guardaba `contextos_recuperados`: el texto completo de los trozos, que el endpoint ni
  siquiera devuelve.
- Ahora se guarda sin ese campo y las vencidas se purgan como máximo una vez por hora y por instancia.
- Las evaluaciones RAGAS, que sí usan ese campo, corren con la caché apagada. Antes podían medir respuestas guardadas en
  vez del pipeline: el mismo sesgo que ya se había corregido en el CI.

## Índices HNSW: no se comprimen por ahora

Medido en producción con un solo vector de consulta:

- **Con HNSW:** ~1,3 s, y devuelve solo **40** vecinos aunque `search_knowledge` pida 300 (`hnsw.ef_search = 40`). La
  parte semántica de la búsqueda híbrida trabaja con un grupo truncado.
- **Exacta secuencial en Postgres:** ~3,7 s, porque en este plan leer de disco es lento.
- **`halfvec`:** ahorraría ~15 MB pero obliga a cambiar las funciones de búsqueda, y no arregla el truncado.
- **Decisión:** llevar la búsqueda (vectorial más léxica) a la memoria de la API: ~24 MB de RAM, exacta, en milisegundos.
  Después borrar los HNSW (31 MB) y dejar la ruta RPC solo como respaldo.

## `ideam_caudal_historico` (63 MB): pendiente de decisión

- La API ya no la lee.
- Una vista materializada necesitaría conservar el crudo para refrescarse, así que no libera espacio. El equivalente que sí
  libera es la tabla resumen, que ya existe, se verificó y vive en RAM, más un respaldo del crudo como el de INVIAS.
- Los scripts fuera de línea que leen el crudo (ENSO, anomalías, inundaciones Caribe) pasarían a `leer_respaldo.py`.
