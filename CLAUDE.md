# StructAI (construdata) — contexto para quien trabaje aquí con Claude

Este archivo es la **memoria portátil** del proyecto: vive en git, viaja con
el repo, y cualquier sesión de Claude Code que abra este directorio lo carga
automáticamente — sin depender de la memoria privada de una cuenta o máquina
en particular. No reemplaza esa memoria privada (más detallada, con
contexto de negocio y decisiones día a día); la complementa con lo que
cualquiera necesita saber de inmediato para no repetir errores ya resueltos.

## Qué es esto

SaaS PWA (`apps/web`, Next.js) + API (`apps/api`, FastAPI) + Supabase, para
ingenieros civiles y maestros de obra en Colombia. Nombre público: **StructAI**
(marca) — "Construdata" es el nombre interno del repo/código. Lleva la NSR-10
(norma sismo-resistente colombiana) y otras normas técnicas a un RAG
consultable, más una base de precios (APU) con trazabilidad normativa.
Repo público: `wilmerjoseperezorozco-dev/structai`.

## Convenciones establecidas — no las reinventes

**Ingesta de normativa**: cada dominio tiene su carpeta en
`scripts/ingesta/<dominio>/`. El script de carga **se versiona en git**; el
documento fuente (PDF/dump/raw) **nunca** — vive en `scripts/ingesta/<dominio>/raw/`,
ya cubierto por `.gitignore`. Patrón de cada script: cargar `.env` desde
`apps/api/.env`, codificar texto con `sentence-transformers` local
(`paraphrase-multilingual-MiniLM-L12-v2`, 384-dim, sin costo), `upsert` a la
tabla de chunks correspondiente con `on_conflict="id"`. Ver `scripts/README.md`.

**Antes de dar un chunk por bueno**: verificar con una consulta de retrieval
real contra la función RPC de búsqueda (`match_<tabla>_chunks`), no solo
confirmar que el `insert`/`upsert` no lanzó error.

**Antes de asumir que falta contenido**: verificar el inventario real en
Supabase (`count(*)`, nunca `list_tables` del MCP — devuelve conteos
estimados/obsoletos, confirmado con `ntc_chunks` mostrando 29 vs. 294 reales)
contra el catálogo maestro. Varias veces este proyecto se asumió un hueco que
ya estaba resuelto — verificar primero evita reauditorías redundantes.

**Heurística de chunks sospechosos**: el prefijo `<Letra>-SEC<N>-*` (visto en
Títulos I, J, E, F) marca sistemáticamente lotes de ingestión antiguos poco
confiables — mal etiquetados, con contenido fabricado, o redundantes con
trabajo verbatim posterior. Si aparece en otro título, verificar contra el
catálogo maestro antes de confiar en él.

**Deprecar sin borrar**: código/datos obsoletos se mueven con `git mv` a una
carpeta `_archivo/` hermana (`archivo.OBSOLETO.ext`) con un `README.md`
explicando el porqué. Nunca `git rm` directo — puede tener valor histórico o
de referencia.

**Honestidad de fuente, siempre verificable**: no se publican cifras o
afirmaciones que no se puedan verificar en vivo (ver `docs/comparacion.md`
como el estándar — cada fila enlaza a algo comprobable). Si un valor no tiene
fuente citable (ej. coeficientes IDF en `motor-aquai/ras2000_tablas.py`), se
marca explícitamente como referencia/no verificado, no se presenta como dato
oficial.

## Respaldo de IA (síntesis LLM)

`packages/construdata/rag_multi_norma.py` — Groq (principal, cuota gratis
200K tokens/día, se agota con uso real) → **OpenAI** (respaldo, `gpt-4o-mini`,
financiado con crédito propio del usuario). NVIDIA NIM se probó como segundo
nivel y se retiró el 2026-08-20 por latencia inconsistente (20s–199s). Los
tres secrets (`GROQ_API_KEY`, `OPENAI_API_KEY`, más los de Supabase) deben
existir tanto en GitHub Actions (Settings → Secrets) como en las variables de
entorno de DigitalOcean (producción) — son almacenes separados, confirmar en
ambos al rotar o agregar credenciales.

## Dónde está cada cosa

- `apps/api/main.py` — FastAPI, endpoints públicos (`/ask`, `/data-status`,
  `/health`), motores cargados condicionalmente (`ENABLE_YOLO`,
  `ENABLE_ESTRUCTURAL`) para no arrastrar dependencias pesadas por defecto.
- `packages/motor-*` — motores de dominio (aquai/hidrosanitario, apu/precios,
  deformacion, geopot, vias, gerencia, estructural), cada uno con tests reales.
- `packages/construdata/rag_multi_norma.py` — RAG multi-norma + delegador de
  motores + respaldo LLM.
- `packages/construdata/ideam_client.py` — datos abiertos IDEAM (datos.gov.co),
  sin API key. Ojo: el catálogo de estaciones mezcla departamentos con y sin
  tilde en el dato real (Bogotá/Boyacá/Guainía/Nariño/Quindío sí la llevan) —
  `_resolver_departamento()` ya lo resuelve, no reinventar el filtro.
- `infra/supabase/SCHEMA.md` + `infra/supabase/migrations/` — schema real
  documentado y migraciones reconstruidas byte a byte desde
  `supabase_migrations.schema_migrations`.
- `docs/comparacion.md` — comparación pública StructAI vs. IA genérica.
- `.github/workflows/ci.yml` — lint+build web, tests de los 7 motores, tests
  de integración de `apps/api` (usa Groq/OpenAI reales, no mocks).
- Roadmap activo: [issues del milestone "Colombia: cobertura nacional y
  visibilidad académica"](https://github.com/wilmerjoseperezorozco-dev/structai/milestone/1).

## Reglas de trabajo con este usuario

- Prioriza verificar sobre asumir — con evidencia real (SQL, retrieval,
  llamadas HTTP en vivo), no "debería funcionar".
- Corregir errores propios explícitamente en el momento en que se detectan,
  no silenciosamente.
- El usuario decide el rumbo del proyecto; no hace falta pedir permiso para
  cada paso técnico intermedio una vez la dirección está clara.
