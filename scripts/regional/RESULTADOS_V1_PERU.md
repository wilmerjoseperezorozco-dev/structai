# Resultados confirmatorios de V1-Perú: C-2 (2026-11-08)

Protocolo: `PROTOCOLO_V1_PERU.md` con las enmiendas 1 y 2. Código: `peru_c2.py` (commit `25a741e`, publicado antes de ejecutarlo). Datos y compuerta: `COMPUERTA_V1_PERU.md`. **C-1 no se calculó** (no concluyente por la tasa de Y1 > 0 de 96,8 %).

**Qué se midió.** Correlación parcial de Spearman entre la exposición vial a terreno bajo (E: fracción de la vía principal de OSM con HAND < 10 m) y los kilómetros de carretera destruida o afectada por 100 km² (Y2, SINPAD 2019-2024), controlando log(población), log(área), fracción del distrito en terreno bajo (T) y densidad de vía principal. IC 95 % por 5.000 remuestreos de departamentos.

| Ámbito | Distritos | Departamentos | ρ parcial | IC 95 % | Lectura según el criterio fijado |
|---|---:|---:|---:|---|---|
| **Perú completo** | 1.483 | 25 | −0,087 | [−0,194; +0,022] | No concluyente (el IC no está dentro de ±0,15 ni sobre 0) |
| Costa | 329 | 13 | **+0,228** | [+0,080; +0,329] | Se replica (límite inferior > 0 y ρ ≥ 0,15) |
| Sierra | 936 | 19 | **−0,223** | [−0,301; −0,088] | No concluyente por el criterio; el IC queda por debajo de cero |
| Selva (alta y baja) | 205 | 13 | +0,076 | [−0,133; +0,243] | No concluyente |
13 distritos sin región se omiten de la parte regional.

## Lectura permitida por el protocolo
- **Perú completo: no hay réplica de C-2, y tampoco ausencia práctica.** El protocolo dice que, si las regiones difieren de signo, el resultado de Perú no se resume en una cifra. Aquí difieren: **positivo en la costa, negativo en la sierra**, nulo en la selva.
- La costa cumple el criterio de réplica. Es una de tres divisiones regionales, sin ajuste por multiplicidad entre regiones (el protocolo solo preveía Holm entre C-1 y C-2), y su límite inferior (+0,08) no está lejos de cero.
- La sierra tiene el patrón contrario con un IC que excluye el cero. El protocolo no define una categoría para una asociación significativa y de signo opuesto; se informa tal cual y no se interpreta como confirmación ni refutación.
- Con C-1 sin evaluar, la tabla de conclusiones del §7 no tiene una fila aplicable. Lo único que se puede decir es: **V1 no se generaliza a Perú como patrón único**, y la heterogeneidad por región natural es el hallazgo.

## Lo que NO se concluye
- No se concluye causalidad ni mecanismo. En la sierra, el terreno bajo respecto al cauce suele ser el fondo de valle; allí la vía principal puede estar más protegida o más vigilada, o el daño a vías de la red rural (que Y2 incluye y E no) puede dominar. Son conjeturas, no probadas.
- Y2 mide la red vial total y E solo la red principal de OSM: desajuste declarado en el protocolo.
- La cobertura de OSM y el reporte de SINPAD pueden variar entre regiones; el análisis de sesgo de reporte (R8) no se ha corrido todavía.
- El HAND de Perú no se validó contra una referencia independiente.
- La costa de Perú es árida: el daño por huaycos y desbordes ocurre en eventos extremos asociados a El Niño; 2019-2024 puede no incluir uno fuerte. No se verificó.

## Siguiente paso (exploratorio, sin interpretar como confirmatorio)
Correr R1-R10 del §6 con Holm por bloque: sensibilidad a corte de HAND y umbral de red, tipo de vía, controles negativos (movimientos en masa, incendios), sesgo de reporte y focalización. El primero útil es separar la sierra por altitud, porque su signo contrario es el resultado más informativo.

---

# Exploratorias, bloque 1: relieve, heterogeneidad regional y la sierra (2026-11-08)

Código: `relieve_distrito_peru.py` y `peru_exploratorias_sierra.py` (commit `cb63a29`, publicado antes de ejecutarlo). **Todo es exploratorio** y no se interpreta como confirmatorio. Mismas definiciones que C-2; IC 95 % por 5.000 remuestreos de departamentos. S2 y S3 son **post hoc**: se añadieron después de ver el signo contrario en la sierra. Corrección a una frase de arriba: dije que no había verificado si el periodo incluía un Niño fuerte; el propio protocolo (R9a) identifica 2023 como año del Niño costero y el ciclón Yaku, aunque ese dato no se contrastó aquí con una fuente externa.

