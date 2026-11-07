# Protocolo de análisis: relieve y reportes de inundación en el Caribe colombiano

Issue #95 (Frente C), 2026-11-06. **Se fija antes de correr cualquier prueba predictor–resultado.** Si algo cambia después, se anota como desviación con su motivo.

## 1. Preguntas, en orden

1. ¿Qué está pasando? (descriptiva: `auditar_datos_caribe.py`)
2. ¿Dónde están los extremos?
3. ¿Cuál es la variabilidad real? (con intervalos, no solo medias)
4. ¿Qué variables tienen poder explicativo, y cuánto, descontando confusión y colinealidad?

## 2. Modelo causal supuesto (DAG en texto)

- **Y\*** (lo que observamos) = proporción de inundación en los reportes UNGRD del municipio.
- **Y** (lo que queremos entender) = ocurrencia real de inundaciones.
- **R** = capacidad de reportar (institucional, urbana).
- Relaciones asumidas: `relieve bajo → Y`; `Y → Y*`; `R → Y*`; `tamaño/urbanización → R`; `tamaño/urbanización → exposición → Y*` (más gente afectada, más reporte).
- **Consecuencias de diseño:**
  - El total de reportes **contiene** los eventos de inundación (Y\*): controlar por él es condicionar por una consecuencia del resultado (riesgo de sesgo de colisionador). **No se usa como control principal**, y se corrige un error de mi diseño anterior.
  - Los reportes de *otros* eventos también dependen del relieve (movimientos en masa en zonas empinadas): tampoco son un control limpio.
  - El mejor control disponible de R es el tamaño de la población registrada (Sisbén, `n_viviendas_muestra`), con la limitación de que cubre solo población registrada.

## 3. Roles de las variables

| Rol | Variable | Justificación |
|---|---|---|
| **Primaria (única confirmatoria)** | Fracción del municipio bajo 10 m (DEM) | Hipótesis física directa; elegida antes de ver resultados |
| Secundarias (con Holm) | Elevación media (invertida); fracción de área inundable según IGAC | Mismo concepto con otra medición / otra fuente: sirven como chequeo, no como pruebas independientes |
| **No entran juntas** | Pendiente media, p90, rango de elevación, fracción pendiente > 15 % | Colineales con el relieve; se usan solo de una en una para la pregunta de movimientos en masa |
| Control / confusión | Tamaño poblacional proxy (Sisbén), área del municipio | Causas comunes de reporte y de exposición |
| **Excluidas como control** | Total de reportes; reportes no inundación | Contienen el resultado o dependen del relieve |
| Estratificación (no control) | Departamento | Bloque de replicación; evita que un departamento domine |
| Descriptivas | Textura y drenaje dominante del suelo | Solo para describir; no se prueban |

Criterio general: seleccionar por **causalidad y plausibilidad física**, no por significancia ni por ajuste. Se sigue el criterio de causa disyuntiva de VanderWeele y Shpitser (controlar los que causan la exposición, el resultado o ambos) con las advertencias de VanderWeele (2019) sobre sus excepciones; se evita la "falacia de la Tabla 2" de Westreich y Greenland (2013): **solo se interpreta el coeficiente de la variable primaria**, no los de los controles. Los trabajos se localizaron por búsqueda; no se leyó su texto completo.

## 4. Análisis confirmatorio

- **Resultado:** proporción de inundación; solo municipios con ≥ 10 reportes (los demás no distinguen "sin inundaciones" de "sin capacidad de reportar").
- **Estimador:** correlación de Spearman con **intervalo de confianza por remuestreo de departamentos** (bloques), **correlación parcial** controlando por el tamaño poblacional proxy, y **tamaño de efecto** con su IC. Se reporta p solo como complemento.
- **Curva de especificaciones:** el mismo estimador bajo controles alternativos (ninguno, población proxy, área, ambos, total de reportes, no-inundación). Si la conclusión cambia con el control, el hallazgo **no es robusto** y se dice así; no se escoge la especificación favorable.
- **Replicación por bloque:** signo y magnitud en cada departamento y "dejar un departamento fuera".
- **Multiplicidad:** Holm sobre las secundarias.

## 5. Validación

- **Unidad independiente = departamento** (7 bloques). Con 7 bloques el IC será muy ancho: se reporta tal cual.
- **Validación espacial por bloques** para cualquier modelo predictivo. Hay debate real: Roberts et al. (2017) y Ploton et al. (2020) muestran que la validación aleatoria infla el desempeño con datos autocorrelacionados, mientras que Wadoux et al. (2021) sostienen que la validación espacial tiene su propio sesgo y depende del diseño de muestreo. **Decisión:** para *extrapolar a regiones nuevas* se usa validación por bloques; para *describir asociaciones dentro de la región* se usa inferencia robusta a la dependencia (bootstrap por bloques) y se informa el I de Moran.
- **Periodo reservado:** reportes de 2024 como prueba temporal para cualquier modelo predictivo; 2022 se analiza aparte (año extremo).
- **Incertidumbre además de exactitud:** calibración (Brier) y cobertura de intervalos, no solo acierto.

## 6. Potencia

Calculada por simulación (`auditar_datos_caribe.py`, sección 8). Es un **piso optimista**: con dependencia espacial la potencia real es menor. Un resultado nulo solo descarta asociaciones por encima del |ρ| mínimo detectable.

## 7. Limitaciones conocidas de antemano

UNGRD mide reportes, no inundaciones. DEM = superficie, 30 m. Polígonos IGAC simplificados y generalizados. Un análisis ecológico (municipios) no autoriza conclusiones sobre individuos o predios. Los municipios sin reportes no son "sin amenaza".

## 8. Enmiendas previas al análisis confirmatorio (2026-11-06, tras la auditoría; antes de ver ninguna asociación predictor–resultado)

La auditoría (`auditoria/auditoria_datos_caribe.md`) mostró problemas de diseño. Se corrigen **antes** de correr el cruce:

