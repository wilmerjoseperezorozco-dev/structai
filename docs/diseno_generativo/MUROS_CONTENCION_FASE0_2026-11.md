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
