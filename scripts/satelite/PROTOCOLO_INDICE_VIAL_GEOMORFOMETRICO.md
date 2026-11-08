# Protocolo: índice geomorfométrico de exposición para vías terciarias, solo con DEM (preregistrado 2026-11-08, antes de calcular ningún índice)

**Pregunta.** ¿Se puede ordenar la red vial terciaria de un territorio por condiciones del terreno usando solo tres variables derivadas del modelo digital de elevación (pendiente crítica, índice topográfico de humedad TWI y distancia a drenajes), sin cartografía geológica? Y la pregunta que decide si vale la pena: **¿el índice de tres variables ordena mejor que la pendiente sola?**

## 0. Dos correcciones a las premisas, antes de empezar
1. **«Las vías en terreno bajo concentran daños en el Caribe» no es lo que encontramos.** El resultado C1a (`RESULTADOS_VIAS_HAND.md`) fue **«no se confirma»**: la red vial *principal* (troncal, primaria, secundaria; no terciaria) tiene +2,9 puntos porcentuales más de exposición a terreno bajo que el territorio, con IC95 % [−0,001; +0,074]. Además **no se validó contra daños**: la UNGRD no registra daños a vías. Es exposición del terreno, no daño.
2. **«La pendiente sola ordena igual que el mapa del SGC»** es cierto en el análisis municipal (AUC 0,78 frente a 0,76), pero con tres matices: no probé si la diferencia es distinguible, los eventos de la UNGRD son *reportes* (con sesgo de reporte), y en el Caribe el AUC de ese mapa es solo 0,59 (la pendiente sola tampoco se midió por región).

## 1. Lo que el índice es y no es
Es un **índice de exposición del terreno** (qué tramos están en condiciones geomorfométricas desfavorables). **No es un índice de priorización de inversión**: eso exigiría además beneficiarios, tránsito, estado actual del camino y costos, que no tenemos. Se ofrece una capa descriptiva aparte «exposición × beneficiarios» (población rural y NBI del municipio), no fundida en el índice.

## 2. Datos
- **Vías:** OpenStreetMap vía Overpass, `highway` ∈ {`tertiary`, `unclassified`, `track`}, con la marca de tiempo de la base. **Límite:** la clase de OSM no es la clasificación legal de vía terciaria (INVIAS / entes territoriales); la cobertura es voluntaria y varía por departamento. La red terciaria oficial de INVIAS (`ie7y-asdn` es la red vial, sin verificar si incluye terciaria) queda para una etapa posterior, tras verificar su cobertura.
- **Terreno:** Copernicus DEM de ~90 m ya descargado (`dem90_<depto>.tif`), con el mismo acondicionamiento de `calcular_hand_caribe.py`.
- **Ámbito:** primario, los 7 departamentos del Caribe continental (08, 13, 20, 23, 44, 47, 70). Secundario, 3 departamentos andinos (05, 25, 68) como contraste de relieve.
- **Validación (indirecta):** eventos de la UNGRD 2019-2024 por municipio, con los controles de sesgo de reporte ya usados (población y el indicador P_A).

## 3. Variables (fijadas ahora)
Muestreo de puntos cada ≈ 90 m a lo largo de cada tramo.
- **Pendiente crítica (C):** fracción de los puntos con pendiente ≥ 15° (umbral fijo; 10° y 25° como sensibilidad).
- **TWI (W):** ln(a / tan β), con a = área de contribución específica (D8) y β la pendiente local; se reporta el percentil 90 del tramo (cuanto mayor, más saturación probable).
- **Distancia a drenaje (D):** distancia al cauce de la red de ≥ 5 km² de área aguas arriba (la misma de HAND); se usa la fracción de puntos a menos de 100 m (100 m, 50 m y 200 m como sensibilidad).

## 4. Índices comparados (sin pesos ajustados a los resultados)
- **I3 (primario):** promedio de los tres rangos percentiles (C, W, D), pesos iguales y fijados ahora. No se ajustan pesos con los eventos de la UNGRD, para no inflar la validación con los mismos datos.
- **I1 (referencia):** solo C (pendiente crítica).
- **I2:** C y D. Sensibilidad: percentil de pendiente p90 en lugar de C.

## 5. Criterios (a nivel municipal; el índice municipal es la media ponderada por longitud de los tramos)
- **V1 (confirmatorio):** ρ parcial de Spearman entre I3 municipal y eventos por 100 km² (movimiento en masa + inundación), controlando población y P_A; IC95 % por bloques de departamento; se cumple si excluye 0.
- **V2 (confirmatorio, el que importa):** ΔAUC = AUC(I3) − AUC(I1) para «hubo al menos un evento»; IC95 % por bloques pareado. **El índice de tres variables «añade valor» solo si el IC excluye 0 a favor de I3.** Dado que ya vimos que la pendiente sola rinde como un mapa complejo, el resultado nulo es plausible y se publica como tal.
- **V3 (descriptivo):** V1 y V2 por región; en el Caribe el relieve es bajo y se espera que C discrimine poco y W/D más.
- **Descriptivo:** correlación entre C, W y D (redundancia); lista de los 20 tramos y de los 20 municipios con mayor índice, sin nombrar estructuras.

## 6. Qué NO se concluye
Que un tramo vaya a fallar, que su construcción sea prioritaria o urgente, ni nada sobre su estado. Que el índice «prediga daños»: la validación usa reportes municipales de eventos, no daños a vías ni ubicaciones de los eventos.

## 7. Limitaciones de antemano
DEM de 90 m: no resuelve taludes de corte ni terraplenes, que son los que fallan en una vía; el TWI y la distancia a drenaje de 90 m son gruesos, sobre todo en llanuras. Sin geología ni suelos. La clase de vía de OSM no es la categoría oficial. La validación es por municipio y por reportes (sesgo de reporte, fuente de 6 años con 2022 atípico). El Caribe es llano: se espera poco poder de la pendiente. **No sustituye una inspección de campo ni un estudio geotécnico.**

## 8. Qué se publica pase lo que pase
V1, V2 y V3, los coeficientes de redundancia y la comparación contra la pendiente sola, incluso si I3 no supera a I1.
