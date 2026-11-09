# Reglas empíricas del selector de tipología (muros en voladizo)

Hallazgos del optimizador de referencia sobre el espacio muestreado; ver hipótesis en el docstring.

## Importancia SHAP (media |SHAP| por clase)

| index | estandar | dentellon | bandeja |
|---|---|---|---|
| phi | 3.3665 | 3.6244 | 0.2702 |
| a_max | 2.3446 | 2.5184 | 0.1083 |
| beta | 0.9425 | 0.9559 | 0.2002 |
| H_tanphi | 0.6928 | 0.5274 | 0.0455 |
| q_adm | 0.3261 | 0.3465 | 0.5464 |
| q_s | 0.3527 | 0.3052 | 0.2157 |
| kh | 0.1345 | 0.2959 | 0.0252 |
| H | 0.2865 | 0.2715 | 0.4355 |
| gamma | 0.1783 | 0.2575 | 0.16 |
| p_acero | 0.159 | 0.168 | 0.0847 |
| mult_concreto | 0.1753 | 0.1415 | 0.3294 |
| fe_cemento | 0.0328 | 0.0342 | 0.0544 |
| fe_acero | 0.0051 | 0.0031 | 0.003 |

## ¿Cuándo supera el dentellón al ensanche de la zapata?

Casos con ambas tipologías factibles: 1650. El dentellón gana en 65.8%; ahorro mediano cuando gana 18.3%.

Árbol (profundidad 3):
```
|--- phi <= 35.79
|   |--- phi <= 34.07
|   |   |--- phi <= 31.86
|   |   |   |--- class: 1
|   |   |--- phi >  31.86
|   |   |   |--- class: 1
|   |--- phi >  34.07
|   |   |--- a_max <= 0.19
|   |   |   |--- class: 1
|   |   |--- a_max >  0.19
|   |   |   |--- class: 1
|--- phi >  35.79
|   |--- kh <= 0.20
|   |   |--- phi <= 37.27
|   |   |   |--- class: 0
|   |   |--- phi >  37.27
|   |   |   |--- class: 0
|   |--- kh >  0.20
|   |   |--- phi <= 38.94
|   |   |   |--- class: 1
|   |   |--- phi >  38.94
|   |   |   |--- class: 1

```

### Mejor corte simple por variable

| variable | umbral | exactitud | sentido |
|---|---|---|---|
| phi | 36.5258 | 0.7958 | x ≤ t → dentellón mejor |
| H | 6.9744 | 0.6685 | x ≤ t → dentellón mejor |
| H_tanphi | 2.5902 | 0.6685 | x > t → dentellón mejor |
| q_adm | 103.7911 | 0.6448 | x > t → dentellón mejor |
| a_max | 0.0599 | 0.6412 | x > t → dentellón mejor |
| beta | 0.7082 | 0.64 | x > t → dentellón mejor |