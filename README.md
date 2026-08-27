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
| **NSR-10** | Los 11 títulos (A–K) tienen contenido cargado. Profundidad variable: varios capítulos en **verbatim completo** —extraído palabra por palabra del PDF oficial y verificado— como el capítulo sísmico de acero (F.3, con sus 11 sistemas estructurales, cerrado por completo), el título I completo, y el capítulo de fuerzas de viento (B.6, 61 páginas del reglamento). Otros conservan una síntesis técnica de referencia (tablas, fórmulas, coeficientes con su fuente exacta) todavía sin transcripción literal completa — el más atrasado hoy es el Título F.4/F.5 (acero formado en frío y aluminio). | 4.061 chunks |
| **NTC + SGSST** | 18 normas técnicas colombianas (ICONTEC) más el marco de Seguridad y Salud en el Trabajo (Decreto 1072/2015, Ley 1562/2012, Resolución 0312/2019) | 294 chunks |
| **Motores de dominio** (AquAI/RAS 2000, GeoPot, Vías/INVIAS, Gerencia) | Corpus propio por motor, normativa específica de cada disciplina | 4.060 chunks |
| **Precios de referencia** | Actividades de construcción con desglose de insumos, base construida sobre contratos y catálogos reales | 4.566 actividades · 10.281 insumos |
| **Proveedores con precio verificado** | 24 proveedores/ferreterías del Atlántico con SKU real en ficha de producto, más 78 proveedores mipyme a nivel nacional (catálogo IAD MIPYMES / Colombia Compra Eficiente) con 114.616 precios individuales comparables — 70 de esos 78 (90%) ya tienen ciudad/departamento real, cruzados contra los registros públicos SECOP II y Cámaras de Comercio (RUES), en 22 departamentos distintos | 102 proveedores |
| **Datos oficiales en vivo, cobertura nacional** | Amenaza sísmica NSR-10 del Servicio Geológico Colombiano (Aa/Av/zona por municipio) · señal estadística de anomalía de caudal del IDEAM contra 60+ años de histórico real por estación (nunca una alerta oficial — eso es competencia exclusiva de IDEAM/UNGRD) · suelos rurales del IGAC/UPRA (taxonomía, drenaje, inundabilidad, pH) · señal estadística de vulnerabilidad de vivienda por material de pared (muestra Sisbén IV, nunca una evaluación estructural) · histórico real de emergencias reportadas a la UNGRD por municipio (fallecidos, viviendas destruidas/averiadas, 2019-2024 — esto es lo que YA pasó, nunca un pronóstico) | 1.121 municipios (SGC) · 949 estaciones con histórico (IDEAM) · 169.088 unidades de suelo (IGAC) · 1.099 municipios (Sisbén) · 41.893 eventos (UNGRD) |

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

## Evaluación empírica del RAG — medido, no solo diseñado

No me quedé en describir la arquitectura de recuperación; la medí, con el marco de evaluación RAGAS (fidelidad, relevancia de respuesta, precisión y cobertura del contexto) sobre un conjunto de preguntas con respuesta correcta verificada de antemano contra el texto oficial de la norma. Documento esto con la misma disciplina que aplico al corpus: con los números reales, no con la impresión de que algo "se ve mejor".

| Etapa (n=12 preguntas) | Fidelidad | Relevancia | Precisión de contexto | Cobertura de contexto |
|---|---|---|---|---|
| Línea base (RRF sin re-ranking) | 0.906 ± 0.193 | 0.917 ± 0.055 | 0.743 ± 0.235 | 1.000 ± 0.000 |
| + Re-ranking por cross-encoder, puntaje combinado | 0.837 ± 0.243 | 0.851 ± 0.271 | **0.875 ± 0.138** | 0.917 ± 0.289 |
| + Descomposición de consultas compuestas | 0.856 ± 0.266 | 0.920 ± 0.043 | 0.875 ± 0.151 | **1.000 ± 0.000** |

