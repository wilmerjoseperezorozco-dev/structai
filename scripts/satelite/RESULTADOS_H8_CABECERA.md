# Resultados H8 (#273): alarma de relieve calculada en el lote, a 0,01° o en la cabecera (2026-11-18)

- **Protocolo:** `PROTOCOLO_ANALISIS.md` §33, publicado en #273 antes de correr el análisis.
- **Código:** `h8_cabecera_vs_lote.py`.
- **Salida:** `h8_cabecera_resultados.json`.
- **Regla:** la misma de H2 y H2b, S(1 km) ≤ 6,5 m.

## Llanura (Meta, Guaviare, Inírida, Casanare): 932 puntos, 8 municipios, 51 bloques, prevalencia de nivel ≤ 2 m de 0,59

| Ubicación de S | AUC | IC95 % | Sensibilidad | Especificidad | VPP | Fracción con alarma |
|---|---|---|---|---|---|---|
| Lote (referencia) | 0,77 | [0,70; 0,83] | 0,75 | 0,66 | 0,77 | 0,58 |
| Redondeo a 0,01° | 0,74 | [0,67; 0,81] | 0,80 | 0,61 | 0,75 | 0,64 |
| Cabecera DIVIPOLA | **0,42** | [0,29; 0,56] | **0,05** | 0,87 | 0,36 | 0,08 |

- **C1, redondeo:** ΔAUC = +0,03 [−0,01; +0,07] → **NO CONCLUYENTE**. La pérdida es pequeña, pero el IC llega hasta 0,07 y no alcanza la equivalencia preregistrada (< 0,05).
- **C2, cabecera:** ΔAUC = +0,35 [+0,21; +0,49] → **NO BASTA**.
  - La cabecera no solo pierde la señal: queda **por debajo del azar** (0,42).
  - La alarma se activa en el 8 % de los puntos, frente al 58 % en el lote. Así detecta 1 de cada 20 niveles someros.
  - Pasa también en los puntos a ≤ 5 km de la cabecera (AUC 0,43 contra 0,75 en el lote).

**Por qué.** Las cabeceras de la Orinoquía se fundaron sobre terrazas y bancos altos, lejos de las vegas que se inundan. Su relieve local es justamente lo contrario del de los pozos someros del mismo municipio. El relieve de la cabecera describe al pueblo, no al lote.

## Quindío (descriptivo, como se fijó): 258 puntos, 9 municipios, prevalencia de nivel ≤ 5 m de 0,14

- La alarma casi no se activa en ninguna ubicación (≤ 2 %).
- AUC en el lote: 0,52; a 0,01°: 0,47; en la cabecera: 0,40.
- C1 da PIERDE (ΔAUC +0,05 [+0,03; +0,09]), pero sobre una regla que ya no discriminaba en el lote. No se interpreta.

## Lectura (fijada de antemano)

- **C2 NO BASTA:** con solo el municipio, `/sitio` **no debe mostrar la alarma de nivel freático**. Sería peor que no decir nada, porque su silencio se leería como "nivel profundo".
- **Redondeo a 0,01°:**
  - la pérdida es de unos 0,03 de AUC, con la sensibilidad casi igual (0,80 contra 0,75);
  - no se pudo demostrar la equivalencia, así que el redondeo se declara como **pérdida pequeña aceptada a cambio de la privacidad**, no como "sin pérdida".
  - Si el usuario autoriza (opt-in) la ubicación del lote, el cálculo puede hacerse en el momento con la coordenada exacta y guardar solo la redondeada. Esto queda como propuesta de diseño, sujeta a revisión de privacidad.
- **Para `/sitio`:** la alarma de relieve requiere el punto del lote (opt-in) y solo aplica en llanura. Si solo hay municipio, se dice "sin dato de lote: mida el nivel freático".

## Limitaciones

- La llanura tiene solo 8 municipios, y la S de la cabecera es constante en cada uno, así que el tamaño efectivo para C2 es muy pequeño. Aun así, el efecto es grande y el IC está lejos del umbral.
- Los bloques de 0,1° no coinciden con los municipios.
- La coordenada DIVIPOLA es un punto del casco urbano, no necesariamente su parte más alta ni más baja.
- 15 puntos se perdieron por el borde de tesela al redondear (declarado en el conteo).
