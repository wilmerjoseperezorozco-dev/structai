# StructAI — IA con trazabilidad normativa para ingeniería civil en Colombia

[![Web](https://img.shields.io/badge/web-structai.online-0ea5e9)](https://www.structai.online)
[![Versión](https://img.shields.io/github/v/release/wilmerjoseperezorozco-dev/structai?label=versi%C3%B3n&color=0ea5e9)](https://github.com/wilmerjoseperezorozco-dev/structai/releases)
[![CI](https://github.com/wilmerjoseperezorozco-dev/structai/actions/workflows/ci.yml/badge.svg)](https://github.com/wilmerjoseperezorozco-dev/structai/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21851529.svg)](https://doi.org/10.5281/zenodo.21851529)
[![Estado en vivo](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fstructai-api-235651108862.us-east1.run.app%2Fdata-status&query=%24.corpus_normativo.nsr10_chunks.chunks&label=chunks%20NSR-10%20en%20vivo&color=16a34a)](https://structai-api-235651108862.us-east1.run.app/data-status)

**StructAI** responde preguntas de ingeniería civil citando la norma colombiana exacta (NSR-10, NTC, RAS 2000, INVIAS) con capítulo y numeral, calcula con motores determinísticos y consulta datos oficiales abiertos del territorio. Si la información no está cargada, lo dice en lugar de inventarla. Piloto en producción en [structai.online](https://www.structai.online); plan gratuito con la NSR-10 completa. *Construdata* es el nombre interno del repositorio.

## Qué resuelve

| Problema del ingeniero o del constructor | Qué hace StructAI | Dónde verlo |
|---|---|---|
| Encontrar el requisito exacto de la norma mientras se calcula | Búsqueda sobre la NSR-10 (títulos A–K), NTC y SG-SST con cita verificable; abstención cuando no hay base | [`/consultar`](https://www.structai.online) |
| Presupuestar con precios reales y desglosados | 4.566 actividades y 10.281 insumos, más 114.616 cotizaciones de 78 proveedores nacionales; revisión de precios atípicos | [`docs/DETALLE_TECNICO.md`](docs/DETALLE_TECNICO.md) |
| Calcular sin salir de la plataforma | Motores activos: estructural, acueducto y alcantarillado, geotecnia, vías, gerencia (EVM), APU y vulnerabilidad de vivienda de mampostería (AIS). El BIM (InfraCortex) está probado pero desactivado por defecto en producción por memoria | `packages/motor-*` |
| Conocer el sitio de la obra | Amenaza sísmica SGC por municipio, microzonificación de Bogotá, Cali y Pereira, caudales IDEAM, suelos IGAC, emergencias UNGRD | [`/data-status`](https://structai-api-235651108862.us-east1.run.app/data-status) |
| Saber si una norma sigue vigente | Registro de normas con cadena de modificaciones y estado de verificación (cadena completa en 6 de 64; el resto, parcial o sin revisar) | `normas_registro` |
| Caracterizar un sitio antes de diseñar | **Informe de sitio** por municipio: amenaza sísmica, suelos, caudales, vulnerabilidad de vivienda, emergencias, susceptibilidad a movimientos en masa y contexto de ENSO, más los títulos de la NSR-10 a consultar; se entrega con datos verificados, sin texto del modelo de lenguaje | [`docs/investigacion/oceanos_azules_y_plugins.md`](docs/investigacion/oceanos_azules_y_plugins.md) |
| Replicar el método fuera de Colombia | E.030 (Perú, edición RM 183-2026) y NEC-SE-DS (Ecuador), verbatim y con aviso profesional propio | [`docs/DETALLE_TECNICO.md`](docs/DETALLE_TECNICO.md) |

## Novedades (9-nov-2026)

- **Motor de redes hidráulicas** (red mallada, bombas, válvulas, periodo extendido y golpe de ariete) con dos revisiones adversarias corregidas y validación contra EPANET. **Aún no está desplegado**: figura como «no desplegado» en la matriz.
- **Registro de motores medidos a producción** y **matriz de madurez** generados desde el código, con verificación en CI: [`REGISTRO_MOTORES.md`](docs/REGISTRO_MOTORES.md) · [`MATRIZ_MADUREZ.md`](docs/MATRIZ_MADUREZ.md).
- **Inventario de licencias** de las dependencias directas: [`LICENCIAS_DEPENDENCIAS.md`](docs/LICENCIAS_DEPENDENCIAS.md).
- **Aviso semanal de vigencia normativa** (solo avisa; no ingesta): [`vigencia_normas.py`](scripts/mantenimiento/vigencia_normas.py).
- Despliegue con verificación previa al tráfico: [`infra/gcp/`](infra/gcp/README.md).

## Madurez por subsistema

No hay una nota única de «madurez»: cada columna sale de una fuente distinta. El TRL es **autoevaluado, sin revisión externa**; «?» significa sin atestar, no que cumpla. Matriz completa, evidencias y límites: [`docs/MATRIZ_MADUREZ.md`](docs/MATRIZ_MADUREZ.md).

| Subsistema | TRL (autoevaluado) | Calidad de software | Operación |
|---|---|---|---|
| Corpus normativo y consulta con citas | 6 | CI de paquetes + job de integración; métricas RAGAS publicadas | En producción |
| Motor de redes hidráulicas | 4 | 105 pruebas, CI, contrato, 422 y límite de tasa | No desplegado |
| Motor de geotecnia | 4 | 88 pruebas, CI, contrato, 422 y límite de tasa | No desplegado |
| Demás motores con contrato (licuación, concreto, análisis, orquestador) | ? | Pruebas y CI; contrato, 422 y límite de tasa | ? |
| Motor estructural / BIM por visión | ? | 18 pruebas, CI | Desactivado por defecto en producción |

Lo que **no** se publica: un badge único de madurez, un porcentaje de cobertura (hoy no se mide) ni TRL 7 o superior (exige uso por terceros medido y revisión técnica independiente). El criterio de «motor medido a producción» tiene cuatro condiciones y hoy **ningún motor las cumple todas**: [`REGLAS_MOTORES_DE_CALCULO.md`](docs/REGLAS_MOTORES_DE_CALCULO.md).

## Tecnologías y librerías

Versiones tomadas de `apps/api/requirements.txt` y `apps/web/package.json`; licencias de las dependencias directas en [`LICENCIAS_DEPENDENCIAS.md`](docs/LICENCIAS_DEPENDENCIAS.md).

| Capa | Qué usa | Para qué |
|---|---|---|
| API | FastAPI 0.141 · Starlette · Uvicorn · Pydantic 2.9 · slowapi · httpx | Endpoints, validación estricta con fallo explícito (422), límites de tasa |
| Autenticación | Supabase Auth · PyJWT · cryptography | Verificación del JWT de Supabase en los endpoints protegidos |
| Recuperación y síntesis | sentence-transformers 5.6 (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dim, local) · Groq (principal) · OpenAI `gpt-4o-mini` (respaldo) · re-ranking | Búsqueda con cita verificable y respuesta con abstención |
| Cálculo | numpy 1.26 · scipy 1.13 · motores propios `packages/motor-*` | Resultados determinísticos con el contrato `ResultadoMotor` |
| Reportes | reportlab 4.2 · openpyxl 3.1 | Memorias de cálculo en PDF y hojas de cálculo |
| Datos | Supabase (Postgres) · datos abiertos IDEAM, SGC, IGAC, UNGRD | Corpus, precios y contexto territorial |
| Web | Next.js 15 · React 18 · TypeScript 5 · Tailwind 3 · next-pwa · react-markdown | PWA para ingenieros y maestros de obra |
| Observabilidad | sentry-sdk · `@sentry/nextjs` · `/health` y `/data-status` públicos | Errores y estado en vivo |
| Infraestructura | Google Cloud Run · Cloud Build · GitHub Actions | Despliegue manual verificado y CI |
| Opcional, desactivado por defecto | ultralytics (**AGPL-3.0**) · opencv-python · ifcopenshell (LGPL) | BIM y visión (InfraCortex); su licencia exige revisión antes de ofrecerlo como servicio |

## Visibilidad e impacto

| A quién sirve | Qué recibe | Cómo se comprueba |
|---|---|---|
| Ingenieros y maestros de obra | Requisito exacto de la norma con cita, y precios desglosados | Pruebe la [web](https://www.structai.online); cada respuesta cita capítulo y numeral |
| Municipios y gestores del riesgo | Informe de sitio con amenaza, suelos, caudales y vulnerabilidad, solo con datos verificados | [`/data-status`](https://structai-api-235651108862.us-east1.run.app/data-status) |
| Academia | Investigación preregistrada, con resultados nulos incluidos y tags reproducibles | Tabla del programa de investigación, [DOI](https://doi.org/10.5281/zenodo.21851529) y [`CITATION.cff`](CITATION.cff) |
| Otros países | Método replicable (E.030 Perú, NEC-SE-DS Ecuador) con aviso profesional propio | [`PROTOCOLO_REPLICACION_PAISES_VECINOS_2026-11.md`](docs/PROTOCOLO_REPLICACION_PAISES_VECINOS_2026-11.md) |

No se publican cifras de usuarios ni de uso porque hoy no se miden en el repositorio. Para alianzas, revisión técnica independiente o acceso educativo: [`docs/contacto-institucional.md`](docs/contacto-institucional.md).

## Estado verificado (7-nov-2026, contra producción)

| Corpus | Cifra | | Base de precios | Cifra |
|---|---:|---|---|---:|
| NSR-10, chunks verbatim | 10.443 | | Actividades de referencia | 4.566 |
| NTC + SG-SST | 294 | | Insumos desglosados | 10.281 |
| Corpus por motor (RAS, GeoPot, Vías, Gerencia) | 4.060 | | Cotizaciones de proveedores nacionales | 114.616 |

Se comprueban ahora mismo en [`/data-status`](https://structai-api-235651108862.us-east1.run.app/data-status). El despliegue a producción es manual, así que lo último de `master` puede ir por delante de lo que sirve la API; `/health` lista los módulos activos.

## Qué se mide, y con qué límites

| Indicador | Resultado | Lectura honesta |
|---|---|---|
| Fidelidad / relevancia (RAGAS, n = 278) | 0,750 / 0,773 | Corrida con 28 % de fallos del juez por timeout; no permite afirmar mejoras ni caídas finas |
| Citas con soporte en el contexto | 88,2 % (239 de 271) | Verificación léxica, sin LLM |
| Proxy de alucinación numérica | 15,4 % (IC95 % 11,5–20,5) | Es una cota de cifras sin respaldo en el contexto, no una tasa de error |
| Recall@10 de recuperación | 0,69 (IC amplio) | Cobertura medida por solapamiento léxico validada contra RAGAS (ρ = 0,59) |
| Latencia | mediana 3,8 s; p95 81 s (n = 53) | La cola larga existe y está documentada |

Métodos, intervalos y casos por categoría: [`PROTOCOLO_METRICAS_SIN_LLM.md`](scripts/evaluacion/PROTOCOLO_METRICAS_SIN_LLM.md). Se reportan también las métricas que salieron mal.

## Programa de investigación

Cada análisis se **preregistra antes de ejecutarse**, usa corrección por comparaciones múltiples y valida por departamento. Los estados cerrados llevan un tag `research/…` reproducible. Todo es una señal estadística: no es una alerta oficial ni sustituye el criterio profesional.

| Línea | Resultado principal | Tag |
|---|---|---|
| Susceptibilidad a movimientos en masa | AUC 0,775 con pesos de evidencia; 0,830 al sumar cobertura del suelo y gradient boosting (mejora significativa). Riesgo de fuga por usar la cobertura de 2021; en el Caribe el modelo completo no supera la pendiente sola | `research/protocolo-22`, `-24`, `h6` |
| Frecuencia de crecientes (IDEAM) | El ajuste estacionario por estación **no está calibrado** (excedencia observada del Q10: 0,135) y el 44 % de estaciones muestra tendencia; no se usa como base de diseño | `research/protocolo-21` |
| Lluvia y ENSO | Mapa de sensibilidad de la lluvia a El Niño y La Niña 1981–2024 | `research/protocolo-15` |
| Relieve y amenaza SGC | Contraste nacional con el mapa de amenaza por movimientos en masa | `research/protocolo-16` |
| Anomalías de caudal | La regla de producción marca 15,5 % de los meses normales, no el 10 % previsto. Añadir la persistencia del mes anterior detecta mejor los saltos (AUC 0,854 → 0,901; se sostiene con bootstrap por departamento); el z estacional por sí solo no supera la regla actual | `research/anomalias-caudal` |
| Coherencia espacio-temporal de anomalías | Las estaciones no son independientes (correlación mediana 0,46 a menos de 50 km). La Niña multiplica por 2-2,7 la fracción de estaciones en anomalía alta en las regiones Andina, Pacífica y Caribe; en la Amazonía el signo es el opuesto | `research/coherencia-anomalias` |
| Respuesta de los máximos anuales a ENSO | Hay efecto dentro de la muestra, pero ni el modelo por estación (41 %) ni el agrupado por región (52 %) superan en predicción a la GEV estacionaria; solo en Andina y Caribe el agrupado gana 60-66 % (exploratorio) | `research/h4-prima` |
| Precios atípicos y recomendador de insumos | Umbral conforme |z| > 2,82 con 5 % de marca; **no alcanza** el 0,90 de sensibilidad preregistrado ante un error ×10 (0,64) | `research/precios-p1-p3` |
| Fórmulas candidatas con logaritmos | Estado preregistrado antes de ejecutar H1–H6 | `research/protocolo-23` |
| Hipótesis H1-H5 (logaritmos, ENSO, umbrales) | Con Holm: confirmadas H3 (los logaritmos mejoran la susceptibilidad, +0,015 de AUC) y H4a (efecto de ENSO dentro de la muestra); **no** H4b, H2 ni H1 (ENSO y terreno no mejoran la predicción) | `research/h1-h5` |
| Umbrales de lluvia para movimientos en masa | La lluvia acumulada de 5 días discrimina (AUC 0,775) pero la curva intensidad-duración no mejora a un umbral simple y dispara casi siempre | `research/protocolo-19` (en cierre) |
| Relación no lineal con rezago (Pacífico y Atlántico → clima del Caribe) | Un modelo lineal estacional da una habilidad modesta que no es robusta tras corregir por comparaciones múltiples; **ningún modelo no lineal la mejora** | `research/rezagos-no-lineales` |
| Valor informativo y costo de los datos | Una conclusión de efecto promedio se conserva con el 5 % de las estaciones y un modelo de susceptibilidad con el 25 % de las filas; las líneas base simples bastan | `research/valor-informativo-p0-p1` |
| Comparación con modelos no medidos | El método simple que respeta la forma del problema alcanza lo que alcanzan los complejos (logística con splines no inferior al boosting) | `research/comparativo-modelos` |

Bibliografía verificada y registro de riesgos de la investigación: [`docs/investigacion/`](docs/investigacion/). Los resultados nulos (por ejemplo, relieve frente a inundaciones UNGRD en el Caribe, n = 195) se publican igual que los positivos.

## Lo que todavía no es

- **Piloto, no cobertura nacional completa.** Los Títulos A y B de la NSR-10 tienen cierre verbatim parcial (A 45,6 %, B 41,9 % de los numerales auditados); el detalle está en [`docs/fuentes-normativas.md`](docs/fuentes-normativas.md).
- **No sustituye al ingeniero.** Cada respuesta incluye un aviso de responsabilidad profesional y de uso de IA; el puntaje de los motores sale siempre de código determinístico, nunca del modelo de lenguaje.
- **Validación externa acotada.** El trabajo de grado que lo sustenta fue aprobado con Meritorio (4,7/5,0); falta la revisión técnica independiente de la extracción normativa por un ingeniero estructural externo.
- **Precios con fecha de carga, no de mercado.** Las referencias del catálogo nacional no son precios vigentes; el chat lo indica.

## Versiones y trazabilidad

`commit` → `issue` → `milestone` por fase → `tag` y `release` por versión estable. Versionado semántico, `master` siempre estable.

- [Releases](https://github.com/wilmerjoseperezorozco-dev/structai/releases) · [`CHANGELOG.md`](CHANGELOG.md) · [política de versiones](docs/VERSIONES.md)
- [Milestones](https://github.com/wilmerjoseperezorozco-dev/structai/milestones) agrupan los issues de cada fase.

## Desarrollo local

```bash
cd apps/web && npm install && npm run dev                              # web
cd apps/api && pip install -r requirements.txt && uvicorn main:app --reload   # API
cd packages/motor-<nombre> && pip install -e ".[dev]" && pytest tests/ -v      # un motor
```

Arquitectura, estructura del monorepo, despliegue y secrets: [`docs/DETALLE_TECNICO.md`](docs/DETALLE_TECNICO.md). Convenciones: [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Colaboración, cita y licencia

Seguridad: [`SECURITY.md`](SECURITY.md). Se buscan alianzas con universidades, gremios y cámaras de comercio, sobre todo para la revisión técnica independiente: [`docs/contacto-institucional.md`](docs/contacto-institucional.md). Acceso educativo gratuito para programas de ingeniería civil. Para citar, usa el DOI de arriba o [`CITATION.cff`](CITATION.cff).

Propiedad de Wilmer José Pérez Orozco, ver [`LICENSE`](LICENSE). Repositorio público con fines de demostración técnica, portafolio y colaboración académica; no es software de código abierto.
