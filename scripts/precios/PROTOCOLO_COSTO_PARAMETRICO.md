# Protocolo: costo paramétrico de pavimentos (ítem 4) y periodo de retorno de alcantarillas (ítem 5)

Preregistrado el 2026-11-07, antes de calcular. Parte del programa de precios (issue #102). Ambos ejercicios son **de propagación y sensibilidad**, no de estimación: combinan un diseño, un precio de referencia y supuestos explícitos. No son presupuestos, no sustituyen un diseño firmado y los precios son de referencia INVIAS 2026-1, no cotizaciones.

## Datos y verificaciones previas (comunes)

- Precios: `invias_actividad_costos` (periodo 2026-1, 140 provincias), columna `costo_directo_total` (COP por unidad de la actividad). No incluye AIU, imprevistos ni diseño.
- **S1.** Cada actividad usada debe tener precio en las 140 provincias.
- **S2.** Verificar en una muestra que `costo_directo_total` = materiales + mano de obra + equipo + transporte. Si no, se usa la suma y se documenta.
- **S3.** Los precios con razón a la mediana nacional > 3 de la misma actividad se marcan como posibles anomalías y se reportan; las estadísticas usan mediana y cuantiles, no promedios.
- Provincia de referencia: la del Atlántico con mayor número de actividades con precio (se declara en el informe).

## Ítem 4: costo paramétrico de pavimento por m²

**Diseño.** `motor-vias` (`DisenadorPavimentos`, tablas AASHTO-93 adaptadas) entrega espesores de rodadura, base y subbase en cm para un par (ESAL, CBR). La malla es la que el propio motor tabula. Límite: ese motor no está validado contra el Manual de Diseño de Pavimentos de INVIAS.

**Actividades elegidas a priori** (no se cambian después de ver resultados): subbase `320,1,1`; base `330,1,1`; rodadura `450,01` (MDC-25); imprimación `420,1` (1 riego por m²); cemento asfáltico `410,2` (60-70). Pavimento rígido: `500,1,1` (concreto hidráulico, m³) sobre la misma base.

**Supuestos declarados** (INVIAS dice de las mezclas 450.x «no incluye suministro de cemento asfáltico»; por eso hay que añadirlo): densidad de la mezcla compactada 2,35 t/m³ y contenido de cemento asfáltico 5,5 % del peso de la mezcla, es decir 129 kg por m³. Sin desperdicio ni factor de compactación.

**Preguntas y qué se reporta** (descriptivo, sin prueba de hipótesis):
1. Costo por m² en la provincia de referencia sobre toda la malla (ESAL × CBR) y participación de cada componente.
2. Dispersión geográfica: para el diseño de referencia (ESAL 5 millones, CBR 8 %), cociente P90/P10 del costo por m² entre las 140 provincias, y fracción de la dispersión logarítmica que desaparece al fijar las capas granulares en su mediana nacional (contrafactual).
3. Sensibilidad en la provincia de referencia: contenido de asfalto 4,5-6,5 %, cemento asfáltico `410,1`/`410,2`/`410,3`, y ±20 % en el espesor de rodadura.
4. Rígido frente a flexible: costo inicial por m² en la malla y el ESAL a partir del cual el rígido cuesta menos que el flexible, si existe.

**No se concluye:** cuál pavimento es mejor, porque falta mantenimiento, vida útil y costo de usuario; ni un valor de obra, porque falta AIU y rendimientos. Cualquier cifra se presenta como costo directo de referencia.

## Ítem 5: periodo de retorno económico de una alcantarilla de cajón

**Curva de crecimiento (índice de crecida).** De `frecuencia_crecientes_ideam.json`, subconjunto limpio fijado a priori: n ≥ 30 años, p-valor KS ≥ 0,10, Mann-Kendall p ≥ 0,10, valores repetidos ≤ 10 %, cuantiles GEV finitos. Factor de crecimiento x_T = Q_T / Q_2 por estación, para T ∈ {2, 5, 10, 25, 50, 100}; curva = mediana entre estaciones; incertidumbre por bootstrap de estaciones. Se reporta el subconjunto del Caribe y el nacional; el análisis principal es el Caribe si tiene ≥ 15 estaciones limpias, y si no, el nacional. Se reporta el CV de x_100 como medida de heterogeneidad regional.

**Limitaciones que se reportan con el resultado:** las estaciones son de ríos medianos y grandes y los máximos anuales del IDEAM son máximos horarios; una cuenca de alcantarilla es pequeña y de crecida más súbita, así que la curva transferida probablemente subestima la cola. La estacionariedad no está calibrada (excedencia observada del Q10: 0,135).

**Modelo.**
- Caudal índice Q_2 ∈ {2, 10} m³/s (supuesto de cuenca pequeña). Caudal de diseño Q_T = Q_2 · x_T.
- Hidráulica de entrada controlada: A = Q_T / (0,6 · √(2 g H)) con H = 1,5 m; cajón cuadrado de lado b = √A (mínimo 0,9 m); longitud 10 m; espesor t = máx(0,20 m; b/12); acero 100 kg por m³ de concreto; zanja de ancho b + 2t + 1,0 m y altura b + 2t + 0,5 m; cabezotes y aletas = 25 % adicional del cuerpo.
- Precios: concreto `630,1,1`, acero `640,1`, excavación `600,2,3` y relleno `610,1`, en la provincia de referencia.
- Probabilidad anual de excedencia: nominal 1/T y escenario pesimista 1,35/T (inflación por la descalibración observada).
- Pérdida por falla = m × C_inv(T = 25), con m ∈ {0,5; 1; 2; 5; 10}. Tasa de descuento r ∈ {4 %; 8 %; 12 %}, vida N = 30 años. Costo esperado total = C_inv(T) + pérdida × Σ p / (1+r)^t.

**Resultado a reportar.** T* que minimiza el costo esperado para cada combinación (Q_2, m, r, escenario de probabilidad), y la **robustez**: el resultado se llama robusto solo si T* es el mismo en ≥ 80 % de las combinaciones de la malla y en ≥ 80 % de los remuestreos de la curva de crecimiento. Si no, se reporta «sin recomendación robusta» y la dependencia de m.

**No se concluye:** un periodo de retorno de diseño para ninguna obra real, ni se compara con la práctica normativa sin citar la norma; es un análisis de cómo cambia el óptimo con la pérdida y la descalibración. La pérdida m es un supuesto, no un dato.

---

## Enmienda 1 (2026-11-07, posterior a los resultados del ítem 5; se declara como tal)

Motivo: al publicar el ítem 5 se señaló que (a) los intervalos de la curva de crecimiento remuestreaban estaciones como si fueran independientes y (b) el criterio de robustez no tenía comprobación de borde. Cambios, fijados antes de ejecutar la corrección:
1. **Bootstrap por conglomerados.** Se remuestrean departamentos completos (con todas sus estaciones limpias) en lugar de estaciones sueltas. Se reporta el ancho P10-P90 de x_T con ambos métodos, el efecto de diseño (cociente de anchos al cuadrado), el número efectivo de estaciones independientes (n / efecto de diseño) y la correlación intraclase (ICC) de ln x_100 por departamento.
2. **Comprobación de borde.** Si T\* coincide con el mayor periodo evaluado, el veredicto es «no informativo» aunque se cumpla el criterio de robustez.
3. La robustez se vuelve a calcular con los remuestreos por conglomerados; el criterio de ≥ 80 % no cambia.
