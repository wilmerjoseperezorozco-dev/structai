# Plan: benchmark con golden dataset y sabotaje controlado

Fecha: 2026-11-10. Estado: **propuesta, nada implementado**. Se coordina con #95 (plan maestro de evaluación) y #109 (auditoría de evaluación, `docs/AUDITORIA_EVALUACION_2026-11.md`) y no los duplica: esta es la pieza que la auditoría dejó pendiente, medir **recall de brechas y falsos positivos con verdad conocida**.

Regla de este plan: **nada toca producción** hasta tener resultados con intervalos de confianza y un criterio de aceptación fijado antes de correr. Solo se integra lo que gane.

---

## 0. Caso de origen (reproducido el 2026-11-10, solo lectura)

Pregunta real: *"¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo?"*. StructAI respondió que pertenece a Vulnerabilidad Vivienda y se abstuvo, con 0 fuentes.

Reproducción local de `_route_con_metodo()` (`packages/construdata/rag_multi_norma.py`), sin llamar al LLM:

| Pregunta | Palabras clave | Decisión | Score |
|---|---|---|---|
| ¿Cuál es la amenaza sísmica (Aa/Av) de Sincelejo? | `{}` | contrastivo → `vulnerabilidad_vivienda` | 0,557 |
| zona de amenaza sísmica de Sincelejo | `{}` | contrastivo → `vulnerabilidad_vivienda` | 0,599 |
| Cual es el Aa y Av de Sincelejo | `{}` | contrastivo → `gerencia` | **0,249** |
| ¿Qué Aa tiene Montería según la NSR-10? | `{}` | ninguno → normativa_general | 0,536 |
| aceleración pico efectiva de Sincelejo | `{}` | contrastivo → `geopot` (correcto) | 0,401 |

La falla tiene cuatro capas, y cada una es un tipo de caso del benchmark:

1. **Palabras clave:** no hay entrada para "amenaza sísmica" ni "Aa/Av" sueltos (solo existen la frase exacta `"aa av fa fv"` y "zona sísmica").
2. **Contrastivo sin umbral ni margen** (`motor_router_contrastivo.py`): acepta `gerencia` con 0,249, y elige `vulnerabilidad_vivienda` con solo 0,085 de ventaja sobre `normativa_general`.
3. **El dato existía.** El enriquecimiento SGC en vivo (1.122 municipios, Aa/Av oficiales) solo se activa si el motor es `geopot` o `aquai`. El enrutamiento lo bloqueó.
4. **Abstención engañosa:** el mensaje dice "el corpus no tiene contenido", pero la causa real fue el enrutamiento. El sistema no distingue entre *no lo tengo* y *lo busqué en el lugar equivocado*.

Este caso entra como **caso de regresión #1** (categoría L3, confusión de motor) y como primer experimento (sección 6, E1). No se corrige en producción hasta medir.

---

## 1. Dos tareas distintas, que hoy se miden mezcladas

| | T1: Chat (pregunta → respuesta) | T2: Auditoría de documento contra lista de control |
|---|---|---|
| Entrada | Pregunta | Documento (memoria, especificación, tabla) + checklist normativo |
| Salida | Respuesta con fuentes | Lista de hallazgos `{ítem, tipo, ubicación, evidencia}` |
| Dónde se sabotea | En el **índice**: se quita, altera o fragmenta el chunk que tiene la respuesta | En el **documento**: se omite o contradice un dato |
| Verdad conocida | Valor y numeral esperados, o abstención esperada | Lista exacta de brechas inyectadas |

El sabotaje controlado sirve para las dos. T2 es la tarea de "extracción + comparación lógica contra una lista de control".

---

## 2. Golden dataset

### 2.1 Semillas: documentos correctos

Se priorizan semillas donde **la verdad se puede calcular**, no solo opinar:

