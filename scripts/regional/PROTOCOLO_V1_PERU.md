# Protocolo V1-Perú: réplica de la hipótesis de exposición vial a terreno bajo con SINPAD (preregistrado 2026-11-08, antes de obtener polígonos, población, red vial, DEM o lluvia de Perú y antes de calcular ninguna asociación)

Pertenece a la fase F4/P4 de `docs/PROTOCOLO_REPLICACION_PAISES_VECINOS_2026-11.md` y se apoya en `docs/F1_VERIFICACION_FUENTES_PERU_ECUADOR_2026-11.md`. Sigue la estructura de `scripts/satelite/PROTOCOLO_V1_CONFIRMACION.md` y `PROTOCOLO_SESGO_REPORTE.md`.

**Qué he visto de los datos antes de fijar este protocolo (declaración de transparencia).** Solo el perfil descriptivo de SINPAD (`scripts/regional/sinpad_perfil.py`): filas por año, tipos de peligro, fracción de registros con daño distinto de cero y distritos con evento por año, **a nivel nacional**. No he cruzado SINPAD con ningún distrito, vía, terreno, población ni lluvia. Ninguna decisión de abajo depende de una asociación observada.

## 1. Hipótesis y por qué se prueba en Perú

**V1 (Colombia).** Los municipios cuya vía principal está sobre terreno bajo respecto al cauce (HAND < 10 m) reportan más daños por habitante, más allá del terreno del municipio completo. Estado: **descubierta en el Caribe (ρ ≈ +0,34), no confirmada fuera de él (ρ = 0,00, IC95 % [−0,10; +0,11], n = 570)**; no mejora la focalización (`RESULTADOS_V1.md`).

**Por qué Perú aporta algo nuevo y no solo otra muestra:**
1. Es un país con otra geología, otro clima y otro registro de emergencias, es decir, una prueba **independiente** de si la asociación es general.
2. SINPAD registra **daño a vías y puentes** (kilómetros de carretera destruida y afectada, puentes), cosa que la UNGRD no tenía. Permite probar la versión física de V1: exposición vial a terreno bajo frente a **daño a la vía**, no solo frente a daño a viviendas.
3. Hay tres regiones naturales muy distintas (costa árida, sierra, selva), lo que prueba directamente la lección de Colombia: «terreno bajo» no significa lo mismo en llanura y en montaña.

**Expectativa, fijada ahora:** dado que en Colombia fuera del Caribe el efecto fue nulo, la expectativa de referencia es **ρ ≈ 0**. Un resultado positivo en Perú no convertiría a V1 en ley general: sería una segunda región con efecto, a contrastar con la heterogeneidad.

## 2. Datos (todos por obtener; nada de lo siguiente está descargado)

| Insumo | Fuente prevista | Estado de verificación |
|---|---|---|
| Emergencias SINPAD 2019–2024 | Ya en mano: `BD_2003-2025_EMERGENCIAS.csv` (INDECI, ODC-BY) | Perfilado; ver `F1_...md` |
| Catálogo de distritos (UBIGEO), polígonos y área | INEI / IGN (a verificar) | **Sin verificar** |
| Población por distrito (Censo 2017) | INEI | **Sin verificar** |
| NBI o pobreza por distrito | INEI | **Sin verificar** |
| Red vial (OSM: troncal, primaria, secundaria) y lugares poblados | OpenStreetMap, extracción regional | **Sin verificar**: tamaño y fecha por declarar |
| DEM Copernicus 90 m y HAND (red de 5 km², mismo método que `calcular_hand_caribe.py`) | Copernicus DEM | Mismo insumo ya usado en Colombia |
| Lluvia mensual (p95) | CHIRPS | Mismo insumo ya usado en Colombia |

**Regla de sustitución, fijada ahora:** si no se obtiene NBI distrital, se omite esa covariable y su interacción (R2) y se declara; no se reemplaza por un indicador inventado. Si la población del censo 2017 no está disponible por distrito, la prueba **no se ejecuta** (la tasa por habitante es el resultado; una población estimada por celdas se podría usar solo en una versión posterior declarada como otro protocolo).

