# Validación del motor de redes (#138) contra EPANET y casos publicados

Fecha: 2026-11-09. Código: `packages/motor-redes`. Tests: `tests/test_validacion_epanet.py`.

## Qué se verificó, con qué y cuánto coincide

| Caso | Fuente | Qué se compara | Resultado medido |
|---|---|---|---|
| `todinitest` (5 nudos, 7 tuberías, 1 embalse, LPS) | OpenWaterAnalytics/epanet-example-networks; salida de regresión de EPANET 2.2.0-dev | Caudales de las tuberías 1 y 2 | 50,27163 y 49,72837 LPS frente a 50,2716 y 49,7284: coinciden a los 4 decimales publicados |
| Net1 en t = 0 (bomba de un punto, tanque a carga fija, 9 nudos) | `Net1.inp` de OpenWaterAnalytics/EPANET (MIT); salida de regresión de EPANET 2.2.0-dev | Cargas en 9 nudos, caudal de bomba, caudales de 6 tuberías | Carga: diferencia máxima 0,0082 ft. Caudal de bomba 1865,02 gpm frente a 1865,08 (0,003 %) |
| Net1: balance y curva de bomba | Cálculo propio | Σ demandas (950 gpm) = bomba + tanque; H de la bomba sobre la parábola de un punto | Exacto a 1e-9 |

La diferencia residual de las cargas se explica por la constante de Hazen-Williams: el motor usa 10,67 (SI) y EPANET usa 4,727 en unidades inglesas, que equivale a 10,6669 (0,03 % menos). Está verificada en un test.

## Límites de esta validación (importante)

- Es una comparación contra **otro solver**, no contra una publicación revisada por pares. Si ambos compartieran un error de concepto, no se vería.
- Los valores esperados son salidas de regresión de EPANET 2.2.0-dev (2018) sobre una variante de Net1 con duración 0, no la corrida de 24 h del manual. **No se verificó** el periodo extendido de 24 h contra valores publicados.
- El repositorio `epanet-example-networks` no tiene licencia: sus archivos no se redistribuyen; solo se citan los números y la topología mínima de dos redes.
- **No se encontraron ni verificaron** valores publicados para Net2, Net3, Hanoi, Anytown, Two-loop, Fossolo, Pescara ni Battle of the Water Networks; no se usa ninguno.
- Golpe de ariete: no se pudieron abrir los ejemplos numéricos de Wylie y Streeter ni de Chaudhry. La validación del ariete es contra la solución analítica de cierre instantáneo sin fricción (Joukowsky, periodo 4L/a), que es exacta.

## Pendiente que sí es validable

1. `test_pda.cpp` de EPANET (MIT): Net1 con demanda ×10 y análisis dirigido por presión (20–100 psi, exponente 0,5): 32,66 % de reducción de demanda y déficit 413,67 en el nudo 21. Requiere implementar demanda dependiente de presión, que el motor no tiene.
2. `test_valve.cpp`: pérdida de 0,0255 ft en la PCV de Net1 al 35 % de apertura; requiere válvula PCV (coeficiente relativo de apertura), distinta de la válvula de K constante actual.
3. Net1 de 24 h con tanque variable y controles de bomba, cuando se tengan valores verificables.
4. Biblioteca de 44 problemas (Mendonça y Gamboa Medina, Rev. Bras. Recursos Hídricos 30, e18, 2025) y WDST de la Universidad de Kentucky: localizadas, no abiertas.

## Novedades de la literatura (sin replicar; ideas, no resultados nuestros)

- EPANET 2.3.x: PDA con mejor convergencia, corrección del gradiente de pérdida a bajo caudal, prevención de salida de tanques vacíos.
- arXiv:2609.06323 (Mu et al., 2026): gradiente global diferenciable con jacobiano por adjunto y escenarios en lote; afirman diferencia máxima de 1,1e-13 ft frente a EPANET 2.2 en 52 redes. Es una afirmación de los autores.
- Una corrección análoga a la de bajo caudal de EPANET 2.3 es la que este motor resolvió con el piso `_Q_MIN` y el criterio de paso de Newton.