## R1 parcial: añadir elevación media y pendiente media como controles
| Región | Sin relieve (C-2) | Con elevación y pendiente |
|---|---|---|
| Costa | +0,228 [+0,080; +0,329] | +0,187 [+0,040; +0,300] |
| Sierra | −0,223 [−0,301; −0,088] | **−0,197** [−0,273; −0,067] |
| Selva | +0,076 [−0,133; +0,243] | +0,077 [−0,121; +0,249] |
Controlar el relieve apenas cambia el signo opuesto de la sierra. No es el relieve medio del distrito lo que lo produce. (No se corrió todavía el modelo cuasi-Poisson con efectos fijos de departamento del R1 completo.)

## R7: ¿difieren las regiones?
Diferencia de ρ entre regiones, remuestreando departamentos del conjunto: costa − sierra = **+0,451** [+0,224; +0,565], p de Holm = 0,0008; selva − sierra = +0,299 [+0,063; +0,444], p de Holm = 0,016. **Las regiones difieren de forma estadísticamente clara; no se reporta un efecto único para Perú.**

## S2 (post hoc): terciles de elevación dentro de la sierra
| Tercil | Elevación media del distrito | n | ρ | IC 95 % |
|---|---|---:|---:|---|
| Bajo | 1.612-3.392 m | 312 | −0,162 | [−0,276; −0,013] |
| Medio | 3.393-3.957 m | 312 | −0,213 | [−0,319; −0,010] |
| Alto | 3.960-4.816 m | 312 | −0,186 | [−0,306; −0,009] |
El signo negativo aparece en los tres, con intervalos que apenas excluyen el cero. No depende de una franja de altitud.

## S3 (post hoc): por departamento dentro de la sierra
Con ≥ 30 distritos (12 departamentos): ρ entre −0,185 y +0,075; 8 son negativos pero **la mayoría son cercanos a cero** (|ρ| < 0,10 en 9 de 12). Dejando fuera un departamento a la vez, el ρ de la sierra queda entre −0,176 y −0,245: **ningún departamento domina**. Lectura prudente: el ρ conjunto de −0,22 parece venir en buena parte de **diferencias entre departamentos** (los de más E tienen menos daño a vías), más que de una relación dentro de cada uno. Esto sugiere que el modelo con efectos fijos de departamento, previsto en el R1 y todavía no corrido, es el siguiente paso, y que el signo negativo podría atenuarse mucho con él. No está demostrado.

## Descriptivo en la sierra
E sube con la elevación (Spearman +0,32) y baja con la pendiente (−0,35); Y2 baja con la elevación (−0,23). La fracción de distritos con algún daño a vías cae de 84 % (cuartil más bajo de E) a 51 % (más alto). Compatible con que los distritos de E alta sean de terreno llano y alto, donde la red vial se daña menos por otros motivos; es una conjetura, no una prueba.

## R9a: sin 2023
| Región | Con todos los años | Sin 2023 |
|---|---|---|
| Costa | +0,228 [+0,080; +0,329] | **+0,019** [−0,147; +0,192] |
| Sierra | −0,223 [−0,301; −0,088] | −0,188 [−0,273; −0,045] |
| Selva | +0,076 [−0,133; +0,243] | +0,168 [−0,062; +0,302] |
**La asociación positiva de la costa desaparece al quitar 2023.** Su réplica en C-2 depende de un año atípico, que es exactamente lo que el protocolo previó como riesgo (análogo a quitar 2022 en Colombia). La sierra se mantiene. La selva sube, sin llegar a ser distinta de cero.

## Qué cambia en la lectura global
1. El resultado de la costa no es una réplica robusta de V1: depende de 2023.
2. Lo único estable es el signo negativo de la sierra, pero puede explicarse por diferencias entre departamentos; falta controlar efectos fijos.
3. La heterogeneidad entre regiones es clara (R7), y por eso no cabe un patrón único para Perú.

## Pendiente de las exploratorias
R1 completo con efectos fijos de departamento; R3 (tipo de vía; requiere repetir el cálculo de exposición separando por tipo); R5 (controles negativos); R6 (focalización); R8 (sesgo de reporte); R9 b-d; R10. **No se pueden correr por falta de datos:** R2 (% urbano, NBI y lluvia no se obtuvieron) y R4 (no se extrajeron los lugares poblados de OSM).

---

# Exploratorias, bloque 2: R1 con efectos fijos de departamento (2026-11-08)

