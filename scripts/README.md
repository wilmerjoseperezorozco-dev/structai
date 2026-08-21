# scripts/

Scripts de ingesta de contenido normativo a Supabase (pgvector). No corren en producción ni en CI — son de un solo uso, ejecutados manualmente cuando se cargó cada corpus.

## `ingesta/<dominio>/`

Cada subcarpeta es un pipeline ya ejecutado para un corpus específico, con el mismo patrón:

- `extract_*.py` — procesa el texto crudo (PDF/Word extraído a texto plano en `raw/`, cuando existe) y genera los chunks estructurados.
- `ingest_*.py` — sube esos chunks a Supabase (`motor_chunks`, `nsr10_chunks`, `ntc_chunks`, etc., según el dominio).
- `raw/` (cuando existe, sin trackear en git) — texto fuente extraído de los PDF/Word originales, usado como input del `extract_*.py` correspondiente. Son archivos de trabajo intermedios, no el documento oficial.

Reorganizado el 2026-08-02 (antes vivían sueltos en `scripts/`, ~35 archivos en la raíz sin agrupar). Ninguno de estos scripts es referenciado por código de producción, CI, ni `package.json` — son historial de cómo se cargó cada corpus, útiles solo si hay que re-ejecutar una ingesta o auditar de dónde salió un chunk.

| Carpeta | Corpus |
|---|---|
| `ccp14/` | Catálogo Construdata 2026 (precios APU) |
| `cra/` | Resoluciones CRA (tarifas de acueducto/alcantarillado) |
| `gerencia/` | Leyes de contratación pública (Ley 80/1150/1474) para motor-gerencia |
| `interventoria/` | Contenido de interventoría de obra |
| `normas_ensayo/` | Normas de ensayo (INV E-1xx / NTC de laboratorio) |
| `nsr10/` | Título G de NSR-10 + el fix de reetiquetado E/F/G del 2026-07-30 |
| `pavimentos/` | Diseño y mantenimiento de pavimentos (AASHTO-93 / INVIAS) |
| `pot/` | Contenido de Plan de Ordenamiento Territorial |
| `res0330/` | Resolución 0330 de 2017 (RAS) |
| `ras2000/` | Corpus real RAS 2000 (303 chunks, reemplazó los 13 redactados a mano) — motor AquAI |
| `tuneles/` | Contenido técnico de túneles |
| `motores/` | `ingest_motor_chunks.py` — carga GeoPot, Vías y Gerencia en `motor_chunks` (AquAI se carga aparte desde `ras2000/`) |
| `normativa_general/` | SGSST (Decreto 1072, Ley 1562), ISO 9001, NTC 1500, y el corpus general de `ingest_normativa.py` |

## `load_nsr10.py` — archivado 2026-08-20

**Corrección de una nota anterior de este mismo archivo**, que decía que este script era "la siguiente tarea pendiente" sobre el corpus NSR-10 — eso era un error de framing: su fuente (`packages/knowledge/nsr10/`, PDFs "RAG+CAG") resultó ser un export roto de un sistema RAG anterior, con títulos desplazados desde el origen (ver `packages/knowledge/_archivo/nsr10-rag-cag-roto/README.md`). No era "pendiente de ejecutar", era una fuente que no debía usarse. Movido a `_archivo/load_nsr10.OBSOLETO.py`. El corpus real de NSR-10 se construye directo desde los PDF oficiales de Google Drive, con los scripts activos de `ingesta/nsr10/`.
