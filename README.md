# StructAI — Plataforma de IA para ingeniería civil en Colombia

[![Web](https://img.shields.io/badge/web-structai.online-0ea5e9)](https://www.structai.online)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21851529.svg)](https://doi.org/10.5281/zenodo.21851529)

SaaS freemium para ingenieros civiles y maestros de obra: cálculos de ingeniería con trazabilidad normativa real (NSR-10, NTC, RAS 2000/Res. 0330, INVIAS, SGSST) y consultas por IA que citan norma, capítulo/artículo y fuente — nunca inventa contenido normativo.

`Construdata` es el nombre interno del repositorio/código; **StructAI** es la marca pública, disponible en [structai.online](https://www.structai.online).

> **Estado actual: prueba piloto en producción.** El backend está desplegado y operativo (ver [Estado de deploy](#estado-de-deploy)). La cobertura normativa cargada hoy es un **piloto enfocado en NSR-10 (contenido técnico detallado en 9 de 11 títulos, con refuerzo activo en evaluación y rehabilitación sísmica de vivienda existente), NTC (18 normas), SGSST (Decreto 1072/2015, Ley 1562/2012, Resolución 0312/2019) y una base de precios de referencia con más de 4.500 actividades y 10.000 insumos de ferretería/proveedores reales del Atlántico** — no es una cobertura completa de toda la normativa colombiana de construcción ni de todo el país todavía. Ver [Cobertura normativa actual](#cobertura-normativa-actual-prueba-piloto) para el detalle honesto de qué está cargado y qué falta, y [Hacia dónde vamos](#hacia-dónde-vamos) para la visión de expansión nacional.

## Los 7 motores

| Motor | Dominio | Paquete |
|---|---|---|
| **APU** | Análisis de Precios Unitarios — base de precios reales del Atlántico: 4.566 actividades, 10.281 insumos, 24 proveedores/ferreterías catalogados | `packages/motor-apu` |
| **Estructural** | Deformación de vigas (Euler-Bernoulli), pandeo de columnas (Euler/Johnson), incertidumbre Monte Carlo | `packages/motor-deformacion` |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos) | `packages/motor-aquai` |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica NSR-10 | `packages/motor-geopot` |
| **Vías** | Diseño vial INVIAS: geometría, pavimentos, mantenimiento, topografía, NTC de materiales | `packages/motor-vias` |
| **Gerencia** | Earned Value Management (PMBOK) + ML predictivo sobre avance de obra | `packages/motor-gerencia` |
| **InfraCortex** | BIM (IFC) → topología del nudo viga-columna → PINN → chequeo por cortante NSR-10 Títulos A/B/C + inspección visual de estribos | `packages/motor-estructural` |

Cada motor expone su propio router FastAPI (`/apu`, `/deform`, `/aquai`, `/geopot`, `/vias`, `/gerencia`, `/estructural`), su propia tabla en Supabase (excepto InfraCortex, que hoy es cómputo puro sin persistencia), y su propio corpus RAG en `motor_chunks` — todos comparten el mismo backend y la misma base de datos.

> **InfraCortex desactivado por defecto en producción** (`ENABLE_ESTRUCTURAL=false`): carga torch + ifcopenshell + opencv (~1-1.5GB), y la instancia actual no tenía margen de RAM para sostenerlo junto al resto de la API. El código está completo y probado (7 tests, 86% cobertura) — activarlo es un cambio de una variable de entorno, no de código.

## Cobertura normativa actual (prueba piloto)

Estado real verificado en producción el 2026-08-20 (conteo directo contra Supabase, no estimado):

| Fuente | Contenido cargado | Chunks |
|---|---|---|
| **NSR-10** | Títulos A, B, C, D, F, G, H, I con contenido técnico detallado (tablas, fórmulas, coeficientes) — con refuerzo reciente en Título F (provisiones sísmicas de acero) y Título A.9 (elementos no estructurales). Títulos E, J, K con resumen de alcance oficial verificado, sin detalle técnico profundo todavía. | 998 |
| **Evaluación y rehabilitación sísmica de vivienda existente** | Marco legal NSR-10 A.10, más síntesis técnica con atribución de AIS 2004, Build Change (2015, método PAM) y AIS 410-23 — la línea de metodologías de reforzamiento de vivienda ya construida en Colombia, base para expansión nacional | incluido en NSR-10/normas_registro |
| **NTC** | 18 normas técnicas colombianas (NTC 30, 121, 174, 396, 454, 504, 673, 1028, 1032, 1328, 1500, 2289, 2516, 3459, 4026, 4027, 4076, 4595) | 294 |
| **SGSST** | Decreto 1072 de 2015, Ley 1562 de 2012, Resolución 0312 de 2019, más contenido genérico SGSST | 75 |
| **APU — precios y proveedores reales** | Base de precios de referencia del Atlántico: 4.566 actividades, 10.281 insumos, 24 proveedores/ferreterías catalogados, con trazabilidad de fuente (Construdata, contratos reales, INVIAS) | 14,871 filas |
| **AquAI / GeoPot / Vías / Gerencia** | Corpus propio por motor (RAS 2000, USCS/Proctor/CBR, INVIAS + NTC de materiales, EVM) | 4,060 chunks |

**Nota sobre la naturaleza del contenido normativo:** los chunks de NSR-10/NTC/SGSST son una **síntesis técnica de referencia** (tablas, coeficientes, fórmulas y su fuente normativa), preparada a partir de los reglamentos oficiales — no una transcripción literal palabra por palabra de los documentos legales. Los documentos de origen privado pero de acceso público usados como base histórica (AIS 2004, Build Change) se resumen en palabras propias con atribución explícita a su autor y nunca se distribuyen como PDF a través de la app. Toda respuesta cita norma/documento y sección exacta para que el usuario pueda verificar contra el texto oficial. El pipeline para ingerir el texto extraído directamente de los PDF oficiales de NSR-10 (`packages/knowledge/nsr10/`, `scripts/load_nsr10.py`) existe pero no se ha ejecutado todavía.

## Hacia dónde vamos

StructAI empezó como una herramienta para Barranquilla y el Atlántico. La base normativa y de precios que hemos construido ya no tiene ese límite técnico — el mismo motor que cita NSR-10, NTC o RAS 2000 para un proyecto en el Atlántico puede hacerlo para cualquier región de Colombia, y el mismo enfoque de trazabilidad normativa es exportable a otros países de Latinoamérica con marcos regulatorios propios. Estas son las líneas de trabajo activas:

- **Cobertura normativa nacional.** Completar los títulos de NSR-10 que hoy solo tienen resumen de alcance (E, J, K) y extender la base de precios más allá del Atlántico, hacia otras regiones del país.
- **Refuerzo sísmico de vivienda ya construida.** Colombia tiene un parque de vivienda informal y de mampostería no reforzada construido antes de que existieran normas sismo-resistentes estrictas. Estamos construyendo, sobre NSR-10 A.10 y la línea AIS 2004 → Build Change → AIS 410-23, contenido orientado a evaluación de vulnerabilidad y técnicas de reforzamiento aplicables a esa vivienda existente — no solo a construcción nueva. El terremoto de agosto de 2026 hizo evidente lo urgente que es esto.
- **Datos climáticos e hidrológicos reales.** Motores como AquAI (acueducto y alcantarillado, RAS 2000) dependen de series de precipitación, caudales y clima confiables. Estamos explorando cómo integrar datos abiertos del IDEAM al pipeline de cálculo, para que los diseños hidráulicos se apoyen en información meteorológica real del sitio del proyecto y no solo en valores de norma. Es una intención de trabajo en desarrollo, no una integración cerrada todavía.
- **Más proveedores y regiones en la base de precios.** Los 24 proveedores/ferreterías catalogados hoy son el piloto; el objetivo es una red de precios verificados que cubra más ciudades y más categorías de insumos.

Si tienes datos técnicos, normativos o de precios que puedan sumar a esta base — o si representas una entidad con interés en colaborar en alguno de estos frentes — el repositorio está abierto para revisión y el contacto está en el perfil del autor.

## Estructura del monorepo

```
construdata/
├── apps/
│   ├── web/       → Next.js 14 (App Router) + PWA        → Vercel (desplegado)
│   ├── native/     → React Native + Expo Router (Fase 0)   → sin publicar aún
│   └── api/        → FastAPI, los 7 motores + RAG          → DigitalOcean App Platform (desplegado)
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

# API (los 7 motores + RAG)
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

**AI-powered civil engineering SaaS for Colombia** — 7 domain engines (6 active in production, 1 disabled by default for RAM) with full normative traceability (NSR-10, RAS 2000 / Res. 0330, INVIAS, NTC, SGSST). Public brand: **StructAI**.

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
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload  # 7 engines + RAG
```

**Status:** Live at [structai.online](https://www.structai.online) (Vercel) · API live on DigitalOcean App Platform · Supabase (pgvector + RLS) in production · RAG powered by Groq (`llama-3.3-70b-versatile`). Current pilot content: NSR-10 (technical detail in 9/11 titles, plus a growing line on seismic retrofit of existing housing), 18 NTC standards, SGSST, and a real Atlántico pricing base (4,566 activities, 10,281 supplies, 24 suppliers). Roadmap: national coverage — see [Hacia dónde vamos](#hacia-dónde-vamos).

</td>
<td width="50%">

### 🇨🇴 Español

**SaaS de IA para ingeniería civil en Colombia** — 7 motores de dominio (6 activos en producción, 1 desactivado por defecto por RAM) con trazabilidad normativa completa (NSR-10, RAS 2000 / Res. 0330, INVIAS, NTC, SGSST). Marca pública: **StructAI**.

**Qué resuelve:** Los ingenieros civiles y directores de obra en Colombia necesitan cálculos que citen la norma real — capítulo, artículo, fuente — no resultados genéricos que pueden no aplicar a los estándares locales. Cada respuesta de StructAI está respaldada por una referencia normativa trazable; el sistema nunca inventa una cita.

**En fase madura:** Los ingenieros inician sesión en la PWA web → seleccionan un dominio (precios unitarios, estructural, agua/saneamiento, geotecnia, vías o gerencia de proyectos) → ingresan parámetros → reciben resultados con cumplimiento normativo y citas explícitas de un corpus RAG construido sobre normas colombianas reales.

| Motor | Dominio |
|-------|---------|
| **APU** | Análisis de precios unitarios — base de precios reales del Atlántico (4.566 actividades, 10.281 insumos, 24 proveedores) |
| **Estructural** | Deformación de vigas, pandeo de columnas, incertidumbre Monte Carlo (NSR-10) |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos) |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica (NSR-10) |
| **Vías** | Diseño geométrico, pavimentos, mantenimiento, topografía (INVIAS) |
| **Gerencia** | Earned Value Management (PMBOK) + seguimiento predictivo ML |

**Inicio rápido:**
```bash
cd apps/web  && npm install && npm run dev      # PWA web
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload  # 7 motores + RAG
```

**Estado:** En producción en [structai.online](https://www.structai.online) (Vercel) · API en producción en DigitalOcean App Platform · Supabase (pgvector + RLS) en producción · RAG con Groq (`llama-3.3-70b-versatile`). Cobertura piloto actual: NSR-10 (detalle técnico en 9/11 títulos, más una línea creciente de reforzamiento sísmico de vivienda existente), 18 normas NTC, SGSST, y una base de precios real del Atlántico (4.566 actividades, 10.281 insumos, 24 proveedores). Visión de expansión nacional en [Hacia dónde vamos](#hacia-dónde-vamos).

</td>
</tr>
</table>