1. **El resultado "proporción de inundación" se abandona como principal.** Su denominador (todos los reportes) está dominado por incendios (22–77 % por año, incluidos estructurales urbanos), cuya frecuencia depende de la capacidad de respuesta y de la urbanización, no de la amenaza de inundación. **Resultado principal nuevo:** eventos de inundación por 100 000 habitantes (población DANE 2020). La proporción queda como sensibilidad.
2. **No se excluyen municipios por tener pocos reportes en el análisis principal**: el total de reportes contiene el resultado y excluir por él es seleccionar sobre una consecuencia del resultado. La exclusión de "zonas mudas" (< 10 reportes) pasa a sensibilidad.
3. **Duplicados:** 975 filas extra de UNGRD con claves idénticas (255 sin datos numéricos; 446 son inundaciones). No se puede saber si son duplicados o eventos repetidos legítimos. Resultado principal con el conteo crudo (tal como lo da la fuente); **sensibilidad con duplicados colapsados**. Una conclusión que cambie entre ambos no es robusta.
4. **Controles:** logaritmo de la población y del área; curva de especificaciones con y sin porcentaje en cabecera; la especificación con el total de reportes se muestra solo para ilustrar su sesgo.
5. **Advertencia sobre el predictor principal:** la fracción < 10 m tiene mediana 0 (muchos empates) y un umbral absoluto de elevación no es físicamente apropiado para llanuras de inundación del interior (p. ej. Cesar, valle a más de 100 m). **No se cambia el predictor principal declarado**; se reporta con esta limitación y se deja como trabajo siguiente la altura sobre el cauce más cercano derivada del DEM.
6. **Regla de veredicto fija:** "asociación" solo si el IC por bloques (departamentos) de la correlación parcial principal excluye 0; "robusta" solo si el signo y la exclusión de 0 se mantienen en todas las especificaciones de la curva (excepto la ilustrativa). En otro caso se informa como no robusta.


## 9. Segundo predictor: altura sobre el cauce más cercano (HAND), definido ANTES de calcular asociaciones (2026-11-06)

Motivo: la fracción < 10 m no es física para llanuras del interior (sección 8.5) y dio un nulo. HAND (altura sobre el drenaje más cercano) es la medida estándar de "dónde el terreno está al alcance del agua de un cauce".

- **Cálculo:** DEM Copernicus GLO-30 agregado a ~90 m (3 arcsegundos) **por departamento** (con 0,15° de margen, para no cortar cuencas en la frontera); océano (elevación exactamente 0) como sin dato; relleno de depresiones y planos; dirección de flujo D8; acumulación; red de drenaje = celdas con área aguas arriba ≥ umbral.
- **Predictor confirmatorio-2 (único):** fracción del municipio con HAND < 10 m, red de **5 km²**. Fijado aquí.
- **Sensibilidad (no confirmatoria):** umbrales de red de 1 y 25 km²; cortes HAND < 5 y < 15 m; HAND mediana.
- **Estatus honesto:** se propone **después** de ver un resultado nulo, así que es **exploratorio con respecto al análisis anterior** aunque la definición se fije antes de verlo. Se reporta con las mismas reglas (correlación parcial, IC por bloques, controles principales, regla de veredicto) y se compara contra el predictor anterior; no se presenta como "confirmación".
- **Limitaciones:** resolución 90 m (el DEM es de superficie); el umbral de red es una elección; municipios en la costa y ciénagas tienen áreas sin dato.


## 10. El "cuándo": precipitación mensual (CHIRPS v3.0) y reportes de inundación, definido ANTES de correrlo (2026-11-06)

Motivo: HAND explica *dónde*, y solo en el año de lluvias extremas (sección 9). La pregunta siguiente es si la lluvia explica *cuándo* se reporta una inundación y si el efecto depende de HAND.

- **Unidad:** municipio-mes, 195 × 72 (2019-01 a 2024-12).
- **Resultado:** al menos un reporte de inundación (UNGRD) en el mes (0/1). Sin dependencia del conteo ni de los duplicados.
- **Predictor:** anomalía estandarizada de la precipitación mensual dentro de cada municipio (z con su propia media y DE de 2019-2024). Es relativa al clima local, no absoluta.
- **Estimador por municipio:** AUC de la anomalía para distinguir meses con inundación de meses sin ella; solo municipios con ≥ 3 meses con inundación y ≥ 12 sin ella.
- **Resumen:** AUC medio entre municipios con IC95 % por remuestreo de **departamentos**; fracción de municipios con AUC > 0,5.
- **Moderador (confirmatorio-3):** correlación de Spearman entre el AUC municipal y la fracción con HAND < 10 m (red 5 km²), con IC por bloques. Hipótesis: la lluvia predice mejor los reportes donde el terreno es bajo respecto al cauce.
- **Regla fija:** "la lluvia discrimina" solo si el IC del AUC medio excluye 0,5; "HAND modera" solo si el IC de la correlación excluye 0.
- **Estatus:** el efecto de la lluvia es una hipótesis física fuerte y casi previsible; la parte informativa es el tamaño del AUC y la moderación por HAND (exploratoria).
- **Limitaciones:** CHIRPS a ~5 km (municipios pequeños quedan con 1-3 píxeles); precipitación mensual no captura crecientes de horas; los reportes UNGRD dependen de la capacidad de reportar (se mitiga comparando cada municipio consigo mismo).


## 11. Hipótesis fluvial: caudal de estaciones IDEAM vs lluvia local (definido ANTES de correrlo, 2026-11-06)

Hipótesis (propuesta para explicar el signo contrario de la sección 10): en municipios con mucho terreno bajo respecto al cauce (HAND), los reportes de inundación siguen la anomalía del **caudal de un río cercano** mejor que la **lluvia local del mes**.

- **Datos:** `ideam_caudal_historico` (valores mensuales por estación), estaciones del Caribe por coordenadas (no por nombre de departamento). Se usa 2019-2024, mismo panel municipio-mes de la sección 10.
- **Estación por municipio:** la estación más cercana al polígono municipal, a ≤ 25 km (sensibilidad: 50 km), con ≥ 48 meses con dato en 2019-2024. Sin escoger la que mejor funcione.
- **Predictor fluvial:** anomalía z del caudal mensual respecto de la propia estación (media y DE de sus meses disponibles).
- **Comparación pareada por municipio:** AUC de la anomalía de caudal menos AUC de la anomalía de lluvia, **en los mismos meses** (solo meses con dato de caudal), con los mismos criterios de elegibilidad de la sección 10 (≥ 3 meses con inundación y ≥ 12 sin ella dentro de esos meses).
- **Prueba principal:** correlación de Spearman entre la fracción con HAND < 10 m y la diferencia de AUC (caudal − lluvia); hipótesis: **positiva**. IC95 % por remuestreo de departamentos.
- **Secundarias:** diferencia media de AUC en el tercil bajo y en el alto de HAND; AUC medio del caudal.
- **Regla fija:** "hipótesis fluvial apoyada" solo si el IC de la correlación principal excluye 0 **y es positivo**. Si es negativo o incluye 0, no se apoya.
- **Limitaciones declaradas:** la cercanía geográfica no garantiza conexión hidrológica (no se verifica que la estación esté aguas arriba del municipio); series mensuales (no captan crecientes de horas); cobertura de estaciones decreciente; la mayoría de estaciones está en cauces medianos y pequeños, no en el cauce principal.


