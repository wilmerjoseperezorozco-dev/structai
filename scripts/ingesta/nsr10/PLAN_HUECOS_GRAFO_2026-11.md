# Plan de ingesta de los huecos reales de la NSR-10 (issue #186)

Fecha: 2026-11-11. Ningún paso de este plan se ha ejecutado contra la base todavía.

## 0. Lo que cambió el diagnóstico

- El grafo `normas_referencias_cruzadas` marcaba 82 numerales citados como "sin destino", y un primer análisis (G2) concluyó que faltaban 80, 5 de ellos usados por motores. **Era un error de método:** se comparaba solo contra la columna `seccion` del chunk, y un chunk contiene varios numerales como encabezados dentro del texto.
- Con el índice por encabezados (`scripts/evaluacion/golden/e5_grafo/indice_numerales.py`: 5.141 numerales indexados), **72 de los 82 ya están en el corpus**, incluidos los 5 de los motores. **No se ingirió nada; habría duplicado contenido.**
- Para medir qué falta **de verdad** se cruzó la auditoría de páginas del 2026-11-08 (`docs/AUDITORIA_NSR10_PAGINAS_2026-11.json`, numerales que existen en el PDF y no aparecen en ningún texto) con el índice de hoy.

## 1. Inventario real de lo que falta (2026-11-11)

| Grupo | Numerales sin texto en el corpus | Causa | Fuente |
|---|---|---|---|
| **K.4** | **52** | **El PDF de Drive termina en K.4.3.16** (`NSR-10-1571-1625.pdf` es el último archivo de la carpeta) | **Falta conseguir la fuente oficial** del resto del Título K |
| K.3 | 9 | Por determinar (el PDF dice "K.3 completo") | `NSR-10-1571-1625.pdf` (ID `1M_lQD8NRDBHaB6pc_GE1n2l2sW34U88Z`) |
| I (I.1–I.4) | 9 | Por determinar | PDF del Título I (ver `docs/fuentes-normativas.md`) |
| H (H.2, H.3) | 6 | Por determinar | `NSR-10-1401-1450.pdf` |
| E (E.7, E.8) | 2 | Restos de la Etapa 2 del 2026-11-08 | PDF del Título E |
| B.6 | 1 | Por determinar | `NSR-10-240-301.pdf` (ID `1ZLlTm7J__ucSvEt99qizpl3AocB12naL`) |
| **Total** | **79** | | |

Citas del grafo que siguen sin destino aun con el índice: 11 numerales, 28 citas (A-4, B.6.5.6.3, D-1, B.6.3, H.6.2.5, H.7.5, F.3.10.1.4, F.5.19, A.1.9, C-11, H-6). A-4 ya está como tabla estructurada (`nsr10_apendice_a4_municipios`). F.5.19, A.1.9, C-11 y H-6 son sospechosos de ser lecturas erróneas del extractor del grafo.

Pendientes ya documentados en `docs/fuentes-normativas.md`, que se cruzan en la Fase 1: F.5.7.7–F.5.8 y apéndices F.5.A–F.5.F (Fase 13); B.3.4 condensado (no verbatim); B.4.3 y B.4.6–B.4.8; fracción del Apéndice C-F (página 560 inexistente en Drive).

## 2. Fases

### Fase 0: sin escribir en la base (se puede hacer ya)

1. Recalcular la resolución de las 1.354 citas del grafo con el índice (exacta / prefijo / sin destino) y reportar la diferencia.
2. Prueba de contrato motor → numeral con el índice: ningún motor puede citar un numeral NSR-10 que no tenga su encabezado en el corpus. Hoy pasa (0 huecos usados por motores).
3. Actualizar `docs/fuentes-normativas.md` con el inventario real de la sección 1.

### Fase 1: verificar contra el PDF (requiere bajar PDFs de Drive, con permiso del usuario por archivo)

