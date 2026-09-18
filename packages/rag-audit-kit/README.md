# rag-audit-kit

Auditoría de cobertura de un corpus RAG contra su documento fuente:
detección de huecos por numeral jerárquico, reportes de cobertura por
capítulo, y una heurística de confianza para detectar chunks "resumen
disfrazado de completo".

## Por qué existe

StructAI audita los 11 títulos de la NSR-10 con el mismo método, sesión
tras sesión, desde hace semanas: extraer los numerales reales del PDF
oficial, compararlos contra lo que ya tiene chunk en Supabase, y revisar a
mano cada candidato a hueco antes de decidir qué ingestar. Ese método
nunca vivió en código reusable — vivía en la cabeza de quien hacía la
auditoría cada vez. Este paquete lo extrae, sin acoplarlo a NSR-10 ni a
Supabase: el patrón de numeral es configurable, y las funciones reciben
listas de Python (texto fuente, valores ya cubiertos), no un cliente de
base de datos concreto. El mismo método sirve para auditar la cobertura
de cualquier otra base de conocimiento con estructura jerárquica —
documentación de una API versionada, una wiki corporativa, una norma en
otro idioma.

## Uso

```python
from src import extraer_numerales, dedup_preservando_orden, comparar_cobertura, reporte_markdown, evaluar_confianza

texto_fuente = abrir_y_extraer_texto("documento.pdf")  # pypdf, pdftotext, lo que sea
numerales = dedup_preservando_orden(extraer_numerales(texto_fuente))

valores_cubiertos = [fila["seccion"] for fila in consultar_corpus_existente()]

reporte = comparar_cobertura(numerales, valores_cubiertos)
print(reporte_markdown(reporte, titulo="Cobertura Título X"))
# -> misma tabla que ya se escribe a mano en docs/fuentes-normativas.md
```

Para el patrón por defecto (`PATRON_NUMERAL_DEFAULT`, calibrado sobre
numerales tipo "A.3.3.4"), ver `src/numerales.py`. Otro dominio pasa su
propio `re.Pattern` a `extraer_numerales(texto, patron=...)`.

## Límite honesto, encontrado validando contra un caso real

Validando este paquete contra Título I de la NSR-10 (ya auditado a mano,
ver `docs/fuentes-normativas.md`) se encontró que varios corpus usan
`seccion` = solo el capítulo o rango padre en texto libre ("I.1", "I.2.1 a
I.2.3") para representar todo su contenido descendiente, sin decirlo de
forma explícita numeral por numeral. Este paquete soporta rangos
explícitos ("X a Y") pero **decide, a propósito, no asumir que un padre
bare cubre todos sus hijos** — sub-reporta cobertura (candidatos a hueco
que una revisión humana descarta rápido) en vez de sobre-reportarla (un
hueco real escondido detrás de una cobertura que en realidad no existía).
Si `pct_cobertura` sale bajo pese a que el título tiene volumen real de
chunks, el siguiente paso es revisar el `texto` real de esos chunks, no
confiar ciegamente en el número — exactamente el mismo criterio que ya
aplicaba este proyecto antes de que existiera esta herramienta.

Detalle completo, incluida la corrida real que encontró esto, en
`tests/test_rag_audit_kit.py::test_validacion_real_titulo_i_reproduce_auditoria_manual`.

## Qué NO hace (todavía)

- No lee PDFs ni ningún formato de documento — recibe texto plano, ya
  extraído por quien llama.
- No decide automáticamente qué hacer con un hueco — genera candidatos
  para revisión humana, nunca una acción.
- `evaluar_confianza` es una señal (ratio de longitud chunk/fuente), no
  una prueba — un ratio bajo puede ser una sección genuinamente breve mal
  detectada como sospechosa; siempre verificar contra el documento real.
