# Clasificación de hipótesis, protocolos y enmiendas del 7 al 9 de noviembre de 2026

Una hipótesis, un protocolo o una enmienda **no es un motor**. Es evidencia sobre si una relación se sostiene. Un motor es una función determinista y reutilizable (entradas → salida con contrato `ResultadoMotor`), verificada contra una referencia independiente. Un resultado de investigación puede dar origen a un motor solo si su criterio preregistrado se cumplió **y** produce algo que alguien pueda calcular con entradas propias. Los criterios que debe cumplir un motor están en [`REGLAS_MOTORES_DE_CALCULO.md`](REGLAS_MOTORES_DE_CALCULO.md) (sección «Criterio de motor medido a producción»).

Lectura hecha sobre el veredicto de cada archivo `RESULTADOS_*.md` (no se re-ejecutó ningún análisis).

## Candidatos a motor (2)

| Origen | Criterio | Lo que produciría | Límites que deben quedar en el contrato | Issue |
|---|---|---|---|---|
| Regionalización de caudales sin aforo, Etapa A | Se cumple, con mejora pequeña (factor de error típico 1,75 frente a 1,88 del área sola) | Caudal de diseño en sitio sin aforo, con intervalo | Rango de validez de área y pendiente; 1 de cada 10 estimaciones se equivoca por factor 4 a 6; pendiente con signo no interpretable; no usar para dimensionar | #151 |
| F1, cribado hidroeléctrico a filo de agua | Descriptivo, preregistrado, sin validación externa | Potencia bruta por tramo y clase legal para una estación | Caudales mensuales, DEM de 90 m, sin caudal ecológico ni derechos de agua; es cribado, no inventario | #152 |

## Alimentan issues que ya existen (no son motores nuevos)

| Hallazgo | Destino |
|---|---|
| 29 municipios con valor de Aa distinto entre el Apéndice A-4 y la capa del SGC | #135 (sísmica municipal) |
| Periodo de retorno económico de alcantarillas (T* = 100 años en 56 de 60 combinaciones, depende de la hidrología de cuencas pequeñas que los datos no entregan) | #139 (alcantarillado y drenaje) |
| Costo en riesgo del índice ICOCIV (6–8 % a 6–12 meses) y transmisión TRM/WTI no significativa | #102 y #113 (precios) |
| Índice de susceptibilidad municipal (AUC fuera de muestra 0,90; se omite en Andina y Pacífica) | #131 (gobernanza de sustitutos; ya conectado como plugin del chat con su límite regional) |
| Regla de lluvia acumulada de 5 días (AUC 0,775; 68 % de falsas alarmas) | No es motor: son señales estadísticas, no alertas oficiales |

## Sin motor: el criterio no se cumplió o el resultado es descriptivo

| Resultado | Veredicto |
|---|---|
| E1, pendiente del cauce en la regionalización | No se cumple |
| H3, régimen térmico como predictor del caudal | No se cumple |
| No estacionariedad espacial (modelo por región) | No se cumple; el modelo no se transfiere al Caribe (factor 3) |
| Etapa B, corrección de sesgo de CHIRPS por cuantiles | No se cumple |
| Brecha A-4 frente a SGC y población (B1) | No se cumple |
| Mapa municipal de intensidad del SGC desde sus puntos | No se reproduce |
| Índice geomorfométrico vial (V1 y V2) | No se cumplen; no supera a la pendiente sola |
| V1 fuera del Caribe y V1-Perú | No se confirma; el hallazgo es la heterogeneidad regional |
| Sesgo de reporte de la UNGRD | No explica el efecto del Caribe |
| Precio de agregados y producción de canteras (B1) | Nulo |
| Ecuaciones de caudal de la literatura | Ninguna evaluable (acceso al texto y rango de validez) |
| Mapa de amenaza del SGC frente a eventos UNGRD | Criterios cumplidos, pero la pendiente sola ordena igual |
| Normales de CHIRPS frente a IDEAM (H1) | Se cumple, mejora práctica pequeña; acuerdo demasiado bueno para ser independiente |
| Docling frente a pypdf en A.2 | Ventaja de 2 fichas de 59; herramienta, no motor |
| Coherencia espacio-temporal de anomalías de caudal | Descriptivo |
| Barrido exploratorio del Caribe | Genera hipótesis; no confirma nada |
| Catálogo de sismos del SGC frente al Aa; intensidad frente al A-4 | Débil; PGA del SGC no comparable con Aa |

El valor de estos resultados negativos es evitar construir motores sobre hipótesis que no se sostuvieron. Las limitaciones de cada caso y lo que haría falta para repetirlo están en [`informes_no_calificados/INFORMES_NO_CALIFICADOS_2026-11.md`](informes_no_calificados/INFORMES_NO_CALIFICADOS_2026-11.md).

## Issues abiertos a partir de esta clasificación

| Issue | Tipo |
|---|---|
| #151 Caudal de diseño en sitios sin aforo por regionalización | Motor |
| #152 Cribado hidroeléctrico a filo de agua (F1) | Motor |
| #153 Señal de lluvia acumulada de 5 días para movimientos en masa | Motor |
| #154 Evaluar la literatura de caudales que no se pudo leer | Repetición con protocolo ya fijado |
| #155 Repetir E1 y el índice vial con DEM de 30 m y radar | Protocolos nuevos |
| #156 Más estaciones para Orinoquía, Amazonía, Pacífica y Caribe | Datos y potencia |
