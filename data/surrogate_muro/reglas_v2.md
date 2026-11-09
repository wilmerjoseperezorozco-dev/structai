# Reglas empíricas del selector de tipología (muros en voladizo)

Hallazgos del optimizador de referencia sobre el espacio muestreado; ver hipótesis en el docstring.

## Importancia SHAP (media |SHAP| por clase)

| index | estandar | dentellon | bandeja |
|---|---|---|---|
| phi | 2.3752 | 2.4347 | 0.1862 |
| a_max | 2.1288 | 1.991 | 0.0773 |
| beta | 0.9878 | 1.0321 | 0.1083 |
| H_tanphi | 0.588 | 0.5197 | 0.2018 |
| H | 0.3011 | 0.3148 | 0.2719 |
| p_acero | 0.3131 | 0.3139 | 0.0415 |
| q_adm | 0.2936 | 0.3031 | 0.4691 |
| q_s | 0.2996 | 0.2676 | 0.1631 |
| kh | 0.1333 | 0.2539 | 0.007 |
| mult_concreto | 0.1972 | 0.1925 | 0.0298 |
| gamma | 0.175 | 0.1762 | 0.4739 |
| fe_cemento | 0.0719 | 0.0589 | 0.167 |
| fe_acero | 0.0074 | 0.0089 | 0.0 |

## ¿Cuándo supera el dentellón al ensanche de la zapata?

Casos con ambas tipologías factibles: 1651. El dentellón gana en 63.7%; ahorro mediano cuando gana 4.9%.

Árbol (profundidad 3):
```
|--- phi <= 36.46
|   |--- kh <= 0.14
|   |   |--- phi <= 34.23
|   |   |   |--- class: 1
|   |   |--- phi >  34.23
|   |   |   |--- class: 0
|   |--- kh >  0.14
|   |   |--- phi <= 35.86
|   |   |   |--- class: 1
|   |   |--- phi >  35.86
|   |   |   |--- class: 1
|--- phi >  36.46
|   |--- kh <= 0.19
|   |   |--- kh <= 0.16
|   |   |   |--- class: 0
|   |   |--- kh >  0.16
|   |   |   |--- class: 0
|   |--- kh >  0.19
|   |   |--- a_max <= 0.30
|   |   |   |--- class: 1
|   |   |--- a_max >  0.30
|   |   |   |--- class: 1

```

### Mejor corte simple por variable

| variable | umbral | exactitud | sentido |
|---|---|---|---|
| phi | 36.5274 | 0.7371 | x ≤ t → dentellón mejor |
| H_tanphi | 2.5263 | 0.6439 | x > t → dentellón mejor |
| H | 7.2646 | 0.6372 | x ≤ t → dentellón mejor |
| a_max | 0.0599 | 0.6336 | x > t → dentellón mejor |
| q_adm | 103.7924 | 0.6323 | x > t → dentellón mejor |
| beta | 0.7082 | 0.6239 | x > t → dentellón mejor |