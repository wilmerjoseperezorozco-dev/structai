# Protocolo: ¿Docling extrae las páginas A.2 de la NSR-10 mejor que lo que tenemos? (fijado el 2026-11-08, antes de ejecutar Docling)

**Pregunta.** Sobre las páginas del Título A que contienen el espectro de diseño y las tablas de zonas de amenaza (A.2.3 a A.2.6), ¿Docling reproduce los números y numerales del documento con más fidelidad que `pypdf`, que es lo que hoy alimenta la ingesta?

**Entrada.** `raw/NSR-10-56-81.pdf`, páginas 3, 4, 8 a 17 (tablas A.2.3-2, A.2.4-x, A.2.5-x y espectro A.2.6; el PDF completo tiene 26 páginas, A-13 a A-38). Docling 2.149.0 con la configuración por defecto (OCR desactivado porque las páginas tienen capa de texto, tablas activadas), instalado en una carpeta aislada.

**Referencia (verdad de terreno).** El texto de los fragmentos de las secciones A.2.3 a A.2.6 en `_ingest_titulo_a_a2_verbatim.py`, transcritos visualmente del PDF en una sesión anterior y verificados por recuperación. **Límite:** la referencia no es independiente del todo (la hizo una persona leyendo las páginas, pueden quedar errores de transcripción) y se transcribió para texto, no para ser un banco de pruebas. Una discrepancia entre un método y la referencia puede ser un error del método **o** de la referencia: las discrepancias se revisan a mano contra la imagen de la página.

**Fichas (fijadas ahora).**
- *Ficha numérica:* cada número con parte decimal o con 3 o más dígitos, como cadena normalizada (coma decimal a punto, sin espacios).
- *Ficha de numeral:* cada numeral de la forma `A.d.d(.d)*` y las ecuaciones `A.d.d-d`.

**Métrica.** Recall por conjunto: fracción de las fichas distintas de la referencia que aparecen en la salida del método. Se calcula para `pypdf` y para Docling (Markdown exportado), por separado para fichas numéricas y de numeral, en total y por grupo de páginas (tablas: 3-4, 10-12, 14; espectro: 15-17).

**Criterio de éxito (fijado antes de ver ningún resultado).** Docling «mejora» si su recall numérico total supera al de `pypdf` en **al menos 3 puntos porcentuales** y su recall de numerales no es menor. Con una referencia de unas decenas a cientos de fichas, diferencias menores de 3 puntos no se distinguen del ruido de la referencia.

**Prueba de tabla (descriptiva).** En la Tabla A.2.3-2 (capitales): número de filas que Docling entrega con nombre, Aa y Av iguales a los de la referencia, sobre las filas de la referencia. Para `pypdf` no hay estructura de tabla; se reporta el recall de las parejas (Aa, Av) cercanas al nombre solo si es viable, y si no, se declara que no es comparable.

**Qué NO se concluye.** Nada sobre otros títulos ni sobre páginas escaneadas (estas tienen capa de texto), ni sobre figuras (las ecuaciones tipográficas pueden salir como imagen). El rendimiento sobre el resto del Título A (A.9, por ejemplo) requeriría otra prueba. Tampoco se evalúa el costo en tiempo y memoria más allá de reportarlo.

**Limitaciones de antemano.** Solo ~13 páginas; una configuración; sin ajuste de parámetros; equipo con poca memoria libre, así que se reporta el tiempo medido tal cual.

**Qué se publica pase lo que pase.** Recall de ambos métodos, la lista de discrepancias revisadas y quién tenía razón en cada una, y el tiempo/memoria.
