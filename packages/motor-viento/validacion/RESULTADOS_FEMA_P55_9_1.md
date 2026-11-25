# Validación de la cubierta liviana (fijaciones) contra FEMA P-55, Ejemplo 9.1 (#292)

- **Prerregistro:** [#292, comentario 7148132351](https://github.com/wilmerjoseperezorozco-dev/structai/issues/292#issuecomment-7148132351). Código `49d262a`, corrido sin cambios.

## Resultado: NO PASA

| Viguetas | Separación adoptada por el libro | Motor (zona 2, prerregistrado) | Criterio s_libro ≤ s_motor < 1,5·s_libro |
|---|---|---|---|
| 16 in | 4 in | 8,65 in | no |
| 24 in | 3 in | 5,77 in | no |

## Diagnóstico post hoc (no cuenta como validación)

1. **Zona: el supuesto prerregistrado no coincide con el del libro.** El libro no usa la zona 2 ("borde"). Toma la succión máxima de toda la cubierta, la de la zona 3 del alero (108,7 psf en exposición C), y la aplica a todo el borde. Lo hace como recomendación de uniformidad ("same nailing schedule … throughout all edge zones").
2. **Con la zona del libro el cálculo coincide.** Con la zona 3 del alero (Fig. 7°–27°), el motor da 128,4 psf ASD y separaciones de 4,63 y 3,09 in. Son exactamente las del libro sin redondear (66 lb / (128,3 psf · s)), que redondea a 4 y 3 in.
3. **Ajuste de exposición C → D a 33 ft:** el motor da 1,179 y el libro 1,18.

## Consecuencias

- La aritmética de la fijación y el Kz de la exposición D quedan comprobados, pero de forma post hoc.
- La validación falló por la regla de selección de zona, y eso es una decisión de diseño:
  - `verificar()` ya revisa cada zona por separado, aleros incluidos.
  - Falta ofrecer la opción "una sola separación en todo el borde, con la zona que gobierna", como hace el libro.
- Cualquier corrección es una v2 y debe validarse con datos distintos. El Ej. 9.1 ya está usado.
