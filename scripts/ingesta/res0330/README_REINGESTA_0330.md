# Re-ingesta de la Resolución 0330/2017 (texto consolidado) — preparada, NO aplicada

Estado: 2026-11-08. Nada de lo descrito aquí se ha ejecutado contra producción.

## Por qué
El texto hoy servido por el RAG (`motor_chunks`, `norma_id` de `RES-0330-2017`, 287 filas = 255 artículos + 32 subchunks de 4 artículos largos) es una transcripción por IA de un PDF escaneado, anterior a las Resoluciones 799 y 908 de 2021. Numera distinto del texto consolidado oficial del Gestor Normativo de la CRA (265 artículos, de los cuales 74 llevan nota de modificación o corrección) y contiene valores distintos (p. ej. SUDS 25 % frente a 30 %). Detalle: `REPORTE_DIFERENCIAS_0330.md`.

## Hallazgo adicional
Salvo cuatro artículos, cada artículo actual tiene **un solo embedding**, y el modelo (`paraphrase-multilingual-MiniLM-L12-v2`) solo lee los primeros 128 tokens: lo que va después en artículos largos no influye en la búsqueda. La re-ingesta divide cada artículo en subchunks de ≤ 110 tokens, repitiendo el encabezado «ARTÍCULO N. TÍTULO.» en cada uno: 265 artículos → 1.344 subchunks, ninguno por encima de 128 tokens (simulación).

## Vigencia (verificada 2026-11-08, página del Ministerio de Vivienda)
0330/2017 → 0650/2017 (transitorio) → 0799/2021 (modifica; rige desde 21-dic-2021) → 0908/2021 (corrige la 0799) → 0548/2022 (transitorio de la 0799). Sin instrumentos posteriores listados; sin búsqueda exhaustiva en el Diario Oficial. La copia CRA es del 2026-08-08.

## Procedimiento (cada paso requiere aprobación del usuario)
1. `python preparar_reingesta_consolidada.py` — regenera `res0330_consolidada.json` y el reporte (solo lectura).
2. `python reingestar_consolidada.py` — simulación (por defecto).
3. `python reingestar_consolidada.py --respaldo` — copia las filas actuales a `%TEMP%\respaldo_motor_chunks_res0330.json`.
4. `python reingestar_consolidada.py --stage` — inserta las filas nuevas con `motor='aquai_stage'`. Si la búsqueda no filtra por motor, esas filas serían visibles unos minutos; contienen el texto correcto.
5. Verificar con consultas reales al RPC de búsqueda: SUDS debe dar 30 %; cámara de caída, Art. 155 con Tabla 20; derogatoria, Art. 258.
6. Ejecutar `swap_res0330.sql` (una transacción: aborta si hay menos de 250 filas stage; borra las actuales, promueve las nuevas y actualiza `normas_registro`).
7. Probar en producción `/consultar` con las tres preguntas del paso 5 y actualizar `docs/fuentes-normativas.md`.

## Riesgos y límites
- Los artículos citados en respuestas ya entregadas cambiarán de número (134 de los coincidentes por título tienen número distinto).
- La comparación por título es ruidosa con títulos repetidos; no sustituye la verificación del paso 5.
- El modelo de embeddings se carga localmente (~0,5 GB); correrlo con poca RAM libre puede fallar.
- Rollback: restaurar desde el respaldo del paso 3.
