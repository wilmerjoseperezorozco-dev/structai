# Resultados: caudales de diseño en sitios sin aforo por regionalización, validación ciega (Etapa A, 2026-11-08)

Protocolo y enmienda 1, fijados antes de ajustar ningún modelo: [`PROTOCOLO_REGIONALIZACION_CAUDALES.md`](PROTOCOLO_REGIONALIZACION_CAUDALES.md). Código: `lluvia_climatologia.py`, `cuencas_estaciones.py`, `regionalizacion_validacion.py`. Salidas: `cuencas_estaciones.csv`, `regionalizacion_resultados.json`.

## Datos finales
257 estaciones del IDEAM con cuenca delineada (variante de ajuste a la red de 1.500 m, elegida con la regla de la enmienda 1: la diferencia de mediana de |elevación del terreno − altitud del catálogo| frente a la mejor variante fue de 4,8 m, menor de 5 m), 50 bloques espaciales de 1°. Por región: Andina 152, Caribe 59, Pacífica 35, Orinoquía 11. Rango de validez: área 5 a 18.600 km², pendiente media 0,7 a 59 %, lluvia media anual 770 a 6.900 mm. Se excluyeron las cuencas que tocan el borde del modelo de terreno (36) y las de menos de 5 km² (2).
**Dos errores propios corregidos antes de ajustar nada:** (1) el modo de ajuste por defecto de la librería devolvía cuencas de una sola celda en 105 estaciones; (2) el chequeo de borde no detectaba cuencas truncadas porque la última fila del terreno es NODATA. Ambos están en la enmienda del protocolo.

## Prueba confirmatoria: **se cumple, con una mejora pequeña**
A T = 10, nuestro método (M2: área, lluvia y pendiente) tiene una mediana de |error ln| menor que el área sola (B1): diferencia **−0,094, IC95 % [−0,350; −0,007]** por bloques espaciales. El límite superior está muy cerca de 0. En términos prácticos: el **factor de error típico** pasa de **1,88 (B1) a 1,75 (M2)**, es decir, un error mediano de unos 75 % en lugar de 88 %.

## Margen de error en la validación ciega (T = 10, 257 estaciones)
| Modelo | Factor de error típico | Sesgo (mediana de Q̂/Q) | Dentro de factor 2 | Cobertura del IC90 |
|---|---:|---:|---:|---:|
| B0 caudal específico constante | 1,81 | 0,98 | 56 % | 90 % |
| B1 área sola | 1,88 | 1,09 | 53 % | 89 % |
| M1 área y lluvia | 1,89 | 1,10 | 54 % | 88 % |
| **M2 área, lluvia y pendiente** | **1,75** | **0,94** | **58 %** | **86 %** |
| M3 M2 con región natural | 1,87 | 0,94 | 53 % | 84 % |
| M4 cuenca gemela | 2,12 | 1,04 | 46 % | no aplica |

**Margen de error cuantificable de M2 a T = 10.** La razón Q estimado / Q observado tiene cuantiles de 5 %, 25 %, 50 %, 75 % y 95 % de **0,25; 0,55; 0,94; 1,68 y 6,04**. Es decir, en la mitad de las estaciones el método acierta dentro de un factor de ~1,7, pero en 1 de cada 10 se queda **4 veces o más por debajo** o se pasa **6 veces o más por encima**. Esto es verdad para todos los periodos de retorno (factor típico de M2: 1,75 a T = 2, 1,72 a T = 5, 1,76 a T = 25, 1,79 a T = 50).

## Lo que no mejora y lo que sí
- **El caudal específico constante (B0) es tan bueno como el área sola**: M2 frente a B0, diferencia −0,044, IC95 % [−0,199; +0,069], no significativa. La relación con el área sola no agrega nada a una constante en estos datos.
- **La pendiente y la lluvia aportan poco por separado**: M2 frente a M1 −0,034 [−0,120; +0,060]; M1 frente a B1 −0,050 [−0,164; +0,039]. Solo la combinación pasa el umbral, y por poco.
- **Los efectos de región no ayudan** (M3 frente a M2: −0,012 [−0,030; +0,007]).
- **La transferencia desde la cuenca gemela empeora** el resultado frente a la regresión (+0,195 [+0,095; +0,289]).
- **Por región natural (T = 10)**: en el Caribe, M2 (1,89) mejora mucho a B1 (2,62); en la Pacífica mejora (1,51 frente a 1,96); en la Andina no hay diferencia (1,80 frente a 1,76), y en la Orinoquía (11 estaciones) tampoco puede concluirse.

