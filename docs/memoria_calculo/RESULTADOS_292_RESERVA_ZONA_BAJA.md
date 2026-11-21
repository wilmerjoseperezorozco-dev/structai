# Resultados #292: margen de utilización u_máx = 0,90 bajo gravedad en zona baja

Corrida única según [`PRERREGISTRO_292_RESERVA_ZONA_BAJA.md`](PRERREGISTRO_292_RESERVA_ZONA_BAJA.md), 2026-11-20.

- **Edificios:** 358 pares (control y tratamiento) de zona baja.
- **Tiempo:** 1.078 s.
- **Datos:** [`brazos.csv`](../../data/memorias_sinteticas/f3b_292/brazos.csv) y [`resultados_292.json`](../../data/memorias_sinteticas/f3b_292/resultados_292.json).
- **Puerta Q2:** 0,44 % de elementos imprecisos. Cumple.

## Veredicto según la regla fijada: **NO ADOPTAR** como valor por defecto

| | Criterio | Resultado | |
|---|---|---|---|
| **H-292a**: Δ percentil 10 de β (central) | ≥ 0,3 con IC > 0 | **+0,27**, IC [0,10; 0,39] | ✘ (queda corto; el IC excluye 0) |
| **H-292b**: Δ fracción con β < 3,8 (alta) | ≥ 0,10 | +0,009, IC [0; 0,02] | ✘ |
| **C-292**: sobrecosto | mediana ≤ 3 % y p90 ≤ 6 % | mediana **0 %**, p90 0,5 %, máx. 3,3 % | ✔ |
| Diseños que dejan de cumplir | 0 | **15 de 358** | ✘ |

## Lo que explica el resultado (descriptivo, posterior)

1. **El margen actúa casi solo donde importa:**
   - El refuerzo cambia en **13 %** de los edificios; en el resto, la cuantía mínima, el sismo o el redondeo a barras enteras ya cubrían el 10 %.
   - **En los 36 edificios más débiles** (β < 3,8 en el control) **cambia en 33**. Donde cambia, Δβ tiene mediana **+0,62** (p10 +0,20, p90 +2,11).
   - Por eso el sobrecosto es casi nulo. Como estadístico de población, el percentil 10 diluye un efecto que está concentrado.
2. **Los 15 que dejan de cumplir son edificios altos** (N de 8 a 12), no pequeños.
   - Todos fallan en las **columnas del piso 1**: con la sección F1 fija, la gravedad dividida por 0,9 no cabe en flexo-compresión.
   - El margen sobre las columnas de los edificios altos es lo que rompe la regla. **En las edificaciones pequeñas (N ≤ 5) ningún diseño falla.**
3. **H-292b no se mueve** (70 % → 69 %). En la variante desfavorable, θS (V = 0,15) domina tanto que un 10 % más de resistencia en pocos edificios no cambia la fracción. Es otra señal de que **medir θS** (vibración ambiental, #276 P1) vale más que sumar resistencia.

## Siguiente paso propuesto (requiere un prerregistro nuevo; no es retroactivo)

Un margen **focalizado**, con la regla de decisión ajustada a lo que se quiere proteger:
- **Variante A:** margen solo en las combinaciones de gravedad de las **vigas**, sin columnas.
- **Variante B:** margen en vigas y columnas, solo con **N ≤ 7** en zona baja.
- **Métrica primaria:** el β de los edificios con β_control < 3,8, más el sobrecosto y los diseños que dejan de cumplir.

**Sesgo declarado:** esas variantes y esa métrica se eligen **después** de ver este resultado, sobre el mismo corpus.

## Limitaciones
- Las secciones F1 están fijas, sin reoptimizar.
- El modelo de β no incluye la carga viva alternada.
- El corpus es sintético y el β es del elemento.
- El margen es un criterio de StructAI, no de la NSR-10. Nada aprueba un diseño sin la F4 y la firma de un ingeniero (#18).
