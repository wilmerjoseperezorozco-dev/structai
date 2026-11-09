# Impermeabilización y excavaciones: Fase 0 (alcance, verificación de supuestos y qué parte es aprendizaje automático)

Estado: planificación, 2026-11-09. No hay código nuevo. Parte de una propuesta de dos frentes: (1) selección de sistema de impermeabilización y predicción de su vida útil; (2) excavaciones: talud frente a contención temporal, rendimiento y consumo de combustible de maquinaria, balance de tierras y alerta de asentamientos en vecinos.

## 1. Criterio de partida

El aprendizaje supervisado necesita etiquetas observadas (qué sistema funcionó, cuándo falló, cuánto rindió una máquina). Donde el objetivo es una cantidad calculable con ecuaciones y una norma, la enumeración exacta con costo es más honesta y no se deja superar por un modelo aprendido; el aprendizaje sirve después como sustituto rápido de un motor ya validado (ese fue el patrón de la zapata, con 5.000 casos y ninguno inseguro; ver `REFUERZO_ML_Y_OPTIMIZACION_2026-11.md`, secciones 2 y 3). Las dos exigencias del proyecto: cada cifra con fuente, y nunca una «solución óptima» sin datos de sitio (`docs/EXCAVACION_VOLADURA_Y_FUENTES_INTERNACIONALES_2026-11.md`, sección 5).

## 2. Lo verificado el 2026-11-09 y su fuente

| Afirmación | Resultado | Fuente |
|---|---|---|
| Factores de seguridad de taludes exigidos | **Tabla H.2.4-1:** taludes en condición estática con agua subterránea normal, FSBM 1,50 (diseño) y 1,25 (construcción); seudoestática con sismo 1,05 (diseño) y 1,00 (construcción), con parámetros sísmicos de construcción al 50 % de los de diseño. El artículo que los invoca para taludes es **H.5.2.7**, no H.4 | NSR-10, H.2.4 y H.5.2.7 (PDF fuente 1401-1450) |
| Cómo se verifica un talud de excavación | **H.5.1.2.1** exige un método de equilibrio límite con superficies cinemáticamente posibles, agua, sobrecargas y grietas de tracción; **no da un ángulo ni una tabla** de inclinaciones. La cohesión de arcillas puede bajar hasta 30 % en un mes | NSR-10, H.5.1.2.1 |
| Asentamientos de vecinos | **H.5.1.3.2** pide modelación analítica o numérica que incorpore el procedimiento constructivo y **medición continua durante la obra**. No fija un límite de distorsión angular en ese artículo | NSR-10, H.5.1.3.2 |
| «Ancho de fisura admisible (C.10.6)» | **C.10.6 es la distribución del refuerzo de flexión para controlar el agrietamiento**, no un valor de ancho de fisura. Ese límite hay que tomarlo de otra fuente y citarla | NSR-10, C.10.6.1 |
| Datos climáticos de IDEAM | Normales climatológicas (`nsz2-kzcq`, 16.761 filas, 4 períodos): precipitación, días con lluvia, humedad relativa, **brillo solar** (no radiación UV), evaporación, temperatura media, máxima y mínima, por estación (294 con brillo solar; 31 en Atlántico en alguno de los períodos) | datos.gov.co |
| Salinidad ambiental y radiación UV | **No existen** en datos.gov.co. La distancia a la costa se puede calcular y el brillo solar sirve de aproximación a la exposición, ambos como proxy declarado | catálogo de datos.gov.co, 6 búsquedas |

**No verificado (viene en la propuesta y no se debe repetir como dato):** que un sistema económico falle «cada 4 años»; que genere «hasta 2,5 veces» más CO₂e que una membrana de 20 años; el esponjamiento «del 15 % al 35 %»; los tiempos de ciclo de cargue y los rendimientos; la tabla de deflexiones admisibles de C.9.5, que no se consultó. Cada una necesita fuente primaria (declaraciones ambientales de producto para el CO₂e, estudios de tiempos y movimientos para rendimientos, manual geotécnico para esponjamiento).

## 3. Clasificación de cada módulo

| Módulo | ¿Hay etiquetas? | ¿Aprendizaje justificado? | Camino propuesto |
|---|---|---|---|
| Selector de sistema de impermeabilización | No: no existe un conjunto de «sistema óptimo» observado | No como clasificador supervisado: aprendería las reglas que uno mismo escriba | Motor de reglas de compatibilidad (elemento, exposición, movimiento) y optimización de costo del ciclo de vida |
| Vida útil y supervivencia | No se encontró un conjunto público con tiempos hasta la filtración | No hay con qué entrenar un bosque de supervivencia | Simulación de Monte Carlo con vidas útiles declaradas y su incertidumbre, VPN a 30-50 años; los datos de falla se piden a interventores, aseguradoras o fabricantes |
| Talud o contención temporal | Parámetros de suelo son del sitio; no hay base pública | No: es un problema de equilibrio límite con FS de la Tabla H.2.4-1 | Enumeración de alternativas (talud, bermas, entibado, pantalla) con FS verificado y costo APU; como el muro de contención |
| Rendimiento de maquinaria y ACPM | No se encontraron estudios de tiempos y movimientos públicos; sí rendimientos de camión por ANDI/UPME | Solo con datos medidos | Modelo físico de ciclo con fuentes citadas; regresión únicamente si se consiguen datos |
| Balance de tierras y ZODME | La estructura del problema es conocida | No aprendizaje por refuerzo: es programación lineal (diagrama de masas) | Optimización lineal con distancias, costo de transporte y criterio de reutilización por clasificación del suelo |
| Asentamientos en vecinos con red neuronal | No hay conjunto de modelos de elementos finitos propio; además, riesgo para la vida | No en esta etapa | Diferida hasta tener un modelo numérico validado; antes, el método analítico de H.5.1.3.2 y la monitorización |

