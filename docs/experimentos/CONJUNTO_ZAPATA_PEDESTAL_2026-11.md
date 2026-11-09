# Optimizador conjunto zapata + pedestal con DXF (2026-11-08)

Código: `packages/motor-concreto/src/{pedestal,diseno_zapata_pedestal,economia_concreto,encofrado_dxf}.py`. Experimento: `scripts/experimentos/conjunto_zapata_pedestal.py` → `conjunto_zapata_pedestal_2026-11.json`. DXF de ejemplo: `ejemplos/conjunto_costa_C2_S1_con_ensayo_co2.dxf`.

`optimizar_conjunto(c, cargas, suelo, exposicion=..., objetivo="costo"|"co2"|"mixto", ruta_dxf=...)` minimiza sobre geometría troncopiramidal, f'c ∈ {21, 28, 35} y ceniza ∈ {0, 10, 20, 25 %}, con la durabilidad C.4 como filtro, y escribe el DXF del óptimo.
El pedestal llega al nivel de desplante: **h_p = Df − h_c**, así que una zapata más gruesa acorta el pedestal (el trade-off entra al objetivo). Costo y CO₂ suman zapata + pedestal (concreto, acero y encofrado).

## Verificación del pedestal (numerales leídos del corpus 2026-11-08)
C.10.9.1 (1–4 % de Ag), C.10-2 (φPn,max con 0,75 y φ = 0,65), C.10.14.1 (aplastamiento, sin el factor √(A2/A1)), C.10-6 y C.10.10.1.2 (k·ℓu/r ≤ 22, r = 0,3c), C.7.6.3 (separación libre), C.12.3.2 (longitud de desarrollo del pasador en compresión, debe caber en la zapata), C.7.10.5 (estribo No. 3, separación ≤ min(16 db, 48 d_est, c)).
**No verifica:** momento ni cortante en la base (C.15.8.1.4, fricción por cortante), gancho del pasador, pedestal de concreto simple (C.22.8), ni el peso del pedestal en la presión sobre el suelo.

## Resultado (15 casos P_serv × q_adm; 3 exposiciones)
Los 45 casos tienen solución con pedestal que cumple. Mediana del diseño de mínimo CO₂ frente al de mínimo costo:

| Exposición | CO₂ | Costo |
|---|---|---|
| Interior C1/S0 | −6,5 % | +0,5 % |
| Costa C2+S1, sin ensayo (ceniza 0) | 0 % | 0 % |
| Costa C2+S1, con ensayo (ceniza ≤ 25 %) | −10,1 % | +0,9 % |

Lectura: con el pedestal incluido, **bajar CO₂ cuesta casi nada** (≤ 1 % de sobrecosto): las dos soluciones difieren casi solo en la ceniza. En interior el costo-óptimo usa 21 MPa con 10 % de ceniza o 28 MPa sin ceniza (según carga). En costa f'c = 35 siempre, y sin ensayo de sulfatos no hay palanca de mezcla.

## Límites
Heredados de la re-optimización (modelo de mezcla, precio de ceniza, geometría troncopiramidal no tratada por la NSR-10, recubrimiento C2 sin valor en C.7.7.6) más los del pedestal de arriba. El DXF es un croquis de paneles, no un plano.