Para cada grupo de la sección 1:
1. Descargar el PDF a `scripts/ingesta/nsr10/raw/` (gitignored), con nombre, ID de Drive y tamaño confirmados antes.
2. Confirmar que el numeral **existe** en el PDF y leer su encabezado y cuerpo; así se descartan las lecturas erróneas.
3. Verificar la vigencia (regla de `CLAUDE.md`: decretos modificatorios de la NSR-10 posteriores a 2010 que toquen ese numeral).

### Fase 2: ingesta (escribe en producción; cada lote se aprueba aparte)

Con el patrón existente (`_ingest_titulo_e_numerales_faltantes.py`):
- extracción de encabezado a encabezado con `base.extraer`;
- re-troceo por tokens reales con `_sub_particionar_por_tokens_reales`;
- ids `NSR10-<T>-<T>_<numeral>`;
- `upsert` con `on_conflict="id"`.

Orden por valor:
1. **B.6** (1) + B.6.5.6.3 si se confirma: viento, el más citado.
2. **H** (6): geotecnia; la usan geopot, geotecnia y licuación.
3. **E** (2): vivienda.
4. **I** (9) y **K.3** (9).
5. **K.4** (52): **bloqueado hasta conseguir la fuente.**

Cada lote se hace en dos pasos:
1. `--dry-run`, revisando a mano el texto extraído contra el PDF;
2. `upsert`, con la verificación posterior que exige `CLAUDE.md`: una consulta real de recuperación contra `match_nsr10_chunks` / `search_knowledge` por numeral, no solo que el upsert no falle.

Se actualizan `fuentes-normativas.md` y el índice en el mismo commit.

### Fase 3: la fuente del Título K

El texto restante de K.4 (desde K.4.3.17) no está en la carpeta de Drive. Opciones, a decidir por el usuario:
- obtener el PDF oficial completo del Título K de una fuente institucional (MinVivienda o la AIS);
- o documentarlo como hueco de fuente, igual que la página 560 del Apéndice C-F.

Antes de cualquier descarga se confirma la fuente oficial y su versión vigente.

## 3. Verificación final

- `auditoria_paginas.py` y `indice_numerales.py` vuelven a correr: los numerales ingeridos dejan de aparecer como faltantes.
- `test_integridad_dominios.py` y la prueba motor → numeral pasan.
- `test_rag_nsr10_regresion.py` (con el modelo local, `-m llm`) sin regresiones.

## Fase 1, Título B: resultados (2026-11-11)

- PDF `NSR-10-240-301.pdf` descargado a `raw/` (3.101.062 bytes, igual al tamaño en Drive).
- Los tres candidatos tienen **encabezado real** en el PDF: B.6.1.2 (pág. 1), B.6.3 Nomenclatura (pág. 3) y B.6.5.6.3 Categorías de exposición (pág. 8). Son huecos verdaderos.
- **Vigencia:**
  - Decreto 1711/2021: el anexo, leído completo, solo cambia la Figura B.6.4-1 del Título B.
  - Decreto 340/2012: cambia B.4.5-1, B.6.4-1 y B.6.4-2.
  - Ninguno de los dos toca estos numerales. **El Decreto 945/2017 está pendiente** (sin copia legible).
- **Hallazgo:** los chunks actuales de B.6.1 y de B.6.2–B.6.4 son **resúmenes parafraseados**, no verbatim (uno dice "PENDIENTE: … mapa de velocidad básica"). El hueco real de B.6 es el inicio completo del capítulo, no solo tres numerales.
- **Hallazgo de vigencia en producción:** el anexo del Decreto 1711 no está aplicado (Aa de Supía 0,15 en vez de 0,25; Figura B.6.4-1; Apéndice F.4-A ausente). Ver #189.
- Script `_ingest_titulo_b_b6_huecos_grafo.py`: dry-run por defecto. B.6.1.2 y B.6.5.6.3 están listos. B.6.3 queda pendiente de transcribir los subíndices a mano (21 símbolos desordenados por la extracción). **Sin upsert.**
