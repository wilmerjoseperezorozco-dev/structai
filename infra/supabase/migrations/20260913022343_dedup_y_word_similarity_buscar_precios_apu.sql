-- Corrige 2 gaps reales de retrieval encontrados en la primera corrida de
-- scripts/evaluacion/ragas_precios.py (categoria "coloquial/sinonimos",
-- la mas debil del dataset: answer_relevancy 0.179, context_recall 0.000).
-- Ver memoria privada project_structai_ragas_precios_baseline (2026-09-07).
--
-- GAP 1 (verificado con SQL directo): "Cuanto cuesta hacer una vereda en
-- concreto?" -- 4 copias EXACTAS de "Rampas para puente peatonal en
-- concreto prefabricado de 35 MPa..." (mismo item_no del catalogo INVIAS
-- regional, cargado una vez por cada una de las 4 regiones INVIAS con
-- precio IDENTICO 1.302.032,25) empataban en score=0.3 y ocupaban 4 de los
-- 8 cupos del top_k, dejando las filas reales de "anden" (score 0.278,
-- SI relevantes) al final o fuera de rango. Mismo patron confirmado en
-- apu_insumos_referencia con "Maestro" (4 copias identicas, una por
-- region INVIAS, 4.377.262,50 cada una). No es ruido de una sola fila --
-- apu_insumos_referencia tiene 10.281 filas para solo 2.440 insumos
-- distintos, ~4.2x de duplicacion estructural del catalogo invias_regional.
--
-- GAP 2 (verificado con SQL directo): "Cuanto cobra un capataz de obra por
-- dia en Barranquilla?" -- la fila real "Maestro" (tabla
-- apu_insumos_referencia) nunca aparecia en el top_k pese a que
-- _expandir_sinonimos_precios() SI agrega "maestro de obra" a la consulta.
-- Causa raiz: similarity(doc, query) de pg_trgm compara el string ENTERO
-- contra el string ENTERO -- un nombre corto de catalogo ("Maestro", 7
-- caracteres) contra una pregunta larga en lenguaje natural (~80
-- caracteres) da un score bajisimo (similarity=0.138, confirmado con SQL
-- directo) aunque el termino aparezca literal en la consulta, porque el
-- denominador del trigram se domina por todos los trigramas de la
-- consulta que "Maestro" no tiene.
--
-- Este intento agrega word_similarity(doc, query) al greatest(...) de
-- score -- es la funcion de pg_trgm hecha especificamente para "documento
-- corto vs. consulta larga" (confirmado con SQL directo:
-- word_similarity('Maestro', <pregunta con sinonimos>) = 1.0). CORREGIDO
-- en la migracion siguiente (20260913023000) tras verificar con SQL
-- directo un efecto secundario real no previsto: word_similarity tambien
-- sube a score=1.0 nombres de actividad CORRUPTOS en
-- apu_precios_referencia (artefactos de extraccion de tabla del PDF
-- fuente, ej. "en concreto", "en en concreto concreto", "EN"), por
-- delante de coincidencias reales mas especificas -- no se revierte esta
-- migracion (deja historial real), se corrige con CREATE OR REPLACE en la
-- siguiente.
--
-- Fix aplicado aqui: (1) deduplicar filas con mismo tipo+nombre+precio
-- ANTES de aplicar el top_k (colapsa las copias identicas del catalogo
-- INVIAS regional sin perder informacion real -- precios genuinamente
-- distintos entre contratos reales se preservan intactos, la clave de
-- dedup incluye el precio); (2) sumar word_similarity() a los 4 calculos
-- de score y a sus filtros WHERE. No rompe el contrato de columnas que
-- consume rag_multi_norma.buscar_precios_apu() (incluye actividad_id,
-- agregada en 20260907120000_agregar_actividad_id_y_desglose_apu.sql).

CREATE OR REPLACE FUNCTION public.buscar_precios_apu(p_query text, p_limit integer DEFAULT 8)
 RETURNS TABLE(tipo text, nombre text, unidad text, precio numeric, precio_solo_mano_obra numeric, region text, tipo_fuente text, fecha_captura date, item_codigo text, categoria_fuente text, score real, actividad_id uuid)
 LANGUAGE sql
 STABLE
 SET search_path TO 'public', 'extensions'