El ± es la desviación estándar entre las 12 preguntas de esa misma corrida, no una estimación — la reporto porque, con una muestra de este tamaño, es tan importante como el promedio: en fidelidad y relevancia, la diferencia entre etapas (≈0.05-0.07) es más chica que la propia dispersión entre preguntas (0.19-0.27), así que no puedo afirmar con esta muestra que esas dos métricas realmente bajaron por el re-ranking — es igual de consistente con ruido de muestra. La mejora en precisión de contexto (0.743 → 0.875) sí es más grande que la dispersión de la corrida que mejora, lo cual la hace la lectura más confiable de las cuatro. Es exactamente el motivo por el que estoy ampliando el conjunto de evaluación más allá de 12 preguntas — con una muestra mayor, esta misma tabla debería volverse más concluyente, no solo más larga.

Tres hallazgos concretos salieron de este trabajo, cada uno generalizable a cualquier sistema RAG híbrido sobre corpus normativo técnico, no solo a este:

1. **La línea base reveló que el cuello de botella real no era el que yo esperaba.** La cobertura del contexto ya era perfecta desde el inicio (1.000): el corpus tenía la información necesaria. El problema real estaba en la precisión (0.743) — el orden en que llegaban los fragmentos correctos, no si existían.
2. **Un defecto de diseño en la fusión de rangos recíprocos (RRF)**: el tamaño del conjunto interno de candidatos de cada rama de búsqueda (vectorial y de texto completo) estaba atado a la cantidad de resultados solicitada por quien llamaba a la función, en vez de ser un valor fijo. Esto producía un ranking no monótono — un fragmento correcto podía aparecer o desaparecer del resultado final según un parámetro que en teoría no debería afectar el orden. Corregido desacoplando ese tamaño interno de la cantidad solicitada.
3. **Combinar el puntaje del re-ranker con el de recuperación híbrida, en vez de reemplazarlo por completo, es lo que realmente funciona.** El reemplazo puro mejoraba la precisión pero degradaba la cobertura (0.917); la combinación normalizada mejoró la precisión de forma sostenida (0.743 → 0.875) sin esa regresión.

### Validación a mayor escala: de 12 a 52 preguntas

Hice justo lo que la tabla de arriba pedía: amplié el conjunto de evaluación de 12 a 52 preguntas, cubriendo ahora Títulos D, E y G completos, más ampliaciones de A, B, C, F, H, I, J, K, y las normas NTC 121/174/1500 y el Decreto 1072 (SGSST) — mismo método de siempre, ningún hecho inventado, cada uno extraído directo del corpus verbatim ya cargado.

| Métrica (n=52 preguntas) | Media ± desviación estándar |
|---|---|
| Fidelidad | 0.826 ± 0.252 (n=49 — 3 respuestas del juez fallaron por ruido real de infraestructura, excluidas, no promediadas como cero) |
| Relevancia de respuesta | 0.858 ± 0.252 |
| Precisión de contexto | 0.784 ± 0.181 |
| Cobertura de contexto | 0.960 ± 0.198 (n=50) |

El hallazgo más importante de esta ampliación no es ningún promedio — es cuánto cambió la dispersión. Con 12 preguntas, la relevancia de respuesta salía en 0.920 ± 0.043: parecía casi perfecta y muy consistente. Con 52, es 0.858 ± 0.252 — la muestra chica estaba dando una imagen artificialmente optimista, no representativa de la varianza real del sistema. Es exactamente la razón por la que valía la pena ampliarla: doce preguntas alcanzan para detectar un problema estructural de diseño, pero no para confiar en qué tan estable es el sistema en el día a día. La precisión de contexto, en cambio, se mantuvo relativamente estable entre ambas escalas (0.875 → 0.784) — una señal más confiable que la relevancia de respuesta.

La verificación previa (más barata, sin el juez de RAGAS) encontró además 3 preguntas de las 40 nuevas donde el hecho existe en el corpus pero no llega al contexto recuperado con la configuración por defecto — un hueco real de precisión de recuperación, no un dato mal cargado. Los dejo documentados como candidatos concretos de mejora, no los escondo: la cuantía máxima de refuerzo a flexión en pórticos DES (Título C), el espesor mínimo de mampostería no reforzada (Título D), y la duración de la Fase 3 del SG-SST para empresas grandes (Decreto 1072) — este último probablemente porque la tabla fuente mezcla los cuatro tamaños de empresa en un solo fragmento denso, diluyendo la señal del embedding.

