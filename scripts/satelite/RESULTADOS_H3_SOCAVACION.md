# Resultados H3 (#273): índice de socavación y continuidad vial (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §27, commit `7bbbc36`, publicado en [#273](https://github.com/wilmerjoseperezorozco-dev/structai/issues/273#issuecomment-6977590287) antes de leer el resultado.
- **Código:** `h3_socavacion_puentes.py`, sin cambios después del prerregistro.
- **Salida:** `h3_socavacion_resultados.json`.

**Muestra:** 1.000 municipios de 21 departamentos.
- 92 municipios tuvieron al menos un puente vehicular averiado por eventos hídricos en 2023-2024. Como son ≥ 30, no se activó la regla de potencia y no se sumaron los puentes peatonales.
- Intervalos: IC95 % por bootstrap por departamento, 2.000 réplicas.

## Criterios prerregistrados

| Criterio | Resultado | ¿Se cumple? |
|---|---|---|
| **C1:** AUC del índice para "hubo puente averiado en 2023-2024" | **0,75** [0,70; 0,81] | Sí; supera el umbral de 0,65 |
| **C2:** AUC(índice) − AUC(solo historial) | +0,04 [−0,02; +0,12] | **No**: el IC contiene 0 |
| **C3:** ρ parcial controlando población y capacidad de reporte | **+0,25** [+0,20; +0,30] | Sí |

**Lectura:**
- El índice **ordena bien** los municipios que tendrán puentes averiados en los dos años siguientes, y no es solo un efecto del reporte (C3).
- Pero **no se demostró que la hidrología y el relieve agreguen algo al historial** (C2). Con estos datos, "dónde ya se dañaron puentes" predice casi igual de bien.

## Descriptivo

**AUC por componente:**
- historial H: 0,71;
- pendiente S: 0,67;
- torrencialidad T (Q10/Q2): 0,57.

T es el componente más débil, coherente con que se calcula en la estación más cercana y no en la cuenca del puente.

**Otros resultados:**
- **Solo municipios con estación a ≤ 50 km** (n = 961): AUC 0,74.
- **Por región:**

| Región | n | AUC |
|---|---|---|
| Andina | 628 | 0,72 |
| Pacífica | 148 | 0,78 |
| Caribe | 195 | 0,75 |

  Son estimaciones puntuales sin intervalo. **El Caribe tiene solo 7 positivos.**
- **AUC de Aa (NSR-10 A-4): 0,61.** Lo esperado en el prerregistro era ≈ 0,5, y **no se cumplió**.
  - La explicación más probable es la confusión con el relieve: el Aa alto está en la zona andina, que es empinada, y la pendiente sola da 0,67.
  - No se probó; queda como pregunta para H5, que controla la región o la pendiente.

## Qué no se concluye

- **No se concluye que los puentes fallaron por socavación local:** la UNGRD no registra el mecanismo ni inventaría los puentes expuestos.
- **El índice sirve para priorizar inspecciones, no para diseñar.**

## Siguiente paso posible (versión 2, necesitaría datos nuevos para validarse)

Torrencialidad por cuenca aguas arriba del puente, en vez de la estación más cercana. Requiere la red de drenaje (`aguas_arriba_fluvial.py` existe solo para el Caribe) y un inventario de puentes (INVIAS o OSM).
