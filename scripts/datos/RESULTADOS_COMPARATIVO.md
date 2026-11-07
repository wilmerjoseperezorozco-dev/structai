# Resultados: comparación con modelos no medidos hasta ahora

Ejecutado el 2026-11-08 según [`PROTOCOLO_COMPARATIVO.md`](PROTOCOLO_COMPARATIVO.md) (commit `e0f2956`, anterior a los resultados). Scripts: `comparativo_susceptibilidad.py`, `scripts/hidro/comparativo_detectores.py`, `scripts/precios/comparativo_intervalos_costo.py`. Las diferencias se valoran frente al ruido, no solo por su signo.

## 1. Susceptibilidad a movimientos en masa (54.723 muestras, validación por grupos de departamentos, 3 réplicas)

| Modelo | AUC | Brier | Δ AUC frente a boosting (IC95 % por departamento) | Superior (Holm) |
|---|---:|---:|---|---|
| Boosting (referencia) | 0,9006 | 0,0962 | — | — |
| Regresión logística L1 | 0,8725 | 0,1018 | −0,0281 (−0,0600; −0,0104) | No (peor) |
| **Logística con splines** | 0,9076 | **0,0886** | +0,0070 (−0,0025; +0,0138) | No |
| Bosque aleatorio | 0,9042 | 0,0916 | +0,0036 (−0,0018; +0,0093) | No |
| Árboles extremadamente aleatorios | 0,9022 | 0,0922 | +0,0016 (−0,0055; +0,0090) | No |
| Perceptrón 64-32 | 0,9095 | 0,0888 | +0,0090 (+0,0017; +0,0164) | No (p Holm 0,066) |

- **Ningún modelo supera al boosting** después de corregir por comparaciones múltiples.
- **La logística con splines es no inferior al boosting** (límite inferior −0,0025 frente a un margen de −0,02) y tiene mejor puntaje de Brier: un modelo aditivo, simple y fácil de explicar alcanza lo mismo. La logística lineal sin splines sí queda peor, así que la no linealidad por capa importa, pero la complejidad extra de los árboles no.
- **Acuerdo espacial:** la correlación de rangos entre las predicciones de los modelos va de 0,84 a 0,95: producen mapas parecidos.
- Límite: el AUC de referencia (0,90) no es el 0,83 de H6, porque la validación cruzada es otra (5 grupos de departamentos y AUC agrupado).

## 2. Detectores de anomalía de caudal (400 estaciones, inyección ×2, intervalos por departamento)

| Método | AUC (×2) | Δ frente a M2 (IC95 %) | Lectura |
|---|---:|---|---|
| B0 regla de producción | 0,8562 | — | Referencia |
| M2 z con persistencia | 0,9008 | — | Mejor de los anteriores |
| M1b escala por rango intercuartílico | 0,8573 | −0,0435 (−0,0485; −0,0374) | Peor |
| **M3 AR(2)** | 0,9021 | +0,0013 (+0,0008; +0,0018) | Supera a M2 (p Holm 0,0015) pero la ganancia es mínima |
| M4 bosque de aislamiento | 0,7773 | −0,1235 (−0,1341; −0,1116) | Mucho peor |

M3 es estadísticamente mejor pero no vale el cambio (mejora en el 66 % de las estaciones, por 0,001 de AUC). M2 es no inferior a M4. **Salvedad:** el bosque de aislamiento marca valores raros en *ambas* colas y la inyección solo sube el caudal, así que su desventaja no es un veredicto general.

## 3. Intervalos de costo a 6 meses (ICOCIV-carreteras, 33 orígenes, tamaño efectivo ≈ 6)

| Método | Cobertura (nominal 0,80) | Ancho medio | Winkler |
|---|---:|---:|---:|
| Bootstrap por bloques | 0,79 | 0,071 | 0,097 |
| **Normal iid** | 0,82 | **0,061** | **0,081** |
| AR(1) con bootstrap de residuos | 0,79 | 0,073 | 0,095 |
| Simulación histórica | 0,79 | 0,075 | 0,102 |

Todos cubren de forma parecida; el más simple (normal iid) da el intervalo más estrecho. Con tamaño efectivo ≈ 6 las diferencias no son interpretables.

## Lo que se concluye
En las tres comparaciones **el método más simple que respeta la forma del problema alcanza lo que alcanzan los complejos**. Esto refuerza la conclusión de `RESULTADOS_VALOR_INFORMATIVO.md`: no se justifica gastar en modelos más pesados con esta evidencia. No se midieron redes profundas, LightGBM/XGBoost ni modelos de series de tiempo de terceros (sin las dependencias instaladas).
