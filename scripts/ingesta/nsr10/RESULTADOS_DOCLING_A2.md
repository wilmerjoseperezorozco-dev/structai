# Resultados: Docling frente a pypdf en las páginas A.2.3-A.2.6 de la NSR-10 (2026-11-08)

Protocolo fijado y publicado antes de ejecutar Docling (commit `e1d53a0`): [`PROTOCOLO_DOCLING_A2.md`](PROTOCOLO_DOCLING_A2.md). Código: `docling_a2_prueba.py`. Salida: `docling_a2_resultados.json`. Docling 2.149.0, configuración por defecto, páginas 3 a 17 de `NSR-10-56-81.pdf`. Referencia: 59 fichas numéricas y 71 numerales de los fragmentos A.2.3 a A.2.6 de `_ingest_titulo_a_a2_verbatim.py`.

## Criterio de éxito: se cumple por la regla, con una ventaja mínima
| Método | Recall numérico (59 fichas) | Recall de numerales (71) |
|---|---:|---:|
| pypdf (lo que usa hoy la ingesta) | 88,1 % (52) | 100 % |
| Docling | **91,5 % (54)** | 100 % |

La regla fijada era «Docling mejora si su recall numérico supera al de pypdf en al menos 3 puntos y el de numerales no es menor». La diferencia es de **3,4 puntos, es decir dos fichas de 59**. La regla se cumple, pero el protocolo ya decía que diferencias de pocos puntos no se distinguen del ruido de la referencia; esta queda apenas por encima del umbral. **No la leo como una mejora sólida.**

## Lo que sí aporta Docling: tablas estructuradas
En la Tabla A.2.3-2 (32 capitales) Docling entrega las filas con columnas separadas: **32 de 32 filas con Aa y Av iguales a la referencia** (31 se emparejaron automáticamente; la de Bogotá no se emparejó solo porque Docling escribe «D. C.» con un espacio, y la revisé a mano: 0,15 / 0,20 / Intermedia, correcta). Detectó 8 tablas. pypdf entrega las mismas cifras pero como líneas de texto sin estructura de columnas; **no probé** qué tan fiable es reconstruir las columnas desde ese texto.

## Lo que Docling no resolvió: las ecuaciones
Las ecuaciones A.2.6-1 a A.2.6-7 salen como `<!-- formula-not-decoded -->`: **no se reconocieron**. Con la configuración por defecto Docling no decodifica fórmulas (tiene una opción de enriquecimiento de fórmulas que **no activé ni probé**; requiere otro modelo). Las fichas que faltan en ambos métodos (0,48; 0,62; 1,87; 3,9 y, solo en Docling, 0,6) corresponden en su mayoría a esas ecuaciones y a constantes del espectro. Es justamente el contenido más importante de A.2.6.

## Corrección a mi propio script
Los recalls «por grupo de páginas» del JSON (`por_grupo`) no son interpretables: comparé cada grupo contra **toda** la referencia, no contra la parte que le corresponde, por eso salen tan bajos (0,05 a 0,6). No los usé para ninguna conclusión. La comparación total sí es válida.

## Costo
Conversión de 15 páginas: **259 s** en CPU (unos 17 s por página, incluida la carga de modelos en la primera ejecución); memoria del proceso 457 MB. Descarga total de modelos y paquetes cercana a 1 GB (la primera ejecución se repitió porque la ruta de la caché superaba el límite de 260 caracteres de Windows, un error mío de configuración; la segunda usó `C:\tmp\hf`).

## Qué concluyo y qué no
1. En estas páginas (con capa de texto), **pypdf ya extrae casi todo lo numérico**; Docling añade estructura de tablas y un par de cifras. El cuello de botella del Título A (~63 %) está en la **cobertura de secciones**, no en extraer mejor estas páginas.
2. Docling es útil donde la estructura de la tabla importa (columnas Aa/Av por ciudad, tablas de coeficientes). **No** sirve, con la configuración por defecto, para las ecuaciones.
3. No concluyo nada sobre páginas escaneadas, otros títulos ni la opción de fórmulas.

## Límites
La referencia es una transcripción visual previa (puede tener errores propios). Solo 59 fichas numéricas. Una configuración, sin ajuste. Los tiempos son de un equipo con poca memoria libre.

## Siguiente paso posible (no ejecutado)
Probar el enriquecimiento de fórmulas de Docling sobre 3 páginas de A.2.6, y usar Docling solo para tablas en la ingesta de las secciones que aún faltan, comparando cada tabla con el PDF antes de ingestar.
