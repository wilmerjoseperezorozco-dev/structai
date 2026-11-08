# Perú y Chile: qué se puede extraer y plan de análisis regional (issue #110)

Fecha: 2026-11-08. Estado: **inventario y plan; no se calculó ni ingestó nada**. Lo extraído del texto normativo viene de una lectura resumida por herramienta (no revisada artículo por artículo contra el original) y debe contrastarse antes de citarse.

## 1. Perú: DS 024-2016-EM (explosivos y voladura)

**Fuente leída:** publicación original en El Peruano (norma legal, 28-jul-2016, vigente desde el día siguiente). Es el **texto de 2016**: no incorpora las modificaciones del DS 023-2017-EM ni la de 2023, de modo que algún artículo puede haber cambiado.

| Artículos | Contenido (resumen, sin verificar artículo por artículo) |
|---|---|
| 267–270 (voladura a cielo abierto) | Evacuación en un radio de seguridad de 500 m; cargar de día o de noche pero **amarrar y disparar solo de día**; señales preventivas de 10 minutos con alcance no menor de 500 m; cerca de edificios, voladura controlada para que no cause daño a edificaciones cercanas (267 i); el titular **monitorea las vibraciones** y toma medidas correctivas (268); horarios de disparo para proteger a trabajadores y pobladores (269) |
| 278–291, Cap. VI «Explosivos» | Autorización y registro ante SUCAMEC (278); polvorines con licencia (279); muros o terraplenes de protección, con 3 m de altura sobre carreteras o vías férreas (280); depósitos separados por tipo (283); polvorín auxiliar subterráneo limitado a 24 horas de consumo (284); control por persona capacitada (285); zona libre de material combustible de 10 m (286); transporte y manipulación por personal autorizado (287–288); destrucción de explosivos por personal entrenado (289); agentes de voladura y ANFO (290–291) |
| Anexos 34, 35, 36 | Destrucción de explosivos y fulminantes; uso de ANFO en minas subterráneas |

**Hallazgo comparado:** igual que la especificación colombiana 2012, en estos artículos **no aparece un límite numérico de vibración**; el reglamento peruano exige *monitorear* y *corregir*. El único criterio de distancia explícito es de seguridad de personas (500 m), no de daño a estructuras. Es una observación sobre el texto de 2016 y sobre el tramo que cubrió la lectura (no se leyó el último 11 % de la página); debe confirmarse contra el consolidado vigente.

**Alcance:** es un reglamento **minero**, no una norma de obra vial. Aplica como referencia comparada (reglas de `referencia_internacional.py`), no como equivalente de la especificación vial.

## 2. Lo que StructAI ya tiene de Perú y Ecuador (conteo real en la base)

- `peru_e030_chunks`: 204 filas; `peru_e030_zonificacion_distrital`: 1.884 filas.
- `ecuador_nec_se_ds_chunks`: 395; `ecuador_nec_se_ds_zonificacion_poblacion`: 512.
- Perú y Ecuador **no tienen fila en `normas_registro`** (consulta por código, sin resultados): su vigencia se maneja por fuera del registro. Es un hueco de gobernanza que hay que cerrar antes de ampliar.

## 3. Datos abiertos para replicar el análisis de Colombia

El análisis colombiano usó DEM Copernicus 30 m, lluvia CHIRPS, HAND, cobertura ESA WorldCover, el mapa de amenaza del SGC y reportes de la UNGRD. Equivalentes (existencia confirmada por búsqueda; licencias y formatos sin verificar):