**Unidad y periodo.** Distrito (UBIGEO, 6 dígitos). Eventos de **2019 a 2024** (igual que la ventana colombiana); se excluyen 2025 (fecha en formato distinto y año en curso) y 2026. Para el recuento se usa la columna `AÑO`, no se interpreta `FECHA`. Los distritos del SINPAD que no estén en el catálogo del INEI se **excluyen y se cuentan** (se informa cuántos y cuánto representan en eventos). Un distrito sin eventos tiene resultado 0 (el registro solo contiene emergencias, por lo que ausencia = cero, **supuesto declarado**, y es el mismo que en Colombia).

**Inclusión.** Distritos con al menos 5 km de vía principal (troncal + primaria + secundaria de OSM) y datos completos de las variables primarias. Se reporta cuántos distritos y cuánta población quedan fuera por esta regla y su distribución por región natural (la cobertura de OSM en la selva puede ser mínima; si la selva queda con menos de 15 distritos incluidos se informa «no evaluable» para ella).

## 3. Variables

- **Exposición vial (E):** fracción de la longitud de vía principal del distrito con HAND < 10 m. Definición idéntica a Colombia.
- **Terreno del distrito (T):** fracción del área del distrito con HAND < 10 m.
- **Resultado primario (Y1), comparable con Colombia:** viviendas destruidas más viviendas afectadas, por 100 mil habitantes, **sumando todos los tipos de peligro**.
- **Resultado secundario (Y2), el nuevo:** kilómetros de carretera destruida más carretera afectada por 100 km² de distrito. Se usan las columnas `CARRETERA DESTRUIDA KM` y `CARRETERA AFECTADA KM`. El SINPAD no distingue la red principal de la secundaria o rural, así que Y2 mide daño a la red vial total y E mide la exposición de la red principal: **desajuste conocido**, que se discute y no se corrige.
- **Resultado terciario (Y3):** viviendas dañadas solo por inundación y huayco (peligros `INUNDACION` y `HUAYCO`); sensibilidad: añadir `LLUVIA INTENSA`. Es el equivalente de la versión «solo inundación» de Colombia.
- **Controles de V1 (idénticos a Colombia):** log(población), log(área), T. Para Y2 se añade además la **densidad de vía principal** (km por 100 km²), porque más vía puede dañarse más.
- **Capacidad de reporte (P_A):** log(1 + registros de `INCENDIO URB. E INDUST.` por 100 mil habitantes), todos los años de 2019–2024. Sensibilidad P_B: todos los peligros no hidrometeorológicos ni de movimientos en masa ni de incendio forestal (incendio urbano, explosión, derrame, contaminación, otros). Sensibilidad P_C: fracción de los registros del distrito sin ningún efecto cuantificado, solo distritos con ≥ 3 registros. Se declara que **el 0 de los daños puede ser «no evaluado»**: P_C mide eso y no distingue.
- **Región natural:** costa, sierra y selva (selva alta y baja unidas), asignada a cada distrito por la modalidad de la columna `REGIÓN NATURAL` de sus registros. Distritos sin registros: por el departamento dominante según una tabla fijada antes de cruzar (departamentos de la costa, sierra y selva por la clasificación del INEI; si no se obtiene, se omiten de los análisis por región y se informa).
- **Bloques para la incertidumbre:** los 25 departamentos (24 más Callao). Todos los IC95 % son por remuestreo de departamentos (con Lima y Callao dentro; sensibilidad sin ellos).

## 4. Compuerta de datos (se evalúa antes de cualquier asociación)

Se calcula y publica primero, sin asociaciones: nº de distritos incluidos, población incluida, distribución de E por región natural, tasa de distritos con Y1 > 0 y con Y2 > 0, y nº de departamentos con al menos 10 distritos incluidos.

