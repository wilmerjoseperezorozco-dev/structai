# Prerregistro #324: redimensionar por viento

Fijado el 2026-11-25, **antes** de correr la población. Solo se corrió un piloto de 1 edificio (id 106) para revisar que el script funcione.

- **Script:** `scripts/memorias_sinteticas/viento_324.py`.

## Hallazgo previo: no hace falta cambiar código

El punto 1 del issue pedía que el optimizador incluyera las combinaciones con W. Al revisar el código, **ya lo hace**.

`optimizar_edificio_3d.optimizar` usa como juez `disenar_edificio`, y este agrega las combinaciones B.2.4-3, -4 y -6 con los casos de viento 1–4 cuando el proyecto declara `VientoB6`. Lo que faltaba era **correrlo con viento**.

La búsqueda de secciones es una rejilla:
- h de viga entre 400 y 850 mm;
- columna c entre 300 y 1.500 mm en la mitad inferior, y c − Δ arriba, con Δ ∈ {0; 150};
- bisección por deriva sísmica y luego hasta 4 tamaños más.

**La deriva por viento no tiene límite en la NSR-10** y no entra en la búsqueda.

## Población y brazos

**Población: 25 edificios**, del grupo de 272 de #242 / #322, con W36D y los casos 1–4:
- **falla (11):** no cumplen con la sección del corpus. Son los 10 de #242 más el 1701 de #322.
- **cambia (14):** cumplen, pero su refuerzo difiere del diseño sin viento.

**Brazos:**
- `sin_viento`: el optimizador como generó el corpus;
- `W36D`: el mismo optimizador con VientoB6(36 m/s, D).

El sobrecosto se mide contra `sin_viento`, que corre con el mismo código.

## Predicciones

| Id | Métrica | Predicción |
|---|---|---|
| **R0** (control) | `sin_viento` reproduce las secciones del corpus (c inferior, c superior, h de viga) | 25/25. Si no, se reporta, y la referencia sigue siendo `sin_viento` |
| **R1** (primaria) | Grupo falla: el optimizador con W36D encuentra un diseño que cumple dentro de la rejilla | **11/11** (hay columnas hasta 1.500 mm) |
| **R2** | Grupo falla: sobrecosto directo (vigas + columnas) de W36D frente a `sin_viento` | mediana entre +2 % y +15 % |
| R3 | Grupo cambia: el óptimo con W36D no es más caro que la sección del corpus con el refuerzo por viento (W36D_c14 de #322) | ≥ 12/14; mediana del sobrecosto frente a `sin_viento` < 3 % |
| R4 | Grupo falla: la solución sube la columna inferior frente a `sin_viento` | ≥ 8/11 (la falla es biaxial en las columnas de los pisos bajos) |

## Reglas

- Los criterios no cambian después de ver los resultados. Los errores se reportan por id.
- Muros y sistemas combinados (#119) quedan fuera, porque el motor no los diseña todavía. Si R1 falla, el informe dice en qué edificios haría falta otro sistema.
- **Un optimizador nunca aprueba un diseño: solo propone, y el ingeniero firma.**
