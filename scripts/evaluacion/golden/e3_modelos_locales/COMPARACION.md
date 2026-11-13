# Comparación de modelos locales (#172)

Criterio prerregistrado: ver el docstring de `comparar_modelos.py`. Casos pareados (presentes en todos): **137**.

| Modelo | Pasa | Tasa | Wilson IC95 | Bootstrap por título IC95 | Latencia p50 | Origen de filas |
|---|---|---|---|---|---|---|
| qwen2.5:7b | 127/137 | 92.7% | 87.1%–96.0% | 88.3%–98.9% | 122 s | {'ctx16384': 10, 'ctx8192_sin_truncar': 128, 'excluidos_truncados_8k': 0} |
| llama3:8b | 113/137 | 82.5% | 75.3%–87.9% | 76.1%–90.2% | 107 s | {'ctx16384': 138, 'ctx8192_sin_truncar': 0, 'excluidos_truncados_8k': 0} |
| hermes3:latest | 112/137 | 81.8% | 74.4%–87.3% | 73.5%–94.5% | 142 s | {'ctx16384': 137, 'ctx8192_sin_truncar': 0, 'excluidos_truncados_8k': 0} |

Candidato (mayor tasa): **qwen2.5:7b**

| Rival | Solo candidato acierta | Solo rival acierta | p McNemar | p Holm | ¿Se distingue? |
|---|---|---|---|---|---|
| llama3:8b | 18 | 4 | 0.0043 | 0.0043 | sí |
| hermes3:latest | 17 | 2 | 0.0007 | 0.0015 | sí |

**Gana qwen2.5:7b**: se distingue de todos los rivales (p_Holm < 0.05).