La prueba confirmatoria se declara **«no concluyente por falta de potencia»** (y no se interpreta) si ocurre cualquiera de estas condiciones, fijadas ahora:
- menos de 300 distritos analizables en total;
- menos de 15 departamentos con al menos 10 distritos incluidos;
- más del 90 % de los distritos con Y1 > 0 o menos del 10 %;
- E tiene un rango intercuartílico menor que 0,05 (sin variación suficiente).

Aprendido del índice vial colombiano: un resultado casi constante o con muy pocos bloques no se puede interpretar.

## 5. Pruebas confirmatorias

**C-1 (primaria, comparable con Colombia).** Correlación parcial de Spearman entre E y Y1 controlando log(población), log(área) y T. **Se replica** si el IC95 % por departamentos tiene límite inferior > 0 **y** ρ ≥ 0,15. **No se replica (ausencia práctica)** si todo el IC95 % queda dentro de ±0,15 (equivalencia). En otro caso, **no concluyente**.

**C-2 (nueva, daño a vías).** Igual, con Y2 y los controles de C-1 más la densidad de vía principal. Mismo criterio.

**Corrección por multiplicidad:** Holm sobre {C-1, C-2}. Y3 y todo lo demás son secundarios.

Cada confirmatoria se reporta **en Perú completo y por región natural** (costa, sierra, selva), con la misma regla; el resultado «de Perú» no se resume en una sola cifra si las regiones difieren de signo.

## 6. Pruebas exploratorias (todas se reportan; Holm dentro de cada bloque)
- **R1. Modelo cuasi-Poisson** de Y1 (con desfase log población) con efectos fijos de departamento, errores agrupados por departamento. Covariables: E, T, log área, % urbano (si se obtiene), NBI (si se obtiene), lluvia p95 mensual, **elevación media y pendiente media del distrito** (añadidas por la heterogeneidad de relieve). Razón de tasas por +0,10 de E. Se reporta la muestra conjunta y cada región.
- **R2. Interacciones** de E con % urbano, NBI y lluvia p95 (una a una).
- **R3. Tipo de vía** (troncal, primaria, secundaria por separado).
- **R4. Mecanismo.** Razón de momios (Mantel-Haenszel por distrito) de que un lugar poblado de OSM esté en terreno bajo si queda a ≤ 1 km de vía principal, y cambio del coeficiente de E al añadir esa fracción. Mismos indicadores que `RESULTADOS_V1.md`.
- **R5. Controles negativos.** Mismo modelo con (a) movimientos en masa (`DESLIZAMIENTO`, `DERRUMBE DE CERRO`, `ALUD`) y (b) `INCENDIO FORESTAL` por 100 mil habitantes. Una asociación fuerte indicaría sesgo de reporte o de tamaño. Atención: los movimientos en masa dependen del relieve, que correlaciona con E en la sierra; se interpreta con cautela.
- **R6. Focalización.** Validación dejando un departamento fuera: clasificación con (a) población, (b) población + T, (c) lo anterior + E; fracción de Y1 que acumula el 20 % mejor clasificado en el departamento omitido; diferencia (c) − (b) con IC95 % por departamentos. **Evalúa también Y2** (fracción de km de carretera dañada).
- **R7. Heterogeneidad.** Interacción E × región natural (Holm sobre 2). Si es significativa, no se reporta un efecto único.
- **R8. Sesgo de reporte (como `PROTOCOLO_SESGO_REPORTE.md`).** S1 (P_A frente a NBI/% urbano/población con efectos fijos), S2 (P_A frente a E y a la densidad de vía), S3 (atenuación del efecto de E en R1 al añadir P_A; «explica la mitad» si 1 − ln(RR con P_A)/ln(RR sin P_A) ≥ 0,5; si el efecto es ≈ 1 no hay nada que atenuar), S4 (registros por 100 mil habitantes por región y año).
- **R9. Sensibilidades temporales.** (a) Sin 2023 (año del Niño costero y el ciclón Yaku, atípico; análogo a quitar 2022 en Colombia); (b) panel distrito-año con efectos fijos de año en lugar de totales; (c) sin Lima y Callao; (d) sin los 10 distritos con mayor Y1.
- **R10. Contexto comparado (descriptivo).** Gráfico de bosque con ρ de C-1 en Perú (total y por región) junto a los de Colombia (Caribe, resto, Andina, Pacífica). Se reporta la heterogeneidad (I²); no se interpreta como estimación única.

