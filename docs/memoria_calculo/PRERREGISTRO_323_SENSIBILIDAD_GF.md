# Prerregistro #323: sensibilidad del factor de ráfaga Gf al amortiguamiento y al periodo

Fijado el 2026-11-25, **antes** de correr la población. Solo se corrió un piloto de 2 edificios para revisar que el script funcione.

- **Script:** `scripts/memorias_sinteticas/viento_323.py`.
- **Código:** opción `VientoB6.periodo_gf` (`"modelo"` o `"cu_ta"`), solo para medir. El diseño sigue usando el modelo.

## Pregunta

Gf (B.6.5.8.2) depende de dos entradas que la NSR-10 no fija:
- β, que hoy es 0,02 (HIPÓTESIS);
- n1, que hoy es 1/T del modelo con inercias fisuradas.

¿Cuánto cambian ρ = 1,6W/E y el refuerzo si esas entradas cambian dentro de un rango razonable?

## Población y brazos

- **Población:** la de #242 y #322, 272 pórticos de zona baja que no son edificios bajos.
- **Viento:** W36D (36 m/s, exposición D), con los casos 1–4.

| Brazo | β | Periodo para n1 |
|---|---|---|
| **b02** (referencia = diseño actual) | 0,02 | modelo |
| b01 | 0,01 | modelo |
| b05 | 0,05 | modelo |
| cuta | 0,02 | Cu·Ta (A.4.2.1) |

## Anclaje (cálculo previo sobre edificios sintéticos, no de la población)

Con planta de 20 × 20 m, exposición D y 36 m/s, `factor_rafaga` da:

| h | T modelo | G con β 0,01 / 0,02 / 0,05 | Con Cu·Ta |
|---|---|---|---|
| 24 m | 1,0 s | 0,883 (rígida en los tres) | 0,883 |
| 36 m | 1,4 s | 0,956 / 0,920 / 0,897 | 0,880 (pasa a rígida) |
| 54 m | 2,0 s | 0,989 / 0,937 / 0,902 | 0,906 |

Lectura: frente a β = 0,02, β = 0,01 sube G entre 4 y 6 %, y β = 0,05 lo baja entre 2 y 4 %. Cu·Ta es más corto que el T del modelo (en #274 era así en el 97 %), así que lo baja entre 3 y 4 %, o vuelve rígida la ráfaga. Como ρ escala con G, ρ cambia en la misma proporción.

## Predicciones

En cada brazo, la razón es max(ρx, ρy) del brazo sobre la de b02, por edificio. IC95 con bootstrap (2.000 remuestreos, semilla 3230).

| Id | Métrica | Predicción |
|---|---|---|
| **S0** (control) | b02 reproduce la firma de W36D_c14 de #322 | 272/272 |
| **S1** | Mediana de la razón de ρ | b01 en [1,02; 1,08]; b05 en [0,95; 0,99]; cuta en [0,90; 0,99] |
| **S2** (primaria) | Edificios cuyo refuerzo cambia frente a b02 | b01: entre 1 y 15; b05: ≤ 15; cuta: ≤ 20 |

## Reglas de decisión (fijas)

- **D1, β:**
  - si b01 cambia el refuerzo en 14 o más edificios (> 5 %), la memoria agrega una advertencia: el diseño es sensible a β, con el número medido;
  - si son 13 o menos, la memoria declara que la sensibilidad a β medida es pequeña.
  - En ambos casos β = 0,02 sigue siendo HIPÓTESIS. **No se cambia el valor por defecto con este resultado**, porque escogerlo es un juicio de ingeniería, no una medición.
- **D2, periodo:** el diseño sigue usando el T del modelo, porque representa la rigidez real. Cu·Ta es un tope pensado para que el sismo sea conservador; al ser más corto, para viento no lo es. El brazo cuta solo cuantifica esa diferencia.
- Los criterios no cambian después de ver los resultados.

## Fuera de alcance (#323, parte 2)

Validar Gf contra un ejemplo resuelto oficial y gratuito. Mientras no lo haya, Gf sigue como "verificado a mano".
