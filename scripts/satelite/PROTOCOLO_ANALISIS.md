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
