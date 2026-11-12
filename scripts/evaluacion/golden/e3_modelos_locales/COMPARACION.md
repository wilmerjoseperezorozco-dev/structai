# Comparación de modelos locales (#172)

Criterio prerregistrado: ver el docstring de `comparar_modelos.py`. Casos pareados (presentes en todos): **38**.

| Modelo | Pasa | Tasa | Wilson IC95 | Bootstrap por título IC95 | Latencia p50 | Origen de filas |
|---|---|---|---|---|---|---|
| qwen2.5:7b | 38/38 | 100.0% | 90.8%–100.0% | 100.0%–100.0% | 144 s | {'ctx16384': 9, 'ctx8192_sin_truncar': 129, 'excluidos_truncados_8k': 0} |
| llama3:8b | 34/38 | 89.5% | 75.9%–95.8% | 81.8%–100.0% | 91 s | {'ctx16384': 0, 'ctx8192_sin_truncar': 38, 'excluidos_truncados_8k': 0} |
| hermes3:latest | 34/38 | 89.5% | 75.9%–95.8% | 73.9%–100.0% | 116 s | {'ctx16384': 0, 'ctx8192_sin_truncar': 38, 'excluidos_truncados_8k': 0} |

Candidato (mayor tasa): **qwen2.5:7b**

| Rival | Solo candidato acierta | Solo rival acierta | p McNemar | p Holm | ¿Se distingue? |
|---|---|---|---|---|---|
| llama3:8b | 4 | 0 | 0.1250 | 0.2500 | no |
| hermes3:latest | 4 | 0 | 0.1250 | 0.2500 | no |

**Empate estadístico** entre qwen2.5:7b, llama3:8b, hermes3:latest. Regla de desempate: el más barato a <= 3% del candidato (qwen2.5:7b) → se elige **qwen2.5:7b** (100.0%, 144 s por caso).