| Variable | Global | Perú | Chile |
|---|---|---|---|
| Relieve | Copernicus DEM | — | — |
| Lluvia | CHIRPS | SENAMHI (no verificado) | DMC / DGA (no verificado) |
| Cobertura | ESA WorldCover | — | — |
| Inventario de movimientos en masa | — | **INGEMMET GEOCATMIN**: inventario de peligros geológicos y mapa de susceptibilidad; reportado como integrado a la plataforma nacional de datos abiertos | **SERNAGEOMIN**: Observatorio Nacional de Peligros Geológicos y Mineros; ~8.000 productos liberados. El dataset de remociones en masa no se confirmó |
| Emergencias (equivalente a UNGRD) | — | INDECI / SINPAD (**corregido 2026-11-08: sí existe** en datosabiertos.gob.pe, ODC-BY, 2003–hoy; ver `F1_VERIFICACION_FUENTES_PERU_ECUADOR_2026-11.md`) | SENAPRED (**no encontrado**) |
| Caudales | — | ANA (no buscado) | DGA (aparece en un catálogo de la IRI hasta 2024) |
| Riesgo y escenarios | — | CENEPRED/SIGRID (informes de evaluación de peligros) | — |

**Límite crítico:** la parte de eventos (UNGRD) fue la que permitió medir el *sesgo de reporte* en Colombia. Sin un equivalente verificado en Perú o Chile, esa línea no se puede replicar todavía.

## 4. Chile

- **DS 132 (Reglamento de Seguridad Minera):** sigue siendo el texto base (aprobado en 2002, publicado en 2004), con modificaciones (DS 34 de 2013; el Título XV por DS 30 de 2021 y un decreto de 2024) y una actualización en consulta desde 2025. Una nota de prensa de julio de 2026 habla de un nuevo decreto que lo modifica; **no se confirmó que esté en vigor**. Las fuentes dan fechas de vigencia contradictorias (2004 y 2007). No se encontró nada sobre el control de explosivos (Ley 17.798).
- Estándares de túneles de Vialidad 2023: citados por un artículo de 2024; no verificados.
- No se descargó nada. La vigencia exige leer las modificaciones en BCN LeyChile.

## 5. Brechas continentales (hipótesis de trabajo, no propuestas de norma)

Hoy solo una brecha tiene evidencia en dos países:

- **G1:** ni la especificación vial colombiana 2012 ni el reglamento minero peruano 2016 fijan **límites numéricos de vibración**; exigen aprobación o monitoreo. En EE. UU. sí existen (30 CFR 816.67). Hipótesis: la región carece de criterio numérico propio y los diseñadores importan valores sin prueba de transferibilidad. Falta ver si Chile y Ecuador lo fijan, y si la edición 2022 de INVÍAS lo agrega.

Otras brechas candidatas, sin evidencia todavía, por tanto solo preguntas:

- **G2:** ¿hay inventarios nacionales de puentes y de taludes abiertos y comparables entre países? (en Colombia no se halló el inventario nacional de puentes).
- **G3:** ¿existen referencias regionales para criterios de taludes en roca, o cada país cita FHWA y AASHTO por separado?
- **G4:** ¿qué normas de Perú y Chile están vigentes pero no ingestadas, y cuántas se parecen a las colombianas? Una comparación solo es válida con texto verificado y vigencia fechada.

Una «norma continental» no es un entregable técnico de este proyecto. Lo que sí se puede entregar son **tablas comparativas con fuente y vigencia** que muestren dónde coinciden o difieren los países y qué falta. Cualquier propuesta normativa requeriría revisión de especialistas y de las entidades de cada país.

## 6. Orden propuesto (cada paso con protocolo previo)

1. Registrar Perú y Ecuador en `normas_registro` y fechar su vigencia (la RM 183-2026-VIVIENDA ya se conoce para la E.030).
2. Verificar en el texto consolidado los artículos 267–270 y 278–291 del DS 024-2016-EM y las modificaciones de 2017 y 2023.
3. Confirmar licencia y descarga de INGEMMET GEOCATMIN y de SERNAGEOMIN; pedir permiso para bajar archivos (nombre, fuente y tamaño).
4. Protocolo de replicación en una región piloto de Perú con las mismas variables de relieve, lluvia y cobertura del Caribe colombiano, **sin interpretar** hasta confirmar datos de eventos.
5. Decidir si hay equivalentes de INDECI y SENAPRED antes de intentar el análisis de sesgo de reporte.
