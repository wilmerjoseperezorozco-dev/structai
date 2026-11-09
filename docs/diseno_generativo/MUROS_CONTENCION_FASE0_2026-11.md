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

## 9. Calibración del dentellón y mínimos constructivos (2026-11-09)

**Dentellón.** Se retiró la hipótesis escalonada («tan φ si la profundidad ≥ 0,30 m»), que explicaba buena parte del 53,7 % de victorias del dentellón de la sección 8. Modelo actual (`muro_contencion.resistencia_dentellon`), sin empuje pasivo (H.6.7b), continuo en la profundidad d_k y nulo sin dentellón:
- *Aporte de punta* (HIPÓTESIS): sobre el ancho w de la punta la falla pasa por suelo (tan φ) en lugar de concreto-suelo (tan 2φ/3): (tan φ − μ)·q_punta·w·min(d_k/w, 1). La presión en la punta se toma de la distribución lineal de contacto.
- *Reacción de las caras verticales*: en reposo la cara frontal y la posterior se anulan (K0 simétrico); solo la parte desplazada (Kp − Ka) cuenta, y esa es la que H.6.7b excluye. Parámetro `eta_pasivo_dentellon` (0 = lectura estricta, por defecto); η > 0 solo como sensibilidad.
- Verificado con caso de mano (`test_dentellon_estricto_solo_aporta_la_punta_de_suelo`), continuidad y monotonía en d_k (`test_dentellon_es_continuo_en_la_profundidad`). 159 pruebas pasan.

**Sensibilidad a η** (512 casos re-optimizados, `sensibilidad_dentellon.json`):

| η | con solución | gana dentellón | gana estándar | ahorro mediano |
|---|---|---|---|---|
| 0 (estricto) | 44,5 % | 30,9 % | 13,5 % | 5,0 % |
| 0,25 | 45,9 % | 35,0 % | 10,7 % | 6,8 % |
| 0,5 | 47,3 % | 36,7 % | 10,4 % | 8,1 % |
| 1,0 | 49,8 % | 39,3 % | 10,4 % | 10,8 % |

Lectura: el dentellón sigue siendo la tipología ganadora más frecuente incluso en la lectura estricta, pero su ventaja crece con el empuje pasivo que se le conceda; la cifra de la sección 8 (53,7 %, ahorro 10,9 %) era mayor que la de cualquier η probado (≤ 39 %), es decir, el escalón regalaba más fricción que el empuje pasivo total. La fracción de casos sin solución sube de 32 % a 56 % porque ya no se regala fricción tan φ. η queda como decisión de ingeniería (no la fija la NSR-10): con η = 0 los resultados son defendibles ante H.6.7b.

**Mínimos constructivos.** `t_corona = 0,25 m` pasa a ser constante de diseño (`T_CORONA`), ya no variable de búsqueda. Los demás mínimos (h_zapata 0,30; t_base 0,30; b_puntera 0,10; dentellón 0,10; vuelo de bandeja 0,40) son *pisos constructivos declarados* y se reportan aparte (`*_en_piso`), no como límite de búsqueda. Resultado del nuevo dataset (`dataset_v2.csv`, 4096 casos, 0 errores):
- Variables pegadas al **techo** de búsqueda: ≤ 0,8 % en todas (compuerta del 5 % cumplida).
- Variables pegadas al **piso** constructivo: h_zapata ≈ 59 %, t_base ≈ 57 %, b_puntera ≈ 29–34 %, vuelo de bandeja 50 %, dentellón 19 %. Esto NO es un hallazgo del optimizador: indica que, para estos rangos, el piso constructivo rige sobre la mecánica; hay que revisarlos con un constructor antes de publicarlos como regla.

**Sustituto reentrenado** (`modelos_v2`, 614 reservados): viabilidad 95,8 % (base 56,4 %), tipología 91,4 % (mayoritaria 64,6 %), b_talon MAE 0,33 m, resto ≤ 0,08 m (bandeja: vuelo 0,23 m). **Guardrail** (400): 0 inseguros, 0 falsos inviables; directo 22,3 %, reparado 17,3 %, exacto 3,5 %, sin solución 57 %; brecha mediana 1,3 % (IC95 0,9–2,0 %), p90 10,6 %, p99 25,9 %; 14 casos < −1 % (optimizador local). Más brecha que en la v1 (p90 6 %): el espacio es más difícil y la corona fija recorta grados de libertad. Reglas: φ sigue dominando (corte ≈ 36,5°, 74 % de exactitud, menor que el 80 % de v1).

Sigue pendiente: contrafuertes, anclajes/base inclinada para la región inviable, contraste con un ejemplo publicado (compuerta Fase 2).

