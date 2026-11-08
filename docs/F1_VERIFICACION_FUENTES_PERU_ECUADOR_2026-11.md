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

## Actualización del mismo día: intento de descarga (sin éxito)
- **Corrección:** el conjunto «Emergencias históricas registradas por el INDECI» tiene archivos anuales solo de **2003 a 2018** (más una versión ArcGIS de 2007). La descripción dice «hasta el presente», pero **no hay recurso de 2019 en adelante**. Antes escribí «2003–hoy»: era incorrecto. Consecuencia: **no hay solapamiento con el periodo de la UNGRD (2019–2024) ni con el de las pruebas colombianas recientes**, y la réplica directa de P3/P4/P9 con SINPAD de este conjunto no es posible; solo sirve para análisis dentro de 2003–2018 (CHIRPS cubre ese periodo).
- **Descarga:** se pidió `Emergencias2018.xls` (sitio oficial, 1 archivo). El servidor respondió **HTTP 418** con una página HTML de un cortafuegos web (cookie `HWWAFSESID`, cabecera `Block-Event-Id`), no con el archivo (3.195 bytes de HTML). Es una barrera contra clientes automáticos. **No se intentó eludirla.** No se obtuvo ningún dato.
- **Pendiente:** el usuario puede bajar el archivo desde el navegador (enlace directo: `https://www.datosabiertos.gob.pe/sites/default/files/Emergencias2018.xls`) y dejarlo en una carpeta; entonces se inspecciona la estructura.

## Actualización 2: el usuario abrió la página oficial; SINPAD sí sirve (2026-11-08)
**Error mío, corregido.** Concluí que el conjunto de INDECI terminaba en 2018 y que no servía para 2019-2024. Era el conjunto equivocado: el vigente es otro, «Emergencias y daños a nivel nacional por departamento» (INDECI, **ODC-BY**, modificado 2026-10-30, actualización semestral). Mi primera lectura lo descartó por su título («por departamento»), que **no describe su contenido**: son microdatos a nivel de **distrito** con código UBIGEO. El usuario tenía razón al insistir.

**Archivos** (leídos desde el navegador de la app, que no tropieza con el cortafuegos; descarga autorizada para SINPAD):
| Archivo | Tamaño | Contenido |
|---|---:|---|
| `BD_2003-2025_EMERGENCIAS.csv` | 27.040.446 bytes | 142.139 emergencias, 2003-2025 |
| `BD_2026_Semestre_I.csv` | 1.742.009 bytes | 9.352 emergencias, primer semestre de 2026 |
| `Diccionario de datos_9.xlsx` | 13.752 bytes | 55 filas de diccionario |
Copias de trabajo fuera del repo (no se versionan); perfil reproducible con `scripts/regional/sinpad_perfil.py`.

**Estructura:** 49 columnas; código de emergencia, fecha, año, mes, UBIGEO distrital (6 dígitos en el 100 % de las filas), departamento/provincia/distrito, peligro (22 tipos en 2019-2024), origen natural o inducido, región natural, y daños (fallecidos, desaparecidos, lesionados, damnificados, afectados, viviendas, centros educativos y de salud, cultivos, **puentes destruidos/afectados, carretera destruida/afectada en km, camino rural en km**, canales, animales, peso y costo de la ayuda humanitaria).

**Perfil 2019-2024:** 50.807 emergencias en 1.871 distritos de 26 departamentos. Peligros más frecuentes: lluvia intensa 16.272, incendio urbano 8.208, vientos fuertes 7.752, bajas temperaturas 6.213, incendio forestal 3.228, deslizamiento 2.217, inundación 2.117, erosión 958, huayco 902, derrumbe de cerro 827. Movimientos en masa (deslizamiento, huayco, derrumbe de cerro, alud, erosión: **agrupación mía, sin validar**): 4.917 registros en 1.124 distritos.

