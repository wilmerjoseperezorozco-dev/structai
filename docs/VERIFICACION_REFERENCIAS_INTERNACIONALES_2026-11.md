# Verificación de referencias internacionales para excavación y voladura (issue #110)

Fecha: 2026-11-08. Estado: **primera pasada**. Se confirmó la existencia y la identidad de cada fuente, no su contenido numérico completo. Nada se ingestó. Recordatorio: todo fragmento extranjero entra con `norma_ref = INT/<PAIS>/<AÑO> — …` y se presenta siempre como referencia comparada, no obligatoria en Colombia (`referencia_internacional.py`).

| Fuente | Qué se verificó | Qué NO se verificó | Licencia / acceso | Decisión |
|---|---|---|---|---|
| **USBM RI 8507** (Siskind, Stagg, Kopp, Dowding, 1980) | Identidad, autores y año; el informe está en CDC Stacks. Resumen oficial: mediciones en 76 viviendas y 219 voladuras de producción; niveles seguros de 0,5 a 2,0 pulg/s para estructuras residenciales | Los valores por frecuencia y la distinción yeso/panel: **las páginas del cuerpo del PDF son imagen escaneada** sin texto. El propio texto legible trae una fe de erratas (corrige valores de la tabla 9), que habría que aplicar al ingestar | Publicación del gobierno federal de EE. UU. (a confirmar la licencia del ejemplar) | Ingestar solo con OCR revisado a mano y la fe de erratas aplicada. Hasta entonces se cita el resumen, no el criterio |
| **30 CFR 816.67** (OSMRE, EE. UU.) | Texto oficial en eCFR, legible. Límites de sobrepresión (134 a 129 dB pico según la respuesta del instrumento; 105 dBC) y de velocidad pico de partícula (1,25 pulg/s hasta 300 pies; 1,00 de 301 a 5.000 pies; 0,75 por encima) con registro sismográfico por voladura. Historial de enmiendas (1983, 2016, 2017) y una nota editorial sobre enmiendas eliminadas | La Figura 1 (límites por frecuencia) está solo como imagen. **El texto no dice a qué actividad aplica; por contexto normativo es minería de superficie con permiso**, no obra vial | Texto regulatorio federal, de acceso público | **Mejor candidata técnica**: es texto verificable con valores numéricos. Siempre con la salvedad de que se diseñó para minería de superficie en EE. UU. |
| **FHWA, Rock Slopes Reference Manual** | La referencia correcta es **FHWA HI-99-007** (Munfakh, Wyllie, Mah, 1998), citada por Iowa DOT y WSDOT. Otro manual de FHWA, «Rock Blasting and Overbreak Control», figura como FHWA-HI-92-001. El informe de 1989 «Rock Slopes: Design, Excavation, Stabilization» está en el repositorio ROSAP (número citado: FHWA-S-89-045) | No se obtuvo ningún PDF ni se leyó contenido. La numeración sale de citas secundarias | Publicaciones federales de EE. UU.; confirmar licencia y disponibilidad | Verificar en el sitio de FHWA/ROSAP antes de ingestar. **Corrige la referencia «FHWA-NHI-99-007» que figuraba en un borrador anterior** |
| **Perú, DS 024-2016-EM** (seguridad y salud ocupacional en minería) | Publicado en El Peruano el 2016-07-28; 5 títulos, 56 capítulos, 417 artículos según el decreto aprobatorio. Fuente oficial: El Peruano. Modificado por el DS 023-2017-EM | **Contenido del capítulo de explosivos no leído.** El número del artículo 75 citado en documentos de empresa no se verificó. **La modificación de 2023 se cita con dos números distintos (034-2023-EM y 035-2023-EM)** en fuentes secundarias | Publicación oficial peruana | No ingestar hasta resolver la modificación de 2023 con el texto oficial. El número «034-2023» del borrador anterior queda sin confirmar |
| **Chile DS 132** y estándares de túneles de Vialidad 2023 | Una búsqueda anterior no devolvió el DS 132 | Todo | — | Pendiente de búsqueda |
| **DIN 4150-3, BS 7385-2** | Nada: listadas de memoria | Todo | Normalmente de pago | No ingestar texto; solo cita. Pendiente |

## Lecturas

1. **Ya hay una base citable:** el 30 CFR 816.67 da valores numéricos verificables para contrastar con el vacío de la especificación colombiana 2012. Su límite principal es de aplicabilidad (minería de superficie, EE. UU.), que es justo la prueba de transferibilidad que exigen las reglas.
2. **El RI 8507 es la referencia más citada pero hoy no está en texto utilizable.** Ingestarlo exige un OCR cuyos errores se revisen a mano; las cifras de las fuentes secundarias no se usan como si fueran el informe.
3. **Dos correcciones propias:** el código del manual de FHWA y el número de la modificación peruana de 2023 estaban mal o sin confirmar en el documento anterior.
4. **Ninguna de estas fuentes valida un diseño en Colombia.** Sirven para decirle al usuario qué criterios existen y con qué límites.

## Pendiente

- OCR revisado del RI 8507 con la fe de erratas, o pedir el texto a una biblioteca con versión con capa de texto.
- Obtener el HI-99-007 y el HI-92-001 de FHWA y leer su capítulo de voladura.
- Leer el capítulo de explosivos del DS 024-2016-EM en el texto oficial y fijar el número de la modificación de 2023.
- Buscar el DS 132 de Chile y los estándares de túneles de 2023.
- Crear la primera prueba de transferibilidad entre el criterio de 30 CFR 816.67 y el caso de una obra vial en cordillera colombiana (requiere protocolo previo).
