-- Migracion real aplicada en produccion (Supabase project zuiwdtwkahkrrnnatniy)
-- Version: 20260625154152
-- Nombre: structai_sgsst_chunks
-- Reconstruida via supabase_migrations.schema_migrations.statements el 2026-08-20.
-- NO se re-ejecuta automaticamente: Supabase compara la version contra
-- schema_migrations remoto y solo aplica versiones nuevas. Esta version ya
-- existe en produccion -- este archivo es el registro versionado, no una
-- migracion pendiente.

CREATE TABLE IF NOT EXISTS public.ntc_chunks (
  id        bigserial PRIMARY KEY,
  norma     text NOT NULL,
  seccion   text NOT NULL,
  titulo    text,
  contenido text NOT NULL,
  embedding vector(1536),
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ntc_chunks_norma ON public.ntc_chunks (norma);

INSERT INTO public.ntc_chunks (norma, seccion, titulo, contenido) VALUES
('SGSST', 'Dec.1072 Art.2.2.4.6.3', 'Objeto del SGSST',
'El Sistema de Gestión de la Seguridad y Salud en el Trabajo (SG-SST) consiste en el desarrollo de un proceso lógico y por etapas, basado en la mejora continua e incluye la política, la organización, la planificación, la aplicación, la evaluación, la auditoría y las acciones de mejora con el objetivo de anticipar, reconocer, evaluar y controlar los riesgos que puedan afectar la seguridad y la salud en el trabajo.'),
('SGSST', 'Dec.1072 Art.2.2.4.6.8', 'Obligaciones del empleador en obra',
'Obligaciones del empleador en obra de construcción: 1) Definir, firmar y divulgar la política de SST. 2) Asignación de responsabilidades. 3) Gestión de peligros y riesgos: identificación, evaluación, valoración y controles. 4) Prevención y promoción de la salud. 5) Integración de SST con los demás sistemas de gestión. 6) Reportar accidentes a ARL dentro de 2 días hábiles de evento grave o mortal.'),
('SGSST', 'Dec.1072 Art.2.2.4.6.25', 'Trabajo en alturas',
'Trabajo en alturas (≥1.5m sobre nivel inferior) es trabajo de alto riesgo. Requisitos: 1) Permiso de trabajo en alturas firmado por coordinador certificado; 2) Trabajadores certificados Resolución 1178/2017; 3) Arnés de cuerpo completo certificado ANSI Z359; 4) Línea de vida resistencia mínima 22kN; 5) Doble eslinga con absorbedor de energía; 6) Inspección pre-operacional; 7) Plan de rescate documentado. Aplica en andamios, bordes de losa, escaleras, excavaciones.'),
('SGSST', 'Dec.1072 Tabla GTC-45', 'Matriz de riesgos en construcción',
'Niveles de riesgo GTC-45 para construcción: NIVEL I Muy Alto (No aceptable) — trabajo en alturas sin EPP, excavación sin entibado, operación de grúas sin certificación. Acción: Suspensión inmediata. NIVEL II Alto — demoliciones, espacios confinados, químicos peligrosos. Acción: Corrección urgente. NIVEL III Medio — corte con disco, compactación, soldadura. Acción: Mantener controles. NIVEL IV Bajo — labores manuales básicas.'),
('SGSST', 'Res.0312/2019 Art.3', 'Estándares mínimos SG-SST construcción',
'Resolución 0312/2019 estándares mínimos por tamaño: Empresas 11-50 trabajadores Riesgo IV-V: 21 estándares. Más de 50 trabajadores: 60 estándares. Estándares en: I) Recursos 10%; II) Gestión integral SG-SST 15%; III) Gestión salud 20%; IV) Gestión peligros y riesgos 30%; V) Gestión amenazas 10%; VI) Verificación 5%; VII) Mejoramiento 10%. Calificación mínima aprobatoria: 86% del total de estándares.'),
('SGSST', 'Res.0312/2019 EPP', 'EPP obligatorio en construcción',
'EPP obligatorio en construcción colombiana: Cabeza: casco clase B dieléctrico para riesgo eléctrico, clase A para resto. Ojos: gafas ANSI Z87.1. Oídos: protección auditiva si ruido >85dB en 8h. Respiratorio: N95 para polvo de sílice, respirador con filtro para químicos. Manos: guantes vaqueta o dieléctricos según actividad. Pies: botas puntera de acero + suela antideslizante. Cuerpo: overol, chaleco reflectivo en zonas vehiculares. Caídas: arnés cuerpo completo + eslinga doble + absorbedor energía (alturas ≥1.5m).'),
('SGSST', 'Res.0312/2019 Indicadores', 'Indicadores SGSST construcción',
'Indicadores de resultado SG-SST para construcción: IF (Índice Frecuencia) = (N° accidentes × 240.000) / Horas Hombre Trabajadas. IS (Índice Severidad) = (días perdidos × 240.000) / HHT. ILI (Índice Lesión Incapacitante) = IF × IS / 1000. Metas sector construcción Colombia: IF < 6, IS < 150. Reporte obligatorio a ARL mensualmente. Investigación de accidentes: dentro de 15 días hábiles. Conservar registros mínimo 20 años.');

GRANT SELECT ON public.ntc_chunks TO authenticated, anon;