Código: `peru_r1_efectos_fijos.py` (commit `eec36ec`, publicado antes de ejecutarlo). **Exploratorio.** Modelos cuasi-Poisson (GLM Poisson con errores robustos) con efectos fijos de departamento. Y1: viviendas dañadas con desfase log(población). Y2 (análogo, no previsto en R1): km de carretera dañada con desfase log(área). Covariables: E (por +0,10), T, elevación media, pendiente media (y log área en Y1). **No incluyen lluvia p95, % urbano ni NBI**, así que es un R1 parcial. IC 95 %: errores robustos agrupados por departamento (pocos grupos, poco confiables) y remuestreo de departamentos (2.000 réplicas). Sin corrección de Holm: son 12 intervalos y no se ajustaron.

## Razón de tasas por +0,10 de E (IC por remuestreo de departamentos; entre paréntesis, el robusto agrupado)
| Ámbito | n / deptos | Y1 viviendas | Y2 km de carretera |
|---|---|---|---|
| Perú | 1.483 / 25 | 1,07 [0,98; 1,20] ([0,97; 1,18]) | 1,02 [0,90; 1,16] ([0,89; 1,16]) |
| Costa | 329 / 13 | 1,06 [0,95; 1,32] ([0,89; 1,26]) | **1,11 [1,02; 1,38]** ([0,96; 1,28]) |
| Sierra | 936 / 19 | 1,00 [0,90; 1,16] ([0,87; 1,15]) | 0,88 [0,74; 1,01] ([0,76; 1,01]) |
| Selva | 205 / 13 | 1,04 [0,93; 1,20] ([0,90; 1,20]) | **1,25 [1,02; 1,34]** ([1,12; 1,39]) |

## R1b: Spearman parcial dentro de departamento (el análogo directo de C-2 con efectos fijos)
| Ámbito | ρ dentro de departamento | IC 95 % | ρ de C-2 sin efectos fijos |
|---|---:|---|---:|
| Perú | −0,042 | [−0,106; +0,009] | −0,087 |
| Costa | **+0,154** | [+0,082; +0,222] | +0,228 |
| Sierra | **−0,089** | [−0,131; −0,034] | −0,223 |
| Selva | +0,036 | [−0,118; +0,163] | +0,076 |

## Lectura (exploratoria)
1. **Viviendas dañadas (Y1): ninguna asociación en ningún ámbito.** Todos los intervalos incluyen 1. Con efectos fijos de departamento, la exposición vial a terreno bajo no predice daño a viviendas en Perú.
2. **Sierra: la asociación negativa se reduce a la mitad o menos.** Pasa de ρ = −0,22 a −0,09, y en el modelo de conteo la razón de tasas es 0,88 con un intervalo que roza 1 (límite superior 1,01). Se confirma la sospecha del bloque 1: **la mayor parte del signo negativo era una diferencia entre departamentos**, no una relación dentro de ellos. Queda un efecto pequeño y de signo negativo que no se puede distinguir de cero en el modelo de conteo.
3. **Costa: se mantiene positiva dentro de departamento** (ρ = +0,15; RR 1,11), pero recuérdese R9a: sin 2023 la asociación de la costa desaparece. Dos hallazgos que se leen juntos: dentro de cada departamento hay asociación, pero la sostiene un año.
4. **Selva: los dos métodos discrepan.** El modelo de conteo da un RR de 1,25 para km de carretera (positivo) y el ρ de rangos es 0,04 (nulo). Con 205 distritos y 13 departamentos, y un Y2 de cola pesada, el modelo de conteo puede estar dominado por pocos distritos con muchos kilómetros dañados. No se interpreta; hace falta mirar influencia.
5. **Perú completo: nulo en ambos resultados.** No hay patrón único.

## Límites de este bloque
- R1 incompleto: faltan lluvia p95, % urbano y NBI. Sin ellos, la vulnerabilidad social y la lluvia local no están controladas.
- Pocos departamentos por ámbito (13 a 25): los IC agrupados son poco confiables, por eso se da también el de remuestreo; entre ambos hay diferencias (por ejemplo costa, Y2).
- Sin corrección por multiplicidad entre los 12 intervalos. Si ninguna asociación fuera real, esperaríamos que alguno excluyera 1 por azar; los de la costa y la selva en Y2 tienen límites inferiores de 1,02, muy cerca de 1.
- Y2 incluye toda la red vial y E solo la principal de OSM.


