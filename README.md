# StructAI — IA con trazabilidad normativa para ingeniería civil en Colombia

[![Web](https://img.shields.io/badge/web-structai.online-0ea5e9)](https://www.structai.online)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21851529.svg)](https://doi.org/10.5281/zenodo.21851529)
[![Estado en vivo](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fplankton-app-9qinh.ondigitalocean.app%2Fdata-status&query=%24.corpus_normativo.nsr10_chunks.chunks&label=chunks%20NSR-10%20en%20vivo&color=16a34a)](https://plankton-app-9qinh.ondigitalocean.app/data-status)

## Por qué existe esto

El 10 de agosto de 2026 un terremoto de magnitud 7.4 dejó más de 287 muertos en Colombia. No fue una sorpresa geológica — el país entero está sobre zona de amenaza sísmica, y buena parte de su vivienda se construyó antes de que existieran normas sismo-resistentes estrictas, o se construyó después pero sin que nadie verificara en obra que se cumplían. Yo soy ingeniero civil, y llevo meses construyendo StructAI porque estoy convencido de algo simple: si un ingeniero puede consultar la norma exacta —no una aproximación, no un resumen genérico de un asistente de IA que nunca vio el reglamento colombiano— en el momento en que está calculando, se cometen menos errores. Y en este país, un error de cálculo estructural no es un detalle técnico. Es una vida.

Esa es la apuesta completa de StructAI: una plataforma de inteligencia artificial que responde preguntas de ingeniería civil citando la norma real —NSR-10, RAS 2000, INVIAS, NTC— con capítulo y artículo, nunca con una cita inventada. Si no tiene la información cargada, lo dice. Si la tiene, la muestra con su fuente, verificable contra el texto oficial.

`Construdata` es el nombre interno del repositorio; **StructAI** es la marca pública, en [structai.online](https://www.structai.online).

## Qué hay hoy, verificado en vivo — no una promesa

Todo lo que sigue se puede comprobar ahora mismo contra producción, sin confiar en este documento: [`GET /data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

| Corpus | Contenido | Cifra real hoy |
|---|---|---|
| **NSR-10** | Los 11 títulos (A–K) tienen contenido cargado. Profundidad variable: varios capítulos en **verbatim completo** —extraído palabra por palabra del PDF oficial y verificado— como el capítulo sísmico de acero (F.3), el título I completo, y el capítulo de fuerzas de viento (B.6, 61 páginas del reglamento). Otros conservan una síntesis técnica de referencia (tablas, fórmulas, coeficientes con su fuente exacta) todavía sin transcripción literal completa. | 1.007 chunks |
| **NTC + SGSST** | 18 normas técnicas colombianas (ICONTEC) más el marco de Seguridad y Salud en el Trabajo (Decreto 1072/2015, Ley 1562/2012, Resolución 0312/2019) | 294 chunks |
| **Motores de dominio** (AquAI/RAS 2000, GeoPot, Vías/INVIAS, Gerencia) | Corpus propio por motor, normativa específica de cada disciplina | 4.060 chunks |
| **Precios de referencia** | Actividades de construcción con desglose de insumos, base construida sobre contratos y catálogos reales | 4.566 actividades · 10.281 insumos |
| **Proveedores con precio verificado** | 24 proveedores/ferreterías del Atlántico con SKU real en ficha de producto, más 78 proveedores mipyme a nivel nacional (catálogo IAD MIPYMES / Colombia Compra Eficiente) con 114.616 precios individuales comparables — 58 de esos 78 (74%) ya tienen ciudad/departamento real, cruzados contra los registros públicos SECOP II y Cámaras de Comercio (RUES), en 21 departamentos distintos | 102 proveedores |
| **Datos oficiales en vivo, cobertura nacional** | Amenaza sísmica NSR-10 del Servicio Geológico Colombiano (Aa/Av/zona por municipio) · señal estadística de anomalía de caudal del IDEAM contra 60+ años de histórico real por estación (nunca una alerta oficial — eso es competencia exclusiva de IDEAM/UNGRD) · suelos rurales del IGAC/UPRA (taxonomía, drenaje, inundabilidad, pH) · señal estadística de vulnerabilidad de vivienda por material de pared (muestra Sisbén IV, nunca una evaluación estructural) | 1.121 municipios (SGC) · 949 estaciones con histórico (IDEAM) · 169.088 unidades de suelo (IGAC) · 1.099 municipios (Sisbén) |

**Nota de integridad**: un primer intento de pipeline automático de ingesta resultó ser un export roto de un sistema RAG anterior, con contenido desplazado desde su título de origen — se descartó por completo y quedó archivado (`packages/knowledge/_archivo/`), nunca en uso. Todo el corpus real se construye extrayendo directo de los PDF oficiales, con verificación cruzada contra el catálogo maestro de cada norma antes de publicarse. Cuando se encuentra un lote de contenido mal etiquetado o de baja confianza —ha pasado, más de una vez— se elimina y se documenta por qué, no se disimula.

## La metodología — cómo funciona esto de verdad

StructAI no es un chatbot con un PDF pegado en el prompt. Es un sistema de recuperación aumentada (RAG) construido con una regla que no se negocia: **una cita inventada es peor que no citar nada, porque parece verificable y no lo es.**

En la práctica, eso significa:

1. **Búsqueda híbrida, no solo semántica.** Cada consulta combina similitud vectorial (embeddings locales, `sentence-transformers`, sin costo por consulta) con búsqueda léxica de texto completo, fusionadas con Reciprocal Rank Fusion — porque el significado y la palabra exacta de un artículo normativo importan igual.
2. **El modelo cita solo lo que está en el contexto recuperado.** Si un número de artículo no aparece literalmente en el fragmento que se le entregó, el sistema no lo escribe. Dice "la sección correspondiente de [norma]" en vez de inventar un `A.9.4.3` que no existe.
3. **Si el dominio no tiene contenido cargado, el sistema lo dice explícitamente** en vez de responder con una aproximación genérica que suena bien pero no está verificada.
4. **Cada respuesta se puede rastrear hasta su fuente** —`normas_registro`, con estado de vigencia y derogación incluido— y el pipeline completo de carga está versionado en `scripts/ingesta/`, no oculto.
5. **La verificación no es una promesa, es un proceso repetido.** Antes de dar por buena una sección nueva del corpus, se prueba con preguntas reales contra el motor de búsqueda, no solo se confirma que la carga a la base de datos no falló. Y cuando el propio pipeline de recuperación tuvo un error real —encontrado auditando por qué una respuesta fallaba, corregido en la fuente— quedó documentado en el historial de migraciones, no parchado en silencio.

Esta disciplina es, en el fondo, el mismo método científico aplicado a software: hipótesis, verificación contra la fuente primaria, corrección explícita del error propio. Es también la base metodológica de mi trabajo de grado sobre NSR-10/SGSST/NTC, próximo a sustentar — StructAI es la prueba de concepto aplicada de esa investigación, no un producto separado de ella.

## Los 7 motores

| Motor | Dominio |
|---|---|
| **APU** | Análisis de Precios Unitarios — la base de precios reales descrita arriba |
| **Estructural** (`motor-deformacion`) | Deformación de vigas (Euler-Bernoulli), pandeo de columnas (Euler/Johnson), incertidumbre por Monte Carlo |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos), con datos hidrometeorológicos reales del IDEAM (datos.gov.co) como referencia de campo |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica NSR-10 |
| **Vías** | Diseño vial INVIAS: geometría, pavimentos, mantenimiento, topografía, NTC de materiales |
| **Gerencia** | Earned Value Management (PMBOK) + aprendizaje automático predictivo sobre avance de obra |
| **InfraCortex** | BIM (IFC) → topología del nudo viga-columna → red neuronal informada por física (PINN) → chequeo por cortante NSR-10 Títulos A/B/C, más inspección visual de estribos por visión artificial |

Cada motor expone su propio router FastAPI, su propia tabla en Supabase, y su propio corpus de búsqueda — todos comparten el mismo backend y la misma base de datos, pero ninguno depende de que otro exista para funcionar.

> **InfraCortex está desactivado por defecto en producción** (`ENABLE_ESTRUCTURAL=false`): carga `torch` + `ifcopenshell` + `opencv` (~1-1.5 GB), y la instancia actual no tiene margen de RAM para sostenerlo junto al resto de la API. El código está completo y probado (7 tests, 86% de cobertura) — activarlo es una variable de entorno, no una reescritura.

## Lo que todavía no es — honestidad antes que marketing

StructAI es un piloto en producción real, con usuarios reales, no una maqueta ni una cobertura nacional completa. Concretamente, a la fecha:

- **La base de precios con SKU real (marca, especificación técnica, norma) cubre el Atlántico.** La capa nacional (IAD MIPYMES, 78 proveedores) ya tiene ciudad/departamento real para 58 de esos proveedores (cruzados contra SECOP II y el registro de Cámaras de Comercio) — los 20 restantes no aparecen en ninguno de los dos registros públicos, así que se quedan como "Nacional" en vez de inventar una ubicación. Ninguno de los dos niveles trae todavía marca/especificación técnica a escala nacional — eso requeriría una fuente distinta, no una extensión de la actual.
- **La profundidad verbatim del corpus normativo es desigual entre títulos.** Algunos capítulos son transcripción literal verificada; otros son síntesis técnica fiel pero no palabra por palabra. Esa diferencia es visible en el propio corpus, no está escondida.
- **Orinoquía, Pacífico (más allá de las estaciones IDEAM ya integradas) y Bogotá** son las regiones donde la expansión de cobertura normativa y de precios está activa pero no cerrada.
- **No hay validación externa todavía.** Ningún ingeniero estructural certificado ajeno a este proyecto ha revisado formalmente la metodología de extracción del corpus. Es exactamente el tipo de colaboración que estoy buscando — ver la sección siguiente.

El roadmap completo, con cada punto abierto o cerrado, es público: [issues del repositorio](https://github.com/wilmerjoseperezorozco-dev/structai/issues) y su [milestone activo](https://github.com/wilmerjoseperezorozco-dev/structai/milestone/1).

## Hacia dónde va esto — lo aplicativo y lo que viene

StructAI empezó como una herramienta para Barranquilla y el Atlántico. La base técnica que existe hoy —el mismo motor que cita NSR-10, NTC o RAS 2000 para un proyecto local— ya no tiene ese límite: funciona igual para cualquier región de Colombia, y el enfoque de trazabilidad normativa es exportable a cualquier país de Latinoamérica con su propio marco regulatorio. Estas son las líneas de trabajo reales, no aspiracionales:

- **Evaluación de vulnerabilidad sísmica de vivienda ya construida.** Colombia tiene un parque enorme de vivienda informal y de mampostería no reforzada, construida antes de que existieran normas sismo-resistentes estrictas —o construida después, sin supervisión técnica real. Sobre NSR-10 A.10 y la línea metodológica AIS 2004 → Build Change → AIS 410-23, estoy construyendo contenido orientado a evaluar esa vivienda existente y a técnicas de reforzamiento aplicables, no solo a construcción nueva. El terremoto de agosto de 2026 no inició esta línea de trabajo — la volvió urgente.
- **Datos ambientales y geológicos reales integrados al cálculo, no solo a la norma.** Esto ya no es un objetivo — es cobertura nacional real: amenaza sísmica del Servicio Geológico Colombiano en los 1.121 municipios del país, anomalía estadística de caudal del IDEAM contra el histórico real de cada río (nunca presentada como alerta oficial, eso sigue siendo competencia exclusiva de IDEAM/UNGRD), y suelos rurales del IGAC/UPRA. Es exactamente el tipo de señal que importa antes de un evento, no solo después: zona de amenaza sísmica de un municipio, o si el caudal de un río está saliéndose de lo normal para la época del año. El objetivo hacia adelante es que cada motor nuevo se apoye en esta misma disciplina de datos oficiales en vivo, no en valores tabulados sueltos.
- **Cobertura normativa y de precios verdaderamente nacional**, con la misma exigencia de verificación que hoy se aplica al Atlántico, no una versión diluida.
- **Investigación aplicada, no solo producto.** El diseño de StructAI —extracción verificada, citación literal, honestidad ante la ausencia de datos— es en sí mismo un objeto de estudio para quien investigue sistemas de IA confiables en dominios de alto riesgo (ingeniería, salud, derecho). Es la pregunta de fondo detrás de mi trabajo de grado, y una línea que me interesa seguir más allá de él.

## Colaboración con universidades, gremios y Cámaras de Comercio

Esto es una invitación concreta, no una frase de cierre. Si diriges o participas en un programa de ingeniería civil, si representas a la Asociación Colombiana de Ingeniería Sísmica (AIS) —cuya metodología de rehabilitación sísmica ya cito con atribución explícita—, a una Cámara de Comercio —cuyo registro público (RUES) ya cruzo hoy para darle ciudad real a 58 de los 78 proveedores nacionales—, o a cualquier entidad con interés real en cómo se está citando y verificando la normativa colombiana con IA, quiero hablar contigo. Ofrezco acceso educativo gratuito para estudiantes y docentes, y estoy buscando activamente:

- Revisión externa de la metodología de extracción del corpus por parte de un ingeniero estructural certificado.
- Datos técnicos, normativos o de precios reales que puedan sumar a esta base, siempre con atribución documentada.
- Colaboración institucional para llevar esto de un piloto en el Atlántico a una herramienta con alcance nacional real.

El detalle completo de cómo contactar y qué tipo de colaboración busco está en [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

## Arquitectura RAG — cómo está construido, sin rodeos

- **Embeddings**: 100% locales y sin costo por consulta (`sentence-transformers`, `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones) — no dependen de una API externa de pago.
- **Vectores**: `pgvector` nativo en Supabase/PostgreSQL, no un servicio de vectores separado.
- **Síntesis de respuesta**: [Groq](https://groq.com) (`gpt-oss-120b`, 1-3 segundos de latencia típica) como motor principal, con [OpenAI](https://openai.com) (`gpt-4o-mini`) como respaldo automático si Groq se queda sin cuota diaria — dos niveles, no uno, porque un sistema que cita normativa de seguridad no puede darse el lujo de quedar mudo.
- **Trazabilidad**: cada respuesta incluye `norma_ref` real (documento + sección/artículo exacto), y advierte explícitamente si la norma citada está derogada o modificada.

## Estructura del monorepo

```
construdata/
├── apps/
│   ├── web/        → Next.js 14 (App Router) + PWA          → Vercel (desplegado)
│   ├── native/      → React Native + Expo Router (Fase 0)    → sin publicar aún
│   └── api/         → FastAPI, los 7 motores + RAG           → DigitalOcean App Platform (desplegado)
├── packages/
│   ├── motor-apu/, motor-deformacion/, motor-aquai/,
│   │   motor-geopot/, motor-vias/, motor-gerencia/  → cada uno con su pyproject.toml y sus tests
│   ├── shared-types/    → tipos TS + cliente API compartidos entre web y native
│   ├── construdata/     → schema SQL + RAG multi-norma + delegador de motores + clientes de datos abiertos (IDEAM)
│   ├── knowledge/       → _archivo/ con la fuente PDF descartada (ver nota de integridad arriba)
│   ├── ai-gateway/      → gateway multi-proveedor — experimental
│   ├── bim-intelligence/→ IFC + Qdrant — experimental, no conectado al producto
│   └── motor-estructural/ → InfraCortex: IFC + PINN + NSR-10 A/B/C, router `/estructural` conectado
├── scripts/ingesta/  → pipeline de carga del corpus, versionado por dominio (el documento fuente, no)
├── infra/supabase/   → schema y migraciones reales, reconstruidas byte a byte contra producción
├── docs/             → comparación pública, canal de colaboración institucional
└── .github/workflows/ → CI: lint + tsc, tests Python por motor (7), tests de integración del RAG
```

## Desarrollo local

```bash
# Web
cd apps/web && npm install && npm run dev

# API (6 motores activos + RAG; InfraCortex/YOLO opcionales, ver abajo)
cd apps/api && pip install -r requirements.txt && uvicorn main:app --reload

# Habilitar InfraCortex (motor-estructural) o YOLO localmente además de lo anterior:
#   pip install -r requirements-estructural.txt && export ENABLE_ESTRUCTURAL=true
#   pip install -r requirements-vision.txt      && export ENABLE_YOLO=true

# Un motor Python de forma aislada
cd packages/motor-<nombre> && pip install -e ".[dev]" && pytest tests/ -v

# App nativa (Fase 0, Expo)
cd apps/native && npm install && npm start
```

## Estado de deploy

| Componente | Estado |
|---|---|
| `apps/web` | ✅ Desplegado en Vercel (PWA), deploy automático en cada push a `master` |
| `apps/api` | ✅ Desplegado en DigitalOcean App Platform, deploy automático en cada push a `master`. Login requerido (Supabase Auth) para `/ask`, `/apu/calculate` y `/detect` |
| `apps/native` | 🔄 Fase 0 de un roadmap más largo — shell nativo, sin sensores todavía |
| Supabase | ✅ En producción, RLS activo en todas las tablas, `pgvector` para los 3 corpus RAG |

Verificable ahora mismo, sin confiar en esta tabla: [`GET /health?deep=true`](https://plankton-app-9qinh.ondigitalocean.app/health) y [`GET /data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

## Secrets de GitHub Actions (reales, verificados contra `ci.yml`)

| Secret | Uso |
|---|---|
| `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` | Backend, tests de integración |
| `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Build de `apps/web` |
| `NEXT_PUBLIC_API_URL` | Build de `apps/web` |
| `GROQ_API_KEY` | Síntesis de respuestas del RAG — motor principal |
| `OPENAI_API_KEY` | Respaldo automático si Groq se queda sin cuota diaria |

## StructAI frente a un asistente de IA genérico

Ver [`docs/comparacion.md`](./docs/comparacion.md) — comparación verificable, no marketing, contra la alternativa real que la mayoría de ingenieros ya prueba primero: preguntarle directamente a ChatGPT, Claude o Gemini sin ninguna base normativa o de precios conectada.

## Convenciones de contribución

Ver [`CONTRIBUTING.md`](./CONTRIBUTING.md) — formato de commits, cómo instalar un motor en modo desarrollo, y qué decisiones de arquitectura están deliberadamente sin resolver todavía.

## Licencia

Propiedad de Wilmer José Pérez Orozco — ver [LICENSE](./LICENSE). El repositorio es público con fines de demostración técnica, portafolio y colaboración académica; no es software de código abierto.

---

## 🌐 Overview · Resumen

<table>
<tr>
<td width="50%">

### 🇬🇧 English

**AI-powered civil engineering platform for Colombia**, built after the August 2026 earthquake made one thing clear: engineers need to verify the exact norm behind a calculation, not a generic approximation. Every StructAI answer cites the real regulation — chapter, article, source — and the system explicitly says so when it doesn't have the answer, rather than inventing one.

7 domain engines (6 active in production, 1 disabled by default for RAM), full normative traceability across NSR-10, RAS 2000/Res. 0330, INVIAS, NTC, and SGSST. Public brand: **StructAI**.

**Live coverage** (verified now, not a claim): 1,007 NSR-10 chunks across all 11 titles, 294 NTC/SGSST chunks, 4,060 domain-engine chunks, and a pricing base of 4,566 activities / 10,281 supplies / 102 verified suppliers (24 local Atlántico + 78 national). Check it yourself: [`GET /data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

**Quick start:**
```bash
cd apps/web  && npm install && npm run dev
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload
```

**Looking for:** university and institutional collaboration — free educational access, external methodology review, and data partnerships. See [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

</td>
<td width="50%">

### 🇨🇴 Español

**Plataforma de IA para ingeniería civil en Colombia**, construida después de que el terremoto de agosto de 2026 dejara clara una cosa: el ingeniero necesita verificar la norma exacta detrás de un cálculo, no una aproximación genérica. Cada respuesta de StructAI cita el reglamento real —capítulo, artículo, fuente— y el sistema dice explícitamente cuando no tiene la respuesta, en vez de inventar una.

7 motores de dominio (6 activos en producción, 1 desactivado por defecto por RAM), trazabilidad normativa completa sobre NSR-10, RAS 2000/Res. 0330, INVIAS, NTC y SGSST. Marca pública: **StructAI**.

**Cobertura en vivo** (verificada ahora, no una promesa): 1.007 chunks de NSR-10 en los 11 títulos, 294 de NTC/SGSST, 4.060 de los motores de dominio, y una base de precios de 4.566 actividades / 10.281 insumos / 102 proveedores verificados (24 locales del Atlántico + 78 nacionales). Compruébalo tú mismo: [`GET /data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

**Inicio rápido:**
```bash
cd apps/web  && npm install && npm run dev
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload
```

**Busco:** colaboración universitaria e institucional — acceso educativo gratuito, revisión externa de la metodología, y alianzas de datos. Ver [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

</td>
</tr>
</table>
