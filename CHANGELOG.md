# Historial de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y versionado [SemVer](https://semver.org/lang/es/). La política completa de versiones, tags y milestones está en [`docs/VERSIONES.md`](docs/VERSIONES.md).

Cada versión corresponde a un tag `vX.Y.Z` sobre `master`. Los estados cerrados de investigación llevan además un tag `research/…` (ver la política). Las versiones `v1.1.0`–`v1.9.0` conservan también su tag descriptivo original por compatibilidad de enlaces.

## [Sin publicar] → v1.16.0

Precios y costos de obra, métricas del RAG sin LLM y anomalías de caudal. En curso: costo paramétrico de pavimentos y periodo de retorno de alcantarillas.

### Agregado
- Revisión de precios frente al catálogo IAD MIPYMES (`motor-apu`): tamizaje robusto por ítem, umbral conforme (|z| > 2,82) y evaluación por inyección de errores. Tag `research/precios-p1-p3`.
- Recomendador de insumos para APU por vecinos, validado ocultando un insumo a la vez.
- Métricas de evaluación del RAG que no dependen de un LLM: recall@K, MRR, NDCG, soporte de citas, proxy de alucinación numérica, abstención y latencia. Tag `research/metricas-sin-llm`.
- Anomalías de caudal IDEAM: comparación de la regla de producción con un z robusto estacional con persistencia. Tag `research/anomalias-caudal`.
- Resultados de H6 y de la frecuencia de crecientes (protocolos 21 y 24). Tags `research/protocolo-21`, `research/protocolo-24`, `research/h6`.

- Costo paramétrico de pavimentos (espesores de `motor-vias` × precios INVIAS 2026-1) y ejercicio de periodo de retorno económico de alcantarillas, con protocolo preregistrado. Resultados en `scripts/precios/RESULTADOS_COSTO_PARAMETRICO.md`. Tag `research/costo-parametrico`.
- Transmisión de TRM y petróleo al ICOCIV (DANE, 69 meses) y Monte Carlo del costo en riesgo de una obra vial, con protocolo preregistrado y validación fuera de muestra. Resultados en `scripts/precios/RESULTADOS_P3_P4.md`. Tag `research/icociv-p3-p4`.
- Política de versiones, `CHANGELOG.md`, milestones por fase y portada nueva (`README.md`; el detalle completo pasa a `docs/DETALLE_TECNICO.md`).

