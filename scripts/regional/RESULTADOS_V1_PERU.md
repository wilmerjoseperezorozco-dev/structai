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
