# Resultados B1: precio de agregados y producción de canteras (2026-11-08)

Protocolo fijado antes de calcular: [`PROTOCOLO_AGREGADOS_CANTERAS.md`](PROTOCOLO_AGREGADOS_CANTERAS.md). Código: `agregados_canteras.py`. Salida: `agregados_canteras_resultados.json`.

**Resultado: nulo.** Con 140 provincias (62 insumos de agregados en m³ de INVIAS 2026-1, 32 departamentos) y 535 municipios con producción declarada a la ANM en 2019-2024:

| Hipótesis | ρ de Spearman | IC95 % por departamentos | Holm (α = 0,05) |
|---|---:|---|---|
| B1a: índice de prima vs volumen declarado del departamento (esperado negativo) | −0,07 | [−0,41; +0,23] | No cumple (p ajustado 1,00) |
| B1b: índice vs distancia al productor más cercano (esperado positivo) | +0,03 | [−0,30; +0,36] | No cumple (p ajustado 0,87) |
| B1c: parcial, controlando por la distancia a Bogotá | +0,08 | [−0,28; +0,38] | Solo descriptiva (B1b no se cumplió) |
| Referencia: índice vs distancia a Bogotá | −0,11 | [−0,41; +0,33] | — |
| Referencia: índice vs distancia al puerto | +0,12 | [−0,26; +0,39] | — |

**Lectura.** En los precios de referencia de INVIAS, la prima de los agregados de una provincia no se explica por la oferta declarada de canteras de su departamento ni por la distancia a los 25 mayores municipios productores. Tampoco la explican la distancia a Bogotá ni al puerto. Todos los intervalos son anchos e incluyen 0 en ambos sentidos.

**Qué no se puede concluir.** No se concluye que la oferta no influya en el precio: se concluye que **estos datos no lo muestran**. Hay tres razones que limitan la lectura:
1. Solo hay 32 departamentos independientes, así que la potencia es baja: un efecto moderado (|ρ| < 0,4) no se distinguiría de cero.
2. El volumen de la ANM es el declarado para regalías, y gran parte de los agregados sale de extracción informal o de río sin título.
3. Los precios de INVIAS son de referencia, calculados por la entidad, y pueden suavizar la geografía real del mercado. La ubicación se aproximó con la capital departamental.

**Qué sugiere para el trabajo siguiente.** Si se quiere contrastar la oferta, hacen falta cotizaciones de mercado con ubicación (no precios de referencia) o volúmenes verificados de canteras. Con los datos actuales no vale la pena refinar este modelo.
