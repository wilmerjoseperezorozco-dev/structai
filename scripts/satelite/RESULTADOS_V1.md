# Resultados V1: confirmación fuera del Caribe y refinamiento (2026-11-08)

Protocolo (con su enmienda previa) fijado antes de calcular: [`PROTOCOLO_V1_CONFIRMACION.md`](PROTOCOLO_V1_CONFIRMACION.md). Código: `v1_municipal.py` (terreno, vías, lugares poblados), `v1_analisis.py` (análisis preregistrado) y `v1_posthoc.py` (verificaciones posteriores, no preregistradas). Salidas: `v1_municipal.json`, `v1_panel.csv`, `v1_resultados.json`. OpenStreetMap consultado el 2026-11-08. Panel: 1.000 municipios de 21 departamentos (195 de descubrimiento en el Caribe y 805 de confirmación en 14 departamentos). Antioquia falló una vez por un error de lectura de red y se reintentó con éxito; ningún departamento de la lista quedó sin procesar.

## Veredicto: **V1 no se confirma**
**C-1 (confirmatoria).** En los 14 departamentos de confirmación (570 municipios con al menos 5 km de vía principal), la correlación parcial de Spearman entre la exposición vial y las viviendas dañadas por 100 mil habitantes es **ρ = 0,00, IC95 % por departamentos [−0,10; +0,11]**. El criterio exigía un límite inferior mayor que 0 y ρ ≥ 0,15. No se cumple ninguna de las dos condiciones.

| Muestra | Resultado | ρ parcial | IC95 % por departamentos | n |
|---|---|---:|---|---:|
| Descubrimiento (Caribe), recalculado con esta tubería | viviendas dañadas (todos los eventos) | +0,34 | [+0,18; +0,45] | 159 |
| **Confirmación (14 departamentos)** | **viviendas dañadas (todos los eventos), primario** | **0,00** | **[−0,10; +0,11]** | 570 |
| Confirmación | viviendas dañadas solo por inundación | +0,10 | [+0,01; +0,18] | 570 |
| Confirmación | reportes de inundación | +0,09 | [+0,02; +0,17] | 570 |
| Conjunta (21 departamentos) | viviendas dañadas (todos los eventos) | +0,09 | [−0,01; +0,21] | 729 |

La estimación del Caribe se reproduce con la nueva tubería (+0,34 frente a +0,34 del barrido), lo que indica que el cálculo es consistente. **El efecto es regional**, no general: por región natural, Caribe +0,34, Andina +0,02 [−0,10; +0,15] y Pacífica −0,05 [−0,14; +0,30] (Orinoquia solo tiene un departamento y no se estima).

## Robustez (muestra conjunta salvo que se indique; razón de tasas por cada +0,10 de exposición vial, con efectos fijos de departamento)
- **R1.** Conjunta: RR = 1,02 [0,91; 1,14]. Descubrimiento: **1,20 [1,11; 1,30]**. Confirmación: **0,88 [0,79; 0,98]**. Fuera del Caribe el efecto estimado va en sentido contrario.
- **R2 (interacciones, Holm sobre 4).** Ninguna significativa tras la corrección: con vivienda vulnerable p = 0,18; NBI 2018 p = 0,84; porcentaje en cabecera p = 0,06; lluvia p95 p = 0,34. No hay evidencia de que el efecto se concentre donde la vivienda o los ingresos son más frágiles.
- **R3 (tipo de vía).** Troncal 0,99 [0,88; 1,10], primaria 1,07 [0,88; 1,30], secundaria 1,00 [0,89; 1,11]. Sin diferencias.
- **R5 (controles negativos).** Movimientos en masa 0,95 [0,89; 1,01], incendio forestal 0,96 [0,89; 1,05], reportes de inundación 1,00 [0,91; 1,09]. Los controles no muestran sesgo de reporte por el tamaño de la red vial en la muestra conjunta.

