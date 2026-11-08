# F1: verificación de fuentes nacionales de Perú y Ecuador (issue #110)

Fecha: 2026-11-08. Protocolo: `PROTOCOLO_REPLICACION_PAISES_VECINOS_2026-11.md`, fase F1. **Solo lectura: no se descargó ningún archivo.** Todo se hizo con búsqueda web y lectura de páginas.

Niveles de verificación usados abajo:
- **Página primaria leída:** una herramienta leyó la página oficial del portal (la herramienta resume el texto; no vi el original en pantalla).
- **Solo búsqueda:** el dato sale de resultados de búsqueda; no se abrió la fuente. No es evidencia suficiente.
- **No accesible:** la página falló; no se sabe nada.

## Corrección de lo dicho antes
`PERU_CHILE_EXTRACCION_Y_PLAN_REGIONAL_2026-11.md` dice que el equivalente de la UNGRD en Perú (INDECI/SINPAD) «no se encontró». **Era incorrecto o incompleto:** el portal nacional de datos abiertos lo publica (ver P-EV abajo). Faltó buscar en el portal en vez de solo en buscadores generales.

## Perú

| Id | Fuente | Qué hay (según la página leída) | Licencia | Nivel | Qué falta antes de usarla |
|---|---|---|---|---|---|
| P-EV | **Emergencias históricas registradas por el INDECI** (datosabiertos.gob.pe, publicador MINDEF) | Registros del SINPAD, 2003 hasta hoy; archivos anuales; modificado 2026-09-15; primera publicación 2018-03-23; actualización anual | **ODC-BY** (la página lo indica) | Página primaria leída | Columnas, tamaños y codificación **no se ven en la página**. Los recursos rotulados «csv» apuntan a archivos `.xls` (Emergencias20XX.xls), y el de 2007 en formato ArcGIS (`.zip`). El número de archivos varía en la página (16 listados). Hay que ver si trae tipo de evento, fecha, ubicación y daños. Es un registro de **reportes** (como la UNGRD), por tanto el sesgo de reporte aplica |
| P-EV2 | «Emergencias y daños a nivel nacional por departamento» (INDECI) | Consolidado del SINPAD por departamento; docx, xlsx, 2 csv | No indicada | Página primaria leída | Agregado por departamento: sirve poco para análisis municipal; fechas no indicadas |
| P-MM | **Inventario de peligros geológicos de INGEMMET** (GEOCATMIN) | La búsqueda indica: inventario nacional concluido en 2009; descarga libre de «bases de datos referenciales» en GEOCATMIN; una capa «Peligros Geológicos» en un servicio ArcGIS REST con versión de febrero de 2013; una fuente de CENEPRED menciona 36.188 peligros inventariados (fecha incierta) | No es CC explícita; un documento del CENEPRED dice que se permite el uso citando a GEOCATMIN | **Solo búsqueda**. El servicio REST dio error de certificado y no se abrió (no se desactivó la verificación) | Confirmar en el sitio de INGEMMET si hay descarga de la capa, formato, fecha de corte (2009/2013) y términos de uso. **Inventario con fecha de corte antigua:** no cubre eventos recientes |
| P-CAU | **CAMELS-PE** (SENAMHI; Zenodo) | 136 cuencas con caudal diario observado y simulado, forzantes, atributos; v1.0.1 DOI 10.5281/zenodo.21195425; la revisión menciona v2.0 (1981–2025) con DOI 10.5281/zenodo.23890227 | **CC BY 4.0** (página del preprint) | Página primaria leída (preprint; 100.000 de 132.895 caracteres) | **Es un preprint en revisión** (discusión desde 2026-07-10): no tiene validez de publicación final. Limitaciones declaradas por los autores: caudales por curvas de descarga con lecturas diurnas que pueden perder crestas, extrapolación en caudales altos, desfase de 7 h entre lluvia y caudal, subestimación de la lluvia por pluviómetros en cuencas andinas. **Observaciones disponibles en 109 de 136 cuencas**; el resto es caudal simulado. Los caudales máximos (lo que usa nuestra regionalización) son justo lo más débil. No se leyeron las últimas 32.895 caracteres de la página |
| P-LL | SENAMHI / ANA (pluviómetros y caudales) | La búsqueda indica descarga web en el portal de SENAMHI (la serie histórica diaria llegaría hasta ~2013–2014, con una base nueva para estaciones recientes) y SNIRH de la ANA; no se encontró API oficial documentada | Sin verificar | **Solo búsqueda** (fuente secundaria: guía de Purdue) | Abrir los portales y comprobar cobertura, licencia y si hay descarga masiva |
| P-AM | Mapa de susceptibilidad por movimientos en masa 1:1.000.000 (INGEMMET) | Existe según la búsqueda; el 86 % de los movimientos inventariados cae en susceptibilidad alta o muy alta (cifra de una fuente secundaria) | Sin verificar | **Solo búsqueda** | Equivalente al mapa del SGC, pero a escala nacional gruesa; sin descarga confirmada |

## Ecuador

