# Resultados: pronóstico del acero corrugado (ICOCIV) — #262

Generado por `pronostico_acero.py` según el prerregistro del #262. Pérdida en log del índice; MASE escalado por el MAE del naive a un paso en la ventana de cada origen. DM: una cola (el modelo mejor que la referencia), HAC Newey-West rezago h−1 y corrección de Harvey.

Orden ARIMA elegido en el ICCP 2000–2021 (M4): (1, 1, 0).

## h = 3 meses (exploratorio, sin corrección)

| Modelo | n | MASE | Cobertura 80 % | Winkler 80 % | DM vs M0 | p (una cola) |
|---|---|---|---|---|---|---|
| M0 Caminata aleatoria | 31 | 1.113 | 94% | 0.1547 | — | — |
| M1 Naive estacional (m=12) | 31 | 2.460 | 81% | 0.2625 | 1.76 | 0.956 |
| M2 Caminata con deriva | 31 | 1.263 | 94% | 0.1647 | 1.58 | 0.937 |
| M3 ARIMA (AICc por origen) | 31 | 1.439 | 100% | 0.1833 | 0.86 | 0.802 |
| M4 ARIMA (orden del ICCP) | 31 | 1.035 | 100% | 0.2088 | -0.69 | 0.248 |
| M5 ARIMAX (TRM, chatarra) | 31 | 1.649 | 87% | 0.1925 | 1.20 | 0.881 |
| M6 Chronos-Bolt base | 31 | 1.411 | 77% | 0.1708 | 1.01 | 0.840 |

## h = 6 meses (principal)

| Modelo | n | MASE | Cobertura 80 % | Winkler 80 % | DM vs M0 | p (una cola) |
|---|---|---|---|---|---|---|
| M0 Caminata aleatoria | 28 | 1.880 | 82% | 0.2164 | — | — |
| M1 Naive estacional (m=12) | 28 | 2.581 | 71% | 0.2541 | 0.65 | 0.739 |
| M2 Caminata con deriva | 28 | 2.308 | 82% | 0.3072 | 1.28 | 0.894 |
| M3 ARIMA (AICc por origen) | 28 | 2.617 | 79% | 0.2946 | 0.77 | 0.775 |
| M4 ARIMA (orden del ICCP) | 28 | 1.770 | 100% | 0.3736 | -0.46 | 0.325 |
| M5 ARIMAX (TRM, chatarra) | 28 | 1.985 | 100% | 0.2912 | 0.22 | 0.585 |
| M6 Chronos-Bolt base | 28 | 2.441 | 75% | 0.3125 | 0.86 | 0.802 |

## h = 12 meses (exploratorio, sin corrección)

| Modelo | n | MASE | Cobertura 80 % | Winkler 80 % | DM vs M0 | p (una cola) |
|---|---|---|---|---|---|---|
| M0 Caminata aleatoria | 22 | 2.839 | 59% | 0.3271 | — | — |
| M1 Naive estacional (m=12) | 22 | 2.839 | 59% | 0.3271 | 0.00 | 0.500 |
| M2 Caminata con deriva | 22 | 3.764 | 45% | 0.8241 | 0.61 | 0.726 |
| M3 ARIMA (AICc por origen) | 22 | 3.082 | 68% | 0.2958 | 0.22 | 0.587 |
| M4 ARIMA (orden del ICCP) | 22 | 2.880 | 100% | 0.6149 | 0.05 | 0.518 |
| M5 ARIMAX (TRM, chatarra) | 22 | 3.067 | 73% | 0.2923 | 0.21 | 0.581 |
| M6 Chronos-Bolt base | 22 | 3.821 | 77% | 0.4979 | 0.30 | 0.618 |

## Hipótesis (h = 6)

- **H1** (Holm sobre M1, M2, M3, M4, M5, M6): M1 no rechaza (p=0.739), M2 no rechaza (p=0.894), M3 no rechaza (p=0.775), M4 no rechaza (p=0.325), M5 no rechaza (p=0.585), M6 no rechaza (p=0.802).
- **H2** M5 vs M3: DM -1.19, p = 0.122.
- **H3** M4 vs M3: DM -0.78, p = 0.220.
- **H4** M6 vs campeón clásico de la primera mitad (M4), en la segunda mitad: DM 2.42, p = 0.985.

## Regla de integración

**Ningún modelo cumple.** Según el prerregistro, StructAI no pronostica: muestra el índice vigente con una banda de volatilidad histórica rotulada como tal.

Intervalos de M0–M2: pronóstico + cuantiles 10/90 de sus errores a h pasos en la ventana (detalle de implementación declarado en el script).

Fuente: DANE, www.dane.gov.co · U.S. Bureau of Labor Statistics · Banco de la República (datos.gov.co).
