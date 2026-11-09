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

## 6. Fase 1a: ejecución con datos sintéticos y revisión (2026-11-09)

Código: `packages/motor-concreto/src/excavacion_estabilidad.py`, `excavacion_metricas.py`, `excavacion_contencion.py`; ejercicio: `scripts/excavacion/comparar_alternativas_sintetico.py` (salida `data/excavacion/comparacion_sintetica.json`). **Las entradas del ejercicio son inventadas** (suelo c' = 10 kPa, φ' = 27°, H = 6 m, lindero a 8 m, sobrecarga 10 kPa, COV de c' 0,30 y de tan φ' 0,10, consecuencia de falla 400 millones COP por metro de frente, precios de excavación y pantalla, consumo y rendimiento de la máquina); el factor de emisión del diésel es el de FECOC (10,2765 kg/gal), con fuente. Sirve para validar la tubería, no para decidir una obra.

### 6.1 Validación y errores hallados en la revisión independiente

El número de estabilidad del corte vertical con φ = 0 (4,25) coincide en tres cálculos independientes (módulo, intersección de polígonos, integrador del revisor). Una revisión de código posterior halló errores que las pruebas originales no detectaban; todos se corrigieron y cada uno tiene prueba de regresión:

| Hallazgo | Efecto antes de corregir | Corrección |
|---|---|---|
| Presión de poros sin limitar a la superficie del terreno | FS = 0,0013 en un caso con freática a 3 m (físicamente absurdo); distorsionaba el ángulo máximo seguro | Carga piezométrica limitada al terreno |
| Refinamiento Nelder-Mead sin cotas | Con φ = 0 y sismo, círculos de radio 10⁴³ y FS ≈ 10⁻⁴²; el selector elegía contención para cualquier arcilla con sismo | Dominio acotado (R ≤ 15·max(H, retiro), profundidad ≤ 1,2 H) |
| `sismo=True` sin kh | Análisis estático contra FS 1,00: talud de 67,3° en vez de 61,9° | El selector exige kh coherente con `sismo` |
| Alternativas comparadas con hipótesis distintas | Taludes sin sobrecarga ni grieta frente a una contención con sobrecarga; el talud "máximo seguro" de 54,2° no cumplía 1,25 con grieta y sobrecarga (50,6° sí) | Misma sobrecarga y grieta en todas |
| Voladizo con φ ≈ 0 | Excepción cruda de `brentq` | Devuelve `requiere_apoyos` |
| Empotramiento del voladizo sin factor | Resultante horizontal sin equilibrar (empotramiento corto) | `factor_longitud` obligatorio, del usuario |
| Costo de consecuencia sin base de longitud | Se sumaba un evento a costos por metro | Declarado por metro de frente |
| Bishop sin convergencia y FS infinito | Aceptados en silencio | El círculo se descarta; sin superficie válida lanza error |

Quedan como limitaciones documentadas: la grieta se modela seca (no conservador con freática alta), el agua se trata sin red de flujo, y la bisección del ángulo máximo supone FS decreciente con el ángulo (no vale con franja de sobrecarga en coordenadas absolutas).

### 6.2 Resultados (mismas hipótesis para todas las alternativas)

| Alternativa (sintética) | Retiro (m) | IEG | FS medio | Pf | Costo total (millones COP/m) |
|---|---|---|---|---|---|
| Talud 51° con berma de 2 m a media altura | 6,93 | 0,74 | 1,59 | 0,08 % | 2,3 |
| Contención en voladizo (13,1 m de pantalla con factor 1,3; M máx 281 kN·m/m) | 0,5 | 0,95 | — | 0,5 % (supuesto) | 11,4 |
| Talud 45° | 6,00 | 0,77 | 1,38 | 2,5 % | 12,1 |
| Talud 50,6° (máximo con FS 1,25) | 4,93 | 0,80 | 1,25 | 7,3 % | 31,0 |
| Talud 35° | 8,57 | 0,70 | 1,69 | 0,2 % | 3,0 (no cabe en el predio) |

### 6.3 Discusión

1. **El ángulo que apenas cumple la Tabla H.2.4-1 es el más caro cuando se valora el riesgo.** Con FS 1,25 la probabilidad de falla estimada es 7,3 %; a 45° baja a 2,5 % y con una berma de 2 m a 0,08 %. La norma fija un factor mínimo, no un riesgo aceptable, y la distancia entre ambos es de un orden de magnitud en probabilidad.
2. **La berma es la intervención de mayor rendimiento en este caso:** sube el FS de 1,25 a 1,59 con 2 m más de retiro y 6 m² más de corte por metro (IEG de 0,80 a 0,74). Su costo extra de excavación es marginal frente al riesgo evitado.
3. **La contención en voladizo no gana ni con probabilidad de falla cero:** su costo sin riesgo (9,4 millones COP/m) ya supera el costo total de la mejor alternativa de talud. Por tanto, el resultado no depende del supuesto de Pf = 0,5 % que se le asignó. Solo cambia si el lindero queda a menos de ~6,9 m (retiro de la berma): entonces la mejor alternativa de talud que cabe cuesta más (12,1 millones a 45° y 31,0 a 50,6°) y la contención pasa a ser la más barata.
4. **Eficiencia geométrica y riesgo se oponen:** la contención tiene el mayor IEG (0,95) pero un voladizo de 6 m con 7,1 m de empotramiento está en el límite de lo razonable; en obra se compararía con pantallas apoyadas, no dimensionadas aquí.
5. **Alcance de las conclusiones:** dependen de la consecuencia (400 millones por metro), de la variabilidad supuesta y de los precios inventados. La probabilidad de falla es una estimación de confiabilidad de primer orden con FS log-normal y variables independientes, no una frecuencia observada. Sin datos de sitio ni de obra, la conclusión transferible es la estructura de la decisión (talud mínimo normativo frente a talud con riesgo valorado frente a contención), no las cifras.

