# E1b + E1c: qué enrutador le sirve a StructAI (issue #169)

Fecha: 2026-11-10. Sin LLM, solo lectura en Supabase, sin cambios en producción.
Reproducir:

```
python scripts/evaluacion/golden/e1_enrutador/e1b_clasificadores.py
python scripts/evaluacion/golden/e1_enrutador/e1c_corpus.py
```

Mismo test que el E1 (58 preguntas, 7 estratos). Los parámetros se ajustaron con dev o con validación cruzada sobre el entrenamiento. McNemar exacto contra producción, Holm sobre las 8 comparaciones.

## Resultados (test, n = 58)

| Familia | Variante | Estricto | Aceptable [IC95] | Callejón | p Holm |
|---|---|---|---|---|---|
| Producción | V1 keyword → centroides | 55,2 % | 70,7 % [58–81] | 6 | — |
| Rechazo | V3 V1 + margen δ = 0,18 | 56,9 % | 86,2 % [75–93] | 2 | 0,094 |
| Clasificador (E1b) | C3 MiniLM + regresión logística con rechazo | 82,8 % | 84,5 % [73–92] | 3 | 0,29 |
| Corpus (E1c) | K1 voto de los top-10 de la búsqueda | 34,5 % | 67,2 % [54–78] | 1 | 1,0 |
| | K2 K1 + rechazo ρ = 0,4 | 32,8 % | 67,2 % | 1 | 1,0 |
| | K3 jerárquico: país → precio → K2 | 43,1 % | 77,6 % [65–86] | 1 | 1,0 |
| | K4 keyword → K3 | 51,7 % | 86,2 % [75–93] | 1 | 0,29 |
| | K5 acuerdo K3 + C3, si no NG | 44,8 % | 79,3 % | 1 | 1,0 |
| **Post hoc** | **K6 keyword → C3** | **84,5 %** | **86,2 %** [75–93] | 2 | 0,094 |

Techo de complementariedad: eligiendo siempre bien entre keyword y C3 se llega a 50/58 = 86,2 % estricto. K6 queda a una pregunta de ese techo.

Estricto por estrato:

| Estrato (n test) | V1 | V3 | C3 | K1 | K4 | K6 |
|---|---|---|---|---|---|---|
| S1 sísmica por municipio (18) | 17 % | 0 %¹ | 94 % | 0 %¹ | 0 %¹ | 94 % |
| S2 directa (15) | 100 % | 100 % | 87 % | 40 % | 100 % | 100 % |
| S3 coloquial (10) | 60 % | 80 % | 90 % | 60 % | 60 % | 80 % |
| S5 negación (3) | 33 % | 33 % | 33 % | 33 % | 33 % | 33 % |
| S6 confusor sísmico (5) | 20 % | 60 % | 40 % | 60 % | 60 % | 40 % |

¹ Enrutan a `normativa_general`: es aceptable (también trae el dato del SGC), pero no es el dominio especializado.

## Discusión

### 1. El enrutamiento consciente del corpus fracasa aquí, y el porqué es el hallazgo más útil

El voto del corpus (K1) es el peor de todos (34,5 % estricto); acierta solo 40 % de las preguntas *directas*. No es un problema del método, sino de **cómo está organizado el corpus**:

| Motor | Lo que dice ser (`MOTOR_LABEL`) | Lo que contiene `motor_chunks` |
|---|---|---|
| `vias` (2.816) | diseño geométrico, pavimentos, mantenimiento | 1.220 CCP-14 (puentes) + **1.145 Normas de Ensayo de Agregados** + 63 de Cemento + 143 Túneles |
| `geopot` (106) | sísmica + laboratorio de suelos, concreto y agregados | **89 de la Guía POT**; el laboratorio casi no tiene corpus |
| `gerencia` (818) | EVM y predicción de proyectos | Ley 80, Ley 1474, Ley 1150, manuales de interventoría |
| `normativa_general` | NSR-10, NTC, SG-SST | 10.909 chunks de NSR-10: domina cualquier voto por volumen |

**La taxonomía de los motores y la del corpus no coinciden.** El laboratorio de agregados vive en `vias`, así que "el concreto que me llegó parece aguado" va a vías. Por la misma razón, los centroides geopot–vías están a coseno 0,78. Es el **entrelazamiento semántico** que describe Loghmani (2026), presente en los datos y no solo en el modelo. Esto cambia la lectura de Bansal y Agarwal (2026): el enrutamiento consciente del corpus solo sirve si el corpus está particionado igual que los dominios.

