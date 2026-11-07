# Resultados P3 y P4: transmisión y Monte Carlo del costo (ICOCIV)

Ejecutado el 2026-11-07 según el protocolo del commit `da76f47` (sección «P3 y P4» de [`PROTOCOLO_PRECIOS.md`](PROTOCOLO_PRECIOS.md)). Script: `p3_p4_transmision_montecarlo.py`. Datos: ICOCIV (DANE) 2021-01 a 2026-09, 69 meses, un solo anexo (el de septiembre de 2026 contiene la serie completa en sus hojas 1 y 16). Señal estadística de corto plazo, no pronóstico.

## P3 — transmisión

| Resultado | Valor |
|---|---|
| Variación mensual media de ICOCIV-carreteras | +0,56 % tanto en 2021-2022 como en 2023-2026 |
| Desviación mensual | 0,53 % en 2021-2022; **0,99 %** en 2023-2026 (casi el doble) |
| Autocorrelación al rezago 1 | +0,21 (2021-2022); +0,50 (2023-2026) |
| TRM → carreteras, acumulado a 6 meses | +0,194, EE 0,101, p 0,056; **p Holm 0,111: no significativo** |
| WTI → carreteras, acumulado a 6 meses | −0,047, EE 0,046, p 0,308: no significativo |
| Efecto mínimo detectable (80 %) | 0,283 (TRM) y 0,128 (WTI) |

**Lectura.** El signo de la TRM es el esperado pero el efecto no se distingue de cero y la prueba tiene poca potencia (el efecto mínimo detectable, 0,28, supera al estimado). El WTI no muestra transmisión al índice, y su límite de detección (0,13) es bajo: el índice de obras civiles es una canasta amplia y suaviza el petróleo; **eso no dice que un contrato concreto con cemento asfáltico no esté expuesto**.

**Exploratorio (sin corrección, no confirmatorio).** IPC a 6 meses: +3,41 (p < 0,001); ONI a 6 meses: −0,011 por °C (p 0,009); interacción 2021-2022 × TRM: +0,227 (p 0,114). El IPC y el índice de costos se mueven juntos por el ciclo inflacionario común: es co-movimiento, no transmisión causal. El ONI coincide con un único ciclo (La Niña 2021-2022) en pleno episodio inflacionario: no se separa del régimen de precios con estos datos.

## P4 — Monte Carlo (bootstrap por bloques de 3 meses)

| Horizonte | Muestra | P5 | P50 | P95 | Costo en riesgo (P95 − P50) |
|---|---|---:|---:|---:|---:|
| 6 meses | completa | 1,003 | 1,029 | 1,088 | 5,9 % |
| 12 meses | completa | 1,021 | 1,065 | 1,140 | 7,5 % |
| 12 meses | solo 2023-2026 | 1,011 | 1,053 | 1,130 | 7,7 % |

**Validación fuera de muestra** (intervalo nominal 80 % a 6 meses, 33 orígenes, tamaño efectivo ≈ 6 por solapamiento): cobertura 0,79 con bloques y 0,82 con una normal iid. Cumple el criterio [0,65; 0,95], pero la referencia ingenua cubre igual de bien: **no hay evidencia de que el bootstrap por bloques aporte algo frente a la normal simple**, y con tamaño efectivo 6 la cobertura se estima con mucho error.

**Cota (no estimación).** El cemento asfáltico es el 32 % del costo directo por m² del ítem 4. Si se moviera uno a uno con WTI × TRM, el costo en riesgo a 12 meses sería 27,7 % (frente a 7,5 % del índice). Es un límite superior; la verdad está entre ambos y depende de la cláusula de ajuste de cada contrato.

## Qué se puede y qué no concluir
- Sí: orden de magnitud del riesgo de costo de una obra vial según el índice de canasta (≈ 6-8 % a 6-12 meses) y que la volatilidad mensual del índice se duplicó desde 2023.
- No: que el dólar o el petróleo se transmitan (o no) al costo; ni un pronóstico. 69 meses con un solo ciclo no identifican transmisiones de corto plazo.
