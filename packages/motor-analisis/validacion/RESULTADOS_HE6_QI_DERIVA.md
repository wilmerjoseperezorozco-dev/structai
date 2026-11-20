# Resultados HE6 (#274): Qi en pórticos que cumplen la deriva

Prerregistro: `PRERREGISTRO_HE6_QI_DERIVA.md`. Corrida del 2026-11-19, de 07:20 a 07:57, con `he6_qi_deriva.py`. Datos: `he6_resultados.json`.

## Veredicto: **CONFIRMADA** ("raro" en la malla con pesos iguales)

| Método | Cumplen la deriva | Qi_max > 0,10 | Proporción | IC95 de Wilson | Qi_max mediano | Qi_max máximo |
|---|---|---|---|---|---|---|
| **Espectral (principal)** | 500 de 500 | 11 | 2,2 % | [1,2 %; 3,9 %] | 0,038 | 0,127 |
| Fuerza horizontal equivalente (sensibilidad) | 500 de 500 | 6 | 1,2 % | [0,6 %; 2,6 %] | 0,029 | 0,117 |

Todos los edificios encontraron un diseño que cumple antes de llegar al tope de 1,20 m (mediana de 1 paso de crecimiento, máximo 4).

## Dónde no es raro (descriptivo)

Qi > 0,10 aparece **solo** cuando se juntan baja sismicidad y altura:
- **Por Aa (espectral):** 0,10 → 9 de 100; 0,15 → 2 de 100; 0,20 a 0,30 → 0 de 300.
- **Por pisos (espectral):** de 3 a 9 pisos → 0 de 350; 10 → 1 de 50; 11 → 3 de 50; 12 → 7 de 50.
- **Subgrupo Aa = 0,10 y N ≥ 10 (espectral):** 9 de 30, es decir 30 %, con IC95 de Wilson [17 %; 48 %].

  Este subgrupo lo definí **después** de ver los resultados: es exploratorio. Ahí P-Δ **no** es raro.
- **Luces:** solo aparece con L ≤ 6 m; con L = 7–8 m no hay ningún caso.

Esto coincide con la expectativa física declarada en el prerregistro, Qi ≈ θ·P/V. Con poca demanda sísmica, V es pequeño frente a P. Además, la deriva ya no gobierna el diseño: varios de esos edificios usan solo el 62–70 % del límite de deriva, porque las columnas salen del prediseño por carga axial. Por eso cumplir la deriva no garantiza un Qi bajo.

## Qué significa para el motor y para la F3

- **Por fuera de ese rango:** cumplir la deriva del 1 % hace que P-Δ casi nunca obligue (A.6.2.3). En Aa ≥ 0,20 o en edificios de hasta 9 pisos, la malla no tuvo ningún caso.
- **Verificación siempre activa:** el motor ya calcula Qi en cada análisis (F1 y F2). Tiene que **advertir siempre** cuando Qi > 0,10, sobre todo en zonas de amenaza baja o intermedia (Aa ≤ 0,15) con 10 pisos o más.
- **Prioridad de P-Δ:** dentro de la F3 queda **media**. La necesitan los edificios altos en zonas de baja sismicidad, un caso acotado y que el motor puede detectar.

## Limitaciones

- **Representatividad.** La malla tiene pesos iguales y no representa el inventario real. En Colombia, los edificios altos en Aa = 0,10 (por ejemplo, la costa Caribe) son una fracción que esta malla no pondera.
- **Geometría.** Las plantas son cuadradas y simétricas, sin muros ni mampostería, con columnas iguales en altura y el primer diseño que cumple.
- **Cargas.** D = 7,0 y L = 1,8 kN/m² son típicas, no medidas.
