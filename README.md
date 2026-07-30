# StructAI — Plataforma de IA para ingeniería civil en Colombia

SaaS freemium para ingenieros civiles y maestros de obra: cálculos de ingeniería con trazabilidad normativa real (NSR-10, NTC, RAS 2000/Res. 0330, INVIAS, SGSST) y consultas por IA que citan norma, capítulo/artículo y fuente — nunca inventa contenido normativo.

`Construdata` es el nombre interno del repositorio/código; **StructAI** es la marca pública.

> **Estado actual: prueba piloto en producción.** El backend está desplegado y operativo (ver [Estado de deploy](#estado-de-deploy)). La cobertura normativa cargada hoy es un **piloto enfocado en NSR-10 (9 de 11 títulos con contenido técnico detallado), NTC (21 normas) y SGSST (Decreto 1072/2015, Ley 1562/2012, Resolución 0312/2019), integrado con el motor de APU** — no es una cobertura completa de toda la normativa colombiana de construcción. Ver [Cobertura normativa actual](#cobertura-normativa-actual-prueba-piloto) para el detalle honesto de qué está cargado y qué falta.

## Los 7 motores

| Motor | Dominio | Paquete |
|---|---|---|
| **APU** | Análisis de Precios Unitarios — catálogo Construdata 2026 Barranquilla | `packages/motor-apu` |
| **Estructural** | Deformación de vigas (Euler-Bernoulli), pandeo de columnas (Euler/Johnson), incertidumbre Monte Carlo | `packages/motor-deformacion` |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos) | `packages/motor-aquai` |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica NSR-10 | `packages/motor-geopot` |
| **Vías** | Diseño vial INVIAS: geometría, pavimentos, mantenimiento, topografía, NTC de materiales | `packages/motor-vias` |
| **Gerencia** | Earned Value Management (PMBOK) + ML predictivo sobre avance de obra | `packages/motor-gerencia` |
| **InfraCortex** | BIM (IFC) → topología del nudo viga-columna → PINN → chequeo por cortante NSR-10 Títulos A/B/C + inspección visual de estribos | `packages/motor-estructural` |

Cada motor expone su propio router FastAPI (`/apu`, `/deform`, `/aquai`, `/geopot`, `/vias`, `/gerencia`, `/estructural`), su propia tabla en Supabase (excepto InfraCortex, que hoy es cómputo puro sin persistencia), y su propio corpus RAG en `motor_chunks` — todos comparten el mismo backend y la misma base de datos.

> **InfraCortex desactivado por defecto en producción** (`ENABLE_ESTRUCTURAL=false`): carga torch + ifcopenshell + opencv (~1-1.5GB), y la instancia actual no tenía margen de RAM para sostenerlo junto al resto de la API. El código está completo y probado (7 tests, 86% cobertura) — activarlo es un cambio de una variable de entorno, no de código.

## Cobertura normativa actual (prueba piloto)

Estado real verificado en producción el 2026-07-30 (conteo directo contra Supabase, no estimado):

| Fuente | Contenido cargado | Chunks |
|---|---|---|
| **NSR-10** | Títulos A, B, C, D, F, G, H, I con contenido técnico detallado (tablas, fórmulas, coeficientes). Títulos E, J, K con resumen de alcance oficial verificado, sin detalle técnico profundo todavía. | 563 |
| **NTC** | 21 normas técnicas colombianas (NTC 30, 121, 174, 396, 454, 504, 673, 1028, 1032, 1328, 1500, 2289, 2516, 3459, 4026, 4027, 4076, 4595, entre otras) | 265 |
| **SGSST** | Decreto 1072 de 2015, Ley 1562 de 2012, Resolución 0312 de 2019 | 68 |
| **APU** | Catálogo Construdata 2026 Barranquilla | 29 ítems |
| **AquAI / GeoPot / Vías / Gerencia** | Corpus propio por motor (RAS 2000, USCS/Proctor/CBR, INVIAS + NTC de materiales, EVM) | 3,600 chunks |

**Nota sobre la naturaleza del contenido normativo:** los chunks de NSR-10/NTC/SGSST son una **síntesis técnica de referencia** (tablas, coeficientes, fórmulas y su fuente normativa), preparada a partir de los reglamentos oficiales — no una transcripción literal palabra por palabra de los documentos legales. Toda respuesta cita norma y sección exacta para que el usuario pueda verificar contra el texto oficial. El pipeline para ingerir el texto extraído directamente de los PDF oficiales de NSR-10 (`packages/knowledge/nsr10/`, `scripts/load_nsr10.py`) existe pero no se ha ejecutado todavía.

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
│   ├── bim-intelligence/ → IFC + Qdrant — experimental, no conectado al producto
│   └── motor-estructural/ → InfraCortex: IFC + PINN + NSR-10 A/B/C — router `/estructural` conectado
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
| `apps/web` | ✅ Desplegado en Vercel (PWA), deploy automático en cada push a `master` |
| `apps/api` | ✅ Desplegado en DigitalOcean App Platform (`apps-s-1vcpu-2gb`), deploy automático en cada push a `master`. Login requerido (Supabase Auth) para `/ask`, `/apu/calculate` y `/detect` |
| `apps/native` | 🔄 Fase 0 del roadmap de 12 meses (ver `docs/` o memoria del proyecto) — shell nativo, sin sensores todavía |
| Supabase | ✅ En producción, RLS activo en todas las tablas, pgvector para los 3 corpus RAG |

**Verificado en producción (2026-07-30):** login real, `/health` con chequeo profundo de dependencias (Supabase, Groq, memoria), y `/ask` end-to-end citando norma real — respuesta típica ~2-4s tras el arranque del contenedor (el modelo de embeddings se precalienta en background al desplegar, no en la primera consulta de un usuario).

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

---

## 🌐 Overview · Resumen

<table>
<tr>
<td width="50%">

### 🇬🇧 English

**AI-powered civil engineering SaaS for Colombia** — 6 domain engines with full normative traceability (NSR-10, RAS 2000 / Res. 0330, INVIAS, NTC, SGSST). Public brand: **StructAI**.

**What it solves:** Civil engineers and construction managers in Colombia need calculations that cite the actual norm — chapter, article, source — not generic results that may not apply to local standards. Every StructAI answer is backed by a traceable normative reference; the system never invents a citation.

**At maturity:** Engineers log in via the web PWA → select a domain (unit prices, structural, water/sanitation, geotechnics, roads, or project management) → enter parameters → receive normative-compliant results with explicit citations from a RAG corpus built on local Colombian standards.

| Engine | Domain |
|--------|--------|
| **APU** | Unit price analysis — Construdata 2026 Barranquilla catalogue |
| **Structural** | Beam deflection, column buckling, Monte Carlo uncertainty (NSR-10) |
| **AquAI** | Water & sanitation — RAS 2000 / Res. 0330-2017 (11 modules) |
| **GeoPot** | Geotechnics & lab: soils, concrete, aggregates, seismic (NSR-10) |
| **Roads** | Geometric design, pavements, maintenance, topography (INVIAS) |
| **Management** | Earned Value Management (PMBOK) + ML predictive progress tracking |

**Quick start:**
```bash
cd apps/web  && npm install && npm run dev      # web PWA
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload  # 6 engines + RAG
```

**Status:** Web live on Vercel · API live on DigitalOcean App Platform · Supabase (pgvector + RLS) in production · RAG powered by Groq (`llama-3.3-70b-versatile`). Current pilot content: NSR-10 (9/11 titles with technical detail), 21 NTC standards, SGSST (Decreto 1072/2015, Ley 1562/2012, Res. 0312/2019), APU catalogue.

</td>
<td width="50%">

### 🇨🇴 Español

**SaaS de IA para ingeniería civil en Colombia** — 6 motores de dominio con trazabilidad normativa completa (NSR-10, RAS 2000 / Res. 0330, INVIAS, NTC, SGSST). Marca pública: **StructAI**.

**Qué resuelve:** Los ingenieros civiles y directores de obra en Colombia necesitan cálculos que citen la norma real — capítulo, artículo, fuente — no resultados genéricos que pueden no aplicar a los estándares locales. Cada respuesta de StructAI está respaldada por una referencia normativa trazable; el sistema nunca inventa una cita.

**En fase madura:** Los ingenieros inician sesión en la PWA web → seleccionan un dominio (precios unitarios, estructural, agua/saneamiento, geotecnia, vías o gerencia de proyectos) → ingresan parámetros → reciben resultados con cumplimiento normativo y citas explícitas de un corpus RAG construido sobre normas colombianas reales.

| Motor | Dominio |
|-------|---------|
| **APU** | Análisis de precios unitarios — catálogo Construdata 2026 Barranquilla |
| **Estructural** | Deformación de vigas, pandeo de columnas, incertidumbre Monte Carlo (NSR-10) |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos) |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica (NSR-10) |
| **Vías** | Diseño geométrico, pavimentos, mantenimiento, topografía (INVIAS) |
| **Gerencia** | Earned Value Management (PMBOK) + seguimiento predictivo ML |

**Inicio rápido:**
```bash
cd apps/web  && npm install && npm run dev      # PWA web
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload  # 6 motores + RAG
```

**Estado:** Web en producción en Vercel · API en producción en DigitalOcean App Platform · Supabase (pgvector + RLS) en producción · RAG con Groq (`llama-3.3-70b-versatile`). Cobertura piloto actual: NSR-10 (9/11 títulos con detalle técnico), 21 normas NTC, SGSST (Decreto 1072/2015, Ley 1562/2012, Res. 0312/2019), catálogo APU.

</td>
</tr>
</table>
