# Clasificador por etapa v2: colegas (vivienda) + EPC (redes) (#196)

Generado por `scripts/presupuesto/clasificador_etapas_v2.py`. TF-IDF de caracteres + regresión logística con rechazo. Sin LLM.

- Oro de colegas: 877 APU (vivienda campestre).
- EPC: **545** actividades únicas etiquetadas por su capítulo/subcapítulo de la cartilla, mapeado a la taxonomía (`MAPEO_EPC` en el script, revisable). Excluidas por ambiguas: 19 (CONCRETOS, MORTEROS, ACERO DE  / MORTEROS - SUMINISTRO 6, PLANTAS DE TRATAMIENTO DE AGUA / MATERIALES PARA FILTROS 6, PLANTAS DE TRATAMIENTO DE AGUA / ELEMENTOS EN POLIETILENO 5, RELLENOS / OBRAS DE PROTECCION (SUMINISTR 2).
- Por capítulo de la taxonomía en EPC: 0.2 4, 1.1 12, 1.2 36, 1.4 64, 1.6 6, 1.7 3, 2.1 3, 3.1 3, 3.2 4, 3.3 10, 3.5 4, 4.1 6, 4.2 15, 4.3 370, 4.4 5

| Experimento | n | Exactitud capítulo | Exactitud ETAPA | Macro-F1 | τ | Cobertura | Precisión etapa (aceptadas) |
|---|---|---|---|---|---|---|---|
| A colegas → EPC (línea base) | 545 | 8.8% | 22.8% | 0.20 | 0.6 | 3.9% | 95.2% |
| B colegas + EPC → EPC (actividad no vista) | 545 | 91.9% | 93.9% | 0.66 | 0.0 | 100.0% | 93.9% |
| B2 colegas + EPC → EPC (subcapítulo no visto) | 545 | 80.7% | 85.7% | 0.34 | 0.25 | 82.6% | 94.4% |
| v1: colegas → colegas (E1b) | 877 | 88.5% | 92.2% | 0.72 | 0.175 | 97.6% | 93.2% |
| C colegas + EPC → colegas (E1b) | 877 | 90.0% | 92.5% | 0.70 | 0.125 | 99.5% | 92.9% |

En B, las actividades de redes (4.3) se predicen como: 4.3 357, 1.4 6, 4.1 5, 3.3 2.

Criterio (fijado antes): B mejora la etapa en EPC frente a A (**+71.2%**) y C no baja más de 2 puntos la etapa en vivienda (**+0.2%**). Veredicto: **se adopta v2**.

Propuestas v2 para las 1340 actividades sin etiqueta de la base, por etapa: 0 3, 1 491, 2 208, 3 281, 4 357. Siguen sin validar en la base: hace falta la muestra etiquetada por una persona (`_privado/muestra_para_etiquetar.csv`).