## 7. Fase 1b: balance de tierras por programación lineal (datos sintéticos)

Código: `packages/motor-concreto/src/excavacion_balance.py` (6 pruebas: casos con solución a mano, conservación de volúmenes, optimalidad frente a una heurística en 25 instancias aleatorias, infactibilidad); ejercicio: `scripts/excavacion/balance_tierras_sintetico.py` (salida `data/excavacion/balance_tierras_sintetico.json`). Con fuente: factor de emisión del diésel (FECOC, 10,2765 kg/gal) y rango de rendimiento de la volqueta sencilla del catálogo de flota (9-11 km/gal). **Sintéticos:** volúmenes (3 zonas de corte, 8.000 m³; 2 rellenos, 4.200 m³ en banco equivalente), fracciones aprovechables, distancias, tarifa de botadero, precio de préstamo, costo por m³-km, esponjamiento 25 %, capacidad suelta 6 m³. El combustible supone viaje cargado de ida y vacío de vuelta al mismo rendimiento, y cuenta solo el transporte (no la extracción del préstamo ni la compactación).

| Escenario (sintético) | Objetivo | Costo (millones COP) | Reutilización | ACPM (gal) | kg CO₂e | Préstamo (m³) | Botadero (m³) |
|---|---|---|---|---|---|---|---|
| Base | costo = reutilización | 104,3 | 49,4 % | 2.027 | 20.831 | 250 | 4.050 |
| Suelo de peor calidad (aprovechable a la mitad) | ambos | 228,2 | 24,7 % | 3.603 | 37.028 | 2.225 | 6.025 |
| Préstamo barato (8.000 COP/m³) | ambos | 99,3 | 49,4 % | 2.027 | 20.831 | 250 | 4.050 |
| Préstamo caro (60.000 COP/m³) | ambos | 112,3 | 49,4 % | 2.027 | 20.831 | 250 | 4.050 |
| Relleno 2 a 25 km y préstamo a 3 km | mínimo costo | 128,3 | 37,5 % | 2.463 | 25.310 | 1.200 | 5.000 |
| Relleno 2 a 25 km y préstamo a 3 km | máxima reutilización | 131,9 | 49,4 % | 2.933 | 30.140 | 250 | 4.050 |

### Discusión

1. **La reutilización está acotada por la oferta, no por el costo, en los escenarios con rellenos cercanos.** La cota es la oferta aprovechable (49,4 % del corte); la demanda (52,5 %) queda 250 m³ por encima y se cubre con préstamo. Cuando el movimiento de tierras entre el corte y el relleno es corto, mover material propio siempre es más barato que traerlo: el precio del préstamo (8.000 a 60.000 COP/m³) solo cambia el costo total en 5 a 8 millones y no la decisión.
2. **La calidad del suelo domina el resultado:** con la mitad de material aprovechable, el costo se multiplica por 2,2, la reutilización cae a 24,7 % y el diésel sube 78 %. Es la variable que más conviene medir antes de cualquier optimización (clasificación del suelo y ensayos), porque ningún ajuste de logística compensa material inservible.
3. **Reutilizar más puede costar más carbono, no menos.** Con un relleno a 25 km y un préstamo a 3 km, llevar el material propio sube la reutilización de 37,5 % a 49,4 % (+11,9 puntos) a cambio de +3,6 millones de COP (+2,8 %) y +4.830 kg CO₂e (+19 %) solo por transporte. La intuición de que reutilizar siempre reduce la huella solo vale cuando la distancia de acarreo es corta; aquí falta añadir lo que el modelo no cuenta (extracción y producción del material de préstamo, ocupación de botadero), que podría invertir el signo.
4. **Límites:** el modelo es lineal (sin costos fijos de apertura de un botadero ni de un frente de préstamo, sin restricciones de flota ni de tiempo), asume una sola tarifa por m³-km y volúmenes en banco ya convertidos por compactación. La conclusión transferible es la estructura (la oferta aprovechable acota la reutilización; la distancia relativa decide si más reutilización ahorra o encarece carbono), no las cifras, que son inventadas.