## 12. Hipótesis 1: clima y retrasos de obra (SECOP II + CHIRPS), definida ANTES de correrla (2026-11-06)

**Pregunta:** ¿la lluvia anómala durante la ejecución de un contrato de obra se asocia con prórrogas y suspensiones?

- **Unidad:** contrato de obra de una **alcaldía** de los 7 departamentos del Caribe, con la ciudad resuelta a un municipio de los 195 (vía DIVIPOLA), inicio entre 2020-01 y 2024-12 y ventana planeada dentro de 2024-12. Se excluyen estados no iniciados o sin resultado final ('En ejecución', 'Aprobado', 'En aprobación', 'enviado Proveedor'). Las alcaldías se eligen porque el sitio de obra coincide, con alta probabilidad, con la ciudad; en gobernaciones y entidades nacionales la "ciudad" es la de la entidad.
- **Ventana de exposición:** desde la fecha de inicio hasta inicio + duración declarada (no se usa la fecha de fin, que puede ya incluir prórrogas; en el 49 % de los contratos fin − inicio ≈ duración).
- **Exposición principal:** anomalía de precipitación mensual (CHIRPS) respecto de la media del **mismo mes calendario** del municipio (2019-2024), promediada sobre los meses de la ventana y estandarizada (1 DE = 1 unidad). Elimina la estacionalidad. **Sensibilidad:** z sin quitar la estacionalidad; máximo mensual de la ventana.
- **Resultado principal:** prórroga = `dias_adicionados` > 0. **Secundario:** al menos una suspensión (tabla de adiciones).
- **Modelo:** regresión logística con controles log(valor del contrato), log(duración en días), año de inicio y departamento. Efecto = razón de momios por +1 DE de exposición; **IC 95 % por remuestreo de municipios** (clústeres).
- **Regla fija:** "asociación" solo si el IC excluye 1. Se informa n, eventos y la razón de momios mínima detectable (potencia 80 %, aproximación de Wald).
- **Limitaciones declaradas:** muestra pequeña; las prórrogas tienen muchas causas (cambio de alcance, falta de recursos); datos autorreportados y fechas inconsistentes; la lluvia de CHIRPS es de ~5 km y mensual; una asociación no establece causalidad.


### 12b. Enmienda por potencia insuficiente: extensión a todo el país (2026-11-06)

El piloto del Caribe quedó **inconcluyente**, no nulo: 306 contratos en solo 20 municipios, RM 1,02 [0,73; 1,75] y razón de momios mínima detectable de 1,39. La extensión a Colombia continental (CHIRPS 1.120 municipios, 32 departamentos) se decide **por falta de potencia, no por la dirección del resultado**. Diseño idéntico a la sección 12; solo cambia el ámbito. El análisis principal pasa a ser el nacional; el del Caribe se conserva como piloto (`clima_retrasos_obras_caribe.json`). Se usa `scripts/secop/clima_retrasos_obras.py colombia`.


### 12c. Mejora del límite "ciudad de la entidad ≠ sitio de obra" (2026-11-06)

El resultado nacional restringido a alcaldías es informativo (RM 1,00 [0,84; 1,17], n = 2.522, MDE 1,13), pero descarta 39.884 contratos de otras entidades. Se usa la **ubicación de ejecución** de SECOP II (`gra4-pcp2`, solo `id_contrato` y `localizaci_n`; proveedor no descargado) para incluir todas las entidades. **Regla:** solo contratos con **exactamente un** municipio de ejecución; el resto del diseño (ventana, exposición, controles, regla de veredicto) es el de la sección 12. Se reporta junto al resultado de alcaldías; una conclusión que cambie entre ambos no es robusta. Se corre con `clima_retrasos_obras.py colombia ubicacion`.


## 13. El Niño y la energía eléctrica: hidrología y precio de bolsa (XM + ONI), definido ANTES de correrlo (2026-11-06)

**Pregunta:** ¿el ENSO (índice ONI) mueve los aportes hídricos y el precio de bolsa de la energía en Colombia, y es **asimétrico** (El Niño ≠ La Niña)?

- **Datos (mensuales, 2000-01 a 2026-10):** XM (API pública) `AporEner` y `AporEnerMediHist` (aportes de energía y su media histórica), `PPPrecBolsNaci` (precio de bolsa nacional ponderado diario, COP/kWh) y `PorcVoluUtilDiar` (volumen útil, descriptivo); ONI de NOAA CPC (mes central de cada trimestre móvil; NDJ del año Y se centra en dic. de Y−1); IPC total del DANE para deflactar a pesos de septiembre de 2026.
- **Variables:** `y_aportes` = log(media mensual de AporEner / media mensual de AporEnerMediHist); `y_precio` = log(precio de bolsa mensual medio × IPC_sep2026 / IPC_mes); `x` = ONI del mismo mes (la serie ya es una media móvil de 3 meses). **Rezagos 1, 2 y 3 meses: solo descriptivos**, no confirmatorios.
- **Controles (principales):** 11 variables de mes calendario y tendencia temporal lineal y cuadrática. **Robustez:** añadir log del WTI mensual (FRED, proxy del costo de combustibles de la generación térmica).
- **Estimador:** MCO con errores robustos a autocorrelación (Newey-West, 12 rezagos) y **IC95 % por bootstrap de bloques móviles de 12 meses** (5.000 réplicas); la inferencia es el bootstrap.
- **Confirmatorio 1 (hidrología):** β de `x` en `y_aportes` es **negativo** y su IC excluye 0.
- **Confirmatorio 2 (precio):** β de `x` en `y_precio` es **positivo** y su IC excluye 0; efecto reportado como % de cambio por +1 °C de ONI.
- **Confirmatorio 3 (asimetría):** `y_precio` ~ ONI⁺ (= máx(ONI, 0)) + ONI⁻ (= mín(ONI, 0)); se reporta la diferencia de magnitudes |β⁺| − |β⁻| con IC de bloques. Hipótesis nula: simetría.
- **Validación temporal reservada:** ajustar con 2000-2018 y evaluar en 2019-2026 el error absoluto medio de `y_precio` con y sin ONI (con el mismo conjunto de controles); "ENSO aporta" solo si **el error baja** en el periodo reservado.
- **Regla fija:** "ENSO afecta el precio de bolsa" solo si se cumplen el confirmatorio 2 **y** la mejora en el periodo reservado. Si el confirmatorio 1 falla, no se afirma el mecanismo hidrológico aunque haya correlación con el precio.
- **Descriptivo adicional:** tabla por episodio de El Niño (ONI ≥ +0,5 durante ≥ 5 trimestres consecutivos): pico del precio real frente a la media de los 12 meses previos.
- **Limitaciones declaradas:** ~320 meses pero **pocos episodios independientes de ENSO** (la inferencia efectiva es mucho menor que n); cambios regulatorios y de mercado (p. ej. cargo por confiabilidad, entrada de nuevas plantas, Hidroituango) alteran el nivel y no se modelan; el precio de bolsa depende del gas y de la demanda, no solo de la hidrología; el IPC total deflacta con un índice que mezcla componentes; las cifras recientes de XM y del DANE son provisionales.


