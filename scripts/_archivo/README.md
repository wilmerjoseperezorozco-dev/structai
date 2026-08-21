# Archivo: scripts obsoletos

## `load_nsr10.OBSOLETO.py`

Archivado el 2026-08-20 (repaso de backend, issue #8 en GitHub). Leía los
PDFs "RAG+CAG" de `packages/knowledge/_archivo/nsr10-rag-cag-roto/`
(fuente rota, ver el README de esa carpeta) y nunca llegó a ejecutarse por
completo. El pipeline real usado para cargar NSR-10 título por título fue
directo contra los PDF oficiales de Google Drive, con scripts que sí siguen
activos en `scripts/ingesta/nsr10/` (`insert_titulo_d_nucleo.py`,
`insert_titulo_h_i_nucleo.py`, `extract_nsr10_titulo_g.py`,
`ingest_nsr10_titulo_g.py`) — esos NO están archivados porque sí se
ejecutaron y sí cargaron contenido real verificado.