## 4. Fases propuestas

1. **Fase 1a, excavación determinista** (la de mayor respaldo normativo ya verificado): equilibrio límite de taludes con los FS de la Tabla H.2.4-1, empujes y alternativas de contención, costo con la base APU, huella de CO₂e con rendimientos de combustible con fuente. Entrada: parámetros del sitio.
2. **Fase 1b, balance de tierras** por programación lineal.
3. **Fase 1c, impermeabilización:** reglas de compatibilidad, clima de la normal climatológica más cercana y distancia a la costa, VPN estocástico. Sin cifras de vida útil sin fuente.
4. **Fase 2:** vacíos y verificación extremo a extremo con casos reales; adquisición de datos de falla y de tiempos de maquinaria.
5. **Aprendizaje automático** solo sobre los motores validados, como sustituto rápido, con la comprobación de que no produce soluciones inseguras.

## 5. Preguntas abiertas para decidir

- ¿Hay acceso a datos reales de fallas de impermeabilización (interventorías, aseguradoras, fabricantes) o a estudios de tiempos de maquinaria de obras propias?
- Si no, ¿se acepta que el primer producto sea un motor de decisión con incertidumbre explícita, no un modelo entrenado?
- Orden de ejecución: 1a, 1b y 1c, o empezar por el frente con mejor respaldo normativo (1a).

## 6. Fase 1a: ejecución con datos sintéticos (2026-11-09)

Código: `packages/motor-concreto/src/excavacion_estabilidad.py` y `excavacion_metricas.py`; ejercicio: `scripts/excavacion/comparar_alternativas_sintetico.py` (salida `data/excavacion/comparacion_sintetica.json`). **Todas las entradas del ejercicio son inventadas** (suelo c' = 10 kPa, φ' = 27°, H = 6 m, lindero a 8 m, COV de c' 0,30 y de tan φ' 0,10, consecuencia de falla 400 millones COP por metro, precio de excavación, consumo y factor de emisión). Sirve para validar la tubería, no para decidir una obra.

El motor de taludes se contrastó con un cálculo independiente de momentos por intersección de polígonos (corte vertical φ = 0: número de estabilidad 4,25 en ambos). Una primera versión de la búsqueda del círculo crítico sobrestimaba el FS de taludes inclinados hasta 5 %; se corrigió y el desvío residual es menor a 1 %.

| Alternativa (sintética) | Retiro (m) | ¿Cabe a 8 m? | IEG | FS medio | Pf | Costo total (millones COP/m) |
|---|---|---|---|---|---|---|
| Talud al máximo seguro (54,2°, FS 1,25) | 4,33 | sí | 0,82 | 1,25 | 8,4 % | 35,6 |
| Talud 45° | 6,00 | sí | 0,77 | 1,44 | 0,9 % | 5,7 |
| Talud 35° | 8,57 | no | 0,70 | 1,74 | 0,01 % | 2,2 |
| Contención temporal | — | — | — | — | — | sin dimensionar |

Lectura bajo esos supuestos: el ángulo que apenas cumple la Tabla H.2.4-1 es el más barato de excavar y el más caro una vez se pone precio al riesgo; entre las alternativas que caben en el predio, 45° minimiza el costo total. La conclusión depende de la consecuencia y de la variabilidad supuestas, no de datos de sitio. La probabilidad de falla es una estimación de confiabilidad de primer orden con FS log-normal, no una frecuencia observada.

### 6.1 Bermas y contención en voladizo (mismas entradas sintéticas)

Se conectaron las bermas al cálculo de riesgo (`costo_riesgo_geotecnico(..., bermas=...)`) y se agregó `excavacion_contencion.py`: pantalla en voladizo con empujes de Rankine, empuje pasivo reducido por un factor del usuario, sin agua, sin apoyos, sin verificación estructural. El empotramiento se contrastó con el cierre analítico del equilibrio de momentos en suelo granular (1 % de tolerancia). Sobrecarga sintética 10 kPa, FS pasivo 1,5, precio de pantalla sintético.

| Alternativa (sintética) | Retiro (m) | IEG | FS medio | Pf | Costo total (millones COP/m) |
|---|---|---|---|---|---|
| Talud 54° con berma de 2 m a media altura | 6,33 | 0,76 | 1,57 | 0,08 % | 2,3 |
| Talud 45° | 6,00 | 0,77 | 1,44 | 0,9 % | 5,7 |
| Contención en voladizo (11,5 m de pantalla, M máx 281 kN·m/m) | 0,5 | 0,95 | — | 0,5 % (supuesto) | 10,5 |
| Talud 54° sin berma | 4,33 | 0,82 | 1,25 | 8,4 % | 35,6 |

La berma sube el FS de 1,25 a 1,57 con 2 m más de retiro y 6 m² más de corte por metro, y desplaza el óptimo. Dos advertencias: la probabilidad de falla de la contención es un supuesto, no un cálculo (el módulo no la estima), así que su posición en el ranking depende de ese supuesto; y un voladizo de 6 m con 5,5 m de empotramiento está en el límite de lo razonable, por lo que en una obra real se compararía con una pantalla apoyada. Con 35° fuera del predio, el ranking solo incluye alternativas que caben en el lindero.
