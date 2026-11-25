# Resultados #322: efecto de los casos 2–4 de viento (Fig. B.6.5-6)

- **Prerregistro:** [`PRERREGISTRO_322_VIENTO_TORSIONAL.md`](PRERREGISTRO_322_VIENTO_TORSIONAL.md), publicado en [#322](https://github.com/wilmerjoseperezorozco-dev/structai/issues/322#issuecomment-7149825876) antes de correr.
- **Corrida:** 1.088 diseños (272 edificios × 4 brazos), 0 errores, 7 min.
- **Datos:** `data/memorias_sinteticas/f1_322/` (no versionados).

## Veredictos: todas las predicciones se cumplen

| Id | Resultado | Predicción | Veredicto |
|---|---|---|---|
| **T0** | c1 reproduce la firma de #242: 272/272 en W28C y 272/272 en W36D | 272/272 | **se cumple**: la comparación es limpia |
| **T1** | W36D: **10/272 (3,7 %)** cambian refuerzo, IC95 [2,0; 6,6 %] | entre 1 y 40 | **se cumple**, pero el rango era amplio: la prueba es débil |
| T1b | 9 de los 10 ya estaban entre los 24 gobernados por viento en #242 | ≥ 80 % | **se cumple** (90 %) |
| T2 | 1 edificio deja de cumplir (id 1701); los que no cumplen pasan de 10 a 11 | ≤ 10 | **se cumple** |
| **T3** | columnas 9, vigas 1 | k_columnas ≥ k_vigas | **se cumple**: lo que esperaba el anclaje físico (biaxial del caso 3) |
| T4 | W28C: 0/272 cambian, IC95 [0; 1,4 %] | ≤ 5 | **se cumple** |

**Costo** en los 10 que cambian: mediana +0,5 %, máximo +1,7 %.

## Lectura

- **Los casos 2–4 son obligatorios (B.6.5.12.3) y quedan activos por defecto.** Su efecto es pequeño y se concentra donde el viento ya gobernaba: 10 de 272 edificios con W36D y ninguno con W28C. El costo sube menos del 2 %.
- **El efecto cae sobre las columnas, no sobre las vigas.** Es coherente con el cálculo previo:
  - el caso 2 (torsión) no supera al caso 1 en el marco de borde cuando hay 3 a 6 marcos por dirección (0,92–0,97);
  - la carga simultánea en X y Y (casos 3 y 4) sí aumenta la flexión biaxial de las columnas.
  - **No se registró qué caso gobierna cada elemento**, así que "es el caso 3" sigue siendo hipótesis y no está medido.
- **El edificio 1701 deja de cumplir.** Pasa a la lista de redimensionamiento de #324, junto con los 10 de #242.

## Limitaciones

- Solo cargas laterales. La succión de cubierta no se combina con los casos 2–4 (HIPÓTESIS declarada).
- e = 0,15·B también en estructuras flexibles; no se calcula e_R (B.6.5-19).
- El nodo maestro está en el centro geométrico de la planta.
- **Sigue pendiente:** los casos torsionales de **edificios bajos** (Fig. B.6.5-7, nota 5), parte 2 de #322. Siguen declarados como no verificados en la memoria.
- La misma población de #242, con una pregunta distinta. No es una validación contra la realidad: mide la sensibilidad del diseño a una obligación de la norma.