## 14. Hipótesis fluvial con verificación aguas arriba (red de drenaje), definida ANTES de correrla (2026-11-06)

Mejora del límite de la sección 11: "la cercanía geográfica no garantiza conexión hidrológica".

- **Conexión hidrológica:** para cada estación IDEAM con ≥ 48 meses de caudal (2019-2024) se ubica su celda en el DEM de ~90 m del departamento (el mismo de HAND), **ajustada a la celda de mayor área acumulada en un radio de 3 celdas** (≈ 270 m), y se sigue el flujo D8 río abajo. Una estación está **conectada** con un municipio si esa ruta pasa por el polígono municipal. La ruta termina en el mar/sin dato, en el borde de la cuadrícula del departamento o en un sumidero. Los pares cuya ruta sale de la cuadrícula **antes** de llegar al municipio son **indeterminados** y se reportan aparte, no se cuentan como "no conectados".
- **Fiabilidad de la ubicación:** se registra el área acumulada de la celda ajustada; si es < 5 km² se marca "no está sobre un cauce resuelto".
- **Estación asignada (principal):** para cada municipio, la estación **conectada más cercana** (distancia al polígono) a ≤ 100 km. Sin estación conectada → excluido del principal.
- **Estadístico:** el mismo de la sección 11: correlación de Spearman entre la fracción con HAND < 10 m y (AUC del caudal − AUC de la lluvia en los mismos meses); IC95 % por remuestreo de departamentos; mismos criterios de elegibilidad (≥ 3 meses con inundación y ≥ 12 sin ella).
- **Comparación pre-declarada:** contra el resultado de la sección 11 (estación más cercana sin verificar conexión: ρ = +0,41 [+0,06; +0,57] a 25 km).
- **Regla fija:** "reforzada" si el IC del principal excluye 0 **y** el ρ es ≥ al de la sección 11; "debilitada" si el IC incluye 0 o el ρ es menor; "insuficiente" si hay < 30 municipios elegibles. También se reporta el estimado de los pares **no conectados** (si hay ≥ 15) como contraste.
- **Limitaciones declaradas:** DEM de superficie a 90 m; ajuste de la estación a la red es una elección y puede caer en un cauce vecino; las cuadrículas son departamentales con margen de 0,15°, así que la conexión entre departamentos queda indeterminada si la ruta sale de la cuadrícula; solo ~68 estaciones utilizables; un caudal medido en un tramo no es el que inunda un municipio aguas abajo (atenuación, afluentes).


## 15. Mapa de sensibilidad de la lluvia a El Niño y La Niña, 1981-2024 (CHIRPS v3.0 + ONI), definido ANTES de correrlo (2026-11-07)

**Pregunta:** ¿cómo responde la lluvia mensual de cada municipio de Colombia a El Niño y a La Niña, es **asimétrica**, y varía por región natural?

- **Datos:** CHIRPS v3.0 mensual, 1.120 municipios (polígonos IGAC), 1981-01 a 2024-12 (528 meses); ONI de NOAA CPC (mes central de cada trimestre móvil).
- **Anomalía:** por municipio y por mes calendario, z = (lluvia − media del mes) / DE del mes, con media y DE de 1981-2024. Quita la estacionalidad.
- **Predictores:** `NIÑO = máx(ONI, 0)` y `NIÑA = máx(−ONI, 0)`. Modelo por municipio: z = a + δ·NIÑO + γ·NIÑA. **δ < 0** significa que El Niño seca; **γ > 0** significa que La Niña moja. **Rezago principal: 0** (el ONI ya es una media de 3 meses); rezagos 1-3 solo descriptivos.
- **Asimetría:** |δ| − |γ| (> 0: El Niño pesa más que La Niña).
- **Regiones** (por departamento): Caribe (08, 13, 20, 23, 44, 47, 70); Andina (05, 11, 15, 17, 25, 41, 54, 63, 66, 68, 73); Pacífica (19, 27, 52, 76); Orinoquía (50, 81, 85, 99); Amazonía (18, 86, 91, 94, 95, 97).
- **Inferencia:** bootstrap de bloques móviles de 12 meses (2.000 réplicas), remuestreando el **mismo** índice de tiempo para todos los municipios; las regiones se evalúan sobre la serie z media regional.
- **Confirmatorios por región:** R1: δ < 0 con IC que excluye 0. R2: γ > 0 con IC que excluye 0. R3: IC de |δ| − |γ| que excluye 0 (asimetría).
- **Validación temporal reservada:** ajuste 1981-2010, prueba 2011-2024; R² fuera de muestra = 1 − SSE(modelo) / SSE(climatología) sobre la serie regional, con IC de bloques. "ENSO explica la lluvia de la región" solo si **(R1 o R2) y R² fuera de muestra > 0 con IC que excluye 0**.
- **Mapas:** δ, γ y |δ| − |γ| por municipio, y máscara de los municipios cuyo IC (bloques) excluye 0. **Significancia de campo:** se reporta la fracción de municipios marcados; con 5 % esperable por azar, y municipios vecinos comparten píxeles de CHIRPS (la fracción NO equivale a pruebas independientes).
- **Descriptivo:** desviación % de la lluvia regional respecto de su climatología durante cada episodio (ONI ≥ +0,5 o ≤ −0,5 durante ≥ 5 meses consecutivos).
- **Limitaciones declaradas:** ≈ 11 episodios de cada fase (inferencia efectiva mucho menor que 528 meses); CHIRPS es un producto satelital con estaciones y su calidad en los años 80 es menor; resolución ~5 km; el ONI resume el Pacífico central y no captura el Atlántico/Caribe; correlación espacial entre municipios; no se modelan otras oscilaciones (p. ej. MJO, NAO).


## 16. Contraste del relieve y de SIMMA con el Mapa Nacional de Amenaza por Movimientos en Masa del SGC (1:100.000), definido ANTES de correrlo (2026-11-07)