| Id | Fuente | Qué hay | Licencia | Nivel | Qué falta |
|---|---|---|---|---|---|
| E-EV | **Registro de eventos peligrosos de la SNGR** | **No hay descarga abierta encontrada.** Hay un trámite en gob.ec para pedir información histórica de daños y de información espacial; informes de situación en PDF (por ejemplo, 78 eventos adversos desde el 1-ene-2025 por cantón y parroquia); la prensa cita 66.046 eventos entre 2010 y 2023 | Por solicitud | Búsqueda; página del trámite no abierta | Una solicitud formal (la haría el usuario) a atencionciudadana@gestionderiesgos.gob.ec; la cifra de 66.046 eventos es de prensa, sin verificar |
| E-EV2 | **DesInventar Sendai** (UNDRR) | La búsqueda indica que su página de descarga lista Ecuador y Perú entre las bases por país | La licencia del *software* es Apache-2; la de los **datos** no se vio | La página de descarga devolvió **403**: no accesible | Abrir la página en un navegador, ver los archivos de Ecuador y Perú, su periodo (históricamente 1970–2009 para Ecuador, según un estudio), y los términos de los datos. Puede ser una fuente común para ambos países |
| E-MM | Inventario de movimientos en masa del IIGE | **No se encontró ningún portal con datos abiertos.** Solo tesis (EPN: mapa a 1:1.000.000; PUCE), estudios locales y un inventario del sismo de Pedernales 2016 (Chunga et al., 2019); la herramienta MARLI (Sellers et al., 2021) para reportar | — | Solo búsqueda | Pedir a la IIGE, o revisar el suplemento de Chunga et al.; sin inventario nacional abierto no se puede replicar P5 |
| E-CAU | Caudales del INAMHI | No hay portal abierto encontrado; los estudios citan datos «proporcionados por el instituto» y anuarios (1963–2010) digitalizados, algunos en Scribd (procedencia no verificada). No existe un CAMELS-EC; Caravan no cubre Ecuador. iMHEA tiene sitios andinos pareados (Ecuador, Perú, Bolivia) pero no es de muestra grande | — | Solo búsqueda | Solicitud al INAMHI, o la red iMHEA para una prueba limitada |
| E-OD | Portal nacional de datos abiertos (datosabiertos.gob.ec), búsqueda «riesgos» | Solo mapas agroclimáticos de riesgo por inundación, sequía y helada (2022, XLSX) y conjuntos administrativos de gestión de riesgos. **Ningún inventario de movimientos en masa ni registro de eventos** | No indicada | Página primaria leída | — |

## Lectura por prueba del protocolo

| Prueba | Perú | Ecuador |
|---|---|---|
| P1 terreno (solo insumos globales) | Ejecutable | Ejecutable |
| P7 rezagos ONI/TNA→lluvia (CHIRPS) | Ejecutable | Ejecutable |
| P10 comparación normativa | Ejecutable en la parte verificada de E.030 (caps. 2–4, RM 183-2026) | Bloqueada por vigencia no verificada |
| P3 amenaza oficial frente a eventos | **Potencialmente ejecutable** si P-EV trae ubicación y fecha utilizables; el mapa oficial (P-AM) no tiene descarga confirmada | **Bloqueada** (sin eventos abiertos ni mapa descargable) |
| P4 exposición vial (réplica de V1) | Ejecutable si P-EV sirve; mismo condicionante | Bloqueada |
| P5 susceptibilidad con ML | Condicionada a una capa de INGEMMET con descarga y fecha adecuada | Bloqueada (sin inventario) |
| P6 transferibilidad de la regionalización | Parcial: CAMELS-PE, pero solo 109 cuencas con observación, y es preprint; **los máximos son lo menos fiable** | Bloqueada |
| P8 coherencia de caudales y ENSO | Condicionada a caudales mensuales de SENAMHI/ANA o de CAMELS-PE | Bloqueada |
| P9 umbrales lluvia-duración | Condicionada a fecha de evento en P-EV (la fecha podría ser la del reporte) | Bloqueada |

Ecuador queda con solo P1 y P7 (y quizá P10 cuando se verifique la vigencia) hasta obtener datos por solicitud formal. No se sustituirá nada por indicadores inventados.

## Riesgos específicos que esta verificación hace visibles
1. **Sesgo de reporte en P-EV:** SINPAD es un registro de emergencias reportadas, como la UNGRD. Debe medirse con el mismo método (indicador de capacidad de reporte) y la limitación es la ya conocida.
2. **Fecha de corte del inventario peruano (2009/2013):** comparar con eventos de 2003–2026 mezclaría épocas. La réplica de SGC–UNGRD (eventos recientes frente a un mapa) requeriría una definición de periodo.
3. **CAMELS-PE como preprint:** puede cambiar entre v1.0.1 y v2.0; no se puede citar como validado.
4. **Posible fuga:** PISCO (la lluvia con que se construyó CAMELS-PE) se calibra con las estaciones de SENAMHI; compararlo con pluviómetros de SENAMHI no es independiente (mismo problema que CHIRPS y las normales del IDEAM).

## Permisos de descarga que se pedirían (nada se bajó)
| Archivo | Fuente | Tamaño | Para qué |
|---|---|---|---|
| Emergencias20XX.xls (un año de prueba, p. ej. 2019) | datosabiertos.gob.pe, dataset «Emergencias históricas registradas por el INDECI» | **No se conoce** (la página no lo muestra) | Ver columnas y calidad antes de bajar todo |
| Registro de Ecuador y Perú de DesInventar Sendai | desinventar-api.undrr.org | No se conoce | Fuente común de eventos para ambos países |
| CAMELS-PE v1.0.1 | Zenodo 10.5281/zenodo.21195425 | No se conoce | Cuencas y caudales; usar solo con las advertencias de arriba |

## Siguiente paso propuesto
1. Que el usuario autorice descargar **un solo año** de SINPAD para inspeccionar la estructura; el tamaño se verifica al empezar y se informa antes de continuar.
2. Abrir en el navegador la página de DesInventar (que devolvió 403) y la del INGEMMET (certificado) para completar lo que quedó en «solo búsqueda».
3. En paralelo, el usuario podría iniciar la solicitud formal a la SNGR y al INAMHI de Ecuador.
