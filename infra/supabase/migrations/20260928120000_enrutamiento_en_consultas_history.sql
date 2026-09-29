-- Columnas de auditoría del enrutamiento de dominio en consultas_history --
-- criterio de aceptación pendiente del issue #35 ("se puede loggear/auditar
-- qué ruta tomó cada consulta real, para poder medir después si el
-- enrutamiento acierta"). Ver packages/construdata/rag_multi_norma.py,
-- _route_con_metodo() -- misma idea de fondo que CLM-8B (Stanford/NVIDIA,
-- 2026-09-23), medido en scripts/evaluacion/comparar_enrutador_keyword_vs_contrastivo.py
-- (65.2% -> 95.7% el combinado).
--
-- dominio_enrutado: el motor/dominio real elegido para esta consulta
-- (ej. 'aquai', 'apu_precios', 'normativa_general').
-- metodo_enrutamiento: 'keyword' (encontró palabra clave), 'contrastivo'
-- (respaldo por embeddings, el keyword no encontró nada) o 'ninguno' (cayó
-- a normativa_general por defecto).
-- score_enrutamiento: similitud coseno del enrutador contrastivo cuando
-- aplica; NULL si el método fue 'keyword' (no produce un score comparable).

alter table public.consultas_history
  add column if not exists dominio_enrutado text,
  add column if not exists metodo_enrutamiento text,
  add column if not exists score_enrutamiento numeric;

comment on column public.consultas_history.dominio_enrutado is
  'Motor/dominio real elegido para esta consulta (aquai, apu_precios, normativa_general, etc.)';
comment on column public.consultas_history.metodo_enrutamiento is
  'Método que decidió el enrutamiento: keyword | contrastivo | ninguno';
comment on column public.consultas_history.score_enrutamiento is
  'Similitud coseno del enrutador contrastivo (0-1); NULL si el método fue keyword';
