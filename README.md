# StructAI — IA con trazabilidad normativa para ingeniería civil en Colombia

[![Web](https://img.shields.io/badge/web-structai.online-0ea5e9)](https://www.structai.online)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21851529.svg)](https://doi.org/10.5281/zenodo.21851529)
[![Estado en vivo](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fstructai-api-235651108862.us-east1.run.app%2Fdata-status&query=%24.corpus_normativo.nsr10_chunks.chunks&label=chunks%20NSR-10%20en%20vivo&color=16a34a)](https://structai-api-235651108862.us-east1.run.app/data-status)

**`Construdata`** es el nombre interno del repositorio; **StructAI** es la marca pública, en [structai.online](https://www.structai.online). Todo lo citado en este documento se puede verificar ahora mismo contra producción — [`/data-status`](https://structai-api-235651108862.us-east1.run.app/data-status) y [`/health?deep=true`](https://structai-api-235651108862.us-east1.run.app/health) — sin tener que confiar en el texto.

**Si esto te sirve:** [pruébalo en structai.online](https://www.structai.online) (plan gratis con NSR-10 completa) · una ⭐ ayuda a que más gente lo encuentre · para citarlo académicamente, usa el DOI del badge de arriba · acceso educativo gratuito para programas de ingeniería civil, ver [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

<details>
<summary><b>📑 Mapa del documento</b> — todo lo de abajo, en orden</summary>

1. [Por qué existe esto](#por-qué-existe-esto)
2. [Qué hay hoy, verificado en vivo](#qué-hay-hoy-verificado-en-vivo--no-una-promesa)
3. [Auditoría verbatim de la NSR-10, título por título](#auditoría-verbatim-de-la-nsr-10-título-por-título)
4. [Infraestructura del RAG — rendimiento medido, no solo diseñado](#infraestructura-del-rag--rendimiento-medido-no-solo-diseñado)
5. [La metodología](#la-metodología--cómo-funciona-esto-de-verdad)
6. [Evaluación empírica RAGAS](#evaluación-empírica-del-rag--medido-no-solo-diseñado)
7. [Los 7 motores](#los-7-motores)
8. [Lo que todavía no es](#lo-que-todavía-no-es--honestidad-antes-que-marketing)
9. [Hacia dónde va esto](#hacia-dónde-va-esto--lo-aplicativo-y-lo-que-viene)
10. [Colaboración institucional](#colaboración-con-universidades-gremios-y-cámaras-de-comercio)
11. [Arquitectura, estructura del repo, desarrollo local, deploy, secrets](#arquitectura-rag--cómo-está-construido-sin-rodeos)

</details>

## Por qué existe esto

El 10 de agosto de 2026 un terremoto de magnitud 7.4 dejó 289 muertos en Colombia (cifra oficial final del Gobierno). No fue una sorpresa geológica — el país entero está sobre zona de amenaza sísmica, y buena parte de su vivienda se construyó antes de que existieran normas sismo-resistentes estrictas, o después pero sin que nadie verificara en obra que se cumplían. Soy ingeniero civil, y llevo meses construyendo StructAI sobre una convicción simple: si un ingeniero puede consultar la norma exacta —no una aproximación, no un resumen genérico de una IA que nunca vio el reglamento colombiano— en el momento en que está calculando, se cometen menos errores. En este país, un error de cálculo estructural no es un detalle técnico. Es una vida.

Esa es la apuesta completa: una plataforma de IA que responde preguntas de ingeniería civil citando la norma real —NSR-10, RAS 2000, INVIAS, NTC— con capítulo y artículo, nunca con una cita inventada. Si no tiene la información cargada, lo dice.

<details>
<summary><b>La región tiene un patrón, no es solo Colombia</b> — comparación con Ecuador y Venezuela</summary>

Seis semanas antes del terremoto de Chocó, Venezuela sufrió el suyo: un sismo doble de magnitud 7,2/7,5 el 24 de junio de 2026, epicentro frente a La Guaira, a solo 10 km de profundidad. Cruzando los tres sismos más recientes y mejor documentados de la región andino-caribeña con datos públicos de USGS, informes oficiales de cada país y una estimación del Banco Mundial, aparece un patrón que no depende de la magnitud:

| Evento | Fecha | Magnitud | Profundidad | Muertos | Pérdidas económicas |
|---|---|---|---|---|---|
| Ecuador — Pedernales | abr-2016 | 7,8 | 20 km | 656 | US$3.000M+ |
| Colombia — Chocó | ago-2026 | 7,4 | ~103–110 km | 289 | US$9.571M |
| Venezuela — La Guaira | jun-2026 | 7,2 / 7,5 | 10 km | 6.301–6.438 | US$19.600M |

Venezuela tuvo el sismo de *menor* magnitud de los tres y, aun así, más de nueve veces las muertes de Ecuador y más de veinte veces las de Colombia. La variable que explica la diferencia no es cuán fuerte tembló en el hipocentro — es cuán cerca de la superficie ocurrió, y cuánta población densamente construida estaba directamente encima. Profundidad y exposición poblacional ya se pueden mapear hoy con datos públicos. Lo que ningún país de la región tiene mapeado sistemáticamente todavía es la tercera variable: qué tan vulnerable es, edificio por edificio, lo que ya está construido. Colombia (autoconstrucción sin supervisión técnica) y Venezuela (edificios con planta baja flexible, señalados por su propio Colegio de Ingenieros al pedir la actualización de su norma) tienen el mismo vacío, con nombres distintos. Esa tercera variable es la línea de trabajo real descrita en ["Hacia dónde va esto"](#hacia-dónde-va-esto--lo-aplicativo-y-lo-que-viene).

*Fuentes: USGS; Servicio Geológico Colombiano y UNGRD; informes oficiales de Ecuador y Venezuela; Banco Mundial. Cifras a la última actualización oficial disponible; deliberadamente no se citan nombres de víctimas ni de edificaciones específicas.*

</details>

**Nota de integridad**: un primer intento de pipeline automático de ingesta resultó ser un export roto de un sistema RAG anterior, con contenido desplazado desde su título de origen — se descartó por completo y quedó archivado (`packages/knowledge/_archivo/`), nunca en uso. Todo el corpus real se extrae directo de los PDF oficiales, con verificación cruzada contra el catálogo maestro de cada norma antes de publicarse. Cuando se encuentra un lote mal etiquetado o de baja confianza —ha pasado, más de una vez— se elimina y se documenta por qué, no se disimula.

## Qué hay hoy, verificado en vivo — no una promesa

Todo lo que sigue se comprueba ahora mismo contra producción: [`GET /data-status`](https://structai-api-235651108862.us-east1.run.app/data-status).

| Corpus | Contenido | Cifra real hoy |
|---|---|---|
| **NSR-10** | Los 11 títulos (A–K) cargados. Los 11 ya pasaron auditoría estricta numeral por numeral (barrido completo) — detalle título por título [más abajo ↓](#auditoría-verbatim-de-la-nsr-10-título-por-título) | 8.454 chunks |
| **NTC + SGSST** | 18 normas técnicas colombianas (ICONTEC) + marco de Seguridad y Salud en el Trabajo (Decreto 1072/2015, Ley 1562/2012, Res. 0312/2019) | 294 chunks |
| **Motores de dominio** (AquAI/RAS 2000, GeoPot, Vías/INVIAS, Gerencia) | Corpus propio por motor, normativa específica de cada disciplina | 4.060 chunks |
| **Precios de referencia** | Actividades de construcción con desglose de insumos. Para 927 de 4.566 actividades (20,3%) el chat ya devuelve el desglose material/mano de obra/equipo real, no solo el precio todo-costo | 4.566 actividades · 10.281 insumos |
| **Proveedores con precio verificado** | 24 ferreterías del Atlántico con SKU real + 78 proveedores mipyme nacionales (IAD MIPYMES / Colombia Compra Eficiente), 114.616 precios individuales — 70 de 78 (90%) con ciudad/departamento real, cruzados contra SECOP II y RUES, en 22 departamentos | 102 proveedores |
| **Datos oficiales en vivo, cobertura nacional** | Amenaza sísmica NSR-10 (SGC, Aa/Av/zona) · anomalía estadística de caudal (IDEAM, 60+ años de histórico, nunca una alerta oficial) · suelos rurales (IGAC/UPRA) · señal de vulnerabilidad de vivienda por material de pared (Sisbén IV, nunca una evaluación estructural) · histórico real de emergencias (UNGRD, 2019-2024 — lo que ya pasó, nunca un pronóstico) | 1.121 municipios (SGC) · 949 estaciones (IDEAM) · 169.088 unidades de suelo (IGAC) · 1.099 municipios (Sisbén) · 41.893 eventos (UNGRD) |
| **Perú y Ecuador — no solo Colombia** | E.030 (Perú, ya en la edición vigente RM 183-2026-VIVIENDA) y NEC-SE-DS (Ecuador) verbatim, conectadas a `/consultar`, cada una con su propio aviso profesional (CIP / CICE) y zonificación sísmica por distrito | 204 chunks + 1.884 distritos (Perú) · 395 chunks + 512 localidades (Ecuador) |

<details>
<summary>Por qué Perú y Ecuador, y no un país al azar — y por qué la fila de datos oficiales trae dos tipos de señal distintos</summary>

Los tres países comparten el mismo motor sísmico real — la subducción de la placa de Nazca — así que no es una expansión comercial genérica, es la misma línea de falla. Construir los tres corpus con el mismo rigor produjo un hallazgo real: Colombia y Ecuador convergen en el mismo sistema de clasificación de suelos (A-F, mismos umbrales de velocidad de onda de corte), algo que el estudio comparativo de referencia de la región (WCEE 2012, Bommer y Pinho) no pudo ver porque se hizo contra la norma ecuatoriana de 2001, ya reemplazada — no es una crítica a ese estudio, es lo que pasa al comparar las normas *vigentes hoy*, verbatim, en vez de citar una comparación de más de una década como si describiera el estado actual.

Amenaza sísmica, anomalía de caudal y suelos son señales de **antes** de un evento — dónde hay más riesgo latente. Sisbén y UNGRD son la mitad de **después** — dónde ya sabemos que hay más población vulnerable, y qué tan grave fue el impacto real la última vez. Cruzar ambas mitades nació directo del terremoto de agosto de 2026: no es solo para calcular una estructura nueva, es para priorizar dónde enfocar una respuesta real. Sigue en desarrollo, con dos frentes abiertos sin resolver: el subregistro de comunidades étnicas en la respuesta oficial ([issue #15](https://github.com/wilmerjoseperezorozco-dev/structai/issues/15)) y si vale la pena una referencia rápida de la NSR-10 para brigadas de evaluación de daño en campo, protocolo ATC-20 ([issue #16](https://github.com/wilmerjoseperezorozco-dev/structai/issues/16)).

</details>

## Auditoría verbatim de la NSR-10, título por título

Método: extraer con `pypdf`/`pdftotext` cada numeral real del PDF fuente y compararlo contra lo que hay en la base de datos — no solo mirar si el chunk que existe se ve completo. Los 11 títulos ya pasaron por esto, barrido completo, ninguno sin auditar.

| Título | Estado | Numerales reales | Hallazgo clave |
|---|:---:|---|---|
| **A** — Requisitos generales | 🟡 Parcial | — | 6 capítulos completos aún sin cobertura; el de irregularidades (A.3.3) ya cerrado |
| **B** — Cargas | 🟡 Parcial | 7 secciones | 3 de 7 secciones ya cerradas, cierre progresivo |
| **C** — Concreto estructural | ✅ Cerrado | 26 huecos → 0 | El más grande del corpus (~1,4% faltante); hallazgo mayor: el capítulo C.18.5 completo (preesforzado) no tenía ni un chunk |
| **D** — Mampostería | ✅ Cerrado | 9 huecos → 0 | Hueco puntual, cerrado el mismo día que se encontró |
| **E** — Vivienda de 1 y 2 pisos | ✅ Limpio | 252 | Único hallazgo sin confirmar: remisión cruzada a un numeral (E.7.26.2) que no existe como encabezado real, probable typo del documento fuente |
| **F** — Estructuras metálicas | 🟡 Parcial | — | F.1–F.4 (acero) 100% verbatim; falta cerrar el tramo final de F.5 (aluminio) |
| **G** — Madera y guadua | ✅ Cerrado | 18 huecos → 0 | Incluye la corrección de un typo real del documento (G.12.4.2.2 impreso → G.12.3.2.2 real) |
| **H** — Estudios geotécnicos | ✅ Cerrado | H.3.3–H.10 | Cubría solo ~18% al auditarlo; cerrado por completo la misma sesión |
| **I** — Supervisión técnica | ✅ Limpio | — | Sin hallazgos |
| **J** — Requisitos de protección contra incendio | 🔴 Pendiente | 159 reales, 49 chunks | El hueco más grande y de tipo distinto: casi todo el título está en resumen parafraseado, no verbatim — candidato a re-ingesta completa, dejado explícito para otra sesión |
| **K** — Requisitos complementarios | ✅ Cerrado | K.4.3.10–16 | Corregía una afirmación propia anterior de "K.4.3 completo" |

**Resumen honesto**: 8 de los 10 títulos re-auditados tenían algún hueco real (todos menos I y E). De esos 8, **H, K, G, D y C ya están cerrados en verbatim completo** — solo quedan **A, B y J** con hueco real pendiente, J el más grande y explícitamente diferido. Detalle completo, con cada numeral y cada excepción documentada, en [`docs/fuentes-normativas.md`](docs/fuentes-normativas.md).

## Infraestructura del RAG — rendimiento medido, no solo diseñado

Igual que el corpus, la infraestructura de búsqueda se audita con evidencia real, no se da por buena porque "no tira error". Cuatro bugs reales encontrados y corregidos, cada uno verificado con `EXPLAIN ANALYZE` o con una segunda auditoría independiente antes de darlo por cerrado:

| # | Problema real encontrado | Cómo se detectó | Corrección |
|---|---|---|---|
| 1 | El modelo de embeddings trunca en silencio cualquier fragmento de más de 128 tokens para la búsqueda semántica | Auditoría con el tokenizador real (no una estimación por caracteres): 493 de 4.129 fragmentos (11,9%) excedían el límite, con severidad desigual por título (K/B/J/A al 100%, C/D al 0%) | Los 493 se volvieron a fragmentar respetando el límite real, sin releer ningún PDF — verificado con una segunda auditoría independiente: 0% sobre el límite |
| 2 | El índice `ivfflat` de pgvector daba recall real de ~10% — un chunk con similitud coseno 0,60 contra su propia consulta no aparecía ni en el top-50 | Comparación manual del cálculo de similitud contra el resultado real del RPC de búsqueda | Índice eliminado y reemplazado por **HNSW** (nativo de pgvector) — recall@10 verificado empíricamente: 99,6–100% en las 5 tablas de embeddings |
| 3 | El único índice de texto completo (GIN) estaba sobre una expresión distinta a la que usa la función de búsqueda real — nunca se usaba | Medición de latencia real de `search_knowledge()`: forzaba `Parallel Seq Scan` completo en 3 tablas (~1,4s) | GIN nuevo, alineado exacto con la expresión real de la función |
| 4 | La sub-consulta compartida por las dos ramas de búsqueda (semántica y léxica) se materializaba por estar referenciada dos veces — anulando por completo los índices nuevos | `EXPLAIN ANALYZE` del cuerpo real de la función (una llamada a función es una caja negra para el planificador — hubo que reconstruir la consulta exacta para verlo) | `NOT MATERIALIZED` explícito — sin tocar la lógica, un solo hint |

**Progresión medida, misma consulta real, de punta a punta:**

| Paso | Latencia de `search_knowledge()` |
|---|---:|
| Antes (sin índice vectorial) | 3.803 ms |
| + índices HNSW y GIN | 2.387 ms |
| + `NOT MATERIALIZED` | **626 ms** |

**~83% de reducción total**, con correctez verificada en cada paso (no solo velocidad): mismos resultados sensatos, y las rutas de filtro por norma y por motor siguen funcionando. Detalle completo, con cada plan de ejecución real, en el historial de commits públicos y en [`infra/supabase/migrations/`](infra/supabase/migrations/).

## La metodología — cómo funciona esto de verdad

StructAI no es un chatbot con un PDF pegado en el prompt. Es un sistema de recuperación aumentada (RAG) con una regla que no se negocia: **una cita inventada es peor que no citar nada, porque parece verificable y no lo es.**

1. **Búsqueda híbrida, no solo semántica.** Similitud vectorial (embeddings locales, sin costo por consulta) + búsqueda léxica de texto completo, fusionadas con Reciprocal Rank Fusion.
2. **El modelo cita solo lo que está en el contexto recuperado.** Si un artículo no aparece literalmente en el fragmento entregado, el sistema no lo escribe.
3. **Si el dominio no tiene contenido cargado, lo dice explícitamente**, en vez de responder con una aproximación genérica que suena bien pero no está verificada.
4. **Cada respuesta se rastrea hasta su fuente** (`normas_registro`, con estado de vigencia y derogación), y el pipeline de carga está versionado en `scripts/ingesta/`, no oculto.
5. **La verificación es un proceso repetido, no una promesa.** Antes de dar por buena una sección nueva del corpus, se prueba con preguntas reales contra el motor de búsqueda. Cuando el propio pipeline tuvo un error real, quedó documentado en el historial de migraciones, no parchado en silencio.

Es, en el fondo, el mismo método científico aplicado a software: hipótesis, verificación contra la fuente primaria, corrección explícita del error propio — también la base metodológica de mi trabajo de grado sobre NSR-10/SGSST/NTC, próximo a sustentar. StructAI es la prueba de concepto aplicada de esa investigación.

## Evaluación empírica del RAG — medido, no solo diseñado

Medido con RAGAS (fidelidad, relevancia de respuesta, precisión y cobertura de contexto) sobre preguntas con `ground_truth` verificado de antemano contra el texto oficial — nunca inventado. El conjunto de evaluación creció en 5 rondas sucesivas a medida que se necesitaba más señal:

| Corrida | n preguntas | Fidelidad | Relevancia | Precisión de contexto | Cobertura de contexto |
|---|---:|---|---|---|---|
| Línea base (RRF sin re-ranking) | 12 | 0,906 ± 0,193 | 0,917 ± 0,055 | 0,743 ± 0,235 | 1,000 ± 0,000 |
| + re-ranking cross-encoder | 12 | 0,837 ± 0,243 | 0,851 ± 0,271 | **0,875 ± 0,138** | 0,917 ± 0,289 |
| + descomposición de consultas | 12 | 0,856 ± 0,266 | 0,920 ± 0,043 | 0,875 ± 0,151 | **1,000 ± 0,000** |
| Ampliación de cobertura | 52 | 0,826 ± 0,252 | 0,858 ± 0,252 | 0,784 ± 0,181 | 0,960 ± 0,198 |
| + categorías complejas (síntesis, adversarial, compuestas, coloquial) | 143 | 0,757 ± 0,255 | 0,848 ± 0,256 | 0,798 ± 0,218 | 0,915 ± 0,264 |
| **Post-HNSW/NOT MATERIALIZED (esta sesión)** | **278** | *en curso — se actualiza al terminar la corrida* | | | |

<details>
<summary>Hallazgos concretos por corrida — qué cambió, y por qué, no solo el número final</summary>

- **12 preguntas**: la cobertura del contexto ya era perfecta desde el inicio (1,000) — el corpus tenía la información; el problema real estaba en la precisión (0,743), el orden en que llegaban los fragmentos correctos. Un defecto real de diseño en la fusión RRF (el tamaño del pool interno de candidatos estaba atado a la cantidad de resultados solicitada, produciendo un ranking no monótono) se encontró y corrigió en el camino. Combinar el puntaje del re-ranker con el de recuperación híbrida, en vez de reemplazarlo, es lo que funcionó (precisión 0,743 → 0,875 sin degradar cobertura).
- **52 preguntas**: el hallazgo no fue ningún promedio, fue cuánto cambió la dispersión — con 12 preguntas la relevancia salía en 0,920 ± 0,043 (parecía casi perfecta); con 52, 0,858 ± 0,252 — la muestra chica daba una imagen artificialmente optimista. La precisión de contexto, en cambio, se mantuvo relativamente estable.
- **143 preguntas** (agregando síntesis cruzada entre títulos, adversariales, compuestas precio+norma, coloquiales): las preguntas de síntesis entre dos títulos salieron *mejor* que el resto (relevancia 0,937) — contrario a lo esperado de una pregunta "más difícil". Las compuestas precio+norma salieron débiles (relevancia 0,000, fidelidad 0,486) — señal real, candidata a revisar, no ruido de infraestructura.
- **278 preguntas** (esta sesión): primera corrida real de las 113 preguntas más nuevas del dataset (nunca antes verificadas contra `ask()` en producción), y primera medición de calidad después del trabajo de infraestructura (HNSW + GIN + `NOT MATERIALIZED`, ver arriba) — el objetivo es confirmar que la latencia bajó sin que la calidad de recuperación se moviera para peor.
- **Precios** (55 preguntas, rama aparte): fidelidad 0,792 ± 0,313, relevancia 0,686 ± 0,426, precisión de contexto 0,682 ± 0,369, cobertura 0,727 ± 0,449. Proveedor y proveedor nacional casi perfectos (0,85–1,0); insumos individuales el más débil. La categoría adversarial (materiales inventados) muestra relevancia 0,000 — verificado a mano que **no es una falla real**: el sistema sí rechaza inventar un precio, pero esa métrica de RAGAS penaliza un "no lo tengo" honesto. El hallazgo real sin corregir: jerga regional ("vereda" vs. "andén") no siempre encuentra el precio real cuando compite contra filas casi duplicadas.

</details>

## Los 7 motores

| Motor | Dominio |
|---|---|
| **APU** | Análisis de Precios Unitarios — la base de precios reales de arriba |
| **Estructural** (`motor-deformacion`) | Deformación de vigas (Euler-Bernoulli), pandeo de columnas (Euler/Johnson), incertidumbre Monte Carlo |
| **AquAI** | Acueducto y alcantarillado — RAS 2000 / Res. 0330-2017 (11 módulos), con datos hidrometeorológicos reales del IDEAM |
| **GeoPot** | Geotecnia y laboratorio: suelos, concreto, agregados, sísmica NSR-10 |
| **Vías** | Diseño vial INVIAS: geometría, pavimentos, mantenimiento, topografía, NTC de materiales |
| **Gerencia** | Earned Value Management (PMBOK) + aprendizaje automático predictivo sobre avance de obra |
| **InfraCortex** | BIM (IFC) → topología viga-columna → chequeo por cortante NSR-10 A/B/C, más inspección visual de estribos |

Cada motor expone su propio router FastAPI, su propia tabla en Supabase y su propio corpus — comparten backend y base de datos, pero ninguno depende de otro para funcionar.

> **InfraCortex está desactivado por defecto en producción** (`ENABLE_ESTRUCTURAL=false`): carga `torch` + `ifcopenshell` + `opencv` (~1-1,5 GB) y la instancia actual no tiene margen de RAM para sostenerlo junto al resto de la API. Código completo y probado (7 tests, 86% de cobertura) — activarlo es una variable de entorno, no una reescritura.

## Lo que todavía no es — honestidad antes que marketing

StructAI es un piloto en producción real, con usuarios reales, no una maqueta ni una cobertura nacional completa:

- **Precios con SKU real** (marca, especificación técnica) cubre el Atlántico. La capa nacional (78 proveedores mipyme) tiene ciudad/departamento real para 70 — los 8 restantes son casos genuinamente ambiguos (homónimos, uniones temporales sin registro regular) y se quedan como "Nacional" en vez de adivinar.
- **A, B y J** de la NSR-10 siguen con hueco real — ver la [tabla título por título](#auditoría-verbatim-de-la-nsr-10-título-por-título) arriba, con J como el caso explícitamente diferido.
- **Orinoquía, Pacífico** (más allá de las estaciones IDEAM ya integradas) **y Bogotá** son las regiones donde la expansión de cobertura está activa pero no cerrada.
- **No hay validación externa todavía.** Ningún ingeniero estructural certificado ajeno a este proyecto ha revisado formalmente la metodología de extracción — es exactamente el tipo de colaboración que busco, ver [más abajo](#colaboración-con-universidades-gremios-y-cámaras-de-comercio).

Roadmap completo, cada punto abierto o cerrado: [issues del repositorio](https://github.com/wilmerjoseperezorozco-dev/structai/issues) y su [milestone activo](https://github.com/wilmerjoseperezorozco-dev/structai/milestone/1).

## Hacia dónde va esto — lo aplicativo y lo que viene

StructAI empezó como una herramienta para Barranquilla y el Atlántico. La base técnica ya no tiene ese límite — funciona igual para cualquier región de Colombia, y el enfoque de trazabilidad normativa ya está exportado de verdad a dos países más (Perú y Ecuador), con el mismo rigor verbatim.

- **Evaluación de vulnerabilidad sísmica de vivienda ya construida.** Sobre NSR-10 A.10 y la línea metodológica AIS 2004 → Build Change → AIS 410-23, para vivienda informal/mampostería no reforzada construida sin supervisión técnica real — no solo construcción nueva. El terremoto de agosto de 2026 volvió esto urgente; cruzarlo con Venezuela confirmó que el vacío no es exclusivamente colombiano.
- **Datos ambientales y geológicos reales integrados al cálculo, no solo a la norma.** Ya no es un objetivo, es cobertura nacional real (ver la tabla de arriba) — el objetivo hacia adelante es que cada motor nuevo se apoye en esta misma disciplina de datos oficiales en vivo.
- **Cobertura normativa y de precios verdaderamente nacional**, con la misma exigencia de verificación que hoy se aplica al Atlántico.
- **Investigación aplicada, no solo producto.** El diseño de StructAI —extracción verificada, citación literal, honestidad ante la ausencia de datos— es en sí mismo un objeto de estudio para sistemas de IA confiables en dominios de alto riesgo. Es la pregunta de fondo de mi trabajo de grado, y una línea que me interesa seguir más allá de él.

## Colaboración con universidades, gremios y Cámaras de Comercio

Invitación concreta, no una frase de cierre. Si diriges o participas en un programa de ingeniería civil, representas a la AIS (cuya metodología ya cito con atribución), a una Cámara de Comercio (cuyo registro público RUES ya cruzo hoy), o a cualquier entidad con interés real en cómo se cita y verifica la normativa colombiana con IA, quiero hablar contigo. Ofrezco acceso educativo gratuito y busco activamente:

- Revisión externa de la metodología de extracción por un ingeniero estructural certificado.
- Datos técnicos, normativos o de precios reales que sumen a esta base, con atribución documentada.
- Colaboración institucional para llevar esto de un piloto en el Atlántico a una herramienta con alcance nacional real.

Detalle completo de cómo contactar: [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

## Arquitectura RAG — cómo está construido, sin rodeos

- **Embeddings**: 100% locales, sin costo por consulta (`sentence-transformers`, `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones).
- **Vectores**: `pgvector` nativo en Supabase/PostgreSQL con índice **HNSW** (no un servicio de vectores separado, no el `ivfflat` original — ver [Infraestructura del RAG](#infraestructura-del-rag--rendimiento-medido-no-solo-diseñado) arriba).
- **Síntesis de respuesta**: [Groq](https://groq.com) (`gpt-oss-120b`, 1-3s típico) como motor principal, [OpenAI](https://openai.com) (`gpt-4o-mini`) como respaldo automático si Groq se queda sin cuota diaria.
- **Trazabilidad**: cada respuesta incluye `norma_ref` real (documento + sección/artículo exacto), y advierte si la norma citada está derogada o modificada.

## Estructura del monorepo

```
construdata/
├── apps/
│   ├── web/        → Next.js 14 (App Router) + PWA          → Vercel (desplegado)
│   ├── native/      → React Native + Expo Router (Fase 0)    → sin publicar aún
│   └── api/         → FastAPI, los 7 motores + RAG           → Google Cloud Run (desplegado)
├── packages/
│   ├── motor-apu/, motor-deformacion/, motor-aquai/,
│   │   motor-geopot/, motor-vias/, motor-gerencia/  → cada uno con su pyproject.toml y sus tests
│   ├── shared-types/    → tipos TS + cliente API compartidos entre web y native
│   ├── construdata/     → schema SQL + RAG multi-norma + delegador de motores + clientes de datos abiertos (IDEAM)
│   ├── knowledge/       → _archivo/ con la fuente PDF descartada (ver nota de integridad arriba)
│   ├── ai-gateway/      → gateway multi-proveedor — experimental
│   ├── bim-intelligence/→ IFC + Qdrant — experimental, no conectado al producto
│   └── motor-estructural/ → InfraCortex: IFC + NSR-10 A/B/C, router `/estructural` conectado
├── scripts/ingesta/  → pipeline de carga del corpus, versionado por dominio (el documento fuente, no)
├── scripts/evaluacion/ → datasets y corridas RAGAS, versionadas
├── infra/supabase/   → schema y migraciones reales, reconstruidas byte a byte contra producción
├── docs/             → comparación pública, canal de colaboración institucional
└── .github/workflows/ → CI: lint + tsc, tests Python por motor (7), tests de integración del RAG
```

## Desarrollo local

```bash
# Web
cd apps/web && npm install && npm run dev

# API (6 motores activos + RAG; InfraCortex/YOLO opcionales, ver abajo)
cd apps/api && pip install -r requirements.txt && uvicorn main:app --reload

# Habilitar InfraCortex (motor-estructural) o YOLO localmente además de lo anterior:
#   pip install -r requirements-estructural.txt && export ENABLE_ESTRUCTURAL=true
#   pip install -r requirements-vision.txt      && export ENABLE_YOLO=true

# Un motor Python de forma aislada
cd packages/motor-<nombre> && pip install -e ".[dev]" && pytest tests/ -v

# App nativa (Fase 0, Expo)
cd apps/native && npm install && npm start
```

## Estado de deploy

| Componente | Estado |
|---|---|
| `apps/web` | ✅ Desplegado en Vercel (PWA), deploy automático en cada push a `master` |
| `apps/api` | ✅ Desplegado en Google Cloud Run (`us-east1`), deploy manual vía `gcloud run deploy` — CI/CD automático (Cloud Build trigger) todavía no armado. Login requerido (Supabase Auth) para `/ask`, `/apu/calculate` y `/detect` |
| `apps/native` | 🔄 Fase 0 de un roadmap más largo — shell nativo, sin sensores todavía |
| Supabase | ✅ En producción, RLS activo en todas las tablas, `pgvector`/HNSW para los 3 corpus RAG |

Verificable ahora mismo: [`GET /health?deep=true`](https://structai-api-235651108862.us-east1.run.app/health) y [`GET /data-status`](https://structai-api-235651108862.us-east1.run.app/data-status).

## Secrets de GitHub Actions (reales, verificados contra `ci.yml`)

| Secret | Uso |
|---|---|
| `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` | Backend, tests de integración |
| `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Build de `apps/web` |
| `NEXT_PUBLIC_API_URL` | Build de `apps/web` |
| `GROQ_API_KEY` | Síntesis de respuestas del RAG — motor principal |
| `OPENAI_API_KEY` | Respaldo automático si Groq se queda sin cuota diaria |

## StructAI frente a un asistente de IA genérico

Ver [`docs/comparacion.md`](./docs/comparacion.md) — comparación verificable, no marketing, contra la alternativa real que la mayoría de ingenieros ya prueba primero: preguntarle directamente a ChatGPT, Claude o Gemini sin ninguna base normativa o de precios conectada.

## Convenciones de contribución

Ver [`CONTRIBUTING.md`](./CONTRIBUTING.md) — formato de commits, cómo instalar un motor en modo desarrollo, y qué decisiones de arquitectura están deliberadamente sin resolver todavía.

## Licencia

Propiedad de Wilmer José Pérez Orozco — ver [LICENSE](./LICENSE). El repositorio es público con fines de demostración técnica, portafolio y colaboración académica; no es software de código abierto.

---

## 🌐 Overview · Resumen

<table>
<tr>
<td width="50%">

### 🇬🇧 English

*Full detail above is in Spanish, my working language for this project. This is a condensed mirror covering the same ground, not just an intro.*

**Why this exists.** On August 10, 2026, a magnitude-7.4 earthquake killed 289 people in Colombia (the government's final official count). It wasn't a geological surprise — the whole country sits on seismic-hazard zones, and much of its housing predates strict seismic codes, or was built afterward without on-site verification. I'm a civil engineer; StructAI exists because if an engineer can look up the exact regulation — not a generic AI approximation that never saw the Colombian code — at the moment of calculating, fewer errors get made. A structural miscalculation here isn't a technical detail. It's a life.

<details>
<summary><b>The region has a pattern, not just Colombia</b></summary>

Six weeks before the Chocó earthquake, Venezuela had its own: a magnitude-7.2/7.5 doublet on June 24, 2026, off La Guaira at 10 km depth. Cross-referencing the three most recent, best-documented Andean-Caribbean earthquakes (USGS data, official reports, World Bank estimates):

| Event | Date | Magnitude | Depth | Deaths | Economic losses |
|---|---|---|---|---|---|
| Ecuador — Pedernales | Apr-2016 | 7.8 | 20 km | 656 | US$3,000M+ |
| Colombia — Chocó | Aug-2026 | 7.4 | ~103–110 km | 289 | US$9,571M |
| Venezuela — La Guaira | Jun-2026 | 7.2 / 7.5 | 10 km | 6,301–6,438 | US$19,600M |

Venezuela had the *smallest* magnitude and still more than nine times Ecuador's death toll. What explains the gap isn't shaking strength — it's depth and how much densely built population sat above it. What no country maps systematically yet: how vulnerable, building by building, what's already standing is. Colombia (informal construction) and Venezuela (soft-story buildings) share the same gap under different names.

</details>

**What's live today, verified now.** Check it yourself: [`GET /data-status`](https://structai-api-235651108862.us-east1.run.app/data-status).

| Corpus | Real figure |
|---|---:|
| NSR-10 (all 11 titles, strict numeral-by-numeral audit, full sweep — [table above](#auditoría-verbatim-de-la-nsr-10-título-por-título)) | 8,454 chunks |
| NTC + occupational health & safety framework | 294 chunks |
| Domain engines (AquAI, GeoPot, Vías, Gerencia) | 4,060 chunks |
| Reference pricing (927/4,566 activities with real supply breakdown) | 4,566 activities · 10,281 supplies |
| Verified suppliers (24 local + 78 national, 90% with real city/department) | 114,616 comparable prices |
| Official live data: seismic hazard, streamflow anomaly, soils, housing vulnerability, emergency history | 1,121 municipalities (SGC) · 949 stations (IDEAM) · 169,088 soil units (IGAC) · 1,099 municipalities (Sisbén) · 41,893 events (UNGRD) |
| Peru (E.030, current 2026 edition) & Ecuador (NEC-SE-DS), verbatim, live in chat | 204 chunks + 1,884 districts (Peru) · 395 chunks + 512 localities (Ecuador) |

**NSR-10 audit, honestly**: 8 of 10 re-audited titles had a real gap (all but I and E). Of those, **H, K, G, D and C are already closed in full verbatim** the same day the gap was found — only **A, B and J** remain open, J being the largest and explicitly deferred (159 real numerals, only 49 chunks, mostly paraphrased summary instead of verbatim — a candidate for full re-ingestion).

<details>
<summary><b>RAG infrastructure — measured performance, not just design</b></summary>

Four real bugs found and fixed, each verified with `EXPLAIN ANALYZE` or an independent second audit:

| # | Real problem | How it was found | Fix |
|---|---|---|---|
| 1 | Embeddings silently truncate fragments over 128 tokens | Real-tokenizer audit: 493/4,129 fragments (11.9%) over limit | Re-split respecting the real limit; second audit confirmed 0% over limit |
| 2 | `ivfflat` pgvector index had ~10% real recall | A chunk with 0.60 real cosine similarity to its own query missing from top-50 | Replaced with **HNSW**; recall@10 verified empirically at 99.6–100% |
| 3 | The only full-text GIN index used a different expression than the real search function — never actually used | Latency profiling of `search_knowledge()`: forced full `Parallel Seq Scan` (~1.4s) | New GIN, aligned exactly to the real expression |
| 4 | The CTE shared between the semantic and lexical search branches got materialized (referenced twice), nullifying the new indexes entirely | `EXPLAIN ANALYZE` on the real function body (a function call is a black box to the planner — had to reconstruct the exact query to see it) | Explicit `NOT MATERIALIZED` |

**Measured, same real query, end to end**: 3,803 ms (no index) → 2,387 ms (HNSW+GIN) → **626 ms** (`NOT MATERIALIZED`) — **~83% total reduction**, correctness verified at every step, not just speed.

</details>

**The methodology.** Not a chatbot with a PDF pasted into the prompt. A retrieval-augmented generation (RAG) system on one non-negotiable rule: **an invented citation is worse than none, because it looks verifiable and isn't.** Hybrid search (vector + full-text, RRF-fused) · the model cites only what's in retrieved context · explicit "not loaded" instead of a plausible guess · every answer traces to its source, with repeal/amendment status · verification is a repeated process against real questions, not a one-time promise. Same scientific method applied to software — also the backbone of my undergraduate thesis on NSR-10/SGSST/NTC, soon to be defended; StructAI is its applied proof of concept.

**Empirical RAG evaluation — measured, not just designed.**

| Run | n questions | Faithfulness | Relevancy | Context precision | Context recall |
|---|---:|---|---|---|---|
| Baseline (RRF, no re-ranking) | 12 | 0.906 ± 0.193 | 0.917 ± 0.055 | 0.743 ± 0.235 | 1.000 ± 0.000 |
| + cross-encoder re-ranking | 12 | 0.837 ± 0.243 | 0.851 ± 0.271 | **0.875 ± 0.138** | 0.917 ± 0.289 |
| + query decomposition | 12 | 0.856 ± 0.266 | 0.920 ± 0.043 | 0.875 ± 0.151 | **1.000 ± 0.000** |
| Coverage expansion | 52 | 0.826 ± 0.252 | 0.858 ± 0.252 | 0.784 ± 0.181 | 0.960 ± 0.198 |
| + complex categories (cross-title, adversarial, compound, colloquial) | 143 | 0.757 ± 0.255 | 0.848 ± 0.256 | 0.798 ± 0.218 | 0.915 ± 0.264 |
| **Post-HNSW/NOT MATERIALIZED (this session)** | **278** | *in progress — updated once the run finishes* | | | |

Key findings: the 12-question baseline showed context recall was already perfect (1.000) — the real bottleneck was precision (0.743, ranking order), and a real RRF design defect (internal candidate-pool size tied to the caller's requested count) was found and fixed. At 52 questions, answer relevancy's apparent near-perfection (0.920±0.043 at n=12) turned out to be small-sample optimism (0.858±0.252 at n=52) — context precision held up more reliably. At 143, cross-title synthesis questions scored *better* than the rest (0.937 relevancy), while compound price+regulation questions came out weak (0.000/0.486) — a real, unfixed signal. A separate 55-question pricing evaluation shows supplier branches near-perfect (0.85–1.0) and individual-supply items weakest; the adversarial-material category's 0.000 relevancy is a known RAGAS metric limitation against honest refusals, not a real failure.

**The 7 engines**: APU (unit pricing) · Structural/`motor-deformacion` (beam deflection, column buckling, Monte Carlo) · AquAI (water/sewerage, RAS 2000, real IDEAM data) · GeoPot (geotechnics) · Vías (INVIAS road design) · Gerencia (EVM + predictive ML) · InfraCortex (BIM/IFC shear check, disabled by default for RAM — code complete, 7 tests, 86% coverage).

**What this isn't yet.** A real production pilot, not a mockup or full national coverage. Pricing with real SKUs covers Atlántico only; NSR-10 Titles A, B and J still have real gaps (J deferred, largest, ~159 numerals mostly in paraphrase not verbatim); Orinoquía, the Pacific, and Bogotá are active but not closed; no external validation yet by a certified structural engineer outside this project — exactly the collaboration I'm looking for.

**Where this is going.** Seismic vulnerability assessment of already-built housing (NSR-10 A.10 + AIS 2004 → Build Change → AIS 410-23) · real environmental/geological data already at national scale, more engines to follow the same discipline · truly national regulatory and pricing coverage · applied research on trustworthy AI in high-stakes domains — the question behind my thesis.

**University, guild, and Chamber of Commerce collaboration.** A concrete invitation. If you lead a civil engineering program, represent AIS or a Chamber of Commerce, or have real interest in how Colombian regulation is cited and verified with AI, I want to talk — free educational access, and I'm looking for external methodology review, real data contributions with documented attribution, and institutional partners to go from an Atlántico pilot to real national reach. Detail: [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

**RAG architecture.** 100% local embeddings, no per-query cost (`sentence-transformers`, 384-dim) · native `pgvector` + **HNSW** on Supabase/PostgreSQL (not `ivfflat`, see infrastructure section above) · [Groq](https://groq.com) primary synthesis with [OpenAI](https://openai.com) automatic fallback · every answer traceable with repeal/amendment status.

**Quick start:**
```bash
cd apps/web  && npm install && npm run dev
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload
```

**Deploy status:** `apps/web` on Vercel (auto-deploy on push) · `apps/api` on Google Cloud Run (manual deploy, login required via Supabase Auth) · `apps/native` Phase 0 · Supabase in production, RLS everywhere, `pgvector`/HNSW. Verify: [`/health?deep=true`](https://structai-api-235651108862.us-east1.run.app/health) · [`/data-status`](https://structai-api-235651108862.us-east1.run.app/data-status).

**License.** Owned by Wilmer José Pérez Orozco — see [LICENSE](./LICENSE). Public for technical demonstration, portfolio, and academic collaboration; not open-source software.

</td>
<td width="50%">

### 🇨🇴 Español

**Plataforma de IA para ingeniería civil en Colombia**, construida después de que el terremoto de agosto de 2026 dejara clara una cosa: el ingeniero necesita verificar la norma exacta detrás de un cálculo, no una aproximación genérica. Cada respuesta cita el reglamento real —capítulo, artículo, fuente— y el sistema dice explícitamente cuando no tiene la respuesta.

7 motores de dominio (6 activos en producción, 1 desactivado por defecto por RAM), trazabilidad normativa completa sobre NSR-10, RAS 2000/Res. 0330, INVIAS, NTC y SGSST. Marca pública: **StructAI**.

**Cobertura en vivo**: 8.454 chunks de NSR-10 en los 11 títulos — todos auditados numeral por numeral; H, K, G, D y C ya cerrados en verbatim completo el mismo día que se encontró el hueco; solo A, B y J siguen pendientes (J el más grande, dejado explícito para otra sesión). 294 de NTC/SGSST, 4.060 de motores de dominio, 4.566 actividades / 10.281 insumos / 102 proveedores verificados. Compruébalo tú mismo: [`/data-status`](https://structai-api-235651108862.us-east1.run.app/data-status).

**Infraestructura del RAG**: 4 bugs reales de rendimiento encontrados y corregidos esta sesión (truncamiento silencioso de embeddings, índice `ivfflat` con ~10% de recall real, índice de texto desalineado, CTE materializada anulando los índices) — `search_knowledge()` bajó de 3.803 ms a 626 ms (~83%), con correctez verificada en cada paso. Detalle completo arriba, en "Infraestructura del RAG".

**Evaluación empírica del RAG**: medida con RAGAS, no solo diseñada — precisión de contexto 0,743 → 0,875 tras re-ranking y descomposición de consultas; corrida más reciente en curso sobre 278 preguntas, tras el trabajo de infraestructura de esta sesión. Detalle completo arriba, en "Evaluación empírica del RAG".

**Inicio rápido:**
```bash
cd apps/web  && npm install && npm run dev
cd apps/api  && pip install -r requirements.txt && uvicorn main:app --reload
```

**Busco:** colaboración universitaria e institucional — acceso educativo gratuito, revisión externa de la metodología, y alianzas de datos. Ver [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

</td>
</tr>
</table>
