# Excavación y voladura en vías troncales: qué dice la norma colombiana y qué fuentes internacionales la complementan (issue #110)

Fecha: 2026-11-08. Alcance: **normativo y de riesgo**; el repositorio no recibe procedimientos operativos de manejo de explosivos. Estado: borrador. La verificación de fuentes extranjeras está en `VERIFICACION_REFERENCIAS_INTERNACIONALES_2026-11.md`. Lo marcado «verificado» se leyó en el texto; lo marcado «sin verificar» salió de un resumen o de una búsqueda.

## 1. Lo que dice la especificación colombiana (edición 2012)

**Fuente leída:** capítulo 2 «Explanaciones» de las Normas y Especificaciones INVÍAS 2012, en la copia anexa a una convocatoria pública de Findeter (212 páginas, texto extraíble). Es una copia de terceros de una edición **anterior a la vigente**: las Especificaciones Generales vigentes se adoptaron por la Res. 4561/2022 y se modificaron después (Res. 6044/2024 y 2025). El artículo 210-22 no se obtuvo, así que **no se puede afirmar que el texto de abajo siga igual en la edición vigente**.

| Artículo (2012) | Qué dice sobre explosivos y voladura (verificado en el texto) |
|---|---|
| 200.4 (desmonte y limpieza) | No se permite el uso de explosivos para remover la vegetación |
| 201.3 (demolición y remoción) | El interventor puede autorizar explosivos; el constructor responde por los daños de un manejo incorrecto. Con explosivos se lleva registro detallado de clase, proveedor, existencias y consumo; su uso, manejo y almacenamiento se confían a personas experimentadas y se sujetan a las leyes y reglamentos de las entidades que los controlan. Si los explosivos no son admisibles por impacto ambiental, se recurre a técnicas alternativas |
| 210.1.3.2.1 | Define «excavación en roca»: masas de roca fuertemente litificada que requieren **empleo sistemático de explosivos**, y bloques mayores de 1 m³ que para fragmentarse los requieren. El criterio práctico es que dureza y fracturamiento no permitan remover con equipo mecánico |
| 210.4 (excavación) | El constructor debe evitar inestabilidad de taludes en roca o de bloques por voladuras inadecuadas o por descalce del pie; la excavación avanza coordinada con contención y drenaje |
| 210.4.1.5 | Procedimientos, tipos y cantidades de explosivos y equipos, y la secuencia y disposición de las voladuras, **los aprueba antes el interventor**. La aprobación **no exime** al constructor de responsabilidad por errores y daños de las voladuras. Toda excavación en roca se profundiza 15 cm bajo la subrasante |
| Pago (210 y 201) | El precio unitario incluye perforación en roca, precortes, explosivos y voladuras, y los costos de adquisición, transporte, escoltas, almacenamiento, vigilancia y control |
| 221 (pedraplenes) | Menciona voladuras con explosivos para preparar la superficie de apoyo según el proyecto |

**Hallazgo principal:** en las 11 páginas de ese capítulo donde aparecen «explosivos» o «voladura», y tras buscar en las 212 páginas los términos «vibración», «velocidad pico», «partícula», «mm/s», «sobrepresión» y «onda aérea» (los únicos aciertos eran granulometría y la palabra «particulares»), **no hay límites numéricos de vibración, de sobrepresión ni de distancia a estructuras, ni un método de diseño de voladura**. La norma delega en la aprobación del interventor y en las leyes de control de explosivos. Falta comprobar si la edición 2022 y los apéndices técnicos de los contratos de concesión agregan esos límites. Hasta entonces es una hipótesis, no una conclusión.

Ya está en el corpus el Manual de Interventoría 2022 (registro de provisión, consumo y existencia de explosivos) y el Manual de Túneles 2021 (28 fragmentos con términos de voladura/explosivos); las Especificaciones Generales de Carreteras **no** están.

## 2. Fuentes internacionales candidatas

Criterio de aceptación: sirven como **referencia comparada**, nunca como norma colombiana. Cada respuesta del sistema que las use debe decir que son referencias de otro país y que en Colombia no son obligatorias.