### Problemas de calidad encontrados (hay que tratarlos antes de cualquier análisis)
1. **Fecha de 2025 en otro formato.** Los 16.401 registros de 2025 vienen como `MM/DD/AA` (mes primero, año de dos dígitos): en 9.579 el segundo campo supera 12 y en ninguno el primero. El resto (2003-2024) es `DD/MM/AAAA` y su año coincide siempre con la columna AÑO. Interpretar 2025 como día primero falsearía fechas y rezagos. El diccionario dice «DD/MM/AAAA o MM/DD/AA» pero no avisa de cuál se usa dónde.
2. **Esquemas distintos entre archivos.** El de 2026 renombra columnas (`COD_UBIGEO`, `DEP`, `CODIGO EMERGENCIA INPAD`, `FECHA DE EMERGENCIA`, etc.; el de 2003-2025 tiene `COD. DISTRITO`, `DPTO.`...). Hay que armonizar antes de unirlos; y los canales de riego pasan de conteo a km en 2026 (los nombres terminan en «KM»): **la unidad cambió**.
3. **Codificación latin-1** y separador `;`. Leer como UTF-8 falla.
4. **Códigos repetidos:** 7 códigos de emergencia aparecen más de una vez, en fechas y distritos distintos (reutilización del identificador). No sirven como clave única.
5. **Ceros y datos faltantes son indistinguibles:** las columnas de daños no tienen vacíos (100 % no nulos), por lo que un 0 puede ser «sin daño» o «no evaluado». Solo el 0,8 % de los registros tiene fallecidos, el 33 % viviendas destruidas, el 1,7 % puentes destruidos, el 6 % carretera destruida.
6. **Salto de volumen en 2023-2025.** Registros por año: 4.492 (2019), 5.210, 7.799, 7.251, **12.388 (2023), 13.667 (2024), 16.401 (2025)**. Los distritos con al menos un evento no suben en proporción (1.063 en 2019; 1.666 en 2023; 1.573 en 2024; 1.671 en 2025), es decir, hay más registros por distrito. Puede ser más lluvia (Niño costero/Niña) o un cambio de práctica de registro; con estos datos no se puede separar. Es el mismo tipo de duda que el pico de 2022 de la UNGRD.
7. **Tasa base alta.** 1.571 a 1.671 distritos con evento por año en 2023-2025. Si Perú tiene unos 1.890 distritos (cifra de memoria, **sin verificar**), la mayoría tiene algún evento al año y el AUC por «hubo al menos un evento» tendrá poca potencia, como en Colombia.
8. **Fecha de evento o de reporte:** el diccionario dice «fecha en la que ocurrió el evento», sin garantía. Puede ser la de registro (misma limitación que la UNGRD).

### Qué cambia en el plan de F1
| Prueba | Antes | Ahora |
|---|---|---|
| P3 amenaza oficial frente a eventos | Condicionada | **Eventos disponibles, 2019-2024, distrital.** El obstáculo pasa a ser el mapa oficial (INGEMMET, descarga sin confirmar) |
| P4 exposición vial (réplica de V1) | Condicionada | **Eventos disponibles.** Además trae **daño a vías y puentes**, que la UNGRD no tenía: permite una validación que en Colombia no pudimos hacer. Riesgo: confusión con tamaño de red y sesgo de reporte |
| P9 umbrales lluvia-duración | Condicionada | **Fechas disponibles** (con el cuidado de 2025 y de reporte frente a ocurrencia). 2019-2024 coincide con la ventana de Colombia |
| Sesgo de reporte | Bloqueado | **Posible:** hay incendios urbanos e industriales (8.208) como indicador de capacidad de reporte, análogo al de la UNGRD; tendrá las mismas limitaciones |
| Ecuador | Bloqueado | Sin cambios |

### Lo que no se ha hecho
No se ha calculado ninguna relación. Falta: fijar el protocolo de cada prueba (no se puede mirar y luego decidir), unir con un catálogo de distritos (UBIGEO del INEI) que **aún no se ha obtenido**, y verificar en el diccionario completo el significado de las 49 columnas (solo se leyeron las primeras 25 filas).

## Actualización 3: insumos geográficos y de población para V1-Perú (2026-11-08)
Descargas autorizadas por el usuario; archivos fuera del repo.
| Archivo | Fuente | Tamaño | Notas |
|---|---|---:|---|
| `per_admin_boundaries.shp.zip` | OCHA COD-AB Perú (HDX), origen IGN, CC BY-IGO | 37.244.958 bytes (la página anunciaba 40,9 M) | Integridad del zip comprobada; niveles 0 a 3, líneas y puntos. El tamaño anunciado difiere del real; no se investigó por qué |
| `per_admin_boundaries.xlsx` | idem | 415.223 bytes | Atributos: 1.873 distritos con `adm3_pcode`, área en km², coordenadas del centro |
| Tabla INEI «población total proyectada al 30 de junio, 2018-2026» | INEI vía gob.pe (descargada por el usuario desde su navegador) | 212.580 bytes | 1.892 distritos con UBIGEO; «información de carácter referencial» (proyección, no censo) |

**Auditoría de unión (`scripts/regional/peru_auditoria_union.py`), sin ninguna asociación:**
- Los 1.871 distritos de SINPAD 2019-2024 existen todos en la tabla de población del INEI.
- **1.853 (99,0 %) tienen polígono.** Los 18 sin polígono son distritos posteriores a 2015 (los límites son de 2015); concentran **437 de 50.807 registros (0,86 %)** y se excluyen y se informan, como fija la enmienda 1.
- 1 polígono no tiene población INEI; 20 distritos del INEI no tienen polígono.
- Área total de los polígonos: 1.286.519 km² (orden de magnitud del territorio peruano; no se comparó con una cifra oficial).
- El código `adm3_pcode` es `PE` + UBIGEO de 6 dígitos y coincide con el de SINPAD.

Con esto la unión de datos del protocolo V1-Perú es viable. **Faltan** la red vial (OSM), el DEM y el HAND, y la compuerta de §4 completa.