### Limitaciones documentadas
- `motor-vias` entrega la misma estructura de pavimento flexible (5/15/15 cm) en 28 de 32 combinaciones; probable error de unidades en los coeficientes estructurales (issue #103). Los costos paramétricos se presentan como el costo de lo que el motor entrega hoy.
- El periodo de retorno económico de alcantarillas resultó en el borde de la malla (T = 100) y casi insensible al costo; no se emite recomendación.
- La sensibilidad de la revisión de precios ante un error ×10 es de 0,64, por debajo del criterio preregistrado de 0,90: no se presenta como un detector confiable de errores de unidad.
- Las estimaciones de crecientes por estación no resultaron calibradas (la excedencia observada del Q10 fue 0,135); no se usan como base de diseño.

## [1.15.0] — Programa de investigación del Caribe y registro de vigencia normativa

Periodo: 6–7 de noviembre de 2026.

### Agregado
- Programa de análisis con datos abiertos y satelitales para el Caribe colombiano: relieve (Copernicus DEM), agua superficial (Sentinel-1), HAND, precipitación CHIRPS v3 y cruces con emergencias UNGRD. Todos los análisis tienen protocolo preregistrado y reportan también los resultados nulos.
- Protocolos 15, 16, 22 y 23 (sensibilidad de la lluvia a ENSO, contraste con el mapa de amenaza del SGC, susceptibilidad por pesos de evidencia y fórmulas candidatas). Tags `research/protocolo-15`, `-16`, `-22`, `-23`.
- Apéndice A-4 de la NSR-10 (Aa, Av, Ae y Ad por código DANE) ingestado desde el PDF y consolidado con el Decreto 092 de 2011.
- Registro de normas con estado de verificación y cadenas de modificación (`normas_registro`, `normas_modificaciones`).
- Registro de riesgos de la investigación y bibliografía verificada (`docs/investigacion/`).
- Series del DANE (IPC, PIB trimestral, cemento gris) con verificación cruzada y geografía de precios INVIAS 2026-1.

### Corregido
- Referencia errónea a un decreto como consolidación de la NSR-10 (era de subsidios de vivienda): corregida en base de datos, migraciones y documentación.
- Valores oficiales del Manual INVIAS 2008 en `motor-vias` (radios, distancia de parada y de adelantamiento) y pendientes máximas según la Tabla 4.2.
- La respuesta de precios ya no presenta la fecha de carga como fecha del precio ni da combustibles desactualizados como vigentes.
- Aviso de IA siempre visible en el chat (issue #85) y RLS habilitado en `microzonificacion_sismica_local`.

### Evaluación
- Paquete `eval-stats` y análisis estadístico retroactivo de los scorecards RAGAS (issue #95).

## [1.14.0] — Análisis geoespacial de amenazas, microzonificación y servidor MCP

Periodo: 29–30 de septiembre de 2026.

### Agregado
- Cruces con datos reales de movimientos en masa, pendiente (SRTM), geología, distancia a cauces, deforestación, sismos UNGRD, ONI y caudal IDEAM (issue #61). Se publican también los resultados nulos.
- Microzonificación sísmica local de Bogotá, Cali y Pereira, en producción como aviso informativo (issue #76).
- Factores de amortiguamiento (Eurocódigo 8 y ASCE 7-05/FEMA 450) como extensión opcional, trazable a NSR-10 A.3.8.1.
- Prototipo de servidor MCP que expone `/consultar` a clientes de IA (issue #78).
- Motor `motor-acero-frio` (NSR-10 F.4), MVP con ancho efectivo de Winter (issue #81).
- Cliente de deforestación IDEAM/SMByC por punto.

### Corregido
- Fórmula del espectro elástico NSR-10 A.2.6 en `motor-estructural`, que subestimaba Sa.
- Detección de la norma citada explícitamente en preguntas de motor (issue #58).

## [1.13.0] — Cierre verbatim de los Títulos A, B, J y F.5, y enrutador contrastivo

Periodo: 22–28 de septiembre de 2026.

### Agregado
- Cierre verbatim de los Títulos A (plan de 7 fases), B (con la decisión sobre las figuras Cp/GCp diferida al issue #56), J (incendios) y F.5 (aluminio, en 12 fases).
- Enrutador contrastivo de dominio por embeddings, conectado a producción como respaldo del enrutador por palabras clave; registro del método de enrutamiento por consulta (issue #35).
- Exportación del dataset de fine-tuning QLoRA desde corridas RAGAS reales y verificación de 105 casos.
- Trabajo de grado sustentado y aprobado con calificación Meritorio (4,7/5,0).

### Corregido
- Normalización de tildes en el enrutamiento (issue #59).

## [1.12.0] — Operación del RAG y motor de vulnerabilidad de vivienda

Periodo: 16–18 de septiembre de 2026.

### Agregado
- Caché de respuestas exactas, límite de tiempo a Groq y registro de costo de OpenAI.
- Sistema de feedback cerrado (backend y botones 👍/👎).
- Paquete reutilizable `rag-audit-kit` y CI de cobertura de ingesta que bloquea regresiones.
- Tabla paraguas `proyectos` cruzando los motores.
- Motor determinístico de vulnerabilidad de vivienda (checklist AIS, Título E), Fase 1 del issue #51.

### Corregido
- La CI ya no compite con la cuota de Groq de producción (issue #53).

## [1.11.0] — NSR-10 verbatim, integridad del corpus y evaluación RAGAS

Periodo: 31 de agosto – 13 de septiembre de 2026.

### Agregado
- Ingesta verbatim de los Títulos C, D, F y K, cierre del Título H (H.1–H.10) y ampliaciones de A y B.
- Auditoría numeral por numeral de los 11 títulos de la NSR-10.
- Evaluación RAGAS con n = 278, índices HNSW en las tablas de embeddings, catálogo de datos formal y auditoría de cambios a `profiles`.
- Búsqueda de precios con sinónimos regionales, deduplicación y refuerzo de sinónimos exactos.

### Corregido
- Re-troceo de todo el corpus: 493 chunks se truncaban en silencio por límite de tokens.
- Paginación silenciosa en la zonificación de Perú y en el Aa/Av por municipio (se perdía el 47 % de los distritos peruanos).
- CI en rojo por reranker sin cachear y Node desalineado.

## [1.10.0] — Replicabilidad internacional, seguridad y producto

Periodo: 24–28 de agosto de 2026.

### Agregado
- Corpus de Perú (E.030, edición vigente RM 183-2026-VIVIENDA) y Ecuador (NEC-SE-DS), conectados a `/consultar`, con búsqueda híbrida RRF.
- Señal de vulnerabilidad de vivienda (Sisbén IV) cruzada con amenaza sísmica SGC, e histórico de emergencias UNGRD por municipio.
- Aviso de responsabilidad profesional determinístico (issue #18).
- Plan Pro de lanzamiento, rol de administrador y checkout.
- SEO base y datos estructurados.

### Seguridad
- RLS activado en 11 tablas públicas; cabeceras HTTP de seguridad en la API.
- Parches de vulnerabilidades reales de dependencias (backend y frontend) y auditoría de superficie clásica (SQLi, XSS, DDoS, sesión, fuerza bruta).

### Corregido
- La E.030 de Perú se había cargado con la edición 2019 cuando la vigente era otra: se reemplazó por la RM 183-2026-VIVIENDA y se añadió la regla de verificar vigencia antes de ingestar.

## Versiones anteriores

`v0.1.0` y `v1.0.0`–`v1.9.0` están descritas en sus [releases de GitHub](https://github.com/wilmerjoseperezorozco-dev/structai/releases).
