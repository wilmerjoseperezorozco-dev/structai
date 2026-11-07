# Resultados: coherencia espacio-temporal de las anomalías de caudal

Ejecutado el 2026-11-07 según [`PROTOCOLO_COHERENCIA.md`](PROTOCOLO_COHERENCIA.md) (commit `69f5b3d`, anterior a los resultados). Script: `coherencia_anomalias.py`. 610 estaciones IDEAM con ≥ 240 meses (1934-01 a 2026-08). Descriptivo: señal estadística, no alerta oficial.

## C1 — las anomalías altas están sincronizadas

Razón de varianzas VR (1 = estaciones independientes). El nulo de permutación da VR ≈ 1,0-1,15 en todas las regiones; p = 0,002 en todas (mínimo posible con 500 permutaciones); Holm 0,010.

| Región | Estaciones | VR | IC95 % (bloques de 12 meses) |
|---|---:|---:|---|
| Andina | 329 | 18,8 | 9,4 – 30,5 |
| Caribe | 97 | 7,0 | 4,0 – 11,2 |
| Pacífica | 104 | 5,5 | 3,4 – 8,1 |
| Orinoquía | 43 | 2,8 | 1,8 – 3,9 |
| Amazonía | 37 | 2,2 | 1,6 – 2,9 |

**Cuidado al comparar regiones:** VR crece con el número de estaciones (con sincronía perfecta, la varianza del conteo escala como N², y el nulo como N), así que no es una medida de «qué región es más coherente». Lo que se sostiene es que **en todas** hay sincronía muy por encima de la independencia.

## C2 — la sincronía depende de ENSO (tercer orden)

Fracción media de estaciones en anomalía alta por mes, La Niña (ONI ≤ −0,5) frente a neutral:

| Región | La Niña | Neutral | Diferencia (IC95 %) | p Holm |
|---|---:|---:|---|---:|
| Andina | 5,8 % | 2,2 % | +3,6 pp (+2,0; +5,3) | 0,005 |
| Pacífica | 5,4 % | 2,1 % | +3,2 pp (+1,7; +5,2) | 0,005 |
| Caribe | 4,9 % | 2,2 % | +2,7 pp (+1,1; +4,4) | 0,006 |
| Orinoquía | 2,8 % | 2,5 % | +0,3 pp (−0,8; +1,7) | 0,541 |
| Amazonía | 1,5 % | 2,6 % | **−1,1 pp** (−2,0; −0,3) | 0,997 |

La Niña multiplica por 2-2,7 la fracción de estaciones en anomalía alta en las regiones Andina, Pacífica y Caribe; en Orinoquía no hay efecto y en la Amazonía el signo es **opuesto** al esperado (la hipótesis era positiva, así que no es «significativa» en esa dirección).

*Exploratorio, sin ajuste:* en anomalías **bajas**, El Niño frente a neutral: Caribe +5,8 pp (9,3 % frente a 3,5 %), Pacífica +2,6, Andina +2,0, Orinoquía +0,8, Amazonía −0,4.

## C3 — alcance espacial

| Distancia | Correlación mediana de los z mensuales |
|---|---:|
| 0 – 50 km | +0,46 |
| 50 – 100 km | +0,37 |
| 100 – 200 km | +0,33 |
| 200 – 400 km | +0,27 |
| 400 – 800 km | +0,20 |
| > 800 km | +0,10 |

La dependencia decae lentamente: no cae bajo 0,10 hasta pasados 800 km. La correlación media dentro de cada región es 0,28-0,39, de modo que 100 a 329 estaciones equivalen a unas **2,5-3,3 independientes** para un promedio regional del z mensual (suponiendo equicorrelación).

## Qué implica y qué no
- **Sí:** las estaciones no son réplicas independientes para anomalías mensuales; cualquier intervalo que las trate así es demasiado estrecho. Esto motivó la enmienda 1 de `PROTOCOLO_ANOMALIAS.md`: con bootstrap por departamento, C1 (M1 − B0) deja de ser significativo (p Holm 0,0875) y C2 (M2 − M1) se sostiene (p 0,001).
- **Sí:** la fase de ENSO modula **cuántas estaciones se desvían a la vez**, no solo cuánto se desvía cada una. Es una relación de tercer orden medida de forma directa.
- **No:** el «≈ 3 estaciones efectivas» es para el promedio regional de anomalías mensuales; no se traslada tal cual a los máximos anuales (la corrección del ítem 5 dio 73 efectivas de 132 y 0,33 de ICC por departamento).
- **No:** una explicación causal. Parte de la correlación viene de forzantes comunes (estacionalidad residual, ENSO), que es justamente lo que C2 muestra.
- Límites: estaciones con huecos distintos, cuencas de tamaños muy diversos y una climatología de todo el registro que absorbe parte de la tendencia.