La descomposición de consultas compuestas (preguntas que combinan dos conceptos normativos independientes) llevó la cobertura del contexto del caso que la motivó de 0.0 a 1.0 — con una limitación que documento explícitamente, no oculto: esa corrida en particular coincidió con el agotamiento de cuota del proveedor de LLM principal, lo que confunde parcialmente la atribución de las métricas de generación (no de recuperación) a esa intervención específica.

## Los 7 motores

| Motor | Dominio |
|---|---|
| **APU** | Análisis de Precios Unitarios — la base de precios reales descrita arriba |
| **Estructural** (`motor-deformacion`) | Deformación de vigas (Euler-Bernoulli), pandeo de columnas (Euler/Johnson), incertidumbre por Monte Carlo |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos), con datos hidrometeorológicos reales del IDEAM (datos.gov.co) como referencia de campo |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica NSR-10 |
| **Vías** | Diseño vial INVIAS: geometría, pavimentos, mantenimiento, topografía, NTC de materiales |
| **Gerencia** | Earned Value Management (PMBOK) + aprendizaje automático predictivo sobre avance de obra |
| **InfraCortex** | BIM (IFC) → topología del nudo viga-columna → chequeo por cortante NSR-10 Títulos A/B/C (fórmulas clásicas), más inspección visual de estribos |

Cada motor expone su propio router FastAPI, su propia tabla en Supabase, y su propio corpus de búsqueda — todos comparten el mismo backend y la misma base de datos, pero ninguno depende de que otro exista para funcionar.

> **InfraCortex está desactivado por defecto en producción** (`ENABLE_ESTRUCTURAL=false`): carga `torch` + `ifcopenshell` + `opencv` (~1-1.5 GB), y la instancia actual no tiene margen de RAM para sostenerlo junto al resto de la API. El código está completo y probado (7 tests, 86% de cobertura) — activarlo es una variable de entorno, no una reescritura.

## Lo que todavía no es — honestidad antes que marketing

StructAI es un piloto en producción real, con usuarios reales, no una maqueta ni una cobertura nacional completa. Concretamente, a la fecha:

- **La base de precios con SKU real (marca, especificación técnica, norma) cubre el Atlántico.** La capa nacional (IAD MIPYMES, 78 proveedores) ya tiene ciudad/departamento real para 70 de esos proveedores (cruzados contra SECOP II y el registro de Cámaras de Comercio) — los 8 restantes son casos genuinamente ambiguos (homónimos, uniones temporales sin registro mercantil regular) y se quedan como "Nacional" en vez de adivinar. Ninguno de los dos niveles trae todavía marca/especificación técnica a escala nacional — eso requeriría una fuente distinta, no una extensión de la actual.
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

Esto es una invitación concreta, no una frase de cierre. Si diriges o participas en un programa de ingeniería civil, si representas a la Asociación Colombiana de Ingeniería Sísmica (AIS) —cuya metodología de rehabilitación sísmica ya cito con atribución explícita—, a una Cámara de Comercio —cuyo registro público (RUES) ya cruzo hoy para darle ciudad real a 70 de los 78 proveedores nacionales—, o a cualquier entidad con interés real en cómo se está citando y verificando la normativa colombiana con IA, quiero hablar contigo. Ofrezco acceso educativo gratuito para estudiantes y docentes, y estoy buscando activamente:

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
│   └── motor-estructural/ → InfraCortex: IFC + NSR-10 A/B/C, router `/estructural` conectado
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

*Full detail above is in Spanish, my working language for this project. This section is a complete mirror of it, not just an intro, so an English-speaking reader doesn't miss anything.*

**Why this exists.** On August 10, 2026, a magnitude-7.4 earthquake killed more than 287 people in Colombia. It wasn't a geological surprise — the whole country sits on seismic-hazard zones, and a large share of its housing was built before strict seismic codes existed, or built afterward without anyone verifying compliance on site. I'm a civil engineer, and I've spent months building StructAI on one conviction: if an engineer can look up the exact regulation — not an approximation, not a generic AI summary that never actually saw the Colombian code — at the moment they're calculating, fewer errors get made. In this country, a structural miscalculation isn't a technical detail. It's a life. StructAI cites the real regulation — NSR-10, RAS 2000, INVIAS, NTC — with chapter and article, never an invented citation. If it doesn't have the information loaded, it says so.

