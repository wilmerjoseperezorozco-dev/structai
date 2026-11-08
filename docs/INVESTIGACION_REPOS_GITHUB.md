# Repositorios de GitHub candidatos para StructAI (2026-11-08)

**Alcance y límite.** Esta es una revisión de **metadatos** (licencia, estrellas, último commit, descripción) consultados en vivo con la API de GitHub el 2026-11-08. **No instalé ni probé ninguno.** La columna «Utilidad para StructAI» es una evaluación propia, no una medición. Las estrellas indican popularidad, no calidad ni adecuación. Donde la API devolvió licencia «NOASSERTION/Other» (licencia mixta o no reconocida) lo marco y hay que leer el archivo de licencia antes de usarlo.

## 1. Analítica del producto (la pregunta sobre Matomo)
Hoy `apps/web` solo usa `@vercel/analytics` (vistas de página; en el código no hay eventos propios).

| Repo | Licencia | ★ | Último push | Lenguaje |
|---|---|---:|---|---|
| [matomo-org/matomo](https://github.com/matomo-org/matomo) | GPL-3.0 | 22.013 | 2026-11-08 | PHP |
| [umami-software/umami](https://github.com/umami-software/umami) | MIT | 39.989 | 2026-11-07 | TypeScript |
| [plausible/analytics](https://github.com/plausible/analytics) | AGPL-3.0 | 29.795 | 2026-11-08 | Elixir |
| [PostHog/posthog](https://github.com/PostHog/posthog) | mixta (NOASSERTION) | 40.698 | 2026-11-08 | Python |

**Evaluación (propia).** Matomo es el más completo (embudos, mapas de calor, segmentos), pero requiere un servidor con PHP y MariaDB/MySQL: StructAI hoy corre en Cloud Run + Supabase + Vercel, y Matomo no encaja de forma natural en ese stack; habría que añadir y mantener otra pieza de infraestructura (o contratar su versión alojada, cuyo precio no verifiqué). Umami (MIT, TypeScript/Next.js, base PostgreSQL) encaja mejor con el stack. Cualquiera sirve si se respeta lo siguiente, que importa más que la herramienta:
- **No enviar el texto de las preguntas al sistema de analítica.** Una pregunta de un ingeniero puede contener datos de un proyecto o de un cliente. Registrar solo eventos sin contenido: «consulta enviada», «norma citada», «sin resultado», «descarga de informe», «error».
- **Habeas data (Ley 1581 de 2012).** Anonimizar IP, sin cookies de seguimiento entre sitios y aviso en la política de privacidad. No verifiqué los requisitos legales exactos; requiere revisión.
- **Lo que sí vale la pena medir:** consultas sin resultado o con baja confianza de recuperación (detectan huecos del corpus), consultas por tipo de motor (precios, norma, hidrosanitario), tasa de uso del aviso de responsabilidad profesional y errores. Esto último se guarda mejor en la base propia (Supabase) que en una herramienta de analítica.

**No usé Matomo en esta sesión:** no existe una instancia ni datos que analizar, y montarla requiere decidir dónde alojarla y crear una cuenta o un servidor, algo que te corresponde decidir a ti.

## 2. Extracción de PDF de normas (el cuello de botella de la ingesta verbatim)
La ingesta de la NSR-10 documentó 9 errores de extracción de PDF (`project_structai_nsr10_titulo_c_verbatim`), y el Título A sigue en ~63 %.

| Repo | Licencia | ★ | Último push |
|---|---|---:|---|
| [docling-project/docling](https://github.com/docling-project/docling) | MIT | 70.286 | 2026-11-08 |
| [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | mixta | 83.307 | 2026-11-08 |
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | MIT | 194.412 | 2026-11-07 |

**Utilidad:** probar Docling (tablas y fórmulas) sobre las páginas A.2 del espectro, donde la extracción actual falla más, y comparar con la transcripción verificada. Es la prueba de mayor retorno y más barata de esta lista. Criterio de éxito a fijar antes: porcentaje de numerales y celdas de tabla reproducidos exactamente.

## 3. Cálculo estructural independiente (para verificar los motores)
| Repo | Licencia | ★ | Último push |
|---|---|---:|---|
| [JWock82/Pynite](https://github.com/JWock82/Pynite) | MIT | 780 | 2026-10-31 |
| [anastruct/anaStruct](https://github.com/anastruct/anaStruct) | LGPL-3.0 | 471 | 2026-11-06 |
| [robbievanleeuwen/section-properties](https://github.com/robbievanleeuwen/section-properties) | MIT | 569 | 2026-04-16 |
| [zhuminjie/OpenSeesPy](https://github.com/zhuminjie/OpenSeesPy) | mixta | 288 | 2026-10-28 |
| [IfcOpenShell/IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) | LGPL-3.0 | 2.943 | 2026-11-08 |

**Utilidad:** como **referencia independiente** para las pruebas de `motor-estructural` (comparar resultados de un pórtico o una sección contra Pynite/section-properties), no como reemplazo. IfcOpenShell abriría la lectura de modelos BIM (IFC); es una línea de producto nueva, no un arreglo.

## 4. Amenaza sísmica
| Repo | Licencia | ★ | Último push |
|---|---|---:|---|
| [gem/oq-engine](https://github.com/gem/oq-engine) | **AGPL-3.0** | 470 | 2026-11-08 |

**Utilidad:** referencia de cálculo probabilista de amenaza para contrastar el Aa del A-4 con el modelo del SGC. **Aviso de licencia:** AGPL obliga a publicar el código de un servicio de red que lo incorpore; usarlo como herramienta externa, offline, para investigación, no tiene ese efecto, pero no debe integrarse al backend sin una decisión consciente.

## 5. Hidrología y terreno (más allá de PySheds)
La investigación usa PySheds (GPL-3.0, 915 ★, push 2026-10-26).

| Repo | Licencia | ★ | Último push |
|---|---|---:|---|
| [Deltares/pyflwdir](https://github.com/Deltares/pyflwdir) | MIT | 120 | 2026-11-06 |
| [Deltares/hydromt](https://github.com/Deltares/hydromt) | MIT | 124 | 2026-11-05 |
| [jblindsay/whitebox-tools](https://github.com/jblindsay/whitebox-tools) | MIT | 1.221 | 2026-05-26 |
| [opengeos/leafmap](https://github.com/opengeos/leafmap) | MIT | 3.797 | 2026-11-06 |

**Utilidad:** repetir la delineación de cuencas de la regionalización de caudales con `pyflwdir` o WhiteboxTools para ver cuánto del error (factor ~1,75) viene de la delineación con PySheds a 90 m. Es una verificación de sensibilidad barata y de licencia permisiva.

## 6. Observabilidad y evaluación de LLM
| Repo | Licencia | ★ | Último push |
|---|---|---:|---|
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | mixta | 37.148 | 2026-11-08 |
| [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) | Apache-2.0 | 16.260 | 2026-02-24 |
| [mlflow/mlflow](https://github.com/mlflow/mlflow) | Apache-2.0 | 28.726 | 2026-11-08 |

**Utilidad:** Langfuse para trazar costo, latencia y fallos de las llamadas al LLM (encaja con el roadmap de costos y calidad: caché del LLM, respaldo Groq→OpenAI). Ojo: RAGAS (la herramienta que ya usamos) tuvo su último push en febrero de 2026, mucho menos activo que los demás; conviene fijar su versión.

## 7. Ajuste fino, inferencia y PWA
| Repo | Licencia | ★ | Último push |
|---|---|---:|---|
| [unslothai/unsloth](https://github.com/unslothai/unsloth) | Apache-2.0 | 79.189 | 2026-11-08 |
| [vllm-project/vllm](https://github.com/vllm-project/vllm) | Apache-2.0 | 96.548 | 2026-11-08 |
| [serwist/serwist](https://github.com/serwist/serwist) | MIT | 1.501 | 2026-10-04 |

**Utilidad:** Unsloth para el ajuste QLoRA ya planeado (dataset propio de 209 pares); vLLM solo si algún día se sirve un modelo propio (hoy no); Serwist para modo sin conexión de la PWA (obra sin cobertura).

## Orden recomendado (esfuerzo bajo, retorno claro)
1. **Docling** sobre las páginas A.2 del espectro (§2).
2. **Pynite / section-properties** como referencia de las pruebas de `motor-estructural` (§3).
3. **Verificación de la delineación de cuencas** con `pyflwdir` (§5).
4. **Analítica sin contenido** con Umami o Matomo (§1), después de decidir dónde alojarla.
5. **Langfuse** para trazar costos del LLM (§6).

## 8. Segunda ronda: repositorios propuestos por el equipo (2026-11-08)
Misma limitación: metadatos y lectura del README; **no ejecuté ni instalé nada**.

| Repo | Licencia | ★ | Último push | Veredicto |
|---|---|---:|---|---|
| [vasudevan2604/geotechnical-report-extractor](https://github.com/vasudevan2604/geotechnical-report-extractor) | **sin licencia** | 0 | 2026-10-13 | **No usar. Ver aviso.** |
| [runtosolve/StructuralDataDash](https://github.com/runtosolve/StructuralDataDash) | sin licencia | n/d | 2026-07-05 | Solo como idea |
| [datadrivenconstruction/OpenConstructionERP](https://github.com/datadrivenconstruction/OpenConstructionERP) | **AGPL-3.0** | 1.313 | 2026-11-08 | Referencia de producto; no integrar |
| [imcs-compsim/pinns_for_comp_mech](https://github.com/imcs-compsim/pinns_for_comp_mech) | MIT | 72 | 2026-11-06 | Investigación; no producción |
| [hzlbbfrog/Generative-BIM](https://github.com/hzlbbfrog/Generative-BIM) | Apache-2.0 | 33 | 2025-07-27 | Investigación; bajo retorno |
| [ugurfeyzullah/Structural-optimization-with-VP](https://github.com/ugurfeyzullah/Structural-optimization-with-VP) | Apache-2.0 | 5 | 2024-06-25 | Descartar (depende de Dynamo/Revit/RSA) |
| [Nmg1994/Flood_Susceptibility_Model](https://github.com/Nmg1994/Flood_Susceptibility_Model) | sin licencia | 7 | 2026-06-08 | Solo como método a citar |
| [climatechange-ai-tutorials/flood-mapping-optical-and-microwave](https://github.com/climatechange-ai-tutorials/flood-mapping-optical-and-microwave) | MIT | 3 | 2025-12-06 | **Útil** (ver abajo) |

**Aviso sobre `geotechnical-report-extractor`.** El repositorio tiene 0 estrellas, creado el 2026-01-15 por una cuenta con 2 repositorios públicos, sin licencia, y su README manda a «descargar la aplicación» desde un `.zip` dentro del propio repositorio (`outler/…zip`, 0,6 MB y 1,4 MB). Ese patrón (README que empuja a descargar un ejecutable empaquetado) es típico de repositorios señuelo. El código en texto (`geotech.py`, Streamlit + PyMuPDF + pdfplumber + reportlab) leído sin ejecutar **no mostró** llamadas de red, `exec`, `eval` ni `subprocess`, y su pie de página atribuye la autoría a «AlexEngineered», de modo que parece una copia del trabajo de otra persona. **No descargué ni abrí los `.zip`.** Recomendación: no descargar esos archivos; si interesa la idea (extracción de parámetros de informes geotécnicos), buscar el original del autor atribuido y respetar su licencia. Además, está pensado para informes en inglés de EE. UU.; no se ajusta a un estudio de suelos colombiano (NSR-10, Título H) sin rehacer las expresiones regulares.

**StructuralDataDash.** Extrae datos de ensayos de artículos con un LLM y un caché de PDF. Es la misma idea que ya usamos con la bibliografía, sin licencia (no se puede reutilizar el código) y orientado a la AISC.

**OpenConstructionERP.** Presupuesto de obra (BOQ), cuantificación desde PDF/CAD/BIM, 4D/5D. Se solapa con nuestro motor de precios APU. Declara «120.000+ posiciones con precio» pero **no verifiqué** que los precios sean de Colombia ni su vigencia. AGPL: integrar su código obligaría a publicar el nuestro; sirve como comparación de producto.

**PINNs, Generative-BIM, optimización con Dynamo.** Investigación académica. El proyecto ya eliminó la PINN por no ser un modelo real en producción; ninguno aporta algo desplegable hoy.

**Modelo de susceptibilidad a inundación (Nmg1994).** Seis algoritmos de aprendizaje automático comparados; sin licencia, de modo que no se reutiliza código. Nuestra regionalización y la susceptibilidad municipal ya cubren ese terreno con validación a ciegas.

**Cartografía de inundaciones con Sentinel-1/2 (Climate Change AI, MIT).** Es el que sí abre una línea nueva: validar el HAND < 10 m y la susceptibilidad del Caribe contra **extensiones de agua observadas por satélite** (SAR de Sentinel-1 atraviesa nubes), en vez de contra reportes de la UNGRD. Es la validación que a la hipótesis de vías en terreno bajo le faltó. Hipótesis candidata, sin preregistrar: «las celdas HAND < 10 m del Caribe se inundan con más frecuencia en el SAR que las de HAND ≥ 10 m». Datos gratuitos; hay que verificar el volumen de descarga antes.

**Tema `structural-health-monitoring` (Python, por estrellas).** Los más votados son académicos y pequeños (máximo 62 estrellas, la mayoría con último cambio en 2018-2021). Ninguno es una librería lista para producción. Mencionable: `Ayberkrk/timoshenko` (Apache-2.0, análisis modal y flujos de sensores, 3 estrellas, activo) como ejemplo de bloques reutilizables, y `CSUCRYE/bridge-inspection-ai` (clasificador de fisuras); su exactitud declarada de 99,8 % es de su propia partición y no la verifiqué.

## 9. Analítica con Umami: estado
Código preparado, **inerte hasta configurar dos variables de entorno**: `NEXT_PUBLIC_UMAMI_SCRIPT_URL` y `NEXT_PUBLIC_UMAMI_WEBSITE_ID` (`apps/web/src/app/layout.tsx`, `apps/web/src/lib/analitica.ts`). El módulo solo acepta una lista cerrada de eventos y propiedades de tipo categoría, y descarta cualquier texto libre, así que ni una pregunta ni el nombre de un proyecto pueden salir hacia la analítica. Respeta «No rastrear». **Falta:** alojar una instancia de Umami (propia o en su nube; crear la cuenta o el servidor es decisión del equipo) y llamar a `registrarEvento` desde los puntos del producto (hoy no hay ninguna llamada).