**Pregunta:** ¿el relieve del DEM (y la densidad de inventario SIMMA) concuerda, por municipio, con la amenaza que publica el SGC? Es una referencia independiente del piloto de susceptibilidad (que solo contaba con puntos SIMMA).

- **Datos:** SGC, capa `Municipios_100K` (1.122 municipios): porcentaje de área en amenaza baja/media/alta/muy alta. **Índice SGC = % alta + % muy alta.** Se excluyen municipios con categoría `SIN` o `CD`. DEM: 195 municipios del Caribe ya calculados (`dem_poligonos_caribe.json`). SIMMA: puntos del inventario dentro del polígono municipal, por 100 km².
- **Confirmatorios (Spearman, IC95 % bootstrap de bloques por departamento, 2.000 réplicas):**
  - **C1:** ρ(pendiente p90 del DEM, índice SGC) > 0 con IC que excluye 0.
  - **C2:** ρ(densidad SIMMA, índice SGC) > 0 con IC que excluye 0.
  - **C3:** el índice SGC aporta sobre la pendiente: ρ parcial(densidad SIMMA, índice SGC | pendiente p90) > 0 con IC que excluye 0.
- **Descriptivo:** concordancia de terciles; municipios con mayor desacuerdo (rangos).
- **Limitaciones declaradas:** el mapa SGC es un modelo (no observación) y posiblemente usa pendiente como insumo, por lo que C1 es parcialmente circular: se interpreta como **consistencia**, no como validación; SIMMA tiene sesgo de reporte/acceso; municipios planos del Caribe tienen poca variación (rango restringido); DEM a ~90 m frente a escala 1:100.000; el análisis es municipal (falacia ecológica).


## 17. Extensión nacional del contraste con el SGC (§16), definida ANTES de correrla (2026-11-07)

**Pregunta:** ¿lo observado en el Caribe (relieve y SIMMA concuerdan con el mapa de amenaza del SGC) se sostiene en los ~1.100 municipios de Colombia continental, y varía por región natural?

- **Datos:** DEM Copernicus GLO-30 por polígono municipal IGAC (mismo método que el Caribe, `extraer_dem_poligonos.py nacional`), índice SGC (% alta + % muy alta), SIMMA por 100 km². San Andrés queda fuera. Se excluyen categorías SIN/CD del SGC. Regiones: las de la sección 15.
- **Confirmatorios** (Spearman, IC95 % bootstrap de bloques por departamento, 2.000 réplicas): **N1** ρ(pendiente p90, SGC) > 0; **N2** ρ(densidad SIMMA, SGC) > 0; **N3** ρ parcial(SIMMA, SGC | pendiente p90) > 0. Todos con IC que excluye 0.
- **Heterogeneidad (N4):** ρ de N1 y N3 por región. Se declara «heterogénea» si algún IC regional excluye el valor nacional puntual. Con regiones pequeñas (< 30 municipios) solo se reporta.
- **Comparación con el Caribe:** se reporta si el ρ del Caribe (+0,52; +0,49; +0,31) cae dentro del IC nacional.
- **Limitaciones:** las de la §16 más: municipios muy grandes se leen decimados (tope 4 M píxeles); SIMMA tiene cobertura desigual entre regiones (sesgo de reporte), y la comparación entre regiones mezcla riesgo con capacidad de inventario; la circularidad SGC–pendiente se mantiene.


## 18. Validación del HAND con las huellas de inundación de La Niña 2010-2011 (IGAC), definida ANTES de correrla (2026-11-07)

**Pregunta:** ¿el HAND (fracción del municipio con HAND < 10 m) predice qué parte del municipio resultó inundada en La Niña 2010-2011, y aporta algo sobre la sola cota baja?

- **Datos:** IGAC, `Inundacion_Nina_100k_2011` (2.517 polígonos, escala 1:100.000, descargados tal cual, simplificados 0,0003°); HAND de los 195 municipios del Caribe (`hand_caribe.json`, `frac_hand_lt10_5`); cota baja del DEM (`frac_bajo_10m`). Variable respuesta: **fracción del área municipal cubierta por las huellas** (unión de polígonos ∩ municipio).
- **Confirmatorios** (Spearman, IC95 % bootstrap de bloques por departamento, 2.000 réplicas): **F1** ρ(fracción inundada, fracción HAND<10 m) > 0 con IC que excluye 0. **F2** ρ parcial(fracción inundada, HAND<10 | fracción cota<10 m) > 0 con IC que excluye 0 (el HAND aporta más allá de la altitud).
- **Descriptivo:** concordancia de terciles; municipios con mayor desacuerdo.
- **Limitaciones declaradas:** las huellas son una cartografía de una sola emergencia (no una frecuencia); pueden incluir cuerpos de agua permanentes (ciénagas, ríos grandes) y por tanto inflar la fracción en municipios ribereños; escala 1:100.000 frente a un DEM de ~90 m; el HAND es de superficie y no resuelve llanuras; análisis municipal (falacia ecológica); sin control de escorrentía local ni defensas.


## 19. Umbrales de lluvia acumulada–duración para movimientos en masa (E–D), definidos ANTES de correrlos (2026-11-07)

**Pregunta:** ¿la lluvia acumulada de CHIRPS discrimina los días con movimiento en masa reportado de los días sin él, se puede resumir en una curva E–D (E = a·D^b) y esa regla conserva capacidad en años no usados para calibrar? ¿Cambia por región?

- **Datos:** eventos `MOVIMIENTO EN MASA` de la UNGRD (tabla `ungrd_emergencias`, 2019-2024, 7.451 eventos, 712 municipios, fecha y municipio; **la fecha es la del reporte**, no necesariamente la de ocurrencia). Lluvia: CHIRPS v3.0 diario (sat, final), media municipal sobre los píxeles del polígono (`extraer_chirps_diario_colombia.py`).
- **Unidad:** municipio-día. **Positivo:** ≥ 1 evento ese día. **Negativo:** día sin evento en municipios con ≥ 1 evento en el periodo (capacidad de reporte demostrada), excluyendo ±2 días alrededor de cada evento.
- **Predictores:** lluvia acumulada E_D = suma de los D días que terminan el día del evento (inclusive), D ∈ {1, 2, 3, 5, 7, 10, 15, 30}; versión normalizada E_D / lluvia anual media del municipio.
- **Calibración:** 2019-2022. **Prueba reservada:** 2023-2024.
- **Confirmatorios:**
  - **T1:** AUC de E_D (positivos vs negativos) > 0,5 en la prueba reservada, con IC95 % bootstrap de bloques por departamento (2.000 réplicas), para el D* elegido solo con la calibración (D de mayor AUC).
  - **T2:** curva E–D. Para cada D, umbral = percentil 5 de E_D de los positivos de calibración; se ajusta log E = log a + b·log D por mínimos cuadrados. Regla de alerta: E_D ≥ a·D^b para algún D. **TSS = sensibilidad − tasa de falsas alarmas > 0** en la prueba reservada, con IC (bloques por departamento).
  - **T3:** la regla de T2 supera a la regla de un solo D* (TSS mayor), o se declara que no aporta.
