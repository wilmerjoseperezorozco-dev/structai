# Protocolo del barrido exploratorio de relaciones entre variables municipales del Caribe (preregistrado 2026-11-08, antes de calcular ninguna correlación)

**Propósito.** Generar hipótesis, no confirmarlas. Con los datos que ya reunimos por municipio, buscar qué pares de variables de familias distintas se asocian más allá de lo esperable por el tamaño del municipio, para decidir qué hipótesis vale la pena preregistrar y confirmar después con datos nuevos.

**Unidad y alcance.** Municipios de los siete departamentos del Caribe continental (08, 13, 20, 23, 44, 47, 70) con datos completos en las variables que entran al barrido.

**Variables (fijadas ahora, por familia).**
- *Terreno (T):* elevación media, pendiente media (%), fracción con elevación < 10 m (DEM Copernicus 30 m), fracción con HAND < 10 m (red de 5 km²).
- *Suelo (S):* fracción de área con inundación según el IGAC.
- *Lluvia (L):* precipitación anual media 2019-2024 (CHIRPS), coeficiente de variación de la lluvia mensual, p95 de la lluvia mensual.
- *Eventos (E):* reportes UNGRD de inundación/creciente/avenida torrencial por 100 mil habitantes; personas afectadas por 100 mil habitantes en todos los eventos; viviendas destruidas o averiadas por 100 mil habitantes.
- *Infraestructura (I):* exposición vial (fracción de la vía principal con HAND < 10 m), km de vía principal por 100 km², puentes por 100 km de vía.
- *Social (O):* porcentaje de vivienda de material vulnerable (Sisbén), porcentaje de población en cabecera.
- *Amenaza oficial (A):* porcentaje del territorio en amenaza alta o muy alta por movimientos en masa (mapa del SGC).

**Controles.** log(población) y log(área): cada asociación se calcula como correlación **parcial de Spearman** (por rangos) controlando por ambos.

**Qué se compara.** Todos los pares de variables de **familias distintas** (los pares dentro de una misma familia son mecánicos y se reportan aparte como comprobación de consistencia, nunca como candidatos).

**Criterio de candidato.** Un par es **candidato** si cumple las tres condiciones:
1. q < 0,10 con corrección de Benjamini-Hochberg sobre todos los pares entre familias.
2. |ρ parcial| ≥ 0,20.
3. El signo se mantiene en las 7 omisiones de un departamento (leave-one-department-out).

**Qué NO se concluye.** Un candidato no es un hallazgo: es una hipótesis para preregistrar y confirmar con otros departamentos o con datos independientes. No se interpreta causalidad. Con 7 departamentos y menos de unos 160 municipios, la potencia es limitada y los falsos candidatos son esperables; por eso el umbral de efecto y la estabilidad por departamento.

**Límites declarados de antemano.** Los reportes de la UNGRD dependen de la capacidad del municipio para reportar; el HAND de 90 m y la cobertura de OpenStreetMap tienen los límites ya descritos en `PROTOCOLO_VIAS_HAND.md`; las variables de lluvia cubren solo 2019-2024. No se usan datos de personas ni de entidades contratantes.
