# Prerregistro HE6 (#274): índice de estabilidad Qi en pórticos que cumplen la deriva

Fijado el 2026-11-19, **antes** de calcular Qi en la malla. Código: `he6_qi_deriva.py`.

## Pregunta

Si un pórtico de concreto cumple la deriva del 1 % de la NSR-10 (A.6.4), ¿es raro que el índice de estabilidad supere Qi = 0,10? Por encima de ese valor, A.6.2.3 obliga a incluir los efectos P-Δ.

## Por qué importa

Si es raro, `/sitio` y el motor 3D pueden tratar P-Δ como una verificación que casi nunca gobierna, y la F3 deja de ser urgente. Si no es raro, la F3 (P-Δ) tiene prioridad.

Una expectativa física, que **no** es el criterio: Qi ≈ θ·P/V. Con θ ≤ 0,0143 (el 1 %/0,7) y V/P ≈ Sa, en zonas de baja sismicidad (Sa pequeña) Qi podría superar 0,10.

## Edificios (malla paramétrica, no una muestra del inventario real)

**Malla:** 500 edificios.
- Pisos: N de 3 a 12, de 3 m cada uno.
- Luces: L ∈ {4, 5, 6, 7, 8} m, en planta cuadrada de 3×3 vanos.
- Sitio: Aa = Av ∈ {0,10; 0,15; 0,20; 0,25; 0,30}, perfil C o D.
- Grupo de uso I (I = 1).

**Materiales y cargas:**
- Concreto f'c = 28 MPa, Ec = 4700√f'c (C.8.5.1), G = Ec/2,4.
- Inercias fisuradas (C.10.10.4.1): columnas 0,70·Ig y vigas 0,35·Ig. Por eso la deriva se multiplica por 0,7 (A.6.4.1.1).
- Masa sísmica D = 7,0 kN/m² (losa, acabados, muros y pórtico). Carga para Pi: D + L, con L = 1,8 kN/m² (A.6.0).

**Prediseño:**
- Vigas: h0 = máx(L/12; 0,30) y b = máx(0,25; h/2), redondeadas a 0,05.
- Columnas cuadradas iguales en todo el edificio. La inicial c0 sale de la carga axial de la columna interior: √(Pu/(0,40·f'c)), con Pu = N·(1,2D + 1,6L)·L² y mínimo 0,30 m.
- Si no cumple la deriva, en cada paso crecen a la vez la columna y la altura de viga 0,05 m, hasta un tope de 1,20 m cada una.
- Se toma el **primer** diseño que cumple. Los que no cumplen con los topes se reportan aparte.

**Análisis:**
- **Principal:** espectral (A.5), con T = mín(T del modelo, Cu·Ta), Vs con ese T y ajuste A.5.4.5 al 80 % (edificios regulares y simétricos). Incluye torsión accidental corriendo el centro de masa ±5 %, y la deriva se mide en el centro de masa (A.6.3.1.1).
- **Sensibilidad:** fuerza horizontal equivalente (A.4) con el mismo T, distribución A.4.3 y torsión accidental (F1).
- Qi = Pi·Δcm/(Vi·hpi) (A.6.2-2), con Δ y V del análisis, sin el factor 0,7.

**Nota de transparencia:** durante la preparación revisé si un edificio (12 pisos, 8 m, Aa 0,25, perfil D) podía cumplir la deriva solo agrandando columnas. No pudo, porque gobiernan las vigas, y por eso el prediseño hace crecer las dos. No calculé ni miré Qi en ningún edificio.

## Medida y criterio

Proporción de edificios que cumplen la deriva y tienen Qi_max > 0,10, con IC95 de Wilson.

| Veredicto | Condición |
|---|---|
| **CONFIRMADA** ("raro") | límite superior < 0,10 |
| **REFUTADA** | límite inferior > 0,10 |
| **NO CONCLUYENTE** | en otro caso |

**Descriptivo:** resultados por Aa y por número de pisos, mediana de Qi_max y cantidad de edificios sin diseño.

## Limitaciones declaradas

- La malla no representa la distribución real de edificios en Colombia: la proporción es sobre la malla, con pesos iguales.
- Plantas cuadradas, simétricas y regulares, sin muros ni mampostería, con columnas iguales en altura.
- Se usa el primer diseño que cumple, no un diseño óptimo.
- Las cargas son típicas, no medidas.
