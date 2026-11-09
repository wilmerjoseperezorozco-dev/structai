# Muros de contención — Fase 0 (planificación y protocolo del experimento)

Fecha: 2026-11-08. Alcance: muro de contención en voladizo, con variantes de pantalla de espesor variable, bandeja de alivio y contrafuertes. Todo lo marcado HIPÓTESIS es un supuesto de investigación no verificado contra la norma ni contra ensayos.

## 1. Qué dice la norma y qué no (leído del corpus el 2026-11-08)

| Tema | Fuente en el corpus | Valor / regla |
|---|---|---|
| Estados límite de falla | H.6.2.1 | rotura estructural, deformaciones, volteo, capacidad de carga, erosión del apoyo, deslizamiento, estabilidad general del talud |
| Acciones por metro de muro | H.6.3 | peso propio, empuje de tierras, fricción muro-suelo, empuje hidrostático o filtración, sobrecargas, sismo |
| Deslizamiento | Tabla H.6.9-1 | FS ≥ 1,60 (construcción y estático); 1,05 seudoestático |
| Volcamiento | Tabla H.6.9-1 | momento resistente / actuante ≥ 3,00 estático; ≥ 2,00 seudoestático |
| Excentricidad | Tabla H.6.9-1 | e/B ≤ 1/6 estático; ≤ 1/4 seudoestático |
| Capacidad portante | H.6.9 → Tabla H.4.7-1 | F_SICP ≥ 3,0 (D+L normal), 2,5 (D+L máxima), 1,5 (con sismo seudoestático) |
| Estabilidad general | Tabla H.6.9-1 | 1,50 estático permanente; 1,05 seudoestático |
| Desplante | H.6.7(a) | al menos 1 m bajo la superficie frente al muro, bajo la zona de cambios volumétricos |
| Deslizamiento sin pasivo | H.6.7(b) | la estabilidad no puede contar con el empuje pasivo |
| Drenaje | H.6.5 | todo muro lleva filtros y drenajes atrás; el empuje del agua se suma si no se evita |
| Sismo | H.6.8 y H.5.2.5 | K_ST ≤ a_max y K_ST/a_max ≥ 0,80 en suelos; a_max del Capítulo A.2 |
| Estado activo | H.6.4.4 | aplicable solo si el muro puede deformarse lo suficiente por flexión o giro |

**La NSR-10 del corpus no contiene** las fórmulas de Rankine, Coulomb ni Mononobe-Okabe (se buscaron por texto: Rankine 0 resultados, Mononobe 0). Los coeficientes de empuje y el empuje sísmico se calculan con teoría geotécnica clásica y se declaran HIPÓTESIS hasta contrastarlos con un ejemplo publicado verificable. Lo estructural (flexión, cortante, acero mínimo) irá por el Título C leído del corpus; las combinaciones de carga con empuje de tierras (factor de H) se leen de B.2 en la Fase 2, no se asumen.

## 2. Revisión del experimento de zapata: qué pudo sesgarlo (verificado con el dataset de 5.000 casos)

| Hallazgo | Evidencia | Consecuencia para muros |
|---|---|---|
| Variable pegada al límite | h_e = 300 mm (mínimo de la rejilla) en 4.486 de 4.488 casos; ninguna zapata prismática fue óptima | Antes de generar datos, verificar que ninguna variable de diseño quede en el límite en más del 5 % de los casos; si ocurre, el límite es el resultado, no la variable |
| Casos sin solución | 10,2 % del total; 38 % con Pu en el cuarto cuartil, 38 % con momentos altos, 19 % con q_adm bajo | Dato de primera clase: el sustituto predice factibilidad; "sin solución" se reporta, no se extrapola |
| Entradas independientes | |corr| máx entre entradas 0,03 | Suelo con φ, γ y c correlacionados; altura y sobrecarga acordes con el tipo de muro |
| Rangos supuestos | Todos los rangos de entrada son hipótesis | Cada rango lleva fuente o la marca SUPUESTO; un conjunto aparte con casos realistas (perfiles de la región) |
| Subconjunto de un LHS | Los primeros N de un LHS de 20.000 no son un LHS de N | Usar una secuencia de Sobol con scramble: cualquier prefijo de potencia de 2 queda bien distribuido |
| Etiquetas dependen del optimizador | Rejilla de 50 mm, búsqueda acotada (lado del pedestal, L ≤ 6 m) | Registrar en un manifiesto los límites de búsqueda; el sustituto hereda sus sesgos |
| Una sola partición | Una semilla, sin intervalos | Bootstrap sobre el conjunto reservado y estadística pareada (`packages/eval-stats`) |
| Solo dentro de distribución | El benchmark usa la misma distribución del entrenamiento | Conjunto fuera de distribución (rangos desplazados) y tasa de caída al exacto |
| Motor sin contraste externo | La zapata no se comparó con un ejemplo publicado | Fase 2 de muros incluye ejemplos publicados verificables antes de generar datos |