# Bloque 3 exploratorio: R5, controles negativos (2026-11-08)
Mismo modelo que R1 (cuasi-Poisson con efectos fijos de departamento, desfase log población) y mismo Spearman parcial dentro de departamento, pero con otros resultados, todos en viviendas destruidas + afectadas por 100 mil habitantes. Código: `peru_r5_controles_negativos.py` (commit 06fe08e, publicado antes de correr). 1.000 réplicas de remuestreo de departamentos por modelo (no 2.000 como R1). Todo exploratorio.

- (a) Movimientos en masa (deslizamiento, derrumbe de cerro, alud): control negativo, con la salvedad de que dependen del relieve.
- (b) Incendio forestal: control negativo.
- (c) Inundación + huayco (Y3 del protocolo): referencia, el peligro que la hipótesis sí vincula con terreno bajo.

## Razón de tasas por +0,10 de E [IC 95 % por remuestreo de departamentos]
| Ámbito | (a) mov. en masa | (b) incendio forestal | (c) inundación + huayco |
|---|---|---|---|
| Perú (n = 1.483) | 1,01 [0,83; 1,17] | 0,96 [0,75; 1,21] | 1,09 [0,99; 1,22] |
| Costa (329) | 0,75 [0,38; 4,02] | 1,24 [0,95; 4,89] | 1,09 [0,94; 1,80] |
| Sierra (936) | 0,98 [0,68; 1,30] | 0,97 [0,74; 1,25] | 1,21 [0,98; 1,38] |
| Selva (205) | 1,12 [0,80; 1,37] | 1,04 [0,74; 1,22] | 1,08 [0,91; 1,33] |

## Spearman parcial dentro de departamento
| Ámbito | (a) mov. en masa | (b) incendio forestal | (c) inundación + huayco |
|---|---|---|---|
| Perú | −0,009 [−0,066; +0,041] | +0,035 [−0,022; +0,098] | +0,047 [−0,003; +0,117] |
| Costa | −0,074 [−0,105; +0,039] | +0,136 [−0,012; +0,204] | **+0,196 [+0,064; +0,223]** |
| Sierra | −0,014 [−0,096; +0,072] | +0,025 [−0,039; +0,107] | +0,066 [−0,014; +0,148] |
| Selva | **−0,096 [−0,466; −0,006]** | +0,082 [−0,155; +0,190] | +0,188 [−0,027; +0,295] |

Proporción de distritos con algún daño a viviendas: mov. en masa 27,6 %; incendio 21,2 %; inundación + huayco 40,5 %.

## Lectura (exploratoria)
1. **Los controles negativos se comportan como tales a nivel nacional.** Para movimientos en masa e incendio forestal, en Perú, la razón de tasas está en 1,01 y 0,96 y el ρ en −0,01 y +0,04, con intervalos que incluyen el valor nulo. La medida de exposición vial no parece estar captando un sesgo general de reporte o de tamaño del distrito.
2. **El resultado de referencia (inundación + huayco) apunta en el sentido de la hipótesis, pero débil.** RR 1,09 en Perú con límite inferior 0,99, ρ = +0,05 con límite inferior −0,003. En la costa el ρ es +0,20 con intervalo que excluye 0; en la sierra el RR es 1,21 con límite inferior 0,98. Es un patrón compatible con la hipótesis, no una confirmación, y no cambia el veredicto de C-1 y C-2.
3. **Por región los controles no son uniformemente limpios.** En la selva el ρ de movimientos en masa tiene un intervalo que excluye 0 (−0,10, límite superior −0,006) con solo 205 distritos y un intervalo de remuestreo muy ancho (hasta −0,47). Con 36 intervalos en este bloque, que uno excluya el valor nulo es lo esperable por azar (alrededor de 2 de 36 con 95 %); no se interpreta, pero queda reportado. En la costa el ρ del incendio forestal (+0,14) y los RR de costa con cola superior de 4 a 5 muestran la inestabilidad de ese ámbito (13 departamentos).
4. **Coherencia con R9a.** La señal de la costa en el resultado de referencia es la misma región en la que R9a mostró que la asociación depende de 2023, por lo que tampoco debe leerse como robusta.

## Límites de este bloque
- Sin corrección por multiplicidad entre los 36 intervalos; los resultados con intervalo que excluye el valor nulo son pocos y cercanos al borde.
- Los movimientos en masa dependen del relieve, que correlaciona con E en la sierra, así que no es un control limpio allí; el control más informativo es el incendio forestal.
- Mismos faltantes que R1: lluvia p95, % urbano y NBI.
- Y3 se mide con registros de viviendas, no de red vial; no es el mismo daño que Y2.
- 1.000 réplicas por modelo; los extremos de los IC en la costa (RR hasta 4,9) son inestables.