| Semilla | Formato | Oráculo |
|---|---|---|
| NSR-10 Tabla A.2.3-2 (Aa/Av por ciudad) + Apéndice A-4 | tabla, sub-tabla | Texto verbatim de `nsr10_chunks` + servicio SGC |
| NSR-10 A.2.4 (Fa/Fv por perfil de suelo) + A.2.6 (espectro) | tabla + ecuación | Recálculo determinista |
| NSR-10 C.9.3 / C.21 (factores φ, R0) | factor escalar | Verbatim |
| Memorias generadas por `motor-concreto`, `motor-redes`, `motor-aquai` | mixto, algoritmo | El propio motor (motor-redes ya validado contra EPANET) |
| Res. 0330 consolidada (SUDS 30 %, art. 2017 vs 2021) | texto normativo | `scripts/ingesta/res0330/res0330_consolidada.json` |

Una memoria generada por un motor con pruebas es **correcta por construcción**, y el motor calcula qué cambia al sabotearla.

### 2.2 Lista de control, atómica por semilla

```json
{"item_id": "A.2.3-2/Sincelejo/Aa", "requisito": "Aa de Sincelejo", "numeral": "NSR-10 Tabla A.2.3-2",
 "tipo_dato": "tabla", "valor": 0.10, "unidad": "g", "tolerancia": 0.0, "obligatorio": true}
```
`tipo_dato` ∈ {tabla, sub_tabla, ecuacion, factor, algoritmo, texto, unidad, referencia}.

### 2.3 Operadores de sabotaje (deterministas, con semilla y diff guardado)

**Omisión:** el sistema debe detectar que falta algo.
- `OM-FILA`: borrar una fila de tabla. `OM-CELDA`: vaciar una celda.
- `OM-ECU`: borrar una ecuación, o un término de ella.
- `OM-FACTOR`: borrar φ, R0, I, Fa…
- `OM-PASO`: borrar un paso de un algoritmo o procedimiento.
- `OM-UNIDAD`: dejar el número y quitar la unidad.
- `OM-REF`: quitar la cita del numeral.

**Contradicción:** el sistema debe detectar que choca con la norma.
- `CT-VALOR`: valor fuera de norma (Aa 0,10 → 0,25; φ 0,65 → 0,90).
- `CT-UNIDAD`: kN ↔ kgf, MPa ↔ kgf/cm² sin convertir.
- `CT-DESIG`: invertir ≥ ↔ ≤.
- `CT-FILA`: tomar el valor de la fila vecina (otra ciudad, otro perfil de suelo).
- `CT-VERSION`: norma derogada (Res. 0330 SUDS 25 % vs 30 %; E.030 2019 vs 2026).
- `CT-NEG`: invertir una negación ("no requiere" ↔ "requiere").

El enrutador contrastivo **no sirve como oráculo** de contradicción. Clasifica dominio, no verifica valores. La verdad sale del checklist más el motor o la tabla verbatim.

**Controles (miden falsos positivos):** el sistema debe decir "sin brechas".
- `CL-ORIG`: documento intacto.
- `CL-PARAF`: paráfrasis o reordenamiento.
- `CL-FORMATO`: tabla → prosa, ecuación LaTeX → texto plano.
- `CL-EQUIV`: unidades equivalentes (0,15 g = 1,47 m/s²) o sinónimos ("aceleración pico efectiva" = Aa).
- `CL-TOLER`: cambio dentro de la tolerancia normativa.

**Validador de la mutación:** antes de aceptar un caso se verifica que la omisión o contradicción efectivamente viola el checklist (para contradicciones, recalculando con el motor), y que los controles no violan nada. Una mutación que no se puede verificar se descarta.

### 2.4 Esquema de un caso

```json
{"caso_id": "A23-SINC-CT-VALOR-01", "tarea": "T2", "semilla": "nsr10/A.2.3-2", "formato": "tabla",
 "operador": "CT-VALOR", "categoria_limitante": "contradiccion",
 "documento": "...", "checklist_ref": "A.2.3-2",
 "esperado": [{"item_id": "A.2.3-2/Sincelejo/Aa", "tipo": "contradiccion", "valor_doc": 0.25, "valor_norma": 0.10}],
 "diff": "...", "seed": 17, "split": "test"}
```

