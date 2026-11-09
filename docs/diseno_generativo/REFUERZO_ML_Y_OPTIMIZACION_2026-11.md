# Aprendizaje automático y optimización del refuerzo (barras, estribos, separaciones, despiece)

Fecha: 2026-11-09. Estado: investigación y una medición propia; sin motor nuevo. Lo citado de la literatura proviene de resúmenes de búsqueda web (Elicit no tiene acceso por API en este plan) y debe verificarse en el texto completo antes de apoyarse en una cifra.

## 1. Estado de los motores (auditoría de costo y CO₂)

| Elemento | Costo APU y CO₂ antes | Ahora |
|---|---|---|
| Zapata + pedestal (prismática y troncopiramidal) | sí (`diseno_zapata_pedestal`) | sí |
| Muro de contención (voladizo, contrafuertes, anclaje) | sí | sí |
| Viga | **no** (solo refuerzo) | `cantidades_costo.cantidades_viga` + `costo_co2` |
| Columna | **no** | `cantidades_costo.cantidades_columna` + `costo_co2` |
| Zapata prismática suelta, pedestal suelto | no (solo masa de acero) | se evalúan solo dentro del conjunto |
| Pilotes, muros de corte, cerchas, escaleras, nudos, losas | no existen | ver matriz |

Las cantidades de viga y columna son aproximadas y declaradas (sin traslapos, sin ganchos suplementarios, anclaje de 40 diámetros, estribo con dos ganchos de 135°): sirven para comparar alternativas, no para presupuestar (subestiman el acero real, orden de 5–15 %, sin medir).

## 2. Medición propia: cuánto pesa el detallado en una sección fija

