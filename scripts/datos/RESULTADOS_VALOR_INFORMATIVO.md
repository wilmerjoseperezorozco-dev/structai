# Resultados P0-P1: valor informativo y costo de los datos

Ejecutado el 2026-11-08 según [`PROTOCOLO_VALOR_INFORMATIVO.md`](PROTOCOLO_VALOR_INFORMATIVO.md) (commit `bd60961`, anterior a los resultados). Scripts: `registro_costos.py`, `p1_estaciones.py`, `p1_susceptibilidad.py`. Los ahorros son de estos conjuntos de datos y estos análisis, no una garantía general.

## P0 — costo real de lo que almacenamos
Ver [`REGISTRO_COSTOS.md`](REGISTRO_COSTOS.md). Local ≈ 1,2 GB (581 MB en `scripts/precios/_cache`, en su mayoría copias en JSON de tablas que ya están en la base; 307 MB en `scripts/satelite/_cache`). Producción ≈ 441 MB en las tablas principales. A esta escala el almacenamiento no es un cuello de botella; el ahorro importaría al escalar a rásteres de todo el país.

## P1 — frontera costo-utilidad (menor fracción del costo con no inferioridad)

| Banco | Pregunta y margen | Aleatoria | Estratificada por departamento | Cobertura espacial / adelgazamiento |
|---|---|---:|---:|---:|
| A. Curva de crecimiento (130 estaciones) | Error ≤ 5 % en x_25 y x_100 | 100 % | 50 % | 100 % |
| B. Conclusión C2 de anomalías (402 estaciones) | Estimación ±20 % e IC > 0 en ≥ 95 % de sorteos | 25 % | **5 %** | 10 % |
| C. Susceptibilidad (54.723 filas de entrenamiento) | ΔAUC con límite inferior > −0,01 | 25 % | 25 % | 25 % |

Banco C, ΔAUC frente a los datos completos (AUC espacial de referencia 0,9006; no es el 0,83 de H6, porque la validación cruzada es otra): con el 10 % de las filas, −0,0091 (aleatoria), −0,0069 (estratificada) y −0,0122 (adelgazamiento), ninguna no inferior; con el 25 %, −0,0020, −0,0009 y +0,0003, todas no inferiores. **El adelgazamiento por celdas no mejora a la selección aleatoria.**

Exploratorio, banco A: con un margen de 10 % la aleatoria necesita el 50 % del costo y con 20 %, el 25 %. La elección de δ cambia mucho el ahorro.

### C′ — ablación de capas (datos completos)

| Se quita | ΔAUC (IC95 %) | Lectura |
|---|---|---|
| Relieve | −0,0485 (−0,0692; −0,0323) | Aporta mucho |
| Geología | −0,0153 (−0,0261; −0,0044) | Aporta |
| Cobertura del suelo | −0,0104 (−0,0174; −0,0056) | Aporta |
| Lluvia anual | −0,0013 (−0,0113; +0,0111) | **Inconcluso**: el efecto puntual es casi nulo, pero el intervalo no alcanza el margen de −0,01, así que no se puede afirmar que sea prescindible |

La lluvia es la capa más cara de obtener (descarga de CHIRPS, unas 3,5 h para el periodo diario), y es la candidata a prescindir si un estudio con más potencia confirma que no aporta.

## Lo que sostiene H-VI y lo que no
- **Sostiene:** la reducción posible depende de la pregunta (un efecto promedio se conserva con el 5 % de las estaciones; una cuantía de precisión del 5 % necesita el 50 %). Un modelo de susceptibilidad conserva su AUC con la cuarta parte de las filas.
- **No sostiene:** que haga falta un método sofisticado. Las estrategias simples ya logran lo posible en B y C. Los márgenes de A y B no tienen la misma exigencia, así que su comparación directa es indicativa.
- **Banco D (normas del RAG):** no se ejecutó (P1c).

## Puerta hacia aprendizaje por refuerzo — resultado y enmienda

**Resultado literal.** La puerta pedía que el oráculo permitiera, en A **y** B, una fracción de costo al menos 10 puntos menor que la mejor estrategia sin etiqueta. En A: oráculo 2 % frente a 50 % (48 puntos). En B: oráculo 2 % frente a 5 % (3 puntos). **La puerta no se cumple** y P2 y P3 no se justifican con esta evidencia.

**Enmienda 1 (posterior a los resultados, declarada).** La puerta tenía un defecto de diseño además de no cumplirse: un oráculo que ve la respuesta no es alcanzable por ningún selector real, así que mide un techo teórico y no una oportunidad de aprendizaje. Una puerta informativa debe exigir que un selector *entrenado en algunas tareas* supere a las líneas base en tareas *no vistas* (validación dejando una tarea fuera). Para eso hacen falta al menos tres tareas distintas con referencia completa; hoy hay tres bancos, pero con unidades de selección y márgenes distintos, así que antes habría que homogeneizarlos. Hasta entonces la conclusión es que **las líneas base simples bastan**.