AS $function$
  with q as (
    select
      to_tsquery('spanish', (select string_agg(lexeme, ' | ') from unnest(to_tsvector('spanish', p_query)))) as tsq,
      p_query as raw
  ),
  items_nacional_match as (
    select i.item_no, i.item_nombre, i.unidad,
           greatest(ts_rank_cd(to_tsvector('spanish', i.item_nombre), (select tsq from q)),
                    similarity(i.item_nombre, (select raw from q)),
                    word_similarity(i.item_nombre, (select raw from q))) as score
    from apu_items_nacional i, q
    where to_tsvector('spanish', i.item_nombre) @@ (select tsq from q)
       or similarity(i.item_nombre, (select raw from q)) > 0.2
       or word_similarity(i.item_nombre, (select raw from q)) > 0.4
  ),
  stats_nacional as (
    select d.item_no, count(*) as n_proveedores,
           min(d.precio_sin_iva) as precio_min, max(d.precio_sin_iva) as precio_max
    from apu_precios_nacional_detalle d
    where d.precio_valido and not d.precio_sospechoso
    group by d.item_no
  ),
  mejor_nacional as (
    select distinct on (d.item_no) d.item_no, d.precio_sin_iva, p.nombre as proveedor_nombre,
           p.departamento as proveedor_departamento, p.municipio as proveedor_municipio
    from apu_precios_nacional_detalle d
    join apu_proveedores_nacional p on p.id = d.proveedor_id
    where d.precio_valido and not d.precio_sospechoso
    order by d.item_no, d.precio_sin_iva asc
  ),
  candidatos as (
    select 'actividad'::text as tipo, actividad as nombre, unidad, precio_todo_costo as precio, precio_solo_mano_obra,
           region, tipo_fuente, fecha_captura, item_codigo, categoria_fuente,
           greatest(ts_rank_cd(to_tsvector('spanish', actividad), (select tsq from q)),
                    similarity(actividad, (select raw from q)),
                    word_similarity(actividad, (select raw from q))) as score,
           id as actividad_id
    from apu_precios_referencia, q
    where tipo_fuente <> 'catalogo_iad_mipymes'
      and (to_tsvector('spanish', actividad) @@ (select tsq from q)
       or similarity(actividad, (select raw from q)) > 0.2
       or word_similarity(actividad, (select raw from q)) > 0.4)
    union all
    select 'insumo', insumo, unidad, coalesce(precio_unitario_real, valor_unitario), null,
           region, tipo_fuente, fecha_captura, null, null,
           greatest(ts_rank_cd(to_tsvector('spanish', insumo), (select tsq from q)),
                    similarity(insumo, (select raw from q)),
                    word_similarity(insumo, (select raw from q))) as score,
           null::uuid
    from apu_insumos_referencia, q
    where to_tsvector('spanish', insumo) @@ (select tsq from q)
       or similarity(insumo, (select raw from q)) > 0.2
       or word_similarity(insumo, (select raw from q)) > 0.4
    union all
    select 'proveedor', producto || ' — ' || proveedor, presentacion_unidad, precio_cop, null,
           ciudad, 'proveedor_' || lower(replace(proveedor, ' ', '_')), fecha_captura, null, null,
           greatest(ts_rank_cd(to_tsvector('spanish', producto), (select tsq from q)),
                    similarity(producto, (select raw from q)),
                    word_similarity(producto, (select raw from q))) as score,
           null::uuid
    from apu_proveedores_catalogo, q
    where to_tsvector('spanish', producto) @@ (select tsq from q)
       or similarity(producto, (select raw from q)) > 0.2
       or word_similarity(producto, (select raw from q)) > 0.4
    union all
    select 'proveedor_nacional',
           im.item_nombre || ' — mejor precio real: ' || mn.proveedor_nombre,
           im.unidad, mn.precio_sin_iva, null,
           coalesce(
             case when mn.proveedor_municipio is not null then mn.proveedor_municipio || ', ' || mn.proveedor_departamento
                  when mn.proveedor_departamento is not null then mn.proveedor_departamento
             end,
             'Nacional'
           ),
           'catalogo_iad_mipymes_detalle', null, im.item_no::text,
           'Comparado entre ' || sn.n_proveedores || ' proveedores mipyme reales de todo el país (rango $' ||
             trim(to_char(sn.precio_min, 'FM999G999G999')) || '–$' || trim(to_char(sn.precio_max, 'FM999G999G999')) || ' COP sin IVA)',
           im.score,
           null::uuid
    from items_nacional_match im
    join stats_nacional sn on sn.item_no = im.item_no
    join mejor_nacional mn on mn.item_no = im.item_no
  ),
  dedup as (
    select distinct on (tipo, lower(trim(nombre)), precio)
           tipo, nombre, unidad, precio, precio_solo_mano_obra, region, tipo_fuente,
           fecha_captura, item_codigo, categoria_fuente, score, actividad_id
    from candidatos
    order by tipo, lower(trim(nombre)), precio, score desc, region
  )
  select tipo, nombre, unidad, precio, precio_solo_mano_obra, region, tipo_fuente, fecha_captura, item_codigo, categoria_fuente, score, actividad_id
  from dedup
  order by score desc
  limit p_limit;
$function$
