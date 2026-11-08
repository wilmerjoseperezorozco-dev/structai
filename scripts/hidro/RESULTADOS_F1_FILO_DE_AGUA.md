# F1: cribado de potencial hidroeléctrico a filo de agua — resultados

Ejecutado el 2026-11-08 según `PROTOCOLOS_PERFILES_LONGITUDINALES.md` (F1 + Enmienda 1, publicada antes de calcular). Código: `perfiles_extraer.py`, `f1_filo_de_agua_analisis.py`. Datos: `f1_tramos.csv` (tramos), `f1_resultados.json` (cifras). Es un **cribado de prefactibilidad**, no un inventario de potencial.

## Resultado principal (tramos de 2 km, análisis preregistrado)
- 257 perfiles extraídos; 1 excluido por menos de 120 meses de caudal; **256 cuencas analizadas**, 10.347 tramos.
- Solo el **41,3 %** de los tramos es utilizable (pendiente sobre el piso del DEM de 90 m); 199 de 256 cuencas tienen al menos un tramo utilizable en el rango de escalamiento de caudal (A(x)/A_est ≥ 0,25).
- **Cuencas con al menos un tramo candidato** (potencia bruta ≥ 100 kW con Q mínimo —percentil 10 mensual— tanto con k = 1 como con k = 0,8): **68,4 %** (IC 95 % por bloques de 1°: 56,2 – 79,1). Por región: Andina 81,8 %, Orinoquía-Amazonía 54,5 %, Caribe 27,6 %.
- 1.357 tramos candidatos; mediana de caída 48 m y de Q_p10 de la estación 7 m³/s.
- Mediana, por cuenca, de la mayor potencia bruta con Q_p10: 2.751 kW (IC 95 %: 1.494 – 3.798).

## Sensibilidad (preregistrada)
| Tamaño de tramo | Cuencas con candidato | IC 95 % | Tramos candidatos (rango A ≥ 0,25 / ≥ 0,05) |
|---|---|---|---|
| 1 km | 75,4 % | 65,2 – 84,6 | 2.673 / 5.005 |
| 2 km | 68,4 % | 56,2 – 79,1 | 1.357 / 2.622 |
| 5 km | 62,2 % | 50,8 – 72,1 | 578 / 1.123 |

La conclusión cualitativa no cambia con el tamaño de tramo ni con ampliar el rango de escalamiento.

## Lo que esto sí y no dice
- **Sí:** coherente con la hipótesis de que las caídas concentradas están en cuencas andinas; la diferencia Andina vs. Caribe es grande y sus ICs no se solapan en lo esencial. Parte de esa diferencia es mecánica (más pendiente y más caída), no un hallazgo independiente.
- **El umbral de 100 kW es permisivo**: se alcanza con 1 m³/s y 10 m de caída. Que 68 % de las cuencas tengan un candidato dice poco de aprovechabilidad.
- **Los candidatos de mayor potencia no son «pequeñas centrales»**: los 10 primeros (hasta ~300 MW brutos) están en estaciones con Q_p10 de 130 – 420 m³/s, y 6 de los 10 son tramos distintos de la misma estación (no son independientes). Los umbrales legales de pequeña central no se aplicaron porque no están verificados en texto.
- **Exploratorio, no preregistrado (post hoc):** restringiendo a caudal escalado entre 0,5 y 20 m³/s y caída ≥ 20 m por tramo de 2 km quedan 927 tramos en 133 cuencas (118 andinas, 13 caribes, 2 de Orinoquía-Amazonía); potencia bruta mediana 2,1 MW, p90 6,0 MW; 110 cuencas con al menos un tramo ≥ 1 MW. Se reporta como hipótesis a validar, no como resultado.

## Limitaciones
1. Caudales **mensuales**: el percentil 10 mensual sobrestima el caudal firme frente a un Q95 diario (sesgo favorable a la hipótesis).
2. Los caudales solo existen en la estación; hacia aguas arriba se escalan por área (exponente 1 y 0,8) sin validación.
3. DEM de 90 m: el 59 % de los tramos queda fuera por estar en el piso; la caída bruta de los demás es una aproximación.
4. Los perfiles son la ruta más larga hasta cada estación, no la red de drenaje; muchos afluentes de alta caída no están representados.
5. Algunas estaciones pueden estar aguas abajo de embalses o captaciones existentes, que alteran Q_p10; no se verificó.
6. Faltan caudal ecológico, derechos de agua, geología, accesos, conexión eléctrica y licenciamiento.
7. No hay validación externa (no existe en el proyecto un inventario verificado de proyectos de pequeñas centrales). Por el protocolo, los resultados se presentan como cribado.

## Siguiente paso sugerido
Verificar los umbrales legales de pequeña central (Ley 1715/2014 y normas de la UPME/CREG) antes de clasificar por potencia, y conseguir un inventario público de proyectos para validar.
