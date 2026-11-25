# Resultados #323: sensibilidad del factor de ráfaga Gf al amortiguamiento y al periodo

- **Prerregistro:** [`PRERREGISTRO_323_SENSIBILIDAD_GF.md`](PRERREGISTRO_323_SENSIBILIDAD_GF.md), publicado en #323 antes de correr.
- **Corrida:** 1.088 diseños (272 × 4 brazos), 0 errores, 8,6 min.
- **Población:** 245 de los 272 edificios tienen ráfaga flexible en b02.

## Veredictos

| Id | Resultado | Predicción | Veredicto |
|---|---|---|---|
| S0 | b02 reproduce #322: 272/272 | 272/272 | **se cumple** |
| S1 b01 (β 0,01) | mediana de la razón de ρ: **1,049**, IC95 [1,047; 1,052]; máximo 1,09 | [1,02; 1,08] | **se cumple** |
| S1 b05 (β 0,05) | **0,968**, IC95 [0,966; 0,969]; mínimo 0,93 | [0,95; 0,99] | **se cumple** |
| S1 cuta (Cu·Ta) | **0,992**, IC95 [0,991; 0,994]; rango [0,92; 1,03]; 25 edificios pasan a ráfaga rígida | [0,90; 0,99] | **NO se cumple**: el efecto es menor de lo previsto |
| **S2** b01 | **29/272 (10,7 %)** cambian refuerzo, IC95 [7,5; 14,9 %]; los que no cumplen pasan de 11 a 14 | entre 1 y 15 | **NO se cumple**: más sensible de lo previsto |
| **S2** b05 | **20/272 (7,4 %)**, IC95 [4,8; 11,1 %]; los que no cumplen pasan de 11 a 10 | ≤ 15 | **NO se cumple** |
| S2 cuta | 14/272 (5,1 %); los que no cumplen siguen en 11 | ≤ 20 | **se cumple** |

## Lectura

1. **Mi anclaje acertó en cuánto se mueve la fuerza (S1), pero no en cuánto se mueve el diseño (S2).**
   - Un cambio de apenas +5 % en W cambia el refuerzo del 11 % de los edificios: más del que produjeron los casos 2–4 (3,7 %, #322).
   - **El refuerzo es discreto:** muchos diseños gobernados por viento están justo en el umbral de una barra o de un espaciamiento, y un 3–5 % basta para saltar.
   - Es la misma razón por la que β = 0,05 (−3 %) también cambia 20 edificios: en la dirección opuesta, pero cambia.
2. **Regla D1 aplicada:** b01 cambia 29 edificios, que es ≥ 14. Por eso la memoria ahora **advierte**, en todo edificio con ráfaga flexible, que el diseño es sensible a β, con los números medidos. Pide justificar β para el sistema del proyecto. **β = 0,02 sigue por defecto como HIPÓTESIS**: el prerregistro prohibía cambiarlo con este resultado.
3. **Periodo (D2):** usar Cu·Ta en lugar del T del modelo cambia poco la fuerza (−0,8 % en mediana), menos de lo que anticipé. Mi caso sintético suponía una diferencia de T mayor que la real. Aun así, cambia el refuerzo de 14 edificios. El diseño sigue usando el T del modelo.
4. **La lección general** vale más allá de Gf: **cualquier entrada incierta que mueva W un 3–5 % cambia el armado de ~1 de cada 10 edificios gobernados por viento.** Por eso las HIPÓTESIS sobre viento no son detalles: deben declararse con su sensibilidad.

## Limitaciones

- Solo W36D (36 m/s, exposición D), el escenario más severo. Con W28C el viento casi no gobierna (#242), así que la sensibilidad debería ser menor; no se midió.
- No hay validación externa de Gf. Sigue como "verificado a mano" hasta conseguir un ejemplo oficial y gratuito (#323, parte 2).
- La comparación es entre diseños del mismo motor: mide la estabilidad del diseño, no su acierto frente a la realidad.
