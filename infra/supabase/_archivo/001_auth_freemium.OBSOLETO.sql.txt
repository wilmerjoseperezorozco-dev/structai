-- ══════════════════════════════════════════════════════════════
-- MIGRACIÓN 001: Auth + Freemium + Trazabilidad
-- ══════════════════════════════════════════════════════════════

-- Perfil de usuario con plan
CREATE TABLE IF NOT EXISTS user_profiles (
  id                UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email             TEXT NOT NULL,
  nombre            TEXT,
  plan              TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free','pro','pro_anual')),
  apu_usados_mes    INT  NOT NULL DEFAULT 0,
  mes_actual        TEXT NOT NULL DEFAULT TO_CHAR(NOW(), 'YYYY-MM'),
  proyectos_count   INT  NOT NULL DEFAULT 0,
  wompi_customer_id TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Proyectos de cada usuario
CREATE TABLE IF NOT EXISTS proyectos (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  nombre      TEXT NOT NULL,
  descripcion TEXT,
  ciudad      TEXT DEFAULT 'Barranquilla',
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Trazabilidad: cada APU calculado queda registrado
CREATE TABLE IF NOT EXISTS trazabilidad_apu (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  proyecto_id      UUID REFERENCES proyectos(id) ON DELETE SET NULL,
  actividad_id     TEXT NOT NULL,
  descripcion      TEXT NOT NULL,
  unidad           TEXT NOT NULL,
  cantidad         NUMERIC(12,4) NOT NULL DEFAULT 1,
  precio_unitario  NUMERIC(14,2) NOT NULL,
  costo_total      NUMERIC(14,2) NOT NULL,
  pu_p05           NUMERIC(14,2),
  pu_p95           NUMERIC(14,2),
  norma_ref        TEXT,
  uuid_calculo     UUID NOT NULL,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Trazabilidad: consultas NSR-10/NTC
CREATE TABLE IF NOT EXISTS trazabilidad_consultas (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  proyecto_id  UUID REFERENCES proyectos(id) ON DELETE SET NULL,
  pregunta     TEXT NOT NULL,
  normas       TEXT[],
  respuesta    TEXT,
  fuentes      JSONB,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Reset mensual de contador APU
CREATE OR REPLACE FUNCTION reset_apu_mensual()
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  UPDATE user_profiles
  SET apu_usados_mes = 0, mes_actual = TO_CHAR(NOW(), 'YYYY-MM')
  WHERE mes_actual <> TO_CHAR(NOW(), 'YYYY-MM');
END;
$$;

-- Trigger: crear perfil al registrarse
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  INSERT INTO user_profiles (id, email)
  VALUES (NEW.id, NEW.email)
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- RLS
ALTER TABLE user_profiles       ENABLE ROW LEVEL SECURITY;
ALTER TABLE proyectos            ENABLE ROW LEVEL SECURITY;
ALTER TABLE trazabilidad_apu     ENABLE ROW LEVEL SECURITY;
ALTER TABLE trazabilidad_consultas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "own_profile"    ON user_profiles        FOR ALL USING (auth.uid() = id);
CREATE POLICY "own_projects"   ON proyectos            FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_apu_trace"  ON trazabilidad_apu     FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "own_query_trace" ON trazabilidad_consultas FOR ALL USING (auth.uid() = user_id);
