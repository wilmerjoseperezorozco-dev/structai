# Resultados H2 (#273): nivel freático somero inferido sin perforar (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §30, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6995348139) antes de cruzar niveles con predictores.
- **Código:** `h2_saturacion_freatica.py`, sin cambios después del prerregistro. **Salida:** `h2_saturacion_resultados.json`.
- **Muestra principal:** 453 pozos y aljibes con nivel estático medido (SGC; Meta, Guaviare e Inírida). El 43 % tiene el nivel a ≤ 2 m. Son 27 bloques de 0,1°.

## Veredicto principal (C1, nivel ≤ 2 m): **NO CONCLUYENTE**

| Predictor | AUC | IC95 % |
|---|---|---|
| **Índice completo** (relieve + estación IDEAM + IGAC) | **0,71** | [0,58; 0,83] |
| **Relieve local solo** (DEM, cota − mínima a ≤ 1 km) | **0,77** | [0,67; 0,85] |
| Relieve a 3 km | 0,70 | [0,60; 0,80] |
| Altura sobre la estación IDEAM más cercana | 0,68 | [0,52; 0,80] |
| IGAC municipal (drenaje deficiente + inundable) | 0,44 | [0,34; 0,58] |

- **C2:** ΔAUC (índice − relieve solo) = **−0,06** [−0,12; +0,01]. La cadena completa **no** mejora al relieve. El IGAC municipal resta.
- **Lo que funciona es el DEM.** El relieve local discrimina bien (0,77, IC por encima de 0,60), y la correlación del índice con la profundidad es ρ = −0,51.
- **El IGAC municipal no sirve a nivel de punto.** Casi no varía dentro de la muestra (el 92 % de los puntos está en 3 municipios) y en esos municipios va en contra (0,44). Era la salvedad prerregistrada: una fracción municipal no describe el lote.

## Sensibilidad

| Variante | AUC del índice | IC95 % | Veredicto |
|---|---|---|---|
| Nivel ≤ 1 m | 0,63 | [0,50; 0,74] | NO CONCLUYENTE |
| **Nivel ≤ 3 m** | **0,78** | [0,67; 0,89] | **ÚTIL** |
| Con Casanare (947 puntos, campo ambiguo) | 0,78 | [0,70; 0,85] | ÚTIL (ahí el IGAC sí aporta: 0,65) |

**Por tipo y capa** (nivel ≤ 2 m):
- **Por tipo:** pozos 0,80; aljibes 0,65.
- **Por capa:** Meta 0,78, Inírida 0,76 y Guaviare 0,62.

**Alarma "índice en el tercio superior"** (nivel ≤ 2 m):
- detecta el 48 % de los puntos someros;
- acierta el 62 % de las veces, frente a una prevalencia del 43 %.

## Lectura (fijada de antemano)

- **La hipótesis, tal como se formuló** (IGAC + estación IDEAM + cota): **no confirmada** en el umbral prerregistrado. El IC del índice baja de 0,60.
- **Hallazgo útil para StructAI:** el **relieve local del DEM** solo sí discrimina el nivel freático somero (AUC 0,77, y 0,83 para ≤ 3 m) en estas llanuras. Para `/sitio` conviene una alarma basada en el relieve, no en la fracción IGAC municipal: "posible nivel freático somero: verificar con apique o piezómetro". **No sustituye la medición.**
- **El IGAC sirve para describir el municipio, no el lote.** Para usarlo a nivel de punto habría que tener los polígonos de las unidades de suelo, no la tabla municipal.
- Como la regla del relieve se identificó después de ver los resultados, hay que validarla en otra muestra antes de ponerla en producción. Sirven Casanare o Quindío con el campo confirmado, o datos de otra región.

## Limitaciones

- Las mediciones son de fechas y estaciones distintas.
- Hay sesgo de selección en los aljibes.
- Solo hay llanuras orientales; no se puede generalizar.
- Hay pocos bloques espaciales.
- El DEM de 90 m mide superficie, no terreno.
- La estación más cercana puede estar en otro río.
- El caudal actual no entró.