## 7. Qué se concluye según el resultado

| Resultado | Lectura permitida |
|---|---|
| C-1 y C-2 se replican | Es una segunda región con asociación; V1 sigue sin ser general (Colombia fuera del Caribe fue nulo). Pasa a revisarse si la asociación es de reporte (R8) o territorial |
| C-1 se replica y C-2 no | La asociación es con viviendas dañadas (población y vulnerabilidad), no con daño a vías |
| C-2 se replica y C-1 no | Hallazgo nuevo sobre daño a vías: requiere confirmación adicional (departamentos de arranque, otro año) antes de afirmar nada |
| Ninguno se replica | V1 se descarta como patrón general con dos países, aunque queda la excepción del Caribe |
| Equivalencia (IC dentro de ±0,15) | Se puede afirmar ausencia práctica en esa región |
| «No concluyente» | No se interpreta. Se informa qué falta |

## 8. Qué NO se concluye
- Ninguna asociación es causal. El objetivo es **focalizar** dónde inspeccionar o planificar, nunca atribuir culpa.
- Un resultado en Perú no modifica ningún resultado de Colombia ni se usa para decidir en Colombia.
- No se evalúa el estado de ninguna estructura ni se nombra ninguna (el SINPAD no la identifica).
- Los valores de E no son comparables entre llanura y montaña (en Colombia la mediana fue 0,56 en el Caribe y 0,17 en la Andina). Por eso hay análisis por región.

## 9. Límites declarados
- HAND de 90 m no ve diques, terraplenes ni encajonamiento; en cañones andinos «HAND < 10 m» puede ser el cauce entero.
- OpenStreetMap es voluntario: la cobertura de la selva puede ser baja y selecciona los distritos incluidos hacia los más conectados (sesgo de supervivencia); se reporta.
- SINPAD es un registro de **emergencias reportadas**, no de eventos; capacidad de reporte y riesgo real se mezclan. Los registros por año pasan de ~4.500 (2019) a ~13.700 (2024): puede ser físico o un cambio de práctica.
- Los daños en cero no distinguen «sin daño» de «no evaluado».
- Y2 mide daño a toda la red vial (incluida la rural), E mide solo la red principal de OSM.
- Los códigos de emergencia no son únicos (7 repetidos) y el SINPAD no tiene sitio exacto, solo distrito.
- El resultado de 2019-2024 puede estar dominado por pocos eventos grandes; por eso R9(d).
- Con 25 bloques el IC por departamentos puede ser ancho; la Costa tiene pocos distritos con vía en terreno bajo variable.

## 10. Orden de ejecución y permisos
1. Verificar y obtener catálogo UBIGEO, polígonos, población y NBI (INEI/IGN): **se pedirá permiso con nombre, fuente y tamaño antes de bajar cada archivo**.
2. Obtener red vial y lugares poblados de OSM por región (tamaño por declarar; fecha de extracción registrada).
3. Calcular HAND de Perú con el método ya usado (el DEM se descarga por teselas; tamaño por declarar).
4. Ejecutar la compuerta de datos (§4) y publicarla **antes** de cualquier asociación.
5. Solo si la compuerta pasa, correr C-1 y C-2 con el código fijado en un commit anterior a los resultados; luego lo exploratorio.
6. Informe de resultados con el mismo formato que `RESULTADOS_V1.md`, incluidos los resultados negativos y las verificaciones posteriores rotuladas como tales.