### 2.5 Tamaño y particiones

- **Piloto:** 10 semillas × (1 limpio + 3 controles benignos + ~6 omisiones + ~6 contradicciones) ≈ 160 casos.
- **v1:** ~40 semillas, ≈ 600 casos. Al menos 30 casos positivos y 30 controles por cada estrato de formato, para que los intervalos sirvan.
- Particiones `dev` y `test`. Los casos de `test` **nunca** se usan como few-shot ni para ajustar prompts. Los documentos saboteados **nunca** se ingieren a Supabase.

---

## 3. Taxonomía de limitantes (etiqueta de cada falla)

| Código | Limitante | Respuesta correcta | Cómo se aísla |
|---|---|---|---|
| L1 | Ausencia total del documento en el corpus | Abstención explícita | Se quita el chunk del índice local |
| L2 | Falla de recuperación (el documento existe) | La respuesta correcta | Corrida con **contexto oráculo**: si acierta con el chunk dorado inyectado y falla con el recuperado, es recuperación |
| L3 | Confusión de motor o de intención | Enrutar al motor correcto | Matriz de confusión del enrutador (caso Sincelejo) |
| L4 | Negación explícita | Respetar la negación | Operador `CT-NEG` |
| L5 | Mención indirecta o sinónimo | Reconocer la equivalencia, sin brecha | `CL-EQUIV` + preguntas parafraseadas |
| L6 | Falso positivo (brecha inventada) | Sin brecha | Controles `CL-*` |
| L7 | Alucinación numérica | Cifras solo del contexto | Reutilizar `_detectar_posible_alucinacion_numerica()` |
| L8 | Vigencia normativa | Citar la versión vigente | `CT-VERSION` |
| L9 | Abstención falsa | Responder | Casos donde el dato existe (Sincelejo) |

**Escalera de diagnóstico por caso:** ¿enrutó bien? → ¿el chunk dorado está en el top-k? → ¿acierta con contexto oráculo? → ¿la respuesta está soportada por el contexto? La primera pregunta que falla es la causa.

---

## 4. Métricas

**Por ítem del checklist (T2):** TP / FP / FN / TN →
- **Recall** (brechas encontradas / inyectadas).
- **Precisión** (brechas reales / reportadas).
- F1 y especificidad.
- **Tasa de documentos limpios con al menos una brecha inventada** (falsos positivos a nivel documento).

El emparejamiento hallazgo ↔ ítem es primero **determinista** (item_id o numeral + valor + tipo omisión/contradicción), con dos niveles: estricto (tipo y ubicación correctos) y laxo (ítem correcto). El juez LLM solo desempata, y se calibra con `anotacion_experto.py` antes de confiar en él.

**T1:**
- Exactitud del valor.
- Abstención correcta (L1) vs **abstención falsa** (L9).
- Exactitud del enrutador y matriz de confusión.
- Recall@k y MRR del chunk dorado.

**Groundedness:** cada hallazgo debe citar un fragmento que exista literalmente en el documento o contexto (chequeo de cadena, `metricas_sin_llm.py`). También se mide el porcentaje de cifras de la respuesta que aparecen en el contexto.

**Consistencia:**
1. Por formato (estratificada).
2. Ante transformaciones benignas: invarianza `CL-*` vs `CL-ORIG`.
3. Entre 3 paráfrasis de la misma pregunta.
4. Entre 3 corridas repetidas (acuerdo / κ de Fleiss).

**Operación:** latencia p50/p95, tokens y costo por caso.

**Estadística:** `packages/eval-stats` (IC bootstrap, pruebas pareadas sobre los mismos casos, corrección de Holm). Las hipótesis y el umbral de aceptación se escriben **antes** de cada corrida.

---

## 5. Qué se compara