## 3. Fases y puertas de salida

Cada fase termina con una puerta; no se pasa a la siguiente si no se cumple. Cada fase se escribe sin mirar los resultados de los otros elementos para no heredar sus supuestos.

**Fase 0 — Planificación (este documento).** Puerta: tabla normativa verificada, supuestos listados, protocolo del experimento fijado antes de ver datos.

**Fase 1 — Estabilidad externa del muro en voladizo.** Geometría por metro de muro, empuje activo de Rankine (con relleno inclinado), volcamiento, deslizamiento sin pasivo, excentricidad y presión de contacto, con los factores de la Tabla H.6.9-1. Puerta: pruebas contra cálculo a mano y contra soluciones cerradas; equilibrio verificado; sin optimización todavía.

**Fase 2 — Diseño estructural.** Flexión y cortante de pantalla, puntera y talón por franja de 1 m (Título C), acero mínimo, longitud de desarrollo, combinaciones de B.2, costo APU y CO₂ (se reutiliza `economia_concreto`). Puerta: contraste con un ejemplo publicado y verificable; lista explícita de lo que no se verifica.

**Fase 3 — Variantes geométricas y ablación.** Pantalla de espesor lineal o parabólico, bandeja de alivio, contrafuertes; empuje sísmico pseudoestático con K_ST ≥ 0,80·a_max. Cada variante se compara contra el mismo muro sin ella con las mismas cargas (diseño pareado), así el beneficio de la bandeja se mide y no se supone.

**Fase 4 — Optimizador exacto y protocolo de datos.** Búsqueda de referencia, manifiesto de supuestos, comprobación de variables en el límite, muestreo Sobol con suelo correlacionado, conjuntos reservado y fuera de distribución. Puerta: ninguna variable en el límite en más del 5 %; casos sin solución caracterizados.

**Fase 5 — Sustituto y validación.** LightGBM más clasificador de factibilidad, validador determinista, benchmark con intervalos de confianza. Puerta: 0 diseños inseguros tras re-verificación independiente y brecha reportada con intervalo.

## 4. Variables y rangos (todos SUPUESTO hasta verificar fuente)

- Geometría: altura de pantalla 2–8 m; espesor de base de zapata 0,3–1,2 m; espesor de pantalla en corona 0,2–0,5 m y en base 0,3–1,2 m; puntera y talón por búsqueda.
- Relleno: γ 16–20 kN/m³, φ 26–38°, sobrecarga 0–30 kPa, inclinación 0–20°.
- Suelo de apoyo: φ 20–38°, c 0–50 kPa, γ 16–21 kN/m³, q_adm 100–400 kPa.
- Correlación: γ y φ del relleno con coeficiente positivo (HIPÓTESIS 0,6); se documenta y se prueba la sensibilidad.
- Drenaje: se supone drenado (H.6.5 lo exige); el caso con nivel freático se agrega en Fase 3.

## 5. Límites conocidos desde ya

- Rankine supone pared lisa y vertical: se usa con relleno inclinado y plano virtual en el extremo del talón; Coulomb y Mononobe-Okabe quedan para la Fase 3.
- No se verifica estabilidad general del talud (H.6.2.1), asentamientos ni efectos de socavación.
- Sin contraste con ensayos ni con instrumentación de muros reales.
- Ningún resultado sustituye la revisión de un ingeniero que firme memorias de cálculo.

## 6. Estado de la Fase 2 (2026-11-08)

Implementado en `packages/motor-concreto/src/muro_contencion_estructural.py` con 12 pruebas de cálculo a mano (`tests/test_muro_contencion_estructural.py`): Mu y Vu de la pantalla (1,6 H), puntera y talón con presiones mayoradas de dos combinaciones (A: 1,2D+1,6H+1,6Q; B: 0,9D+1,6H), elección de barras con As mín C.10.5.1, εt ≥ 0,005, separación máxima, recubrimientos C.7.7.1, acero horizontal y vertical mínimo C.14.3, costo APU y CO₂ por metro.

**Puerta pendiente**: el contraste con un ejemplo publicado verificable NO se ha hecho (no se cita de memoria). Hasta entonces los resultados son verificaciones internas de coherencia, no validación externa. Tampoco se leyó B.2: las combinaciones A y B son HIPÓTESIS. Lo no verificado está en `SUPUESTOS` del módulo (desarrollo y empalmes, corte de barras, cortante por fricción en la unión, fisuración, drenaje).

