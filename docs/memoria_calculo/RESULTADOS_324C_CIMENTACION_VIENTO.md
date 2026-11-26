# Resultados #324-C: cimentación de los edificios que se redimensionan por viento

- **Prerregistro:** [`PRERREGISTRO_324C_CIMENTACION_VIENTO.md`](PRERREGISTRO_324C_CIMENTACION_VIENTO.md), publicado en #324 antes de correr.
- **Corrida:** 22 diseños × 3 estratos de q_adm, 0 errores, 0 zapatas sin solución, 28 s.

## Veredictos (estrato primario q_adm = 200 kPa; los otros como sensibilidad)

| Id | Resultado | Predicción de Wilmer | Contrapredicción de Claude | Veredicto |
|---|---|---|---|---|
| **H1** | Δpp con mediana **+0,24** (rango −0,8 a +2,4). Con 100 kPa: +0,03. Con 400 kPa: +0,61 (máx. +5,2) | +3 a +7 pp | ≤ +1 pp | Wilmer: **refutada**. Claude: **se cumple** |
| **H2** | **0/11** gobernados por excentricidad o levantamiento, en los tres estratos. Ninguna combinación de servicio da tracción neta. El máximo es 44 % de las zapatas de un edificio con 400 kPa | ≥ 7/11 | ≤ 3/11 | Wilmer: **refutada**. Claude: **se cumple** |
| **H3** | Luz máxima: viga 6,5 m frente a columna 5,75 m (**mayor**). H/B_mín: 3,05 frente a 3,86 (**menor**) | mayor en las dos | — | **refutada a medias**: luces sí, esbeltez no. n = 3, exploratoria |
| H3, mecanismo | Uso de la deriva sísmica en los 3 de viga: 0,29–0,41, lejos de 1. Con viento la deriva **baja** en 10 de 11 | "rigidizar controla la deriva" | — | **mecanismo refutado**: la viga peraltada alivia el momento de la columna (resistencia), no la deriva |
| H4 | En 8 edificios con ΔV_inf > 0, la mediana de compensación es **−16 %**. Es **bimodal**: en 4 la mitad superior también crece (−67 a −78 %) y en 4 se adelgaza (36 %, 42 %, 42 % y 135 %) | 15–30 % | — | **refutada**: ningún edificio cae en el rango |

## Lo que salió y nadie predijo

1. **El suelo decide más que el viento.**

   | Estrato | Cimentación / superestructura | Edificios donde alguna zapata aislada no cabe |
   |---|---|---|
   | 100 kPa | 38 % | **11/11** (135 zapatas) |
   | 200 kPa | 16 % | 5/11 |
   | 400 kPa | 8 % | 0/11 |

   Con 100 kPa, los edificios de 9–12 pisos **no admiten zapatas aisladas**: piden losa o pilotes. Eso cambia el costo mucho más que el viento.
2. **La cimentación sí se encarece más que la superestructura en suelo firme:** +16 % con 400 kPa, frente a +8,6 %. Pero pesa poco en el total (8 %), así que el sobrecosto global apenas sube. En suelo blando la zapata la define la carga de gravedad, no el viento, y su sobrecosto es igual al de la superestructura (+8,5 %).
3. **El momento de vuelco del viento no domina** en pórticos de 9–12 pisos. Cada columna lleva mucha carga axial (de 1.500 a 5.000 kN en servicio), así que la excentricidad M/P queda dentro del núcleo central. Ni siquiera con 0,6D+W se levanta una zapata.
4. **H4 es bimodal porque el optimizador escoge entre dos estrategias:**
   - "columna grande abajo, delgada arriba" (Δ = 150): 414, 554, 910 y 1701. En el 910, la reducción de arriba supera lo agregado abajo y el volumen neto **baja**.
   - "todo un tamaño más": 898, 1106, 1278 y 1413.

## Consecuencias

- Para estos edificios, **el momento de vuelco del viento no justifica pilotes ni anclajes**. Lo que obliga a otra solución es **q_adm**. El ingeniero necesita el estudio de suelos antes de comparar sistemas.
- **Abrir un issue** (#119 o uno nuevo): losa de cimentación y pilotes para q_adm ≤ 100 kPa. Hoy el motor solo marca "no cabe".
- El mecanismo correcto para la viga peraltada es la **redistribución del momento en el nudo**. La memoria no debe decir que es por deriva.

## Limitaciones

- Zapata aislada cuadrada.
- Sin despegue en servicio, un criterio estricto que favorecía a H2 y aun así dio 0/11.
- Sin pedestal, sin Ω0 y sin excavación.
- Las zapatas que no caben se cuentan como aisladas: el costo con 100 kPa es una aproximación.
- q_adm por estrato declarado, no por sitio.
- 11 edificios y un solo escenario de viento (W36D).
- **No diseña cimentaciones reales.**
