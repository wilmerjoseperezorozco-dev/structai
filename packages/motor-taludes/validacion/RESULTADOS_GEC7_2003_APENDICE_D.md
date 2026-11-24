# Validación de la v2: estabilidad global contra GEC 7 de 2003, Apéndice D (#241)

- **Prerregistro:** [#241, comentario 7130299158](https://github.com/wilmerjoseperezorozco-dev/structai/issues/241#issuecomment-7130299158), publicado antes de correr.
- **Fuente:** FHWA-IF-03-017 (copia oficial de ROSA P.; la sha-512 coincide con la de la ficha).
- **Código:** commit `7d62ea2`, script `validacion/gec7_2003_apendice_d.py` (`7e5c90c`). Se corrió sin cambios.

## Resultado: NO PASA (1 de 2 casos primarios dentro de ±10 %)

| Caso | FS SNAIL | FS motor | Desvío | ¿Dentro? |
|---|---|---|---|---|
| 2: uniforme, D + L | 1,51 | 1,653 | +9,4 % | sí |
| 4: no uniforme, D + L | 1,50 | 1,674 | +11,6 % | **no** |
| 5: no uniforme, sismo (informativo) | 1,13 | 1,297 | +14,8 % | (no) |
| Control sin clavos, H = 0,7 m (informativo) | 1,23 | 1,397 | +13,6 % | (no) |

**Sensibilidades** (informativas):
- caso 2 con L = 7,2 m: 1,695;
- carga viva de 0 a 5 m: 1,708 en el caso 2 y 1,719 en el caso 4.

**Sesgo:** el motor queda **por encima** de SNAIL en los cuatro casos, es decir, del lado inseguro. El control no tiene clavos y muestra el mismo sesgo, así que la diferencia no viene del refuerzo.

## Diagnóstico post hoc (NO prerregistrado, no cuenta como validación)

1. **Defecto en el control del paramento continuo.** Los círculos críticos de los casos 2, 4 y 5 cortan el paramento entre 0,51 y 0,69 m sobre el pie. El control evalúa el terreno en el punto de salida interpolado en la malla. En un paramento vertical, el salto de 0 a H ocurre entre dos puntos de la malla, así que el control no lo ve. Por eso la fila 7 (a 0,5 m del pie) aparece como `fuera`.
2. **Ese defecto no explica la diferencia: la empeora.** Si se exige que el círculo pase por el pie o por debajo, los FS suben:

   | Caso | FS forzado | Desvío |
   |---|---|---|
   | 2 | 1,966 | +30 % |
   | 4 | 1,764 | +18 % |
   | 5 | 1,391 | +23 % |
   | Control | 2,117 | +72 % |

3. **Causa probable: la forma de la superficie.** SNAIL busca cuñas bilineales por el pie. En un corte vertical, la superficie crítica es casi plana y un círculo por el pie no la aproxima bien.
   - En el control, el método de Culmann (plano por el pie, con c y tanφ reducidos por el FS) da FS ≈ 1,29. Ese valor está entre SNAIL (1,23) y el Bishop circular (1,40).
   - Que el motor de excavaciones (`altura_critica_vertical_rankine`) dé una altura menor que el mejor círculo es consistente con esto.

## Qué sigue (v3, con datos distintos)

- Corregir el control de salida: exigir que la altura del círculo en el paramento sea ≤ tolerancia, de forma analítica y no con la malla.
- Agregar superficies no circulares por el pie: cuñas bilineales con equilibrio de fuerzas (como SNAIL), o Spencer o Janbu con superficies poligonales.
- Validar la v3 en casos que no sean este ni el Apéndice C de 2015.
- Hasta entonces **no se integra a la API**. El Método A tampoco tiene validación independiente.