| Fuente | Para qué sirve | Estado de verificación | Acceso |
|---|---|---|---|
| USBM RI 8507 (Siskind et al., 1980), vibración de voladuras y daño a estructuras | Criterios de velocidad pico de partícula según frecuencia (la búsqueda indica entre 0,5 pulg/s a baja frecuencia y 2,0 pulg/s a alta, según estructura). Dowding (1996) señala que el estudio casi no midió voladuras por debajo de 5 Hz | Rangos confirmados por búsqueda secundaria; texto no leído | Publicación de una agencia federal de EE. UU. (a confirmar la licencia del ejemplar) |
| FHWA, Rock Slopes Reference Manual (FHWA HI-99-007) | Taludes en roca de carreteras, incluida la voladura controlada | **Sin verificar** (la búsqueda no lo devolvió) | Publicación federal de EE. UU., por confirmar |
| Perú: DS 024-2016-EM (seguridad y salud ocupacional en minería) con DS 023-2017-EM y una modificación de 2023 (número sin confirmar: se cita como 034 y como 035) | Marco andino cercano para explosivos y labores subterráneas | Cadena parcial confirmada en búsqueda; texto consolidado sin verificar; hay un proyecto de nueva modificación | Publicación oficial peruana |
| Chile: DS 132 (seguridad minera) y estándares de túneles de Vialidad 2023 | Referencia andina; los estándares de túneles de 2023 reemplazarían partes del Manual de Carreteras según un artículo de 2024 | **Sin verificar**; no se encontró el DS 132 | Por confirmar |
| Normas de vibración europeas (DIN 4150-3, BS 7385-2) | Criterios alternativos a la USBM | **Sin verificar**, listadas de memoria | Normalmente de pago: no se ingesta el texto, solo se cita |
| ISRM, métodos sugeridos; clasificaciones de macizo (RMR, Q, GSI) | Caracterización de roca | Literatura académica abierta en parte | Mixto |
| Ferroviaria: AREMA, UIC | Pendientes y geometría de vía | **Sin verificar**, de pago | No se ingesta texto |

## 3. Reglas para usar datos de otros países

1. **Etiquetado:** todo fragmento internacional lleva `norma_ref` con país y año, y un indicador de «referencia comparada, sin vigencia en Colombia».
2. **Transferibilidad:** un criterio extranjero se acepta solo con una prueba explícita de aplicabilidad (geología, meteorización tropical, sismicidad, tipo de estructura). Los criterios de vibración de EE. UU. se calibraron con casas y minas de ese país, no con vivienda colombiana.
3. **Jerarquía de respuesta:** primero lo colombiano vigente; si no existe un valor, decirlo; después el criterio internacional con su límite de aplicabilidad. El sistema no debe presentar un valor extranjero como si fuera exigencia nacional.
4. **No ingestar texto de pago o con licencia dudosa.** Solo metadatos y cita.
5. **Verificar vigencia** de la fuente extranjera con el mismo rigor que la colombiana.

### Implementación de las reglas (2026-11-08)
- `packages/construdata/referencia_internacional.py`: convención `norma_ref = INT/<PAIS>/<AÑO> — <nombre>`, validador y regla de prompt.
- `rag_multi_norma.py`: el contexto marca los fragmentos con ese prefijo («🌐 REFERENCIA INTERNACIONAL») y, solo si hay alguno, el prompt agrega la regla de jerarquía (primero Colombia; decir si no hay valor; país, año y límite de aplicabilidad; no mezclar citas).
- `apps/api/tests/test_referencia_internacional.py`: 8 pruebas, sin red. **No hay aún fragmentos extranjeros en la base**; las reglas no cambian ninguna respuesta actual. No se probó con un LLM real, porque no hay datos con los que probarlo.

## 4. Hipótesis que se desprenden (cada una con protocolo antes de calcular)

- **H-B1:** si la norma colombiana no fija límites de vibración, ¿qué criterio debe usar un diseñador? Pregunta de evaluación para el RAG: la respuesta correcta es «la especificación no fija valores; criterios internacionales como USBM RI 8507 existen con estas limitaciones». Se puede medir con preguntas de abstención parcial.
- **H-B2:** ¿la edición 2022 agregó límites que la 2012 no tenía? Se resuelve leyendo el artículo 210-22 y los apéndices de concesiones.
- **H-C1:** comparación excavación mecánica / voladura / túnel por tramo, con datos reales de costos (INVÍAS, SECOP) y de macizo; sin datos de macizo no se afirma.
- **H-T:** pruebas de transferibilidad: ¿los resultados de otros países sobre estabilidad de taludes en roca reproducen los inventarios SIMMA de Colombia en cuencas andinas? Requiere datos y protocolo.

## 5. Sobre «soluciones óptimas»

El sistema puede dar respaldo trazable (qué norma, qué país, con qué límite), pero **«óptimo» exige datos de sitio y validación que hoy no existen para la mayoría de estos dominios**. La meta realista es apoyo a la decisión con fuentes citadas y límites declarados, no una solución única. Cada respuesta debe indicar qué parte es norma colombiana, qué parte es referencia extranjera y qué parte es inferencia.

## 6. Pendiente

- **Artículo 210-22 (intento 2, sin éxito):** se probaron el índice de la edición 2022 en Scribd (80 páginas, texto truncado), el texto de una resolución de 2022 en el SIDN de la Rama Judicial (solo parte resolutiva del Diario Oficial) y un apéndice técnico de concesión de la ANI (agregados; no trae el 210). Ninguno contiene el artículo. Vías que quedan: (a) descarga del documento completo en el sitio de INVÍAS o de MinTransporte (no se localizó una URL directa); (b) los apéndices técnicos de contratos de concesión de la ANI que reproducen el artículo; (c) un derecho de petición a INVÍAS, que presentaría el usuario; (d) una biblioteca universitaria con el volumen impreso.
- Cadena de modificaciones de 2022 a 2025 del capítulo 2 sin verificar.
- Verificar en fuente primaria las referencias extranjeras marcadas «sin verificar».
- Decidir con el usuario el orden de ingesta.
