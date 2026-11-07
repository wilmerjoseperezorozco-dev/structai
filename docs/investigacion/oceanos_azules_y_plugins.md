# Océanos azules del subsuelo y catálogo de plugins del chat

Documento de investigación, 2026-11-08. Separa lo verificado de lo que falta verificar. No contiene diseños operativos ni promete resultados.

## 1. ¿Todo esto es para que lo recupere el chat?

La arquitectura apunta ahí, pero hoy la conexión es parcial. El chat consulta tres tipos de cosas: el corpus normativo (RAG), los motores de cálculo (delegador) y bloques de datos en vivo que enriquecen la respuesta.

| Ya conectado al chat | No conectado todavía (existe en el repositorio) |
|---|---|
| Normativa NSR-10, NTC, RAS, INVIAS, Perú, Ecuador | Revisión de precios atípicos (`motor-apu`, con pruebas) |
| Motores: APU, estructural, AquAI, GeoPot, Vías, Gerencia, vulnerabilidad de vivienda | Recomendador de insumos para APU |
| Bloques: amenaza sísmica SGC, anomalía de caudal IDEAM, vulnerabilidad Sisbén, historial UNGRD, deforestación, microzonificación, noticias | Modelo de susceptibilidad a movimientos en masa |
| Servidor MCP con una sola herramienta de lectura (`consultar`) | Costo en riesgo con ICOCIV, coherencia de anomalías, sensibilidad a ENSO, registro de vigencia de normas |

Conclusión: lo que se crea como investigación **no llega solo al chat**. Para que lo recupere hay que convertirlo en un plugin con un contrato claro (sección 5).

## 2. Océano azul A: agua subterránea

