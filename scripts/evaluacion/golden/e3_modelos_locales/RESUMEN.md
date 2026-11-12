# Modelos locales en las baterías de StructAI (#172)

| Modelo | Batería | n | Pasa | Hecho | Enruta | Alucinación num. | Latencia p50 / p95 | tok/s | Truncados | Errores |
|---|---|---|---|---|---|---|---|---|---|---|
| hermes3:latest (ctx 8192) | motores | 13 | 13/13 | 13/13 | 13/13 | 0 | 90s / 187s | 5.4 | 0 | 0 |
| hermes3:latest (ctx 8192) | nsr10 | 25 | 21/25 | 21/25 | — | 0 | 127s / 232s | 4.5 | 0 | 0 |
| llama3:8b (ctx 8192) | motores | 13 | 11/13 | 11/13 | 13/13 | 0 | 77s / 111s | 6.2 | 0 | 0 |
| llama3:8b (ctx 8192) | nsr10 | 25 | 23/25 | 23/25 | — | 0 | 96s / 239s | 4.9 | 0 | 0 |
| qwen2.5:14b (ctx 8192) | motores | 13 | 13/13 | 13/13 | 13/13 | 0 | 185s / 350s | 2.8 | 0 | 0 |
| qwen2.5:14b (ctx 8192) | nsr10 | 25 | 24/25 | 24/25 | — | 0 | 212s / 469s | 2.4 | 0 | 0 |
| qwen2.5:7b (ctx 8192) | motores | 13 | 13/13 | 13/13 | 13/13 | 0 | 132s / 230s | 5.1 | 0 | 0 |
| qwen2.5:7b (ctx 8192) | nsr10 | 125 | 106/125 | 106/125 | — | 4 | 122s / 221s | 5.8 | 0 | 0 |
| qwen2.5:7b (ctx 16384) | motores | 1 | 1/1 | 1/1 | 1/1 | 0 | 213s / 213s | 5.7 | 0 | 0 |
| qwen2.5:7b (ctx 16384) | nsr10 | 9 | 9/9 | 9/9 | — | 0 | 302s / 452s | 3.2 | 0 | 0 |