**What's live today, verified now — not a promise.** Everything below can be checked right now against production, without trusting this document: [`GET /data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

| Corpus | Content | Real figure today |
|---|---|---|
| **NSR-10** | All 11 titles (A–K) have content loaded. Depth varies: several chapters are **full verbatim** — extracted word-for-word from the official PDF and verified — such as the steel seismic-provisions chapter (F.3, all 11 structural systems, fully closed), the complete Title I, and the wind-load chapter (B.6, 61 pages of the code). Others keep a faithful technical summary (tables, formulas, coefficients with their exact source) not yet transcribed verbatim in full — the furthest behind today is Title F.4/F.5 (cold-formed steel and aluminum). | 4,061 chunks |
| **NTC + SGSST** | 18 Colombian technical standards (ICONTEC) plus the occupational health & safety framework (Decree 1072/2015, Law 1562/2012, Resolution 0312/2019) | 294 chunks |
| **Domain engines** (AquAI/RAS 2000, GeoPot, Vías/INVIAS, Gerencia) | Own corpus per engine, discipline-specific regulation | 4,060 chunks |
| **Reference pricing** | Construction activities broken down into supplies, built from real contracts and catalogs | 4,566 activities · 10,281 supplies |
| **Suppliers with verified pricing** | 24 suppliers/hardware stores in Atlántico with real SKUs, plus 78 national SME suppliers (IAD MIPYMES / Colombia Compra Eficiente catalog) with 114,616 individual comparable prices — 70 of those 78 (90%) already have a real city/department, cross-checked against the public SECOP II and Chamber of Commerce (RUES) records, across 22 different departments | 102 suppliers |
| **Live official data, national coverage** | NSR-10 seismic hazard from the Colombian Geological Survey (Aa/Av/zone per municipality) · statistical streamflow-anomaly signal from IDEAM against 60+ years of real historical data per station (never an official alert — that stays IDEAM/UNGRD's exclusive competence) · rural soils from IGAC/UPRA (taxonomy, drainage, flood risk, pH) · statistical housing-vulnerability signal by wall material (Sisbén IV sample, never a structural assessment) · real historical emergency records reported to UNGRD by municipality (deaths, destroyed/damaged homes, 2019–2024 — this is what already happened, never a forecast) | 1,121 municipalities (SGC) · 949 stations with history (IDEAM) · 169,088 soil units (IGAC) · 1,099 municipalities (Sisbén) · 41,893 events (UNGRD) |

**The methodology — how this actually works.** StructAI is not a chatbot with a PDF pasted into the prompt. It's a retrieval-augmented generation (RAG) system built on one non-negotiable rule: **an invented citation is worse than no citation, because it looks verifiable and isn't.** In practice: (1) hybrid search, not just semantic — every query combines vector similarity (local embeddings, `sentence-transformers`, no per-query cost) with full-text lexical search, fused with Reciprocal Rank Fusion, because both meaning and the exact wording of a regulatory article matter; (2) the model cites only what's in the retrieved context — if an article number doesn't appear literally in the fragment it was given, it doesn't write it; (3) if a domain has no content loaded, the system says so explicitly instead of answering with a plausible-sounding but unverified approximation; (4) every answer is traceable to its source (`normas_registro`, including repeal/amendment status), and the entire ingestion pipeline is version-controlled in `scripts/ingesta/`, not hidden; (5) verification is a repeated process, not a one-time promise — before trusting a new corpus section, I test it with real questions against the search engine, not just confirm the database write didn't error. This discipline is, at bottom, the scientific method applied to software: hypothesis, verification against the primary source, explicit correction of my own error. It's also the methodological backbone of my undergraduate thesis on NSR-10/SGSST/NTC, soon to be defended — StructAI is the applied proof of concept of that research, not a separate product from it.

**Empirical RAG evaluation — measured, not just designed.** I didn't stop at describing the retrieval architecture; I measured it with the RAGAS evaluation framework (faithfulness, answer relevancy, context precision, context recall) against a question set with correctness verified independently ahead of time.

| Stage (n=12 questions) | Faithfulness | Relevancy | Context precision | Context recall |
|---|---|---|---|---|
| Baseline (RRF, no re-ranking) | 0.906 ± 0.193 | 0.917 ± 0.055 | 0.743 ± 0.235 | 1.000 ± 0.000 |
| + Cross-encoder re-ranking, combined score | 0.837 ± 0.243 | 0.851 ± 0.271 | **0.875 ± 0.138** | 0.917 ± 0.289 |
| + Compound-query decomposition | 0.856 ± 0.266 | 0.920 ± 0.043 | 0.875 ± 0.151 | **1.000 ± 0.000** |

The ± is the standard deviation across the 12 questions of that same run, not an estimate — I report it because, at this sample size, it matters as much as the average: for faithfulness and relevancy, the difference between stages (≈0.05–0.07) is smaller than the spread between questions within a single run (0.19–0.27), so I can't claim from this sample that those two metrics genuinely dropped because of re-ranking — it's equally consistent with sample noise. The context-precision gain (0.743 → 0.875) is larger than the spread of the run it improves into, which makes it the most trustworthy read of the four. This is exactly why I'm expanding the evaluation set beyond 12 questions — with a larger sample, this same table should become more conclusive, not just longer.

Three concrete findings came out of this, each generalizable to any hybrid RAG system over technical regulatory corpora, not just this one: **(1)** the baseline showed the real bottleneck wasn't the one I expected — context recall was already perfect (1.000), the real problem was precision (0.743), i.e. ranking order, not missing content; **(2)** a real design defect in Reciprocal Rank Fusion — each branch's internal candidate-pool size was tied to the caller's requested result count instead of being a fixed value, producing a non-monotonic ranking where a correct fragment could appear or vanish depending on a parameter that shouldn't have affected order, fixed by decoupling that pool size; **(3)** combining the re-ranker's score with the original hybrid-retrieval score, instead of replacing it outright, is what actually works — pure replacement improved precision but degraded recall (0.917), while the combined, normalized score improved precision consistently (0.743 → 0.875) without that regression. Query decomposition took the context recall of the case that motivated it from 0.0 to 1.0 — with a limitation I document explicitly, not hide: that particular run coincided with the primary LLM provider's quota running out, which partly confounds attribution of the generation metrics (not the retrieval ones) to that specific change.

**Scaling up the evaluation: from 12 to 52 questions.** I did exactly what the table above called for: expanded the evaluation set from 12 to 52 questions, now covering Titles D, E and G in full plus extensions of A, B, C, F, H, I, J, K, and the NTC 121/174/1500 standards and Decree 1072 (SGSST) — same method as always, nothing invented, every fact pulled straight from the already-loaded verbatim corpus.

| Metric (n=52 questions) | Mean ± standard deviation |
|---|---|
| Faithfulness | 0.826 ± 0.252 (n=49 — 3 judge calls failed on real infrastructure noise, excluded, not averaged in as zero) |
| Answer relevancy | 0.858 ± 0.252 |
| Context precision | 0.784 ± 0.181 |
| Context recall | 0.960 ± 0.198 (n=50) |

The most important finding of this expansion isn't any single average — it's how much the spread changed. At 12 questions, answer relevancy came out at 0.920 ± 0.043: it looked almost perfect and very consistent. At 52, it's 0.858 ± 0.252 — the small sample was giving an artificially optimistic picture, not a representative one of the system's real variance. That's exactly why the expansion was worth doing: twelve questions are enough to catch a structural design problem, not enough to trust how stable the system really is day to day. Context precision, by contrast, held up relatively steady across both scales (0.875 → 0.784) — a more trustworthy signal than answer relevancy turned out to be.

The cheaper pre-check (no RAGAS judge involved) also found 3 of the 40 new questions where the fact exists in the corpus but doesn't reach the retrieved context under the default configuration — a real retrieval-precision gap, not a bad data load. I document them as concrete improvement candidates rather than hide them: the maximum flexural reinforcement ratio in DES moment frames (Title C), the minimum thickness of unreinforced masonry (Title D), and the Phase 3 duration of SG-SST implementation for large companies (Decree 1072) — the last one likely because its source table packs all four company-size tiers into one dense fragment, diluting the embedding's signal.

**The 7 engines:**

| Engine | Domain |
|---|---|
| **APU** | Unit price analysis — the real pricing base described above |
| **Structural** (`motor-deformacion`) | Beam deflection (Euler-Bernoulli), column buckling (Euler/Johnson), Monte Carlo uncertainty |
| **AquAI** | Water supply & sewerage — RAS 2000 / Res. 0330-2017 (11 modules), with real IDEAM hydro-meteorological data (datos.gov.co) as field reference |
| **GeoPot** | Geotechnics and lab testing: soils, concrete, aggregates, NSR-10 seismic provisions |
| **Vías** | INVIAS road design: geometry, pavements, maintenance, topography, materials standards |
| **Gerencia** | Earned Value Management (PMBOK) + predictive machine learning on construction progress |
| **InfraCortex** | BIM (IFC) → beam-column node topology → NSR-10 Titles A/B/C shear check (classical formulas), plus visual stirrup inspection |

Each engine exposes its own FastAPI router, its own Supabase table, and its own search corpus — they all share the same backend and database, but none depends on another to function. **InfraCortex is disabled by default in production** (`ENABLE_ESTRUCTURAL=false`): it loads `torch` + `ifcopenshell` + `opencv` (~1–1.5 GB), and the current instance doesn't have the RAM headroom to sustain it alongside the rest of the API. The code is complete and tested (7 tests, 86% coverage) — enabling it is an environment variable, not a rewrite.

**What this isn't yet — honesty before marketing.** StructAI is a real production pilot with real users, not a mockup or full national coverage. Specifically, today: the pricing base with real SKUs (brand, technical spec, standard) covers Atlántico — the national layer (IAD MIPYMES, 78 suppliers) already has a real city/department for 70 of those suppliers, cross-checked against SECOP II and the Chamber of Commerce registry; the remaining 8 are genuinely ambiguous cases (name collisions, temporary unions without regular commercial registration) and stay labeled "National" instead of guessing; neither tier yet brings brand/technical spec to national scale. The regulatory corpus's verbatim depth is uneven across titles — some chapters are verified literal transcription, others a faithful technical summary but not word-for-word, and that difference is visible in the corpus itself, not hidden. Orinoquía, the Pacific (beyond the IDEAM stations already integrated), and Bogotá are where coverage expansion is active but not closed. There's no external validation yet — no certified structural engineer outside this project has formally reviewed the corpus-extraction methodology; that's exactly the kind of collaboration I'm looking for. The full roadmap, every point open or closed, is public: [repository issues](https://github.com/wilmerjoseperezorozco-dev/structai/issues) and its [active milestone](https://github.com/wilmerjoseperezorozco-dev/structai/milestone/1).

**Where this is going.** StructAI started as a tool for Barranquilla and Atlántico. The technical base that exists today — the same engine that cites NSR-10, NTC, or RAS 2000 for a local project — no longer has that limit: it works the same for any region of Colombia, and the normative-traceability approach is exportable to any Latin American country with its own regulatory framework. Real lines of work, not aspirational ones: **seismic vulnerability assessment of already-built housing** — Colombia has a large stock of informal and unreinforced-masonry housing built before strict seismic codes existed, or built afterward without real technical supervision; building on NSR-10 A.10 and the AIS 2004 → Build Change → AIS 410-23 methodological line, I'm building content aimed at assessing that existing housing and applicable retrofit techniques, not just new construction — the August 2026 earthquake didn't start this line of work, it made it urgent; **real environmental and geological data integrated into the calculation, not just the norm** — this is no longer a goal, it's real national coverage: seismic hazard from the Colombian Geological Survey across the country's 1,121 municipalities, statistical streamflow anomaly from IDEAM against each river's real history (never presented as an official alert, that stays IDEAM/UNGRD's exclusive competence), and rural soils from IGAC/UPRA; **truly national regulatory and pricing coverage**, held to the same verification standard applied to Atlántico today, not a diluted version; **applied research, not just product** — StructAI's design (verified extraction, literal citation, honesty about missing data) is itself a subject of study for anyone researching trustworthy AI systems in high-stakes domains (engineering, health, law) — it's the underlying question behind my thesis, and a line I want to keep pursuing beyond it.