**Lo verificado.**
- El Servicio Geológico Colombiano (SGC) tiene un programa de aguas subterráneas y estudió el acuífero de Morroa (Sucre) con un modelo conceptual y un pozo exploratorio ([GeoFlash SGC, 2015](https://www2.sgc.gov.co/Noticias/Documents/GeoFlash_13_03_2015.pdf)). Hay tesis sobre recarga artificial y caracterización geoestadística del mismo acuífero ([EAFIT](https://repository.eafit.edu.co/server/api/core/bitstreams/2dacaf7d-259e-4dea-a50b-c549b45cd1a8/content)).
- Para Atlántico y Bolívar solo encontré una síntesis de 1988 ([Boletín Geológico](https://granate.sgc.gov.co/index.php/boletingeo/article/download/212/178/192)).
- En datos abiertos (datos.gov.co) hay registros de **concesiones** de agua subterránea de algunas corporaciones autónomas regionales (Corpoboyacá, Corpourabá, Corantioquia), que son registros administrativos y no mediciones de nivel, caudal ni calidad. No apareció un conjunto hidrogeológico ni un catálogo de acuíferos.

**Por verificar:** si el SGC publica un visor o servicio de aguas subterráneas utilizable, y qué tiene la CRA del Atlántico. Sin datos de pozos con nivel y caudal no se puede validar ningún modelo.

**Problemas para aplicar relaciones de segundo orden (regresiones):**
- Los pozos se perforan donde se espera agua: **sesgo de selección**, no una muestra del acuífero.
- Heterogeneidad del subsuelo y pocos puntos: la interpolación (kriging) depende de pocos datos.
- Sin series de nivel no hay dinámica (tercer orden): la recarga depende de la lluvia y de ENSO, y ya tenemos lluvia (CHIRPS), suelos (IGAC) y geología (SGC) como variables explicativas.
- Intrusión salina cerca de la costa y subsidencia son relevantes en el Caribe, pero requieren mediciones.

## 3. Océano azul B: fracking y microsismicidad

**Contexto verificado (es un tema disputado).** Los pilotos Kalé y Platero, en Puerto Wilches (Santander), se aprobaron en 2020 y quedaron congelados antes de fracturar; las fuentes se contradicen sobre su estado actual y el debate político sigue abierto ([La República](https://www.larepublica.co/economia/fracking-lo-que-hereda-y-le-espera-al-gobierno-de-abelardo-de-la-espriella-4441514); [Portafolio](https://www.portafolio.co/economia/finanzas/fracking-en-colombia-suspenden-temporalmente-proyectos-piloto-564321)). No encontré informes del SGC sobre sismicidad inducida en esa zona (no es prueba de que no existan).

**Lo que dice la ciencia.**
- Los eventos inducidos potencialmente dañinos **no se pueden predecir con confianza antes de operar**, y los semáforos de control (protocolos de «luz de tráfico») aún no han demostrado ser confiables ([Nature Reviews Earth & Environment](https://link.springer.com/10.1038/s43017-020-0049-7)). Varios eventos de «luz roja» no tuvieron aviso previo o ocurrieron tras terminar la inyección ([Imperial College](https://spiral.imperial.ac.uk/entities/publication/e5591138-ca81-4e00-b7a7-bc04612fa012)).
- Los modelos de pronóstico pierden sensibilidad al volumen inyectado y fallan si un evento grande aparece pronto ([EGU 2019](https://meetingorganizer.copernicus.org/EGU2019/EGU2019-18415.pdf?pdf)).
- Se proponen modelos de aprendizaje automático para hacer los semáforos adaptativos, con dos problemas abiertos: no se distingue del todo un sismo natural de uno inducido, y el riesgo tras cerrar la inyección sigue difícil de manejar ([Frontiers, 2020](https://www.frontiersin.org/articles/10.3389/feart.2020.00227)).

**Lo que sí podríamos aportar, de interés público.**
1. **Línea base de sismicidad natural** del Magdalena Medio *antes* de cualquier operación: magnitud de completitud, valor b y agrupamiento en el tiempo. Es lo que permite, más adelante, separar lo natural de lo inducido.
2. Cruzar esa línea base con la amenaza sísmica de la NSR-10 para las estructuras cercanas.

**Lo que no haría.** Un motor que «optimice» el fracturamiento: faltan los datos de inyección (son del operador, no públicos), el tema es riesgoso para la seguridad y para la licencia social, y cualquier cifra sin esos datos sería inventada. Propongo encuadrarlo como **monitoreo y transparencia**, no como diseño de operación.

**Por verificar:** cómo se accede al catálogo de eventos de la Red Sismológica Nacional (en datos.gov.co no apareció) y su completitud en la zona.

**Problemas para segundo orden:** confusión entre sismicidad natural e inducida, catálogo incompleto a magnitudes bajas, pocos eventos, ausencia de datos de inyección y colas pesadas para la magnitud máxima.

## 3b. Océano azul C: ingeniería eléctrica

**Lo verificado.**
- Hay producción mensual de electricidad por fuente desde el año 2000 en datos abiertos (UPME, 2.786 filas) y ya extrajimos datos de XM (aportes hídricos, precio de bolsa) para la hipótesis 13.
- Resultado propio, 284 meses: por cada +1 °C del ONI los aportes hídricos bajan ×0,84 (IC −0,20 a −0,12 en log) y el precio de bolsa sube ×1,35 (IC +0,14 a +0,40). **Pero al añadir ENSO el pronóstico fuera de muestra empeora** (error 1,13 frente a 0,70): la relación existe y no es predictiva con esta forma simple. Es el mismo patrón que en las crecientes (H4).
- Contexto de 2026: XM reportó aportes al 60 % del promedio histórico y El Niño en formación; la generación depende en 60-80 % de la hidráulica ([Finance Colombia](https://www.financecolombia.com/el-nino-warming-patterns-signal-operational-risks-for-colombian-power-and-agriculture/); [Rio Times](https://www.riotimesonline.com/colombia-reservoirs-slip-as-wildfire-alerts-spread/)). Un estudio con VAR halla efecto significativo de los eventos extremos de ENSO sobre los precios de la electricidad, mayor cuando los precios ya están altos.

**Problemas para segundo orden:** endogeneidad entre demanda y precio; regulación (precio de escasez) que crea umbrales; rupturas estructurales; pocos ciclos de ENSO. Para «ciudad inteligente» (microrredes, respuesta de la demanda) hacen falta medidores inteligentes cuyos datos no son abiertos.

## 3c. Océano azul D: oceanografía y costa

**Lo verificado.**
- El conjunto «Nivel del Mar» del IDEAM en datos abiertos tiene **solo dos estaciones**: Tesoro-INVEMAR (Bolívar, 2012-2020, 194.733 observaciones) y Juanchaco (Pacífico, 2005-2020). No cubre Barranquilla y termina en 2020. Ocho años no bastan para una tendencia de nivel del mar.
- El Índice de Calidad de Aguas Marinas y Costeras (INVEMAR, 1.715 filas) incluye estaciones como Bocas de Ceniza (Atlántico).
- INVEMAR reporta las mayores tasas de erosión de origen humano del Caribe continental en Magdalena (5,3 m/año), Córdoba (3,3) y La Guajira (3,2) ([resumen FAO](https://agris.fao.org/search/es/records/67488e107625988a371d78df)); también hay estudios de la afectación por ascenso del nivel del mar ([INVEMAR](https://boletin.invemar.org.co/ojs/index.php/boletin/article/download/871/735/3920)).
- No encontré datos abiertos de oleaje, mareas ni batimetría. Los caudales del Magdalena sí están en nuestros datos del IDEAM.

**Problemas para segundo orden:** pocas estaciones y series cortas; la línea de costa se puede medir por satélite (Sentinel-2, Landsat) pero requiere un protocolo propio; el oleaje y las tormentas (tercer orden) no tienen datos abiertos; los espigones del Magdalena confunden la tendencia natural.

## 3d. Océano azul E: composición del suelo

**Lo verificado.** Tenemos 169.088 unidades de suelo del IGAC en la base. SoilGrids (global, 250 m) explica en promedio cerca del 61 % de la variación en su validación, sin validación local para Colombia que yo haya encontrado, y es grueso para el trabajo geotécnico de un sitio ([SoilGrids250m](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5313206/)).

**Un estudio de segundo orden realizable con lo que ya tenemos:** ¿se puede predecir la clase de sitio de la NSR-10 (A a F) a partir de las capas de suelo? La validación existe: las microzonificaciones de Bogotá, Cali y Pereira dan la clase y la velocidad de onda de corte. Es un problema acotado, con verdad de referencia y con un plugin natural (clase de suelo estimada con su incertidumbre).

**Problemas:** los estudios de suelos de obra son privados; la textura no equivale a las propiedades geotécnicas (SPT, Vs30); la resolución de 250 m no ve la variación a escala de lote.

## 3e. Océano azul F: ecología evolutiva y biodiversidad

**Lo verificado.** SiB Colombia es el nodo nacional de GBIF, con millones de registros de presencia en acceso abierto con licencias Creative Commons ([GBIF](https://www.gbif.org/news/82303/colombia-launches-new-national-biodiversity-data-portal)); en 2026 reportó 2.940.251 registros publicados en dos años con el sector privado. En datos.gov.co hay el listado oficial de especies silvestres amenazadas (Ministerio de Ambiente) y conjuntos de fauna y flora de algunas corporaciones regionales. No encontré aplicaciones de evaluación de impacto ni de ecología evolutiva con estos datos.

**Por qué importa a la ingeniería civil:** licenciamiento ambiental y conectividad ecológica de vías.

**Problemas para segundo orden:** los registros de presencia se concentran donde hay gente y carreteras (sesgo de muestreo), faltan los datos de ausencia, y los modelos de distribución (de presencia sola) son frágiles. La parte «evolutiva» (diversidad filogenética, endemismo) necesita árboles filogenéticos que no verifiqué como abiertos: **es una expedición**, no un paso inmediato. Conecta con el proyecto de conservación del tití cabeciblanco del Atlántico.

## 4. Cómo mejorar de forma iterativa
El ciclo que ya usamos: verificar el dato en vivo → protocolo preregistrado → línea base simple → comparación con alternativas → publicar también el resultado negativo → **conectar al chat solo lo que superó su criterio**, con su aviso y su fecha de datos.

**Una lección que se repite en tres dominios.** Las crecientes (H4), la energía (H13) y, en menor medida, el costo de obra muestran el mismo patrón: la relación con ENSO existe dentro de la muestra pero un modelo simple con ENSO **no mejora el pronóstico fuera de muestra**. Antes de abrir más océanos conviene resolver eso (ventanas, rezagos, agrupación por región, validación hacia adelante), porque cada océano nuevo heredará el mismo problema.

**Datos limitantes de cada océano:** acuíferos (sin series de nivel), microsismos (catálogo sin acceso verificado y sin datos de inyección), electricidad (sin medidores inteligentes abiertos), costa (dos estaciones de nivel del mar), suelos (sin estudios de obra), biodiversidad (solo presencia).

## 5. Catálogo de plugins candidatos

**Contrato mínimo de cualquier plugin:** entrada con esquema, función determinística (el modelo de lenguaje solo explica, nunca calcula), fuente y fecha de los datos, límites declarados, aviso de responsabilidad y pruebas. Tipos: **dato** (consulta en vivo), **motor** (cálculo), **skill** (flujo que combina varios), **corpus** (texto indexado), **externo** (integración con otro sistema).

| # | Plugin | Tipo | Qué responde | Estado | Esfuerzo | Riesgo / condición |
|---|---|---|---|---|---|---|
| 1 | Fase de ENSO y qué implica en su región | dato | «¿Viene un periodo más lluvioso en mi zona?» | Mapa de sensibilidad y ONI existen | Bajo | Rotular como señal estadística |
| 2 | **Informe de sitio** (municipio) | skill | Amenaza sísmica, microzonificación, suelos, susceptibilidad, caudales, ENSO, emergencias | Piezas existen, falta integrarlas | Medio | Cada bloque con su límite; en el Caribe la susceptibilidad es débil |
| 3 | Revisión de precios | motor | «¿Este precio es razonable?» | Módulo y pruebas existen | Bajo | Sensibilidad 0,64 ante ×10: no es detector de errores de unidad |
| 4 | Recomendador de insumos | motor | «¿Qué insumos faltan en mi APU?» | Existe | Bajo | acierto@10 de 0,84 |
| 5 | Vigencia de normas | dato | «¿Esta norma sigue vigente y qué la modificó?» | Registro de 64 normas en la base | Bajo | Cadenas tomadas de resúmenes web, no de textos oficiales |
| 6 | Costo en riesgo del presupuesto | skill | «¿Cuánto puede subir mi obra en 6-12 meses?» | Resultados existen | Medio | Requiere actualizar el ICOCIV cada mes; no es pronóstico |
| 7 | Susceptibilidad por punto | dato | «¿Qué tan susceptible es este lugar?» | Modelo existe | Medio | Hay que publicar sus límites regionales |
| 8 | Estado regional de caudales | dato | «¿Hoy hay anomalías coherentes en mi región?» | Resultados de coherencia existen | Medio | Depende de refrescar el IDEAM (issue #71) |
| 9 | Costo paramétrico de pavimento | motor | Costo por m² por tránsito y subrasante | **Bloqueado** por el issue #103 | Bajo | No conectar hasta corregir las unidades |
| 10 | Sismicidad reciente y línea base | dato | «¿Qué sismos hubo cerca de este sitio?» | No hay acceso verificado | Alto | Verificar el servicio del SGC primero |
| 11 | Agua subterránea | dato | «¿Hay un acuífero en esta zona?» | No hay datos verificados | Alto | Solo concesiones por corporación regional |
| 12 | WhatsApp, ERP, Excel, Revit | externo | Consultas desde el celular o el sistema de costos | Issues #79 y #80 | Alto | Revit/BIM es el diferenciador de los competidores |
| 13 | Servidor MCP ampliado | externo | Exponer más herramientas a asistentes de IA | Prototipo con una herramienta | Medio | Control de uso y costo |
| 14 | Riesgo energético para la obra | skill | «¿Hay riesgo de racionamiento o de precios altos de energía este año?» | Datos de XM y UPME ya los usamos | Medio | La relación con ENSO es real pero no predictiva fuera de muestra; presentar como contexto |
| 15 | Clase de sitio NSR-10 estimada | motor | «¿Qué clase de suelo (A-F) es probable aquí?» | Falta el estudio de validación contra microzonificaciones | Medio-alto | Solo con incertidumbre explícita; no sustituye el estudio de suelos |
| 16 | Fauna amenazada cerca de la obra | dato | «¿Hay especies amenazadas registradas cerca del proyecto?» | Acceso a SiB/GBIF por verificar | Medio | Registros de presencia con sesgo; es una revisión previa, no un estudio de impacto |
| 17 | Costa: erosión y nivel del mar | dato | «¿Qué tan expuesta está esta costa?» | Datos abiertos muy limitados | Alto | Prioridad baja hasta tener datos |

**Orden sugerido:** 1, 5, 3 y 4 (rápidos y ya existentes), luego 2, que integra todo y es la base natural de una «ciudad inteligente». Los océanos azules (10 y 11) quedan condicionados a verificar datos.

## 6. Qué hace falta decidir
- ¿Se conectan primero los plugins rápidos (1, 5, 3, 4)?
- ¿Se hace la verificación de datos del SGC para sismicidad y agua subterránea antes de comprometer esfuerzo?
- Para el fracking, ¿se acepta el encuadre de línea base y monitoreo?

## 7. Estado de conexión al chat (2026-11-08)

| Plugin | Estado |
|---|---|
| 1. Fase de ENSO y qué implica en su región | **Conectado** |
| 2. Informe de sitio | **Conectado** (reúne los bloques de datos oficiales del municipio, la susceptibilidad, el contexto de ENSO y los títulos de la NSR-10 a consultar; funciona aunque el modelo de lenguaje esté caído) |
| 3. Revisión de precios | **Conectado** |
| 4. Recomendador de insumos | **Conectado** (sugerencia por vecinos si se nombran insumos; si no, composición de la actividad INVIAS más parecida) |
| 5. Vigencia de normas | **Conectado** |
| 7. Susceptibilidad | **Conectado a escala de municipio**, con el mapa oficial del SGC y un índice relativo que se omite en las regiones donde no concuerda con ese mapa (ver `scripts/satelite/RESULTADOS_SUSCEPTIBILIDAD_MUNICIPAL.md`) |
| 6. Costo en riesgo, 8. Estado regional de caudales | Pendientes |
| 9. Costo paramétrico de pavimento | **No conectar**: corregido el error de unidades (#103), pero el rígido y la política de espesores siguen sin verificar (#106) |
| 10, 11, 14-17 | Sin datos verificados o prioridad baja |
