# E1: enrutador de dominio (issue #169)

Fecha: 2026-11-10. Sin LLM, sin escritura en Supabase, sin cambios en código de producción.
Reproducir:

```
python scripts/evaluacion/golden/e1_enrutador/generar_dataset_e1.py
python scripts/evaluacion/golden/e1_enrutador/e1_enrutador.py
```

Las cifras completas, por estrato y con las pruebas, están en `resultados_e1.json`.

## Datos

- 96 preguntas etiquetadas en 7 estratos y 52 plantillas. Partición por plantilla: 38 dev / 58 test.
- Fuga contra los ejemplos de referencia del contrastivo: 0 casos (ni duplicados exactos ni coseno ≥ 0,95).
- τ y δ se ajustaron **solo con dev**. Las cifras de abajo son de **test**.
- "Aceptable" incluye `normativa_general` para Aa/Av. Se verificó que `ask()` general también antepone el dato del SGC en vivo (`rag_multi_norma.py`, bloque `DATO OFICIAL EN VIVO (SGC)`).

## Resultados (test, n = 58)

| Variante | Estricto | Aceptable [IC95 Wilson] | Callejón falso¹ | McNemar vs V1 (Holm) |
|---|---|---|---|---|
| V0 solo keyword | 48,3 % | 84,5 % [73,1–91,6] | 0 | p = 0,115 |
| **V1 producción** | 55,2 % | **70,7 %** [58,0–80,8] | **6** | — |
| V2 umbral τ = 0,55 | 53,4 % | 86,2 % [75,1–92,8] | 2 | p = 0,047 |
| V3 margen δ = 0,18 sobre NG | 56,9 % | 86,2 % [75,1–92,8] | 2 | p = 0,047 |
| V4 regla municipio + intención sísmica | 82,8 % | 82,8 % [71,1–90,4] | 0 | p = 0,047 |
| **V5 regla + margen** | **89,7 %** | **89,7 %** [79,2–95,2] | **0** | **p = 0,017** |

¹ Pregunta respondible que termina en `vulnerabilidad_vivienda`: 0 `motor_chunks` y sin rama propia en el chat, así que la abstención está garantizada.

Caso de origen, "¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?" (ventaja sobre NG = 0,085):

| V1 | V2 | V3 | V5 |
|---|---|---|---|
| vulnerabilidad_vivienda ✗ | vulnerabilidad_vivienda ✗ | normativa_general ✓ | geopot ✓ |

## Hallazgos

1. **En este dataset, el respaldo contrastivo empeora más de lo que arregla.** Producción (70,7 %) queda por debajo de keyword solo (84,5 %). El contrastivo arregla coloquiales (S3), pero manda preguntas generales y sísmicas a dominios equivocados: 12 a `vulnerabilidad_vivienda`, 8 a `vias`, 4 a `ecuador_nec_se_ds` ("hola, ¿qué puedes hacer?" → Ecuador).
2. **Un umbral absoluto no basta; hace falta un margen.** Con τ = 0,55, Sincelejo (0,557) sigue fallando. Lo que separa los aciertos de los errores es la ventaja sobre `normativa_general`, no el score absoluto.
3. **`vulnerabilidad_vivienda` es un callejón sin salida en el chat.** 0 chunks y sin camino propio: hasta sus preguntas legítimas terminan en abstención. Esto es independiente del enrutador.
4. **Negación (S5):** keyword y producción fallan cuando la pregunta nombra el dominio que **no** quiere ("no necesito el costo…" → apu_precios; "sin hablar de pavimentos…" → vias).
5. **Colisiones de palabras clave:** "tanque … RAS" → geopot; "concreto … aguado" → vias.
6. **Tráfico real insuficiente para validar:** `consultas_history` tiene 54 filas, 3 con método registrado (desde el 27/10). La única decisión del contrastivo es justamente la de Sincelejo.

## Limitaciones (por qué esto todavía no se integra)

- n = 58 en test. Los intervalos son anchos y V2, V3 y V4 quedan apenas bajo 0,05 tras Holm.
- Las etiquetas y la regla sísmica de V4/V5 las escribió la misma persona. La regla nació del caso de origen y las plantillas de S1 comparten su vocabulario, así que **V4/V5 están sesgadas a favor**. Falta un set held-out redactado por otra persona.
- Estratos S4, S5 y S7 tienen 3 o 4 casos en test; no permiten concluir por estrato.

## Recomendación para F5 (decisión de integración, todavía no)

1. El candidato es **V3 (margen δ sobre `normativa_general`)**: es el cambio más pequeño y general, arregla el caso de origen sin una regla ad hoc, y no pierde contra V1 en ningún estrato con n ≥ 5. En test: S1 67 → 94 %, S3 60 → 80 %, S6 20 → 60 %, S2 igual (100 %). Pierde 1 de 3 casos en S4 (sinónimos), donde n es demasiado chico para concluir. V5 se evalúa como mejora adicional con un set held-out de otra persona.
2. Aparte del enrutador: decidir qué hace el chat con `vulnerabilidad_vivienda`. Delegar al endpoint determinista `/vulnerabilidad-vivienda/checklist`, o cargar sus chunks.
3. Antes de integrar: unas 60 preguntas held-out redactadas por una segunda persona, y volver a correr. Integrar solo si V3 mantiene la mejora con un IC que no cruce 0 y sin regresión en `test_rag_motores_regresion.py`.
