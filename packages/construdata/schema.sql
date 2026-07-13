-- ══════════════════════════════════════════════════════════════
-- CONSTRUDATA 2026 — SCHEMA SUPABASE
-- Base de precios construcción Barranquilla
-- ══════════════════════════════════════════════════════════════

-- 1. MATERIALES CONSTRUDATA
CREATE TABLE IF NOT EXISTS construdata_materiales (
  id           TEXT PRIMARY KEY,          -- CD-MAT-001
  codigo       TEXT UNIQUE NOT NULL,
  descripcion  TEXT NOT NULL,
  unidad       TEXT NOT NULL,
  precio_cop   NUMERIC(12,2) NOT NULL,    -- precio sin IVA
  precio_iva   NUMERIC(12,2),             -- precio con IVA
  variacion_pct NUMERIC(5,2) DEFAULT 8.0, -- variación ±% para Monte Carlo
  capitulo     TEXT,                       -- A, B, C, D...
  subcapitulo  TEXT,
  proveedor    TEXT,
  ciudad       TEXT DEFAULT 'Barranquilla',
  fuente       TEXT DEFAULT 'Construdata',
  mes_ref      TEXT DEFAULT '2026-01',
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 2. MANO DE OBRA
CREATE TABLE IF NOT EXISTS construdata_mano_obra (
  id                  TEXT PRIMARY KEY,
  categoria           TEXT NOT NULL,        -- Oficial, Ayudante, Maestro...
  salario_dia_cop     NUMERIC(10,2) NOT NULL,
  factor_prestaciones NUMERIC(6,4) DEFAULT 1.6084,
  costo_real_dia      NUMERIC(10,2) GENERATED ALWAYS AS
                        (salario_dia_cop * factor_prestaciones) STORED,
  smmlv_base          NUMERIC(12,2),        -- SMMLV vigente
  ciudad              TEXT DEFAULT 'Barranquilla',
  mes_ref             TEXT DEFAULT '2026-01',
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- 3. EQUIPO Y MAQUINARIA
CREATE TABLE IF NOT EXISTS construdata_equipo (
  id            TEXT PRIMARY KEY,
  descripcion   TEXT NOT NULL,
  unidad        TEXT NOT NULL,              -- hr, dia, mes
  valor_hora    NUMERIC(10,2) NOT NULL,
  valor_dia     NUMERIC(10,2) GENERATED ALWAYS AS (valor_hora * 8) STORED,
  incluye       TEXT,                       -- depreciación, mantenimiento, combustible
  ciudad        TEXT DEFAULT 'Barranquilla',
  mes_ref       TEXT DEFAULT '2026-01',
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 4. APU GUARDADOS (resultados del motor)
CREATE TABLE IF NOT EXISTS apu_resultados (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actividad_id    TEXT NOT NULL,
  descripcion     TEXT NOT NULL,
  unidad          TEXT NOT NULL,
  costo_materiales NUMERIC(14,2),
  costo_mano_obra  NUMERIC(14,2),
  costo_equipo     NUMERIC(14,2),
  costo_directo    NUMERIC(14,2),
  aiu_pct          NUMERIC(5,2),
  precio_unitario  NUMERIC(14,2),
  pu_mean          NUMERIC(14,2),
  pu_std           NUMERIC(14,2),
  pu_p05           NUMERIC(14,2),
  pu_p95           NUMERIC(14,2),
  incertidumbre_pct NUMERIC(5,2) GENERATED ALWAYS AS
    (CASE WHEN pu_mean > 0 THEN ROUND((pu_std / pu_mean * 100)::NUMERIC, 1) ELSE 0 END) STORED,
  capitulo        TEXT,
  norma_ref       TEXT,
  ciudad          TEXT DEFAULT 'Barranquilla',
  fuente_precios  TEXT DEFAULT 'Construdata 2026',
  usuario         TEXT,
  proyecto        TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 5. PROYECTOS (presupuesto completo)
CREATE TABLE IF NOT EXISTS proyectos (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre      TEXT NOT NULL,
  descripcion TEXT,
  ciudad      TEXT DEFAULT 'Barranquilla',
  normas      TEXT[] DEFAULT ARRAY['NSR-10','NTC','SISO'],
  usuario     TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 6. PRESUPUESTO (capítulos × items × APU)
CREATE TABLE IF NOT EXISTS presupuesto_items (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proyecto_id  UUID REFERENCES proyectos(id) ON DELETE CASCADE,
  capitulo     TEXT NOT NULL,
  actividad    TEXT NOT NULL,
  apu_id       UUID REFERENCES apu_resultados(id),
  cantidad     NUMERIC(14,3) NOT NULL,
  unidad       TEXT,
  precio_unit  NUMERIC(14,2),
  subtotal     NUMERIC(16,2) GENERATED ALWAYS AS (cantidad * precio_unit) STORED,
  subtotal_mc  NUMERIC(16,2),              -- usando pu_mean de Monte Carlo
  orden        INT DEFAULT 0,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 7. GRAFO DE DEPENDENCIAS (NSR-10 + NTC + Seg. Ind.)
CREATE TABLE IF NOT EXISTS knowledge_graph (
  id          TEXT PRIMARY KEY,            -- SEC_A1, NTC_001, SEG_001
  tipo        TEXT NOT NULL,               -- norma, seccion, articulo, formula, tabla
  norma       TEXT NOT NULL,               -- NSR-10, NTC-6001, SISO, RETIE
  capitulo    TEXT,
  titulo      TEXT NOT NULL,
  texto       TEXT NOT NULL,
  embedding   vector(1536),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS knowledge_edges (
  source_id  TEXT REFERENCES knowledge_graph(id),
  target_id  TEXT REFERENCES knowledge_graph(id),
  relacion   TEXT NOT NULL,                -- depende_de, referencia, complementa, restriccion
  peso       NUMERIC(4,2) DEFAULT 1.0,
  PRIMARY KEY (source_id, target_id, relacion)
);

-- ÍNDICES
CREATE INDEX IF NOT EXISTS idx_mat_capitulo  ON construdata_materiales(capitulo);
CREATE INDEX IF NOT EXISTS idx_mat_ciudad    ON construdata_materiales(ciudad);
CREATE INDEX IF NOT EXISTS idx_apu_act       ON apu_resultados(actividad_id);
CREATE INDEX IF NOT EXISTS idx_pres_proy     ON presupuesto_items(proyecto_id);
CREATE INDEX IF NOT EXISTS idx_kg_norma      ON knowledge_graph(norma);
CREATE INDEX IF NOT EXISTS idx_kg_embed      ON knowledge_graph USING ivfflat(embedding vector_cosine_ops) WITH (lists=10);

-- VISTA: Presupuesto resumen por capítulo
CREATE OR REPLACE VIEW v_presupuesto_capitulos AS
SELECT
  p.nombre AS proyecto,
  pi.capitulo,
  COUNT(*) AS actividades,
  SUM(pi.subtotal)::NUMERIC(16,2) AS total_det,
  SUM(pi.subtotal_mc)::NUMERIC(16,2) AS total_mc
FROM presupuesto_items pi
JOIN proyectos p ON p.id = pi.proyecto_id
GROUP BY p.nombre, pi.capitulo
ORDER BY p.nombre, pi.capitulo;
