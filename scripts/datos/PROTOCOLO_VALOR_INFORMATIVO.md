# Protocolo: valor informativo de subconjuntos de datos y reducción de costo (P0-P1)

Preregistrado el 2026-11-08, antes de ejecutar. Línea de investigación de arquitectura de datos del programa StructAI.

## Hipótesis (falsable)
**H-VI.** Para fenómenos dados, un subconjunto S de los datos (estaciones, muestras, capas, fragmentos normativos) reproduce las conclusiones científicas preregistradas de los datos completos con un costo C(S) menor, y la reducción posible depende de la escala del fenómeno (mayor para fenómenos regionales que para locales, por la dependencia espacial medida en `RESULTADOS_COHERENCIA.md`). Un modelo de aprendizaje por refuerzo (P3) solo se evalúa si supera a las líneas base simples (puerta de P2/P3, abajo).

## Definiciones
- **Utilidad U(S):** retención de la conclusión de un experimento ya ejecutado con datos completos (la referencia).
- **Rigor preservado = no inferioridad:** margen δ fijado abajo antes de correr; se declara «no inferior» solo si el criterio se cumple con el intervalo, no con la estimación puntual.
- **Costo C(S):** fracción de filas y de bytes del conjunto completo, más tiempo de procesamiento medido. El «x %» es un resultado: 1 − (menor fracción de costo con la que se cumple no inferioridad), con su incertidumbre.
- **Selección sin etiqueta:** las estrategias de P1 no usan el desenlace para elegir (evita inferencia selectiva). La única excepción es el *oráculo* del banco A y B, que se usa solo como cota superior del margen.

## P0 — registro de costos
Inventario reproducible de lo que se almacena y procesa hoy: bytes locales por carpeta (sin `node_modules` ni `.git`), tamaño en producción de las tablas del corpus (datos, vectores e índices) y tiempos de procesamiento registrados (por ejemplo, la descarga diaria de CHIRPS). Salida: `REGISTRO_COSTOS.md`.

## P1 — frontera costo-utilidad con líneas base simples
Fracciones de costo evaluadas: 2, 5, 10, 25, 50 y 100 %. Estrategias (todas sin etiqueta):
- **E1 aleatoria**, **E2 estratificada por departamento** (proporcional) y **E3 cobertura espacial** (muestreo del punto más lejano por latitud y longitud en estaciones; adelgazamiento por celdas de 0,1° en muestras).

| Banco | Datos | Utilidad y margen δ | Réplicas |
|---|---|---|---|
| **A** curva de crecimiento | 132 estaciones limpias (§ ítem 5) | Error relativo del x_T mediano en T = 25 y 100 frente a la curva completa. No inferior si el percentil 95 del error absoluto ≤ 5 % (δ_A) | 200 sorteos por fracción para E1 y E2; E3 es determinista |
| **B** detección de anomalías | 402 estaciones (`anomalias_por_estacion.csv`) | La conclusión C2 (M2 − M1 en AUC) se conserva: estimación dentro de ±20 % de la completa (δ_B) y IC95 % por departamento que excluye 0, en ≥ 95 % de los sorteos | 200 |
| **C** susceptibilidad (H6) | 54.723 muestras con 7 capas; GBM con validación cruzada dejando fuera departamentos (5 grupos) | AUC espacial del modelo con todas las capas. No inferior si el límite inferior del IC95 % de (AUC_subconjunto − AUC_completo) > −0,01 (δ_C); IC por remuestreo de departamentos | 3 particiones |
| **C′** ablación de capas | Las mismas muestras, quitando cada grupo de capas (relieve, geología, cobertura, lluvia) | Mismo criterio δ_C: ¿qué capas son prescindibles? | 3 |
| **D** normas del RAG | Fragmentos del índice | recall@10 y soporte de citas con el índice podado; δ_D = −0,02 en recall@10 | **P1c, no se ejecuta hoy**: requiere rehacer la recuperación con identificadores de fragmento y vectores |

**Oráculo (solo A y B).** Selección voraz que usa la respuesta completa para fijar la cota superior de lo lograble a cada fracción.

## Puerta de P2 y P3
Se justifican el bandido contextual (P2) y el refuerzo (P3) únicamente si el oráculo permite, en A **y** B, una fracción de costo no inferior al menos 10 puntos porcentuales menor que la mejor estrategia sin etiqueta (hay margen que aprender). Si no, la conclusión es que las líneas base simples ya alcanzan lo posible y no se avanza.

## Qué no se concluye
Que una estrategia de selección sea válida para otros fenómenos ni para otros periodos; estos bancos no varían la ventana temporal. Un ahorro medido aquí es de este conjunto de datos y este análisis, no una garantía general. Los resultados nulos se publican.