Con `diseno_viga.disenar` (que enumera todos los detallados factibles de una sección: diámetro de barra, número de barras superiores e inferiores, estribo, separaciones) y el módulo de cantidades, sobre una viga de luz libre 5,6 m con una demanda típica (f'c 28 MPa, columnas 400 mm):

| Sección | Detallados factibles | Sobrecosto del peor frente al mejor | Rango de acero |
|---|---|---|---|
| 250×500 | 2 | 6 % | 181–203 kg |
| 300×500 | 5 | 13 % | 159–207 kg |
| 300×600 | 8 | 17 % | 117–177 kg |
| 350×600 | 8 | 12 % | 129–180 kg |
| 400×700 | 10 | 13 % | 129–193 kg |
| 300×700 | 8 | 14 % | 119–174 kg |

Mediana 13 %. Dos advertencias: (a) los resultados de DMO y DES coincidieron para esta demanda, no se interpretan como equivalencia general; (b) el costo usa las cantidades simplificadas de arriba.

**Consecuencia para el ML.** Para una viga aislada el espacio de detallado tiene entre 2 y 10 alternativas y se resuelve por enumeración exacta; un modelo aprendido no aporta ahí. El ML aporta cuando el espacio crece o se acopla: muchos elementos que comparten diámetros y longitudes, cortes de barras y traslapos a lo largo del vano, losas y muros con mallas y refuerzo variable, y estimación rápida dentro de un optimizador exterior.

## 3. Qué dice la literatura (a verificar)

- **Optimización matemática y metaheurística del detallado de vigas** (algoritmos genéticos con variables como puntos de corte del acero): hay modelos que minimizan costo, peso o ambos ([Engineering Structures](https://www.sciencedirect.com/science/article/abs/pii/S0141029621010117)); también multiobjetivo costo–CO₂–fisuración con NSGA-II ([ResearchGate](https://www.researchgate.net/publication/371850061_Towards_Sustainable_Reinforced_Concrete_Beams_Multi-objective_Optimization_for_Cost_CO_Emission_and_Crack_Prevention)).
- **Aprendizaje por refuerzo profundo (DDPG)** para dimensiones de la viga y refuerzo de momento negativo, con el refuerzo positivo por ecuación (Jeong y Jo, 2021, *Computer-Aided Civil and Infrastructure Engineering* 36(12):1508–1529; [resumen](https://experts.arizona.edu/en/publications/deep-reinforcement-learning-for-automated-design-of-reinforced-co/)); trabajo posterior de viga de bajo carbono con el mismo enfoque ([ResearchGate](https://www.researchgate.net/publication/395894318_Intelligent_low_carbon_reinforced_concrete_beam_design_optimization_via_deep_reinforcement_learning)).
- **Colisiones de barras en nudos** con aprendizaje por refuerzo multiagente y BIM: cada barra es un agente que se enruta ([ISARC 2019](https://www.iaarc.org/publications/2019_proceedings_of_the_36th_isarc/automated_clash_resolution_of_rebar_design_in_rc_joints_using_multi_agent_reinforcement_learning_and_bim.html)).
- **Corte de barras como problema de corte unidimensional (1D-CSP):** con longitudes comerciales de 12 m el desperdicio reportado va de 2,7 % a 14,5 % según el estudio; un caso con programación lineal entera redujo el desperdicio de DB25 de 17,1 % a 1,95 % ([Sustainability 12(15):5950](https://mdpi.com/2071-1050/12/15/5950) y estudios relacionados); también hay trabajos con algoritmos genéticos ([Can. J. Civ. Eng.](https://www.sciencegate.app/document/10.1139/l03-101)). Los traslapos limitan la reducción del desperdicio.
- Sin resultados en la búsqueda para separación de estribos con sustituto, ni para generación profunda de despieces completos.

## 4. Propuesta por niveles (de mayor a menor certeza de valor)

1. **Optimización exacta con cantidades reales (sin ML).** Enumerar detallados factibles y elegir por costo + λ·CO₂ con `cantidades_costo`; añadir como variables la longitud de corte de barras, traslapos y estandarización de diámetros. Es la línea base contra la que se mide cualquier ML.
2. **Despiece y corte (1D-CSP) a nivel de proyecto.** Programación lineal entera o generación de columnas sobre las longitudes que salen de los motores, con longitudes comerciales de 6, 9 y 12 m. Aquí el ahorro es de obra (desperdicio) y no aparece en el costo por elemento. Es el candidato de mayor retorno y no requiere aprendizaje.
3. **Estandarización entre elementos.** Penalizar la variedad de diámetros y de separaciones de estribos por proyecto (menos referencias de acero, menos errores de montaje). Se formula como optimización con una penalización combinatoria; el ML sirve de heurística de arranque.
4. **Sustituto del detallado para losas, muros y marcos completos.** Cuando el espacio crece (mallas, refuerzo variable por franja, cortes escalonados) se entrena LightGBM o una red pequeña sobre las etiquetas del optimizador exacto, con el mismo contrato de guardia que zapata y muro: el modelo propone, el verificador determinista decide.
5. **Aprendizaje por refuerzo para colisiones en nudos y geometría 3D.** Útil solo con modelo BIM de armado; requiere datos que hoy no existen en el repositorio. Último en prioridad.

**Variables discretas.** Diámetros del catálogo (#3 a #8 en el motor de vigas; hasta #11 en el de contrafuertes), número de barras y separaciones redondeadas a 25 mm: el modelo propone y se redondea al catálogo antes de validar, como en el kit común (issue de kit compartido).

## 5. Datos y validación

- Etiquetas: el optimizador exacto de cada motor, con la métrica de brecha de criterio ya usada en zapata.
- Realidad: planos de despiece de obras (cuando haya autorización) para medir el sesgo de las cantidades simplificadas; sin ellos el costo del refuerzo es comparativo, no absoluto.
- Métricas: sobrecosto frente al óptimo exacto, fracción de diseños inseguros (debe ser 0 por la guardia), desperdicio de corte y número de referencias de acero por proyecto.

## 5b. Métricas de detallado (2026-11-09) y huecos medidos

`packages/motor-concreto/src/metricas_refuerzo.py`: η_acero = As_prov/As_req (As_req despejado de φMn = Mu), separación libre exigida max(db, 25 mm, 4/3·TMN), holgura de confinamiento frente a C.21.5.3.2, desperdicio de corte 1D (primer ajuste decreciente, cota superior) y costo de mano de obra con tarifa suministrada (no se fija un valor por defecto). Hipótesis: el 4/3·TMN es la lectura de C.3.3.2 (el numeral llega truncado en el corpus; C.7.6.1 sí está completo).

Medición sobre las secciones de la sección 2 (demanda de prueba de los tests, f'c 28 MPa, 41 detallados factibles por nivel):

| Métrica | Resultado |
|---|---|
| η superior | mediana 1,24 (mín 1,00; máx 1,52) |
| η inferior | mediana 1,83 (máx 2,77); lo fijan la relación M⁺/M⁻ en la cara y el redondeo entero de barras, no la demanda de flexión |
| Detallados que dejan de cumplir al exigir 4/3·TMN | 0 con TMN 19 mm; 3 de 41 con TMN 25 mm |
| Confinamiento (DMO y DES) | s_conf / límite normativo, mediana 0,94 |

Lectura: el motor actual no incumple con TMN de 19 mm, pero sí con 25 mm en 3 de 41 casos, por lo que conviene pasar el TMN como dato. Los números 1,02–1,06 de la propuesta pegada son metas no verificadas; con una demanda de prueba no se puede afirmar qué η alcanzaría un optimizador con diámetros mixtos.

## 5c. Despiece 1D a nivel de proyecto (2026-11-09, issue #127)

`packages/motor-concreto/src/despiece_proyecto.py`: reúne las barras longitudinales de todos los elementos por diámetro, parte las que exceden la barra comercial máxima con traslapo (40·db, hipótesis) y resuelve el corte con programación entera sobre patrones maximales (`scipy.optimize.milp`), con óptimo probado en los casos medidos.

Medición sobre un proyecto **sintético** (60 vigas de luces 3,2–7,8 m generadas con `disenar`, DMO, f'c 28 MPa, mejor diseño por acero; 363 barras; longitudes comerciales 6, 9 y 12 m como supuesto):

| Diámetro | Longitud útil | Compra, primer ajuste decreciente | Compra, ILP | Desperdicio FFD → ILP |
|---|---|---|---|---|
| #5 | 1.440,6 m | 1.836 m | 1.476 m | 21,5 % → 2,4 % (≈ 561 kg menos) |
| #7 | 279,2 m | 315 m | 315 m | 11,4 % → 11,4 % |
| #8 | 656,2 m | 840 m | 840 m | 21,9 % → 21,9 % |

Cautelas: (a) el proyecto es sintético, no hay planos reales; (b) el primer ajuste compra la barra más corta que aloja cada pieza nueva, una línea base débil: la comparación honesta frente a obra es contra "todo de 12 m"; (c) donde las piezas son largas (#7, #8: 7–8 m) ninguna longitud comercial 6/9/12 permite mejorar y el desperdicio es estructural; ahí el ahorro viene de ajustar la luz o los empalmes, no del corte; (d) no hay ganchos de despiece ni mermas.

## 5d. Línea base de 6 m, figuras y verificación NSR-10 (2026-11-09, issue #127)

**Longitudes comerciales (verificado en catálogos, no en el mercado local).** Aceros Arequipa Colombia publica barras de 6, 9 y 12 m; Ternium Colombia, 6 y 12 m (9 m en algunos diámetros); Aceros Crea, 12 m. Diaco y Gerdau no aparecieron en la búsqueda. Ferretería suele vender 6 m. Los precios por longitud y el sobreprecio de figurado o de largos especiales **no se encontraron**: la comparación usa el mismo COP/kg en todos los escenarios.

**Qué dice la NSR-10 (verificado en `nsr10_chunks`) y está implementado en `figuras_acero.py`:**

| Tema | Numeral | Regla |
|---|---|---|
| Gancho 180° | C.7.1.1 | + 4db, no menor que 65 mm |
| Gancho 90° | C.7.1.2 | + 12db |
| Gancho de estribo, #8 y menores | C.7.1.3 | 135° + 6db (se usa ≥ 75 mm en estribos sísmicos) |
| Diámetro de doblado | C.7.2.2, Tabla C.7.2 | estribos #5 y menores 4db; #3 a #8 6db (barras > #8: fila no recuperada, no soportadas) |
| Longitud de desarrollo en tracción | C.12.2.1/.2 | fy/(2,1·√f'c)·db (≤ #6) o /1,7 (≥ #7) en buenas condiciones; /1,4 y /1,1 en los demás casos; ≥ 300 mm |
| Traslapo en tracción | C.12.15.1 | clase A 1,0·ld; clase B 1,3·ld; ≥ 300 mm |
| Traslapo en compresión | C.12.16.1 | 0,071·fy·db (fy ≤ 420), ≥ 300 mm; +1/3 si f'c < 21 MPa |
| Gancho de desarrollo | C.12.5.1/.2 | 0,24·fy/√f'c·db, ≥ max(8db; 150 mm) |
| Sin traslapo | C.12.14.2.1 | barras mayores que No. 36 (#11) |
| Dovelas | C.15.8.2 | área ≥ 0,005·Ag; ≤ No. 36 |
| Estribo de dos piezas | C.21.5.3.6 | estribo con gancho sísmico + gancho suplementario con 90° alternados |

**Figuras:** recta, L, C, S (desfase), estribo cerrado, gancho suplementario y dovela, con longitud de corte descontando cada doblez. Hipótesis no recuperadas del corpus: extensión del gancho de 90° del suplementario (6db) y pendiente máxima de la S (1:6 del ACI 318, se advierte).

**Recomendación cuando el usuario no cumple.** `verificar_traslapo`, `verificar_gancho` y `verificar_diametro_doblado` devuelven el numeral, el mínimo y un valor recomendado que **nunca baja del mínimo** (se redondea hacia arriba). Optimizar desperdicio solo se hace entre alternativas que cumplen; si algo no cumple, la recomendación es subir al mínimo o evitar el empalme con una barra más larga, no ahorrar acero.

**Medición** (proyecto sintético: 60 vigas 300×600 DMO, luces 3,2–7,8 m, longitudinales + estribos, 2.308 piezas, traslapos clase B "otros casos" con f'c 28 y fy 420; COP/kg 4.151 igual en todos):

| Escenario | Compra | Desperdicio | Acero comprado | Frente a A |
|---|---|---|---|---|
| A. 6 m, corte a conveniencia | 6.912 m | 15,8 % | 9.742 kg | — |
| B. 6 m planificado (ILP) | 6.912 m | 15,8 % | 9.742 kg | 0,0 % |
| C. 6 y 12 m planificado | 6.144 m | 12,2 % | 8.886 kg | −8,8 % |
| D. 12 m planificado | 6.144 m | 12,2 % | 8.886 kg | −8,8 % |
| E. a medida hasta 18 m (supuesto) | 5.393 m | 0 % | 7.383 kg | −24,2 % |

Lectura: (1) con solo 6 m planificar no mejora al corte a conveniencia en este caso: el ahorro viene de la longitud comprada (12 m), no del algoritmo; (2) el escenario E es una **cota superior**: supone que la fábrica entrega cada pieza a medida, figurada y al mismo precio por kg, lo que no está verificado; (3) los estribos cortos (~1,55 m) pierden mucho en 6 m y se recuperan en 12 m; (4) el proyecto es sintético y sin planos reales, solo vigas.

## 5e. Transporte del acero: vehículo, combustible y CO₂ (2026-11-09, issue #127)

**Problema.** La ferretería vende varillas de 6 m, el plano pide piezas (p. ej. 185 cm) y el comprador tiene un vehículo con largo de carga limitado. Para cada pieza hay tres caminos: (a) cortarla en la tienda si cabe; (b) llevarla en un vehículo más largo; (c) empalmar con traslapo NSR-10 para que cada tramo quepa, lo que gasta más acero y lo debe aprobar el diseñador. `packages/motor-concreto/src/transporte_acero.py` (`planificar`) compara estos caminos con combustible, CO₂ de transporte y CO₂ del acero extra por empalmes.

**Datos con fuente.**
- Rendimiento diésel (ANDI 2018, recogido por UPME 2020, Tabla 6.1), km/galón en terreno plano / ondulado / montañoso: camión de 2 ejes 12,70 / 10,01 / 7,81; tractocamión de 2 ejes 8,76 / 6,76 / 5,07; de 3 ejes 6,64 / 4,92 / 3,34. Carga liviana < 10 t en rutas urbanas de tres empresas (MinTransporte 2019): 19,3 / 23,1 / 26,4 km/galón.
- CO₂ de combustión: diésel 10,2765 kg/galón (FECOC, edición 2016, mezcla B10, tomado de un anexo de la EAB); EPA 8,887 kg/galón de gasolina y 10,180 de diésel. La gasolina colombiana es E10, así que el valor real es algo menor (sin ajustar).

**Sin fuente (los aporta quien llama; no se inventaron):** rendimiento de moto, camioneta y NHR; largo y capacidad de carga de cada vehículo; reglas legales de carga sobresaliente; precio del combustible; tarifa de flete.

**Casos medidos** (traslapo clase B con f'c 21 MPa y fy 420; #4 = 1/2"):

| Caso | Resultado |
|---|---|
| 10 varillas de 1/2" → 30 piezas de 185 cm, moto con 2 m de carga | corte en tienda, 3 piezas por varilla (7,5 % de desperdicio), 55 kg; 10 km ida y vuelta: 0,12–0,25 gal y 1,1–2,2 kg CO₂ según rinda la moto entre 160 y 80 km/gal (valores de sensibilidad, no medidos) |
| 8 barras de 5,6 m (viga), moto de 2 m, sin permitir empalmes | inviable: hay que usar un vehículo más largo o entrega a domicilio |
| Las mismas 8 barras, empalmando para que quepan en la moto | 32 empalmes de 1,08 m, 78,9 kg de acero en vez de 44,5 (+34,4 kg, +77 %) y +45,5 kg CO₂e del acero extra |
| Las mismas 8 barras, camión de 2 ejes (12,70 km/gal), 10 km | 1 viaje, 0,79 gal, 8,1 kg CO₂; a 30 km, 24,3 kg CO₂ |

**Lectura.** Cuando la pieza cabe en el vehículo, cortar en la tienda es lo mejor (3 piezas de 185 cm por varilla de 6 m dejan 45 cm de sobrante). Cuando no cabe, empalmar para que la barra entre en una moto cuesta 45 kg CO₂e de acero extra frente a 8 kg CO₂ de un viaje en camión a 10 km (en esta medición, y solo si el empalme fuera aceptable en esa barra, que no se evaluó estructuralmente). El empalme no se recomienda para ahorrar transporte salvo que lo apruebe el ingeniero diseñador. Los viajes de la moto salen de una capacidad de carga ilustrativa de 40 kg, no medida.

**Parque automotor por ciudad.** No hay en datos abiertos un cuadro de camiones por tipología y municipio: los boletines del RUNT solo traen totales nacionales y matrículas por clase, y el desglose detallado se pide por solicitud formal a la concesión RUNT. El estudio de UPME 2020 caracteriza el parque de carga (camión, tractocamión, volqueta) pero no por municipio. Siguiente paso: solicitar el RUNT por municipio y clase (Barranquilla, Soledad, Bogotá, Medellín, Cali) y ligar cada ciudad a la tipología de vehículo disponible para alquiler.

## 5f. Flota de obra por configuración y viajes discretos (2026-11-09, issue #127)

`packages/motor-concreto/src/flota_construccion.py`: catálogo de cinco configuraciones (camión liviano, volqueta sencilla, C3/mixer, minimula, tractomula) tomado de una tabla aportada por el usuario, con la función escalón de viajes (`viajes`, `viajes_mixer`), emisión por km y por tonelada-km, factor de terreno y conexión con `transporte_acero.planificar`.

**Contraste con fuentes.** Los rangos de km/galón de la volqueta sencilla (9–11), la minimula (5,5–7) y la tractomula (4,5–6) quedan dentro de los rangos de ANDI 2018 para camión de 2 ejes y tractocamión de 2 y 3 ejes (plano a montañoso). El camión liviano (14–18) queda por debajo del 19,3–26,4 medido en rutas urbanas de tres empresas (MinTransporte 2019): es conservador. C3/mixer no tiene fuente de rendimiento. Las emisiones por km y por ton-km de la tabla reproducen la división del factor de CO₂ (10,2765 kg/gal) entre el rendimiento y la carga media, con viaje cargado y **sin retorno vacío**.

**Un error de la tabla pegada.** El ejemplo de la zapata de 16,2 t dice que caben en un mixer de 8 m³ y que "basta 1 viaje (7,5 m³)": 16,2 t con 2,4 t/m³ son 6,75 m³; 7,5 m³ son 18 t. La conclusión (1 viaje, y 2 viajes para 21 t = 8,75 m³) se mantiene y está en las pruebas.

**Límites oficiales (verificados).** Resolución 20223040045295 de 2022, Resolución Única Compilatoria de Tránsito, arts. 4.3.3.7 a 4.3.3.10 (compilan la Res. 4100/2004 con las Res. 2888/2005 y 1782/2009). Ancho máximo 2,60 m y altura 4,40 m (con el vehículo descargado). Longitud máxima: designación 2, 10,80 m; 3 y 4, 12,20 m; combinaciones con semirremolque, remolque o remolque balanceado, 18,50 m. Peso bruto vehicular (kg): 2 = 17.000; 3 = 28.000; 2S1 = 27.000; 2S2 = 32.000; 2S3 = 40.500; 3S1 = 29.000; 3S2 = 48.000; 3S3 = 52.000. Peso por eje: sencillo 6.000 (2 llantas) u 11.000 (4 llantas); tándem 11.000 / 17.000 / 22.000 (4 / 6 / 8 llantas); trídem 16.500 a 24.000. Una copia anterior de la 4100 (con la 1782/2009) decía 16.000 kg para la designación 2: se usa la compilación de 2022. La carga útil del catálogo queda por debajo del PBV legal en las cinco configuraciones (la diferencia es la tara), comprobado en pruebas. La nomenclatura (primer dígito: ejes del camión o tracto; S semirremolque; R remolque; B balanceado) está en el art. 3 de la 4100 y remite a la NTC 4788, cuyo texto no se obtuvo.

**Carga larga y moto.** La compilación define carga extradimensionada como carga **indivisible** que excede la carrocería; la varilla es divisible, así que ese régimen no aplica. No se encontró en estos textos la distancia que puede sobresalir una carga. Referencias periodísticas (no normativas): señalizar la carga que sobresale con trapo rojo de día y luz roja de noche, y llevar en moto carga excesiva o sobredimensionada es multa tipo C (15 SMLDV) con posible inmovilización, con vigas de construcción entre los ejemplos no permitidos. El texto de la Ley 769 de 2002 sobre carga sobresaliente falta por verificar; hasta entonces el largo de carga de una moto debe tomarse como el largo del vehículo sin sobresalir.

**Sigue abierto:** consumo por terreno del SICE-TAC (ninguna fuente accesible trae la tabla; se usa el factor de terreno de ANDI 2018) y parque de carga por municipio (el RUNT solo publica totales nacionales; cifra de 2020 de UPME con datos RUNT: 378.592 vehículos de carga, 71 % camiones, edad media mayor de 22 años; sin desglose para el Atlántico).

## 5g. Mezcla de camiones por territorial (INVIAS, 2006–2011) (2026-11-09, issue #127)

Fuente: libro `1922-cuadros-trafico-promedio-diario.xlsx` descargado de INVIAS (tránsito promedio diario semanal, TPDS, por estación de conteo y territorial; el archivo original no se versiona). Se procesa con `scripts/transporte/composicion_camiones_invias.py` y deja `data/transporte/composicion_camiones_invias.csv` (3.837 filas, 868 estaciones, años 2006 a 2011). **Es un libro de Excel, no un PDF, y las series son de estaciones de conteo, no de peajes; termina en 2011.**

Mezcla de camiones 2011 (% de los camiones contados, n estaciones; clases INVIAS C-2P, C-2G, C-3-4, C-5, >C-5):

| Territorial | n | C-2P | C-2G | C-3-4 | C-5 | >C-5 |
|---|---|---|---|---|---|---|
| Atlántico | 15 | 27,7 | 24,5 | 12,9 | 9,3 | 25,6 |
| Bolívar | 17 | 20,4 | 25,1 | 17,5 | 9,7 | 27,4 |
| Magdalena | 18 | 18,1 | 22,8 | 10,8 | 9,6 | 38,8 |
| Cesar | 23 | 16,9 | 26,9 | 9,3 | 7,9 | 39,0 |
| Antioquia | 49 | 28,0 | 38,1 | 13,9 | 6,3 | 13,8 |
| Cundinamarca | 46 | 31,3 | 33,4 | 11,8 | 8,4 | 15,0 |
| Valle | 57 | 24,7 | 29,8 | 13,6 | 10,4 | 21,6 |
| Total (22 territoriales) | 569 | 26,0 | 31,1 | 12,1 | 9,4 | 21,4 |

Lectura: en la Costa Caribe (Atlántico, Bolívar, Magdalena, Cesar) la proporción de camiones de más de cinco ejes es de 26 a 39 %, frente a 14–15 % en Antioquia y Cundinamarca; en el interior pesan más los camiones de dos ejes. Es la mezcla que circula por la vía, no el parque registrado ni la oferta de alquiler; la suma entre estaciones cuenta varias veces el mismo camión. La equivalencia con el catálogo (C-2P ≈ liviano, C-2G ≈ sencillo, C-3-4 ≈ C3, C-5 ≈ minimula, >C-5 ≈ tractomula) es una inferencia no verificada: las definiciones de clase no están en el libro. Datos de hace 15 años: sirven como señal de tendencia territorial, no como flota actual.

## 5h. Cruces estadísticos: peajes y contratación de obra frente a la mezcla de camiones (2026-11-09, issue #127)

Script: `scripts/transporte/cruces_peajes_secop.py` (semilla 20261109, 5.000 remuestreos bootstrap, 9.999 permutaciones). Resultados completos en `data/transporte/cruces_resultados.json`.

**Datos.** Mezcla de camiones 2011 por estación (sección 5g); tarifas por categoría I–VII de 179 peajes del recurso `68qj-5xux` de datos.gov.co (165 utilizables: se excluyen 13 sin categoría III y el peaje La Parada, con tarifa plana de $2.700 en las siete categorías); departamento del peaje por punto en polígono (DANE MGN 2018; un peaje cae fuera del polígono y se asigna al más cercano; Puerto Triunfo queda en Boyacá aunque su nombre y su vía apuntan a Antioquia, señal de ruido en las coordenadas de origen); 50.154 contratos de obra de SECOP II con valor entre 0 y $10¹² (2 descartados por valor absurdo). El campo `territorial` del recurso de peajes es un código numérico sin diccionario verificado, por eso no se usó.

**Hipótesis de trabajo (no verificadas).** Clase INVIAS → categoría de peaje por número de ejes (H0: C-2P→III, C-2G→IV, C-3-4→V, C-5→VI, >C-5→VII), con dos variantes de sensibilidad (H1, H2). Las tarifas cumplen III ≤ IV ≤ V en todos los peajes usados, pero **29 de 165 peajes (18 %) tienen la categoría III por debajo de la II**, lo que indica otra definición de categorías en esos peajes y debilita H0 justo ahí. Las tarifas no traen fecha de vigencia. Cuando una categoría pesada vale 0 se arrastra la última no nula.

### Cruce 1: tarifas de peajes y mezcla de camiones (19 departamentos con ambos datos)

| Resultado | Estimación | IC 95 % | p |
|---|---|---|---|
| T1. Tarifa de la categoría V entre departamentos (Kruskal–Wallis, 17 grupos con ≥2 peajes, n = 147) | H = 20,6; ε² = 0,035 | — | 0,19 (Holm 0,58) |
| T2. Proporción de pesados (C-5 y >C-5) frente a la forma de la tarifa R = V/III (Spearman, n = 19) | ρ = 0,11 | −0,34 a 0,51 | 0,66 (Holm 0,95) |

No hay evidencia de que los departamentos con más camiones pesados tengan un cuadro tarifario distinto, ni de que la tarifa pesada difiera más entre departamentos de lo esperable por el azar de los peajes incluidos. Con n = 19 el intervalo de T2 es ancho: no se descarta una asociación moderada de cualquier signo.

El costo esperado de peaje por paso de camión (suma de la proporción de cada clase por la tarifa de su categoría, bootstrap conjunto sobre estaciones y peajes) va de unos $31.600 a $44.900 según el departamento (H0). **Crece por construcción con la proporción de pesados** porque los pesados pagan más, así que no se contrasta contra ella: la correlación descriptiva (ρ = 0,25 con H0; 0,18 con H1; 0,39 con H2) es circular y no es un hallazgo. Casanare y Quindío tienen un solo peaje, así que su intervalo solo recoge la variación de estaciones.

**Atlántico.** Con los seis peajes el costo esperado es $44.925 (IC 36.404–58.906) y R = 4,06, el mayor del país. Cuatro de esos seis (Galapa 02, Juan Mina, Puerto Colombia y Papiros) tienen el cuadro atípico (III < II, V ≈ 5 × III). Con solo los dos peajes de cuadro regular (Sabanagrande, Galapa) el costo baja a $39.813 (IC 37.232–41.681; H1 $38.658; H2 $37.746), dentro del rango de otros departamentos. La "prima" del Atlántico no es robusta: depende de cómo se interpreten las categorías de cuatro peajes.

**Efecto del cambio de mezcla 2006 → 2011 con tarifas fijas (estaciones comunes, bootstrap pareado).**

| Ámbito | Estaciones comunes | Δ proporción de pesados | Δ costo por paso (H0) |
|---|---|---|---|
| Atlántico | 13 | +12,9 pp (IC 5,3 a 19,3) | +$7.261 (IC 4.588 a 9.755) |
| Bolívar | 17 | +1,3 pp (−2,3 a 4,6) | +$928 (102 a 1.855) |
| Antioquia | 48 | −1,2 pp (−3,2 a 0,9) | −$277 (−1.060 a 536) |
| Cundinamarca | 45 | +0,7 pp (−2,6 a 3,8) | −$10 (−1.359 a 1.335) |
| Total nacional | 530 | +1,6 pp (0,1 a 3,0) | +$501 (91 a 894) |

El aumento de pesados en Atlántico (de 12,4 % a 26,0 % en la comparación anterior, sección 5g) se sostiene con intervalo que excluye cero y es la única variación grande entre territoriales con muestra amplia. Con 13 estaciones y estaciones de conteo no aleatorias, es evidencia fuerte de cambio en esos puntos, no una estimación del departamento entero. El costo en pesos usa tarifas actuales sobre una mezcla de 2006 y 2011: mide el efecto de la mezcla, no el gasto histórico real.

### Cruce 2: contratación de obra (SECOP II) y mezcla de camiones (21 departamentos)

Se excluye la territorial Ocaña porque no se verificó su equivalencia con un departamento. Bogotá se suma a Cundinamarca. Los contratos son de 2016–2026 y la mezcla de 2011: el desfase es de 5 a 15 años.

| Resultado | Estimación | IC 95 % | p (permutación) |
|---|---|---|---|
| T3. Valor contratado en obras viales frente a proporción de pesados, controlando el número de estaciones (Spearman parcial, n = 21) | ρ = 0,56 | 0,19 a 0,83 | 0,012 (Holm 0,047) |
| Mismo cálculo sin controlar | ρ = 0,49 | — | — |
| T4. Cuota vial del valor total frente a pesados (Spearman, n = 21) | ρ = 0,16 | −0,38 a 0,62 | 0,48 (Holm 0,95) |

La asociación T3 existe, pero **no es específica de las obras viales**: con el valor total contratado sale ρ parcial = 0,50 (IC 0,10 a 0,78), con intervalos que se solapan con el vial, y la cuota vial no se asocia (T4). La lectura sensata es que los departamentos con mayor volumen de contratación de obra tienden a tener más camiones pesados circulando (Cesar, Magdalena y Tolima combinan 45–48 % de pesados con contratación alta), probablemente por una causa común de escala económica y carga de materiales o minerales, no porque la obra vial genere camiones. El número de contratos, a diferencia del valor, no se asocia (ρ parcial = 0,14). Es estable al quitar un departamento a la vez (ρ parcial entre 0,49 sin Caquetá y 0,66 sin Antioquia). Pero con cuatro pruebas corregidas por Holm el p ajustado de T3 es 0,047, apenas bajo 0,05: debe leerse como exploratorio.

### Límites

Falacia ecológica (la correlación entre departamentos no dice nada sobre contratos o camiones individuales); n de 19 a 21; desfase temporal entre 2011 y 2016–2026; estaciones de conteo no aleatorias; clase de camión INVIAS ↔ categoría de peaje sin verificar y evidentemente inválida para el 18 % de peajes; tarifas sin fecha; coordenadas de peajes con ruido; el control por número de estaciones solo corrige parcialmente el tamaño del departamento (el valor total contratado se correlaciona ρ = 0,39 con el número de estaciones). Para convertir esto en resultado habría que tener la definición oficial de categorías de peaje por resolución, tarifas con fecha y mezcla de camiones reciente (pendiente de solicitud al INVIAS).

## 5i. Cruces 3 a 5: retrasos, ejecución y densidad de peajes frente a la mezcla de camiones (2026-11-09, issue #127)

Script: `scripts/transporte/cruces_secop_logistica.py` (reutiliza `cruces_peajes_secop.py`; resultados en `data/transporte/cruces_secop_logistica.json`). El predictor es siempre la proporción de camiones pesados (C-5 y >C-5) de 2011 del departamento, de modo que **todo efecto es ecológico**: describe departamentos, no contratos individuales, y no establece causa.

**Cruce 3. Contrato: prórroga, suspensión y adición de valor.** Logit sobre 40.278 contratos de obra de 21 departamentos (de 50.154: se pierden los de duración no interpretable, 4.871 con «Dia(s)» sin número o «No definido», los sin fecha de firma y los de departamentos sin mezcla). Controles: log del valor, log de la duración, obra vial, modalidad, pyme y **año de firma** (los contratos recientes no han tenido tiempo de acumular prórrogas). Errores agrupados por departamento con inferencia t de 20 grados de libertad (21 grupos son pocos; la normal habría dado p más pequeños).

| Resultado | Tasa | OR por +10 pp de pesados | IC 95 % | p (t, 20 gl) | p Holm (6 pruebas) |
|---|---|---|---|---|---|
| Prórroga (días adicionados > 0) | 29,3 % | 1,144 | 1,039 a 1,260 | 0,009 | 0,043 |
| Suspensión | 19,8 % | 1,295 | 1,011 a 1,659 | 0,041 | 0,147 |
| Adición de valor | 8,7 % | 1,000 | 0,869 a 1,150 | 0,997 | 0,997 |

La prórroga es robusta: al quitar cada departamento por turno el OR queda entre 1,12 (sin Magdalena) y 1,17 (sin Cesar) y los 21 casos tienen p < 0,05. No es un efecto Caribe: la tasa de prórroga es 30,1 % en el Caribe y 27,5 % en el resto, y la correlación entre departamentos (ρ = 0,45, p = 0,04) es de magnitud parecida a la del modelo de contrato. La suspensión no es robusta (14 de 21 casos leave-one-out con p < 0,05; sin Cundinamarca p = 0,19) y no sobrevive a Holm. Las adiciones de valor no se asocian. Lectura prudente: los departamentos con más tráfico pesado tienden a tener más contratos de obra con plazos ampliados, el odds de prórroga es ~14 % mayor por cada 10 puntos porcentuales adicionales de pesados. Mecanismos plausibles (logística de materiales, estado de las vías, clima) no se pudieron separar de confusores de región (seguridad, capacidad institucional) con los datos locales.

**Cruce 4. Ejecución: avance real frente a esperado.** En el 86 % de los 7.624 registros «Confirmado» con ambos valores, el avance real es idéntico al esperado, lo que sugiere autollenado: la brecha mediana es 0 en todos los departamentos y no sirve. Se usó la proporción de registros con atraso (real < esperado), 8,5 % en el país y de 0 a 16,2 % por departamento (15 departamentos con ≥ 30 registros). Spearman parcial con pesados, controlando estaciones: ρ = 0,56 (IC 0,02 a 0,87), p = 0,040, **Holm 0,147**. Sugerente y coherente con el cruce 3, pero débil y dependiente de la calidad del reporte.

**Cruce 5. Densidad de peajes.** Los peajes por departamento se asocian fuertemente con el valor contratado en obra vial (ρ parcial = 0,85, IC 0,61 a 0,95, p < 0,001, Holm 0,001) pero eso es **escala**: los peajes siguen el volumen total de contratación (ρ = 0,85) y, al controlar por el valor total en vez de por estaciones, el efecto específico vial cae a ρ = 0,46 con IC de −0,23 a 0,82 (cruza cero). Con pesados: ρ parcial = 0,47 (IC 0,01 a 0,77), p = 0,037, Holm 0,147.

**Qué se sostiene y qué no.** Se sostiene la asociación de pesados con prórroga (robusta, Holm 0,043). Son exploratorios la suspensión, la proporción de atraso y los peajes con pesados (Holm 0,147). Son efecto de escala, no de causa vial, los peajes con obra vial (como ya ocurría con SECOP en 5h). No hay efecto sobre adiciones de valor.

**Límites.** Falacia ecológica; 21 grupos; mezcla de 2011 frente a contratos 2016–2026; la proporción de pesados puede ser un indicador de la estructura económica del departamento (minería, agroindustria, comercio exterior) más que del tráfico en sí; la duración «Dia(s)» sin número excluye ~10 % de los contratos; el campo de avance parece autollenado; sin covariables departamentales (pobreza, capacidad fiscal, seguridad) cargadas localmente. Siguiente paso útil: incorporar covariables del DNP o DANE y repetir el logit con efectos aleatorios.

## 5j. Prórrogas y pesados con covariables económicas departamentales (2026-11-09, issue #127)

Script: `scripts/transporte/cruces_covariables.py`; resultados en `data/transporte/cruces_covariables.json`. Pregunta: ¿la asociación de 5i sobrevive al control por escala y estructura económica del departamento? Covariables: PIB departamental a precios constantes de 2015 (DANE, recurso `kgyi-qc7j` de datos.gov.co), promedio 2016–2023: log del PIB total y participación de minería, agro, industria y construcción (Bogotá se suma a Cundinamarca).

**Método en dos etapas.** Con 21 departamentos la inferencia de efectos aleatorios es frágil. Etapa 1: logit de contrato (40.278 contratos) con efectos fijos de departamento y los controles de 5i, que da un efecto de prórroga ajustado por departamento con su error. Etapa 2: regresión ponderada por 1/ee² de ese efecto sobre pesados (+10 pp) y covariables estandarizadas, con inferencia t de G − k grados de libertad.

Las covariables casi no se correlacionan con la proporción de pesados (Spearman: log PIB 0,29; minería 0,10; agro −0,20; industria 0,22; construcción −0,32), así que no son candidatas fuertes a explicar la asociación.

| Modelo (prórroga) | OR por +10 pp de pesados | IC 95 % | p (t) | gl |
|---|---|---|---|---|
| M0 solo pesados | 1,171 | 1,018 a 1,347 | 0,030 | 19 |
| M1 + escala (log PIB) | 1,166 | 1,005 a 1,352 | 0,043 | 18 |
| M2 + escala + minería | 1,212 | 1,050 a 1,400 | 0,012 | 17 |
| M3 + escala + minería + agro | 1,215 | 1,049 a 1,407 | 0,012 | 16 |
| M4 + escala + minería + agro + industria + construcción | 1,214 | 1,031 a 1,429 | 0,023 | 14 |

La estimación de prórroga **no se atenúa** al controlar por economía (1,17 sin covariables; 1,17 a 1,21 con ellas) y es coherente con el 1,144 del logit agrupado de 5i. La hipótesis de que los pesados fueran solo un indicador de tamaño o de minería queda debilitada con estas covariables, aunque no descartada: faltan seguridad, capacidad institucional y pobreza, que no hay cargadas localmente.

**Suspensión.** Sin covariables el efecto no es distinguible de cero (OR 1,14; p = 0,22) y solo aparece al sumar covariables (OR 1,25; p = 0,026 con M4, 14 gl). Aumentar la significancia al agregar regresores, con 21 observaciones y varias especificaciones sin corregir, es señal de fragilidad, no de hallazgo: se mantiene como exploratorio, consistente con el resultado no robusto de 5i.

**Límites.** Mismos de 5i (ecológico, 21 grupos, mezcla de 2011); con k = 6 en M4 quedan 14 grados de libertad; el PIB es de 2016–2023 y los contratos de 2016–2026; no hay covariables de seguridad, pobreza ni capacidad institucional; las cinco especificaciones no son pruebas independientes ni se corrigieron entre sí. Es un chequeo de sensibilidad de una asociación ya detectada, no una nueva prueba.

## 5k. Cierre de confusores, variables nuevas disponibles y huecos por cruce (2026-11-09, issue #127)

### Cierre de covariables de seguridad y de capacidad institucional

Script: `scripts/transporte/cruces_seguridad_institucional.py`; resultados en `data/transporte/cruces_seguridad_institucional.json`. Mismo modelo en dos etapas de 5j, añadiendo cada covariable sobre M1 (pesados + log PIB). Todas salen de datos.gov.co y cubren los 21 departamentos:

- **Seguridad:** homicidios de la Policía Nacional (`m8fd-ahd9`), 2016–2025, por cada 100 mil personas de 5 a 16 años.
- **Capacidad institucional:** índice de desempeño institucional MIPG/FURAG de las alcaldías (`gfs5-jqxi`), promedio por departamento.
- **Amenazas hidrometeorológicas:** emergencias UNGRD por inundación, deslizamiento, avenida torrencial, creciente, vendaval o movimiento en masa (`wwkg-r6te`, solo 2019–2022), por 100 mil personas de 5 a 16 años.
- **Inversión en transporte:** log del valor de proyectos SGR del sector Transporte (`mzgh-shtp`).

| Prórroga: modelo | OR por +10 pp de pesados | IC 95 % | p (t) | gl |
|---|---|---|---|---|
| M1 pesados + log PIB | 1,166 | 1,005 a 1,352 | 0,043 | 18 |
| + seguridad (homicidios) | 1,198 | 1,036 a 1,384 | 0,018 | 17 |
| + institucional (MIPG) | 1,162 | 0,996 a 1,357 | 0,056 | 17 |
| + amenazas hidro (UNGRD) | 1,205 | 1,042 a 1,394 | 0,015 | 17 |
| + inversión SGR transporte | 1,222 | 1,049 a 1,424 | 0,013 | 17 |
| conjunto: PIB + seguridad + institucional + hidro | 1,217 | 1,047 a 1,416 | 0,014 | 15 |

**La asociación de la prórroga con los pesados no se explica por ninguna de las covariables:** el OR se mantiene en 1,16 a 1,22. Con el control institucional el p sube a 0,056, en el borde de 0,05; no se puede decir que sobreviva ni que no, y ese es el confusor más relevante. Las covariables casi no se relacionan con el efecto departamental de la prórroga (Spearman: homicidios 0,22; institucional −0,15; hidro 0,17; SGR −0,03; PIB 0,16) ni con los pesados (|ρ| ≤ 0,39).

**Suspensión: no hay efecto con ninguna combinación** (p entre 0,07 y 0,22). Esto confirma que el p = 0,026 de 5j fue un artefacto de especificación y se descarta como hallazgo.

Debilidades de estas covariables, medidas o inferidas: (i) la población departamental total no está cargada, así que las tasas usan la población de 5 a 16 años del MEN como proxy de escala, válido solo si esa población es aproximadamente proporcional a la total; (ii) el recurso de emergencias UNGRD ubica a Valle del Cauca entre los de menos emergencias (36 por 100 mil, frente a 435 en Cauca), lo que sugiere subregistro o diferencias de reporte y no menor amenaza; (iii) el índice MIPG se promedió sin ponderar entre municipios y años disponibles, sin verificar la cobertura temporal.

### Variables nuevas disponibles (verificadas en el catálogo de datos.gov.co)

| Recurso | Qué trae | Qué cierra | Estado |
|---|---|---|---|
| `8yi9-t44c` Tráfico Vehicular ANI | Tráfico mensual por peaje y categoría, 2014–2026; 132 peajes con datos en 2024 | Mezcla reciente con la **misma categoría que la tarifa**; elimina el mapeo clase INVIAS → categoría y el desfase de 2011 (solo concesiones ANI) | Estructura verificada; falta el cruce |
| `7gj8-j6i3` Tarifas ANI | Tarifa por peaje y categoría con `ultimofechacambiopeaje` | Fecha de vigencia de la tarifa | Ya usado sin la fecha |
| `qac6-9mkr` Recaudo Vehicular ANI | Recaudo por peaje y periodo | Costo real pagado frente al esperado | Estructura verificada |
| `atkg-vhpp` Pesaje de carga | 10,9 millones de registros: configuración (C2, 3S3, 3S2, 2S2, C3…), peso registrado, peso máximo, estación (126) | Mezcla real de carga pesada y **sobrecarga**; las configuraciones coinciden con las designaciones de la Res. 2022 usadas en `flota_construccion.py` | Rango de fechas y ubicación de estaciones sin verificar |
| `wwkg-r6te` / `rgre-6ak4` / `2343-nuqp` UNGRD | Emergencias con vías y puentes averiados | Extender 2019–2022 a 2023–2024 | Solo se usó el primero |
| `mzgh-shtp` SGR | Ejecución física y financiera por proyecto | Retrasos de obra de otra fuente | Solo se usó el valor |
| `cdw6-jexv` y hermanos SIEVCAC | Eventos del conflicto armado por municipio | Seguridad más específica que homicidios | No usado |
| `ufg7-is7r`, `ie7y-asdn` Red vial | Postes de referencia y tramos con superficie | Geolocalizar estaciones de conteo y medir superficie | No usado |
| `ubicaciones.jsonl` (caché SECOP) | Municipio de la obra frente al de la entidad | Subir n de 21 a cientos | Ya extraído, sin usar en los cruces |

### Huecos por cruce

| Cruce | Hueco | Efecto sobre la conclusión | Cómo cerrarlo |
|---|---|---|---|
| 1. Tarifas × mezcla | Clase INVIAS → categoría de peaje sin verificar. La búsqueda encuentra al menos dos esquemas: siete categorías (III y IV camiones de 2 ejes; V de 3 y 4; VI de 5; VII de 6) en una tabla INVIAS de 2021, y un esquema de cinco categorías (III = 3 y 4 ejes) en un proyecto de resolución de 2026. No leí los PDFs completos y no confirmé cuál rige. Eso no explica por sí solo los 29 peajes con III < II | Alto: invalida H0 en el 18 % de los peajes | Usar tráfico ANI por categoría con la tarifa de la misma categoría |
| 1. | Mezcla 2011 con tarifas actuales | Alto | Tráfico ANI 2014–2026 |
| 1. | Tarifas sin fecha en el análisis; coordenadas con ruido (Puerto Triunfo en Boyacá) | Medio | Usar `ultimofechacambiopeaje`; validar por nombre del tramo |
| 1. | Solo concesiones ANI cubren el tráfico por categoría; faltan los peajes INVIAS | Medio | Pedir tráfico al INVIAS |
| 2–5. | Departamento = ubicación de la entidad, no de la obra. n = 21 | **Alto**: limita todo el poder estadístico y fuerza el diseño ecológico | Usar `ubicaciones.jsonl` a nivel municipal; modelo multinivel |
| 2–5. | Predictor de 2011, contratos de 2016–2026 | Alto | Mezcla ANI o pesaje 2024 |
| 2–5. | `valor_vial` por expresión regular sin validar precisión | Medio | Muestra etiquetada a mano |
| 3. | Prórroga binaria (`dias_adicionados > 0`) sin tiempo ni causa; contratos recientes con menos exposición | Medio: se mitigó con efectos fijos de año | Análisis de supervivencia con la fecha de la modificación; separar causas |
| 3. | 10 % de contratos excluidos por duración no interpretable («Dia(s)» sin número) | Bajo a medio | Calcular duración con fecha de inicio y fin |
| 4. | Avance real = esperado en el 86 % de los registros | Alto: la variable casi no mide | Usar `valor_pagado`, `valor_facturado` y `valor_pendiente_de_ejecucion` de los contratos |
| Covariables | Población total ausente (proxy 5–16); subregistro UNGRD; MIPG sin ponderar ni verificar años | Medio | Proyecciones DANE; 2023–2024 de UNGRD; ponderar por municipio |
| Transversal | Varias especificaciones y cruces explorados sin una corrección global; Holm cubre solo cada familia | Medio | Registrar hipótesis y modelo antes del siguiente cruce; reservar datos nuevos para confirmar |

### Orden recomendado

1. Tráfico ANI × tarifas (cierra el cruce 1 completo: mapeo, desfase y fecha; bajo costo).
2. Ubicación municipal de obras y modelo multinivel (cierra el principal límite de potencia en los cruces 2 a 5).
3. Ejecución con `valor_pagado/facturado/pendiente` y prórroga como tiempo hasta el evento.
4. Pesaje de carga: sobrecarga y mezcla real por configuración, previa geolocalización de las estaciones.
5. Población DANE, SIEVCAC y UNGRD 2023–2024 para completar covariables.

## 5l. Tráfico ANI por categoría: persistencia, cruce 1 corregido y réplica de la prórroga (2026-11-09, issue #127)

Script: `scripts/transporte/cruces_trafico_ani.py`; resultados en `data/transporte/cruces_trafico_ani.json`. Fuentes: tráfico vehicular mensual ANI por peaje y categoría con la tarifa aplicada (`8yi9-t44c`) y coordenadas de peajes (`68qj-5xux`, unión por nombre normalizado: 107 de 132 peajes ANI se ubican en un departamento; 25 sin coincidencia se excluyen). Tráfico y tarifa comparten categoría, así que no se necesita mapear clases INVIAS.

**Hallazgo metodológico que condiciona todo: las concesiones no usan el mismo esquema de categorías.** De 131 peajes con camiones en 2024, 78 registran tráfico en las categorías VI y VII (esquema de siete categorías: V = 3 y 4 ejes, VI = 5 ejes, VII = 6 o más). Los otros 53 (40 %) no registran tráfico en VI ni VII, y su categoría V concentra del 43 al 53 % de los camiones: ahí V agrupa tres o más ejes (esquema de cinco categorías). Mezclarlos asigna casi cero pesados a Cesar, Boyacá, Nariño y Atlántico, lo que contradice INVIAS 2011 (47, 28, 21 y 35 %) y la lógica del carbón en Cesar. Se mantienen solo los 78 con esquema de siete categorías (64 ubicados en 16 departamentos tras la unión por nombre). Esto también refuerza la advertencia del cruce 1 de 5h: la tarifa por categoría no es comparable entre peajes si no se conoce el esquema de cada uno.

**Persistencia de la mezcla (Spearman entre departamentos, pesados = (VI+VII)/(III a VII) frente a (C-5 + >C-5) de INVIAS).**

| Comparación | n | ρ | IC 95 % | p (perm.) |
|---|---|---|---|---|
| INVIAS 2011 frente a ANI 2016 | 13 | 0,16 | −0,48 a 0,70 | 0,59 |
| INVIAS 2011 frente a ANI 2024 | 14 | 0,55 | −0,01 a 0,86 | 0,043 |
| ANI 2016 frente a ANI 2024 | 14 | 0,47 | −0,25 a 0,98 | 0,095 |

La mezcla de 2011 conserva una relación moderada con la de 2024, pero con intervalos muy anchos y sin una relación visible con 2016; con 45 peajes en 2016 la muestra por departamento es mínima. Es compatible con persistencia parcial y no permite afirmar ni descartar que 2011 sea un buen proxy. (Con todos los peajes sin filtrar por esquema el ρ de 2011 frente a 2024 era −0,18: un artefacto del esquema, no una conclusión.)

**Cruce 1 corregido (pesados ANI 2024 frente a forma de tarifa R = V/III, n = 16): ρ = −0,52, IC −0,86 a 0,00, p = 0,040.** Con todos los peajes y sin filtrar el esquema el mismo cálculo daba +0,55 (p = 0,013). Un cambio de signo por una decisión de limpieza de datos indica que **no es un hallazgo**: la forma de la tarifa depende del contrato de cada concesión y las 16 observaciones no la separan de eso. El resultado nulo de 5h (INVIAS 2011, ρ = 0,11) tampoco se sostiene como evidencia de ausencia de relación.

**Réplica de la prórroga con un predictor reciente e independiente (14 departamentos con SECOP, mezcla 2011 y ANI 2024; 33.398 contratos).**

| Predictor | Modelo | OR por +10 pp | IC 95 % | p (t) | gl |
|---|---|---|---|---|---|
| INVIAS 2011 | solo pesados | 1,182 | 0,976 a 1,432 | 0,082 | 12 |
| INVIAS 2011 | + log PIB | 1,174 | 0,961 a 1,434 | 0,106 | 11 |
| ANI 2024 | solo pesados | 1,014 | 0,867 a 1,185 | 0,853 | 12 |
| ANI 2024 | + log PIB | 1,017 | 0,866 a 1,195 | 0,820 | 11 |

**La asociación entre pesados y prórrogas no se replica con la mezcla de 2024.** Con el predictor INVIAS 2011 el OR se mantiene en 1,17 a 1,18 (ya no significativo por tener solo 14 departamentos), pero con ANI 2024 es 1,01 (IC 0,87 a 1,19). Como el IC de ANI incluye el 1,17 de 5i, no se refuta con rigor: hay poco poder y ANI cubre solo concesiones. Pero tampoco hay apoyo: lo que 5i, 5j y 5k llamaron "se sostiene" debe leerse como **no replicado**. Que el resultado dependa de qué fuente y qué año mide los pesados es compatible con que lo capturado por la mezcla INVIAS 2011 sea algo más específico (qué estaciones se contaron, estructura regional de entonces) que el flujo de carga pesada actual.

**Qué cambia en las conclusiones anteriores.** La prórroga como asociación departamental robusta a covariables (5i a 5k) queda como un hallazgo de una sola fuente, no replicado. La suspensión sigue sin efecto. Los resultados de escala (peajes y contratación de obra) no dependen del predictor de pesados y siguen en pie.

**Pendiente para decidir.** Una réplica con más poder exige la ubicación municipal de las obras (n de 16 a cientos), peajes INVIAS con categoría por esquema, y el pesaje de carga (`atkg-vhpp`) como medida independiente de la mezcla reciente.

## 6. Qué no hace este documento

No prueba que un modelo aprendido supere a la enumeración exacta para vigas aisladas (la medición de la sección 2 sugiere que no); no valida las cantidades contra planos reales; no incluye traslapos ni ganchos suplementarios.
