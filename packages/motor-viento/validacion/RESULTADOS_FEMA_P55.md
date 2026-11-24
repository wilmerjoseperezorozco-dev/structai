# Validación del motor de viento B.6 v1 contra FEMA P-55, Ejemplos 8.5 y 8.7 (#292)

- **Prerregistro:** [#292, comentario 7147728081](https://github.com/wilmerjoseperezorozco-dev/structai/issues/292#issuecomment-7147728081), publicado antes de abrir las soluciones.
- **Código:** `77fa908` (motor) y script `validacion/fema_p55_ejemplos_8_5_8_7.py`.

## Resultado: PASA, con una corrección del script declarada

| Caso | Libro | Motor | Desvío | Tolerancia |
|---|---|---|---|---|
| 8.7 cubierta, zona 1 (psf) | 34,7 | 34,67 | −0,1 % | ±5 % |
| 8.7 cubierta, zona 2 | 58,2 | 58,17 | −0,05 % | ±5 % |
| 8.7 cubierta, zona 3 | 87,5 | 87,55 | +0,06 % | ±5 % |
| 8.7 muro, zona 4 | 37,6 | 37,61 | +0,02 % | ±5 % |
| 8.7 muro, zona 5 | 46,4 | 46,42 | +0,04 % | ±5 % |
| 8.5 levantamiento ASD, θ = 20°, luz 24 ft (plf) | 424 | 428,3 | +1,0 % | ±10 % |

## Cambios hechos después de ver los resultados (declarados)

1. **Signo en H1.** El motor da la succión negativa (convención de B.6.5.12.1.1), y el libro tabula la "suction pressure" en magnitud. Con la comparación con signo, la primera corrida dio NO PASA (desvío −200 %). Se corrigió a `abs()`. Las magnitudes no cambiaron.
2. **θ por superficie en 8.7.** El libro toma la envolvente de las figuras:
   - cubierta con GCp de θ ≤ 7° (Fig. 30.4-2A = B.6.5-8B);
   - muros sin la reducción del 10 % (θ > 10°).

   Se capturó como dato (`_theta` = 5°, `_theta_muro` = 20°). El prerregistro decía "con la figura que use el libro".

## Diagnóstico (informativo, no cuenta)

- **Las componentes horizontales no cambian el resultado.** El libro sí las incluye (momentos respecto del apoyo a sotavento), mientras que el modelo prerregistrado solo usa las verticales. A 20° la diferencia queda en 1 %, pero puede ser compensación numérica: con otras geometrías habría que medirla.
- **Aleros.** El libro tabula los aleros con GCp −2,2 y −3,7, que son de la figura de 7° a 27° (B.6.5-8C). Con θ ≤ 7°, el motor da 49,9 y 82,3 psf, frente a 64,6 y 108,7. Es la misma envolvente de figuras: el motor debe ofrecer la envolvente cuando no se conoce θ.
- **Alcance de la validación.** H1 es casi una consulta de tablas más q, y H2 es un solo punto. Valida los coeficientes y la estática básica, no la V de la NSR-10 ni las combinaciones 0,9D + 1,6W.
- **Pendientes ≥ 30°:** el motor da levantamiento neto negativo, es decir, sin levantamiento. Coincide con la nota (d) de la Tabla 8-6: "Reduced uplift forces may be calculated for greater roof slopes".

## Qué sigue

- Integrar el caso W en el diseño de las vigas de cubierta (#292):
  - B.2.4-4: 1,2D + 1,6W + 1,0L + 0,5Lr;
  - B.2.4-6: 0,9D + 1,6W;
  - refuerzo en la cara contraria.
- Otro caso independiente para la parte que falta: componentes horizontales o luces distintas. La Tabla 8-6 da 36 valores más (luces y velocidades), pero salen del mismo método del libro.
