# Validación en suelo granular (SPT del CCP-14) con la CYCU (#118)

- **Prerregistro:** [#118, comentario 6976346539](https://github.com/wilmerjoseperezorozco-dev/structai/issues/118#issuecomment-6976346539).
- **Código:** script `validacion/cycu_arena_2025.py` y motor `src/arena_spt.py`, ambos del commit `80e6ac5`, sin cambios.
- **Datos:** Chen et al. (2025), CYCU pile load test database, doi:10.17632/x6c63j8bv8.1, licencia CC BY 4.0.

## Resultado principal: CALIBRADO en promedio, con dispersión alta

| Grupo | n | Sitios | λ (media geométrica) | IC95 (bootstrap por sitio) | COV | Veredicto |
|---|---|---|---|---|---|---|
| Todas | 81 | 34 | **0,96** | [0,78; 1,17] | 0,63 | CALIBRADO |
| Excavadas, β (L2) | 16 | 7 | 0,90 | [0,68; 1,18] | 0,36 | NO CONCLUYENTE (pocos sitios, como se anticipó) |
| Hincadas, Meyerhof (Davisson) | 65 | 27 | 0,97 | [0,76; 1,22] | 0,66 | CALIBRADO |

- **Exclusiones** (reglas prerregistradas):
  - 163 filas no son granulares;
  - 36 no tienen σ'v y 2 no tienen N;
  - 1 tiene el estrato representativo lejos de la punta;
  - 9 tienen Qm > Qmax;
  - 3 no tienen capacidad interpretada.
- **Cuantiles de λ (todas):** p10 0,47, p50 1,00 y p90 1,82.
- **52 % de las pruebas tiene λ < 1.**
- **Sensibilidad (Terzaghi y Peck, n = 65):** λ = 1,07.
- **Fracción media de punta en el predicho:** 0,31 en excavadas y 0,49 en hincadas.

## Hallazgo post hoc (no prerregistrado)

Con los factores de seguridad de la NSR-10 (fricción 1,50 y punta 3,0), el FS global medio es 1,95. Aun así, **en 11 de las 81 pruebas (14 %) la capacidad medida queda por debajo de la admisible del motor**: 2 de 16 excavadas y 9 de 65 hincadas.

## Lectura

1. Los métodos SPT del CCP-14 no tienen sesgo en promedio sobre esta base, a diferencia de la arcilla (λ = 1,48, conservador).
2. **La dispersión es el problema.** Con COV 0,63 y p10 0,47, el FS de la NSR-10 no alcanza a cubrir la cola baja. Eso es coherente con el CCP-14: es LRFD y usa factores de resistencia bajos para estos métodos, que equivalen a FS globales mayores que 2.
3. **No se puede atribuir la cola baja con estos datos.** Las causas posibles son:
   - la energía del SPT, que no se declara;
   - un N representativo de la punta aplicado a todo el fuste;
   - el criterio de falla.

## Consecuencia para el motor (decisión pendiente; no se recalibra con estos datos)

- En arena con SPT, el motor no debe presentar la capacidad admisible con FS de la NSR-10 sin advertencia.
- Opciones a evaluar:
  - **FS mínimo mayor**, o los φ del CCP-14;
  - **exigir prueba de carga**, como recomienda el CCP-14 para usar factores mayores.
- Cualquier cambio es una versión nueva que debe validarse con datos distintos de estos 81.
