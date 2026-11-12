# E3: modelos locales (Ollama en WSL) en las baterías de StructAI (#172)

Fecha: 2026-11-12. Hardware: Ryzen 5 8640HS, CPU sin GPU, WSL 16 GB / 10 núcleos, `num_ctx` 8192, temperatura 0,1.
Recuperación, enrutamiento y prompts idénticos a producción; solo cambia el generador (`_llamar_llm_con_respaldo`
parcheado). Caché de respuestas de producción desactivada (`RAG_CACHE_DISABLED`). Sin Groq ni OpenAI.
Tabla completa: `RESUMEN.md` (`python correr_bateria.py --resumen`). Respuestas: `resultados/<modelo>.jsonl`.

## Fase 3: piloto (38 casos = 13 motores + 25 NSR-10 estratificados)

| Modelo | Pasa | p50 por caso |
|---|---|---|
| qwen2.5:7b | **38/38** | ~2,5 min |
| qwen2.5:14b | 37/38 | ~3,5 min |
| llama3:8b | 34/38 | ~1,5 min |
| hermes3 | 34/38 | ~1,8 min |

McNemar exacto, qwen2.5:7b vs llama3:8b y vs hermes3: discordantes 4–0, p = 0,125 (no significativo con n = 38).
El 14B no mejora al 7B y cuesta ~2× → descartado para CI. Elegido **qwen2.5:7b**.

## Fase 4: batería completa con qwen2.5:7b (138 casos)

| Batería | Pasa | Wilson IC95 |
|---|---|---|
| Motores | 13/13 | 77–100 % |
| NSR-10 | 106/125 (84,8 %) | 77,5–90,0 % |
| **Total** | **119/138 (86,2 %)** | 79,5–91,0 % |

Fallos por título: **H 9**, F 5 (aluminio), K 2 (vidrio), B 1, NTC 174 1, H/F restantes en la lista de `resultados`.

### Alucinación numérica: 4 marcas, 1 real

| Caso | Valor marcado | Veredicto |
|---|---|---|
| D-no-reforzada-zona-baja-Aa-005 | 1.123 | Falso positivo: "1.123 municipios" viene del prompt del sistema |
| F-espesor-minimo-entregado-95porciento | 2,00 / 1,90 mm | Falso positivo: ejemplo ilustrativo del 95 %, aritmética correcta |
| F-f546-tirante-excentrico-06ao | 0,4 | Falso positivo: 1 − 0,6 derivado del dato correcto |
| H-kst-amax-macizos-rocosos-100 | 0,05 MPa | **Real**: Kst/amax es adimensional; valor y unidad inventados (caso fallido) |

→ 1/138 alucinaciones reales (0,7 %). El detector debería ignorar cifras presentes en el prompt del sistema y
aritmética derivada de cifras del contexto (mejora propuesta, no aplicada).

## Discusión

