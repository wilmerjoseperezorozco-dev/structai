# Resultados E1: pendiente del cauce principal y regionalización de caudales máximos (2026-11-08)

Protocolo: [`PROTOCOLO_PENDIENTE_CAUCE.md`](PROTOCOLO_PENDIENTE_CAUCE.md) (con Enmienda 1, ambos publicados antes de calcular). Código: `pendiente_cauce_extraer.py`, `pendiente_cauce_analisis.py`. Salidas: `pendiente_cauce.csv`, `pendiente_cauce_resultados.json`.

**Resultado primario: no se cumple.** Con esta muestra y este DEM, añadir o sustituir la pendiente de cauce no mejora de forma demostrable la estimación regional a T = 10 años.

## Muestra y calidad
- 257 cuencas de la Etapa A; **256 en el análisis**. Una (0015037020, departamento 47) se excluyó por la regla declarada de no tener S_ts: su ruta de flujo cruza una celda sin dato de cota (desnivel NaN). En el JSON esta exclusión aparece bajo la etiqueta `sin_fila_de_cauce`, que es un nombre equivocado mío: la fila existe, lo que falta es la pendiente.
- Ninguna ruta inválida, ninguna diferencia de área mayor al 15 % con la Etapa A, ninguna con L < 0,5 √A. Longitud mediana del cauce: 62 km.
- El modelo de referencia M2 reproduce la Etapa A: factor típico 1,75 a T = 10; coeficientes de la misma magnitud (ln A +0,50; ln P +1,26; ln S −0,73; Etapa A con una cuenca más: −4,77 / 0,50 / 1,27 / −0,73).
- **Limitación del insumo, medida:** en la mediana de las cuencas, el **44 %** de los tramos de celda de la ruta quedan en el piso de 0,0005 m/m del protocolo. Con celdas de ~90 m, el relieve del cauce en tramos planos o estrechos no se resuelve, y la pendiente de Taylor-Schwarz sale sistemáticamente baja (mediana 0,0017 m/m).

## Primario (T = 10, IC 97,5 % por corrección de Bonferroni; negativo = mejora)
| Contraste | Diferencia (mediana de \|ln(Q̂/Q)\|) | IC 97,5 % | Decisión |
|---|---:|---|---|
| M2b (añade S_cauce) − M2 | −0,0027 | [−0,0088; +0,0049] | No se cumple |
| M2c (sustituye por S_cauce) − M2 | +0,0436 | [−0,0169; +0,1127] | No se cumple (apunta a peor) |

Factor de error típico a T = 10: M2 1,75; M2c 1,82; M2b 1,76. R² del ajuste completo: M2 0,553; M2c 0,485; M2b 0,554. Con T = 2, 5, 25 y 50 la imagen es la misma (diferencias de M2b − M2 entre −0,004 y 0,000 con IC que incluyen 0; M2c es peor, y a T = 2 su IC excluye 0 hacia peor: +0,082).

## Secundarios (descriptivos; 24 contrastes sin corrección, no cambian la decisión)
- **Cuencas con pendiente media > 30 % (n = 111):** M2b − M2 = −0,0110 [−0,0212; −0,0038]. Es el único contraste cuyo IC excluye 0 a favor del modelo con S_cauce, **pero** el efecto es de ~1 % en el error logarítmico, pertenece a una familia de 24 contrastes sin corregir, y el estrato ≤ 30 % va en sentido contrario (+0,0052 [−0,0023; +0,0119]). **No lo presento como hallazgo**; es una pista a confirmar con otro DEM u otra muestra.
- Caribe (n = 58) y Andina (n = 152): ningún contraste con IC que excluya 0.
- **Variante S_10-85** (sensibilidad prevista): M2c10 factor 1,74 a T = 10 (similar a M2) y R² 0,561; sus contrastes por estrato incluyen 0. La pendiente 10-85 correlaciona 0,83 con la pendiente media de la cuenca en logaritmos; la de Taylor-Schwarz solo 0,52, otra señal de que esta última está dominada por el piso.

## Coeficientes
La pendiente entra con **signo negativo** en todos los modelos (S_cuenca −0,73 [−0,88; −0,44]; S_cauce de Taylor-Schwarz en M2c −0,62 [−0,94; −0,24]; en M2b el coeficiente de S_cauce es −0,09 [−0,41; +0,16] porque comparte información con S_cuenca). Es decir, a igual área y lluvia, las cuencas más empinadas de esta muestra tienen caudales máximos **más bajos**. No lo interpreto físicamente: puede deberse a confusión con otras características (clima, geología, regulación, altitud) que el modelo no incluye.

## Qué se concluye y qué no
- Se concluye que en estas 256 cuencas, con DEM de ~90 m, la geometría del cauce no aporta información demostrable sobre M2.
- **No se concluye** que la pendiente de cauce sea irrelevante: un DEM más fino (el Copernicus original es de 30 m; la cadena actual lo agrega a 90 m) y cuencas más pequeñas podrían cambiar el resultado. Tampoco se concluye nada sobre el dominio de la Resolución 0330 (menos de 80 ha), que esta muestra no cubre (cuenca mínima 5 km²).
- Sigue sin medirse la lluvia de diseño por duración, que es el otro insumo ausente.
