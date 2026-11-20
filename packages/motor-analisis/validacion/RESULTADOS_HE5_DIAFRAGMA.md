# Resultados HE5 (#274): diafragma rígido frente a semirrígido

Prerregistro: `PRERREGISTRO_HE5_DIAFRAGMA.md`. Corrida del 2026-11-19, de 07:32 a 07:51, con `he5_diafragma.py`. Datos: `he5_resultados.json`.

## Veredicto: **CONFIRMADA** (en pórticos sin muros)

Población principal: aspecto < 3, 162 edificios, E_losa = 0,5·Ec.

| E_losa | Edificios con error ≥ 5 % | Proporción | IC95 de Wilson | Error mediano | Error máximo | Veredicto |
|---|---|---|---|---|---|---|
| **0,5·Ec (principal)** | 2 de 162 | 1,2 % | [0,3 %; 4,4 %] | 0,46 % | 5,8 % | **CONFIRMADA** |
| 0,25·Ec | 5 de 162 | 3,1 % | [1,3 %; 7,0 %] | 0,64 % | 6,4 % | CONFIRMADA |
| 1,0·Ec | 0 de 162 | 0 % | [0 %; 2,3 %] | 0,30 % | 4,9 % | CONFIRMADA |

El veredicto se mantiene en las dos sensibilidades.

## Descriptivo (E_losa principal)

| Grupo | Edificios con error ≥ 5 % / n | Error mediano | Error máximo |
|---|---|---|---|
| Aspecto 1,00 | 0 / 27 | 0,19 % | 1,9 % |
| Aspecto 2,00 | 0 / 27 | 0,50 % | 4,4 % |
| Aspecto 2,67 | 1 / 27 | 0,74 % | 5,8 % |
| Aspecto 3,00 (aparte) | 2 / 27 | 0,85 % | 6,4 % |
| 3 pisos | 0 / 54 | 0,23 % | 1,4 % |
| 6 pisos | 0 / 54 | 0,46 % | 1,7 % |
| 10 pisos | 2 / 54 | 1,6 % | 5,8 % |
| t = 0,05 m (torta de aligerada) | 2 / 54 | 0,64 % | 5,8 % |
| t = 0,10 m | 0 / 54 | 0,42 % | 4,9 % |
| t = 0,15 m | 0 / 54 | 0,34 % | 4,3 % |

Los casos con error de 5 % o más siguen un patrón. Los cumplen todos estos:
- 10 pisos y L = 8 m;
- torta de 5 cm;
- aspecto ≥ 2,33;
- carga en la dirección **larga** (Y).

El error crece con el aspecto, con la altura y con una losa más delgada.

Una observación que no verifiqué: el error es mayor con la carga paralela a la dimensión larga que con la perpendicular. Eso sugiere que lo que gobierna es la deformación axial en el plano a lo largo de los pórticos largos, no la flexión de la losa como viga de gran canto. Para confirmarlo hay que separar los dos efectos.

## Qué significa para el motor

- **Pórticos sin muros, aspecto < 3:** el diafragma rígido es adecuado. El error típico está por debajo del 1 % y casi nunca llega al 5 %.
- **Cuándo advertir:** el motor puede avisar ("considere un diafragma semirrígido") cuando se juntan aspecto ≥ 2,33, 10 pisos o más y una losa aligerada con torta delgada.

## Limitaciones

- **Sin muros.** No hay muros ni núcleos. Con elementos verticales muy rígidos en los extremos, el diafragma trabaja como viga y la diferencia es mayor. Este resultado **no** aplica a sistemas combinados ni de muros; eso es una hipótesis aparte.
- **Malla de la losa.** Hay una membrana QM6 por vano, sin estudio de convergencia en esta malla. La flexión pura sí está verificada como exacta.
- **Planta y prediseño.** Las plantas son regulares y sin aberturas. El prediseño es por gravedad, sin iterar la deriva.
- **Torsión.** No hay torsión accidental. Ambos modelos reciben la misma carga, con la resultante en el centro de masa.
