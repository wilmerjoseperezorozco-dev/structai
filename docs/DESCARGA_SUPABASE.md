# Descarga de Supabase para seguir en el plan gratuito (2026-11-16)

El plan gratuito de Supabase tiene un tope de 500 MB. El 2026-11-16 la base estaba en **489 MB**; después de los cambios
de abajo quedó en **263,1 MB**. Cada número se midió en producción con consultas de solo lectura, antes y después de cada cambio.

| Cambio | Antes | Después | Cómo se verificó |
|---|---|---|---|
| 3 índices btree duplicados (IDEAM, INVIAS costos, INVIAS precios) | 489 MB | 466 MB | Mismas columnas y orden que su restricción UNIQUE; reversible (`20261116120000`) |
| `invias_actividad_insumos` vaciada | 466 MB | 312 MB | Respaldo con conteo, md5 de los ids en orden y sumas exactas idénticos a la base; `TRUNCATE` con candado (`20261116130000`) |
| `ideam_caudal_historico` vaciada | 312 MB | **263,1 MB** | Mismo protocolo que INVIAS (`20261116140000`) |

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

## Respaldo de `ideam_caudal_historico`

- Archivo `ideam_caudal_historico_2026-11-16.jsonl.gz` (3,3 MB; 352.022 filas). sha256 `7a412fee…52fe`.
- Mismas dos copias que INVIAS. Antes del `TRUNCATE` se verificó contra la base: conteo, md5 de las llaves en orden, suma
  exacta de `caudal_m3s` y md5 de las columnas de texto.
- Los scripts fuera de línea que leían el crudo (ENSO, anomalías, inundaciones Caribe) leen ahora el respaldo con
  `leer_respaldo.py`. La API usa la tabla resumen `ideam_caudal_estadisticas_mes`, que sigue en Supabase.

## Índice RAG local (búsqueda híbrida en memoria)

- `scripts/rag/construir_indice_local.py` hace **una** lectura de los 5 corpus (nsr10, ntc, motor, Perú E.030 y
  Ecuador NEC: 15.862 filas) y de `normas_registro`. Escribe `apps/api/datos_indice/indice_rag.npz` (26 MB) con su
  manifiesto y sha256. La carpeta está en `.gitignore`, pero entra en la imagen Docker por `.gcloudignore`.
- `--si-cambio` compara antes una huella barata de cada tabla (conteo y último `created_at`/`updated_at`). Si nada
  cambió, no vuelve a descargar.
- `infra/gcp/desplegar.sh` (paso 3/7) lo corre antes de Cloud Build y verifica el sha256. Después de desplegar la
  revisión candidata exige que `/health?deep=true` diga `indice_rag_local.activo = true`; si no, no mueve el tráfico.
  `SIN_INDICE_RAG=1` despliega sin índice.
- En cada arranque en frío Cloud Run carga el índice desde el disco de la imagen, sin egress de Supabase.
- La API (`packages/construdata/indice_local.py`) replica `search_knowledge` y `search_knowledge_<país>`:
  - semántica exacta (coseno sobre todos los vectores, sin el truncado a 40 de HNSW);
  - `to_tsvector('spanish')` emulado con el parser por defecto de Postgres y `snowballstemmer==2.2.0`, el mismo de PG17;
  - `ts_rank` en float32;
  - fusión RRF con `full join` por id.
- Si el archivo falta, el sha256 no cuadra o el índice lanza un error, la API vuelve a las RPC de Supabase.
  `RAG_INDICE_LOCAL=false` la apaga.

### Paridad medida contra Postgres (2026-11-16, solo lectura)

- **tsvector, documento por documento:**
  - Perú y Ecuador idénticos;
  - ntc: 1 documento distinto (un texto con forma de URL);
  - motor ≈ 25 de 4.060 y nsr10 ≈ 13 de 10.909 distintos.
  - Las diferencias que quedan son casos raros del parser de Postgres (rutas y URL mezcladas con tildes).
- **Búsqueda:** 23 consultas en los 5 corpus, con filtros por norma y por motor, consulta vacía y consulta sin sentido.
  `scripts/rag/paridad_top10.py` compara contra Postgres con búsqueda exacta, sin índices:
  - las consultas solo semánticas dan un top-10 idéntico;
  - parte léxica, 23/23 idénticas: mismo número de coincidencias, mismo multiconjunto de `ts_rank` y mismos ids por
    encima del corte de empates;
  - solapamiento medio del top-10 híbrido: **0,96**. Lo que falta es solo el orden entre documentos empatados: las RPC
    ordenan por `rrf_score` sin desempate y Postgres resuelve esos empates en orden arbitrario.
- La comparación contra HNSW en producción (`ef_search = 40`) no se midió. Por construcción, el índice local es
  exacto y HNSW es aproximado.

## Índices HNSW: no se comprimen por ahora

Medido en producción con un solo vector de consulta:

- **Con HNSW:** ~1,3 s, y devuelve solo **40** vecinos aunque `search_knowledge` pida 300 (`hnsw.ef_search = 40`). La
  parte semántica de la búsqueda híbrida trabaja con un grupo truncado.
- **Exacta secuencial en Postgres:** ~3,7 s, porque en este plan leer de disco es lento.
- **`halfvec`:** ahorraría ~15 MB pero obliga a cambiar las funciones de búsqueda, y no arregla el truncado.
- **Decisión:** llevar la búsqueda (vectorial más léxica) a la memoria de la API: ~26 MB, exacta, en milisegundos. Hecho
  arriba.
- **Los HNSW (31 MB) se mantienen** hasta validar el índice local en producción, después de fusionar #229 y #230.
  Mientras tanto son el respaldo de la ruta RPC. Borrarlos será otra migración, con su aprobación.