### 2. Lo que sí funciona: léxico preciso + clasificador con rechazo

- Keyword es casi perfecto cuando hay vocabulario literal (S2: 100 %) y ciego cuando no lo hay (S1: 0 aciertos propios).
- C3 aprende lo contrario: generaliza en lo municipal y lo coloquial (S1 94 %, S3 90 %).
- Son complementarios, y **K6 (keyword → C3) reemplaza el respaldo por centroides por un clasificador con rechazo, con el mismo modelo MiniLM y el mismo costo.** Pasa de 55 % a 84,5 % estricto y llega casi al techo de combinar ambos.
- Es la evidencia más directa a favor de la hipótesis: el centroide único era el eslabón débil (Xu et al., 2026) y la opción de rechazo es lo que evita los errores por casi empate (Chow, 1970).

### 3. Lo que ningún enrutador resuelve

- **Negación (S5, 33 % en todos):** "no necesito el costo…", "no quiero evaluar la vivienda…". Todos los métodos ven las palabras del dominio negado. Hace falta otro mecanismo: quitar la cláusula negada antes de enrutar, o enrutar por cláusula.
- **Confusores sísmicos (S6, 20–60 %):** cortante basal, R0 o coeficiente de importancia son NSR-10 general, pero suenan a geopot o a vivienda. Son preguntas *multi-dominio* por naturaleza: un enrutador de una sola etiqueta tiene un techo aquí.
- **Callejones:** el arreglo de vivienda (commit 4e1e823) los vuelve respondibles, aunque el enrutamiento siga errado.

### 4. Límites de este análisis

- **n = 58, y con Holm sobre 8 comparaciones ninguna diferencia es significativa.** Lo único robusto es la dirección: todas las variantes con rechazo o clasificador quedan por encima de producción.
- **K6 es post hoc** (diseñada viendo los estratos del test). Hay que confirmarla en un set nuevo.
- C3 se entrenó con 124 ejemplos, entre 5 y 17 por dominio. Con más etiquetas debería mejorar, y también cambiar.
- Las etiquetas son de una sola persona. El tráfico real es mínimo (54 consultas; 3 con el método registrado).

## Recomendaciones para StructAI

1. **Candidato a integrar tras validarse: K6.** Mantener keyword primero y reemplazar los centroides por MiniLM + regresión logística con rechazo hacia `normativa_general`. El cambio vive en `motor_router_contrastivo.py`, sin tocar la interfaz de `_route_con_metodo()`. Condición: confirmarlo con unas 60 preguntas held-out de otra persona, con IC que no cruce 0 y sin regresión en `test_rag_motores_regresion.py`.
2. **Alinear la taxonomía del corpus con la de los motores, antes de cualquier enrutamiento por corpus.** Las Normas de Ensayo de agregados y cemento deberían declararse como fuente del laboratorio (geopot o un dominio "materiales") en `FUENTES_DOMINIO`. Y `MOTOR_LABEL` de gerencia debería decir que cubre contratación pública. Es el mismo tipo de brecha que la de vivienda: piezas que funcionan solas pero no encajan.
3. **E1d: negación y preguntas multi-dominio.** Enrutar por cláusula y descartar las cláusulas negadas. Evaluar enrutamiento multi-etiqueta (ya existe la ruta compuesta precio + norma) para S6.
4. **Datos:** el registro de `metodo_enrutamiento` empezó el 27/10 y desde entonces solo hay 3 consultas. Con más tráfico, ese log se convierte en el único set real no escrito por el equipo; conviene revisarlo cada mes contra este mismo protocolo.

## Referencias

- Bansal, P. y Agarwal, S. (2026). *Lightweight Query Routing for Adaptive RAG: A Baseline Study on RAGRouter-Bench*. arXiv:2604.03455.
- Xu, Y., Kang, M. y Lü, L. (2026). *A Multi-cluster Boundary Learning Method for Out-of-Scope Intent Detection via MiniLM Embedding*. arXiv:2607.07974.
- Loghmani, N. (2026). *Semantic Entanglement in Vector-Based Retrieval*. arXiv:2604.17677.
- Chow, C. K. (1970). On optimum recognition error and reject tradeoff. *IEEE Transactions on Information Theory*, 16(1), 41–46.
- Ethayarajh, K. (2019). How Contextual are Contextualized Word Representations? *EMNLP-IJCNLP 2019*.
