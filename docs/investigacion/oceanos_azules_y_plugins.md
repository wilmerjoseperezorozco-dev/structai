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

## 4. Cómo mejorar de forma iterativa
El ciclo que ya usamos: verificar el dato en vivo → protocolo preregistrado → línea base simple → comparación con alternativas → publicar también el resultado negativo → **conectar al chat solo lo que superó su criterio**, con su aviso y su fecha de datos.

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

**Orden sugerido:** 1, 5, 3 y 4 (rápidos y ya existentes), luego 2, que integra todo y es la base natural de una «ciudad inteligente». Los océanos azules (10 y 11) quedan condicionados a verificar datos.

## 6. Qué hace falta decidir
- ¿Se conectan primero los plugins rápidos (1, 5, 3, 4)?
- ¿Se hace la verificación de datos del SGC para sismicidad y agua subterránea antes de comprometer esfuerzo?
- Para el fracking, ¿se acepta el encuadre de línea base y monitoreo?