- qwen2.5:7b es viable como **generador del CI nocturno** (#178): 86 % en la batería NSR-10 sin GPU, ~2 min por caso
  → la batería completa cabe en ~4,5 h de noche. **No va a producción** (decisión del usuario).
- Los fallos se concentran en el **Título H**, que es justamente el título con huecos de corpus
  (`scripts/ingesta/nsr10/PLAN_HUECOS_GRAFO_2026-11.md`). Falta separar si fallan por recuperación o por generación:
  medir recall@k del chunk esperado en esos 9 casos (sin LLM) antes de culpar al modelo.
- No hay referencia de Groq medida en esta corrida (no se gastó cuota); la comparación con producción queda pendiente
  de una corrida de referencia autorizada.

## Incidente de la corrida

WSL se apagó por inactividad entre dos renovaciones del keepalive (una falló al lanzarse desde PowerShell). 5 casos
quedaron con `ConnectError`; se borraron de la caché y se re-corrieron. Para #178: el proceso nocturno debe verificar
`/api/version` antes de cada caso y reintentar, en vez de grabar el error.

## Fase 4b: ¿recuperación o generación? (2026-11-12)

`recuperacion_sin_llm.py` corre `ask()` de producción con un generador falso y verifica si el hecho esperado está en
el contexto recuperado (mismo `_contiene_alguna` del test). Resultado: **120/125 con el hecho en contexto**; los 21
casos del Título H lo tienen todos. Los fallos de H NO eran de recuperación.

Causa real: **truncamiento silencioso de Ollama.** 9 casos tenían contextos > 18.000 caracteres; con `num_ctx` 8192 y
`num_predict` 700 no cabían y Ollama recortó el prompt a la mitad (exactamente 4.098 tokens en los 9). De esos 9
pasaba 1; del resto, 118/129. El indicador `prompt_truncado` (>= num_ctx − 8) no lo detectaba.

Re-corrida de esos 9 con `STRUCTAI_NUM_CTX=16384`: **9/9 OK** (prompts reales de 8.207 a 10.284 tokens; ~4–7 min por
caso). Desaparece también la única alucinación numérica real (Kst/amax).

| Clasificación de los 19 fallos originales | n |
|---|---|
| Truncamiento del prompt (config, no modelo) | 8 (todos H) |
| Recuperación: hecho ausente del contexto | 5 (F 3, K 2) |
| Generación: el hecho estaba y el modelo no lo usó | 6 (H raíces, F 3, B 1, NTC 174 1) |

**Resultado corregido de qwen2.5:7b con num_ctx 16384: 127/138 (92,0 %, Wilson IC95 86,3–95,5 %); NSR-10 114/125.**
Recomendación para #178: `num_ctx` 16384 (o calcularlo por caso), y marcar truncado si `prompt_eval_count` es mucho
menor que la estimación de tokens del prompt (~caracteres/3,5). Las comparaciones entre modelos deben repetirse con
la misma ventana corregida: con 8192 se medía, en parte, cómo cada modelo tolera un contexto cortado.

## Fase 4c: robustez del proceso nocturno y fallos restantes (2026-11-12)

**Causa raíz de las caídas:** WSL apaga la distro ~16 s después de que sale su último proceso, y con ella
el servicio de Ollama (journalctl: ciclos Started/Stopped cada ~16 s tras un `wsl -- true`). Por eso se
cayeron dos corridas cuando venció un keepalive externo. Cambios en `correr_bateria.py`:
- El harness mantiene `wsl.exe -d Ubuntu -- sleep infinity` como proceso hijo mientras corre y pide a
  Windows no suspenderse (`SetThreadExecutionState`). Se libera al salir.
- Antes de cada caso verifica `/api/version`; si Ollama no responde, espera hasta 600 s.
- Un error de conexión en cualquier llamada del caso (incluida la descomposición, que `ask()` atrapa
  por dentro) descarta y repite el caso completo (2 reintentos). **Nunca se graba un caso con Ollama
  caído**: si no vuelve, sale con código 4 y relanzar retoma de la caché.
- `num_ctx` 16384 por defecto; `prompt_truncado` también se marca si leyó < 60 % de los tokens estimados
  (caracteres / 3,2), porque Ollama recorta a ~num_ctx/2 en vez de llenar la ventana.
Verificado: con puerto muerto corta sin grabar (exit 4); con WSL apagado, Ollama vuelve en ~13 s y sigue
vivo sin uso; un caso real pasa de punta a punta.

`nocturno.sh` corre los modelos indicados con la batería completa, relanza ante el código 4 y al final
ejecuta `comparar_modelos.py` (criterio prerregistrado: McNemar exacto + Holm contra el de mayor tasa,
IC de Wilson y bootstrap por título; empate → el más barato solo si está a ≤ 3 puntos del candidato).

**Los 5 fallos de recuperación** (`diagnostico_fallos.py`, búsqueda literal en `nsr10_chunks`):

| Caso | Diagnóstico |
|---|---|
| F-f544-kz-6061-t6 | Recuperación: la Tabla F.5.4.4-1 (kz) está en el corpus y no se trae |
| K-esfuerzos-termicos-probabilidad-rotura-08porciento | Recuperación probable: K.4.2.4 (esfuerzos térmicos) contiene "0.8" |
| K-templado-vs-termoendurecido-compresion | No concluyente: la variante "moderada" es genérica |
| F-f52-durabilidad-a-agua-salada-proteccion | Dato no hallado literalmente: hueco o redacción distinta |
| F-f541-2-esfuerzo-limite-po-6061-t6 | Dato no hallado literalmente: hueco o redacción distinta |