- **Heterogeneidad:** T1 y T2 por región natural (sección 15); se reportan a, b y TSS por región cuando haya ≥ 100 eventos de calibración.
- **Limitaciones declaradas:** la fecha es la del reporte; **2022 aporta 4.176 de 7.451 eventos** (dominio de una temporada); CHIRPS a 5 km y media municipal subestiman la intensidad convectiva local; los días «negativos» pueden incluir eventos no reportados (inflan las falsas alarmas); sin humedad antecedente del suelo; no es un sistema de alerta temprana operativo ni sustituye la evaluación local; el TSS no equivale a probabilidad de ocurrencia.


## 20. Distribución del área de los movimientos en masa del inventario SIMMA (polígonos), definida ANTES de correrla (2026-11-07)

**Pregunta:** ¿qué distribución describe el área de los 209 polígonos de movimientos en masa publicados por el SGC, y cuánto cambia el resultado según el tipo de movimiento?

- **Datos:** SGC, `SIMMA/Capas_Principales/MapServer/3` (Poligono, 209 objetos con tipo y subtipo, sin fecha ni volumen). Área en m² con geometría proyectada MAGNA-SIRGAS Origen Nacional (EPSG:9377).
- **Ajuste:** log-normal, inversa gamma de tres parámetros (Malamud et al. 2004 como referencia funcional) y ley de potencia por cola (método de Clauset: xmin por mínimo KS, α por máxima verosimilitud). Comparación por AIC (log-normal vs inversa gamma) y razón de verosimilitud de Vuong frente a la log-normal en la cola.
- **Confirmatorios:** **M1** la log-normal o la inversa gamma se ajusta con KS p > 0,05 (bootstrap paramétrico, 1.000 réplicas). **M2** la cola sigue una ley de potencia con α entre 1,5 y 3,5 y KS p > 0,05.
- **Descriptivo:** mediana, percentiles 50/90/99 de área; ajuste por tipo con ≥ 30 polígonos.
- **Limitaciones declaradas:** 209 polígonos son una **muestra no probabilística** (cartografía de detalle en zonas específicas, no un inventario completo del país); los inventarios subrepresentan los eventos pequeños, lo que sesga hacia la izquierda el máximo de la distribución; **no hay volumen medido**, y la conversión área→volumen exigiría relaciones empíricas ajenas a estos datos; sin fecha no hay frecuencia temporal, solo distribución de tamaños; **no sirve para dimensionar barreras ni obras de contención**, que requieren energía de impacto y trayectoria.


## 21. Frecuencia de crecientes con los caudales máximos anuales del IDEAM, definida ANTES de correrla (2026-11-07)

**Pregunta:** ¿se pueden ajustar distribuciones de valores extremos (GEV, Log-Pearson III, Gumbel) a los máximos anuales del IDEAM de modo que sus caudales de retorno estén calibrados en años no usados para ajustar, y qué tan inciertos son?

- **Datos:** IDEAM, `Q_MX_A` (almacén abierto, un valor por año y estación). **Verificación hecha antes de correr** (2 estaciones): el valor anual coincide con el máximo de la serie horaria `CAUDAL_H` y de `Q_MX_D`; **es un máximo horario, no el pico instantáneo**, y subestima el pico en cuencas pequeñas. Se observan valores idénticos en años distintos en algunas series (p. ej. 2019 y 2022, o 2020 y 2021 en la 0011027030), posible señal de relleno o de saturación del sensor.
- **Inclusión:** ≥ 30 años con valor > 0; último año ≥ 2000. **Filtro de calidad:** se marca (y se analiza aparte) toda estación en que > 10 % de los años repite exactamente un valor de otro año.
- **Ajuste:** GEV por máxima verosimilitud; Log-Pearson III por momentos de log10; Gumbel por máxima verosimilitud. Retornos T = 2, 5, 10, 25, 50, 100 años. IC95 % por bootstrap paramétrico (300 réplicas) para el GEV. **T ≤ 50 es el rango principal; T = 100 es extrapolación** (con 30-60 años de registro) y se rotula así.
- **Confirmatorios** (agregados con IC95 % de bootstrap de bloques por departamento, 2.000 réplicas):
  - **C1 (calibración fuera de muestra):** ajustar con el primer 70 % de los años (cronológico) y contar, en el 30 % restante, la fracción de años que supera el Q10 estimado. Se declara «calibrado» si el IC de esa fracción agregada contiene 0,10. Ídem para Q2 (esperado 0,50).
  - **C2 (bondad de ajuste del GEV):** prueba KS con p-valor por bootstrap paramétrico; se cumple si la fracción de estaciones rechazadas al 5 % es ≤ 15 %.
  - **C3 (elección):** comparar, estación por estación, la log-verosimilitud predictiva fuera de muestra (misma partición 70/30) entre GEV y Log-Pearson III; se reporta cuál gana más a menudo, con IC.
- **Descriptivo:** fracción de estaciones con tendencia significativa (Mann-Kendall, α = 0,05; se espera ~5 % por azar, y los vecinos no son independientes); mediana de la razón (ancho del IC de Q50 / Q50); fracción con forma ξ fuera de [−0,5; 0,5] (ajuste inestable).
- **Limitaciones declaradas:** máximo horario ≠ pico instantáneo (subestimación del caudal de diseño real); series con posibles valores repetidos o rellenados; estacionariedad supuesta (el clima de 2010-2011 y 2022 no es independiente); estaciones de una misma cuenca no son independientes; **no sustituye** el estudio hidrológico de un proyecto con ingeniero responsable y no incluye áreas de drenaje ni transposición a sitios sin aforo.


## 22. Susceptibilidad a movimientos en masa por pesos de evidencia y regresión logística, definida ANTES de correrla (2026-11-07)

**Pregunta:** ¿la litología/edad, la distancia a fallas, la pendiente y la curvatura permiten discriminar dónde hay movimientos en masa inventariados, mejor que la pendiente sola, y esa capacidad sobrevive cuando se valida en un departamento que el modelo no vio?

