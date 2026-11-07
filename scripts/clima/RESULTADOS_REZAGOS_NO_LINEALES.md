# Resultados: relación no lineal con rezago (ONI, TNA → lluvia y temperatura del Caribe)

Ejecutado el 2026-11-08 según [`PROTOCOLO_REZAGOS_NO_LINEALES.md`](PROTOCOLO_REZAGOS_NO_LINEALES.md) (commit `e1de3d2`, anterior a los resultados). Script: `rezagos_no_lineales.py`. Lluvia: CHIRPS, 195 municipios del Caribe, 528 meses (1981-2024). Temperatura: 130 estaciones del IDEAM, 216 meses evaluables (2005-2026). Validación por 6 bloques con purga de 12 meses. Una corrección declarada: los meses sin objetivo definido dentro de una partición (menos de 5 estaciones con climatología) se excluyen del entrenamiento y de la evaluación de todos los modelos.

## Habilidad fuera de muestra (1 − MSE/MSE de la climatología)

| Objetivo, horizonte | M1 lineal | M1s lineal estacional | M2 aditivo no lineal | M3 boosting | M4 interacción ONI×TNA |
|---|---:|---:|---:|---:|---:|
| Lluvia, 1 mes | +0,103 | **+0,119** | −0,034 | +0,059 | +0,111 |
| Lluvia, 3 meses | +0,074 | +0,097 | −0,059 | +0,075 | +0,043 |
| Temperatura, 1 mes | +0,080 | +0,028 | −0,254 | −0,136 | −0,035 |
| Temperatura, 3 meses | +0,043 | −0,038 | −0,256 | −0,115 | −0,021 |

## Pruebas confirmatorias
- **Habilidad (M1s frente a climatología), Holm sobre las 4 combinaciones:** lluvia 1 mes p = 0,080; lluvia 3 meses p = 0,087; temperatura p = 0,721 en ambos. **Ninguna alcanza significancia** tras la corrección (sin corregir, la lluvia daba p = 0,020 y 0,029).
- **No linealidad (M2, M3 y M4 frente a M1s):** ningún modelo no lineal es mejor que el lineal estacional (p Holm = 1,000 en todos). La spline aditiva (M2) es **peor**: ΔMSE +0,177 con IC95 % [+0,012; +0,301] para la lluvia a 1 mes. **Conclusión preregistrada: no hay evidencia de una relación no lineal útil en estos datos.**

## Descriptivo
- **Por estación del año (lluvia, M1s):** la habilidad se concentra en junio-agosto (+0,39 a 1 mes), es moderada en diciembre-febrero (+0,14) y septiembre-noviembre (+0,17) y **negativa en marzo-mayo (−0,25)**: ahí el modelo empeora la predicción.
- **Respuesta lineal de la lluvia a 1 mes (coeficientes estandarizados por rezago):** el ONI es negativo a los rezagos 1 y 2 (−0,12, −0,18: El Niño reduce la lluvia uno o dos meses después) y el TNA es positivo al rezago 1 (+0,19: un Atlántico más cálido aumenta la lluvia al mes siguiente). Los signos coinciden con la literatura.
- **Temperatura máxima horaria del Caribe:** tendencia de **+0,26 °C por década** (IC95 % +0,03 a +0,61), por debajo del efecto mínimo detectable de ≈ 0,42 °C/década con el ruido observado: la tendencia es positiva pero **la prueba no tiene potencia suficiente** para afirmarla con seguridad.

## Qué se concluye y qué no
- Un modelo **lineal con modulación estacional** de ONI y TNA aporta una predicción modesta de la lluvia del Caribe (explica ≈ 10-12 % de la varianza mensual, concentrado en junio-agosto), no robusta tras corregir por comparaciones múltiples.
- **No** se encontró que la no linealidad, la interacción entre los dos océanos o los árboles de decisión mejoren esa predicción; con la temperatura no hay habilidad. Es coherente con los resultados negativos de H4 y H13 y con la comparación de modelos simples.
- Límites: promedios regionales (que pueden ocultar umbrales locales), anomalías en lugar de temperaturas absolutas del mar (el umbral de convección se define en valores absolutos), un solo ciclo de datos de temperatura relativamente corto, y relaciones no estacionarias. No se midieron DLNM, CCM, redes profundas ni modelos de umbral (ver `docs/investigacion/relaciones_no_lineales_con_rezago.md`).
