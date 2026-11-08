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