## Ecuaciones propias (ajuste con las 257 estaciones; ln Q en m³/s; A en km², P en mm, S en %)
T = 10: **ln Q = −4,77 + 0,50 ln A + 1,27 ln P − 0,73 ln S**, R² = 0,55, desviación residual 0,99 en logaritmo natural. IC95 % por bloques: exponente del área [0,40; 0,61], de la lluvia [0,65; 1,69] y de la pendiente [−0,87; −0,40]. Para los demás periodos, en `regionalizacion_resultados.json` (T = 2: A 0,58; T = 50: A 0,43). **No usar fuera de los rangos de validez de arriba.**
**Advertencia sobre los signos.** La pendiente sale con **signo negativo**: a igual área y lluvia, las cuencas más empinadas tienen caudales máximos *menores* en estos datos. Esto contradice la expectativa física para crecientes y casi seguro refleja confusión (pendiente y elevación son proxis de región y de cuencas de montaña con registros horarios, que suavizan picos rápidos). La ecuación sirve para estimar, no para interpretar causas, y no debe leerse como «más pendiente, menos caudal».

## Incertidumbre y sensibilidad
- **Errores supuestos en los predictores** (área 15 %, pendiente 20 %, lluvia 15 %; son supuestos, no errores medidos): agregan una dispersión de solo 0,25 en ln Q, frente a una desviación residual del modelo de 0,99. **El error del método viene del propio modelo y de los datos de caudal, no de los errores de los predictores.**
- **El resultado de M2 es estable**: factor típico 1,73 a 1,78 con registros de 40 años o más, con forma ξ estable, objetivo Log-Pearson III, sin zona de exclusión (0 km) o con 100 km, o con otra variante de ajuste a la red (500 m). Con la celda de la estación (0 m, solo 79 estaciones) sube a la mejor cifra (1,61 frente a 1,97 de B1), pero con una muestra menor y sesgada hacia estaciones en cauces grandes. **La zona de exclusión no cambia el resultado**: no se detectó fuga por vecindad espacial.
- **B1 es más sensible** que M2 a los filtros (por ejemplo 2,07 con cuencas de hasta 2.000 km²).

## Lectura
1. Es posible estimar el caudal de diseño en un sitio sin aforo con un error típico de factor ~1,75, y esto se verificó a ciegas con 257 estaciones. Es una **herramienta de tamizaje**: sirve para ordenar, priorizar y dar un orden de magnitud, no como valor de diseño.
2. La ventaja del método sobre una constante simple es **pequeña** y la pendiente sale con un signo que no se interpreta. No debe presentarse como una mejora decisiva.
3. En el Caribe la mejora es grande (de 2,62 a 1,89), pero con solo 59 estaciones y sin haber probado por qué: puede deberse a que la lluvia diferencia mucho entre cuencas planas (la ciénaga y la llanura no se modelan), y no se verificó.
4. Una de cada diez estimaciones se equivoca por un factor de 4 a 6: **quien use la cifra para dimensionar una obra debe aplicar el margen y confirmar con un estudio hidrológico**.

## Límites
Caudal observado es el máximo horario, no el pico instantáneo: subestima los picos de cuencas pequeñas, lo que **empeora el error del método en la dirección de sobrestimar** frente a lo observado. Estacionariedad supuesta. DEM de 90 m. El área de cuenca no se verificó con un valor oficial: el ajuste a la red de drenaje puede equivocarse de cauce (por eso se probaron tres variantes). Excluye cuencas reguladas, trasvasadas o con minería no identificadas. La lluvia media anual no es la lluvia de la tormenta de diseño. **No sustituye el estudio hidrológico de un proyecto con ingeniero responsable.** La Etapa B (corrección de sesgo de CHIRPS con pluviómetros) no se ha ejecutado.