| Eje | Variantes |
|---|---|
| Modelo | Groq (actual), gpt-4o-mini (respaldo actual), Ollama `qwen2.5:7b` local en HOMELAB (costo 0) |
| Prompt | Prompt actual del dominio; extracción estructurada guiada por checklist; extracción en JSON sin juicio |
| Arquitectura | (a) LLM juzga todo; (b) RAG + LLM; (c) **LLM extrae valores a un esquema y Python compara contra el checklist** |
| Enrutador | keyword; keyword → contrastivo (actual); contrastivo con **umbral mínimo y margen** sobre `normativa_general`; abstención explícita "dominio ambiguo" |
| Troceo de tablas | tabla completa; **sub-tabla** (filas con encabezado repetido); fila serializada (`Ciudad: Sincelejo \| Aa: 0,10 \| Av: 0,15`) |

Hipótesis principal: la arquitectura (c) baja los falsos positivos sin perder recall. Es la misma regla que ya rige los motores: el LLM no calcula, solo extrae y explica.

---

## 6. Experimentos, en orden

- **E1, enrutador (barato, sin LLM).** Unas 150 preguntas etiquetadas con su motor: las 23 del comparador + las de `test_rag_motores_regresion.py` + variantes de Aa/Av por municipio, sinónimos y negaciones. Se mide exactitud y abstención falsa con cada variante del enrutador. Reutiliza `scripts/evaluacion/comparar_enrutador_keyword_vs_contrastivo.py`.
- **E2, tabla vs sub-tabla (sin LLM).** Recall@k del chunk dorado con un índice local por variante de troceo, sobre Tabla A.2.3-2, A.2.4-3 y φ de C.9.3.
- **E3, T2 piloto (160 casos).** Matriz modelo × prompt × arquitectura (a/b/c), 3 repeticiones.
- **E4, T1 con sabotaje del índice.** L1 / L2 / L5 / L9 con contexto oráculo vs recuperado.

---

## 7. Aislamiento de producción

- Rama `eval/golden-sabotaje`. Código en `scripts/evaluacion/golden/`:
  - `semillas/`, `checklists/`
  - `mutaciones.py`, `validar_mutacion.py`
  - `casos/*.jsonl`
  - `harness.py`, `metricas.py`
- **Snapshot del corpus:** exportar en solo lectura los chunks relevantes a JSONL local versionado, con fecha y conteo. El índice de evaluación es local (numpy, o el Qdrant que ya está en `docker-compose.yml`). Ninguna corrida escribe en Supabase.
- **Cuota:** las corridas no usan la `GROQ_API_KEY` de producción (issue #53). Usan OpenAI con `LLM_FORZAR_OPENAI=true`, una clave Groq separada u Ollama local. Las respuestas se cachean por `(caso, config)` para no pagar dos veces.
- Las baterías existentes (`test_rag_nsr10_regresion.py`, `test_rag_motores_regresion.py`) son la **puerta de no-regresión**: un cambio que gane aquí y pierda allá no se integra.

---

## 8. Validez del dataset

- Una segunda persona revisa una muestra de semillas, checklists y mutaciones; idealmente un ingeniero o profesor de la CUC. Se mide su concordancia con quien los creó. La auditoría de evaluación ya señaló el riesgo de que los datasets los escriba el mismo equipo que construye el sistema.
- Cada caso guarda su diff y su seed, así que el dataset completo se puede regenerar.
- Se reporta por estrato, no solo el promedio. Los faltantes del juez se reportan como faltantes, no se descartan en silencio (lección de §3.3 de la auditoría).

---

## 9. Fases y criterios de salida

| Fase | Entregable | Sale cuando |
|---|---|---|
| F0 | Este protocolo + taxonomía + esquema + caso Sincelejo como regresión | Revisado y con issue abierto |
| F1 | 10 semillas + checklists | Cada ítem tiene numeral y valor verificados contra la fuente |
| F2 | Generador + validador de mutaciones | 100 % de los casos piloto pasan el validador |
| F3 | Harness offline + snapshot + caché | Una corrida completa sin escribir en Supabase ni usar cuota de producción |
| F4 | E1–E4 | Resultados con IC |
| F5 | Informe + decisión | Se integra solo lo que mejore la métrica preregistrada, con IC que no cruce 0 y sin regresión en las baterías existentes |
