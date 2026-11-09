# L1. Optimización estructural multiobjetivo: costo, seguridad normativa y carbono

Estado: **Fase 0, protocolo (9 de noviembre de 2026).** No se ha ejecutado ningún análisis ni se ha escrito código para esta línea. Los umbrales marcados «a fijar» se congelan **antes** de la primera corrida y se registran con fecha; después no se modifican sin una enmienda escrita.

Marco general: [#98](https://github.com/wilmerjoseperezorozco-dev/structai/issues/98) (capa de optimización multiobjetivo, cuyo primer piloto es vial). Esta línea es la contraparte estructural.

## 1. Pregunta e hipótesis

**Pregunta.** ¿Una optimización que considera a la vez costo, cantidades, emisiones y holgura normativa encuentra diseños de pórticos de concreto reforzado más baratos y de menor huella que el diseño convencional, sin empeorar su seguridad normativa?

**H1 (de no inferioridad).** Para un conjunto de pórticos preregistrado, el diseño elegido de la frontera de Pareto, frente al diseño convencional:

1. reduce el costo directo APU en al menos *Δc* (a fijar);
2. no aumenta la probabilidad de incumplimiento normativo en más de *δ* (a fijar), medida con la definición del apartado 4;
3. no empeora la deriva máxima ni la razón demanda/capacidad máxima más allá de lo que fija la norma (cada diseño cumple NSR-10 de forma determinista; la hipótesis es sobre la *holgura*, no sobre el cumplimiento).

**Alcance real de la afirmación.** Los precios son los de Barranquilla (APU 2026) y los factores de emisión son A1–A3 (cemento: EPD Argos Cartagena; resto: Pardo 2022). La hipótesis se enuncia, por tanto, para pórticos de concreto de la costa Caribe colombiana con esos precios y factores; extenderla a «Colombia» exigiría precios y factores de otras regiones. La zona sísmica sí varía por municipio.

## 2. Motores y lo que ya existe

| Pieza | Estado hoy |
|---|---|
| `orquestador/diseno_integral` | Evalúa en bloque (vectorizado) toda la rejilla de secciones de viga y columna con deriva A.6.4, estabilidad Q, columna fuerte–viga débil, costo APU y reanálisis escalar del óptimo. **Minimiza solo el costo.** |
| `motor-analisis` | Análisis del pórtico plano y combinaciones. |
| `motor-concreto` | Verificación del Título C, `cantidades_costo` (acero y concreto de vigas y columnas, CO₂e), `economia_concreto`. |
| `motor-apu` | Precios de Barranquilla. |
| `muro_pareto` | Frontera costo–CO₂e de un **muro** barriendo un precio sombra λ. Sirve de antecedente, no de método (ver apartado 5). |

**Lo que falta**
- Un resultado por candidato con masa de acero, masa de concreto y CO₂e agregados a nivel de pórtico (hoy `CandidatoIntegral` trae costo, deriva, Q y razón columna fuerte–viga débil, pero no cantidades ni emisiones).
- Las razones demanda/capacidad máximas por tipo (flexión, flexo-compresión, cortante) como salida explícita.
- La frontera de Pareto a nivel de pórtico.
- La medida de probabilidad de incumplimiento (apartado 4).
- El registro de evidencias de cada corrida (entradas, versión de norma, hash del código, semilla).

## 3. Objetivos y variables

- **Objetivos a minimizar:** costo directo APU (COP); masa total de acero y de concreto (kg); CO₂e A1–A3 (kg); deriva máxima Δ/hp; razón demanda/capacidad máxima (cuanto menor, mayor holgura).
- **Variables de decisión:** lado de columna, base y altura de viga, resistencia del concreto, cuantías y diámetros resultantes del diseño exacto. Una sola sección de viga y una de columna por pórtico (supuesto heredado del motor).
- **Restricciones:** todas las verificaciones de NSR-10 que hoy aplica el motor (deriva 1,0 % hp, Q, columna fuerte–viga débil, flexo-compresión, cortante por capacidad, confinamiento).

## 4. Probabilidad de incumplimiento: definición que hay que fijar

La verificación normativa es **determinista y binaria**: un diseño cumple o no. Por sí sola no da una «probabilidad». Para que H1 sea comprobable se define:

> *P_inc(d)* = fracción de realizaciones de Monte Carlo, con la semilla preregistrada, en las que el diseño *d* incumple al menos una verificación cuando se perturban las entradas inciertas.

Entradas inciertas y distribuciones: **a fijar y documentar con su fuente** (resistencia real del concreto y del acero, sobrecarga viva, módulo de elasticidad, amplitud de la demanda sísmica). No se inventan distribuciones: se toman de literatura citada o se declaran como supuesto de sensibilidad y se barren.

**Riesgo conocido, y por eso la holgura es un objetivo.** Un diseño de costo mínimo queda pegado a la restricción: cumple por poco y, en cuanto se perturban las entradas, su *P_inc* sube. Minimizar el costo sin controlar la holgura tiende a aumentar *P_inc*. Incluir la razón demanda/capacidad máxima como objetivo es lo que permite que la frontera exhiba el intercambio en vez de ocultarlo. Es plausible que H1 no se sostenga con *δ* pequeño; ese resultado es válido y se reporta.

El Monte Carlo se corre **solo sobre los candidatos finales**, no en cada evaluación del optimizador.

## 5. Método

1. **Frontera exacta por enumeración.** El motor ya evalúa toda la rejilla declarada; con eso se calcula el conjunto de soluciones no dominadas sin un algoritmo heurístico. Un barrido de precio sombra λ solo alcanza los puntos del casco convexo y puede perder puntos de la frontera real; por eso no se usa como método principal. NSGA-II queda reservado para el caso en que se amplíe el espacio de variables más allá de lo enumerable.
2. **Selección de puntos.** Se reportan puntos nombrados y fijados de antemano (por ejemplo, mínimo costo, mínimo CO₂e, mejor holgura y un compromiso por criterio declarado), no una elección posterior al ver los resultados.
3. **Validación determinista final.** Cada punto elegido se reanaliza con la ruta escalar de referencia, independiente de la ruta vectorizada, y se vuelve a verificar completo contra el Título C y el Título A. Un punto que no pasa se descarta y se cuenta.
4. **Comparación con dos líneas base**, fijadas antes de correr:
   - **B0, diseño convencional:** secciones por predimensionamiento de práctica corriente, con la regla escrita y citada, diseñadas con el mismo motor.
   - **B1, mínimo costo con cumplimiento:** lo que hace hoy el motor. Aísla el efecto de añadir objetivos; B0 mide el efecto de optimizar en general.
5. **Conjunto de casos preregistrado.** Matriz de pórticos (luces, número de pisos, municipio y zona sísmica, perfil de suelo, capacidad de disipación DMI/DMO/DES). El número de casos y la regla de selección se congelan antes de ejecutar; análisis pareado por caso, tamaño de efecto con intervalo bootstrap, y se reportan los casos en que no hay mejora.

## 6. Resultados que se reportarán

Por caso y por línea base: costo, masa de acero y de concreto, CO₂e, deriva, razón demanda/capacidad máxima por tipo y *P_inc*. Más la frontera completa de cada caso y el número de candidatos evaluados, factibles y descartados en la validación final.

## 7. Límites declarados desde el inicio

- Pórtico plano, sin torsión ni P-Delta en la deriva; una sección de viga y una de columna en todo el pórtico; sin diseño de nudos, cimentación, losas ni empalmes (supuestos vigentes del motor).
- El óptimo lo es sobre la rejilla declarada, no sobre todos los diseños posibles.
- Los resultados valen **dentro del modelo**. Un optimizador explota los errores del modelo; por eso la validación final y la retro-validación contra ejemplos publicados son obligatorias antes de confiar en una propuesta.
- Costos A1–A3 sin transporte, construcción ni fin de vida.
- La salida es una propuesta para revisión del ingeniero responsable, con el aviso de responsabilidad profesional del [#18](https://github.com/wilmerjoseperezorozco-dev/structai/issues/18). No sustituye el criterio profesional.

## 8. Fases

| Fase | Contenido | Condición para pasar |
|---|---|---|
| 0 | Este protocolo | Congelar *Δc*, *δ*, distribuciones, conjunto de casos y reglas de B0 |
| 1 | Cantidades, CO₂e y razones demanda/capacidad como salida de `diseno_integral` | Pruebas contra cálculo a mano |
| 2 | Frontera exacta por enumeración y un caso piloto con retro-validación | El piloto reproduce un ejemplo publicado |
| 3 | Monte Carlo de incumplimiento sobre los candidatos finales | Distribuciones documentadas |
| 4 | Matriz de casos y análisis preregistrado | Protocolo congelado |
| 5 | Informe, con nulos incluidos | |

## 9. ¿Llegará a ser un motor?

No automáticamente. Según el criterio de [`CLASIFICACION_HIPOTESIS_Y_MOTORES_2026-11.md`](../CLASIFICACION_HIPOTESIS_Y_MOTORES_2026-11.md), una hipótesis es evidencia, no un motor. La Fase 1 sí produce funciones reutilizables (cantidades, CO₂e, razones) que irían como motor con contrato `ResultadoMotor`; el resultado de H1 se publica como hallazgo, con su límite, tanto si se cumple como si no.
