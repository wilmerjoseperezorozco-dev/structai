# Resultados H6 (#273): vías principales en terreno bajo frente a vías averiadas por eventos hídricos (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §32, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6996094890) antes de cruzar exposición con daño vial.
- **Código:** `h6_vias_terreno_bajo.py`.
  - **Corrección de implementación:** la primera ejecución falló antes de producir resultados, porque la matriz de controles se pasó traspuesta a `parcial`. Se corrigió (cada control como columna) sin cambiar el análisis.
- **Salida:** `h6_vias_resultados.json`.
- **Muestra:** 729 municipios con ≥ 5 km de vía principal, en 21 departamentos.

## Veredictos

| Medida | Valor | IC95 % | Veredicto |
|---|---|---|---|
| **C1:** ρ parcial(expo_vial, vías averiadas hídricas 2019-2024 \| población, reporte, km de vía, pendiente) | **+0,12** | [+0,03; +0,21] | **CONFIRMADA** (justo encima del umbral de 0,10) |
| **C2:** lo mismo en 2023-2024, controlando además el índice H3 | +0,03 | [−0,06; +0,15] | **NO CONCLUYENTE** |
| ρ bruto (sin controles) | −0,01 | | |
| Control negativo (incendios forestales) | +0,02 | | sin sesgo aparente |

## Cómo leerlo

- **La asociación existe, pero solo después de controlar la pendiente, y es débil.**
  - Sin controles es nula (−0,01). En los municipios montañosos hay mucho daño vial (por crecientes y avenidas torrenciales) y pocas vías en terreno bajo. Ese efecto tapa el de la llanura.
  - A igual pendiente, población y red, más vía en terreno bajo se asocia con algo más de daño vial por agua.
  - Es más claro en el tercil llano (+0,16) que en el medio (+0,04) y el montañoso (+0,07).
- **No sirve para predecir.**
  - Para "alguna vía averiada en 2023-2024", el AUC de expo_vial es 0,48 [0,42; 0,54]. El índice H3 da 0,64 [0,57; 0,71], y combinar los dos **empeora** el resultado (0,61).
  - Controlando H3, expo_vial no agrega información confirmada (C2).
- **Por región:**

  | Región | n | ρ parcial | IC95 % |
  |---|---|---|---|
  | Andina | 452 | +0,11 | [+0,01; +0,21] |
  | Caribe | 159 | +0,14 | [−0,10; +0,32] |
  | Pacífica | 100 | +0,08 | [+0,06; +0,31] |

  En la Pacífica el IC no contiene la estimación puntual: con solo 4 departamentos el bootstrap es inestable, así que no se interpreta.

## Lectura (fijada de antemano)

- **C1 confirmada, C2 no:** hay una relación física coherente (vías en terreno bajo, más daño por agua, a igual relieve), pero es pequeña y no mejora al índice H3 para priorizar.
- Con V1 (viviendas), el patrón se repite: **el HAND municipal de 90 m tiene señal, pero muy débil para decidir**.
- **Para StructAI:**
  - mostrar en `/sitio` la fracción del corredor vial en terreno bajo como **contexto**, no como indicador de priorización;
  - para priorizar, el índice H3 sigue siendo mejor.
  - El paso que podría cambiar esto es medir por **tramo o punto**, no por municipio. Hoy no hay daño vial georreferenciado en la UNGRD.

## Limitaciones

- `vias_averiadas` es un conteo de la UNGRD, sin tipo ni longitud, e incluye vías terciarias que el predictor no mide.
- OSM es voluntario.
- El HAND de 90 m no ve terraplenes.
- Es un análisis municipal (falacia ecológica).
- Hay pocos departamentos por región para los IC regionales.
