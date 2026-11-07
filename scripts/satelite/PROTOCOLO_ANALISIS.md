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
