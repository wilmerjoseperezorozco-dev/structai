# scripts/

Scripts de ingesta de contenido normativo a Supabase (pgvector). No corren en producción ni en CI — son de un solo uso, ejecutados manualmente cuando se cargó cada corpus.

## Convención (formalizada 2026-08-20, issue #8 punto 3)

**El script SÍ se versiona en git. El documento fuente NO.**

- **Scripts** (`extract_*.py`, `ingest_*.py`, `_ingest_*.py`, `insert_*.py`, `fix_*.py`) — siempre en `ingesta/<dominio>/`, siempre trackeados. Son código: pequeños, texto, y la única forma real de auditar de dónde salió cada chunk (trazabilidad académica — igual que el DOI/CITATION.cff del proyecto). Antes de esta fecha, la sesión de trabajo del 2026-08-20 (reauditoría de NSR-10 Título F/I/K.4 + 78 proveedores nacionales) había creado 21 scripts nuevos en `packages/construdata/normativa_raw/nsr10/`, una carpeta gitignorada — inconsistente con esta misma convención, que ya existía para el resto de `scripts/ingesta/`. Se migraron aquí (con `git mv` implícito: se copiaron y se borró el original) y se corrigió un bug real que ese movimiento habría introducido si no se hubiera revisado: los scripts calculaban `PROJECT_ROOT` con `Path(__file__).resolve().parents[4]`, calibrado para su profundidad original (`packages/construdata/normativa_raw/nsr10/`, 4 niveles bajo la raíz) — en su nueva ubicación (`scripts/ingesta/nsr10/`, 3 niveles) eso habría apuntado un directorio por encima de la raíz real del repo. Corregido a `parents[3]` y verificado que `apps/api/.env` se encuentra desde ahí antes de dar el cambio por bueno.
- **Documentos fuente** (PDF, Excel, dumps de texto extraído, catálogos intermedios) — SIEMPRE fuera de git, en `ingesta/<dominio>/raw/` (patrón `scripts/ingesta/*/raw/` en `.gitignore`, línea 44). Quedan como referencia de trabajo local, no se pierden, pero nunca se publican — mismo criterio ya aplicado a los PDFs "RAG+CAG" archivados (`packages/knowledge/_archivo/`, ver issue #8 punto 1): un documento de terceros o un dump de extracción intermedio no es código, no aporta a la reproducibilidad de forma proporcional a su peso/riesgo de licencia, y el script ya documenta de dónde salió (usualmente un `drive_file_id` citable).

`packages/construdata/normativa_raw/` (fuera de `nsr10/`, ya migrada) sigue existiendo para los dominios que aún no tienen scripts propios versionados (aci, aisc_360, apu_nacional, ccp14, cra, fratelli, gerencia_leyes, ntc, pavimentos, pot, ras2000, res0330, sgsst, tuneles, vias) — pendiente aplicar la misma migración si esos dominios llegan a tener scripts de ingesta reales que valga la pena versionar.

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
| `peru_e030/` | Primer corpus del programa de replicabilidad internacional — E.030 "Diseño Sismorresistente" de Perú, tabla propia `peru_e030_chunks` (espejo de `nsr10_chunks`, no reutilizada porque la numeración de artículos es incompatible entre normas). Base legal para citar verbatim: Art. 9(b) del Decreto Legislativo N° 822 (Ley de Derecho de Autor de Perú) excluye los textos oficiales legislativos/administrativos/judiciales del copyright — verificado 2026-08-24, misma categoría legal que NSR-10 en Colombia. Capítulos I (Disposiciones Generales), II (Peligro Sísmico: zonificación, perfiles de suelo S0-S4, parámetros de sitio, factor C), III (Categoría/Sistema Estructural/Regularidad: coeficiente R0 por sistema, irregularidades en altura/planta, coeficiente R=R0·Ia·Ip) y IV (Análisis Estructural: fuerza cortante en la base V, período fundamental T y tabla CT, análisis modal espectral CQC, análisis tiempo-historia) cargados a 2026-08-24. |

## `load_nsr10.py` — archivado 2026-08-20

**Corrección de una nota anterior de este mismo archivo**, que decía que este script era "la siguiente tarea pendiente" sobre el corpus NSR-10 — eso era un error de framing: su fuente (`packages/knowledge/nsr10/`, PDFs "RAG+CAG") resultó ser un export roto de un sistema RAG anterior, con títulos desplazados desde el origen (ver `packages/knowledge/_archivo/nsr10-rag-cag-roto/README.md`). No era "pendiente de ejecutar", era una fuente que no debía usarse. Movido a `_archivo/load_nsr10.OBSOLETO.py`. El corpus real de NSR-10 se construye directo desde los PDF oficiales de Google Drive, con los scripts activos de `ingesta/nsr10/`.