- **Presencias:** puntos del inventario SIMMA (SGC, `SIMMA/Capas_Principales/MapServer/1`, 9.177 puntos; el caché anterior tenía 6.826). **Fondo:** puntos aleatorios sobre tierra en los polígonos municipales de Colombia continental, razón 5:1, semilla fija. Problema de solo presencia: el AUC mide discriminación frente al fondo, **no** probabilidad de ocurrencia.
- **Variables condicionantes** (en cada punto): pendiente y curvatura (Copernicus DEM GLO-30; pendiente por diferencias finitas en una ventana 3×3, curvatura por laplaciano); **litología/edad** (unidad del Mapa Geológico de Colombia V2023, capa `Unidades Cronoestratigráficas`, agrupada por el campo `Edad`); **distancia a la falla más cercana** (capa `Fallas` del mismo mapa, 1:1.000.000; clases < 1, 1-5, 5-10, 10-25, > 25 km). Las variables continuas se discretizan en clases por cuantiles del conjunto de presencias.
- **Pesos de evidencia:** para cada clase C: W⁺ = ln[P(C|presencia) / P(C|fondo)], W⁻ = ln[P(¬C|presencia) / P(¬C|fondo)], contraste = W⁺ − W⁻. Se suman los pesos de las variables como puntaje de susceptibilidad.
- **Independencia condicional:** se contrasta con la V de Cramér entre variables (pares con V > 0,3 se declaran dependientes, y el puntaje de pesos de evidencia se interpreta como sobrestimado) y se compara con una **regresión logística** con las mismas variables, que no la requiere.
- **Confirmatorios:**
  - **S1:** AUC de la regresión logística con las cuatro variables, con validación dejando un **departamento** fuera, > 0,5 con IC95 % (bootstrap de bloques por departamento, 2.000 réplicas).
  - **S2:** el modelo completo supera a la **pendiente sola** (línea base), en AUC espacial, con IC de la diferencia que excluye 0.
  - **S3:** el puntaje de pesos de evidencia alcanza un AUC espacial no inferior en más de 0,02 al de la regresión logística (si la independencia no se sostiene, se espera que sea inferior; se reporta).
- **Descriptivo:** pesos por clase (cuáles aumentan y cuáles reducen la susceptibilidad); AUC por región natural; comparación con el índice del SGC (§16) donde haya municipios comunes.
- **Limitaciones declaradas:** SIMMA es un inventario con sesgo de acceso y de cartografía (zonas estudiadas, no todo el país), y sin fecha ni magnitud; el fondo puede incluir movimientos no inventariados; la geología a 1:1.000.000 es gruesa y las unidades se agrupan por edad, no por litología real; las fallas a esa escala omiten estructuras locales; las clases por cuantiles dependen de la muestra; AUC espacial por departamento sigue sobreestimando si hay autocorrelación entre departamentos vecinos; **no es un mapa de amenaza normativo** (no incluye detonantes ni probabilidad temporal) y no sustituye una zonificación con estudio de campo.


## 23. Fórmulas candidatas con logaritmos y contraste con la normativa: hipótesis, línea base y criterios, definidos ANTES de correrlos (2026-11-07)

**Alcance y límites (valen para toda la sección):**
- Son **hipótesis de investigación**. Ninguna fórmula se incorpora al producto ni sustituye una norma o una curva oficial. Las normas vigentes (NSR-10 y las demás) se siguen citando textualmente.
- **Nada de lo que sigue cambia el texto de la NSR-10.** Una modificación del reglamento solo puede salir de su proceso oficial (Comisión Asesora Permanente y Ministerio de Vivienda). Aquí solo se genera evidencia que podría aportarse a ese proceso por los canales institucionales; la decisión de aportarla es del usuario.
- **Línea base obligatoria:** toda candidata se compara con (i) el modelo ya definido en el protocolo correspondiente y (ii) cuando exista, la ecuación publicada, **solo después de leer la fuente y registrar sus coeficientes, unidades y rango de validez**. Hasta entonces no se afirma que se «contradice» una ecuación publicada.
- **Familia de hipótesis:** cinco ejecutables (H1-H5). Se corrige por **Holm a α = 0,05** sobre esa familia; cada resultado se reporta con su p-valor ajustado.
- **Mejora** = la diferencia pareada de la métrica fuera de muestra respecto de la línea base tiene IC95 % (bootstrap de bloques por departamento, 2.000 réplicas) que excluye 0, con **a lo sumo 2 parámetros adicionales**. **Contradicción** = lo mismo en sentido contrario, con datos que no se usaron para ajustar. Ninguna de las dos se afirma si el análisis se rotula exploratorio.
- **Datos reservados:** los mismos cortes de cada protocolo de origen (calibración 2019-2022 y prueba 2023-2024 para lluvia y deslizamientos; 70/30 cronológico para crecientes; un departamento fuera para susceptibilidad). Nada se elige con los datos de prueba.

**H1 — umbral E–D normalizado por la lluvia anual media (§19).** Candidata: log(E/MAP) = log a + b·log D. Línea base: log E = log a + b·log D con los mismos datos. Métrica: TSS con la regla del percentil 5. **Prueba de transferencia:** ajuste en cuatro regiones y prueba en la quinta (dejar una región fuera); **mejora** si el TSS normalizado supera al no normalizado con IC que excluye 0. Se reporta además el coeficiente b de cada región (¿cambia con la normalización?).

**H2 — umbral E–D con terreno y ENSO (§19).** Regresión cuantil τ = 0,05 de log E sobre log D, **más** log(pendiente p90 municipal) y ONI del mes del evento (2 parámetros adicionales). Línea base: la curva global de H1. Métrica: TSS reservado (2023-2024) y razón de verosimilitud pseudo-cuantil. **Mejora** si ΔTSS tiene IC que excluye 0.

**H3 — susceptibilidad con variables continuas en logaritmo (§22).** logit p = β₀ + β₁·log(pendiente) + β₂·log(1 + distancia a falla) + términos de edad geológica (clases). Línea base: la regresión logística del §22 con variables discretizadas por cuantiles. Métrica: AUC dejando un departamento fuera; **mejora** si ΔAUC (pareado por réplica) excluye 0.

**H4 — GEV con el ONI como covariable de localización (§21).** Candidata: μ(t) = μ₀ + μ₁·ONI̅(t), con ONI̅ = media anual (enero-diciembre) del ONI del año del máximo; sensibilidad (descriptiva) con el rezago de un año. Línea base: GEV estacionaria del §21. **H4a (significancia de campo):** fracción de estaciones con razón de verosimilitud p < 0,05 mayor que 5 % con IC (bloques) que excluye 0,05. **H4b (predictiva):** en el 30 % reservado, la candidata tiene mayor log-verosimilitud predictiva que la estacionaria en más del 50 % de las estaciones (IC que excluye 50 %). Control de FDR (Benjamini-Hochberg, q = 0,10) en el listado por estación. Limitación declarada: el valor anual no trae la fecha del máximo.

