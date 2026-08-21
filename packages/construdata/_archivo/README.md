# Archivo: scripts obsoletos

## `seed_ntc_knowledge.OBSOLETO.py`

Archivado el 2026-08-20 (repaso de backend, issue #8 en GitHub). Su propio
docstring ya documentaba el problema: apuntaba a un diseño de esquema
(`knowledge_nodes`/`knowledge_chunks`/`knowledge_edges`) que **nunca
existió** en el proyecto Supabase real, y generaba embeddings de 1536
dimensiones con OpenAI (`text-embedding-3-small`) cuando el esquema real de
`ntc_chunks.embedding` es `vector(384)` (el tamaño de
`paraphrase-multilingual-MiniLM-L12-v2`, el modelo local que usa
`rag_multi_norma.py`). Ejecutarlo tal cual habría fallado en el insert o,
peor, insertado embeddings de un espacio vectorial incompatible con el
resto del corpus, rompiendo la similitud coseno silenciosamente.

`ntc_chunks` se pobló con NTC/SGSST reales por otras vías (ver memoria del
proyecto — `scripts/ingest_normativa.py` y las rondas posteriores de
reauditoría). Este script no se necesita ni se debe rehabilitar sin
reescribirlo desde cero contra el esquema y el modelo de embeddings reales.
