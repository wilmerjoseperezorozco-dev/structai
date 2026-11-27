# Resultados #333 (H5 y H6): costo real de la transición de cimentación

- **Prerregistro:** [`PRERREGISTRO_333_H5_H6.md`](PRERREGISTRO_333_H5_H6.md), publicado en #333 antes de correr.
- **Corrida:** 22 diseños, 0 errores, 100 s.

## Veredictos

| Id | Resultado | Predicción de Wilmer | Contrapredicción de Claude | Veredicto |
|---|---|---|---|---|
| **H5** | Con 200 kPa, la zapata **rectangular** resuelve los **5 de 5** que no cabían; la losa no hizo falta. C_cim / C_super tiene mediana de **18,6 %** (rango 15,5–23,7 %), frente a 16,8 % con la aproximación de zapatas cuadradas de #324-C en los mismos 5. Sin viento: 17,5 % | 25–35 % | < 25 % | Wilmer: **refutada**. Claude: **se cumple** |
| **H6** | Con 100 kPa, la losa rígida **no es factible en 0 de 11** edificios, ni sin viento ni con W36D: q_máx > q_adm con todos los voladizos. La transición más barata sin pilotes no existe en ninguno de los 11 | Δ < +0,5 pp | losa no factible en ≥ 8/11 | Wilmer: **inconclusa**, no hay losa que medir. Claude: **se cumple** (11/11) |

## Por qué ninguna losa sirve con 100 kPa (descriptivo, post hoc)

Presión bruta de D+L bajo la losa más grande que se probó (1 m de voladizo):

| Edificio (N) | Solo el edificio, ΣP/A | Con losa de 300 mm y relleno |
|---|---|---|
| 910 (9) | 73,9 kPa | 101,5 kPa |
| 1729 (10) | 76,5 | 104,1 |
| 1106 (10) | 79,7 | 107,3 |
| 554 (12) | 84,9 | 112,5 |
| 414 (10) | 85,5 | 113,1 |
| 1762 (11) | 88,0 | 115,6 |
| 1290 (12) | 92,0 | 119,6 |
| 1701 (11) | 98,8 | 126,4 |
| 898 (11) | 103,9 | 131,5 |
| 1278 (10) | 107,6 | 135,2 |
| 1413 (12) | 117,0 | 144,6 |

- **Un edificio de pórticos de 9–12 pisos pesa 74–117 kPa sobre toda su huella.** Con la losa y el relleno sobre ella (desplante de 1,5 m), ninguno baja de 100 kPa.
- En 3 edificios (898, 1278 y 1413) el edificio solo ya supera los 100 kPa. Ninguna losa superficial con q_adm bruta los sostiene.
- **Con 100 kPa, la única salida que queda es la cimentación profunda (pilotes) o una losa compensada con sótano**, si el estudio de suelos da un q_adm neto a mayor profundidad. Ninguna de las dos está modelada.
- **Esto corrige #324-C:** la fila de 100 kPa (cimentación = 38 % de la superestructura) cobraba zapatas aisladas que no caben. **No es un costo de una solución real.** Es una cota inferior de algo que no se puede construir así.

## Lo que salió y nadie predijo

1. **En suelo medio, la transición cuesta poco.** La rectangular agrega +1,9 pp a la razón cimentación / superestructura (18,6 % frente a 16,8 %). La "frontera de viabilidad" que proponía H5 no aparece con 200 kPa.
2. **El viento casi no mueve la transición:**
   - con W36D la razón es 18,6 %, y sin viento 17,5 %;
   - los mismos 5 edificios no caben en los dos diseños;
   - los dos se resuelven con rectangulares.
3. **La frontera real está en el suelo blando, y es binaria:** con 200 kPa todo se resuelve en superficie; con 100 kPa nada.

## Consecuencias

- **H6 necesita pilotes o una losa compensada para tener respuesta.** Eso pide un perfil de suelo declarado, sea un SPT por estrato para `motor-pilotes` o un q_adm neto con la profundidad. Se propone como v2 de #333, con prerregistro propio.
- **La memoria del motor de cimentación** debe decir que, con q_adm ≈ 100 kPa y 9 pisos o más, la cimentación superficial no es viable en estos pórticos.
- **#324-C:** se añade una nota a la fila de 100 kPa: el costo no corresponde a una solución construible.

## Limitaciones

- La losa es rígida, sin interacción suelo-estructura. Los momentos se calculan con coeficiente, así que el acero es una cota superior. No se modela C.11.11.7.
- q_adm bruta y desplante de 1,5 m.
- Voladizo de hasta 1 m como hipótesis; un voladizo mayor bajaría la presión, pero lo limitan los linderos.
- No se modelan zapata combinada, pilotes, losa aligerada ni losa compensada.
- 11 edificios y un solo escenario de viento.
- **Nada de esto diseña cimentaciones reales:** el estudio de suelos, la interacción suelo-estructura y la firma del ingeniero son insustituibles.