**H5 — forma ξ compartida por región (§21).** La GEV con ξ fijado en la mediana regional (calculada solo con el 70 % de calibración de las demás estaciones de la región) frente a la GEV con ξ libre. **Mejora** si la log-verosimilitud predictiva reservada no es peor que −0,5 por estación en mediana y el ancho relativo del IC de Q50 se reduce (mediana de la razón < 1).

**H6 — escalamiento de duraciones para curvas IDF (Bell, 1969, calibrado).** **No se ejecuta**: no hay lluvia sub-horaria histórica abierta (verificado el 7 de noviembre de 2026). Queda registrada para cuando se disponga de pluviógrafos del IDEAM o de una fuente comparable.

**Pista B — contraste descriptivo de la amenaza sísmica de la NSR-10 con el modelo nacional del SGC (sin criterios confirmatorios).**
- **Pregunta:** ¿cuánto y dónde difiere, por municipio, la aceleración Aa de diseño de la NSR-10 (Apéndice A-4) del valor del Modelo Nacional de Amenaza Sísmica del SGC para el mismo período de retorno?
- **Datos y verificación previa:** Aa por municipio del Apéndice A-4. **Verificado el 7 de noviembre de 2026:** la ingesta textual del Título A contiene la Tabla A.2.2-1 (valores por región de los mapas) y las referencias al apéndice, pero **no** la tabla municipal completa; hay que ingestarla desde el PDF fuente (ver `docs/fuentes-normativas.md`) y verificar su vigencia (el Decreto 1401 de 2023 modificó parcialmente el reglamento). Modelo SGC (Resolución 080 de 2020) con su sistema de consulta. **Antes de calcular, verificar** que ambas fuentes sean descargables con licencia que lo permita, y registrar que Aa (aceleración efectiva sobre roca) y la aceleración pico del modelo **no son idénticas** (definiciones, suelo de referencia y período de retorno pueden diferir).
- **Producto:** tabla y mapa de diferencias relativas con su incertidumbre, y lista de municipios donde la diferencia supera 25 %; no se propone ninguna fórmula ni valor de reemplazo.
- **Límites:** no usar datos del evento de agosto de 2026 ni conclusiones sobre daños sin revisión; los valores son de referencia y no de diseño.

**Limitaciones comunes:** las de §15, §19, §21 y §22 (sesgo de reporte, fecha de reporte, CHIRPS de 5 km, máximo horario del IDEAM, DEM de 90 m, autocorrelación espacial); la inferencia sobre cinco hipótesis aún puede sobreestimar; los resultados son regionales y comparativos, no de diseño.


### Aclaraciones al §23 (2026-11-07, antes de correr H1, H2, H4 y H5; H3 ya se había corrido)
- **Familia de Holm:** H1, H2, H3, H4a y H4b, con **p-valores bootstrap bilaterales** (bloques por departamento, 2.000 réplicas; p = 2·mín(P(Δ ≤ 0), P(Δ ≥ 0)) con corrección +1). **H5 se evalúa por su regla** (sin p-valor) y se reporta aparte.
- **H3 ya se corrió una vez** antes de programar la corrida final (resultado previo a Holm: ΔAUC = +0,0153, IC95 % [+0,0055; +0,0288]). La candidata cambia dos cosas a la vez respecto de la línea base (usa logaritmos y omite la curvatura), así que **la atribución de la mejora es ambigua**; se añade un control exploratorio (lineal sin curvatura) que no entra a la familia.
- **Corrida programada:** `corrida_final.sh` ejecuta cada análisis cuando su insumo esté listo y `consolidar_corrida.py` aplica Holm. Resultados en `resultados_corrida/`. Un insumo ausente se reporta como «no disponible», no como resultado nulo.


## 24. Cobertura del suelo satelital (ESA WorldCover 2021) y aprendizaje automático en la susceptibilidad, definidos ANTES de correrlos (2026-11-07)

**Pregunta:** ¿una variable satelital gratuita (cobertura del suelo, 10 m) y un modelo de gradiente boosting mejoran la discriminación de movimientos en masa frente a la regresión logística del §22, dejando un departamento fuera?

- **Datos:** las mismas 9.130 presencias SIMMA y 45.593 puntos de fondo del §22. **Nueva variable satelital:** clase de cobertura de ESA WorldCover v200 (2021, 11 clases, 10 m, licencia CC BY 4.0, COG en AWS), leída por teselas en una malla de ~90 m (por la vista de resumen del COG, vecino más cercano). **Nueva variable climática:** lluvia anual media del municipio del punto (CHIRPS v3.0, 1981-2024, media de los 528 meses).
- **Modelos** (validación dejando un departamento fuera; 23 departamentos con ≥ 20 presencias, como en el §22):
  - **B0:** logística del §22 (pendiente, curvatura, log(1 + distancia a falla), edad).
  - **B1:** B0 + cobertura (clases como variable categórica) + lluvia anual media.
  - **G0:** gradiente boosting (`HistGradientBoostingClassifier`, hiperparámetros por defecto fijados: 200 iteraciones, profundidad máx. 4, tasa 0,05, sin ajuste con los datos de prueba) con las variables de B0.
  - **G1:** gradiente boosting con las variables de B1.
- **Confirmatorios** (diferencia pareada de AUC espacial; IC95 % por bootstrap de bloques por departamento, 2.000 réplicas; **Holm a α = 0,05 sobre estos dos**):
  - **E1 (aporte de la variable satelital y la lluvia):** AUC(B1) − AUC(B0) > 0.
  - **E2 (aporte del aprendizaje automático):** AUC(G1) − AUC(B1) > 0.
- **Descriptivo:** AUC(G0) − AUC(B0) (el efecto del modelo con las mismas variables), AUC por región natural y la importancia por permutación de G1 en un departamento reservado.
- **Limitaciones declaradas:** la cobertura es de **2021**, posterior a muchos de los movimientos del inventario (el inventario no tiene fecha), así que puede reflejar el **efecto** del movimiento (suelo desnudo) y no su causa → **posible fuga causal**, que haría E1 optimista; la cobertura se muestrea en un píxel de ~90 m del resumen del COG; la lluvia es municipal (ecológica); el gradiente boosting con 55.000 puntos y 6 variables puede sobreajustar al departamento de entrenamiento mayoritario (Antioquia, Boyacá); AUC espacial por departamento sigue sobreestimando por autocorrelación entre departamentos vecinos. **No es un mapa de amenaza normativo.**