## 7. Fase 3a/3b (2026-11-08): B.2 leída, variantes y sismo

**B.2 leída del corpus.** B.2.4-2 (1,2(D+F+T)+1,6(L+H)+0,5(...)) confirma la combinación A con la sobrecarga como L. B.2.4-7 (0,9D+1,0E+1,6H) es la combinación sísmica. **Corrección:** la combinación B de la Fase 2 (0,9D+1,6H sin W ni E) NO está literalmente en B.2.4; queda como chequeo adicional conservador. B.2.4.2.4 permite 1,4E cuando E se basa en niveles de servicio: lo uso para el seudoestático (interpretación mía, HIPÓTESIS). H.6.7(c) lista «dentellones reforzados» y H.6.7(b) prohíbe contar el empuje pasivo; H.5.2.5 da K_ST/a_max ≥ 0,80 para suelos.

**Implementado** (`muro_contencion.py`, `muro_pantalla.py`, `muro_refuerzo.py`, `muro_contencion_estructural.py`; 27 pruebas nuevas): pantalla lineal o parabólica con verificación en 8 secciones, bandeja de alivio (sombreado del empuje, contramomento, losa), dentellón (fricción plena tan φ si ≥ 0,30 m, diseñado con el déficit de la fricción simple), Mononobe-Okabe validado contra una cuña de Coulomb independiente, estabilidad seudoestática (FS 1,05 / 2,00 / e ≤ B/4) y combinación sísmica estructural.

**Hallazgo del modelo, a medir en la ablación:** con el método del plano virtual en el extremo del talón, la bandeja NO cambia el empuje global (el suelo sobre ella ya está en el prisma), solo la pantalla y el peso. Cualquier beneficio de estabilidad que se le atribuya depende de un modelo más fino (cuña de Coulomb con rozamiento muro-suelo) que no está implementado. Contrafuertes: no implementados.

## 8. Dataset, sustituto y guardrail (2026-11-08)

**Dataset** (`data/surrogate_muro/`, Sobol scrambled, 4.096 casos, 0 errores, 1,5 s por caso por proceso): 32 % sin solución; ganadora: dentellón 53,7 %, estándar 14 %, bandeja 0,2 %. Ahorro mediano frente al estándar lineal del mismo caso: 10,9 % (p90 35 %).

**Puerta de la Fase 4 NO cumplida (variables en el límite):** t_corona en su mínimo en 76-98 % de los casos, h_zapata 52-60 %, t_base 39-47 %, profundidad del dentellón 81 %. Son mínimos constructivos del optimizador (`LIMITES`), no resultados de optimización: el modelo aprende en buena parte a repetirlos. Además, **el predominio del dentellón es en gran medida consecuencia de mi hipótesis** (fricción tan φ si profundidad ≥ 0,30 m, escalón único): hasta calibrar ese supuesto con un método de superficie de falla o ensayo, «el dentellón gana en 54 %» no es un hallazgo de mecánica. La bandeja casi nunca gana porque el modelo del plano virtual no le da beneficio de estabilidad.

**Sustituto** (reservado 614 casos): factibilidad 97,2 % (tasa base 71,2 %); tipología 95,9 % (mayoritaria 77,1 %); MAE de b_talon 0,22-0,32 m, de las demás dimensiones ≤ 0,09 m (t_corona y t_base, que viven en el mínimo, ~0,005-0,03 m).

**Guardrail** (400 reservados): directo 35,8 %, reparado 33,8 %, exacto 1,8 %, sin solución 28,8 %; **0 inseguros** tras re-verificación (por construcción del validador, solo respecto de lo que el motor verifica), 0 factibles perdidos; brecha mediana 1,26 % (IC95 0,96-1,54 %), p90 6,0 %, p99 15 %. 37 casos con brecha < -1 %: el sustituto + reparación superó al optimizador de referencia, que es una búsqueda local y no un óptimo global.

**Pareto** (`muro_pareto.py`): el costo y el CO₂ solo se separan con la mezcla (f'c y ceniza); para H = 4,5 m: mínimo costo 2,96 M COP/m con 1.320 kg CO₂e/m; mínima huella 3,01 M COP/m con 1.041 kg (+1,5 % costo, -21 % CO₂). Factores de CO₂ «bajo/alto» son SUPUESTOS.

**Reglas (SHAP + árboles)** en `data/surrogate_muro/reglas.md`: solo descriptivas del optimizador bajo estas hipótesis; φ domina la elección (corte en φ ≈ 36,5°, exactitud 80 %).
