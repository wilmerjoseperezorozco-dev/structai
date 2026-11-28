# Resultados de la fase 2: índice local vs RPC

Generado por `analizar_fase2.py` según `docs/evaluacion/PREREGISTRO_INDICE_LOCAL.md`. Bootstrap de pares: 10000 réplicas, semilla 20261116. Población: 138 preguntas, 12 sin efecto (prompt idéntico), 126 generadas en los dos modos.

Generaciones rechazadas con 413 (cuentan como no aprobadas en la tabla principal): 5 en modo local, 6 en modo rpc.

## con 413 como no aprobada (principal)

| Grupo | n | Local ✓ [Wilson] | RPC ✓ [Wilson] | solo local / solo RPC | p McNemar | Local − RPC [IC95 boot] | Efecto mín. detectable (80 %) | Decisión |
|---|---|---|---|---|---|---|---|---|
| todas (generadas) | 126 (+0 sin efecto) | 115 = 91.3 % [85.0 %–95.1 %] | 114 = 90.5 % [84.1 %–94.5 %] | 3 / 2 | 1.000 | +0.8 pts [-2.4, +4.8] | ±5.0 pts | no se detecta diferencia con este n |
| todas (batería total) | 126 (+12 sin efecto) | 115 = 91.3 % [85.0 %–95.1 %] | 114 = 90.5 % [84.1 %–94.5 %] | 3 / 2 | 1.000 | +0.7 pts [-2.2, +3.6] | ±4.5 pts | no se detecta diferencia con este n |
| nsr10 (generadas) | 120 (+0 sin efecto) | 109 = 90.8 % [84.3 %–94.8 %] | 108 = 90.0 % [83.3 %–94.2 %] | 3 / 2 | 1.000 | +0.8 pts [-2.5, +4.2] | ±5.2 pts | no se detecta diferencia con este n |
| nsr10 (batería total) | 120 (+5 sin efecto) | 109 = 90.8 % [84.3 %–94.8 %] | 108 = 90.0 % [83.3 %–94.2 %] | 3 / 2 | 1.000 | +0.8 pts [-2.4, +4.0] | ±5.0 pts | no se detecta diferencia con este n |
| motores (generadas) | 6 (+0 sin efecto) | 6 = 100.0 % [61.0 %–100.0 %] | 6 = 100.0 % [61.0 %–100.0 %] | 0 / 0 | 1.000 | +0.0 pts [+0.0, +0.0] | — (sin pares discordantes) | no se detecta diferencia con este n |
| motores (batería total) | 6 (+7 sin efecto) | 6 = 100.0 % [61.0 %–100.0 %] | 6 = 100.0 % [61.0 %–100.0 %] | 0 / 0 | 1.000 | +0.0 pts [+0.0, +0.0] | — (sin pares discordantes) | no se detecta diferencia con este n |

## sin los pares con 413

| Grupo | n | Local ✓ [Wilson] | RPC ✓ [Wilson] | solo local / solo RPC | p McNemar | Local − RPC [IC95 boot] | Efecto mín. detectable (80 %) | Decisión |
|---|---|---|---|---|---|---|---|---|
| todas (generadas) | 119 (+0 sin efecto) | 113 = 95.0 % [89.4 %–97.7 %] | 113 = 95.0 % [89.4 %–97.7 %] | 1 / 1 | 1.000 | +0.0 pts [-2.5, +2.5] | ±3.3 pts | no se detecta diferencia con este n |
| todas (batería total) | 119 (+12 sin efecto) | 113 = 95.0 % [89.4 %–97.7 %] | 113 = 95.0 % [89.4 %–97.7 %] | 1 / 1 | 1.000 | +0.0 pts [-2.3, +2.3] | ±3.0 pts | no se detecta diferencia con este n |
| nsr10 (generadas) | 113 (+0 sin efecto) | 107 = 94.7 % [88.9 %–97.5 %] | 107 = 94.7 % [88.9 %–97.5 %] | 1 / 1 | 1.000 | +0.0 pts [-2.7, +2.7] | ±3.5 pts | no se detecta diferencia con este n |
| nsr10 (batería total) | 113 (+5 sin efecto) | 107 = 94.7 % [88.9 %–97.5 %] | 107 = 94.7 % [88.9 %–97.5 %] | 1 / 1 | 1.000 | +0.0 pts [-2.5, +2.5] | ±3.4 pts | no se detecta diferencia con este n |
| motores (generadas) | 6 (+0 sin efecto) | 6 = 100.0 % [61.0 %–100.0 %] | 6 = 100.0 % [61.0 %–100.0 %] | 0 / 0 | 1.000 | +0.0 pts [+0.0, +0.0] | — (sin pares discordantes) | no se detecta diferencia con este n |
| motores (batería total) | 6 (+7 sin efecto) | 6 = 100.0 % [61.0 %–100.0 %] | 6 = 100.0 % [61.0 %–100.0 %] | 0 / 0 | 1.000 | +0.0 pts [+0.0, +0.0] | — (sin pares discordantes) | no se detecta diferencia con este n |

La regla de decisión se aplica a la fila **todas (batería total)** de la tabla principal: IC95 entero > 0 → mejora; cruza 0 → no se detecta diferencia (no se afirma equivalencia); entero < 0 → regresión y se revierte con `RAG_INDICE_LOCAL=false`.
