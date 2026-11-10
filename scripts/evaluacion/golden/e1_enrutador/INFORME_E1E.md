# E1e: umbral de confianza y aprendizaje activo para el clasificador de dominio (issue #169)

Fecha: 2026-11-10. Sin LLM, solo lectura en Supabase.
Reproducir: `python scripts/evaluacion/golden/e1_enrutador/e1e_umbral_activo.py` (resultados en `resultados_e1e.json`).

Clasificador: embeddings MiniLM de producción + regresión logística. Regla de decisión: responder con el dominio si p_max ≥ τ; si no, rechazar hacia `normativa_general`. Test: los mismos 58 casos del E1.

## 1. Ajuste del umbral (selective classification)

τ se elige por validación cruzada sobre los datos etiquetados, minimizando un costo tipo Chow (1970): `errores de dominio + λ · rechazos de preguntas que no eran NG`, con λ = 0,35. Mandar a NG cuesta menos que mandar al motor equivocado: en el E1, NG fue aceptable en el 94 % de las sísmicas municipales, y los motores equivocados produjeron los callejones.

Barrido en test con la semilla de producción (86 ejemplos):

| τ | 0,20 | 0,30 | 0,40 | **0,50 (CV)** | 0,60 | 0,70 | 0,80 | 0,90 |
|---|---|---|---|---|---|---|---|---|
| Estricto | 53,4 % | 56,9 % | 55,2 % | 53,4 % | 48,3 % | 43,1 % | 36,2 % | 24,1 % |
| Aceptable | 60,3 % | 79,3 % | 86,2 % | 84,5 % | 81,0 % | 77,6 % | 72,4 % | 60,3 % |
| Callejones | 8 | 5 | 2 | 2 | 2 | 1 | 0 | 0 |

- **El τ elegido por CV (0,50) cae en la zona óptima del test (0,40–0,50)**: el ajuste generaliza.
- La tabla es una decisión de producto, no solo técnica. τ bajo da más respuestas especializadas pero más callejones; τ alto es más seguro pero contesta más veces con lo general. Por encima de 0,80 no hay callejones, pero el estricto se desploma.
- AURC (área bajo la curva riesgo-cobertura; menor es mejor): 0,190 con la semilla.

## 2. Aprendizaje activo (lotes de 10, 15 rondas, test intacto)

Pool: 371 preguntas con etiqueta conocida (baterías de NSR-10 y de precios + dev del E1).

| Estrategia | Estricto medio (área bajo la curva) | Aceptable medio |
|---|---|---|
| Entropía | **0,611** | **0,830** |
| Menor confianza | 0,601 | 0,829 |
| Margen | 0,551 | 0,806 |
| Margen + diversidad | 0,543 | 0,807 |
| Aleatoria (media de 5) | 0,524 | 0,819 |

Las estrategias por incertidumbre (entropía, menor confianza) superan al azar. Pero las curvas son ruidosas y **no crecen de forma sostenida**. Y etiquetar el pool completo deja al modelo en 55,2 % estricto, apenas por encima de la semilla.

## 3. El hallazgo principal: distribución por encima de cantidad

| Entrenamiento | n | τ (CV) | Estricto | Aceptable | Callejones | AURC |
|---|---|---|---|---|---|---|
| Semilla de producción | 86 | 0,50 | 53,4 % | 84,5 % | 2 | 0,190 |
| + **38** preguntas del tipo de uso real (dev E1) | 124 | 0,45 | **79,3 %** | **89,7 %** | 1 | **0,047** |
| + **333** de las baterías (NSR-10 y precios) | 419 | 0,70 | 43,1 % | 75,9 % | 2 | 0,172 |
| + las 371 | 457 | 0,70 | 55,2 % | 77,6 % | 1 | 0,078 |

- **38 etiquetas representativas valen más que 333 de otra distribución, y estas últimas empeoran el modelo.** El pool de baterías es 63 % `normativa_general` y casi no tiene vías, gerencia ni agua (2 a 4 preguntas cada uno). El modelo aprende ese sesgo: τ sube a 0,70 y rechaza más.
- Es la misma conclusión de la auditoría de evaluación (#109): las baterías de StructAI son casi solo NSR-10. Sirven para medir la NSR-10, no para entrenar un enrutador.
- **Inconsistencia de política.** El pool etiquetó el Título A como NG y el test etiquetó Aa/Av como geopot. Por eso se escribió `docs/evaluacion/GUIA_ETIQUETADO_DOMINIO.md`, alineada con la nueva taxonomía de `FUENTES_DOMINIO` (commit 1543fbb).
- **Límite:** dev y test comparten autor y estilo, aunque no comparten plantilla. Los +26 puntos del dev son, por tanto, un techo optimista. La confirmación sigue siendo el held-out de otra persona.

## 4. Qué queda operativo

`aprendizaje_activo.py` implementa el ciclo con el pool correcto, **las consultas reales** de `consultas_history`, más preguntas de colegas si se pasan con `--extra`:

```
python aprendizaje_activo.py seleccionar --n 20        # entropía + diversidad -> _privado/por_etiquetar_FECHA.csv
python aprendizaje_activo.py incorporar _privado/por_etiquetar_FECHA.csv   # valida y agrega al almacén
python aprendizaje_activo.py estado
```

- Primera corrida (2026-11-10): pool de 53 consultas reales; eligió 10, todas con confianza entre 0,21 y 0,73 (9 bajo el umbral). Son las que más le enseñan al modelo.
- Las consultas reales y sus etiquetas viven en `_privado/` (en `.gitignore`): pueden contener datos de usuarios.
- Cada ciclo reentrena y reajusta τ con todo lo etiquetado.

## Recomendación

1. **Clasificador de producción candidato:** K6 (keyword → MiniLM + regresión logística con τ por CV), entrenado con la semilla + E1 + las consultas reales que se vayan etiquetando. No con las baterías.
2. **Ritmo:** un ciclo de aprendizaje activo de 20 consultas por mes, o cada 100 consultas nuevas, siguiendo la guía.
3. **τ como parámetro de producto**, documentado y revisable (tabla de la sección 1). Con el costo λ = 0,35, el valor actual es 0,45–0,50.
4. **Integración** solo después del held-out de otra persona: IC que no cruce 0 frente a producción y sin regresión en `test_rag_motores_regresion.py`.

## Referencias

- Chow, C. K. (1970). On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory*, 16(1), 41–46.
- Settles, B. (2009). *Active Learning Literature Survey*. Computer Sciences Technical Report 1648, University of Wisconsin–Madison.
- Geifman, Y. y El-Yaniv, R. (2017). Selective Classification for Deep Neural Networks. *NeurIPS 2017* (curva riesgo-cobertura).
