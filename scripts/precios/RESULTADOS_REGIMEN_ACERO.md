# Resultados: régimen del precio del acero (cadenas de Markov)

Evento: el acero corrugado (ICOCIV) sube ≥ 2 % en los próximos 3 meses. 31 orígenes; frecuencia observada del evento en ellos: 19%.

Transición estimada en el ICCP 2000–2021 (estado 0 = media más baja): permanencia 0.471 y 0.975; duración media 1.9 y 40.6 meses.

| Modelo | Brier | BSS vs B0 | Log-score | DM vs B0 | p (una cola) | Holm |
|---|---|---|---|---|---|---|
| B0 Climatología | 0.1805 | +0.000 | 0.552 | — | — | — |
| B1 Cadena de Markov observada | 0.1698 | +0.059 | 0.528 | -1.08 | 0.145 | no rechaza |
| R1 HMM 2 estados (ICOCIV) | 0.1637 | +0.093 | 0.520 | -0.60 | 0.275 | no rechaza |
| R2 HMM con transición del ICCP | 0.1708 | +0.054 | 0.533 | -0.33 | 0.372 | no rechaza |

## Calibración

- **B0**: 0.2–0.4 → n=31, p̄=0.30, obs=0.19
- **B1**: 0.0–0.2 → n=3, p̄=0.16, obs=0.33; 0.2–0.4 → n=27, p̄=0.28, obs=0.19; 0.4–0.6 → n=1, p̄=0.42, obs=0.00
- **R1**: 0.0–0.2 → n=26, p̄=0.16, obs=0.23; 0.2–0.4 → n=5, p̄=0.21, obs=0.00
- **R2**: 0.0–0.2 → n=29, p̄=0.16, obs=0.21; 0.2–0.4 → n=1, p̄=0.21, obs=0.00; 0.4–0.6 → n=1, p̄=0.54, obs=0.00

## Regla de integración

**Ningún modelo cumple.** StructAI no muestra un semáforo de régimen del acero.

Fuente: DANE, www.dane.gov.co.