## Mecanismo: ¿actúa la vía como indicador de población en terreno bajo?
- **P1 (preregistrada).** Los lugares poblados (ciudades, pueblos, aldeas y caseríos de OpenStreetMap) que están a 1 km o menos de una vía principal tienen **más probabilidad de estar en terreno bajo** que los más lejanos: razón de momios de Mantel-Haenszel 1,57 [1,37; 1,79] en 576 municipios. Es un resultado real y respalda la teoría de que las vías se tienden en los fondos de valle y arrastran población con ellas. *Por región (posterior, no preregistrado):* Andina 1,85 [1,53; 2,25], Pacífica 1,67 [1,19; 2,36], Caribe **1,24 [0,98; 1,57]**, Orinoquia 1,11 [0,56; 2,21] (15 municipios).
- **P2 (preregistrada).** En la muestra conjunta el coeficiente de la exposición vial ya es casi 1,0, de modo que la «reducción del 75 %» que arroja el cálculo no se interpreta (es una fracción de un efecto casi nulo). *Verificación posterior solo en el Caribe:* al agregar los indicadores de mecanismo, el RR pasa de 1,20 [1,11; 1,30] a 1,25 [1,10; 1,42]; **no se reduce**. Por tanto, **la asociación del Caribe no se explica por el hecho de que la vía indique población en terreno bajo**.

## Aplicación en política pública (R6, focalización)
Al dejar un departamento fuera y priorizar el 20 % de municipios mejor clasificado, se capturan en promedio estas fracciones de las viviendas dañadas: solo población 48,7 %, más HAND municipal y área 49,8 %, más exposición vial 49,5 % (20 departamentos). La exposición vial **no mejora la focalización**: C − B = −0,3 puntos porcentuales [−1,2; +0,5]. Con estos datos, el tamaño de la población es lo que más pesa, y ni el terreno municipal ni la vía agregan información útil para decidir dónde enfocar recursos.

## Lectura e interpretación
1. La asociación que se vio en el Caribe **no es una ley general**. Puede reflejar algo propio de esa región (red vial sobre llanuras de inundación, ganadería y agricultura anfibia, capacidad de reporte) o un hallazgo espurio del barrido, que probaba 120 pares con 7 departamentos.
2. El sustento teórico sobre desarrollo lineal se apoya en un hallazgo propio: **los lugares poblados cerca de las vías sí están más en terreno bajo, sobre todo en la región Andina y la Pacífica**. Pero esa mayor exposición no se traduce en más daños reportados. Una explicación posible, no probada, es que en la montaña el terreno bajo respecto al cauce (HAND < 10 m) es el fondo del valle, donde las obras de protección y el ordenamiento son más frecuentes, y que el HAND de 90 m no distingue una llanura de inundación de un valle encajonado.
3. Las medidas no son comparables entre regiones: la exposición vial mediana es 0,56 en el Caribe y 0,17 en la Andina, y la fracción mediana del municipio en HAND < 10 m es 0,49 y 0,06. «Terreno bajo» significa cosas distintas en una llanura y en una montaña.

## Límites
- El resultado primario suma todos los eventos de la UNGRD (incendios, vendavales, etc.) para ser comparable con el descubrimiento; la versión solo-inundación es positiva en la confirmación (+0,10 [+0,01; +0,18]) pero no alcanza el umbral preregistrado de 0,15 y no se usa para confirmar.
- La UNGRD mide también la capacidad de reportar; el NBI 2018 y el control por población lo mitigan sin eliminarlo.
- HAND de 90 m no ve diques ni terraplenes; OpenStreetMap es voluntario y la cobertura varía; NBI es del censo 2018, no del periodo de los eventos.
- No se evaluó el estado de ninguna estructura ni se nombra ninguna.

## Qué sigue
- **No** se debe usar la exposición vial como indicador de focalización: el criterio de validación cruzada no lo respalda.
- Si se quiere entender el efecto del Caribe, el paso lógico es medir el **sesgo de reporte de la UNGRD** (cuánto reporta cada municipio por su capacidad y no por su riesgo), que es la explicación alternativa más fuerte que queda.
- Una variable de «terreno bajo» con sentido físico comparable entre llanura y montaña (por ejemplo, el área inundable según el modelo de inundación o la huella de La Niña 2010-2011) probaría mejor la hipótesis en el interior.
