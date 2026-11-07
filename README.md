# StructAI — IA con trazabilidad normativa para ingeniería civil en Colombia

[![Web](https://img.shields.io/badge/web-structai.online-0ea5e9)](https://www.structai.online)
[![Versión](https://img.shields.io/github/v/release/wilmerjoseperezorozco-dev/structai?label=versi%C3%B3n&color=0ea5e9)](https://github.com/wilmerjoseperezorozco-dev/structai/releases)
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
| Replicar el método fuera de Colombia | E.030 (Perú, edición RM 183-2026) y NEC-SE-DS (Ecuador), verbatim y con aviso profesional propio | [`docs/DETALLE_TECNICO.md`](docs/DETALLE_TECNICO.md) |

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
| Anomalías de caudal | La regla de producción marca 15,5 % de los meses normales, no el 10 % previsto; un z robusto con persistencia detecta mejor saltos (AUC 0,854 → 0,901) pero no crecientes sostenidas | `research/anomalias-caudal` |
| Precios atípicos y recomendador de insumos | Umbral conforme |z| > 2,82 con 5 % de marca; **no alcanza** el 0,90 de sensibilidad preregistrado ante un error ×10 (0,64) | `research/precios-p1-p3` |
| Fórmulas candidatas con logaritmos | Estado preregistrado antes de ejecutar H1–H6 | `research/protocolo-23` |

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

Se buscan alianzas con universidades, gremios y cámaras de comercio, sobre todo para la revisión técnica independiente: [`docs/contacto-institucional.md`](docs/contacto-institucional.md). Acceso educativo gratuito para programas de ingeniería civil. Para citar, usa el DOI de arriba o [`CITATION.cff`](CITATION.cff).

Propiedad de Wilmer José Pérez Orozco, ver [`LICENSE`](LICENSE). Repositorio público con fines de demostración técnica, portafolio y colaboración académica; no es software de código abierto.
