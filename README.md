# StructAI — Plataforma de IA para ingeniería civil en Colombia

SaaS freemium para ingenieros civiles y maestros de obra: cálculos de ingeniería con trazabilidad normativa real (NSR-10, NTC, RAS 2000/Res. 0330, INVIAS, SGSST) y consultas por IA que citan norma, capítulo/artículo y fuente — nunca inventa contenido normativo.

`Construdata` es el nombre interno del repositorio/código; **StructAI** es la marca pública.

## Los 6 motores

| Motor | Dominio | Paquete |
|---|---|---|
| **APU** | Análisis de Precios Unitarios — catálogo Construdata 2026 Barranquilla | `packages/motor-apu` |
| **Estructural** | Deformación de vigas (Euler-Bernoulli), pandeo de columnas (Euler/Johnson), incertidumbre Monte Carlo | `packages/motor-deformacion` |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos) | `packages/motor-aquai` |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica NSR-10 | `packages/motor-geopot` |
| **Vías** | Diseño vial INVIAS: geometría, pavimentos, mantenimiento, topografía, NTC de materiales | `packages/motor-vias` |
| **Gerencia** | Earned Value Management (PMBOK) + ML predictivo sobre avance de obra | `packages/motor-gerencia` |

Cada motor expone su propio router FastAPI (`/apu`, `/deform`, `/aquai`, `/geopot`, `/vias`, `/gerencia`), su propia tabla en Supabase, y su propio corpus RAG en `motor_chunks` — todos comparten el mismo backend y la misma base de datos.

## Estructura del monorepo

```
construdata/
├── apps/
│   ├── web/       → Next.js 14 (App Router) + PWA        → Vercel (desplegado)
│   ├── native/     → React Native + Expo Router (Fase 0)   → sin publicar aún
│   └── api/        → FastAPI, los 6 motores + RAG          → sin desplegar aún (Render/Cloud Run)
├── packages/
│   ├── motor-apu/, motor-deformacion/, motor-aquai/,
│   │   motor-geopot/, motor-vias/, motor-gerencia/  → cada uno con su pyproject.toml
│   ├── shared-types/  → tipos TS + cliente API compartidos entre web y native
│   ├── construdata/   → schema SQL + pipeline de ingesta RAG general (NSR-10/NTC/SGSST)
│   ├── knowledge/     → PDFs fuente de NSR-10
│   ├── ai-gateway/    → gateway multi-proveedor (Claude/Gemini/OpenAI) — experimental
│   └── bim-intelligence/ → IFC + Qdrant — experimental, no conectado al producto
├── infra/supabase/  → estado real de las migraciones (ver infra/supabase/migrations/README.md)
└── .github/workflows/  → CI: lint + tsc, tests Python por motor, build web
```

**Nota sobre el workspace:** `package.json` raíz declara `"workspaces": ["apps/native", "packages/shared-types"]` — deliberadamente acotado. `apps/web` y `apps/api` se despliegan de forma standalone (no dependen del workspace), así que quedan fuera de esa lista a propósito.

## RAG — arquitectura real

- **Embeddings**: 100% locales y gratis (`sentence-transformers`, `paraphrase-multilingual-MiniLM-L12-v2`, 384-dim) — no usan OpenAI.
- **Vectores**: pgvector nativo en Supabase/PostgreSQL (`motor_chunks`, `nsr10_chunks`, `ntc_chunks`), no un servicio de vectores externo.
- **Síntesis de respuesta**: [Groq](https://groq.com) (`llama-3.3-70b-versatile`) — se evaluó Ollama local (demasiado lento para producción) y se descartó por costo/latencia frente a Groq.
- **Trazabilidad**: cada respuesta cita `norma_ref` real (documento + sección/artículo). Si el dominio se detecta pero no hay contenido cargado, el sistema lo dice explícitamente — nunca inventa una cita.

## Desarrollo local

```bash
# Web
cd apps/web && npm install && npm run dev

# API (los 6 motores + RAG)
cd apps/api && pip install -r requirements.txt && uvicorn main:app --reload

# Un motor Python de forma aislada
cd packages/motor-<nombre> && pip install -e ".[dev]" && pytest tests/ -v

# App nativa (Fase 0, Expo)
cd apps/native && npm install && npm start
```

## Estado de deploy

| Componente | Estado |
|---|---|
| `apps/web` | ✅ Desplegado en Vercel, deploy automático en cada push a `master` |
| `apps/api` | ❌ Sin desplegar — `apps/web` en producción muestra "sin conexión" en toda funcionalidad de IA hasta que esto se resuelva |
| `apps/native` | 🔄 Fase 0 del roadmap de 12 meses (ver `docs/` o memoria del proyecto) — shell nativo, sin sensores todavía |
| Supabase | ✅ En producción, RLS activo en todas las tablas |

## Secrets de GitHub Actions (reales, verificados contra `ci.yml`)

| Secret | Uso |
|---|---|
| `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` | Backend, tests de integración |
| `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Build de `apps/web` |
| `NEXT_PUBLIC_API_URL` | Build de `apps/web` |
| `GROQ_API_KEY` | Síntesis de respuestas del RAG |

## Convenciones de contribución

Ver [CONTRIBUTING.md](./CONTRIBUTING.md) — formato de commits, cómo instalar un motor en modo desarrollo, y qué decisiones de arquitectura están deliberadamente sin resolver todavía.

## Licencia

Propiedad de Wilmer José Pérez Orozco — ver [LICENSE](./LICENSE). El repositorio es público con fines de demostración técnica/portafolio; no es software de código abierto.
