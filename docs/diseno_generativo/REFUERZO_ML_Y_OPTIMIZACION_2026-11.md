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

## 6. Qué no hace este documento

No prueba que un modelo aprendido supere a la enumeración exacta para vigas aisladas (la medición de la sección 2 sugiere que no); no valida las cantidades contra planos reales; no incluye traslapos ni ganchos suplementarios.
