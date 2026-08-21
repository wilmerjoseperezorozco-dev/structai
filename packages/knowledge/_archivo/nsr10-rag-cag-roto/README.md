# Archivo: PDFs "RAG+CAG" — fuente rota, nunca usada realmente

Archivados el 2026-08-20 (repaso de backend, issue #8 en GitHub).

Estos 9 PDFs (`RAG+CAG Capitulo A.pdf` ... `RAG+CAGcapituloH.pdf`) NO son
extractos oficiales de la NSR-10. Son un **export JSON/LaTeX roto de un
sistema RAG/CAG anterior** (de una sesión de trabajo previa a este
proyecto), descubierto el 2026-08-03 al depurar por qué el chat respondía
mal sobre el Título F: el archivo nombrado "Capitulo F.pdf" traía en su
propio metadata `"titulo_completo": "Estructuras de Madera"` — cuando el
Título F real de la NSR-10 es "Estructuras Metálicas". El contenido
semántico de cada chunk generado desde estos PDFs era mayormente correcto,
pero la LETRA del título venía desplazada desde el origen — un problema
de la fuente, no de cómo se procesó.

Ver `scripts/ingesta/nsr10/fix_nsr10_titulos_reales.py` (no archivado, sigue
en `scripts/ingesta/nsr10/`) para el detalle completo de esa corrección real
que sí se aplicó en producción.

## Por qué no se usaron nunca en serio

`scripts/_archivo/load_nsr10.OBSOLETO.py` (el pipeline que leía estos PDFs)
nunca llegó a ejecutarse de forma completa — el trabajo real de ingesta de
NSR-10 título por título (Título C, D, F, G, H, I, luego la reauditoría
completa de F.3 e I del 2026-08-20) se hizo **directo contra los PDF
oficiales reales** de Google Drive (carpeta "METADATOS", catálogo
verificado página por página), nunca desde estos archivos.

## Por qué se archivan y no se borran

Quedan como referencia histórica de un intento anterior y de la fuente de
un bug real ya corregido — mismo criterio que
`infra/supabase/_archivo/001_auth_freemium.OBSOLETO.sql.txt`. No se
importan desde ningún código activo.