## 10. Contrafuertes y tirantes preesforzados (2026-11-09)

Se agregan dos tipologías al optimizador (`TIPOLOGIAS_EXTENDIDAS`; el sustituto y el dataset v2 siguen conociendo solo las tres anteriores). 178 pruebas del paquete pasan (19 nuevas en `test_muro_contrafuerte_anclaje.py`, con esperados a mano).

**Contrafuertes** (`muro_contrafuerte.py`; geometría en `GeometriaMuro`: `contrafuerte_sep`, `contrafuerte_esp`). Pantalla de espesor uniforme; contrafuerte triangular de lado h × b_talon. En la estabilidad entra con su peso neto (γc − γ) y su centroide. Diseño (HIPÓTESIS, el corpus NSR-10 no trae el método): pantalla y talón como losas continuas entre contrafuertes con M = wL'²/12 (cota superior) y V = wL'/2; refuerzo horizontal por niveles en dos caras; momento vertical de la pantalla = mitad del horizontal (**sin calibrar con una placa de Czerny/Bares**); contrafuerte como voladizo rectangular de ancho esp con barra principal inclinada (As = As_vertical/cos ψ), estribos horizontales = máximo entre amarre, cortante (C.11.4.7) y mínimo, amarres verticales del talón. Sin corte de barras, torsión ni aporte de ala.

**Tirantes** (`muro_anclaje.py`; `anc_fuerza_kn_m`, `anc_y`, `anc_incl_deg`). Componente horizontal Th que se opone al empuje y vertical Tv que carga la base, ambos en el equilibrio y en las presiones mayoradas (factor 1,0, acción permanente). Dimensionamiento (HIPÓTESIS; H.6.7 solo menciona anclajes): cordón 15,2 mm con esfuerzo de servicio ≤ 0,60 fpu, adherencia τ = 150 kPa **supuesta** con FS 2,0, longitud libre hasta la superficie de falla de Rankine + 1,5 m (mín. 4,5 m), fija mín. 3 m y máx. 12 m, separación 2,5 m, cota 0,80 h y 15° fijas en el optimizador. La pantalla se diseña **sin** el alivio del tirante (conservador) y **no** se verifica punzonamiento ni flexión local en la cabeza. Precios de perforación (180.000 COP/m) y cabeza (450.000) y precio del cordón (2,5 × acero) son **SUPUESTOS**: el APU consultado no los trae.

**Región sin solución** (`region_sin_solucion.py`, primeros 512 casos del dataset v2; `region_sin_solucion*.json`). Casos que ninguna de las tres tipologías anteriores resolvía: 284 (55,5 %).
- Tirantes recuperan **50 %** de ellos (65,8 % de 1,5–3 m; 74,0 % de 3–5 m; 48,7 % de 5–6,5 m; 24,2 % de 6,5–8 m; 80,5 % con a_max < 0,15 g frente a 36,8 % con a_max > 0,35 g). La recuperación es la misma con precios de anclaje ×1, ×3 y ×6: es un resultado mecánico, no económico.
- Contrafuertes recuperan **0,4 %** (1 caso): con H ≤ 8 m el voladizo con tirantes domina, y el límite que queda es el deslizamiento seudoestático.
- Sin solución después: 27,7 % (antes 55,5 %). Lo que queda necesita más que estas dos soluciones (base inclinada, anclajes más largos o más fuertes, mejora del terreno).
- En los 228 casos que ya tenían solución, ganar o no depende del **precio supuesto del tirante**: gana alguna tipología nueva en 73,7 % (ahorro mediano 18,6 %) con los precios base, 23,2 % (11,3 %) con ×3 y 10,1 % (7,5 %) con ×6; con ×6 gana únicamente el contrafuerte. Esa cifra económica NO es publicable hasta tener precios reales de anclajes.

**Muros altos** (φ = 34°, q_adm 300 kPa, a_max 0,15 g, costo en millones COP/m): a H = 6 m el estándar cuesta 5,35 y el contrafuerte 6,60; a 8 m, 10,71 frente a 12,62 (el tirante 10,34); a H = 10 m y 12 m **solo el contrafuerte tiene solución** (19,9 y 27,2); a H = 14 m ninguna dentro de los límites de búsqueda. Coherente con la práctica: el contrafuerte no compite en alturas moderadas y es la salida cuando el voladizo agota espesor y talón.

**Pendiente:** calibrar el momento vertical de la pantalla con una placa; precios reales de anclajes; verificar la cabeza del anclaje; contraste con ejemplo publicado (compuerta Fase 2); reentrenar el sustituto con cinco tipologías (hoy no las conoce); base inclinada.