**University, guild, and Chamber of Commerce collaboration.** This is a concrete invitation, not a closing line. If you lead or take part in a civil engineering program, if you represent the Colombian Association of Seismic Engineering (AIS) — whose seismic-rehabilitation methodology I already cite with explicit attribution —, a Chamber of Commerce — whose public registry (RUES) I already cross-check to give a real city to 70 of the 78 national suppliers —, or any entity genuinely interested in how Colombian regulation is being cited and verified with AI, I want to talk. I offer free educational access for students and faculty, and I'm actively looking for: external review of the corpus-extraction methodology by a certified structural engineer; real technical, regulatory, or pricing data that can add to this base, always with documented attribution; institutional collaboration to take this from an Atlántico pilot to a tool with real national reach. Full detail on how to reach out and what kind of collaboration I'm looking for: [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

**RAG architecture — how it's built, no detours.** Embeddings: 100% local, no per-query cost (`sentence-transformers`, `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions) — no dependency on a paid external API. Vectors: native `pgvector` on Supabase/PostgreSQL, not a separate vector service. Answer synthesis: [Groq](https://groq.com) (`gpt-oss-120b`, 1–3s typical latency) as the primary engine, with [OpenAI](https://openai.com) (`gpt-4o-mini`) as an automatic fallback if Groq runs out of daily quota — two tiers, not one, because a system that cites safety regulation can't afford to go silent. Traceability: every answer includes a real `norma_ref` (document + exact section/article), and explicitly warns if the cited regulation has been repealed or amended.

**Quick start:**
```bash
cd apps/web  && npm install && npm run dev
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload
```

**Deploy status:** `apps/web` on Vercel (PWA, auto-deploy on every push to `master`) · `apps/api` on DigitalOcean App Platform (auto-deploy on every push, login required via Supabase Auth for `/ask`, `/apu/calculate`, `/detect`) · `apps/native` is Phase 0 of a longer roadmap — native shell, no sensors yet · Supabase in production, RLS on every table. Verify it yourself, without trusting this table: [`GET /health?deep=true`](https://plankton-app-9qinh.ondigitalocean.app/health) and [`GET /data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

**License.** Owned by Wilmer José Pérez Orozco — see [LICENSE](./LICENSE). The repository is public for technical demonstration, portfolio, and academic collaboration purposes; it is not open-source software.

</td>
<td width="50%">

### 🇨🇴 Español

**Plataforma de IA para ingeniería civil en Colombia**, construida después de que el terremoto de agosto de 2026 dejara clara una cosa: el ingeniero necesita verificar la norma exacta detrás de un cálculo, no una aproximación genérica. Cada respuesta de StructAI cita el reglamento real —capítulo, artículo, fuente— y el sistema dice explícitamente cuando no tiene la respuesta, en vez de inventar una.

7 motores de dominio (6 activos en producción, 1 desactivado por defecto por RAM), trazabilidad normativa completa sobre NSR-10, RAS 2000/Res. 0330, INVIAS, NTC y SGSST. Marca pública: **StructAI**.

**Cobertura en vivo** (verificada ahora, no una promesa): 4.061 chunks de NSR-10 en los 11 títulos, 294 de NTC/SGSST, 4.060 de los motores de dominio, y una base de precios de 4.566 actividades / 10.281 insumos / 102 proveedores verificados (24 locales del Atlántico + 78 nacionales). Compruébalo tú mismo: [`GET /data-status`](https://plankton-app-9qinh.ondigitalocean.app/data-status).

**Evaluación empírica del RAG**: medida con RAGAS, no solo diseñada — precisión de contexto 0.743 → 0.875 tras re-ranking combinado y descomposición de consultas, con un defecto real de fusión RRF encontrado y corregido en el camino. Detalle completo arriba, en "Evaluación empírica del RAG".

**Inicio rápido:**
```bash
cd apps/web  && npm install && npm run dev
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload
```

**Busco:** colaboración universitaria e institucional — acceso educativo gratuito, revisión externa de la metodología, y alianzas de datos. Ver [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

</td>
</tr>
</table>
