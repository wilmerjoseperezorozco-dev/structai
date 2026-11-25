# Prerregistro #322: efecto de los casos 2–4 de viento (Fig. B.6.5-6) en edificios de zona sísmica baja

Fijado el 2026-11-24, **antes** de correr la población. Solo se corrió un piloto de 2 edificios para revisar que el script funcione.

- **Código:** `_casos_viento_parciales` en `packages/orquestador/src/diseno_edificio_3d.py`, commit `7870dcc` más la opción `casos_parciales` de este commit.
- **Script:** `scripts/memorias_sinteticas/viento_322.py`.

## Qué cambia

La NSR-10 B.6.5.12.3 obliga a los casos 2–4 de la Fig. B.6.5-6 en el método general:
- **caso 2:** 0,75·P por eje, con un momento torsor M_T = 0,75·F·e;
- **caso 3:** 0,75·P en X y en Y a la vez;
- **caso 4:** 0,563·P en X y en Y, con M_T = 0,563(Fx·ex + Fy·ey).

En todos, e = ±0,15·B. Se recorren todos los signos.

Hipótesis declaradas en la memoria:
- solo cargas laterales;
- e = 0,15·B también si la estructura es flexible.

Estos casos **son obligatorios**: quedan activos por defecto pase lo que pase aquí. **Lo que se mide es cuánto cambian el diseño.**

## Población y brazos

- **Población:** la misma de #242, 272 pórticos de concreto de zona baja que no son edificios bajos. La pregunta es distinta: el efecto de los casos 2–4, no el del viento.
- **Brazos por edificio:** W28C y W36D, cada uno con **solo el caso 1 (c1)** y con **los casos 1–4 (c14)**. Es el mismo código; solo cambia `VientoB6.casos_parciales`.

## Anclaje físico (antes de ver datos)

Toma una planta cuadrada y regular con n marcos por dirección igualmente espaciados, diafragma rígido y marcos de igual rigidez en X y Y. La fuerza del **marco de borde** en el caso 2, comparada con el caso 1, es:

  0,75·[1 + 0,45·(n − 1)/(n + 1)]

Eso da 0,92 con n = 3, 0,97 con n = 5 y tiende a 1,09 cuando n → ∞.

En la población, n va de 3 a 6, así que **el caso 2 casi nunca supera al caso 1 en vigas ni en marcos de borde**.

En cambio, el **caso 3** pone 0,75 en ambos ejes a la vez sobre las columnas, que es flexión biaxial. Con interacción lineal suma 1,5 frente a 1,0 del caso 1. El caso 4 da unos 0,69 por eje, que suman cerca de 1,4. **El caso 3 debería gobernar las columnas allí donde el viento ya gobierna.**

## Predicciones

Las IC95 son de Wilson.

| Id | Métrica | Predicción |
|---|---|---|
| **T0** (control) | W28C_c1 y W36D_c1 reproducen la firma de refuerzo de #242 | 272/272 en ambos. Si no, se reporta antes de interpretar nada |
| **T1** (primaria) | W36D: edificios cuyo refuerzo cambia de c1 a c14 | 1 ≤ k ≤ 40, es decir, entre 0,4 % y 14,7 % |
| T1b | De los que cambian en T1, cuántos ya tenían refuerzo gobernado por viento en #242 (control ≠ c1) | ≥ 80 % |
| T2 | W36D: edificios que cumplían con c1 y dejan de cumplir con c14 | ≤ 10 |
| T3 | W36D: cambios en columnas frente a vigas | k_columnas ≥ k_vigas |
| T4 | W28C: edificios cuyo refuerzo cambia de c1 a c14 | ≤ 5 |

Descriptivo, sin criterio: el costo relativo en los edificios que cambian y los que recuperan el cumplimiento.

## Reglas

- Los criterios no cambian después de ver los resultados.
- Los errores se reportan por id y no se reemplazan.
- Si T0 falla, se diagnostica la diferencia de código antes de leer T1–T4.
- Cualquier ajuste del código de viento es una versión nueva, medida con otra pregunta u otros datos.
