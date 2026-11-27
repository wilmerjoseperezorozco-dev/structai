# Resultados H2b (#273): validación fuera de muestra de la regla de relieve (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §31, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6995471867) antes de evaluarla.
- **Código:** `h2b_validacion_relieve.py`. **Salida:** `h2b_validacion_resultados.json`.
- **Regla:** relieve local (cota DEM − mínima a ≤ 1 km) **≤ 6,5 m → alarma** de nivel freático somero.

## Casanare (llanura, 494 puntos, 24 bloques): **VALIDADA**

| Nivel | Prevalencia | AUC del relieve | Sensibilidad | Especificidad | VPP de la alarma |
|---|---|---|---|---|---|
| **≤ 2 m** | 75 % | **0,74** [0,65; 0,81] | 0,77 | 0,57 | **0,84** [0,79; 0,89] |
| ≤ 3 m | 89 % | 0,85 [0,73; 0,92] | 0,74 | 0,77 | 0,96 [0,94; 0,99] |

- La regla, fijada en Meta, Guaviare e Inírida, conserva su capacidad en Casanare. El AUC baja de 0,77 a 0,74, como se espera fuera de muestra.
- Funciona igual en pozos (0,76) y en aljibes (0,78).
- **Salvedades:**
  - En Casanare el agua es somera en casi todas partes (75 % de los puntos), así que la ganancia del VPP sobre la prevalencia es modesta: de 75 % a 84 %.
  - La validación tiene una contaminación parcial: en H2 vi el AUC del índice en Casanare, no el del relieve.

## Quindío (andino, 258 puntos, 12 bloques): **NO SIRVE**

| Nivel | Prevalencia | AUC del relieve | Alarmas |
|---|---|---|---|
| ≤ 2 m | 5 % | 0,57 [0,17; 0,81] | 0,8 % de los puntos |
| ≤ 5 m (criterio) | 14 % | 0,52 [0,35; 0,74] → NO CONCLUYENTE | 0,8 % |

- En terreno montañoso casi ningún punto tiene un relieve local ≤ 6,5 m, así que la alarma casi nunca se enciende.
- Además, el relieve no ordena la profundidad (ρ = 0,06). En los Andes el nivel freático depende de otras cosas (ceniza volcánica, acuíferos colgados, fracturas) que un DEM de 90 m no ve.

## Lectura (fijada de antemano)

- **Para StructAI:** la alarma "posible nivel freático somero" basada en el relieve **se puede usar en llanuras y valles aluviales** (validada en Casanare), siempre como orientativa y con la recomendación de verificar con apique o piezómetro.
- **En zona andina no se muestra.** Hay que decir en `/sitio` que el indicador no aplica en ladera.
- **Pendiente:** definir de forma objetiva cuándo un sitio es "llanura" (por ejemplo, la pendiente p90 del municipio o la pendiente local del DEM) y validar ese límite.

## Limitaciones

- La validación está concentrada en una región (Orinoquía).
- Los niveles son de fechas distintas.
- El campo de nivel se confirmó por consistencia, no con el diccionario oficial del SGC.
- Quindío tiene pocos casos someros.
